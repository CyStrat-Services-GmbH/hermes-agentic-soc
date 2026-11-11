"""Truthful, local capability inventory: implemented != planned != configured."""

import json

from .. import __version__
from ..security import BoundaryError
from .templates import PROFILES


def inventory(root, get_config, technology=None):
    registry = json.loads((root / "templates" / "registry.yaml").read_text(encoding="utf-8"))
    technologies = registry["technologies"]
    selected = technologies
    if technology:
        selected = [row for row in technologies if row["id"] == technology]
        if not selected:
            raise BoundaryError("Unknown technology id. Call soc_capabilities without a filter to list valid ids.")
    settings = {key: get_config(key, default) for key, default in (
        ("thor_path", ""), ("evidence_roots", []), ("scan_roots", []))}
    return {
        "ok": True, "version": __version__, "network_calls": 0,
        "summary": {
            "profiles": len(PROFILES),
            "skills": len(list((root / "skills").glob("*/SKILL.md"))),
            "technology_templates": len(technologies),
            "live_remote_connectors": 0,
        },
        "implemented": [
            "Local THOR JSON v1/v2 evidence import and deterministic first assessment",
            "Local THOR FileScan wrapper, requiring an external executable and host approval",
            "Specialist profile templates and approved fresh-profile provisioning",
            "Supplied-alert triage, offline reports and auditable planning",
        ],
        "planned_integrations": [
            {**row, "integration_state": "planned", "live_verified": False}
            for row in selected
        ],
        "local_configuration": {
            "thor_path_configured": isinstance(settings["thor_path"], str) and bool(settings["thor_path"].strip()),
            "evidence_roots_configured": isinstance(settings["evidence_roots"], list) and bool(settings["evidence_roots"]),
            "scan_roots_configured": isinstance(settings["scan_roots"], list) and bool(settings["scan_roots"]),
            "scanner_probed": False,
            "note": "Configuration presence is not operational validation. No paths, credentials or environment values are exposed.",
        },
        "next_steps": [
            "Choose a specialist profile for the use case.",
            "Use approved local evidence now, or review a technology scaffold for future integration.",
            "Validate tenant RBAC, MCP/API contract and data-sharing scope before enabling any remote integration.",
        ],
    }
