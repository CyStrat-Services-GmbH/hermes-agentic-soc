"""Lazy runtime: registration itself performs no I/O."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from .audit import Audit
from .security import BoundaryError, Redactor, contained
from .tools import templates, thor, triage
from .scoring.thor_first_assessment import assess, markdown


class Runtime:
    def __init__(self, root: Path, data_factory, get_config):
        self.root = root
        self.data_factory = data_factory
        self.get_config = get_config

    def data(self) -> Path:
        data = self.data_factory()
        data.mkdir(mode=0o700, parents=True, exist_ok=True)
        return data

    def redactor(self) -> Redactor:
        salt_path = self.data() / "pseudonym.salt"
        try:
            fd = os.open(salt_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "wb") as f:
                f.write(os.urandom(32))
        salt = salt_path.read_bytes()
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
        data = self.data()
        audit = Audit(data)
        audit.write(name, "started")
        try:
            result = self.execute(name, params)
            audit.write(name, "completed", ok=bool(result.get("ok", True)))
            return result
        except Exception as exc:
            audit.write(name, "rejected", error_type=type(exc).__name__)
            if isinstance(exc, BoundaryError):
                return {"ok": False, "error": str(exc)}
            return {"ok": False, "error": "Operation failed safely; inspect operator logs. No raw evidence exposed.",
                    "error_type": type(exc).__name__}

    def execute(self, name: str, p: dict) -> dict:
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
            out = self.data() / "reports" / run_id
            out.mkdir(parents=True, mode=0o700)
            self.write(out / "normalized.json", parsed)
            result = {"ok": True, "report_id": run_id, "inventory": parsed["inventory"],
                      "source_sha256": parsed["source_sha256"], "normalized": str(out / "normalized.json")}
            if name == "thor_first_assessment":
                case = assess(parsed)
                self.write(out / "case.json", case)
                text = markdown(case, parsed)
                with (out / "report.md").open("x", encoding="utf-8") as f:
                    f.write(text)
                result.update({"verdict": case["verdict"], "priority": case["priority"],
                               "case_json": str(out / "case.json"), "report": str(out / "report.md"),
                               "preview": text[:6000]})
            return result
        if name == "soc_alert_triage":
            return triage.triage(p["alert"], self.redactor())
        if name == "soc_research_plan":
            return triage.research_plan(p["scope"], p["target"], self.redactor())
        raise BoundaryError("Unknown tool.")

    @staticmethod
    def write(path: Path, value):
        with path.open("x", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
