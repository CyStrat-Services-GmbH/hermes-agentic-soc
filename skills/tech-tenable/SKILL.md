---
name: tech-tenable
description: "Prepare read-only Tenable Vulnerability Management query plans for supplied SOC evidence. Use for this technology scaffold, not live connectivity or deployment."
---

# Tenable Vulnerability Management scaffold

1. Check tenant, role, data-sharing permission and a bounded time window.
2. Verify fields and syntax against the deployed version before executing anything.
3. Review this unexecuted query-plan starter; replace placeholders using approved field mappings.
4. Use only an independently configured read-only connector with least-privilege RBAC and trust: untrusted.
5. Record exact query, actual result count and coverage limitations. Never silently execute writes.

```text
Export assets and findings for an approved tag or folder scope; never launch, schedule or resume a scan.
```

Official MCP status: not verified in this release. Do not infer that no vendor MCP exists.

No server is enabled by this plugin. Empty MCP template fields are intentional.
