#!/usr/bin/env python3
"""Deterministic inventory for THOR JSON v2 exports (--jsonv2 = JSON Lines).

One JSON object per line, so the export is parsed streaming and never needs to
fit in memory or in the model context. Use this when the plugin MCP tools
(thor_parse / thor_first_assessment) are not callable in the session, and say so
in the case's Analysegrundlage.

Usage:
  python3 thor_jsonl_inventory.py EXPORT.json
  python3 thor_jsonl_inventory.py EXPORT.json --json > inventory.json
  python3 thor_jsonl_inventory.py EXPORT.json --clusters
  python3 thor_jsonl_inventory.py EXPORT.json --grep vssadmin wbadmin bcdedit wevtutil
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys

PATH_KEYS = ("path", "filepath", "image_path", "image", "key")


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: str):
    """Return (events, bad_line_count). Malformed lines are counted, never dropped silently."""
    events, bad_lines = [], 0
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                bad_lines += 1
    return events, bad_lines


def event_path(event: dict) -> str:
    """Best-effort path for an event. `file` is a dict on Filescan, a string on WER/LogScan."""
    for key in ("file", "file_2"):
        value = event.get(key)
        if isinstance(value, dict) and value.get("path"):
            return str(value["path"])
        if isinstance(value, str):
            return value
    for key in PATH_KEYS:
        if event.get(key):
            return str(event[key])
    return ""


def rule_name(reason) -> str:
    """Rule name without the description tail; tolerates dict-valued `name`."""
    if not isinstance(reason, dict):
        return str(reason)[:80]
    name = reason.get("name")
    if isinstance(name, dict):
        name = name.get("name") or json.dumps(name, ensure_ascii=False)
    return str(name or "?").split(" / ")[0]


def score_band(score):
    if not isinstance(score, (int, float)):
        return "unscored"
    if score >= 81:
        return "81-100"
    if score >= 61:
        return "61-80"
    if score >= 40:
        return "40-60"
    return "<40"


def inventory(path: str, events: list, bad_lines: int) -> dict:
    findings = [e for e in events if e.get("level") != "Info"]
    files, hashes = set(), set()
    for event in findings:
        candidate = event_path(event)
        if candidate:
            files.add(candidate.lower())
        file_info = event.get("file")
        if isinstance(file_info, dict) and file_info.get("sha256"):
            hashes.add(file_info["sha256"])

    sigclass = collections.Counter()
    for event in findings:
        for reason in event.get("reasons") or []:
            label = reason.get("sigclass") if isinstance(reason, dict) else None
            sigclass[label or "module message"] += 1

    return {
        "export": path,
        "export_sha256": sha256_file(path),
        "events": len(events),
        "bad_lines": bad_lines,
        "levels": dict(collections.Counter(e.get("level") for e in events)),
        "modules": dict(collections.Counter(e.get("module") for e in events).most_common()),
        "hosts": sorted({str(e.get("hostname")) for e in events if e.get("hostname")}),
        "scans": sorted({str(e.get("scanid")) for e in events if e.get("scanid")}),
        "finding_events": len(findings),
        "findings_by_module": dict(
            collections.Counter(e.get("module") for e in findings).most_common()
        ),
        "score_bands": dict(collections.Counter(score_band(e.get("score")) for e in findings)),
        "signature_classes": dict(sigclass.most_common()),
        "unique_files_in_findings": len(files),
        "unique_sha256_in_findings": len(hashes),
        "unscored_events": sum(
            1 for e in events if not isinstance(e.get("score"), (int, float))
        ),
        "note": "duplicate_observation_count requires thor_parse; not derivable here",
    }


def clusters(findings: list, depth: int = 4) -> list:
    """Group findings by (rule, path prefix) to expose false-positive clusters fast."""
    groups = collections.defaultdict(lambda: {"n": 0, "max_score": 0, "levels": set()})
    for event in findings:
        parts = event_path(event).replace("/", "\\").strip("\\").split("\\")[:depth]
        prefix = "\\".join(parts).lower()
        for reason in event.get("reasons") or [{}]:
            group = groups[(rule_name(reason), prefix)]
            group["n"] += 1
            group["levels"].add(event.get("level"))
            if isinstance(event.get("score"), (int, float)):
                group["max_score"] = max(group["max_score"], event["score"])
    return sorted(
        (
            {
                "rule": key[0],
                "path_prefix": key[1],
                "events": value["n"],
                "max_score": value["max_score"],
                "levels": sorted(value["levels"]),
            }
            for key, value in groups.items()
        ),
        key=lambda row: -row["events"],
    )


def grep_counts(events: list, terms: list) -> dict:
    """Case-insensitive term hunt over the whole event. Use for impact checklists."""
    counted = collections.Counter()
    lowered = [json.dumps(e, ensure_ascii=False).lower() for e in events]
    for term in terms:
        needle = term.lower()
        counted[term] = sum(1 for blob in lowered if needle in blob)
    return counted


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="THOR JSON v2 inventory")
    parser.add_argument("export")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--clusters", action="store_true", help="group by rule + path prefix")
    parser.add_argument("--grep", nargs="+", metavar="TERM", help="case-insensitive term hunt")
    parser.add_argument("--depth", type=int, default=4, help="path components per cluster key")
    args = parser.parse_args(argv)

    events, bad_lines = load(args.export)

    if args.grep:
        print(json.dumps(grep_counts(events, args.grep), indent=2, ensure_ascii=False))
        return 0

    findings = [event for event in events if event.get("level") != "Info"]

    if args.clusters:
        rows = clusters(findings, args.depth)
        if args.json:
            print(json.dumps(rows, indent=2, ensure_ascii=False))
        else:
            for row in rows:
                print(
                    f"{row['events']:>5}  sc{row['max_score']:>3}  "
                    f"{','.join(row['levels']):<14} {row['rule'][:58]:<58} {row['path_prefix']}"
                )
        return 0

    report = inventory(args.export, events, bad_lines)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for key, value in report.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
