# Results documentation dictionary

Use these three compact dictionaries instead of individual folder summaries:

- [`Results Dictionary`](results-dictionary.md) — where every artifact family lives.
- [`Reports - Profiles`](reports-profiles.md) — player profiles, heatmaps, starter reports, team profiles, and coaching reports.
- [`Reports - Rankings`](reports-rankings.md) — global, goalkeeper, position, role, and team rankings.

## Exact-file search

The results tree currently contains **2,768 files**. Use [`file_dictionary.csv`](file_dictionary.csv) for spreadsheet search or [`file_dictionary.json`](file_dictionary.json) for programmatic search. These are indexes only; the three Markdown documents above are the human-readable dictionary.

## Canonical rule

Use `global_rankings_outfield.csv` or `player_rankings_300plus.csv` for outfield order, `goalkeeper_rankings.csv` for goalkeeper order, and `player_rankings.csv` as the complete feature/profile master table. Use `results/reports/canonical/` for narrative summaries. A validation task may explicitly call for an out-of-fold artifact from `audit/` or `diagnostics/`. Role Quality v3 supplies position/role order, and match-bootstrap Uncertainty is descriptive rather than a scoring penalty.

Rebuild after result changes with `python results/documentation/generate_documentation.py`.
