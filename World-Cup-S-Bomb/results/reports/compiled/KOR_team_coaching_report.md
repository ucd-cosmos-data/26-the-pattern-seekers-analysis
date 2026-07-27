# South Korea — Team Coaching Report

## Model-grounded summary

South Korea: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Young-Gwon Kim + Seung-Gyu Kim (0.730). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.3593
- Mean possession EvA gap: 0.001341
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Moon-Hwan Kim (Fullback/Wingback)
2. Heung-Min Son (Attacking Midfield/Wing)
3. Young-Gwon Kim (Center Back)
4. In-Beom Hwang (Defensive Midfield)
5. Jin-Su Kim (Fullback/Wingback)
6. Woo-Young Jung (Defensive Midfield)
7. Seung-Gyu Kim (Goalkeeper)
8. Min Jae Kim (Center Back)
9. Gue-Sung Cho (Forward)
10. Kang-In Lee (Central/Wide Midfield)
11. Hee-Chan Hwang (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.118 |
| Pressing | 6.170 |
| Recovery | 0.195 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 93, INSUFFICIENT_MINUTES: 17.

## Unified 360-VAEP + xT player leaders

1. Heung-Min Son — Target Forward; rating 0.2082, VAEP/90 +0.385, xT/90 +0.078
2. Jin-Su Kim — Attacking Wingback; rating 0.0983, VAEP/90 +0.216, xT/90 +0.041
3. Moon-Hwan Kim — Attacking Wingback; rating 0.0784, VAEP/90 +0.140, xT/90 +0.046
4. In-Beom Hwang — Box-to-Box Runner; rating 0.0494, VAEP/90 +0.106, xT/90 +0.061
5. Woo-Young Jung — Ball-Winner; rating 0.0200, VAEP/90 +0.001, xT/90 +0.050

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.1081 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.0540 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.0356 cumulative Net xG)

_Counterfactual values are predictive scenario estimates, not causal treatment effects. Substitutions below the gain floor or with confidence intervals crossing zero are suppressed._

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
