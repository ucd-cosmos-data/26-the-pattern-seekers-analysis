"""Leakage-safe opposition and off-ball context for outfield Impact v4.

The opponent expectation is derived from information available before the
relevant match.  The preferred variants use the frozen 6 October 2022 FIFA
ranking; the cumulative-xG challenger only consumes matches with an earlier
kick-off.  Player and team labels are join keys, never numerical features.

The positional-prevention family uses team defensive-shape summaries from
StatsBomb 360 frames.  Public 360 frames do not identify every non-actor
player, so the team signal is allocated continuously by minutes and by each
player's identity-free 360 shape evidence.  That limitation is explicit in
the release audit rather than being presented as directly observed individual
positioning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold, cross_val_predict


OPPOSITION_VARIANTS = (
    "fifa_log_rank",
    "fifa_inverse_sqrt",
    "cumulative_pre_match_xg",
)

TEAM_SHAPE_360_FEATURES = (
    "avg_defensive_centroid_x",
    "avg_defensive_centroid_y",
    "avg_back_line_height",
    "avg_defensive_hull_area",
    "avg_defensive_width",
    "avg_defensive_depth",
    "avg_defenders_behind_ball",
    "avg_central_defenders",
    "avg_defenders_within_5",
    "avg_defenders_within_10",
    "avg_nearest_defender_distance",
    "avg_mean_defender_distance",
    "avg_defensive_density",
)

PLAYER_SHAPE_360_FEATURES = (
    "defensive_positioning_score",
    "defensive_off_ball_score",
)


@dataclass(frozen=True)
class ContextBuildResult:
    """One-row-per-defending-team-match context and its audit."""

    frame: pd.DataFrame
    audit: dict[str, Any]


@dataclass(frozen=True)
class PreventionBuildResult:
    """OOF team-shape prevention estimates and validation audit."""

    frame: pd.DataFrame
    audit: dict[str, Any]


def _schedule(matches: pd.DataFrame) -> pd.DataFrame:
    required = {
        "match_id",
        "match_date",
        "kick_off",
        "home_team",
        "away_team",
    }
    missing = required.difference(matches.columns)
    if missing:
        raise ValueError(f"matches are missing fields: {sorted(missing)}")
    match_time = pd.to_datetime(
        matches["match_date"].astype(str)
        + " "
        + matches["kick_off"].astype(str),
        errors="raise",
    )
    rows: list[dict[str, Any]] = []
    for match_id, kickoff, home, away in zip(
        matches["match_id"],
        match_time,
        matches["home_team"],
        matches["away_team"],
        strict=True,
    ):
        rows.extend(
            (
                {
                    "match_id": int(match_id),
                    "match_datetime": kickoff,
                    "team": str(home),
                    "opponent": str(away),
                },
                {
                    "match_id": int(match_id),
                    "match_datetime": kickoff,
                    "team": str(away),
                    "opponent": str(home),
                },
            )
        )
    return pd.DataFrame(rows)


def _attacking_match_outcomes(possessions: pd.DataFrame) -> pd.DataFrame:
    required = {
        "match_id",
        "team",
        "possession_uid",
        "xg_generated",
        "entered_final_third",
        "entered_penalty_area",
    }
    missing = required.difference(possessions.columns)
    if missing:
        raise ValueError(
            f"possession context is missing fields: {sorted(missing)}"
        )
    output = (
        possessions.groupby(["match_id", "team"], as_index=False)
        .agg(
            attacking_possessions=("possession_uid", "nunique"),
            xg_generated=("xg_generated", "sum"),
            final_third_entries=("entered_final_third", "sum"),
            penalty_area_entries=("entered_penalty_area", "sum"),
        )
        .sort_values(["match_id", "team"], kind="mergesort")
        .reset_index(drop=True)
    )
    if "end_minute" in possessions:
        durations = (
            possessions.groupby(["match_id", "team"], as_index=False)
            .agg(match_minutes=("end_minute", "max"))
        )
        output = output.merge(
            durations,
            on=["match_id", "team"],
            how="left",
            validate="one_to_one",
        )
        output["match_minutes"] = (
            pd.to_numeric(output["match_minutes"], errors="coerce")
            .fillna(90.0)
            .clip(lower=90.0)
        )
    else:
        # Synthetic fixtures and older extracts do not carry timestamps.
        output["match_minutes"] = 90.0
    return output


def _fifa_strength(
    schedule: pd.DataFrame,
    fifa_rankings: pd.DataFrame,
    *,
    variant: str,
) -> tuple[pd.Series, dict[str, Any]]:
    required = {"team", "fifa_rank", "ranking_date", "source"}
    missing = required.difference(fifa_rankings.columns)
    if missing:
        raise ValueError(
            f"FIFA ranking input is missing fields: {sorted(missing)}"
        )
    ranks = fifa_rankings.copy()
    ranks["ranking_date"] = pd.to_datetime(
        ranks["ranking_date"], errors="raise"
    )
    if ranks["team"].duplicated().any():
        raise ValueError("FIFA ranking input requires one row per team")
    merged = schedule[["opponent", "match_datetime"]].merge(
        ranks.rename(columns={"team": "opponent"}),
        on="opponent",
        how="left",
        validate="many_to_one",
    )
    if merged["fifa_rank"].isna().any():
        missing_teams = sorted(
            merged.loc[merged["fifa_rank"].isna(), "opponent"].unique()
        )
        raise ValueError(f"FIFA ranks are missing opponents: {missing_teams}")
    if not (merged["ranking_date"] < merged["match_datetime"]).all():
        raise ValueError("FIFA context must predate every tournament match")
    rank = pd.to_numeric(merged["fifa_rank"], errors="raise").astype(float)
    tournament_median = float(
        pd.to_numeric(ranks["fifa_rank"], errors="raise").median()
    )
    if variant == "fifa_log_rank":
        transformed = -np.log(rank)
        standardized = (transformed - transformed.mean()) / transformed.std(
            ddof=0
        )
        strength = (1.0 + 0.25 * standardized).clip(0.40, 1.60)
    elif variant == "fifa_inverse_sqrt":
        strength = np.sqrt(tournament_median / rank)
    else:
        raise ValueError(f"unsupported FIFA opposition variant: {variant}")
    strength = strength / float(strength.mean())
    audit = {
        "variant": variant,
        "source": str(ranks["source"].iloc[0]),
        "ranking_date": ranks["ranking_date"].max().date().isoformat(),
        "strictly_predates_all_matches": True,
        "post_event_fields_used": [],
    }
    return pd.Series(strength, index=schedule.index, dtype=float), audit


def _cumulative_pre_match_strength(
    schedule: pd.DataFrame,
    attack: pd.DataFrame,
    *,
    prior_matches: float = 1.0,
) -> tuple[pd.Series, dict[str, Any]]:
    if prior_matches <= 0:
        raise ValueError("prior_matches must be positive")
    attacking = schedule.rename(
        columns={"team": "attacking_team"}
    ).merge(
        attack.rename(columns={"team": "attacking_team"}),
        on=["match_id", "attacking_team"],
        how="left",
        validate="one_to_one",
    )
    # Fixed pre-tournament neutral prior.  A tournament-final mean would let
    # current/future outcomes change an earlier match's context.
    neutral = 1.0
    attacking = attacking.sort_values(
        ["attacking_team", "match_datetime", "match_id"],
        kind="mergesort",
    )
    attacking["prior_match_count"] = attacking.groupby(
        "attacking_team", sort=False
    ).cumcount()
    attacking["cumulative_prior_xg"] = (
        attacking.groupby("attacking_team", sort=False)["xg_generated"]
        .cumsum()
        .sub(attacking["xg_generated"])
    )
    attacking["cumulative_prior_match_equivalents"] = (
        attacking.groupby("attacking_team", sort=False)["match_minutes"]
        .cumsum()
        .sub(attacking["match_minutes"])
        .div(90.0)
    )
    attacking["strength"] = (
        attacking["cumulative_prior_xg"] + prior_matches * neutral
    ) / (
        attacking["cumulative_prior_match_equivalents"] + prior_matches
    ) / neutral
    lookup = attacking[
        ["match_id", "attacking_team", "match_datetime", "strength"]
    ].rename(columns={"attacking_team": "opponent"})
    output = schedule.merge(
        lookup,
        on=["match_id", "opponent", "match_datetime"],
        how="left",
        validate="one_to_one",
    )
    if output["strength"].isna().any():
        raise ValueError("cumulative pre-match strength could not be joined")
    # The expanding features above exclude the current row by construction.
    audit = {
        "variant": "cumulative_pre_match_xg",
        "source": "strictly earlier Qatar 2022 matches",
        "prior_matches": prior_matches,
        "chronology_guard": (
            "cumulative xG and match-minutes minus current row"
        ),
        "strictly_prior_match_only": True,
        "post_event_fields_used": [],
    }
    return output["strength"].astype(float), audit


def build_opponent_context(
    matches: pd.DataFrame,
    possessions: pd.DataFrame,
    fifa_rankings: pd.DataFrame,
    *,
    variant: str,
) -> ContextBuildResult:
    """Build expected opponent exposure without player/team-name features."""

    if variant not in OPPOSITION_VARIANTS:
        raise ValueError(
            f"opposition variant must be one of {OPPOSITION_VARIANTS}"
        )
    schedule = _schedule(matches)
    attack = _attacking_match_outcomes(possessions)
    opponent_outcomes = attack.rename(
        columns={
            "team": "opponent",
            "attacking_possessions": "opponent_possessions_context_v4",
            "xg_generated": "opponent_xg_observed_v4",
            "final_third_entries": "opponent_final_third_entries_v4",
            "penalty_area_entries": "opponent_penalty_area_entries_v4",
        }
    )
    context = schedule.merge(
        opponent_outcomes,
        on=["match_id", "opponent"],
        how="left",
        validate="one_to_one",
    )
    if context[
        [
            "opponent_possessions_context_v4",
            "opponent_xg_observed_v4",
            "opponent_penalty_area_entries_v4",
        ]
    ].isna().any().any():
        raise ValueError("opponent outcomes are incomplete")
    if variant.startswith("fifa_"):
        strength, source_audit = _fifa_strength(
            schedule, fifa_rankings, variant=variant
        )
    else:
        strength, source_audit = _cumulative_pre_match_strength(
            schedule, attack
        )
    context["opponent_attack_strength_match_v4"] = strength.to_numpy()
    context["opponent_expected_exposure_v4"] = (
        context["opponent_attack_strength_match_v4"]
        * context["opponent_possessions_context_v4"]
        / 100.0
    )
    context["opponent_xg_rate_per100_v4"] = (
        context["opponent_xg_observed_v4"]
        / context["opponent_possessions_context_v4"]
        * 100.0
    )
    context["opponent_penalty_area_entry_rate_v4"] = (
        context["opponent_penalty_area_entries_v4"]
        / context["opponent_possessions_context_v4"]
    )
    audit = {
        "source": source_audit,
        "rows": int(len(context)),
        "matches": int(context["match_id"].nunique()),
        "teams": int(context["team"].nunique()),
        "identity_fields_used_as_numeric_features": False,
        "opponent_labels_used_only_as_schedule_join_keys": True,
        "strength_min": float(
            context["opponent_attack_strength_match_v4"].min()
        ),
        "strength_max": float(
            context["opponent_attack_strength_match_v4"].max()
        ),
    }
    return ContextBuildResult(context, audit)


def _numeric_design(frame: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    design = frame.loc[:, list(columns)].apply(
        pd.to_numeric, errors="coerce"
    )
    medians = design.median()
    design = design.fillna(medians)
    scales = design.std(ddof=0).replace(0.0, 1.0)
    return (design - design.mean()) / scales


def build_off_ball_prevention_oof(
    possessions: pd.DataFrame,
    context: pd.DataFrame,
    *,
    ridge_alpha: float = 10.0,
    n_splits: int = 8,
) -> PreventionBuildResult:
    """Validate and estimate 360-frame positional prevention out of fold."""

    if ridge_alpha <= 0:
        raise ValueError("ridge_alpha must be positive")
    team_shape = (
        possessions.groupby(["match_id", "defending_team"], as_index=False)[
            list(TEAM_SHAPE_360_FEATURES)
        ]
        .mean()
        .rename(columns={"defending_team": "team"})
    )
    target_frame = context[
        [
            "match_id",
            "team",
            "opponent_attack_strength_match_v4",
            "opponent_penalty_area_entry_rate_v4",
        ]
    ].copy()
    strength_design = target_frame[
        ["opponent_attack_strength_match_v4"]
    ]
    groups = target_frame["match_id"]
    folds = min(n_splits, int(groups.nunique()))
    if folds < 2:
        raise ValueError("off-ball OOF validation needs at least two matches")
    expected_entry_rate = cross_val_predict(
        Ridge(alpha=2.0),
        strength_design,
        target_frame["opponent_penalty_area_entry_rate_v4"],
        groups=groups,
        cv=GroupKFold(folds),
    )
    target_frame["entry_denial_target_per100_v4"] = (
        expected_entry_rate
        - target_frame["opponent_penalty_area_entry_rate_v4"]
    ) * 100.0
    validation = target_frame.merge(
        team_shape,
        on=["match_id", "team"],
        how="left",
        validate="one_to_one",
    )
    design = _numeric_design(validation, TEAM_SHAPE_360_FEATURES)
    predicted = cross_val_predict(
        Ridge(alpha=ridge_alpha),
        design,
        validation["entry_denial_target_per100_v4"],
        groups=validation["match_id"],
        cv=GroupKFold(folds),
    )
    validation["entry_denial_oof_prediction_v4"] = predicted
    target = validation["entry_denial_target_per100_v4"].to_numpy(
        dtype=float
    )
    null = np.full_like(target, target.mean())
    rmse = float(np.sqrt(mean_squared_error(target, predicted)))
    null_rmse = float(np.sqrt(mean_squared_error(target, null)))
    spearman = float(spearmanr(target, predicted).statistic)
    gate_passed = bool(
        np.isfinite(spearman)
        and spearman > 0.0
        and rmse < null_rmse
    )
    audit = {
        "feature_family": "possession-adjusted-entry-denial-360-v1",
        "features": list(TEAM_SHAPE_360_FEATURES),
        "requires_recorded_player_defensive_events": False,
        "oof_group": "match_id",
        "match_disjoint": True,
        "folds": folds,
        "ridge_alpha": ridge_alpha,
        "rows": int(len(validation)),
        "oof_rmse": rmse,
        "null_rmse": null_rmse,
        "oof_spearman": spearman,
        "gate_passed": gate_passed,
        "individual_attribution": (
            "team 360 prevention allocated continuously by minutes and "
            "identity-free player shape evidence"
        ),
        "limitation": (
            "public 360 frames do not identify every non-actor outfielder; "
            "the player allocation is modeled, not direct tracking attribution"
        ),
    }
    if not gate_passed:
        raise RuntimeError("off-ball prevention failed its preregistered OOF gate")
    keep = [
        "match_id",
        "team",
        "entry_denial_target_per100_v4",
        "entry_denial_oof_prediction_v4",
        *TEAM_SHAPE_360_FEATURES,
    ]
    return PreventionBuildResult(validation[keep].copy(), audit)


def allocate_match_context_to_players(
    predictions: pd.DataFrame,
    samples: pd.DataFrame,
    players: pd.DataFrame,
    context: pd.DataFrame,
    prevention: pd.DataFrame,
) -> pd.DataFrame:
    """Create identity-free player-match v4 defense stage inputs."""

    required_prediction = {
        "match_id",
        "team",
        "player_id",
        "minutes",
        "signed_ridge_oof_prediction",
    }
    required_samples = {
        "match_id",
        "team",
        "player_id",
        "opponent_possessions",
        "positioning_360_coverage",
    }
    for label, frame, required in (
        ("predictions", predictions, required_prediction),
        ("samples", samples, required_samples),
        ("players", players, {"player_id", *PLAYER_SHAPE_360_FEATURES}),
    ):
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"{label} are missing fields: {sorted(missing)}")
    frame = predictions[list(required_prediction)].merge(
        samples[list(required_samples)],
        on=["match_id", "team", "player_id"],
        how="left",
        validate="one_to_one",
    )
    frame = frame.merge(
        context[
            [
                "match_id",
                "team",
                "opponent",
                "opponent_attack_strength_match_v4",
                "opponent_expected_exposure_v4",
            ]
        ],
        on=["match_id", "team"],
        how="left",
        validate="many_to_one",
    ).merge(
        prevention[
            [
                "match_id",
                "team",
                "entry_denial_target_per100_v4",
                "entry_denial_oof_prediction_v4",
            ]
        ],
        on=["match_id", "team"],
        how="left",
        validate="many_to_one",
    ).merge(
        players[["player_id", *PLAYER_SHAPE_360_FEATURES]],
        on="player_id",
        how="left",
        validate="many_to_one",
    )
    numeric_required = [
        "signed_ridge_oof_prediction",
        "opponent_possessions",
        "opponent_attack_strength_match_v4",
        "entry_denial_oof_prediction_v4",
    ]
    if frame[numeric_required].isna().any().any():
        raise ValueError("player-match context contains missing required evidence")
    frame["off_ball_player_shape_available_v4"] = frame[
        list(PLAYER_SHAPE_360_FEATURES)
    ].notna().all(axis=1)
    # Missing 360 evidence is explicitly neutral, never interpreted as zero
    # prevention. Availability is published alongside the imputation.
    for column in PLAYER_SHAPE_360_FEATURES:
        frame[column] = pd.to_numeric(
            frame[column], errors="coerce"
        ).fillna(0.5)
    frame["match_minutes_v4"] = frame.groupby(
        ["match_id", "team"], sort=False
    )["minutes"].transform("max")
    time_share = (
        pd.to_numeric(frame["minutes"], errors="raise")
        / frame["match_minutes_v4"]
    ).clip(0.0, 1.0)
    frame["defensive_value_raw_v4"] = (
        frame["signed_ridge_oof_prediction"]
        * frame["opponent_possessions"]
        / 100.0
    )
    frame["opponent_expected_exposure_player_v4"] = (
        frame["opponent_attack_strength_match_v4"]
        * frame["opponent_possessions"]
        / 100.0
        * time_share
    )
    individual_shape = (
        0.65 * frame["defensive_positioning_score"]
        + 0.35 * frame["defensive_off_ball_score"]
        - 0.5
    ) * 2.0
    team_prediction = frame["entry_denial_oof_prediction_v4"]
    team_scale = float(
        prevention["entry_denial_oof_prediction_v4"].std(ddof=0)
    )
    if not np.isfinite(team_scale) or team_scale <= 0:
        raise ValueError("OOF prevention predictions have zero variance")
    responsibility = 0.75 + 0.25 * ((individual_shape + 1.0) / 2.0)
    team_prevention = (
        team_prediction / team_scale * time_share * responsibility
    )
    individual_prevention = (
        individual_shape
        * pd.to_numeric(frame["minutes"], errors="raise")
        / 90.0
    )
    # The match-disjoint team prediction and the identity-free player shape
    # allocation receive equal fixed weight.  Giving the static player proxy
    # majority weight would let an unobserved non-actor attribution dominate
    # the family that actually cleared the OOF gate.
    frame["off_ball_prevention_raw_v4"] = (
        0.50 * team_prevention + 0.50 * individual_prevention
    )
    frame["off_ball_prevention_coverage_v4"] = pd.to_numeric(
        frame["positioning_360_coverage"], errors="coerce"
    ).clip(0.0, 1.0)
    return frame.sort_values(
        ["match_id", "team", "player_id"], kind="mergesort"
    ).reset_index(drop=True)
