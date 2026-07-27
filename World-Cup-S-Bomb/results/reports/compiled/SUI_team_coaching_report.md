# Switzerland — Team Coaching Report

## Model-grounded summary

Switzerland: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Direct Long Play to Short Under Pressure). Strongest positive squad synergy: Granit Xhaka + Manuel Obafemi Akanji (0.755). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.1079
- Mean possession EvA gap: 0.000360
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Granit Xhaka (Defensive Midfield)
2. Manuel Obafemi Akanji (Center Back)
3. Ricardo Iván Rodríguez Araya (Fullback/Wingback)
4. Remo Freuler (Defensive Midfield)
5. Breel-Donald Embolo (Forward)
6. Yann Sommer (Goalkeeper)
7. Silvan Widmer (Fullback/Wingback)
8. Ruben Vargas (Attacking Midfield/Wing)
9. Nico Elvedi (Center Back)
10. Xherdan Shaqiri (Central/Wide Midfield)
11. Noah Okafor (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.030 |
| Pressing | 2.987 |
| Recovery | -0.646 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 121, INSUFFICIENT_MINUTES: 22.

## Unified 360-VAEP + xT player leaders

1. Breel-Donald Embolo — Target Forward; rating 0.1938, VAEP/90 +0.312, xT/90 +0.011
2. Ricardo Iván Rodríguez Araya — Wide Creator; rating 0.0457, VAEP/90 +0.024, xT/90 +0.044
3. Granit Xhaka — Ball-Winner; rating 0.0345, VAEP/90 +0.056, xT/90 +0.049
4. Remo Freuler — Ball-Winner; rating 0.0287, VAEP/90 +0.047, xT/90 +0.020
5. Manuel Obafemi Akanji — Deep Playmaker; rating 0.0063, VAEP/90 +0.031, xT/90 +0.011

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Direct Long Play to Short Under Pressure (0.0491 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Short Under Pressure (0.0408 cumulative Net xG)
- Against High-Intensity Press: switch from Direct Long Play to Short Under Pressure (0.0120 cumulative Net xG)

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
