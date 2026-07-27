# Poland — Team Coaching Report

## Model-grounded summary

Poland: Patient Build-up led the observed baseline by 0.0041 mean EvA. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Kamil Glik + Matty Cash (0.756). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.1530
- Mean possession EvA gap: 0.004133
- Most common optimal style: Patient Build-up

## Optimized starting 11

1. Kamil Glik (Center Back)
2. Matty Cash (Fullback/Wingback)
3. Robert Lewandowski (Forward)
4. Bartosz Bereszyński (Fullback/Wingback)
5. Piotr Zieliński (Central/Wide Midfield)
6. Grzegorz Krychowiak (Defensive Midfield)
7. Jakub Piotr Kiwior (Center Back)
8. Wojciech Szczęsny (Goalkeeper)
9. Przemysław Frankowski (Central/Wide Midfield)
10. Krystian Bielik (Defensive Midfield)
11. Kamil Grosicki (Attacking Midfield/Wing)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.054 |
| Pressing | 1.148 |
| Recovery | -0.413 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 90, INSUFFICIENT_MINUTES: 20.

## Unified 360-VAEP + xT player leaders

1. Robert Lewandowski — Target Forward; rating 0.2195, VAEP/90 +0.410, xT/90 +0.019
2. Piotr Zieliński — Ball-Winner; rating 0.0952, VAEP/90 +0.089, xT/90 +0.059
3. Bartosz Bereszyński — Wide Creator; rating 0.0608, VAEP/90 +0.078, xT/90 +0.040
4. Grzegorz Krychowiak — Ball-Winner; rating 0.0197, VAEP/90 +0.012, xT/90 +0.025
5. Matty Cash — Box-to-Box Runner; rating 0.0124, VAEP/90 -0.090, xT/90 +0.038

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2162 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2053 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1831 cumulative Net xG)

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
