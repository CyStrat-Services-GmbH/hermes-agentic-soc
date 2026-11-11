# THOR modules: fields, typical false positives and evaluation questions

Primary sources: [THOR Log Analysis Manual](https://log-analysis-manual.nextron-systems.com/en/latest/) and [THOR scan modes](https://thor-manual.nextron-systems.com/en/latest/usage/scan-modes.html). Field names follow THOR's log output; exact casing differs between text, JSON v1 and JSON v2. Weights: L low, M medium, H high. "→ benign" or "→ malicious" is the direction of the indicator when the answer is yes.

## Filescan

Observes files on disk: name, path, size, type, hashes, PE metadata and signature matches. Archive contents can appear as `archive.zip|inner-file`.

Characteristic fields: `FILE`, `SCORE`, `MD5`/`SHA1`/`SHA256`, `OWNER`, `SIZE`, `TYPE`, `FIRSTBYTES`, `COMPANY`, `DESC`, `CREATED`, `MODIFIED`, `ACCESSED`, `REASON_1…n`.

Typical false positives: legitimate files matching a filename regex IOC; THOR reports or clear-text signatures left from earlier scans; dual-use admin tools (`nmap.exe`, `ncat.exe`); legitimate tools in the Recycle Bin under renamed names (`$IR4HB6A.exe`); very old files triggering size anomalies; old or rare legitimate program versions triggering signature anomalies (often `java.exe`/`javaw.exe`).

| Question | Direction (weight) |
|---|---|
| `SIZE` is 0 bytes (often reset by AV after detection) | benign for the file now, but check AV logs (H) |
| `FIRSTBYTES` start with natural-language text in a script | benign (H) |
| `FIRSTBYTES` contain commands such as `net user /domain` | malicious (M) |
| `OWNER` is a normal user account | benign (L) |
| `OWNER` is a service account such as `IIS_IUSRS`, `tomcat`, `apache` | malicious (M) |
| `TYPE` does not match the extension | malicious (L) |
| `TYPE` is `EXE` with a benign extension such as `.txt` or `.pdf` | malicious (M), unless a user renamed a portable tool to pass mail filters |
| PE `COMPANY`/`DESC` do not match the expected product | malicious (M)/(L) |
| Created or modified years in the past | benign (L) |
| Only reason is a filename-pattern match | benign (L) |
| Rule starts with `VUL_` or `VULN_` (vulnerability, not malware) | benign as compromise indicator (M) |
| Hack tool in a standard install or backup location (`/usr/bin/ncat`) | benign (M) |

Remember `OWNER` is the file system owner, not the account that executed or placed the file.

## ProcessCheck

Observes running processes: parent/child relations, priority, image location, network connections and YARA matches on process memory. Sub-features include process handles and process integrity (PE-Sieve: replaced or implanted PE → Warning; patched, IAT-hooked, unreachable → Notice).

Characteristic fields: `PID`, `PPID`, `PARENT`, `NAME`, `OWNER`, `COMMAND`, `PATH`, `CREATED`, `MD5`, `CONNECTION_COUNT`, `LISTEN_PORTS`, `RULE`, `SCORE`, `STRINGS`.

Typical false positives: legitimate software started from unusual locations; very old Windows versions with unusual parent/child or priority patterns; connections to "suspicious" GeoIP regions that are normal for the site; memory matches inside AV, EDR, VMware Tools, GRR or SearchIndexer processes that hold clear-text signatures. Nextron also notes many ProcessCheck false positives on systems running SentinelOne.

| Question | Direction (weight) |
|---|---|
| Executable is a well-known Sysinternals tool | benign (M) |
| Parent is a Microsoft Office application | malicious (H) |
| Owner starts with `IWAM_`, `IUSR_` or `IIS_` | malicious (M) |
| Memory match in a browser or VMware Tools process | benign (L) |
| Memory match in an AV or security-tool process | benign (H) |

Process findings are volatile. If the scan is the only evidence, the process may already be gone; preserve memory only through an approved acquisition.

## SHIMCache (AppCompatCache)

Observes registry cache entries holding the full image path and a timestamp. Depending on the Windows version, the timestamp may be a last-modification or creation time of the file; it is not reliably an execution time. If the file still exists, THOR enriches the entry with hashes; a missing hash means the file was not found at scan time.

Typical false positives: legitimate software in unusual locations; THOR's own previous runs from working directories such as `C:\Temp\` or `C:\thor\`.

Evaluation: apply the file path checks to `ELEMENT`/`FILE`; an empty hash means the file is gone or was elsewhere. **Never conclude execution from SHIMCache alone.**

## AmCache

Observes AmCache entries with path, SHA1, size, `FIRST_RUN`/creation data, product and company. Unlike SHIMCache, the SHA1 identifies the exact binary.

| Question | Direction (weight) |
|---|---|
| First run on a Sunday (where Sunday is not a working day) | malicious (M) |
| First run between 00:00 and 06:00 local time | malicious (M) |

Apply path and hash checks. Interpret `FIRST_RUN` according to the entry type and Windows version; corroborate execution with other artefacts.

## ServiceCheck

Observes registered Windows services: name, image path, start type, account, hashes and modification time. Messages include "Service started from typical attacker location" and YARA matches on service entries.

Typical false positives: legitimate software with service binaries in `%AppData%`; services matching regex filename IOCs; admin-registered services in odd places (`C:\srvany.exe`).

| Question | Direction (weight) |
|---|---|
| `SERVICE_NAME` is random (`98ncjs87e`) or a bare GUID | malicious (M) |
| `START_TYPE` is on-demand | benign (L) |
| Modified in an unusual window (e.g. Sunday 00:00–06:00 where nobody works) | malicious (M) |
| YARA match on the service entry | malicious (M) |
| Image path is a script or command interpreter in a temp folder | malicious (M); compare with service-installation events if Eventlog data exists |

## Autoruns

Uses Sysinternals Autoruns output: location, entry, enabled state, category, publisher, image path, launch string and hashes. Autoruns SHA1 values can be unreliable and may be suppressed.

| Question | Direction (weight) |
|---|---|
| Message is "New or changed autoruns element" (a change notice) | benign (L); relevant on critical systems or within the incident window |
| `PUBLISHER` empty | malicious (L) |
| `DESC` empty | malicious (L) |
| Hash fields empty: the image was not found at scan time | neutral, but verify the launch target |

## Registry

Matches from filename IOCs, keywords or YARA rules on registry values (`KEY`, `NAME`, `MATCHED_STRINGS`). Not available in THOR Lite.

Typical false positives: system files in backup locations; keyboard-layout preloads normal for the region; values starting with `4d5a` by chance.

| Question | Direction (weight) |
|---|---|
| Matched string points to a suspicious location that is legitimate here | benign (M), otherwise malicious (M) |
| `RDP_Preload` keyboard layout implausible for the site | malicious (M) |
| `RDP_Preload` keyboard layout plausible for the site | benign (M) |

## ScheduledTasks and AtJobs

List tasks at Info level and apply string checks to the command line. Fields include `NAME`, `COMMAND`, `USER`, `LASTRUN`, `NEXTRUN`, hashes.

| Question | Direction (weight) |
|---|---|
| Task name looks random (`jd8slpk8d8`) | malicious (H) |
| Task name uses the local language and business terms (`Datensicherung`) | benign (H) |

Typical false positives: software updaters and administrative jobs. `LASTRUN` is the only task field that speaks about execution; corroborate it.

## WMIStartup

Queries WMI for persistence elements. The same items often appear in Autoruns. Correlate both instead of counting them twice.

## Eventlog and EVTX (full THOR only)

Applies Sigma, keyword and IOC checks to Windows event logs; EVTX file scanning covers exported logs on disk. The same source event can appear from the live log and from an EVTX copy; deduplicate by channel, event ID and record ID.

Interpretation notes:

- The event's own timestamp is the source-event time, distinct from THOR's detection time.
- For security products' events (e.g. Microsoft Defender detection and action events), confirm the action's result status and error code before claiming a threat was removed. An action name such as "remove" is not proof of success.
- A Sigma rule level is the rule author's rating, not THOR's score. Nextron's default minimum Sigma level is high, reduced to medium in intense mode ([changelog](https://thor-manual.nextron-systems.com/en/latest/changelog/log.html)).

## LogScan

Processes `*.log` files line by line with filename and keyword IOCs and log-type YARA rules. Fields: `FILE`, `LINE`, `ELEMENT`, `PATTERN`.

Typical false positives: vulnerability scans producing HTTP 404 lines; RoboCopy logs listing hack-tool file names.

| Question | Direction (weight) |
|---|---|
| Log path implies very old data | benign (M) |
| Remote IP of the line is known malicious | malicious (H) |
| Web access line ends with status 404 | benign (M) |
| Line shows an antivirus alert | malicious (M): AV alerts often go unnoticed; report them |

## DNSCache

Compares DNS cache entries with known C2 servers and regex checks. Fields: `ENTRY`, `IP`, `TLD`, `SIGNATURE`.

Typical false positives: company domains under blacklisted TLDs; reversed `in-addr.arpa` strings; too-short third-party IOC domains matching longer benign names.

Evaluate the FQDN and IP against approved threat intelligence (disclosure approval required) and whether a suspicious-TLD name is plausibly corporate.

## Hosts

Evaluates hosts-file entries ("New hosts entry", "Suspicious entry found in Hosts file").

| Question | Direction (weight) |
|---|---|
| New entry looks legitimate (development mapping) | benign (M) |
| Entry redirects a security vendor's update server | malicious (M) |
| Entry maps a well-known or security domain to an unexpected address, including loopback or local addresses that block updates | malicious (M) |

Some security tools add immunisation entries; verify before escalating.

## UserAccounts and LoggedIn

UserAccounts checks suspicious names, Administrators membership, active Guest accounts, accounts created on Sundays and recent logons; with a hot time frame (`-f`) it flags activity on given dates. LoggedIn checks current sessions.

| Question | Direction (weight) |
|---|---|
| Suspicious name that is plausible in the organisation (short initials) | benign (M) |
| Guest account active although it should not be | malicious (H) |
| Guest account in local Administrators | malicious (H) |
| Account activity inside the declared hot time frame | malicious (M) |

## Firewall

Evaluates local firewall rules with allow and block lists. A legitimate service on a non-standard port is a common false positive. Check whether the port matches the rule's product.

## HotfixCheck

Reports outdated systems (no hotfix for 90 days). If THOR could not read hotfix information it may report none; that is a collection gap, not a vulnerability finding.

## VulnerabilityCheck

Covers a small set of vulnerabilities used for lateral movement or persistence; YARA rules for vulnerabilities start with `VUL_`. Inactive configurations (backups, localhost-only services) are not relevant. A vulnerability is exposure, not compromise.

## WER (Windows Error Reporting)

Analyses crash reports. Crashed exploits, scanners, dumpers or backdoors can remain visible here after attackers removed their tools. A CVE reference in the message is a malicious indicator (M); ordinary application crashes are common false positives.

## Mutex and Named Pipes

Match names against IOCs (full THOR's private IOC set includes mutexes and named pipes). A match is a strong lead because names are often malware-specific, but generic names collide. Correlate with the owning process.

## Rootkit, SkeletonKey, ReginFS

Treat messages from these modules as relevant and high priority. Validate with memory forensics and domain controller review.

## DeepDive

Findings on memory images or raw disk regions cannot be judged from THOR events alone; the dump or recovered chunk is needed. Analyse only when other indicators justify it. Typical false positives: AV signatures in `pagefile.sys`, security-product data folders, THOR's own process dumps.

## Init, Info and Error events

Scan metadata: version, flags, start/end, resource-control warnings (`Rescontrol`), module errors. Use them to establish coverage. Errors and resource limits are coverage gaps that belong in the limitations.
