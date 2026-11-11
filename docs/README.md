[Project overview](../README.md) / Documentation

# Documentation

Hermes Agentic SOC turns supplied evidence into a conservative first assessment and gives Hermes specialist guidance for SOC work. This documentation separates operational instructions, design intent and executed validation so you can tell what is usable today and what is still planned.

## Choose your path

| Audience | Recommended reading |
|---|---|
| Evaluating the project | [Product overview](../README.md) → [Capabilities](CAPABILITIES.md) → [Roadmap](INTEGRATION-ROADMAP.md) |
| Running the plugin | [Getting started](GETTING-STARTED.md) → [Operator guide](OPERATOR-GUIDE.md) → [Security model](../SECURITY.md) |
| Analysing THOR results | [THOR analysis suite](THOR-ANALYSIS.md) → [Operator guide](OPERATOR-GUIDE.md#assessment-policy) |
| Reviewing architecture | [Architecture](ARCHITECTURE.md) → [Security model](../SECURITY.md) → [Validation](VALIDATION.md) |
| Building an integration | [Roadmap and acceptance gates](INTEGRATION-ROADMAP.md) → [SOC Suite contract](CYSTRAT-SOC-SUITE.md) → [Contributing](../CONTRIBUTING.md) |
| Reviewing the offensive-research plan | [Planned, not shipped](PLANNED-OFFENSIVE-RESEARCH.md) → [Security model](../SECURITY.md) |
| Reading in German | [Deutsche Projektübersicht](../README.de.md) |

## Reading status labels

- **Implemented:** Code exists for the stated local function. Any environment-specific test limitations remain in the validation record.
- **Scaffold / planned:** Skills, descriptors or design material exist, but they are not verified live connections.
- **Planned, not shipped:** A capability that a later release will add. Nothing of it exists in this version — no profile, skill, workflow, tool or switch.
- **Not supported:** Do not rely on the plugin for the stated operation.

A configured path or endpoint is not evidence of a working integration. Check the local `soc_capabilities` inventory and the [validation record](VALIDATION.md) rather than assuming readiness from a template.

## Reference and governance

- **Operations:** [Quickstart](GETTING-STARTED.md), [operator guide](OPERATOR-GUIDE.md), [tools and roles](CAPABILITIES.md), [THOR analysis suite](THOR-ANALYSIS.md).
- **Design:** [Architecture](ARCHITECTURE.md), [integration roadmap](INTEGRATION-ROADMAP.md), [CyStrat SOC Suite](CYSTRAT-SOC-SUITE.md).
- **Assurance:** [Security](../SECURITY.md), [executed validation](VALIDATION.md), [0.1.2 review](REVIEW-0.1.2.md), [historical 0.1.1 review](REVIEW-0.1.1.md).
- **Contribution:** [Development guide](../CONTRIBUTING.md), [skill feedback and update workflow](SKILL-UPDATE-WORKFLOW.md), [release blockers](../TODO.md), [license placeholder](../LICENSE), [notice](../NOTICE).
- **Presentation:** [English messaging](MARKETING-EN.md), [logo provenance](../assets/brand/README.md).

Historical review logs document the version tested, not a promise about every future commit. The private repository and pending license are release constraints throughout this documentation.
