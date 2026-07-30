# Results dictionary

A compact directory of every result artifact family. Repeated player and team files are represented once by their filename pattern.

## Fast lookup

| If you need… | Go to |
|---|---|
| Active Tournament Impact v3 rankings | [`reports/ranking/player_rankings_v3.csv`](../reports/ranking/player_rankings_v3.csv) |
| Primary 300+-minute Tournament Impact view | [`reports/ranking/global_rankings_outfield_300min.csv`](../reports/ranking/global_rankings_outfield_300min.csv) |
| Full-cohort player table | [`reports/ranking/player_rankings.csv`](../reports/ranking/player_rankings.csv) |
| Searchable JSON rankings | [`reports/ranking/player_rankings.json`](../reports/ranking/player_rankings.json) |
| One player’s profile | [`reports/player_profiles/`](../reports/player_profiles/) |
| One player’s heatmap | [`reports/visuals/heatmaps/`](../reports/visuals/heatmaps/) |
| One team’s profile | [`reports/team_profiles/`](../reports/team_profiles/) |
| Full team coaching report | [`reports/teams/`](../reports/teams/) |
| Tournament final summary | [`reports/canonical/final_summary.md`](../reports/canonical/final_summary.md) |
| Model metrics and gate result | [`reports/canonical/model_summary.md`](../reports/canonical/model_summary.md) |
| Coach-facing tactical notes | [`reports/canonical/coaches_notebook.md`](../reports/canonical/coaches_notebook.md) |
| Validation evidence | [`diagnostics/`](../diagnostics/) and [`audit/`](../audit/) |
| Run provenance/configuration | [`metadata/`](../metadata/) |
| Tactical simulations | [`simulations/`](../simulations/) |
| Exact filename search | [`file_dictionary.csv`](file_dictionary.csv) |

## Complete artifact-family dictionary

| Artifact family | Path or filename pattern | Files | Information contained |
|---|---|---:|---|
| Top-level release metadata | `results/*` | 0 | Release-level cleanup and publication metadata. |
| Legacy summary alias | `results/Summary/*` | 1 | Compatibility alias of the active model summary. |
| Audit tables | `results/audit/*` | 6 | Observed-versus-expected and out-of-fold audit tables. |
| Model diagnostics | `results/diagnostics/*` | 20 | Validation metrics, calibration, importance, and cluster diagnostics. |
| Ranking-repair diagnostics | `results/diagnostics/ranking_repair/**/*` | 25 | Immutable champion evidence, event-scope checks, component gates, bootstrap intervals, stale-content classifications, and the final v3 release audit. |
| Publication figures | `results/figures/*` | 14 | Charts and the technical onboarding presentation. |
| Run metadata | `results/metadata/*` | 6 | Configuration, provenance, and feature-definition records. |
| Supporting/legacy outputs | `results/miscellaneous/*` | 49 | Exploratory summaries and noncanonical model leaderboards. |
| Reports directory guide | `results/reports/README.md` | 21 | Short guide to the report tree. |
| Canonical reports | `results/reports/canonical/*` | 5 | Current final summary, model summary, and coaches notebook. |
| Final-summary compatibility alias | `results/reports/final/*` | 1 | Compatibility alias of the active tournament final summary. |
| Tournament rankings | `results/reports/ranking/*` | 17 | Active Qatar 2022 v3 Tournament Impact, Role Quality, uncertainty, goalkeeper, audit, alias, and methodology artifacts. |
| Per-team tournament rankings | `results/reports/ranking/by_team/<TEAM>.csv` | 32 | Complete feature-rich active v3 ranking table for each of the 32 national teams. |
| Unified per-team tournament rankings | `results/reports/ranking/by_team_unified/<TEAM>.csv` | 32 | Exact six-field Tournament Impact v3 publication table for each of the 32 national teams. |
| Archived legacy rankings | `results/reports/ranking/legacy/*` | 3 | Pre-v3 tables retained only for before/after reproducibility. |
| Canonical report data | `results/reports/canonical/data/*` | 2 | Team metrics and defensive-disruption tables supporting reports. |
| Formatted final report | `results/reports/docs/final_summary.docx` | 1 | Word edition of the final tournament report. |
| Player profiles | `results/reports/player_profiles/<player-slug>-<player-id>.md` | 593 | One human-readable role and valuation profile per player. |
| Starter report pairs | `results/reports/starters/<TEAM>/<player-id>_starter_report.{md,json}` | 1,186 | Markdown and JSON player reports organized by national-team code. |
| Team coaching report pairs | `results/reports/teams/<TEAM>_team_coaching_report.{md,json}` | 64 | Human-readable and structured coaching reports for 32 teams. |
| Team profiles | `results/reports/team_profiles/<team-name>.md` | 32 | Concise threat, defensive, resistance, and squad-rating profiles. |
| Active v3 ranking figures | `results/reports/v3_figures/*` | 7 | Current ranking, goalkeeper, champion/challenger, position composition, model-evidence, and stability figures. |
| Legacy V5 figures | `results/reports/v5_figures/*` | 4 | Historical V5 ranking and ElasticNet figures retained for comparison; not active release figures. |
| Player heatmaps | `results/reports/visuals/heatmaps/<player-slug>-<player-id>.svg` | 593 | One scalable spatial-event heatmap per player. |
| Simulation outputs | `results/simulations/*` | 6 | Tactical-style, substitution, suppression, and out-of-fold simulations. |

**Coverage:** 2,720 of 2,720 result artifacts.

## Which version wins?

Use `results/reports/ranking/player_rankings.csv` or its explicit `player_rankings_v3.csv` version for active player rankings and `results/reports/canonical/` for active narrative summaries. `player_rankings_v2.csv`, `v5_player_rankings.csv`, and `v5_player_rankings.json` are compatibility aliases of that active v3 table. `reports/ranking/legacy/`, `reports/v5_figures/`, and `MIscellaneous/` may contain older or exploratory evidence and must not override canonical rankings or validation conclusions.

For a literal one-row-per-file lookup, filter `file_dictionary.csv` by `path`, `filename`, `folder`, or `information`. The JSON edition contains the same dictionary for programmatic use.
