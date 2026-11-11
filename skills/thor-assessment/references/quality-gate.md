# Quality gate for THOR cases

Check every item before handover. Any "no" keeps the case in draft and names the open item.

## Counting and scope

- [ ] Event count, levels and modules come from `thor_parse` / `thor_first_assessment`, not from reading.
- [ ] INFO, NOTICE, unknown-score and ERROR events are accounted for.
- [ ] Events, automatic observation groups and analyst findings are reported separately, with the reason they differ.
- [ ] The per-finding event counts were computed in code and sum exactly to the finding-event count (not added up by eye).
- [ ] The mapping table states the partition of finding events (how many carry `reasons`, how many are reason-less module observations such as `ProcessIntegrity`), and that partition explains the events-vs-findings gap.
- [ ] Export origin, THOR edition, known flags/mode, filters and split parts are documented.
- [ ] Coverage gaps are stated (e.g. THOR Lite: no Registry, Eventlog, SHIMCache or Sigma).

## Analysis

- [ ] Every ALERT and WARNING was reviewed with module and signature context.
- [ ] Every reported finding has a false-positive review outcome with a reason.
- [ ] Multi-source duplicates (same path, record ID, detection ID, command line) were merged deliberately.
- [ ] Prevalence was considered when more than one host is in scope.
- [ ] Confirmed, Strong Indicator and Not Derivable claims are labelled.

## Claims that must not appear without independent evidence

- [ ] Execution inferred from SHIMCache alone.
- [ ] File owner presented as the executing user.
- [ ] Scan or detection time presented as attack time.
- [ ] Successful remediation inferred from an AV action name.
- [ ] Attribution inferred from a rule or IOC name.
- [ ] Lateral movement, credential use or password cracking without matching artefacts.
- [ ] A clean host inferred from missing findings.
- [ ] Undated evidence quietly ordered into the timeline. A match whose captured context carries no timestamp (a session line in a tool trace, a substring from a log) is Confirmed as an event and **Not Derivable** as to time: give it an explicit `undatiert` entry and say so in `Grenzen` — never omit it, never date it from the containing file's mtime.

## Output

- [ ] All nine sections are present in order; the Assessment block is analytical.
- [ ] Tool-Erstbewertung and Analystenbewertung are both shown; deviations are justified.
- [ ] Priority and criticality are set independently and justified.
- [ ] No passwords, LM/NTLM hashes or credential match strings appear anywhere.
- [ ] Indicators intended for sharing are marked with their sharing status.
- [ ] Every action that changes a system is marked as requiring approval.
- [ ] The case contains no material from other cases without shared technical indicators.
