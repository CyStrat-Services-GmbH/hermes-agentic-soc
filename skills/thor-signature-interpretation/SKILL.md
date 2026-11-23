---
name: thor-signature-interpretation
description: "Interpret THOR scores, levels, reasons and rule names: how the total score is calculated, why levels can differ from scores, what signature types (YARA, filename/keyword/hash/C2 IOCs, Sigma, anomaly checks) and rule prefixes (MAL, HKTL, WEBSHELL, EXPL, VULN, SUSP, PUA) mean and how much weight each deserves. Use when a THOR event's score or rule name drives a triage decision; not as a substitute for module context or false-positive review."
---

# THOR scores, reasons and rule names

A THOR score expresses confidence and severity together, from 0 to 100. A rule name expresses what the signature author was looking for. Neither is a verdict on your incident. This skill tells you how much each one actually says.

## How THOR scores

- **Signature scores** ([scoring system](https://thor-manual.nextron-systems.com/en/latest/usage/other-topics.html), [scoring and levels](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-log-analysis/references/scoring-and-levels.md), [custom signatures](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-custom-signatures/SKILL.md)):
  - YARA: the rule's `score` meta, 75 if it has none. A `falsepositive` meta turns the rule's score negative. Combined with a negative `score` it flips back to positive.
  - Filename IOC: the score in the second CSV field; negative values are allowed.
  - Hash IOC: 100 for `hash` or `hash;description`, otherwise the given score. THOR 11 YAML IOCs have no default: an omitted score counts as 0.
  - Keyword IOC 70, C2 IOC 75, named-pipe IOC 100, mutex/event IOC 70, STIX IOC 75.
  - Sigma: by rule level, low 40, medium 50, high 70, critical 100. In THOR 11 a custom `score:` field in the rule overrides the level.
  - Trusted-hash IOC files: THOR 10 drops all Filescan reasons of the file; THOR 11 adds -100, so the total becomes 0.
- **Total score.** Sub-scores are not added. They are sorted descending and combined so that each further reason weighs half as much as the previous one:

  ```text
  100 * (1 - (1 - s0/100/2^0) * (1 - s1/100/2^1) * (1 - s2/100/2^2) * …)
  ```

  Several weak reasons therefore cannot simply add up to an alert. Positive sub-scores are capped at 100. Each negative sub-score multiplies the remaining uncertainty by `(1 + |s|/100)`: it lowers the total but cannot pull a 100 down. A sub-score of -100 or lower forces the total to 0.
- **Alert condition.** Every alert needs a total of at least 81 **and** at least one sub-score above 75 (THOR 11: 76 or higher). A total of 81 or more without such a sub-score is a Warning, and a Warning can reach 100: two default YARA hits (75, 75) give 84, a Warning ([scoring and levels](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-log-analysis/references/scoring-and-levels.md)).
- **Default levels.** Notice from 40, warning from 60, alert from 81. THOR 10 lets operators change these with `--notice`, `--warning` and `--alert`. THOR 11 fixes them; those flags are deprecated and ignored there. In both versions `-x`/`--min` (default 40) hides lower scores ([CLI flags](https://thor-manual.nextron-systems.com/en/latest/usage/flags.html), [flag map](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor/references/flag-map-v10-v11.md)).
- **Unscored findings (THOR 10).** Some THOR 10 findings carry no score at all, for example the SHIMCache Warning `Found entry in suspicious directory`. `--min` does not filter them. Treat the level as given and the score as unknown ([scoring and levels](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-log-analysis/references/scoring-and-levels.md)).
- **Shown reasons.** Only positive scores and, by default, the top two reasons are printed. `--max-reasons` (THOR 10) or `--alert-reason-limit` (THOR 11) changes this; `--intense`, `--deep` and `--lab` print all. The real count is in `REASONS_COUNT` (text), `reasons_count` (THOR 10 JSON v1) or `reason_count` (THOR 11 JSON); THOR 10 JSON v2 has no count. A missing reason in the export is not evidence that no other reason existed.

Plugin behaviour: the exported level takes precedence over the default score bands. `score_level_disagreement_count` in the inventory shows how often the level and the plugin's score-only band disagree. Disagreement is expected and is not data corruption: a score of 81 or more without a sub-score above 75 is exported as Warning by design. On THOR 10, custom thresholds are a further cause; THOR 11 thresholds are fixed. The plugin never sums reason scores to invent a total.

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
| Sigma (full THOR and THOR Lite 11; THOR Lite 10 only with the `allowsigma` licence special) | A log-event pattern | Depends on the rule level and log context |
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

- THOR lists initialised rules with `--print-signatures` (THOR 10) or `--list-signatures` (THOR 11).
- Nextron's public VALHALLA rule info page (`https://valhalla.nextron-systems.com/info/rule/RULE_NAME`) shows metadata, past matches and AV verdicts; lookups are rate limited ([analysis and info](https://thor-manual.nextron-systems.com/en/latest/usage/analysis-and-info.html)).
- This plugin performs no lookups. A rule name alone is not customer data, but do not combine it with host, path or customer identifiers in any external query.
- THOR Lite ships only the open-source signature base, plus YARA Forge rules and the operator's own signatures if installed. A rule from Nextron's private set cannot appear in a Lite result.
- Nextron's companion skills, if installed: `thor-custom-signatures` documents IOC file formats, YARA meta attributes and how custom signatures are scored; `thor-log-analysis` explains levels and the scoring formula with worked examples.

## Output block

```text
Event <E-ID> · Score <Score> · Level <Level> (Default-Band: <Band>)
Gründe: <Regel (Sub-Score)>, … (ggf. gekürzt durch --max-reasons / --alert-reason-limit)
Signaturtyp: <Hash / YARA spezifisch / YARA generisch / Filename IOC / Keyword / C2 / Sigma / Anomalie>
Präfix-Lesart: <z. B. HKTL = Tool-Präsenz, keine Nutzung belegt>
Aussagekraft: <hoch / mittel / gering> – Begründung: <…>
```
