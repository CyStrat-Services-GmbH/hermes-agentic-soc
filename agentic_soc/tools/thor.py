"""THOR JSON v2/v3 adapter and local executable integration.

THOR 10.7 writes JSON v2 with ``--jsonfile=FILE --jsonv2``; THOR 11 writes JSONL v3 by default.
JSON v1 (THOR 10 ``--jsonfile`` without ``--jsonv2``) keeps its reasons in flat ``reason_N`` keys;
it is refused instead of being imported without them.

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
import stat
import tempfile
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

from ..security import BoundaryError, Redactor, canonical, contained, private_directory

MAX_BYTES = 50 * 1024 * 1024
MAX_EVENTS = 100000
# THOR only raises an alert when one sub-score is above 75 (THOR 11 states it as "at least 76").
ALERT_SUBSCORE = 75
LOG_VERSION = re.compile(r"v?([123])(?:\.\d+){0,2}")
V1_REASON_KEY = re.compile(r"(?:reason|subscore)_\d+")
V3_TYPES = {"THOR assessment", "THOR message", "THOR finding"}  # "THOR finding": early THOR 11 previews
RECORD_ID = re.compile(r"\bEventRecordID: (\d+)")


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


def band(score: float | None, top_subscore: float | None = None) -> str:
    """THOR's default level for a total score. 81+ is an alert only if a sub-score is above 75."""
    if score is None:
        return "UNKNOWN"
    if score >= 81:
        return "ALERT" if top_subscore is None or top_subscore > ALERT_SUBSCORE else "WARNING"
    return "WARNING" if score >= 60 else "NOTICE" if score >= 40 else "INFO"


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

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise BoundaryError("JSON numeric overflow is not supported.")
        return number

    def loads(value):
        try:
            return json.loads(value, object_pairs_hook=pairs, parse_constant=reject_constant, parse_float=finite_float)
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


def read_stable_evidence(path: Path) -> bytes:
    """Bounded regular-file read; do not follow a final-component replacement symlink."""
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    except OSError:
        raise BoundaryError("Evidence could not be opened as a stable regular file.") from None
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise BoundaryError("Evidence must be a regular file.")
        if before.st_size > MAX_BYTES:
            raise BoundaryError("Evidence exceeds the 50 MiB import limit.")
        raw = stream.read(MAX_BYTES + 1)
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
        raise BoundaryError("Evidence changed during import. Acquire a stable copy before analysis.")
    if len(raw) > MAX_BYTES:
        raise BoundaryError("Evidence exceeds the 50 MiB import limit.")
    return raw


def identity_text(value):
    return value if isinstance(value, str) and value.strip() and not any(ord(c) < 32 for c in value) else ""


def positive_id(value):
    return ((isinstance(value, int) and not isinstance(value, bool) and value > 0)
            or (isinstance(value, str) and value.isascii() and value.isdecimal() and int(value) > 0))


def timestamp_identity(value):
    try:
        return isinstance(value, str) and datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except (ValueError, TypeError, OverflowError):
        return False


def as_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def record_schema(raw_event: dict, e: dict) -> str | None:
    """'1', '2' or '3' for a THOR JSON record; None if the record cannot be classified safely."""
    version = None
    if "log_version" in e or "version" in e:
        match = LOG_VERSION.fullmatch(str(e.get("log_version", e.get("version"))))
        if not match:
            return None
        version = match.group(1)
    if raw_event.get("type") in V3_TYPES or "meta" in e:
        meta = e.get("meta")
        ok = (raw_event.get("type") in V3_TYPES and isinstance(meta, dict)
              and any(k in meta for k in ("level", "module")))
        return "3" if ok and version in (None, "3") else None
    if version == "1" or (version is None and any(V1_REASON_KEY.fullmatch(k) for k in e)):
        return "1"
    return "2" if version in (None, "2") else None


def reason(name, score, rule, kind, description) -> dict:
    return {"name": str(name if name is not None else "unnamed"), "score": score_number(score),
            "rule": str(rule) if rule is not None else "", "kind": str(kind) if kind is not None else "",
            "description": str(description if description is not None else "")[:1000]}


def reason_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    return value if isinstance(value, list) else [{"name": str(value), "summary": str(value)}]


def view_v2(e: dict) -> dict:
    """Common view of a THOR 10 JSON v2 record (flat module keys; nested file/image objects)."""
    obj = {**as_dict(e.get("details")), **e}
    file_value = obj.get("file")
    if isinstance(file_value, dict):  # Filescan, SHIMCache, LogScan
        artifact, path = file_value, file_value.get("path", file_value.get("name", ""))
    elif isinstance(file_value, str):  # Amcache: path string, file details in file_2
        artifact, path = as_dict(obj.get("file_2")), file_value
    else:  # ProcessCheck image (with path), ServiceCheck image (path in image_path)
        artifact = as_dict(obj.get("image"))
        path = artifact.get("path", obj.get("image_path", ""))
    times = {k: artifact[k] for k in ("created", "modified", "accessed") if isinstance(artifact.get(k), str)}
    if isinstance(obj.get("event_time"), str):
        times["event_time"] = obj["event_time"]
    entry = obj.get("entry")
    found = RECORD_ID.search(entry) if isinstance(entry, str) else None
    record_id = found.group(1) if found else as_dict(entry).get("eventrecordid")
    reasons = []
    for r in reason_list(obj.get("reasons")):
        r = r if isinstance(r, dict) else {"name": str(r)}
        sig = as_dict(r.get("signature"))
        reasons.append(reason(r.get("name"), r.get("score"), sig.get("rulename"), r.get("sigclass"),
                              sig.get("description")))
    return {"level": obj.get("level"), "module": obj.get("module"), "message": obj.get("message"),
            "score": obj.get("score"), "host": e.get("hostname", e.get("host")), "scan_id": e.get("scanid"),
            "time": e.get("time", e.get("timestamp")), "path": path, "artifact": artifact, "top": obj,
            "times": times, "pid": obj.get("pid"), "process_name": obj.get("process_name", ""),
            "process_start": obj.get("created") if "pid" in obj else None,
            "event_id": obj.get("event_id"), "record_id": record_id, "channel": obj.get("event_channel"),
            "reasons": reasons}


def view_v3(e: dict) -> dict:
    """Common view of a THOR 11 JSON v3 record (meta block, typed subject, reasons with signatures)."""
    meta, subject = as_dict(e.get("meta")), as_dict(e.get("subject"))
    kind = subject.get("type")
    if kind == "file":
        artifact = subject
    else:  # process and service images, AmCache and other file references
        artifact = as_dict(subject.get("image")) or as_dict(subject.get("file"))
    times = {k: v for k, v in as_dict(artifact.get("file_times")).items()
             if k in {"created", "modified", "accessed"} and isinstance(v, str)}
    entry = as_dict(subject.get("entry"))
    if kind == "eventlog entry" and isinstance(entry.get("timecreated_systemtime"), str):
        times["event_time"] = entry["timecreated_systemtime"]
    reasons = []
    for r in reason_list(e.get("reasons")):
        r = r if isinstance(r, dict) else {"summary": str(r)}
        sig = as_dict(r.get("signature"))
        reasons.append(reason(r.get("summary"), sig.get("score"), sig.get("rule_name"), sig.get("kind"),
                              sig.get("description")))
    hashes = dict(as_dict(artifact.get("hashes")))
    if "sha1" in subject:  # AmCache keeps the recorded SHA1 on the entry itself
        hashes.setdefault("sha1", subject["sha1"])
    process = kind == "process"
    eventlog = kind == "eventlog entry"
    return {"level": meta.get("level"), "module": meta.get("module"), "message": e.get("message"),
            "score": e.get("score"), "host": meta.get("hostname"), "scan_id": meta.get("scan_id"),
            "time": meta.get("time"), "path": artifact.get("path", ""), "artifact": hashes, "top": {},
            "times": times, "pid": subject.get("pid") if process else None,
            "process_name": subject.get("name", "") if process else "",
            "process_start": subject.get("created") if process else None,
            "event_id": entry.get("eventid") if eventlog else None,
            "record_id": entry.get("eventrecordid") if eventlog else None,
            "channel": entry.get("channel") if eventlog else None, "reasons": reasons}


def parse(path: Path, redactor: Redactor) -> dict:
    raw = read_stable_evidence(path)
    try:
        records = events_from_text(raw.decode("utf-8-sig"))
    except UnicodeDecodeError:
        raise BoundaryError("Evidence must be UTF-8 JSON/NDJSON.") from None
    events = []
    unsupported, legacy_v1 = [], []
    schemas = Counter()
    for index, raw_event in enumerate(records):
        e = lowerkeys(raw_event)
        schema = record_schema(raw_event, e)
        if schema == "1":
            legacy_v1.append(index + 1)
            continue
        if schema is None:
            unsupported.append(index + 1)
            continue
        v = view_v3(e) if schema == "3" else view_v2(e)
        if v["level"] is None and v["module"] is None and v["message"] is None and v["score"] is None:
            unsupported.append(index + 1)
            continue
        schemas[f"v{schema}"] += 1
        normalized_reasons = v["reasons"]
        score = score_number(v["score"])
        # Never add/max individual reason scores to invent the object's final score.
        subscores = [r["score"] for r in normalized_reasons if r["score"] is not None]
        default_band = band(score, max(subscores) if subscores else None)
        source_level = str(v["level"] or "").upper()
        if source_level == "WARN":
            source_level = "WARNING"
        if source_level not in {"ALERT", "WARNING", "NOTICE", "INFO", "ERROR", "DEBUG"}:
            source_level = "UNKNOWN"
        severity = source_level if source_level != "UNKNOWN" else default_band
        host = identity_text(v["host"]) or "unknown"
        scan_id = identity_text(v["scan_id"])
        path_value = identity_text(v["path"])
        message = str(v["message"] if v["message"] is not None else "")
        reason_text = canonical(normalized_reasons) + message + path_value
        credential_context = bool(re.search(r"(?i)(?:\b(?:sam|ntds|ntlm|lmhash|password|credential)\b|\.sam\b)", reason_text))
        hashes = {}
        if not credential_context:
            for key, length in (("md5", 32), ("sha1", 40), ("sha256", 64)):
                h = v["artifact"].get(key, v["top"].get(key, ""))
                if isinstance(h, str) and re.fullmatch(f"[a-fA-F0-9]{{{length}}}", h):
                    hashes[key] = h.lower()
        # THOR's own status output (start-up, licence and coverage notices, match limits, the report) is a
        # message, not a finding. v3 types it; in v2 a finding has a score, reasons or a described artifact.
        if schema == "3":
            record_kind = "message" if raw_event.get("type") == "THOR message" else "finding"
        else:
            artifact = path_value or hashes or v["times"] or v["pid"] is not None or v["event_id"] is not None
            record_kind = ("finding" if score is not None or normalized_reasons or source_level == "ALERT" or artifact
                           else "message")
        module = str(v["module"] if v["module"] is not None else "unknown")
        pid, start = v["pid"], v["process_start"]
        identity = [host, scan_id, path_value, hashes, pid, v["event_id"], v["record_id"], v["channel"], start]
        # Missing host/scan, unhashed paths and reused PIDs cannot establish identity.
        stable_host_scan = host not in {"", "unknown"} and bool(scan_id)
        stable_file = bool(path_value and hashes)
        stable_record = bool(positive_id(v["record_id"]) and positive_id(v["event_id"]) and identity_text(v["channel"]))
        stable_process = bool(positive_id(pid) and timestamp_identity(start))
        if not stable_host_scan or not (stable_file or stable_record or stable_process):
            identity.extend([module, index])
        key = hmac.new(redactor.salt, canonical(identity).encode(), hashlib.sha256).hexdigest()[:20]
        event = {
            "event_id": f"E{index + 1:06d}", "finding_id": f"F-{key}", "record_kind": record_kind,
            "host": redactor.token(host, "host"), "module": module,
            "scan_id": redactor.token(scan_id or "unknown", "scan"),
            "score": score, "level": severity, "source_level": source_level,
            "score_band": default_band, "message": message,
            "file": path_value, "process": {"name": str(v["process_name"] or ""), "pid": pid},
            "hashes": hashes, "reasons": normalized_reasons,
            "detection_time": str(v["time"]) if v["time"] is not None else None,
            # Detection time is never promoted to artifact activity time.
            "artifact_times": v["times"],
            "evidence_strength": "Confirmed",
            "evidence_claim": "The supplied export contains this scanner observation, not proof of execution or malicious intent.",
            "attack": [],  # No speculative mapping from rule names or free-text T-numbers.
        }
        events.append(redactor.clean(event))
    if legacy_v1:
        raise BoundaryError(f"{len(legacy_v1)} THOR JSON v1 records; v1 is not supported. Use THOR 10.7 with "
                            "--jsonfile=FILE --jsonv2 (JSON v2) or THOR 11 (JSON v3). No partial assessment produced.")
    if unsupported:
        raise BoundaryError(f"{len(unsupported)} unsupported or malformed events; no partial assessment produced.")
    inventory = {
        "event_count": len(events),
        "finding_count": len({e["finding_id"] for e in events}),
        "levels": dict(Counter(e["level"] for e in events)),
        "modules": dict(Counter(e["module"] for e in events)),
        "hosts": sorted({e["host"] for e in events}),
        "scans": sorted({e["scan_id"] for e in events}),
        "log_versions": dict(schemas),
        "record_kinds": dict(Counter(e["record_kind"] for e in events)),
        "message_levels": dict(Counter(e["level"] for e in events if e["record_kind"] == "message")),
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
                            "THOR JSON v1, text logs and the hash CSV are not supported; use JSON v2 (THOR 10.7 --jsonv2) or v3 (THOR 11).",
                            "Personal-data minimisation is best effort; review outputs before sharing."]}


def subprocess_env() -> dict:
    # No inherited provider credentials, proxy secrets, PYTHONPATH or YOLO flags.
    # THOR_LICENSE (base64 of a .lic file) is THOR's own license source and only reaches THOR.
    allowed = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LANG", "LC_ALL", "THOR_LICENSE"}
    return {k: v for k, v in os.environ.items() if k in allowed}


THOR_VERSION = re.compile(r"^THOR (\d+)\.(\d+)\.(\d+)(\S*)", re.MULTILINE)
# Per THOR major version: the help call that lists every flag the scan uses, the flags it must list,
# and the JSON output. THOR 10.7 shows most of them only in --fullhelp; THOR 11 shows them in --help long.
LAUNCH = {
    10: {"help": ["--fullhelp"], "output": "thor.json", "schema": "v2",
         "required": {"--module", "--path", "--jsonfile", "--jsonv2", "--rebase-dir", "--suppresspi",
                      "--nolog", "--nocsv", "--nothordb"}},
    11: {"help": ["--help", "long"], "output": "thor.jsonl", "schema": "v3",
         "required": {"--module", "--path", "--json", "--output-directory", "--no-personal-data",
                      "--no-html", "--no-csv", "--no-thordb"}},
}


def launch_argv(major: int, exe: str, target: str, run_dir: str) -> list[str]:
    """Fixed Filescan argv. THOR 10's optional-value --jsonfile only takes its value with '='."""
    if major == 10:
        return [exe, "--module", "Filescan", "--path", target, "--jsonfile=thor.json", "--jsonv2",
                "--rebase-dir", run_dir, "--suppresspi", "--nolog", "--nocsv", "--nothordb"]
    return [exe, "--module", "Filescan", "--path", target, "--json", "thor.jsonl",
            "--output-directory", run_dir, "--no-personal-data", "--no-html", "--no-csv", "--no-thordb"]


def probe(exe: Path, args: list[str], cwd: str) -> tuple[int, str]:
    proc = subprocess.run([str(exe), *args], cwd=cwd, env=subprocess_env(),
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15, check=False)
    return proc.returncode, proc.stdout[:2_000_000].decode("utf-8", errors="replace")


def scan(thor_path: str, target: str, scan_roots: list[Path], data_root: Path,
         timeout: int = 900, execute: bool = False) -> dict:
    if not thor_path:
        return {"ok": False, "error": "THOR Lite is not configured. Obtain it separately from Nextron and set thor_path.",
                "download": "https://www.nextron-systems.com/thor-lite/",
                "setup": ["Register on the THOR Lite page with a business e-mail address; Nextron e-mails a download link and the .lic license file.",
                          "Unpack the package into its own program folder and save the .lic attachment into that folder.",
                          "Run thor-lite-util update in the program folder, then set thor_path to the THOR Lite binary.",
                          "Details: docs/OPERATOR-GUIDE.md, section 'Obtain THOR Lite'. The operator does this; the agent does not."]}
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
    # THOR syntax that would change the scanned path: ':' suffixes (NOWALK, v10 placeholders), ','
    # (THOR 11 splits --path as CSV), '<...>' placeholders, and $VAR / %VAR% expansion.
    if (":" in path_text[len(p.drive):] or any(c in path_text for c in ",<>$%")
            or any(ord(c) < 32 for c in path_text)):
        raise BoundaryError("Special THOR path syntax is not supported.")
    data_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix="thor-help-", dir=data_root) as help_dir:
        code, version_text = probe(exe, ["--version"], help_dir)
        found = THOR_VERSION.search(version_text)
        if code != 0 or not found:
            raise BoundaryError("Could not read a THOR version from --version; execution refused.")
        version = tuple(int(x) for x in found.groups()[:3])
        label = found.group(0).removeprefix("THOR ")
        major = version[0]
        if version < (10, 7) or major not in LAUNCH:
            raise BoundaryError(f"THOR {label} is not supported; use THOR or THOR Lite 10.7 or 11.")
        launch = LAUNCH[major]
        code, help_text = probe(exe, launch["help"], help_dir)
    # Verify exact flags, not prefix matches.
    flags = set(re.findall(r"--[a-z][a-z0-9-]*", help_text))
    required = launch["required"]
    if code != 0 or not required <= flags:
        raise BoundaryError(f"THOR {label} CLI help lacks required verified output/privacy flags; execution refused.")
    run_id = uuid.uuid4().hex
    run_dir = data_root / "scans" / run_id
    argv = launch_argv(major, str(exe), str(p), str(run_dir))
    if not execute:
        return {"ok": True, "dry_run": True, "platform": platform.system(), "thor_version": label,
                "json_schema": launch["schema"], "verified_flags": sorted(required),
                "requires_human_approval": True,
                "note": "No scan executed; CLI version and help only. Run execute=true through Hermes to request approval."}
    private_directory(data_root, "scans")
    private_directory(data_root / "scans", run_id)
    timeout = max(10, min(int(timeout), 3600))
    # stdout can contain sensitive evidence; discard it. THOR writes its log into the private run dir.
    try:
        proc = subprocess.run(argv, cwd=run_dir, env=subprocess_env(), stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"ok": False, "run_id": run_id, "timed_out": True, "thor_version": label,
                "error": "THOR timed out. Any partial output is incomplete and cannot establish a clean host."}
    output = run_dir / launch["output"]
    ok = proc.returncode == 0 and output.is_file()
    return {"ok": ok, "run_id": run_id, "returncode": proc.returncode, "thor_version": label,
            "json_schema": launch["schema"], "output": str(output) if output.is_file() else None,
            "scan_completed": ok, "note": "Execution status only; findings require parsing and analyst review."}
