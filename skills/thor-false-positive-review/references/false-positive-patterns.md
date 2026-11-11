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

## Environment-specific

- Systems running SentinelOne can produce many ProcessCheck false positives.
- Very old Windows versions (XP, 2003) show unusual parent/child relations and process priority warnings.
- Application crashes in Windows Error Reporting are mostly ordinary software faults.

## Patterns that look benign but must not be dismissed

- An admin tool combined with a random-name service, an unusual scheduled task or a temp-folder batch file on the same host.
- A "security product" process whose image path or signer does not match the installed product.
- A Recycle Bin item whose hash does not match the claimed legitimate tool.
- Any finding from Rootkit, SkeletonKey or ReginFS modules: always high priority.
