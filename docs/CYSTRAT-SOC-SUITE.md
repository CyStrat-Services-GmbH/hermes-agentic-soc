[Project overview](../README.md) / [Documentation](README.md) / CyStrat SOC Suite

# CyStrat SOC Suite

<p><img src="../assets/brand/cystrat.png" width="260" alt="CyStrat Services GmbH"></p>

> [!NOTE]
> **Integration design / scaffold.** Dedicated skill and proposed read-only MCP contract; no verified live connection.

CyStrat SOC Suite is included as a first-class entry in the plugin's technology inventory. It has a dedicated skill and MCP preparation files, but is not represented as a working live connector.

## Shipped files

- `skills/tech-cystrat-soc-suite/SKILL.md`: tenant-/case-scoped analysis workflow, source provenance and local-inference boundaries.
- `templates/mcp/cystrat-soc-suite.example.json`: disabled MCP descriptor with no server process or invented endpoint.
- `templates/mcp/cystrat-soc-suite.contract.json`: proposed read-only tool contract and acceptance criteria, explicitly not implemented.
- `templates/registry.yaml`: `cystrat-soc-suite`, type `soc-platform`, status `scaffold`.

## Architecture intent

Treat the suite as the analyst/agent-facing console above underlying telemetry platforms such as Splunk, Elastic and a planned CyStrat log-store interface. Retain the original platform, record IDs, timestamps, query filters and evidence provenance. Keep tenant isolation server-enforced and derive tenant identity from the authenticated principal, never from a model's assertion.

The project context specifies local inference. Do not introduce online model calls or public indicator uploads as a side effect of this integration.

## Not yet delivered

There is no verified deployed endpoint, MCP server transport, service-account/RBAC contract or live acceptance test. The inspected Suite V2 application route file is a scaffold. Proposed tool names are design artifacts only; they are not registered with Hermes.

Before implementation, obtain the actual API specification, read-only authentication path, tenant-isolation design, pagination/rate limits, data retention requirements and an authorized test tenant. Test rejected writes and cross-tenant access before enabling any connector.
