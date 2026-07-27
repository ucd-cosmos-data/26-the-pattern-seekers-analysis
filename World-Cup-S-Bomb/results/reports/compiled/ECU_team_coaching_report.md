# Ecuador — Team Coaching Report

## Model-grounded summary

Ecuador: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Patient Build-up to Short Under Pressure). Strongest positive squad synergy: not available. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.5571
- Mean possession EvA gap: 0.002544
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Piero Martín Hincapié Reyna (Center Back)
2. Felix Eduardo Torres Caicedo (Center Back)
3. Pervis Josué Estupiñán Tenorio (Fullback/Wingback)
4. Moisés Isaac Caicedo Corozo (Defensive Midfield)
5. Hernán Ismael Galíndez (Goalkeeper)
6. Angelo Smit Preciado Quiñónez (Fullback/Wingback)
7. Gonzalo Jordy Plata Jiménez (Central/Wide Midfield)
8. Enner Remberto Valencia Lastra (Attacking Midfield/Wing)
9. Jhegson Sebastián Méndez Carabalí (Defensive Midfield)
10. Michael Steveen Estrada Martínez (Forward)
11. Jeremy Leonel Sarmiento Morante (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.004 |
| Pressing | 1.896 |
| Recovery | 0.400 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 68, INSUFFICIENT_MINUTES: 9.

## Unified 360-VAEP + xT player leaders

No player cleared the 300-minute V4 evaluation cutoff.

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Patient Build-up to Short Under Pressure (0.1544 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Short Under Pressure (0.1356 cumulative Net xG)
- Against Wide Retreating Block: switch from Patient Build-up to Short Under Pressure (0.1334 cumulative Net xG)

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
