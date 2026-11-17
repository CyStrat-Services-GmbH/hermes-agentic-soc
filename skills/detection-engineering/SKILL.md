---
name: detection-engineering
description: "Draft and test Sigma/YARA detections from supplied evidence. Use for detection development with fixtures, not automatic production deployment."
---

# Detection Engineering

1. Identify the observed behaviour, telemetry source and unsupported assumptions.
2. Draft an original rule with explicit logsource, field mappings and false-positive notes.
3. Write at least one positive and one negative synthetic fixture before claiming the rule works.
4. Run both in a controlled lab and record the actual output, including failures.
5. Map ATT&CK only with a behaviour-specific rationale; do not extract technique IDs as proof from arbitrary text.
6. Document the data source prerequisite; a rule whose source is absent is not a detection.
7. Produce a reviewed pull-request draft. No live rule deployment in this MVP.

Companion skills, when the operator has installed them: `yara-rule-skill` (YARAHQ) for YARA naming, metadata, string choice, performance, yaraQA issue IDs and YARA-Forge quality gates; `thor-custom-signatures` (Nextron's thor-skill) for THOR IOC files, YARA and Sigma placement and false-positive filters. Their guidance takes precedence over the summary here. See docs/OPERATOR-GUIDE.md, "Companion skills".

Do not copy Nextron private rules or signature packs. Review licenses of external Sigma/YARA rules separately.
