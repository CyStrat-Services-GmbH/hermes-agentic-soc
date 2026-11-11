# Export inventory when `thor_parse` cannot run

`thor_parse` and `thor_first_assessment` accept THOR JSON v1/v2 only. They return `BOUNDARY_REJECTED` for **THOR JSON v3** (`"… unsupported events (including possible THOR v3)"`), for a **plain-text report** (`"Malformed JSON/NDJSON"`) and for truncated NDJSON. A refusal is not a reason to sample. Count the export yourself with the recipes below, then reconcile against the export's own `Report` module — that reconciliation is the evidence that your inventory is complete.

A refusal is a legitimate tool outcome: quote it in the case's `Analysegrundlage` instead of working around it silently.

## JSONL v3 (`log_version: v3.0.0`)

One object per line, two `type` values: `THOR assessment` (findings, every one carries a `score`) and `THOR message` (lifecycle, progress, `Report`). Messages are not assessments.

```text
{
  "type": "THOR assessment",
  "meta":   {"time": "<+02:00>", "level": "Alert|Warning|Notice|Info", "module": "<name>", "scan_id": "S-…", "hostname": "<host>"},
  "message":"Suspicious file found",
  "score":  84,
  "subject": {"type": "file", "path": "C:\\…", "hashes": {"md5":"…","sha1":"…","sha256":"…"}, "file_times": {…}, "pe_info": {…}},
  "reasons": [{"summary": "YARA rule <NAME> / …", "signature": {"score": 75, "kind": "YARA Rule", "rule_name": "<NAME>"}, "matched": [{…}]}],
  "ancestors": null, "derivatives": null
}
```

What breaks naive v1/v2 scripts: level/module/host/scan live under `meta.`; the artefact is `subject.` behind a `type` discriminator (`file`, `process`, `eventlog entry`, `Windows service`, `registry value`, `registry key`, `shim cache`, `shim database entry`, `AmCache entry`, `process start`, `hotfix summary`, `autorun entry`, `scheduled task`, `WMI startup command`, `antivirus exclusion`); `reasons` may be `null`; timestamps are RFC 3339 with offset.

```python
import json, collections
rows = [json.loads(l) for l in open(path, encoding='utf-8-sig') if l.strip()]
A = [r for r in rows if r.get('type') == 'THOR assessment']
collections.Counter(r['meta']['level'] for r in A)   # Alert/Warning/Notice/Info
collections.Counter(r['meta']['module'] for r in A)
collections.Counter(r.get('score') for r in A)        # full histogram, not just the maximum
print(len(rows), len(A), len(rows) - len(A))          # lines, assessments, messages
```

Collect unique paths and hashes from `subject` only. A recursive walk over the whole event also picks up `ancestors` and `derivatives` and inflates the numbers.

## Text report (`…_thor_<date>_<time>.txt`)

One record per line, always the same shape — verified against a full multi-thousand-line export with zero non-conforming lines:

```regex
^([A-Z][a-z]{2} +\d+ \d\d:\d\d:\d\d) (\S+)/(\S+) THOR: (Info|Notice|Warning|Alert|Error): MODULE: (\S+) (.*)$
```

Group 1 timestamp, 2 hostname, 3 IP, 4 level, 5 module, 6 payload. The payload is a `KEY: value` stream (`MESSAGE:`, `SCANID:`, `SCORE:`, `FILE:`, `SHA256:`, `REASON_1: … SUBSCORE_1: … REF_1: … MATCHED_1: …`, `PID:`, `COMMAND:`, `PROCESS_NAME:`, `IMAGE_FILE:`). Split on the known keys, never on `:` — `FILE:` values contain drive colons and `COMMAND:` values contain quoted paths.

Two traps:

- **No year in the timestamp.** The year comes from the file name and is confirmed by the `Report` line `Begin Time: Tue Aug 18 15:27:27 2026`. State the derivation; never imply the year was in the data.
- **The line prefix is local wall-clock while `Eventlog` payload fields are UTC.** Windows `TimeCreated_SystemTime` differs from the prefix by the UTC offset. Convert explicitly and label which clock you used.

```python
import re, collections
pat = re.compile(r'^([A-Z][a-z]{2} +\d+ \d\d:\d\d:\d\d) (\S+)/(\S+) THOR: (Info|Notice|Warning|Alert|Error): MODULE: (\S+) (.*)$')
recs = [m.groups() for m in map(pat.match, open(path, encoding='utf-8-sig').read().splitlines()) if m]
collections.Counter(r[3] for r in recs)
collections.Counter(r[4] for r in recs)
```

A text export has no module-wide hash inventory: hashes exist only on individual findings. Never claim a unique-file or unique-hash count from a text report — say the count is not derivable in that format.

## Reconciliation (the completeness check)

| Export | Report line | Meaning |
|---|---|---|
| JSONL v3 | `Assessments` → `{"alerts":n,"warnings":n,"notices":n,"infos":n}` | Must equal your level counter over assessments |
| JSONL v3 | `Messages` → `{"errors":n,"notices":n,"infos":n}` | Lifecycle lines; `errors` must be 0 on a healthy scan |
| JSONL v3 | `Begin Time` / `End Time` / `Scan took …` | Scan duration for the case header |
| Text | `Results` → `ALERTS: n WARNINGS: n NOTICES: n ERRORS: n` | Must equal the per-level line counts |
| Text | `Thor Version`, `Thor Build`, `Effective argument list`, `Signature Database`, `Sigma Database` | Edition, flags and signature base for `Analysegrundlage` |

One unit of disagreement means the export is truncated or filtered. A filtered export is a scope statement, not a data set.

## Numbers worth quoting in `Analysegrundlage`

- Line count, assessments, messages and unparsable lines — all four, separately.
- Level distribution and the full score histogram.
- Per-module level matrix, so a reader can see where the export is dense.
- Unique paths and unique hashes **from `subject` only**, with the denominator named (assessments, not lines).
- Observation groups by artefact identity, and the analyst finding count with the reason for the difference.
- Scan duration, THOR version and build, flags, signature and Sigma database versions, plus every coverage warning (disabled components, log-object limits, channels that could not be opened).

## Pitfalls

- **The `Messages` counter excludes the `Report` block.** In THOR 11 exports the `Messages` line (`{"errors":…,"notices":…,"infos":…}`) counts only non-report messages; the export still contains the 7 `Report`/`Init`-report lines (`Assessments`, `Messages`, `Begin Time`, `End Time`, `Scan took …`, `Thor Scan finished`, log-file note). So `messages_parsed = infos + notices + 7`. Reconcile with that offset instead of reporting a 7-line mismatch. `errors` must still be 0.
- **Match limits make rule counts lower bounds.** `MatchLimit` notices (`Rule triggered more than 10 times. Future matches will be suppressed`) mean the export stops listing further matches for that rule. Quote the count as "n shown, further matches suppressed" and never as the total. In THOR 11 this hits bulk Sigma rules first (`Important Windows Event Auditing Disabled`, `Suspicious Process By Web Server Process`, `System Processes CLI Anomaly`).
- **Boot time from process creation times.** `Init` → `System Information` → `uptime` is reported in a unit that does not always match seconds and can contradict the rest of the export. Derive the boot time from the creation times of `smss.exe`/`csrss.exe`/`wininit.exe`/`services.exe` in `ProcessCheck` and cross-check any "running since …" claim against it before asserting continuous runtime.
- **A single `SUSP_Echo_Pipe_Pattern_*` fact lands in many containers.** The same `cmd.exe /c echo <x> > \\.\pipe\<x>` string is reported in the Eventlog entry, the registry hive, `SYSTEM.LOG1`, `System.evtx`/`Security.evtx`, the Defender MPLog (`LogScan`) and often `access.log`. Count it once and merge every hit onto the originating event.
- **A unique-hash count over the whole export is dominated by benign `Info` events.** Thousands of hashes from `ServiceCheck`, `Firewall` and `Amcache` mean nothing as an indicator; quote per artefact family.
- **Grouping by module alone over-reports massively.** `Amcache` and `RegistryChecks` describe the same `Amcache.hve` content, so one executed binary can produce 20+ rows. Group by path, hash or command line.
- **Score is not level.** Events can sit at score ≥ 80 while exported as `Warning`; report the disagreement instead of recounting alerts.
- **Module totals are not finding counts.** `Starting module`, `Skipping entries older than …` and per-path progress lines inflate them.
- **Two exports of one host need a module diff**, not a union: a module missing from the later export is a coverage gap in that run.
- **Object log limits and disabled components are coverage**, not noise: mutex, event, firewall-rule and scheduled-task limits mean further objects were only logged when suspicious, and `Integritycheck`/`KnowledgeDB`/`Auditlog` being disabled narrows the case.
