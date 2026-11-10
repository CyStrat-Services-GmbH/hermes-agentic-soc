---
name: thor-assessment
description: "Produce evidence-bounded first assessments of THOR JSON v1/v2 exports. Use for deterministic event counting and case reports, not unsupported CSV or v3 input."
---

# Thor Assessment

1. Use an absolute input path in an operator-approved evidence root.
2. Call thor_first_assessment; use its exact inventory, never count snippets.
3. Separate source events from correlated observations. INFO and unknown scores remain visible.
4. Inspect the generated JSON and Markdown. Preserve the nine case sections: Titel, Summary, Assessment, Bewertung, Priorität, Kritikalität, IOCs und Artefakte, Timeline, Maßnahmen.
5. Separate Confirmed scanner observations, Strong Indicator interpretations and Not Derivable claims.
6. Do not claim execution from SHIMCache, owner=executing-user, successful remediation, credential reuse, attribution or initial access without independent evidence.
7. Never reproduce passwords, LM/NTLM hashes or raw match/firstbytes contents. Report malware hashes only from typed artifact fields.
8. Draft actions; do not isolate, block, deploy or post a ticket.

Input example: thor_first_assessment({"path":"/absolute/plugin/examples/demo/thor.json"}).
Output: exact event/finding counts, bounded verdict, private report paths and a draft-only ticket.
