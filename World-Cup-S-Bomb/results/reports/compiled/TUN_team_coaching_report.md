# Tunisia — Team Coaching Report

## Model-grounded summary

Tunisia: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.788. Strongest positive squad synergy: not available. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.1552
- Mean possession EvA gap: 0.000626
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Montassar Omar Talbi (Center Back)
2. Ellyes Joris Skhiri (Defensive Midfield)
3. Yassine Meriah (Center Back)
4. Aymen Dahmen (Goalkeeper)
5. Aïssa Bilal Laïdouni (Defensive Midfield)
6. Ali Abdi (Fullback/Wingback)
7. Youssef Msakni (Attacking Midfield/Wing)
8. Dylan Daniel Mahmoud Bronn (Center Back)
9. Issam Jebali (Forward)
10. Anis Ben Slimane (Attacking Midfield/Wing)
11. Wajdi Kechrida (Fullback/Wingback)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.059 |
| Pressing | -2.788 |
| Recovery | 1.194 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 91, INSUFFICIENT_MINUTES: 19.

## Unified 360-VAEP + xT player leaders

No player cleared the 300-minute V4 evaluation cutoff.

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.0891 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.0468 cumulative Net xG)
- Against Set-Piece Compact Shape: switch from Direct Long Play to Patient Build-up (0.0193 cumulative Net xG)

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
