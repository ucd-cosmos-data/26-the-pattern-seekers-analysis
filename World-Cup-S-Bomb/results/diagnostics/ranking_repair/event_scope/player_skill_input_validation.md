# Player Skill Input Validation

- Events: 234,637
- Matches: 64
- Player-match component rows: 1,996
- Unique players: 680
- Lineup intervals: 1,995
- Possession lineups: 11,016
- Possessions with 11 attackers: 100.00%
- Possessions with 11 defenders: 100.00%
- Player-credited regulation/extra-time goals: 169
- Own goals: 3
- Official match goals including own goals: 172
- Shootout goals held in the separate channel: 26

## Checks

| Check | Result |
|---|---|
| All 64 matches have lineup intervals | PASS |
| All possession IDs remain unique | PASS |
| At least 99% of possessions have 11 attackers | PASS |
| At least 99% of possessions have 11 defenders | PASS |
| Player-match components cover at least 650 players | PASS |
| Player minutes are non-negative | PASS |
| Official match goals reconcile to 172 | PASS |
| Shootout goals remain separate | PASS |
| Ordinary player goals exclude shootouts | PASS |
