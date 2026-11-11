"""Check local documentation targets without network calls or dependencies.

This intentionally checks file targets, not external URL availability or
renderer-specific heading anchors. Exit nonzero for broken links or missing
brand panels, keeping the check usable offline and in CI.
"""

from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_LINK = re.compile(r"\b(?:src|href)=[\"']([^\"']+)[\"']")
INTEGRATION_SECTION = re.compile(
    r"^## One agent\. Your wider security stack\.\n(.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
PEER_PLATFORM_ROW = re.compile(r"^\|\s*SOC platform\s*\|", re.MULTILINE)


def integration_gaps(root: Path) -> list[str]:
    """Keep the README integration table in sync with the shipped scaffolds.

    Every technology template is an entry in the published table, and the
    CyStrat SOC Suite is published as a cross-domain platform rather than as
    one more domain row. A table that silently lags the registry understates
    the shipped scope.
    """
    templates = sorted((root / "templates/mcp").glob("*.example.json"))
    readme = root / "README.md"
    if not templates or not readme.exists():
        return []
    match = INTEGRATION_SECTION.search(readme.read_text(encoding="utf-8"))
    if match is None:
        return ["README.md: section 'One agent. Your wider security stack.' is missing"]
    section = match.group(1)
    gaps = []
    for path in templates:
        technology = json.loads(path.read_text(encoding="utf-8")).get("technology")
        if technology and technology not in section:
            gaps.append(f"README.md: scaffold not listed in the integration table: {technology}")
    if PEER_PLATFORM_ROW.search(section):
        gaps.append(
            "README.md: CyStrat SOC Suite spans all domains; it must not be a peer 'SOC platform' row"
        )
    return gaps


def main() -> int:
    files = sorted({
        *ROOT.glob("*.md"),
        *ROOT.joinpath("docs").glob("*.md"),
        ROOT / "assets/brand/README.md",
    })
    scaffolds = sorted((ROOT / "templates/mcp").glob("*.example.json"))
    failures = []
    checked = 0
    for file in files:
        text = file.read_text(encoding="utf-8")
        # Avoid interpreting illustrative command/code text as navigation.
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for target in [*INLINE_LINK.findall(text), *HTML_LINK.findall(text)]:
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            checked += 1
            resolved = (file.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                failures.append(f"{file.relative_to(ROOT)}: {target}")
    for name in ("cystrat", "nextron", "exploit-labs"):
        panel = ROOT / f"assets/brand/{name}.png"
        if not panel.exists() or panel.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            failures.append(f"Missing or invalid brand PNG: {panel.name}")
    failures.extend(integration_gaps(ROOT))
    if failures:
        print("\n".join(f"FAIL {item}" for item in failures))
        return 1
    print(f"PASS: {len(files)} Markdown files, {checked} local targets, {len(scaffolds)} integration entries, 3 brand PNGs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
