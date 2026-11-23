---
name: threat-hunt
description: "Draft bounded read-only hunts from falsifiable hypotheses and supplied indicators. Use for hunt planning and query review, not unrestricted query execution or incident declaration."
---

# Threat Hunt

1. State the hypothesis so that a specific observation would refute it, with tenant, population, time bounds and required telemetry.
2. Confirm which telemetry actually exists for that population and its retention before designing queries.
3. Read the relevant technology skill for a starter query; replace schema placeholders only against the approved tenant's real field mappings.
4. Permit only read-only search with bounded results. Never use saved searches, macros, scripts or lookup writes without independent review.
5. Record the exact query, its scope, its limit and the actual result count.
6. Analyse prevalence with an explicit denominator; low prevalence raises relevance but does not prove maliciousness.
7. Report coverage: which hosts and logs could have shown the activity, and which could not.
8. Deliver confirmed observations, excluded alternatives, visibility gaps, the verdict on the hypothesis and the next hunt.

Do not upload customer indicators to public TI services without explicit data-sharing approval.
