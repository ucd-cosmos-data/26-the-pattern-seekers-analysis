# Senegal — Team Coaching Report

## Model-grounded summary

Senegal: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -1.491. Strongest positive squad synergy: Kalidou Koulibaly + Edouard Mendy (0.753). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.2354
- Mean possession EvA gap: 0.004290
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Youssouf Sabaly (Fullback/Wingback)
2. Kalidou Koulibaly (Center Back)
3. Ismaïla Sarr (Attacking Midfield/Wing)
4. Boulaye Dia (Attacking Midfield/Wing)
5. Edouard Mendy (Goalkeeper)
6. Nampalys Mendy (Defensive Midfield)
7. Ismail Jakobs (Fullback/Wingback)
8. Idrissa Gana Gueye (Attacking Midfield/Wing)
9. Abdou Diallo (Center Back)
10. Krépin Diatta (Attacking Midfield/Wing)
11. Cheikh Ahmadou Bamba Mbacke Dieng (Forward)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.016 |
| Pressing | -1.491 |
| Recovery | -0.488 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 79, INSUFFICIENT_MINUTES: 20.

## V5 role-aware player leaders

1. Ismaïla Sarr — Target Forward; rating 0.7461, VAEP/90 +0.436, xT/90 +0.090, role-adjusted 0.615
2. Boulaye Dia — Target Forward; rating 0.6550, VAEP/90 +0.256, xT/90 -0.008, role-adjusted 0.397
3. Youssouf Sabaly — Attacking Wingback; rating 0.5531, VAEP/90 +0.115, xT/90 +0.078, role-adjusted 0.376
4. Edouard Mendy — Goalkeeper; rating 0.4924, VAEP/90 -0.104, xT/90 +0.005, role-adjusted 0.000
5. Kalidou Koulibaly — Sweeper CB; rating 0.3428, VAEP/90 +0.044, xT/90 +0.011, role-adjusted 0.654

_Only players with at least 300 tournament minutes are ranked. V5 uses 40% VAEP/90, 15% VAEP/touch, 15% xT/90, 15% continuous role-adjusted value, 10% completeness, and 5% coverage-qualified off-ball contribution, followed by position-group minutes shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.3251 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2672 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1931 cumulative Net xG)

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
