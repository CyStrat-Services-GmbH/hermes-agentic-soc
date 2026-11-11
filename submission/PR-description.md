# Add agentic-soc: evidence-first THOR triage and SOC specialists

## Status

Prepared submission text, not a claim that this PR is open or admitted. The repository is PRIVATE by owner decision. Renewed publication approval and license approval remain release blockers. Pin the catalog entry to the actual approved public code commit and re-run validation on that exact tree before submission.

## Functionality and public Hermes surfaces

Hermes Agentic SOC provides seven native tools, three slash commands, one pre-tool approval policy and namespaced skills. It imports supplied THOR JSON v1/v2 evidence, counts all events exactly, groups matching artifact observations and produces deterministic bounded first-assessment JSON/Markdown. It can invoke an independently installed local THOR Lite FileScan and provision a fresh no-credential specialist profile through the public Hermes CLI.

Six defense personas are fully authored; three research personas and twenty-one technology integrations, including CyStrat SOC Suite, remain clearly labelled scaffolds. Four YAML workflow references are declarative guidance, not an executable engine. No UI or automatic MCP startup is claimed. Offensive Security is a planned contribution by exploit labs and managing director Johannes Schönborn, currently only skeleton/marketing metadata and an operator-disabled gated preview.

## Rule 13 disclosure

- Network: no direct external network/LLM calls, telemetry or self-updater. Hermes-owned profile initialization and separately operator-enabled MCPs remain host responsibilities.
- Reads: operator-approved evidence roots, shipped demo and profile-scoped plugin data; local scanner reads the approved FileScan target.
- Commands: fixed argv to configured THOR `--help` and optional FileScan; `hermes profile create --no-credentials` and `hermes profile show` for new profile provisioning. No shell strings or sudo.
- Background processes: none intentionally started. Scanner calls have timeouts; the external executable itself is trusted operator software.
- Credentials: none stored or read by the plugin. No `.env`/`auth.json`/browser/CLI token access.
- State/privacy: local pseudonym salt, minimised metadata audit, normalized events and case reports. Minimisation is best effort, not guaranteed anonymisation.
- Approvals: pre_tool_call escalates scan/profile execution to Hermes human approval. No production write or ticket-posting connector exists.
- Vendor components: no THOR binaries, signatures, private rules or license files. Tool acquired separately by the user.
- Licensing: proposed Apache-2.0 is NOT effective until explicit final approval and metadata update.

## Validation and evidence

Attach the results from docs/VALIDATION.md for the pinned commit. A synthetic offline demo is available at `examples/demo/run_demo.py`; an actual licensed THOR run and an interactive live-model session are not claimed unless separately recorded.

## Maintainers

CyStrat Services GmbH and Nextron Systems GmbH. Joint publication is sponsor-approved; Nous catalog approval and independent vendor-binary redistribution rights are not inferred.

<sub>Created with [Perplexity](https://www.perplexity.ai/computer/tasks/2a9c7307-4e2a-4278-8f44-06c302036905)</sub>
