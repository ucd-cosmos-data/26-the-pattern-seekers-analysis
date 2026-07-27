# World Cup V4 Model Summary

## V4 Model Explanations

This document is the canonical technical summary for the consolidated World
Cup coaching pipeline. The production pipeline has schema version 4 and uses
the locked `transition-conceded-v2` classifier bundle for rare-event
probabilities. The player-evaluation, spatial, simulation, and reporting layers
are V4.

The system is intended for coaching review, opponent preparation, and
prioritizing possessions for video analysis. It is not a causal model, an
automated lineup selector, or a substitute for medical, scouting, and
match-context judgment.

## System architecture

The pipeline combines four connected layers:

1. **Rare transition classifier:** estimates the probability that a possession
   leads to `transition_conceded`.
2. **Probability calibration and decision gate:** applies Platt calibration and
   abstains when no threshold reaches the required precision.
3. **Hurdle and counterfactual evaluation:** combines calibrated event risk with
   conditional xG, tactical scenarios, lineup context, and substitution
   constraints.
4. **V4 player and spatial evaluation:** integrates event value, pressure,
   tournament minutes, functional roles, successful action endpoints, and
   StatsBomb 360 freeze-frame context.

## Rare-event classification model

| Item | Production value |
|---|---|
| Target | `transition_conceded` |
| Selected classifier | Logistic Regression |
| Serialized model | `models/coaching_model_benchmark_v2.joblib` |
| Calibration | Platt |
| Threshold status | No validated threshold; abstention |
| Training matches | 35 |
| Calibration matches | 10 |
| Threshold-selection matches | 10 |
| Untouched test matches | 9 |
| Test rows / positives | 1,349 / 2 |
| Test positive rate | 0.1483% |
| Unique test probabilities | 1,252 |
| Test Brier score | 0.001478 |
| Test PR-AUC | 0.016655 |
| Test ROC-AUC | 0.742019 |

Logistic Regression was selected from Logistic Regression, Random Forest,
Histogram Gradient Boosting, and XGBoost candidates. Training, calibration,
threshold selection, and test match sets are disjoint. Serialized-artifact
replay reproduces the saved probabilities.

The threshold optimizer did not find a threshold satisfying the required
precision floor. The production behavior is therefore to abstain rather than
emit low-confidence transition warnings. Precision, recall, and F-0.5 are
undefined for this abstaining policy, not zero.

## Tournament out-of-fold validation

| Metric | Result |
|---|---:|
| Matches | 64 |
| Teams | 32 |
| OOF possessions | 9,685 |
| Positive events | 13 |
| Brier score | 0.001339 |
| PR-AUC | 0.005958 |
| ROC-AUC | 0.689341 |
| Unique probabilities | 8,739 |

Every evaluated match was excluded from model fitting and fold calibration.
The nonconstant probability output confirms that the classifier has not
collapsed to a single prediction. The very low PR-AUC nevertheless shows that
individual positive-event identification remains difficult at this event
rate.

## Hurdle and counterfactual layer

The hurdle evaluator estimates expected transition cost from the calibrated
event probability and the conditional xG model. If the classifier abstains or
the calibrated probability is below a validated threshold, the actionable
transition-risk contribution resolves to zero.

Substitution simulations enforce position compatibility, formation
requirements, available minutes, realistic timing, a minimum expected Net xG
gain of `0.0050`, and a match-bootstrap confidence interval strictly above
zero. In the current production run:

| Counterfactual result | Count |
|---|---:|
| Tactical scenarios evaluated | 29,055 |
| Validated substitutions | 0 |
| Suppressed substitutions | 3,608 |

This is a safety result: the model found no substitution with enough evidence
to publish as a validated intervention.

## Player evaluation

Players with fewer than 300 tournament minutes are excluded before ranking.
The current cohort contains 142 of 680 observed players; 538 were removed by
the sample-size cutoff.

For attacking roles, the primary value signal is risk-adjusted OBV per 90.
Turnovers receive a location-sensitive penalty, and a turnover under event or
SB360-derived pressure receives exactly 50% of the normal penalty. This avoids
penalizing difficult high-block possessions as heavily as unpressured losses.

The supplied open-data export does not contain licensed StatsBomb proprietary
OBV. The production artifact therefore uses the explicitly labeled
`open_event_value_fallback`. It must not be described as native proprietary
OBV.

The role composite is standardized with
`groupby("Functional role")`. A score of 50 is the role mean and 10 score
points represent one population standard deviation within that role.

## Standard event, metadata, and StatsBomb 360 distinctions

1. **Standard event data** supplies player actions, outcomes, start locations,
   pass endpoints, carry endpoints, shot xG, and the event-level
   `under_pressure` flag.
2. **Player and match metadata** supplies player identity, team, position,
   lineup context, and tournament minutes.
3. **StatsBomb 360** links event UUIDs to visible actor locations, defensive
   density, nearby-defender counts, and nearest-defender distance.

The spatial layer includes 81,231 successful action endpoints and 72,016 linked
SB360 actor snapshots. A total of 203,454 events have SB360 context, producing
142 player heatmaps over 9,394 pitch-density cells.

StatsBomb 360 contains event-time freeze-frame snapshots, not continuous
optical tracking. The heatmaps represent observed successful endpoints and
visible actor positions; they do not reconstruct unobserved movement between
events.

Fullbacks and wingbacks are protected from the `Holding Anchor` role. Players
above the 35% combined final-third spatial threshold are classified as
`Attacking Wingback`. Hakimi and Dest are currently classified as
`Wide Creator`, not `Holding Anchor`.

## Report artifacts

| Artifact | Count or path |
|---|---|
| Team reports | 32 |
| Player heatmaps | 142 |
| Compiled report files | 64 |
| Final tournament report | `results/reports/final/world_cup_team_performance_and_top_players.md` |
| Pipeline manifest | `results/reports/pipeline_manifest.json` |
| Full validation output | `results/MIscellaneous/eda_validation_report.json` |

## Known limitations

- The event prevalence is approximately 0.13%, leaving only 13 OOF positive
  examples. Metrics and threshold estimates therefore have high uncertainty.
- The current classifier abstains because no tested threshold achieved the
  required precision. It should not be represented as a validated binary alert
  model.
- ROC-AUC is moderate, but PR-AUC is low. For this rare-event problem, PR-AUC,
  calibration, and decision utility are more informative than accuracy.
- Player scores are normalized within functional role and are not valid
  cross-role measures of absolute quality.
- The consolidated team leaderboard currently sorts role-relative scores
  across different roles. This can produce misleading team-wide ordering, such
  as Mbappé appearing fifth for France despite leading France in displayed Net
  xG/90. That ordering is a report-layer limitation and should be corrected
  before treating the list as an overall player rank.
- Open-event value is a documented fallback rather than licensed StatsBomb
  OBV.
- Counterfactual results are predictive scenarios, not causal estimates of
  what would have happened under another tactic or lineup.

## Current validity statement

The pipeline is valid for exploratory, probability-aware coaching support and
video-review prioritization over the supplied tournament data. Its leakage
controls, calibration split, artifact replay, spatial provenance, minute
cutoff, and counterfactual suppression rules are defensible. It is not yet
strong enough for autonomous rare-event alerts or cross-role player ranking.
