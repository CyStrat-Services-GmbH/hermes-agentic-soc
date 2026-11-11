[Project overview](../README.md) / [Documentation](README.md) / Offensive Security preview

# Offensive Security: gated preview

<p><img src="../assets/brand/exploit-labs.png" width="260" alt="exploit labs"></p>

> [!IMPORTANT]
> **Planning only · disabled by default.** No operational offensive implementation from exploit labs is delivered in this release.

The project sponsor has specified **exploit labs**, led by managing director **Johannes Schönborn**, as the planned developer and contributor of the Offensive Security part. Attribution is limited to this skeleton, marketing and preview materials. The existing code license/copyright and defense implementation authorship are not changed.

## Included now

- `red-team-planner`, `adversary-emulation`, `purple-team-validator`: planning personas marked scaffold.
- `authorized-research`: instructions for exact scope, authorization reference, validity window and rules of engagement.
- `soc_research_plan`: a structural scope check and generic plan, not contributed exploit tooling.
- Operator setting `offensive_preview_enabled:false`: closed by default, checked in tool policy and runtime.
- No scanner, exploit, persistence, credential extraction, target interaction or live offensive connector.

## Opt-in boundary

Only the operator may enable the preview through the intended Hermes profile's plugin settings. A model tool argument cannot enable it. Valid scope is still required after enabling; legal authorization is still the human operator's responsibility.

```yaml
plugins:
  entries:
    agentic-soc:
      settings:
        offensive_preview_enabled: false
```

Do not flip this setting automatically after a denial. Any future implementation from exploit labs needs a separate code review, tests, delivery acknowledgement and license decision before replacing these scaffolds.

## Marketing wording

“Defense und THOR-Integration: CyStrat Services × Nextron Systems.
Offensive Security: geplanter Beitrag von exploit labs und Geschäftsführer Johannes Schönborn.
Aktuell als Gated Preview, ohne operative Angriffsfunktionen.”

This is a private preview. No public posting, repository visibility change or catalog submission is authorized by adding these credits.
