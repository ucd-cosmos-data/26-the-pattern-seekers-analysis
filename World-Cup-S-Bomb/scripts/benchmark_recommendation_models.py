#!/usr/bin/env python3
"""Benchmark pre-decision classification, xG hurdle, and net-value layouts."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

from benchmark_coaching_models import (
    ENSEMBLES,
    model_definitions,
    score_predictions,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_recommendation_features.csv"
)
DEFAULT_CLASSIFICATION = (
    PROJECT_ROOT / "results" / "recommendation_model_leaderboard.csv"
)
DEFAULT_FOLDS = PROJECT_ROOT / "results" / "recommendation_model_fold_metrics.csv"
DEFAULT_XG = PROJECT_ROOT / "results" / "recommendation_xg_leaderboard.csv"
DEFAULT_PREDICTIONS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_recommendation_oof_predictions.csv"
)
DEFAULT_REPORT = PROJECT_ROOT / "results" / "recommendation_model_benchmark.md"

RANDOM_STATE = 42
CATEGORICAL_FEATURES = [
    "attacking_style",
    "play_pattern",
    "competition_stage",
]
CONTEXT_FEATURES = ["period", "start_minute", "start_x", "start_y"]
CLASSIFICATION_TARGETS = {
    "shot": "shot",
    "box_entry": "entered_penalty_area",
    "transition_box_15": "transition_box_15",
    "transition_shot_15": "transition_shot_15",
}


def recommendation_preprocessor(
    numeric_features: list[str],
) -> ColumnTransformer:
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "one_hot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric, numeric_features),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ],
        sparse_threshold=0,
    )


def regression_models() -> dict[str, object]:
    return {
        "Ridge": Ridge(alpha=10.0),
        "Random Forest": RandomForestRegressor(
            n_estimators=350,
            min_samples_leaf=6,
            max_features=0.7,
            n_jobs=2,
            random_state=RANDOM_STATE,
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=250,
            learning_rate=0.035,
            max_depth=2,
            min_samples_leaf=8,
            subsample=0.85,
            loss="huber",
            random_state=RANDOM_STATE,
        ),
        "Histogram Gradient Boosting": HistGradientBoostingRegressor(
            learning_rate=0.05,
            max_iter=250,
            max_leaf_nodes=15,
            min_samples_leaf=12,
            l2_regularization=1.0,
            random_state=RANDOM_STATE,
        ),
        "XGBoost": XGBRegressor(
            n_estimators=400,
            learning_rate=0.035,
            max_depth=3,
            min_child_weight=6,
            subsample=0.85,
            colsample_bytree=0.8,
            reg_lambda=2.0,
            objective="reg:squarederror",
            n_jobs=2,
            random_state=RANDOM_STATE,
        ),
    }


def regression_metrics(
    truth: np.ndarray, prediction: np.ndarray
) -> dict[str, float]:
    clipped = np.clip(prediction, 0, None)
    correlation = spearmanr(truth, clipped).statistic
    return {
        "mae": float(mean_absolute_error(truth, clipped)),
        "rmse": float(np.sqrt(mean_squared_error(truth, clipped))),
        "spearman": float(correlation) if np.isfinite(correlation) else 0.0,
    }


def layout_columns(data: pd.DataFrame) -> dict[str, list[str]]:
    history = [
        column
        for column in data
        if column.startswith(("team_", "opponent_"))
    ]
    players = [
        column
        for column in data
        if column.startswith(("att_", "def_", "matchup_"))
    ]
    return {
        "Context + History": CONTEXT_FEATURES + history,
        "Player-Aware": CONTEXT_FEATURES + history + players,
    }


def classification_benchmark(
    data: pd.DataFrame,
    layouts: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    models = model_definitions()
    leaderboard: list[dict[str, object]] = []
    fold_metrics: list[dict[str, object]] = []
    prediction_frames: list[pd.DataFrame] = []

    for layout, numeric in layouts.items():
        feature_columns = CATEGORICAL_FEATURES + numeric
        for target_name, target_column in CLASSIFICATION_TARGETS.items():
            base_predictions: dict[str, list[pd.DataFrame]] = {
                name: [] for name in models
            }
            for fold in sorted(data["validation_fold"].unique()):
                fold_data = data[data["validation_fold"].eq(fold)]
                train = fold_data[~fold_data["is_test_fold"]]
                test = fold_data[fold_data["is_test_fold"]]
                for model_name, estimator in models.items():
                    pipeline = Pipeline(
                        [
                            ("preprocess", recommendation_preprocessor(numeric)),
                            ("model", clone(estimator)),
                        ]
                    )
                    pipeline.fit(
                        train[feature_columns], train[target_column].astype(int)
                    )
                    probability = pipeline.predict_proba(
                        test[feature_columns]
                    )[:, 1]
                    frame = test[
                        ["possession_uid", "match_id", "validation_fold"]
                    ].copy()
                    frame["truth"] = test[target_column].astype(int).to_numpy()
                    frame["prediction"] = probability
                    base_predictions[model_name].append(frame)
                    fold_metrics.append(
                        {
                            "layout": layout,
                            "target": target_name,
                            "model": model_name,
                            "fold": fold,
                            "rows": len(test),
                            "positive_rate": frame["truth"].mean(),
                            **score_predictions(
                                frame["truth"].to_numpy(), probability
                            ),
                        }
                    )

            complete = {
                name: pd.concat(frames, ignore_index=True).sort_values(
                    "possession_uid"
                )
                for name, frames in base_predictions.items()
            }
            all_predictions = dict(complete)
            for ensemble_name, members in ENSEMBLES.items():
                ensemble = complete[members[0]].copy()
                ensemble["prediction"] = np.mean(
                    [complete[name]["prediction"].to_numpy() for name in members],
                    axis=0,
                )
                all_predictions[ensemble_name] = ensemble
                for fold, group in ensemble.groupby("validation_fold"):
                    fold_metrics.append(
                        {
                            "layout": layout,
                            "target": target_name,
                            "model": ensemble_name,
                            "fold": fold,
                            "rows": len(group),
                            "positive_rate": group["truth"].mean(),
                            **score_predictions(
                                group["truth"].to_numpy(),
                                group["prediction"].to_numpy(),
                            ),
                        }
                    )

            for model_name, frame in all_predictions.items():
                metrics = score_predictions(
                    frame["truth"].to_numpy(), frame["prediction"].to_numpy()
                )
                leaderboard.append(
                    {
                        "layout": layout,
                        "target": target_name,
                        "model": model_name,
                        "rows": len(frame),
                        "positive_rate": frame["truth"].mean(),
                        **metrics,
                    }
                )
                saved = frame.rename(
                    columns={
                        "truth": f"truth__{target_name}",
                        "prediction": "prediction",
                    }
                )
                saved["layout"] = layout
                saved["target"] = target_name
                saved["model"] = model_name
                prediction_frames.append(saved)

    result = pd.DataFrame(leaderboard)
    result["target_rank"] = result.groupby("target")["log_loss"].rank(
        method="min"
    )
    return (
        result.sort_values(["target", "log_loss", "brier"]),
        pd.DataFrame(fold_metrics),
        pd.concat(prediction_frames, ignore_index=True),
    )


def conditional_xg_benchmark(
    data: pd.DataFrame,
    layouts: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    outcomes = {
        "attacking_xg_given_shot": ("shot", "xg_generated"),
        "transition_xg_given_shot": (
            "transition_shot_15",
            "transition_xg_15",
        ),
    }
    records: list[dict[str, object]] = []
    predictions: list[pd.DataFrame] = []
    models = regression_models()
    for layout, numeric in layouts.items():
        feature_columns = CATEGORICAL_FEATURES + numeric
        for outcome_name, (gate, target) in outcomes.items():
            for model_name, estimator in models.items():
                frames = []
                for fold in sorted(data["validation_fold"].unique()):
                    fold_data = data[data["validation_fold"].eq(fold)]
                    train = fold_data[
                        ~fold_data["is_test_fold"] & fold_data[gate].eq(1)
                    ]
                    test = fold_data[
                        fold_data["is_test_fold"] & fold_data[gate].eq(1)
                    ]
                    pipeline = Pipeline(
                        [
                            ("preprocess", recommendation_preprocessor(numeric)),
                            ("model", clone(estimator)),
                        ]
                    )
                    pipeline.fit(train[feature_columns], train[target])
                    prediction = np.clip(
                        pipeline.predict(test[feature_columns]), 0, None
                    )
                    frame = test[
                        ["possession_uid", "match_id", "validation_fold"]
                    ].copy()
                    frame["truth"] = test[target].to_numpy()
                    frame["prediction"] = prediction
                    frames.append(frame)
                complete = pd.concat(frames, ignore_index=True)
                records.append(
                    {
                        "layout": layout,
                        "outcome": outcome_name,
                        "model": model_name,
                        "rows": len(complete),
                        **regression_metrics(
                            complete["truth"].to_numpy(),
                            complete["prediction"].to_numpy(),
                        ),
                    }
                )
                complete["layout"] = layout
                complete["outcome"] = outcome_name
                complete["model"] = model_name
                predictions.append(complete)
    result = pd.DataFrame(records)
    result["outcome_rank"] = result.groupby("outcome")["rmse"].rank(method="min")
    return (
        result.sort_values(["outcome", "rmse", "mae"]),
        pd.concat(predictions, ignore_index=True),
    )


def hurdle_and_net_value(
    data: pd.DataFrame,
    classifications: pd.DataFrame,
    conditional: pd.DataFrame,
) -> pd.DataFrame:
    actual = (
        data[data["is_test_fold"]][
            [
                "possession_uid",
                "xg_generated",
                "transition_xg_15",
                "net_xg_15",
            ]
        ]
        .drop_duplicates("possession_uid")
        .set_index("possession_uid")
    )
    records: list[dict[str, object]] = []
    best_components: dict[tuple[str, str], tuple[str, pd.Series]] = {}
    for layout in classifications["layout"].unique():
        for side, class_target, regression_outcome, actual_column in [
            (
                "attack",
                "shot",
                "attacking_xg_given_shot",
                "xg_generated",
            ),
            (
                "transition",
                "transition_shot_15",
                "transition_xg_given_shot",
                "transition_xg_15",
            ),
        ]:
            class_subset = classifications[
                classifications["layout"].eq(layout)
                & classifications["target"].eq(class_target)
            ]
            reg_subset = conditional[
                conditional["layout"].eq(layout)
                & conditional["outcome"].eq(regression_outcome)
            ]
            for class_model, class_frame in class_subset.groupby("model"):
                probability = class_frame.set_index("possession_uid")["prediction"]
                for reg_model, reg_frame in reg_subset.groupby("model"):
                    conditional_map = reg_frame.set_index("possession_uid")[
                        "prediction"
                    ]
                    mean_conditional = float(conditional_map.mean())
                    expected = probability * mean_conditional
                    truth = actual.loc[expected.index, actual_column]
                    metrics = regression_metrics(
                        truth.to_numpy(), expected.to_numpy()
                    )
                    records.append(
                        {
                            "layout": layout,
                            "outcome": f"expected_{side}_xg",
                            "classifier": class_model,
                            "conditional_regressor": reg_model,
                            **metrics,
                        }
                    )
                    key = (layout, side)
                    current = best_components.get(key)
                    if current is None or metrics["rmse"] < current[0]:
                        best_components[key] = (
                            metrics["rmse"],
                            expected.rename(f"expected_{side}_xg"),
                            class_model,
                            reg_model,
                        )

        attack = best_components[(layout, "attack")]
        transition = best_components[(layout, "transition")]
        common = attack[1].index.intersection(transition[1].index)
        predicted_net = attack[1].loc[common] - transition[1].loc[common]
        truth_net = actual.loc[common, "net_xg_15"]
        records.append(
            {
                "layout": layout,
                "outcome": "expected_net_xg",
                "classifier": f"attack={attack[2]}; transition={transition[2]}",
                "conditional_regressor": (
                    f"attack={attack[3]}; transition={transition[3]}"
                ),
                **regression_metrics(
                    truth_net.to_numpy(), predicted_net.to_numpy()
                ),
            }
        )
    return pd.DataFrame(records).sort_values(["outcome", "rmse", "mae"])


def write_report(
    path: Path,
    data: pd.DataFrame,
    classification: pd.DataFrame,
    xg: pd.DataFrame,
) -> None:
    lines = [
        "# Pre-Decision Recommendation Model Benchmark",
        "",
        f"- Unique possessions: {data['possession_uid'].nunique():,}",
        f"- Matches: {data['match_id'].nunique()}",
        "- Validation: five match-held-out folds with fold-specific historical features",
        "- Exact current-possession defensive shape is excluded",
        "- Team and player performance inputs use only earlier matches available to the training fold",
        "",
        "## Classification winners",
        "",
        "| Target | Layout | Model | Log loss | Brier | ROC-AUC | PR-AUC |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for target in CLASSIFICATION_TARGETS:
        row = classification[classification["target"].eq(target)].iloc[0]
        lines.append(
            f"| {target} | {row['layout']} | {row['model']} | "
            f"{row['log_loss']:.4f} | {row['brier']:.4f} | "
            f"{row['roc_auc']:.4f} | {row['pr_auc']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Net-value result",
            "",
        ]
    )
    for _, row in xg[xg["outcome"].eq("expected_net_xg")].iterrows():
        lines.append(
            f"- {row['layout']}: RMSE {row['rmse']:.4f}, "
            f"MAE {row['mae']:.4f}, Spearman {row['spearman']:.4f}"
        )
    lines.extend(
        [
            "",
            "These results measure prediction, not causal treatment effects. Candidate-style "
            "simulation must hold all other inputs constant and report uncertainty.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument(
        "--classification-output", type=Path, default=DEFAULT_CLASSIFICATION
    )
    parser.add_argument("--fold-output", type=Path, default=DEFAULT_FOLDS)
    parser.add_argument("--xg-output", type=Path, default=DEFAULT_XG)
    parser.add_argument("--predictions-output", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = pd.read_csv(args.input, low_memory=False)
    layouts = layout_columns(data)
    classification, folds, class_predictions = classification_benchmark(
        data, layouts
    )
    conditional_summary, conditional_predictions = conditional_xg_benchmark(
        data, layouts
    )
    xg_summary = hurdle_and_net_value(
        data, class_predictions, conditional_predictions
    )
    xg_output = pd.concat(
        [
            conditional_summary.assign(result_type="conditional"),
            xg_summary.assign(result_type="hurdle"),
        ],
        ignore_index=True,
        sort=False,
    )
    for path in [
        args.classification_output,
        args.fold_output,
        args.xg_output,
        args.predictions_output,
        args.report_output,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    classification.to_csv(args.classification_output, index=False)
    folds.to_csv(args.fold_output, index=False)
    xg_output.to_csv(args.xg_output, index=False)
    class_predictions.to_csv(args.predictions_output, index=False)
    write_report(args.report_output, data, classification, xg_summary)
    print(
        classification.groupby("target", sort=False).head(1)[
            ["target", "layout", "model", "log_loss", "roc_auc", "pr_auc"]
        ].to_string(index=False)
    )
    print(
        xg_summary[xg_summary["outcome"].eq("expected_net_xg")][
            ["layout", "rmse", "mae", "spearman"]
        ].to_string(index=False)
    )
    print(f"Wrote report to {args.report_output}")


if __name__ == "__main__":
    main()
