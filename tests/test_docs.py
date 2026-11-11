"""Offline tests for documentation navigation and asset checks."""

from pathlib import Path
import runpy
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
