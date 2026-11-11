---
name: thor-signature-interpretation
description: "Interpret THOR scores, levels, reasons and rule names: how the total score is calculated, why levels can differ from scores, what signature types (YARA, filename/keyword/hash/C2 IOCs, Sigma, anomaly checks) and rule prefixes (MAL, HKTL, WEBSHELL, EXPL, VULN, SUSP, PUA) mean and how much weight each deserves. Use when a THOR event's score or rule name drives a triage decision; not as a substitute for module context or false-positive review."
---

# THOR scores, reasons and rule names

A THOR score expresses confidence and severity together, from 0 to 100. A rule name expresses what the signature author was looking for. Neither is a verdict on your incident. This skill tells you how much each one actually says.

## How THOR scores

- **Signature scores.** YARA rules carry a score in their metadata; filename IOCs carry one in their second CSV field; hash IOCs default to 100; keyword and C2 IOCs map to warning or alert defaults. YARA rules flagged `falsepositive` reduce an element's score ([scoring system](https://thor-manual.nextron-systems.com/en/latest/usage/other-topics.html)).
- **Total score.** Sub-scores are not added. They are sorted descending and combined so that each further reason weighs half as much as the previous one:

  ```text
  100 * (1 - (1 - s0/100/2^0) * (1 - s1/100/2^1) * (1 - s2/100/2^2) * …)
  ```

  Several weak reasons therefore cannot simply add up to an alert.
- **Alert condition.** File system alerts additionally require at least one sub-score above 75 (alert threshold minus 25).
- **Default levels.** Notice from 40, warning from 60, alert from 81 on the command line (`--notice`, `--warning`, `--alert`). Operators can change these thresholds ([CLI flags](https://thor-manual.nextron-systems.com/en/latest/usage/flags.html)).
- **Default scores for unscored messages:** warning 60, alert 80.
- **Shown reasons.** Only positive scores and, by default, the top two reasons are printed. `--max-reasons` changes this. A missing reason in the export is not evidence that no other reason existed.

Plugin behaviour: the exported level takes precedence over the default score bands because thresholds may have been customised. `score_level_disagreement_count` in the inventory shows how often level and default band disagree; a high count usually means custom thresholds, not data corruption. The plugin never sums reason scores to invent a total.

## Signature types and their weight

| Type | What matched | Typical reliability |
|---|---|---|
| Hash IOC | Exact file content | High for identity of the file; says nothing about use |
| YARA (specific strings) | Content characteristic of a family or tool | High when strings are unique; check the rule's purpose |
| YARA (generic/anomaly) | Capabilities, obfuscation, structure | Medium to low; frequent false positives |
| Filename IOC (exact) | A known tool or malware file name | Medium; names are trivially reused |
| Filename IOC (regex) | A naming pattern | Low; frequent false positives |
| Keyword IOC | A string in a log line, command line or registry value | Medium; context decides |
| C2 IOC | A known C2 domain or IP | Medium to high; check freshness and sinkholes |
| Sigma (full THOR) | A log-event pattern | Depends on the rule level and log context |
| Anomaly checks | Location, extension, size, signature, parent/child, timestamp anomalies | Low alone; meaningful in combination |

## Rule name prefixes

Nextron's signature base and the community YARA style guide classify rules by the leading category ([YARA Style Guide](https://neo23x0.github.io/YARA-Style-Guide/)). Interpret them as the signature author's hypothesis:

| Prefix | Meaning | Analyst reading |
|---|---|---|
| `MAL_` | Malware | Strong lead. Validate the specific family claim with the file. |
| `HKTL_` | Hack tool | Tool presence, not use. Authorised admins and pentesters use these too; check authorisation and context. |
| `WEBSHELL_` | Web shell | High relevance inside a web root used by an active server; low in archives of old code. |
| `EXPL_` | Exploit code | High relevance in productive paths; check for PoC collections or security research folders. |
| `VULN_` / `VUL_` | Vulnerable component or configuration | Exposure, not compromise. Route to vulnerability management. |
| `SUSP_` | Suspicious characteristics, anomalies | Lower confidence; frequent false positives; needs corroboration. |
| `SUSP_APT_` | Forensic artefacts typical of intrusions (tool output, command-line patterns) | Relevant: these describe traces left by activity, not a product. |
| `PUA_` | Possibly unwanted application | Policy issue in most cases. |
| `APT_` (secondary classifier) | Associated with a nation-state actor in the rule author's research | Never attribution by itself. |

Rules without a category prefix (older rules, custom rules, Sigma titles) need the same skepticism: read the description and reference if available.

## Looking up a rule

- THOR lists initialised rules with `--print-signatures`.
- Nextron's public VALHALLA rule info page (`https://valhalla.nextron-systems.com/info/rule/RULE_NAME`) shows metadata, past matches and AV verdicts; lookups are rate limited ([analysis and info](https://thor-manual.nextron-systems.com/en/latest/usage/analysis-and-info.html)).
- This plugin performs no lookups. A rule name alone is not customer data, but do not combine it with host, path or customer identifiers in any external query.
- THOR Lite ships only the open-source signature base. A rule from Nextron's private set cannot appear in a Lite result.

## Output block

```text
Event <E-ID> · Score <Score> · Level <Level> (Default-Band: <Band>)
Gründe: <Regel (Sub-Score)>, … (ggf. gekürzt durch --max-reasons)
Signaturtyp: <Hash / YARA spezifisch / YARA generisch / Filename IOC / Keyword / C2 / Sigma / Anomalie>
Präfix-Lesart: <z. B. HKTL = Tool-Präsenz, keine Nutzung belegt>
Aussagekraft: <hoch / mittel / gering> – Begründung: <…>
```
