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

Goalkeepers use a separate, non-comparable scale. The primary block is a StatsBomb Open Data PSxG-GA proxy per 90, supported by reliability-shrunk overall and high-leverage save rates. Penalty performance, cross control, sweeping, distribution under pressure, and minutes complete the rate matrix.

Only one goalkeeper per team is ranked: the goalkeeper with the most Qatar 2022 minutes. Ties are resolved by actions, then player ID and name. Backups remain in the complete dataset with `is_main_goalkeeper = false`, no goalkeeper score, and no rank.

Each available goalkeeper input is converted to a percentile within the 32-main-goalkeeper cohort. Missing-input weights are renormalized. Overall save rate is shrunk with eight prior shots, while high-leverage save rate uses three prior shots, reducing small-denominator volatility.

Tournament impact is objective and identity-free: each saved period-five shootout penalty contributes 0.20, the goalkeeper's within-cohort VAEP/90 percentile contributes up to 0.04, and the high-leverage-save volume percentile contributes up to 0.02. Regular-time penalties remain in the penalty-rate block; team advancement and player names are never inputs.

The composite score is shrunk toward the cohort mean using available-feature coverage and `minutes / (minutes + 180)` before the final 0–1 rescale.

| Goalkeeper score part | Source field | Weight |
|---|---|---:|
| PSxG-GA proxy per 90 | `psxg_ga_p90` | 34% |
| Reliability-shrunk save rate | `save_rate_shrunk` | 11% |
| Reliability-shrunk high-leverage save rate | `high_leverage_save_rate_shrunk` | 11% |
| Penalty save rate | `penalties_saved_rate` | 13% |
| Reliability-shrunk penalty save rate | `penalty_save_rate_shrunk` | 8% |
| Cross stopping | `cross_stopping_rate` | 5% |
| Claims per 90 | `claims_p90` | 3% |
| Sweeper actions per 90 | `sweeper_actions_p90` | 4% |
| Distribution under pressure | `distribution_under_pressure` | 5% |
| Tournament minutes | `minutes` | 6% |

### Analyst-practice references

- [StatsBomb: Intro to Goalkeeper Analysis](https://blogarchive.statsbomb.com/articles/soccer/intro-to-goalkeeper-analysis/) â€” goals saved above average and adjusted save percentage.
- [StatsBomb: Introducing Goalkeeper Radars](https://blogarchive.statsbomb.com/articles/soccer/introducing-goalkeeper-radars/) â€” claims, aggressive distance, and distribution style.
- [Hudl StatsBomb: Expected Goals Explained](https://statsbomb.com/soccer-metrics/expected-goals-xg-explained/) â€” post-shot xG for goalkeeper shot-stopping evaluation.
- [Opta Analyst: Expected Goals on Target](https://theanalyst.com/articles/what-are-expected-goals-on-target-xgot) â€” goalmouth placement and goals prevented interpretation.

## Ranking fields

- `global_rank_v2`: all eligible outfield players.
- `position_rank_v2`: outfield players within the formal group.
- `role_rank_v2`: outfield players within the coherent role.
- `team_rank_v2`: outfield players within the national team.
- `gk_rank_v2`: the 32 team-main goalkeepers only.

The 300-minute file filters on Qatar 2022 minutes and preserves the all-player `global_rank_v2`, allowing direct comparison with the unfiltered table.

## Leading goalkeeper evidence

These rows are generated from the scored table after ranking; player identity is not an input. They show why tournament-impact actions can complement, but do not rewrite, the continuous shot-stopping evidence. A negative PSxG-GA proxy remains visible rather than being replaced by a favorable value.

| Gk Rank V2 | Player Name | Psxg Ga P90 | Save Rate Shrunk | High Leverage Save Rate Shrunk | Penalties Saved Rate | Shootout Penalties Saved | Tournament Impact Score | Gk Rating V2 |
|---|---|---|---|---|---|---|---|---|
| 1 | Dominik Livaković | 0.9375 | 0.7527 | 0.1968 | 0.5000 | 4.0000 | 0.8259 | 1.0000 |
| 2 | Damián Emiliano Martínez | -0.0736 | 0.5407 | 0.1935 | 0.3000 | 3.0000 | 0.6438 | 0.5971 |
| 3 | Yassine Bounou | 0.2171 | 0.6503 | 0.3935 | 1.0000 | 2.0000 | 0.4297 | 0.5876 |
