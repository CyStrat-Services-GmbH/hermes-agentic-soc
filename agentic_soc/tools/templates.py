"""Shipped profiles: inspection and no-credential local installation."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from ..security import BoundaryError, check_scope
from .thor import subprocess_env

PROFILES = {
    "soc-l1-triage": ("mvp", "Triage incoming alerts, evidence and escalation", "alert-triage"),
    "soc-l2-incident-responder": ("mvp", "Validate incidents and prepare approved response", "alert-triage"),
    "threat-hunter": ("mvp", "Hypothesis-driven, bounded read-only hunting", "threat-hunt"),
    "dfir-compromise-assessment": ("mvp", "THOR evidence and compromise-assessment triage", "compromise-assessment"),
    "detection-engineer": ("mvp", "Draft and test Sigma/YARA detections without deployment", "threat-hunt"),
    "vulnerability-manager": ("mvp", "Prioritize supplied vulnerability evidence", "alert-triage"),
    "red-team-planner": ("scaffold", "Authorized research planning only", "purple-team"),
    "adversary-emulation": ("scaffold", "Lab emulation plans only, no execution", "purple-team"),
    "purple-team-validator": ("scaffold", "Compare planned lab signals with supplied detections", "purple-team"),
}


def list_templates() -> dict:
    return {"profiles": [{"id": k, "status": v[0], "description": v[1], "workflow": v[2],
                          "scope_required": v[0] == "scaffold"} for k, v in PROFILES.items()],
            "note": "Technology connectors are opt-in scaffolds, not live integrations."}


def install(root: Path, template: str, name: str, execute: bool = False,
            scope: dict | None = None, target: str = "", *, profile_home: Path | None = None) -> dict:
    if template not in PROFILES or not re.fullmatch(r"soc-[a-z0-9][a-z0-9-]{0,42}", name):
        raise BoundaryError("Select a known template and a new soc-prefixed profile name.")
    if PROFILES[template][0] == "scaffold":
        check_scope(scope, target)
    argv = ["hermes", "profile", "create", name, "--no-credentials", "--no-skills", "--no-alias",
            "--description", PROFILES[template][1]]
    if not execute:
        return {"ok": True, "dry_run": True, "command": argv, "requires_human_approval": True,
                "note": "Does not copy keys. Hermes may still share default-root subscription auth; not credential isolation. No overwrite."}
    if profile_home is None or not profile_home.is_absolute():
        raise BoundaryError("An explicit host-derived profile home is required; refusing process-global fallback.")
    env = subprocess_env()
    env["HERMES_HOME"] = str(profile_home)
    hermes = shutil.which("hermes")
    if not hermes:
        raise BoundaryError("Hermes CLI is required for profile creation.")
    # Discover and verify the new profile's path through the documented public command.
    proc = subprocess.run([hermes, *argv[1:]], env=env,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          stdin=subprocess.DEVNULL, timeout=60, check=False)
    if proc.returncode:
        raise BoundaryError("Hermes profile creation failed; existing profiles are never overwritten.")
    show = subprocess.run([hermes, "profile", "show", name],
                          env=env, stdin=subprocess.DEVNULL, capture_output=True, timeout=15, check=False)
    if show.returncode:
        return {"ok": False, "profile_created": True,
                "error": "Profile created without credentials, but structured path discovery failed. Install persona manually; no path guessed."}
    try:
        # `profile show` has no --json in Hermes 0.23.1. Parse only its labelled
        # public CLI Path line, and fail closed if the output format changes.
        matches = re.findall(r"^Path:\s+(.+)$", show.stdout.decode("utf-8"), re.MULTILINE)
        if len(matches) != 1:
            raise ValueError
        raw_dest = Path(matches[0])
        if not raw_dest.is_absolute() or raw_dest.is_symlink():
            raise ValueError
        destination = raw_dest.resolve(strict=True)
        if destination.name != name or destination.parent.name != "profiles":
            raise ValueError
    except (ValueError, TypeError, OSError, UnicodeError):
        raise BoundaryError("Hermes profile response did not contain a validated home path.") from None
    source = root / "templates" / "profiles" / template
    for filename in ("SOUL.md",):
        to = destination / filename
        if to.is_symlink():
            raise BoundaryError("Refusing a symlinked persona destination.")
        # Only this newly-created profile is touched. Preserve Hermes's fresh
        # default persona, never an existing profile's custom persona.
        if to.exists():
            to.rename(destination / "SOUL.hermes-default.md")
        with to.open("x", encoding="utf-8") as out:
            out.write((source / filename).read_text(encoding="utf-8"))
    skill_dir = destination / "skills" / "agentic-soc"
    if skill_dir.exists():
        raise BoundaryError("Refusing to overwrite an existing skill directory.")
    shutil.copytree(root / "skills", skill_dir)
    return {"ok": True, "profile_created": True, "persona_installed": True,
            "credentials_copied": False, "credential_isolation": False,
            "note": "Configure model/auth separately. Hermes may share root subscription auth. Enable agentic-soc in this profile. SOUL is instruction, not a sandbox."}
