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
- Rating 95% CI: [-0.1267, -0.0095] (bootstrap SE 0.0332)
- Rank stability: bootstrap mean rank 3.6; P(team #1) 0%, P(top 3) 37%

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
- Rating 95% CI: [-0.0335, 0.0308] (bootstrap SE 0.0174)
- Rank stability: bootstrap mean rank 1.5; P(team #1) 49%, P(top 3) 96%

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
- Rating 95% CI: [-0.0692, -0.0400] (bootstrap SE 0.0073)
- Rank stability: bootstrap mean rank 3.4; P(team #1) 0%, P(top 3) 59%

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
- Rating 95% CI: [-0.0080, 0.0071] (bootstrap SE 0.0038)
- Rank stability: bootstrap mean rank 1.5; P(team #1) 47%, P(top 3) 96%

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

<!-- PLAYER_ROLE_VALIDATION_START -->
## Player-role and valuation validation status

**Production state retained.** The probabilistic role matrix and learned valuation were evaluated as challengers but were not promoted because they missed their predeclared statistical gates.

| Component | Decision | Validation evidence |
|---|---|---|
| Probabilistic GMM roles | **REJECTED** | K=9; silhouette 0.3159; median 500-bootstrap ARI 0.6961 vs required 0.70 |
| Learned Ridge valuation | **REJECTED** | OOF Spearman 0.7095 → 0.7150; gain 95% CI [-0.0053, +0.0165] crosses zero |

The active calibrated 360-VAEP model therefore remains unchanged: OOF ROC-AUC 0.948994, PR-AUC 0.084827, Brier 0.001123. Messi remains Argentina rank #1 and Mbappé remains France rank #1; no player-name override was used.
<!-- PLAYER_ROLE_VALIDATION_END -->

<!-- ROLE_AWARE_VALUATION_START -->
## Continuous role-aware valuation A/B test

**Decision: `REJECTED_RETAIN_INCUMBENT`.** The challenger was not promoted. Its Spearman correlation with the incumbent ranking was 0.9854, above the predeclared 0.90 ceiling, so it did not change the overall ordering enough to qualify as the intended systemic correction.

| Benchmark | Incumbent | Challenger diagnostic |
|---|---:|---:|
| Messi global rank | 1 | 1 |
| Mbappé global rank | 2 | 2 |
| Griezmann global rank | 21 | 6 |

The diagnostic Griezmann movement came from creation (0.799), pressing (0.711), and completeness (0.862), with no player-name rule. Nevertheless, all published player/team rankings retain the incumbent 360-VAEP+xT rating.

Foundational model performance remains unchanged: OOF ROC-AUC 0.948994, PR-AUC 0.084827, Brier 0.001123, ECE 0.000336.
<!-- ROLE_AWARE_VALUATION_END -->

<!-- CONTINUOUS_ROLE_REFINEMENT_START -->
## Accepted continuous role refinement

**34 of 142 players (23.9%) received an evidence-backed post-K-Means role refinement; 108 retained their original role.** The original cluster label remains available as `kmeans_functional_role`. Ratings, team ranks, VAEP and xT were not changed by this role-only promotion.

France refinements:

- Olivier Giroud: Target Forward → **Target Forward / Penalty-Box Anchor**
- Antoine Griezmann: Ball-Winner → **Hybrid Playmaker / Roaming Creator**
- Theo Bernard François Hernández: Wide Creator → **Attacking Wingback**
- Ibrahima Konaté: Deep Playmaker → **Ball-Playing Centre-Back**
- Aurélien Djani Tchouaméni: Ball-Winner → **Holding / Controlling Midfielder**

Refinements use continuous progression, creation, finishing, pressing, defensive, security, aerial and completeness scores with broad-position safeguards. No player-name condition is used.
<!-- CONTINUOUS_ROLE_REFINEMENT_END -->
