# Validation record

## Release 0.2.3: rule-13 disclosure in the README, catalog entry submitted

The catalog review reads the README at the pinned commit, and it had no disclosure section: the security content lived in `docs/OPERATOR-GUIDE.md` and `SECURITY.md`, which rule 13 does not name. This release adds a `## Security disclosure` section to both READMEs covering network, commands, reads outside the plugin, writes, credentials, background activity and model context, and removes a leftover release TODO block from the German README that still described the licence as pending.

| Content | Status |
|---|---|
| `README.md` / `README.de.md`: `## Security disclosure` | Added, in the categories rule 13 lists |
| `README.de.md`: stale "release-blocking TODO: obtain final licence approval" | Removed — the licence is settled as Apache-2.0 |
| `docs/CATALOG-SUBMISSION.md` | PR number, test count and open items corrected; hackathon section added |
| `submission/catalog-entry.yaml` | Kept identical to the submitted entry file |

| Check | Executed result |
|---|---|
| Regression suite | 184 passed |
| Generator | `build_assets.py` idempotent; 6 profiles, 30 generated + 9 hand-authored skills, 25 technology scaffolds, 3 workflows |
| Documentation checker | PASS |
| Plugin Doctor (Hermes 0.23.0) | 7 tools, 1 hook |
| Catalog validation | `hermes plugins validate . --install-deps` passed |


## Release 0.2.2: exploit labs is a confirmed cooperation partner

exploit labs was described as a planned contributor only. Their support and cooperation on the plugin are confirmed, so every statement now says so — while the offensive-research capability itself stays unbuilt and out of this version. Agreed cooperation is not a shipped feature, and the documentation keeps the two apart.

| Content | Status |
|---|---|
| README, README.de, INTEGRATION-ROADMAP, MARKETING-EN, PLANNED-OFFENSIVE-RESEARCH, submission notes | Reworded: confirmed supporter and cooperation partner, contributor of the planned offensive-research part |
| Generator footers (`scripts/build_assets.py`, `scripts/profile_souls.py`) | Reworded; profile SOULs regenerated |
| "Planned, not shipped" boundary for the offensive-research capability | Unchanged — still absent, not previewable, not enableable |

| Check | Executed result |
|---|---|
| Regression suite | 180 passed |
| Generator | `build_assets.py` idempotent; 6 profiles, 30 generated + 9 hand-authored skills, 25 technology scaffolds, 3 workflows |
| Documentation checker | PASS: 23 Markdown files, 198 local targets, 3 brand PNGs |
| Plugin Doctor (Hermes 0.23.0) | 7 tools, 1 hook |
| Catalog validation | Validation passed |

## Release 0.2.1: partnership and contributor statements carry no personal names

Documentation and generated persona text named individuals from Nextron Systems and exploit labs. Those statements now speak about the companies only: Nextron Systems' management confirms support and cooperation, exploit labs is the planned contributor of the future offensive-research release. No claim, credit or role changes; only who is named.

| Content | Status |
|---|---|
| README, README.de, INTEGRATION-ROADMAP, MARKETING-EN, PLANNED-OFFENSIVE-RESEARCH, REVIEW-0.1.1, submission notes | Rewritten to company-only wording |
| Generated persona footer (`scripts/build_assets.py`, `scripts/profile_souls.py`) and every regenerated profile SOUL | Rewritten; generator is the source, templates follow |
| Release notes of v0.2.0 on GitHub | Corrected in place |

| Check | Executed result |
|---|---|
| Regression suite | 180 passed |
| Generator | `build_assets.py` idempotent; 6 profiles, 30 generated + 9 hand-authored skills, 25 technology scaffolds, 3 workflows |
| Documentation checker | PASS: 23 Markdown files, 198 local targets, 3 brand PNGs |
| Plugin Doctor (Hermes 0.23.0) | 7 tools, 1 hook |
| Catalog validation | Validation passed |
| No personal names | No person name remains in tracked files or generated templates |

Not established: commit history of v0.2.0 still contains the names in its commit message; removing them would require rewriting published history, which this release does not do.

## Release 0.2.0: defense-only package, Apache-2.0, catalog evidence

Breaking release. The offensive/research part is no longer part of the shipped package — not disabled, removed: three research profiles, the `authorized-research` skill, the `purple-team` workflow, the `soc_research_plan` tool, the `offensive_preview_enabled` config key and the scope checker that only that tool used. `docs/PLANNED-OFFENSIVE-RESEARCH.md` states what is planned for a later release and that nothing of it is previewable or enableable now.

| Content | Status |
|---|---|
| Defense-only profile set: six roles from L1 triage to vulnerability management | Implemented |
| Removal of all offensive/research artefacts (profiles, skill, workflow, tool, config key, scope checker) | Implemented |
| License changed from a placeholder to Apache-2.0 (`LICENSE`, `NOTICE`, `plugin.yaml`, both READMEs) | Implemented |
| Nextron Systems support and cooperation recorded (confirmed by Nextron Systems' management), without claiming a vendor licence grant | Documentation |
| `docs/CATALOG-SUBMISSION.md`: all 18 catalog admission rules mapped to evidence; prepared entry in `submission/catalog-entry.yaml` (not version-controlled) | Documentation |
| Vulnerability management domain with four templates (see 0.1.7 content in the previous section) | Implemented |

| Check | Executed result |
|---|---|
| Regression suite | 180 passed |
| Generator | `build_assets.py` idempotent; 6 profiles, 30 generated + 9 hand-authored skills, 25 technology scaffolds, 3 workflows |
| Documentation checker | PASS: 23 Markdown files, 198 local targets, 3 brand PNGs |
| Plugin Doctor (Hermes 0.23.0) | 7 tools, 1 hook |
| Catalog validation | Validation passed (hooks, middleware, collisions, security scan, no core override) |
| `soc_capabilities` | `profiles: 6, skills: 39, technology_templates: 25, live_remote_connectors: 0` |
| No offensive residue | No profile, skill, workflow, tool or config key for offensive research exists in the tree |

Breaking for consumers: a caller of `soc_research_plan` or an installer of a research profile has to stop calling it. Tool count 8 → 7, profiles 9 → 6, skills 40 → 39, workflows 4 → 3.

Not established: the catalog admission itself (repository is private, owner decision open), and any hackathon-specific requirement, which is not part of this repository.

## Release 0.1.6: metadata-only workspace member

The plugin shipped a `[build-system]` (setuptools). Hermes materialises every enabled plugin as a member of one dependency workspace per installation — `pm/plugins_state.py::dependency_homes` returns the default home plus every live profile — and uv identifies a member by `[project].name`. A buildable member keeps that name (`pm/workspace.py::_workspace_member` renames only virtual members), so enabling this plugin in two profiles produced two members called `hermes-agentic-soc` and `uv lock` refused:

```
Two workspace members are both named `hermes-agentic-soc`
```

`hermes plugins enable` aborted; the second profile had to carry a local rename in its copy, which in turn made `check-updates` report a phantom update.

0.1.6 removes `[build-system]`. The plugin is a manifest plugin loaded from its directory; it needs no wheel. Hermes now treats it as a virtual member and gives each profile a unique `hermes-plugin-<dir>-<hash>` name.

| Check | Executed result |
|---|---|
| Two live profiles, same plugin, same install root | Both `enable` calls succeeded; no `uv lock` conflict; both report `8 tool(s), 1 hook(s)` |
| `hermes plugins validate .` without the build backend | Validation passed: hooks and middleware match, no collisions, security scan safe, no core override |
| Regression suite | 191 passed |
| Generator | `build_assets.py` idempotent |
| Documentation checker | PASS |
| Loading path | `plugin.yaml` + `register(ctx)` from the plugin directory; no package install involved |

Not established: whether `pip install .` on this tree still works — it is not part of the documented workflow. If a wheel is ever needed, restore `[build-system]` **and** accept that only one profile per installation may enable the plugin.

## Release 0.1.5: corrections from the harvest and local-only validation

A patch release on top of 0.1.4. It restores two skill paragraphs the harvest dropped, and removes hosted CI in favour of the local gate.

| Content | Status |
|---|---|
| `thor-module-analysis/SKILL.md`: an AmCache `first_run` is not per-file execution time; count distinct values and bucket sizes before dating an execution, and never read a `$Recycle.Bin` path as proof of where a program ran | Restored from `soc-thor-assessment` |
| `thor-timeline-correlation/references/timestamp-semantics.md`: every `accessed` time inside the scan window is an artefact of the scan itself; same distribution check on the AmCache `first_run` row | Restored from `soc-thor-assessment` |
| `.github/workflows/test.yml` removed, Actions disabled in the repository settings | No hosted CI |
| `CONTRIBUTING.md`: local validation policy — checks run before every push, a failing local run blocks, no workflow without an owner decision | Documentation |

| Check | Executed result |
|---|---|
| Regression suite | 191 passed |
| Generator | `build_assets.py` idempotent |
| Documentation checker | PASS: 22 Markdown files, 195 local targets, 3 brand PNGs |
| Plugin Doctor (Hermes 0.23.0) | 8 tools, 1 hook |
| Catalog validation | Validation passed |
| Drift after both harvests | `harvest_profile_skills.py`: the repository is a superset of both profiles |

Why the correction was needed: one commit took the `soc-dfir-thor` version of two files wholesale instead of merging both profiles. The re-run of the drift report after the merge caught it — which is the behaviour the workflow in `docs/SKILL-UPDATE-WORKFLOW.md` prescribes.

No hosted CI exists in this repository. Every figure above comes from a local run on Python 3.14.9 and Hermes Agent v0.23.0; nothing is inferred from a runner.

## Release 0.1.4: harvest of profile skill lessons, update workflow, Hermes floor

Version 0.1.4 brings back what two running SOC profiles learned while working real exports, and defines how that traffic happens from now on.

| Content | Status |
|---|---|
| THOR skill lessons from `soc-dfir-thor` (tool path): output-shape intake, `--lookback` semantics, max file size, behavioural coverage, Eventlog/EVTX double count, per-rule match cap, Sigma titles in `DESCRIPTION_1`; four new references and four inventory scripts | Implemented |
| THOR skill lessons from `soc-thor-assessment` (no-tool path): `references/export-inventory.md`, fallback for an exposed-but-refusing tool, artefact-family grouping, "quantify an all N claim" | Implemented |
| `docs/SKILL-UPDATE-WORKFLOW.md` — repo-first authoring, harvest, review gates, distribution including the gateway restart | Documentation |
| `scripts/harvest_profile_skills.py` — dry-run drift report, `--write` into the repository only | Tooling |
| Hermes minimum lowered from 0.23.1 to 0.23.0 after registration and real tool execution on 0.23.0 | Implemented |

| Check | Executed result |
|---|---|
| Regression suite (Python 3.14.9) | 191 passed |
| Generator | `build_assets.py` idempotent; hand-authored THOR skills validated, never overwritten |
| Documentation checker | PASS: 22 Markdown files, 195 local targets, 3 brand PNGs |
| Plugin Doctor, Hermes 0.23.0, repository checkout | Passed: 8 tools, 1 hook |
| Catalog validation `hermes plugins validate .` | Validation passed: declared hooks and middleware match, no tool collisions, security scan safe, no core override |
| Boundary gate | A path outside `evidence_roots` refused with `BOUNDARY_REJECTED`; the case continued only on a byte-identical copy inside the allowed root |
| Drift after the harvest | `harvest_profile_skills.py` reports the repository as a superset; no lesson exists only in a profile |

Two profiles edited the same fallback block of `thor-assessment/SKILL.md`. They are complementary (tool path vs. no-tool path), so both survive in that order; the merge is recorded in the pull request.

Not established: the behavioural quality of the new guidance on a specific model, a licensed THOR Enterprise or Lite run, and hosts outside the verified versions.

## Hermes minimum version: 0.23.0

The declared minimum is 0.23.0. The package uses only documented registration, configuration and storage seams, and the earlier `>=0.23.1` floor blocked registration on a 0.23.0 host without a demonstrated API dependency. The floor was lowered after registering and exercising the plugin on such a host.

| Check | Executed result |
|---|---|
| `hermes plugins doctor . --ci` on Hermes 0.23.0 | Passed: 8 tools, 1 hook |
| `hermes plugins validate .` | Validation passed: declared hooks and middleware match registrations, no built-in tool collisions, security scan safe, no core override |
| Tool execution on 0.23.0 | `soc_capabilities`, `thor_parse` and `thor_first_assessment` ran against a 4,023-event THOR 10.7.31 JSON v2 export; inventory reproduced (4,023 events, 4,022 observation groups, INFO 3,848 / WARNING 129 / NOTICE 46), Verdächtig / P3 / MEDIUM |
| Boundary enforcement | A path outside the configured `evidence_roots` was refused with `BOUNDARY_REJECTED`; the run continued only on a byte-identical copy inside the allowed root |
| Regression suite | 191 passed |

Not established: behaviour on Hermes builds older than 0.23.0, and any API surface introduced after 0.23.0 — the plugin does not use one, but that is an inspection result, not a runtime test.

## Release 0.1.3: THOR analysis suite and profile personas

Version 0.1.3 adds a nine-skill THOR analysis suite with eight reference files, a synthetic multi-module worked example and rewritten, role-specific SOUL.md templates for all nine profiles. Tools, hooks, slash commands, the assessment policy and runtime boundaries are unchanged; `policy_version` remains `0.1.2`.

| Check | Executed result |
|---|---|
| Python 3.14.8 regression suite | 191 passed (`v013-python314.txt`) |
| Python 3.11.17 regression suite | 191 passed (`v013-python311.txt`) |
| Agent Skills validator | All 36 skill directories valid (`v013-skills.txt`) |
| Skill contracts | Frontmatter, size, links, tool and skill references, no long hex strings, safety phrases and nine-section order tested for all THOR skills |
| Worked example against real tools | `examples/analysis/thor-multimodule.json`: 7 events, 7 automatic groups, ALERT 2 / WARNING 2 / NOTICE 2 / INFO 1, Verdächtig P2; SHIMCache-without-hash stays separate; numbers in the worked example asserted by tests |
| SOUL contracts | All nine SOULs: required sections, shipped skills match `skills.txt`, common boundaries present, gated-preview rules and credits correct |
| Generator | `scripts/build_assets.py` is idempotent (identical tree hash after a second run) and validates the hand-authored skills |
| Hermes `skill_view` (real host, scratch home) | Plugin enabled; 36 `agentic-soc:` skills registered; `thor-assessment` lists its three references; `worked-example.md` and `modules.md` served via `file_path` |
| Profile provisioning (real Hermes CLI, scratch home) | `dfir-compromise-assessment` created; new SOUL.md installed, default SOUL backed up, 36 skills and 8 reference files copied |
| Plugin Doctor, fresh home | Passed; 8 tools, 1 hook (`v013-doctor.txt`) |
| Catalog validation `--install-deps`, fresh home | Validation passed: declared tools/hooks match, security scan safe, no core override. The host again printed `dependency preparation failed: Dependency inputs changed while preparing publication; retry.` before validating; as in 0.1.2 this is not a clean dependency-preparation pass (`v013-catalog.txt`) |
| Documentation checker | 194 local targets across 21 Markdown files passed |
| Documented CLI example | `python -m agentic_soc assess …/thor-multimodule.json` returned 7 events, 7 groups, Verdächtig, P2 |

Not established: the skills' behavioural quality with a specific model on real customer data, a licensed THOR Enterprise or Lite run, and Windows/macOS hosts. The skills guide reasoning; they do not add parser support for THOR JSON v3, text logs or the legacy CSV.

## README navigation and badge refinement

The README refinement adds six locally stored static SVG badges, linked topic tags and explicit official-company links in both language versions. No runtime, registration, repository visibility or license change is included.

| Check | Executed result |
|---|---|
| Python 3.14.8 regression suite | 158 passed |
| Python 3.11.17 regression suite | 158 passed |
| Offline documentation checker | 181 local file targets across 20 Markdown files passed |
| Badge tests | Six accessible, self-contained SVGs parsed; version label matches `plugin.yaml` |
| GitHub Markdown API | Both README versions rendered; English output retains the three linked logos, six linked badges and company links |
| Badge visual inspection | Two-row badge montage inspected for clipping and contrast |
| Company destinations | CyStrat, Nextron Systems and exploit labs official homepages fetched successfully |
| Whitespace validation | `git diff --check` passed |

Badge values are static documentation labels, not live service or CI monitors. Local file checks do not validate renderer-specific fragment anchors; successful homepage fetches are a point-in-time check, not ongoing availability monitoring.

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

Logs are prefixed `review-v012-` in `docs/validation/`. Python 3.12/3.13 and Windows/macOS were not locally executed for this review. No hosted CI is used in this repository, so there are no runner results to compare against.

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

The source and test logs are stored under `docs/validation/`. The project targets Python 3.11–3.14; only the two versions listed above are claimed as locally executed, and no hosted CI exists to cover the others.

## Inspected host and environment

Hermes upstream revision: `b1a6350602383fdbed9b0bd0eb15d86eaa335da8`. The declared minimum is `v0.23.0`: the package uses only documented registration, configuration and storage seams, and registration plus tool execution were verified on a 0.23.0 host (see below). The native package uses only documented registration/config/storage seams ([plugin API](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)).

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
