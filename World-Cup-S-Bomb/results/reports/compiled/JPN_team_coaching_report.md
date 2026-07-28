# Japan — Team Coaching Report

## Model-grounded summary

Japan: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Maya Yoshida + Shūichi Gonda (0.773). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.5031
- Mean possession EvA gap: 0.005446
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Shūichi Gonda (Goalkeeper)
2. Junya Ito (Fullback/Wingback)
3. Wataru Endo (Defensive Midfield)
4. Daichi Kamada (Attacking Midfield/Wing)
5. Ko Itakura (Center Back)
6. Maya Yoshida (Center Back)
7. Hidemasa Morita (Defensive Midfield)
8. Shogo Taniguchi (Center Back)
9. Yuto Nagatomo (Fullback/Wingback)
10. Takuma Asano (Forward)
11. Yuki Soma (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.029 |
| Pressing | 10.178 |
| Recovery | -0.086 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 105, INSUFFICIENT_MINUTES: 16.

## V5 role-aware player leaders

1. Junya Ito — Attacking Wingback; rating 0.5802, VAEP/90 +0.121, xT/90 +0.054, role-adjusted 0.305
2. Shūichi Gonda — Goalkeeper; rating 0.5397, VAEP/90 -0.162, xT/90 +0.007, role-adjusted 0.000
3. Daichi Kamada — Target Forward; rating 0.4990, VAEP/90 +0.174, xT/90 +0.023, role-adjusted 0.000
4. Wataru Endo — Ball-Winner; rating 0.4856, VAEP/90 -0.014, xT/90 +0.038, role-adjusted 0.458
5. Maya Yoshida — Sweeper CB; rating 0.4598, VAEP/90 -0.129, xT/90 +0.006, role-adjusted 0.169

_Only players with at least 300 tournament minutes are ranked. V5 uses 40% VAEP/90, 15% VAEP/touch, 15% xT/90, 15% continuous role-adjusted value, 10% completeness, and 5% coverage-qualified off-ball contribution, followed by position-group minutes shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.4231 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.4056 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1832 cumulative Net xG)

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
