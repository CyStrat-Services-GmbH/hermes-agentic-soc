"""Local triage and scope-gated planning. No outbound APIs."""

from ..security import BoundaryError, check_scope


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


def research_plan(scope: dict, target: str, redactor) -> dict:
    validation = check_scope(scope, target)
    return redactor.clean({
        "scope_validation": validation, "target": redactor.token(target, "target"),
        "plan": ["Verify authorization with asset owner", "Define ATT&CK hypothesis and lab signal",
                 "Draft detections and expected telemetry", "Compare supplied lab observations with expected signals",
                 "Document gaps, evidence and rollback requirements"],
        "execution": "not_supported", "network_calls": 0,
    })
