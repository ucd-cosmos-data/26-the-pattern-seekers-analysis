# Portugal — Team Coaching Report

## Model-grounded summary

Portugal: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -4.222. Strongest positive squad synergy: Kléper Laveran Lima Ferreira + Diogo Meireles Costa (0.754). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.7544
- Mean possession EvA gap: 0.001849
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Kléper Laveran Lima Ferreira (Center Back)
2. Bruno Miguel Borges Fernandes (Attacking Midfield/Wing)
3. Rúben Santos Gato Alves Dias (Center Back)
4. Bernardo Mota Veiga de Carvalho e Silva (Central/Wide Midfield)
5. João Pedro Cavaco Cancelo (Fullback/Wingback)
6. João Félix Sequeira (Attacking Midfield/Wing)
7. Raphaël Adelino José Guerreiro (Fullback/Wingback)
8. Cristiano Ronaldo dos Santos Aveiro (Forward)
9. Diogo Meireles Costa (Goalkeeper)
10. Rúben Diogo Da Silva Neves (Defensive Midfield)
11. Otávio Edmilson da Silva Monteiro (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.006 |
| Pressing | -4.222 |
| Recovery | -0.010 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 123, INSUFFICIENT_MINUTES: 20.

## Unified 360-VAEP + xT player leaders

1. Cristiano Ronaldo dos Santos Aveiro — Target Forward; rating 0.2844, VAEP/90 +0.665, xT/90 +0.009 [95% CI 0.2078–0.3604]
2. João Félix Sequeira — Target Forward; rating 0.2101, VAEP/90 +0.405, xT/90 +0.046 [95% CI 0.1595–0.2786]
3. Bruno Miguel Borges Fernandes — Hybrid Playmaker / Roaming Creator; rating 0.1671, VAEP/90 +0.220, xT/90 +0.128 [95% CI 0.1332–0.2087]
4. Bernardo Mota Veiga de Carvalho e Silva — Box-to-Box / Engine Midfielder; rating 0.1382, VAEP/90 +0.251, xT/90 +0.058 [95% CI 0.1086–0.1724]
5. Raphaël Adelino José Guerreiro — Wide Creator; rating 0.1134, VAEP/90 +0.267, xT/90 +0.076 [95% CI 0.0717–0.1483]
- Rank confidence: P(Cristiano Ronaldo dos Santos Aveiro is the team's true #1) = 100% (2,000-sample match bootstrap).

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.1823 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.1821 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.0995 cumulative Net xG)

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

<!-- ROLE_AWARE_VALUATION_START -->
## Continuous role-aware valuation A/B test

**Decision: `REJECTED_RETAIN_INCUMBENT`.** The challenger was not promoted. Its Spearman correlation with the incumbent ranking was 0.9854, above the predeclared 0.90 ceiling, so it did not change the overall ordering enough to qualify as the intended systemic correction.

| Benchmark | Incumbent | Challenger diagnostic |
|---|---:|---:|
| Messi global rank | 1 | 1 |
| Mbappé global rank | 2 | 2 |
| Griezmann global rank | 21 | 6 |

The diagnostic Griezmann movement came from creation (0.799), pressing (0.711), and completeness (0.862), with no player-name rule. Nevertheless, all published player/team rankings retain the incumbent 360-VAEP+xT rating.

Foundational model performance remains unchanged: OOF ROC-AUC 0.948994, PR-AUC 0.084827, Brier 0.001123, ECE 0.000336.
<!-- ROLE_AWARE_VALUATION_END -->

<!-- CONTINUOUS_ROLE_REFINEMENT_START -->
## Accepted continuous role refinement

**34 of 142 players (23.9%) received an evidence-backed post-K-Means role refinement; 108 retained their original role.** The original cluster label remains available as `kmeans_functional_role`. Ratings, team ranks, VAEP and xT were not changed by this role-only promotion.

France refinements:

- Olivier Giroud: Target Forward → **Target Forward / Penalty-Box Anchor**
- Antoine Griezmann: Ball-Winner → **Hybrid Playmaker / Roaming Creator**
- Theo Bernard François Hernández: Wide Creator → **Attacking Wingback**
- Ibrahima Konaté: Deep Playmaker → **Ball-Playing Centre-Back**
- Aurélien Djani Tchouaméni: Ball-Winner → **Holding / Controlling Midfielder**

Refinements use continuous progression, creation, finishing, pressing, defensive, security, aerial and completeness scores with broad-position safeguards. No player-name condition is used.
<!-- CONTINUOUS_ROLE_REFINEMENT_END -->
