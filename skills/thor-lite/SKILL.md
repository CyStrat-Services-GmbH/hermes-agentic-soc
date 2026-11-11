---
name: thor-lite
description: "Prepare and request a local THOR Lite FileScan through the agentic-soc tools: verify the separately installed executable, keep the scan inside operator-approved roots, request execution through Hermes's human approval and hand complete output to analysis. Use for scan preparation and execution requests; not for interpreting results (use thor-assessment) or for remote, process or full-system scans."
---

# THOR Lite scans

The plugin can launch a separately installed THOR Lite for one bounded job: a `FileScan` of an operator-approved directory, with JSON v2 output and privacy flags. It never downloads THOR, its signatures or licences.

## Know what Lite covers

THOR Lite has five modules, centred on the file system scan, process scan and autoruns checks, and uses Nextron's open-source signature base. It has no Registry, Eventlog, SHIMCache or Sigma scanning and no private Nextron rule or IOC sets ([THOR Lite](https://www.nextron-systems.com/thor-lite/)). The plugin's launcher further restricts Lite to `--module FileScan` on one directory.

Consequences for the case:

- A clean Lite FileScan of one directory says nothing about other paths, processes, persistence, logs or memory.
- Use on third-party networks and paid engagements requires THOR Enterprise. Confirm the licence with Nextron before scanning customer systems.

## Procedure

1. **Scope.** Confirm the case, the asset owner's authorisation and the exact directory. Choose the DFIR profile (`dfir-compromise-assessment`) if needed via `soc_template_list`.
2. **Installation.** The operator obtains THOR Lite from [Nextron](https://www.nextron-systems.com/thor-lite/) and sets `thor_path` and `scan_roots` in the profile's plugin settings. Never change these settings yourself to make a request fit.
3. **Preflight.** Call `thor_lite_scan` with `execute:false` and the absolute directory. The tool checks the CLI help for the exact required flags (`--module`, `--path`, `--jsonfile`, `--jsonv2`, `--rebase-dir`, `--suppresspi`, `--nolog`, `--nocsv`) and returns a dry run.
4. **Execution request.** Request `execute:true` only for the reviewed directory through a normal tool call. Hermes asks the human; a model-written `execute:true` is a request, not approval. The `/thor-scan` slash command is preview-only.
5. **Completion check.** A timeout, a non-zero exit code or missing `thor.json` is an incomplete scan. Incomplete output cannot establish a clean result.
6. **Hand-over.** Pass the returned output path to `thor_parse` and continue with `agentic-soc:thor-assessment`. Record THOR version, flags, start and end in the case.

## Limits of the launcher

- Fixed argument list, no custom flags, no remote scans, no process or memory scans, no `--action_command`.
- The configured executable is trusted operator software. The plugin does not sandbox it or verify its publisher signature.
- `--suppresspi` reduces personal data in THOR's output; it does not make raw scan data safe to share.

Reference: [THOR command-line flags](https://thor-manual.nextron-systems.com/en/latest/usage/flags.html).
