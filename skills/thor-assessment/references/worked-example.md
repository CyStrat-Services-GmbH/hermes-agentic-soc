# Worked example: multi-module THOR export

Input: `examples/analysis/thor-multimodule.json` in the plugin distribution. The data is synthetic; the rule names start with `DEMO_` and match no real signature. Run it offline:

```bash
python -m agentic_soc assess "$(pwd)/examples/analysis/thor-multimodule.json" --output /tmp/thor-example
```

## Tool layer

`thor_parse` / `thor_first_assessment` return:

| Inventory field | Value |
|---|---|
| `event_count` | 7 |
| `finding_count` | 7 |
| `levels` | ALERT 2, WARNING 2, NOTICE 2, INFO 1 |
| `modules` | Filescan 2, SHIMCache 1, ServiceCheck 1, Autoruns 1, ProcessCheck 1, Init 1 |
| `unique_files` | 3 |
| `unique_hashes` | 2 |
| `unknown_score_count` | 1 |
| Tool verdict | Verdächtig, P2 (provisional) |

The regression suite asserts these values, so this table stays accurate.

## Analyst layer

Score-first order: E000005 (90), E000001 (85), E000003 (70), E000002 (60), E000006 (45), E000004 (40), E000007 (no score).

| Event | Module | Analyst reading | Outcome |
|---|---|---|---|
| E000005 | ProcessCheck | Generic in-memory signature inside a security product's process. Security and AV process memory often holds clear-text signatures. Verify that the process is the genuine product binary (path, signer) before closing. | False Positive (pending binary verification) |
| E000001 | Filescan | Hack-tool rule (score 80) plus location anomaly on an executable in `C:\Users\Public\Documents`, a folder that should not contain executables. `modified` is earlier than `created`, which is typical for copied or extracted files and is not proof of timestomping. | Strong Indicator: hack-tool presence |
| E000002 | SHIMCache | Same path as E000001, no hash. The tool keeps it separate because file identity without a hash is not stable. The path match justifies analyst correlation with E000001. A SHIMCache entry does not prove execution. | Merged into the E000001 finding |
| E000003 | ServiceCheck | Random-looking service name pointing to a batch file in `C:\Windows\Temp`. Matches a common remote-execution pattern, but no source event (e.g. service installation) is in this export. | Suspicious |
| E000006 | Filescan | Vulnerability rule on a configuration file in a 2019 backup folder. Only relevant if an active service uses it. | Inconclusive, low priority: verify whether active |
| E000004 | Autoruns | "New or changed autoruns element" is a change notice. No entry details are in the export; it cannot be linked to E000003 without evidence. | Inconclusive |
| E000007 | Init | Scan metadata. Not evidence of coverage or of a clean host. | Informational |

Result: **7 events → 7 automatic groups → 6 analyst findings** (E000001+E000002 merged), of which one is likely false positive, two are security-relevant (hack-tool artefact, suspicious service), two need verification and one is informational.

## Lessons

- **Automatic grouping is conservative.** Multi-source evidence without a shared hash or record ID needs explicit analyst correlation with a stated reason.
- **Pseudonymisation can hide well-known profiles.** The tool pseudonymises every segment after `C:\Users\`, including `Public`. Check the original restricted export before interpreting a "user" path.
- **The highest score is not the most important finding.** The top-scoring alert is the most likely false positive here.
- **Priority stays provisional.** The tool's P2 is reasonable while the hack-tool artefact and the service are unvalidated. Whether it becomes P1 depends on asset criticality, recency and corroborating telemetry, not on the scanner level.
