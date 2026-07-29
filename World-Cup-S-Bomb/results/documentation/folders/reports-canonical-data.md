# `results/reports/canonical/data/`

Canonical tabular data backing the published reports.

## Inventory

- Direct files: **2**
- Immediate subfolders: **0**
- Formats: `.csv` (2)

## Files

| File | Format and scale | Information contained | Structure |
|---|---|---|---|
| [`defense_disruption.csv`](../../reports/canonical/data/defense_disruption.csv) | .csv; 593 data rows × 6 columns; 47,504 bytes | Tabular dataset: defense disruption. | Columns: player_id, xd_total, xd_actions, xd_mean_action_threat, xd90, xd90_pct |
| [`team_metrics_v2.csv`](../../reports/canonical/data/team_metrics_v2.csv) | .csv; 32 data rows × 16 columns; 8,225 bytes | Tabular dataset: team metrics v2. | Columns: team, total_xt_created, total_xa_created, pressured_passes, pressure_resistance_rate, defensive_hull_area, defensive_density, defensive_width, defensive_depth, mean_creation_score, mean_defensive_score, mean_ball_security_score, mean_xd90, mean_creation_score_ranked_300, mean_defensive_score_ranked_300, mean_ball_security_score_ranked_300 |

## Interpretation and use

Use human-readable Markdown, office documents, and figures for review. Use CSV, JSON, and Parquet artifacts for reproducible analysis. Consult the canonical model summary and provenance metadata before comparing metrics across model generations.
