# Timestamp semantics for THOR artefacts

Use this table to label timestamps correctly. When in doubt, describe the timestamp by its field name and source instead of interpreting it.

| Artefact / field | What the time means | Common mistakes |
|---|---|---|
| THOR `time` (event log time) | When THOR wrote the event during the scan. | Treating it as attack time. |
| File `CREATED` (Windows `$STANDARD_INFORMATION`) | When the file was created **at this location**. Copying or extracting usually sets a new creation time. | Treating it as the file's origin date. |
| File `MODIFIED` | Last content modification. Usually preserved by copy and extraction. | Treating `MODIFIED` earlier than `CREATED` as timestomping. This is normal for copied and extracted files; it is at most a weak indicator. |
| File `ACCESSED` | Last access, often not updated (disabled or delayed by the OS). | Treating it as last use. **Every `accessed` time that falls inside the scan window is an artefact of the scan itself** — THOR read the file. Never present those as user or attacker activity. |
| Timestomping detections (THOR's own checks, MFT analysis in intense mode) | THOR saw a timestamp inconsistency it considers suspicious. | Treating a simple created/modified inversion as the same thing. Prefer THOR's explicit detection or `$FILE_NAME` comparisons from MFT analysis. |
| SHIMCache timestamp | Version-dependent metadata recorded in the AppCompatCache (often a file modification time, sometimes creation-related). Nextron describes it as last-execution or creation time depending on the Windows version ([scan modes](https://thor-manual.nextron-systems.com/en/latest/usage/scan-modes.html)). | Treating it as execution time; treating the entry as proof of execution. |
| AmCache `FIRST_RUN` / entry times | Time associated with the AmCache entry; SHA1 identifies the binary. | Assuming every AmCache entry is an execution. Corroborate. **Check the distribution before dating anything**: when most entries share one few-second window, the value reflects a bulk write during install or inventory, not per-file execution. Compare against the host's install date and the count of distinct values. (see the uniform-timestamp test below). |
| AmCache `CREATED` (hive FileKey time) | A key-derived timestamp that THOR parses from the Amcache FileKey name. | Using it as a file time. On real exports it produces impossible values (years `2045`, `2096`, `2097`, i.e. after the scan). Use `FILE_CREATED` (`file_2.created`) and `FIRST_RUN` instead, and check the field against the scan end before trusting any value from it. |
| Scheduled task `LASTRUN` / `NEXTRUN` | Last and next scheduled run as recorded by the task scheduler. | Treating `NEXTRUN` as activity. Also: THOR can emit these in **host-local time with a `Z` suffix** — values land 1–2 h after the scan end on a CEST host. Verify by comparing `NEXTRUN` against the `Report` end time before ordering any task event. |
| Service `MODIFIED` | Last modification of the service's registry key. | Treating it as installation time. |
| Account `LAST_LOGON`, `PASS_AGE` | Last recorded logon and password age for the account. | Assuming the logon was interactive or by the account owner. |
| Event log entry time | Time recorded by the logging system for that event. | Ignoring the host's clock offset or timezone. |
| Log line timestamp (LogScan) | Time written by the application into its log. | Assuming UTC; ignoring application timezone settings. |
| THOR text-report line prefix (`Aug 18 13:27:13 <host> THOR: …`) | **UTC**, second precision, no year — while every inline field on the same line (`START_TIME`, `EVENT_TIME`, file `CREATED`/`MODIFIED`, service `MODIFIED`, `LASTRUN`) is **host-local**. | Treating prefix and fields as one zone: the same scan then reads two hours apart, or a whole timeline shifts by the offset. Verify the offset once per export instead of assuming it — the `Thor Scan started` line's prefix equals `START_TIME` minus the offset (`13:27:13` vs `START_TIME: Tue Aug 18 15:27:13 2026` on a CEST host), and `EVENT_TIME` equals `TimeCreated_SystemTime` inside `ENTRY` plus the same offset. Label the prefix `THOR-Erkennungszeit (UTC)` and the fields `Quell-Eventzeit (lokal)`. |
| Prefetch file (`C:\Windows\Prefetch\<IMAGE>-<HASH>.pf`) `MODIFIED` | Last execution of that image name: the `.pf` exists because the image ran, and each run rewrites it. The embedded hash identifies the path/name combination. | Reading a boot-time reference to the `.pf` (ETL/WDI `FileName:`) as a fresh execution. |
| ETL / `BootPerfDiagLogger` `FileName:` records (WDI logfiles) | A file-object open recorded by the boot performance logger during a boot — often the prefetch service reading its own database, or the OS touching a binary at boot. | Treating a `FileName` reference to a binary or `.pf` as execution. It is an access, in boot context. |
| Log/trace match captured from a file (`LogScan`, remote-access tool traces, `ConsoleHost_history.txt`) | The containing file's `MODIFIED` is the last write of the whole file, not the time of the matched line. The rule's `context`/`matched` string frequently omits the line's own timestamp entirely. | Dating the matched action from the file time. The event is Confirmed; its time is `Not Derivable` unless the captured context carries one. |
| Archive member times | Times stored in the archive, often from the packer's system. | Treating them as host activity. |

## AmCache: inventory sweep versus execution

The decisive test is **internal comparison, not the individual value**. Sort the entries by `FIRST_RUN` and ask whether unrelated binaries land in the same second:

- **Thousands of unrelated binaries sharing one or two `FIRST_RUN` seconds** (a fresh Windows build, a feature upgrade, a re-imaged host) is the inventory sweep the OS performs at install or upgrade time. Nothing in that cluster is evidence of execution — including `vssadmin.exe`, `bcdedit.exe`, `wbadmin.exe` and `wevtutil.exe`, which are exactly the binaries a ransomware checklist asks about.
- **A sparse timestamp that stands alone**, plausibly after the tool was copied to the host, is at most a corroborating indicator and still needs a second source (SHIMCache, 4688/Sysmon, prefetch, a service or task referencing it).
- Anchor the cluster before interpreting it, and prefer an anchor that is always present. `Startup` records `System Uptime`, so boot time = scan start minus uptime; a `FIRST_RUN` second ten minutes after boot is the post-boot driver/registry enumeration, not execution. A same-second cluster that sits at an install or feature-upgrade date is the same sweep. `installed_on` is often absent from the export — the uptime anchor never is. If the cluster is close to the scan date, discount it wholesale.

Practical consequence: an AmCache-only "dual-use binary ran" claim is `Not Derivable`. Say the entry exists, say it is inventory-shaped, and name what would settle it.

## Evidence without a usable time

Some of the most important artefacts carry no timestamp at all: a session line inside a tool trace, a substring matched in a log, a `matched`/`context` field that begins mid-line. Do not drop them and do not date them from the containing file.

- Keep the event, label its time `Not Derivable`, and put an explicit `undatiert` row in the timeline at the position its evidence supports (after the earliest artefact that proves the tool existed, not after the file's mtime).
- Name in `Grenzen` what would date it: the full log file, netflow/firewall records for the peer address, the counterparty's console.
- When the order of two undated events matters to the verdict, say the order is unknown. A sequence assembled from file mtimes can invert the real one.

## Clocks and formats

- THOR can use UTC (`--utc`) and RFC 3339 (`--rfc3339`). Default timestamps use the ANSI C format, which omits the year ([output options](https://thor-manual.nextron-systems.com/en/latest/usage/output-options.html)).
- In the `--text` report the line prefix and the inline field times use **different zones** (row above). Convert once at parse time and keep the original string beside the converted value — never silently rewrite one into the other, and never place both in one timeline table without the zone label.
- Record the host's timezone and any known clock drift before ordering events from different hosts.
- Timestamps in NTFS can be manipulated by an attacker with sufficient rights. Label file times as "Confirmed as recorded", not as "Confirmed as happened".
