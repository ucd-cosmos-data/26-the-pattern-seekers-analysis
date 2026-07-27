# United States — Team Coaching Report

## Model-grounded summary

United States: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -0.925. Strongest positive squad synergy: Matthew Charles Turner + Tim Ream (0.756). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.3304
- Mean possession EvA gap: 0.001101
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Tyler Adams (Defensive Midfield)
2. Yunus Dimoara Musah (Central/Wide Midfield)
3. Antonee Robinson (Fullback/Wingback)
4. Christian Pulisic (Attacking Midfield/Wing)
5. Timothy Weah (Attacking Midfield/Wing)
6. Sergino Dest (Fullback/Wingback)
7. Tim Ream (Center Back)
8. Matthew Charles Turner (Goalkeeper)
9. Weston McKennie (Central/Wide Midfield)
10. Walker Zimmerman (Center Back)
11. Joshua Sargent (Forward)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.068 |
| Pressing | -0.925 |
| Recovery | 0.496 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, INSUFFICIENT_MINUTES: 15.

## Unified 360-VAEP + xT player leaders

1. Christian Pulisic — Progressive Winger; rating 0.2496, VAEP/90 +0.527, xT/90 +0.114
2. Timothy Weah — Progressive Winger; rating 0.2230, VAEP/90 +0.466, xT/90 +0.018
3. Yunus Dimoara Musah — Ball-Winner; rating 0.1005, VAEP/90 +0.118, xT/90 +0.046
4. Antonee Robinson — Wide Creator; rating 0.0958, VAEP/90 +0.186, xT/90 +0.085
5. Sergino Dest — Box-to-Box Runner; rating 0.0741, VAEP/90 +0.103, xT/90 +0.098

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.0836 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.0715 cumulative Net xG)
- Against Set-Piece Compact Shape: switch from Direct Long Play to Patient Build-up (0.0514 cumulative Net xG)

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
