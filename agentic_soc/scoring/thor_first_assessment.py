"""Conservative, explainable triage, not a probability of compromise."""

from __future__ import annotations

from collections import defaultdict


def assess(parsed: dict) -> dict:
    inv = parsed["inventory"]
    groups = defaultdict(list)
    for event in parsed["events"]:
        groups[event["finding_id"]].append(event)
    findings = []
    for finding_id, events in groups.items():
        scores = [e["score"] for e in events if e["score"] is not None]
        levels = {e["level"] for e in events}
        severity = next((x for x in ("ALERT", "WARNING", "NOTICE", "ERROR", "UNKNOWN", "INFO", "DEBUG") if x in levels), "UNKNOWN")
        findings.append({"finding_id": finding_id, "event_ids": [e["event_id"] for e in events],
                         "host": events[0]["host"], "module": events[0]["module"],
                         "score": max(scores) if scores else None, "level": severity,
                         "evidence_strength": "Strong Indicator" if severity in {"ALERT", "WARNING"} else "Confirmed",
                         "rationale": "Scanner severity drives triage; it does not establish malware execution or a compromised host."})
    levels = {f["level"] for f in findings}
    if "ALERT" in levels:
        priority, criticality = "P2", "HIGH"
        classification, verdict = "Suspicious – Further Investigation Required", "Verdächtig"
        rule = "R1: at least one exported ALERT; urgent analyst validation, not automatic confirmed compromise."
    elif levels & {"WARNING", "NOTICE"}:
        priority, criticality = "P3", "MEDIUM"
        classification, verdict = "Suspicious – Further Investigation Required", "Verdächtig"
        rule = "R2: WARNING/NOTICE without ALERT; validate artifacts and false-positive context."
    else:
        priority, criticality = "P3", "LOW"
        classification, verdict = "Inconclusive", "Nicht abschließend beurteilbar"
        rule = "R3: no suspicious finding in supplied export; scan coverage and completeness unverified."
    result = {
        "schema_version": "1.0", "policy_version": "0.1.0",
        "inventory": inv, "findings": findings, "verdict": verdict,
        "classification": classification, "priority": priority, "criticality": criticality,
        "confidence": {"label": "limited", "meaning": "Evidence coverage, not a numerical compromise probability."},
        "rationale": rule,
        "context_missing": ["asset criticality", "containment status", "source completeness", "validated incident recency"],
        "limitations": parsed["limitations"] + [
            "Initial access, attacker identity, execution, lateral movement and successful remediation are not established.",
            "Priority is provisional: impact, asset criticality, scope and recency require analyst validation.",
            "THOR score thresholds may be operator-customized; exported level takes precedence over default score bands.",
        ],
        "recommended_actions": [
            "Validate the highest-severity artifact and triggering rule in the original restricted evidence.",
            "Preserve original evidence and verify its SHA-256 against the import record.",
            "Determine asset criticality, scan scope, event recency and whether containment already occurred.",
            "For validated active compromise, request explicit incident-response approval before isolation or blocking.",
            "Where Lite coverage is insufficient, evaluate appropriately licensed THOR Enterprise or Thunderstorm with Nextron.",
        ],
        "ticket_draft": {"status": "draft_only", "writes_performed": False, "requires_human_approval": True,
                         "title": f"THOR triage: {len(findings)} correlated observations; {priority} provisional"},
    }
    return result


def markdown(case: dict, parsed: dict) -> str:
    i = case["inventory"]
    events = parsed["events"]
    lines = [
        "# Titel", "THOR-Erstbewertung des bereitgestellten Exports",
        "", "## Summary",
        f"Der Export enthält exakt {i['event_count']} Events und {i['finding_count']} korrelierte Beobachtungsgruppen.",
        f"Scanner-Level: {i['levels']}. Module: {i['modules']}.",
        f"Vorläufiges Verdict: {case['verdict']}. Vollständige Scanabdeckung ist nicht nachgewiesen.",
        "", "## Assessment",
        f"Event-Scope: {i['event_count']} Events auf {len(i['hosts'])} pseudonymisierten Host-Identitäten.",
        "Kernfinding: Scanner-Beobachtungen im Export, keine unabhängig bestätigte Kompromittierung.",
        "Korrelation: gleicher Host, Scan und Artefaktkontext werden gruppiert; Gruppen ohne belastbaren Schlüssel bleiben getrennt.",
        "Artefakte: Datei-/Prozess-Kontext und Regelgründe stehen in den normalisierten Events; Rohdaten verbleiben separat.",
        "Identitäten: Hostnamen sind pseudonymisiert. Dateibesitzer und ausführende Benutzer werden nicht gleichgesetzt.",
        f"Klassifizierungsgrund: {case['rationale']}",
        "Impact: möglicher Sicherheitsvorfall; tatsächliche Auswirkungen bedürfen einer Analystenvalidierung.",
        "Grenzen: Initial Access, Ausführung, Attribution, vollständiger Systemzustand und erfolgreiche Bereinigung sind nicht ableitbar.",
        "", "## Bewertung", case["classification"],
        "Bestätigt: Der Export enthält die gezählten Scanner-Beobachtungen.",
        "Starker Indikator: ALERT/WARNING rechtfertigen Untersuchung, nicht automatisch einen True Positive.",
        "Nicht ableitbar: Ausführung, Angreiferidentität, initialer Zugang und tatsächliche Folgeschäden.",
        "", "## Priorität", f"{case['priority']} (vorläufig).",
        "Begründung: Scanner-Level bestimmt die Triage; Impact, Systemkritikalität, Umfang und Aktualität sind noch zu validieren.",
        "", "## Kritikalität", f"{case['criticality']} (vorläufig, unabhängig von der operativen Priorität).",
        "", "## IOCs und Artefakte",
    ]
    for event in events[:100]:
        path = str(event["file"]).replace("`", "'").replace("\n", " ")
        lines.append(f"- {event['event_id']} / {event['finding_id']}: {event['level']}, {event['module']}, `{path or 'kein Dateipfad'}`; Beweiskraft: Scanner-Beobachtung bestätigt.")
        for key, value in event["hashes"].items():
            lines.append(f"  - Artefakt-{key}: `{value}`; kein Nachweis bösartiger Ausführung.")
    if len(events) > 100:
        lines.append(f"- Anzeige auf 100 Events begrenzt; alle {len(events)} Events stehen in normalized.json.")
    lines.extend(["", "## Timeline",
                  "Erkennungszeitpunkte sind keine Angriffszeitpunkte; Artefaktzeiten werden separat bezeichnet."])
    timeline = sorted({(str(value), key, e["finding_id"]) for e in events
                       for key, value in e["artifact_times"].items()})
    for value, key, finding in timeline[:100]:
        lines.append(f"- {value}: Artefakt-Metadatum {key}, {finding}; keine Ausführung daraus abgeleitet.")
    if not timeline:
        lines.append("Keine belastbare Aktivitäts-Timeline aus dem Export ableitbar.")
    lines.extend(["", "## Maßnahmen"] + [f"- {x}" for x in case["recommended_actions"]])
    lines.extend(["", "## Einschränkungen"] + [f"- {x}" for x in case["limitations"]])
    lines.extend(["", "## Ticket-Entwurf", case["ticket_draft"]["title"],
                  "Nur Entwurf. Kein Ticket angelegt, kein System isoliert, keine Blockierung vorgenommen."])
    return "\n".join(lines) + "\n"
