"""Offline tests for documentation navigation and asset checks."""

from pathlib import Path
import runpy

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
