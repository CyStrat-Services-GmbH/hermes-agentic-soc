<p align="center">
  <a href="https://www.cystrat-services.com/"><img src="assets/brand/cystrat.png" width="30%" alt="CyStrat Services GmbH"></a>
  <a href="https://www.nextron-systems.com/"><img src="assets/brand/nextron.png" width="30%" alt="Nextron Systems"></a>
  <a href="https://xplt.com/"><img src="assets/brand/exploit-labs.png" width="30%" alt="exploit labs"></a>
</p>

<h1 align="center">Hermes Agentic SOC</h1>

<p align="center"><strong>Cybersecurity from Germany. For the world.</strong></p>

<p align="center">
  <a href="plugin.yaml"><img src="assets/badges/version.svg" alt="Version 0.1.3"></a>
  <a href="docs/GETTING-STARTED.md#prerequisites"><img src="assets/badges/python.svg" alt="Standalone-Engine: Python ab 3.11"></a>
  <a href="docs/GETTING-STARTED.md#install-in-hermes"><img src="assets/badges/hermes.svg" alt="Hermes ab 0.23.1"></a>
</p>
<p align="center">
  <a href="#lizenz-und-veröffentlichungsstatus"><img src="assets/badges/preview.svg" alt="Private Entwicklungsvorschau"></a>
  <a href="docs/INTEGRATION-ROADMAP.md"><img src="assets/badges/integrations.svg" alt="21 geplante, nicht aktive Anbindungen"></a>
  <a href="LICENSE"><img src="assets/badges/license.svg" alt="Lizenzfreigabe offen; Apache-2.0 nur vorgeschlagen"></a>
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
> **Private Entwicklungsvorschau · v0.1.3.** Die lokale Evidenzanalyse ist implementiert. Die 21 Technologieanbindungen sind Vorlagen, keine produktiven Connectoren; Offensive Security ist eine deaktivierte Planungsvorschau. Apache-2.0 ist lediglich vorgeschlagen.

## Was heute enthalten ist

| Bereich | Umfang | Einordnung |
|---|---|---|
| Hermes-Erweiterung | 8 native Tools, 4 Slash-Kommandos, 1 Approval-Hook | Öffentliche Plugin-Schnittstellen |
| Evidenzanalyse | THOR JSON v1/v2 und NDJSON, exakte Zählung und konservative Beobachtungsgruppen | Keine Unterstützung für v3 oder Legacy-CSV/Text |
| Erstbewertung | Deterministische Bewertung, JSON und deutscher Neun-Abschnitte-Bericht | Vorläufige Triage, kein automatischer Kompromittierungsnachweis |
| Fachwissen | 6 Defense-Profile, 3 Research-Skelette, 36 Skills | 9 Skills für die THOR-Ergebnisanalyse, 6 Domain-Skills, 21 technologiebezogene Planungsvorlagen |
| Workflows | 4 deklarative Referenzen | Keine ausführbare Workflow-Engine |
| Anbindungen | 21 geplante Technologien einschließlich CyStrat SOC Suite | 0 verifiziert aktive Remote-Connectoren |
| Lokaler Scan | Wrapper für separat bezogenes THOR | Menschliche Freigabe nötig; echter Herstellerscan hier nicht validiert |

Die [THOR-Analyse-Suite](docs/THOR-ANALYSIS.md) bündelt neun Skills für die Auswertung von THOR-Ergebnissen: Modul- und Signaturinterpretation, False-Positive-Prüfung, Korrelation und Timeline, Flottenanalyse, sicherer Umgang mit IOCs und die Übernahme von SIEM-Exporten. Die Zählung bleibt bei den deterministischen Tools; die Skills sorgen für die fachlich saubere Bewertung.

Die [Capability-Referenz](docs/CAPABILITIES.md) beschreibt die Werkzeuge und Rollen. Der [Validierungsnachweis](docs/VALIDATION.md) trennt ausgeführte Tests von offenen Abnahmen.

## Drei Unternehmen, klar abgegrenzte Beiträge

- **[CyStrat Services GmbH](https://www.cystrat-services.com/):** SOC- und Incident-Response-Erfahrung als Grundlage für wiederverwendbare Skills, Rollen und Abläufe im gemeinsamen Defense-Projekt.
- **[Nextron Systems](https://www.nextron-systems.com/):** THOR und forensische Bewertung im gemeinsamen Projekt; Scanner, Signaturen, Regeln und Lizenzen werden nicht mitgeliefert.
- **[exploit labs](https://xplt.com/):** Geplanter Entwickler und Contributor des Offensive-Security-Teils unter Geschäftsführer Johannes Schönborn. In dieser Version ausschließlich als Skelett, Marketing-Credit und Gated Preview enthalten.

Die [Research-Vorschau](docs/GATED-PREVIEW.md) erfordert Operator-Opt-in und einen gültigen deklarierten Scope. Sie erstellt ausschließlich Pläne und enthält weder operative Exploits noch Interaktionen mit Zielsystemen.

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

## Lizenz und Veröffentlichungsstatus

Die finale Rechteklärung steht aus; Apache-2.0 ist nur vorgeschlagen. Der [Lizenzplatzhalter](LICENSE) erteilt keine vorläufige Open-Source-Lizenz.

- [ ] **Release-blockierendes TODO:** Finale Zustimmung einholen und `LICENSE`, `NOTICE` sowie `plugin.yaml` gemeinsam aktualisieren.

Das Repository bleibt privat. Eine Änderung der Sichtbarkeit, Veröffentlichung oder Einreichung setzt eine erneute ausdrückliche Freigabe voraus.

---

<p align="center">
  <a href="https://www.cystrat-services.com/">CyStrat Services</a> ·
  <a href="https://www.nextron-systems.com/">Nextron Systems</a> ·
  <a href="https://xplt.com/">exploit labs</a> ·
  <a href="docs/README.md">Zur Dokumentation</a>
</p>
