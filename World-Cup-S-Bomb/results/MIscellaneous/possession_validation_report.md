# Possession Preprocessing Validation Report

- Source: `notebooks/all_events.csv`
- Output: `data/processed/world_cup_possessions.csv`
- Source event rows: 234,637
- Penalty-shootout rows excluded: 106
- Candidate possession groups: 11,154
- Output possessions: 11,016
- Matches: 64
- Teams: 32
- Shots: 1,438
- Opponent transition shots retained by StatsBomb in the prior possession: 15
- Possessions with a shot: 1,282
- Possession-team goals including own goals: 169
- Opponent transition goals: 3
- Tournament goals accounted for: 172
- Total xG: 154.174

## Validation checks

| Check | Result |
|---|---|
| All 64 matches represented | PASS |
| All 32 teams represented | PASS |
| Possession IDs are unique | PASS |
| No penalty-shootout rows | PASS |
| No negative durations | PASS |
| Pass completion is within 0-100 | PASS |
| Every team has a known opponent | PASS |
| All 172 tournament goals are accounted for | PASS |

## Important scope note

`all_events.csv` does not contain general StatsBomb 360 freeze frames. The defensive columns are event-based pressure/action proxies and must not be labeled as exact defensive-line height or team compactness.
