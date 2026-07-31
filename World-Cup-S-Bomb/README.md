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

## Active player-ranking pipeline

`scripts/run_pipeline.py` is the production entry point for the extended player
analysis. It preserves the match-cross-fitted VAEP/xT, continuous and
probabilistic role, spatial, network, 360, and off-ball evidence, then publishes
the `ranking-repair-v3.0-qatar-2022` contract:

- **Tournament Impact v3** is signed total contribution in common action-value
  units and determines global and team order.
- **Role Quality v3** is one empirical-Bayes posterior contribution rate and
  determines position and role order.
- **Uncertainty** is a whole-match bootstrap interval/status; it explains
  precision and never becomes another exposure penalty.

Ordinary outfield features use Qatar 2022 periods 1–4 only. Period 5 is retained
solely as a separate shootout channel, so shootout kicks cannot enter ordinary
goals, assists, xG, xA, xT, VAEP, or Tournament Impact. The active score does
not use within-position z-scores as absolute global value, the former repeated
exposure cascade, or the former one-sided defensive publication lift.

Goalkeepers remain a dedicated branch with exactly one ranked main goalkeeper
per team. Continuous play, regular penalties, and shootouts are separate;
shootouts are capped at 10% of the dedicated score. The fallback
`percentile_equivalent_placement` is a publication bridge, not measured
absolute cross-position value.

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

One canonical execution writes the active narrative under `results/reports/`
and the current ranking artifacts under `results/reports/ranking/`:

- `ranking/player_rankings.csv` and `ranking/player_rankings.json` — complete
  feature/profile master data for all eligible players
- `ranking/global_rankings_outfield.csv` — global outfield leaderboard
- `ranking/player_rankings_300plus.csv` and
  `ranking/player_rankings_300plus.json` — 300+-minute outfield leaderboard
- `ranking/goalkeeper_rankings.csv`, `ranking/goalkeeper_rankings.json`, and
  `ranking/goalkeeper_rankings.md` — separate consolidated goalkeeper ranking
- `ranking/unified_tournament_rankings.csv` — compact outfield-only publication
  table
- 32 complete tables under both `ranking/by_team/` and
  `ranking/by_team_unified/`
- `ranking/ranking_methodology.md` and `ranking/ranking_audit.md`
- `canonical/model_summary.{json,md}` and canonical compatibility mirrors
- `canonical/final_summary.md` and final-summary compatibility mirrors
- `docs/final_summary.docx`
- 32 reports under `team_profiles/`
- coverage-qualified reports under `player_profiles/` and `starters/`
- six active outfield ranking/validation figures under `v3_figures/` and one
  current goalkeeper figure under `v5_figures/`
- portable manifests with relative paths and SHA-256 hashes

Versioned duplicate ranking exports and the superseded V4 report tree are not
part of the published results. The release writer removes those stale artifacts
before regenerating the canonical files above.

The canonical run publishes the regenerated leaderboard, selected
learned-or-fallback calibration weights, status counts, and before/after
validation. See the
[`results/reports` index](results/reports/README.md) for the canonical reports
and the boundary between the full player master data, outfield leaderboards,
and the separate goalkeeper ranking.

StatsBomb 360 absences remain missing and are accompanied by evidence and
coverage fields. Public freeze frames identify the event actor but do not
provide stable identities for every off-ball player; consequently, named
player off-ball results are coverage-qualified event-actor proxies, not
optical-tracking movement estimates.

The tournament ranking layer evaluates only the 2022 FIFA World Cup. Formal
`GK/CB/FB/DM/CM/AM/FW` groups and probabilistic roles interpret Role Quality;
they cannot change common-unit Tournament Impact. Names, reputation, teams,
advancement, awards, and external rankings are excluded from scoring.

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
RMSE alone. These learned action values feed the v3 ranking layer; they do not
themselves define global order. Tournament Impact, Role Quality, and
Uncertainty remain separate in the published player cohort.

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
- [`results/reports/canonical/model_summary.md`](results/reports/canonical/model_summary.md)

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

With `notebooks/all_events.csv` present, run the canonical orchestration from
the repository root:

```bash
.venv/bin/python scripts/run_pipeline.py --reuse-validated-oof
```

This executes the event-scope repair, component validation, active v3 ranking
release, reports, figures, manifests, documentation, and artifact validators in
dependency order. The standalone
`quantify_player_rating_uncertainty.py`/`annotate_reports_with_uncertainty.py`
pair remains available only for reproducing historical pre-v3 report packets;
active v3 uncertainty is generated with the ranking itself.

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
| `results/reports/ranking/player_rankings.csv` | Complete feature-rich Qatar 2022 player master data; use the dedicated outfield and goalkeeper files for leaderboard order |
| `results/reports/ranking/unified_tournament_rankings.csv` | Six-field active publication view derived from v3 placement fields |
| `results/reports/ranking/goalkeeper_rankings.csv` | Dedicated 32-goalkeeper consolidated v5 ranking with PSxG-style shot stopping, clutch/state leverage, penalties, shootouts, support play, reliability, and uncertainty |
| `results/reports/final_validation.csv` | Side-by-side OOF metrics for all candidate architectures and the legacy baseline |
| `results/reports/pipeline_manifest.json` | End-to-end runtime, artifact, count, and invariant checks |
| `results/eda_validation_report.json` | Final acceptance and regression-test result |
| `results/reports/canonical/model_summary.md` | Active v3 methodology, champion/challenger gates, event scope, goalkeeper boundary, and retained fallbacks |

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
- The player-ranking formula is an evaluation layer, not a model feature.
  Tournament Impact totals signed common-unit contribution without
  within-position normalization. Role Quality applies one fitted
  empirical-Bayes rate shrinkage; uncertainty is published separately.
- Ordinary player-evaluation outcomes and action values use periods 1–4.
  Period-five shootouts stay in separately named audit/GK fields.

The next-action target is rare: the pooled development target has a positive
rate of approximately 0.118%. Consequently, low RMSE is partly a consequence
of class imbalance; PR-AUC, Brier score, and calibration should be considered
together. Adjacent actions can have overlapping future-action windows, so rows
within a match are not independent even though no match crosses a fold.
Rankings describe this tournament sample and are not causal estimates or
permanent measures of player quality. External competitions are still needed
to assess generalization.

The v3 ranking calculation resamples whole matches and publishes impact
intervals, rank-stability bands, and `stable`/`moderate`/`wide` labels directly
in the active table. This uncertainty changes no score or rank.
`scripts/quantify_player_rating_uncertainty.py` and its standalone outputs are
retained as historical/compatibility diagnostics for the pre-v3 formula; they
do not override the active v3 fields.

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

The five-stage tactical proposal, leak-free learned-value foundation, and
Qatar 2022 ranking-repair v3 release are the active architecture. Component
promotion remains conditional on the recorded champion/challenger and artifact
gates; a failed component retains its frozen champion and is disclosed rather
than hidden. None of the following items blocks use of the existing
retrospective analysis:

1. Predict attacking style from only the first 5–10 seconds of a possession.
2. Measure attacking tactical flexibility across teams.
3. Refit attacking and defensive style clusters inside validation folds and
   use nested cross-validation to remove the remaining Stage 5 transductive and
   winner-selection limitations. **Addressed** by
   `scripts/validate_nested_coaching_models.py` (fold-local clustering + nested
   CV, PR-AUC selection); the production benchmark keeps the fast single-CV path
   and the nested script is the unbiased release-time check.
4. Validate VAEP calibration and player-ranking stability on another
   competition or season. V3 quantifies within-tournament stability by
   whole-match bootstrap; cross-competition validation remains open.
5. Add continuous integration for compilation, lightweight leakage-contract
   tests, and artifact-schema checks. The full 64-match pipeline can remain a
   scheduled or release validation because of its runtime and data footprint.

Repository housekeeping can be handled independently: the historical
`results/MIscellaneous/` directory name may be normalized in a dedicated
link-preserving cleanup, and locally authored presentation material should be
committed only when it is intentionally part of the project deliverables.
