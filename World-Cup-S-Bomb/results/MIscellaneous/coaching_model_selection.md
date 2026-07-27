# Coaching Model Uncertainty and Final Selection

## Selection design

- Match-cluster bootstrap replicates: 5,000
- Resampling unit: complete match
- Primary selection metric: out-of-fold log loss
- Practical tie margin: 0.001 absolute log loss
- Rule: among retrospective candidates within the margin of the empirical best, select the least complex model.
- Confidence intervals describe sampling uncertainty; they do not remove winner-selection optimism from using the same cross-validation predictions.

## Final retrospective selections

| Target | Selected model | Layout | Log loss (95% CI) | Delta vs empirical best (95% CI) | ROC-AUC | PR-AUC |
|---|---|---|---:|---:|---:|---:|
| box_entry | Histogram Gradient Boosting | Tactical + Shape | 0.3556 (0.3446–0.3660) | +0.0000 (+0.0000–+0.0000) | 0.9041 | 0.8304 |
| shot | XGBoost | Tactical + Shape | 0.2486 (0.2368–0.2606) | +0.0007 (-0.0006–+0.0020) | 0.8918 | 0.5238 |

## Prospective start-context baselines

| Target | Model | Log loss (95% CI) | ROC-AUC | PR-AUC |
|---|---|---:|---:|---:|
| box_entry | Logistic Regression | 0.5532 (0.5428–0.5631) | 0.6888 | 0.5816 |
| shot | Logistic Regression | 0.3538 (0.3383–0.3705) | 0.6642 | 0.2441 |

## Interpretation

The selected retrospective models are parsimonious representatives of a near-tied candidate set, not statistically proven universal winners. The prospective baselines remain separate because completed-possession styles and shape cannot be used at possession start.

These intervals address match-to-match sampling variation. A locked architecture evaluated through nested cross-validation or an external tournament remains necessary for an unbiased generalization claim.

<!-- PROSPECTIVE_VALIDATION_START -->
## Prospective possession-model validation

**Overall status: `PARTIAL_PASS_ROLLBACK`.** Box-entry prediction passed every discrimination, calibration, and paired match-bootstrap gate. The shot challenger improved numerically but its confidence interval crossed zero, so it was rejected. The combined prospective artifact was not deployed and the stable production state was preserved.

| Target | Status | Baseline ROC-AUC | Challenger ROC-AUC | PR-AUC | Brier | ECE | Paired ROC gain (90% interval) |
|---|---|---:|---:|---:|---:|---:|---:|
| Box entry | **PASSED** | 0.6888 | 0.7268 | 0.6131 | 0.1722 | 0.0309 | +0.0155 [+0.0106, +0.0205] |
| Shot | **REJECTED** | 0.6642 | 0.6841 | 0.2686 | 0.0960 | 0.0118 | +0.0038 [-0.0030, +0.0120] |

_This challenger is isolated from 360-VAEP/xT player ratings, transition risk, retrospective possession models, and tactical clustering. Player and team descriptive metrics therefore remain unchanged._
<!-- PROSPECTIVE_VALIDATION_END -->
