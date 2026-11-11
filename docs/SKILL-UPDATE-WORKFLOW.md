# Skill feedback and update workflow

A SOC profile learns while it works. A lesson about a THOR module, a counting trap or a
false-positive pattern is worth more than the case that produced it — but only if it reaches the
repository, is reviewed there and comes back to every profile that needs it. This page defines that
path. It is deliberately the same path for every skill in this repository: one channel in, one
review, one distribution.

## 1. The five rules

**R1 — Repo-first.** A skill change is authored in the repository, not in a profile. Profiles are
consumers.

**R2 — Profiles are runtime snapshots, not forks.** `soc_template_install` copies `skills/` once,
with `shutil.copytree`, and refuses to overwrite an existing directory. Nothing in `plugins update`
or a restart refreshes that copy. A profile directory is therefore a snapshot taken at install
time; treating it as a place to edit turns it into an untracked fork with no author, no reason and
no rollback.

**R3 — One lesson, one commit, evidence in the body.** A commit says which observation forced the
change, which export or test showed it, and what the skill said before. "Improved wording" is not a
reason; "Amcache `first_run` is not per-file execution time, seen on a 4,023-event export" is.

**R4 — One copy per profile.** The plugin registers the same skill names from its own `skills/`
directory live. If a profile additionally holds a second copy under a different directory name
(`skills/agentic-soc.pre-v013.bak`), `skill_view` refuses the name as ambiguous and agents start
editing files through the terminal instead — the exact path that produced the drift this workflow
removes. Old snapshots belong outside `skills/`.

**R5 — No customer evidence in the repository.** Lessons enter the repo as guidance and synthetic
fixtures. Real exports, paths, hosts, accounts and hashes stay in the case directory.

## 2. Roles

| Role | Owns |
|---|---|
| SOC profile (`soc-*`) | Authors the finding during a case: what was misunderstood, what the export showed, what the skill should say instead |
| `dev-tl` (team lead) | Harvests, forms the branch, keeps commits thematic, opens the PR |
| `dev-qa` | Reviews the lesson for correctness and for the four gates below |
| Repo maintainer | Merges, cuts the version, distributes to the profiles |
| Operator | Approves anything that restarts a gateway or widens an evidence root |

## 3. The two channels

**Channel A — case finding.** While working a case the profile may learn something the skill does
not yet say. It records the finding in the case directory, not in the skill:

```markdown
<!-- case-notes/skill-findings.md -->
### F-1 · agentic-soc:thor-assessment
Observation: two Eventlog rows for one Sigma match (Eventlog and EVTX read the same .evtx)
Evidence: 437 finding events → 341 distinct observations on the 2026-07-17 export
Proposed change: dedupe on (EVENT_ID, EVENT_TIME, channel, ruleset, score) before counting
Confidence: confirmed
```

**Channel B — harvest.** The team lead compares profile snapshots against the repository, takes the
findings that are worth generalising and turns them into a pull request. Channel B never trusts the
profile as a source of truth: it re-derives the change against the current `skills/` tree and
reviews it file by file.

## 4. Harvest procedure

```bash
cd ~/projects/hermers-agentic-soc-plugin
git fetch origin && git switch -c dev origin/main    # or continue an existing dev branch

# 1. Drift report — read-only, no writes anywhere
python3 scripts/harvest_profile_skills.py \
  --profile ~/.hermes/profiles/soc-dfir-thor/skills/agentic-soc \
  --profile ~/.hermes/profiles/soc-thor-assessment/skills/agentic-soc

# 2. Take one profile at a time, file by file
python3 scripts/harvest_profile_skills.py \
  --profile ~/.hermes/profiles/soc-dfir-thor/skills/agentic-soc --only thor-assessment --write
git diff                                   # mandatory reading, every file

# 3. Validate, commit, push, open the PR
python scripts/build_assets.py && git diff --exit-code
python -m pytest -q
python scripts/check_docs.py
hermes plugins doctor . --ci
git commit -m "feat(skills): <one lesson>"
git push -u origin dev
gh pr create --base main --head dev --fill
```

Never harvest two profiles into one commit. When both profiles changed the same file, merge them
deliberately and say in the PR which half came from which profile and why both survive.

## 5. Review gates

A harvest PR is reviewed against four questions, in this order:

1. **Correctness** — is the technical claim supported by the cited manual page, the export or a
   test? A skill sentence that generalises one export into a rule is rejected.
2. **Scope** — does it stay inside the skill that owns the topic? Module field knowledge belongs to
   `thor-module-analysis`, triage thresholds to `thor-assessment`, and so on.
3. **Boundaries** — no write action, no widened `evidence_roots`/`scan_roots`, no claim of live
   connectivity, no private Nextron rule or customer artefact.
4. **Contract** — generator idempotent, `check_docs.py` green, `pytest` green, Plugin Doctor reports
   the same tools and hooks as `plugin.yaml` declares.

## 6. Release (dev → main), then distribute

A release is a merge of `dev` into `main`, and it has five parts. Skipping the last three is how `dev` silently falls behind and how a version ends up tagged but not released.

```bash
# 1. the release commit carries the version bump
git switch dev
#    bump plugin.yaml, pyproject.toml, agentic_soc/__init__.py, the badge, both READMEs,
#    CAPABILITIES, OPERATOR-GUIDE, the workflow descriptors and the test assertion
python scripts/build_assets.py && python -m pytest -q && python scripts/check_docs.py

# 2. pull request dev -> main, then merge it
gh pr create --base main --head dev --title "Release X.Y.Z" --body-file <notes>
gh pr merge <n> --merge

# 3. tag on main and publish the release page
git switch main && git pull --ff-only
git tag -a vX.Y.Z -m "Release X.Y.Z" && git push origin vX.Y.Z
gh release create vX.Y.Z --title "…" --notes "…"

# 4. bring dev back onto main -- the merge commit exists only on main
git switch dev && git merge --ff-only origin/main && git push origin dev

# 5. distribute to the profiles (see below)
```

**Step 4 is not optional.** `main` always gains a merge commit that `dev` does not have, so leaving it out shows `dev is 1 commit behind` on every release. `git rev-parse main^{tree}` and `git rev-parse dev^{tree}` must be equal afterwards — equal commits, not just equal content.

A tag without a release page is a half-finished release: `gh release list` is where a reader looks for what shipped. Both are part of step 3.

### Distribution

After the release, the change reaches the profiles only if it is pushed there explicitly:

```bash
hermes plugins update agentic-soc                 # or git fetch + checkout in the install dir
# then refresh the profile snapshot
mv  ~/.hermes/profiles/<p>/skills/agentic-soc \
    ~/.hermes/profiles/<p>/backups/skills-agentic-soc-<date>
cp -a <install-dir>/skills  ~/.hermes/profiles/<p>/skills/agentic-soc
```

Then, in order:

1. **Delete or relocate the old snapshot out of `skills/`** — otherwise the duplicate name makes
   `skill_view` ambiguous (R4).
2. **Restart the gateway** of the profile. Tools and skills are registered when the gateway starts;
   `plugins doctor` can be green while a running session still holds a prompt without any
   `thor_*` tool. `scripts/session_tool_probe.py` inside the profile shows what the current session
   actually received.
3. **Verify** with `soc_capabilities` (version and skill count) and one `skill_view` of a changed
   skill.

## 7. Version and traceability

- The plugin manifest carries the version; a skill change that alters guidance for a shipped
  release bumps it in the same PR.
- Every hand-authored skill lives under `skills/` and is listed in `HAND_AUTHORED` in
  `scripts/build_assets.py`. The generator validates those files and never overwrites them.
- Profile personas are generated from `scripts/profile_souls.py`; `tests/test_thor_skills.py`
  enforces their contract. A persona is never hand-edited in a profile.

## 8. Deutsche Kurzfassung

- **Das Repo ist die Quelle, das Profil ist eine Momentaufnahme.** Der Profilordner
  `skills/agentic-soc` entsteht einmalig per `copytree` und wird von `plugins update` nicht
  aktualisiert.
- **Jede Lektion wird im Repo geschrieben, nicht im Profil.** Während eines Falls notiert das
  Profil den Befund im Fallverzeichnis; der Teamlead überführt ihn in einen Branch und einen PR.
- **Ein Thema pro Commit, Begründung und Beleg im Body**, ein Profil pro Commit, bei Kollisionen
  beide Fassungen bewusst zusammenführen.
- **Prüfkette vor dem Push:** `build_assets.py` ohne Diff, `pytest`, `check_docs.py`,
  `hermes plugins doctor . --ci`.
- **Nach dem Merge aktiv ausrollen:** Profilkopie sichern und ersetzen, den alten Snapshot aus
  `skills/` entfernen (sonst sind Skill-Namen mehrdeutig), Gateway neu starten und mit
  `soc_capabilities` gegenprüfen.
