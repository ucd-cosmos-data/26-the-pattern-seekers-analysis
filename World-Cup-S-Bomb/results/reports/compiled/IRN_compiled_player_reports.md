# IRN — V4 Player Evaluation Collection

- Included 300+ minute players: 3
- Rankings use one cross-role 360-VAEP plus xT formula.
- Heatmaps combine successful on-ball endpoints and SB360 actor snapshots.

---

<!-- PLAYER_REPORT 1: 5220_starter_report.md -->

# Morteza Pouraliganji — Starter Report

- Team: Iran (IRN)
- Position: Right Center Back
- Functional role: Sweeper CB
- VAEP offense per 90: 0.1095
- VAEP defense per 90: -0.0552
- VAEP total per 90: 0.0542
- VAEP per touch: 0.00062
- Spatial xT per 90: 0.0086
- Final-third spatial share: 5.4%
- Unified final player rating: 0.0105
- Team rank: #2
- Rating 95% CI: [-0.0073, 0.0249] (bootstrap SE 0.0082)
- Rank stability: bootstrap mean rank 2.0; P(team #1) 0%, P(top 3) 95%

![V4 event and 360 heatmap](../heatmaps/IRN/5220_heatmap.svg)

## Physical profile

| Metric | Score |
|---|---:|
| Aerial dominance | 0.750 |
| Pressing intensity per 90 | 10.62 |
| Recovery index per 90 | 2.36 |

## Top chemistry partners

- Seyed Majid Hosseini — synergy 0.669, 305 shared minutes
- Mehdi Taremi — synergy 0.585, 305 shared minutes
- Unknown — synergy 0.544, 250 shared minutes

## Tactical recommendations

- Use a compact pressing trigger rather than sustained solo pressure.
- Target this player on direct restarts and back-post deliveries.
- Pair with a faster recovery defender after aggressive rotations.

_The heatmap combines successful event endpoints with StatsBomb 360 actor
snapshots. StatsBomb 360 is freeze-frame context, not continuous player
tracking. Scores exclude players below 300 tournament minutes._

---

<!-- PLAYER_REPORT 2: 5226_starter_report.md -->

# Mehdi Taremi — Starter Report

- Team: Iran (IRN)
- Position: Center Forward
- Functional role: Target Forward
- VAEP offense per 90: 0.3615
- VAEP defense per 90: 0.0502
- VAEP total per 90: 0.4116
- VAEP per touch: 0.00468
- Spatial xT per 90: 0.0526
- Final-third spatial share: 40.8%
- Unified final player rating: 0.2247
- Team rank: #1
- Rating 95% CI: [0.1932, 0.2558] (bootstrap SE 0.0165)
- Rank stability: bootstrap mean rank 1.0; P(team #1) 95%, P(top 3) 95%

![V4 event and 360 heatmap](../heatmaps/IRN/5226_heatmap.svg)

## Physical profile

| Metric | Score |
|---|---:|
| Aerial dominance | 0.389 |
| Pressing intensity per 90 | 19.47 |
| Recovery index per 90 | 3.54 |

## Top chemistry partners

- Morteza Pouraliganji — synergy 0.585, 305 shared minutes
- Unknown — synergy 0.573, 240 shared minutes
- Seyed Majid Hosseini — synergy 0.526, 305 shared minutes

## Tactical recommendations

- Lead the first pressing trigger and protect the inside passing lane.
- Use recovery capacity to support higher attacking positions.

_The heatmap combines successful event endpoints with StatsBomb 360 actor
snapshots. StatsBomb 360 is freeze-frame context, not continuous player
tracking. Scores exclude players below 300 tournament minutes._

---

<!-- PLAYER_REPORT 3: 5228_starter_report.md -->

# Seyed Majid Hosseini — Starter Report

- Team: Iran (IRN)
- Position: Left Center Back
- Functional role: Sweeper CB
- VAEP offense per 90: -0.0022
- VAEP defense per 90: -0.0823
- VAEP total per 90: -0.0845
- VAEP per touch: -0.00115
- Spatial xT per 90: 0.0097
- Final-third spatial share: 3.9%
- Unified final player rating: -0.0246
- Team rank: #3
- Rating 95% CI: [-0.0405, -0.0083] (bootstrap SE 0.0086)
- Rank stability: bootstrap mean rank 3.0; P(team #1) 0%, P(top 3) 95%

![V4 event and 360 heatmap](../heatmaps/IRN/5228_heatmap.svg)

## Physical profile

| Metric | Score |
|---|---:|
| Aerial dominance | 0.417 |
| Pressing intensity per 90 | 10.32 |
| Recovery index per 90 | 5.31 |

## Top chemistry partners

- Morteza Pouraliganji — synergy 0.669, 305 shared minutes
- Unknown — synergy 0.575, 250 shared minutes
- Unknown — synergy 0.574, 240 shared minutes

## Tactical recommendations

- Use a compact pressing trigger rather than sustained solo pressure.
- Use recovery capacity to support higher attacking positions.

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
