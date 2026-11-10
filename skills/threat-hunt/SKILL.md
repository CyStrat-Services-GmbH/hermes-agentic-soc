---
name: threat-hunt
description: "Draft bounded read-only hunts from hypotheses and IOCs. Use for hunt planning and query review, not unrestricted query execution."
---

# Threat Hunt

1. Define hypothesis, tenant, asset scope, time bounds and telemetry prerequisites.
2. Read the relevant technology skill for a starter query.
3. Replace schema placeholders only after inspecting the approved tenant's actual field mappings.
4. Permit only read-only search with bounded results. Never use saved searches, macros, scripts or lookup writes without independent review.
5. Record exact queries and supplied results; an empty query result is not proof of no compromise.
6. Deliver confirmed observations, alternative hypotheses, coverage gaps and a next hunt.

Do not upload customer indicators to public TI services without explicit data-sharing approval.
