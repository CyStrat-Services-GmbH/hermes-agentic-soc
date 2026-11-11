# Hash checks

Apply to typed `MD5`/`SHA1`/`SHA256` fields of malware or tool artefacts. Never apply to credential hashes (LM/NTLM, password hashes), and never reproduce those.

**Disclosure first.** A reputation lookup tells the service that someone is interested in that hash. Look up only with explicit data-sharing approval for that indicator, prefer an approved internal or private threat-intelligence source, and never upload a file. See `agentic-soc:thor-ioc-handling`.

Source: [THOR Log Analysis Manual, Hash Checks](https://log-analysis-manual.nextron-systems.com/en/latest/). Weights: L low, M medium, H high.

| Question | Direction (weight) |
|---|---|
| Unknown to the reputation service | malicious (H): rare binaries deserve attention, not reassurance |
| Flagged suspicious by more than 2 engines | malicious (H) |
| Flagged malicious by more than 10 engines | malicious (H) |
| Other known names are hashes or carry `.vir`/`.virobj` extensions | malicious (L) |
| First submission more than 7 years ago | benign (L) |
| Negative community votes or comments | malicious (M) |
| An engine's label contains `Hack`, `Scan`, `Dump`, `Password` or `Webshell` | malicious (H) |
| Part of a vendor software catalogue (e.g. Microsoft) | benign (H) |
| Rated "probably harmless" | benign (H) |
| Valid signature from a trusted vendor | benign (M) |
| Known file names are only legitimate names | benign (L) |
| PE compilation timestamp older than 10 years | benign (L) |

## Interpretation limits

- "Unknown" is not "clean". Custom tooling, internal software and targeted malware are all unknown.
- Many detections for a dual-use tool (e.g. a remote-administration utility) confirm what the tool is, not that its use was unauthorised.
- A matching hash across hosts proves the same file content. It says nothing about who placed it or whether it ran.
