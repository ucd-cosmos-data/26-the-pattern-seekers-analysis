# Canonical V5 Reports

These are the current role-aware player analytics outputs. They supersede V4
player-rating values embedded in historical simulation packets; possession,
transition-risk, and tactical-scenario results remain valid for their original
targets.

## Current player hierarchy

| Global rank | Player | Team | Functional role | Final rating |
|---:|---|---|---|---:|
| 1 | Lionel Andrés Messi Cuccittini | Argentina | Progressive Winger | 0.8479 |
| 2 | Kylian Mbappé Lottin | France | Progressive Winger | 0.8086 |
| 3 | Christian Pulisic | United States | Progressive Winger | 0.8081 |
| 4 | Raphael Dias Belloli | Brazil | Progressive Winger | 0.8012 |
| 5 | Antoine Griezmann | France | Hybrid Playmaker / Roaming Creator | 0.8001 |

## Report index

- [`player_rankings.csv`](player_rankings.csv) and
  [`player_rankings.json`](player_rankings.json): canonical global, position,
  role, and team rankings.
- [`player_profiles/`](player_profiles/): 142 coverage-qualified individual
  reports.
- [`team_profiles/`](team_profiles/): 32 current team summaries.
- [`coaches_notebook.md`](coaches_notebook.md): passing, pressing, spatial,
  and line-breaking leaders.
- [`model_summary.md`](model_summary.md) and
  [`model_summary.json`](model_summary.json): VAEP metrics, GMM stability,
  attention-gate results, feature importance, and provenance.
- [`final_summary.md`](final_summary.md): tournament findings and rating
  movements.
- [`rating_validation_comparison.csv`](rating_validation_comparison.csv):
  old-versus-new ratings.
- [`artifact_manifest.json`](artifact_manifest.json): generated-file hashes.

## Active model state

The active player layer is `role_aware_fallback`. The lightweight attention
challenger remains implemented but failed its match-disjoint discrimination
gate and does not affect final ratings. The selected probabilistic role model
uses 13 components with tied covariance. New and legacy rankings have Spearman
correlation 0.9848.

V5 ratings use 40% VAEP/90, 15% VAEP/touch, 15% xT/90, 15% continuous
role-adjusted value, 10% completeness, and 5% coverage-qualified off-ball
contribution, followed by broad-position minutes shrinkage.
