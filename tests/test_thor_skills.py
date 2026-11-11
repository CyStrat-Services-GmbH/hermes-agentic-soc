"""Contracts for the THOR analysis skill suite and the generated profile SOULs.

These tests keep the skills honest: every tool, skill and reference they name
must exist, the worked example must match what the real tools return, and
every SOUL must keep its safety contract.
"""

import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from agentic_soc.runtime import Runtime
from agentic_soc.tools.templates import PROFILES
from build_assets import HAND_AUTHORED
from profile_souls import ROLES

THOR_SKILLS = sorted(HAND_AUTHORED)
EXAMPLE = ROOT / "examples/analysis/thor-multimodule.json"
MANIFEST = yaml.safe_load((ROOT / "plugin.yaml").read_text())
TOOLS = set(MANIFEST["provides_tools"])
SETTINGS = set(MANIFEST["config_schema"])
ALL_SKILLS = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}


def skill_files(name):
    return sorted((ROOT / "skills" / name).rglob("*.md"))


def frontmatter(name):
    text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---")[1]), text


def test_suite_is_complete_and_registered():
    assert len(THOR_SKILLS) == 9
    assert set(THOR_SKILLS) <= ALL_SKILLS
    assert len(ALL_SKILLS) == 36


@pytest.mark.parametrize("name", THOR_SKILLS)
def test_skill_frontmatter_and_size(name):
    meta, text = frontmatter(name)
    assert set(meta) == {"name", "description"} and meta["name"] == name
    assert 100 <= len(meta["description"]) <= 1024
    assert "Use " in meta["description"] and "not " in meta["description"].lower()
    assert len(text.splitlines()) < 500


@pytest.mark.parametrize("name", THOR_SKILLS)
def test_links_tools_and_skill_references_resolve(name):
    for file in skill_files(name):
        text = file.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if not re.match(r"https?://", target):
                assert (file.parent / target.split("#")[0]).is_file(), f"{file}: {target}"
        for tool in re.findall(r"`((?:thor|soc)_[a-z_]+)`", text):
            assert tool in TOOLS or tool in SETTINGS, f"{file}: unknown tool or setting {tool}"
        for skill in re.findall(r"agentic-soc:([a-z0-9-]+)", text):
            assert skill in ALL_SKILLS, f"{file}: unknown skill {skill}"
    for ref in HAND_AUTHORED[name]:
        assert ref in (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def test_skills_never_carry_credential_material_or_long_hex():
    for name in THOR_SKILLS:
        for file in skill_files(name):
            text = file.read_text(encoding="utf-8")
            assert not re.search(r"\b[0-9a-fA-F]{32,}\b", text), file
            assert not re.search(r"(?i)aad3b435b51404ee", text), file


def test_core_safety_rules_are_present():
    lead = (ROOT / "skills/thor-assessment/SKILL.md").read_text(encoding="utf-8")
    for phrase in ("never proves a clean host", "SHIMCache alone", "untrusted data",
                   "Tool-Erstbewertung", "Analystenbewertung", "require human approval"):
        assert phrase in lead
    lite = (ROOT / "skills/thor-lite/SKILL.md").read_text(encoding="utf-8")
    assert "no Registry, Eventlog, SHIMCache or Sigma" in lite
    ioc = (ROOT / "skills/thor-ioc-handling/SKILL.md").read_text(encoding="utf-8")
    assert "Never upload a file" in ioc and "LM/NTLM" in ioc


def test_case_output_keeps_nine_sections_in_order():
    text = (ROOT / "skills/thor-assessment/references/case-output.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## \d\. (.+)$", text, flags=re.M)
    assert headings == ["Titel", "Summary", "Assessment", "Bewertung", "Priorität",
                        "Kritikalität", "IOCs und Artefakte", "Timeline", "Maßnahmen"]


def test_worked_example_matches_real_tool_output(tmp_path):
    runtime = Runtime(ROOT, lambda: tmp_path,
                      lambda key, default=None: [str(EXAMPLE.parent)] if key == "evidence_roots" else default)
    result = runtime.call("thor_first_assessment", {"path": str(EXAMPLE)})
    assert result["ok"] and result["verdict"] == "Verdächtig" and result["priority"] == "P2"
    inv = result["inventory"]
    assert (inv["event_count"], inv["finding_count"]) == (7, 7)
    assert inv["levels"] == {"ALERT": 2, "WARNING": 2, "NOTICE": 2, "INFO": 1}
    assert inv["modules"] == {"Filescan": 2, "SHIMCache": 1, "ServiceCheck": 1, "Autoruns": 1,
                              "ProcessCheck": 1, "Init": 1}
    assert (inv["unique_files"], inv["unique_hashes"], inv["unknown_score_count"]) == (3, 2, 1)
    doc = (ROOT / "skills/thor-assessment/references/worked-example.md").read_text(encoding="utf-8")
    for row in ("| `event_count` | 7 |", "| `finding_count` | 7 |", "| `unique_files` | 3 |",
                "| `unique_hashes` | 2 |", "| `unknown_score_count` | 1 |",
                "ALERT 2, WARNING 2, NOTICE 2, INFO 1", "Verdächtig, P2"):
        assert row in doc
    # The lesson the example teaches must stay true: SHIMCache without a hash is not auto-grouped.
    import json
    events = json.loads(Path(result["normalized"]).read_text())["events"]
    by_module = {e["module"]: e for e in events}
    assert by_module["SHIMCache"]["file"] == events[0]["file"]
    assert by_module["SHIMCache"]["finding_id"] != events[0]["finding_id"]
    assert "[user-" in events[0]["file"]  # C:\Users\Public is pseudonymised like a profile


@pytest.mark.parametrize("name", sorted(PROFILES))
def test_soul_contract(name):
    soul = (ROOT / "templates/profiles" / name / "SOUL.md").read_text(encoding="utf-8")
    shipped = (ROOT / "templates/profiles" / name / "skills.txt").read_text().split()
    assert soul.startswith(f"# {name} · ")
    for section in ("## Identity", "## How you work", "## Decision standards", "## What you deliver",
                    "## When to escalate", "## Boundaries", "## Communication", "## Skills and workflow"):
        assert section in soul
    assert shipped == [f"agentic-soc:{s}" for s in ROLES[name]["skills"]]
    for skill in ROLES[name]["skills"]:
        assert f"`agentic-soc:{skill}`" in soul and skill in ALL_SKILLS
    for tool in re.findall(r"`((?:thor|soc)_[a-z_]+)`", soul):
        assert tool in TOOLS or tool in SETTINGS
    for phrase in ("untrusted data", "Confirmed", "not a sandbox", "LM/NTLM", "request, not consent"):
        assert phrase in soul
    if PROFILES[name][0] == "scaffold":
        assert "offensive_preview_enabled" in soul and "soc_research_plan" in soul
        assert "exploit labs" in soul and "built by CyStrat Services × Nextron Systems" not in soul
    else:
        assert "built by CyStrat Services × Nextron Systems" in soul and "exploit labs" not in soul


def test_dfir_profile_ships_the_whole_thor_suite():
    assert set(THOR_SKILLS) <= set(ROLES["dfir-compromise-assessment"]["skills"])
