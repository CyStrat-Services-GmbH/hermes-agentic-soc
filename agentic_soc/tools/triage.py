"""Local triage and scope-gated planning. No outbound APIs."""

from ..security import BoundaryError


def triage(alert: dict, redactor) -> dict:
    if not isinstance(alert, dict) or not isinstance(alert.get("title"), str) or not alert["title"].strip():
        raise BoundaryError("Alert requires a nonempty title and structured context.")
    severity = str(alert.get("severity", "unknown")).lower()
    priority = "P2" if severity in {"critical", "high"} else "P3"
    return redactor.clean({
        "title": alert["title"], "priority": priority, "verdict": "Needs analyst review",
        "provided_evidence": alert.get("evidence", []),
        "enrichment_performed": False, "network_calls": 0,
        "missing": [k for k in ("host", "timestamp", "evidence", "asset_criticality") if not alert.get(k)],
        "actions": ["Validate source alert and time window", "Correlate supplied evidence read-only",
                    "Escalate validated malicious or high-impact activity to L2", "Prepare response draft for human approval"],
        "ticket": {"status": "draft_only", "writes_performed": False},
    })
