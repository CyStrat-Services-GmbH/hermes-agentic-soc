import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agentic_soc.api import BY_NAME, TOOLS, policy, validate
from agentic_soc.runtime import Runtime
from agentic_soc.security import BoundaryError, Redactor, check_scope, contained
from agentic_soc.tools import templates, thor
from agentic_soc.scoring.thor_first_assessment import assess, markdown

DEMO = ROOT / "examples/demo/thor.json"


@pytest.fixture
def redactor():
    return Redactor(b"0" * 32)


@pytest.fixture
def parsed(redactor):
    return thor.parse(DEMO, redactor)


@pytest.fixture
def scope():
    now = datetime.now(timezone.utc)
    return {"targets": ["lab.internal"], "authorization_ref": "ROE-2026-001",
            "valid_from": (now - timedelta(hours=1)).isoformat(),
            "valid_until": (now + timedelta(hours=1)).isoformat(),
            "rules_of_engagement": "Isolated lab planning only, no production contact.",
            "allowed_activities": ["research", "emulation-planning"]}


@pytest.mark.parametrize("score,expected", [
    (None, "UNKNOWN"), (0, "INFO"), (39, "INFO"), (40, "NOTICE"),
    (59, "NOTICE"), (60, "WARNING"), (80, "WARNING"), (81, "ALERT"), (180, "ALERT")])
def test_default_bands(score, expected):
    assert thor.band(score) == expected


@pytest.mark.parametrize("value", [True, False, "NaN", float("inf"), -1, "invalid", [], {}])
def test_invalid_scores_unknown(value):
    assert thor.score_number(value) is None


def test_exact_inventory_and_correlation(parsed):
    i = parsed["inventory"]
    assert i["event_count"] == 4
    assert i["finding_count"] == 3
    assert i["levels"] == {"ALERT": 1, "WARNING": 1, "NOTICE": 1, "INFO": 1}
    assert i["modules"] == {"Filescan": 2, "ProcessCheck": 1, "Init": 1}
    assert i["unknown_score_count"] == 1
    assert i["coverage_verified"] is False


@pytest.mark.parametrize("suffix,content", [
    ("json", '[{"Level":"Warning","Module":"Filescan","Message":"test","Score":65}]'),
    ("jsonl", '{"level":"info","module":"Init","message":"start"}\n{"level":"alert","module":"Filescan","score":90}\n'),
    ("json", '{"events":[{"level":"notice","module":"Filescan","score":40}]}'),
    ("json", '{"findings":[{"Level":"Notice","Module":"Filescan","Details":{"score":40}}]}'),
    ("json", '{"level":"info","module":"Init","message":"one event"}'),
])
def test_supported_encodings(tmp_path, redactor, suffix, content):
    p = tmp_path / f"input.{suffix}"
    p.write_text(content)
    assert thor.parse(p, redactor)["inventory"]["event_count"] >= 1


@pytest.mark.parametrize("content", ["", "[]", "{}", "null", "not json", '{"level":"info"}\nmalformed',
                                       '{"log_version":"v3.0.0","level":"info","module":"Init"}',
                                       '{"type":"THOR assessment","score":95}'])
def test_bad_or_unsupported_input_refused(tmp_path, redactor, content):
    p = tmp_path / "input.json"
    p.write_text(content)
    with pytest.raises(BoundaryError):
        thor.parse(p, redactor)


def test_reason_scores_not_summed(tmp_path, redactor):
    p = tmp_path / "input.json"
    p.write_text(json.dumps({"module": "Filescan", "level": "Warning", "reasons": [{"score": 90}, {"score": 90}]}))
    e = thor.parse(p, redactor)["events"][0]
    assert e["score"] is None
    assert e["level"] == "WARNING"


def test_export_level_overrides_custom_threshold(tmp_path, redactor):
    p = tmp_path / "input.json"
    p.write_text(json.dumps({"module": "Filescan", "level": "Notice", "score": 90}))
    e = thor.parse(p, redactor)["events"][0]
    assert e["score_band"] == "ALERT"
    assert e["level"] == "NOTICE"


def test_same_path_different_host_scan_or_hash_not_merged(tmp_path, redactor):
    base = {"module": "Filescan", "level": "alert", "hostname": "A", "scanid": "1",
            "file": {"path": "/tmp/a", "sha256": "a" * 64}}
    b = {**base, "hostname": "B"}
    c = {**base, "scanid": "2"}
    d = {**base, "file": {"path": "/tmp/a", "sha256": "b" * 64}}
    p = tmp_path / "input.json"
    p.write_text(json.dumps([base, b, c, d]))
    assert thor.parse(p, redactor)["inventory"]["finding_count"] == 4


def test_redaction_and_credential_material(tmp_path, redactor):
    sensitive = "b" * 32
    e = {"hostname": "private-host", "module": "Filescan", "level": "alert",
         "message": f"SAM dump NTLM={sensitive} user@example.org 192.0.2.1",
         "firstbytes": sensitive, "file": {"path": r"C:\Users\Alice\dump.sam", "md5": sensitive},
         "reasons": [{"name": "demo", "matched": sensitive}]}
    p = tmp_path / "input.json"
    p.write_text(json.dumps(e))
    result = json.dumps(thor.parse(p, redactor))
    for raw in (sensitive, "private-host", "Alice", "user@example.org", "192.0.2.1"):
        assert raw not in result
    assert thor.parse(p, redactor)["events"][0]["hashes"] == {}


def test_hashes_only_from_typed_artifacts(parsed):
    assert parsed["events"][0]["hashes"]["sha256"] == "a" * 64
    assert parsed["events"][0]["attack"] == []


def test_case_schema_and_mandatory_sections(parsed):
    case = assess(parsed)
    jsonschema.validate(case, json.loads((ROOT / "agentic_soc/schemas/case.json").read_text()))
    for e in parsed["events"]:
        jsonschema.validate(e, json.loads((ROOT / "agentic_soc/schemas/finding.json").read_text()))
    text = markdown(case, parsed)
    required = ["# Titel", "## Summary", "## Assessment", "## Bewertung", "## Priorität",
                "## Kritikalität", "## IOCs und Artefakte", "## Timeline", "## Maßnahmen"]
    positions = [text.index(x) for x in required]
    assert positions == sorted(positions)
    assert case["classification"] == "Suspicious – Further Investigation Required"
    assert case["ticket_draft"]["writes_performed"] is False
    assert "2026-11-11T08:00" not in text  # Detection time never masquerades as attack activity.


def test_no_alerts_does_not_mean_clean(tmp_path, redactor):
    p = tmp_path / "input.json"
    p.write_text('{"level":"info","module":"Init","message":"start"}')
    case = assess(thor.parse(p, redactor))
    assert case["classification"] == "Inconclusive"
    assert case["verdict"] != "Unauffällig"


def test_scope_valid(scope):
    assert check_scope(scope, "lab.internal")["authorization_verified"] is False


@pytest.mark.parametrize("change", [
    {"authorization_ref": ""}, {"valid_until": "2000-01-01T00:00:00Z"},
    {"valid_from": "2099-01-01T00:00:00Z"}, {"valid_from": "2026-01-01"},
    {"rules_of_engagement": ""}, {"allowed_activities": ["exploit"]},
    {"allowed_activities": []}, {"targets": ["*.internal"]},
])
def test_scope_denials(scope, change):
    scope.update(change)
    with pytest.raises(BoundaryError):
        check_scope(scope, "lab.internal")


def test_scope_missing():
    with pytest.raises(BoundaryError):
        check_scope({}, "lab.internal")


def test_containment_symlink_traversal(tmp_path):
    root = tmp_path / "allowed"
    root.mkdir()
    secret = tmp_path / "elsewhere.json"
    secret.write_text("{}")
    (root / "link.json").symlink_to(secret)
    with pytest.raises(BoundaryError):
        contained(root / "link.json", [root])


@pytest.mark.parametrize("name", [".env", "auth.json", "credentials", "config.yaml"])
def test_credentials_never_imported(tmp_path, name):
    p = tmp_path / name
    p.write_text("{}")
    with pytest.raises(BoundaryError):
        contained(p, [tmp_path])


def test_schema_guards_and_host_approval():
    assert policy("terminal", {}) is None
    assert policy("thor_lite_scan", {"target": "/tmp", "execute": True})["action"] == "approve"
    assert policy("soc_template_install", {"name": "soc-a", "template": "soc-l1-triage", "execute": True})["action"] == "approve"
    assert policy("thor_lite_scan", {"target": "/tmp", "execute": False}) is None
    assert policy("thor_lite_scan", {"target": "/tmp", "execute": "false"})["action"] == "block"
    assert policy("thor_parse", {"path": "/a", "command": "echo anything"})["action"] == "block"
    assert policy("thor_parse", None)["action"] == "block"


def test_research_profiles_scope_gated(tmp_path):
    with pytest.raises(BoundaryError):
        templates.install(ROOT, "red-team-planner", "soc-lab")
    assert templates.install(ROOT, "soc-l1-triage", "soc-l1")["dry_run"]


def test_profile_creation_requires_host_home():
    with pytest.raises(BoundaryError):
        templates.install(ROOT, "soc-l1-triage", "soc-unit", execute=True)


def test_profile_create_fixed_cli_and_profile_context(tmp_path):
    home = tmp_path / "hermes"
    destination = home / "profiles" / "soc-unit"
    destination.mkdir(parents=True)
    (destination / "SOUL.md").write_text("Hermes fresh default")
    responses = [SimpleNamespace(returncode=0),
                 SimpleNamespace(returncode=0, stdout=f"Profile: soc-unit\nPath:    {destination}\n".encode())]
    with patch("shutil.which", return_value="/usr/local/bin/hermes"), patch("subprocess.run", side_effect=responses) as run:
        result = templates.install(ROOT, "dfir-compromise-assessment", "soc-unit", execute=True, profile_home=home)
        assert result["ok"] and result["credential_isolation"] is False
        argv = run.call_args_list[0].args[0]
        assert "--no-credentials" in argv and "--no-alias" in argv and "--no-skills" in argv
        assert run.call_args_list[0].kwargs["env"]["HERMES_HOME"] == str(home)
        assert (destination / "SOUL.hermes-default.md").read_text() == "Hermes fresh default"
        assert "dfir-compromise-assessment" in (destination / "SOUL.md").read_text()
        assert len(list((destination / "skills/agentic-soc").glob("*/SKILL.md"))) == 29


def test_runtime_audit_and_report_files(tmp_path):
    runtime = Runtime(ROOT, lambda: tmp_path, lambda k, d=None: d)
    result = runtime.call("thor_first_assessment", {"path": str(DEMO)})
    assert result["ok"]
    assert Path(result["report"]).is_file()
    assert json.loads(Path(result["case_json"]).read_text())["inventory"]["event_count"] == 4
    denied = runtime.call("thor_parse", {"path": "/etc/passwd"})
    assert not denied["ok"]
    records = [json.loads(x) for x in (tmp_path / "audit.jsonl").read_text().splitlines()]
    assert [x["status"] for x in records] == ["started", "completed", "started", "rejected"]
    assert "/etc/passwd" not in (tmp_path / "audit.jsonl").read_text()


def test_no_shell_or_secret_inheritance():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "nope", "HERMES_YOLO": "1", "PYTHONPATH": "/bad"}):
        env = thor.subprocess_env()
        assert not {"OPENAI_API_KEY", "HERMES_YOLO", "PYTHONPATH"} & env.keys()


def scan_setup(tmp_path):
    exe = tmp_path / "scanner"
    exe.write_text("# fake; never actually executed by this unit test\n")
    exe.chmod(0o700)
    target = tmp_path / "target"
    target.mkdir()
    help_output = b"--jsonfile --jsonv2 --rebase-dir --suppresspi --path --module --nolog --nocsv"
    return exe, target, help_output


def test_scan_missing_no_download(tmp_path):
    r = thor.scan("", str(tmp_path), [], tmp_path / "data")
    assert not r["ok"] and "nextron-systems.com" in r["download"]


def test_scan_dry_run_and_exact_flags(tmp_path):
    exe, target, help_output = scan_setup(tmp_path)
    with patch("subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=help_output)) as run:
        result = thor.scan(str(exe), str(target), [target], tmp_path / "data")
        assert result["dry_run"] and run.call_count == 1
        assert run.call_args.args[0] == [str(exe), "--help"]
    with patch("subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=b"--jsonfile-unsafe")):
        with pytest.raises(BoundaryError):
            thor.scan(str(exe), str(target), [target], tmp_path / "data")


def test_scan_timeout_is_incomplete(tmp_path):
    exe, target, help_output = scan_setup(tmp_path)
    with patch("subprocess.run", side_effect=[SimpleNamespace(returncode=0, stdout=help_output),
                                             subprocess.TimeoutExpired("thor", 10)]):
        result = thor.scan(str(exe), str(target), [target], tmp_path / "data", execute=True)
        assert result["timed_out"] and not result["ok"]


def test_scan_file_only_scope_and_suppressed_outputs(tmp_path):
    exe, target, help_output = scan_setup(tmp_path)
    with patch("subprocess.run", side_effect=[SimpleNamespace(returncode=0, stdout=help_output),
                                             SimpleNamespace(returncode=0)]) as run:
        result = thor.scan(str(exe), str(target), [target], tmp_path / "data", execute=True)
        argv = run.call_args.args[0]
        assert argv[1:3] == ["--module", "FileScan"]
        assert "--suppresspi" in argv and "--nolog" in argv and "--nocsv" in argv
        assert not result["ok"]  # zero exit without JSON is not a completed scan.


def test_every_template_skill_and_registry_complete():
    listing = templates.list_templates()["profiles"]
    schema = json.loads((ROOT / "agentic_soc/schemas/profile-template.json").read_text())
    for profile in listing:
        jsonschema.validate(profile, schema)
        folder = ROOT / "templates/profiles" / profile["id"]
        for filename in ("SOUL.md", "config.example.yaml", "skills.txt", "mcp.example.json", "README.md"):
            assert (folder / filename).is_file()
        for name in (folder / "skills.txt").read_text().splitlines():
            assert (ROOT / "skills" / name.split(":")[1] / "SKILL.md").is_file()
    registry = yaml.safe_load((ROOT / "templates/registry.yaml").read_text())
    assert len(registry["technologies"]) == 21
    for tech in registry["technologies"]:
        assert tech["status"] == "scaffold" and tech["live_connector"] is False
        mcp = json.loads((ROOT / "templates" / tech["mcp"]["template"]).read_text())
        assert mcp["enabled"] is False and mcp["mcp_servers"] == {}
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        text = skill.read_text()
        metadata = yaml.safe_load(text.split("---")[1])
        assert metadata["name"] == skill.parent.name
        assert 1 <= len(metadata["description"]) <= 1024


def test_manifest_matches_actual_registration():
    spec = importlib.util.spec_from_file_location("soc_test_plugin", ROOT / "__init__.py",
                                                 submodule_search_locations=[str(ROOT)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    class Context:
        def __init__(self):
            self.tools, self.hooks, self.commands, self.skills = {}, {}, {}, {}
        def get_config(self, key, default=None):
            return default
        def register_tool(self, **kwargs):
            self.tools[kwargs["name"]] = kwargs
        def register_hook(self, name, callback):
            self.hooks[name] = callback
        def register_command(self, name, handler, description):
            self.commands[name] = handler
        def register_skill(self, name, path):
            self.skills[name] = path
    context = Context()
    module.register(context)
    manifest = yaml.safe_load((ROOT / "plugin.yaml").read_text())
    assert set(context.tools) == set(manifest["provides_tools"])
    assert set(context.hooks) == set(manifest["provides_hooks"])
    assert len(context.skills) == 29
    assert set(context.commands) == {"soc-templates", "thor-scan", "thor-assess"}
    assert "preview-only" in context.commands["thor-scan"]('{"target":"/tmp","execute":true}')
    assert "preview-only" in context.commands["thor-scan"]('{"target":"/tmp","execute":"false"}')
    for tool in context.tools.values():
        jsonschema.Draft202012Validator.check_schema(tool["schema"]["parameters"])
