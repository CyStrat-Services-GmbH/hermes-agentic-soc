# Security model and disclosure

This package is defensive SOC tooling with research-planning scaffolds, not an exploitation framework. It has no target-interaction research tool or production containment/ticket-write connector.

## Deployment review

| Before you… | Confirm |
|---|---|
| Import customer evidence | Approved narrow roots, safe staging and retention policy |
| Use a model provider | Permission for minimized tool outputs to enter that provider's context |
| Execute THOR | Appropriate license, trusted executable, approved target and host-owned human approval |
| Provision a profile | Correct Hermes root and independently verified account isolation requirements |
| Enable research planning | Operator opt-in, valid declared scope and restricted lab tools |
| Design a remote connector | Server-side read-only RBAC, tenant boundaries and negative acceptance tests |

Use the [operator guide](docs/OPERATOR-GUIDE.md) for configuration and the [validation record](docs/VALIDATION.md) for test coverage. The controls below are application boundaries, not a guarantee that the entire Hermes host is sandboxed.

## Boundaries

Evidence imports resolve symlinks and must remain inside explicit operator-approved roots. Common credential stores/files are refused. The shipped synthetic demo directory and the plugin's private data directory are also accepted roots. Imports are capped at 50 MiB and 100,000 structured records.

These are application boundaries, not a sandbox: the Hermes host, an operator-selected executable and the local OS account retain their own authority. A TOCTOU race or a malicious local operator is outside this MVP's security boundary. Do not point the host at untrusted writable evidence directories without an acquisition/staging process.

THOR CLI help and execution use argv lists, no shell interpolation and a minimal environment. Only a configured executable and FileScan in an explicitly configured directory are supported. No custom extra flags, remote scans, process scans, privilege escalation, `action_command` hooks, downloads or vendor updates are supported.

The host pre-tool policy requests human approval for scan/profile execution. Direct library calls are not a protected authorization boundary. The scope checker validates declared fields, exact targets, UTC-aware validity and allowed activities, but cannot verify a legal authorization document. These limitations are visible in tool output.

The scan slash command refuses `execute:true` and only previews. The inspected low-level host `ctx.dispatch_tool` path invokes registry handlers directly; unlike the normal agent tool executor, it must not be assumed to run approval hooks. Execution must go through a normal agent tool call. A fully trusted third-party plugin with arbitrary code/registry access remains outside this package's threat boundary.

SOUL and skill instructions are behavioral guidance only. They cannot stop an agent from using unrelated tools outside this package. Deploy research personas in an independently restricted lab environment with a narrow host tool allowlist.

## Sensitive data

The plugin never reads `.env`, OAuth stores, browser profiles or external CLI tokens. It does not perform outbound HTTP, telemetry or LLM calls. Credentials for future connectors must use Hermes's approved secret scope, never plain configuration values or custom token files.

Output minimisation removes known credential key patterns, raw match/firstbytes content, opaque hashes in prose, common account-path identifiers, email addresses, SIDs and IP addresses. Typed malware/tool hash fields are retained only outside recognized credential-dump contexts. Host and scan identifiers are HMAC-pseudonymized with a profile-local salt.

This is not exhaustive DLP: arbitrary names, unusual formats or personal data embedded in free prose may remain. `--suppresspi` does not make raw scanner reports automatically safe to publish. Review outputs, apply your retention policy and restrict access to reports and scanner files. Tool outputs may be sent by Hermes to the selected LLM provider.

Audit JSONL records event metadata, not raw tool parameters. It is append-only by convention, not tamper-evident, externally anchored or a full forensic custody ledger. Source SHA-256 identifies bytes imported; it does not certify origin or completeness. No raw customer evidence is shipped in the repository.

## Failure behavior

Malformed/unsupported input refuses assessment instead of silently dropping events. Unknown scores stay unknown. Unsupported v3 does not fall back to guessed v2. Empty/INFO-only exports never establish a clean host. Timeouts and absent scanner JSON are incomplete runs, even when the process exit is zero.

Execution is bounded by a timeout. The configured THOR binary is trusted operator software; the package does not sandbox it, control vendor-internal network behavior, verify its publisher signature or guarantee cleanup of vendor-spawned descendants. Use OS job/container controls for stronger guarantees.

Report privately to the repository maintainers through an existing agreed channel; do not post customer logs, credentials or exploit details in public issues. No unverified security-contact email is invented here.
