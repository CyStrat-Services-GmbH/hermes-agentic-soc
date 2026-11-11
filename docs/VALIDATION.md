# Validation record

## Documentation refresh

The documentation refresh leaves the plugin at v0.1.2 and adds six documentation-check tests to the previous 145-test suite. Runtime behavior, registrations and generated skills/templates are unchanged.

| Check | Executed result |
|---|---|
| Python 3.14.8 regression suite | 151 passed |
| Python 3.11.17 regression suite | 151 passed |
| Offline documentation checker | Local Markdown/HTML file targets and three PNG signatures passed; external URLs and renderer-specific heading anchors are not checked |
| GitHub Markdown API | README rendered with three logo images and the status callout; architecture Mermaid block recognized |
| Original logo panels | Visually inspected together on their fixed dark backgrounds |
| Synthetic demo from documented CLI | 4 source events, 3 observation groups, provisional P2 and complete report paths |
| Generated assets | Re-running `scripts/build_assets.py` produced no changes to skills, templates, workflows or schemas |
| Whitespace validation | `git diff --check` passed |

This is documentation and regression verification, not a fresh vendor-scanner or live-tenant acceptance test. Earlier host-validation limitations below remain applicable.

## Review release 0.1.2

The third review introduces a local capability inventory and hardens evidence imports, report publication and audit failure responses. The following checks were executed against the changed source; no live remote connector or licensed THOR scan is implied.

| Review check | Executed result |
|---|---|
| Python 3.14 regression suite | 145 passed |
| Python 3.11 regression suite | 145 passed |
| Agent Skills validation | All 29 directories valid |
| Generated assets | Re-running `scripts/build_assets.py` leaves the generated-content diff unchanged |
| Fresh-home Plugin Doctor | Passed; eight tools and one hook registered |
| Catalog capability/security checks | Passed; declared tools and hooks match registrations, no core override |
| Catalog `--install-deps` preparation | Not a clean pass: two fresh-home attempts reported the host warning described below |
| Offline demo | Exactly 4 synthetic source events and 3 observation groups; complete report bundle created |
| Capability CLI | 9 profiles, 29 skills, 21 technology templates, 0 live remote connectors; Suite filter tested |

Both `validate --install-deps` attempts printed `dependency preparation failed: Dependency inputs changed while preparing publication; retry.`, then ran successful plugin validation and exited zero. The inspected host catches preparation exceptions and continues with its existing environment. Therefore the successful capability/security checks do not establish a successful fresh dependency-preparation step. No host internals were patched to hide or bypass the warning.

Logs are prefixed `review-v012-` in `docs/validation/`. Python 3.12/3.13 and Windows/macOS were not locally executed for this review; GitHub Actions results are recorded separately when available.

## Review release 0.1.1 (historical)

The repository is now **private by owner decision**. Review changes and test logs supersede the original MVP snapshot below. The reviewed version adds stronger input/approval/storage boundaries, an operator-disabled exploit labs research preview and CyStrat SOC Suite as the 21st integration scaffold, for 29 total skills.

Current detailed findings are in `REVIEW-0.1.1.md`; review-specific validation logs are prefixed `review-`. No new THOR vendor-binary or live-tenant validation is claimed.

| Review check | Executed result |
|---|---|
| Python 3.14 regression suite | 115 passed |
| Python 3.11 regression suite | 115 passed |
| Agent Skills validation | 29 valid skill directories |
| Plugin Doctor, independent scratch Hermes home | Passed, 7 tools and 1 hook |
| Catalog validation with `--install-deps`, independent scratch home | Passed, security scan safe, no core override |
| Offline CLI | 4 exact events / 3 observation groups, no real scan |
| Preview defaults | Offensive planning and persona installation fail closed until operator opt-in |
| CyStrat SOC Suite | Dedicated skill + disabled MCP descriptor + proposed contract; no live connection claimed |

## Original 0.1.0 snapshot (historical)

Validation date: 2026-11-11. The following results were executed in the build sandbox, not inferred from CI configuration.

## Executed successfully

| Check | Result |
|---|---|
| Local Python 3.14.8 test suite | 65 passed |
| Local Python 3.11.17 test suite | 65 passed |
| Agent Skills validator | All 28 shipped skill directories valid |
| `hermes plugins doctor . --ci` | Passed; 7 tools, 1 hook |
| `hermes plugins validate . --install-deps` | Passed; declared tools/hooks match, security scan safe, no core override |
| Synthetic offline demo | 4 events, 3 observation groups, provisional P2 / suspicious, JSON and Markdown created |
| Actual Hermes CLI profile provisioning | Fresh DFIR persona, default-persona backup and 28 copied skills verified in a scratch Hermes root |
| Scope, input and privacy tests | Missing/expired scope, unlisted targets, malformed/v3 JSON, unknown scores, symlink escape and common credential inputs refused |
| Scan-launcher tests | CLI capability probe, fixed FileScan argv, dry-run, no-output exit and timeout tested with mocks |
| Slash-command execution restriction | `execute:true` refused by `/thor-scan`; normal tool pipeline required |

The source and test logs are stored under `docs/validation/`. The repository's GitHub Actions workflow declares Python 3.11–3.14; only the two versions listed above are claimed as locally executed.

## Inspected host and environment

Hermes upstream revision: `b1a6350602383fdbed9b0bd0eb15d86eaa335da8`. The GitHub latest release observed during this build was `v0.23.1`, which is the declared minimum. The native package uses only documented registration/config/storage seams ([plugin API](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)).

An initial direct `uv pip install -e hermes-upstream` encountered an upstream dependency conflict: `browser-harness==0.1.13` requested Pillow 12.3.0 while Hermes requested Pillow 13.0.0. No plugin dependency caused it: the plugin has zero third-party runtime dependencies. A separate development environment was prepared, and the Hermes CLI's own runtime preparation subsequently completed for Doctor and `validate --install-deps`. This is disclosed rather than misrepresented as a successful initial full-environment install.

## Findings incorporated into the implementation

- **Auth fallback:** Actual `hermes profile create --no-credentials` still reports default-root subscription-auth sharing in this inspected host. The plugin claims no copying, not auth isolation, and returns `credential_isolation:false`.
- **Multiplexed profile context:** CLI children receive explicit host-derived `HERMES_HOME`; no process-global value is used to select the destination.
- **Low-level dispatch:** The inspected `ctx.dispatch_tool` directly invokes registry handlers. The scan slash command is therefore preview-only, and execution must use normal agent tool calls through the host's pre-tool approval gate.
- **Vendor scope:** FileScan module selection is explicit; `--path` alone is not described as preventing process-module activity ([THOR flags](https://thor-manual.nextron-systems.com/en/latest/usage/flags.html)).

## Not established by these checks

No actual licensed THOR executable was installed or scanned. No live SIEM/SOAR/EDR/TI tenant was contacted. A human-approved interactive scan, unattended host refusal, provider-backed `/plugins` UI session, Windows/macOS acceptance, externally published video, catalog admission and form submission are not claimed.

The authorization-scope checker validates a declaration, not legal authority. Privacy minimisation is not complete anonymisation. Source hashes are not a custody certificate. A synthetic test suite is not an independent security audit.

## Release state

The original delivery used a public repository; the owner subsequently made it private. A catalog-entry generator pins a clean Git commit after it is created; that generated file is deliberately excluded from the plugin's source commit to avoid a self-referential SHA. Opening a catalog PR now requires both renewed public-visibility authorization and final code-license approval.
