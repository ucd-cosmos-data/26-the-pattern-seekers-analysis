#!/usr/bin/env python3
"""Benchmark leakage-safe tactical and player-aware coaching model layouts."""

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
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POSSESSIONS = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_clusters.csv"
)
DEFAULT_COMPONENTS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_player_match_components.csv"
)
DEFAULT_LINEUPS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_possession_lineups.csv"
)
DEFAULT_FEATURES = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_player_aware_model_features.csv"
)
DEFAULT_LEADERBOARD = PROJECT_ROOT / "results" / "coaching_model_leaderboard.csv"
DEFAULT_FOLDS = PROJECT_ROOT / "results" / "coaching_model_fold_metrics.csv"
DEFAULT_PREDICTIONS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_coaching_model_oof_predictions.csv"
)
DEFAULT_REPORT = PROJECT_ROOT / "results" / "coaching_model_benchmark.md"
DEFAULT_MODEL = PROJECT_ROOT / "models" / "coaching_model_benchmark.joblib"

RANDOM_STATE = 42
N_SPLITS = 5
PRIOR_MINUTES = 270.0
PRIOR_ATTEMPTS = 30.0

RATE_SKILLS = {
    "progressive_passes_p90": "progressive_passes",
    "final_third_passes_p90": "final_third_passes",
    "box_passes_p90": "box_passes",
    "key_passes_p90": "key_passes",
    "crosses_p90": "crosses",
    "switches_p90": "switches",
    "through_balls_p90": "through_balls",
    "progressive_carries_p90": "progressive_carries",
    "shots_p90": "shots",
    "xg_p90": "xg_sum",
    "turnovers_p90": "turnovers",
    "pressures_p90": "pressures",
    "counterpressures_p90": "counterpressures",
    "interceptions_won_p90": "interceptions_won",
    "recoveries_p90": "recoveries",
    "blocks_p90": "blocks",
    "clearances_p90": "clearances",
    "dribbled_past_p90": "dribbled_past",
    "fouls_p90": "fouls",
}

RATIO_SKILLS = {
    "pass_completion": ("completed_passes", "passes"),
    "dribble_success": ("successful_dribbles", "dribbles"),
    "pressure_retention": (
        "successful_under_pressure_actions",
        "under_pressure_actions",
    ),
    "duel_win_rate": ("duels_won", "duels"),
    "interception_win_rate": ("interceptions_won", "interceptions"),
    "aerial_win_rate": ("aerial_wins", "aerial_events"),
}

MEAN_SKILLS = {
    "pass_progression_per_pass": ("pass_progression_sum", "passes"),
    "carry_progression_per_carry": ("carry_progression_sum", "carries"),
}

ATTACK_SKILLS = [
    "pass_completion",
    "progressive_passes_p90",
    "final_third_passes_p90",
    "box_passes_p90",
    "key_passes_p90",
    "crosses_p90",
    "switches_p90",
    "through_balls_p90",
    "progressive_carries_p90",
    "dribble_success",
    "shots_p90",
    "xg_p90",
    "pressure_retention",
    "turnovers_p90",
    "pass_progression_per_pass",
    "carry_progression_per_carry",
    "aerial_win_rate",
]

DEFENSE_SKILLS = [
    "pressures_p90",
    "counterpressures_p90",
    "duel_win_rate",
    "interceptions_won_p90",
    "interception_win_rate",
    "recoveries_p90",
    "blocks_p90",
    "clearances_p90",
    "dribbled_past_p90",
    "fouls_p90",
    "aerial_win_rate",
]

CATEGORICAL_FEATURES = [
    "attacking_style",
    "defensive_style",
    "play_pattern",
    "competition_stage",
]

TACTICAL_NUMERIC_FEATURES = [
    "period",
    "start_minute",
    "start_x",
    "start_y",
    "avg_back_line_height",
    "std_back_line_height",
    "avg_defensive_hull_area",
    "avg_defensive_width",
    "avg_defensive_depth",
    "avg_defenders_behind_ball",
    "avg_central_defenders",
    "avg_defenders_within_5",
    "avg_defenders_within_10",
    "avg_nearest_defender_distance",
    "avg_mean_defender_distance",
]

TARGETS = {
    "shot": "shot",
    "box_entry": "entered_penalty_area",
    "transition_conceded": "opponent_transition_shot",
}

ENSEMBLES = {
    "Soft Vote: All": [
        "Logistic Regression",
        "Random Forest",
        "Gradient Boosting",
        "Histogram Gradient Boosting",
        "XGBoost",
    ],
    "Soft Vote: Boosting": [
        "Gradient Boosting",
        "Histogram Gradient Boosting",
        "XGBoost",
    ],
    "Soft Vote: LR + XGB": ["Logistic Regression", "XGBoost"],
}


def mode_or_unknown(series: pd.Series) -> str:
    clean = series.dropna().astype(str)
    return clean.mode().iloc[0] if not clean.empty else "Unknown"


def aggregate_components(components: pd.DataFrame) -> pd.DataFrame:
    sum_columns = sorted(
        set(RATE_SKILLS.values())
        | {item for pair in RATIO_SKILLS.values() for item in pair}
        | {item for pair in MEAN_SKILLS.values() for item in pair}
        | {"minutes"}
    )
    aggregated = components.groupby("player_id")[sum_columns].sum()
    positions = components.groupby("player_id")["position_group"].agg(mode_or_unknown)
    aggregated["position_group"] = positions
    return aggregated


def prior_table(aggregated: pd.DataFrame) -> pd.DataFrame:
    groups = []
    labeled = aggregated.copy()
    for position, group in labeled.groupby("position_group"):
        totals = group.drop(columns=["position_group"]).sum()
        totals["position_group"] = position
        groups.append(totals)
    global_totals = labeled.drop(columns=["position_group"]).sum()
    global_totals["position_group"] = "__GLOBAL__"
    groups.append(global_totals)
    totals_table = pd.DataFrame(groups).set_index("position_group")
    priors = pd.DataFrame(index=totals_table.index)
    minutes = totals_table["minutes"].replace(0, np.nan)
    for skill, numerator in RATE_SKILLS.items():
        priors[skill] = 90 * totals_table[numerator] / minutes
    for skill, (numerator, denominator) in RATIO_SKILLS.items():
        priors[skill] = totals_table[numerator] / totals_table[denominator].replace(
            0, np.nan
        )
    for skill, (numerator, denominator) in MEAN_SKILLS.items():
        priors[skill] = totals_table[numerator] / totals_table[denominator].replace(
            0, np.nan
        )
    global_values = priors.loc["__GLOBAL__"]
    return priors.fillna(global_values)


def build_profiles(
    components: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    aggregated = aggregate_components(components)
    priors = prior_table(aggregated)
    profiles = pd.DataFrame(index=aggregated.index)
    profiles["position_group"] = aggregated["position_group"]
    profiles["profile_minutes"] = aggregated["minutes"]

    for skill, numerator in RATE_SKILLS.items():
        prior = aggregated["position_group"].map(priors[skill]).astype(float)
        profiles[skill] = (
            aggregated[numerator] + prior * PRIOR_MINUTES / 90
        ) / (aggregated["minutes"] + PRIOR_MINUTES) * 90
    for skill, (numerator, denominator) in RATIO_SKILLS.items():
        prior = aggregated["position_group"].map(priors[skill]).astype(float)
        profiles[skill] = (
            aggregated[numerator] + prior * PRIOR_ATTEMPTS
        ) / (aggregated[denominator] + PRIOR_ATTEMPTS)
    for skill, (numerator, denominator) in MEAN_SKILLS.items():
        prior = aggregated["position_group"].map(priors[skill]).astype(float)
        profiles[skill] = (
            aggregated[numerator] + prior * PRIOR_ATTEMPTS
        ) / (aggregated[denominator] + PRIOR_ATTEMPTS)
    return profiles, priors


def parse_player_ids(value: object) -> list[int]:
    if isinstance(value, list):
        return [int(item) for item in value]
    return [int(item) for item in json.loads(str(value))]


def player_vector(
    player_id: int,
    profiles: pd.DataFrame,
    priors: pd.DataFrame,
    positions: dict[int, str],
) -> pd.Series:
    if player_id in profiles.index:
        return profiles.loc[player_id]
    position = positions.get(player_id, "__GLOBAL__")
    if position not in priors.index:
        position = "__GLOBAL__"
    fallback = priors.loc[position].copy()
    fallback["position_group"] = position
    fallback["profile_minutes"] = 0.0
    return fallback


def aggregate_lineup(
    player_ids: list[int],
    profiles: pd.DataFrame,
    priors: pd.DataFrame,
    positions: dict[int, str],
    skills: list[str],
    prefix: str,
) -> dict[str, float]:
    vectors = pd.DataFrame(
        [player_vector(player_id, profiles, priors, positions) for player_id in player_ids]
    )
    if vectors.empty:
        fallback = priors.loc["__GLOBAL__"]
        vectors = pd.DataFrame([fallback])
        vectors["profile_minutes"] = 0.0
        vectors["position_group"] = "__GLOBAL__"
    outfield = vectors[~vectors["position_group"].eq("Goalkeeper")]
    if outfield.empty:
        outfield = vectors
    output: dict[str, float] = {}
    for skill in skills:
        output[f"{prefix}_mean_{skill}"] = float(outfield[skill].mean())
        output[f"{prefix}_max_{skill}"] = float(outfield[skill].max())
    output[f"{prefix}_mean_profile_minutes"] = float(
        outfield["profile_minutes"].mean()
    )
    output[f"{prefix}_known_player_share"] = float(
        outfield["profile_minutes"].gt(0).mean()
    )
    return output


def lineup_features(
    rows: pd.DataFrame,
    profiles: pd.DataFrame,
    priors: pd.DataFrame,
    positions: dict[int, str],
) -> pd.DataFrame:
    records: list[dict[str, float]] = []
    for row in rows.itertuples(index=False):
        attacking_ids = parse_player_ids(row.attacking_player_ids)
        defending_ids = parse_player_ids(row.defending_player_ids)
        record = aggregate_lineup(
            attacking_ids, profiles, priors, positions, ATTACK_SKILLS, "att"
        )
        record.update(
            aggregate_lineup(
                defending_ids, profiles, priors, positions, DEFENSE_SKILLS, "def"
            )
        )
        # The attacking lineup's defensive recovery ability describes rest
        # defense after losing possession; the defending lineup's attacking
        # ability describes the counter threat immediately after a regain.
        record.update(
            aggregate_lineup(
                attacking_ids,
                profiles,
                priors,
                positions,
                DEFENSE_SKILLS,
                "att_recovery",
            )
        )
        record.update(
            aggregate_lineup(
                defending_ids,
                profiles,
                priors,
                positions,
                ATTACK_SKILLS,
                "opp_counter",
            )
        )
        record["matchup_dribble_vs_duel"] = record[
            "att_max_dribble_success"
        ] * (1 - record["def_max_duel_win_rate"])
        record["matchup_pressure_resistance"] = record[
            "att_mean_pressure_retention"
        ] / (1 + record["def_mean_pressures_p90"])
        record["matchup_aerial_edge"] = (
            record["att_max_aerial_win_rate"]
            - record["def_max_aerial_win_rate"]
        )
        record["matchup_progression_vs_interception"] = record[
            "att_mean_progressive_passes_p90"
        ] / (1 + record["def_mean_interceptions_won_p90"])
        record["matchup_rest_defense_vs_counter"] = (
            record["att_recovery_mean_recoveries_p90"]
            + record["att_recovery_mean_pressures_p90"]
        ) / (
            1
            + record["opp_counter_mean_progressive_passes_p90"]
            + record["opp_counter_mean_progressive_carries_p90"]
        )
        record["matchup_turnover_counter_pressure"] = record[
            "att_mean_turnovers_p90"
        ] * (
            record["opp_counter_mean_progressive_passes_p90"]
            + record["opp_counter_mean_progressive_carries_p90"]
        )
        records.append(record)
    return pd.DataFrame(records, index=rows.index)


def cross_fitted_player_features(
    data: pd.DataFrame,
    components: pd.DataFrame,
    splits: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[pd.DataFrame, np.ndarray]:
    positions = (
        components.groupby("player_id")["position_group"]
        .agg(mode_or_unknown)
        .to_dict()
    )
    output: pd.DataFrame | None = None
    fold_ids = np.full(len(data), -1, dtype=int)
    for fold, (train_index, test_index) in enumerate(splits):
        train_matches = set(data.iloc[train_index]["match_id"])
        test_matches = set(data.iloc[test_index]["match_id"])
        fold_ids[test_index] = fold

        for match_id in sorted(train_matches):
            profile_source = components[
                components["match_id"].isin(train_matches)
                & components["match_id"].ne(match_id)
            ]
            profiles, priors = build_profiles(profile_source)
            row_index = data.index[
                data["match_id"].eq(match_id)
                & data.index.isin(data.index[train_index])
            ]
            features = lineup_features(
                data.loc[row_index], profiles, priors, positions
            )
            if output is None:
                output = pd.DataFrame(
                    np.nan, index=data.index, columns=features.columns
                )
            output.loc[row_index, features.columns] = features

        profile_source = components[components["match_id"].isin(train_matches)]
        profiles, priors = build_profiles(profile_source)
        row_index = data.index[data["match_id"].isin(test_matches)]
        features = lineup_features(data.loc[row_index], profiles, priors, positions)
        if output is None:
            output = pd.DataFrame(np.nan, index=data.index, columns=features.columns)
        output.loc[row_index, features.columns] = features

    if output is None or output.isna().any().any():
        raise RuntimeError("Cross-fitted player features are incomplete")
    return output, fold_ids


def model_definitions() -> dict[str, object]:
    return {
        "Logistic Regression": LogisticRegression(
            C=1.0, max_iter=2_000, solver="lbfgs", random_state=RANDOM_STATE
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=350,
            min_samples_leaf=8,
            max_features=0.7,
            n_jobs=2,
            random_state=RANDOM_STATE,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=250,
            learning_rate=0.035,
            max_depth=2,
            min_samples_leaf=10,
            subsample=0.85,
            random_state=RANDOM_STATE,
        ),
        "Histogram Gradient Boosting": HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_iter=250,
            max_leaf_nodes=15,
            min_samples_leaf=15,
            l2_regularization=1.0,
            random_state=RANDOM_STATE,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=400,
            learning_rate=0.035,
            max_depth=3,
            min_child_weight=8,
            subsample=0.85,
            colsample_bytree=0.8,
            reg_lambda=2.0,
            objective="binary:logistic",
            eval_metric="logloss",
            n_jobs=2,
            random_state=RANDOM_STATE,
        ),
    }


def preprocessor(numeric_features: list[str]) -> ColumnTransformer:
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


def expected_calibration_error(
    truth: np.ndarray, probability: np.ndarray, bins: int = 10
) -> float:
    edges = np.linspace(0, 1, bins + 1)
    assignments = np.clip(np.digitize(probability, edges) - 1, 0, bins - 1)
    error = 0.0
    for bin_id in range(bins):
        mask = assignments == bin_id
        if mask.any():
            error += mask.mean() * abs(truth[mask].mean() - probability[mask].mean())
    return float(error)


def score_predictions(truth: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    clipped = np.clip(probability, 1e-6, 1 - 1e-6)
    return {
        "log_loss": float(log_loss(truth, clipped, labels=[0, 1])),
        "brier": float(brier_score_loss(truth, clipped)),
        "roc_auc": float(roc_auc_score(truth, clipped)),
        "pr_auc": float(average_precision_score(truth, clipped)),
        "ece": expected_calibration_error(truth, clipped),
    }


def benchmark(
    data: pd.DataFrame,
    splits: list[tuple[np.ndarray, np.ndarray]],
    layouts: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    models = model_definitions()
    prediction_frame = data[["possession_uid", "match_id"]].copy()
    fold_records: list[dict[str, object]] = []
    leaderboard_records: list[dict[str, object]] = []

    for layout_name, numeric_features in layouts.items():
        feature_columns = CATEGORICAL_FEATURES + numeric_features
        for target_name, target_column in TARGETS.items():
            truth = data[target_column].astype(int).to_numpy()
            model_predictions: dict[str, np.ndarray] = {
                name: np.full(len(data), np.nan) for name in models
            }
            for fold, (train_index, test_index) in enumerate(splits):
                for model_name, estimator in models.items():
                    pipeline = Pipeline(
                        [
                            ("preprocess", preprocessor(numeric_features)),
                            ("model", clone(estimator)),
                        ]
                    )
                    pipeline.fit(
                        data.iloc[train_index][feature_columns],
                        truth[train_index],
                    )
                    probability = pipeline.predict_proba(
                        data.iloc[test_index][feature_columns]
                    )[:, 1]
                    model_predictions[model_name][test_index] = probability
                    metrics = score_predictions(truth[test_index], probability)
                    fold_records.append(
                        {
                            "layout": layout_name,
                            "target": target_name,
                            "model": model_name,
                            "fold": fold,
                            "test_matches": len(
                                set(data.iloc[test_index]["match_id"])
                            ),
                            "test_rows": len(test_index),
                            "positive_rate": truth[test_index].mean(),
                            **metrics,
                        }
                    )

            all_predictions = dict(model_predictions)
            for ensemble_name, members in ENSEMBLES.items():
                all_predictions[ensemble_name] = np.mean(
                    [model_predictions[name] for name in members], axis=0
                )
                for fold, (_, test_index) in enumerate(splits):
                    metrics = score_predictions(
                        truth[test_index],
                        all_predictions[ensemble_name][test_index],
                    )
                    fold_records.append(
                        {
                            "layout": layout_name,
                            "target": target_name,
                            "model": ensemble_name,
                            "fold": fold,
                            "test_matches": len(
                                set(data.iloc[test_index]["match_id"])
                            ),
                            "test_rows": len(test_index),
                            "positive_rate": truth[test_index].mean(),
                            **metrics,
                        }
                    )

            for model_name, probability in all_predictions.items():
                metrics = score_predictions(truth, probability)
                fold_subset = [
                    record
                    for record in fold_records
                    if record["layout"] == layout_name
                    and record["target"] == target_name
                    and record["model"] == model_name
                ]
                leaderboard_records.append(
                    {
                        "layout": layout_name,
                        "target": target_name,
                        "model": model_name,
                        "rows": len(data),
                        "matches": data["match_id"].nunique(),
                        "positive_rate": truth.mean(),
                        **metrics,
                        "fold_log_loss_std": float(
                            np.std([record["log_loss"] for record in fold_subset])
                        ),
                        "fold_brier_std": float(
                            np.std([record["brier"] for record in fold_subset])
                        ),
                    }
                )
                safe_name = (
                    f"{layout_name}__{target_name}__{model_name}"
                    .lower()
                    .replace(" ", "_")
                    .replace(":", "")
                    .replace("+", "plus")
                )
                prediction_frame[safe_name] = probability
            prediction_frame[f"truth__{target_name}"] = truth

    leaderboard = pd.DataFrame(leaderboard_records)
    leaderboard["target_rank"] = leaderboard.groupby("target")["log_loss"].rank(
        method="min"
    )
    leaderboard = leaderboard.sort_values(
        ["target", "log_loss", "brier", "model"]
    )
    return leaderboard, pd.DataFrame(fold_records), prediction_frame


def fit_selected_models(
    data: pd.DataFrame,
    leaderboard: pd.DataFrame,
    layouts: dict[str, list[str]],
) -> dict[str, object]:
    base_models = model_definitions()
    selected: dict[str, object] = {}
    for target_name, target_column in TARGETS.items():
        winner = leaderboard[leaderboard["target"].eq(target_name)].iloc[0]
        layout = str(winner["layout"])
        model_name = str(winner["model"])
        numeric = layouts[layout]
        columns = CATEGORICAL_FEATURES + numeric
        truth = data[target_column].astype(int)

        if model_name in base_models:
            pipeline = Pipeline(
                [
                    ("preprocess", preprocessor(numeric)),
                    ("model", clone(base_models[model_name])),
                ]
            )
            pipeline.fit(data[columns], truth)
            fitted: object = pipeline
        else:
            members = ENSEMBLES[model_name]
            pipelines = []
            for member in members:
                pipeline = Pipeline(
                    [
                        ("preprocess", preprocessor(numeric)),
                        ("model", clone(base_models[member])),
                    ]
                )
                pipeline.fit(data[columns], truth)
                pipelines.append((member, pipeline))
            fitted = {"kind": "equal_weight_ensemble", "members": pipelines}
        selected[target_name] = {
            "target_column": target_column,
            "layout": layout,
            "model_name": model_name,
            "categorical_features": CATEGORICAL_FEATURES,
            "numeric_features": numeric,
            "model": fitted,
            "cross_validated_metrics": {
                key: float(winner[key])
                for key in ["log_loss", "brier", "roc_auc", "pr_auc", "ece"]
            },
        }
    return selected


def write_report(
    path: Path,
    data: pd.DataFrame,
    leaderboard: pd.DataFrame,
    player_feature_count: int,
) -> None:
    lines = [
        "# Coaching Model Architecture Benchmark",
        "",
        "## Design",
        "",
        f"- Eligible possessions: {len(data):,}",
        f"- Matches: {data['match_id'].nunique()}",
        f"- Cross-validation: {N_SPLITS}-fold stratified group CV by match",
        f"- Derived lineup features: {player_feature_count}",
        "- Player profiles for every validation match were computed without that match.",
        "- Player and team names were excluded from predictive inputs.",
        "- Shot, goal, xG, box-entry, and transition outcomes were excluded from inputs.",
        "- Probabilities are compared primarily by log loss and Brier score; ROC-AUC, PR-AUC, and calibration error are secondary diagnostics.",
        "",
        "## Winners",
        "",
        "| Target | Layout | Model | Log loss | Brier | ROC-AUC | PR-AUC | ECE |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for target in TARGETS:
        row = leaderboard[leaderboard["target"].eq(target)].iloc[0]
        lines.append(
            f"| {target} | {row['layout']} | {row['model']} | "
            f"{row['log_loss']:.4f} | {row['brier']:.4f} | "
            f"{row['roc_auc']:.4f} | {row['pr_auc']:.4f} | {row['ece']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This benchmark selects predictive layouts, not causal treatment effects. "
            "The next recommendation layer must compare candidate attacking styles under "
            "the same context and apply uncertainty and risk constraints.",
            "",
            "Player skill values are empirical-Bayes estimates derived from event data and "
            "shrunk toward position priors. A future player can be processed with the same "
            "component schema without retraining on their identity.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--possessions", type=Path, default=DEFAULT_POSSESSIONS)
    parser.add_argument("--components", type=Path, default=DEFAULT_COMPONENTS)
    parser.add_argument("--lineups", type=Path, default=DEFAULT_LINEUPS)
    parser.add_argument("--features-output", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--leaderboard-output", type=Path, default=DEFAULT_LEADERBOARD)
    parser.add_argument("--fold-output", type=Path, default=DEFAULT_FOLDS)
    parser.add_argument("--predictions-output", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--model-output", type=Path, default=DEFAULT_MODEL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    possessions = pd.read_csv(args.possessions, low_memory=False)
    components = pd.read_csv(args.components, low_memory=False)
    lineups = pd.read_csv(args.lineups, low_memory=False)
    data = possessions[
        possessions["attacking_style_cluster"].ge(0)
        & possessions["defensive_style_cluster"].ge(0)
        & possessions["period"].le(4)
    ].copy()
    data = data.merge(
        lineups[
            [
                "possession_uid",
                "attacking_player_ids",
                "defending_player_ids",
            ]
        ],
        on="possession_uid",
        how="left",
        validate="one_to_one",
    ).reset_index(drop=True)
    if data[["attacking_player_ids", "defending_player_ids"]].isna().any().any():
        raise RuntimeError("Missing lineup lists after possession merge")

    splitter = StratifiedGroupKFold(
        n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE
    )
    splits = list(
        splitter.split(data, data["shot"].astype(int), groups=data["match_id"])
    )
    player_features, fold_ids = cross_fitted_player_features(
        data, components, splits
    )
    data = pd.concat([data, player_features], axis=1)
    data["validation_fold"] = fold_ids
    player_columns = player_features.columns.tolist()
    layouts = {
        "Tactical + Shape": TACTICAL_NUMERIC_FEATURES,
        "Player-Aware": TACTICAL_NUMERIC_FEATURES + player_columns,
    }

    leaderboard, fold_metrics, predictions = benchmark(data, splits, layouts)
    full_profiles, full_priors = build_profiles(components)
    positions = (
        components.groupby("player_id")["position_group"]
        .agg(mode_or_unknown)
        .to_dict()
    )
    full_player_features = lineup_features(
        data, full_profiles, full_priors, positions
    )
    final_data = data.drop(columns=player_columns).copy()
    final_data = pd.concat([final_data, full_player_features], axis=1)
    selected = fit_selected_models(final_data, leaderboard, layouts)

    for path in [
        args.features_output,
        args.leaderboard_output,
        args.fold_output,
        args.predictions_output,
        args.report_output,
        args.model_output,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    pd.concat(
        [
            data[["possession_uid", "match_id", "validation_fold"]],
            player_features,
        ],
        axis=1,
    ).to_csv(args.features_output, index=False)
    leaderboard.to_csv(args.leaderboard_output, index=False)
    fold_metrics.to_csv(args.fold_output, index=False)
    predictions.to_csv(args.predictions_output, index=False)
    write_report(args.report_output, data, leaderboard, len(player_columns))
    joblib.dump(
        {
            "version": 1,
            "purpose": "Possession outcome model architecture benchmark",
            "selected_models": selected,
            "targets": TARGETS,
            "layouts": layouts,
            "player_skill_schema": {
                "rate_skills": RATE_SKILLS,
                "ratio_skills": RATIO_SKILLS,
                "mean_skills": MEAN_SKILLS,
                "prior_minutes": PRIOR_MINUTES,
                "prior_attempts": PRIOR_ATTEMPTS,
            },
            "identity_features_used": False,
            "validation": f"{N_SPLITS}-fold StratifiedGroupKFold by match",
        },
        args.model_output,
    )
    print(
        leaderboard.groupby("target", sort=False).head(1)[
            ["target", "layout", "model", "log_loss", "brier", "roc_auc", "pr_auc"]
        ].to_string(index=False)
    )
    print(f"Wrote leaderboard to {args.leaderboard_output}")
    print(f"Wrote model bundle to {args.model_output}")
    print(f"Wrote report to {args.report_output}")


if __name__ == "__main__":
    main()
