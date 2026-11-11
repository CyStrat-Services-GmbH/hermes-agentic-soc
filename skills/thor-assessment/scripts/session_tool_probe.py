#!/usr/bin/env python3
"""Report which tools the CURRENT Hermes session really has.

Why: a plugin can be enabled and pass `hermes plugins doctor` while the running
gateway serves sessions whose system prompt carries none of its tools (the
gateway registers plugins at start-up). Reading the session snapshot answers the
question in one step; guessing from `hermes plugins list` does not.

Usage:
    python3 session_tool_probe.py [profile_dir] [--filter thor]

Exit codes: 0 = probe ran, 1 = prompt not resolvable, 2 = no state.db/sessions.
"""

import json
import pathlib
import sqlite3
import sys


def parse_args(argv):
    filt = None
    positional = []
    i = 0
    while i < len(argv):
        if argv[i] == "--filter" and i + 1 < len(argv):
            filt = argv[i + 1]
            i += 2
            continue
        positional.append(argv[i])
        i += 1
    if positional:
        profile = pathlib.Path(positional[0]).expanduser()
    else:
        profile = _find_profile(pathlib.Path(__file__).resolve().parent)
    return profile, filt


def _find_profile(start):
    """Walk upwards to the directory that owns state.db (the profile root)."""
    for candidate in [start, *start.parents]:
        if (candidate / "state.db").is_file():
            return candidate
    return start


def main(argv):
    profile, filt = parse_args(argv)
    db = profile / "state.db"
    if not db.is_file():
        print("no state.db at %s" % db)
        return 2

    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    row = con.execute(
        "select id, started_at, tool_names from sessions order by started_at desc limit 1"
    ).fetchone()
    if not row:
        print("no sessions recorded in %s" % db)
        return 2

    session_id, started, prompt_hash = row
    print("session: %s (started %s)" % (session_id, started))
    print("profile: %s" % profile)

    names = []
    if prompt_hash:
        lookup = str(prompt_hash).strip()
        found = con.execute(
            "select prompt from system_prompts where hash like ?",
            (lookup[:16] + "%",),
        ).fetchone()
        if found:
            try:
                names = [
                    t["function"]["name"]
                    for t in json.loads(found[0]).get("tools", [])
                    if isinstance(t, dict) and "function" in t
                ]
            except (ValueError, KeyError, TypeError):
                names = []

    if not names:
        print("prompt not resolvable from state.db - compare with the live tool list instead")
        return 1

    print("tools in this session prompt: %d" % len(names))
    if filt:
        hits = [n for n in names if filt.lower() in n.lower()]
        print("matching %r: %s" % (filt, ", ".join(hits) if hits else "NONE"))
        if hits:
            print("VERDICT: present")
        else:
            print(
                "VERDICT: MISSING from this session - compare the gateway process start "
                "time with the plugin install/checkout, then ask the operator to restart it"
            )
    else:
        print("names: %s" % ", ".join(names))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
