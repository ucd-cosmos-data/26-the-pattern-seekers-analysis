# England — Team Coaching Report

## Model-grounded summary

England: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -3.654. Strongest positive squad synergy: John Stones + Jordan Pickford (0.815). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.0404
- Mean possession EvA gap: 0.002882
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Luke Shaw (Fullback/Wingback)
2. John Stones (Center Back)
3. Harry Maguire (Center Back)
4. Declan Rice (Defensive Midfield)
5. Harry Kane (Forward)
6. Jude Bellingham (Defensive Midfield)
7. Jordan Pickford (Goalkeeper)
8. Jordan Brian Henderson (Central/Wide Midfield)
9. Bukayo Saka (Attacking Midfield/Wing)
10. Kyle Walker (Fullback/Wingback)
11. Phil Foden (Attacking Midfield/Wing)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.012 |
| Pressing | -3.654 |
| Recovery | 0.987 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 82, INSUFFICIENT_MINUTES: 17.

## Unified 360-VAEP + xT player leaders

1. Harry Kane — Target Forward; rating 0.1828, VAEP/90 +0.275, xT/90 +0.047
2. Luke Shaw — Wide Creator; rating 0.1223, VAEP/90 +0.269, xT/90 +0.085
3. Jude Bellingham — Ball-Winner; rating 0.1069, VAEP/90 +0.300, xT/90 +0.042
4. Harry Maguire — Deep Playmaker; rating 0.0462, VAEP/90 +0.150, xT/90 +0.035
5. Declan Rice — Ball-Winner; rating 0.0276, VAEP/90 +0.043, xT/90 +0.022

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2988 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2831 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1794 cumulative Net xG)

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
