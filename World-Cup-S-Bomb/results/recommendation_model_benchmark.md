# Pre-Decision Recommendation Model Benchmark

- Unique possessions: 9,685
- Matches: 64
- Validation: five match-held-out folds with fold-specific historical features
- Exact current-possession defensive shape is excluded
- Team and player performance inputs use only earlier matches available to the training fold

## Classification winners

| Target | Layout | Model | Log loss | Brier | ROC-AUC | PR-AUC |
|---|---|---|---:|---:|---:|---:|
| shot | Context + History | XGBoost | 0.3338 | 0.1001 | 0.7299 | 0.2802 |
| box_entry | Context + History | XGBoost | 0.4866 | 0.1645 | 0.7841 | 0.6454 |
| transition_box_15 | Player-Aware | Soft Vote: All | 0.1233 | 0.0261 | 0.5835 | 0.0369 |
| transition_shot_15 | Player-Aware | Gradient Boosting | 0.0804 | 0.0150 | 0.5542 | 0.0163 |

## Net-value result

- Context + History: RMSE 0.0686, MAE 0.0237, Spearman 0.2508
- Player-Aware: RMSE 0.0687, MAE 0.0238, Spearman 0.2534

These results measure prediction, not causal treatment effects. Candidate-style simulation must hold all other inputs constant and report uncertainty.
