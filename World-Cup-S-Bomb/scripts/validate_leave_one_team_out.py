#!/usr/bin/env python3
"""Run leave-one-team-out validation for the model-only recommendation policy."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from build_recommendation_simulator import (
    ATTACK_STYLES,
    CATEGORICAL_FEATURES,
    MIN_PROPENSITY,
    candidate_rows,
    feature_layouts,
    fit_propensity,
    model_families,
    pipeline,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FEATURES = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_recommendation_features.csv"
)
DEFAULT_STYLES = PROJECT_ROOT / "results" / "attacking_style_profiles.csv"
DEFAULT_TEAM_RESULTS = (
    PROJECT_ROOT / "results" / "recommendation_leave_one_team_out.csv"
)
DEFAULT_CHOICES = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "recommendation_leave_one_team_out_choices.csv"
)
DEFAULT_REPORT = (
    PROJECT_ROOT / "results" / "recommendation_leave_one_team_out.md"
)

RANDOM_STATE = 42
BOOTSTRAP_ITERATIONS = 2_000


def fit_attack_family(
    train: pd.DataFrame,
    candidates: pd.DataFrame,
    classifier: object,
    regressor: object,
    numeric: list[str],
) -> pd.DataFrame:
    columns = CATEGORICAL_FEATURES + numeric
    shot_model = pipeline(classifier, numeric, CATEGORICAL_FEATURES)
    shot_model.fit(train[columns], train["shot"].astype(int))
    shot_probability = shot_model.predict_proba(candidates[columns])[:, 1]

    xg_train = train[train["shot"].eq(1)]
    xg_model = pipeline(regressor, numeric, CATEGORICAL_FEATURES)
    xg_model.fit(xg_train[columns], xg_train["xg_generated"])
    conditional_xg = np.clip(xg_model.predict(candidates[columns]), 0, None)

    box_model = pipeline(classifier, numeric, CATEGORICAL_FEATURES)
    box_model.fit(
        train[columns], train["entered_penalty_area"].astype(int)
    )
    box_probability = box_model.predict_proba(candidates[columns])[:, 1]

    output = candidates[
        [
            "possession_uid",
            "match_id",
            "team",
            "attacking_style",
        ]
    ].copy()
    output["expected_xg"] = shot_probability * conditional_xg
    output["box_probability"] = box_probability
    return output


def match_cluster_interval(
    choices: pd.DataFrame, iterations: int = BOOTSTRAP_ITERATIONS
) -> tuple[float, float, float]:
    rng = np.random.default_rng(RANDOM_STATE)
    groups = {
        match_id: group["policy_difference"].to_numpy()
        for match_id, group in choices.groupby("match_id")
    }
    matches = np.array(list(groups))
    estimates = np.empty(iterations)
    for index in range(iterations):
        sampled = rng.choice(matches, size=len(matches), replace=True)
        estimates[index] = np.concatenate(
            [groups[match_id] for match_id in sampled]
        ).mean()
    return (
        float(choices["policy_difference"].mean()),
        float(np.quantile(estimates, 0.025)),
        float(np.quantile(estimates, 0.975)),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--styles", type=Path, default=DEFAULT_STYLES)
    parser.add_argument("--team-output", type=Path, default=DEFAULT_TEAM_RESULTS)
    parser.add_argument("--choices-output", type=Path, default=DEFAULT_CHOICES)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    all_rows = pd.read_csv(args.features, low_memory=False)
    data = all_rows[all_rows["is_test_fold"]].copy().reset_index(drop=True)
    styles = pd.read_csv(args.styles)
    attack_numeric, _ = feature_layouts(data)
    propensity_numeric = [
        column for column in attack_numeric if not column.startswith("candidate_")
    ]
    family_specs = model_families()
    choice_frames = []
    team_records = []

    for team in sorted(data["team"].unique()):
        train = data[
            ~data["team"].eq(team) & ~data["opponent"].eq(team)
        ].copy()
        test = data[data["team"].eq(team)].copy()
        candidates = candidate_rows(test, styles)
        family_frames = []
        for family, (classifier, regressor) in family_specs.items():
            prediction = fit_attack_family(
                train,
                candidates,
                classifier,
                regressor,
                attack_numeric,
            )
            prediction["model_family"] = family
            family_frames.append(prediction)
        family_predictions = pd.concat(family_frames, ignore_index=True)
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
        family_predictions["score"] = (
            family_predictions["expected_xg"]
            + box_value * family_predictions["box_probability"]
        )
        mean_scores = (
            family_predictions.groupby(
                ["possession_uid", "attacking_style"]
            )["score"]
            .mean()
            .unstack()
            .reindex(columns=ATTACK_STYLES)
        )
        recommended = mean_scores.idxmax(axis=1)
        propensity = fit_propensity(train, test, propensity_numeric).set_index(
            "possession_uid"
        )
        observed = test.set_index("possession_uid")
        observed_q = np.array(
            [
                mean_scores.loc[uid, style]
                for uid, style in observed["attacking_style"].items()
            ]
        )
        policy_q = np.array(
            [
                mean_scores.loc[uid, style]
                for uid, style in recommended.items()
            ]
        )
        patient_q = mean_scores["Patient Build-up"].to_numpy()
        propensity_values = propensity.loc[observed.index, "raw_propensity"].clip(
            lower=MIN_PROPENSITY
        ).to_numpy()
        realized = (
            observed["xg_generated"]
            + box_value * observed["entered_penalty_area"]
        ).to_numpy()
        observed_actions = observed["attacking_style"].to_numpy()
        recommended_actions = recommended.loc[observed.index].to_numpy()
        model_dr = policy_q + np.where(
            recommended_actions == observed_actions,
            (realized - observed_q) / propensity_values,
            0.0,
        )
        patient_dr = patient_q + np.where(
            observed_actions == "Patient Build-up",
            (realized - observed_q) / propensity_values,
            0.0,
        )
        choices = pd.DataFrame(
            {
                "possession_uid": observed.index,
                "match_id": observed["match_id"].to_numpy(),
                "held_out_team": team,
                "observed_style": observed_actions,
                "recommended_style": recommended_actions,
                "raw_propensity": propensity.loc[
                    observed.index, "raw_propensity"
                ].to_numpy(),
                "model_policy_value": model_dr,
                "always_patient_value": patient_dr,
            }
        )
        choices["policy_difference"] = (
            choices["model_policy_value"] - choices["always_patient_value"]
        )
        choice_frames.append(choices)
        team_records.append(
            {
                "team": team,
                "possessions": len(choices),
                "matches": choices["match_id"].nunique(),
                "model_policy_value": choices["model_policy_value"].mean(),
                "always_patient_value": choices["always_patient_value"].mean(),
                "policy_difference": choices["policy_difference"].mean(),
                "positive_difference": choices["policy_difference"].mean() > 0,
                "observed_style_match_rate": (
                    choices["recommended_style"] == choices["observed_style"]
                ).mean(),
                "fraction_propensity_below_005": choices[
                    "raw_propensity"
                ].lt(MIN_PROPENSITY).mean(),
            }
        )
        print(
            f"{team}: Δ={team_records[-1]['policy_difference']:.5f} "
            f"({len(choices):,} possessions)",
            flush=True,
        )

    all_choices = pd.concat(choice_frames, ignore_index=True)
    team_results = pd.DataFrame(team_records).sort_values(
        "policy_difference", ascending=False
    )
    mean, low, high = match_cluster_interval(all_choices)
    positive_teams = int(team_results["positive_difference"].sum())
    report = [
        "# Leave-One-Team-Out Recommendation Validation",
        "",
        f"- Teams held out: {len(team_results)}",
        f"- Overall model-only − always Patient Build-up: {mean:.6f} [{low:.6f}, {high:.6f}]",
        f"- Teams with a positive difference: {positive_teams}/{len(team_results)}",
        f"- Median team difference: {team_results['policy_difference'].median():.6f}",
        f"- Worst team difference: {team_results['policy_difference'].min():.6f}",
        "",
        "Each model was trained without any match involving the held-out team. "
        "Prior player/team summaries remain available as supplied input features, "
        "matching the intended new-team use case.",
    ]
    for path in [args.team_output, args.choices_output, args.report_output]:
        path.parent.mkdir(parents=True, exist_ok=True)
    team_results.to_csv(args.team_output, index=False)
    all_choices.to_csv(args.choices_output, index=False)
    args.report_output.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
