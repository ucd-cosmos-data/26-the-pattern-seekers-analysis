#!/usr/bin/env python3
"""Quantify model uncertainty and make simplicity-aware final selections."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.pipeline import Pipeline

import benchmark_coaching_models as benchmark


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POSSESSIONS = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_clusters.csv"
)
DEFAULT_LEADERBOARD = PROJECT_ROOT / "results" / "coaching_model_leaderboard.csv"
DEFAULT_PREDICTIONS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_coaching_model_oof_predictions.csv"
)
DEFAULT_BENCHMARK_MODEL = PROJECT_ROOT / "models" / "coaching_model_benchmark.joblib"
DEFAULT_UNCERTAINTY = PROJECT_ROOT / "results" / "coaching_model_uncertainty.csv"
DEFAULT_SELECTION = PROJECT_ROOT / "results" / "coaching_model_selection.md"
DEFAULT_FINAL_MODEL = PROJECT_ROOT / "models" / "coaching_model_final.joblib"

RANDOM_STATE = 42
BOOTSTRAP_REPLICATES = 5_000
PRACTICAL_LOG_LOSS_MARGIN = 0.001

MODEL_COMPLEXITY = {
    "Logistic Regression": 1,
    "Histogram Gradient Boosting": 2,
    "XGBoost": 3,
    "Gradient Boosting": 3,
    "Random Forest": 4,
    "Soft Vote: LR + XGB": 5,
    "Soft Vote: Boosting": 6,
    "Soft Vote: All": 7,
}

LAYOUT_COMPLEXITY = {
    "Start Context": 1,
    "Context + Attack Style": 2,
    "Context + Both Styles": 3,
    "Tactical + Shape": 4,
    "Player-Aware": 5,
}


def match_bootstrap_samples(
    predictions: pd.DataFrame,
    replicates: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    matches = np.asarray(sorted(predictions["match_id"].unique()))
    counts = (
        predictions.groupby("match_id")
        .size()
        .reindex(matches)
        .to_numpy(dtype=float)
    )
    rng = np.random.default_rng(RANDOM_STATE)
    samples = rng.integers(
        0,
        len(matches),
        size=(replicates, len(matches)),
    )
    return matches, counts, samples


def bootstrap_mean(
    values: np.ndarray,
    match_ids: pd.Series,
    matches: np.ndarray,
    counts: np.ndarray,
    samples: np.ndarray,
) -> np.ndarray:
    sums = (
        pd.Series(values)
        .groupby(match_ids.reset_index(drop=True))
        .sum()
        .reindex(matches)
        .to_numpy(dtype=float)
    )
    return sums[samples].sum(axis=1) / counts[samples].sum(axis=1)


def uncertainty_table(
    leaderboard: pd.DataFrame,
    predictions: pd.DataFrame,
    replicates: int,
) -> pd.DataFrame:
    matches, counts, samples = match_bootstrap_samples(predictions, replicates)
    records: list[dict[str, Any]] = []
    distributions: dict[tuple[str, str, str], np.ndarray] = {}

    for row in leaderboard.itertuples(index=False):
        prediction_column = benchmark.prediction_column_name(
            row.layout,
            row.target,
            row.model,
        )
        if prediction_column not in predictions:
            raise ValueError(f"Missing OOF prediction column: {prediction_column}")
        truth = predictions[f"truth__{row.target}"].to_numpy(dtype=float)
        probability = np.clip(
            predictions[prediction_column].to_numpy(dtype=float),
            1e-6,
            1 - 1e-6,
        )
        row_log_loss = -(
            truth * np.log(probability)
            + (1 - truth) * np.log(1 - probability)
        )
        row_brier = (truth - probability) ** 2
        log_loss_distribution = bootstrap_mean(
            row_log_loss,
            predictions["match_id"],
            matches,
            counts,
            samples,
        )
        brier_distribution = bootstrap_mean(
            row_brier,
            predictions["match_id"],
            matches,
            counts,
            samples,
        )
        key = (row.target, row.layout, row.model)
        distributions[key] = log_loss_distribution
        records.append(
            {
                **row._asdict(),
                "log_loss_ci_low": float(
                    np.quantile(log_loss_distribution, 0.025)
                ),
                "log_loss_ci_high": float(
                    np.quantile(log_loss_distribution, 0.975)
                ),
                "brier_ci_low": float(np.quantile(brier_distribution, 0.025)),
                "brier_ci_high": float(np.quantile(brier_distribution, 0.975)),
            }
        )

    output = pd.DataFrame(records)
    output["delta_log_loss_vs_best"] = np.nan
    output["delta_ci_low"] = np.nan
    output["delta_ci_high"] = np.nan
    output["empirical_best"] = False
    output["within_practical_margin"] = False
    output["selected"] = False

    for (target, timing), group in output.groupby(["target", "timing"]):
        best_index = group["log_loss"].idxmin()
        best_row = output.loc[best_index]
        best_key = (target, best_row["layout"], best_row["model"])
        best_distribution = distributions[best_key]
        output.loc[best_index, "empirical_best"] = True

        for index in group.index:
            row = output.loc[index]
            key = (target, row["layout"], row["model"])
            delta = distributions[key] - best_distribution
            output.loc[index, "delta_log_loss_vs_best"] = (
                row["log_loss"] - best_row["log_loss"]
            )
            output.loc[index, "delta_ci_low"] = float(
                np.quantile(delta, 0.025)
            )
            output.loc[index, "delta_ci_high"] = float(
                np.quantile(delta, 0.975)
            )
            output.loc[index, "within_practical_margin"] = (
                row["log_loss"]
                <= best_row["log_loss"] + PRACTICAL_LOG_LOSS_MARGIN
            )

    for target, group in output[output["timing"].eq("Retrospective")].groupby(
        "target"
    ):
        candidates = group[group["within_practical_margin"]].copy()
        candidates["model_complexity"] = candidates["model"].map(
            MODEL_COMPLEXITY
        )
        candidates["layout_complexity"] = candidates["layout"].map(
            LAYOUT_COMPLEXITY
        )
        selected_index = candidates.sort_values(
            [
                "model_complexity",
                "layout_complexity",
                "log_loss",
                "brier",
            ]
        ).index[0]
        output.loc[selected_index, "selected"] = True

    return output.sort_values(
        ["target", "timing", "log_loss", "brier"],
    ).reset_index(drop=True)


def fit_candidate(
    data: pd.DataFrame,
    target_column: str,
    layout: dict[str, Any],
    model_name: str,
) -> object:
    numeric = list(layout["numeric_features"])
    categorical = list(layout["categorical_features"])
    columns = categorical + numeric
    missing = sorted(set(columns) - set(data.columns))
    if missing:
        raise ValueError(
            "Final refit requires unavailable columns: " + ", ".join(missing)
        )
    truth = data[target_column].astype(int)
    base_models = benchmark.model_definitions()

    if model_name in base_models:
        pipeline = Pipeline(
            [
                (
                    "preprocess",
                    benchmark.preprocessor(numeric, categorical),
                ),
                ("model", clone(base_models[model_name])),
            ]
        )
        pipeline.fit(data[columns], truth)
        return pipeline

    pipelines = []
    for member in benchmark.ENSEMBLES[model_name]:
        pipeline = Pipeline(
            [
                (
                    "preprocess",
                    benchmark.preprocessor(numeric, categorical),
                ),
                ("model", clone(base_models[member])),
            ]
        )
        pipeline.fit(data[columns], truth)
        pipelines.append((member, pipeline))
    return {"kind": "equal_weight_ensemble", "members": pipelines}


def selected_specification(
    row: pd.Series,
    layouts: dict[str, dict[str, Any]],
    data: pd.DataFrame,
) -> dict[str, Any]:
    layout = layouts[str(row["layout"])]
    target_column = benchmark.TARGETS[str(row["target"])]
    return {
        "target_column": target_column,
        "layout": str(row["layout"]),
        "timing": str(row["timing"]),
        "model_name": str(row["model"]),
        "categorical_features": list(layout["categorical_features"]),
        "numeric_features": list(layout["numeric_features"]),
        "model": fit_candidate(
            data,
            target_column,
            layout,
            str(row["model"]),
        ),
        "metrics": {
            key: float(row[key])
            for key in [
                "log_loss",
                "log_loss_ci_low",
                "log_loss_ci_high",
                "brier",
                "brier_ci_low",
                "brier_ci_high",
                "roc_auc",
                "pr_auc",
                "ece",
            ]
        },
    }


def write_report(
    path: Path,
    uncertainty: pd.DataFrame,
    replicates: int,
) -> None:
    lines = [
        "# Coaching Model Uncertainty and Final Selection",
        "",
        "## Selection design",
        "",
        f"- Match-cluster bootstrap replicates: {replicates:,}",
        "- Resampling unit: complete match",
        "- Primary selection metric: out-of-fold log loss",
        f"- Practical tie margin: {PRACTICAL_LOG_LOSS_MARGIN:.3f} absolute log loss",
        "- Rule: among retrospective candidates within the margin of the empirical best, select the least complex model.",
        "- Confidence intervals describe sampling uncertainty; they do not remove winner-selection optimism from using the same cross-validation predictions.",
        "",
        "## Final retrospective selections",
        "",
        "| Target | Selected model | Layout | Log loss (95% CI) | Delta vs empirical best (95% CI) | ROC-AUC | PR-AUC |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    selected = uncertainty[uncertainty["selected"]]
    for row in selected.sort_values("target").itertuples(index=False):
        lines.append(
            f"| {row.target} | {row.model} | {row.layout} | "
            f"{row.log_loss:.4f} ({row.log_loss_ci_low:.4f}–{row.log_loss_ci_high:.4f}) | "
            f"{row.delta_log_loss_vs_best:+.4f} "
            f"({row.delta_ci_low:+.4f}–{row.delta_ci_high:+.4f}) | "
            f"{row.roc_auc:.4f} | {row.pr_auc:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Prospective start-context baselines",
            "",
            "| Target | Model | Log loss (95% CI) | ROC-AUC | PR-AUC |",
            "|---|---|---:|---:|---:|",
        ]
    )
    prospective = uncertainty[
        uncertainty["layout"].eq("Start Context")
        & uncertainty["model"].eq("Logistic Regression")
    ]
    for row in prospective.sort_values("target").itertuples(index=False):
        lines.append(
            f"| {row.target} | {row.model} | "
            f"{row.log_loss:.4f} ({row.log_loss_ci_low:.4f}–{row.log_loss_ci_high:.4f}) | "
            f"{row.roc_auc:.4f} | {row.pr_auc:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The selected retrospective models are parsimonious representatives of a near-tied candidate set, not statistically proven universal winners. The prospective baselines remain separate because completed-possession styles and shape cannot be used at possession start.",
            "",
            "These intervals address match-to-match sampling variation. A locked architecture evaluated through nested cross-validation or an external tournament remains necessary for an unbiased generalization claim.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--possessions", type=Path, default=DEFAULT_POSSESSIONS)
    parser.add_argument("--leaderboard", type=Path, default=DEFAULT_LEADERBOARD)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument(
        "--benchmark-model",
        type=Path,
        default=DEFAULT_BENCHMARK_MODEL,
    )
    parser.add_argument("--uncertainty", type=Path, default=DEFAULT_UNCERTAINTY)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--final-model", type=Path, default=DEFAULT_FINAL_MODEL)
    parser.add_argument(
        "--bootstrap-replicates",
        type=int,
        default=BOOTSTRAP_REPLICATES,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.bootstrap_replicates < 1_000:
        raise ValueError("Use at least 1,000 bootstrap replicates")

    leaderboard = pd.read_csv(args.leaderboard)
    predictions = pd.read_csv(args.predictions)
    benchmark_bundle = joblib.load(args.benchmark_model)
    uncertainty = uncertainty_table(
        leaderboard,
        predictions,
        args.bootstrap_replicates,
    )

    possessions = pd.read_csv(args.possessions, low_memory=False)
    data = possessions[
        possessions["attacking_style_cluster"].ge(0)
        & possessions["defensive_style_cluster"].ge(0)
        & possessions["period"].le(4)
    ].copy()
    layouts = benchmark_bundle["layouts"]

    selected_models = {}
    for _, row in uncertainty[uncertainty["selected"]].iterrows():
        selected_models[str(row["target"])] = selected_specification(
            row,
            layouts,
            data,
        )

    prospective_baselines = {}
    prospective = uncertainty[
        uncertainty["layout"].eq("Start Context")
        & uncertainty["model"].eq("Logistic Regression")
    ]
    for _, row in prospective.iterrows():
        prospective_baselines[str(row["target"])] = selected_specification(
            row,
            layouts,
            data,
        )

    for path in [args.uncertainty, args.selection, args.final_model]:
        path.parent.mkdir(parents=True, exist_ok=True)
    uncertainty.to_csv(args.uncertainty, index=False)
    write_report(args.selection, uncertainty, args.bootstrap_replicates)
    joblib.dump(
        {
            "version": 1,
            "purpose": "Simplicity-aware final possession outcome models",
            "selection_rule": {
                "primary_metric": "out-of-fold log loss",
                "practical_margin": PRACTICAL_LOG_LOSS_MARGIN,
                "bootstrap_unit": "match",
                "bootstrap_replicates": args.bootstrap_replicates,
                "random_state": RANDOM_STATE,
            },
            "selected_models": selected_models,
            "prospective_baselines": prospective_baselines,
        },
        args.final_model,
    )

    print(
        uncertainty[uncertainty["selected"]][
            [
                "target",
                "layout",
                "model",
                "log_loss",
                "log_loss_ci_low",
                "log_loss_ci_high",
            ]
        ].to_string(index=False)
    )
    print(f"Wrote uncertainty table to {args.uncertainty}")
    print(f"Wrote selection report to {args.selection}")
    print(f"Wrote final model bundle to {args.final_model}")


if __name__ == "__main__":
    main()
