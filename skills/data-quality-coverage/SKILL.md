---
name: data-quality-coverage
description: "Assess whether the available telemetry can answer the question at all. Use when a result is empty, partial or suspiciously clean, not as a reason to stop investigating."
---

# Data Quality Coverage

1. List the data sources the question requires, and which of them actually exist for the scope in question.
2. For each source, record coverage (hosts, users, applications), retention and known ingestion gaps.
3. Check integrity signals: parser errors, dropped events, time skew, duplicate suppression, sampling and filter rules.
4. Distinguish three states explicitly: activity absent, activity not collected, and collection not verifiable.
5. Quantify what you can: expected versus present hosts, expected versus received events, first and last event per source.
6. Name the blind spots that matter for this specific case, not a generic list.
7. Recommend the smallest additional data that would change the decision, and who can provide it.

A clean result from an unverified source is a coverage finding, never an all-clear.
