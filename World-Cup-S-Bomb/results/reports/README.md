# Canonical V5 Reports

These are the current V5 role-aware player analytics outputs. They supersede
V4 player-rating values embedded in historical simulation packets; possession,
transition-risk, and tactical-scenario results remain valid for their original
targets. Final report and profile paths use stable unversioned canonical names.

## Current player hierarchy

| Global rank | Player | Team | Functional role | Final rating |
|---:|---|---|---|---:|
| 1 | Lionel Andrés Messi Cuccittini | Argentina | Progressive Winger | 0.8371 |
| 2 | Kylian Mbappé Lottin | France | Progressive Winger | 0.8258 |
| 3 | Julián Álvarez | Argentina | Target Forward | 0.7526 |
| 4 | Vinícius José Paixão de Oliveira Júnior | Brazil | Progressive Winger | 0.7354 |
| 5 | Ángel Fabián Di María Hernández | Argentina | Progressive Winger | 0.7329 |

## Report index

- [`v5_player_rankings.csv`](v5_player_rankings.csv) and
  [`v5_player_rankings.json`](v5_player_rankings.json): global outfield,
  position, role, team, and separate goalkeeper rankings.
- [`player_profiles/`](player_profiles/): 142 coverage-qualified
  individual reports.
- [`team_profiles/`](team_profiles/): 32 current team summaries.
- [`v5_coaches_notebook.md`](v5_coaches_notebook.md): passing, pressing,
  spatial, and line-breaking leaders.
- [`model_summary.md`](model_summary.md) and
  [`model_summary.json`](model_summary.json):
  VAEP, ElasticNet, goalkeeper, GMM, attention, and regression-gate
  diagnostics.
- [`final_summary.md`](final_summary.md): tournament findings and rating
  movements.
- [`v5_rating_validation_comparison.csv`](v5_rating_validation_comparison.csv):
  old-versus-new ratings.
- [`v5_figures/`](v5_figures/): global, France, goalkeeper, and coefficient
  plots.
- [`v5_artifact_manifest.json`](v5_artifact_manifest.json): generated-file
  hashes.

## Active model state

The active player layer is `attention`. Its causal, match-disjoint challenger
passed both retrospective and prospective gates; only out-of-fold attention
context enters the grouped ElasticNet valuation fit. The current-fold
prospective attention metrics are ROC-AUC 0.8815, PR-AUC 0.9750, ECE 0.0147,
and Brier score 0.0907. The legacy VAEP validation metrics are unchanged.

Outfield V5 ratings use 40% independently scaled offensive/defensive VAEP
evidence, 15% VAEP/touch, 15% xT/90, 15% grouped-ElasticNet role-adjusted
value, 10% top-three quality-adjusted completeness, and 5%
coverage-qualified off-ball contribution, followed by broad-position minutes
shrinkage. Goalkeepers are excluded from global outfield rank and evaluated
only through goalkeeper-specific evidence.
