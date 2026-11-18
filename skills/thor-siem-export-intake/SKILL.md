---
name: thor-siem-export-intake
description: "Prepare THOR results that arrive as SIEM or CSV exports (Splunk, Elastic, other log platforms, THOR's hash CSV) for analysis: identify the actual format, convert embedded THOR JSON into NDJSON for thor_parse, reconcile row counts, and document filters, truncation and multi-source duplicates. Use before thor-assessment whenever THOR data did not come as a native thor.json; not for estimating counts from unsupported formats."
---

# THOR results from SIEM and CSV exports

Many THOR cases start from a search result rather than from the scanner's own file. The export's format decides what the plugin can analyse, and the search that produced it decides what the analysis can claim.

## 1. Identify the format

Inspect the header and a few rows, without interpreting content yet:

| Format | How to recognise it | Path |
|---|---|---|
| A. THOR JSON per row | A raw/message column holds one complete JSON object per row (fields such as `module`, `level`, `message`, `log_version`) | Convert to NDJSON (step 2), then `thor_parse`. JSON v1 rows (flat `reason_1`, `subscore_1` keys) are refused; ask for an export of a `--jsonv2` log. |
| B. THOR text or syslog lines | Raw column holds `KEY: value` text (e.g. `MODULE: Filescan MESSAGE: …`) | Not supported by `thor_parse`. See step 4. |
| C. THOR hash CSV | Three columns, no header: MD5, path, score. THOR 10 and THOR 11 both write it by default (`<host>_files_md5s.csv`) for file findings at or above `--min` ([output options](https://thor-manual.nextron-systems.com/en/latest/usage/output-options.html), [log formats](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-log-analysis/references/log-formats.md)) | Too limited for an assessment: no level, module or reasons. Request the scan's text or JSON log instead. |
| D. THOR JSON v3 | `type` begins with `THOR `, nested object model | Convert to NDJSON (step 2), then `thor_parse`, which reads v3. THOR 11 cannot write v2 (`--jsonv2` has no effect there), so do not ask for a v2 export of a THOR 11 scan ([flag map](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor/references/flag-map-v10-v11.md)). Field shapes: [json-v3-shape.md](../thor-assessment/references/json-v3-shape.md). |
| E. SIEM-normalised fields only | Columns already mapped to the SIEM's schema, no raw event | Analyse as SIEM data, not as THOR output. State the mapping you relied on. |

## 2. Convert embedded JSON (format A)

Conversion must not change the event count.

1. Take the raw column only, one JSON object per line, UTF-8, no header.
2. Count non-empty export rows and NDJSON lines. They must be equal.
3. Place the NDJSON in an operator-approved evidence root. Keep the original export unchanged next to it and record both SHA-256 values.
4. Run `thor_parse`. Its `event_count` must equal the row count. If not, stop and explain the difference before any assessment.

Use an operator-approved code-execution tool for steps 1 and 2. If none is available, ask the operator to perform the conversion with documented commands. Never re-type or summarise rows.

## 3. Document the export's limits

Record in the case and repeat in Summary and Assessment:

- **Search and filter.** The exact query (e.g. `_raw contains "execute.bat"`), index or data view, and time range. A filtered export is not a complete host timeline, and the absence of other events proves nothing.
- **Truncation.** SIEM UIs and APIs cap result sets. Compare the export's row count with the search's total hit count.
- **Ingestion duplicates.** The same THOR event may be indexed twice (e.g. syslog and file ingestion), and the same source event may appear as live Eventlog, EVTX and security-product log entries. Deduplicate by THOR fields and source identifiers, and explain the pattern.
- **Field mapping.** SIEM parsers rename and drop fields. Prefer raw values over parsed ones.
- **Time.** Distinguish the SIEM's index time, THOR's event time and the artefact's time.

Elastic's Nextron THOR integration ingests unencrypted THOR v2 JSON logs through its own pipeline ([Elastic integration](https://www.elastic.co/docs/reference/integrations/nextron_thor_apt_scanner)); exported documents may carry Elastic field names instead of raw THOR fields.

THOR can also forward events itself (`-s host:port:FORMAT:PROTOCOL`, formats such as CEF or JSON). A JSON target fed by THOR 11 receives v3 objects ([log formats](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-log-analysis/references/log-formats.md)). Nextron's `thor-deployment` skill, if installed, describes these forwarding options; `thor-maintenance` covers `thor-util logconvert`.

## 4. Unsupported formats (B, C, E)

The plugin's deterministic tools cannot count or correlate these formats. You may still analyse them, under stricter rules:

- Count programmatically with an operator-approved code-execution tool and keep the script with the case. Never estimate from visible rows.
- Mark the case "ausserhalb der Tool-Unterstützung analysiert" and do not present results as `thor_first_assessment` output.
- Apply the same evidence-strength labels, credential rules and nine-section structure from `agentic-soc:thor-assessment`.
- Prefer requesting the native JSON log. It is almost always the better evidence.

## Output block

```text
Exportquelle: <SIEM/Index/Datei> · Format: <A–E> · Abfrage/Filter: <…> · Zeitraum: <…>
Zeilen im Export: <n> · Treffer laut Suche: <n> · NDJSON-Zeilen: <n> · thor_parse event_count: <n>
SHA-256 Original: <…> · SHA-256 NDJSON: <…>
Bekannte Duplikatquellen: <…>
Einschränkungen für die Bewertung: <…>
```
