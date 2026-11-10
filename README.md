# Hermes Agentic SOC

Evidence-first cybersecurity specialists for Hermes Agent, built by **CyStrat Services × Nextron Systems**. The MVP provides native tools, deterministic THOR export assessment, reviewable research plans, reusable personas and explicitly labelled technology scaffolds.

Version 0.1.0 targets Hermes >=0.23.1 and Python >=3.11 for the standalone engine. Hermes itself may require a newer Python version. This is an MVP, not an autonomous incident commander or a replacement for a forensic investigation.

## License status

**Proposed license: Apache-2.0. Final approval is pending.** `LICENSE` deliberately grants no provisional open-source rights. Public source visibility is not a license grant. Do not label this release Apache-2.0 or OSI-open-source until the rights holders approve and replace `LICENSE`, `plugin.yaml` and `NOTICE` together. This is a release blocker, not a hidden TODO.

The partners' joint-publication permission has been confirmed by the project sponsor. That does not grant redistribution rights for THOR executables, signatures, licenses, private rules or third-party content.

## What works and what does not

| Component | Status |
|---|---|
| Seven native Hermes tools, three slash commands, approval policy hook | Implemented |
| THOR JSON v1/v2, JSON arrays, event wrapper and NDJSON import | Implemented, synthetic-fixture tested |
| Counts, same-artifact observation grouping, German case JSON/Markdown | Implemented, deterministic |
| THOR launcher | Implemented; separately installed local executable required, actual vendor-binary scan not tested here |
| Six defense personas and eight workflow/domain skills | Shipped |
| Three offensive/purple-team personas | Planning scaffolds; scope-gated, no target interaction |
| Twenty technology-specific skills and MCP descriptors | Scaffolds, no live SIEM/SOAR/EDR/TI integration |
| Four workflow references | Declarative YAML references, not an executable workflow engine |
| Containment, blocking, rule deployment, ticket posting | Not implemented; draft-only |
| THOR v3, legacy text/CSV, full forensic correlation | Not supported in 0.1.0 |

No THOR executable, rules, signatures or license files are included or downloaded by the plugin. Obtain THOR separately from the [official Nextron THOR Lite page](https://www.nextron-systems.com/thor-lite/). That page currently reserves third-party networks and paid engagements for THOR Enterprise; confirm your specific partner license with Nextron before using customer systems ([Nextron licensing information](https://www.nextron-systems.com/thor-lite/)).

## Install

Install the repository at a reviewed full commit SHA, then enable it explicitly. Hermes supports a full-SHA pin and separate enablement through the [plugin system](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins).

```bash
hermes plugins install CyStrat-Services-GmbH/hermes-agentic-soc --no-enable
hermes plugins enable agentic-soc
hermes plugins doctor agentic-soc --ci
```

For a pinned install, add `--ref` followed by the 40-character SHA published with the release. `/plugins` and the tool picker in a new Hermes session should show `agentic_soc` tools once enabled; a full interactive provider-backed chat is not part of the offline test.

The package is a native `plugin.yaml` / `register(ctx)` plugin. It deliberately has no root `plugin.json` or root `mcp.json`: no portable package or MCP process is auto-started, and native skills must not be registered twice.

## Quick offline demonstration

```bash
git clone https://github.com/CyStrat-Services-GmbH/hermes-agentic-soc.git
cd hermes-agentic-soc
python examples/demo/run_demo.py --output /tmp/hermes-agentic-soc-demo
```

The supplied fixture is synthetic, contains no malware and produces exactly **4 source events and 3 correlated observation groups**. One group combines two observations about the same artifact; one is process context and one is an informational record. These are observation groups, not three proven security incidents.

In a Hermes session, use absolute paths:

```text
/soc-templates
/thor-assess /absolute/path/hermes-agentic-soc/examples/demo/thor.json
/thor-scan {"target":"/absolute/operator-approved/directory","execute":false}
```

`/thor-assess` returns a minimised report preview and private report paths. No source evidence is uploaded by this plugin, but any tool output may enter the active Hermes model's conversation; use an appropriate local or approved provider.

## Operator configuration

Merge only these settings into the intended profile's `config.yaml`. Replace example absolute paths with your installation and evidence directories; keep evidence roots narrow.

```yaml
plugins:
  entries:
    agentic-soc:
      enabled: true
      settings:
        thor_path: /opt/nextron/thor-lite/thor-lite-linux
        evidence_roots:
          - /srv/ir/case-2026-001
        scan_roots:
          - /srv/ir/lab
        scan_timeout: 900
```

The binary path is operator-supplied, not an assumed vendor filename. On Windows use absolute Windows paths. With no `thor_path`, the scan tool provides the official acquisition URL; with no `scan_roots`, scan preparation/execution is refused.

The launcher runs `--help` first and verifies exact options. It limits the MVP to `--module FileScan`, a specific `--path`, JSON v2 output and private run-local outputs, with `--suppresspi --nolog --nocsv`. `--path` alone is not a module boundary, so it must not be used to imply process-scan containment ([THOR flags](https://thor-manual.nextron-systems.com/en/latest/usage/flags.html)).

The live scan request uses `execute:true` only to request execution. The `pre_tool_call` hook returns Hermes's `approve` directive, which escalates to the host human-approval gate; the plugin does not approve itself ([Hermes hook API](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)). Do not run sensitive actions in an unattended/auto-approved host configuration.

`/thor-scan` is deliberately preview-only. The inspected host's low-level `ctx.dispatch_tool` path calls the registry directly, so this package does not use it for scan execution. Request actual execution as a normal agent tool call through the host approval pipeline; other fully trusted plugins and direct library calls are outside this authorization boundary.

## Tools and profiles

| Tool | Purpose |
|---|---|
| `soc_template_list` | List all nine role templates, status and workflow |
| `soc_template_install` | Preview or create a new `soc-` profile via `hermes profile create --no-credentials` |
| `thor_lite_scan` | Probe local THOR capabilities, or request a human-approved FileScan |
| `thor_parse` | Strict allowed-root import, exact event inventory and artifact grouping |
| `thor_first_assessment` | Deterministic first assessment and nine-section German case report |
| `soc_alert_triage` | Supplied-evidence triage, no remote enrichment |
| `soc_research_plan` | Structurally validate declared authorization scope and draft a lab/research plan |

Defense roles: `soc-l1-triage`, `soc-l2-incident-responder`, `threat-hunter`, `dfir-compromise-assessment`, `detection-engineer`, `vulnerability-manager`. Research scaffolds: `red-team-planner`, `adversary-emulation`, `purple-team-validator`.

Profile installation uses only documented CLI commands, never private profile-store imports. A successful new-profile create is followed by path discovery from the labelled `profile show` output; the plugin fails closed if that public CLI format changes. It replaces only the newly seeded default persona, preserving it as `SOUL.hermes-default.md`, and copies shipped skills. Existing profiles are never overwritten.

Configure model/auth and enable the plugin in the new profile explicitly. The plugin itself does not read or write `.env`, `auth.json`, CLI token stores or OAuth credentials; Hermes owns profile creation and credential semantics ([profile documentation](https://hermes-agent.nousresearch.com/docs/user-guide/profiles)).

Important integration finding: `--no-credentials` prevents copying keys/model, but the inspected Hermes implementation still permits default-root subscription-auth fallback. Do not treat it as credential isolation. The plugin therefore reports `credential_isolation:false`, disables bundled-skill seeding/alias creation, and explicitly passes the active host-derived `HERMES_HOME` to CLI children rather than relying on process-global multiplexed state. Use an independently isolated Hermes root/OS runtime when strict account separation is required.

## Assessment policy

- **Counts:** Every imported structured event is counted, including INFO and unknown scores. Observation groups use host, scan and typed artifact context; records without a reliable artifact key remain independent.
- **Scores:** Default bands are NOTICE >=40, WARNING >=60 and ALERT >=81, but an explicit source level takes precedence because THOR permits custom thresholds. Individual reason scores are never summed to fabricate the object's final score ([THOR CLI](https://thor-manual.nextron-systems.com/en/latest/usage/flags.html)).
- **Evidence:** Confirmed means a scanner observation exists in the supplied export. A suspicious interpretation remains a Strong Indicator; execution, initial access, attribution, lateral movement and successful remediation are Not Derivable without other evidence.
- **Verdicts:** ALERT leads to provisional P2/HIGH triage, not an automatic confirmed compromise. WARNING/NOTICE leads to P3/MEDIUM; informational-only input is Inconclusive, never clean-host assurance.
- **Time:** Detection timestamps are not attack timestamps. Artifact metadata is separately labelled, never treated as proof of execution.
- **ATT&CK:** No automatic mapping from arbitrary rule text or IDs. Analyst-supported mapping is intentionally deferred.

JSON v2 is open-ended, and THOR 11 introduces a different v3 object model; this release refuses v3 instead of silently misparsing it ([Nextron JSON definitions](https://github.com/NextronSystems/jsonlog)).

## Technology and MCP expansion

`templates/registry.yaml` contains all twenty requested technology entries. Each has its own skill with a query starter or structured query plan, an inactive MCP descriptor and explicit scaffold status.

Splunk and Elastic have vendor-documented MCP offerings; no credentials, tenant endpoint or automatic connection is bundled ([Splunk MCP setup](https://help.splunk.com/en/splunk-enterprise/mcp-server-for-splunk-platform/2.0/connecting-to-the-mcp-server-and-settings), [Elastic Agent Builder MCP](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/mcp-server)). For all other entries, official MCP status is recorded as not verified, not asserted absent.

An opt-in native Hermes MCP configuration must use `trust: untrusted`, a narrow tool allowlist and server-side read-only RBAC. Trust is not a complete read-only control; Hermes may permit tools marked `readOnlyHint:true`, so audit annotations and privileges ([Hermes MCP trust semantics](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)). A template, prompt or SOUL cannot enforce authorization across unrelated tools.

Elastic's Nextron integration is a separate THOR Cloud API ingestion path supporting unencrypted v2 `thor.json` logs, not a bundled arbitrary-local-file importer ([Nextron THOR Cloud integration](https://www.elastic.co/docs/reference/integrations/nextron_thor_apt_scanner)).

## Security disclosure

- **Network:** No direct network calls, telemetry, self-updater or hidden LLM calls. Profile CLI operations may perform Hermes-owned initialization; independently enabled MCP servers are outside this package.
- **File reads:** Explicit input evidence under operator-approved roots; symlink escapes and common credential files/stores are refused. Evidence limit 50 MiB / 100,000 events. Local THOR reads the explicitly authorized FileScan target.
- **Subprocesses:** Configured executable `--help`, then optionally its fixed-argv scan; `hermes profile create/show` for approved profile creation. No shell command strings, sudo or inherited provider tokens.
- **State:** Normalized events, case reports, scanner output, a pseudonym salt and metadata-only audit JSONL under profile-scoped `plugin_data_dir("agentic-soc")`. No stored external credentials.
- **Privacy:** Structured data minimisation and HMAC host pseudonyms are best effort, not guaranteed anonymisation or automatic GDPR compliance. Review all outputs and raw scan data before sharing. Directory permissions depend on the host OS and filesystem.
- **Approvals:** Host-owned approval for execution/profile creation. No write-capable remote connectors or external ticket writer. Do not bypass host guards using direct Python calls.
- **Audit:** Started/completed/rejected metadata, generated IDs and error classes only; raw arguments and evidence are not logged. Local JSONL is not tamper-proof or a legal chain-of-custody system.

See [SECURITY.md](SECURITY.md), [architecture](docs/ARCHITECTURE.md) and [open issues](TODO.md).

## Development and validation

```bash
python -m pip install 'pytest>=8,<10' 'jsonschema>=4.18,<5' 'PyYAML>=6,<7'
python scripts/build_assets.py
python -m pytest -q
hermes plugins doctor . --ci
hermes plugins validate . --install-deps
```

Runtime dependencies are Python standard library only. Optional test/build dependencies have upper bounds; CI matrix results must be distinguished from locally executed tests. See `docs/VALIDATION.md` for the actual results and test environment of this build.

## Roadmap and contribution

License approval and a real separately licensed THOR smoke test come first. Next are fixture-backed v3 support, stronger event-log correlation, evidence-retention controls, independently validated live read-only connectors and host-tested write approval flows. Do not promote a scaffold to `mvp` without tests and an accurate disclosure.

Add profiles, workflows, connector descriptors and skills through `scripts/build_assets.py`, regenerate, test and open a focused PR. See [CONTRIBUTING.md](CONTRIBUTING.md). Do not commit customer logs or vendor assets.

## Deutsch

Hermes Agentic SOC wird gemeinsam von CyStrat Services GmbH und Nextron Systems GmbH entwickelt. Der Schwerpunkt dieses MVP liegt auf nachvollziehbarer SOC-Triage, Spezialisten-Profilen, Skills und einer regelbasierten Erstbewertung von THOR-JSON-Exporten.

THOR Lite wird separat von Nextron bezogen und lokal konfiguriert. Scanner, Signaturen, private Regeln und Lizenzdateien sind weder Bestandteil des Plugins noch werden sie automatisch heruntergeladen. Die Erlaubnis zur gemeinsamen Veröffentlichung ersetzt keine Freigabe zur Weitergabe dieser Komponenten.

Die sechs Defense-Profile sind ausgearbeitet; drei Research-Profile und alle zwanzig Technologieanbindungen sind klar gekennzeichnete Vorlagen. Das Plugin greift damit noch nicht live auf Kundensysteme zu. Es erstellt Berichte und Entwürfe, aber führt keine Isolation, Blockierung oder Ticketveröffentlichung aus.

Die Code-Lizenz bleibt bis zur finalen Freigabe offen. Apache-2.0 ist nur vorgeschlagen. Ein öffentlicher Quellcode ist ohne Lizenzfreigabe noch keine abgeschlossene Open-Source-Veröffentlichung.
