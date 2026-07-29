# Reports - Profiles

Dictionary for locating player profiles, starter reports, heatmaps, and team reports. Collections are described by pattern rather than by one summary per file.

## Profile locations

| What you want | Location/pattern | Count | Format | What it contains |
|---|---|---:|---|---|
| Player profile | `results/reports/player_profiles/<player-slug>-<player-id>.md` | 593 | Markdown | Identity, team, position, functional/probabilistic role, rating components, evidence coverage, and interpretation. |
| Player heatmap | `results/reports/visuals/heatmaps/<player-slug>-<player-id>.svg` | 593 | SVG | Spatial density of the player’s recorded event locations. |
| Starter report | `results/reports/starters/<TEAM>/<player-id>_starter_report.md` | 0 | Markdown | Human-readable player match/role report organized by team. |
| Starter data | `results/reports/starters/<TEAM>/<player-id>_starter_report.json` | 0 | JSON | Structured version of the same starter report. |
| Team profile | `results/reports/team_profiles/<team-name>.md` | 32 | Markdown | Threat creation, compactness, pressure resistance, and squad ratings. |
| Team coaching report | `results/reports/teams/<TEAM>_team_coaching_report.md` | 32 | Markdown | Full coach-facing tactical and player report. |
| Team coaching data | `results/reports/teams/<TEAM>_team_coaching_report.json` | 32 | JSON | Structured coaching-report content for downstream use. |
| Tournament player/team summary | `results/reports/canonical/final_summary.md` | 1 | Markdown | General player summary, all-team overview, and each team’s top five players. |
| Formatted final report | `results/reports/docs/final_summary.docx` | 1 | Word | Office-document edition of the final report. |

## Team-code dictionary

`<TEAM>` is one of: `ARG`, `AUS`, `BEL`, `BRA`, `CAN`, `CMR`, `CRC`, `CRO`, `DEN`, `ECU`, `ENG`, `ESP`, `FRA`, `GER`, `GHA`, `IRN`, `JPN`, `KOR`, `KSA`, `MAR`, `MEX`, `NED`, `POL`, `POR`, `QAT`, `SEN`, `SRB`, `SUI`, `TUN`, `URU`, `USA`, `WAL`.

## Finding a person

1. Search `results/reports/player_profiles/` by surname or StatsBomb player ID.
2. Use the same slug/ID in `results/reports/visuals/heatmaps/` for the spatial view.
3. For JSON, locate the player ID under `results/reports/starters/<TEAM>/`.
4. If the filename is uncertain, search [`file_dictionary.csv`](file_dictionary.csv) by `filename` or `path`.

Example: Christian Pulisic’s profile is [`reports/player_profiles/christian-pulisic-8246.md`](../reports/player_profiles/christian-pulisic-8246.md).
