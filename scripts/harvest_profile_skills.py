#!/usr/bin/env python3
"""Compare a profile's copied skill tree with the repository and harvest differences.

The repository is the source of truth for skills; a profile's ``skills/agentic-soc``
directory is a snapshot written once at install time (``shutil.copytree``) that no
plugin update refreshes. This script answers two questions without guessing:

* what drifted between a profile snapshot and ``skills/``?
* can the profile's version be taken over into a working tree, file by file?

Dry run is the default. ``--write`` copies only from the profile into the repository
and never touches the profile; it refuses to run on a dirty tree unless ``--force``
is given, so a harvest is always reviewable as a plain ``git diff``.

Standard library only, like the rest of the runtime.

Exit codes: 0 = no drift, 1 = drift found (report mode), 2 = usage or safety refusal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__", ".git"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree(root: Path) -> dict[str, str]:
    """Relative POSIX path -> sha256 for every file below *root*."""
    out: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        out[path.relative_to(root).as_posix()] = _hash(path)
    return out


def _skill_of(rel: str) -> str:
    return rel.split("/", 1)[0]


def compare(repo_skills: Path, profile_skills: Path, only: set[str]) -> dict[str, dict]:
    """Classify every file that either side has, restricted to *only* when given."""
    repo = _tree(repo_skills)
    prof = _tree(profile_skills)
    rows: dict[str, dict] = {}
    for rel in sorted(set(repo) | set(prof)):
        if only and _skill_of(rel) not in only:
            continue
        r, p = repo.get(rel), prof.get(rel)
        if r == p:
            continue
        rows[rel] = {
            "file": rel,
            "skill": _skill_of(rel),
            "state": "profile-only" if r is None else "repo-only" if p is None else "modified",
            "repo_sha256": r,
            "profile_sha256": p,
        }
    return rows


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args], capture_output=True, text=True, check=False
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report or harvest drift between a profile's skill snapshot and skills/.",
    )
    parser.add_argument("--repo", type=Path, default=REPO_ROOT,
                        help="repository root (default: this script's repository)")
    parser.add_argument("--profile", type=Path, action="append", required=True,
                        help="profile skills/agentic-soc directory; repeat for several profiles")
    parser.add_argument("--only", action="append", default=[],
                        help="restrict to one skill directory, e.g. thor-assessment; repeatable")
    parser.add_argument("--write", action="store_true",
                        help="copy profile files into the repository (repository only, never the profile)")
    parser.add_argument("--force", action="store_true",
                        help="allow --write on a dirty working tree")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    repo_skills = (args.repo / "skills").resolve()
    if not repo_skills.is_dir():
        print(f"error: {repo_skills} is not a skills directory", file=sys.stderr)
        return 2

    profiles = []
    for raw in args.profile:
        path = raw.expanduser().resolve()
        if not path.is_dir():
            print(f"error: {path} is not a directory", file=sys.stderr)
            return 2
        if repo_skills in path.parents or path in repo_skills.parents:
            print(f"error: {path} overlaps the repository skills tree", file=sys.stderr)
            return 2
        profiles.append(path)

    only = set(args.only)
    report = {str(p): compare(repo_skills, p, only) for p in profiles}
    drift = sum(len(rows) for rows in report.values())

    if args.json:
        print(json.dumps({"repo_skills": str(repo_skills),
                          "profiles": report,
                          "differing_files": drift}, indent=2, ensure_ascii=False))
    else:
        for profile, rows in report.items():
            print(f"\n{profile}")
            print(f"  {len(rows)} differing file(s)")
            for row in rows.values():
                print(f"  {row['state']:<12} {row['file']}")
        print(f"\ntotal differing files: {drift}")

    if not args.write:
        return 1 if drift else 0

    if not drift:
        print("nothing to harvest")
        return 0
    if not args.force:
        status = _git(args.repo, "status", "--porcelain")
        if status.returncode != 0:
            print("error: --write needs a git working tree; pass --force for a plain directory",
                  file=sys.stderr)
            return 2
        if status.stdout.strip():
            print("error: working tree is not clean; commit or stash first, or pass --force",
                  file=sys.stderr)
            return 2

    written = 0
    for profile, rows in report.items():
        source_root = Path(profile)
        for row in rows.values():
            if row["state"] == "repo-only":
                print(f"skip (repository is newer): {row['file']}")
                continue
            source = source_root / row["file"]
            target = repo_skills / row["file"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            written += 1
            print(f"wrote {row['file']}")
    print(f"\n{written} file(s) copied into {repo_skills} — review with `git diff` before committing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
