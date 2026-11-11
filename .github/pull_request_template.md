## What changes

<!-- One sentence on the behaviour, not on the files. -->

## Why

<!-- The problem, the incident, the issue, the reviewer comment. -->

## Which rule or boundary it touches

- [ ] Tool surface (`provides_tools` / `provides_hooks` changed → the manifest, the
      catalog entry and `tests/test_core.py` change together)
- [ ] Security boundary (`agentic_soc/security.py`, `runtime.py`, `audit.py`)
- [ ] Disclosure (a behaviour changed that the README's *Security disclosure* table describes)
- [ ] Profile templates or skills (generated from `scripts/build_assets.py` — edit the generator)
- [ ] Documentation only

## Checks run

<!-- Paste the real output lines, not a promise. -->

```
python scripts/build_assets.py && git diff --exit-code   # generator idempotent
python -m pytest -q                                      # suite result
python scripts/check_docs.py                             # link check
hermes plugins doctor . --ci                             # tools/hooks
hermes plugins validate . --install-deps                 # catalog checks
```

- [ ] Every command above was executed and its result is quoted
- [ ] No `__pycache__`, `.env`, evidence file or credential is part of this diff

## Release impact

- [ ] No version bump needed (documentation, tests, typo)
- [ ] Version bumped in `plugin.yaml`, `pyproject.toml`, `agentic_soc/__init__.py`,
      `assets/badges/version.svg`, both READMEs and `tests/test_hardening.py`
- [ ] Breaking for consumers (say what stops working)

If this commit lands on `main`, the catalog pin
([`docs/CATALOG-SUBMISSION.md`](docs/CATALOG-SUBMISSION.md)) needs its own re-pin PR —
the catalog installs the exact SHA, not the branch.
