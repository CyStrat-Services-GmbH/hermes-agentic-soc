# Case output for THOR assessments (German)

Write the case in German, in exactly this order. No section may be omitted. Paths, hashes, event IDs, rule names and command lines go in code format. Timestamps carry their timezone; use UTC when the source does.

`thor_first_assessment` already produces a deterministic nine-section report plus `Einschränkungen` and `Ticket-Entwurf`. Use it as the tool layer and add the analyst layer below. Do not rewrite the tool's numbers.

## 1. Titel

One technical, specific line:

```text
<Tool, Artefakt oder Aktivität> auf <System oder Systemgruppe> – <wesentliche Auswirkung oder offene Frage>
```

Example: `Hacktool-Treffer und auffälliger Dienst auf LAB-WS02 – Validierung einer möglichen Remote-Ausführung erforderlich`

## 2. Summary

Three to five short paragraphs:

- Affected systems and the evidence scope (export origin, THOR edition, filters).
- Exact event count and analyst finding count, with the reason they differ.
- The most important finding.
- The key impact, confirmed or possible.
- The key limitation of the evidence.

## 3. Assessment

The central analytical block. Never replace it with a data dump. Cover all eight points in compact form:

1. **Event-Scope:** exact count, distribution by level and module.
2. **Kernfinding:** what was concretely observed.
3. **Korrelation:** which events describe the same fact, which are independent, and why.
4. **Artefakte:** files, paths, processes, services, tasks, registry keys, log sources.
5. **Identitäten:** users, SIDs, owners; state what each proves and what it does not.
6. **Klassifizierungsgrund:** why true positive, suspicious, inconclusive or false positive.
7. **Impact:** confirmed or probable consequence.
8. **Grenzen:** what the export cannot establish.

Template (fill, do not copy literally):

```text
Der Export enthält <N> Events: <Verteilung nach Level/Modul>. Das Tool bildet daraus
<N> automatische Beobachtungsgruppen; nach Analystenkorrelation ergeben sich <N> Findings,
weil <Begründung, z. B. Filescan- und SHIMCache-Event beschreiben dieselbe Datei>.

Kernfinding: <Sachverhalt>. Belegt durch <Event-IDs, Regeln, Artefakte>.

Artefakte und Zusammenhänge: <Dateien, Dienste, Prozesse>. <Technischer Zusammenhang
oder ausdrücklich: kein belegter Zusammenhang>.

Identitäten: <Owner/Benutzer>. Belegt ist <…>; nicht belegt ist <…>.

Klassifizierung: <Klasse>, weil <technische Begründung>. False-Positive-Prüfung: <Ergebnis>.
Auswirkungen: <bestätigt / möglich>.

Nicht aus dem Export ableitbar: <Grenzen, inkl. Abdeckungslücken der THOR-Edition>.
```

## 4. Bewertung

State both layers:

```text
Tool-Erstbewertung: <Verdict, Priorität, Kritikalität aus thor_first_assessment>
Analystenbewertung: <eine der Klassen unten> – Begründung der Abweichung: <…>
```

Classes:

- `True Positive – Confirmed Malicious Activity`
- `True Positive – Confirmed Security-Relevant Activity` (e.g. authorised admin or pentest tool)
- `Suspicious – Further Investigation Required`
- `Inconclusive`
- `False Positive`

Then:

```text
Bestätigt:
- …

Starke Indikatoren:
- …

Nicht aus diesem Export ableitbar:
- …
```

## 5. Priorität

One of `P1 – Immediate Response Required`, `P2 – Urgent Investigation Required`, `P3 – Standard Investigation`, `P4 – Informational`. The justification must reference impact, scope, asset criticality and recency. Mark it provisional while validation is open.

## 6. Kritikalität

One of `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`. Independent of priority: an old, already-contained credential theft can be CRITICAL with lower operational priority.

## 7. IOCs und Artefakte

Apply `agentic-soc:thor-ioc-handling`. Only confirmed, relevant artefacts; each with event ID, source field, evidence strength and sharing status. No credential hashes, no passwords, no raw match strings of credential material. Rule names are detection references, listed separately from IOCs.

## 8. Timeline

Apply `agentic-soc:thor-timeline-correlation`. One entry per distinct activity or state change, each with its timestamp type (`Artefaktzeit`, `Quell-Eventzeit`, `THOR-Erkennungszeit`). Detection time is never attack time. If no reliable activity timeline exists, say so in one sentence.

## 9. Maßnahmen

Concrete, prioritised and specific to the findings, not generic IR boilerplate. Each action has a target, an owner role and a statement that it requires approval if it changes a system. Typical order: validate → preserve evidence → scope (fleet, other telemetry) → contain (approval) → eradicate and recover (approval) → detection improvements.

## Appendix

- `Einschränkungen` from the tool, extended by analyst limitations.
- `Ticket-Entwurf`: draft only. No ticket is created by this plugin.
- `Analysegrundlage`: export hash (`source_sha256`), THOR edition/version if known, filters, skills used.
