# Coaching Model Architecture Benchmark

## Design

- Eligible possessions: 9,685
- Matches: 64
- Cross-validation: 5-fold stratified group CV by match
- Derived lineup features: 64
- Player profiles for every validation match were computed without that match.
- Player and team names were excluded from predictive inputs.
- Shot, goal, xG, box-entry, and transition outcomes were excluded from inputs.
- Probabilities are compared primarily by log loss and Brier score; ROC-AUC, PR-AUC, and calibration error are secondary diagnostics.

## Winners

| Target | Layout | Model | Log loss | Brier | ROC-AUC | PR-AUC | ECE |
|---|---|---|---:|---:|---:|---:|---:|
| shot | Tactical + Shape | Soft Vote: LR + XGB | 0.2480 | 0.0778 | 0.8922 | 0.5313 | 0.0094 |
| box_entry | Tactical + Shape | Soft Vote: All | 0.3559 | 0.1129 | 0.9050 | 0.8319 | 0.0140 |
| transition_conceded | Tactical + Shape | Logistic Regression | 0.0095 | 0.0013 | 0.8190 | 0.0055 | 0.0001 |

## Interpretation

This benchmark selects predictive layouts, not causal treatment effects. The next recommendation layer must compare candidate attacking styles under the same context and apply uncertainty and risk constraints.

Player skill values are empirical-Bayes estimates derived from event data and shrunk toward position priors. A future player can be processed with the same component schema without retraining on their identity.
