# Reports - Rankings

Dictionary for locating and interpreting the active player, goalkeeper, position, role, and team rankings.

## Active ranking files

| Ranking resource | Location | Use |
|---|---|---|
| Complete ranking table | [`results/reports/ranking/player_rankings.csv`](../reports/ranking/player_rankings.csv) | Spreadsheet/dataframe source; 593 data rows × 398 columns. |
| Global outfield ranking | [`results/reports/ranking/global_rankings_outfield.csv`](../reports/ranking/global_rankings_outfield.csv) | All eligible outfield players ordered by `global_rank_v2`. |
| Primary 300+-minute ranking | [`results/reports/ranking/global_rankings_outfield_300min.csv`](../reports/ranking/global_rankings_outfield_300min.csv) | Filters exclusively on Qatar 2022 `minutes_played >= 300`. |
| Goalkeeper ranking | [`results/reports/ranking/goalkeeper_rankings.csv`](../reports/ranking/goalkeeper_rankings.csv) | Separate non-comparable rating for exactly one team-main goalkeeper per nation. |
| Complete ranking JSON | [`results/reports/ranking/player_rankings.json`](../reports/ranking/player_rankings.json) | Same records for applications and APIs. |
| Ranking methodology | [`results/reports/ranking/ranking_methodology.md`](../reports/ranking/ranking_methodology.md) | Position-aware weights, normalization, sample treatment, and role logic. |
| Ranking audit | [`results/reports/ranking/ranking_audit.md`](../reports/ranking/ranking_audit.md) | Before/after comparisons and eyes-test results. |
| Human-readable leaders | [`results/reports/canonical/final_summary.md`](../reports/canonical/final_summary.md) | Overall, position-group, movement, team, and top-five summaries. |
| Coach-facing leaders | [`results/reports/canonical/coaches_notebook.md`](../reports/canonical/coaches_notebook.md) | Pressing, networks, line breaking, spatial advantages, and goalkeeper leaders. |

## Ranking-field dictionary

| Field | Meaning |
|---|---|
| `position_group_360` | Formal tournament-usage group: GK, CB, FB, DM, CM, AM, or FW. |
| `global_rank_v2` | Position-aware global outfield rank; goalkeepers are blank. |
| `gk_rank_v2` | Rank among the 32 team-main goalkeepers; backups are blank. |
| `is_main_goalkeeper` | `true` only for the goalkeeper with the most Qatar 2022 minutes on that team. |
| `position_rank_v2` | Rank within `position_group_360`. |
| `role_rank_v2` | Rank within the coherent functional role. |
| `team_rank_v2` | Outfield rank within the 2022 national team. |
| `final_player_rating_v2` / `gk_rating_v2` | Separate 0–1 outfield and goalkeeper tournament scores. |
| `global_rank` | Global outfield rank. In the 300+ file this is recalculated only among eligible outfield players; goalkeepers are blank. |
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

`results/MIscellaneous/` contains coaching, recommendation, transition, and xG model leaderboards. These evaluate auxiliary models and are not the active player ranking. Use the active CSV above for player ordering.

To find any ranking-related filename, filter [`file_dictionary.csv`](file_dictionary.csv) for `rank` or `leaderboard`.
