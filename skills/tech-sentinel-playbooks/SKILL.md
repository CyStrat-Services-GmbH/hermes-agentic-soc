---
name: tech-sentinel-playbooks
description: "Prepare read-only Sentinel Playbooks query plans for supplied SOC evidence. Use for this technology scaffold, not live connectivity or deployment."
---

# Sentinel Playbooks scaffold

1. Check tenant, role, data-sharing permission and a bounded time window.
2. Verify fields and syntax against the deployed version before executing anything.
3. Review this unexecuted query-plan starter; replace placeholders using approved field mappings.
4. Use only an independently configured read-only connector with least-privilege RBAC and trust: untrusted.
5. Record exact query, actual result count and coverage limitations. Never silently execute writes.

```text
Review a supplied Logic App definition and run history; never trigger a run.
```

Official MCP status: not verified in this release. Do not infer that no vendor MCP exists.

No server is enabled by this plugin. Empty MCP template fields are intentional.
