"""Offline tests for documentation navigation and asset checks."""

from pathlib import Path
import runpy
import json
import re
import xml.etree.ElementTree as ET

import pytest


CHECK = Path(__file__).resolve().parents[1] / "scripts/check_docs.py"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def run_check(root):
    namespace = runpy.run_path(str(CHECK))
    main = namespace["main"]
    main.__globals__["ROOT"] = root.resolve()
    return main()


@pytest.fixture
def documentation(tmp_path):
    brand = tmp_path / "assets/brand"
    brand.mkdir(parents=True)
    (brand / "README.md").write_text("# Marks\n", encoding="utf-8")
    for name in ("cystrat", "nextron", "exploit-labs"):
        (brand / f"{name}.png").write_bytes(PNG_SIGNATURE)
    return tmp_path


def test_repository_documentation():
    assert run_check(CHECK.parents[1]) == 0


def test_valid_markdown_html_and_external_targets(documentation):
    (documentation / "README.md").write_text(
        '[Brand](assets/brand/README.md#marks)\n'
        '<img src="assets/brand/cystrat.png">\n'
        '[External](https://example.invalid/not-fetched)\n'
        '[Anchor](#example)\n'
        '```text\n[Illustration](not-a-real-file)\n```\n',
        encoding="utf-8",
    )
    assert run_check(documentation) == 0


@pytest.mark.parametrize("target", ["missing.md", "../outside.md"])
def test_broken_or_escaping_target_is_refused(documentation, target):
    (documentation / "README.md").write_text(
        f"[Broken]({target})\n", encoding="utf-8"
    )
    assert run_check(documentation) == 1


def test_invalid_brand_signature_is_refused(documentation):
    (documentation / "assets/brand/cystrat.png").write_bytes(b"not a png")
    assert run_check(documentation) == 1


def test_url_encoded_file_target(documentation):
    (documentation / "with space.md").write_text("# Example\n", encoding="utf-8")
    (documentation / "README.md").write_text(
        "[Encoded](with%20space.md)\n", encoding="utf-8"
    )
    assert run_check(documentation) == 0


@pytest.mark.parametrize(
    "name", ["version", "python", "hermes", "preview", "integrations", "license"]
)
def test_badges_are_self_contained_accessible_svg(name):
    path = CHECK.parents[1] / f"assets/badges/{name}.svg"
    root = ET.parse(path).getroot()
    ns = "{http://www.w3.org/2000/svg}"
    assert root.tag == f"{ns}svg"
    assert root.attrib["role"] == "img"
    assert root.find(f"{ns}title").text
    assert root.attrib["height"] == "28"
    for element in root.iter():
        assert element.tag in {f"{ns}{tag}" for tag in ("svg", "title", "rect", "path", "g", "text")}
        assert not any(key.startswith("on") for key in element.attrib)
        assert not any("href" in key for key in element.attrib)


def test_version_badge_matches_manifest():
    repository = CHECK.parents[1]
    manifest = (repository / "plugin.yaml").read_text(encoding="utf-8")
    version = re.search(r'^version:\s*"([^"]+)"', manifest, re.MULTILINE).group(1)
    root = ET.parse(repository / "assets/badges/version.svg").getroot()
    labels = [item.text for item in root.iter("{http://www.w3.org/2000/svg}text")]
    assert version in labels


def _badge_labels(repository, name):
    """Every visible label plus the SVG title, as one lowercase-free string."""
    root = ET.parse(repository / f"assets/badges/{name}.svg").getroot()
    ns = "{http://www.w3.org/2000/svg}"
    texts = [item.text or "" for item in root.iter(f"{ns}text")]
    title = root.find(f"{ns}title")
    texts.append((title.text or "") if title is not None else "")
    return " ".join(texts)


def _manifest_field(repository, field):
    manifest = (repository / "plugin.yaml").read_text(encoding="utf-8")
    match = re.search(rf'^{field}:\s*(.+)$', manifest, re.MULTILINE)
    assert match, f"{field} missing from plugin.yaml"
    return match.group(1).strip().strip('"')


def test_license_badge_matches_manifest():
    """A badge that still says 'pending approval' contradicts a settled licence."""
    repository = CHECK.parents[1]
    licence = _manifest_field(repository, "license")
    labels = _badge_labels(repository, "license")
    assert licence in labels
    assert "pending" not in labels.lower()
    assert "proposed" not in labels.lower()


def test_hermes_badge_matches_manifest_floor():
    repository = CHECK.parents[1]
    floor = _manifest_field(repository, "requires_hermes").lstrip(">= ").strip()
    labels = _badge_labels(repository, "hermes")
    assert floor in labels, f"badge does not show the manifest floor {floor}"


def test_integrations_badge_matches_registry():
    repository = CHECK.parents[1]
    registry = json.loads((repository / "templates/registry.yaml").read_text(encoding="utf-8"))
    count = len(registry["technologies"])
    labels = _badge_labels(repository, "integrations")
    assert str(count) in labels, f"badge does not show the registry count {count}"


SECTION = (
    "## One agent. Your wider security stack.\n\n"
    "{table}\n\n"
    "## Next section\n"
)


def scaffold(root, technology):
    directory = root / "templates/mcp"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{technology.lower().replace(' ', '-')}.example.json").write_text(
        '{"status": "scaffold", "enabled": false, "technology": "%s"}' % technology,
        encoding="utf-8",
    )


def test_integration_table_matching_registry_passes(documentation):
    scaffold(documentation, "Tenable Vulnerability Management")
    (documentation / "README.md").write_text(
        SECTION.format(table="| Domain | Technologies |\n|---|---|\n| Vulnerability management | Tenable Vulnerability Management |"),
        encoding="utf-8",
    )
    assert run_check(documentation) == 0


def test_scaffold_missing_from_readme_is_refused(documentation):
    scaffold(documentation, "Qualys VMDR")
    (documentation / "README.md").write_text(
        SECTION.format(table="| Domain | Technologies |\n|---|---|\n| SIEM | Splunk |"),
        encoding="utf-8",
    )
    assert run_check(documentation) == 1


def test_soc_suite_as_peer_domain_row_is_refused(documentation):
    scaffold(documentation, "CyStrat SOC Suite")
    (documentation / "README.md").write_text(
        SECTION.format(table="| Domain | Technologies |\n|---|---|\n| SOC platform | CyStrat SOC Suite |"),
        encoding="utf-8",
    )
    assert run_check(documentation) == 1


def test_missing_integration_section_is_refused(documentation):
    scaffold(documentation, "Splunk")
    (documentation / "README.md").write_text("# Readme\n", encoding="utf-8")
    assert run_check(documentation) == 1
