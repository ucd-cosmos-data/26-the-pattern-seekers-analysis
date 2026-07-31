# Reports - Rankings

Dictionary for locating and interpreting the active Qatar 2022 `ranking-repair-v3.0-qatar-2022` player and goalkeeper release.

## Active score contract

- **Tournament Impact v3** is signed total contribution in common action-value units. It determines global and team order without within-position z-scoring or a position-dependent publication lift.
- **Role Quality v3** is one empirical-Bayes posterior contribution rate interpreted through probabilistic roles. It determines position and role order; it does not manufacture global value.
- **Uncertainty** is a whole-match bootstrap score/rank interval and status. It describes tournament-sample precision and is never another minutes or exposure penalty.

Ordinary outfield evidence uses only Qatar 2022 periods 1–4. Period 5 is shootout-only and is excluded at feature construction from goals, assists, xG, xA, xT, VAEP, and Tournament Impact.

## Active ranking files

| Ranking resource | Location | Use |
|---|---|---|
| Complete player master table | [`results/reports/ranking/player_rankings.csv`](../reports/ranking/player_rankings.csv) | Feature/profile source for all eligible players; 593 data rows × 625 columns. It is not the cross-position leaderboard. |
| Unified tournament ranking | [`results/reports/ranking/unified_tournament_rankings.csv`](../reports/ranking/unified_tournament_rankings.csv) | Exact six-field outfield-only publication view. |
| Complete feature-rich team tables | [`results/reports/ranking/by_team/`](../reports/ranking/by_team/) | One active v3 table per team, ordered by `team_rank_v3`/publication `Team Rank`. |
| Complete unified team tables | [`results/reports/ranking/by_team_unified/`](../reports/ranking/by_team_unified/) | One exact six-field v3 CSV per team, ordered by publication `Team Rank`. |
| Global outfield ranking | [`results/reports/ranking/global_rankings_outfield.csv`](../reports/ranking/global_rankings_outfield.csv) | Every eligible outfield player ordered by `global_rank_v3`, including players below 300 minutes. |
| Primary 300+-minute outfield ranking | [`results/reports/ranking/player_rankings_300plus.csv`](../reports/ranking/player_rankings_300plus.csv) | Outfield-only view filtered on Qatar 2022 `minutes_played >= 300`; JSON is also available. |
| Goalkeeper ranking | [`results/reports/ranking/goalkeeper_rankings.csv`](../reports/ranking/goalkeeper_rankings.csv) | Separate consolidated v5 order for all 32 eligible goalkeepers, with PSxG-style shot stopping, clutch/state leverage, penalties, shootouts, support play, exposure/reliability, and uncertainty. JSON and Markdown editions contain the same current order. |
| Human-readable goalkeeper ranking | [`results/reports/ranking/goalkeeper_rankings.md`](../reports/ranking/goalkeeper_rankings.md) | All 32 goalkeepers in the same dedicated order, formatted for direct reading. |
| Complete ranking JSON | [`results/reports/ranking/player_rankings.json`](../reports/ranking/player_rankings.json) | Same records for applications and APIs. |
| Ranking methodology | [`results/reports/ranking/ranking_methodology.md`](../reports/ranking/ranking_methodology.md) | Active v3 event scope, common-unit impact, single empirical-Bayes rate treatment, bootstrap uncertainty, attack/defense selection, and goalkeeper boundary. |
| Ranking audit | [`results/reports/ranking/ranking_audit.md`](../reports/ranking/ranking_audit.md) | Champion/challenger gates, confidence intervals, stability, scorer/defender checks, and goalkeeper calibration/cap tests. |
| Human-readable leaders | [`results/reports/canonical/final_summary.md`](../reports/canonical/final_summary.md) | Tournament Impact, Role Quality, uncertainty, team, position/role, high-impact substitute, and dedicated goalkeeper leaders. |
| Coach-facing leaders | [`results/reports/canonical/coaches_notebook.md`](../reports/canonical/coaches_notebook.md) | Pressing, networks, line breaking, spatial advantages, and goalkeeper leaders. |

## Ranking-field dictionary

| Field | Meaning |
|---|---|
| `position_group_360` | Formal tournament-usage group: GK, CB, FB, DM, CM, AM, or FW. |
| `tournament_impact_raw_v3` / `tournament_impact_v3` | Active signed common-unit total and its order-preserving publication value. Reporting position cannot change either. |
| `global_rank_v3` | Active global outfield rank from Tournament Impact v3. |
| `team_rank_v3` | Active within-team rank from Tournament Impact v3. |
| `role_quality_v3` | Single empirical-Bayes posterior contribution rate; uncertainty is not folded into it as an extra penalty. |
| `position_rank_v3` | Rank within `position_group_360` from Role Quality v3. |
| `role_rank_v3` | Rank within the functional/probabilistic role from Role Quality v3. |
| `uncertainty_low_v3` / `uncertainty_high_v3` | Whole-match bootstrap interval for Tournament Impact. |
| `bootstrap_rank_best_v3` / `bootstrap_rank_worst_v3` | Bootstrap rank-stability band. |
| `uncertainty_status_v3` | `stable`, `moderate`, or `wide` tournament-sample precision label; never a scoring input. |
| `ordinary_event_periods_v3` | Provenance field fixed to periods `1-4` for ordinary outfield performance. |
| `shootout_attempts` / `shootout_goals` | Separate period-five audit fields, excluded from ordinary outfield impact. |
| `is_main_goalkeeper` | `true` only for the goalkeeper with the most Qatar 2022 minutes on that team. |
| `psxg_shot_stopping_value_v5` | Reliability-adjusted PSxG-style ordinary-play shot-stopping value. |
| `clutch_save_value_v5` / `state_leverage_prevention_value_v5` | High-leverage and match-state prevention channels in the consolidated goalkeeper score. |
| `regular_penalty_impact_v5` / `shootout_win_probability_added_v5` | Separately estimated and reliability-controlled regular-penalty and shootout contributions. |
| `support_composite_v5` | Cross/claim, sweeping, and pressured-distribution support component. |
| `goalkeeper_consolidated_value_score_v5` / `goalkeeper_consolidated_value_rank_v5` | Current goalkeeper score and dedicated rank for the 32-player eligible cohort. |
| `goalkeeper_score_interval_low_v5` / `goalkeeper_score_interval_high_v5` | Goalkeeper score uncertainty interval; uncertainty does not change the point estimate. |
| `Global Rank` / `Team Rank` | Six-field publication aliases of the selected v3 ranking/placement fields. |
| `Tournament Performance Score` | Six-field order-preserving v3 publication score. Consult the feature-rich table for common-unit impact, role quality, uncertainty, and goalkeeper boundaries. |
| `global_rank_v2`, `team_rank_v2`, `position_rank_v2`, `role_rank_v2`, `final_player_rating_v2`, `gk_rating_v2` | Clearly labelled legacy comparison fields only; they are not active v3 scores or ranks. |

## Current ranking figures

[`results/reports/v3_figures/`](../reports/v3_figures/) contains the six current outfield ranking/validation figures. [`results/reports/v5_figures/goalkeeper_rankings_v5.png`](../reports/v5_figures/goalkeeper_rankings_v5.png) is the current consolidated goalkeeper figure.

## Canonical-file rule

Only the unversioned files listed above are published ranking artifacts. Versioned duplicates and obsolete ranking folders are removed during regeneration. Goalkeepers do not appear in either outfield leaderboard.

## Other leaderboards

`results/MIscellaneous/` contains coaching, recommendation, transition, and xG model leaderboards. These evaluate auxiliary models and are not the active player ranking. Use the active CSV above for player ordering.

To find any ranking-related filename, filter [`file_dictionary.csv`](file_dictionary.csv) for `rank` or `leaderboard`.
