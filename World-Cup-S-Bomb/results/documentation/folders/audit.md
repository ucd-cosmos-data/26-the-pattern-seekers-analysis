# `results/audit/`

Observed-versus-expected comparison tables used to audit possession predictions, team aggregates, and out-of-fold behavior.

## Inventory

- Direct files: **6**
- Immediate subfolders: **0**
- Formats: `.csv` (4), `.parquet` (2)

## Files

| File | Format and scale | Information contained | Structure |
|---|---|---|---|
| [`expected_vs_actual_possessions.parquet`](../../audit/expected_vs_actual_possessions.parquet) | .parquet; Binary table; inspect with pandas or PyArrow for the physical schema; 132,108 bytes | Observed-versus-model-expected audit output. | Apache Parquet columnar dataset |
| [`expected_vs_actual_possessions_oof.parquet`](../../audit/expected_vs_actual_possessions_oof.parquet) | .parquet; Binary table; inspect with pandas or PyArrow for the physical schema; 159,200 bytes | Observed-versus-model-expected audit output. | Apache Parquet columnar dataset |
| [`expected_vs_actual_team_summary.csv`](../../audit/expected_vs_actual_team_summary.csv) | .csv; 32 data rows × 7 columns; 3,563 bytes | Observed-versus-model-expected audit output. | Columns: team, possessions, total_wasted_net_xg, mean_eva_gap, actual_expected_net_xg, optimal_expected_net_xg, most_common_optimal_style |
| [`expected_vs_actual_team_summary_oof.csv`](../../audit/expected_vs_actual_team_summary_oof.csv) | .csv; 32 data rows × 8 columns; 4,374 bytes | Observed-versus-model-expected audit output. | Columns: team, possessions, total_wasted_net_xg, mean_eva_gap, actual_expected_net_xg, optimal_expected_net_xg, most_common_optimal_style, tactical_reason_code |
| [`recurrent_tactical_mistakes.csv`](../../audit/recurrent_tactical_mistakes.csv) | .csv; 362 data rows × 7 columns; 36,622 bytes | Tabular dataset: recurrent tactical mistakes. | Columns: team, defensive_style, actual_style, optimal_style, possessions, wasted_net_xg, mean_eva_gap |
| [`recurrent_tactical_mistakes_oof.csv`](../../audit/recurrent_tactical_mistakes_oof.csv) | .csv; 465 data rows × 7 columns; 45,157 bytes | Tabular dataset: recurrent tactical mistakes oof. | Columns: team, defensive_style, actual_style, optimal_style, possessions, wasted_net_xg, mean_eva_gap |

## Interpretation and use

Use human-readable Markdown, office documents, and figures for review. Use CSV, JSON, and Parquet artifacts for reproducible analysis. Consult the canonical model summary and provenance metadata before comparing metrics across model generations.
