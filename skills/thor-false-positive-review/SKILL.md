---
name: thor-false-positive-review
description: "Decide systematically whether a THOR finding is a true positive, an authorised but security-relevant activity, suspicious, inconclusive or a false positive, using THOR's known false-positive patterns, prevalence and context checks. Use for every ALERT and WARNING and every NOTICE that will be reported; also for drafting (not applying) suppression filters. Not for closing findings without a written reason."
---

# THOR false-positive review

THOR deliberately reports too much rather than too little. Most of an analyst's time goes into separating real traces from benign anomalies. Do it systematically, write down the reason, and never close a finding because it is inconvenient.

## Procedure

For each observation (after `thor-module-analysis` and `thor-signature-interpretation`):

1. **Known pattern?** Compare against the catalogue in [references/false-positive-patterns.md](references/false-positive-patterns.md).
2. **Prevalence.** How many hosts show the same rule, path or hash? Per Nextron's experience, the most relevant findings appear on 1–5, sometimes up to 30 endpoints; elements on 100 or more endpoints are most likely false positives unless strong indicators say otherwise ([Log Analysis Manual](https://log-analysis-manual.nextron-systems.com/en/latest/)). Use `agentic-soc:thor-fleet-triage` for the numbers. Never apply this heuristic to a single-host export.
3. **Authorisation.** Is the tool or change explained by documented administration, a security product, a pentest or a change ticket? Ask the asset owner; do not assume.
4. **Context.** Location, owner, signer, age, parent process, persistence and network context (see the module reference). Weigh indicators; one strong malicious indicator beats several weak benign ones.
5. **Contradictions.** Does any other event in the case contradict the benign explanation (e.g. an "admin tool" plus a random service pointing to a temp batch file on the same host)?
6. **Decide and document** using the outcome table below.

## Outcomes

| Outcome | Use when | Required wording |
|---|---|---|
| `True Positive – Confirmed Malicious Activity` | Evidence shows malicious artefacts or activity, not just their possibility. | Which evidence confirms it. |
| `True Positive – Confirmed Security-Relevant Activity` | Real and relevant, but authorised or not malicious (admin tool, pentest output, vulnerable config). | Who authorised it and how it was verified. |
| `Suspicious – Further Investigation Required` | Malicious explanation is plausible and unrefuted. | What would confirm or refute it. |
| `Inconclusive` | The export lacks the data to decide. | Which data is missing. |
| `False Positive` | The match is wrong or the artefact is demonstrably benign. | The specific reason (pattern, verification). |

"Benign" and "false positive" are not the same. A correctly detected admin tool is a true positive with low risk. Calling it a false positive hides it from the next analyst.

## Suppression proposals

Recurring false positives should be filtered at the source, not re-analysed every scan. THOR supports regex false-positive filters applied to the full event, and the Analysis Cockpit supports baselines ([configuration](https://thor-manual.nextron-systems.com/en/latest/usage/configuration.html), [analysis](https://thor-manual.nextron-systems.com/en/latest/usage/analysis.html)).

- Draft the narrowest filter that removes the false positive (exact path plus rule, not the whole rule).
- State the risk: what a real attack matching the filter would look like.
- Mark the proposal as requiring approval. This plugin never writes THOR configuration.

## Output block

```text
Finding <F-ID / Event-IDs>
FP-Muster geprüft: <Muster oder „kein bekanntes Muster“>
Prävalenz: <n Hosts von m> (Quelle: <Inventar/Fleet-Matrix>) – oder „nicht bewertbar (Einzelhost)“
Autorisierung: <bestätigt durch … / nicht bestätigt / nicht geprüft>
Widersprüche: <…>
Ergebnis: <Outcome> – Begründung: <…>
Filtervorschlag (Entwurf, Freigabe erforderlich): <…>
```
