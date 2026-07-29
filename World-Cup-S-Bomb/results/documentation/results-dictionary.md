# Results dictionary

A compact directory of every result artifact family. Repeated player and team files are represented once by their filename pattern.

## Fast lookup

| If you need… | Go to |
|---|---|
| Primary 300+-minute rankings | [`reports/canonical/player_rankings_300plus.csv`](../reports/canonical/player_rankings_300plus.csv) |
| Full-cohort player table | [`reports/canonical/player_rankings.csv`](../reports/canonical/player_rankings.csv) |
| Searchable JSON rankings | [`reports/canonical/player_rankings.json`](../reports/canonical/player_rankings.json) |
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
| Audit tables | `results/audit/*` | 6 | Observed-versus-expected and out-of-fold audit tables. |
| Model diagnostics | `results/diagnostics/*` | 17 | Validation metrics, calibration, importance, and cluster diagnostics. |
| Publication figures | `results/figures/*` | 14 | Charts and the technical onboarding presentation. |
| Run metadata | `results/metadata/*` | 5 | Configuration, provenance, and feature-definition records. |
| Supporting/legacy outputs | `results/MIscellaneous/*` | 49 | Exploratory summaries and noncanonical model leaderboards. |
| Reports directory guide | `results/reports/README.md` | 1 | Short guide to the report tree. |
| Canonical reports | `results/reports/canonical/*` | 7 | Current rankings, final summary, model summary, and coaches notebook. |
| Canonical report data | `results/reports/canonical/data/*` | 2 | Team metrics and defensive-disruption tables supporting reports. |
| Formatted final report | `results/reports/docs/final_summary.docx` | 1 | Word edition of the final tournament report. |
| Player profiles | `results/reports/player_profiles/<player-slug>-<player-id>.md` | 593 | One human-readable role and valuation profile per player. |
| Starter report pairs | `results/reports/starters/<TEAM>/<player-id>_starter_report.{md,json}` | 1,186 | Markdown and JSON player reports organized by national-team code. |
| Team coaching report pairs | `results/reports/teams/<TEAM>_team_coaching_report.{md,json}` | 64 | Human-readable and structured coaching reports for 32 teams. |
| Team profiles | `results/reports/team_profiles/<team-name>.md` | 32 | Concise threat, defensive, resistance, and squad-rating profiles. |
| Report figures | `results/reports/v5_figures/*` | 4 | Current ranking and ElasticNet coefficient figures. |
| Player heatmaps | `results/reports/visuals/heatmaps/<player-slug>-<player-id>.svg` | 593 | One scalable spatial-event heatmap per player. |
| Simulation outputs | `results/simulations/*` | 6 | Tactical-style, substitution, suppression, and out-of-fold simulations. |

**Coverage:** 2,580 of 2,580 result artifacts.

## Which version wins?

Use `results/reports/canonical/` for active published values. `MIscellaneous/` may contain older or exploratory leaderboards and must not override canonical rankings or validation conclusions.

For a literal one-row-per-file lookup, filter `file_dictionary.csv` by `path`, `filename`, `folder`, or `information`. The JSON edition contains the same dictionary for programmatic use.
