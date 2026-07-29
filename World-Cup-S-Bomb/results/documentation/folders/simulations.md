# `results/simulations/`

Tactical-style and substitution simulation outputs, including out-of-fold variants and suppression audits.

## Inventory

- Direct files: **6**
- Immediate subfolders: **0**
- Formats: `.csv` (2), `.parquet` (4)

## Files

| File | Format and scale | Information contained | Structure |
|---|---|---|---|
| [`oof_fold_integrity.csv`](../../simulations/oof_fold_integrity.csv) | .csv; 64 data rows × 6 columns; 1,837 bytes | Tabular dataset: oof fold integrity. | Columns: held_out_match, evaluation_rows, model_train_matches, calibration_matches, development_matches, heldout_excluded |
| [`optimized_starting_lineups.csv`](../../simulations/optimized_starting_lineups.csv) | .csv; 352 data rows × 6 columns; 23,729 bytes | Tabular dataset: optimized starting lineups. | Columns: team, rank, player_id, player, position_group, optimization_score |
| [`substitution_optimization.parquet`](../../simulations/substitution_optimization.parquet) | .parquet; Binary table; inspect with pandas or PyArrow for the physical schema; 8,024 bytes | Columnar analytical dataset: substitution optimization. | Apache Parquet columnar dataset |
| [`substitution_suppressions.parquet`](../../simulations/substitution_suppressions.parquet) | .parquet; Binary table; inspect with pandas or PyArrow for the physical schema; 16,927 bytes | Audit of simulation recommendations removed by safety or eligibility rules. | Apache Parquet columnar dataset |
| [`tactical_style_simulations.parquet`](../../simulations/tactical_style_simulations.parquet) | .parquet; Binary table; inspect with pandas or PyArrow for the physical schema; 314,444 bytes | Counterfactual tactical or substitution simulation output. | Apache Parquet columnar dataset |
| [`tactical_style_simulations_oof.parquet`](../../simulations/tactical_style_simulations_oof.parquet) | .parquet; Binary table; inspect with pandas or PyArrow for the physical schema; 498,977 bytes | Counterfactual tactical or substitution simulation output. | Apache Parquet columnar dataset |

## Interpretation and use

Use human-readable Markdown, office documents, and figures for review. Use CSV, JSON, and Parquet artifacts for reproducible analysis. Consult the canonical model summary and provenance metadata before comparing metrics across model generations.
