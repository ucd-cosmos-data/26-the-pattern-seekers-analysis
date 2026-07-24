#!/usr/bin/env python3
"""Benchmark enhanced direct and hierarchical rare-event transition models."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from benchmark_coaching_models import score_predictions


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_recommendation_features.csv"
)
DEFAULT_LEADERBOARD = (
    PROJECT_ROOT / "results" / "transition_model_leaderboard.csv"
)
DEFAULT_FOLDS = PROJECT_ROOT / "results" / "transition_model_fold_metrics.csv"
DEFAULT_PREDICTIONS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_transition_oof_predictions.csv"
)
DEFAULT_REPORT = PROJECT_ROOT / "results" / "transition_model_benchmark.md"

RANDOM_STATE = 42
CATEGORICAL_FEATURES = [
    "attacking_style",
    "first_play_pattern",
    "competition_stage",
    "score_state",
]
CONTEXT_FEATURES = [
    "period",
    "start_minute",
    "start_x",
    "start_y",
    "score_difference",
]
TARGETS = {
    "transition_final_third_15": "transition_final_third_15",
    "transition_box_15": "transition_box_15",
}


def model_specs() -> dict[str, tuple[object, bool]]:
    return {
        "Logistic Regression": (
            LogisticRegression(
                C=0.5,
                max_iter=2_000,
                solver="lbfgs",
                random_state=RANDOM_STATE,
            ),
            False,
        ),
        "Logistic Regression: Weighted": (
            LogisticRegression(
                C=0.5,
                max_iter=2_000,
                solver="lbfgs",
                random_state=RANDOM_STATE,
            ),
            True,
        ),
        "Random Forest": (
            RandomForestClassifier(
                n_estimators=400,
                min_samples_leaf=8,
                max_features=0.7,
                n_jobs=2,
                random_state=RANDOM_STATE,
            ),
            False,
        ),
        "Gradient Boosting": (
            GradientBoostingClassifier(
                n_estimators=300,
                learning_rate=0.03,
                max_depth=2,
                min_samples_leaf=10,
                subsample=0.85,
                random_state=RANDOM_STATE,
            ),
            False,
        ),
        "Gradient Boosting: Weighted": (
            GradientBoostingClassifier(
                n_estimators=300,
                learning_rate=0.03,
                max_depth=2,
                min_samples_leaf=10,
                subsample=0.85,
                random_state=RANDOM_STATE,
            ),
            True,
        ),
        "Histogram Gradient Boosting": (
            HistGradientBoostingClassifier(
                learning_rate=0.04,
                max_iter=300,
                max_leaf_nodes=15,
                min_samples_leaf=15,
                l2_regularization=2.0,
                random_state=RANDOM_STATE,
            ),
            False,
        ),
        "XGBoost": (
            XGBClassifier(
                n_estimators=450,
                learning_rate=0.03,
                max_depth=3,
                min_child_weight=8,
                subsample=0.85,
                colsample_bytree=0.8,
                reg_lambda=3.0,
                objective="binary:logistic",
                eval_metric="logloss",
                n_jobs=2,
                random_state=RANDOM_STATE,
            ),
            False,
        ),
        "XGBoost: Weighted": (
            XGBClassifier(
                n_estimators=450,
                learning_rate=0.03,
                max_depth=3,
                min_child_weight=8,
                subsample=0.85,
                colsample_bytree=0.8,
                reg_lambda=3.0,
                objective="binary:logistic",
                eval_metric="logloss",
                n_jobs=2,
                random_state=RANDOM_STATE,
            ),
            True,
        ),
    }


def preprocessor(numeric_features: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric_features,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "one_hot",
                            OneHotEncoder(
                                handle_unknown="ignore", sparse_output=False
                            ),
                        ),
                    ]
                ),
                CATEGORICAL_FEATURES,
            ),
        ],
        sparse_threshold=0,
    )


def layouts(data: pd.DataFrame) -> dict[str, list[str]]:
    history = [
        column
        for column in data
        if column.startswith(("team_", "opponent_", "candidate_"))
    ]
    players = [
        column
        for column in data
        if column.startswith(
            (
                "att_",
                "def_",
                "opp_counter_",
                "matchup_",
            )
        )
    ]
    return {
        "Enhanced History": CONTEXT_FEATURES + history,
        "Rest-Defense Player-Aware": CONTEXT_FEATURES + history + players,
    }


def sqrt_balance_weights(truth: pd.Series) -> np.ndarray:
    positives = max(int(truth.sum()), 1)
    negatives = max(len(truth) - positives, 1)
    positive_weight = min(float(np.sqrt(negatives / positives)), 10.0)
    return np.where(truth.to_numpy(dtype=int) == 1, positive_weight, 1.0)


def fit_probability(
    estimator: object,
    weighted: bool,
    numeric_features: list[str],
    train: pd.DataFrame,
    test: pd.DataFrame,
    target: str,
) -> np.ndarray:
    columns = CATEGORICAL_FEATURES + numeric_features
    pipeline = Pipeline(
        [
            ("preprocess", preprocessor(numeric_features)),
            ("model", clone(estimator)),
        ]
    )
    fit_params = {}
    if weighted:
        fit_params["model__sample_weight"] = sqrt_balance_weights(train[target])
    pipeline.fit(train[columns], train[target].astype(int), **fit_params)
    return pipeline.predict_proba(test[columns])[:, 1]


def ranking_metrics(
    truth: np.ndarray, probability: np.ndarray
) -> dict[str, float]:
    metrics: dict[str, float] = {}
    prevalence = float(truth.mean())
    order = np.argsort(-probability)
    for share in (0.05, 0.10, 0.20):
        count = max(1, int(np.ceil(len(truth) * share)))
        selected = truth[order[:count]]
        captured = selected.sum() / max(truth.sum(), 1)
        selected_rate = selected.mean()
        label = int(100 * share)
        metrics[f"recall_at_{label}pct"] = float(captured)
        metrics[f"lift_at_{label}pct"] = float(
            selected_rate / prevalence if prevalence > 0 else 0
        )
    return metrics


def evaluate_frame(frame: pd.DataFrame) -> dict[str, float]:
    truth = frame["truth"].to_numpy(dtype=int)
    probability = frame["probability"].to_numpy(dtype=float)
    return {
        **score_predictions(truth, probability),
        **ranking_metrics(truth, probability),
    }


def direct_predictions(
    data: pd.DataFrame,
    feature_layouts: dict[str, list[str]],
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for layout, numeric in feature_layouts.items():
        for target_name, target in TARGETS.items():
            for model_name, (estimator, weighted) in model_specs().items():
                for fold in sorted(data["validation_fold"].unique()):
                    fold_data = data[data["validation_fold"].eq(fold)]
                    train = fold_data[~fold_data["is_test_fold"]]
                    test = fold_data[fold_data["is_test_fold"]]
                    probability = fit_probability(
                        estimator, weighted, numeric, train, test, target
                    )
                    frame = test[
                        ["possession_uid", "match_id", "validation_fold"]
                    ].copy()
                    frame["truth"] = test[target].astype(int).to_numpy()
                    frame["probability"] = probability
                    frame["layout"] = layout
                    frame["target"] = target_name
                    frame["model"] = model_name
                    frame["architecture"] = "Direct"
                    frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def hierarchical_box_predictions(
    data: pd.DataFrame,
    feature_layouts: dict[str, list[str]],
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for layout, numeric in feature_layouts.items():
        for model_name, (estimator, weighted) in model_specs().items():
            for fold in sorted(data["validation_fold"].unique()):
                fold_data = data[data["validation_fold"].eq(fold)]
                train = fold_data[~fold_data["is_test_fold"]]
                test = fold_data[fold_data["is_test_fold"]]
                final_probability = fit_probability(
                    estimator,
                    weighted,
                    numeric,
                    train,
                    test,
                    "transition_final_third_15",
                )
                conditional_train = train[
                    train["transition_final_third_15"].eq(1)
                ]
                conditional_probability = fit_probability(
                    estimator,
                    weighted,
                    numeric,
                    conditional_train,
                    test,
                    "transition_box_15",
                )
                frame = test[
                    ["possession_uid", "match_id", "validation_fold"]
                ].copy()
                frame["truth"] = test["transition_box_15"].astype(int).to_numpy()
                frame["probability"] = final_probability * conditional_probability
                frame["layout"] = layout
                frame["target"] = "transition_box_15"
                frame["model"] = model_name
                frame["architecture"] = "Hierarchical: final third × box"
                frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def ensemble_predictions(predictions: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    unweighted_models = [
        "Logistic Regression",
        "Random Forest",
        "Gradient Boosting",
        "Histogram Gradient Boosting",
        "XGBoost",
    ]
    weighted_models = [
        "Logistic Regression: Weighted",
        "Gradient Boosting: Weighted",
        "XGBoost: Weighted",
    ]
    group_columns = ["layout", "target", "architecture"]
    for keys, group in predictions.groupby(group_columns):
        for name, members in [
            ("Soft Vote: Unweighted", unweighted_models),
            ("Soft Vote: Weighted", weighted_models),
        ]:
            subset = group[group["model"].isin(members)]
            pivot = subset.pivot_table(
                index=["possession_uid", "match_id", "validation_fold", "truth"],
                columns="model",
                values="probability",
            )
            if not set(members).issubset(pivot.columns):
                continue
            frame = pivot[members].mean(axis=1).rename("probability").reset_index()
            frame["layout"], frame["target"], frame["architecture"] = keys
            frame["model"] = name
            frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def summarize(
    predictions: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    leaderboard_records: list[dict[str, object]] = []
    fold_records: list[dict[str, object]] = []
    keys = ["layout", "target", "model", "architecture"]
    for values, group in predictions.groupby(keys):
        metrics = evaluate_frame(group)
        leaderboard_records.append(
            {
                **dict(zip(keys, values)),
                "rows": len(group),
                "positive_rate": group["truth"].mean(),
                **metrics,
            }
        )
        for fold, fold_group in group.groupby("validation_fold"):
            fold_records.append(
                {
                    **dict(zip(keys, values)),
                    "fold": fold,
                    "rows": len(fold_group),
                    "positive_rate": fold_group["truth"].mean(),
                    **evaluate_frame(fold_group),
                }
            )
    leaderboard = pd.DataFrame(leaderboard_records)
    leaderboard["pr_lift_over_prevalence"] = (
        leaderboard["pr_auc"] / leaderboard["positive_rate"]
    )
    leaderboard["pr_rank"] = leaderboard.groupby("target")["pr_auc"].rank(
        method="min", ascending=False
    )
    return (
        leaderboard.sort_values(
            ["target", "pr_auc", "log_loss"], ascending=[True, False, True]
        ),
        pd.DataFrame(fold_records),
    )


def write_report(
    path: Path, data: pd.DataFrame, leaderboard: pd.DataFrame
) -> None:
    unique = data.drop_duplicates("possession_uid")
    lines = [
        "# Enhanced Transition Model Benchmark",
        "",
        f"- Possessions: {len(unique):,}",
        f"- 15-second final-third transitions: {int(unique['transition_final_third_15'].sum()):,} ({unique['transition_final_third_15'].mean():.2%})",
        f"- 15-second box transitions: {int(unique['transition_box_15'].sum()):,} ({unique['transition_box_15'].mean():.2%})",
        "- Validation: five match-held-out folds with strictly prior historical features",
        "",
        "## Best PR-AUC models",
        "",
        "| Target | Layout | Architecture | Model | PR-AUC | PR lift | ROC-AUC | Log loss | Recall@10% |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for target in TARGETS:
        row = leaderboard[leaderboard["target"].eq(target)].iloc[0]
        lines.append(
            f"| {target} | {row['layout']} | {row['architecture']} | "
            f"{row['model']} | {row['pr_auc']:.4f} | "
            f"{row['pr_lift_over_prevalence']:.2f}× | {row['roc_auc']:.4f} | "
            f"{row['log_loss']:.4f} | {row['recall_at_10pct']:.2%} |"
        )
    lines.extend(
        [
            "",
            "Weighted models are retained only if rare-event ranking improves without "
            "unacceptable probability degradation. Hierarchical box models estimate "
            "P(final third) × P(box | final third).",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--leaderboard-output", type=Path, default=DEFAULT_LEADERBOARD)
    parser.add_argument("--fold-output", type=Path, default=DEFAULT_FOLDS)
    parser.add_argument("--predictions-output", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = pd.read_csv(args.input, low_memory=False)
    feature_layouts = layouts(data)
    direct = direct_predictions(data, feature_layouts)
    hierarchical = hierarchical_box_predictions(data, feature_layouts)
    base = pd.concat([direct, hierarchical], ignore_index=True)
    ensembles = ensemble_predictions(base)
    predictions = pd.concat([base, ensembles], ignore_index=True)
    leaderboard, folds = summarize(predictions)
    for path in [
        args.leaderboard_output,
        args.fold_output,
        args.predictions_output,
        args.report_output,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    leaderboard.to_csv(args.leaderboard_output, index=False)
    folds.to_csv(args.fold_output, index=False)
    predictions.to_csv(args.predictions_output, index=False)
    write_report(args.report_output, data, leaderboard)
    print(
        leaderboard.groupby("target", sort=False).head(1)[
            [
                "target",
                "layout",
                "architecture",
                "model",
                "pr_auc",
                "roc_auc",
                "log_loss",
                "recall_at_10pct",
            ]
        ].to_string(index=False)
    )
    print(f"Wrote report to {args.report_output}")


if __name__ == "__main__":
    main()
