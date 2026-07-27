# Morocco — Team Coaching Report

## Model-grounded summary

Morocco: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Sofyan Amrabat + Yassine Bounou (0.877). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.4814
- Mean possession EvA gap: 0.003112
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Hakim Ziyech (Attacking Midfield/Wing)
2. Achraf Hakimi Mouh (Fullback/Wingback)
3. Azzedine Ounahi (Central/Wide Midfield)
4. Sofiane Boufal (Central/Wide Midfield)
5. Youssef En-Nesyri (Forward)
6. Sofyan Amrabat (Defensive Midfield)
7. Selim Amallah (Central/Wide Midfield)
8. Yahia Attiyat allah (Fullback/Wingback)
9. Yassine Bounou (Goalkeeper)
10. Romain Saïss (Center Back)
11. Achraf Dari (Center Back)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.018 |
| Pressing | 4.404 |
| Recovery | -0.129 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 128, INSUFFICIENT_MINUTES: 22, GAIN_BELOW_THRESHOLD: 4.

## Unified 360-VAEP + xT player leaders

1. Youssef En-Nesyri — Target Forward; rating 0.1563, VAEP/90 +0.228, xT/90 -0.000
2. Sofiane Boufal — Progressive Winger; rating 0.1268, VAEP/90 +0.205, xT/90 +0.079
3. Hakim Ziyech — Box-to-Box Runner; rating 0.1034, VAEP/90 +0.084, xT/90 +0.071
4. Azzedine Ounahi — Ball-Winner; rating 0.0974, VAEP/90 +0.137, xT/90 +0.036
5. Yahia Attiyat allah — Wide Creator; rating 0.0839, VAEP/90 +0.165, xT/90 +0.033

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.3750 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.3232 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.2357 cumulative Net xG)

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
