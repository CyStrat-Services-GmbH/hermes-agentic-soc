# Remote-access and remote-admin tool artefacts

AnyDesk, TeamViewer, ScreenConnect, VNC, Remote Utilities, Atera and the OEM remote-assist tools are dual-use: the binary is usually signed and its presence alone proves nothing, but it is also the shortest path an intruder takes to an interactive session. This class needs its own pass, because the score ordering works against you here.

## Never triage this class by score

THOR scores a remote-access binary by filename and PUA IOC — mid-band, typically 40–72 — and those events lose against security-product false positives sitting at 80. Meanwhile the only artefact that proves an **inbound session** is the tool's own log/trace file, matched by an `INFO_RemoteAdmin_…` rule at around 40. Work the class bottom-up: grep the rule names for `RemoteAdmin`, `AnyDesk`, `TeamViewer`, `ScreenConnect`, `Atera`, `Remote Utilities`, `VNC`, `RAdmin` before you start on the high scores, and read every such event in full even when its level is Notice.

A rule name tells you which artefact matched, never who was on the other end. `INFO_RemoteAdmin_AnyDesk_Session_Remote_IP_Apr23` is an informational rule; the fact that it matched is the finding.

## Which module answers which question

| Question | Module | Field / artefact |
|---|---|---|
| Is the tool installed as a service? | `ServiceCheck` | service name, `image_path`, `start_type`; **absence of a service entry is not evidence the tool was unused** |
| Was it running at scan time? | `ProcessCheck`, `ProcessIntegrity` | live process, `image.path`, `created`; frequently absent |
| Did the image ever run? | `Filescan` on `C:\Windows\Prefetch\<IMAGE>-<HASH>.pf` | `.pf` `modified` ≈ last execution; the file exists because the image ran |
| How did it get there? | `Filescan`, `SHIMCache`, `Amcache` | download copy in `Downloads`, random-suffixed copies in the tool's `temp` directory, `FIRST_RUN` |
| Was there a session, from where? | `Filescan`/`LogScan` on the tool's trace file | `INFO_RemoteAdmin_*` match, e.g. `anynet.any_socket - Logged in from <ip>:<port> on relay <id>` |
| Was the user blocking it? | `RegistryChecks` | firewall rules with `Action=Block` for the tool's image path |
| Persistence? | `Autoruns`, `WMIStartup`, `RegistryHive`, `ScheduledTasks` | Run key, startup folder, task; check separately — portable use leaves none |
| Interactive desktop use? | `RegistryHive` on `NTUSER.DAT` | `FeatureUsage\AppSwitched`, `Shell\MuiCache`, `NotifyIconSettings`, `AppCompatFlags\Compatibility Assistant\Store` |

## The trace file is the only session evidence — and it may be undated

Remote-access tools keep their own logs under the user profile or `ProgramData`. That is where a peer address appears. Three traps:

1. **The match context usually has no timestamp.** The rule captures a substring around `Logged in from` / `New connection`, not the line's leading time. The session is then **Confirmed as an event and `Not Derivable` as to time** — say exactly that, and do not infer a date from the file's mtime, which only bounds the last write.
2. **The trace file is often older than the scan's lookback window.** Its `created` time is a legitimate lower bound for "the tool has been in this profile since", and it survives a `--lookback` scan only because the scan itself writes to it.
3. **One match is one session line, not one session.** A 1 MB trace can hold a single matched login among thousands of unremarkable lines. Request the full file for session count, duration, file transfer and clipboard activity; the export cannot give you those.

## Portable versus installed

A remote-access tool run straight out of `Downloads`, `%TEMP%`, `%ProgramData%\<Tool>\temp` or `%APPDATA%\<Tool>` under a random-suffixed image name (`AnyDesk<4 hex>.exe`, several such copies carrying one identical hash) is the portable/unpacked variant: no service, no uninstaller, no run key, identical hashes across copies because each run unpacks the same source binary. That pattern is characteristic of "quickly let someone in" — support, a vendor session, or an intruder — and it is why service-less operation must not be read as "not used".

Record the distinction explicitly (`installiert` / `portabel`) plus the owner of the profile directory. **The file owner is not the account that started the tool.**

## Execution ranking for this class

Strongest first: `.pf` prefetch file present and its `modified` time → `PcaAppLaunchDic.txt` line → live `ProcessCheck`/`ProcessIntegrity` process → `SHIMCache` with `exec_flag: true` → `Amcache` `FIRST_RUN`. **Not** execution: the `.pf` path appearing as a `FileName:` in an ETL/`BootPerfDiagLogger` record (a boot-time file open), a `MuiCache`/`AppSwitched` value alone (shell bookkeeping), or a `Filename IOC` match on the download copy. See `thor-timeline-correlation/references/timestamp-semantics.md`.

## Output shape for the finding

```text
Tool: <name + version> — <installiert | portabel>, Pfad <…>, SHA-256 <…>, signiert durch <vendor>
Ausführung: <belegt durch …> — letzte belegte Ausführung <Zeit> (<Typ>)
Sitzung: <Gegenstelle + Relay/Session-ID, oder "keine Sitzungszeile im Export">
Sitzungszeit: <Zeit> | Not Derivable – <Grund>
Persistenz: <Run-Key/Dienst/Task oder "keine">
Klassifizierung: True Positive – bestätigte sicherheitsrelevante Aktivität (nicht verwaltetes Fernzugriffswerkzeug)
Nicht belegt: Autorisierung, Urheber, Inhalt der Sitzung, Bösartigkeit des Binaries
```

The classification is almost always **True Positive – Confirmed Security-Relevant Activity**, neither "malicious" nor "false positive": tool and use are real, the intent is unanswered. Reserve `Suspicious – Further Investigation Required` for the session question and name what would settle it — ownership of the peer address, netflow/firewall data for that endpoint, the full trace file.

## Scope follow-ups the export cannot do

- Peer address ownership and reputation need explicit data-sharing approval before any lookup.
- Session time and volume need firewall/proxy/netflow for the peer address, or the tool's server-side console.
- Whether other hosts carry the same tool needs the fleet view (`agentic-soc:thor-fleet-triage`); a single-host export cannot tell a support tool from an intrusion.
- A missing process at scan time is not evidence the tool was unused, and an absent tool is not evidence the host was clean.
