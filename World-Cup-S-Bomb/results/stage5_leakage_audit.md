# Stage 5 Leakage and Target-Validity Audit

## Verdict

The current Stage 5 benchmark is valid as a **retrospective possession-outcome
classifier**, subject to the selection and model-selection limitations below.
It is not valid as a model that predicts success at the start of a possession.

Direct outcome columns are excluded from model inputs, outcome-dependent
denominators were removed from both clustering pipelines, match groups are kept
separate during cross-validation, and validation-match player performance is
excluded from player profiles. The remaining problem is temporal: attacking
styles, defensive styles, and defensive-shape averages describe the completed
possession and therefore contain information that was unavailable at its start.

## Audited population

- Tournament possessions in periods 1–4: 11,016
- Stage 5 eligible possessions: 9,685 (87.92%)
- Matches: 64
- Shot positives: 1,207 (12.46%)
- Penalty-area target positives: 3,060 (31.60%)
- Opponent-transition-shot positives: 13 (0.13%)

Eligibility is not outcome-neutral in practice. Shot rate is 12.46% in the
eligible sample and 5.63% in the excluded sample. Penalty-area target rate is
31.60% in the eligible sample and 20.59% in the excluded sample. Reported
performance therefore applies to possessions with sufficient attacking actions
and 360 coverage, not automatically to every tournament possession.

## Safeguards that pass

1. `shot`, goal, xG, penalty-area outcomes, and transition outcomes are absent
   from the Stage 5 predictor lists.
2. Attacking- and defensive-style rate denominators use passes, carries, and
   dribbles only. `shot_count` does not affect clustering eligibility or rate
   features.
3. Imputation, scaling, and categorical encoding are fitted inside each
   cross-validation training fold.
4. `StratifiedGroupKFold` keeps complete matches in either training or
   validation for a fold.
5. Validation-match player components are excluded when player profiles are
   built. Training-row player profiles also leave out the row's own match.
6. Team and player identity strings are not supplied directly to the outcome
   models.

## Temporal and validation limitations

### Full-possession styles

`attacking_style` is assigned from duration, passing, carrying, progression,
width, and pressure behavior over the completed possession. `defensive_style`
is assigned from pressure actions and spatial frames over the completed
possession. These are legitimate retrospective descriptors, but neither is
known at possession start.

### Outcome-proximal defensive shape

Every Stage 5 possession uses at least three 360 frames. Of 1,207 shot-positive
possessions, 1,175 include the actual shot event's freeze frame in the spatial
averages. Consequently, features such as average defender distance, defensive
width, and back-line height often include the defensive state at the shot.

This is temporal leakage for a start-of-possession forecast. It is not direct
label leakage for a retrospective explanatory model.

### Tournament-wide cluster fitting

The attacking and defensive scalers, clipping limits, cluster counts, and
K-Means models are fitted once on the full tournament before the Stage 5
cross-validation split. Validation-match outcomes are not used, but validation
feature distributions influence the style representation. This makes the
benchmark transductive. For a strict unseen-match estimate, clustering must be
fit inside each training fold or frozen from an independent reference dataset.

### Play-pattern timing

The original possession table used the modal play pattern over the completed
possession. Step 3 added `first_play_pattern`, taken from the first
non-administrative event, for prospective layouts. It differs from the modal
field in 6 of 11,016 modeled possessions.

### Winner-selection optimism

Sixteen layout/model candidates are ranked for each target using the same
out-of-fold predictions reported as final performance. The best candidate is
therefore selected and evaluated on the same cross-validation exercise. A
locked final architecture, nested cross-validation, or a separate test set is
needed for an unbiased final performance claim.

### Player-profile caveat

Performance components are cross-fitted correctly, but the player-to-position
lookup is computed from the full tournament. This is a minor source of
validation information for players whose positions are established in held-out
matches. Position lookup should be fold-local in a strict prospective test.

## Timing diagnostic

A five-fold, match-grouped logistic-regression diagnostic produced:

| Target | Feature layout | Log loss | ROC-AUC | PR-AUC |
|---|---|---:|---:|---:|
| Shot | Start context | 0.3540 | 0.6632 | 0.2430 |
| Shot | Start context + both styles | 0.3263 | 0.7665 | 0.2958 |
| Shot | Start context + styles + full-possession shape | 0.2559 | 0.8831 | 0.5125 |
| Penalty-area target | Start context | 0.5532 | 0.6886 | 0.5815 |
| Penalty-area target | Start context + both styles | 0.4785 | 0.8045 | 0.6775 |
| Penalty-area target | Start context + styles + full-possession shape | 0.3672 | 0.8982 | 0.8184 |

Start context contains period, start minute, start coordinates, play pattern,
and competition stage. The large improvement from completed-possession shape
confirms that the current headline performance should not be presented as an
early prediction result.

## Target decisions

| Target | Decision | Reason |
|---|---|---|
| Shot | Approve | 1,207 positives provide adequate support. For prospective use, only information available before the shot cutoff may be used. |
| Penalty-area target | Approve with rename | The implementation is true when the possession records an entry or ends inside the penalty area. It should be described precisely rather than as a pure crossing-event label. |
| Opponent transition shot | Reject from primary Stage 5 | Only 13 positives exist, with 1–4 positives per validation fold. PR-AUC is 0.0055, so the reported ROC-AUC is not evidence of a useful model. |

The later pre-decision transition pipeline does not reuse this rejected target.
It defines whether the opponent reaches the final third or penalty area within
15 seconds of the next possession, producing materially larger samples
(including 259 penalty-area transitions). Those targets are evaluated in
`benchmark_transition_models.py` and remain separate from the retrospective
Stage 5 benchmark.

## Approved feature sets

### Retrospective explanatory model

The existing attacking style, defensive style, and completed-possession
defensive-shape summaries may be used if the output is consistently described
as retrospective classification or explanation. It must not be presented as a
live forecast or causal recommendation.

### Prospective start-context model

Approved inputs:

- Period and possession start minute
- Possession start coordinates
- Competition stage
- First-event play pattern
- Current lineup
- Player profiles computed only from matches preceding or outside the
  evaluation match

Conditionally approved inputs:

- Defensive shape from a clearly defined first 360 snapshot, provided all later
  frames are excluded and the prediction occurs after that snapshot
- Style probabilities predicted from an early window, provided the early-style
  model is itself trained without future-possession features

Not approved for a start-context model:

- Completed-possession attacking-style assignment
- Completed-possession defensive-style assignment
- Any defensive-shape average using later possession frames
- End location, duration, action counts, entries, shots, goals, or xG
- Player performance from the match being predicted

## Required corrections before a coaching recommendation layer

1. Declare the prediction cutoff: possession start or first 360 snapshot.
2. Use the cutoff-safe `first_play_pattern` field added in Step 3.
3. Remove completed-possession styles and shape averages from the prospective
   layout, or replace them with independently predicted early styles and
   first-snapshot shape.
4. Fit style preprocessing inside training folds, or freeze it from an
   independent dataset.
5. Make player-position lookup fold-local.
6. Keep the legacy `transition_conceded` target out of the primary benchmark;
   evaluate the separately defined 15-second transition targets in their
   dedicated pre-decision pipeline.
7. Compare nested feature layouts on identical folds.
8. Lock the selected architecture and evaluate it with nested cross-validation
   or a separate held-out test design.
9. Report coverage and restrict claims to the eligible population.

## Stage 5 conclusion and implementation status

Stage 5 contains useful retrospective signal and its direct leakage safeguards
are materially sound. The reported shot and penalty-area metrics are not valid
evidence of start-of-possession forecasting performance.

Step 3 now separates a cutoff-safe Start Context layout from the retrospective
style, shape, and player-aware layouts; uses `first_play_pattern`; removes the
transition target; and reports a fixed-model feature ablation. Tournament-wide
cluster fitting, fold-local position lookup, external or nested validation, and
eligible-population limits remain unresolved before coaching recommendations.

Step 4 adds a 5,000-replicate match-cluster bootstrap, reports paired uncertainty
against the empirical winner, locks simplicity-aware final retrospective
models, and preserves separate prospective baselines. These intervals quantify
match-to-match variation but do not remove winner-selection optimism.

Step 5 adds a common interpretation procedure for both selected retrospective
models. Feature-group and individual-feature importance are calculated on
held-out match folds by permuting values within matches, with uncertainty
estimated by resampling complete matches. Defensive shape is the dominant
feature group for both targets, and back-line height is the most important
individual input.

Model-response profiles are explicitly labeled as descriptive and noncausal.
SHAP was not included because the selected estimators use different model
families and the correlated shape variables and one-hot style indicators make
individual attributions sensitive to representation and background choices.
This completes the retrospective Stage 5 analysis; the unresolved safeguards
above still apply to any future live-forecast or coaching-recommendation layer.
The separately added transition pipeline addresses a different, cutoff-defined
risk question and should be reported with its own rare-event ranking metrics.
