"""Third-pass reliability, capability transparency and failure-semantics regressions."""

import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from agentic_soc.audit import Audit
from agentic_soc.runtime import Runtime
from agentic_soc.security import BoundaryError, Redactor
from agentic_soc.tools.thor import events_from_text, parse, read_stable_evidence
from agentic_soc.tools.capabilities import inventory
from agentic_soc.scoring.thor_first_assessment import assess

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples/demo/thor.json"
R = Redactor(b"x" * 32)


def runtime(tmp_path, settings=None):
    settings = settings or {}
    return Runtime(ROOT, lambda: tmp_path, lambda k, d=None: settings.get(k, d))


@pytest.mark.parametrize("value", ["1e999", "-1e999", "1.0e999999"])
def test_numeric_overflow_is_rejected(value):
    with pytest.raises(BoundaryError):
        events_from_text('{"module":"Filescan","score":' + value + '}')


@pytest.mark.parametrize("version", ["vv2", "vvv1.0.0", "vV2"])
def test_repeated_version_prefix_is_rejected(tmp_path, version):
    p = tmp_path / "input.json"
    p.write_text(json.dumps({"log_version": version, "module": "Filescan"}))
    with pytest.raises(BoundaryError):
        parse(p, R)


@pytest.mark.parametrize("field,value", [
    ("hostname", None), ("hostname", {}), ("hostname", True),
    ("scanid", []), ("scanid", True), ("scanid", 42),
])
def test_non_scalar_host_or_scan_cannot_establish_identity(tmp_path, field, value):
    e = {"hostname": "host", "scanid": "scan", "level": "Info", "module": "Filescan",
         "file": {"path": "/tmp/x", "sha256": "a"*64}}
    e[field] = value
    p = tmp_path / "input.json"
    p.write_text(json.dumps([e, e]))
    assert parse(p, R)["inventory"]["finding_count"] == 2


@pytest.mark.parametrize("pid,start", [(True, "2026-11-11T00:00:00Z"), ([], "2026-11-11T00:00:00Z"),
                                     (12, "yesterday"), (12, "2026-11-11T00:00:00")])
def test_invalid_process_identity_does_not_merge(tmp_path, pid, start):
    e = {"hostname": "host", "scanid": "scan", "level": "Info", "module": "ProcessCheck",
         "process": {"pid": pid, "start_time": start}}
    p = tmp_path / "input.json"
    p.write_text(json.dumps([e, e]))
    assert parse(p, R)["inventory"]["finding_count"] == 2


def test_distinct_whitespace_paths_remain_distinct(tmp_path):
    a = {"hostname": "host", "scanid": "scan", "level": "Info", "module": "Filescan",
         "file": {"path": "/tmp/x", "sha256": "a"*64}}
    b = {**a, "file": {"path": "/tmp/x ", "sha256": "a"*64}}
    p = tmp_path / "input.json"
    p.write_text(json.dumps([a, b]))
    assert parse(p, R)["inventory"]["finding_count"] == 2


@pytest.mark.skipif(not hasattr(os, "O_NOFOLLOW"), reason="Final-component nofollow is POSIX-specific")
def test_parser_itself_refuses_final_symlink(tmp_path):
    path = tmp_path / "input.json"
    path.symlink_to(DEMO)
    with pytest.raises(BoundaryError):
        read_stable_evidence(path)


def test_changing_evidence_is_rejected(tmp_path):
    path = tmp_path / "input.json"
    path.write_text("{}")
    stat = path.stat()
    before = SimpleNamespace(st_mode=stat.st_mode, st_size=2, st_mtime_ns=1, st_ctime_ns=1)
    after = SimpleNamespace(st_mode=stat.st_mode, st_size=2, st_mtime_ns=2, st_ctime_ns=1)
    with patch("os.fstat", side_effect=[before, after]):
        with pytest.raises(BoundaryError, match="changed during import"):
            read_stable_evidence(path)


def test_report_bundle_is_atomic_on_write_failure(tmp_path):
    r = runtime(tmp_path)
    original = r.write
    def fail_case(path, value):
        if path.name == "case.json":
            raise OSError("simulated disk failure")
        return original(path, value)
    with patch.object(r, "write", side_effect=fail_case):
        result = r.call("thor_first_assessment", {"path": str(DEMO)})
    assert not result["ok"]
    assert list((tmp_path / "reports").iterdir()) == []


def test_report_bundle_contains_all_files_when_published(tmp_path):
    result = runtime(tmp_path).call("thor_first_assessment", {"path": str(DEMO)})
    assert result["ok"]
    folders = list((tmp_path / "reports").iterdir())
    assert len(folders) == 1 and not folders[0].name.startswith(".staging-")
    assert {p.name for p in folders[0].iterdir()} == {"normalized.json", "case.json", "report.md"}


def test_final_audit_failure_does_not_claim_action_was_refused(tmp_path):
    r = runtime(tmp_path)
    with patch.object(Audit, "write", side_effect=[None, OSError("disk full")]), \
         patch.object(r, "execute", return_value={"ok": True, "profile_created": True}) as execute:
        result = r.call("soc_template_list", {})
    assert execute.call_count == 1
    assert not result["ok"] and result["operation_completed"] is True
    assert result["error_code"] == "AUDIT_FINALIZATION_FAILED"
    assert result["retry_safe"] is False
    assert result["operation_result"]["profile_created"] is True
    assert "refused" not in result["error"].lower()


def test_initial_audit_failure_prevents_action(tmp_path):
    r = runtime(tmp_path)
    with patch.object(Audit, "write", side_effect=OSError), patch.object(r, "execute") as execute:
        result = r.call("soc_template_list", {})
    execute.assert_not_called()
    assert result["execution_started"] is False and result["retry_safe"] is False


def test_execution_exception_does_not_claim_no_side_effects(tmp_path):
    r = runtime(tmp_path)
    with patch.object(r, "execute", side_effect=OSError("private details")):
        result = r.call("soc_template_list", {})
    assert result["execution_started"] is True and result["retry_safe"] is False
    assert "partial effects" in result["error"]
    assert "private details" not in json.dumps(result)


@pytest.mark.parametrize("level", ["ERROR", "unknown"])
def test_error_exports_do_not_get_low_criticality(tmp_path, level):
    p = tmp_path / "input.json"
    p.write_text(json.dumps({"level": level, "module": "Init"}))
    result = assess(parse(p, R))
    assert result["classification"] == "Inconclusive"
    assert result["criticality"] == "MEDIUM"


def test_capabilities_separates_roadmap_from_current_functions(tmp_path):
    result = runtime(tmp_path).call("soc_capabilities", {})
    assert result["ok"] and result["network_calls"] == 0
    assert result["summary"] == {"profiles": 9, "skills": 29, "technology_templates": 21, "live_remote_connectors": 0}
    assert len(result["planned_integrations"]) == 21
    assert all(x["integration_state"] == "planned" and not x["live_verified"] for x in result["planned_integrations"])
    assert not result["offensive_preview"]["enabled"]


def test_capabilities_configuration_is_not_verification(tmp_path):
    result = runtime(tmp_path, {"thor_path": "/secret/operator/path", "scan_roots": ["/private/scope"],
                                "offensive_preview_enabled": "true"}).call("soc_capabilities", {})
    assert result["local_configuration"]["thor_path_configured"]
    assert result["local_configuration"]["scanner_probed"] is False
    assert not result["offensive_preview"]["enabled"]
    assert "/secret" not in json.dumps(result) and "/private" not in json.dumps(result)


def test_suite_filter_and_unknown_technology():
    result = inventory(ROOT, lambda k, d=None: d, "cystrat-soc-suite")
    assert len(result["planned_integrations"]) == 1
    assert result["planned_integrations"][0]["name"] == "CyStrat SOC Suite"
    with pytest.raises(BoundaryError):
        inventory(ROOT, lambda k, d=None: d, "../../etc/passwd")


def test_runtime_success_envelope_consistent(tmp_path):
    assert runtime(tmp_path).call("soc_template_list", {})["ok"] is True
    assert runtime(tmp_path).call("soc_alert_triage", {"alert": {"title": "demo"}})["ok"] is True
