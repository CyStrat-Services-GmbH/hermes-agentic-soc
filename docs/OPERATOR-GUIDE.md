[Project overview](../README.md) / [Documentation](README.md) / Operator guide

# Operator guide

This guide is the detailed operational reference for Hermes Agentic SOC v0.2.6. Start with [Getting started](GETTING-STARTED.md) for a short evaluation path, or use the sections below to review configuration, tool behavior and assessment policy.

[Obtain THOR Lite](#obtain-thor-lite) · [Install](#install) · [Offline demo](#quick-offline-demonstration) · [Configuration](#operator-configuration) · [Tools and profiles](#tools-and-profiles) · [Companion skills](#companion-skills) · [Assessment policy](#assessment-policy) · [MCP expansion](#technology-and-mcp-expansion) · [Security](#security-disclosure)

## Operating assumptions

Version 0.2.0 targets Hermes >=0.23.0 and Python >=3.11 for the standalone engine; Hermes itself may require a newer Python version. Use [capabilities](CAPABILITIES.md) for the supported scope, [validation](VALIDATION.md) for executed tests and the [0.1.2 review](REVIEW-0.1.2.md) for detailed findings.

The code is licensed under Apache-2.0. The [integration roadmap](INTEGRATION-ROADMAP.md) describes planned, not live, integrations; [offensive research](PLANNED-OFFENSIVE-RESEARCH.md) is planned for a later release and is not part of this version.

No THOR executable, rules, signatures or license files are included or downloaded by the plugin. Obtain THOR separately as described in [Obtain THOR Lite](#obtain-thor-lite) and confirm your specific license with Nextron before using customer systems.

## Obtain THOR Lite

The operator sets THOR Lite up once, outside the plugin:

1. **Register.** Submit the form on the [THOR Lite page](https://www.nextron-systems.com/thor-lite/) with a business e-mail address. Nextron replies with an e-mail that contains a download link and the license file (`*.lic`) as an attachment. The license is valid for one year; register the same address again to renew it. Once it has expired, THOR stops right after start with exit code 1 and lists the licenses it found, so a scan through the plugin then ends as incomplete ([thor-scan](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-scan/SKILL.md)).
2. **Download** the package for your platform from the link in that e-mail or from the [THOR Lite download page](https://www.nextron-systems.com/download-thor-lite/), which offers Windows, macOS and Linux packages (currently THOR Lite 10).
3. **Unpack** it into its own program folder, for example `/opt/nextron/thor-lite` or `C:\thor-lite`.
4. **Add the license.** Save the `.lic` attachment from the e-mail into that program folder. The download page does not provide it; only the e-mail does. THOR Lite cannot fetch a license from the Management Center or the Customer Portal either. THOR reads every `*.lic` file in the program folder and its subfolders, so a `licenses/` subfolder works too ([editions and licenses](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor/references/editions-and-licenses.md)). THOR can also read a base64-encoded license from the `THOR_LICENSE` environment variable, but the plugin starts THOR with a minimal environment, so that variable never reaches the launcher; use the `.lic` file.
5. **Update the signatures** from the program folder with `thor-lite-util update` (Windows: `thor-lite-util.exe update`). To add the curated public YARA Forge rules once, run `thor-lite-util yara-forge download --ruleset core`; later `update` runs keep them current. `thor-lite-util` needs outbound HTTPS to `update-lite.nextron-systems.com`. YARA Forge rules come from GitHub and use only the `HTTP_PROXY`/`HTTPS_PROXY` environment variables, not the proxy flags of `thor-lite-util` ([thor-maintenance](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-maintenance/SKILL.md)).
6. **Check the version** with `./thor-lite-linux-64 --version`, `thor64-lite.exe --version` or `./thor-lite-macosx --version`, then set `thor_path` to the binary's absolute path ([Operator configuration](#operator-configuration)).

THOR Lite permits internal company use, use by government agencies, education and research on the organisation's own systems. Paid engagements and customer or third-party networks need a commercial THOR license.

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

The review release also includes a standard-library-only CLI:

```bash
python -m agentic_soc profiles
python -m agentic_soc capabilities
python -m agentic_soc capabilities --technology cystrat-soc-suite
python -m agentic_soc demo --output /tmp/hermes-agentic-soc-demo
python -m agentic_soc assess /absolute/evidence/thor.json --output /tmp/soc-case
```

These commands never execute THOR, install profiles or post anything externally. The explicit input file authorizes its parent only for this offline invocation; output still uses private files and structured redaction.

The supplied fixture is synthetic, contains no malware and produces exactly **4 source events and 3 correlated observation groups**. One group combines two observations about the same artifact; one is process context and one is an informational record. These are observation groups, not three proven security incidents.

In a Hermes session, use absolute paths:

```text
/soc-templates
/soc-capabilities
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
        thor_path: /opt/nextron/thor-lite/thor-lite-linux-64
        evidence_roots:
          - /srv/ir/case-2026-001
        scan_roots:
          - /srv/ir/lab
        scan_timeout: 900
```

The binary path is operator-supplied, not an assumed vendor filename. On Windows use absolute Windows paths. With no `thor_path`, the scan tool provides the official acquisition URL; with no `scan_roots`, scan preparation/execution is refused.

The launcher reads the version with `--version`, then checks that the full CLI help lists every flag it uses: `--fullhelp` on THOR 10.7, whose `--help` shows only the most important options, and `--help long` on THOR 11. It supports THOR and THOR Lite 10.7 and 11 and refuses other versions. Each scan is a `--module Filescan` run on one `--path`, with JSON output and private run-local files only:

| | THOR 10.7 | THOR 11 |
|---|---|---|
| JSON log | `--jsonfile=thor.json --jsonv2` (JSON v2) | `--json thor.jsonl` (JSON v3) |
| Output directory | `--rebase-dir <run dir>` | `--output-directory <run dir>` |
| Privacy, no extra files | `--suppresspi --nolog --nocsv --nothordb` | `--no-personal-data --no-html --no-csv --no-thordb` |

THOR 10 takes the optional `--jsonfile` value reliably only with `=` ([thor-skill flag map](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor/references/flag-map-v10-v11.md)). `--nothordb` keeps scan state out of the system-wide ThorDB (`/var/lib/thor`, `%ProgramData%\thor`); without it, a run without root logs an Error. Paths with THOR syntax that would change what is scanned are refused: `:` after the drive, `,` (THOR 11 splits `--path` as CSV), `<…>` placeholders and `$`/`%` variables. `--path` alone is not a module boundary, so it must not be used to imply process-scan containment ([THOR flags](https://thor-manual.nextron-systems.com/en/latest/usage/flags.html)).

The live scan request uses `execute:true` only to request execution. The `pre_tool_call` hook returns Hermes's `approve` directive, which escalates to the host human-approval gate; the plugin does not approve itself ([Hermes hook API](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)). Do not run sensitive actions in an unattended/auto-approved host configuration.

Offensive research is not part of this version. There is no research profile, no research-planning tool and no `offensive_preview_enabled` switch; nothing can be enabled to obtain one. See [the plan](PLANNED-OFFENSIVE-RESEARCH.md).

`/thor-scan` is deliberately preview-only. The inspected host's low-level `ctx.dispatch_tool` path calls the registry directly, so this package does not use it for scan execution. Request actual execution as a normal agent tool call through the host approval pipeline; other fully trusted plugins and direct library calls are outside this authorization boundary.

## Tools and profiles

| Tool | Purpose |
|---|---|
| `soc_template_list` | List all seven role templates, status and workflow |
| `soc_capabilities` | Distinguish implemented functions, planned integrations and configuration presence; optional technology filter |
| `soc_template_install` | Preview or create a new `soc-` profile via `hermes profile create --no-credentials` |
| `thor_lite_scan` | Probe local THOR capabilities (10.7 or 11), or request a human-approved Filescan |
| `thor_parse` | Strict allowed-root import, exact event inventory and artifact grouping |
| `thor_first_assessment` | Deterministic first assessment and nine-section German case report |
| `soc_alert_triage` | Supplied-evidence triage, no remote enrichment |

Shipped roles: `soc-l1-triage`, `soc-l2-analyst`, `soc-incident-handler`, `threat-hunter`, `dfir-compromise-assessment`, `detection-engineer`, `vulnerability-manager`. Analysis and response are deliberately separate profiles: `soc-l2-analyst` investigates and recommends, `soc-incident-handler` prepares the approval-ready response and never executes it. Offensive/research roles are not shipped in this version.

Profile installation uses only documented CLI commands, never private profile-store imports. A successful new-profile create is followed by path discovery from the labelled `profile show` output; the plugin fails closed if that public CLI format changes. It replaces only the newly seeded default persona, preserving it as `SOUL.hermes-default.md`, and copies shipped skills. Existing profiles are never overwritten.

Configure model/auth and enable the plugin in the new profile explicitly. The plugin itself does not read or write `.env`, `auth.json`, CLI token stores or OAuth credentials; Hermes owns profile creation and credential semantics ([profile documentation](https://hermes-agent.nousresearch.com/docs/user-guide/profiles)).

Important integration finding: `--no-credentials` prevents copying keys/model, but the inspected Hermes implementation still permits default-root subscription-auth fallback. Do not treat it as credential isolation. The plugin therefore reports `credential_isolation:false`, disables bundled-skill seeding/alias creation, and explicitly passes the active host-derived `HERMES_HOME` to CLI children rather than relying on process-global multiplexed state. Use an independently isolated Hermes root/OS runtime when strict account separation is required.

## Companion skills

Two separately maintained skill sets own topics this plugin deliberately leaves to their maintainers. The plugin's skills refer to them by name; they are not copied into this repository, so a profile reads the maintainer's current version.

| Skill set | Maintainer | Use for |
|---|---|---|
| [thor-skill](https://github.com/Nextron-Labs/thor-skill) | Nextron Systems | THOR 10.7 and 11 editions and flags (`thor`, `thor-scan`, `thor-lite`), `thor-util` updates and YARA Forge (`thor-maintenance`), custom IOCs, YARA, Sigma and false-positive filters (`thor-custom-signatures`), troubleshooting, deployment and THOR Lens |
| [yara-rule-skill](https://github.com/YARAHQ/yara-rule-skill) | YARAHQ | Writing and reviewing YARA rules: YARA Style Guide, Performance Guidelines, yaraQA issue IDs and YARA-Forge quality gates |

The plugin's THOR skills name the relevant Nextron skill where it helps, for example `thor-maintenance` in `agentic-soc:thor-lite` and `thor-log-analysis` in `agentic-soc:thor-assessment`. If a skill set is not installed, those pointers simply do not apply.

Clone both and add them to the profile's `config.yaml` as external skill directories:

```bash
git clone https://github.com/Nextron-Labs/thor-skill.git ~/src/thor-skill
git clone https://github.com/YARAHQ/yara-rule-skill.git ~/src/yara-rule-skill
```

```yaml
skills:
  external_dirs:
    - ~/src/thor-skill/skills
    - ~/src/yara-rule-skill
```

Keep them current with `git pull` in each clone, then restart the profile's gateway so the new text is loaded.

Both sets ship a skill named `thor-lite`. This plugin's copy is always addressed as `agentic-soc:thor-lite` and governs the plugin's launcher; Nextron's `thor-lite` describes the product. Nextron's `thor-scan` builds command lines for a human operator. Inside a SOC profile, a scan still runs only through `thor_lite_scan` and its human approval, never through a hand-built command line.

## Assessment policy

- **Counts:** Every imported structured event is counted, including INFO and unknown scores. Correlation requires explicit host and scan plus file path/hash, event ID/record ID/channel, or process PID/start time; missing identifiers remain independent. Duplicate observation and score/level disagreement counters expose data-quality limits.
- **Scores:** Default bands are NOTICE >=40, WARNING >=60 and ALERT >=81, but an explicit source level takes precedence. THOR also requires a sub-score above 75 for an alert, so a score of 81 or more can correctly be exported as WARNING; the parser applies the same rule when an export carries no level. THOR 10 additionally permits custom thresholds; THOR 11 does not ([thor-skill scoring](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-log-analysis/references/scoring-and-levels.md)). Individual reason scores are never summed to fabricate the object's final score ([THOR CLI](https://thor-manual.nextron-systems.com/en/latest/usage/flags.html)).
- **Evidence:** Confirmed means a scanner observation exists in the supplied export. A suspicious interpretation remains a Strong Indicator; execution, initial access, attribution, lateral movement and successful remediation are Not Derivable without other evidence.
- **Verdicts:** ALERT leads to provisional P2/HIGH triage, not an automatic confirmed compromise. WARNING/NOTICE leads to P3/MEDIUM; informational-only input is Inconclusive, never clean-host assurance.
- **Time:** Detection timestamps are not attack timestamps. Timezone-aware ISO artifact timestamps are ordered in UTC; invalid or timezone-free values remain in normalized data but are omitted from the timeline with an explicit count.
- **ATT&CK:** No automatic mapping from arbitrary rule text or IDs. Analyst-supported mapping is intentionally deferred.

`thor_parse` reads JSON v2 (THOR 10.7 with `--jsonv2`) and JSON v3 (THOR 11) through separate field maps ([Nextron JSON definitions](https://github.com/NextronSystems/jsonlog)). It refuses JSON v1, which THOR 10 writes when `--jsonv2` is missing, because v1 keeps the reasons in flat `reason_N` keys. THOR 11 ignores `--jsonv2`, so every THOR 11 JSON export is v3. THOR's own status messages (start-up, licence and privilege notices, match limits, the end-of-scan report) are marked `record_kind: message` and never raise the verdict; an ERROR message still prevents a low-risk result. The public THOR Lite download is currently THOR Lite 10 ([thor-skill THOR Lite](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-lite/SKILL.md)).

## Technology and MCP expansion

`templates/registry.yaml` contains twenty-five technology entries. Six domains carry twenty-four templates; **CyStrat SOC Suite** is listed separately because it spans all of them. Each has its own skill with a query starter or structured query plan, an inactive MCP descriptor and explicit scaffold status.

| Planned coverage | Technology templates |
|---|---|
| SIEM | Microsoft Sentinel, Splunk, Elastic Security, IBM QRadar, Google SecOps, Wazuh, Graylog |
| SOAR and case management | TheHive / Cortex, Shuffle, Cortex XSOAR, Sentinel Playbooks |
| EDR, XDR and endpoint investigation | Defender XDR, CrowdStrike, SentinelOne, Velociraptor |
| Threat intelligence | MISP, OpenCTI, VirusTotal |
| Detection engineering | Sigma, YARA |
| Vulnerability management | Tenable Vulnerability Management, Qualys VMDR, Rapid7 InsightVM, Greenbone / OpenVAS |
| Cross-domain platform | CyStrat SOC Suite — spans the six domains above instead of forming one of them |

This is a planned technology and workflow ecosystem, not 25 production connectors. Sigma/YARA are detection toolchains rather than remote SOC services. Live tenant compatibility, endpoints, authorization and data-sharing controls must be verified separately for each integration.

The CyStrat SOC Suite entry includes a dedicated tenant-/case-scoped skill and an explicitly proposed read-only MCP contract. The inspected Suite V2 routes contain no implemented application endpoints; no live MCP endpoint is invented. Integration status remains scaffold until the deployed API, authorization and tenant-isolation tests are available.

Splunk and Elastic have vendor-documented MCP offerings; no credentials, tenant endpoint or automatic connection is bundled ([Splunk MCP setup](https://help.splunk.com/en/splunk-enterprise/mcp-server-for-splunk-platform/2.0/connecting-to-the-mcp-server-and-settings), [Elastic Agent Builder MCP](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/mcp-server)). For all other entries, official MCP status is recorded as not verified, not asserted absent.

An opt-in native Hermes MCP configuration must use `trust: untrusted`, a narrow tool allowlist and server-side read-only RBAC. Trust is not a complete read-only control; Hermes may permit tools marked `readOnlyHint:true`, so audit annotations and privileges ([Hermes MCP trust semantics](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)). A template, prompt or SOUL cannot enforce authorization across unrelated tools.

Elastic's Nextron integration is a separate THOR Cloud API ingestion path supporting unencrypted v2 `thor.json` logs, not a bundled arbitrary-local-file importer ([Nextron THOR Cloud integration](https://www.elastic.co/docs/reference/integrations/nextron_thor_apt_scanner)).

## Security disclosure

- **Network:** No direct network calls, telemetry, self-updater or hidden LLM calls. Profile CLI operations may perform Hermes-owned initialization; independently enabled MCP servers are outside this package.
- **File reads:** Explicit input evidence under operator-approved roots; symlink escapes and common credential files/stores are refused. Evidence limit 50 MiB / 100,000 events. Local THOR reads the explicitly authorized Filescan target.
- **Subprocesses:** Configured executable `--version` and full CLI help, then optionally its fixed-argv scan; `hermes profile create/show` for approved profile creation. No shell command strings, sudo or inherited provider tokens.
- **State:** Normalized events, case reports, scanner output, a pseudonym salt and metadata-only audit JSONL under profile-scoped `plugin_data_dir("agentic-soc")`. No stored external credentials.
- **Privacy:** Structured data minimisation and HMAC host pseudonyms are best effort, not guaranteed anonymisation or automatic GDPR compliance. Review all outputs and raw scan data before sharing. Directory permissions depend on the host OS and filesystem.
- **Approvals:** Host-owned approval for execution/profile creation. No write-capable remote connectors or external ticket writer. Do not bypass host guards using direct Python calls.
- **Audit:** Started/completed/rejected metadata, generated IDs and error classes only; raw arguments and evidence are not logged. Local JSONL is not tamper-proof or a legal chain-of-custody system.

See the [security model](../SECURITY.md), [architecture](ARCHITECTURE.md) and [open work](../TODO.md).

## Development and validation

```bash
python -m pip install 'pytest>=8,<10' 'jsonschema>=4.18,<5' 'PyYAML>=6,<7'
python scripts/build_assets.py
python -m pytest -q
hermes plugins doctor . --ci
hermes plugins validate . --install-deps
```

Runtime dependencies are Python standard library only. Optional test/build dependencies have upper bounds. All checks run locally — this repository uses no hosted CI — so only locally executed results are claimed. See the [validation record](VALIDATION.md) for the actual results and test environment of this build.

## Roadmap and contribution

License approval comes first. A THOR Lite 10.7 and 11 smoke test passed on macOS; Windows and Linux runs are still open. Next are stronger event-log correlation, evidence-retention controls, independently validated live read-only connectors and host-tested write approval flows. Do not promote a scaffold to `mvp` without tests and an accurate disclosure.

Add profiles, workflows, connector descriptors and skills through `scripts/build_assets.py`, regenerate, test and open a focused PR. See [CONTRIBUTING.md](../CONTRIBUTING.md). Do not commit customer logs, vendor software or detection content; approved documentation logos have separate [provenance and usage boundaries](../assets/brand/README.md).
