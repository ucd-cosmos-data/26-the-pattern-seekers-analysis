#!/usr/bin/env python3
"""Build and validate a candidate-style attacking recommendation simulator."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier, XGBRegressor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FEATURES = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_recommendation_features.csv"
)
DEFAULT_STYLE_PROFILES = PROJECT_ROOT / "results" / "attacking_style_profiles.csv"
DEFAULT_POLICY_RESULTS = (
    PROJECT_ROOT / "results" / "recommendation_policy_evaluation.csv"
)
DEFAULT_CANDIDATES = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_candidate_style_oof.csv"
)
DEFAULT_REPORT = PROJECT_ROOT / "results" / "recommendation_simulator_summary.md"
DEFAULT_DEMO_JSON = (
    PROJECT_ROOT / "results" / "argentina_france_recommendation.json"
)
DEFAULT_DEMO_MD = (
    PROJECT_ROOT / "results" / "argentina_france_recommendation.md"
)
DEFAULT_MODEL = PROJECT_ROOT / "models" / "recommendation_simulator.joblib"

RANDOM_STATE = 42
FINAL_MATCH_ID = 3869685
MIN_PROPENSITY = 0.05
STYLE_PRIOR_POSSESSIONS = 50.0
PENALTY_GRID = (0.0, 0.25, 0.5, 1.0, 1.5, 2.0)
ATTACK_STYLES = [
    "Patient Build-up",
    "Short Under Pressure",
    "Direct Long Play",
]
CATEGORICAL_FEATURES = [
    "attacking_style",
    "play_pattern",
    "competition_stage",
    "score_state",
]
PROPENSITY_CATEGORICAL = [
    "play_pattern",
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


def model_families() -> dict[str, tuple[object, object]]:
    return {
        "Linear": (
            LogisticRegression(
                C=0.5, max_iter=2_000, solver="lbfgs", random_state=RANDOM_STATE
            ),
            Ridge(alpha=10.0),
        ),
        "Random Forest": (
            RandomForestClassifier(
                n_estimators=300,
                min_samples_leaf=8,
                max_features=0.7,
                n_jobs=2,
                random_state=RANDOM_STATE,
            ),
            RandomForestRegressor(
                n_estimators=300,
                min_samples_leaf=6,
                max_features=0.7,
                n_jobs=2,
                random_state=RANDOM_STATE,
            ),
        ),
        "Gradient Boosting": (
            GradientBoostingClassifier(
                n_estimators=250,
                learning_rate=0.035,
                max_depth=2,
                min_samples_leaf=10,
                subsample=0.85,
                random_state=RANDOM_STATE,
            ),
            GradientBoostingRegressor(
                n_estimators=250,
                learning_rate=0.035,
                max_depth=2,
                min_samples_leaf=8,
                subsample=0.85,
                loss="huber",
                random_state=RANDOM_STATE,
            ),
        ),
        "Histogram Gradient Boosting": (
            HistGradientBoostingClassifier(
                learning_rate=0.05,
                max_iter=250,
                max_leaf_nodes=15,
                min_samples_leaf=15,
                l2_regularization=2.0,
                random_state=RANDOM_STATE,
            ),
            HistGradientBoostingRegressor(
                learning_rate=0.05,
                max_iter=250,
                max_leaf_nodes=15,
                min_samples_leaf=12,
                l2_regularization=2.0,
                random_state=RANDOM_STATE,
            ),
        ),
        "XGBoost": (
            XGBClassifier(
                n_estimators=400,
                learning_rate=0.035,
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
            XGBRegressor(
                n_estimators=400,
                learning_rate=0.035,
                max_depth=3,
                min_child_weight=6,
                subsample=0.85,
                colsample_bytree=0.8,
                reg_lambda=3.0,
                objective="reg:squarederror",
                n_jobs=2,
                random_state=RANDOM_STATE,
            ),
        ),
    }


def make_preprocessor(
    numeric: list[str], categorical: list[str]
) -> ColumnTransformer:
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
                numeric,
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
                categorical,
            ),
        ],
        sparse_threshold=0,
    )


def pipeline(
    estimator: object, numeric: list[str], categorical: list[str]
) -> Pipeline:
    return Pipeline(
        [
            ("preprocess", make_preprocessor(numeric, categorical)),
            ("model", clone(estimator)),
        ]
    )


def feature_layouts(data: pd.DataFrame) -> tuple[list[str], list[str]]:
    history = [
        column
        for column in data
        if column.startswith(("team_", "opponent_", "candidate_"))
    ]
    players = [
        column
        for column in data
        if column.startswith(
            ("att_", "def_", "opp_counter_", "matchup_")
        )
    ]
    return CONTEXT_FEATURES + history, CONTEXT_FEATURES + history + players


def candidate_rows(
    rows: pd.DataFrame, style_profiles: pd.DataFrame
) -> pd.DataFrame:
    candidates = pd.concat(
        [rows.assign(attacking_style=style) for style in ATTACK_STYLES],
        ignore_index=True,
    )
    fingerprints = style_profiles.set_index("style_label")
    for column in [name for name in style_profiles if name.startswith("z_")]:
        candidates[f"candidate_{column}"] = candidates["attacking_style"].map(
            fingerprints[column]
        )
    return candidates


def fit_outcome_family(
    train: pd.DataFrame,
    candidates: pd.DataFrame,
    classifier: object,
    regressor: object,
    attack_numeric: list[str],
    transition_numeric: list[str],
) -> pd.DataFrame:
    attack_columns = CATEGORICAL_FEATURES + attack_numeric
    transition_columns = CATEGORICAL_FEATURES + transition_numeric

    shot_model = pipeline(classifier, attack_numeric, CATEGORICAL_FEATURES)
    shot_model.fit(train[attack_columns], train["shot"].astype(int))
    shot_probability = shot_model.predict_proba(candidates[attack_columns])[:, 1]

    xg_train = train[train["shot"].eq(1)]
    xg_model = pipeline(regressor, attack_numeric, CATEGORICAL_FEATURES)
    xg_model.fit(xg_train[attack_columns], xg_train["xg_generated"])
    conditional_xg = np.clip(
        xg_model.predict(candidates[attack_columns]), 0, None
    )

    box_model = pipeline(classifier, attack_numeric, CATEGORICAL_FEATURES)
    box_model.fit(
        train[attack_columns], train["entered_penalty_area"].astype(int)
    )
    box_probability = box_model.predict_proba(candidates[attack_columns])[:, 1]

    final_model = pipeline(classifier, transition_numeric, CATEGORICAL_FEATURES)
    final_model.fit(
        train[transition_columns],
        train["transition_final_third_15"].astype(int),
    )
    final_probability = final_model.predict_proba(
        candidates[transition_columns]
    )[:, 1]

    conditional_train = train[train["transition_final_third_15"].eq(1)]
    transition_box_model = pipeline(
        classifier, transition_numeric, CATEGORICAL_FEATURES
    )
    transition_box_model.fit(
        conditional_train[transition_columns],
        conditional_train["transition_box_15"].astype(int),
    )
    conditional_box = transition_box_model.predict_proba(
        candidates[transition_columns]
    )[:, 1]
    transition_box_probability = final_probability * conditional_box

    transition_xg_per_box = (
        train.loc[train["transition_box_15"].eq(1), "transition_xg_15"].mean()
    )
    if not np.isfinite(transition_xg_per_box):
        transition_xg_per_box = 0.0

    result = candidates[
        [
            "possession_uid",
            "match_id",
            "match_date",
            "team",
            "opponent",
            "attacking_style",
            "validation_fold",
        ]
    ].copy()
    result["shot_probability"] = shot_probability
    result["box_probability"] = box_probability
    result["expected_attacking_xg"] = shot_probability * conditional_xg
    result["transition_box_probability"] = transition_box_probability
    result["expected_transition_xg"] = (
        transition_box_probability * transition_xg_per_box
    )
    return result


def fit_propensity(
    train: pd.DataFrame,
    test: pd.DataFrame,
    numeric: list[str],
) -> pd.DataFrame:
    columns = PROPENSITY_CATEGORICAL + numeric
    model = pipeline(
        LogisticRegression(
            C=0.5,
            max_iter=2_000,
            solver="lbfgs",
            random_state=RANDOM_STATE,
        ),
        numeric,
        PROPENSITY_CATEGORICAL,
    )
    model.fit(train[columns], train["attacking_style"])
    probabilities = model.predict_proba(test[columns])
    class_index = {name: index for index, name in enumerate(model.classes_)}
    observed = np.array(
        [
            probabilities[row, class_index[style]]
            for row, style in enumerate(test["attacking_style"])
        ]
    )
    return pd.DataFrame(
        {
            "possession_uid": test["possession_uid"].to_numpy(),
            "raw_propensity": observed,
            "propensity": np.clip(observed, MIN_PROPENSITY, 1.0),
        }
    )


def historical_fallbacks(
    train: pd.DataFrame,
    test: pd.DataFrame,
    penalty: float,
    box_value: float,
) -> pd.Series:
    train = train.copy()
    global_style = (
        train.assign(
            realized_utility=(
                train["xg_generated"]
                + box_value * train["entered_penalty_area"]
                - penalty * train["transition_xg_15"]
            )
        )
        .groupby("attacking_style")["realized_utility"]
        .agg(["mean", "count"])
    )
    global_mean = float(train["xg_generated"].mean())
    records: dict[str, str] = {}
    train_dates = pd.to_datetime(train["match_date"])
    for match_id, match_rows in test.groupby("match_id"):
        date = pd.to_datetime(match_rows["match_date"]).min()
        for team in match_rows["team"].unique():
            history = train[
                train["team"].eq(team) & train_dates.lt(date)
            ].copy()
            history["realized_utility"] = (
                history["xg_generated"]
                + box_value * history["entered_penalty_area"]
                - penalty * history["transition_xg_15"]
            )
            team_style = history.groupby("attacking_style")[
                "realized_utility"
            ].agg(["mean", "count"])
            scores = {}
            for style in ATTACK_STYLES:
                team_mean = (
                    float(team_style.loc[style, "mean"])
                    if style in team_style.index
                    else global_mean
                )
                count = (
                    float(team_style.loc[style, "count"])
                    if style in team_style.index
                    else 0.0
                )
                prior_mean = (
                    float(global_style.loc[style, "mean"])
                    if style in global_style.index
                    else global_mean
                )
                scores[style] = (
                    count * team_mean + STYLE_PRIOR_POSSESSIONS * prior_mean
                ) / (count + STYLE_PRIOR_POSSESSIONS)
            chosen = max(scores, key=scores.get)
            for uid in match_rows.loc[
                match_rows["team"].eq(team), "possession_uid"
            ]:
                records[uid] = chosen
    return pd.Series(records, name="fallback_style")


def aggregate_family_predictions(family_frames: list[pd.DataFrame]) -> pd.DataFrame:
    stacked = pd.concat(
        [
            frame.assign(model_family=family)
            for family, frame in family_frames
        ],
        ignore_index=True,
    )
    metrics = [
        "shot_probability",
        "box_probability",
        "expected_attacking_xg",
        "transition_box_probability",
        "expected_transition_xg",
    ]
    keys = [
        "possession_uid",
        "match_id",
        "match_date",
        "team",
        "opponent",
        "attacking_style",
        "validation_fold",
    ]
    means = stacked.groupby(keys)[metrics].mean().add_suffix("_mean")
    standard_deviations = stacked.groupby(keys)[metrics].std().add_suffix("_std")
    output = pd.concat([means, standard_deviations], axis=1).reset_index()
    return output.merge(
        stacked[
            keys + ["model_family"] + metrics
        ],
        on=keys,
        how="left",
    )


def policy_choices(
    candidate_predictions: pd.DataFrame,
    test: pd.DataFrame,
    train: pd.DataFrame,
    propensity: pd.DataFrame,
    penalty: float,
    box_value: float,
) -> pd.DataFrame:
    candidates = candidate_predictions.copy()
    candidates["family_score"] = (
        candidates["expected_attacking_xg"]
        + box_value * candidates["box_probability"]
        - penalty * candidates["expected_transition_xg"]
    )
    candidates["mean_score"] = (
        candidates["expected_attacking_xg_mean"]
        + box_value * candidates["box_probability_mean"]
        - penalty * candidates["expected_transition_xg_mean"]
    )
    vote_counts = (
        candidates.sort_values("family_score", ascending=False)
        .groupby(["possession_uid", "model_family"], as_index=False)
        .first()
        .groupby(["possession_uid", "attacking_style"])
        .size()
        .rename("family_votes")
        .reset_index()
    )
    summary = candidates.drop_duplicates(
        ["possession_uid", "attacking_style"]
    ).merge(vote_counts, on=["possession_uid", "attacking_style"], how="left")
    summary = summary.sort_values(
        ["possession_uid", "mean_score"], ascending=[True, False]
    )
    top = summary.groupby("possession_uid").nth(0).reset_index()
    second = summary.groupby("possession_uid").nth(1).reset_index()
    choice = top[
        [
            "possession_uid",
            "attacking_style",
            "mean_score",
            "family_votes",
        ]
    ].rename(
        columns={
            "attacking_style": "model_style",
            "mean_score": "model_score",
        }
    )
    choice["runner_up_score"] = second["mean_score"].to_numpy()
    choice["score_margin"] = (
        choice["model_score"] - choice["runner_up_score"]
    )
    family_scores = candidates[
        ["possession_uid", "model_family", "attacking_style", "family_score"]
    ]
    top_family = choice[
        ["possession_uid", "model_style"]
    ].merge(
        family_scores,
        left_on=["possession_uid", "model_style"],
        right_on=["possession_uid", "attacking_style"],
        how="left",
    ).rename(columns={"family_score": "top_family_score"})
    runner_family = choice[
        ["possession_uid"]
    ].assign(runner_style=second["attacking_style"].to_numpy()).merge(
        family_scores,
        left_on=["possession_uid", "runner_style"],
        right_on=["possession_uid", "attacking_style"],
        how="left",
    ).rename(columns={"family_score": "runner_family_score"})
    family_differences = top_family[
        ["possession_uid", "model_family", "top_family_score"]
    ].merge(
        runner_family[
            ["possession_uid", "model_family", "runner_family_score"]
        ],
        on=["possession_uid", "model_family"],
        how="inner",
    )
    family_differences["family_score_difference"] = (
        family_differences["top_family_score"]
        - family_differences["runner_family_score"]
    )
    uncertainty = family_differences.groupby("possession_uid")[
        "family_score_difference"
    ].agg(["mean", "std", "count"])
    uncertainty["score_margin_se"] = uncertainty["std"].fillna(0) / np.sqrt(
        uncertainty["count"].clip(lower=1)
    )
    # A one-sided 95% model-family disagreement bound is a pragmatic
    # uncertainty guard, not a formal causal confidence interval.
    uncertainty["score_margin_lower_bound"] = (
        uncertainty["mean"] - 1.645 * uncertainty["score_margin_se"]
    )
    choice = choice.merge(
        uncertainty[
            ["score_margin_se", "score_margin_lower_bound"]
        ].reset_index(),
        on="possession_uid",
        how="left",
    )
    choice["clear_winner"] = (
        choice["family_votes"].ge(4)
        & choice["score_margin_lower_bound"].gt(0)
    )
    fallbacks = historical_fallbacks(train, test, penalty, box_value)
    choice = choice.merge(
        fallbacks.rename_axis("possession_uid").reset_index(),
        on="possession_uid",
        how="left",
    )
    choice["recommended_style"] = np.where(
        choice["clear_winner"],
        choice["model_style"],
        choice["fallback_style"],
    )
    observed = test[
        [
            "possession_uid",
            "match_id",
            "team",
            "attacking_style",
            "xg_generated",
            "entered_penalty_area",
            "transition_xg_15",
        ]
    ].copy()
    observed["realized_utility"] = (
        observed["xg_generated"]
        + box_value * observed["entered_penalty_area"]
        - penalty * observed["transition_xg_15"]
    )
    choice = choice.merge(observed, on="possession_uid", how="left")
    choice = choice.merge(propensity, on="possession_uid", how="left")
    mean_scores = summary[
        ["possession_uid", "attacking_style", "mean_score"]
    ]
    policy_score = mean_scores.rename(
        columns={
            "attacking_style": "recommended_style",
            "mean_score": "q_policy",
        }
    )
    observed_score = mean_scores.rename(
        columns={
            "attacking_style": "attacking_style",
            "mean_score": "q_observed",
        }
    )
    choice = choice.merge(
        policy_score,
        on=["possession_uid", "recommended_style"],
        how="left",
    ).merge(
        observed_score,
        on=["possession_uid", "attacking_style"],
        how="left",
    )
    matched = choice["recommended_style"].eq(choice["attacking_style"])
    choice["dr_value"] = choice["q_policy"] + np.where(
        matched,
        (choice["realized_utility"] - choice["q_observed"])
        / choice["propensity"],
        0.0,
    )
    score_lookup = summary.pivot(
        index="possession_uid",
        columns="attacking_style",
        values="mean_score",
    )

    def dr_for_policy(policy_styles: pd.Series) -> np.ndarray:
        policy_q = np.array(
            [
                score_lookup.loc[uid, style]
                for uid, style in zip(
                    choice["possession_uid"], policy_styles
                )
            ]
        )
        policy_matches = policy_styles.to_numpy() == choice[
            "attacking_style"
        ].to_numpy()
        return policy_q + np.where(
            policy_matches,
            (choice["realized_utility"].to_numpy() - choice["q_observed"].to_numpy())
            / choice["propensity"].to_numpy(),
            0.0,
        )

    choice["dr_model_only"] = dr_for_policy(choice["model_style"])
    choice["dr_fallback_only"] = dr_for_policy(choice["fallback_style"])
    for style in ATTACK_STYLES:
        choice[f"dr_always__{style}"] = dr_for_policy(
            pd.Series(style, index=choice.index)
        )
    choice["penalty"] = penalty
    choice["box_value"] = box_value
    return choice


def cluster_bootstrap_interval(
    choices: pd.DataFrame, iterations: int = 1_000
) -> tuple[float, float, float]:
    rng = np.random.default_rng(RANDOM_STATE)
    matches = choices["match_id"].unique()
    means = np.empty(iterations)
    groups = {
        match_id: group["dr_value"].to_numpy()
        for match_id, group in choices.groupby("match_id")
    }
    for iteration in range(iterations):
        sampled = rng.choice(matches, size=len(matches), replace=True)
        values = np.concatenate([groups[match_id] for match_id in sampled])
        means[iteration] = values.mean()
    return (
        float(choices["dr_value"].mean()),
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
    )


def simulate_fold(
    fold_data: pd.DataFrame,
    style_profiles: pd.DataFrame,
    attack_numeric: list[str],
    transition_numeric: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = fold_data[~fold_data["is_test_fold"]].copy()
    test = fold_data[fold_data["is_test_fold"]].copy()
    candidates = candidate_rows(test, style_profiles)
    family_outputs: list[tuple[str, pd.DataFrame]] = []
    fitted_models: dict[str, object] = {}
    for family, (classifier, regressor) in model_families().items():
        output = fit_outcome_family(
            train,
            candidates,
            classifier,
            regressor,
            attack_numeric,
            transition_numeric,
        )
        family_outputs.append((family, output))
        fitted_models[family] = {
            "classifier_spec": str(classifier),
            "regressor_spec": str(regressor),
        }
    aggregated = aggregate_family_predictions(family_outputs)
    propensity_numeric = [
        column
        for column in attack_numeric
        if not column.startswith("candidate_")
    ]
    propensity = fit_propensity(train, test, propensity_numeric)
    return aggregated, propensity, pd.DataFrame(
        [{"family": key, "specification": value} for key, value in fitted_models.items()]
    )


def argentina_france_demo(
    data: pd.DataFrame,
    candidates: pd.DataFrame,
    selected_penalty: float,
    box_value: float,
    style_profiles: pd.DataFrame,
) -> tuple[dict[str, object], str]:
    final_rows = data[
        data["match_id"].eq(FINAL_MATCH_ID) & data["is_test_fold"]
    ]
    final_candidates = candidates[candidates["match_id"].eq(FINAL_MATCH_ID)].copy()
    recommendations = []
    fingerprints = style_profiles.set_index("style_label")
    for team in ["Argentina", "France"]:
        team_rows = final_candidates[final_candidates["team"].eq(team)].copy()
        team_rows["score"] = (
            team_rows["expected_attacking_xg_mean"]
            + box_value * team_rows["box_probability_mean"]
            - selected_penalty * team_rows["expected_transition_xg_mean"]
        )
        profiles = (
            team_rows.groupby("attacking_style")
            .agg(
                expected_xg=("expected_attacking_xg_mean", "mean"),
                box_probability=("box_probability_mean", "mean"),
                transition_probability=(
                    "transition_box_probability_mean",
                    "mean",
                ),
                score=("score", "mean"),
            )
            .sort_values("score", ascending=False)
        )
        top_style = str(profiles.index[0])
        second_style = str(profiles.index[1])
        margin = float(profiles.iloc[0]["score"] - profiles.iloc[1]["score"])
        family_style = team_rows.groupby(
            ["model_family", "attacking_style"]
        )["score"].mean().unstack()
        family_votes = int(family_style.idxmax(axis=1).eq(top_style).sum())
        family_difference = (
            family_style[top_style] - family_style[second_style]
        )
        margin_lower_bound = float(
            family_difference.mean()
            - 1.645
            * family_difference.std(ddof=1)
            / np.sqrt(max(len(family_difference), 1))
        )
        clear = family_votes >= 4 and margin_lower_bound > 0
        if not clear:
            fold = int(final_rows["validation_fold"].iloc[0])
            training_history = data[
                data["validation_fold"].eq(fold)
                & ~data["is_test_fold"]
                & data["team"].eq(team)
                & pd.to_datetime(data["match_date"]).lt(
                    pd.to_datetime(final_rows["match_date"]).min()
                )
            ].copy()
            training_history["historical_utility"] = (
                training_history["xg_generated"]
                + box_value * training_history["entered_penalty_area"]
                - selected_penalty * training_history["transition_xg_15"]
            )
            global_history = data[
                data["validation_fold"].eq(fold) & ~data["is_test_fold"]
            ].copy()
            global_history["historical_utility"] = (
                global_history["xg_generated"]
                + box_value * global_history["entered_penalty_area"]
                - selected_penalty * global_history["transition_xg_15"]
            )
            global_means = global_history.groupby("attacking_style")[
                "historical_utility"
            ].mean()
            team_summary = training_history.groupby("attacking_style")[
                "historical_utility"
            ].agg(["mean", "count"])
            fallback_scores = {}
            for style in ATTACK_STYLES:
                prior = float(global_means.get(style, global_history["historical_utility"].mean()))
                count = float(team_summary.loc[style, "count"]) if style in team_summary.index else 0.0
                mean = float(team_summary.loc[style, "mean"]) if style in team_summary.index else prior
                fallback_scores[style] = (
                    count * mean + STYLE_PRIOR_POSSESSIONS * prior
                ) / (count + STYLE_PRIOR_POSSESSIONS)
            top_style = max(fallback_scores, key=fallback_scores.get)
        style_row = fingerprints.loc[top_style]
        recommendations.append(
            {
                "team": team,
                "recommended_style": top_style,
                "runner_up": second_style,
                "clear_model_winner": clear,
                "score_margin": margin,
                "model_family_votes": family_votes,
                "score_margin_lower_bound": margin_lower_bound,
                "style_scores": profiles.reset_index().to_dict("records"),
                "coaching_specifics": {
                    "tempo": (
                        "fast"
                        if style_row["z_progression_speed"] > 0.5
                        else "controlled"
                    ),
                    "passing": (
                        "longer and more direct"
                        if style_row["z_average_pass_length"] > 0.5
                        else "shorter combinations"
                    ),
                    "width": (
                        "use the full width"
                        if style_row["z_width_span_y"] > 0
                        else "favor compact channels"
                    ),
                    "carrying": (
                        "encourage progressive carries"
                        if style_row["z_progressive_carry_share"] > 0
                        else "progress primarily through passing"
                    ),
                },
                "explanation": (
                    "Model advantage across held-out pre-match scenarios."
                    if clear
                    else "No sufficiently clear model advantage; fallback uses the "
                    "team's prior attacking-style tendency."
                ),
            }
        )
    payload = {
        "fixture": "Argentina vs France",
        "match_id": FINAL_MATCH_ID,
        "status": "held-out retrospective pre-match demonstration",
        "selected_transition_penalty": selected_penalty,
        "box_entry_value": box_value,
        "recommendations": recommendations,
        "limitations": [
            "Observational policy evaluation is not proof of causal effectiveness.",
            "Transition risk remains low-confidence and receives constrained influence.",
            "The demonstration uses prior-only fold features and starting-lineup context.",
        ],
    }
    lines = [
        "# Argentina–France Held-Out Recommendation",
        "",
        f"- Selected transition penalty: {selected_penalty:.2f}",
        f"- Estimated box-entry value: {box_value:.4f} xG-equivalent",
        "",
    ]
    for item in recommendations:
        lines.extend(
            [
                f"## {item['team']}",
                "",
                f"**Recommendation:** {item['recommended_style']}",
                "",
                item["explanation"],
                "",
                f"- Tempo: {item['coaching_specifics']['tempo']}",
                f"- Passing: {item['coaching_specifics']['passing']}",
                f"- Width: {item['coaching_specifics']['width']}",
                f"- Carrying: {item['coaching_specifics']['carrying']}",
                "",
            ]
        )
    return payload, "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--style-profiles", type=Path, default=DEFAULT_STYLE_PROFILES)
    parser.add_argument("--policy-output", type=Path, default=DEFAULT_POLICY_RESULTS)
    parser.add_argument("--candidates-output", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--demo-json", type=Path, default=DEFAULT_DEMO_JSON)
    parser.add_argument("--demo-md", type=Path, default=DEFAULT_DEMO_MD)
    parser.add_argument("--model-output", type=Path, default=DEFAULT_MODEL)
    parser.add_argument(
        "--reuse-candidates",
        action="store_true",
        help="Reuse saved OOF candidate predictions and rerun only policy evaluation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = pd.read_csv(args.features, low_memory=False)
    styles = pd.read_csv(args.style_profiles)
    attack_numeric, transition_numeric = feature_layouts(data)
    candidate_frames = []
    propensity_frames = []
    model_specs_frames = []
    choice_frames: dict[float, list[pd.DataFrame]] = {
        penalty: [] for penalty in PENALTY_GRID
    }

    saved_candidates = (
        pd.read_csv(args.candidates_output, low_memory=False)
        if args.reuse_candidates and args.candidates_output.exists()
        else None
    )
    for fold in sorted(data["validation_fold"].unique()):
        fold_data = data[data["validation_fold"].eq(fold)]
        train = fold_data[~fold_data["is_test_fold"]]
        if saved_candidates is None:
            candidates, propensity, specifications = simulate_fold(
                fold_data, styles, attack_numeric, transition_numeric
            )
        else:
            candidates = saved_candidates[
                saved_candidates["validation_fold"].eq(fold)
            ].copy()
            propensity_numeric = [
                column
                for column in attack_numeric
                if not column.startswith("candidate_")
            ]
            propensity = fit_propensity(
                train,
                fold_data[fold_data["is_test_fold"]],
                propensity_numeric,
            )
            specifications = pd.DataFrame()
        candidate_frames.append(candidates)
        propensity_frames.append(propensity)
        if not specifications.empty:
            specifications["fold"] = fold
            model_specs_frames.append(specifications)
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
        for penalty in PENALTY_GRID:
            choice_frames[penalty].append(
                policy_choices(
                    candidates,
                    fold_data[fold_data["is_test_fold"]],
                    train,
                    propensity,
                    penalty,
                    box_value,
                )
            )

    all_candidates = pd.concat(candidate_frames, ignore_index=True)
    policy_records = []
    all_choices = {}
    for penalty, frames in choice_frames.items():
        choices = pd.concat(frames, ignore_index=True)
        all_choices[penalty] = choices
        mean, low, high = cluster_bootstrap_interval(choices)
        policy_records.append(
            {
                "transition_penalty": penalty,
                "dr_policy_value": mean,
                "ci_low": low,
                "ci_high": high,
                "clear_winner_rate": choices["clear_winner"].mean(),
                "fallback_rate": (~choices["clear_winner"]).mean(),
                "observed_style_match_rate": choices[
                    "recommended_style"
                ].eq(choices["attacking_style"]).mean(),
                "mean_propensity": choices["propensity"].mean(),
                "minimum_propensity": choices["propensity"].min(),
                "observed_behavior_value": choices["realized_utility"].mean(),
                "dr_model_only_value": choices["dr_model_only"].mean(),
                "dr_fallback_only_value": choices["dr_fallback_only"].mean(),
                **{
                    f"dr_always__{style}": choices[
                        f"dr_always__{style}"
                    ].mean()
                    for style in ATTACK_STYLES
                },
            }
        )
    policy_results = pd.DataFrame(policy_records)
    policy_results["value_rank"] = policy_results["dr_policy_value"].rank(
        ascending=False, method="min"
    )
    eligible = policy_results[
        policy_results["ci_low"].ge(policy_results.loc[
            policy_results["transition_penalty"].eq(0), "ci_low"
        ].iloc[0])
    ]
    selected = (
        eligible.sort_values(
            ["dr_policy_value", "transition_penalty"],
            ascending=[False, True],
        ).iloc[0]
        if not eligible.empty
        else policy_results.loc[
            policy_results["transition_penalty"].eq(0)
        ].iloc[0]
    )
    selected_penalty = float(selected["transition_penalty"])
    selected_choices = all_choices[selected_penalty]
    average_box_value = float(selected_choices["box_value"].mean())
    demo_payload, demo_markdown = argentina_france_demo(
        data,
        all_candidates,
        selected_penalty,
        average_box_value,
        styles,
    )

    for path in [
        args.policy_output,
        args.candidates_output,
        args.report_output,
        args.demo_json,
        args.demo_md,
        args.model_output,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    policy_results.to_csv(args.policy_output, index=False)
    all_candidates.to_csv(args.candidates_output, index=False)
    args.demo_json.write_text(
        json.dumps(demo_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    args.demo_md.write_text(demo_markdown + "\n", encoding="utf-8")
    report_lines = [
        "# Recommendation Simulator Policy Evaluation",
        "",
        f"- Selected transition penalty: {selected_penalty:.2f}",
        f"- Doubly robust policy value: {selected['dr_policy_value']:.5f}",
        f"- 95% clustered bootstrap interval: [{selected['ci_low']:.5f}, {selected['ci_high']:.5f}]",
        f"- Clear-winner rate: {selected['clear_winner_rate']:.2%}",
        f"- Historical fallback rate: {selected['fallback_rate']:.2%}",
        f"- Observed-behavior value: {selected['observed_behavior_value']:.5f}",
        f"- Historical-fallback-only value: {selected['dr_fallback_only_value']:.5f}",
        f"- Model-only value: {selected['dr_model_only_value']:.5f}",
        "",
        "Risk penalties were compared with match-clustered uncertainty. The lowest "
        "penalty among statistically competitive policies is preferred.",
        "",
        "This is observational off-policy evaluation and does not establish causal effects.",
    ]
    args.report_output.write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )
    joblib.dump(
        {
            "version": 1,
            "selected_transition_penalty": selected_penalty,
            "box_entry_value": average_box_value,
            "attack_styles": ATTACK_STYLES,
            "feature_layouts": {
                "attack_numeric": attack_numeric,
                "transition_numeric": transition_numeric,
                "categorical": CATEGORICAL_FEATURES,
            },
            "model_family_specifications": (
                pd.concat(model_specs_frames, ignore_index=True)
                if model_specs_frames
                else "Reused previously generated OOF candidate predictions"
            ),
            "policy_evaluation": policy_results,
            "note": (
                "Bundle contains validated architecture metadata. Production refit "
                "is deferred until external-format input is supplied."
            ),
        },
        args.model_output,
    )
    print(policy_results.to_string(index=False))
    print(f"Selected transition penalty: {selected_penalty:.2f}")
    print(f"Wrote simulator report to {args.report_output}")
    print(f"Wrote Argentina-France demo to {args.demo_md}")


if __name__ == "__main__":
    main()
