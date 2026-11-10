---
name: tech-elastic-security
description: "Prepare read-only Elastic Security query plans for supplied SOC evidence. Use for this technology scaffold, not live connectivity or deployment."
---

# Elastic Security scaffold

1. Check tenant, role, data-sharing permission and a bounded time window.
2. Verify current fields and language syntax against the operator's deployed version.
3. Review the starter below. It is an unexecuted planning example, not a verified integration.
4. Run only through an independently configured read-only connector with least-privilege RBAC.
5. Record query, scope, actual result count and coverage limitations. Never silently execute writes.

Language or plan: ES|QL.

```text
FROM logs-* | WHERE @timestamp > NOW() - 24 hours | KEEP @timestamp, event.dataset | LIMIT 100
```

Vendor MCP documentation: https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/mcp-server

No server is enabled by this plugin. Empty MCP template fields are intentional.
For Elastic THOR ingestion, see the separately maintained integration:
https://www.elastic.co/docs/reference/integrations/nextron_thor_apt_scanner
