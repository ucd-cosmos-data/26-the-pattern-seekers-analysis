# Coaching Model Explanations

## Scope and method

- These explanations apply only to the selected **retrospective** models. They do not turn completed-possession measurements into possession-start forecasts.
- Permutation importance is evaluated on held-out match folds. Values are shuffled within each match, and positive values mean worse log loss after the information is disrupted.
- Group intervals use a match-cluster bootstrap. They describe match-to-match sampling variation, not causal uncertainty.
- Response profiles substitute one input while holding the recorded values of all other inputs fixed. They describe model behavior and are not intervention effects.

## Selected models

| Target | Model | Layout |
|---|---|---|
| Penalty-area entry | Histogram Gradient Boosting | Tactical + Shape |
| Shot | XGBoost | Tactical + Shape |

## Feature-group importance

| Target | Group | Delta log loss (95% CI) |
|---|---|---:|
| Penalty-area entry | Defensive Shape | +0.5076 (+0.4893–+0.5261) |
| Penalty-area entry | Attacking Style | +0.0755 (+0.0691–+0.0817) |
| Penalty-area entry | Start Context | +0.0230 (+0.0202–+0.0260) |
| Penalty-area entry | Defensive Style | +0.0059 (+0.0048–+0.0070) |
| Shot | Defensive Shape | +0.3063 (+0.2875–+0.3251) |
| Shot | Attacking Style | +0.0122 (+0.0098–+0.0147) |
| Shot | Start Context | +0.0025 (+0.0013–+0.0037) |
| Shot | Defensive Style | +0.0002 (-0.0002–+0.0005) |

## Most important individual inputs

- **Shot:** Back-line height (+0.1293), Mean defender distance (+0.0459), Back-line-height variation (+0.0354), Central defenders (+0.0201), Attacking style (+0.0130).
- **Penalty-area entry:** Back-line height (+0.1799), Back-line-height variation (+0.1046), Attacking style (+0.0779), Central defenders (+0.0444), Defenders behind ball (+0.0133).

## Model response profiles

- **Shot:** changing back-line height from 17.11 to 80.25 changes the final model's mean response from 0.282 to 0.015.
  - For attacking style, the lowest and highest mean substituted responses are Short Under Pressure (0.086) and Patient Build-up (0.140).
  - For defensive style, the lowest and highest mean substituted responses are High-Intensity Press (0.117) and Compact Pressure Block (0.126).
- **Penalty-area entry:** changing back-line height from 17.11 to 80.25 changes the final model's mean response from 0.539 to 0.077.
  - For attacking style, the lowest and highest mean substituted responses are Short Under Pressure (0.177) and Patient Build-up (0.357).
  - For defensive style, the lowest and highest mean substituted responses are High-Intensity Press (0.219) and Compact Pressure Block (0.319).

All categorical substitution profiles are provided in `coaching_effect_profiles.csv`; they carry the same noncausal interpretation.

## Why SHAP is not included

SHAP was deliberately omitted from the primary deliverables. The two selected models use different estimator families, the tactical shape inputs are strongly related to one another, and one-hot style indicators make individual attributions sensitive to representation and background choices. A SHAP view would therefore be less comparable and potentially less stable than the same held-out, match-aware permutation procedure used for both targets. This decision should be revisited only with a predeclared background sample and an attribution-stability analysis.

## Limits

Importance does not establish that changing a feature will change an outcome. Full-possession shape and style can also contain information from after the possession began, including the shot frame for many shot possessions. The results support retrospective pattern description only.
