---
name: tech-splunk
description: "Prepare read-only Splunk query plans for supplied SOC evidence. Use for this technology scaffold, not live connectivity or deployment."
---

# Splunk scaffold

1. Check tenant, role, data-sharing permission and a bounded time window.
2. Verify fields and syntax against the deployed version before executing anything.
3. Review this unexecuted SPL starter; replace placeholders using approved field mappings.
4. Use only an independently configured read-only connector with least-privilege RBAC and trust: untrusted.
5. Record exact query, actual result count and coverage limitations. Never silently execute writes.

```text
index=APPROVED_INDEX earliest=-24h latest=now | head 100 | table _time host sourcetype
```

Vendor MCP documentation: https://help.splunk.com/en/splunk-enterprise/mcp-server-for-splunk-platform/2.0/connecting-to-the-mcp-server-and-settings

No server is enabled by this plugin. Empty MCP template fields are intentional.
