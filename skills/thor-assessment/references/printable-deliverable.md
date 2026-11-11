# Printable case deliverable (HTML + A4 PDF)

Use when the requester wants the case as something they can send, print or file — "mach ein PDF draus", "HTML-Report", "Report für die Geschäftsleitung". The Markdown case stays the authoritative long form; the printable is a **derived** artefact with the same numbers, the same claim labels and the same ban on credential material. Never write it independently and never let a number differ between the two.

Deliver both files, one `MEDIA:` line per artefact, and name which is which in one sentence.

## Procedure

1. **Finish the Markdown case first.** Every figure in the printable comes from the export, not from re-typing the Markdown. Re-derive the KPI block from the parser output.
2. **Check the render tooling before designing anything:**

   ```bash
   command -v google-chrome chromium wkhtmltopdf pandoc 2>/dev/null
   ```

   Headless Chrome/Chromium is the reliable path on Linux and needs no extra packages; it is also the one that honours the `page-break-*` properties below properly.
3. **Generate one self-contained HTML file with a short build script that reads the parser and inventory output, and keep the builder next to the `.html`.** No figure may be typed by hand: the KPI block, the per-finding counts and the review table have to equal the Markdown to the digit, and a hand-assembled group count silently contradicts the table standing next to it. No CDN, no web fonts, no external CSS — the report must render offline, survive being mailed around, and stay re-renderable years later. Font stack: `"Liberation Sans","DejaVu Sans",Arial,sans-serif` with `"DejaVu Sans Mono"` for paths, hashes and rule names.
4. **Print CSS baseline:**

   ```css
   @page { size: A4; margin: 16mm 14mm 14mm 14mm; }
   tbody tr { page-break-inside: avoid; }
   h2 { page-break-after: avoid; }
   .lead { page-break-after: avoid; page-break-inside: avoid; }
   .box, .verdict, .kpis { page-break-inside: avoid; }
   code { word-break: normal; overflow-wrap: anywhere; }
   ```
5. **Render:**

   ```bash
   google-chrome --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
     --virtual-time-budget=4000 \
     --print-to-pdf="<out>.pdf" "file:///abs/path/<in>.html"
   ```

   `file://` needs the absolute path. `--no-pdf-header-footer` suppresses Chrome's own date/URL header; put provenance in your own footer block instead.
6. **Verify the PDF, page by page — this is not optional:**

   ```bash
   pdfinfo out.pdf | grep -E '^(Pages|Page size)'      # A4 = 594.96 x 841.92 pts
   pdftoppm -r 100 -png out.pdf /tmp/page && ls /tmp/page-*.png
   ```

   Then look at every page. The layout bugs below are invisible in the HTML and in `pdfinfo`; only the raster shows them.
7. **Gate the content of the rendered file, not just its layout:**

   ```bash
   pdftotext out.pdf - | grep -icE '<credential-string-patterns>'   # must be 0
   grep -cE 'https?://|src=|@import' report.html                     # must be 0
   ```

   The first proves the artefact that gets forwarded carries none of the credential material the Markdown withholds; the second proves it is self-contained.

   **A failed build still renders.** `--print-to-pdf` converts whatever HTML is on disk, so a builder that crashed or a `compile` error leaves the *previous* version in place while Chrome reports success and writes a plausibly sized PDF. Confirm the HTML's size or timestamp changed, and check one figure in the raster, before you call the render done.

## Layout pitfalls that cost a re-render each

- **Chrome silently clips a table row that straddles a page boundary.** The remainder of the cell is *lost*, not carried to the next page — a file path in the last row simply stops mid-token and no error appears anywhere. `tbody tr { page-break-inside: avoid }` is mandatory for any content-bearing table, and the page raster is the only way to catch it.
- **`page-break-before: always` on section wrappers buys nothing and costs pages.** It leaves a half-empty sheet whenever the preceding section ends early and inflates the page count. Let the content flow; Chrome repeats `thead` automatically across page breaks, so long tables stay readable without forced breaks.
- **`word-break: break-all` on inline `code` shreds identifiers** — `SUSP_RANSOM_*` renders as `SUSP_ RANSOM_ *` and hashes break mid-group. Use `overflow-wrap: anywhere` with `word-break: normal`: the token then breaks only when it genuinely cannot fit.
- **Orphan headings and split lead paragraphs.** A section heading alone at the bottom of a page, or its introductory paragraph cut across the break, reads as a formatting defect in a document meant to look deliberate. Both rules are in the baseline above.
- **Long mono tokens in a fixed-width metadata grid wrap mid-token.** Give that one cell a smaller `font-size` instead of widening the grid — widening unbalances the whole row for the sake of a single identifier.
- **`word-break: break-all` on inline `code` shreds identifiers** — `SUSP_RANSOM_*` renders as `SUSP_ RANSOM_ *` and hashes break mid-group. Use `overflow-wrap: anywhere` with `word-break: normal`: the token then breaks only when it genuinely cannot fit. Even that splits a long identifier in a narrow column (`ProcessConnections` → `ProcessConnection` / `s`), so add `td:first-child code { white-space: nowrap }` and treat the footer the same way — otherwise `--intense --threads 4` becomes `-` / `intense --threads 4`.
- **Inline approval flags on a hanging indent collide with the text.** `text-indent: -6mm` shifts the number only, so a badge at the end of a numbered action renders as `…geleistet.[FREIGABE]` and, once it wraps, lands flush against the left margin. Give the action `position: relative; padding-left: 7mm` and its number span `position: absolute; left: 0`; the badge then flows inline with an explicit `margin-left`.
- **A wrapper grid needs the break rule too.** `page-break-inside: avoid` on `.box` does not protect you when the two-column *container* straddles the boundary: Chrome paints the container borders on both pages and the next page opens with empty frames. Apply the rule to the wrapper as well and let the whole block move.
- **A footer alone on the last page wastes a whole sheet.** Tighten the base scale instead of inserting a break: base `font-size` 9.2 → 9.0 pt, `line-height` 1.42 → 1.37, table-cell padding and `h2` top margin, then re-render and confirm the page count dropped. Losing one page this way is invisible to the reader; a sheet holding only a footer is not.
- **German numbers, not English.** Python's `f'{n:,}'` writes `7,239` where the case must read `7.239`. Format every injected count through one helper (`f'{n:,}'.replace(',', '.')`) and read the KPI strip off the raster — a thousands separator is the first thing a German reader notices and the last thing a code review catches.
- **CSS page numbers do not work in Chrome print** (margin boxes with counters are unsupported). Provenance belongs in a footer block at the end of the document: creation timestamp, export filename, export SHA-256, classification, and the statement that no credential material is contained.

## Structure that reads as a decision, not a data dump

Order the page the way the case argues: **verdict first, evidence second, limits third.**

1. Title band plus a four-cell metadata grid (host, scan ID, scanner/version, assessment timestamp).
2. **Verdict banner** — the answer in one sentence, then the qualifying caveat in a red sub-box. A reader who stops after ten seconds must still leave with the correct, bounded answer.
3. KPI strip: events, alerts/errors, notices+warnings, analyst findings, highest score.
4. Tool layer versus analyst layer side by side — never merged.
5. Coverage table with **element counts** (not module names), followed by a red-marked coverage-gap table for every channel that returned `0`.
6. Impact checklist with a zero column for the destructive indicators.
7. Findings table with one outcome pill per finding, then the timeline with its time-type column, then the approval-flagged actions, then the limits.

Keep every system-changing action marked with its approval flag inline, exactly as in the Markdown — the printable is what gets forwarded, so the approval gate has to survive the copy.

## File placement

Write to a `cases/` directory beside the working directory, one stem per case, three suffixes:

```text
<YYYY-MM-DD>_<Host>_THOR-Erstbewertung.md     <- authoritative long form
<YYYY-MM-DD>_<Host>_THOR-Report.html          <- self-contained source
<YYYY-MM-DD>_<Host>_THOR-Report.pdf           <- rendered A4
```

Keep the `.html` next to the `.pdf`: it is the re-renderable source, and without it a later correction means rebuilding the whole document.
