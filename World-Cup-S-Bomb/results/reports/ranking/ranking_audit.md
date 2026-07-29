# Qatar 2022 Ranking Audit

- Overall status: `PASS`
- Scope: 2022 FIFA World Cup tournament data only
- External rankings in score: none
- External analysis policy: Qatar 2022-specific and audit-only

## Eyes-test checks

- [x] `ranking_input_scope_2022_world_cup_only`
- [x] `one_ranked_main_goalkeeper_per_team`
- [x] `backup_goalkeepers_are_unranked`
- [x] `harry_kane_team_rank_1_to_2`
- [x] `robert_lewandowski_team_rank_1_to_2`
- [x] `harry_kane_global_top_10`
- [x] `robert_lewandowski_global_top_20`
- [x] `messi_top_20`
- [x] `mbappe_top_20`
- [x] `bounou_top_8_goalkeeper`
- [x] `courtois_top_8_goalkeeper`
- [x] `martinez_top_2_goalkeeper`
- [x] `livakovic_top_8_goalkeeper`
- [x] `szczesny_top_8_goalkeeper`
- [x] `credible_top_20_standout_coverage`
- [x] `no_role_position_contradictions`
- [x] `no_high_goal_forward_below_mid_tier_teammate`

## Before and after

| Player | Old global | New global | Old team | New team |
|---|---:|---:|---:|---:|
| Harry Kane | 301 | 7 | 13 | 1 |
| Robert Lewandowski | 144 | 4 | 2 | 1 |

## New global top 20

| Rank | Player | Team | 360 group | Role | Rating |
|---:|---|---|---|---|---:|
| 1 | Lionel Andrés Messi Cuccittini | Argentina | AM | Progressive Winger | 1.0000 |
| 2 | Kylian Mbappé Lottin | France | FW | Progressive Winger | 0.9389 |
| 3 | Bruno Miguel Borges Fernandes | Portugal | AM | Progressive Winger | 0.8365 |
| 4 | Robert Lewandowski | Poland | FW | Target Forward / Penalty-Box Anchor | 0.8227 |
| 5 | Christian Pulisic | United States | AM | Progressive Winger | 0.7847 |
| 6 | Mehdi Taremi | Iran | FW | Target Forward | 0.7779 |
| 7 | Harry Kane | England | FW | Target Forward | 0.7777 |
| 8 | Mateo Kovačić | Croatia | CM | Deep Playmaker / Metronome | 0.7730 |
| 9 | Neymar da Silva Santos Junior | Brazil | AM | Progressive Winger | 0.7702 |
| 10 | Luka Modrić | Croatia | CM | Deep Playmaker / Metronome | 0.7648 |
| 11 | Antoine Griezmann | France | AM | Hybrid Playmaker / Roaming Creator | 0.7607 |
| 12 | Ángel Fabián Di María Hernández | Argentina | AM | Progressive Winger | 0.7554 |
| 13 | Olivier Giroud | France | FW | Target Forward / Penalty-Box Anchor | 0.7453 |
| 14 | Richarlison de Andrade | Brazil | FW | Pressing Forward | 0.7381 |
| 15 | Salem Mohammed Al Dawsari | Saudi Arabia | AM | Progressive Winger | 0.7362 |
| 16 | Jamal Musiala | Germany | AM | Hybrid Playmaker / Roaming Creator | 0.7310 |
| 17 | Gonçalo Matias Ramos | Portugal | FW | Target Forward | 0.7308 |
| 18 | Memphis Depay | Netherlands | FW | Target Forward | 0.7234 |
| 19 | Álvaro Borja Morata Martín | Spain | FW | Target Forward | 0.7100 |
| 20 | Julián Álvarez | Argentina | FW | Pressing Forward | 0.7086 |

The audit is diagnostic only. Player names are never inputs to the score.
