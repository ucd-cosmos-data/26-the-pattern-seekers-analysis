# Pre-Decision Recommendation Model Benchmark

- Unique possessions: 9,685
- Matches: 64
- Validation: five match-held-out folds with fold-specific historical features
- Exact current-possession defensive shape is excluded
- Team and player performance inputs use only earlier matches available to the training fold

## Classification winners

| Target | Layout | Model | Log loss | Brier | ROC-AUC | PR-AUC |
|---|---|---|---:|---:|---:|---:|
| shot | Context + History | XGBoost | 0.3341 | 0.1001 | 0.7272 | 0.2824 |
| box_entry | Context + History | Soft Vote: Boosting | 0.4858 | 0.1640 | 0.7857 | 0.6487 |
| transition_box_15 | Player-Aware | Gradient Boosting | 0.1233 | 0.0261 | 0.5723 | 0.0334 |
| transition_shot_15 | Player-Aware | Gradient Boosting | 0.0810 | 0.0150 | 0.5413 | 0.0156 |

## Net-value result

- Context + History: RMSE 0.0686, MAE 0.0237, Spearman 0.2482
- Player-Aware: RMSE 0.0687, MAE 0.0239, Spearman 0.2491

These results measure prediction, not causal treatment effects. Candidate-style simulation must hold all other inputs constant and report uncertainty.
