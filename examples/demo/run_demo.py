"""Offline, reproducible demonstration. Never executes a real scanner."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agentic_soc.runtime import Runtime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runtime = Runtime(ROOT, lambda: args.output.resolve(), lambda key, default=None: default)
    print("Hermes Agentic SOC | CyStrat Services × Nextron Systems")
    print("OFFLINE SYNTHETIC DEMO. No scanner or target interaction.")
    listing = runtime.call("soc_template_list", {})
    print(f"Profiles: {len(listing['profiles'])}; six defense MVP templates, three research scaffolds.")
    result = runtime.call("thor_first_assessment", {"path": str(ROOT / "examples/demo/thor.json")})
    print(json.dumps({k: v for k, v in result.items() if k != "preview"}, indent=2, ensure_ascii=False))
    if not result.get("ok"):
        return 1
    print("Exact inventory: 4 events, 3 correlated observation groups.")
    print("Evidence-bounded verdict; no automatic containment. Ticket remains draft-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
