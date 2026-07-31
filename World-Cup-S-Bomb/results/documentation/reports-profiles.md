# Reports - Profiles

Dictionary for locating player profiles, starter reports, heatmaps, and team reports. Active profiles use the Qatar 2022 v3 contract: Tournament Impact, Role Quality, and Uncertainty are separate products. Collections are described by pattern rather than by one summary per file.

## Profile locations

| What you want | Location/pattern | Count | Format | What it contains |
|---|---|---:|---|---|
| Player profile | `results/reports/player_profiles/<player-slug>-<player-id>.md` | 593 | Markdown | Tournament Impact v3 and global/team ranks; Role Quality v3 and role/position ranks; match-bootstrap interval/status; corrected periods 1–4 outcomes; active components; and clearly separated compatibility fields. |
| Player heatmap | `results/reports/visuals/heatmaps/<player-slug>-<player-id>.svg` | 593 | SVG | Spatial density of the player’s recorded event locations. |
| Starter report | `results/reports/starters/<TEAM>/<player-id>_starter_report.md` | 593 | Markdown | Human-readable v3 impact, role-quality, outcome, component, and uncertainty report organized by team. |
| Starter data | `results/reports/starters/<TEAM>/<player-id>_starter_report.json` | 593 | JSON | Structured v3 version of the same starter report. |
| Team profile | `results/reports/team_profiles/<team-name>.md` | 64 | Markdown | Team context plus active v3 player leaders, with regulation/extra-time outcomes separated from shootouts. |
| Team coaching report | `results/reports/teams/<TEAM>_team_coaching_report.md` | 32 | Markdown | Full coach-facing tactical report with active Tournament Impact, Role Quality, and Uncertainty fields. |
| Team coaching data | `results/reports/teams/<TEAM>_team_coaching_report.json` | 32 | JSON | Structured coaching-report content for downstream use. |
| Tournament player/team summary | `results/reports/canonical/final_summary.md` | 1 | Markdown | General player summary, all-team overview, and each team’s top five players. |
| Formatted final report | `results/reports/docs/final_summary.docx` | 1 | Word | Office-document edition of the final report. |

Only Qatar 2022 periods 1–4 contribute to ordinary outfield profile outcomes. Period-five conversions appear only in explicitly named shootout fields. For goalkeepers, the dedicated ranking contains one main goalkeeper per team; any `percentile_equivalent_placement` is a publication fallback, not measured absolute cross-position value.

## Team-code dictionary

`<TEAM>` is one of: `ARG`, `AUS`, `BEL`, `BRA`, `CAN`, `CMR`, `CRC`, `CRO`, `DEN`, `ECU`, `ENG`, `ESP`, `FRA`, `GER`, `GHA`, `IRN`, `JPN`, `KOR`, `KSA`, `MAR`, `MEX`, `NED`, `POL`, `POR`, `QAT`, `SEN`, `SRB`, `SUI`, `TUN`, `URU`, `USA`, `WAL`.

## Finding a person

1. Search `results/reports/player_profiles/` by surname or StatsBomb player ID.
2. Use the same slug/ID in `results/reports/visuals/heatmaps/` for the spatial view.
3. For JSON, locate the player ID under `results/reports/starters/<TEAM>/`.
4. If the filename is uncertain, search [`file_dictionary.csv`](file_dictionary.csv) by `filename` or `path`.

Example: Christian Pulisic’s profile is [`reports/player_profiles/christian-pulisic-8246.md`](../reports/player_profiles/christian-pulisic-8246.md).
