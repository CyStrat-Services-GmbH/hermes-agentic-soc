"""Native Hermes entrypoint; all registration through documented public APIs."""

import json
from pathlib import Path

def register(ctx):
    from .agentic_soc.api import TOOLS, policy
    from .agentic_soc.runtime import Runtime

    root = Path(__file__).resolve().parent

    def data_root():
        from plugins.plugin_storage import plugin_data_dir
        return plugin_data_dir("agentic-soc")

    runtime = Runtime(root, data_root, ctx.get_config)

    def make_handler(spec):
        def handle(params, **kwargs):
            # Runtime owns validation + fail-closed audit. Do not create a second
            # handler-level path that may raise while trying to log invalid input.
            return json.dumps(runtime.call(spec["name"], params), ensure_ascii=False)
        return handle

    for spec in TOOLS:
        ctx.register_tool(name=spec["name"], toolset="agentic_soc", schema=spec, handler=make_handler(spec))
    def audited_policy(tool_name, args, **kwargs):
        try:
            from .agentic_soc.tools.templates import PROFILES
            offensive = tool_name == "soc_research_plan" or (
                tool_name == "soc_template_install" and isinstance(args, dict)
                and PROFILES.get(args.get("template"), ("",))[0] == "scaffold")
            if offensive and ctx.get_config("offensive_preview_enabled", False) is not True:
                from .agentic_soc.audit import Audit
                Audit(runtime.data()).write(tool_name, "preview_gate_blocked")
                return {"action": "block", "message": "Offensive Security preview is disabled. Only the operator may opt in; this does not enable target execution."}
        except Exception:
            return {"action": "block", "message": "Agentic SOC could not verify the preview gate; action refused."}
        decision = policy(tool_name, args, **kwargs)
        if decision is not None:
            try:
                from .agentic_soc.audit import Audit
                Audit(runtime.data()).write(tool_name, "policy_" + decision["action"])
            except Exception:
                return {"action": "block", "message": "Agentic SOC audit is unavailable; action refused."}
        return decision

    ctx.register_hook("pre_tool_call", audited_policy)
    for skill in sorted((root / "skills").glob("*/SKILL.md")):
        ctx.register_skill(skill.parent.name, skill)

    def templates_command(raw_args, **kwargs):
        if raw_args.strip():
            return "Use soc_template_install for a reviewed installation plan. /soc-templates lists available templates."
        return ctx.dispatch_tool("soc_template_list", {})

    def capabilities_command(raw_args, **kwargs):
        technology = raw_args.strip()
        return ctx.dispatch_tool("soc_capabilities", {"technology": technology} if technology else {})

    def scan_command(raw_args, **kwargs):
        try:
            params = json.loads(raw_args)
        except (ValueError, TypeError):
            return 'Usage: /thor-scan {"target":"/absolute/allowed/directory","execute":false}'
        if not isinstance(params, dict) or params.get("execute", False) is not False:
            return "Slash command is preview-only. Request thor_lite_scan with execute=true as a normal agent tool call so the host approval pipeline runs."
        return ctx.dispatch_tool("thor_lite_scan", params)

    def assess_command(raw_args, **kwargs):
        path = raw_args.strip()
        if not path:
            return "Usage: /thor-assess /absolute/path/to/thor.json"
        return ctx.dispatch_tool("thor_first_assessment", {"path": path})

    ctx.register_command("soc-templates", templates_command, "List SOC profiles")
    ctx.register_command("soc-capabilities", capabilities_command, "Show current functions, planned integrations and preview state")
    ctx.register_command("thor-scan", scan_command, "Preview a local THOR Lite scan; execution uses the normal tool approval pipeline")
    ctx.register_command("thor-assess", assess_command, "Assess allowed THOR JSON evidence")
