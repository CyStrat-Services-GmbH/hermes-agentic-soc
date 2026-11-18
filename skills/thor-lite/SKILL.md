---
name: thor-lite
description: "Prepare and request a local THOR Lite Filescan through the agentic-soc tools: verify the separately installed executable, keep the scan inside operator-approved roots, request execution through Hermes's human approval and hand complete output to analysis. Use for scan preparation and execution requests; not for interpreting results (use thor-assessment) or for remote, process or full-system scans."
---

# THOR Lite scans

The plugin can launch a separately installed THOR Lite 10.7 or 11 for one bounded job: a `Filescan` of an operator-approved directory, with JSON output (v2 on 10.7, v3 on 11) and privacy flags. `thor_parse` reads both. The plugin never downloads THOR, its signatures or licences.

## Know what Lite covers

THOR Lite runs a reduced module set. Which modules depends on the version ([THOR Lite](https://www.nextron-systems.com/thor-lite/), [Lite feature matrix](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-lite/references/limitations.md)):

- **THOR Lite 10.7:** Filescan, Autoruns and ProcessCheck. Eventlog and Sigma run only if the licence carries the `allowsigma` special.
- **THOR Lite 11:** Filescan, Autoruns, ProcessCheck and the Windows Eventlog module, with the Sigma engine and EVTX parsing.
- **Neither edition** has RegistryChecks, SHIM cache, Amcache, services, scheduled tasks, WMI or user modules.

Lite uses Nextron's open-source signature set, plus YARA Forge and the operator's own signatures if installed. It has no private Nextron rule or IOC sets. The plugin's launcher further restricts Lite to `--module Filescan` on one directory.

Consequences for the case:

- A clean Lite Filescan of one directory says nothing about other paths, processes, persistence, logs or memory.
- Paid engagements and customer or third-party networks need a commercial THOR licence. Lite's startup notice says it permits non-commercial use only ([THOR Lite skill](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-lite/SKILL.md)). Confirm the licence with Nextron before scanning customer systems.

## Procedure

1. **Scope.** Confirm the case, the asset owner's authorisation and the exact directory. Choose the DFIR profile (`dfir-compromise-assessment`) if needed via `soc_template_list`.
2. **Installation.** The operator obtains THOR Lite from [Nextron](https://www.nextron-systems.com/thor-lite/) (registration, licence file and signature update are described in the operator guide, section "Obtain THOR Lite") and sets `thor_path` and `scan_roots` in the profile's plugin settings. Never change these settings yourself to make a request fit.
3. **Preflight.** Call `thor_lite_scan` with `execute:false` and the absolute directory. The tool reads the version with `--version`, checks the full CLI help (`--fullhelp` on 10.7, `--help long` on 11) for the exact flags it will use, and returns a dry run that names the THOR version and the JSON schema it will write (v2 or v3). THOR 10.7 must list `--module`, `--path`, `--jsonfile`, `--jsonv2`, `--rebase-dir`, `--suppresspi`, `--nolog`, `--nocsv` and `--nothordb`; THOR 11 must list `--module`, `--path`, `--json`, `--output-directory`, `--no-personal-data`, `--no-html`, `--no-csv` and `--no-thordb` ([flag map](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor/references/flag-map-v10-v11.md)). Other versions, and help without these flags, are refused. Report a refusal to the operator; do not work around it.
4. **Execution request.** Request `execute:true` only for the reviewed directory through a normal tool call. Hermes asks the human; a model-written `execute:true` is a request, not approval. The `/thor-scan` slash command is preview-only.
5. **Completion check.** A timeout, a non-zero exit code, a missing `thor.json` (10.7) or `thor.jsonl` (11), or a missing end-of-scan `Report` record (THOR 10 message `Results`, THOR 11 messages `Assessments` and `Messages`) is an incomplete scan. Exit code 0 alone does not prove that the directory was walked. THOR exits 0 whatever it found, and it skips network mounts without all-drives scanning; THOR 10 on macOS also skips `/Volumes`, and THOR 11 on Linux treats FUSE mounts as network ([exit codes](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor/references/versions-and-outputs.md), [file system classes](https://github.com/Nextron-Labs/thor-skill/blob/master/skills/thor-scan/references/selection-and-excludes.md)). Incomplete output cannot establish a clean result.
6. **Hand-over.** Pass the returned output path to `thor_parse` and continue with `agentic-soc:thor-assessment`. Record THOR version, flags, start and end in the case.

If `thor_lite_scan` is missing from the session's tool list although the plugin is enabled, the gateway was started before the plugin was installed — see `agentic-soc:thor-assessment` step 2 for the session probe and the operator restart. Until the tool is back, no local scan can be requested: do not hand-build a THOR command line as a substitute for the approved launcher, because that bypasses the root restriction and the human approval the launcher exists for.

## Limits of the launcher

- Fixed argument list, no custom flags, no remote scans, no process or memory scans, no `--action_command`.
- THOR Lite 10.7 writes JSON v2 only with `--jsonv2`; without it the JSON is v1, which `thor_parse` refuses. THOR Lite 11 always writes JSONL v3.
- The configured executable is trusted operator software. The plugin does not sandbox it or verify its publisher signature.
- `--suppresspi` (10.7) or `--no-personal-data` (11) reduces personal data in THOR's output; it does not make raw scan data safe to share.

## Nextron's companion skills

If the operator installed Nextron's thor-skill (operator guide, section "Companion skills"), load these by name when they help:

- Nextron's `thor-lite` for product facts: editions, licence terms, setup and Lite limits.
- `thor-maintenance` for `thor-lite-util update` and YARA Forge.
- `thor-troubleshooting` when a scan is incomplete, slow or refused for licence reasons.
- `thor-scan` to explain what a Filescan in default mode covers and what other scan modes would add.

`thor-scan` builds command lines for a human operator. Inside a SOC profile, a scan still runs only through `thor_lite_scan` and its human approval.

Reference: [THOR command-line flags](https://thor-manual.nextron-systems.com/en/latest/usage/flags.html).
