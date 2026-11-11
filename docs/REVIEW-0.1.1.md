# Second-pass review: Hermes Agentic SOC 0.1.1

Review date: 2026-11-11. This is a source-code review with implemented fixes and regression tests, not an independent penetration test or a formal security certification.

## Findings and corrections

| Severity | Finding in 0.1.0 | Correction in 0.1.1 |
|---|---|---|
| High | Approval message was generic and the host rule key was not explicitly bound to the requested arguments. | Approval displays canonical argument JSON and a SHA-256-derived rule key; changing target/profile/scope changes the fingerprint. Host approval policy still controls one-time/session/permanent behavior. |
| High | File paths or process PIDs without sufficient identity could be grouped, and missing host/scan identities could collide. | Correlation requires explicit host+scan and either file+hash, event/record/channel, or PID+start time. Ambiguous observations remain separate. |
| Medium | The parser rejected v3 but could accept other unsupported explicit versions. | Explicit versions outside v1/v2 are refused; duplicate JSON keys, case-colliding keys, nonfinite constants and ambiguous wrappers are refused. |
| Medium | File-size protection was primarily at path validation; direct parser calls could read larger files. | Parser reads at most 50 MiB+1, then refuses oversize. NDJSON event count is bounded while reading lines. |
| Medium | Markdown reports interpolated untrusted module names and metadata. | Evidence text is escaped and flattened before rendering. Raw rule content is never treated as instructions. |
| Medium | Timeline used lexical sorting and could include invalid or timezone-free strings. | Valid timezone-aware ISO timestamps are sorted in UTC. Excluded metadata counts are disclosed. Detection time is never attack time. |
| Medium | Existing data-root permissions and output files depended on umask. Child output directories and audit/salt symlinks needed stronger checks. | POSIX root/child modes are 0700; generated JSON/Markdown files are 0600. Child directories, salt and audit refuse symlinks. Audit supports short writes. |
| Medium | Unavailable audit could raise before a safe tool response; direct runtime calls bypassed schema validation. | Failed audit prevents execution; runtime validates the same tool schemas before work. |
| Medium | Literal wildcard text could pass if it exactly matched an identically wildcarded target declaration. | Wildcard/control syntax is rejected even if both fields match. |
| Medium | Bearer strings, URL credentials and terminal/bidi controls were insufficiently minimized. | Added bearer and URL userinfo redaction plus terminal-control/bidi removal. Still best-effort, not exhaustive DLP. |
| Product | The central Assessment block was too generic for an analyst. | It now includes the highest-severity concrete observations and reasons, duplicate counts and explicit correlation rules. |
| Product | Demo use required a separate script and confusing host-only execution assumptions. | Added `python -m agentic_soc profiles`, `demo` and `assess`; no live scan or profile mutation exposed through this CLI. |
| Product | Private repository status was not reflected throughout documentation. | Private-development notice and no-publication boundary added. Catalog and video remain review drafts. |
| Low | CI action tags were mutable. | Checkout and setup-python are pinned to the verified full commit SHAs behind their existing major-version tags. |

## New project requirements

### exploit labs

The sponsor has designated exploit labs and managing director Johannes Schönborn for the planned Offensive Security contribution. This appears only in the research skeleton, marketing and gated-preview documentation. No delivered exploit labs operative implementation or copyright/license grant is asserted.

`offensive_preview_enabled` is a strict boolean operator setting, false by default. The policy hook and runtime reject offensive-profile and research-plan calls while disabled. Valid scope remains mandatory after opt-in; no target interaction is implemented.

### CyStrat SOC Suite

The suite is the twenty-first technology entry and has its own skill, inactive MCP descriptor and proposed read-only contract. The intended design preserves tenant identity, case/evidence scope, provenance from Splunk/Elastic and local-model intent. No endpoint, executable or token is invented.

The inspected `CyStrat_SOC_Suite_V2/server/routes.ts` contains only a route-registration scaffold and no implemented application API methods. The new MCP names are explicitly proposals, not callable tools or proof of a working remote service. A live implementation remains blocked on a verified API and authorization contract.

## Validation scope

Regression coverage includes approval fingerprints, unknown versions, ambiguous JSON, correlation with missing identity, PID reuse, channels, Markdown injection, UTC timeline ordering, privacy strings, output permissions, symlinks, audit failures, concurrent salt access, offline CLI and preview-gate bypass attempts.

The code has zero third-party runtime dependencies. Skill/registry generation is deterministic and must leave no tracked diff after regeneration. Actual test counts and executed host checks are recorded in `docs/VALIDATION.md` and `docs/validation/`.

## Residual risks and deliberate non-features

- Host approval configuration can allow session/permanent decisions; fingerprints narrow reuse but cannot impose a policy stronger than the host.
- Direct trusted Python code or another fully trusted plugin is outside this package's authorization boundary.
- The external THOR executable is operator-trusted, not sandboxed or publisher-verified by this plugin. Its internal behavior is not controlled by the wrapper.
- Application path checks are not a substitute for trusted evidence staging, OS sandboxing, ACLs or protection against a malicious local account.
- Privacy redaction remains best effort; source provenance and complete chain of custody require additional controls.
- No real THOR binary scan, live SIEM tenant, customer data, production response or attack execution was used in this review.
- The license remains pending. Repository privacy, public video publishing and hackathon submission require new explicit approval.
