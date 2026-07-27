# StatsBomb 360 Cache Validation

- Matches: 64
- Matches downloaded this run: 63
- Existing match caches reused: 1
- Unique event frames: 203,882
- Player-location rows: 3,084,800
- Frames per match: 2,373–4,511
- Player rows per match: 32,932–68,296

## Checks

| Check | Result |
|---|---|
| All 64 matches cached | PASS |
| Every match has freeze frames | PASS |
| Every match has player locations | PASS |
| Frame event keys are unique within matches | PASS |
| Player rows outnumber frame rows | PASS |

## Storage

- Raw resumable cache: `data/interim/frames360/raw/<match_id>.json.gz`
- Flattened player locations: `data/interim/world_cup_360_frames.csv`
- Frame visible areas: `data/interim/world_cup_360_visible_areas.csv`
