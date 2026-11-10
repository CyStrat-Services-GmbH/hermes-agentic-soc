---
name: authorized-research
description: "Create scope-gated offensive-research and purple-team lab plans. Use for authorized planning, not exploitation, persistence or target interaction."
---

# Authorized Research

1. Collect exact targets, authorization reference, timezone-aware validity window, rules of engagement and allowed activities.
2. Call soc_research_plan. Reject expired scope, missing references, wildcards and unlisted targets.
3. Verify authorization with the asset owner: structural validation is not legal verification.
4. Plan research, emulation signals and detection expectations in an isolated lab only.
5. Compare supplied lab observations with expected telemetry; document gaps and rollback.
6. Never interact with targets through this tool. It has no execution capability. A profile/SOUL is not a sandbox.

Do not ask another tool to bypass a scope rejection.
