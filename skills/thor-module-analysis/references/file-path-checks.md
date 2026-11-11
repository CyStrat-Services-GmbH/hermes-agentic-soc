# File path checks

Apply to every path in a THOR event, whatever the module. Source: [THOR Log Analysis Manual, File Path Checks](https://log-analysis-manual.nextron-systems.com/en/latest/). Weights: L low, M medium, H high.

| Question | Direction (weight) |
|---|---|
| In a temporary directory (`C:\Temp`, `…\AppData\Local\Temp`, `C:\Windows\Temp`) | malicious (M) |
| Path contains local-language business terms (`…\Datensicherung`, `C:\Progs\Zeiterfassung\`) | benign (M) |
| The same file matches on more than 1 / more than 10 systems | benign (M) |
| The same file matches on more than 100 systems | benign (H), unless strong indicators say otherwise |
| Public search for the file name points to goodware or Windows components | benign (M) |
| Public search for the file name points to malware or hack tools | malicious (M) |
| An exact search for the full path returns nothing | malicious (L) |
| Sandbox or AV reports exist for the name or path | malicious (M) |
| Looks like a backup directory or a home folder on a server drive | benign (M) |
| In `%AppData%` of a user profile | malicious (L) |
| In a folder that should not hold executables (`C:\Windows\Fonts`, `C:\PerfLogs`, `C:\Windows\inf`, `C:\Users\Public\Documents`, `…\Microsoft\certs`) | malicious (M) |
| File name looks like an admin tool (`C:\robocopy-migration.exe`) | benign (L) |
| Mounted or shared network path (`\\tsclient\C$`, `\\server1\C$\temp\m.exe`) | malicious (M) |
| Looks like odd but plausible custom software (`C:\Temp\Arbeitszeitnachweis\AZN-service.exe`) | benign (M) |
| Executable directly in a folder that normally holds only subfolders (`C:\ProgramData\1.exe`) | malicious (M) |
| A renamed file that a user likely changed to pass filters (`ChromePortable.txt`) | benign (L) |

## Plugin-specific notes

- The plugin pseudonymises the first path segment after `C:\Users\`, `/home/` and `/Users/`, including well-known profiles such as `Public` or `Default`. Check the original restricted export before reading a pseudonymised segment as a personal account.
- Public web searches disclose the searched term. Searching a generic file name is usually acceptable; searching a customer-specific path, host name or user name is not without data-sharing approval.
