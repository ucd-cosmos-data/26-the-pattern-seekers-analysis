# World Cup S-Bomb

This project uses StatsBomb Open Data from all 64 matches of the 2022 FIFA
World Cup to discover attacking and defensive possession styles, analyze their
observed matchups, model whether a possession produces a shot or reaches the
penalty area, and evaluate players with a match-cross-fitted VAEP/xT pipeline.

The core analysis is complete. The possession-style outcome models are
retrospective classifiers: full-possession style and 360 defensive-shape
measurements are not available at possession start, so those results must not
be presented as live forecasts, causal effects, or prescriptive coaching
advice. The separate player-evaluation pipeline uses next-action targets,
pre-action features, match-level out-of-fold scoring, and cross-fitted xT.

## Research workflow

1. Convert event data into one row per possession.
2. Discover three attacking styles with K-Means.
3. Derive 360 defensive-shape features and discover four defensive styles.
4. Describe attacking-style effectiveness against each defensive style.
5. Benchmark, select, and explain models for shot and penalty-area-entry
   outcomes.

A separate pre-decision pipeline builds strictly prior team/player history and
models 15-second counterattack risk using final-third and penalty-area
transitions. It is distinct from the retrospective Stage 5 outcome models.

The original proposal is in
[`data/raw/info.md`](data/raw/info.md).

## Role-aware player pipeline

`scripts/run_pipeline.py` is the production entry point for the extended player
analysis. It preserves match-cross-fitted VAEP/xT calculations, K-Means
functional roles, and legacy comparison columns. V2 rates all eligible
outfield players from 45 minutes and goalkeepers from 90 minutes; 300 minutes
is only the primary outfield reliability label. It adds pre-action score,
time, opponent-strength, and game-phase context as a VAEP challenger that is
accepted only by a development-OOF non-inferiority gate (the canonical run
retains the baseline feature set); continuous role
vectors; probabilistic GMM roles; spatial and passing-network features;
explicit role-weighted offensive/defensive channels; team-disjoint ElasticNet
calibration; xD-style defensive disruption; sample-adjusted completeness;
off-ball scoring; and 450-minute empirical-Bayes shrinkage. Goalkeepers use a
weighted seven-component matrix including high-leverage saves.

Run the complete pipeline from the repository root:

```powershell
python .\scripts\run_pipeline.py
```

For a quick reproducibility run using already-validated legacy outputs:

```powershell
python .\scripts\run_pipeline.py --skip-legacy-foundation
```

The lightweight spatial attention challenger is opt-in:

```powershell
python .\scripts\run_pipeline.py --skip-legacy-foundation --enable-attention
```

Its baseline and attention predictions are evaluated out of fold with
match-disjoint `GroupKFold`. When it meets both retrospective and prospective
ROC-AUC/ECE gates, its out-of-fold context signal enters a second
match-grouped ElasticNet fit. Failure prints the documented fallback message
and continues with the role-aware layer. All attention is causal; future
events are masked.

One canonical execution writes the explicit V5 artifacts below under
`results/reports/`, plus unversioned compatibility aliases:

- `v5_player_rankings.csv` and `v5_player_rankings.json`
- `v5_coaches_notebook.md`
- `model_summary.json` and `model_summary.md`
- `final_summary.md`
- 32 reports under `team_profiles/`
- coverage-qualified individual reports under `player_profiles/`
- `v5_rating_validation_comparison.csv`
- four diagnostic plots under `v5_figures/`
- `v5_artifact_manifest.json` with SHA-256 hashes

The same execution refreshes the downstream compatibility tables in
`data/processed/player_evaluations.csv`,
`data/processed/player_leaderboard.csv`,
`results/reports/player_leaderboard.csv`, and
`results/reports/team_player_leaderboards.csv`. The V4 possession and
transition-model packets remain historical records; obsolete V4 final/model
summaries are removed only after the complete V5 artifact set passes its
publication checks.

The canonical run publishes the regenerated leaderboard, selected
learned-or-fallback calibration weights, status counts, and before/after
validation. See the
[`results/reports` index](results/reports/README.md) for the canonical reports
and the boundary between V5 player values and historical V4 tactical outputs.

StatsBomb 360 absences remain missing and are accompanied by evidence and
coverage fields. Public freeze frames identify the event actor but do not
provide stable identities for every off-ball player; consequently, named
player off-ball results are coverage-qualified event-actor proxies, not
optical-tracking movement estimates.

## Main results

The attacking clusters are:

- Patient Build-up: 50.22% of eligible attacking possessions
- Short Under Pressure: 34.56%
- Direct Long Play: 15.22%

The defensive clusters are:

- Wide Retreating Block: 52.57% of eligible 360 possessions
- Compact Pressure Block: 32.23%
- High-Intensity Press: 7.70%
- Set-Piece Compact Shape: 7.51%

The final retrospective outcome models are:

| Target | Selected model | Log loss (95% match-bootstrap CI) | ROC-AUC | PR-AUC |
|---|---|---:|---:|---:|
| Shot | XGBoost | 0.2486 (0.2368–0.2606) | 0.8918 | 0.5238 |
| Penalty-area entry | Histogram Gradient Boosting | 0.3556 (0.3446–0.3660) | 0.9041 | 0.8304 |

Defensive shape is the dominant feature group for both targets. Back-line
height is the most important individual input under held-out, within-match
permutation. These are predictive associations, not estimates of what would
happen if a team changed its defensive line.

The leak-free player-evaluation comparison is:

| Model | Evaluation | ROC-AUC | PR-AUC | Brier | RMSE |
|---|---|---:|---:|---:|---:|
| XGBoost 360-VAEP | Development match OOF | 0.9490 | 0.0848 | 0.001123 | 0.033511 |
| CatBoost 360-VAEP | Development match OOF | 0.9445 | 0.0932 | 0.001129 | 0.033596 |
| Logistic Regression 360-VAEP | Development match OOF | 0.9310 | 0.0210 | 0.001167 | 0.034161 |
| Legacy transition classifier | Tournament OOF | 0.6893 | 0.0060 | 0.001339 | 0.036593 |
| Selected XGBoost 360-VAEP | Final untouched test | 0.9672 | 0.1499 | 0.001494 | 0.038652 |

The legacy transition classifier predicts a different target and is shown as a
reporting baseline, not as a VAEP model-selection candidate. Because positive
next-action windows are rare, PR-AUC and calibration are more informative than
RMSE alone. The final role-relative hierarchy rates the 45/90-minute eligible
cohort and exposes separate high-reliability ranks.

See the following reports for details:

- [`results/MIscellaneous/attacking_style_summary.md`](results/MIscellaneous/attacking_style_summary.md)
- [`results/MIscellaneous/defensive_style_summary.md`](results/MIscellaneous/defensive_style_summary.md)
- [`results/MIscellaneous/defensive_matchup_summary.md`](results/MIscellaneous/defensive_matchup_summary.md)
- [`results/MIscellaneous/coaching_model_benchmark.md`](results/MIscellaneous/coaching_model_benchmark.md)
- [`results/MIscellaneous/coaching_model_selection.md`](results/MIscellaneous/coaching_model_selection.md)
- [`results/MIscellaneous/coaching_model_explanations.md`](results/MIscellaneous/coaching_model_explanations.md)
- [`results/MIscellaneous/recommendation_model_benchmark.md`](results/MIscellaneous/recommendation_model_benchmark.md)
- [`results/MIscellaneous/transition_model_benchmark.md`](results/MIscellaneous/transition_model_benchmark.md)
- [`results/MIscellaneous/stage5_leakage_audit.md`](results/MIscellaneous/stage5_leakage_audit.md)
- [`results/reports/final_validation.csv`](results/reports/final_validation.csv)
- [`results/eda_validation_report.json`](results/eda_validation_report.json)
- [`results/reports/model_summary.md`](results/reports/model_summary.md)

## Environment

Use Python 3.12. From this directory:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On macOS, XGBoost also requires the OpenMP runtime:

```bash
brew install libomp
```

Dependencies are pinned in [`requirements.txt`](requirements.txt).

## Input data

The analysis expects:

- `data/raw/matches.csv`: the tracked 64-match tournament manifest
- `notebooks/all_events.csv`: flattened StatsBomb events for competition 43,
  season 106
- StatsBomb 360 frames downloaded by `scripts/cache_360_frames.py`

The event export is intentionally ignored because of its size. It can be
recreated with the acquisition cells in `notebooks/fifa_all_files.ipynb`, which
use `statsbombpy` and concatenate the event frames for every match.

StatsBomb Open Data is made available for research and analysis under
StatsBomb's open-data terms. Follow the attribution requirements in the
upstream dataset.

## Reproduce the pipeline

With `notebooks/all_events.csv` present, run these commands in order:

```bash
.venv/bin/python scripts/preprocess_possessions.py
.venv/bin/python scripts/cluster_attacking_styles.py
.venv/bin/python scripts/cache_360_frames.py
.venv/bin/python scripts/build_defensive_features.py
.venv/bin/python scripts/cluster_defensive_styles.py
.venv/bin/python scripts/analyze_defensive_matchups.py
.venv/bin/python scripts/build_player_skill_inputs.py
.venv/bin/python scripts/benchmark_coaching_models.py
.venv/bin/python scripts/select_coaching_models.py
.venv/bin/python scripts/explain_coaching_models.py
.venv/bin/python scripts/build_recommendation_features.py
.venv/bin/python scripts/benchmark_recommendation_models.py
.venv/bin/python scripts/benchmark_transition_models.py
.venv/bin/python scripts/run_team_simulation_reports.py
.venv/bin/python scripts/quantify_player_rating_uncertainty.py
.venv/bin/python scripts/annotate_reports_with_uncertainty.py
.venv/bin/python scripts/eda_validation_checks.py --final
```

`quantify_player_rating_uncertainty.py` writes the per-player uncertainty table;
`annotate_reports_with_uncertainty.py` then folds those confidence figures into
the compiled team markdowns. Both are additive and idempotent — they change no
grade — and must run after `run_team_simulation_reports.py` regenerates the
reports, so the annotations are not lost.

The 360 download is cached by match and resumes from valid existing files.
Pass `--force` only when a complete redownload is intended.

`run_team_simulation_reports.py` performs the consolidated player evaluation,
match-level OOF audit, simulations, and report generation. A repeated reporting
run can reuse the existing leakage-audited 64-match legacy transition outputs:

```bash
.venv/bin/python scripts/run_team_simulation_reports.py --reuse-validated-oof
```

This option does not reuse VAEP candidate predictions: XGBoost, CatBoost, and
Logistic Regression are still evaluated on the shared development folds, xT is
still cross-fitted by match, and the selected architecture still receives one
final untouched-test evaluation.

The final validation command exits nonzero if any acceptance gate fails,
including partition overlap, missing OOF action scores, forbidden post-action
features, player-hierarchy invariants, artifact replay, or report completeness.

Intermediate datasets are ignored because they are large and reproducible.
Reusable model bundles are stored in `models/`; human-readable reports, compact
result tables, and figures are stored in `results/`.

### Primary generated artifacts

| Artifact | Purpose |
|---|---|
| `models/vaep_360_xt.joblib` | Selected calibrated VAEP models, feature schema, partitions, and cross-fitted xT grid |
| `data/processed/player_evaluations.csv` | Role-relative values for the 45-minute outfield / 90-minute goalkeeper cohort, with reliability statuses |
| `data/processed/player_event_value_audit.parquet` | Per-action targets, OOF/test probabilities, xT values, and scoring-partition provenance |
| `data/processed/player_evaluation_provenance.json` | Feature contract, split assignments, metrics, and leakage controls |
| `results/reports/final_validation.csv` | Side-by-side OOF metrics for all candidate architectures and the legacy baseline |
| `results/reports/pipeline_manifest.json` | End-to-end runtime, artifact, count, and invariant checks |
| `results/eda_validation_report.json` | Final acceptance and regression-test result |
| `results/reports/model_summary.md` | Current methodology, validation gates, learned coefficients, goalkeeper audit, and player hierarchy |

## Validation design and limitations

### VAEP/xT player evaluation

- Labels cover only the next three actions (offsets 1–3); the current action's
  result, endpoint, completion flag, goal, and shot xG are excluded.
- Development cross-validation keeps complete matches in either training or
  validation. Every development action receives an OOF probability, while
  test actions are scored only by the final development-fitted model.
- XGBoost, CatBoost, and Logistic Regression use the same development folds.
  Architecture selection is based only on development OOF metrics, and the
  disjoint 10-match test partition is opened once for final evaluation.
- xT grids are fitted outside the match partition they score. Deterministic
  feature hashing and fixed missing-value defaults avoid learning preprocessing
  state from the test partition; Logistic Regression scaling is fold-local.
- The player-rating formula is an evaluation layer, not a model feature.
  Role-weighted offense/defense channels, calibrated composite components,
  and xD are shrunk toward the player's position-group mean using
  `minutes/(minutes+450)`.

The next-action target is rare: the pooled development target has a positive
rate of approximately 0.118%. Consequently, low RMSE is partly a consequence
of class imbalance; PR-AUC, Brier score, and calibration should be considered
together. Adjacent actions can have overlapping future-action windows, so rows
within a match are not independent even though no match crosses a fold.
Rankings describe this tournament sample and are not causal estimates or
permanent measures of player quality. External competitions are still needed
to assess generalization.

`scripts/quantify_player_rating_uncertainty.py` attaches match-sampling
uncertainty to every rating (a match-cluster bootstrap that reruns the exact
production formula on resampled matches). It changes no grade — it reports a
standard error, confidence interval, rank stability, and, per team, the
probability that the #1 player truly outranks the #2. Outputs:
`results/reports/player_rating_uncertainty.csv` and
`results/MIscellaneous/player_rating_uncertainty.md`. Read the point ranking
alongside these: several team leads are within sampling noise (e.g. the
Argentina #1 gap is a lean, not a separation), which the bare ranking hides.

### Retrospective possession models

- Cross-validation keeps complete matches in either training or validation.
- Player-history profiles exclude the validation match.
- Imputation, scaling, and encoding are fitted inside model-training folds.
- Confidence intervals resample complete matches.
- The modeled population contains 9,685 possessions with sufficient attacking
  and 360 coverage, or 87.92% of tournament possessions in periods 1–4.
- Style clustering is fitted tournament-wide before outcome-model validation,
  making the production Stage 5 benchmark transductive. `scripts/validate_nested_coaching_models.py`
  now provides an unbiased companion estimate with fold-local clustering (clusters
  refit on each outer training split only).
- The production benchmark selects the architecture and reports performance on the
  same cross-validation, so winner-selection optimism remains there; the nested
  script removes it by choosing the model in an inner loop and scoring the untouched
  outer fold once.
- Model selection is keyed on average precision (PR-AUC), the imbalance-aware
  metric, with precision/recall reported at an operating threshold (see
  `results/coaching_model_selection.md` and `results/coaching_model_operating_points.csv`).
- Full-possession defensive shape includes the shot frame for 1,175 of 1,207
  shot-positive modeled possessions.

Only the separate Start Context logistic-regression baselines use information
available at possession start. A genuine live model would need a declared
prediction cutoff, early-window features, fold-local style construction, and
nested or external validation.

## Project status and optional extensions

The five-stage tactical proposal and the leak-free V5 player-evaluation
pipeline are complete. The production pipeline and final acceptance report pass,
so none of the following items blocks use of the existing retrospective
analysis:

1. Predict attacking style from only the first 5–10 seconds of a possession.
2. Measure attacking tactical flexibility across teams.
3. Refit attacking and defensive style clusters inside validation folds and
   use nested cross-validation to remove the remaining Stage 5 transductive and
   winner-selection limitations. **Addressed** by
   `scripts/validate_nested_coaching_models.py` (fold-local clustering + nested
   CV, PR-AUC selection); the production benchmark keeps the fast single-CV path
   and the nested script is the unbiased release-time check.
4. Validate VAEP calibration and player-ranking stability on another
   competition or season. Within-tournament ranking stability is now quantified
   by `scripts/quantify_player_rating_uncertainty.py`; cross-competition
   validation remains open.
5. Add continuous integration for compilation, lightweight leakage-contract
   tests, and artifact-schema checks. The full 64-match pipeline can remain a
   scheduled or release validation because of its runtime and data footprint.

Repository housekeeping can be handled independently: the historical
`results/MIscellaneous/` directory name may be normalized in a dedicated
link-preserving cleanup, and locally authored presentation material should be
committed only when it is intentionally part of the project deliverables.
