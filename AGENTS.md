# AGENTS.md

Operating rules for anyone — human or agent — filing work for this repository.
Scope: how work is tracked (Jira + Kanban), how it reaches `main`, and what
"done" means here. Everything else lives in [CONTRIBUTING.md](CONTRIBUTING.md).

## 1. Where this project lives

| | |
|---|---|
| Repository | `CyStrat-Services-GmbH/hermes-agentic-soc` (public, Apache-2.0) |
| Jira project | **CAHDHS** — *CS-Agentic-Hub-Dev-Hermes-Agentic-SOC* (id `10622`, next-gen, cloud id `78ff5b08-2870-4e73-8102-bba62e04899e`) |
| Issue types in CAHDHS | Epic, Story, Task, Bug, Subtask (no custom types) |
| Kanban board | **`hermers-agentic-soc-plugin`** — spelled with an `e`, this is the canonical slug, not a typo |
| Board workdir | the local checkout of this repository (set once on the board, not per card) |
| Catalog entry | `NousResearch/hermes-agent` → `plugin-catalog/agentic-soc.yaml` (pin = released commit) |

**Every card on that board is bound to a Jira issue in CAHDHS, and every issue in
CAHDHS that produces code has exactly one card on that board.** One of the two
alone is an incomplete record: Jira is the system of record for *what* and *why*,
the board is the system of record for *who is working right now*.

## 2. Non-negotiables

- `main` and `dev` are protected: **pull request only**, no direct push, no force
  push, no deletion. Rulesets `protect-main` and `protect-dev` enforce it for
  everyone, including maintainers. `v*` tags cannot be moved or deleted.
- `dev` is the integration branch. `main` carries released states only.
- One pull request per Jira issue. Never bundle unrelated issues into one PR.
- No hosted CI. The local chain is the gate and its output goes into the PR body:
  ```
  python scripts/build_assets.py && git diff --exit-code
  python -m pytest -q
  python scripts/check_docs.py
  hermes plugins doctor . --ci
  hermes plugins validate . --install-deps
  ```
- Generated assets (`skills/**`, `templates/**`, `agentic_soc/schemas/*`,
  `assets/badges/*`) are edited in `scripts/build_assets.py`, never by hand.
  A hand edit shows up as `git diff` after the generator runs.
- Every behaviour change that a user would notice **before** installing is added
  to the `## Security disclosure` table in the README. If the table and the code
  disagree, the table is wrong.
- Released states are pinned in the catalog. Any change landing on `main` needs
  its own re-pin PR under catalog rule 4; the pin never follows a branch.

## 3. Jira: creating an issue

Mandatory on every issue:

| Field | Rule |
|---|---|
| Project | `CAHDHS` — nothing else, no other project for this work |
| Summary | Imperative, specific, no ticket-speak: "Correct the licence badge", not "Badge issue" |
| Description | What hurts, what the fix should achieve, how it is verified. Link the file paths. |
| Assignee | Marc-Kevin Lindner unless the issue names someone else |
| Due date | Always set, ISO `YYYY-MM-DD` |
| Labels | `bot:<profile>` (who executes) **and** `exec:orchestrator|subagents|hybrid` (how it executes) |
| Estimate | **Maximum 2 h per issue.** Anything larger is split into subtasks |
| Parent | A parent that has subtasks carries **no estimate of its own**; the effort is the sum of its children |

```bash
# via the Atlassian MCP server
mcp__atlassian__createJiraIssue(
  cloudId="78ff5b08-2870-4e73-8102-bba62e04899e",
  projectKey="CAHDHS",
  issueTypeName="Task",           # or Story / Bug / Epic / Subtask
  summary="Correct the licence badge on the README",
  description="...",
  additional_fields={"labels": ["bot:dev-tl", "exec:orchestrator"],
                     "duedate": "2026-11-14",
                     "parent": {"key": "CAHDHS-12"}},   # subtasks only
)
```

Rules of thumb that come from experience, not from Jira:

- **No vague tickets.** If the scope is unclear, clarify first — a ticket created
  on a guess is rework with a number.
- **Write the verification into the description** before the work starts. "Is the
  badge correct?" is verifiable; "improve the README" is not.
- **Do not open an issue for work you are about to do in the same minute** unless
  the record has value: regressions, decisions, anything a reviewer will ask about.

### Status workflow

| Transition | Who | When |
|---|---|---|
| To Do → In Progress | whoever picks it up | when the Kanban card goes `running` |
| In Progress → In Review | the implementer | when the PR is open and its checks are quoted |
| In Review → Done | **Team lead only**, after the review is approved | never on a self-report |
| Anything → Blocked | whoever is blocked | with the reason and who can unblock |

A merged pull request is not a status. The review decides, the lead writes it.

## 4. Kanban: creating the card

- **Always pass the board.** `board='hermers-agentic-soc-plugin'`. A card without
  it lands on the default board and is invisible to this project.
- One card per Jira issue. The Jira key goes into the card **title** and into the
  body, so either system can find the other:
  `CAHDHS-14 — Correct the licence badge`
- `workspace_path` stays `NULL` for repository cards: the board's
  `default_workdir` is the checkout, and a per-card path breaks the worktree spawn.
- Body carries the same contract as the Jira description plus the acceptance
  criteria — a worker never has to open Jira to know when it is done.
- Read the card id back after creation and record it in the Jira issue. Two ids,
  one piece of work.

```python
kanban_create(
    board="hermers-agentic-soc-plugin",
    title="CAHDHS-14 — Correct the licence badge",
    assignee="dev-tl",
    body="Jira: CAHDHS-14\n\nProblem: …\nAcceptance: pytest 187 passed, check_docs PASS, badge shows Apache-2.0\n",
    workspace_kind="dir",
    workspace_path=None,
)
```

Status rules: `running` when a worker starts, `review` when the PR is up and the
checks are quoted, `done` only with the Jira issue already at Done. `blocked`
always names the blocker and the person who can clear it — "waiting" is not a
blocker reason.

## 5. The flow, end to end

```
Intake (request, finding, review comment)
  └─ Jira issue in CAHDHS  ── 2 h max, due date, labels, assignee
       └─ Kanban card on hermers-agentic-soc-plugin (same title, Jira key first)
            └─ branch: fix|feat|docs/<slug>   →   PR into dev
                 └─ local chain green, PR body quotes the output
                      └─ review approved  →  merge into dev
                           └─ release PR dev → main, version bumped in 9 places
                                └─ tag vX.Y.Z + release notes
                                     └─ catalog re-pin PR (rule 4)
                                          └─ Jira → Done, card → done
```

A release touches more than the code. The current version string lives in
**13 files**: `plugin.yaml`, `pyproject.toml`, `agentic_soc/__init__.py`,
`assets/badges/version.svg`, `README.md`, `README.de.md`,
`docs/CAPABILITIES.md`, `docs/OPERATOR-GUIDE.md`, `CHANGELOG.md`, the version
assertion in `tests/test_hardening.py`, and the three generated
`templates/workflows/*.yaml` descriptors. The workflow descriptors come from
`scripts/build_assets.py` — bump them there, not in the output. Miss one of the
others and a badge, a test or the manifest disagrees with the release.

## 6. What this repository will not accept

- A commit that adds a THOR binary, signature, rule set or licence file. THOR is
  licensed separately and stays outside this package.
- Offensive-research profiles, skills, workflows or tools. They are planned for a
  later release; see [docs/PLANNED-OFFENSIVE-RESEARCH.md](docs/PLANNED-OFFENSIVE-RESEARCH.md).
- Customer evidence, hostnames, credentials or scan output in any commit, issue,
  PR or screenshot. Use the synthetic demo data in `examples/`.
- A pull request whose description lacks the Jira key, the commands that were run
  and their actual output.
- Direct pushes to `main` or `dev`, force pushes, and "temporary" ruleset bypasses.
