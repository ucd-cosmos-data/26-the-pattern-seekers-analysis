#!/usr/bin/env python3
"""Quantify model uncertainty and make simplicity-aware final selections."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.pipeline import Pipeline

import benchmark_coaching_models as benchmark

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.coaching_selection import (  # noqa: E402
    bootstrap_average_precision_ci,
    mark_selection,
    operating_point,
)
DEFAULT_POSSESSIONS = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_clusters.csv"
)
DEFAULT_LEADERBOARD = PROJECT_ROOT / "results" / "MIscellaneous" / "coaching_model_leaderboard.csv"
DEFAULT_PREDICTIONS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_coaching_model_oof_predictions.csv"
)
DEFAULT_BENCHMARK_MODEL = PROJECT_ROOT / "models" / "coaching_model_benchmark.joblib"
DEFAULT_UNCERTAINTY = PROJECT_ROOT / "results" / "MIscellaneous" / "coaching_model_uncertainty.csv"
DEFAULT_SELECTION = PROJECT_ROOT / "results" / "MIscellaneous" / "coaching_model_selection.md"
DEFAULT_OPERATING_POINTS = (
    PROJECT_ROOT / "results" / "MIscellaneous" / "coaching_model_operating_points.csv"
)
DEFAULT_FINAL_MODEL = PROJECT_ROOT / "models" / "coaching_model_final.joblib"

RANDOM_STATE = 42
BOOTSTRAP_REPLICATES = 5_000
# Selection is keyed on average precision (PR-AUC): the positive class is rare, so
# log loss / ROC-AUC are optimistic. The log-loss margin is retained only for the
# secondary reporting columns.
PRIMARY_METRIC = "pr_auc"
PRACTICAL_PR_AUC_MARGIN = 0.005
PRACTICAL_LOG_LOSS_MARGIN = 0.001
OPERATING_MIN_PRECISION = 0.30

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
    match_id_values = predictions["match_id"].to_numpy()
    records: list[dict[str, Any]] = []
    truth_by_row: dict[tuple[str, str, str], tuple[np.ndarray, np.ndarray]] = {}

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
        truth_by_row[(row.target, row.layout, row.model)] = (truth, probability)
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

    # Simplicity-aware selection keyed on average precision (PR-AUC). The ranking
    # logic lives in src/coaching_selection.mark_selection so it can be unit-tested
    # on out-of-fold arrays without the training stack.
    selection_input = (
        output[["target", "timing", "layout", "model", "pr_auc", "log_loss"]]
        .assign(
            model_complexity=output["model"].map(MODEL_COMPLEXITY),
            layout_complexity=output["layout"].map(LAYOUT_COMPLEXITY),
        )
        .to_dict("records")
    )
    flags = pd.DataFrame(
        mark_selection(
            selection_input,
            primary_metric=PRIMARY_METRIC,
            margin=PRACTICAL_PR_AUC_MARGIN,
            higher_is_better=True,
            secondary_metric="log_loss",
            secondary_higher_is_better=False,
        )
    )
    for column in [
        "empirical_best",
        "within_practical_margin",
        "delta_primary_vs_best",
        "selected",
    ]:
        output[column] = flags[column].to_numpy()
    output = output.rename(
        columns={"delta_primary_vs_best": "delta_pr_auc_vs_best"}
    )

    # Average precision is a set-level metric, so its bootstrap CI must be
    # recomputed per resampled match set rather than averaged per row. Compute it
    # (reusing the same match draws) only for the rows the report shows: the pick,
    # the empirical best, and the prospective baselines.
    output["pr_auc_ci_low"] = np.nan
    output["pr_auc_ci_high"] = np.nan
    display_mask = (
        output["selected"]
        | output["empirical_best"]
        | (
            output["layout"].eq("Start Context")
            & output["model"].eq("Logistic Regression")
        )
    )
    for index in output[display_mask].index:
        row = output.loc[index]
        truth, probability = truth_by_row[
            (row["target"], row["layout"], row["model"])
        ]
        ci = bootstrap_average_precision_ci(
            truth,
            probability,
            match_id_values,
            matches=matches,
            samples=samples,
        )
        output.loc[index, "pr_auc_ci_low"] = ci["pr_auc_ci_low"]
        output.loc[index, "pr_auc_ci_high"] = ci["pr_auc_ci_high"]

    return output.sort_values(
        ["target", "timing", "pr_auc"],
        ascending=[True, True, False],
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
    operating_points: dict[str, dict[str, Any]],
) -> None:
    lines = [
        "# Coaching Model Uncertainty and Final Selection",
        "",
        "## Selection design",
        "",
        f"- Match-cluster bootstrap replicates: {replicates:,}",
        "- Resampling unit: complete match",
        "- Primary selection metric: out-of-fold average precision (PR-AUC)",
        f"- Practical tie margin: {PRACTICAL_PR_AUC_MARGIN:.3f} absolute average precision",
        "- Rule: among retrospective candidates within the PR-AUC margin of the empirical best, select the least complex model.",
        "- PR-AUC is the primary metric because the positive class is rare; ROC-AUC and log loss are optimistic under class imbalance and are reported as secondary diagnostics.",
        "- Confidence intervals describe match-to-match sampling; they do not remove winner-selection optimism from using the same cross-validation predictions. See `scripts/validate_nested_coaching_models.py` for an unbiased nested estimate.",
        "",
        "## Final retrospective selections",
        "",
        "| Target | Selected model | Layout | PR-AUC (95% CI) | ROC-AUC | Log loss | Brier |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    selected = uncertainty[uncertainty["selected"]]
    for row in selected.sort_values("target").itertuples(index=False):
        lines.append(
            f"| {row.target} | {row.model} | {row.layout} | "
            f"{row.pr_auc:.4f} ({row.pr_auc_ci_low:.4f}–{row.pr_auc_ci_high:.4f}) | "
            f"{row.roc_auc:.4f} | {row.log_loss:.4f} | {row.brier:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Operating thresholds (pooled out-of-fold)",
            "",
            "Threshold maximises F0.5 (precision-weighted) subject to precision ≥ "
            f"{OPERATING_MIN_PRECISION:.2f}. Pooled out-of-fold values illustrate "
            "decision-time behaviour on the rare positive class, which ROC-AUC hides.",
            "",
            "| Target | Model | Threshold | Precision | Recall | F0.5 | Flagged | Base rate | Status |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for target in sorted(operating_points):
        op = operating_points[target]
        if op.get("status") == "no_positives":
            lines.append(
                f"| {target} | {op.get('model', '')} | — | — | — | — | — | — | no positives |"
            )
            continue
        lines.append(
            f"| {target} | {op.get('model', '')} | {op['threshold']:.3f} | "
            f"{op['precision']:.3f} | {op['recall']:.3f} | {op['f_beta']:.3f} | "
            f"{op['predicted_positive_rate'] * 100:.1f}% | "
            f"{op['base_rate'] * 100:.1f}% | {op['status']} |"
        )

    lines.extend(
        [
            "",
            "## Prospective start-context baselines",
            "",
            "| Target | Model | PR-AUC (95% CI) | ROC-AUC | Log loss |",
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
            f"{row.pr_auc:.4f} ({row.pr_auc_ci_low:.4f}–{row.pr_auc_ci_high:.4f}) | "
            f"{row.roc_auc:.4f} | {row.log_loss:.4f} |"
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
    parser.add_argument(
        "--operating-points",
        type=Path,
        default=DEFAULT_OPERATING_POINTS,
    )
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

    # Operating-threshold performance for the selected retrospective models,
    # scored on the pooled out-of-fold predictions.
    operating_points: dict[str, dict[str, Any]] = {}
    for _, row in uncertainty[uncertainty["selected"]].iterrows():
        column = benchmark.prediction_column_name(
            row["layout"], row["target"], row["model"]
        )
        truth = predictions[f"truth__{row['target']}"].to_numpy(dtype=float)
        probability = predictions[column].to_numpy(dtype=float)
        point = operating_point(
            truth, probability, min_precision=OPERATING_MIN_PRECISION
        )
        point["model"] = str(row["model"])
        point["layout"] = str(row["layout"])
        operating_points[str(row["target"])] = point

    for path in [
        args.uncertainty,
        args.selection,
        args.operating_points,
        args.final_model,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    uncertainty.to_csv(args.uncertainty, index=False)
    pd.DataFrame(
        [{"target": target, **point} for target, point in operating_points.items()]
    ).to_csv(args.operating_points, index=False)
    write_report(
        args.selection,
        uncertainty,
        args.bootstrap_replicates,
        operating_points,
    )
    joblib.dump(
        {
            "version": 2,
            "purpose": "Simplicity-aware final possession outcome models",
            "selection_rule": {
                "primary_metric": "out-of-fold average precision (PR-AUC)",
                "practical_margin": PRACTICAL_PR_AUC_MARGIN,
                "operating_min_precision": OPERATING_MIN_PRECISION,
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
                "pr_auc",
                "pr_auc_ci_low",
                "pr_auc_ci_high",
                "log_loss",
            ]
        ].to_string(index=False)
    )
    print(f"Wrote uncertainty table to {args.uncertainty}")
    print(f"Wrote selection report to {args.selection}")
    print(f"Wrote operating points to {args.operating_points}")
    print(f"Wrote final model bundle to {args.final_model}")


if __name__ == "__main__":
    main()
