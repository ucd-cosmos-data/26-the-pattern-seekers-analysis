# Qatar 2022 Ranking Methodology

This model evaluates players based solely on their performances at the 2022 FIFA World Cup. Club form, career reputation, and other competitions are excluded.

No external ranking is an input to the score. If external analysis is consulted for an eyes test, it must refer specifically to the 2022 FIFA World Cup and remains audit-only; it cannot alter a player’s features or points.

## Position and role context

`position_group_360` uses `GK`, `CB`, `FB`, `DM`, `CM`, `AM`, and `FW`. The source position and functional role are retained in `functional_role_original`; only hard contradictions are repaired for reporting. Role labels do not award points by themselves.

## Outfield score

Each component is an average of tournament feature percentiles. Rate, progression, possession, defense, and off-ball metrics are normalized within `position_group_360`. Goals, xG, xA, VAEP volume, and xT volume form a common tournament-impact bridge so the global ordering is not merely six unrelated positional leaderboards.

| Group | Finishing | Creation | Progression | Possession | Defending | Off-ball | Common impact |
|---|---:|---:|---:|---:|---:|---:|---:|
| FW | 0.47 | 0.17 | 0.06 | 0.04 | 0.04 | 0.10 | 0.12 |
| AM | 0.25 | 0.28 | 0.14 | 0.08 | 0.05 | 0.08 | 0.12 |
| CM | 0.10 | 0.25 | 0.23 | 0.15 | 0.13 | 0.07 | 0.07 |
| DM | 0.05 | 0.13 | 0.22 | 0.18 | 0.28 | 0.10 | 0.04 |
| FB | 0.08 | 0.18 | 0.20 | 0.12 | 0.25 | 0.10 | 0.07 |
| CB | 0.03 | 0.05 | 0.17 | 0.18 | 0.37 | 0.15 | 0.05 |

For goal-centric forward roles, only finishing above the 70th percentile receives a smooth boost, capped at 0.06. This is a role-and-output rule and never checks player identity.

The raw score is shrunk toward its positional mean using `minutes / (minutes + 180)`, then robustly rescaled to 0–1. `minutes_played` is a documented alias of the project’s Qatar 2022 `minutes` field.

## Goalkeepers

Goalkeepers use a separate, non-comparable scale. Penalty-save volume is retained because knockout shootouts are meaningful tournament evidence; shot stopping, high-leverage saves, cross control, sweeping, distribution, and sample reliability remain part of the score.

Only one goalkeeper per team is ranked: the goalkeeper with the most Qatar 2022 minutes. Ties are resolved by actions, then player ID and name. Backups remain in the complete dataset with `is_main_goalkeeper = false`, no goalkeeper score, and no rank.

Each available goalkeeper input is converted to a percentile within the 32-main-goalkeeper cohort. Missing-input weights are renormalized, then the weighted score is shrunk toward the cohort mean using feature coverage and `minutes / (minutes + 180)` before the final 0–1 rescale.

| Goalkeeper score part | Source field | Weight |
|---|---|---:|
| Goals prevented per 90 | `goals_prevented_proxy_p90` | 18% |
| Save rate | `save_rate` | 10% |
| High-leverage save rate | `high_leverage_save_pct` | 7% |
| Penalties saved | `penalties_saved` | 32% |
| Reliability-shrunk penalty save rate | `penalty_save_rate_shrunk` | 10% |
| Cross stopping | `cross_stopping_rate` | 6% |
| Sweeper actions per 90 | `sweeper_actions_p90` | 4% |
| Distribution under pressure | `distribution_under_pressure` | 4% |
| Claims per 90 | `claims_p90` | 3% |
| Tournament minutes | `minutes` | 6% |

## Ranking fields

- `global_rank_v2`: all eligible outfield players.
- `position_rank_v2`: outfield players within the formal group.
- `role_rank_v2`: outfield players within the coherent role.
- `team_rank_v2`: outfield players within the national team.
- `gk_rank_v2`: the 32 team-main goalkeepers only.

The 300-minute file filters on Qatar 2022 minutes and preserves the all-player `global_rank_v2`, allowing direct comparison with the unfiltered table.
