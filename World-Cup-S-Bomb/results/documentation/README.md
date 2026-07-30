# Results documentation dictionary

Use these three compact dictionaries instead of individual folder summaries:

- [`Results Dictionary`](results-dictionary.md) — where every artifact family lives.
- [`Reports - Profiles`](reports-profiles.md) — player profiles, heatmaps, starter reports, team profiles, and coaching reports.
- [`Reports - Rankings`](reports-rankings.md) — global, goalkeeper, position, role, and team rankings.

## Exact-file search

The results tree currently contains **2,683 files**. Use [`file_dictionary.csv`](file_dictionary.csv) for spreadsheet search or [`file_dictionary.json`](file_dictionary.json) for programmatic search. These are indexes only; the three Markdown documents above are the human-readable dictionary.

## Canonical rule

Use `results/reports/ranking/` for active player ordering and `results/reports/canonical/` for narrative summaries. A validation task may explicitly call for an out-of-fold artifact from `audit/` or `diagnostics/`.

Rebuild after result changes with `python results/documentation/generate_documentation.py`.
