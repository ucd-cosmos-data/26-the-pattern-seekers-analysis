# Argentina — Team Coaching Report

## Model-grounded summary

Argentina: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.135. Strongest positive squad synergy: Nicolás Hernán Otamendi + Damián Emiliano Martínez (0.927). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 2.9806
- Mean possession EvA gap: 0.005266
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Lionel Andrés Messi Cuccittini (Attacking Midfield/Wing)
2. Damián Emiliano Martínez (Goalkeeper)
3. Rodrigo Javier De Paul (Defensive Midfield)
4. Enzo Fernandez (Defensive Midfield)
5. Alexis Mac Allister (Central/Wide Midfield)
6. Nahuel Molina Lucero (Fullback/Wingback)
7. Julián Álvarez (Forward)
8. Marcos Javier Acuña (Fullback/Wingback)
9. Nicolás Hernán Otamendi (Center Back)
10. Ángel Fabián Di María Hernández (Central/Wide Midfield)
11. Cristian Gabriel Romero (Center Back)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.043 |
| Pressing | -2.135 |
| Recovery | 0.730 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 122, INSUFFICIENT_MINUTES: 18, GAIN_BELOW_THRESHOLD: 3.

## Unified 360-VAEP + xT player leaders

1. Lionel Andrés Messi Cuccittini — Progressive Winger; rating 0.3297, VAEP/90 +0.694, xT/90 +0.158
2. Julián Álvarez — Target Forward; rating 0.2905, VAEP/90 +0.636, xT/90 +0.032
3. Ángel Fabián Di María Hernández — Progressive Winger; rating 0.2879, VAEP/90 +0.786, xT/90 +0.200
4. Marcos Javier Acuña — Attacking Wingback; rating 0.1687, VAEP/90 +0.446, xT/90 +0.068
5. Alexis Mac Allister — Ball-Winner; rating 0.1423, VAEP/90 +0.284, xT/90 +0.007

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.9990 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.7842 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.4272 cumulative Net xG)

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
