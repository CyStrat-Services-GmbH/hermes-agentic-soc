"""Prepare a catalog draft; never publishes a private repository or submits a PR."""

import argparse
import json
import re
import subprocess
import tomllib
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    if dirty:
        raise SystemExit("Refusing a dirty source tree; commit reviewed code before pinning.")
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise SystemExit("HEAD is not a full 40-character Git commit SHA.")
    repo = "https://github.com/CyStrat-Services-GmbH/hermes-agentic-soc"
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    entry = {
        "name": "agentic-soc", "repo": repo, "sha": sha,
        "description": "Evidence-first SOC specialists and deterministic THOR JSON triage; THOR is installed separately.",
        "maintainer": "CyStrat-Services-GmbH", "tier": "community", "category": "tools",
        "requires_hermes": ">=0.23.1", "version": version,
        "docs_url": repo, "readme": True, "platforms": [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # JSON is YAML 1.2; keeps all versions and SHA explicitly quoted.
    args.output.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {args.output} at {sha}.")
    print("PRIVATE REPOSITORY: do not submit until the owner explicitly approves public visibility, the license and the exact commit.")


if __name__ == "__main__":
    main()
