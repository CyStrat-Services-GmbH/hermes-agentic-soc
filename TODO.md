# Release blockers and open work

## Before an Open Source / hackathon release

- **License:** Obtain final rights-holder approval. Replace the placeholder LICENSE and `LicenseRef-Pending-Approval` with the actual approved license. Apache-2.0 is proposed, not granted.
- **THOR verification:** Operator installs an appropriately licensed THOR Lite separately; test a bounded authorized directory and the actual installed CLI flags/output.
- **Submission:** Record a real video shorter than 90 seconds, publish the approved post on X tagging @NousResearch, and submit PR/video links through the official form.
- **Catalog:** Open the prepared catalog PR only after license approval. Catalog entry must pin a real public 40-character commit, not a placeholder or working-tree state.

## Confirmed publication constraints

- Joint CyStrat / Nextron presentation and publication are approved by the sponsor.
- THOR is external. No vendor binary, signature, private rule or license is included, downloaded or sublicensed.
- Product logos are not bundled; no inferred authorization to redistribute new brand assets.

## Functional roadmap

- Real integration acceptance tests across Windows, Linux and macOS.
- Signed-off read-only connector implementations and tool-specific host approvals.
- THOR v3 support using version-specific fixtures; legacy CSV/text adapters kept separate.
- Forensic multi-source event-log correlation, provenance and full unique-entity inventory.
- Analyst-controlled ATT&CK mapping with evidence-specific rationale.
- Executable workflow runner only after explicit state, approval and recovery design.
- Customer data retention/erasure, hardened access controls and audit export.
- Threat-model review for untrusted logs and MCP results.
