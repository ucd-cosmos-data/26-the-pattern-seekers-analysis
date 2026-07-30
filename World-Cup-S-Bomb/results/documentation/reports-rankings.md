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
| Complete ranking table | [`results/reports/ranking/player_rankings.csv`](../reports/ranking/player_rankings.csv) | Spreadsheet/dataframe source; 593 data rows × 539 columns. |
| Explicit v3 ranking table | [`results/reports/ranking/player_rankings_v3.csv`](../reports/ranking/player_rankings_v3.csv) | Versioned byte-identical source for the active table. |
| Unified tournament ranking | [`results/reports/ranking/unified_tournament_rankings.csv`](../reports/ranking/unified_tournament_rankings.csv) | Exact six-field v3 publication view. It includes all eligible outfield players and one team-main goalkeeper per team; backup goalkeepers remain unranked. |
| Complete feature-rich team tables | [`results/reports/ranking/by_team/`](../reports/ranking/by_team/) | One active v3 table per team, ordered by `team_rank_v3`/publication `Team Rank`. |
| Complete unified team tables | [`results/reports/ranking/by_team_unified/`](../reports/ranking/by_team_unified/) | One exact six-field v3 CSV per team, ordered by publication `Team Rank`. |
| Global outfield ranking | [`results/reports/ranking/global_rankings_outfield.csv`](../reports/ranking/global_rankings_outfield.csv) | Every eligible outfield player ordered by `global_rank_v3`, including players below 300 minutes. |
| Primary 300+-minute ranking | [`results/reports/ranking/global_rankings_outfield_300min.csv`](../reports/ranking/global_rankings_outfield_300min.csv) | Filters exclusively on Qatar 2022 `minutes_played >= 300`. |
| Goalkeeper ranking | [`results/reports/ranking/goalkeeper_rankings.csv`](../reports/ranking/goalkeeper_rankings.csv) | Dedicated v3 rating for exactly one team-main goalkeeper per nation, with continuous play, regular penalties, bounded shootouts, and uncertainty separated. |
| Unified goalkeeper view | [`results/reports/ranking/goalkeeper_rankings_unified.csv`](../reports/ranking/goalkeeper_rankings_unified.csv) | The same 32-player dedicated GK order with publication placement fields appended. Any cross-position fallback is percentile-equivalent only. |
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
| `continuous_goalkeeper_rating_v3` | Dedicated periods 1–4 goalkeeper rating from continuous shot stopping, high-leverage stopping, cross/claim control, sweeping, distribution under pressure, and regular-penalty performance. |
| `shootout_component_v3` | Separate period-five contribution capped at 10% of the dedicated goalkeeper score; there is no per-save additive `0.20`. |
| `dedicated_goalkeeper_score_v3` / `goalkeeper_rank_v3` | Dedicated goalkeeper score and order for the 32 team-main keepers. |
| `percentile_equivalent_placement` | Explicit fallback publication bridge based on dedicated GK cohort rank. It is not measured absolute value and must not be interpreted as common-unit contribution. |
| `Global Rank` / `Team Rank` | Six-field publication aliases of the selected v3 ranking/placement fields. |
| `Tournament Performance Score` | Six-field order-preserving v3 publication score. Consult the feature-rich table for common-unit impact, role quality, uncertainty, and goalkeeper boundaries. |
| `global_rank_v2`, `team_rank_v2`, `position_rank_v2`, `role_rank_v2`, `final_player_rating_v2`, `gk_rating_v2` | Clearly labelled legacy comparison fields only; they are not active v3 scores or ranks. |

## Active v3 figures

The sole active ranking-figure family is [`results/reports/v3_figures/`](../reports/v3_figures/). It contains global and 300+ outfield order, the dedicated goalkeeper order, a representative team view, champion-versus-challenger movement, position composition, model coefficients/importance, and rank stability diagnostics. Existing files under `reports/v5_figures/` are historical/compatibility evidence, not current figures.

## Compatibility aliases and historical outputs

`player_rankings.csv` and `player_rankings_v3.csv` are the active feature-rich table. After v3 promotion, `player_rankings_v2.csv`, `v5_player_rankings.csv`, and `v5_player_rankings.json` are byte-identical compatibility aliases of the corresponding active table; their filenames do not mean the retired v2/V5 formulas remain active. Original pre-v3 tables are preserved under `results/reports/ranking/legacy/`.

Retired methodology may appear only in that explicitly historical material. The active score does not use the old within-position z-score as absolute global value, repeated 450/180/90-minute exposure penalties, the one-sided defensive publication lift, an unbounded `0.20` per shootout save, or a Blom bridge described as measured absolute performance.

## Other leaderboards

`results/MIscellaneous/` contains coaching, recommendation, transition, and xG model leaderboards. These evaluate auxiliary models and are not the active player ranking. Use the active CSV above for player ordering.

To find any ranking-related filename, filter [`file_dictionary.csv`](file_dictionary.csv) for `rank` or `leaderboard`.
