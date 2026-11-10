# Hermes Agentic SOC demo

Target duration: 75–85 seconds. Rehearse and measure the real recording; no video is claimed to exist yet. The official announcement requires a working demo shorter than 90 seconds and a post tagging @NousResearch ([hackathon announcement](https://x.com/NousResearch/status/2118094256438936062)).

## Recording sequence

- **0–10 s:** Title: “Hermes Agentic SOC. CyStrat Services × Nextron Systems.” Say: “Evidence-first SOC specialists for Hermes, with THOR kept external.”
- **10–23 s:** Show `/soc-templates`. Choose the DFIR role and show the `soc_template_install` dry-run. Explain that actual creation requires host approval and does not copy credentials.
- **23–34 s:** Show `/thor-scan` capability/dry-run if THOR is independently installed. Otherwise state clearly: “No licensed scanner installed on this demo host; we use supplied synthetic THOR JSON.” Never imply a scan happened.
- **34–53 s:** Run `/thor-assess` on the shipped absolute demo path. Show exactly four source events and three correlated observation groups, including INFO.
- **53–68 s:** Open the generated report. Show Summary, Assessment and evidence limits: scanner ALERT is suspicious, not proof of execution; scan time is not attack time.
- **68–80 s:** Show draft-only ticket and no-write flag. Explain host approval gates and scope-gated research plans. Close with “Extensible profiles and technology scaffolds, not unreviewed autonomous containment.”

## Terminal fallback

```bash
python examples/demo/run_demo.py --output /tmp/hermes-agentic-soc-demo
```

This demonstrates the real offline implementation, not live Hermes UI behavior. Label it as such if the recorded demo uses this fallback. Do not claim interactive integration from terminal engine output.

## Suggested X post, pending license decision

Built with CyStrat Services × Nextron Systems: Hermes Agentic SOC.
Evidence-first SOC specialists, exact THOR export counts, deterministic first assessment and human-approved actions. THOR stays external. No autonomous containment.
Source and demo: use the actual repository/video URLs.
@NousResearch

Do not call it Apache-2.0/Open Source until the license decision is approved and committed.
