---
name: thor-module-analysis
description: "Interpret THOR findings per scan module (Filescan, ProcessCheck, SHIMCache, AmCache, ServiceCheck, Autoruns, Registry, ScheduledTasks, Eventlog, LogScan, DNSCache, Hosts, UserAccounts, WER, Rootkit and others): what the module observed, which fields to check and which indicators point to benign or malicious. Use while reviewing individual THOR events during an assessment; not for running scans or final classification alone."
---

# THOR module analysis

Every THOR event comes from a module, and each module observes something different. A Filescan hit says a file with these properties existed at scan time. A SHIMCache hit says the system once recorded metadata about a path. Interpreting both the same way is the most common analysis error.

## Procedure

1. Read the event's `module`, `message`, `score`, `reasons` and the module's characteristic fields. In the plugin's `normalized.json` you have the module, message, file path, process name/PID, typed hashes, reasons and artefact timestamps. Other fields stay in the original restricted export.
2. Look up the module in [references/modules.md](references/modules.md): what it observes, which fields matter, typical false positives and the evaluation questions.
3. For any path, apply [references/file-path-checks.md](references/file-path-checks.md). For any hash, apply [references/hash-checks.md](references/hash-checks.md); external lookups need disclosure approval (see `agentic-soc:thor-ioc-handling`).
4. Weigh indicators. The evaluation tables give a direction (benign or malicious) and a weight (low, medium, high). One high-weight indicator outweighs several low-weight ones. Never sum the weights mechanically.
5. Record the result in the output block below and hand it to `agentic-soc:thor-false-positive-review`.

## What a module result proves

| Module family | Proves (Confirmed) | Does not prove alone |
|---|---|---|
| Filescan | A file with this path, size and hash existed when scanned; a rule matched its content or name. | That it ran, who placed it, or when it was used. |
| ProcessCheck | A process with these properties ran at scan time; a rule matched its memory or an anomaly was seen. | Intent; the memory match may be clear-text signatures inside AV/EDR processes. |
| SHIMCache | The system recorded this path in the AppCompatCache. | Execution. The timestamp's meaning varies by Windows version. |
| AmCache | An AmCache entry with this path and SHA1 exists. | Malicious intent; SHA1 identifies the binary, the entry type governs whether it ran. |
| ServiceCheck, Autoruns, ScheduledTasks, WMIStartup | A persistence entry with this configuration exists. | That it was created by an attacker, or when it last ran (unless a run field says so). |
| Eventlog / LogScan | The log contains this entry, and a rule or IOC matched it. | That the logged action succeeded, unless the entry records the outcome. |
| DNSCache, Hosts, Firewall | A configuration or cache entry exists. | That a connection carried malicious traffic. |
| UserAccounts, LoggedIn | An account or session with these properties exists. | Who operated it. |
| Rootkit | A rootkit indicator was observed. | Treat as high priority regardless; validate with memory forensics. |

## Platform and edition notes

- Registry, SHIMCache, AmCache, Mutex, Named Pipes and Eventlog are Windows-specific ([scan modes](https://thor-manual.nextron-systems.com/en/latest/usage/scan-modes.html)).
- THOR Lite has five modules, centred on file system, process and autoruns checks, and no Registry, Eventlog, SHIMCache or Sigma scanning ([THOR Lite](https://www.nextron-systems.com/thor-lite/)). The plugin's launcher runs only `--module FileScan` on an approved directory.
- Message enrichment means other modules can emit events carrying full file paths (e.g. SHIMCache, Eventlog). Do not assume every event with a path came from the file system scan.

## Output block

```text
Event <E-ID> · Modul <Modul> · Level <Level> · Score <Score>
Beobachtet (Confirmed): <was das Modul tatsächlich belegt>
Auffällige Felder: <Feld: Wert-Beschreibung, keine Credentials>
Indikatoren benign: <Indikator (Gewicht)>
Indikatoren malicious: <Indikator (Gewicht)>
Offene Prüfungen: <Prüfung, Datenquelle>
Zwischenstand: <Strong Indicator / Suspicious / vermutlich FP / Informational>
```
