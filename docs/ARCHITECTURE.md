# Architecture

The native Hermes entrypoint registers seven tools, one `pre_tool_call` hook, three slash commands and the shipped namespaced skills. It performs no network or data-directory I/O at registration. It uses only documented `ctx` operations and the public `plugins.plugin_storage.plugin_data_dir` helper ([Hermes plugin API](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)).

## Data flow

```text
Hermes tool / slash command
  -> strict finite JSON-schema argument validation
  -> host pre_tool_call approval for scan/profile execution
  -> lazy profile-scoped Runtime + minimised audit
  -> allowed-root input resolution / fixed-argv local THOR FileScan
  -> strict v1/v2 JSON/NDJSON adapter
  -> exact event inventory + artifact observation grouping
  -> deterministic conservative policy
  -> private normalized.json + case.json + German report.md
  -> minimised preview + report paths + draft-only ticket
```

No LLM decides severity. No external connector is active by default. Workflow YAML files guide agents and reviewers but are not advertised as an executable runner. Root portable `plugin.json`/`mcp.json` files are omitted to avoid accidental MCP launches or duplicate skill namespaces.

## Module ownership

- **api:** Strict finite tool schema subset and host approval directive, with no model-controlled shell flags.
- **security:** Canonical path containment, best-effort minimisation and structural authorization-scope checks.
- **tools/thor:** Strict structured import, explicit version rejection, exact counts and verified local FileScan invocation.
- **scoring:** Conservative provisional policy, evidence limits and case rendering.
- **runtime:** Operator configuration, private output allocation, lazy salt and lifecycle audit.
- **templates/skills:** Extensible role and technology inventory; generated mechanically from reviewable definitions.

## Compatibility and deliberate limits

Hermes v0.23.1 is the declared minimum, with integration validation against the inspected upstream revision recorded in VALIDATION.md. The actual vendor scanner is external and version-probed through its own CLI help. JSON v3 is explicitly unsupported because it is structurally distinct ([Nextron JSON versions](https://github.com/NextronSystems/jsonlog)).

The same-host/scan/file+hash identity is conservative observation grouping, not complete forensic event correlation. Records with no stable artifact key remain separate. Human analysts validate suspicious behavior, potential duplicates, attack time, priority and business impact.
