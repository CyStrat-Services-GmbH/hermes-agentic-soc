[Project overview](../README.md) / [Documentation](README.md) / Integration roadmap

# Integration roadmap

Cybersecurity from Germany. For the world. Our product vision is to turn operational experience into reusable skills, tools, workflows and specialist profiles, so Hermes can work with your tools, your data and your components through explicitly approved connections.

> [!NOTE]
> **25 technology templates. Zero verified live remote connectors.** The matrix below describes intended coverage and acceptance goals, not deployed integrations or committed delivery dates.

## Available in the MVP

- **Evidence-led analysis:** Local THOR JSON v1/v2 import, exact event counts, conservative observation grouping and traceable first assessments.
- **Specialist roles:** Six defense profiles spanning L1 triage, incident response, threat hunting, DFIR, detection engineering and vulnerability management.
- **Reusable knowledge:** 39 skills, comprising a nine-skill THOR analysis suite, six domain/workflow skills and 25 technology-specific scaffolds. Four declarative workflow references guide analysis; they are not a workflow execution engine.
- **Native tooling:** Seven registered tools and four slash commands, including `/soc-capabilities` to inspect actual scope without contacting a vendor or revealing credentials.
- **Controlled local scanning:** A launcher for an independently acquired THOR executable, subject to host approval. No actual licensed vendor scan has been validated in this build.

## Integration roadmap

All technology rows below are **planned integration scope**. Each has a shipped skill and disabled MCP descriptor, but none is a verified live connector in this plugin. Proposed outcomes are acceptance goals, not claims about deployed vendor APIs.

| Category | Planned technologies | Intended read-only value |
|---|---|---|
| SIEM | Microsoft Sentinel; Splunk; Elastic Security; IBM QRadar; Google SecOps; Wazuh; Graylog | Investigate scoped alerts and log context, review bounded searches, preserve source event IDs and query provenance. |
| SOAR / case management | TheHive / Cortex; Shuffle; Cortex XSOAR; Sentinel Playbooks | Review cases, playbook definitions and execution records. Draft handoffs without triggering playbooks or modifying tickets. |
| EDR / XDR / endpoint investigation | Defender XDR; CrowdStrike; SentinelOne; Velociraptor | Review existing detections and endpoint evidence. No live response, isolation or remote collection without a separately reviewed implementation and human approval. |
| Threat intelligence | MISP; OpenCTI; VirusTotal | Enrich approved indicators from authorized sources. No public uploads or indicator disclosure without explicit permission. |
| Detection engineering | Sigma; YARA | Draft original detections and test controlled fixtures. These are detection toolchains, not remote SOC connectors. No automatic deployment. |
| Vulnerability management | Tenable Vulnerability Management; Qualys VMDR; Rapid7 InsightVM; Greenbone / OpenVAS | Read existing findings, affected assets and remediation state in an approved scope. No scan launch, schedule, rescan, exception change or ticket write. |
| Cross-domain platform | CyStrat SOC Suite | Tenant- and case-scoped analysis with source provenance from the underlying telemetry stores. Proposed read-only MCP contract; live API and tenant-isolation verification still required. The Suite is listed above the six domains rather than as a seventh, because its modules cover all of them. |

The 25 entries describe breadth, not launch dates or production readiness. Vendor names identify intended compatibility; they do not imply endorsements or partnerships beyond the contributors identified below.

## How an integration becomes available

- **Contract verification:** Verify the deployed version, documented API/MCP surface, bounded queries and field mappings.
- **Access control:** Establish server-enforced tenant isolation, least-privilege read-only credentials and Hermes-owned secret handling.
- **Evidence and privacy:** Preserve provenance, minimize personal data and obtain separate permission before any external disclosure.
- **Acceptance tests:** Test success paths, unauthorized tenants, expired credentials, denied writes, pagination, rate limits and untrusted instructions in responses.
- **Status promotion:** Change the registry only after tests against an authorized real deployment. Configuration presence alone never means “connected.”

## Partner expertise

- **CyStrat Services GmbH:** SOC, DFIR and incident-response practice translated into profiles, skills and workflows.
- **Nextron Systems GmbH:** THOR and forensic-assessment expertise. Support and cooperation for this plugin are confirmed by Nextron Systems' management. THOR software, signatures and licenses remain separate; nothing of it is bundled.
- **exploit labs:** confirmed supporter and cooperation partner, developer and contributor of a future offensive-research release. That part is still planned and not in this version; see [the plan](PLANNED-OFFENSIVE-RESEARCH.md).

## Your team stays in control

Read-only is the default for the planned connector layer. Future isolation, blocking, ticket closure or other writes require a reviewed implementation and explicit human approval; such write connectors do not exist in this MVP.

The repository remains private and the proposed Apache-2.0 license awaits final approval. No public launch, catalog submission or video publication is authorized by this roadmap.
