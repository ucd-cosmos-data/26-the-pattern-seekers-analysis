#!/usr/bin/env python3
"""Build leakage-safe, pre-decision features for attacking-style recommendations."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from benchmark_coaching_models import (
    build_profiles,
    lineup_features,
    mode_or_unknown,
)


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
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_recommendation_features.csv"
)
DEFAULT_REPORT = PROJECT_ROOT / "results" / "recommendation_feature_validation.md"
DEFAULT_STYLE_PROFILES = PROJECT_ROOT / "results" / "attacking_style_profiles.csv"

RANDOM_STATE = 42
N_SPLITS = 5
TRANSITION_SECONDS = 15.0

ATTACK_STYLES = [
    "Patient Build-up",
    "Short Under Pressure",
    "Direct Long Play",
]
DEFENSE_STYLES = [
    "Wide Retreating Block",
    "High-Intensity Press",
    "Set-Piece Compact Shape",
    "Compact Pressure Block",
]
SHAPE_HISTORY_COLUMNS = [
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


def derive_transition_targets(source: pd.DataFrame) -> pd.DataFrame:
    data = source.sort_values(
        ["match_id", "period", "start_time_seconds", "possession"]
    ).copy()
    grouped = data.groupby("match_id", sort=False)
    next_columns = [
        "period",
        "team",
        "start_time_seconds",
        "duration_seconds",
        "entered_final_third",
        "entered_penalty_area",
        "shot",
        "xg_generated",
    ]
    for column in next_columns:
        data[f"next_{column}"] = grouped[column].shift(-1)
    gap = data["next_start_time_seconds"] - data["end_time_seconds"]
    immediate_opponent = (
        data["next_period"].eq(data["period"])
        & data["next_team"].eq(data["opponent"])
        & gap.between(-1, 10)
        & data["next_duration_seconds"].le(TRANSITION_SECONDS)
    )
    data["transition_final_third_15"] = (
        immediate_opponent & data["next_entered_final_third"].eq(1)
    ).astype(int)
    data["transition_box_15"] = (
        immediate_opponent & data["next_entered_penalty_area"].eq(1)
    ).astype(int)
    data["transition_shot_15"] = (
        immediate_opponent & data["next_shot"].eq(1)
    ).astype(int)
    data["transition_xg_15"] = np.where(
        immediate_opponent, data["next_xg_generated"].fillna(0), 0
    )
    data["net_xg_15"] = data["xg_generated"] - data["transition_xg_15"]
    score_records: list[dict[str, object]] = []
    for _, match in data.groupby("match_id", sort=False):
        score: dict[str, int] = {}
        for index, row in match.sort_values(
            ["period", "start_time_seconds", "possession"]
        ).iterrows():
            team_score = score.get(str(row["team"]), 0)
            opponent_score = score.get(str(row["opponent"]), 0)
            difference = team_score - opponent_score
            score_records.append(
                {
                    "index": index,
                    "team_goals_before": team_score,
                    "opponent_goals_before": opponent_score,
                    "score_difference": difference,
                    "score_state": (
                        "Leading"
                        if difference > 0
                        else "Trailing"
                        if difference < 0
                        else "Tied"
                    ),
                }
            )
            score[str(row["team"])] = team_score + int(row["goal_count"])
    scores = pd.DataFrame(score_records).set_index("index")
    data = data.join(scores)
    return data.sort_index()


def global_history_prior(source: pd.DataFrame) -> dict[str, float]:
    prior: dict[str, float] = {
        "team_prior_matches": float(source["match_id"].nunique()),
        "team_prior_possessions": float(len(source)),
        "team_prior_xg_per_possession": float(source["xg_generated"].mean()),
        "team_prior_shot_rate": float(source["shot"].mean()),
        "team_prior_box_rate": float(source["entered_penalty_area"].mean()),
        "team_prior_transition_final_third_conceded": float(
            source["transition_final_third_15"].mean()
        ),
        "team_prior_transition_box_conceded": float(
            source["transition_box_15"].mean()
        ),
        "team_prior_transition_shot_conceded": float(
            source["transition_shot_15"].mean()
        ),
        "team_prior_transition_xg_conceded": float(
            source["transition_xg_15"].mean()
        ),
        "opponent_prior_matches": float(source["match_id"].nunique()),
        "opponent_prior_possessions": float(len(source)),
        "opponent_prior_xg_allowed": float(source["xg_generated"].mean()),
        "opponent_prior_shot_allowed": float(source["shot"].mean()),
        "opponent_prior_box_allowed": float(source["entered_penalty_area"].mean()),
        "opponent_prior_counter_final_third": float(
            source["transition_final_third_15"].mean()
        ),
        "opponent_prior_counter_box": float(source["transition_box_15"].mean()),
        "opponent_prior_counter_shot": float(source["transition_shot_15"].mean()),
        "opponent_prior_counter_xg": float(source["transition_xg_15"].mean()),
    }
    for style in ATTACK_STYLES:
        prior[f"team_attack_share__{style}"] = float(
            source["attacking_style"].eq(style).mean()
        )
    for style in DEFENSE_STYLES:
        prior[f"opponent_defense_share__{style}"] = float(
            source["defensive_style"].eq(style).mean()
        )
    for column in SHAPE_HISTORY_COLUMNS:
        prior[f"opponent_prior_{column}"] = float(source[column].mean())
    return prior


def team_history_features(
    rows: pd.DataFrame,
    history: pd.DataFrame,
    fallback: dict[str, float],
) -> pd.DataFrame:
    records: list[dict[str, float]] = []
    for row in rows.itertuples(index=False):
        attack_history = history[history["team"].eq(row.team)]
        defense_history = history[history["opponent"].eq(row.opponent)]
        record = dict(fallback)
        if not attack_history.empty:
            record.update(
                {
                    "team_prior_matches": float(
                        attack_history["match_id"].nunique()
                    ),
                    "team_prior_possessions": float(len(attack_history)),
                    "team_prior_xg_per_possession": float(
                        attack_history["xg_generated"].mean()
                    ),
                    "team_prior_shot_rate": float(attack_history["shot"].mean()),
                    "team_prior_box_rate": float(
                        attack_history["entered_penalty_area"].mean()
                    ),
                    "team_prior_transition_final_third_conceded": float(
                        attack_history["transition_final_third_15"].mean()
                    ),
                    "team_prior_transition_box_conceded": float(
                        attack_history["transition_box_15"].mean()
                    ),
                    "team_prior_transition_shot_conceded": float(
                        attack_history["transition_shot_15"].mean()
                    ),
                    "team_prior_transition_xg_conceded": float(
                        attack_history["transition_xg_15"].mean()
                    ),
                }
            )
            for style in ATTACK_STYLES:
                record[f"team_attack_share__{style}"] = float(
                    attack_history["attacking_style"].eq(style).mean()
                )
        else:
            record["team_prior_matches"] = 0.0
            record["team_prior_possessions"] = 0.0
        if not defense_history.empty:
            record.update(
                {
                    "opponent_prior_matches": float(
                        defense_history["match_id"].nunique()
                    ),
                    "opponent_prior_possessions": float(len(defense_history)),
                    "opponent_prior_xg_allowed": float(
                        defense_history["xg_generated"].mean()
                    ),
                    "opponent_prior_shot_allowed": float(
                        defense_history["shot"].mean()
                    ),
                    "opponent_prior_box_allowed": float(
                        defense_history["entered_penalty_area"].mean()
                    ),
                    "opponent_prior_counter_final_third": float(
                        defense_history["transition_final_third_15"].mean()
                    ),
                    "opponent_prior_counter_box": float(
                        defense_history["transition_box_15"].mean()
                    ),
                    "opponent_prior_counter_shot": float(
                        defense_history["transition_shot_15"].mean()
                    ),
                    "opponent_prior_counter_xg": float(
                        defense_history["transition_xg_15"].mean()
                    ),
                }
            )
            for style in DEFENSE_STYLES:
                record[f"opponent_defense_share__{style}"] = float(
                    defense_history["defensive_style"].eq(style).mean()
                )
            for column in SHAPE_HISTORY_COLUMNS:
                record[f"opponent_prior_{column}"] = float(
                    defense_history[column].mean()
                )
        else:
            record["opponent_prior_matches"] = 0.0
            record["opponent_prior_possessions"] = 0.0
        records.append(record)
    return pd.DataFrame(records, index=rows.index)


def cross_fitted_predecision_features(
    data: pd.DataFrame,
    components: pd.DataFrame,
    splits: list[tuple[np.ndarray, np.ndarray]],
) -> pd.DataFrame:
    positions = (
        components.groupby("player_id")["position_group"]
        .agg(mode_or_unknown)
        .to_dict()
    )
    fold_frames: list[pd.DataFrame] = []
    dates = pd.to_datetime(data["match_date"])

    for fold, (train_index, test_index) in enumerate(splits):
        train_matches = set(data.iloc[train_index]["match_id"])
        test_matches = set(data.iloc[test_index]["match_id"])
        training_possessions = data[data["match_id"].isin(train_matches)]
        fallback = global_history_prior(training_possessions)
        _, global_player_priors = build_profiles(
            components[components["match_id"].isin(train_matches)]
        )

        current_fold_frames: list[pd.DataFrame] = []
        for match_id in data["match_id"].unique():
            row_index = data.index[data["match_id"].eq(match_id)]
            match_date = dates.loc[row_index].min()
            prior_matches = set(
                data.loc[
                    data["match_id"].isin(train_matches)
                    & dates.lt(match_date),
                    "match_id",
                ]
            )
            historical_possessions = training_possessions[
                training_possessions["match_id"].isin(prior_matches)
            ]
            historical_components = components[
                components["match_id"].isin(prior_matches)
            ]
            if historical_components.empty:
                profiles = pd.DataFrame()
            else:
                profiles, _ = build_profiles(historical_components)
            history_features = team_history_features(
                data.loc[row_index], historical_possessions, fallback
            )
            player_features = lineup_features(
                data.loc[row_index],
                profiles,
                global_player_priors,
                positions,
            )
            combined = pd.concat([history_features, player_features], axis=1)
            combined["source_index"] = row_index
            combined["validation_fold"] = fold
            combined["is_test_fold"] = match_id in test_matches
            current_fold_frames.append(combined)
        fold_frames.append(pd.concat(current_fold_frames, ignore_index=True))

    output = pd.concat(fold_frames, ignore_index=True)
    feature_columns = [
        column
        for column in output
        if column not in {"source_index", "validation_fold", "is_test_fold"}
    ]
    if output[feature_columns].isna().any().any():
        missing = int(output[feature_columns].isna().sum().sum())
        raise RuntimeError(f"Pre-decision feature generation incomplete: {missing}")
    return output


def write_validation(
    path: Path,
    data: pd.DataFrame,
    derived: pd.DataFrame,
    history_columns: list[str],
    player_columns: list[str],
) -> None:
    unique_possessions = data.drop_duplicates("possession_uid")
    model_input_columns = history_columns + player_columns
    # Names such as ``opp_counter_mean_xg_p90`` are legitimate historical
    # player-profile inputs. Check exact current-possession outcomes rather than
    # rejecting safe prior features merely because their names contain "xg".
    forbidden_current_outcomes = {
        "shot",
        "shot_count",
        "goal",
        "goal_count",
        "xg_generated",
        "entered_final_third",
        "entered_penalty_area",
        "transition_final_third_15",
        "transition_box_15",
        "transition_shot_15",
        "transition_xg_15",
        "net_xg_15",
    }
    forbidden = sorted(
        forbidden_current_outcomes.intersection(model_input_columns)
    )
    checks = {
        "Possession IDs are unique within every feature fold": all(
            group["possession_uid"].is_unique
            for _, group in data.groupby("validation_fold")
        ),
        "Every possession appears once in each feature fold": data.groupby(
            "possession_uid"
        ).size().eq(N_SPLITS).all(),
        "All derived inputs are complete": not derived.isna().any().any(),
        "No current-possession outcome column is in model inputs": not forbidden,
        "All 64 matches are represented": data["match_id"].nunique() == 64,
        "Transition box target has at least 200 positives": data[
            "transition_box_15"
        ].sum()
        >= 200,
    }
    lines = [
        "# Recommendation Feature Validation",
        "",
        f"- Eligible possessions: {data['possession_uid'].nunique():,}",
        f"- Fold-specific feature rows: {len(data):,}",
        f"- Matches: {data['match_id'].nunique()}",
        f"- History features: {len(history_columns)}",
        f"- Player and matchup features: {len(player_columns)}",
        f"- Shot outcomes: {int(unique_possessions['shot'].sum()):,}",
        f"- Box-entry outcomes: {int(unique_possessions['entered_penalty_area'].sum()):,}",
        f"- 15-second opponent box transitions: {int(unique_possessions['transition_box_15'].sum()):,}",
        f"- Attacking xG: {unique_possessions['xg_generated'].sum():.3f}",
        f"- 15-second transition xG conceded: {unique_possessions['transition_xg_15'].sum():.3f}",
        "",
        "Team, opponent, and player performance features use only training-fold matches "
        "dated before the match being represented. Exact current-possession defensive "
        "shape is excluded.",
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    lines.extend(
        f"| {name} | {'PASS' if passed else 'FAIL'} |"
        for name, passed in checks.items()
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise RuntimeError(
            "Recommendation feature validation failed: "
            + ", ".join(name for name, passed in checks.items() if not passed)
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--possessions", type=Path, default=DEFAULT_POSSESSIONS)
    parser.add_argument("--components", type=Path, default=DEFAULT_COMPONENTS)
    parser.add_argument("--lineups", type=Path, default=DEFAULT_LINEUPS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--style-profiles", type=Path, default=DEFAULT_STYLE_PROFILES
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    possessions = pd.read_csv(args.possessions, low_memory=False)
    components = pd.read_csv(args.components, low_memory=False)
    lineups = pd.read_csv(args.lineups, low_memory=False)
    style_profiles = pd.read_csv(args.style_profiles)
    data = derive_transition_targets(possessions)
    data = data[
        data["attacking_style_cluster"].ge(0)
        & data["defensive_style_cluster"].ge(0)
        & data["period"].le(4)
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
    splitter = StratifiedGroupKFold(
        n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE
    )
    splits = list(
        splitter.split(data, data["shot"].astype(int), groups=data["match_id"])
    )
    derived = cross_fitted_predecision_features(data, components, splits)
    metadata_columns = {"source_index", "validation_fold", "is_test_fold"}
    history_columns = [
        column
        for column in derived
        if column not in metadata_columns
        and column.startswith(("team_", "opponent_"))
    ]
    player_columns = [
        column
        for column in derived
        if column not in metadata_columns and column not in history_columns
    ]
    output_columns = [
        "possession_uid",
        "match_id",
        "match_date",
        "competition_stage",
        "team",
        "opponent",
        "period",
        "start_minute",
        "first_play_pattern",
        "start_x",
        "start_y",
        "team_goals_before",
        "opponent_goals_before",
        "score_difference",
        "score_state",
        "attacking_style",
        "shot",
        "entered_penalty_area",
        "xg_generated",
        "transition_final_third_15",
        "transition_box_15",
        "transition_shot_15",
        "transition_xg_15",
        "net_xg_15",
    ]
    base_repeated = data.loc[derived["source_index"], output_columns].reset_index(
        drop=True
    )
    model_features = derived.drop(columns=["source_index"]).reset_index(drop=True)
    output = pd.concat([base_repeated, model_features], axis=1)
    fingerprint_columns = [
        column for column in style_profiles if column.startswith("z_")
    ]
    fingerprints = style_profiles.set_index("style_label")[fingerprint_columns]
    for column in fingerprint_columns:
        output[f"candidate_{column}"] = output["attacking_style"].map(
            fingerprints[column]
        )
    candidate_columns = [f"candidate_{column}" for column in fingerprint_columns]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    validation_columns = history_columns + player_columns + candidate_columns
    write_validation(
        args.report,
        output,
        output[validation_columns],
        history_columns + candidate_columns,
        player_columns,
    )
    print(
        f"Wrote {output['possession_uid'].nunique():,} possessions across "
        f"{N_SPLITS} fold-specific feature sets to {args.output}"
    )
    print(f"Wrote validation report to {args.report}")


if __name__ == "__main__":
    main()
