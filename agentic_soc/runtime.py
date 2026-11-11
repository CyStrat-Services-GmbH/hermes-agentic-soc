"""Lazy runtime: registration itself performs no I/O."""

from __future__ import annotations

import json
import os
import uuid
import threading
import tempfile
import shutil
from pathlib import Path

from .audit import Audit
from .security import BoundaryError, Redactor, contained, private_directory
from .tools import templates, thor, triage, capabilities
from .scoring.thor_first_assessment import assess, markdown

_SALT_LOCK = threading.Lock()

class Runtime:
    def __init__(self, root: Path, data_factory, get_config):
        self.root = root
        self.data_factory = data_factory
        self.get_config = get_config

    def data(self) -> Path:
        data = self.data_factory()
        if data.is_symlink():
            raise BoundaryError("Plugin data root must not be a symlink.")
        data.mkdir(mode=0o700, parents=True, exist_ok=True)
        if os.name == "posix":
            data.chmod(0o700)
        return data

    def redactor(self) -> Redactor:
        salt_path = self.data() / "pseudonym.salt"
        with _SALT_LOCK:
            if salt_path.is_symlink() or (salt_path.exists() and not salt_path.is_file()):
                raise BoundaryError("Pseudonym salt must be a regular non-symlink file.")
            if not salt_path.exists():
                # Publish a complete salt atomically across processes. Readers never
                # observe an empty file between O_EXCL creation and the first write.
                fd, temporary = tempfile.mkstemp(prefix=".salt-", dir=salt_path.parent)
                try:
                    with os.fdopen(fd, "wb") as f:
                        f.write(os.urandom(32))
                        f.flush()
                        os.fsync(f.fileno())
                    try:
                        os.link(temporary, salt_path)
                    except FileExistsError:
                        pass
                finally:
                    Path(temporary).unlink(missing_ok=True)
            fd = os.open(salt_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(fd, "rb") as f:
                salt = f.read(33)
        if len(salt) != 32:
            raise BoundaryError("Pseudonym salt is invalid; operator repair required.")
        return Redactor(salt)

    def evidence(self, path: str) -> Path:
        configured = self.get_config("evidence_roots", [])
        if not isinstance(configured, list):
            raise BoundaryError("evidence_roots must be an operator-configured list.")
        roots = [self.root / "examples" / "demo", self.data()] + [Path(p) for p in configured]
        return contained(path, roots)

    def call(self, name: str, params: dict) -> dict:
        audit = None
        execution_started = False
        try:
            data = self.data()
            audit = Audit(data)
            audit.write(name, "started")
            from .api import BY_NAME, validate
            if name not in BY_NAME:
                raise BoundaryError("Unknown tool.")
            validate(params, BY_NAME[name]["parameters"])
            execution_started = True
            result = self.execute(name, params)
        except Exception as exc:
            try:
                if audit is not None:
                    audit.write(name, "rejected", error_type=type(exc).__name__)
            except Exception:
                return {"ok": False, "error": "Audit unavailable; operator review required.",
                        "error_code": "AUDIT_UNAVAILABLE", "execution_started": execution_started,
                        "retry_safe": False}
            if isinstance(exc, BoundaryError):
                return {"ok": False, "error": str(exc), "error_code": "BOUNDARY_REJECTED",
                        "execution_started": execution_started, "retry_safe": False}
            message = ("Operation did not complete successfully; partial effects may exist. Do not automatically retry."
                       if execution_started else "Operation refused before execution. No raw evidence exposed.")
            return {"ok": False, "error": message,
                    "error_type": type(exc).__name__, "execution_started": execution_started,
                    "retry_safe": False}
        result.setdefault("ok", True)
        try:
            audit.write(name, "completed", ok=bool(result["ok"]))
        except Exception:
            # Never tell the caller "refused" after a scan/profile/report already ran.
            # In particular, do not encourage an automatic repeat of a side effect.
            return {"ok": False, "error_code": "AUDIT_FINALIZATION_FAILED",
                    "error": "Operation returned a result, but its final audit append failed. Do not automatically retry.",
                    "operation_completed": True, "retry_safe": False,
                    "operation_result": result}
        return result

    def execute(self, name: str, p: dict) -> dict:
        if name == "soc_capabilities":
            return capabilities.inventory(self.root, self.get_config, p.get("technology"))
        if name == "soc_template_list":
            return templates.list_templates()
        if name == "soc_template_install":
            return templates.install(self.root, **p, profile_home=self.data().parents[1])
        if name == "thor_lite_scan":
            return thor.scan(self.get_config("thor_path", ""), p["target"],
                             [Path(x) for x in self.get_config("scan_roots", [])],
                             self.data(), self.get_config("scan_timeout", 900), p.get("execute", False))
        if name in {"thor_parse", "thor_first_assessment"}:
            parsed = thor.parse(self.evidence(p["path"]), self.redactor())
            run_id = uuid.uuid4().hex
            reports = private_directory(self.data(), "reports")
            out = reports / run_id
            staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=reports))
            result = {"ok": True, "report_id": run_id, "inventory": parsed["inventory"],
                      "source_sha256": parsed["source_sha256"], "normalized": str(out / "normalized.json")}
            try:
                self.write(staging / "normalized.json", parsed)
                if name == "thor_first_assessment":
                    case = assess(parsed)
                    self.write(staging / "case.json", case)
                    text = markdown(case, parsed)
                    self.write_text(staging / "report.md", text)
                    result.update({"verdict": case["verdict"], "priority": case["priority"],
                                   "case_json": str(out / "case.json"), "report": str(out / "report.md"),
                                   "preview": text[:6000]})
                if out.exists():
                    raise BoundaryError("Unexpected report-ID collision; no existing report was overwritten.")
                staging.rename(out)
            finally:
                if staging.exists():
                    shutil.rmtree(staging)
            return result
        if name == "soc_alert_triage":
            return triage.triage(p["alert"], self.redactor())
        raise BoundaryError("Unknown tool.")

    @staticmethod
    def write(path: Path, value):
        Runtime.write_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))

    @staticmethod
    def write_text(path: Path, value: str):
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(value)
