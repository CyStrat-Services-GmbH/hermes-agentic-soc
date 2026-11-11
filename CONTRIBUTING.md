# Contributing

The code license is pending; resolve the release blocker before accepting contributions under an asserted open-source grant. Apache-2.0 is proposed only. Do not submit private rules, customer evidence or vendor assets.

## Development checks

Use Python 3.11 or newer for the standalone engine and a separate development environment. The runtime has no third-party dependencies; optional test dependencies are bounded.

```bash
python -m pip install 'pytest>=8,<10' 'jsonschema>=4.18,<5' 'PyYAML>=6,<7'
python scripts/build_assets.py
python -m pytest -q
python scripts/check_docs.py
hermes plugins doctor . --ci
hermes plugins validate . --install-deps
```

The last two commands require a prepared Hermes host. Record actual results and warnings; do not infer a clean install from a zero exit code when dependency preparation reported a failure.

## Documentation standards

- **Product claims:** Distinguish implemented local functionality from planning scaffolds, gated previews and verified live integrations.
- **Navigation:** Keep the [documentation index](docs/README.md), English README and German overview aligned; preserve valid relative links.
- **Brands:** Use only the approved documentation assets with [provenance](assets/brand/README.md). Do not redraw marks or treat the proposed code license as a trademark grant.
- **Evidence:** Keep historical validation logs intact and identify the code/environment actually tested.
- **Security:** Never use customer evidence in examples; write fixtures that exercise refused inputs, scope and approval boundaries.

See the [architecture](docs/ARCHITECTURE.md) before changing registration or state handling. `provides_tools`, hooks and capabilities must continue to match actual registrations.

## Extend a template

1. Edit `scripts/build_assets.py`: add a profile, domain skill or technology tuple with an accurate status.
2. Keep descriptions trigger-specific, use quoted YAML frontmatter, and state what the skill must not do.
3. For a vendor MCP claim, fetch and cite the official vendor documentation. Otherwise use `not_verified`, not a guessed command or endpoint.
4. Run the generator, validate all profile/skill references and add positive and negative tests.
5. Run pytest, Plugin Doctor and catalog validation; include actual logs and disclose anything untested.
6. Open a focused PR. Promote `scaffold` to `mvp` only with a real bounded read-only integration test and reviewed threat model.

Run `python scripts/build_assets.py` from the repository root. Generated JSON in `.yaml` files is valid YAML 1.2 and requires no runtime YAML dependency.

No connector may silently enable writes, inherit arbitrary CLI tokens, fetch source-code updates or run arbitrary shell arguments. Any future write action requires a host-owned approval path tested on interactive and unattended surfaces, not an `approved:true` input field.
