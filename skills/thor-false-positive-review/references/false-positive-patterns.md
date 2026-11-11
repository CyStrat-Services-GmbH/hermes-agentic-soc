# Known THOR false-positive patterns

Sources: [THOR Log Analysis Manual](https://log-analysis-manual.nextron-systems.com/en/latest/) and [THOR Manual](https://thor-manual.nextron-systems.com/en/latest/). Every pattern below still needs verification on the specific case. A pattern explains a finding; it does not dismiss it automatically.

## Signatures in the wrong place

| Pattern | How to verify |
|---|---|
| YARA match in the memory of an AV, EDR or security tool (CarbonBlack, GRR and similar) | Process image path and signer belong to the installed product. |
| YARA match in VMware Tools or browser process memory | Same; VMware Tools may hold a copied THOR binary. |
| THOR reports, logs or clear-text signatures left from earlier scans | Path is a THOR working or output directory; timestamps match earlier scans. |
| AV signatures in `pagefile.sys`, disk-surface DeepDive or security-product data folders | DeepDive finding without corroboration; product data paths. |
| THOR's own process dumps | Dump directory of a previous THOR run. |
| Hash-named copies in a vendor remediation or snapshot folder (`...\SARemediation\SystemRepair\snapshots\backup\<40 hex>.exe`) | The directory is a product backup store. These copies routinely trigger every "renamed binary" rule at once — `powershell_ANOMALY`, `SUSP_Renamed_Mshta`, `SUSP_Renamed_RunDLL32`, `APT_Cloaked_CERTUTIL`, `SUSP_Renamed_CreateDump`, `SUSP_Renamed_BrowserCore`, `SUSP_Renamed_Fsquirt`, `SUSP_Cloaked_WScript` — because the filename is a hash. A bundled vulnerable-driver hit (`PUA_VULN_Driver_*`) in the same folder is a stored copy, not a loaded driver: check ServiceCheck and the loaded-module list before treating it as a driver load. One such folder can dominate an entire export. |
| YARA hits inside a vendor AV/EDR module directory (`em018_64.dll`, `em003_64.dll`, `em035_64.dll` below `Program Files\<vendor>\...\Modules\`) | Security products embed sample handling logic. Rules for credential-stealer indicators, wallet extension IDs, browser profile paths and AMSI patching fire on their own modules. Verify signer and product path. |
| `ProcessIntegrity` → `PE-Sieve found process with implanted/patched section` on many processes | With an AV/EDR that hooks APIs installed, PE-Sieve reports implanted or patched sections in most signed system and browser processes (`svchost.exe`, `firefox.exe`, `explorer.exe`, `dwm.exe`). That is the normal state of a hooked process tree, not injection. Corroborate with the process signer and the installed security product before reporting. |
| SHIMCache or AmCache entries for THOR itself run from `C:\Temp\` or `C:\thor\` | Path matches the documented THOR run location. |
| Compressed or archived output of an earlier THOR scan (`*.jsonl.gz`, `*.7z`, `*.zip` wrapping an audit JSONL) | Score 90+ appears because the archive still holds the previously reported match strings, so every rule that fired before fires again inside the container. Verify via the archive fields (`ARCHIVE_FILE`, `ARCHIVE_TYPE`, `EXISTS: nonlocal`), a path under the THOR run or download directory, and a file name carrying an earlier scan ID. Self-reference, not a new finding. |
| `LM_hash_empty_String` plus a `SUSP_ShellcodeIndicator_*` rule stacking to score 90+ in the memory of a signed Microsoft binary (`winlogon.exe`, `msedge.exe`, `WindowsTerminal.exe`) | `LM_hash_empty_String` matches the well-known empty-LM-hash constant that sits in many Windows memory images, and the shellcode indicators match generic byte sequences in Chromium and logon code. Verify: image owner `NT SERVICE\TrustedInstaller`, unchanged image SHA-256 across a second scan, the same rule pair also hitting other signed vendor binaries in the same export, and no file, service or command-line artefact behind it. Do not call it malicious on the rule pair alone — and do not call it benign without that second reference either. |
| Content matches in registry hives, `.evtx` files, MPLog, `access.log` or `pagefile.sys` for a string a real attack command produced (`SUSP_Echo_Pipe_Pattern_Jun26`, `SUSP_Commands_Disabling_Windows_Firewall_Jul23`, `SUSP_PS1_Cmdlet_Defender_Exclusion_Apr21_1`) | Same fact stored in several artefacts, not several findings: one `cmd.exe /c echo <name> > \\.\pipe\<name>` leaves its command line in Event 7045/4688, the registry, the hive copies, the evtx containers and the Defender log. Tie every hit back to the originating event and count it once. |

## Legitimate software that looks odd

| Pattern | How to verify |
|---|---|
| Dual-use admin tools (`nmap.exe`, `ncat.exe`, Sysinternals, remote administration tools) | Authorised by IT; installed in a standard location; consistent with role of the host. |
| Hack tool in a standard package or backup location (`/usr/bin/ncat`, `/backups/…/bin/ncat`) | Package manager ownership; backup path. |
| Legitimate tools in the Recycle Bin under renamed names (`$IR4HB6A.exe`) | Original name in the Recycle Bin metadata; hash of the known tool. **The `$R` + six random characters form is the standard Recycle Bin nomenclature for every deleted file**, so a rule named "renamed \<product>" fires on any deleted copy of that product by construction. Do not read it as deliberate masquerading; check `$I` metadata for the original name and path. |
| Very old files triggering size or signature anomalies | Age, product folder, vendor signature. |
| Old or rare versions of legitimate programs (frequently `java.exe`/`javaw.exe`, unsigned in vendor product folders) | Product installation path and vendor. |
| Legitimate software or services in `%AppData%` or other unusual locations | Known product; signer; installation records. |
| Admin-registered services in odd places (`C:\srvany.exe`) | Change record or admin confirmation. |
| Software updaters and admin scheduled tasks | Vendor, signer, business-language task names. |
| New autorun entries after legitimate installations | Software deployment record. |
| Registry keys whose `modified` timestamp falls inside the OS install window (`CMSTP App Paths`, `Internet Explorer\MAIN\FeatureControl\…\msn.exe`) | Compare `subject.modified` with `installed_on` from the System Information event. A `CMSTP App Paths` key written during provisioning is OS setup, not UAC-bypass staging; an IE FeatureControl key from years earlier is a default. The signature cannot tell them apart — the timestamp can. |

## Naming and pattern collisions

| Pattern | How to verify |
|---|---|
| Legitimate files matching a filename regex IOC | Only reason is the name pattern; content and signer are benign. |
| Services or tasks matching regex filename IOCs | Same. |
| `REG_SUSP_Processor_Driver_Registry_Modification` on any non-`winprint.dll` print processor | The rule reports *any* third-party print processor, which every printer vendor driver installs (`OKC04EPP.DLL`, `OKX05HPP.DLL`, `PSCRIPT5.DLL` and similar). Decide on the file, not the registry value: does the DLL exist under `spool\prtprocs\x64`, is it signed by the printer vendor, is there a Spooler load record? If the export contains no file evidence, the finding is `Inconclusive` at best — never auto-close it, because this is also the exact SprySOCKS persistence pattern. |
| Registry values starting with `4d5a` by chance | Value context is not an embedded PE. |
| Company domains under blacklisted TLDs | Domain is registered to the organisation. |
| Reversed `in-addr.arpa` strings matching blacklisted IPs | DNS cache entry is a reverse lookup. |
| Too-short third-party IOC domains matching longer benign domains | Full FQDN is benign. |
| Short legitimate user names flagged as suspicious | Organisation's naming convention. |

## Regional and environmental context

| Pattern | How to verify |
|---|---|
| Keyboard-layout preloads typical for the region | Site location and staff. |
| Connections to "suspicious" GeoIP regions that are local to the site | Site location; business partners. |
| Accounts created or files modified on Sundays where Sunday is a working day | Regional working week. |
| Hosts-file entries on development systems or from AV immunisation tools | Development role; installed tool. |

## Logs and stale data

| Pattern | How to verify |
|---|---|
| Web scans producing HTTP 404 lines in access logs | Response code; scanner source. |
| RoboCopy or backup logs listing hack-tool file names | Log type and job. |
| Very old log files (`…\2003-04-17-access.log`) | Date in path and content. |
| Vulnerable configurations in inactive locations (backups, localhost-only dev installs) | No running service uses the file. |
| "No hotfixes installed" because THOR could not read hotfix information | Other hotfix sources; module errors. |
| A block of Event 4719 ("auditing disabled") in the same second, subject is the machine account `<HOST>$` | Provisioning applies the audit policy as a batch via `auditpol` or GPO. Tampering spreads over minutes and comes from a user or SYSTEM context with a preceding process record. Check the timestamp against `installed_on` before writing "anti-forensics". |
| `SHIMCache is suspiciously empty` with `entries: 0` on Windows 11 or Server 2022+ | `AppCompatCache` is not maintained the same way on modern builds, so an empty result is a platform state there. Look for a *change* to 0 between two scans, and for other anti-forensic artefacts. A value of 0 in every export of the same host is not evidence of a flush. |
| ShimDB notices citing malware families ("Russian Business Network", "Typical Malware names VT evaluation", "Internal Investigation Client E2") | These are name lists inside the Application Compatibility shim database, matched without a target path, hash or load event. Without a file and a shim-load record they are `False Positive`. |

## Environment-specific

- Systems running SentinelOne can produce many ProcessCheck false positives.
- Very old Windows versions (XP, 2003) show unusual parent/child relations and process priority warnings.
- Application crashes in Windows Error Reporting are mostly ordinary software faults.

## Patterns that look benign but must not be dismissed

- An admin tool combined with a random-name service, an unusual scheduled task or a temp-folder batch file on the same host.
- A "security product" process whose image path or signer does not match the installed product.
- A Recycle Bin item whose hash does not match the claimed legitimate tool.
- Any finding from Rootkit, SkeletonKey or ReginFS modules: always high priority.
