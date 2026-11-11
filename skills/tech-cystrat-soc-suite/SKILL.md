---
name: tech-cystrat-soc-suite
description: "Prepare tenant-scoped CyStrat SOC Suite analysis and MCP integration plans for supplied alerts and cases. Use for the suite above Splunk, Elastic and future log stores; not for an assumed live MCP server or autonomous response."
---

# CyStrat SOC Suite

Status: integration scaffold. The skill and MCP descriptor are shipped; a working live Suite API/MCP server is not claimed.

## Workflow

1. Confirm tenant, case/alert identifier, time window, analyst role and approved local inference environment.
2. Establish the source platform: Splunk, Elastic or the planned CyStrat log-store interface. Do not confuse the analyst console with its telemetry store.
3. Use supplied structured exports until the deployed API and authorization contract are verified. Record original event IDs, source, exact query/filter, timestamps and result limits.
4. Normalize evidence through SOC triage. THOR exports use thor_parse/thor_first_assessment only for supported formats; normalized output is not raw scanner evidence.
5. Compare the proposed read-only MCP contract in templates/mcp/cystrat-soc-suite.contract.json with the deployed service before implementing anything. Those names are design proposals, not callable tools.
6. Enforce server-side tenant identity and RBAC. Never trust a model-provided tenant_id as authorization. Use Hermes-owned secret scope and no embedded tokens.
7. Keep case writes, containment, rule deployment and agent activation out of the MVP connector. Prepare drafts only.
8. Report evidence, gaps and next steps. Preserve local-model intent; do not send customer logs or indicators to an online service without separate authorization.

## MCP boundary

The descriptor has enabled:false and mcp_servers:{}.
There is no guessed hostname, executable, token or endpoint. Configure only after a reviewed service contract, negative tenant-isolation tests, rate limits and read-only RBAC validation.

## Completion

Deliver a scoped analysis draft or integration gap list, not a successful connection claim.
Example: supplied case export -> source-labelled evidence inventory -> analyst assessment -> draft handoff.
