# Defensive Spatial Feature Validation

- Input 360 event frames: 203,882
- Frames with derived spatial metrics: 203,495
- Possession rows: 11,016
- Possessions with spatial frames: 10,590 (96.13%)
- Matches covered: 64
- Teams covered: 32
- Named defensive players: 662
- Named players with 360 actor context: 662

## Checks

| Check | Result |
|---|---|
| All 64 matches have spatial possession features | PASS |
| All 32 attacking teams have spatial possession features | PASS |
| At least 90% of possessions have a 360 frame | PASS |
| At least 95% of cached frames produced metrics | PASS |
| Named defensive players were identified | PASS |
| Most named defensive players have actor context | PASS |
| Possession IDs remain unique | PASS |

## Method notes

- Coordinates are normalized into the possession team's attacking direction.
- `back_line_height` is the median distance from the defending goal of the three deepest observed outfield defenders.
- Defensive footprint uses `scipy.spatial.ConvexHull.volume`, which is enclosed area in two dimensions.
- Off-ball public 360 players are anonymous; named profiles cover defensive event actors only.
- Visible-area and observed-player counts are retained so downstream models can control for partial pitch visibility.
