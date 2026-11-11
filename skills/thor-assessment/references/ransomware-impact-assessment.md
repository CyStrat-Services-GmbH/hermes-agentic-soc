# Assessing ransomware and impact questions from a THOR export

Ransomware is the most common reason a THOR export lands on your desk. It is also the question THOR is least able to answer alone: THOR sees signatures and artefacts, while encryption, deletion and backup destruction are filesystem, VSS and backup-system events.

Split the question before answering it:

1. **Is ransomware code present or was it run?** — signature and artefact question, partly answerable here.
2. **Did encryption or destruction already happen?** — filesystem question, only answerable with VSS status, backup job history and file-server evidence. Say so instead of implying THOR settled it.

## 1. What to search, and what a hit actually proves

| Indicator | Where in the export | A hit proves | A hit does **not** prove |
|---|---|---|---|
| Ransom note | Filescan rule `SUSP_RANSOM_Note_*`; filename IOCs for `readme`, `how_to`, `restore`, `decrypt`, `recover` | A file with note-like content exists | That it sits in an encrypted folder — open the path and check the surrounding tree |
| Encrypted extensions | Search every path field for known suffixes (`.locked`, `.lockbit`, `.conti`, `.encrypted`, `.crypt`, vendor tags) | A file with that name exists | Anything, if the hit is a JSON/JS string inside a cache or bundle rather than a filename |
| Shadow copy destruction | Sigma/LogScan hits for `vssadmin delete shadows`, `wmic shadowcopy delete`, `wbadmin delete catalog`, `bcdedit /set recoveryenabled no` | Someone ran a destructive command | That it succeeded, that it targeted this host's own copies, or who ran it |
| Log clearing | Sigma hits for `wevtutil cl`, Security event 1102 | Clearing was attempted | Which log content was lost |
| Free-space wiping | `cipher /w`, `sdelete` hits | Tool invocation | Scope |
| Mass modification / rename | `Timestomp` findings; large Filescan clusters inside one user data tree | Timestamp inconsistency or bulk activity | Intent — installers, sync clients and restores look the same |
| Staged payload | Executables in `Temp`, `Public`, `Downloads`, `PerfLogs`, `AppData\Local\Temp`, `$Recycle.Bin` that are unsigned or vendor-unknown | Something executable was dropped | Execution, or that it is malicious |
| Family signatures | `MAL_*RANSOM*`, `MAL_*` generally, hash IOCs, leak-site domains | A known family artefact matched | Which stage of the attack was reached |

Destructive-command indicators **only exist if the host produced process-creation telemetry** (Sysmon or 4688). Without it, a zero count is a statement about telemetry, not about the host.

## 2. Artefacts routinely mistaken for ransomware

- `SUSP_RANSOM_Note_Aug22` on a browser cache entry, an Office add-in bundle or any JSON blob containing `wallet`, `@proton` or a list of crypto extension IDs.
- Amcache entries for `vssadmin.exe`, `bcdedit.exe`, `wbadmin.exe`, `wevtutil.exe`, `cipher.exe`, `fsutil.exe`: presence is not execution, and a shared `FIRST_RUN` second across thousands of entries is the inventory sweep of an install — see `thor-timeline-correlation/references/timestamp-semantics.md`.
- `SUSP_DLL_RWX_Section_*` matches inside a crash dump (`DumpScan` chunk hits): RWX sections are ordinary in JIT, .NET and AV code.
- `MEMORY.DMP` as a filename-IOC hit: that is a normal Windows crash dump. It is a **handling** and credential-hygiene item, not a ransomware finding.
- High `ProcessIntegrity`/PE-Sieve counts on a host with an AV product: hook footprint, not injection.

## 3. How to phrase a negative finding

Absence of hits supports exactly one sentence: *no ransomware artefacts were present or visible in this export*. It never supports "the host is clean". Make the sentence carry its own three-part justification:

```text
Kein Ransomware-Artefakt nachweisbar.
Abgedeckt: <Module, die dafür zuständig waren> – geprüft: <exakte Element-Zahlen
  je Modul, z. B. Timestomp 1.402.864 Objekte, Filescan 720.981 Dateien>.
Nicht abgedeckt: <Lookback-Grenze, Dateigrössenlimit, deaktivierte Module,
  fehlendes Sysmon/4688, nicht lesbare Kanäle, fehlende VSS-/Backup-Sicht>.
```

Two rules that keep this honest:

- Cite the **element counts**, not the module names alone. "Timestomp fand nichts" is worthless without "über 1,4 Mio. Objekte".
- Separate **signature-negative** from **behaviour-negative**. A clean YARA run and an intact behavioural trail are different evidence strengths; name both or neither.

## 4. When the requester needs a defensible "clean"

A signature scan cannot deliver that, no matter how clean it looks. Name the approval-gated next steps explicitly rather than hedging in prose:

1. Sysmon plus 4688 process-creation auditing, then a re-scan (system change — approval).
2. Filescan without `--lookback`, so untouched pre-existing files are read.
3. VSS shadow-copy status and backup job history from the backup product.
4. Share, sync-client and file-server side evidence (Dropbox/OneDrive/HiDrive sync logs, SMB server logs) — a workstation scan says nothing about what left the host.

Order the answer so the reader sees the limit before they see the comfort.
