# Croatia — Team Coaching Report

## Model-grounded summary

Croatia: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.690. Strongest positive squad synergy: Dominik Livaković + Joško Gvardiol (0.925). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.9757
- Mean possession EvA gap: 0.001566
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Mateo Kovačić (Central/Wide Midfield)
2. Ivan Perišić (Attacking Midfield/Wing)
3. Luka Modrić (Central/Wide Midfield)
4. Josip Juranović (Fullback/Wingback)
5. Andrej Kramarić (Attacking Midfield/Wing)
6. Joško Gvardiol (Center Back)
7. Marcelo Brozović (Defensive Midfield)
8. Dominik Livaković (Goalkeeper)
9. Borna Sosa (Fullback/Wingback)
10. Dejan Lovren (Center Back)
11. Bruno Petković (Forward)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.041 |
| Pressing | -2.690 |
| Recovery | 0.290 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, INSUFFICIENT_MINUTES: 15.

## Unified 360-VAEP + xT player leaders

1. Ivan Perišić — Wide Creator; rating 0.2144, VAEP/90 +0.407, xT/90 +0.065
2. Andrej Kramarić — Target Forward; rating 0.1937, VAEP/90 +0.365, xT/90 +0.010
3. Mateo Kovačić — Ball-Winner; rating 0.1302, VAEP/90 +0.225, xT/90 +0.065
4. Luka Modrić — Ball-Winner; rating 0.0858, VAEP/90 +0.087, xT/90 +0.092
5. Borna Sosa — Wide Creator; rating 0.0781, VAEP/90 +0.130, xT/90 +0.068

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2061 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2056 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1470 cumulative Net xG)

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
