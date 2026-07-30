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

## V5 role-aware player leaders

1. Bruno Miguel Borges Fernandes — Hybrid Playmaker / Roaming Creator; rating 0.6935, VAEP/90 +0.220, xT/90 +0.128, role-adjusted 0.753
2. João Félix Sequeira — Target Forward; rating 0.6783, VAEP/90 +0.405, xT/90 +0.046, role-adjusted 0.630
3. Cristiano Ronaldo dos Santos Aveiro — Target Forward; rating 0.6545, VAEP/90 +0.665, xT/90 +0.009, role-adjusted 0.745
4. Bernardo Mota Veiga de Carvalho e Silva — Box-to-Box / Engine Midfielder; rating 0.6221, VAEP/90 +0.251, xT/90 +0.058, role-adjusted 0.024
5. Raphaël Adelino José Guerreiro — Wide Creator; rating 0.5960, VAEP/90 +0.267, xT/90 +0.076, role-adjusted 1.000

_Only players with at least 300 tournament minutes are ranked. V5 uses 40% VAEP/90, 15% VAEP/touch, 15% xT/90, 15% continuous role-adjusted value, 10% completeness, and 5% coverage-qualified off-ball contribution, followed by position-group minutes shrinkage._

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
## V5 probabilistic role validation

The production role model selected **K=9 with `tied` covariance by BIC with AIC tie-breaking. K-Means functional roles remain the published baseline; GMM probabilities and entropy are additive descriptors.

- Bootstrap ARI median: 0.6887
- Bootstrap ARI fifth percentile: 0.5522
- PCA explained variance: 0.8688

Roles do not award points directly. Continuous role dimensions only modulate the weights applied to observed contributions.
<!-- PLAYER_ROLE_VALIDATION_END -->

<!-- ROLE_AWARE_VALUATION_START -->
## V5 role-aware valuation and attention gate

**Production decision: `ROLE_AWARE_FALLBACK`.** The role-aware layer is active. The experimental attention challenger was evaluated match-disjoint and rejected because its discrimination was materially worse, despite better calibration.

| Task | Model | ROC-AUC | PR-AUC | ECE | Brier |
|---|---|---:|---:|---:|---:|
| Retrospective | Baseline | 0.6283 | 0.5179 | 0.0659 | 0.2364 |
| Retrospective | Attention | 0.7258 | 0.6257 | 0.0169 | 0.2086 |
| Prospective | Baseline | 0.8855 | 0.9763 | 0.1866 | 0.1389 |
| Prospective | Attention | 0.8815 | 0.9750 | 0.0147 | 0.0907 |

New-versus-legacy ranking Spearman correlation: 0.7112.
<!-- ROLE_AWARE_VALUATION_END -->

<!-- CONTINUOUS_ROLE_REFINEMENT_START -->
## Functional-role compatibility

The accepted functional-role refinements remain available beside the original K-Means label. V5 adds continuous seven-dimensional role vectors and probabilistic roles; neither system contains player-name rules or discrete role bonuses.
<!-- CONTINUOUS_ROLE_REFINEMENT_END -->
