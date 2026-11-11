[Project overview](../README.md) / [Documentation](README.md) / Capability reference

# Capability reference

The native entrypoint is `plugin.yaml` plus `register(ctx)` in `__init__.py`. This reference describes v0.2.4; `soc_capabilities` provides a local inventory without contacting vendors or exposing configuration values.

## Native tools

| Tool | Purpose | Operational boundary |
|---|---|---|
| `soc_capabilities` | Inventory implemented functions, planned integrations and configuration presence | No remote connectivity test or credential disclosure |
| `soc_template_list` | List nine specialist role templates | Read-only inventory |
| `soc_template_install` | Preview or provision a new `soc-` profile | Host approval for creation; existing profiles are not overwritten |
| `thor_lite_scan` | Probe local CLI capabilities, prepare or request a FileScan | External executable, configured scan root and host approval for execution |
| `thor_parse` | Import allowed local structured evidence and count/group observations | Supported JSON v1/v2 only; strict limits and input checks |
| `thor_first_assessment` | Produce deterministic case JSON and a nine-section German report | Provisional first assessment, not forensic certainty |
| `soc_alert_triage` | Triage supplied alert evidence | No remote enrichment |

The single `pre_tool_call` hook requests host-owned approval for sensitive execution. An argument supplied by a model cannot authorize itself, and direct library calls are not a protected execution boundary.

## Slash commands

| Command | Purpose |
|---|---|
| `/soc-capabilities` | Show current local scope, roadmap and preview state |
| `/soc-templates` | List specialist profiles |
| `/thor-assess /absolute/path/thor.json` | Assess allowed structured evidence |
| `/thor-scan {"target":"/absolute/approved/lab","execute":false}` | Preview a local scan only |

`/thor-scan` refuses execution. Actual scans must use the normal agent tool pipeline because the inspected host's low-level dispatch path does not establish the same approval boundary.

## Specialist profiles

| Profile ID | Focus | Status |
|---|---|---|
| `soc-l1-triage` | Initial alert triage and evidence gaps | Defense profile |
| `soc-l2-incident-responder` | Incident analysis and draft response recommendations | Defense profile |
| `threat-hunter` | Hypothesis-led investigation | Defense profile |
| `dfir-compromise-assessment` | Evidence-led compromise assessment | Defense profile |
| `detection-engineer` | Detection logic and validation guidance | Defense profile |
| `vulnerability-manager` | Vulnerability context and prioritization | Defense profile |

Profiles and skills guide behavior; they are not a sandbox for unrelated host tools. See the [research preview](PLANNED-OFFENSIVE-RESEARCH.md) and [security model](../SECURITY.md) before provisioning a research persona.

## Skills, workflows and integrations

- **39 skills:** Nine THOR analysis skills (see [THOR analysis suite](THOR-ANALYSIS.md)), six domain/workflow skills and 25 technology-specific scaffolds. Skill availability is not proof of a live integration.
- **3 workflow references:** Declarative YAML guidance, not an executable orchestration engine.
- **25 technology entries:** Each has a planning skill and inactive MCP descriptor. The verified live remote connector count is zero.
- **CyStrat SOC Suite:** Dedicated skill, inactive descriptor and proposed read-only contract; no invented live endpoint.

See the [integration roadmap](INTEGRATION-ROADMAP.md) for technology coverage and promotion gates. The [operator guide](OPERATOR-GUIDE.md) explains assessment policy, evidence handling and profile-isolation limits.
