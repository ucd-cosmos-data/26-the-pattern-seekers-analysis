# Results dictionary

A compact directory of every result artifact family. Repeated player and team files are represented once by their filename pattern.

## Fast lookup

| If you need… | Go to |
|---|---|
| Global outfield rankings | [`reports/ranking/global_rankings_outfield.csv`](../reports/ranking/global_rankings_outfield.csv) |
| Primary 300+-minute outfield view | [`reports/ranking/player_rankings_300plus.csv`](../reports/ranking/player_rankings_300plus.csv) |
| Separate goalkeeper rankings | [`reports/ranking/goalkeeper_rankings.md`](../reports/ranking/goalkeeper_rankings.md) |
| Full-cohort feature/profile master table | [`reports/ranking/player_rankings.csv`](../reports/ranking/player_rankings.csv) |
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
| Legacy summary alias | `results/Summary/*` | 2 | Compatibility alias of the active model summary. |
| Audit tables | `results/audit/*` | 6 | Observed-versus-expected and out-of-fold audit tables. |
| Model diagnostics | `results/diagnostics/*` | 20 | Validation metrics, calibration, importance, and cluster diagnostics. |
| Ranking-repair diagnostics | `results/diagnostics/ranking_repair/**/*` | 59 | Immutable champion evidence, event-scope checks, component gates, bootstrap intervals, stale-content classifications, and the final v3 release audit. |
| Publication figures | `results/figures/*` | 14 | Charts and the technical onboarding presentation. |
| Run metadata | `results/metadata/*` | 6 | Configuration, provenance, and feature-definition records. |
| Supporting/legacy outputs | `results/miscellaneous/*` | 49 | Exploratory summaries and noncanonical model leaderboards. |
| Reports directory guide | `results/reports/README.md` | 13 | Short guide to the report tree. |
| Canonical reports | `results/reports/canonical/*` | 5 | Current final summary, model summary, and coaches notebook. |
| Final-summary compatibility alias | `results/reports/final/*` | 1 | Compatibility alias of the active tournament final summary. |
| Tournament rankings | `results/reports/ranking/*` | 13 | Active Qatar 2022 v3 Tournament Impact, Role Quality, uncertainty, separate consolidated goalkeeper, audit, and methodology artifacts. |
| Per-team tournament rankings | `results/reports/ranking/by_team/<TEAM>.csv` | 32 | Complete feature-rich active v3 ranking table for each of the 32 national teams. |
| Unified per-team tournament rankings | `results/reports/ranking/by_team_unified/<TEAM>.csv` | 32 | Exact six-field Tournament Impact v3 publication table for each of the 32 national teams. |
| Canonical report data | `results/reports/canonical/data/*` | 2 | Team metrics and defensive-disruption tables supporting reports. |
| Formatted final report | `results/reports/docs/final_summary.docx` | 1 | Word edition of the final tournament report. |
| Player profiles | `results/reports/player_profiles/<player-slug>-<player-id>.md` | 593 | One human-readable role and valuation profile per player. |
| Starter report pairs | `results/reports/starters/<TEAM>/<player-id>_starter_report.{md,json}` | 1,186 | Markdown and JSON player reports organized by national-team code. |
| Team coaching report pairs | `results/reports/teams/<TEAM>_team_coaching_report.{md,json}` | 64 | Human-readable and structured coaching reports for 32 teams. |
| Team profiles | `results/reports/team_profiles/<team-name>.md` | 64 | Concise threat, defensive, resistance, and squad-rating profiles. |
| Current outfield ranking figures | `results/reports/v3_figures/*` | 6 | Current outfield ranking, champion/challenger, position composition, model-evidence, and stability figures. |
| Current consolidated goalkeeper figure | `results/reports/v5_figures/*` | 1 | Current consolidated v5 goalkeeper ranking figure. |
| Player heatmaps | `results/reports/visuals/heatmaps/<player-slug>-<player-id>.svg` | 593 | One scalable spatial-event heatmap per player. |
| Simulation outputs | `results/simulations/*` | 6 | Tactical-style, substitution, suppression, and out-of-fold simulations. |

**Coverage:** 2,768 of 2,768 result artifacts.

## Which version wins?

Use `global_rankings_outfield.csv` or `player_rankings_300plus.csv` for outfield order, `goalkeeper_rankings.csv` for goalkeeper order, and `player_rankings.csv` as the complete feature/profile master table. Use `results/reports/canonical/` for active narrative summaries. `MIscellaneous/` contains auxiliary model evidence and must not override canonical rankings or validation conclusions.

For a literal one-row-per-file lookup, filter `file_dictionary.csv` by `path`, `filename`, `folder`, or `information`. The JSON edition contains the same dictionary for programmatic use.
