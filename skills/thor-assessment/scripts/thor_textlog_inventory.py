#!/usr/bin/env python3
"""Inventory a THOR plain-text report (`--text`) without loading it into context.

A `--text` run writes `<host>_thor_<date>_<time>.txt`, logs
`No json report file will be written`, and has no `normalized.json`. The file is
not JSONL, so `thor_parse`, `thor_jsonl_inventory.py` and `thor_field_shapes.py`
do not apply. This script derives the inventory from the text report itself:

event count, level and module distribution, per-module `scanned_elements`, the
Eventlog channel coverage including the channels that returned 0, the
Eventlog/EVTX duplicate count, the reason / no-reason partition, the score
distribution, and the scan configuration lines.

Line shape:

    Aug 18 13:27:13 <host>/<ip> THOR: <Level>: MODULE: <Module> MESSAGE: <text> KEY: value ...

The key/value tail is split on UPPERCASE keys only. Values are command lines,
paths and full `ENTRY` dumps, so splitting on ':' would shred them, and
CamelCase sub-fields inside `ENTRY` (SubjectUserName:, CommandLine:) must stay
part of the value.

Usage:
    python thor_textlog_inventory.py <report.txt> [--json out.json] [--csv findings.csv]

The script counts; it does not decide findings. Assigning events to analyst
findings stays with the analyst and must use structured fields — never a
substring of the whole line, because rule *descriptions* carry the same
keywords as the artefacts they describe.
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter

FRAME = re.compile(
    r"^(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(?P<src>\S+)\s+"
    r"THOR:\s+(?P<level>\w+):\s+MODULE:\s+(?P<module>.*?)\s+MESSAGE:\s+(?P<msg>.*)$",
    re.S,
)
KEY = re.compile(r"(?:^|\s)([A-Z][A-Z0-9_]{1,30}):\s")
FINDING_LEVELS = ("Alert", "Warning", "Notice")


def parse_line(line):
    m = FRAME.match(line)
    if not m:
        return None
    ev = m.groupdict()
    msg = ev["msg"]
    hits = [(h.start(1), h.end(), h.group(1)) for h in KEY.finditer(msg)]
    fields = {}
    if hits:
        fields["_text"] = msg[: hits[0][0]].strip()
        for i, (start, end, key) in enumerate(hits):
            nxt = hits[i + 1][0] if i + 1 < len(hits) else len(msg)
            value = msg[end:nxt].rstrip()
            name, n = key, 2
            while name in fields:
                name, n = "%s_%d" % (key, n), n + 1
            fields[name] = value
    else:
        fields["_text"] = msg.strip()
    ev["fields"] = fields
    return ev


def rule_names(ev):
    """Rule identity: internal/YARA `RULENAME_n`, else the Sigma title, else `RULE`.

    Sigma matches do not populate `RULENAME_n` — their title sits in
    `DESCRIPTION_1` and their id in `ID_1`. Without that fallback every Sigma
    hit is booked as "reason-less" and the with/without partition is wrong.
    """
    f = ev["fields"]
    raw = f.get("REASONS_COUNT", "1")
    count = int(raw) if str(raw).strip().isdigit() else 1
    names = []
    for i in range(1, count + 1):
        r = f.get("RULENAME_%d" % i)
        if r:
            names.append(r.strip().strip('"'))
    if not names:
        for key in ("DESCRIPTION_1", "RULE"):
            v = f.get(key)
            if v:
                names.append(v.strip().strip('"')[:200])
                break
    return names


def dedupe_key(ev):
    """Identity of one Windows event as recorded by both Eventlog and EVTX."""
    f = ev["fields"]
    return (
        f.get("EVENT_ID"),
        f.get("EVENT_TIME"),
        f.get("EVENT_CHANNEL"),
        tuple(rule_names(ev)),
        f.get("SCORE"),
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("report", help="THOR text report (*_thor_<date>_<time>.txt)")
    ap.add_argument("--json", dest="json_out", help="write the inventory as JSON")
    ap.add_argument("--csv", dest="csv_out", help="write finding events as CSV")
    args = ap.parse_args(argv)

    events, bad = [], []
    with open(args.report, "r", encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip():
                continue
            ev = parse_line(line)
            if ev is None:
                bad.append(lineno)
                continue
            ev["line"] = lineno
            events.append(ev)

    levels = Counter(ev["level"] for ev in events)
    modules = Counter(ev["module"] for ev in events)
    findings = [ev for ev in events if ev["level"] in FINDING_LEVELS]

    # Eventlog and EVTX read the same .evtx files: drop the EVTX twin.
    eventlog_keys = {dedupe_key(ev) for ev in findings if ev["module"] == "Eventlog"}
    kept, twins = [], 0
    for ev in findings:
        if ev["module"] == "EVTX" and dedupe_key(ev) in eventlog_keys:
            twins += 1
            continue
        kept.append(ev)

    with_reason = sum(1 for ev in kept if rule_names(ev))
    reasonless = Counter(
        (ev["module"], ev["fields"].get("_text", "")[:48])
        for ev in kept
        if not rule_names(ev)
    )

    scores = Counter(ev["fields"].get("SCORE", "-") for ev in findings)
    score_ints = sorted({int(s) for s in scores if s.isdigit()})

    scanned = {}
    channels, zero_channels = [], 0
    config = {}
    for ev in events:
        f, text = ev["fields"], ev["fields"].get("_text", "")
        if text == "Finished module" and f.get("SCANNED_ELEMENTS"):
            scanned[ev["module"]] = int(f["SCANNED_ELEMENTS"])
        if text.startswith("Finished scanning Eventlog"):
            ch = text.split("Finished scanning Eventlog", 1)[1].strip()
            n = int(f.get("SCANNED") or 0)
            channels.append((ch, n))
            zero_channels += 1 if n == 0 else 0
        for label, key in (
            ("thor_version", "Thor Version"),
            ("effective_arguments", "Effective argument list"),
            ("max_file_size", "Max. file size to be scanned"),
            ("selected_modules", "Selected modules"),
            ("deselected_modules", "Deselected modules"),
            ("signature_database", "Signature Database"),
            ("sigma_database", "Sigma Database"),
        ):
            if key in text and label not in config:
                config[label] = text.split(key, 1)[1].strip(" :")[:400]
        if text.startswith("Scan took") and "scan_duration" not in config:
            config["scan_duration"] = text

    with open(args.report, "r", encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    config["lookback_present"] = bool(
        re.search(r"Skipping elements that are unchanged", raw, re.I)
    )
    config["json_output"] = "No json report file will be written" not in raw
    config["sigma_suppression_notices"] = len(
        re.findall(r"triggered more than 10 times", raw, re.I)
    )
    config["connection_output_truncated"] = "output threshold reached" in raw.lower()

    inventory = {
        "report": args.report,
        "lines_parsed": len(events),
        "bad_lines": len(bad),
        "levels": dict(levels),
        "finding_events": len(findings),
        "distinct_observations": len(kept),
        "eventlog_evtx_twins_dropped": twins,
        "with_rule_reason": with_reason,
        "without_rule_reason": len(kept) - with_reason,
        "reasonless_breakdown": [
            {"module": k[0], "message": k[1], "count": v}
            for k, v in reasonless.most_common()
        ],
        "modules": dict(modules.most_common()),
        "scanned_elements": scanned,
        "eventlog_channels_total": len(channels),
        "eventlog_channels_empty": zero_channels,
        "eventlog_channels_events_sum": sum(n for _, n in channels),
        "eventlog_channels_top": sorted(channels, key=lambda c: -c[1])[:15],
        "scores": dict(scores.most_common()),
        "score_min": score_ints[0] if score_ints else None,
        "score_max": score_ints[-1] if score_ints else None,
        "config": config,
    }

    print("report                : %s" % args.report)
    print("lines parsed / bad    : %d / %d" % (len(events), len(bad)))
    print("levels                : %s" % dict(levels))
    print("finding events        : %d" % len(findings))
    print("distinct observations : %d  (Eventlog/EVTX twins dropped: %d)"
          % (len(kept), twins))
    print("with/without reason   : %d / %d" % (with_reason, len(kept) - with_reason))
    print("score range           : %s - %s" % (inventory["score_min"], inventory["score_max"]))
    print("eventlog channels     : %d total, %d empty" % (len(channels), zero_channels))
    print("lookback / truncation : %s / %s"
          % (config["lookback_present"], config["connection_output_truncated"]))
    print("\ntop modules (events):")
    for mod, n in modules.most_common(15):
        print("  %-22s %6d  scanned_elements=%s" % (mod, n, scanned.get(mod, "-")))
    print("\nreason-less observations:")
    for (mod, msg), n in reasonless.most_common(12):
        print("  %-20s %5d  %s" % (mod, n, msg))
    if bad:
        print("\nBAD LINES (frame did not match): %s%s"
              % (bad[:10], " ..." if len(bad) > 10 else ""))

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(inventory, fh, indent=2, ensure_ascii=False)
    if args.csv_out:
        cols = ["line", "ts_utc", "level", "module", "score", "event_id",
                "event_channel", "event_time", "rules", "path", "owner",
                "pid", "command", "sha256", "text"]
        with open(args.csv_out, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for ev in kept:
                f = ev["fields"]
                path = (f.get("FILE") or f.get("FILE_1") or f.get("IMAGE_FILE")
                        or f.get("KEY") or f.get("PATH") or f.get("NAME") or "")
                w.writerow([
                    ev["line"], ev["ts"], ev["level"], ev["module"],
                    f.get("SCORE", ""), f.get("EVENT_ID", ""),
                    f.get("EVENT_CHANNEL", ""), f.get("EVENT_TIME", ""),
                    " | ".join(rule_names(ev)), path[:240],
                    f.get("OWNER") or f.get("USER", ""), f.get("PID", ""),
                    (f.get("COMMAND") or "")[:300].replace("\n", " "),
                    f.get("SHA256") or f.get("SHA256_1") or f.get("IMAGE_SHA256", ""),
                    f.get("_text", "")[:200],
                ])
    return 0


if __name__ == "__main__":
    sys.exit(main())
