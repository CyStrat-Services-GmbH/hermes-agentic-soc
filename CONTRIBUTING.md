# Contributing

The code license is pending; resolve the release blocker before accepting contributions under an asserted open-source grant. Apache-2.0 is proposed only. Do not submit private rules, customer evidence or vendor assets.

## Extend a template

1. Edit `scripts/build_assets.py`: add a profile, domain skill or technology tuple with an accurate status.
2. Keep descriptions trigger-specific, use quoted YAML frontmatter, and state what the skill must not do.
3. For a vendor MCP claim, fetch and cite the official vendor documentation. Otherwise use `not_verified`, not a guessed command or endpoint.
4. Run the generator, validate all profile/skill references and add positive and negative tests.
5. Run pytest, Plugin Doctor and catalog validation; include actual logs and disclose anything untested.
6. Open a focused PR. Promote `scaffold` to `mvp` only with a real bounded read-only integration test and reviewed threat model.

Run `python scripts/build_assets.py` from the repository root. Generated JSON in `.yaml` files is valid YAML 1.2 and requires no runtime YAML dependency.

No connector may silently enable writes, inherit arbitrary CLI tokens, fetch source-code updates or run arbitrary shell arguments. Any future write action requires a host-owned approval path tested on interactive and unattended surfaces, not an `approved:true` input field.
