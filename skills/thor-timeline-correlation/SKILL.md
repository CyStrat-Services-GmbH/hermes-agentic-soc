---
name: thor-timeline-correlation
description: "Correlate THOR events into analyst findings and build a defensible timeline: merge multi-source observations of the same artefact, keep artefact time, source-event time and THOR detection time apart, and interpret file, SHIMCache, AmCache, task, account and event-log timestamps correctly. Use after module review when events must be grouped or ordered; not for inferring causality without shared evidence."
---

# THOR correlation and timeline

The scanner gives you observations. A case needs findings and a sequence. Both are easy to overstate: two events in the same minute are not automatically connected, and the time THOR saw something is not the time it happened.

## Part 1: Correlation

### What the tool already grouped

`thor_parse` merges events only when host and scan are known **and** one stable identity exists: file path plus hash, event ID plus record ID plus channel, or PID plus process start time. Everything else stays separate. `duplicate_observation_count` tells you how many events were merged automatically.

### What you merge as analyst

Merge events into one finding when they describe the **same technical fact** and state the key you used:

| Key | Example |
|---|---|
| Same path (with or without hash) on the same host and scan | Filescan hit and SHIMCache entry for the same executable |
| Same path and hash across modules | Filescan and Autoruns/ServiceCheck image path |
| Same event ID, record ID and channel | Live Eventlog event and its EVTX copy |
| Same security-product detection ID | Detection and action events of one AV detection |
| Same service name and image path | ServiceCheck entry and a service-installation event |
| Same command line | Process, task and log line showing the same command |
| Same persistence item via different methods | Autoruns and WMIStartup describing one entry |

Keep events **separate** when they differ in host, target, path or hash, even if they share a rule. Many events can be one finding; many files with distinct targets are many findings.

### What you must not merge

- Events linked only by time proximity, without a shared artefact.
- A process and a file only because both are "suspicious".
- Findings from different cases without a shared technical indicator.

If a link is plausible but unproven, record it as a hypothesis under "Offene Prüfungen", not as a merged finding.

## Part 2: Timestamps

Label every timestamp with its type. Read [references/timestamp-semantics.md](references/timestamp-semantics.md) for what each artefact's time actually means.

| Type (German label) | Meaning |
|---|---|
| `THOR-Erkennungszeit` | When THOR logged the observation (`time` field). Scan time, never activity time. |
| `Artefaktzeit` | A timestamp stored with the artefact (file created/modified/accessed, SHIMCache, AmCache, task last run, account last logon). Meaning depends on the artefact. |
| `Quell-Eventzeit` | The time recorded by the original log source (event log entry, log line). |

Rules:

- Normalise to UTC and state the source timezone. THOR's default text timestamps have no year unless `--rfc3339` was used; never guess the year.
- The plugin ignores timezone-free or invalid artefact timestamps for its timeline and reports how many. Do the same in your analysis.
- One timeline entry per distinct activity or state change. Merge entries that share time and fact. Do not create entries for metadata-only repetitions.
- An event's absence from the timeline is not evidence that nothing happened then.

## Part 3: Sequence and causality

Order findings by their best-supported time. Then state, for each step, how the next one is linked: by a shared artefact (Confirmed), by a strong pattern (Strong Indicator), or not at all (Not Derivable). "Tool placed → service created → service run" requires evidence for each arrow.

## Output block

```text
Finding <F-n>: <Kurzbeschreibung>
Events: <E-IDs> · Korrelationsschlüssel: <Schlüssel> · Automatisch gruppiert: <ja/nein>

Timeline
| Zeit (UTC) | Typ | Quelle (Event/Feld) | Aktivität | Beweiskraft |
|---|---|---|---|---|
| … | Artefaktzeit | E000001 / created | Datei auf Datenträger angelegt | Confirmed (Zeitstempel manipulierbar) |

Verknüpfungen: <Schritt A → B: belegt durch … / nicht belegt>
Hypothesen (nicht belegt): <…>
```
