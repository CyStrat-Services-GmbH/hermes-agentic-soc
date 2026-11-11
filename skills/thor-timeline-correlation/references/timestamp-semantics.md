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
| AmCache `FIRST_RUN` / entry times | Time associated with the AmCache entry; SHA1 identifies the binary. | Assuming every AmCache entry is an execution. Corroborate. **Check the distribution before dating anything**: when most entries share one few-second window, the value reflects a bulk write during install or inventory, not per-file execution. Compare against the host's install date and the count of distinct values. |
| Scheduled task `LASTRUN` / `NEXTRUN` | Last and next scheduled run as recorded by the task scheduler. | Treating `NEXTRUN` as activity. |
| Service `MODIFIED` | Last modification of the service's registry key. | Treating it as installation time. |
| Account `LAST_LOGON`, `PASS_AGE` | Last recorded logon and password age for the account. | Assuming the logon was interactive or by the account owner. |
| Event log entry time | Time recorded by the logging system for that event. | Ignoring the host's clock offset or timezone. |
| Log line timestamp (LogScan) | Time written by the application into its log. | Assuming UTC; ignoring application timezone settings. |
| Archive member times | Times stored in the archive, often from the packer's system. | Treating them as host activity. |

## Clocks and formats

- THOR can use UTC (`--utc`) and RFC 3339 (`--rfc3339`). Default timestamps use the ANSI C format, which omits the year ([output options](https://thor-manual.nextron-systems.com/en/latest/usage/output-options.html)).
- Record the host's timezone and any known clock drift before ordering events from different hosts.
- Timestamps in NTFS can be manipulated by an attacker with sufficient rights. Label file times as "Confirmed as recorded", not as "Confirmed as happened".
