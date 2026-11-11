# Review release 0.1.2

This third implementation review focuses on reliable failure semantics, conservative evidence handling and an honest product story. It is an internal engineering review, not an independent security audit or certification.

## Improvements

- **Capability transparency:** `soc_capabilities`, `/soc-capabilities` and the offline CLI distinguish implemented functions, all 21 planned technologies and local configuration presence. They make no network calls and expose no configured paths or secrets.
- **Complete report publication:** Normalized evidence, case JSON and Markdown are written in a private staging directory. Only the complete bundle is renamed into the visible report namespace; failed staging is removed.
- **Audit failure semantics:** Failure before execution prevents action. Failure appending the final audit record retains the completed operation result and reports `AUDIT_FINALIZATION_FAILED`, `operation_completed:true` and `retry_safe:false`. Execution exceptions warn that partial effects may exist.
- **Stable evidence reads:** A bounded regular-file descriptor read rejects observed metadata changes during import and final-component symlinks on platforms supporting `O_NOFOLLOW`. This is not a claim of perfect protection against hostile privileged filesystem changes or crash durability.
- **Strict numeric parsing:** JSON exponent overflow is rejected rather than producing infinite values. Repeated version prefixes cannot be normalized into a supported version.
- **Conservative identity:** Nulls, objects, booleans, invalid process IDs and timezone-free process start times cannot establish a stable correlation identity. Distinct whitespace-bearing paths remain distinct.
- **No reassurance from missing signal:** ERROR/UNKNOWN-only exports remain Inconclusive with provisional MEDIUM criticality, not LOW reassurance or a clean-host claim.
- **Marketing scope:** README, integration roadmap and the English trailer separate current evidence analysis, planned integrations and the disabled exploit labs preview.

## Regression coverage

`tests/test_review_v012.py` exercises numeric overflow, malformed version prefixes, correlation identity types, path distinctions, symlink refusal, changing evidence, staged-output cleanup, complete report bundles, pre-/post-operation audit failures, execution exceptions, incomplete exports and capability disclosure boundaries. Full executed results are recorded in [VALIDATION.md](VALIDATION.md).

## Deliberate limits

There are zero verified live remote connectors. No real licensed THOR scan, Windows/macOS acceptance run or provider-backed interactive scan approval was performed during this review.

Report redaction remains best-effort minimization, not complete anonymization. The scope gate validates required declarations, not legal authority, and a specialist persona is not a cross-tool sandbox. The case-report language remains German; the new product trailer and roadmap are English.

No THOR binaries, signatures, rules or licenses are bundled or downloaded. The repository remains private and Apache-2.0 remains a proposal pending rights-holder approval.

The inspected Hermes runtime printed an unresolved dependency-preparation warning during `validate --install-deps`, although subsequent capability/security validation passed. This is disclosed in the validation record; a completely clean new-runtime installation is not claimed.
