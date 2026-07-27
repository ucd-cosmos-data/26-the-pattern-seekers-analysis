# Australia — Team Coaching Report

## Model-grounded summary

Australia: Patient Build-up led the observed baseline by 0.0032 mean EvA. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Harry Souttar + Kye Rowles (0.755). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.8514
- Mean possession EvA gap: 0.003189
- Most common optimal style: Patient Build-up

## Optimized starting 11

1. Aaron Mooy (Defensive Midfield)
2. Aziz Eraltay Behich (Fullback/Wingback)
3. Jackson Irvine (Forward)
4. Mathew Leckie (Central/Wide Midfield)
5. Kye Rowles (Center Back)
6. Harry Souttar (Center Back)
7. Riley McGree (Forward)
8. Mathew Ryan (Goalkeeper)
9. Craig Goodwin (Central/Wide Midfield)
10. Mitchell Thomas Duke (Forward)
11. Miloš Degenek (Fullback/Wingback)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.083 |
| Pressing | 3.342 |
| Recovery | -0.799 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 79, INSUFFICIENT_MINUTES: 20.

## Unified 360-VAEP + xT player leaders

1. Mathew Leckie — Target Forward; rating 0.1368, VAEP/90 +0.259, xT/90 +0.021
2. Jackson Irvine — Ball-Winner; rating 0.1088, VAEP/90 +0.009, xT/90 +0.028
3. Aziz Eraltay Behich — Wide Creator; rating 0.0793, VAEP/90 +0.144, xT/90 +0.044
4. Aaron Mooy — Box-to-Box Runner; rating 0.0121, VAEP/90 -0.015, xT/90 +0.029
5. Kye Rowles — Sweeper CB; rating -0.0346, VAEP/90 -0.110, xT/90 +0.002

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2183 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.1707 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1177 cumulative Net xG)

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
