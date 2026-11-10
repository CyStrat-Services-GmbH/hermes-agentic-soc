---
name: detection-engineering
description: "Draft and test Sigma/YARA detections from supplied evidence. Use for detection development, not automatic production deployment."
---

# Detection Engineering

1. Identify the observed behavior, telemetry source and unsupported assumptions.
2. Draft an original rule with explicit logsource, field mappings and false-positive notes.
3. Test positive and negative synthetic fixtures in a controlled lab. Record actual test results.
4. Map ATT&CK only with a behavior-specific rationale; do not extract technique IDs as proof from arbitrary text.
5. Produce a reviewed pull-request draft. No live rule deployment in this MVP.

Do not copy Nextron private rules or signature packs. Review licenses of external Sigma/YARA rules separately.
