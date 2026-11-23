# Migration: the L2 role split

`soc-l2-incident-responder` no longer exists as a shipped template. It is
replaced by two roles with separate decision rights:

| New profile | Owns | Does not own |
|---|---|---|
| `soc-l2-analyst` | Independent validation, classification, scope, impact, priority and the incident **recommendation** | Containment, coordination, communication, execution |
| `soc-incident-handler` | Response **options**, evidence custody, sequencing, rollback design, approval tracking and coordination | The decision to execute; the approval itself |

The split exists because one persona cannot both investigate and run a
response: the investigation is graded on being right, the response on being
safe and reversible. A single role that recommends and then executes its own
recommendation has no second opinion in the loop.

## What changes for an existing installation

Nothing is overwritten. `soc_template_install` only creates new profiles and
never modifies an existing one. An installation created from the old template
keeps its `SOUL.md`, its skill snapshot and its name.

That means an existing `soc-l2-incident-responder` profile keeps working — with
the old, merged role contract. Decide per installation:

1. **Keep it as a legacy profile** and stop using it for new cases. It is not
   in `soc_template_list` any more, so it will not receive template updates.
2. **Create the successors** and retire the old profile once its open cases are
   handed over:
   ```
   soc_template_install(template="soc-l2-analyst",     name="soc-l2",  execute=false)   # dry run first
   soc_template_install(template="soc-incident-handler", name="soc-ih", execute=false)
   ```
3. **Copy nothing by hand between the profiles.** Reinstall the successor
   templates; a hand-copied SOUL silently keeps the old merged contract.

## What is not migrated automatically

- **Skill snapshots.** `templates.py` copies `skills/` at creation time. An
  existing profile keeps the skills it was created with. `scripts/harvest_profile_skills.py`
  documents the current refresh behaviour; do not assume a plugin update
  refreshes an installed profile's skills.
- **Case history and tuning notes** in the operator's own case system. Those
  are not part of this repository.
- **Model and credential configuration.** Configure the successor profile
  explicitly; `--no-credentials` prevents key copying and is not credential
  isolation.

## Verification after migrating

1. `soc_template_list` shows seven templates and no `soc-l2-incident-responder`.
2. The new profile's `SOUL.md` contains `## Handoff contract` and
   `## Emergency path`.
3. `skills.txt` in the new profile lists the leading skill
   (`soc-l2-investigation` or `incident-response`), not `alert-triage`.
4. A synthetic case is passed L1 → L2 → handler, and the handler explicitly
   declines to execute anything without a named human approver.
