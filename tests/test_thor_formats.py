"""THOR JSON v2 (THOR 10.7 --jsonv2) and v3 (THOR 11) record shapes, v1 refusal, status messages.

Record shapes follow real THOR 10.7.32 and THOR 11.0.0 output, reduced to synthetic values.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agentic_soc.security import BoundaryError, Redactor
from agentic_soc.tools.thor import parse
from agentic_soc.scoring.thor_first_assessment import assess, markdown

R = Redactor(b"0" * 32)
SHA = "a" * 64
META = {"hostname": "LAB-WS01", "scan_id": "S-v3demo"}


def run(tmp_path, records, jsonl=True):
    p = tmp_path / ("input.jsonl" if jsonl else "input.json")
    p.write_text("\n".join(json.dumps(r) for r in records) if jsonl else json.dumps(records))
    return parse(p, R)


def v3(kind, level, module, **body):
    return {"type": kind, "meta": {"time": "2026-11-17T17:58:04+01:00", "level": level, "module": module, **META},
            "log_version": "v3.0.0", **body}


V3_FILE = v3("THOR assessment", "Alert", "Filescan", message="Malicious file found", score=91,
             subject={"type": "file", "path": "/srv/case/loader.bin", "hashes": {"sha256": SHA},
                      "file_times": {"modified": "2026-11-15T22:10:03Z", "created": "2026-11-15T22:10:03Z"}},
             reasons=[{"type": "reason", "summary": "YARA rule DEMO_Loader / synthetic",
                       "signature": {"score": 85, "kind": "YARA Rule", "rule_name": "DEMO_Loader",
                                     "origin": "custom", "description": "synthetic"},
                       "matched": [{"data": {"data": "demo", "encoding": "plain"}, "offset": 4}]}],
             reason_count=1)
LITE_NOTICES = [
    v3("THOR message", "Warning", "Startup", message="THOR should be started with Full Disk Access", fields={}),
    v3("THOR message", "Notice", "Init", message="Some modules and features are not available in Lite version and will be disabled", fields={}),
    v3("THOR message", "Info", "Report", message="Assessments",
       fields={"assessments": {"alerts": 0, "warnings": 0, "notices": 0, "infos": 0}}),
]


def test_v3_assessment_fields(tmp_path):
    data = run(tmp_path, [V3_FILE, V3_FILE])
    inv = data["inventory"]
    assert inv["log_versions"] == {"v3": 2} and inv["finding_count"] == 1  # same host, scan, path and hash
    e = data["events"][0]
    assert (e["level"], e["score"], e["module"], e["record_kind"]) == ("ALERT", 91, "Filescan", "finding")
    assert e["file"] == "/srv/case/loader.bin" and e["hashes"] == {"sha256": SHA}
    assert e["artifact_times"] == {"modified": "2026-11-15T22:10:03Z", "created": "2026-11-15T22:10:03Z"}
    assert e["detection_time"] == "2026-11-17T17:58:04+01:00"
    assert e["reasons"][0] == {"name": "YARA rule DEMO_Loader / synthetic", "score": 85, "rule": "DEMO_Loader",
                               "kind": "YARA Rule", "description": "synthetic"}


def test_v3_process_and_eventlog_identity(tmp_path):
    proc = v3("THOR assessment", "Warning", "ProcessCheck", message="Suspicious process found", score=70,
              subject={"type": "process", "pid": 4242, "name": "demo.exe", "created": "2026-11-17T08:00:00Z",
                       "image": {"type": "file", "path": "C:\\demo\\demo.exe", "hashes": {"md5": "b" * 32}}})
    evt = v3("THOR assessment", "Warning", "Eventlog", message="Suspicious eventlog entry found", score=70,
             subject={"type": "eventlog entry",
                      "entry": {"EventID": "4688", "EventRecordID": "85270", "Channel": "Security",
                                "TimeCreated_SystemTime": "2026-11-16T03:04:02Z"}})
    other_channel = json.loads(json.dumps(evt))
    other_channel["subject"]["entry"]["Channel"] = "System"
    data = run(tmp_path, [proc, proc, evt, evt, other_channel])
    assert data["inventory"]["finding_count"] == 3
    p, e = data["events"][0], data["events"][2]
    assert p["process"] == {"name": "demo.exe", "pid": 4242} and p["file"] == "C:\\demo\\demo.exe"
    assert e["artifact_times"] == {"event_time": "2026-11-16T03:04:02Z"}


def test_v3_status_messages_are_not_findings(tmp_path):
    data = run(tmp_path, LITE_NOTICES)
    assert data["inventory"]["record_kinds"] == {"message": 3}
    assert data["inventory"]["message_levels"] == {"WARNING": 1, "NOTICE": 1, "INFO": 1}
    case = assess(data)
    assert case["rationale"].startswith("R4") and case["verdict"] == "Nicht abschließend beurteilbar"
    report = markdown(case, data)
    assert "Keine Befund-Datensätze" in report and "3 THOR-Statusmeldungen (Start" in report
    assert "THOR triage: 0 correlated observations" in case["ticket_draft"]["title"]


def test_status_messages_do_not_mask_findings_and_errors_stay_visible(tmp_path):
    case = assess(run(tmp_path, LITE_NOTICES + [V3_FILE]))
    assert case["rationale"].startswith("R1")
    error = v3("THOR message", "Error", "Filescan", message="Could not read file", fields={})
    case = assess(run(tmp_path, LITE_NOTICES + [error]))
    assert case["rationale"].startswith("R3")


def test_v2_real_module_shapes(tmp_path):
    base = {"time": "2026-01-27T17:05:53Z", "hostname": "LAB-WS01", "scanid": "S-v2demo", "log_version": "v2.0.0"}
    amcache = {**base, "level": "Warning", "module": "Amcache", "message": "Suspicious Amcache entry found",
               "score": 70, "file": "c:\\programdata\\demo.exe", "sha1": "c" * 40, "first_run": "2025-12-23T17:19:21Z",
               "created": "1970-01-01T00:00:00Z", "file_2": {"exists": "yes", "sha256": SHA},
               "reasons": [{"name": "Filename IOC demo", "score": 70, "signature": {"ref": ""},
                            "sigtype": "internal", "sigclass": "Filename IOC"}]}
    eventlog = {**base, "level": "Warning", "module": "Eventlog", "message": "Sigma match on eventlog entry",
                "score": 70, "event_id": 104, "event_channel": "System", "event_time": "2025-08-14T03:09:24Z",
                "entry": "EventID: 104  Provider_Name: Microsoft-Windows-Eventlog  EventRecordID: 124076  Channel: System",
                "reasons": [{"name": "Important Windows Eventlog Cleared", "score": 70,
                             "signature": {"description": "Detects clearing", "rulename": "Eventlog Cleared"},
                             "sigclass": "Sigma Rule"}]}
    data = run(tmp_path, [amcache, eventlog, eventlog])
    a, e = data["events"][0], data["events"][1]
    assert a["file"] == "c:\\programdata\\demo.exe" and a["hashes"] == {"sha1": "c" * 40, "sha256": SHA}
    assert "created" not in a["artifact_times"]  # the Amcache key time is not a file time
    assert e["artifact_times"] == {"event_time": "2025-08-14T03:09:24Z"}
    assert e["reasons"][0]["kind"] == "Sigma Rule" and e["reasons"][0]["description"] == "Detects clearing"
    assert data["inventory"]["finding_count"] == 2  # identical record ID + event ID + channel merge


def test_v2_status_messages_without_score_are_messages(tmp_path):
    base = {"time": "2026-11-17T16:57:51Z", "hostname": "LAB-WS01", "scanid": "S-v2demo", "log_version": "v2.0.0"}
    data = run(tmp_path, [
        {**base, "level": "Notice", "module": "Init", "message": "Some modules and features are not available in Lite version and will be disabled"},
        {**base, "level": "Notice", "module": "Startup", "message": "THOR should be started as 'root' user to have full access to files"},
        {**base, "level": "Info", "module": "Report", "message": "Results", "alerts": 0, "warnings": 0, "notices": 2, "errors": 0},
    ])
    assert data["inventory"]["record_kinds"] == {"message": 3}
    assert assess(data)["rationale"].startswith("R4")


def test_alert_level_follows_subscore_rule_when_level_missing(tmp_path):
    data = run(tmp_path, [{"module": "Filescan", "score": 90,
                           "reasons": [{"name": "a", "score": 70}, {"name": "b", "score": 60}]}])
    e = data["events"][0]
    assert e["score_band"] == "WARNING" and e["level"] == "WARNING"


@pytest.mark.parametrize("records", [
    [{"log_version": "v1.0.0", "level": "Alert", "module": "Filescan", "score": 91, "reason_1": "YARA rule X", "subscore_1": 85}],
    [{"level": "Alert", "module": "Filescan", "score": 91, "reason_1": "YARA rule X", "subscore_1": 85}],
])
def test_json_v1_refused_with_actionable_hint(tmp_path, records):
    with pytest.raises(BoundaryError, match="--jsonv2"):
        run(tmp_path, records)


@pytest.mark.parametrize("record", [
    {**V3_FILE, "log_version": "v2.0.0"},                               # v3 container labelled v2
    {"type": "THOR assessment", "score": 95, "log_version": "v3.0.0"},  # no meta block
    {"meta": {"level": "Alert", "module": "Filescan"}, "score": 95},    # meta without THOR type
])
def test_inconsistent_v3_records_refused(tmp_path, record):
    with pytest.raises(BoundaryError):
        run(tmp_path, [record])
