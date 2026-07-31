# Defensive Analysis File Manifest

Project root:

`/Users/hirenmandalia/Desktop/cosmos/26-the-pattern-seekers-analysis/World-Cup-S-Bomb`

## Reproducible scripts

- `scripts/cache_360_frames.py` — downloads and caches StatsBomb 360 freeze frames.
- `scripts/build_defensive_features.py` — converts freeze frames into possession-level defensive shape features and named defensive-actor profiles.
- `scripts/cluster_defensive_styles.py` — fits and evaluates the possession-level defensive-style clustering model.
- `scripts/analyze_defensive_matchups.py` — evaluates attack-versus-defense cells, team profiles, and named player roles.

## Cached and derived data

- `data/interim/frames360/raw/<match_id>.json.gz` — one compressed raw 360 payload per match (64 files).
- `data/interim/world_cup_360_frames.csv` — flattened player locations from all freeze frames.
- `data/interim/world_cup_360_visible_areas.csv` — visible-area polygons by event.
- `data/interim/world_cup_360_frame_metrics.csv` — spatial defensive metrics by event frame.
- `data/processed/world_cup_defensive_features.csv` — one defensive feature row per possession.
- `data/processed/world_cup_defensive_clusters.csv` — possession features plus defensive-style assignments.
- `data/processed/world_cup_defensive_players.csv` — named defensive-event actor profiles before role clustering.

These large data files are intentionally excluded by the repository `.gitignore` and are reproducible from the scripts.

## Models

- `models/defensive_style_kmeans.joblib` — fitted KMeans pipeline, feature list, clipping bounds, label map, and model metadata.

The model directory is intentionally excluded by `.gitignore`.

## Tabular and written results

- `results/defensive_feature_validation.md` — freeze-frame coverage and feature integrity checks.
- `results/defensive_style_model_selection.csv` — K=3 through K=8 model-selection diagnostics.
- `results/defensive_style_profiles.csv` — cluster centroids, outcomes, and interpreted labels.
- `results/defensive_style_summary.md` — tournament defensive-style summary.
- `results/style_matchup_effectiveness.csv` — all 12 attacking-style × defensive-style outcome cells.
- `results/team_defensive_style_profiles.csv` — defensive-style shares for all 32 teams.
- `results/defensive_player_roles.csv` — 662 named defensive players with role assignments where sample size is sufficient.
- `results/defensive_matchup_summary.md` — matchup and player-role headline findings.

## Figures

- `results/figures/defensive_style_fingerprints.png` — standardized feature fingerprints for the four defensive styles.
- `results/figures/attacking_defensive_matchups.png` — attack-versus-defense xG heatmap with sample sizes.

Figures are intentionally excluded by `.gitignore`.

## Validation snapshot

- 64 matches and 32 teams covered.
- 203,882 cached event frames; 203,495 produced spatial metrics.
- 11,016 possession rows; possession IDs are unique.
- 10,590 possessions have spatial frames (96.13%).
- 9,690 possessions met defensive-clustering eligibility thresholds.
- Four defensive styles selected; silhouette 0.1907 and stability ARI 0.9980.
- 662 named defensive players profiled; 412 met player-role sample thresholds.
- No shot, goal, xG, or other attacking outcome is used as a defensive clustering input.
- The 34 frame-metric rows without a defending-team label are penalty-shootout frames (period 5) outside the possession model. Every modeled defensive-style row has a defending team.

## Interpretation limits

- Freeze frames are event snapshots with partial visible areas, not continuous tracking data.
- Public 360 off-ball players are anonymous; named player roles therefore describe defensive-event actors, while anonymous locations describe team shape.
- Player action counts have not yet been normalized per 90 minutes.
- Matchup results are observational tournament associations, not causal coaching recommendations.
