# Results documentation dictionary

Use these three compact dictionaries instead of individual folder summaries:

- [`Results Dictionary`](results-dictionary.md) — where every artifact family lives.
- [`Reports - Profiles`](reports-profiles.md) — player profiles, heatmaps, starter reports, team profiles, and coaching reports.
- [`Reports - Rankings`](reports-rankings.md) — global, goalkeeper, position, role, and team rankings.

## Exact-file search

The results tree currently contains **2,720 files**. Use [`file_dictionary.csv`](file_dictionary.csv) for spreadsheet search or [`file_dictionary.json`](file_dictionary.json) for programmatic search. These are indexes only; the three Markdown documents above are the human-readable dictionary.

## Canonical rule

Use `results/reports/ranking/player_rankings.csv` (or the explicit `player_rankings_v3.csv` version) for active Tournament Impact v3 ordering and `results/reports/canonical/` for narrative summaries. A validation task may explicitly call for an out-of-fold artifact from `audit/` or `diagnostics/`. Role Quality v3 supplies position/role order, and match-bootstrap Uncertainty is descriptive rather than a scoring penalty. V2/V5-named ranking files are compatibility aliases; historical methodology belongs under `reports/ranking/legacy/`.

Rebuild after result changes with `python results/documentation/generate_documentation.py`.
