#!/usr/bin/env python3
"""Validate recommendation policies with paired, overlap, sensitivity, and placebo tests."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from build_recommendation_simulator import (
    ATTACK_STYLES,
    MIN_PROPENSITY,
    feature_layouts,
    fit_propensity,
    policy_choices,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FEATURES = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_recommendation_features.csv"
)
DEFAULT_CANDIDATES = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_candidate_style_oof.csv"
)
DEFAULT_POLICY = PROJECT_ROOT / "results" / "recommendation_policy_evaluation.csv"
DEFAULT_PAIRED = (
    PROJECT_ROOT / "results" / "recommendation_paired_policy_tests.csv"
)
DEFAULT_PROPENSITY = (
    PROJECT_ROOT / "results" / "recommendation_propensity_diagnostics.csv"
)
DEFAULT_SENSITIVITY = (
    PROJECT_ROOT / "results" / "recommendation_propensity_sensitivity.csv"
)
DEFAULT_PLACEBO = (
    PROJECT_ROOT / "results" / "recommendation_policy_placebo.csv"
)
DEFAULT_CHOICES = (
    PROJECT_ROOT / "data" / "interim" / "recommendation_policy_choices.csv"
)
DEFAULT_REPORT = PROJECT_ROOT / "results" / "recommendation_validation_summary.md"

RANDOM_STATE = 42
CLIP_THRESHOLDS = (0.02, 0.05, 0.10)
BOOTSTRAP_ITERATIONS = 2_000
PLACEBO_ITERATIONS = 1_000


def paired_cluster_bootstrap(
    choices: pd.DataFrame,
    left: str,
    right: str,
    iterations: int = BOOTSTRAP_ITERATIONS,
) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_STATE)
    choices = choices.copy()
    choices["difference"] = choices[left] - choices[right]
    match_values = {
        match_id: group["difference"].to_numpy()
        for match_id, group in choices.groupby("match_id")
    }
    matches = np.array(list(match_values))
    estimates = np.empty(iterations)
    for index in range(iterations):
        sampled = rng.choice(matches, size=len(matches), replace=True)
        values = np.concatenate([match_values[match_id] for match_id in sampled])
        estimates[index] = values.mean()
    return {
        "mean_difference": float(choices["difference"].mean()),
        "ci_low": float(np.quantile(estimates, 0.025)),
        "ci_high": float(np.quantile(estimates, 0.975)),
        "bootstrap_probability_above_zero": float((estimates > 0).mean()),
    }


def propensity_diagnostics(
    propensity: pd.DataFrame,
    test: pd.DataFrame,
    fold: int,
) -> list[dict[str, float | int | str]]:
    joined = propensity.merge(
        test[["possession_uid", "attacking_style"]],
        on="possession_uid",
        how="left",
    )
    records = []
    for style, group in [
        ("__ALL__", joined),
        *list(joined.groupby("attacking_style")),
    ]:
        record: dict[str, float | int | str] = {
            "fold": fold,
            "style": style,
            "rows": len(group),
            "raw_propensity_mean": float(group["raw_propensity"].mean()),
            "raw_propensity_min": float(group["raw_propensity"].min()),
            "raw_propensity_p05": float(group["raw_propensity"].quantile(0.05)),
            "raw_propensity_p50": float(group["raw_propensity"].quantile(0.50)),
        }
        for threshold in CLIP_THRESHOLDS:
            clipped = group["raw_propensity"].clip(lower=threshold)
            weights = 1 / clipped
            record[f"fraction_below_{threshold:.2f}"] = float(
                group["raw_propensity"].lt(threshold).mean()
            )
            record[f"effective_sample_size_{threshold:.2f}"] = float(
                weights.sum() ** 2 / np.square(weights).sum()
            )
            record[f"max_weight_{threshold:.2f}"] = float(weights.max())
        records.append(record)
    return records


def q_style_lookup(
    candidates: pd.DataFrame,
    penalty: float,
    box_value_by_fold: dict[int, float],
) -> pd.DataFrame:
    frame = candidates.copy()
    frame["box_value"] = frame["validation_fold"].map(box_value_by_fold)
    frame["mean_score"] = (
        frame["expected_attacking_xg_mean"]
        + frame["box_value"] * frame["box_probability_mean"]
        - penalty * frame["expected_transition_xg_mean"]
    )
    return (
        frame.drop_duplicates(["possession_uid", "attacking_style"])
        .pivot(
            index="possession_uid",
            columns="attacking_style",
            values="mean_score",
        )
        .reindex(columns=ATTACK_STYLES)
    )


def outcome_placebo(
    choices: pd.DataFrame,
    q_styles: pd.DataFrame,
    iterations: int = PLACEBO_ITERATIONS,
) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE)
    ordered = choices.set_index("possession_uid").loc[q_styles.index].copy()
    patient_q = q_styles["Patient Build-up"].to_numpy()
    observed_action = ordered["attacking_style"].to_numpy()
    learned_action = ordered["recommended_style"].to_numpy()
    model_action = ordered["model_style"].to_numpy()
    q_observed = ordered["q_observed"].to_numpy()
    q_learned = ordered["q_policy"].to_numpy()
    q_model = np.array(
        [
            q_styles.loc[uid, style]
            for uid, style in zip(ordered.index, model_action)
        ]
    )
    propensity = ordered["propensity"].to_numpy()
    outcomes = ordered["realized_utility"].to_numpy()
    matches = ordered["match_id"].to_numpy()

    def differences(values: np.ndarray) -> tuple[float, float]:
        learned = q_learned + np.where(
            learned_action == observed_action,
            (values - q_observed) / propensity,
            0.0,
        )
        patient = patient_q + np.where(
            observed_action == "Patient Build-up",
            (values - q_observed) / propensity,
            0.0,
        )
        model_only = q_model + np.where(
            model_action == observed_action,
            (values - q_observed) / propensity,
            0.0,
        )
        return (
            float((learned - patient).mean()),
            float((model_only - patient).mean()),
        )

    observed_fallback_difference, observed_model_difference = differences(outcomes)
    fallback_placebos = np.empty(iterations)
    model_placebos = np.empty(iterations)
    match_indices = {
        match_id: np.flatnonzero(matches == match_id)
        for match_id in np.unique(matches)
    }
    for iteration in range(iterations):
        shuffled = outcomes.copy()
        for indices in match_indices.values():
            shuffled[indices] = rng.permutation(shuffled[indices])
        fallback_placebos[iteration], model_placebos[iteration] = differences(
            shuffled
        )
    records = []
    for policy_name, observed_difference, placebo_differences in [
        (
            "Fallback-enabled vs always Patient Build-up",
            observed_fallback_difference,
            fallback_placebos,
        ),
        (
            "Model-only vs always Patient Build-up",
            observed_model_difference,
            model_placebos,
        ),
    ]:
        records.append(
            {
                "test": "Shuffle realized utility within matches",
                "policy_comparison": policy_name,
                "observed_policy_difference": observed_difference,
                "placebo_mean": float(placebo_differences.mean()),
                "placebo_ci_low": float(
                    np.quantile(placebo_differences, 0.025)
                ),
                "placebo_ci_high": float(
                    np.quantile(placebo_differences, 0.975)
                ),
                "one_sided_placebo_p_value": float(
                    (placebo_differences >= observed_difference).mean()
                ),
                "iterations": iterations,
            }
        )
    return pd.DataFrame(records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--paired-output", type=Path, default=DEFAULT_PAIRED)
    parser.add_argument("--propensity-output", type=Path, default=DEFAULT_PROPENSITY)
    parser.add_argument("--sensitivity-output", type=Path, default=DEFAULT_SENSITIVITY)
    parser.add_argument("--placebo-output", type=Path, default=DEFAULT_PLACEBO)
    parser.add_argument("--choices-output", type=Path, default=DEFAULT_CHOICES)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = pd.read_csv(args.features, low_memory=False)
    candidates = pd.read_csv(args.candidates, low_memory=False)
    policy = pd.read_csv(args.policy)
    selected_penalty = float(
        policy.sort_values("value_rank").iloc[0]["transition_penalty"]
    )
    attack_numeric, _ = feature_layouts(data)
    propensity_numeric = [
        column for column in attack_numeric if not column.startswith("candidate_")
    ]

    choices_by_clip: dict[float, list[pd.DataFrame]] = {
        threshold: [] for threshold in CLIP_THRESHOLDS
    }
    propensity_records: list[dict[str, object]] = []
    box_value_by_fold: dict[int, float] = {}
    for fold in sorted(data["validation_fold"].unique()):
        fold_data = data[data["validation_fold"].eq(fold)]
        train = fold_data[~fold_data["is_test_fold"]]
        test = fold_data[fold_data["is_test_fold"]]
        fold_candidates = candidates[
            candidates["validation_fold"].eq(fold)
        ]
        propensity = fit_propensity(train, test, propensity_numeric)
        propensity_records.extend(propensity_diagnostics(propensity, test, fold))
        box_value = max(
            float(
                train.loc[
                    train["entered_penalty_area"].eq(1), "xg_generated"
                ].mean()
                - train.loc[
                    train["entered_penalty_area"].eq(0), "xg_generated"
                ].mean()
            ),
            0.0,
        )
        box_value_by_fold[fold] = box_value
        for threshold in CLIP_THRESHOLDS:
            adjusted = propensity.copy()
            adjusted["propensity"] = adjusted["raw_propensity"].clip(
                lower=threshold
            )
            choices_by_clip[threshold].append(
                policy_choices(
                    fold_candidates,
                    test,
                    train,
                    adjusted,
                    selected_penalty,
                    box_value,
                )
            )

    sensitivity_records = []
    for threshold, frames in choices_by_clip.items():
        choices = pd.concat(frames, ignore_index=True)
        sensitivity_records.append(
            {
                "clip_threshold": threshold,
                "rows": len(choices),
                "dr_policy_value": choices["dr_value"].mean(),
                "dr_model_only_value": choices["dr_model_only"].mean(),
                "dr_fallback_only_value": choices["dr_fallback_only"].mean(),
                "dr_always_patient_value": choices[
                    "dr_always__Patient Build-up"
                ].mean(),
                "policy_minus_always_patient": (
                    choices["dr_value"]
                    - choices["dr_always__Patient Build-up"]
                ).mean(),
                "model_only_minus_always_patient": (
                    choices["dr_model_only"]
                    - choices["dr_always__Patient Build-up"]
                ).mean(),
                "fraction_raw_propensity_below_clip": choices[
                    "raw_propensity"
                ].lt(threshold).mean(),
            }
        )
    sensitivity = pd.DataFrame(sensitivity_records)
    selected_choices = pd.concat(
        choices_by_clip[MIN_PROPENSITY], ignore_index=True
    )

    comparisons = {
        "Fallback-enabled policy vs always Patient Build-up": (
            "dr_value",
            "dr_always__Patient Build-up",
        ),
        "Model-only policy vs always Patient Build-up": (
            "dr_model_only",
            "dr_always__Patient Build-up",
        ),
        "Fallback-enabled policy vs historical fallback only": (
            "dr_value",
            "dr_fallback_only",
        ),
        "Model-only policy vs fallback-enabled policy": (
            "dr_model_only",
            "dr_value",
        ),
        "Fallback-enabled policy vs observed behavior": (
            "dr_value",
            "realized_utility",
        ),
    }
    paired_records = []
    for comparison, (left, right) in comparisons.items():
        paired_records.append(
            {
                "comparison": comparison,
                "left_metric": left,
                "right_metric": right,
                **paired_cluster_bootstrap(
                    selected_choices, left, right
                ),
            }
        )
    paired = pd.DataFrame(paired_records)
    q_styles = q_style_lookup(
        candidates, selected_penalty, box_value_by_fold
    )
    placebo = outcome_placebo(selected_choices, q_styles)
    propensity_frame = pd.DataFrame(propensity_records)

    for path in [
        args.paired_output,
        args.propensity_output,
        args.sensitivity_output,
        args.placebo_output,
        args.choices_output,
        args.report_output,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    paired.to_csv(args.paired_output, index=False)
    propensity_frame.to_csv(args.propensity_output, index=False)
    sensitivity.to_csv(args.sensitivity_output, index=False)
    placebo.to_csv(args.placebo_output, index=False)
    selected_choices.to_csv(args.choices_output, index=False)

    learned_test = paired[
        paired["comparison"].eq(
            "Fallback-enabled policy vs always Patient Build-up"
        )
    ].iloc[0]
    model_test = paired[
        paired["comparison"].eq(
            "Model-only policy vs always Patient Build-up"
        )
    ].iloc[0]
    report = [
        "# Recommendation Policy Validation",
        "",
        f"- Selected transition penalty: {selected_penalty:.2f}",
        f"- Fallback policy − always Patient Build-up: {learned_test['mean_difference']:.6f} "
        f"[{learned_test['ci_low']:.6f}, {learned_test['ci_high']:.6f}]",
        f"- Model-only − always Patient Build-up: {model_test['mean_difference']:.6f} "
        f"[{model_test['ci_low']:.6f}, {model_test['ci_high']:.6f}]",
        f"- Fallback outcome-shuffle placebo p-value: {placebo.iloc[0]['one_sided_placebo_p_value']:.4f}",
        f"- Model-only outcome-shuffle placebo p-value: {placebo.iloc[1]['one_sided_placebo_p_value']:.4f}",
        "",
        "A policy is not validated as superior unless its paired match-clustered "
        "interval is above zero and the advantage survives propensity sensitivity "
        "and placebo testing.",
    ]
    args.report_output.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(paired.to_string(index=False))
    print(sensitivity.to_string(index=False))
    print(placebo.to_string(index=False))
    print(f"Wrote validation summary to {args.report_output}")


if __name__ == "__main__":
    main()
