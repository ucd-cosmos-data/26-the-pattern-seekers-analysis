# Brazil — Team Coaching Report

## Model-grounded summary

Brazil: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -6.128. Strongest positive squad synergy: Thiago Emiliano da Silva + Marcos Aoás Corrêa (0.778). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.7461
- Mean possession EvA gap: 0.004167
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Thiago Emiliano da Silva (Center Back)
2. Carlos Henrique Casimiro (Defensive Midfield)
3. Éder Gabriel Militão (Fullback/Wingback)
4. Raphael Dias Belloli (Attacking Midfield/Wing)
5. Richarlison de Andrade (Forward)
6. Lucas Tolentino Coelho de Lima (Defensive Midfield)
7. Vinícius José Paixão de Oliveira Júnior (Central/Wide Midfield)
8. Marcos Aoás Corrêa (Center Back)
9. Danilo Luiz da Silva (Fullback/Wingback)
10. Alisson Ramsés Becker (Goalkeeper)
11. Rodrygo Silva de Goes (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.126 |
| Pressing | -6.128 |
| Recovery | 0.692 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 140, INSUFFICIENT_MINUTES: 25.

## Unified 360-VAEP + xT player leaders

1. Richarlison de Andrade — Target Forward; rating 0.2984, VAEP/90 +0.708, xT/90 +0.012
2. Raphael Dias Belloli — Progressive Winger; rating 0.2420, VAEP/90 +0.477, xT/90 +0.170
3. Vinícius José Paixão de Oliveira Júnior — Progressive Winger; rating 0.2296, VAEP/90 +0.584, xT/90 +0.124
4. Lucas Tolentino Coelho de Lima — Ball-Winner; rating 0.0589, VAEP/90 +0.155, xT/90 +0.043
5. Éder Gabriel Militão — Box-to-Box Runner; rating 0.0570, VAEP/90 +0.068, xT/90 +0.032

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.4708 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.4654 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.3857 cumulative Net xG)

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
