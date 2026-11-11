"""Regression tests derived from the independent second-pass code review."""

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_soc.api import policy
from agentic_soc.audit import Audit
from agentic_soc.runtime import Runtime
from agentic_soc.scoring.thor_first_assessment import assess, markdown, timeline_rows
from agentic_soc.security import BoundaryError, Redactor, check_scope, contained
from agentic_soc.tools.thor import events_from_text, parse

ROOT = Path(__file__).resolve().parents[1]
R = Redactor(b"x" * 32)


def parse_events(tmp_path, events):
    path = tmp_path / "input.json"
    path.write_text(json.dumps(events), encoding="utf-8")
    return parse(path, R)


def test_approval_contains_target_and_content_bound_key():
    a = policy("thor_lite_scan", {"target": "/approved/a", "execute": True})
    b = policy("thor_lite_scan", {"target": "/approved/b", "execute": True})
    c = policy("thor_lite_scan", {"execute": True, "target": "/approved/a"})
    assert "/approved/a" in a["message"]
    assert a["rule_key"] != b["rule_key"]
    assert a["rule_key"] == c["rule_key"]


@pytest.mark.parametrize("version", ["3", "v3.0.0", "4", "v99.1.0", "v2x", "latest", "v2.0.0-beta"])
def test_unknown_versions_refused(tmp_path, version):
    with pytest.raises(BoundaryError):
        parse_events(tmp_path, [{"log_version": version, "module": "Filescan", "level": "Info"}])


@pytest.mark.parametrize("text", [
    '{"level":"Info","level":"Alert"}',
    '{"events":[{"level":"Info"}],"findings":[{"level":"Alert"}]}',
    '{"level":"Alert","score":NaN}',
    '{"level":"Alert","score":Infinity}',
    '{"level":"Alert","score":-Infinity}',
])
def test_ambiguous_json_refused(text):
    with pytest.raises(BoundaryError):
        events_from_text(text)


def test_case_colliding_fields_refused(tmp_path):
    with pytest.raises(BoundaryError):
        parse_events(tmp_path, [{"level": "Info", "Level": "Alert"}])


def test_deep_json_refused():
    with pytest.raises(BoundaryError):
        events_from_text("[" * 2000 + "]" * 2000)


@pytest.mark.parametrize("missing", ["hostname", "scanid", "sha256"])
def test_missing_identity_prevents_overcorrelation(tmp_path, missing):
    event = {"hostname": "A", "scanid": "S", "level": "Warning", "module": "Filescan",
             "file": {"path": "/tmp/x", "sha256": "a" * 64}}
    if missing == "sha256":
        del event["file"]["sha256"]
    else:
        del event[missing]
    data = parse_events(tmp_path, [event, event])
    assert data["inventory"]["finding_count"] == 2


def test_pid_reuse_is_not_identity(tmp_path):
    event = {"hostname": "A", "scanid": "S", "level": "Warning", "module": "ProcessCheck",
             "process": {"pid": 42, "name": "test"}}
    assert parse_events(tmp_path, [event, event])["inventory"]["finding_count"] == 2
    event["process"]["start_time"] = "2026-11-11T00:00:00Z"
    assert parse_events(tmp_path, [event, event])["inventory"]["finding_count"] == 1


def test_record_channels_are_distinct(tmp_path):
    a = {"hostname": "A", "scanid": "S", "level": "Info", "module": "Eventlog",
         "eventid": 1, "recordid": 10, "channel": "System"}
    b = {**a, "channel": "Security"}
    assert parse_events(tmp_path, [a, a, b])["inventory"]["finding_count"] == 2


def test_bearer_url_ansi_bidi_redaction():
    text = "Bearer secret-token-value https://user:pass@private.test \x1b[31mALERT\x1b[0m \u202eevil"
    result = R.text(text)
    assert "secret-token-value" not in result and "user:pass" not in result
    assert "\x1b" not in result and "\u202e" not in result
    assert "ALERT" in result


def test_markdown_evidence_inert_and_case_specific(tmp_path):
    data = parse_events(tmp_path, [{"level": "Alert", "module": "Filescan\n## injected",
                                   "message": "<script>alert(1)</script> [bait](https://evil.test)",
                                   "reasons": [{"name": "custom_demo_rule"}],
                                   "file": {"path": "x`[bait](https://evil.test)"}}])
    report = markdown(assess(data), data)
    assert "\n## injected" not in report
    assert "<script>" not in report and "[bait](" not in report
    assert "Konkrete Beobachtungen" in report and "custom\\_demo\\_rule" in report


def test_timeline_utc_order_and_invalid_values(tmp_path):
    data = parse_events(tmp_path, [
        {"level": "Info", "module": "Filescan", "timestamps": {"created": "2026-11-11T08:00:00+02:00"}},
        {"level": "Info", "module": "Filescan", "timestamps": {"created": "2026-11-11T07:00:00Z"}},
        {"level": "Info", "module": "Filescan", "timestamps": {"created": "2026-11-11T01:00:00"}},
        {"level": "Info", "module": "Filescan", "timestamps": {"created": "yesterday"}},
    ])
    rows, rejected = timeline_rows(data["events"])
    assert len(rows) == 2 and rejected == 2
    assert rows[0][0].hour == 6 and rows[1][0].hour == 7
    assert "2 Zeitangaben" in markdown(assess(data), data)


@pytest.mark.parametrize("target", ["*.lab", "host?", "[host]", "", "host\nbad"])
def test_literal_wildcards_also_refused(target):
    now = datetime.now(timezone.utc)
    scope = {"targets": [target], "authorization_ref": "AUTH-12345",
             "valid_from": (now - timedelta(hours=1)).isoformat(),
             "valid_until": (now + timedelta(hours=1)).isoformat(),
             "rules_of_engagement": "Only isolated lab research planning.",
             "allowed_activities": ["research"]}
    with pytest.raises(BoundaryError):
        check_scope(scope, target)


def test_relative_operator_roots_refused(tmp_path):
    p = tmp_path / "input.json"
    p.write_text("{}")
    with pytest.raises(BoundaryError):
        contained(p, [Path(".")])


def test_internal_state_cannot_be_imported(tmp_path):
    for name in ("pseudonym.salt", "audit.jsonl"):
        p = tmp_path / name
        p.write_text("{}")
        with pytest.raises(BoundaryError):
            contained(p, [tmp_path])


def test_runtime_validates_direct_calls(tmp_path):
    runtime = Runtime(ROOT, lambda: tmp_path, lambda k, d=None: d)
    result = runtime.call("thor_lite_scan", {"target": "/tmp", "execute": "false"})
    assert not result["ok"]
    assert "schema" in result["error"]


def test_audit_unavailable_blocks_before_execute(tmp_path):
    runtime = Runtime(ROOT, lambda: tmp_path, lambda k, d=None: d)
    with patch.object(Audit, "write", side_effect=OSError("disk full")), patch.object(runtime, "execute") as execute:
        result = runtime.call("soc_template_list", {})
        assert not result["ok"] and "Audit unavailable" in result["error"]
        execute.assert_not_called()


def test_symlinked_reports_refused(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (data / "reports").symlink_to(outside, target_is_directory=True)
    runtime = Runtime(ROOT, lambda: data, lambda k, d=None: d)
    result = runtime.call("thor_first_assessment", {"path": str(ROOT / "examples/demo/thor.json")})
    assert not result["ok"] and not list(outside.iterdir())


def test_symlinked_salt_refused(tmp_path):
    target = tmp_path / "outside"
    target.write_bytes(b"x" * 32)
    (tmp_path / "pseudonym.salt").symlink_to(target)
    runtime = Runtime(ROOT, lambda: tmp_path, lambda k, d=None: d)
    with pytest.raises(BoundaryError):
        runtime.redactor()


def test_symlinked_audit_refused(tmp_path):
    outside = tmp_path / "outside"
    outside.write_text("original")
    (tmp_path / "audit.jsonl").symlink_to(outside)
    with pytest.raises(OSError):
        Audit(tmp_path).write("test", "started")
    assert outside.read_text() == "original"


def test_concurrent_salt_initialization(tmp_path):
    runtime = Runtime(ROOT, lambda: tmp_path, lambda k, d=None: d)
    with ThreadPoolExecutor(max_workers=8) as pool:
        tokens = list(pool.map(lambda _: runtime.redactor().token("same"), range(32)))
    assert len(set(tokens)) == 1


@pytest.mark.skipif(os.name != "posix", reason="POSIX permissions only")
def test_reports_owner_only(tmp_path):
    data = tmp_path / "data"
    data.mkdir(mode=0o755)
    runtime = Runtime(ROOT, lambda: data, lambda k, d=None: d)
    result = runtime.call("thor_first_assessment", {"path": str(ROOT / "examples/demo/thor.json")})
    assert result["ok"]
    assert data.stat().st_mode & 0o777 == 0o700
    for name in ("normalized", "case_json", "report"):
        assert Path(result[name]).stat().st_mode & 0o777 == 0o600


def test_size_bound_enforced_by_parser_itself(tmp_path):
    path = tmp_path / "large.json"
    path.write_bytes(b"01234567890")
    with patch("agentic_soc.tools.thor.MAX_BYTES", 10):
        with pytest.raises(BoundaryError):
            parse(path, R)


def test_offline_cli_demo(tmp_path):
    result = subprocess.run([sys.executable, "-m", "agentic_soc", "demo", "--output", str(tmp_path / "out")],
                            cwd=ROOT, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["inventory"]["event_count"] == 4
    assert parsed["inventory"]["finding_count"] == 3
    assert parsed["execution_mode"] == "synthetic_demo_no_scan"


def test_cli_has_no_scan_execution_command():
    result = subprocess.run([sys.executable, "-m", "agentic_soc", "scan", "--execute"],
                            cwd=ROOT, capture_output=True, text=True, timeout=20)
    assert result.returncode != 0


def valid_scope():
    now = datetime.now(timezone.utc)
    return {"targets": ["lab.internal"], "authorization_ref": "AUTH-12345",
            "valid_from": (now - timedelta(hours=1)).isoformat(),
            "valid_until": (now + timedelta(hours=1)).isoformat(),
            "rules_of_engagement": "Isolated lab planning only, no production activity.",
            "allowed_activities": ["research"]}


def test_preview_default_closed_even_with_valid_scope(tmp_path):
    runtime = Runtime(ROOT, lambda: tmp_path, lambda k, d=None: d)
    result = runtime.call("soc_research_plan", {"scope": valid_scope(), "target": "lab.internal"})
    assert not result["ok"] and "disabled gated preview" in result["error"]
    profiles = runtime.call("soc_template_list", {})["profiles"]
    offensive = [p for p in profiles if p["scope_required"]]
    assert len(offensive) == 3
    assert all(p["availability"] == "gated_preview" and p["contributor"] == "exploit labs" for p in offensive)


@pytest.mark.parametrize("enabled", ["true", 1, "yes", False, None])
def test_preview_requires_real_boolean_optin(tmp_path, enabled):
    runtime = Runtime(ROOT, lambda: tmp_path, lambda k, d=None: enabled if k == "offensive_preview_enabled" else d)
    result = runtime.call("soc_research_plan", {"scope": valid_scope(), "target": "lab.internal"})
    assert not result["ok"]


def test_preview_optin_still_scope_gated_no_execution(tmp_path):
    runtime = Runtime(ROOT, lambda: tmp_path, lambda k, d=None: True if k == "offensive_preview_enabled" else d)
    good = runtime.call("soc_research_plan", {"scope": valid_scope(), "target": "lab.internal"})
    assert good["execution"] == "not_supported" and good["network_calls"] == 0
    bad = runtime.call("soc_research_plan", {"scope": valid_scope(), "target": "outside.internal"})
    assert not bad["ok"]


def test_model_cannot_enable_preview_in_arguments(tmp_path):
    runtime = Runtime(ROOT, lambda: tmp_path, lambda k, d=None: d)
    result = runtime.call("soc_research_plan", {"scope": valid_scope(), "target": "lab.internal", "preview_enabled": True})
    assert not result["ok"]


def test_suite_skill_and_mcp_are_explicit_scaffolds():
    registry = json.loads((ROOT / "templates/registry.yaml").read_text())
    suite = next(x for x in registry["technologies"] if x["id"] == "cystrat-soc-suite")
    assert suite["status"] == "scaffold" and suite["live_connector"] is False
    contract = json.loads((ROOT / "templates/mcp/cystrat-soc-suite.contract.json").read_text())
    assert contract["enabled"] is False and contract["endpoint"] is None
    assert "not_implemented" in contract["status"]
    skill = (ROOT / "skills/tech-cystrat-soc-suite/SKILL.md").read_text()
    assert "tenant_id" in skill and "local-model" in skill and "not callable tools" in skill


def test_release_versions_agree():
    import tomllib
    from agentic_soc import __version__
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert project["project"]["version"] == __version__ == "0.1.4"
    assert f'version: "{__version__}"' in (ROOT / "plugin.yaml").read_text()
