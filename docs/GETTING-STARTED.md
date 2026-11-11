[Project overview](../README.md) / [Documentation](README.md) / Getting started

# Getting started

Start with the offline demonstration to understand the output before granting access to real evidence. Native Hermes installation is a separate step and does not install THOR or activate a remote connector.

## Prerequisites

- **Offline engine:** Python 3.11 or newer and an authorized checkout of this private repository. No third-party runtime package is required.
- **Native plugin:** Hermes `>=0.23.1`; use the Python version required by your Hermes installation, which may be newer than the standalone engine's minimum.
- **Real scans:** A separately acquired, appropriately licensed THOR executable. The offline demonstration does not need it.

Read the [license status](../README.md#license-and-release-status) and [security model](../SECURITY.md) before use. The [validation record](VALIDATION.md) lists the host revision and actual acceptance limits.

## Run the offline demonstration

From the repository root:

```bash
python -m agentic_soc demo --output /tmp/hermes-agentic-soc-demo
python -m agentic_soc capabilities --technology cystrat-soc-suite
```

The demo imports the synthetic fixture and creates a private report bundle. Expect 4 source events, 3 observation groups and a provisional suspicious/P2 assessment; this is not a real scan or proof of compromise.

The bundle includes `normalized.json`, `case.json` and a German `report.md`, with report paths returned by the command. Re-running an assessment can create additional case output; inspect returned paths rather than assuming a fixed case directory.

## Install in Hermes

Use an approved full commit SHA for reproducibility. Replace the shell variable below with the reviewed 40-character commit identifier; GitHub access to the private repository is required.

```bash
REVIEWED_COMMIT="<approved-40-character-commit-sha>"
hermes plugins install CyStrat-Services-GmbH/hermes-agentic-soc \
  --ref "$REVIEWED_COMMIT" --no-enable
hermes plugins enable agentic-soc
hermes plugins doctor agentic-soc --ci
```

Installation and enablement are separate operations in the [Hermes plugin system](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins). Do not treat successful offline tests as proof of an interactive provider-backed session or a working scanner.

In a new Hermes session:

```text
/soc-capabilities
/soc-templates
```

The inventory must show planned integrations as planned, not connected. There is no root portable `plugin.json` or auto-started root MCP process.

## Allow a narrow evidence directory

Merge the following into the intended profile's `config.yaml`, substituting your approved absolute directory. Do not replace the rest of the profile configuration.

```yaml
plugins:
  entries:
    agentic-soc:
      enabled: true
      settings:
        evidence_roots:
          - /srv/ir/case-2026-001
```

Then assess an approved local export:

```text
/thor-assess /srv/ir/case-2026-001/thor.json
```

The standalone alternative is:

```bash
python -m agentic_soc assess /srv/ir/case-2026-001/thor.json \
  --output /tmp/soc-case
```

The standalone command authorizes the explicit input file's parent for that invocation only. It does not execute THOR or bypass a Hermes approval gate for sensitive execution.

## Before scanning or creating profiles

Read the [operator guide](OPERATOR-GUIDE.md) for `thor_path`, `scan_roots`, timeouts, CLI probing and profile provisioning. `/thor-scan` only previews; actual execution must use a normal agent tool call through Hermes's approval pipeline.

The inspected Hermes host's `--no-credentials` profile option is not a guarantee of credential isolation. Use an independently isolated Hermes root or OS runtime where strict account separation is required.

## Troubleshooting

| Symptom | Check |
|---|---|
| Private repository cannot be cloned | Confirm authorized GitHub access; do not make the repository public as a workaround |
| Tools do not appear | Confirm the intended profile, explicit plugin enablement and a new Hermes session; run Plugin Doctor |
| Evidence import is refused | Use an absolute supported JSON/NDJSON file beneath an approved root; check symlinks, size and credential-file restrictions |
| THOR is unavailable | Configure the separately obtained executable; the plugin does not download it |
| Scan execution is refused | Check approved roots and host approval; do not use direct Python calls to bypass controls |
| Research planning is refused | Preview is off by default; opt-in does not remove scope requirements or confer legal authorization |
| Dependency preparation warns during validation | Read the disclosed upstream preparation warning in [VALIDATION.md](VALIDATION.md); do not report a clean installation from exit status alone |
