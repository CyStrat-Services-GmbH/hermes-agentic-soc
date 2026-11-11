<p align="center">
  <a href="https://www.cystrat-services.com/"><img src="assets/brand/cystrat.png" width="30%" alt="CyStrat Services GmbH"></a>
  <a href="https://www.nextron-systems.com/"><img src="assets/brand/nextron.png" width="30%" alt="Nextron Systems"></a>
  <a href="https://xplt.com/"><img src="assets/brand/exploit-labs.png" width="30%" alt="exploit labs"></a>
</p>

# Hermes Agentic SOC

**Cybersecurity from Germany. For the world.**

Wenn agentische KI offensiv eingesetzt wird, brauchen Verteidiger mehr als einen weiteren Chatbot. Sie brauchen einen Assistenten, der mit ihrer Evidenz arbeitet, Grenzen kennt und die Entscheidungen beim verantwortlichen Team belässt.

Hermes Agentic SOC übersetzt Cybersicherheitsexpertise in spezialisierte Hermes-Profile, Skills, native Tools und strukturierte Workflow-Referenzen. Das Projekt von CyStrat Services und Nextron Systems startet mit nachvollziehbarer Triage und deterministischer THOR-Erstbewertung; die Roadmap erweitert diesen Ansatz um ausdrücklich freigegebene, standardmäßig lesende Anbindungen an die bestehende Sicherheitslandschaft.

[English overview](README.md) · [Dokumentation](docs/README.md) · [Schnelleinstieg](docs/GETTING-STARTED.md) · [Roadmap](docs/INTEGRATION-ROADMAP.md)

> [!IMPORTANT]
> **Private Entwicklungsvorschau · v0.1.2.** Die lokale Evidenzanalyse ist implementiert. Die 21 Technologieanbindungen sind Vorlagen, keine produktiven Connectoren; Offensive Security ist eine deaktivierte Planungsvorschau. Apache-2.0 ist lediglich vorgeschlagen.

## Was heute enthalten ist

| Bereich | Umfang | Einordnung |
|---|---|---|
| Hermes-Erweiterung | 8 native Tools, 4 Slash-Kommandos, 1 Approval-Hook | Öffentliche Plugin-Schnittstellen |
| Evidenzanalyse | THOR JSON v1/v2 und NDJSON, exakte Zählung und konservative Beobachtungsgruppen | Keine Unterstützung für v3 oder Legacy-CSV/Text |
| Erstbewertung | Deterministische Bewertung, JSON und deutscher Neun-Abschnitte-Bericht | Vorläufige Triage, kein automatischer Kompromittierungsnachweis |
| Fachwissen | 6 Defense-Profile, 3 Research-Skelette, 29 Skills | Davon 21 technologiebezogene Planungsvorlagen |
| Workflows | 4 deklarative Referenzen | Keine ausführbare Workflow-Engine |
| Anbindungen | 21 geplante Technologien einschließlich CyStrat SOC Suite | 0 verifiziert aktive Remote-Connectoren |
| Lokaler Scan | Wrapper für separat bezogenes THOR | Menschliche Freigabe nötig; echter Herstellerscan hier nicht validiert |

Die [Capability-Referenz](docs/CAPABILITIES.md) beschreibt die Werkzeuge und Rollen. Der [Validierungsnachweis](docs/VALIDATION.md) trennt ausgeführte Tests von offenen Abnahmen.

## Drei Unternehmen, klar abgegrenzte Beiträge

- **CyStrat Services GmbH:** SOC- und Incident-Response-Erfahrung als Grundlage für wiederverwendbare Skills, Rollen und Abläufe im gemeinsamen Defense-Projekt.
- **Nextron Systems:** THOR und forensische Bewertung im gemeinsamen Projekt; Scanner, Signaturen, Regeln und Lizenzen werden nicht mitgeliefert.
- **exploit labs:** Geplanter Entwickler und Contributor des Offensive-Security-Teils unter Geschäftsführer Johannes Schönborn. In dieser Version ausschließlich als Skelett, Marketing-Credit und Gated Preview enthalten.

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
