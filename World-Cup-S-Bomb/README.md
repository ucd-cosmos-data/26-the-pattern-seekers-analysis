# World Cup S-Bomb

This project uses StatsBomb Open Data from all 64 matches of the 2022 FIFA
World Cup to discover attacking and defensive possession styles, analyze their
observed matchups, and model whether a possession produces a shot or reaches
the penalty area.

The core analysis is complete. Its supervised models are retrospective
possession classifiers: full-possession style and 360 defensive-shape
measurements are not available at possession start, so the results must not be
presented as live forecasts, causal effects, or prescriptive coaching advice.

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

See the following reports for details:

- [`results/attacking_style_summary.md`](results/attacking_style_summary.md)
- [`results/defensive_style_summary.md`](results/defensive_style_summary.md)
- [`results/defensive_matchup_summary.md`](results/defensive_matchup_summary.md)
- [`results/coaching_model_benchmark.md`](results/coaching_model_benchmark.md)
- [`results/coaching_model_selection.md`](results/coaching_model_selection.md)
- [`results/coaching_model_explanations.md`](results/coaching_model_explanations.md)
- [`results/recommendation_model_benchmark.md`](results/recommendation_model_benchmark.md)
- [`results/transition_model_benchmark.md`](results/transition_model_benchmark.md)
- [`results/stage5_leakage_audit.md`](results/stage5_leakage_audit.md)

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
```

The 360 download is cached by match and resumes from valid existing files.
Pass `--force` only when a complete redownload is intended.

Intermediate datasets are ignored because they are large and reproducible.
Reusable model bundles are stored in `models/`; human-readable reports, compact
result tables, and figures are stored in `results/`.

## Validation design and limitations

- Cross-validation keeps complete matches in either training or validation.
- Player performance profiles exclude the validation match.
- Imputation, scaling, and encoding are fitted inside model-training folds.
- Confidence intervals resample complete matches.
- The modeled population contains 9,685 possessions with sufficient attacking
  and 360 coverage, or 87.92% of tournament possessions in periods 1–4.
- Style clustering is fitted tournament-wide before outcome-model validation,
  making the current benchmark transductive.
- The selected architecture and reported performance use the same
  cross-validation exercise, so winner-selection optimism remains.
- Full-possession defensive shape includes the shot frame for 1,175 of 1,207
  shot-positive modeled possessions.

Only the separate Start Context logistic-regression baselines use information
available at possession start. A genuine live model would need a declared
prediction cutoff, early-window features, fold-local style construction, and
nested or external validation.

## Optional extensions

The five-stage core proposal is complete. Optional follow-on analyses from the
proposal that remain open include predicting attacking style from the first
5–10 seconds of a possession and measuring attacking tactical flexibility
across teams.
