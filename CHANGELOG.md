# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The catalog installs an exact commit, so the changelog is written per release
and the released commit is the one pinned in the catalog entry.

## [Unreleased]

## [0.2.5] — 2026-11-12

### Fixed
- Three README badges still described an older project: `license.svg` said
  "Pending approval" while the manifest, LICENSE and README all say Apache-2.0,
  `integrations.svg` said 21 planned instead of 25, and `hermes.svg` advertised
  0.23.1 although `requires_hermes` is `>=0.23.0`. They are the first thing a
  visitor sees on the repository page.
- Tests now derive each badge from its source of truth (`plugin.yaml` licence and
  floor, `templates/registry.yaml` count), so a badge cannot drift again without
  the suite failing.

## [0.2.4] — 2026-11-11

### Changed
- README (EN/DE), the preview badge, the integration roadmap and the 0.1.1 review
  record no longer describe the repository as private, and link the open catalog
  PR instead. The plugin README is what a reviewer sees at the pinned commit, so
  a wrong visibility claim there was a review defect, not a wording issue.

## [0.2.3] — 2026-11-11

### Added
- `## Security disclosure` in `README.md` and `README.de.md`: network, commands,
  reads outside the plugin, writes, credentials, background activity and model
  context. Rule 13 of the catalog requires this in the README, not only in
  `SECURITY.md`.
- `docs/CATALOG-SUBMISSION.md` records the submission PR and the hackathon path.

### Fixed
- `README.de.md` no longer claims the licence is awaiting approval.

## [0.2.2] — 2026-11-11

### Changed
- exploit labs is described as a confirmed supporter and cooperation partner.
  The offensive-research capability itself remains unbuilt and out of this
  release — cooperation is agreed, delivery is not.

## [0.2.1] — 2026-11-11

### Changed
- Partnership and contributor statements name companies, not people. The
  generator (`scripts/build_assets.py`, `scripts/profile_souls.py`) is the
  source for the persona footer, so it changed first and every profile SOUL was
  regenerated.

## [0.2.0] — 2026-11-11

### Changed
- **Breaking:** the shipped package is defense-only. Removed the three
  offensive/research profiles, the `authorized-research` skill, the `purple-team`
  workflow, the `soc_research_plan` tool, the `offensive_preview_enabled` config
  key and the scope checker that only that tool used. Tool count 8 → 7,
  profiles 9 → 6, skills 40 → 39, workflows 4 → 3.
- Licence changed from a placeholder to **Apache-2.0**; `NOTICE` separates the
  code and documentation from THOR binaries, signatures and brand assets.
- `requires_hermes` is `>=0.23.0`, and the package ships no `[build-system]`
  block so several profiles can install the same plugin without a uv workspace
  name collision.

### Added
- Vulnerability management as the sixth technology domain (Tenable, Qualys
  VMDR, Rapid7 InsightVM, Greenbone/OpenVAS); CyStrat SOC Suite is documented as
  the cross-domain platform instead of one of the domains.
- `docs/PLANNED-OFFENSIVE-RESEARCH.md` states what a later release will add and
  that nothing of it is present, previewable or enableable now.
- `docs/CATALOG-SUBMISSION.md` maps the catalog admission rules to evidence.

Earlier releases (v0.1.0 – v0.1.6) are documented on
[GitHub Releases](https://github.com/CyStrat-Services-GmbH/hermes-agentic-soc/releases).

[Unreleased]: https://github.com/CyStrat-Services-GmbH/hermes-agentic-soc/compare/v0.2.4...HEAD
[0.2.4]: https://github.com/CyStrat-Services-GmbH/hermes-agentic-soc/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/CyStrat-Services-GmbH/hermes-agentic-soc/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/CyStrat-Services-GmbH/hermes-agentic-soc/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/CyStrat-Services-GmbH/hermes-agentic-soc/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/CyStrat-Services-GmbH/hermes-agentic-soc/compare/v0.1.6...v0.2.0
