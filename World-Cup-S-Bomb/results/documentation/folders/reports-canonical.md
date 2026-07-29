# `results/reports/canonical/`

Canonical release artifacts: rankings, final summary, model summary, coaches notebook, and their data exports.

## Inventory

- Direct files: **6**
- Immediate subfolders: **1**
- Formats: `.csv` (1), `.json` (2), `.md` (3)

## Subfolders

- [`results/reports/canonical/data/`](reports-canonical-data.md) — Canonical tabular data backing the published reports.

## Files

| File | Format and scale | Information contained | Structure |
|---|---|---|---|
| [`coaches_notebook.md`](../../reports/canonical/coaches_notebook.md) | .md; 123 lines; 1,553 words; 7,609 bytes | Coaches Notebook | Title: Coaches Notebook; sections: Tactical insights, Passing networks, Pressing leaders, Spatial advantages, Line breakers, Goalkeeper ranking |
| [`final_summary.md`](../../reports/canonical/final_summary.md) | .md; 763 lines; 7,739 words; 42,358 bytes | World Cup V5 Role-Aware Final Report | Title: World Cup V5 Role-Aware Final Report; sections: Executive summary, How to read the player rating, General player summary, Overall leaders, Position-group leaders, Largest upward rank movements, Largest downward rank movements, All-team overview |
| [`model_summary.json`](../../reports/canonical/model_summary.json) | .json; Object with 15 top-level keys; 58,482 bytes | Model-selection, validation, calibration, feature-importance, and metric-gate summary. | Top-level keys: schema_version, selected_layer, metric_gate_passed, metrics, metric_gate, validation_regression_gate, feature_importance, role_aware_elastic_net, goalkeeper_model, cluster_stability, probabilistic_role_selection, rating_weights, composite_calibration, rating_methodology, defense_disruption |
| [`model_summary.md`](../../reports/canonical/model_summary.md) | .md; 1,858 lines; 2,415 words; 42,764 bytes | Model Summary | Title: Model Summary; sections: Attention metric gate, Metrics, Feature importance, Grouped ElasticNet valuation, Goalkeeper model, V2 rating methodology, Composite calibration, Defensive disruption |
| [`player_rankings.csv`](../../reports/canonical/player_rankings.csv) | .csv; 593 data rows × 373 columns; 3,266,975 bytes | Player leaderboard with global, position, role, and team ranks plus valuation features. | Columns: player_name, team, position_group, functional_role, final_player_rating, global_rank, position_rank, role_rank, team_rank, RankingStatus, GKRankingStatus, primary_global_rank, primary_goalkeeper_rank, player_id, actions, aerial_events, aerial_wins, average_x, average_y, blocks, box_passes, carries, carry_progression_sum, clearances, completed_passes, counterpressures, crosses, dribbled_past, dribbles, duels, duels_won, final_third_passes, fouls, goals, interceptions, interceptions_won,… |
| [`player_rankings.json`](../../reports/canonical/player_rankings.json) | .json; Array with 593 records; 9,023,285 bytes | Player leaderboard with global, position, role, and team ranks plus valuation features. | Record keys: player_name, team, position_group, functional_role, final_player_rating, global_rank, position_rank, role_rank, team_rank, RankingStatus, GKRankingStatus, primary_global_rank, primary_goalkeeper_rank, player_id, actions, aerial_events, aerial_wins, average_x, average_y, blocks, box_passes, carries, carry_progression_sum, clearances, completed_passes, counterpressures, crosses, dribbled_past, dribbles, duels, duels_won, final_third_passes, fouls, goals, interceptions, interceptions_… |

## Interpretation and use

Use human-readable Markdown, office documents, and figures for review. Use CSV, JSON, and Parquet artifacts for reproducible analysis. Consult the canonical model summary and provenance metadata before comparing metrics across model generations.
