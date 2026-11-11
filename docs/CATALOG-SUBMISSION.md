# Hermes plugin catalog: readiness and evidence

Status: **PR opened, one prerequisite open.** The entry PR is [NousResearch/hermes-agent#154079](https://github.com/NousResearch/hermes-agent/pull/154079), pinned to `ebb3dfd5ebef4e7bbc8943f40c59401313145f07` (v0.2.2). The one unmet prerequisite is repository visibility: the catalog installs by cloning `repo` at the pinned commit, so a private repository cannot be installed and the catalog CI cannot check it. Everything else below is satisfied at the pinned tree.

Every claim below was checked against the tree at commit `main` of this repository and against the admission rules of the Nous Research plugin catalog (`hermes-agent` → `plugin-catalog/README.md`, mirrored at `/docs/developer-guide/plugins/catalog-submission`). The rule numbers follow that page.

## Blocker

| # | Rule | State | What has to happen |
|---|---|---|---|
| — | *Before you submit:* **public repository** | **Private.** `repo` must be an `https://` URL anyone can clone. | Owner decision. Changing visibility is a business decision (license, brand, THOR boundary) and is **not** covered by this document. Everything else below is already satisfied at the pinned tree. |

Submission is a PR adding one file, `plugin-catalog/agentic-soc.yaml`, to `NousResearch/hermes-agent`. The submitted file is kept in [`submission/catalog-entry.yaml`](../submission/catalog-entry.yaml) for review; it stays out of version control (see `.gitignore`) so a stale copy can never be mistaken for the live entry.

## Rule-by-rule

| Rule | Requirement | State in this repository | Evidence |
|---|---|---|---|
| 1 | Human-merged PR | — | Submission path documented here |
| 2 | Exact 40-char SHA pin | Ready, pin chosen at release | `git rev-parse <tag>`; entry field `sha` |
| 3 | No self-updating code | Compliant: no updater, no network fetch, no telemetry | `SECURITY.md`; no `urllib`/`requests` in `agentic_soc/` |
| 4 | SHA bumps as new PRs | Process documented | `docs/SKILL-UPDATE-WORKFLOW.md` §6 |
| 5 | Owner/major-contributor submission | Compliant: CyStrat Services GmbH is the repository owner | `plugin.yaml` → `author`, `homepage` |
| 6 | Declared capabilities match registration | Compliant: `provides_tools` (7), `provides_hooks` (1) match `register()`; `capabilities: []` because no privileged host surface is requested | `hermes plugins validate .` → "declared hooks — matches registrations"; `tests/test_core.py::test_manifest_matches_actual_registration` |
| 7 | Install scanner at admission | Compliant: local run green | `hermes plugins validate .` → "security scan — safe" |
| 8 | Desktop SDK surface | Not applicable: no `desktop/plugin.js` | — |
| 9 | No runtime override of core | Compliant | `hermes plugins validate .` → "no core override — no runtime rebinds of Hermes core" |
| 10 | Dependency policy is the plugin's | Compliant: zero third-party runtime dependencies, standard library only | `pyproject.toml` (no dependencies), `README.md` §Development |
| 11 | Credentials only through Hermes | Compliant: the plugin reads no credential, `.env`, `auth.json` or token store; `thor_path` is an operator-supplied filesystem path, not a secret | `SECURITY.md`; no `get_secret`, no `os.environ` credential reads |
| 12 | Approvals and unattended runs respected | Compliant: the `pre_tool_call` hook returns `approve` and lets the host ask; nothing auto-approves; no child process runs commands | `test_hardening.py` policy tests |
| 13 | Risky behaviour disclosed | Compliant: network, reads, subprocesses, state and privacy are disclosed | `README.md` §Security disclosure, `SECURITY.md` |
| 14 | Truthful compatibility metadata | Compliant: `requires_hermes: ">=0.23.0"` (SemVer floor, not newer than the current release); `version` matches the pinned code | `plugin.yaml`; `docs/VALIDATION.md` §"Hermes minimum version" |
| 15 | No skins or forks of bundled plugins | Not applicable | — |
| 16 | One listing per lineage | Not applicable: no other listing, no fork | — |
| 17 | No unscannable executable payloads | Compliant: no binary, no `.pyc`, no archive in the tree; `.gitignore` blocks them | `git ls-files` shows no binary; `.gitignore` |
| 18 | Password-manager backends only from the vendor | Not applicable: no login backend | — |

## What a reviewer will read

- **Manifest:** `plugin.yaml` — 7 tools, 1 hook, four config keys, no `requires_env`.
- **Entry point:** `__init__.py` → `register(ctx)`, tools registered from `agentic_soc/api.py`.
- **Boundaries:** `agentic_soc/security.py` (allowed roots, credential-file refusal, symlink containment), `agentic_soc/runtime.py` (audit, fail-closed).
- **Tests:** 184 passing locally on Python 3.14.9 (`python -m pytest -q`).
- **Disclosure:** `SECURITY.md`, `README.md` §Security disclosure, `docs/OPERATOR-GUIDE.md`.

## Evidence a reviewer can reproduce

```bash
hermes plugins doctor . --ci          # 7 tools, 1 hook
hermes plugins validate .             # manifest, capabilities, scan, no core override
python -m pytest -q                   # 184 passed
python scripts/check_docs.py          # documentation links
python scripts/build_assets.py && git diff --exit-code   # generator idempotent
```

No hosted CI exists in this repository by decision; every figure above is a local run and the PR states the commands and their output (rule 13 spirit, `CONTRIBUTING.md` §Development checks).

## Open items

1. **Public repository** — owner decision; the only hard prerequisite still unmet.
2. **Pin maintenance** — every change that lands after the pin needs its own re-pin PR (rule 4) with `version` bumped in the same commit.
3. **Screenshots (optional)** — up to six images pinned to the same SHA; the plugin has no UI, so none are required.

## Hackathon submission (separate from the catalog)

The Hermes Agent Plugin Hackathon has its own form; the catalog PR only has to be **open**, not merged.

| Requirement | State |
|---|---|
| Catalog PR opened | [#154079](https://github.com/NousResearch/hermes-agent/pull/154079) |
| Demo under 90 seconds, posted on X, tagging @NousResearch | External — produced outside this repository |
| Both links entered in the official form before 2026-11-11, 17:00 EST (22:00 UTC) | Owner action; the form still served its start screen when checked at 22:05 UTC |

Judging criteria beyond the mechanical checks are qualitative (problem fit, engineering quality, disclosure, documentation). Nothing in this repository can substitute for the demo, so no claim of hackathon completeness is made here.
