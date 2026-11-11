"""THOR JSON v1/v2 adapter and local executable integration.

References: https://github.com/NextronSystems/jsonlog
https://thor-manual.nextron-systems.com/en/latest/usage/flags.html
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
import platform
import re
import subprocess
import tempfile
import uuid
from collections import Counter
from pathlib import Path

from ..security import BoundaryError, Redactor, canonical, contained, private_directory

MAX_BYTES = 50 * 1024 * 1024
MAX_EVENTS = 100000


def lowerkeys(value):
    if isinstance(value, dict):
        if len({str(k).lower() for k in value}) != len(value):
            raise BoundaryError("Ambiguous case-colliding field names; no assessment produced.")
        return {str(k).lower(): lowerkeys(v) for k, v in value.items()}
    if isinstance(value, list):
        return [lowerkeys(v) for v in value]
    return value


def score_number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        n = float(value)
        return n if math.isfinite(n) and 0 <= n <= 10000 else None
    except (ValueError, TypeError):
        return None


def band(score: float | None) -> str:
    if score is None:
        return "UNKNOWN"
    return "ALERT" if score >= 81 else "WARNING" if score >= 60 else "NOTICE" if score >= 40 else "INFO"


def events_from_text(text: str) -> list[dict]:
    """Strict JSON array, single event, events/findings wrapper, or NDJSON."""
    if not text.strip():
        raise BoundaryError("Empty evidence is not a clean scan.")
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise BoundaryError("Duplicate JSON keys are ambiguous; input refused.")
            obj[key] = value
        return obj

    def reject_constant(value):
        raise BoundaryError("Non-finite JSON constants are not supported.")

    def loads(value):
        try:
            return json.loads(value, object_pairs_hook=pairs, parse_constant=reject_constant)
        except RecursionError:
            raise BoundaryError("JSON nesting exceeds supported limits.") from None
    try:
        data = loads(text)
    except json.JSONDecodeError:
        try:
            data = []
            for line in text.splitlines():
                if line.strip():
                    if len(data) >= MAX_EVENTS:
                        raise BoundaryError("Import is limited to 100000 events.")
                    data.append(loads(line))
        except json.JSONDecodeError:
            raise BoundaryError("Malformed JSON/NDJSON; no partial assessment produced.") from None
    if isinstance(data, dict):
        if "events" in data and "findings" in data:
            raise BoundaryError("Ambiguous events/findings wrapper; choose one explicit event collection.")
        data = data.get("events", data.get("findings", [data]))
    if not isinstance(data, list) or not data or not all(isinstance(x, dict) for x in data):
        raise BoundaryError("Expected one or more structured THOR JSON events.")
    if len(data) > MAX_EVENTS:
        raise BoundaryError("Import is limited to 100000 events; split the source explicitly.")
    return data


def parse(path: Path, redactor: Redactor) -> dict:
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise BoundaryError("Evidence exceeds the 50 MiB import limit.")
    try:
        records = events_from_text(raw.decode("utf-8-sig"))
    except UnicodeDecodeError:
        raise BoundaryError("Evidence must be UTF-8 JSON/NDJSON.") from None
    events = []
    unsupported = []
    for index, raw_event in enumerate(records):
        e = lowerkeys(raw_event)
        version = str(e.get("log_version", e.get("version", ""))).lstrip("v")
        if (version and not re.fullmatch(r"[12](?:\.\d+){0,2}", version)) or str(e.get("type", "")).startswith("THOR "):
            unsupported.append(index + 1)
            continue
        if not any(k in e for k in ("level", "module", "message", "score")):
            unsupported.append(index + 1)
            continue
        details = e.get("details") if isinstance(e.get("details"), dict) else {}
        obj = {**details, **e}
        file_obj = obj.get("file", {})
        if isinstance(file_obj, str):
            file_obj = {"path": file_obj}
        if not isinstance(file_obj, dict):
            file_obj = {}
        process = obj.get("process", {})
        if not isinstance(process, dict):
            process = {"name": str(process)}
        reasons = obj.get("reasons", [])
        if isinstance(reasons, dict):
            reasons = [reasons]
        if not isinstance(reasons, list):
            reasons = [{"name": str(reasons)}]
        normalized_reasons = []
        for reason in reasons:
            r = reason if isinstance(reason, dict) else {"name": str(reason)}
            normalized_reasons.append({
                "name": str(r.get("name", r.get("rule", r.get("summary", "unnamed")))),
                "score": score_number(r.get("score")),
                "description": str(r.get("description", r.get("summary", "")))[:1000],
            })
        score = score_number(obj.get("score"))
        # Never add/max individual reason scores to invent the object's final score.
        source_level = str(obj.get("level", "")).upper()
        if source_level == "WARN":
            source_level = "WARNING"
        if source_level not in {"ALERT", "WARNING", "NOTICE", "INFO", "ERROR", "DEBUG"}:
            source_level = "UNKNOWN"
        severity = source_level if source_level != "UNKNOWN" else band(score)
        host = str(e.get("hostname", e.get("host", "unknown")))
        path_value = str(file_obj.get("path", file_obj.get("name", obj.get("filename", obj.get("path", "")))))
        reason_text = canonical(normalized_reasons) + str(obj.get("message", "")) + path_value
        credential_context = bool(re.search(r"(?i)(?:\b(?:sam|ntds|ntlm|lmhash|password|credential)\b|\.sam\b)", reason_text))
        hashes = {}
        if not credential_context:
            for key, length in (("md5", 32), ("sha1", 40), ("sha256", 64)):
                v = file_obj.get(key, obj.get(key, ""))
                if isinstance(v, str) and re.fullmatch(f"[a-fA-F0-9]{{{length}}}", v):
                    hashes[key] = v.lower()
        timestamps = obj.get("timestamps", {})
        if not isinstance(timestamps, dict):
            timestamps = {}
        # Detection time is never promoted to artifact activity time.
        artifact_times = {k: v for k, v in timestamps.items()
                          if k in {"created", "modified", "accessed", "event_time"} and isinstance(v, str)}
        module = str(obj.get("module", "unknown"))
        identity = [host, e.get("scanid", ""), path_value, hashes,
                    process.get("pid"), obj.get("eventid"), obj.get("recordid"),
                    obj.get("detectionid")]
        # Missing host/scan, unhashed paths and reused PIDs cannot establish identity.
        stable_host_scan = host not in {"", "unknown"} and bool(e.get("scanid"))
        stable_file = bool(path_value and hashes)
        stable_record = bool(obj.get("recordid") and obj.get("eventid") and obj.get("channel"))
        stable_process = bool(process.get("pid") and process.get("start_time"))
        identity.extend([obj.get("channel"), process.get("start_time")])
        if not stable_host_scan or not (stable_file or stable_record or stable_process):
            identity.extend([module, index])
        key = hmac.new(redactor.salt, canonical(identity).encode(), hashlib.sha256).hexdigest()[:20]
        event = {
            "event_id": f"E{index + 1:06d}", "finding_id": f"F-{key}",
            "host": redactor.token(host, "host"), "module": module,
            "scan_id": redactor.token(str(e.get("scanid", "unknown")), "scan"),
            "score": score, "level": severity, "source_level": source_level,
            "score_band": band(score), "message": str(obj.get("message", "")),
            "file": path_value, "process": {"name": process.get("name", ""), "pid": process.get("pid")},
            "hashes": hashes, "reasons": normalized_reasons,
            "detection_time": str(e.get("time", e.get("timestamp"))) if e.get("time", e.get("timestamp")) is not None else None,
            "artifact_times": artifact_times,
            "evidence_strength": "Confirmed",
            "evidence_claim": "The supplied export contains this scanner observation, not proof of execution or malicious intent.",
            "attack": [],  # No speculative mapping from rule names or free-text T-numbers.
        }
        events.append(redactor.clean(event))
    if unsupported:
        raise BoundaryError(f"{len(unsupported)} unsupported events (including possible THOR v3); no partial assessment produced.")
    inventory = {
        "event_count": len(events),
        "finding_count": len({e["finding_id"] for e in events}),
        "levels": dict(Counter(e["level"] for e in events)),
        "modules": dict(Counter(e["module"] for e in events)),
        "hosts": sorted({e["host"] for e in events}),
        "scans": sorted({e["scan_id"] for e in events}),
        "unique_files": len({e["file"] for e in events if e["file"]}),
        "unique_hashes": len({(k, v) for e in events for k, v in e["hashes"].items()}),
        "unknown_score_count": sum(e["score"] is None for e in events),
        "coverage_verified": False,
        "duplicate_observation_count": len(events) - len({e["finding_id"] for e in events}),
        "score_level_disagreement_count": sum(e["score"] is not None and e["source_level"] != "UNKNOWN"
                                              and e["source_level"] != e["score_band"] for e in events),
    }
    return {"schema_version": "1.0", "source_sha256": hashlib.sha256(raw).hexdigest(),
            "inventory": inventory, "events": events,
            "limitations": ["Input may be filtered or incomplete; no clean-host assurance.",
                            "Only stable same-host/same-scan artifact identities are grouped; missing identifiers remain independent.",
                            "THOR JSON v3, legacy text and CSV are not supported in this MVP.",
                            "Personal-data minimisation is best effort; review outputs before sharing."]}


def subprocess_env() -> dict:
    # No inherited provider credentials, proxy secrets, PYTHONPATH or YOLO flags.
    allowed = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LANG", "LC_ALL"}
    return {k: v for k, v in os.environ.items() if k in allowed}


def scan(thor_path: str, target: str, scan_roots: list[Path], data_root: Path,
         timeout: int = 900, execute: bool = False) -> dict:
    if not thor_path:
        return {"ok": False, "error": "THOR Lite is not configured. Obtain it separately from Nextron and set thor_path.",
                "download": "https://www.nextron-systems.com/thor-lite/"}
    exe = Path(thor_path).expanduser()
    if not exe.is_absolute() or not exe.is_file():
        raise BoundaryError("thor_path must name an existing absolute local executable.")
    exe = exe.resolve(strict=True)
    if platform.system() != "Windows" and not os.access(exe, os.X_OK):
        raise BoundaryError("Configured THOR executable is not executable.")
    if not scan_roots:
        raise BoundaryError("Real scan roots must first be configured by the operator.")
    p = contained(target, scan_roots, file=False)
    if not p.is_dir():
        raise BoundaryError("The MVP scans an explicitly allowed directory only.")
    path_text = str(p)
    # Colon after the drive is THOR special syntax, including in parent components.
    if ":" in path_text[len(p.drive):] or any(ord(c) < 32 for c in path_text):
        raise BoundaryError("Special THOR path syntax is not supported.")
    data_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix="thor-help-", dir=data_root) as help_dir:
        probe = subprocess.run([str(exe), "--help"], cwd=help_dir, env=subprocess_env(),
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15, check=False)
        help_text = probe.stdout[:2_000_000].decode("utf-8", errors="replace")
    # Verify exact flags, not prefix matches.
    flags = set(re.findall(r"--[a-z][a-z0-9-]*", help_text))
    required = {"--jsonfile", "--jsonv2", "--rebase-dir", "--suppresspi", "--path", "--module", "--nolog", "--nocsv"}
    if probe.returncode != 0 or not required <= flags:
        raise BoundaryError("Installed THOR CLI help lacks required verified v2/privacy flags; execution refused.")
    run_id = uuid.uuid4().hex
    run_dir = data_root / "scans" / run_id
    argv = [str(exe), "--module", "FileScan", "--path", str(p), "--jsonfile", "thor.json", "--jsonv2",
            "--rebase-dir", str(run_dir), "--suppresspi", "--nolog", "--nocsv"]
    if not execute:
        return {"ok": True, "dry_run": True, "platform": platform.system(),
                "verified_flags": sorted(required), "requires_human_approval": True,
                "note": "No scan executed; CLI help only. Run execute=true through Hermes to request approval."}
    private_directory(data_root, "scans")
    private_directory(data_root / "scans", run_id)
    timeout = max(10, min(int(timeout), 3600))
    # stdout can contain sensitive evidence; discard it. THOR writes its log into the private run dir.
    try:
        proc = subprocess.run(argv, cwd=run_dir, env=subprocess_env(), stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"ok": False, "run_id": run_id, "timed_out": True,
                "error": "THOR timed out. Any partial output is incomplete and cannot establish a clean host."}
    output = run_dir / "thor.json"
    ok = proc.returncode == 0 and output.is_file()
    return {"ok": ok, "run_id": run_id, "returncode": proc.returncode,
            "output": str(output) if output.is_file() else None,
            "scan_completed": ok, "note": "Execution status only; findings require parsing and analyst review."}
