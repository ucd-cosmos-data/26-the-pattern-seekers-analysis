#!/usr/bin/env python3
"""Unbiased nested cross-validation with fold-local style clustering.

The canonical benchmark (`benchmark_coaching_models.py`) fits the attacking and
defensive style clusters **once, tournament-wide**, and then selects the winning
architecture on the *same* cross-validation it reports. Two optimism sources
remain, both noted in the project README:

1. **Transductive clustering** — validation-match possessions influence the
   clusters the model trains on.
2. **Winner-selection optimism** — the architecture is chosen and scored on one
   cross-validation.

This script removes both for the retrospective ``Tactical + Shape`` layout:

* **Fold-local clustering** — attacking/defensive KMeans are refit on each outer
  training split only (`src/fold_local_clustering.FoldLocalClusterer`) and merely
  *assign* the held-out fold.
* **Nested CV** — an inner cross-validation picks the architecture by average
  precision (PR-AUC); the outer test fold, untouched by clustering or selection,
  is scored once. The averaged outer-fold metrics are the unbiased estimate.

It is additive: it does not modify the production benchmark or its artifacts. It
writes `results/nested_coaching_validation.json` and a short markdown summary.

Runtime note: nested CV trains ``n_candidates x inner_folds x outer_folds``
models per target, so it needs the pinned training environment (Python 3.12 +
xgboost). This is intended as a scheduled / release validation, not a fast check.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline

import benchmark_coaching_models as benchmark

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cluster_attacking_styles import (  # noqa: E402
    MODEL_FEATURES as ATTACKING_FEATURES,
    engineer_model_features as engineer_attacking,
)
from cluster_defensive_styles import (  # noqa: E402
    MODEL_FEATURES as DEFENSIVE_FEATURES,
    engineer_features as engineer_defensive,
)
from src.coaching_selection import operating_point  # noqa: E402
from src.fold_local_clustering import FoldLocalClusterer  # noqa: E402

DEFAULT_POSSESSIONS = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_clusters.csv"
)
DEFAULT_ATTACKING_MODEL = PROJECT_ROOT / "models" / "attacking_style_kmeans.joblib"
DEFAULT_DEFENSIVE_MODEL = PROJECT_ROOT / "models" / "defensive_style_kmeans.joblib"
DEFAULT_JSON = PROJECT_ROOT / "results" / "nested_coaching_validation.json"
DEFAULT_SUMMARY = (
    PROJECT_ROOT / "results" / "MIscellaneous" / "nested_coaching_validation.md"
)

RANDOM_STATE = 42
OUTER_SPLITS = 5
INNER_SPLITS = 5
# Base architectures only; soft-vote ensembles are excluded to bound nested cost.
DEFAULT_CANDIDATES = [
    "Logistic Regression",
    "Random Forest",
    "Gradient Boosting",
    "Histogram Gradient Boosting",
    "XGBoost",
]

TACTICAL_NUMERIC = (
    benchmark.START_CONTEXT_NUMERIC_FEATURES + benchmark.SHAPE_NUMERIC_FEATURES
)
TACTICAL_CATEGORICAL = benchmark.START_CONTEXT_CATEGORICAL_FEATURES + [
    "attacking_style",
    "defensive_style",
]


def resolve_features(data: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Keep only layout features present in the data.

    The style columns are produced per fold, so they are always allowed. Any
    other layout feature missing from the possession file (e.g. a column added
    to the benchmark after this data was last regenerated) is dropped with a
    warning rather than failing the whole run.
    """

    fold_local = {"attacking_style", "defensive_style"}
    numeric = [column for column in TACTICAL_NUMERIC if column in data.columns]
    categorical = [
        column
        for column in TACTICAL_CATEGORICAL
        if column in fold_local or column in data.columns
    ]
    missing = sorted(
        set(TACTICAL_NUMERIC + TACTICAL_CATEGORICAL)
        - set(numeric)
        - set(categorical)
    )
    if missing:
        print(f"WARNING: dropping absent layout features: {', '.join(missing)}")
    return numeric, categorical


def load_selected_k(path: Path, fallback: int) -> int:
    if not path.is_file():
        return fallback
    import joblib

    bundle = joblib.load(path)
    return int(bundle.get("selected_k", fallback))


def style_feature_matrices(data: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Engineer the attacking and defensive clustering matrices for every row.

    ``data`` is already filtered to possessions with valid clusters, so the
    engineered features are finite; we only need the numeric matrices that the
    production clusterers consume.
    """

    attacking = engineer_attacking(data)[0][ATTACKING_FEATURES].to_numpy(dtype=float)
    defensive = engineer_defensive(data)[0][DEFENSIVE_FEATURES].to_numpy(dtype=float)
    return attacking, defensive


def assign_fold_local_styles(
    data: pd.DataFrame,
    attacking_matrix: np.ndarray,
    defensive_matrix: np.ndarray,
    train_index: np.ndarray,
    attacking_k: int,
    defensive_k: int,
) -> pd.DataFrame:
    """Return a copy of ``data`` whose style columns are fit on ``train_index``.

    Clusters are learned from the training rows only and assigned to every row,
    so the held-out fold never influences the clustering it is scored against.
    Labels are fold-local integer ids (prefixed) — their identity only needs to
    be consistent within the fold, which one-hot encoding then handles.
    """

    attacking = FoldLocalClusterer(attacking_k, random_state=RANDOM_STATE)
    attacking.fit(attacking_matrix[train_index])
    defensive = FoldLocalClusterer(defensive_k, random_state=RANDOM_STATE)
    defensive.fit(defensive_matrix[train_index])

    assigned = data.copy()
    assigned["attacking_style"] = [f"A{c}" for c in attacking.predict(attacking_matrix)]
    assigned["defensive_style"] = [f"D{c}" for c in defensive.predict(defensive_matrix)]
    return assigned


def build_pipeline(
    model_name: str, numeric: list[str], categorical: list[str]
) -> Pipeline:
    return Pipeline(
        [
            ("preprocess", benchmark.preprocessor(numeric, categorical)),
            ("model", clone(benchmark.model_definitions()[model_name])),
        ]
    )


def select_inner_model(
    train_data: pd.DataFrame,
    target_column: str,
    candidates: list[str],
    numeric: list[str],
    categorical: list[str],
) -> tuple[str, dict[str, float]]:
    """Pick the architecture with the best inner out-of-fold average precision."""

    columns = categorical + numeric
    truth = train_data[target_column].astype(int).to_numpy()
    inner = StratifiedGroupKFold(
        n_splits=INNER_SPLITS, shuffle=True, random_state=RANDOM_STATE + 1
    )
    inner_splits = list(
        inner.split(train_data, truth, groups=train_data["match_id"])
    )

    scores: dict[str, float] = {}
    for model_name in candidates:
        oof = np.full(len(train_data), np.nan)
        for train_idx, valid_idx in inner_splits:
            pipeline = build_pipeline(model_name, numeric, categorical)
            pipeline.fit(
                train_data.iloc[train_idx][columns],
                truth[train_idx],
            )
            oof[valid_idx] = pipeline.predict_proba(
                train_data.iloc[valid_idx][columns]
            )[:, 1]
        scores[model_name] = float(average_precision_score(truth, oof))

    winner = max(scores, key=scores.get)
    return winner, scores


def nested_validate(
    data: pd.DataFrame,
    attacking_matrix: np.ndarray,
    defensive_matrix: np.ndarray,
    target_key: str,
    attacking_k: int,
    defensive_k: int,
    candidates: list[str],
    numeric: list[str],
    categorical: list[str],
) -> dict[str, Any]:
    target_column = benchmark.TARGETS[target_key]
    columns = categorical + numeric
    truth_all = data[target_column].astype(int).to_numpy()

    outer = StratifiedGroupKFold(
        n_splits=OUTER_SPLITS, shuffle=True, random_state=RANDOM_STATE
    )
    outer_splits = list(outer.split(data, truth_all, groups=data["match_id"]))

    fold_records: list[dict[str, Any]] = []
    pooled_truth: list[np.ndarray] = []
    pooled_probability: list[np.ndarray] = []

    for fold_number, (train_index, test_index) in enumerate(outer_splits, start=1):
        assigned = assign_fold_local_styles(
            data,
            attacking_matrix,
            defensive_matrix,
            train_index,
            attacking_k,
            defensive_k,
        )
        train_data = assigned.iloc[train_index].reset_index(drop=True)
        test_data = assigned.iloc[test_index].reset_index(drop=True)

        winner, inner_scores = select_inner_model(
            train_data, target_column, candidates, numeric, categorical
        )

        pipeline = build_pipeline(winner, numeric, categorical)
        pipeline.fit(train_data[columns], train_data[target_column].astype(int))
        probability = pipeline.predict_proba(test_data[columns])[:, 1]
        truth = test_data[target_column].astype(int).to_numpy()

        metrics = benchmark.score_predictions(truth, probability)
        fold_records.append(
            {
                "fold": fold_number,
                "selected_model": winner,
                "inner_pr_auc": inner_scores,
                "test_rows": int(len(truth)),
                **metrics,
            }
        )
        pooled_truth.append(truth)
        pooled_probability.append(probability)

    truth = np.concatenate(pooled_truth)
    probability = np.concatenate(pooled_probability)

    def summarize(metric: str) -> dict[str, float]:
        values = np.array([record[metric] for record in fold_records], dtype=float)
        return {"mean": float(values.mean()), "std": float(values.std(ddof=1))}

    return {
        "target": target_key,
        "target_column": target_column,
        "design": {
            "outer_splits": OUTER_SPLITS,
            "inner_splits": INNER_SPLITS,
            "grouping": "match_id",
            "selection_metric": "average_precision",
            "clustering": "fold-local (refit on outer-train)",
            "attacking_k": attacking_k,
            "defensive_k": defensive_k,
            "candidates": candidates,
        },
        "outer_fold_summary": {
            metric: summarize(metric)
            for metric in ["pr_auc", "roc_auc", "log_loss", "brier"]
        },
        "selected_models_by_fold": [record["selected_model"] for record in fold_records],
        "pooled_operating_point": operating_point(truth, probability),
        "folds": fold_records,
    }


def write_summary(path: Path, results: list[dict[str, Any]]) -> None:
    lines = [
        "# Nested Cross-Validation (Fold-Local Clustering)",
        "",
        "Unbiased estimate for the retrospective `Tactical + Shape` layout. Style",
        "clusters are refit on each outer training split only, and the winning",
        "architecture is chosen by an inner cross-validation, so the outer test",
        "folds are untouched by clustering or model selection.",
        "",
        "| Target | Outer PR-AUC (mean ± sd) | ROC-AUC | Log loss | Selected models |",
        "|---|---:|---:|---:|---|",
    ]
    for result in results:
        summary = result["outer_fold_summary"]
        models = ", ".join(sorted(set(result["selected_models_by_fold"])))
        lines.append(
            f"| {result['target']} | "
            f"{summary['pr_auc']['mean']:.4f} ± {summary['pr_auc']['std']:.4f} | "
            f"{summary['roc_auc']['mean']:.4f} | "
            f"{summary['log_loss']['mean']:.4f} | {models} |"
        )
    lines.extend(
        [
            "",
            "The averaged outer-fold PR-AUC is directly comparable to the pooled-OOF",
            "PR-AUC in `coaching_model_selection.md`; a drop indicates how much of the",
            "single-CV number was transductive or winner-selection optimism.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--possessions", type=Path, default=DEFAULT_POSSESSIONS)
    parser.add_argument("--attacking-model", type=Path, default=DEFAULT_ATTACKING_MODEL)
    parser.add_argument("--defensive-model", type=Path, default=DEFAULT_DEFENSIVE_MODEL)
    parser.add_argument("--attacking-k", type=int, default=None)
    parser.add_argument("--defensive-k", type=int, default=None)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument(
        "--targets",
        nargs="+",
        default=list(benchmark.TARGETS),
        choices=list(benchmark.TARGETS),
    )
    parser.add_argument("--models", nargs="+", default=DEFAULT_CANDIDATES)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    possessions = pd.read_csv(args.possessions, low_memory=False)
    data = possessions[
        possessions["attacking_style_cluster"].ge(0)
        & possessions["defensive_style_cluster"].ge(0)
        & possessions["period"].le(4)
    ].reset_index(drop=True)

    attacking_k = args.attacking_k or load_selected_k(args.attacking_model, 3)
    defensive_k = args.defensive_k or load_selected_k(args.defensive_model, 4)
    attacking_matrix, defensive_matrix = style_feature_matrices(data)
    numeric, categorical = resolve_features(data)

    results = [
        nested_validate(
            data,
            attacking_matrix,
            defensive_matrix,
            target_key,
            attacking_k,
            defensive_k,
            args.models,
            numeric,
            categorical,
        )
        for target_key in args.targets
    ]

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(
            {
                "purpose": "Unbiased nested CV with fold-local style clustering",
                "random_state": RANDOM_STATE,
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_summary(args.summary_output, results)

    for result in results:
        summary = result["outer_fold_summary"]
        print(
            f"{result['target']}: outer PR-AUC "
            f"{summary['pr_auc']['mean']:.4f} ± {summary['pr_auc']['std']:.4f} "
            f"(models: {', '.join(result['selected_models_by_fold'])})"
        )
    print(f"Wrote {args.json_output}")
    print(f"Wrote {args.summary_output}")


if __name__ == "__main__":
    main()
