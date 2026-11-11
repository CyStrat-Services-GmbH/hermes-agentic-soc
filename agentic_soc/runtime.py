"""Lazy runtime: registration itself performs no I/O."""

from __future__ import annotations

import json
import os
import uuid
import threading
import tempfile
from pathlib import Path

from .audit import Audit
from .security import BoundaryError, Redactor, contained, private_directory
from .tools import templates, thor, triage
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
        try:
            data = self.data()
            audit = Audit(data)
            audit.write(name, "started")
            from .api import BY_NAME, validate
            if name not in BY_NAME:
                raise BoundaryError("Unknown tool.")
            validate(params, BY_NAME[name]["parameters"])
            result = self.execute(name, params)
            audit.write(name, "completed", ok=bool(result.get("ok", True)))
            return result
        except Exception as exc:
            try:
                if audit is not None:
                    audit.write(name, "rejected", error_type=type(exc).__name__)
            except Exception:
                return {"ok": False, "error": "Audit unavailable; operation refused. Operator repair required."}
            if isinstance(exc, BoundaryError):
                return {"ok": False, "error": str(exc)}
            return {"ok": False, "error": "Operation failed safely; inspect operator logs. No raw evidence exposed.",
                    "error_type": type(exc).__name__}

    def execute(self, name: str, p: dict) -> dict:
        if name == "soc_template_list":
            return templates.list_templates(self.get_config("offensive_preview_enabled", False) is True)
        if name == "soc_template_install":
            return templates.install(self.root, **p, profile_home=self.data().parents[1],
                                     preview_enabled=self.get_config("offensive_preview_enabled", False) is True)
        if name == "thor_lite_scan":
            return thor.scan(self.get_config("thor_path", ""), p["target"],
                             [Path(x) for x in self.get_config("scan_roots", [])],
                             self.data(), self.get_config("scan_timeout", 900), p.get("execute", False))
        if name in {"thor_parse", "thor_first_assessment"}:
            parsed = thor.parse(self.evidence(p["path"]), self.redactor())
            run_id = uuid.uuid4().hex
            reports = private_directory(self.data(), "reports")
            out = private_directory(reports, run_id)
            self.write(out / "normalized.json", parsed)
            result = {"ok": True, "report_id": run_id, "inventory": parsed["inventory"],
                      "source_sha256": parsed["source_sha256"], "normalized": str(out / "normalized.json")}
            if name == "thor_first_assessment":
                case = assess(parsed)
                self.write(out / "case.json", case)
                text = markdown(case, parsed)
                self.write_text(out / "report.md", text)
                result.update({"verdict": case["verdict"], "priority": case["priority"],
                               "case_json": str(out / "case.json"), "report": str(out / "report.md"),
                               "preview": text[:6000]})
            return result
        if name == "soc_alert_triage":
            return triage.triage(p["alert"], self.redactor())
        if name == "soc_research_plan":
            if self.get_config("offensive_preview_enabled", False) is not True:
                raise BoundaryError("Offensive Security is a disabled gated preview. Ask the operator to review the preview settings; no target execution is available.")
            return triage.research_plan(p["scope"], p["target"], self.redactor())
        raise BoundaryError("Unknown tool.")

    @staticmethod
    def write(path: Path, value):
        Runtime.write_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))

    @staticmethod
    def write_text(path: Path, value: str):
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(value)
