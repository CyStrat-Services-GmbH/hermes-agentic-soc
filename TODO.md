# Release blockers and open work

## Before an Open Source / hackathon release

- **License:** Obtain final rights-holder approval. Replace the placeholder LICENSE and `LicenseRef-Pending-Approval` with the actual approved license. Apache-2.0 is proposed, not granted.
- **THOR verification:** Operator installs an appropriately licensed THOR Lite separately; test a bounded authorized directory and the actual installed CLI flags/output.
- **Publication approval:** Keep source, documentation and video private until the owner explicitly approves the specific public release or submission. A prepared video is not approval to post it.
- **Submission:** After renewed approval, review the current submission requirements, approve the final video/post and submit the required links.
- **Catalog:** Open the prepared catalog PR only after license approval and renewed public-release authorization. Catalog entry must pin a real public 40-character commit, not a placeholder or working-tree state.

## Confirmed publication constraints

- Joint CyStrat / Nextron presentation was approved by the sponsor; the owner's later private-repository instruction controls actual publication.
- THOR is external. No vendor binary, signature, private rule or license is included, downloaded or sublicensed.
- The owner requested the three company logos in the documentation. Original marks and dark-background documentation panels are included with [provenance](assets/brand/README.md); this is not a general trademark or public-release grant.

## Functional roadmap

- Real integration acceptance tests across Windows, Linux and macOS.
- Signed-off read-only connector implementations and tool-specific host approvals.
- THOR v3 support using version-specific fixtures; legacy CSV/text adapters kept separate.
- Forensic multi-source event-log correlation, provenance and full unique-entity inventory.
- Analyst-controlled ATT&CK mapping with evidence-specific rationale.
- Executable workflow runner only after explicit state, approval and recovery design.
- Customer data retention/erasure, hardened access controls and audit export.
- Threat-model review for untrusted logs and MCP results.
