# threat-hunter

Status: mvp. Hypothesis-driven, bounded read-only hunting.

Use soc_template_install in dry-run mode, then approve creation through Hermes. Existing profiles are not overwritten. Model/auth setup and plugin enablement are explicit operator steps. Offline skills are copied to the new profile; no MCP server is auto-enabled.

The persona does not sandbox other Hermes tools. See root SECURITY.md. Workflow: ../../workflows/threat-hunt.yaml.
