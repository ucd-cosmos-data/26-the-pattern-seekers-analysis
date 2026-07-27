# GHA — V4 Player Evaluation Collection

- Included 300+ minute players: 4
- Rankings use one cross-role 360-VAEP plus xT formula.
- Heatmaps combine successful on-ball endpoints and SB360 actor snapshots.

---

<!-- PLAYER_REPORT 1: 3709_starter_report.md -->

# Daniel Amartey — Starter Report

- Team: Ghana (GHA)
- Position: Right Center Back
- Functional role: Sweeper CB
- VAEP offense per 90: -0.0048
- VAEP defense per 90: -0.2336
- VAEP total per 90: -0.2384
- VAEP per touch: -0.00216
- Spatial xT per 90: 0.0118
- Final-third spatial share: 5.2%
- Unified final player rating: -0.0630
- Team rank: #4

![V4 event and 360 heatmap](../heatmaps/GHA/3709_heatmap.svg)

## Physical profile

| Metric | Score |
|---|---:|
| Aerial dominance | 0.545 |
| Pressing intensity per 90 | 7.47 |
| Recovery index per 90 | 3.59 |

## Top chemistry partners

- Mohamed Salisu — synergy 0.662, 301 shared minutes
- Thomas Teye Partey — synergy 0.657, 301 shared minutes
- Lawrence Ati-Zigi — synergy 0.653, 301 shared minutes

## Tactical recommendations

- Use a compact pressing trigger rather than sustained solo pressure.
- Use recovery capacity to support higher attacking positions.

_The heatmap combines successful event endpoints with StatsBomb 360 actor
snapshots. StatsBomb 360 is freeze-frame context, not continuous player
tracking. Scores exclude players below 300 tournament minutes._

---

<!-- PLAYER_REPORT 2: 6383_starter_report.md -->

# Thomas Teye Partey — Starter Report

- Team: Ghana (GHA)
- Position: Right Defensive Midfield
- Functional role: Ball-Winner
- VAEP offense per 90: 0.0190
- VAEP defense per 90: -0.0970
- VAEP total per 90: -0.0780
- VAEP per touch: -0.00053
- Spatial xT per 90: 0.0443
- Final-third spatial share: 15.1%
- Unified final player rating: -0.0002
- Team rank: #2

![V4 event and 360 heatmap](../heatmaps/GHA/6383_heatmap.svg)

## Physical profile

| Metric | Score |
|---|---:|
| Aerial dominance | 0.692 |
| Pressing intensity per 90 | 12.85 |
| Recovery index per 90 | 3.59 |

## Top chemistry partners

- Mohamed Salisu — synergy 0.663, 301 shared minutes
- Daniel Amartey — synergy 0.657, 301 shared minutes
- Lawrence Ati-Zigi — synergy 0.637, 301 shared minutes

## Tactical recommendations

- Lead the first pressing trigger and protect the inside passing lane.
- Target this player on direct restarts and back-post deliveries.
- Use recovery capacity to support higher attacking positions.

_The heatmap combines successful event endpoints with StatsBomb 360 actor
snapshots. StatsBomb 360 is freeze-frame context, not continuous player
tracking. Scores exclude players below 300 tournament minutes._

---

<!-- PLAYER_REPORT 3: 8108_starter_report.md -->

# Lawrence Ati-Zigi — Starter Report

- Team: Ghana (GHA)
- Position: Goalkeeper
- Functional role: Goalkeeper
- VAEP offense per 90: -0.0025
- VAEP defense per 90: -0.1165
- VAEP total per 90: -0.1189
- VAEP per touch: -0.00321
- Spatial xT per 90: 0.0066
- Final-third spatial share: 1.1%
- Unified final player rating: -0.0554
- Team rank: #3

![V4 event and 360 heatmap](../heatmaps/GHA/8108_heatmap.svg)

## Physical profile

| Metric | Score |
|---|---:|
| Aerial dominance | 0.000 |
| Pressing intensity per 90 | 0.00 |
| Recovery index per 90 | 2.39 |

## Top chemistry partners

- Mohamed Salisu — synergy 0.655, 301 shared minutes
- Daniel Amartey — synergy 0.653, 301 shared minutes
- Thomas Teye Partey — synergy 0.637, 301 shared minutes

## Tactical recommendations

- Use a compact pressing trigger rather than sustained solo pressure.
- Avoid isolating this player in high-volume aerial matchups.
- Pair with a faster recovery defender after aggressive rotations.

_The heatmap combines successful event endpoints with StatsBomb 360 actor
snapshots. StatsBomb 360 is freeze-frame context, not continuous player
tracking. Scores exclude players below 300 tournament minutes._

---

<!-- PLAYER_REPORT 4: 30519_starter_report.md -->

# Mohamed Salisu — Starter Report

- Team: Ghana (GHA)
- Position: Left Center Back
- Functional role: Sweeper CB
- VAEP offense per 90: 0.0587
- VAEP defense per 90: -0.0456
- VAEP total per 90: 0.0131
- VAEP per touch: 0.00012
- Spatial xT per 90: 0.0187
- Final-third spatial share: 6.4%
- Unified final player rating: 0.0010
- Team rank: #1

![V4 event and 360 heatmap](../heatmaps/GHA/30519_heatmap.svg)

## Physical profile

| Metric | Score |
|---|---:|
| Aerial dominance | 0.529 |
| Pressing intensity per 90 | 6.87 |
| Recovery index per 90 | 2.09 |

## Top chemistry partners

- Thomas Teye Partey — synergy 0.663, 301 shared minutes
- Daniel Amartey — synergy 0.662, 301 shared minutes
- Lawrence Ati-Zigi — synergy 0.655, 301 shared minutes

## Tactical recommendations

- Use a compact pressing trigger rather than sustained solo pressure.
- Pair with a faster recovery defender after aggressive rotations.

_The heatmap combines successful event endpoints with StatsBomb 360 actor
snapshots. StatsBomb 360 is freeze-frame context, not continuous player
tracking. Scores exclude players below 300 tournament minutes._

<!-- PROSPECTIVE_VALIDATION_START -->
## Prospective possession-model validation

**Overall status: `PARTIAL_PASS_ROLLBACK`.** Box-entry prediction passed every discrimination, calibration, and paired match-bootstrap gate. The shot challenger improved numerically but its confidence interval crossed zero, so it was rejected. The combined prospective artifact was not deployed and the stable production state was preserved.

| Target | Status | Baseline ROC-AUC | Challenger ROC-AUC | PR-AUC | Brier | ECE | Paired ROC gain (90% interval) |
|---|---|---:|---:|---:|---:|---:|---:|
| Box entry | **PASSED** | 0.6888 | 0.7268 | 0.6131 | 0.1722 | 0.0309 | +0.0155 [+0.0106, +0.0205] |
| Shot | **REJECTED** | 0.6642 | 0.6841 | 0.2686 | 0.0960 | 0.0118 | +0.0038 [-0.0030, +0.0120] |

_This challenger is isolated from 360-VAEP/xT player ratings, transition risk, retrospective possession models, and tactical clustering. Player and team descriptive metrics therefore remain unchanged._
<!-- PROSPECTIVE_VALIDATION_END -->
