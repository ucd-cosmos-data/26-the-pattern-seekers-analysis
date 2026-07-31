# Enhanced Transition Model Benchmark

- Possessions: 9,685
- 15-second final-third transitions: 740 (7.64%)
- 15-second box transitions: 259 (2.67%)
- Validation: five match-held-out folds with strictly prior historical features

## Best PR-AUC models

| Target | Layout | Architecture | Model | PR-AUC | PR lift | ROC-AUC | Log loss | Recall@10% |
|---|---|---|---|---:|---:|---:|---:|---:|
| transition_final_third_15 | Enhanced History | Direct | Gradient Boosting: Weighted | 0.0946 | 1.24× | 0.5607 | 0.3396 | 15.00% |
| transition_box_15 | Rest-Defense Player-Aware | Hierarchical: final third × box | Soft Vote: Unweighted | 0.0393 | 1.47× | 0.5900 | 0.1242 | 14.29% |

Weighted models are retained only if rare-event ranking improves without unacceptable probability degradation. Hierarchical box models estimate P(final third) × P(box | final third).
