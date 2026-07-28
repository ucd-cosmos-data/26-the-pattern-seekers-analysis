# England — Team Coaching Report

## Model-grounded summary

England: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -3.654. Strongest positive squad synergy: John Stones + Jordan Pickford (0.815). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.0404
- Mean possession EvA gap: 0.002882
- Most common optimal style: No meaningful change

## Optimized starting 11

1. John Stones (Center Back)
2. Harry Maguire (Center Back)
3. Luke Shaw (Fullback/Wingback)
4. Declan Rice (Defensive Midfield)
5. Jude Bellingham (Defensive Midfield)
6. Harry Kane (Forward)
7. Jordan Pickford (Goalkeeper)
8. Jordan Brian Henderson (Central/Wide Midfield)
9. Bukayo Saka (Attacking Midfield/Wing)
10. Kyle Walker (Fullback/Wingback)
11. Phil Foden (Attacking Midfield/Wing)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.012 |
| Pressing | -3.654 |
| Recovery | 0.987 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 82, INSUFFICIENT_MINUTES: 17.

## V5 role-aware player leaders

1. Jude Bellingham — Box-to-Box / Engine Midfielder; rating 0.6766, VAEP/90 +0.300, xT/90 +0.042, role-adjusted 0.521
2. Luke Shaw — Attacking Wingback; rating 0.6671, VAEP/90 +0.269, xT/90 +0.085, role-adjusted 0.387
3. Harry Maguire — Deep Playmaker; rating 0.6336, VAEP/90 +0.150, xT/90 +0.035, role-adjusted 0.642
4. Harry Kane — Target Forward; rating 0.5879, VAEP/90 +0.275, xT/90 +0.047, role-adjusted 0.838
5. John Stones — Ball-Playing Centre-Back; rating 0.5345, VAEP/90 +0.052, xT/90 +0.010, role-adjusted 0.412

_Only players with at least 300 tournament minutes are ranked. V5 uses 40% VAEP/90, 15% VAEP/touch, 15% xT/90, 15% continuous role-adjusted value, 10% completeness, and 5% coverage-qualified off-ball contribution, followed by position-group minutes shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2988 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2831 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1794 cumulative Net xG)

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
