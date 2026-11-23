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

Companion skills, when the operator has installed them: `yara-rule-skill` (YARAHQ) for YARA naming, metadata, string choice, performance, yaraQA issue IDs and YARA-Forge quality gates; `thor-custom-signatures` (Nextron's thor-skill) for THOR IOC files, YARA and Sigma placement and false-positive filters. Their guidance takes precedence over the summary here. See docs/OPERATOR-GUIDE.md, "Companion skills".

Do not copy Nextron private rules or signature packs. Review licenses of external Sigma/YARA rules separately.
