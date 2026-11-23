---
name: soc-l2-investigation
description: "Run the independent second-level investigation of an escalated case and reach a defensible classification. Use for L2 analysis and the incident recommendation, not for running the response."
---

# Soc L2 Investigation

1. Re-derive L1's numbers before reading its conclusion. Counts, IDs and asset context are verified independently.
2. Rebuild the observation window and check for events outside it that change the reading.
3. Corroborate with independent telemetry: another module, another data source, another host. A single-source case stays single-source.
4. Establish scope in three lists: confirmed affected, suspected, and unknown. Accounts and data belong in scope, not only hosts.
5. Order a timeline with labelled timestamp types and mark which entries are inferred rather than observed.
6. Classify true positive, false positive or inconclusive. An unresolvable contradiction produces inconclusive, not a coin flip.
7. Set priority and criticality independently of L1 and justify both against asset criticality, recency and business impact.
8. Recommend the next step and name its decision owner: declare incident, continue monitoring, tune detection, close.
9. If the case goes to incident handling, state explicitly what the handler must re-verify and which evidence is still unproven.

Never accept an escalated conclusion as established fact. Never convert an L2 assessment into an execution instruction.
