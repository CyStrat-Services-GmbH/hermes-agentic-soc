---
name: thor-lite
description: "Operate separately installed THOR Lite through agentic-soc tools. Use for scan preparation, CLI verification and local scan requests, not incident verdicts."
---

# Thor Lite

1. Call soc_template_list to choose the DFIR role if needed.
2. Obtain THOR Lite separately from Nextron; never fetch binaries or rules into this repository.
3. Ask the operator to configure thor_path and scan_roots; do not alter these to widen a requested scan.
4. Call thor_lite_scan with execute=false and the absolute directory. Check verified flags.
5. Request execute=true only for the reviewed target; let Hermes ask the human. A model-written boolean is not approval.
6. Parse the returned output only after successful completion. A timeout or missing output is incomplete evidence.

Download and licensing: https://www.nextron-systems.com/thor-lite/
CLI: https://thor-manual.nextron-systems.com/en/latest/usage/flags.html
Do not promise Sigma or third-party paid-engagement rights in Lite. Verify licensing with Nextron.
