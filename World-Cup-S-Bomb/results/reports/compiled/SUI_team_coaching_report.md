# Switzerland — Team Coaching Report

## Model-grounded summary

Switzerland: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Direct Long Play to Short Under Pressure). Strongest positive squad synergy: Granit Xhaka + Manuel Obafemi Akanji (0.755). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.1079
- Mean possession EvA gap: 0.000360
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Manuel Obafemi Akanji (Center Back)
2. Granit Xhaka (Defensive Midfield)
3. Remo Freuler (Defensive Midfield)
4. Breel-Donald Embolo (Forward)
5. Yann Sommer (Goalkeeper)
6. Silvan Widmer (Fullback/Wingback)
7. Ruben Vargas (Attacking Midfield/Wing)
8. Ricardo Iván Rodríguez Araya (Fullback/Wingback)
9. Xherdan Shaqiri (Central/Wide Midfield)
10. Nico Elvedi (Center Back)
11. Noah Okafor (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.030 |
| Pressing | 2.987 |
| Recovery | -0.646 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 121, INSUFFICIENT_MINUTES: 22.

## V5 role-aware player leaders

1. Breel-Donald Embolo — Target Forward; rating 0.6985, VAEP/90 +0.312, xT/90 +0.011, role-adjusted 0.597
2. Granit Xhaka — Ball-Winner; rating 0.5634, VAEP/90 +0.056, xT/90 +0.049, role-adjusted 0.613
3. Ricardo Iván Rodríguez Araya — Wide Creator; rating 0.5390, VAEP/90 +0.024, xT/90 +0.044, role-adjusted 0.586
4. Remo Freuler — Ball-Winner; rating 0.5162, VAEP/90 +0.047, xT/90 +0.020, role-adjusted 0.574
5. Manuel Obafemi Akanji — Ball-Playing Centre-Back; rating 0.4367, VAEP/90 +0.031, xT/90 +0.011, role-adjusted 0.708

_Only players with at least 300 tournament minutes are ranked. V5 uses 40% VAEP/90, 15% VAEP/touch, 15% xT/90, 15% continuous role-adjusted value, 10% completeness, and 5% coverage-qualified off-ball contribution, followed by position-group minutes shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Direct Long Play to Short Under Pressure (0.0491 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Short Under Pressure (0.0408 cumulative Net xG)
- Against High-Intensity Press: switch from Direct Long Play to Short Under Pressure (0.0120 cumulative Net xG)

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

The production role model selected **K=13 with `tied` covariance by BIC with AIC tie-breaking. K-Means functional roles remain the published baseline; GMM probabilities and entropy are additive descriptors.

- Bootstrap ARI median: 0.6905
- Bootstrap ARI fifth percentile: 0.6163
- PCA explained variance: 0.8821

Roles do not award points directly. Continuous role dimensions only modulate the weights applied to observed contributions.
<!-- PLAYER_ROLE_VALIDATION_END -->

<!-- ROLE_AWARE_VALUATION_START -->
## V5 role-aware valuation and attention gate

**Production decision: `ROLE_AWARE_FALLBACK`.** The role-aware layer is active. The experimental attention challenger was evaluated match-disjoint and rejected because its discrimination was materially worse, despite better calibration.

| Task | Model | ROC-AUC | PR-AUC | ECE | Brier |
|---|---|---:|---:|---:|---:|
| Retrospective | Baseline | 0.6404 | 0.5652 | 0.0569 | 0.2350 |
| Retrospective | Attention | 0.6011 | 0.5290 | 0.0285 | 0.2391 |
| Prospective | Baseline | 0.8643 | 0.9725 | 0.1919 | 0.1423 |
| Prospective | Attention | 0.7551 | 0.9414 | 0.0249 | 0.1105 |

New-versus-legacy ranking Spearman correlation: 0.9848.
<!-- ROLE_AWARE_VALUATION_END -->

<!-- CONTINUOUS_ROLE_REFINEMENT_START -->
## Functional-role compatibility

The accepted functional-role refinements remain available beside the original K-Means label. V5 adds continuous seven-dimensional role vectors and probabilistic roles; neither system contains player-name rules or discrete role bonuses.
<!-- CONTINUOUS_ROLE_REFINEMENT_END -->
