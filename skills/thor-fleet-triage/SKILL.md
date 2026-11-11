---
name: thor-fleet-triage
description: "Analyse THOR results from many hosts or repeated scans: per-host inventories, prevalence of rules, paths and hashes, rare outliers, scan coverage differences and deltas between scans. Use for compromise assessments across a fleet, campaign scoping and baselining; not for single-host exports (use thor-assessment directly)."
---

# THOR fleet triage

At fleet scale, relevance runs against intuition: what appears everywhere is usually software or configuration, what appears on a few machines is usually what you are looking for. Nextron's experience: the most relevant findings come from 1–5, sometimes up to 30 endpoints; suspicious elements on 100 or more endpoints are most likely false positives unless strong indicators suggest otherwise ([Log Analysis Manual](https://log-analysis-manual.nextron-systems.com/en/latest/)).

## Procedure

### 1. Inventory every part

Parse each host's or scan's export separately with `thor_parse` (limit: 50 MiB or 100,000 events per file). Build a table from the returned inventories, never from reading:

| Part | Host token | Scan token | Events | ALERT | WARNING | NOTICE | INFO | Automatic groups |
|---|---|---|---|---|---|---|---|---|

Host and scan tokens are consistent within the same Hermes profile, so the same host keeps the same token across parts.

### 2. Check coverage before comparing

Hosts are only comparable if they were scanned comparably. From Init, Info and Error events and the scan documentation, record per host: THOR edition and version, scan mode and flags, selected modules, lookback, excludes, start and end, errors and resource-control warnings. A host with no findings and a ten-minute `--quick` scan is not comparable to a host with a full scan.

### 3. Build prevalence

For every rule name, normalised path and typed hash, count the hosts it appears on. This requires aggregation over the normalized outputs:

- With an operator-approved code-execution tool, aggregate programmatically and keep the script with the case.
- Without one, report the per-host inventories and list prevalence only for the few elements you counted from tool output. State explicitly that a complete prevalence matrix was not computed. Never estimate.

### 4. Find the outliers

- Rare: elements on 1–5 hosts with ALERT or WARNING level.
- Unique combinations: a common rule on a host that also has a rare persistence or service finding.
- Odd placement: a common file in an uncommon path on few hosts.
- Coverage outliers: hosts with errors, aborted scans or much shorter duration.

Prevalence lowers relevance; it does not prove benign. A worm or a mass-deployed implant is prevalent too. Check whether a prevalent element has strong malicious indicators before discounting it.

### 5. Compare scans over time

For repeated scans of the same hosts, separate new, persisting and disappeared findings. New findings after a baseline deserve priority; disappeared findings may mean remediation, file deletion by an attacker or reduced coverage. Do not decide which without other evidence.

### 6. Scope the case

Turn the outliers into a host list with a reason per host. Use `agentic-soc:thor-assessment` for each host that needs a full case. Say which hosts were **not** in scope; absence from the export is not absence of compromise.

## Output block

```text
Flottenumfang: <n Hosts, m Scans, Zeitraum>; nicht enthalten: <…>
Vergleichbarkeit: <gleiche Edition/Flags ja/nein; Abweichungen>
Prävalenz-Matrix: <berechnet mit … / nicht berechnet, Grund>

| Element (Regel/Pfad/Hash) | Hosts | Level | Lesart |
|---|---|---|---|
| … | 2 von 140 | ALERT | selten, priorisieren |

Ausreißer-Hosts: <Host-Token: Grund>
Delta zur Vorgängerprüfung: <neu / unverändert / entfallen>
Nächste Schritte: <Einzelfallbewertung für …>
```
