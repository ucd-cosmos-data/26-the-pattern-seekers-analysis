# Reports - Rankings

Dictionary for locating and interpreting the active player, goalkeeper, position, role, and team rankings.

## Canonical ranking files

| Ranking resource | Location | Use |
|---|---|---|
| Complete ranking table | [`results/reports/canonical/player_rankings.csv`](../reports/canonical/player_rankings.csv) | Spreadsheet/dataframe source; 593 data rows × 373 columns. |
| Complete ranking JSON | [`results/reports/canonical/player_rankings.json`](../reports/canonical/player_rankings.json) | Same records for applications and APIs. |
| Human-readable leaders | [`results/reports/canonical/final_summary.md`](../reports/canonical/final_summary.md) | Overall, position-group, movement, team, and top-five summaries. |
| Coach-facing leaders | [`results/reports/canonical/coaches_notebook.md`](../reports/canonical/coaches_notebook.md) | Pressing, networks, line breaking, spatial advantages, and goalkeeper leaders. |

## Ranking-field dictionary

| Field | Meaning |
|---|---|
| `global_rank` | Global outfield rank. Goalkeepers are intentionally blank. |
| `goalkeeper_rank` / `primary_goalkeeper_rank` | Separate goalkeeper-only rank. |
| `position_rank` | Rank within the broad position group. |
| `role_rank` | Rank among players sharing the functional role. |
| `team_rank` | Rank within the player’s national team. |
| `final_player_rating` | Reliability-adjusted final score used for ordering. |
| `RankingStatus` | Outfield ranking eligibility/status explanation. |
| `GKRankingStatus` | Goalkeeper ranking eligibility/status explanation. |

## Ranking figures

| Figure | Location |
|---|---|
| Global outfield ranking | [`v5_global_outfield_rankings.png`](../reports/v5_figures/v5_global_outfield_rankings.png) |
| Goalkeeper-only ranking | [`v5_goalkeeper_rankings.png`](../reports/v5_figures/v5_goalkeeper_rankings.png) |
| France squad ranking | [`v5_france_team_rankings.png`](../reports/v5_figures/v5_france_team_rankings.png) |
| Learned valuation coefficients | [`v5_elasticnet_coefficients.png`](../reports/v5_figures/v5_elasticnet_coefficients.png) |

## Other leaderboards

`results/MIscellaneous/` contains coaching, recommendation, transition, and xG model leaderboards. These evaluate auxiliary models and are not the canonical player ranking. Use the canonical CSV above for player ordering.

To find any ranking-related filename, filter [`file_dictionary.csv`](file_dictionary.csv) for `rank` or `leaderboard`.
