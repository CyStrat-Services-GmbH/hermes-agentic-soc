<p align="center">
  <a href="https://www.cystrat-services.com/"><img src="assets/brand/cystrat.png" width="30%" alt="CyStrat Services GmbH"></a>
  <a href="https://www.nextron-systems.com/"><img src="assets/brand/nextron.png" width="30%" alt="Nextron Systems"></a>
  <a href="https://xplt.com/"><img src="assets/brand/exploit-labs.png" width="30%" alt="exploit labs"></a>
</p>

# Hermes Agentic SOC

**Cybersecurity from Germany. For the world.**

When agentic AI goes on the offensive, defenders need more than another chatbot. They need cybersecurity expertise that can work with their evidence, their tools and their operational boundaries.

Hermes Agentic SOC brings that expertise into Hermes through specialist profiles, reusable skills, native tools and structured workflow references. Developed in the CyStrat Services × Nextron Systems project, it starts with evidence-led triage and deterministic THOR assessment. The roadmap extends that foundation toward approved, read-only access to your wider security stack.

<p align="center">
  <a href="docs/README.md">Documentation</a> ·
  <a href="docs/GETTING-STARTED.md">Quickstart</a> ·
  <a href="docs/INTEGRATION-ROADMAP.md">Integration roadmap</a> ·
  <a href="SECURITY.md">Security</a> ·
  <a href="README.de.md">Deutsch</a>
</p>

> [!IMPORTANT]
> **Private development preview · v0.1.2.** Local evidence analysis is implemented; the 21 technology integrations are planning scaffolds, not live connectors. Offensive Security is a gated planning preview with a planned contribution from exploit labs. Apache-2.0 is proposed, not granted.

## Your environment. Our expertise.

The goal is not to replace your security stack. It is to give Hermes a disciplined way to work with it: understand the evidence, apply specialist knowledge, make uncertainty visible and leave consequential decisions with your team.

- **Evidence before conclusions:** Exact event inventories, conservative same-artifact grouping and traceable first assessments instead of model-invented incident narratives.
- **Specialists for the task:** Six defense personas cover triage, incident response, hunting, DFIR, detection engineering and vulnerability management.
- **Reusable operational knowledge:** 29 shipped skills combine eight domain/workflow skills with 21 technology-specific planning scaffolds.
- **Control by design:** Local evidence boundaries, metadata-only audit records and Hermes-owned approval for sensitive execution. No plugin telemetry, self-updater or hidden LLM calls.

The assessment engine is deterministic. Hermes may use its configured model to interpret tool output, but the plugin does not call a model to calculate severity.

## What you can use today

| Area | Delivered in v0.1.2 | Boundary |
|---|---|---|
| Native Hermes plugin | 8 tools, 4 slash commands, 1 approval-policy hook | Public plugin APIs; no monkey-patching |
| Evidence analysis | THOR JSON v1/v2, arrays, event wrappers and NDJSON | No v3 or legacy CSV/text support |
| First assessment | Exact counts, observation groups, German case JSON/Markdown | Provisional triage, not proof of compromise |
| Local THOR launcher | Fixed-argument FileScan preparation and execution path | External licensed binary and human approval required; real vendor scan not validated here |
| Specialist profiles | 6 defense profiles; 3 research-planning scaffolds | Research preview off by default; no target interaction |
| Workflow references | 4 declarative workflow definitions | Not an executable workflow engine |
| Technology coverage | 21 skills and inactive MCP descriptors | **0 verified live remote connectors** |

The [validation record](docs/VALIDATION.md) distinguishes executed tests from untested scenarios. The [operator guide](docs/OPERATOR-GUIDE.md) documents the detailed approval, privacy and host-isolation limitations.

## Start with evidence, not credentials

Run the synthetic demonstration with Python 3.11 or newer. It requires no THOR installation, provider key or remote connection.

```bash
git clone https://github.com/CyStrat-Services-GmbH/hermes-agentic-soc.git
cd hermes-agentic-soc
python -m agentic_soc demo --output /tmp/hermes-agentic-soc-demo
```

The repository is private, so cloning requires authorized GitHub access. The fixture contains no malware and produces exactly **4 source events → 3 observation groups**, not three proven incidents.

Inspect the delivered scope without contacting a vendor:

```bash
python -m agentic_soc capabilities
python -m agentic_soc capabilities --technology cystrat-soc-suite
python -m agentic_soc profiles
```

For native installation, evidence-root configuration and approval boundaries, follow the [quickstart](docs/GETTING-STARTED.md). For real evidence, use the [operator guide](docs/OPERATOR-GUIDE.md) and your organization's handling policy.

## One agent. Your wider security stack.

The planned integration layer is designed to bring approved security context into Hermes without silently granting write access. Every technology below has a shipped planning skill and inactive MCP descriptor; none is a production connector in this release.

| Domain | Planned technology coverage | Intended value |
|---|---|---|
| SIEM | Microsoft Sentinel, Splunk, Elastic Security, IBM QRadar, Google SecOps, Wazuh, Graylog | Bounded alert and log investigation |
| SOAR / cases | TheHive / Cortex, Shuffle, Cortex XSOAR, Sentinel Playbooks | Case context and draft handoffs |
| EDR / XDR | Defender XDR, CrowdStrike, SentinelOne, Velociraptor | Existing detections and endpoint evidence |
| Threat intelligence | MISP, OpenCTI, VirusTotal | Authorized indicator context, no automatic public uploads |
| Detection engineering | Sigma, YARA | Original detection drafts and controlled fixture testing |
| SOC platform | CyStrat SOC Suite | Proposed tenant- and case-scoped read-only integration |

Sigma and YARA are detection toolchains, not remote SOC services. Future containment, blocking, ticket posting or rule deployment requires a separately reviewed implementation and explicit human approval.

Read the [integration roadmap and acceptance gates](docs/INTEGRATION-ROADMAP.md) or the [CyStrat SOC Suite integration design](docs/CYSTRAT-SOC-SUITE.md). Vendor names describe intended compatibility, not endorsements.

## Different strengths. One mission.

| Contributor | Role in this project | Delivery boundary |
|---|---|---|
| **CyStrat Services GmbH** | SOC and incident-response experience translated into skills, profiles and workflows | Defense-focused project development with Nextron Systems |
| **Nextron Systems** | THOR and forensic-assessment expertise within the joint project | THOR software, signatures and licenses are acquired separately |
| **exploit labs** | Planned developer and contributor of the Offensive Security part, led by Managing Director Johannes Schönborn | Skeleton and gated preview only; no operational offensive implementation is claimed |

The [Offensive Security preview](docs/GATED-PREVIEW.md) is disabled by default. Operator opt-in and a valid declared scope are both required; current outputs are plans, never exploitation or interaction with a target.

Logos identify the named contributors and remain their respective owners' marks. See [brand provenance and usage boundaries](assets/brand/README.md).

## Your team stays in control

- **No bundled scanner:** No THOR binary, signatures, Nextron rules or license files are included or automatically downloaded. Obtain THOR separately through [Nextron](https://www.nextron-systems.com/thor-lite/) and verify the license for your engagement.
- **Approval belongs to Hermes:** Sensitive execution uses the host approval pipeline. `/thor-scan` is preview-only, and an `execute:true` argument is not approval.
- **Read-only integration intent:** No remote connector is active. The planned layer requires server-enforced least privilege; a prompt or MCP trust label is not an authorization control.
- **Privacy has limits:** Output is minimized and identifiers are pseudonymized, not guaranteed anonymous. Tool output can enter the configured Hermes model's context.
- **Audit is local:** Metadata is recorded under `plugin_data_dir("agentic-soc")`. Local JSONL is not tamper-proof or a chain-of-custody certificate.

Read [SECURITY.md](SECURITY.md) before handling customer evidence or enabling any execution path. A synthetic test suite is not an independent security audit.

## Documentation

| If you want to… | Start here |
|---|---|
| Run a safe demo or install the plugin | [Getting started](docs/GETTING-STARTED.md) |
| Configure evidence roots, scanning and specialist profiles | [Operator guide](docs/OPERATOR-GUIDE.md) |
| Understand components and trust boundaries | [Architecture](docs/ARCHITECTURE.md) |
| See tools, commands and specialist roles | [Capability reference](docs/CAPABILITIES.md) |
| Plan an integration or review CyStrat SOC Suite | [Integration roadmap](docs/INTEGRATION-ROADMAP.md) · [SOC Suite](docs/CYSTRAT-SOC-SUITE.md) |
| Review tests, limits and prior findings | [Validation](docs/VALIDATION.md) · [Review 0.1.2](docs/REVIEW-0.1.2.md) |
| Extend the project safely | [Contributing](CONTRIBUTING.md) · [Open work](TODO.md) |
| Read the overview in German | [Deutsche Projektübersicht](README.de.md) |

## Development

The runtime uses the Python standard library only. Optional build/test dependencies have upper bounds.

```bash
python -m pip install 'pytest>=8,<10' 'jsonschema>=4.18,<5' 'PyYAML>=6,<7'
python scripts/build_assets.py
python -m pytest -q
python scripts/check_docs.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for host integration checks, generated-asset rules and the definition of a verified integration.

## License and release status

**Apache-2.0 is proposed only. Final rights-holder approval is pending.** The current [LICENSE](LICENSE) is a placeholder, not a provisional open-source grant; [NOTICE](NOTICE) records the accompanying restrictions.

- [ ] **Release-blocking TODO:** Obtain final approval and update `LICENSE`, `NOTICE` and `plugin.yaml` together before any open-source release.

This repository remains private. Changes to visibility, public video/source publication and catalog or hackathon submission require renewed explicit approval; this documentation does not authorize them.
