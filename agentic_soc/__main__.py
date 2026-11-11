"""Offline CLI for reproducible previews, never host-approval bypass execution.

No live scanner, profile installation, external connector or production write
command is exposed here. Sensitive execution remains in the Hermes host.
"""

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .runtime import Runtime
from .tools.templates import list_templates


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m agentic_soc")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("profiles", help="List shipped profile templates without modifying state")
    demo = sub.add_parser("demo", help="Assess shipped synthetic evidence; no real scan")
    demo.add_argument("--output", type=Path, required=True)
    assess_parser = sub.add_parser("assess", help="Assess a supplied local JSON export; no scanner execution")
    assess_parser.add_argument("input", type=Path)
    assess_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "profiles":
        print(json.dumps(list_templates(), ensure_ascii=False, indent=2))
        return 0
    root = Path(__file__).resolve().parents[1]
    source = root / "examples/demo/thor.json" if args.command == "demo" else args.input.expanduser().resolve()
    # Explicit CLI input authorizes this file's parent for this offline invocation only.
    output = args.output.expanduser().resolve()
    runtime = Runtime(root, lambda: output,
                      lambda key, default=None: [str(source.parent)] if key == "evidence_roots" else default)
    result = runtime.call("thor_first_assessment", {"path": str(source)})
    result["execution_mode"] = "synthetic_demo_no_scan" if args.command == "demo" else "offline_import_no_scan"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
