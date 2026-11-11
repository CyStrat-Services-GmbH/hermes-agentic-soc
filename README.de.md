<p align="center">
  <a href="https://www.cystrat-services.com/"><img src="assets/brand/cystrat.png" width="30%" alt="CyStrat Services GmbH"></a>
  <a href="https://www.nextron-systems.com/"><img src="assets/brand/nextron.png" width="30%" alt="Nextron Systems"></a>
  <a href="https://xplt.com/"><img src="assets/brand/exploit-labs.png" width="30%" alt="exploit labs"></a>
</p>

<h1 align="center">Hermes Agentic SOC</h1>

<p align="center"><strong>Cybersecurity from Germany. For the world.</strong></p>

<p align="center">
  <a href="plugin.yaml"><img src="assets/badges/version.svg" alt="Version 0.2.4"></a>
  <a href="docs/GETTING-STARTED.md#prerequisites"><img src="assets/badges/python.svg" alt="Standalone-Engine: Python ab 3.11"></a>
  <a href="docs/GETTING-STARTED.md#install-in-hermes"><img src="assets/badges/hermes.svg" alt="Hermes ab 0.23.0"></a>
</p>
<p align="center">
  <a href="#lizenz-und-veröffentlichungsstatus"><img src="assets/badges/preview.svg" alt="Frühe öffentliche Vorschau"></a>
  <a href="docs/INTEGRATION-ROADMAP.md"><img src="assets/badges/integrations.svg" alt="25 geplante, nicht aktive Anbindungen"></a>
  <a href="LICENSE"><img src="assets/badges/license.svg" alt="Apache-2.0"></a>
</p>
<p align="center">
  <a href="https://www.cystrat-services.com/">CyStrat Services</a> ·
  <a href="https://www.nextron-systems.com/">Nextron Systems</a> ·
  <a href="https://xplt.com/">exploit labs</a>
</p>

Wenn agentische KI offensiv eingesetzt wird, brauchen Verteidiger mehr als einen weiteren Chatbot. Sie brauchen einen Assistenten, der mit ihrer Evidenz arbeitet, Grenzen kennt und die Entscheidungen beim verantwortlichen Team belässt.

Hermes Agentic SOC übersetzt Cybersicherheitsexpertise in spezialisierte Hermes-Profile, Skills, native Tools und strukturierte Workflow-Referenzen. Das Projekt von CyStrat Services und Nextron Systems startet mit nachvollziehbarer Triage und deterministischer THOR-Erstbewertung; die Roadmap erweitert diesen Ansatz um ausdrücklich freigegebene, standardmäßig lesende Anbindungen an die bestehende Sicherheitslandschaft.

[English overview](README.md) · [Dokumentation](docs/README.md) · [Schnelleinstieg](docs/GETTING-STARTED.md) · [Roadmap](docs/INTEGRATION-ROADMAP.md)

<p align="center">
  <a href="docs/CAPABILITIES.md"><code>Agentic SOC</code></a> ·
  <a href="docs/OPERATOR-GUIDE.md#assessment-policy"><code>DFIR</code></a> ·
  <a href="docs/OPERATOR-GUIDE.md#tools-and-profiles"><code>Threat Hunting</code></a> ·
  <a href="docs/INTEGRATION-ROADMAP.md"><code>Detection Engineering</code></a> ·
  <a href="docs/CYSTRAT-SOC-SUITE.md"><code>Skills &amp; MCP</code></a> ·
  <a href="SECURITY.md"><code>Human Approval</code></a>
</p>

> [!IMPORTANT]
> **Frühe öffentliche Vorschau · v0.2.4.** Die lokale Evidenzanalyse ist implementiert. Die 25 Technologieanbindungen sind Vorlagen, keine produktiven Connectoren. Offensive Research ist **für eine spätere Version geplant und nicht Teil dieser Fassung** — es existiert dafür kein Profil, Skill, Workflow, Tool oder Schalter. Lizenziert unter Apache-2.0.

## Was heute enthalten ist

| Bereich | Umfang | Einordnung |
|---|---|---|
| Hermes-Erweiterung | 8 native Tools, 4 Slash-Kommandos, 1 Approval-Hook | Öffentliche Plugin-Schnittstellen |
| Evidenzanalyse | THOR JSON v1/v2 und NDJSON, exakte Zählung und konservative Beobachtungsgruppen | Keine Unterstützung für v3 oder Legacy-CSV/Text |
| Erstbewertung | Deterministische Bewertung, JSON und deutscher Neun-Abschnitte-Bericht | Vorläufige Triage, kein automatischer Kompromittierungsnachweis |
| Fachwissen | 6 Defense-Profile, 39 Skills | 9 Skills für die THOR-Ergebnisanalyse, 6 Domain-Skills, 25 technologiebezogene Planungsvorlagen |
| Workflows | 4 deklarative Referenzen | Keine ausführbare Workflow-Engine |
| Anbindungen | 25 geplante Technologien; CyStrat SOC Suite domänenübergreifend | 0 verifiziert aktive Remote-Connectoren |
| Lokaler Scan | Wrapper für separat bezogenes THOR | Menschliche Freigabe nötig; echter Herstellerscan hier nicht validiert |

Die [THOR-Analyse-Suite](docs/THOR-ANALYSIS.md) bündelt neun Skills für die Auswertung von THOR-Ergebnissen: Modul- und Signaturinterpretation, False-Positive-Prüfung, Korrelation und Timeline, Flottenanalyse, sicherer Umgang mit IOCs und die Übernahme von SIEM-Exporten. Die Zählung bleibt bei den deterministischen Tools; die Skills sorgen für die fachlich saubere Bewertung.

Die [Capability-Referenz](docs/CAPABILITIES.md) beschreibt die Werkzeuge und Rollen. Der [Validierungsnachweis](docs/VALIDATION.md) trennt ausgeführte Tests von offenen Abnahmen.

## Drei Unternehmen, klar abgegrenzte Beiträge

- **[CyStrat Services GmbH](https://www.cystrat-services.com/):** SOC- und Incident-Response-Erfahrung als Grundlage für wiederverwendbare Skills, Rollen und Abläufe im gemeinsamen Defense-Projekt.
- **[Nextron Systems](https://www.nextron-systems.com/):** THOR und forensische Bewertung im gemeinsamen Projekt; Unterstützung und Zusammenarbeit durch die Geschäftsführung von Nextron Systems bestätigt. Scanner, Signaturen, Regeln und Lizenzen werden nicht mitgeliefert.
- **[exploit labs](https://xplt.com/):** Bestätigter Unterstützer und Kooperationspartner; Entwickler und Contributor des künftigen Offensive-Research-Teils. Dieser Teil ist weiterhin für eine spätere Version geplant und hier nicht enthalten; siehe [Planung](docs/PLANNED-OFFENSIVE-RESEARCH.md).

Die [Research-Vorschau](docs/PLANNED-OFFENSIVE-RESEARCH.md) erfordert Operator-Opt-in und einen gültigen deklarierten Scope. Sie erstellt ausschließlich Pläne und enthält weder operative Exploits noch Interaktionen mit Zielsystemen.

## Sicher evaluieren

Mit Python 3.11 oder neuer im autorisierten Checkout:

```bash
python -m agentic_soc demo --output /tmp/hermes-agentic-soc-demo
python -m agentic_soc capabilities
```

Die synthetische Demo enthält keine Malware und liefert genau 4 Quellereignisse sowie 3 Beobachtungsgruppen. Das sind keine drei nachgewiesenen Sicherheitsvorfälle.

Installation, Profilkonfiguration und Evidenzverzeichnisse sind im [Schnelleinstieg](docs/GETTING-STARTED.md) und im [Operator Guide](docs/OPERATOR-GUIDE.md) beschrieben. THOR wird separat und entsprechend dem jeweiligen Einsatz lizenziert.

## Ihre Umgebung bleibt unter Ihrer Kontrolle

- **Keine versteckten Dienste:** Keine Plugin-Telemetrie, kein Selbst-Updater und keine versteckten LLM-Aufrufe.
- **Menschliche Freigabe:** Sensible Ausführung läuft über Hermes; ein Modellargument ersetzt keine Zustimmung.
- **Read-only als Zielbild:** Künftige Connectoren benötigen serverseitige Rechtebegrenzung und eigene Abnahmetests.
- **Datenschutz mit offengelegten Grenzen:** Minimierung und Pseudonymisierung sind keine garantierte Anonymisierung oder automatische DSGVO-Konformität. Tool-Ausgaben können in den Kontext des konfigurierten Hermes-Modells gelangen.
- **Nachvollziehbarkeit:** Lokales Metadaten-Audit, jedoch kein manipulationssicheres Beweismittelregister.

Lesen Sie vor Kundenevidenz oder Scan-Ausführung das [Sicherheitsmodell](SECURITY.md). Die Roadmap verspricht weder produktive Herstellerkompatibilität noch verbindliche Liefertermine.

## Sicherheits-Offenlegung

Was das Plugin auf der Maschine tut, in den Kategorien, die vor einer Installation geprüft werden:

| Verhalten | Was passiert |
|---|---|
| **Netzwerk** | Keines. Kein HTTP-Client, kein Abruf, keine Telemetrie, keine Update-Prüfung. Evidenz verlässt die Maschine über dieses Plugin nicht. |
| **Kommandozeile** | Zwei Subprozesse. `thor_lite_scan` startet die THOR-Binary des Betreibers aus `thor_path` — separat lizenziert, nie gebündelt oder nachgeladen — nachdem die `--help`-Ausgabe auf die erforderlichen Flags geprüft wurde. `soc_template_install` ruft nach ausdrücklicher Freigabe lokal `hermes profile create … --no-credentials --no-skills --no-alias` auf. Beide bekommen eine PATH-only-Umgebung, erben also keinen Provider-Key und kein Proxy-Secret. |
| **Lesen außerhalb des Plugins** | Evidenzdateien werden nur innerhalb der konfigurierten `evidence_roots` und `scan_roots` gelesen. Pfade außerhalb werden abgewiesen, Symlinks aufgelöst und eingegrenzt, Zugangsdateien (`.env`, `auth.json`, Schlüsselmaterial) namentlich verweigert. |
| **Schreiben** | Fälle, Berichte, Inventare und ein JSONL-Audit landen unter `plugin_data_dir("agentic-soc")` mit Modus `0700`. In die untersuchte Evidenz wird nichts geschrieben. |
| **Zugangsdaten** | Werden nicht gelesen, gespeichert oder weitergereicht. Das Plugin deklariert kein `requires_env` und berührt keinen Secret-Store. |
| **Hintergrundaktivität** | Keine. Kein Watcher, kein Scheduler, kein Daemon; THOR läuft mit Timeout, die Ausgabe wird beim Rückkehr des Aufrufs gelesen. |
| **Modell-Kontext** | Geparste Events und erzeugte Berichte gehen wie jedes andere Tool-Ergebnis in den Session-Kontext und damit zum konfigurierten Modell-Provider. Personendaten werden nach bestem Bemühen minimiert (`--suppresspi`); Ausgaben vor Weitergabe prüfen. |

## Lizenz und Veröffentlichungsstatus

**Apache-2.0.** Der vollständige Lizenztext liegt in [LICENSE](LICENSE); [NOTICE](NOTICE) nennt die Rechteinhaber und was die Lizenz nicht umfasst.

Apache-2.0 passt zu beiden Seiten dieses Projekts: Sie erlaubt die patent- und markensichere Nutzung, die ein Sicherheitsprodukt braucht, ist mit der Open-Source-Lizenz von Hermes Agent vereinbar und erlaubt Unternehmen die Evaluation ohne Sonderprüfung. Sie gilt für Quellcode und Dokumentation — THOR, Signaturen und die Marken von Nextron bleiben unter den Bedingungen von Nextron; Herstellerdokumentation wird verlinkt, nicht einbundelt.

Die gemeinsame Entwicklung mit Nextron Systems ist bestätigt: die **Geschäftsführung von Nextron Systems** hat Unterstützung und Zusammenarbeit für dieses Plugin zugesagt. Das betrifft die Projektzusammenarbeit, nicht eine Rechteeinräumung an THOR, Signaturen oder Marken von Nextron.

Das Repository ist öffentlich unter Apache-2.0. Der Catalog-Eintrag liegt als [NousResearch/hermes-agent#154079](https://github.com/NousResearch/hermes-agent/pull/154079) vor; den geprüften Pin trägt dieser PR, nicht dieses README. Die Veröffentlichung eines Demo-Videos und jede Änderung der Lizenz bleiben Entscheidungen des Rechteinhabers und sind durch dieses Dokument nicht autorisiert.

---

<p align="center">
  <a href="https://www.cystrat-services.com/">CyStrat Services</a> ·
  <a href="https://www.nextron-systems.com/">Nextron Systems</a> ·
  <a href="https://xplt.com/">exploit labs</a> ·
  <a href="docs/README.md">Zur Dokumentation</a>
</p>
