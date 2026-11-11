"""Check local documentation targets without network calls or dependencies.

This intentionally checks file targets, not external URL availability or
renderer-specific heading anchors. Exit nonzero for broken links or missing
brand panels, keeping the check usable offline and in CI.
"""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_LINK = re.compile(r"\b(?:src|href)=[\"']([^\"']+)[\"']")


def main() -> int:
    files = sorted({
        *ROOT.glob("*.md"),
        *ROOT.joinpath("docs").glob("*.md"),
        ROOT / "assets/brand/README.md",
    })
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
    if failures:
        print("\n".join(f"FAIL {item}" for item in failures))
        return 1
    print(f"PASS: {len(files)} Markdown files, {checked} local targets, 3 brand PNGs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
