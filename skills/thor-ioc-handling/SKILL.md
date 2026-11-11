---
name: thor-ioc-handling
description: "Extract, minimise, label and share indicators from THOR results: which artefacts qualify as IOCs, what must never be reproduced (credential hashes, passwords, raw match strings, personal data), defanging, TLP and disclosure approval before any external lookup, and behaviour-based ATT&CK mapping. Use when writing the IOC section of a THOR case or preparing indicators for SIEM, TI or partners; not for automatic uploads or blocking."
---

# THOR indicators: extraction and safe handling

An IOC list is often the part of a case that travels furthest: into a SIEM, a TI platform, a partner's inbox. That makes it the part where mistakes leak customer data or credentials. Extract deliberately, minimise aggressively and share only with approval.

## What qualifies

| Indicator | THOR source | Include when |
|---|---|---|
| File hash (MD5/SHA1/SHA256) | Typed hash fields in Filescan, SHIMCache/AmCache enrichment, Autoruns, ServiceCheck | It identifies a malicious or attacker-tool artefact. Not for credential dumps. |
| File path and name | `FILE`, `IMAGE_PATH`, `ELEMENT` | The path is part of the finding. Generalise user segments for sharing. |
| Service name and image path | ServiceCheck, Eventlog | The service is part of the finding. |
| Scheduled task name and command | ScheduledTasks | Same. |
| Registry key and value | Registry, Autoruns | Same. |
| Domain, IP, URL | DNSCache, ProcessCheck connections, LogScan, Hosts | Malicious or attacker-controlled per evidence; defang for sharing. |
| Mutex, named pipe | Mutex, Pipes | Matched an IOC or is clearly malware-specific. |
| Command line | ProcessCheck, Eventlog, tasks | Relevant and free of secrets. |
| Rule names | Reasons | List as **detection references**, separate from IOCs. A rule name is not an indicator of the attacker. |

## What never appears

- Passwords, LM/NTLM or other password hashes, Kerberos material, tokens and keys.
- `FIRSTBYTES`, matched strings or file content of credential dumps (e.g. SAM/NTDS extracts).
- Personal data that is not needed for the indicator: real user names, e-mail addresses, personal folder names.
- Hashes of credential material, even when they sit in a typed field. The plugin drops typed hashes in credential context automatically; apply the same rule to anything you extract by hand.

Identical hashes of credential dumps across hosts can suggest password reuse. Record that as a Strong Indicator in prose, without the hash values.

## Disclosure before lookup

Any external lookup (public reputation services, public search, shared TI) discloses the indicator and your interest in it.

1. Check the case's data-sharing permission and the customer's policy.
2. Prefer approved internal or private TI sources.
3. Look up only hashes and public infrastructure indicators that are approved for disclosure. Never upload a file.
4. Record each lookup: indicator, service, time, result and approval reference.

This plugin performs no lookups and no uploads.

## Labelling and format

- Defang network indicators for sharing (`hxxp://example[.]com`, `198.51.100[.]7`).
- Give every indicator a TLP or equivalent sharing label, its evidence strength and the event ID it came from.
- Generalise identifying path parts when sharing outside the customer (`C:\Users\<user>\AppData\…`).
- Keep the internal case version and the shareable version separate.

## ATT&CK mapping

Map only observed behaviour, with a rationale and a confidence, never from a rule name or a technique ID in free text. Mark follow-on risks as risks, not as observed techniques. A hack-tool file present on disk supports "tool staged", not "credential dumping performed".

## Output block (case section 7)

```text
| Typ | Wert (intern) | Quelle (Event/Feld) | Beweiskraft | Freigabe |
|---|---|---|---|---|
| SHA256 | `…` | E000001 / sha256 | Confirmed (Datei vorhanden) | intern, TLP:AMBER nach Freigabe |
| Pfad | `C:\Users\<user>\…` | E000001 / file | Confirmed | generalisiert teilbar |

Detection-Referenzen: `<Regelname>` (E000001), …
ATT&CK (nur beobachtetes Verhalten): <Technik> – Begründung: <…> – Konfidenz: <…>
Bewusst nicht aufgenommen: <z. B. Credential-Hashes aus E0000xx>
Externe Abfragen: <keine / Liste mit Freigabe>
```
