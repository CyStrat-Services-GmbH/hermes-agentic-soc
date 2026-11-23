# THOR JSON v3 (`log_version v3.0.0`) — shapes, counting pitfalls

THOR 11 writes a different container than the v2 JSON the rest of this skill assumes. `thor_parse` reads it directly and marks `THOR message` records as `record_kind: message`; read this before writing your own parser or counting by hand. Nextron's `thor-log-analysis` skill, if installed, maps the same fields across text, JSON v1/v2 and v3.

## Record shape

Every line is one JSON object, JSON Lines, no wrapper array:

```json
{"type":"THOR assessment","meta":{"time":"...+02:00","level":"Warning","module":"Filescan","scan_id":"S-...","hostname":"HOST"},
 "message":"Suspicious file found","score":84,"subject":{...},"reasons":[...],"ancestors":null,"derivatives":null,"log_version":"v3.0.0"}
```

- `type` is `"THOR assessment"` for findings **and** `"THOR message"` for all module status output (Starting/Finished module, Hotfix, Listening process, Error Report, Report summary). Only assessments carry `score` and `subject`.
- `meta.level` lives on both kinds, so a level counter over the whole file **mixes findings with status messages**. A `THOR message` can carry any level, including Warning and Error ([log formats](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-log-analysis/references/log-formats.md)). Filter on `type`, never on level alone.
- Status messages carry their payload in `fields` (`scanned_elements`, `duration`, `scanned`, `object`) and are the only source for module coverage numbers.
- `reasons` is a list of objects or `null`. Each reason has `summary`, `signature` and `matched` ([log formats](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-log-analysis/references/log-formats.md)):
  - `signature` carries `score`, `kind`, `rule_name`, `origin`, `reference`, `tags` and `date`, and where the rule sets them also `author`, `description`, `id` and `false_positives`. `rule_name` carries the real rule identifier.
  - `kind` is one of `YARA Rule`, `Sigma Rule`, `Filename IOC`, `Hash IOC`, `Keyword IOC`, `Named Pipe IOC`, `STIX IOC`, `Domain IOC`, `Handle IOC` or `Internal Heuristic`.
  - `matched` is a list of `{data: {data, encoding}, offset, field, context}`. `encoding` can be `hex`. `field` is a JSON pointer into `subject`, such as `/entry/CommandLine`.
- `subject` is a typed object; the module determines the key. Frequent ones: `file` (Filescan has path/hashes/first_bytes/file_times/permissions/pe_info/content), `process` (pid/name/command/owner/image/parent_info/tree/created/session/listen_ports/connections/handles/threads), `Windows service` (key/key_name/image/failure_command), `eventlog entry` (event_id/time/channel/entry{...raw fields}), `autorun entry`, `scheduled task`, `shim database entry`, `registry key` and `registry value`, `mutex`, `named pipe`, `log line` (line_index/line), `hosts file entry`, `antivirus exclusion`, `hotfix summary`. THOR 11 prints the full list with `--describe-object-type all`.

## Counting pitfalls that changed a number in a real case

1. **Finding events ≠ `1 + warnings + notices` taken from a whole-file level counter.** That counter includes the ≤5 Notice status messages. Compute the finding-event count as `len([r for r in records if r['type']=='THOR assessment' and r['meta']['level']!='Info'])` and reconcile it against the `Report` module's own `alerts/warnings/notices/infos` block. A case once carried 236 where the export held 231.
2. **`MatchLimit` notices are content gaps, not events.** "Rule triggered more than 10 times. Future matches will be suppressed." They do not say *which* rule; record the count and put it in `Grenzen`. In THOR 11 this muting applies to the live Eventlog module only. `--lab` lifts it; `--match-limit 0` does not. It is a different cap from the per-rule hit limit (`--match-limit`, default 100,000), which logs a Warning when reached ([output flags](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-scan/references/output.md)).
3. **"Object type reached the log limit"** appears once per truncated object class (Mutex, Events, Firewall, ScheduledTasks, Amcache). A module's `scanned_elements` then exceeds the number of logged objects by far — never equate logged objects with scanned objects.
4. **`file_size_limit` vs `--max_file_size_intense`** are separate keys in `Scan Information`. THOR 11's default `file-size-limit` is 64 MB; `max_file_size_intense` is deprecated but still honoured. A 30 MB value in a v3 export usually means an in-place upgrade kept the THOR 10 `config/thor.yml` (`max_file_size: 31457280`). Quote the value the export states; it is what bounded Filescan content scanning ([flag map](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor/references/flag-map-v10-v11.md), [upgrade notes](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor/references/versions-and-outputs.md)).
5. **`pe_info.signed` / `signatures[].signature_valid` are unreliable offline** — real Microsoft binaries report `signed:false` or `signature_valid:false`. Never conclude "unsigned" from this field.

## Parsing hygiene (Python)

- Streaming line parse, `json.loads` per line, count `bad_lines` instead of dropping them silently.
- A `rk()` helper that returns a **set** makes `'SUSP_Echo_Pipe' in rk` exact membership, which silently returns False. Write `any(p in x for x in rk)` — this bug silently unmapped 28 events once.
- Lowercase the serialised record once (`js = json.dumps(r).lower()`) and compare lowercase needles against it; mixed-case needles (`'RunAsPPL'`) then never match.
- Assign every finding event to exactly one analyst finding, assert `sum(counts) == finding_event_count`, and print the unmapped records rather than bucketing them into an "other" bucket you never look at. Then extract the finding table's numbers **from the same assignment** — a hand-typed "combined benign" row once said 16 where the code said 19.

## What the per-module field names look like (v3, Windows)

`Eventlog.subject.entry` keeps raw channel fields with underscores in the System keys (`EventID`, `TimeCreated_SystemTime`, `EventRecordID`) and CamelCase for event payload (`CommandLine`, `ParentProcessName`, `NewProcessName`, `SubjectUserName`, `TargetUserName`, `ServiceName`, `ImagePath`, `ThreatName`, `ActionName`, `Path`). Defender `1116/1117` deliver `ThreatName`, `ActionID/ActionName`, `Path` (here: the detected command line), `DetectionID`, `Execution_ProcessID` — `ActionName: "Remove"` plus `ErrorCode: 0x0` still does **not** prove the file was removed.
