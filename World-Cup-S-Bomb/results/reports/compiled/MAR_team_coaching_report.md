# Morocco — Team Coaching Report

## Model-grounded summary

Morocco: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Sofyan Amrabat + Yassine Bounou (0.877). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.4814
- Mean possession EvA gap: 0.003112
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Achraf Hakimi Mouh (Fullback/Wingback)
2. Hakim Ziyech (Attacking Midfield/Wing)
3. Yassine Bounou (Goalkeeper)
4. Azzedine Ounahi (Central/Wide Midfield)
5. Youssef En-Nesyri (Forward)
6. Selim Amallah (Central/Wide Midfield)
7. Romain Saïss (Center Back)
8. Nayef Aguerd (Center Back)
9. Sofiane Boufal (Central/Wide Midfield)
10. Sofyan Amrabat (Defensive Midfield)
11. Yahia Attiyat allah (Fullback/Wingback)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.018 |
| Pressing | 4.404 |
| Recovery | -0.129 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 128, INSUFFICIENT_MINUTES: 22, GAIN_BELOW_THRESHOLD: 4.

## V5 role-aware player leaders

1. Sofiane Boufal — Box-to-Box / Engine Midfielder; rating 0.7188, VAEP/90 +0.205, xT/90 +0.079, role-adjusted 0.605
2. Hakim Ziyech — Box-to-Box Runner; rating 0.6699, VAEP/90 +0.084, xT/90 +0.071, role-adjusted 0.660
3. Azzedine Ounahi — Box-to-Box / Engine Midfielder; rating 0.6611, VAEP/90 +0.137, xT/90 +0.036, role-adjusted 0.601
4. Youssef En-Nesyri — Target Forward / Penalty-Box Anchor; rating 0.6363, VAEP/90 +0.228, xT/90 -0.000, role-adjusted 0.573
5. Yahia Attiyat allah — Wide Creator; rating 0.6353, VAEP/90 +0.165, xT/90 +0.033, role-adjusted 0.565

_Only players with at least 300 tournament minutes are ranked. V5 uses 40% VAEP/90, 15% VAEP/touch, 15% xT/90, 15% continuous role-adjusted value, 10% completeness, and 5% coverage-qualified off-ball contribution, followed by position-group minutes shrinkage._

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
