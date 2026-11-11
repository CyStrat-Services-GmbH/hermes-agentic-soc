"""Model-facing schemas, strict argument validation and host policy hook."""

import hashlib

from .security import BoundaryError, canonical

SCOPE = {"type": "object", "description": "Declared authorization scope; operator must verify evidence.",
         "properties": {
             "targets": {"type": "array", "items": {"type": "string"}, "minItems": 1},
             "authorization_ref": {"type": "string", "minLength": 8},
             "valid_from": {"type": "string"}, "valid_until": {"type": "string"},
             "rules_of_engagement": {"type": "string", "minLength": 20},
             "allowed_activities": {"type": "array", "items": {"type": "string", "enum": [
                 "research", "emulation-planning", "detection-engineering", "lab-validation"]}, "minItems": 1}},
         "required": ["targets", "authorization_ref", "valid_from", "valid_until", "rules_of_engagement", "allowed_activities"],
         "additionalProperties": False}


def schema(name, description, props, required=()):
    return {"name": name, "description": description,
            "parameters": {"type": "object", "properties": props, "required": list(required), "additionalProperties": False}}


TOOLS = [
    schema("soc_capabilities", "Show implemented SOC functions, the planned 21-technology integration catalog and gated-preview state. Local inspection only; configuration is not proof of live connectivity.", {
        "technology": {"type": "string", "minLength": 1}}),
    schema("soc_template_list", "List shipped SOC profile templates and their implementation status.", {}),
    schema("soc_template_install", "Preview or create a new defense profile in dry-run first; existing profiles are never overwritten.", {
        "template": {"type": "string"}, "name": {"type": "string"},
        "execute": {"type": "boolean", "default": False}}, ("template", "name")),
    schema("thor_lite_scan", "Probe separately installed THOR Lite or execute an operator-allowed local directory scan after host approval.", {
        "target": {"type": "string"}, "execute": {"type": "boolean", "default": False}}, ("target",)),
    schema("thor_parse", "Import THOR JSON v1/v2 or NDJSON from an allowed root; count and correlate all events.", {
        "path": {"type": "string"}}, ("path",)),
    schema("thor_first_assessment", "Create deterministic, evidence-bounded German THOR Markdown and JSON case reports.", {
        "path": {"type": "string"}}, ("path",)),
    schema("soc_alert_triage", "Triage supplied alert evidence locally; draft-only recommendations, no enrichment or writes.", {
        "alert": {"type": "object", "properties": {"title": {"type": "string"}, "severity": {"type": "string"},
                   "host": {"type": "string"}, "timestamp": {"type": "string"},
                   "evidence": {"type": "array", "items": {"type": "string"}}, "asset_criticality": {"type": "string"}},
                  "required": ["title"], "additionalProperties": False}}, ("alert",)),
]
BY_NAME = {s["name"]: s for s in TOOLS}


def validate(value, spec):
    """Small strict validator for this finite schema subset; zero runtime dependencies."""
    typ = spec.get("type")
    classes = {"object": dict, "array": list, "string": str, "boolean": bool}
    if typ in classes and not isinstance(value, classes[typ]):
        raise BoundaryError("Arguments do not match the declared tool schema.")
    if "enum" in spec and value not in spec["enum"]:
        raise BoundaryError("Argument is outside the declared choices.")
    if typ == "object":
        props = spec.get("properties", {})
        if not set(spec.get("required", [])) <= value.keys():
            raise BoundaryError("Required tool arguments are missing.")
        if spec.get("additionalProperties") is False and not value.keys() <= props.keys():
            raise BoundaryError("Unknown tool arguments are not accepted.")
        for key, item in value.items():
            if key in props:
                validate(item, props[key])
    if typ == "array":
        if len(value) < spec.get("minItems", 0) or len(value) > 10000:
            raise BoundaryError("Array size is outside supported bounds.")
        for item in value:
            validate(item, spec["items"])
    if typ == "string" and not spec.get("minLength", 0) <= len(value) <= 10000:
        raise BoundaryError("String size is outside supported bounds.")


def policy(tool_name: str, args: dict, **kwargs):
    if tool_name not in BY_NAME:
        return None
    try:
        validate(args, BY_NAME[tool_name]["parameters"])
        if tool_name in {"thor_lite_scan", "soc_template_install"} and args.get("execute") is True:
            payload = canonical(args)
            fingerprint = hashlib.sha256((tool_name + payload).encode()).hexdigest()
            return {"action": "approve",
                    "rule_key": f"agentic-soc:{tool_name}:{fingerprint}",
                    "message": f"Human approval required for {tool_name}.\n"
                               f"Exact requested arguments (JSON):\n{payload}\n"
                               "Approval is scoped to this argument fingerprint, not every call to the tool."}
        return None
    except Exception:
        return {"action": "block", "message": "Agentic SOC rejected invalid or unsafe tool arguments."}
