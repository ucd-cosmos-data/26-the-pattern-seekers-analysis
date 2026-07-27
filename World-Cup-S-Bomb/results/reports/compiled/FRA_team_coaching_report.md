# France — Team Coaching Report

## Model-grounded summary

France: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Raphaël Varane + Aurélien Djani Tchouaméni (0.842). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.6468
- Mean possession EvA gap: 0.003107
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Kylian Mbappé Lottin (Forward)
2. Antoine Griezmann (Attacking Midfield/Wing)
3. Adrien Rabiot (Defensive Midfield)
4. Raphaël Varane (Center Back)
5. Theo Bernard François Hernández (Fullback/Wingback)
6. Aurélien Djani Tchouaméni (Defensive Midfield)
7. Jules Koundé (Fullback/Wingback)
8. Ibrahima Konaté (Center Back)
9. Hugo Lloris (Goalkeeper)
10. Marcus Thuram (Central/Wide Midfield)
11. Jordan Veretout (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.105 |
| Pressing | 1.067 |
| Recovery | -0.652 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 122, INSUFFICIENT_MINUTES: 19, GAIN_BELOW_THRESHOLD: 2.

## Unified 360-VAEP + xT player leaders

1. Kylian Mbappé Lottin — Progressive Winger; rating 0.3127, VAEP/90 +0.643, xT/90 +0.134
2. Olivier Giroud — Target Forward; rating 0.2377, VAEP/90 +0.476, xT/90 +0.008
3. Ousmane Dembélé — Progressive Winger; rating 0.2020, VAEP/90 +0.351, xT/90 +0.112
4. Antoine Griezmann — Ball-Winner; rating 0.1995, VAEP/90 +0.343, xT/90 +0.117
5. Adrien Rabiot — Ball-Winner; rating 0.0915, VAEP/90 +0.246, xT/90 +0.013

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.3625 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.3060 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2840 cumulative Net xG)

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
