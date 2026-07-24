#!/usr/bin/env python3
"""Explain selected coaching models with held-out, match-aware diagnostics."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline

import benchmark_coaching_models as benchmark


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POSSESSIONS = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_clusters.csv"
)
DEFAULT_FINAL_MODEL = PROJECT_ROOT / "models" / "coaching_model_final.joblib"
DEFAULT_OOF_PREDICTIONS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_coaching_model_oof_predictions.csv"
)
DEFAULT_IMPORTANCE = (
    PROJECT_ROOT / "results" / "coaching_permutation_importance.csv"
)
DEFAULT_EFFECTS = PROJECT_ROOT / "results" / "coaching_effect_profiles.csv"
DEFAULT_REPORT = PROJECT_ROOT / "results" / "coaching_model_explanations.md"
DEFAULT_FIGURE = (
    PROJECT_ROOT / "results" / "figures" / "coaching_model_explanations.png"
)

RANDOM_STATE = 42
PERMUTATION_REPEATS = 20
BOOTSTRAP_REPLICATES = 2_000

FEATURE_GROUPS = {
    "Start Context": [
        "period",
        "start_minute",
        "start_x",
        "start_y",
        "first_play_pattern",
        "competition_stage",
    ],
    "Attacking Style": ["attacking_style"],
    "Defensive Style": ["defensive_style"],
    "Defensive Shape": benchmark.SHAPE_NUMERIC_FEATURES,
}

FEATURE_LABELS = {
    "period": "Period",
    "start_minute": "Start minute",
    "start_x": "Starting x",
    "start_y": "Starting y",
    "first_play_pattern": "Opening play pattern",
    "competition_stage": "Competition stage",
    "attacking_style": "Attacking style",
    "defensive_style": "Defensive style",
    "avg_back_line_height": "Back-line height",
    "std_back_line_height": "Back-line-height variation",
    "avg_defensive_hull_area": "Defensive hull area",
    "avg_defensive_width": "Defensive width",
    "avg_defensive_depth": "Defensive depth",
    "avg_defenders_behind_ball": "Defenders behind ball",
    "avg_central_defenders": "Central defenders",
    "avg_defenders_within_5": "Defenders within 5m",
    "avg_defenders_within_10": "Defenders within 10m",
    "avg_nearest_defender_distance": "Nearest-defender distance",
    "avg_mean_defender_distance": "Mean defender distance",
}

TARGET_LABELS = {
    "shot": "Shot",
    "box_entry": "Penalty-area entry",
}


def row_log_loss(truth: np.ndarray, probability: np.ndarray) -> np.ndarray:
    probability = np.clip(probability, 1e-6, 1 - 1e-6)
    return -(truth * np.log(probability) + (1 - truth) * np.log(1 - probability))


def fit_selected_fold_model(
    train: pd.DataFrame,
    specification: dict[str, Any],
) -> Pipeline:
    numeric = list(specification["numeric_features"])
    categorical = list(specification["categorical_features"])
    estimator = benchmark.model_definitions()[specification["model_name"]]
    model = Pipeline(
        [
            ("preprocess", benchmark.preprocessor(numeric, categorical)),
            ("model", clone(estimator)),
        ]
    )
    model.fit(
        train[categorical + numeric],
        train[specification["target_column"]].astype(int),
    )
    return model


def permute_within_matches(
    frame: pd.DataFrame,
    columns: list[str],
    match_ids: pd.Series,
    rng: np.random.Generator,
) -> pd.DataFrame:
    output = frame.copy()
    for indices in match_ids.groupby(match_ids, sort=False).groups.values():
        positions = np.asarray(indices, dtype=int)
        shuffled = rng.permutation(positions)
        output.iloc[positions, output.columns.get_indexer(columns)] = (
            frame.iloc[shuffled][columns].to_numpy()
        )
    return output


def cluster_bootstrap_interval(
    match_delta_sums: pd.Series,
    match_counts: pd.Series,
    rng: np.random.Generator,
    replicates: int,
) -> tuple[float, float]:
    matches = match_counts.index.to_numpy()
    samples = rng.integers(0, len(matches), size=(replicates, len(matches)))
    sums = match_delta_sums.reindex(matches).to_numpy(dtype=float)
    counts = match_counts.reindex(matches).to_numpy(dtype=float)
    values = sums[samples].sum(axis=1) / counts[samples].sum(axis=1)
    return float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def permutation_importance(
    data: pd.DataFrame,
    selected_models: dict[str, dict[str, Any]],
    oof_predictions: pd.DataFrame,
    repeats: int,
    bootstrap_replicates: int,
) -> pd.DataFrame:
    splitter = StratifiedGroupKFold(
        n_splits=benchmark.N_SPLITS,
        shuffle=True,
        random_state=benchmark.RANDOM_STATE,
    )
    splits = list(
        splitter.split(data, data["shot"].astype(int), groups=data["match_id"])
    )
    records: list[dict[str, Any]] = []

    for target_index, (target, specification) in enumerate(
        selected_models.items()
    ):
        categorical = list(specification["categorical_features"])
        numeric = list(specification["numeric_features"])
        features = categorical + numeric
        truth = data[specification["target_column"]].astype(int).to_numpy()
        baseline = np.full(len(data), np.nan)
        fitted_folds: list[tuple[np.ndarray, Pipeline]] = []

        for train_index, test_index in splits:
            model = fit_selected_fold_model(data.iloc[train_index], specification)
            baseline[test_index] = model.predict_proba(
                data.iloc[test_index][features]
            )[:, 1]
            fitted_folds.append((test_index, model))

        expected_column = benchmark.prediction_column_name(
            specification["layout"],
            target,
            specification["model_name"],
        )
        expected = oof_predictions[expected_column].to_numpy(dtype=float)
        if not np.allclose(baseline, expected, atol=1e-10, rtol=1e-10):
            maximum_difference = float(np.max(np.abs(baseline - expected)))
            raise RuntimeError(
                "Reconstructed folds do not match saved OOF predictions "
                f"for {target}; maximum difference={maximum_difference:.3g}"
            )

        baseline_loss = row_log_loss(truth, baseline)
        items = [
            ("group", group, columns)
            for group, columns in FEATURE_GROUPS.items()
        ]
        items.extend(
            ("feature", feature, [feature])
            for feature in features
        )

        for item_index, (level, item, columns) in enumerate(items):
            repeat_row_deltas = []
            for repeat in range(repeats):
                permuted_probability = np.full(len(data), np.nan)
                for fold, (test_index, model) in enumerate(fitted_folds):
                    test = data.iloc[test_index][features].reset_index(drop=True)
                    match_ids = data.iloc[test_index]["match_id"].reset_index(
                        drop=True
                    )
                    seed = (
                        RANDOM_STATE
                        + target_index * 1_000_000
                        + item_index * 10_000
                        + repeat * 100
                        + fold
                    )
                    permuted = permute_within_matches(
                        test,
                        columns,
                        match_ids,
                        np.random.default_rng(seed),
                    )
                    permuted_probability[test_index] = model.predict_proba(
                        permuted
                    )[:, 1]
                repeat_row_deltas.append(
                    row_log_loss(truth, permuted_probability) - baseline_loss
                )

            row_delta = np.mean(repeat_row_deltas, axis=0)
            match_delta_sums = (
                pd.Series(row_delta)
                .groupby(data["match_id"].reset_index(drop=True))
                .sum()
            )
            match_counts = data.groupby("match_id").size()
            interval_rng = np.random.default_rng(
                RANDOM_STATE + target_index * 100_000 + item_index
            )
            ci_low, ci_high = cluster_bootstrap_interval(
                match_delta_sums,
                match_counts,
                interval_rng,
                bootstrap_replicates,
            )
            records.append(
                {
                    "target": target,
                    "model": specification["model_name"],
                    "layout": specification["layout"],
                    "timing": specification["timing"],
                    "level": level,
                    "feature_group": (
                        item
                        if level == "group"
                        else next(
                            group
                            for group, members in FEATURE_GROUPS.items()
                            if item in members
                        )
                    ),
                    "feature": "" if level == "group" else item,
                    "label": item if level == "group" else FEATURE_LABELS[item],
                    "delta_log_loss": float(np.mean(row_delta)),
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "permutation_repeats": repeats,
                    "bootstrap_replicates": bootstrap_replicates,
                    "permutation_scope": "within match",
                }
            )

    return pd.DataFrame(records).sort_values(
        ["target", "level", "delta_log_loss"],
        ascending=[True, True, False],
    )


def effect_profiles(
    data: pd.DataFrame,
    selected_models: dict[str, dict[str, Any]],
    importance: pd.DataFrame,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for target, specification in selected_models.items():
        features = (
            list(specification["categorical_features"])
            + list(specification["numeric_features"])
        )
        fitted = specification["model"]

        for feature in ["attacking_style", "defensive_style"]:
            for value in sorted(data[feature].dropna().astype(str).unique()):
                counterfactual = data[features].copy()
                counterfactual[feature] = value
                probability = fitted.predict_proba(counterfactual)[:, 1]
                records.append(
                    {
                        "target": target,
                        "profile_type": "categorical substitution",
                        "feature": feature,
                        "label": FEATURE_LABELS[feature],
                        "value": value,
                        "value_numeric": np.nan,
                        "mean_predicted_probability": float(
                            np.mean(probability)
                        ),
                        "observed_rows": int(data[feature].eq(value).sum()),
                    }
                )

        candidates = importance[
            importance["target"].eq(target)
            & importance["level"].eq("feature")
            & importance["feature"].isin(benchmark.SHAPE_NUMERIC_FEATURES)
        ]
        top_feature = str(candidates.iloc[0]["feature"])
        values = np.unique(
            np.quantile(
                data[top_feature].dropna(),
                np.linspace(0.05, 0.95, 11),
            )
        )
        for value in values:
            counterfactual = data[features].copy()
            counterfactual[top_feature] = value
            probability = fitted.predict_proba(counterfactual)[:, 1]
            records.append(
                {
                    "target": target,
                    "profile_type": "numeric partial response",
                    "feature": top_feature,
                    "label": FEATURE_LABELS[top_feature],
                    "value": f"{value:.6g}",
                    "value_numeric": float(value),
                    "mean_predicted_probability": float(np.mean(probability)),
                    "observed_rows": len(data),
                }
            )
    return pd.DataFrame(records)


def plot_explanations(
    importance: pd.DataFrame,
    effects: pd.DataFrame,
    output: Path,
) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    figure, axes = plt.subplots(2, 2, figsize=(12, 8.5))
    colors = ["#276FBF", "#D1495B"]

    for column, target in enumerate(["shot", "box_entry"]):
        group = importance[
            importance["target"].eq(target)
            & importance["level"].eq("group")
        ].sort_values("delta_log_loss")
        axis = axes[0, column]
        errors = np.vstack(
            [
                group["delta_log_loss"] - group["ci_low"],
                group["ci_high"] - group["delta_log_loss"],
            ]
        )
        axis.barh(
            group["label"],
            group["delta_log_loss"],
            xerr=errors,
            color=colors[column],
            alpha=0.88,
            capsize=3,
        )
        axis.axvline(0, color="#333333", linewidth=0.8)
        axis.set_title(f"{TARGET_LABELS[target]}: feature-group importance")
        axis.set_xlabel("Held-out log-loss increase after permutation")
        axis.grid(axis="y", visible=False)

        profile = effects[
            effects["target"].eq(target)
            & effects["profile_type"].eq("numeric partial response")
        ].sort_values("value_numeric")
        axis = axes[1, column]
        axis.plot(
            profile["value_numeric"],
            profile["mean_predicted_probability"],
            color=colors[column],
            marker="o",
            linewidth=2,
        )
        axis.set_title(
            f"{TARGET_LABELS[target]}: model response to "
            f"{profile.iloc[0]['label'].lower()}"
        )
        axis.set_xlabel(profile.iloc[0]["label"])
        axis.set_ylabel("Mean predicted probability")

    figure.suptitle(
        "Retrospective model explanations",
        fontsize=15,
        fontweight="bold",
    )
    figure.text(
        0.5,
        0.01,
        "Permutation is evaluated out of fold and within matches. "
        "Response curves are descriptive, noncausal substitutions in final models.",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    figure.tight_layout(rect=[0, 0.04, 1, 0.96])
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)


def write_report(
    path: Path,
    selected_models: dict[str, dict[str, Any]],
    importance: pd.DataFrame,
    effects: pd.DataFrame,
) -> None:
    lines = [
        "# Coaching Model Explanations",
        "",
        "## Scope and method",
        "",
        "- These explanations apply only to the selected **retrospective** models. They do not turn completed-possession measurements into possession-start forecasts.",
        "- Permutation importance is evaluated on held-out match folds. Values are shuffled within each match, and positive values mean worse log loss after the information is disrupted.",
        "- Group intervals use a match-cluster bootstrap. They describe match-to-match sampling variation, not causal uncertainty.",
        "- Response profiles substitute one input while holding the recorded values of all other inputs fixed. They describe model behavior and are not intervention effects.",
        "",
        "## Selected models",
        "",
        "| Target | Model | Layout |",
        "|---|---|---|",
    ]
    for target, specification in selected_models.items():
        lines.append(
            f"| {TARGET_LABELS[target]} | {specification['model_name']} | "
            f"{specification['layout']} |"
        )

    lines.extend(
        [
            "",
            "## Feature-group importance",
            "",
            "| Target | Group | Delta log loss (95% CI) |",
            "|---|---|---:|",
        ]
    )
    groups = importance[importance["level"].eq("group")]
    for row in groups.sort_values(
        ["target", "delta_log_loss"],
        ascending=[True, False],
    ).itertuples(index=False):
        lines.append(
            f"| {TARGET_LABELS[row.target]} | {row.label} | "
            f"{row.delta_log_loss:+.4f} "
            f"({row.ci_low:+.4f}–{row.ci_high:+.4f}) |"
        )

    lines.extend(["", "## Most important individual inputs", ""])
    for target in ["shot", "box_entry"]:
        top = importance[
            importance["target"].eq(target)
            & importance["level"].eq("feature")
        ].nlargest(5, "delta_log_loss")
        items = ", ".join(
            f"{row.label} ({row.delta_log_loss:+.4f})"
            for row in top.itertuples(index=False)
        )
        lines.append(f"- **{TARGET_LABELS[target]}:** {items}.")

    lines.extend(["", "## Model response profiles", ""])
    for target in ["shot", "box_entry"]:
        numeric = effects[
            effects["target"].eq(target)
            & effects["profile_type"].eq("numeric partial response")
        ].sort_values("value_numeric")
        low = numeric.iloc[0]
        high = numeric.iloc[-1]
        lines.append(
            f"- **{TARGET_LABELS[target]}:** changing {low['label'].lower()} "
            f"from {low['value_numeric']:.2f} to {high['value_numeric']:.2f} "
            f"changes the final model's mean response from "
            f"{low['mean_predicted_probability']:.3f} to "
            f"{high['mean_predicted_probability']:.3f}."
        )
        for feature in ["attacking_style", "defensive_style"]:
            categorical = effects[
                effects["target"].eq(target)
                & effects["feature"].eq(feature)
            ].sort_values("mean_predicted_probability")
            lowest = categorical.iloc[0]
            highest = categorical.iloc[-1]
            lines.append(
                f"  - For {FEATURE_LABELS[feature].lower()}, the lowest and "
                f"highest mean substituted responses are "
                f"{lowest['value']} ({lowest['mean_predicted_probability']:.3f}) "
                f"and {highest['value']} "
                f"({highest['mean_predicted_probability']:.3f})."
            )

    lines.extend(
        [
            "",
            "All categorical substitution profiles are provided in `coaching_effect_profiles.csv`; they carry the same noncausal interpretation.",
            "",
            "## Why SHAP is not included",
            "",
            "SHAP was deliberately omitted from the primary deliverables. The two selected models use different estimator families, the tactical shape inputs are strongly related to one another, and one-hot style indicators make individual attributions sensitive to representation and background choices. A SHAP view would therefore be less comparable and potentially less stable than the same held-out, match-aware permutation procedure used for both targets. This decision should be revisited only with a predeclared background sample and an attribution-stability analysis.",
            "",
            "## Limits",
            "",
            "Importance does not establish that changing a feature will change an outcome. Full-possession shape and style can also contain information from after the possession began, including the shot frame for many shot possessions. The results support retrospective pattern description only.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--possessions", type=Path, default=DEFAULT_POSSESSIONS)
    parser.add_argument("--final-model", type=Path, default=DEFAULT_FINAL_MODEL)
    parser.add_argument(
        "--oof-predictions",
        type=Path,
        default=DEFAULT_OOF_PREDICTIONS,
    )
    parser.add_argument("--importance-output", type=Path, default=DEFAULT_IMPORTANCE)
    parser.add_argument("--effects-output", type=Path, default=DEFAULT_EFFECTS)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--figure-output", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument(
        "--permutation-repeats",
        type=int,
        default=PERMUTATION_REPEATS,
    )
    parser.add_argument(
        "--bootstrap-replicates",
        type=int,
        default=BOOTSTRAP_REPLICATES,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.permutation_repeats < 5:
        raise ValueError("Use at least five permutation repeats")
    if args.bootstrap_replicates < 1_000:
        raise ValueError("Use at least 1,000 bootstrap replicates")

    possessions = pd.read_csv(args.possessions, low_memory=False)
    data = possessions[
        possessions["attacking_style_cluster"].ge(0)
        & possessions["defensive_style_cluster"].ge(0)
        & possessions["period"].le(4)
    ].copy().reset_index(drop=True)
    final_bundle = joblib.load(args.final_model)
    selected_models = final_bundle["selected_models"]
    oof_predictions = pd.read_csv(args.oof_predictions)
    if not data["possession_uid"].equals(oof_predictions["possession_uid"]):
        raise RuntimeError("Possession order does not match saved OOF predictions")

    importance = permutation_importance(
        data,
        selected_models,
        oof_predictions,
        args.permutation_repeats,
        args.bootstrap_replicates,
    )
    effects = effect_profiles(data, selected_models, importance)

    for output in [args.importance_output, args.effects_output]:
        output.parent.mkdir(parents=True, exist_ok=True)
    importance.to_csv(args.importance_output, index=False)
    effects.to_csv(args.effects_output, index=False)
    plot_explanations(importance, effects, args.figure_output)
    write_report(args.report_output, selected_models, importance, effects)

    print(
        importance[importance["level"].eq("group")][
            ["target", "label", "delta_log_loss", "ci_low", "ci_high"]
        ].to_string(index=False)
    )
    print(f"Wrote importance table to {args.importance_output}")
    print(f"Wrote effect profiles to {args.effects_output}")
    print(f"Wrote explanation report to {args.report_output}")
    print(f"Wrote explanation figure to {args.figure_output}")


if __name__ == "__main__":
    main()
