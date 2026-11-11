#!/usr/bin/env python3
"""THOR JSON v2 field-shape inventory.

Prints, per module, the keys that actually occur and the Python types behind
them, so a parser is written against the real export instead of an assumed
schema. JSON v2 is not schema-uniform: `file` is an object in Filescan but a
plain string in Timestomp/WER/LogScan/ETL/Amcache and absent elsewhere, and
`reasons` is a list of objects in most modules but a list of strings (or
missing) in others.

Usage:
    python3 thor_field_shapes.py <export.json>
    python3 thor_field_shapes.py <export.json> --module ProcessIntegrity
    python3 thor_field_shapes.py <export.json> --keys file,reasons

Malformed lines are counted and reported, never silently dropped.
"""
import argparse
import collections
import json
import sys


def kind(value):
    if isinstance(value, dict):
        return "dict"
    if isinstance(value, list):
        inner = sorted({type(x).__name__ for x in value})
        return "list[" + ",".join(inner) + "]" if inner else "list[]"
    return type(value).__name__


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("export")
    ap.add_argument("--module", help="restrict output to one module")
    ap.add_argument("--keys", help="comma-separated keys whose list items to break down, e.g. file,reasons")
    args = ap.parse_args()

    wanted = {k.strip() for k in args.keys.split(",")} if args.keys else set()
    shapes = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    counts = collections.Counter()
    bad = 0

    try:
        fh = open(args.export, encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"cannot read {args.export}: {exc}", file=sys.stderr)
        return 2

    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            if not isinstance(row, dict):
                bad += 1
                continue
            mod = row.get("module") or "<none>"
            counts[mod] += 1
            for key, value in row.items():
                shapes[mod][key][kind(value)] += 1
                if key in wanted and isinstance(value, list):
                    for item_kind in sorted({kind(x) for x in value}) or ["<empty>"]:
                        shapes[mod][key + "[item]"][item_kind] += 1

    order = [args.module] if args.module else sorted(counts, key=lambda m: (-counts[m], m))
    for mod in order:
        if mod not in shapes:
            continue
        print(f"\n## {mod}  ({counts[mod]} events)")
        for key in sorted(shapes[mod]):
            rendered = ", ".join(f"{t}x{n}" for t, n in sorted(shapes[mod][key].items()))
            print(f"  {key:<26} {rendered}")

    print(f"\nevents={sum(counts.values())} modules={len(counts)} bad_lines={bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
