# Coaching Model Architecture Benchmark

## Design

- Eligible possessions: 9,685
- Matches: 64
- Cross-validation: 5-fold stratified group CV by match
- Derived lineup features: 126
- Player profiles for every validation match were computed without that match.
- Player and team names were excluded from predictive inputs.
- Shot, goal, xG, box-entry, and transition outcomes were excluded from inputs.
- The unsupported 13-positive transition target is excluded from this primary benchmark.
- Probabilities are compared primarily by log loss and Brier score; ROC-AUC, PR-AUC, and calibration error are secondary diagnostics.

## Winners

| Target | Layout | Model | Log loss | Brier | ROC-AUC | PR-AUC | ECE |
|---|---|---|---:|---:|---:|---:|---:|
| shot | Tactical + Shape | Soft Vote: All | 0.2479 | 0.0777 | 0.8935 | 0.5304 | 0.0111 |
| box_entry | Tactical + Shape | Histogram Gradient Boosting | 0.3556 | 0.1134 | 0.9041 | 0.8304 | 0.0110 |

## Fixed-model feature ablation

Every row below uses Logistic Regression on the same match folds so feature-group value is not confounded by changing model families.

| Target | Layout | Timing | Log loss | Improvement | ROC-AUC | PR-AUC | PR-AUC gain |
|---|---|---|---:|---:|---:|---:|---:|
| box_entry | Start Context | Prospective | 0.5532 | — | 0.6888 | 0.5816 | — |
| box_entry | Context + Attack Style | Retrospective | 0.5098 | +0.0434 | 0.7691 | 0.6177 | +0.0361 |
| box_entry | Context + Both Styles | Retrospective | 0.4784 | +0.0314 | 0.8045 | 0.6776 | +0.0599 |
| box_entry | Tactical + Shape | Retrospective | 0.3671 | +0.1113 | 0.8982 | 0.8184 | +0.1408 |
| box_entry | Player-Aware | Retrospective | 0.3984 | -0.0312 | 0.8814 | 0.7884 | -0.0300 |
| shot | Start Context | Prospective | 0.3538 | — | 0.6642 | 0.2441 | — |
| shot | Context + Attack Style | Retrospective | 0.3457 | +0.0081 | 0.7154 | 0.2434 | -0.0007 |
| shot | Context + Both Styles | Retrospective | 0.3261 | +0.0196 | 0.7668 | 0.2972 | +0.0538 |
| shot | Tactical + Shape | Retrospective | 0.2558 | +0.0703 | 0.8831 | 0.5134 | +0.2163 |
| shot | Player-Aware | Retrospective | 0.2811 | -0.0253 | 0.8599 | 0.4623 | -0.0511 |

## Interpretation

This benchmark selects predictive layouts, not causal treatment effects. Only the Start Context layout is available at possession start. Layouts containing styles or full-possession shape are retrospective and must not be presented as early forecasts.

Player skill values are empirical-Bayes estimates derived from event data and shrunk toward position priors. A future player can be processed with the same component schema without retraining on their identity.

<!-- PROSPECTIVE_VALIDATION_START -->
## Prospective possession-model validation

**Overall status: `PARTIAL_PASS_ROLLBACK`.** Box-entry prediction passed every discrimination, calibration, and paired match-bootstrap gate. The shot challenger improved numerically but its confidence interval crossed zero, so it was rejected. The combined prospective artifact was not deployed and the stable production state was preserved.

| Target | Status | Baseline ROC-AUC | Challenger ROC-AUC | PR-AUC | Brier | ECE | Paired ROC gain (90% interval) |
|---|---|---:|---:|---:|---:|---:|---:|
| Box entry | **PASSED** | 0.6888 | 0.7268 | 0.6131 | 0.1722 | 0.0309 | +0.0155 [+0.0106, +0.0205] |
| Shot | **REJECTED** | 0.6642 | 0.6841 | 0.2686 | 0.0960 | 0.0118 | +0.0038 [-0.0030, +0.0120] |

_This challenger is isolated from 360-VAEP/xT player ratings, transition risk, retrospective possession models, and tactical clustering. Player and team descriptive metrics therefore remain unchanged._
<!-- PROSPECTIVE_VALIDATION_END -->
