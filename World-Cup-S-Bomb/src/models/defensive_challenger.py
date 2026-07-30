"""Leakage-safe Qatar 2022 defensive-target and challenger evaluation.

The incumbent defensive head predicts a whitelist-derived defensive VAEP
channel.  This module defines an alternative target directly from the change
in the acting team's probability of conceding between the pre-action state
and the next observable state.  Event labels are therefore explanatory
features only; they never determine which action receives a target.

All learned preprocessing is fitted inside match-disjoint folds.  Player and
team identities are retained solely as grouping and audit metadata and are
explicitly prohibited from the model matrix.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.features.event_scope import (
    EVENT_SCOPE_VERSION,
    filter_ordinary_actions,
    filter_ordinary_events,
)


RANDOM_STATE = 42
TARGET_COLUMN = "threat_prevention_target"
CHAMPION_REFERENCE_CORRELATION = 0.34708091345861314

IDENTITY_COLUMNS = frozenset(
    {
        "player",
        "player_name",
        "player_id",
        "team",
        "team_id",
        "opponent",
        "opponent_team",
        "match_id",
        "game_id",
    }
)

FORBIDDEN_DEFENSIVE_PREDICTOR_FRAGMENTS = (
    "goal",
    "shot",
    "key_pass",
    "assist",
    "xg",
    "xa",
)

DEFENSIVE_FEATURE_GROUPS: dict[str, tuple[str, ...]] = {
    "pressures": (
        "pressures_per100_opponent_possessions",
        "pressure_recovery_rate",
        "pressure_threat_exposure_per100",
    ),
    "interceptions": (
        "interceptions_blocks_per100_opponent_possessions",
        "interception_block_retention_rate",
        "interception_block_threat_exposure_per100",
    ),
    "clearances": (
        "clearances_per100_opponent_possessions",
        "clearance_retention_rate",
        "clearance_threat_exposure_per100",
    ),
    "aerials": (
        "aerial_contests_per100_opponent_possessions",
        "aerial_success_rate",
        "aerial_threat_per_eligible_contest",
    ),
    "positioning": (
        "defensive_actions_per100_opponent_possessions",
        "defensive_actions_per100_opponent_final_third_possessions",
        "high_threat_action_share",
        "mean_pre_action_threat",
        "mean_defensive_start_x",
        "central_danger_action_share",
        "positioning_360_coverage",
        "mean_defensive_density_360",
        "mean_defenders_behind_ball_360",
    ),
    "errors": (
        "errors_penalties_per100_opponent_possessions",
        "fouls_per100_opponent_possessions",
        "failed_defensive_action_rate",
    ),
    "progression": (
        "defensive_progression_per100_opponent_possessions",
        "progression_retention_rate",
    ),
}

DEFENSIVE_FEATURES = tuple(
    feature
    for group in DEFENSIVE_FEATURE_GROUPS.values()
    for feature in group
)


@dataclass(frozen=True)
class RegressionMetrics:
    """Out-of-fold regression metrics on the threat-prevention target."""

    rmse: float
    mae: float
    spearman: float
    rows: int
    groups: int


@dataclass
class CandidateEvaluation:
    """Complete match-disjoint diagnostics for one model architecture."""

    name: str
    metrics: RegressionMetrics
    oof_prediction: np.ndarray
    best_parameters: dict[str, Any]
    fold_audit: list[dict[str, Any]]
    coefficient_stability: dict[str, dict[str, float | None]]
    permutation_importance: dict[str, dict[str, float]]


@dataclass
class DefensiveChallengerEvaluation:
    """Serializable comparison and promotion decision."""

    diagnostics: dict[str, Any]
    oof_predictions: pd.DataFrame


class _CalibratedRegressor:
    """Small wrapper around a fitted regressor and isotonic calibrator."""

    def __init__(
        self,
        estimator: Pipeline,
        calibrator: IsotonicRegression,
    ) -> None:
        self.estimator = estimator
        self.calibrator = calibrator

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        raw = self.estimator.predict(features)
        return np.asarray(self.calibrator.predict(raw), dtype=float)


def _truthy(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return (
        series.fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "1", "yes"})
    )


def _safe_divide(
    numerator: pd.Series,
    denominator: pd.Series,
) -> pd.Series:
    return pd.to_numeric(numerator, errors="coerce") / pd.to_numeric(
        denominator, errors="coerce"
    ).replace(0.0, np.nan)


def _spearman(truth: Sequence[float], prediction: Sequence[float]) -> float:
    left = np.asarray(truth, dtype=float)
    right = np.asarray(prediction, dtype=float)
    valid = np.isfinite(left) & np.isfinite(right)
    if valid.sum() < 3:
        return 0.0
    if np.nanstd(left[valid]) <= 1e-15 or np.nanstd(right[valid]) <= 1e-15:
        return 0.0
    value = spearmanr(left[valid], right[valid]).statistic
    return 0.0 if not np.isfinite(value) else float(value)


def _metrics(
    truth: Sequence[float],
    prediction: Sequence[float],
    groups: Sequence[Any],
) -> RegressionMetrics:
    target = np.asarray(truth, dtype=float)
    estimate = np.asarray(prediction, dtype=float)
    valid = np.isfinite(target) & np.isfinite(estimate)
    if not valid.any():
        raise ValueError("No finite defensive predictions")
    return RegressionMetrics(
        rmse=float(np.sqrt(mean_squared_error(target[valid], estimate[valid]))),
        mae=float(mean_absolute_error(target[valid], estimate[valid])),
        spearman=_spearman(target[valid], estimate[valid]),
        rows=int(valid.sum()),
        groups=int(len(np.unique(np.asarray(groups)[valid]))),
    )


def _assert_feature_contract(feature_names: Sequence[str]) -> None:
    names = tuple(feature_names)
    identity = IDENTITY_COLUMNS.intersection(names)
    if identity:
        raise ValueError(
            "Identity fields may not enter defensive features: "
            f"{sorted(identity)}"
        )
    prohibited = sorted(
        name
        for name in names
        if any(
            fragment in name.lower()
            for fragment in FORBIDDEN_DEFENSIVE_PREDICTOR_FRAGMENTS
        )
    )
    if prohibited:
        raise ValueError(
            "Spurious attacking/identity defensive predictors: "
            f"{prohibited}"
        )


def _event_context(events: pd.DataFrame) -> pd.DataFrame:
    """Return one ordinary-period context row per original StatsBomb event."""

    ordinary = filter_ordinary_events(events)
    required = {"id", "match_id", "possession", "possession_team"}
    missing = required.difference(ordinary.columns)
    if missing:
        raise ValueError(f"Defensive event context missing: {sorted(missing)}")
    optional = (
        "duel_type",
        "duel_outcome",
        "clearance_aerial_won",
        "pass_aerial_won",
        "miscontrol_aerial_won",
        "shot_aerial_won",
        "foul_committed_penalty",
        "interception_outcome",
        "ball_recovery_recovery_failure",
    )
    columns = ["id", "match_id", "possession", "possession_team"]
    columns.extend(column for column in optional if column in ordinary)
    context = ordinary[columns].drop_duplicates("id").rename(
        columns={"id": "original_event_id", "match_id": "_context_game_id"}
    )
    context["original_event_id"] = context["original_event_id"].astype(str)
    return context


def attach_defensive_event_context(
    actions: pd.DataFrame,
    events: pd.DataFrame,
) -> pd.DataFrame:
    """Attach possession and aerial/error context to ordinary SPADL actions."""

    ordinary = filter_ordinary_actions(actions)
    if "original_event_id" not in ordinary:
        raise ValueError("Actions require original_event_id for event context")
    ordinary = ordinary.copy()
    ordinary["original_event_id"] = ordinary["original_event_id"].astype(str)
    context = _event_context(events)
    overlapping = [
        column
        for column in context.columns
        if column in ordinary.columns
        and column not in {"original_event_id", "_context_game_id"}
    ]
    if overlapping:
        ordinary = ordinary.drop(columns=overlapping)
    joined = ordinary.merge(
        context,
        on="original_event_id",
        how="left",
        validate="many_to_one",
    )
    mismatched = (
        pd.to_numeric(joined["game_id"], errors="coerce")
        != pd.to_numeric(joined["_context_game_id"], errors="coerce")
    ) & joined["_context_game_id"].notna()
    if mismatched.any():
        raise RuntimeError("StatsBomb context joined to the wrong match")
    joined = joined.drop(columns="_context_game_id")
    coverage = float(joined["possession"].notna().mean())
    if coverage < 0.99:
        raise RuntimeError(
            f"Defensive possession-context coverage below 99%: {coverage:.2%}"
        )
    return joined


def build_defensive_action_targets(actions: pd.DataFrame) -> pd.DataFrame:
    """Orient the next state and derive action-level threat prevention.

    For an action by team T, the next state's probability that T concedes is
    ``p_concedes`` when T acts again and ``p_scores`` when the opponent acts.
    The target is pre-action conceding probability minus that oriented
    next-state probability.  No action-type filter enters this definition.
    """

    working = filter_ordinary_actions(actions)
    required = {
        "game_id",
        "action_id",
        "team",
        "player_id",
        "p_scores",
        "p_concedes",
        "possession",
        "possession_team",
    }
    missing = required.difference(working.columns)
    if missing:
        raise ValueError(f"Defensive target inputs missing: {sorted(missing)}")
    working = working.sort_values(
        ["game_id", "action_id"], kind="mergesort"
    ).reset_index(drop=True)
    grouped = working.groupby("game_id", sort=False)
    next_team = grouped["team"].shift(-1)
    period_column = (
        "period_id" if "period_id" in working else "period"
    )
    current_period = pd.to_numeric(
        working[period_column], errors="coerce"
    )
    next_period = pd.to_numeric(
        grouped[period_column].shift(-1), errors="coerce"
    )
    same_period_next_state = next_period.eq(current_period)
    next_p_scores = pd.to_numeric(
        grouped["p_scores"].shift(-1), errors="coerce"
    )
    next_p_concedes = pd.to_numeric(
        grouped["p_concedes"].shift(-1), errors="coerce"
    )
    working["pre_action_conceding_probability"] = pd.to_numeric(
        working["p_concedes"], errors="coerce"
    ).clip(0.0, 1.0)
    working["post_action_conceding_probability"] = np.where(
        next_team.eq(working["team"]),
        next_p_concedes,
        next_p_scores,
    )
    working["post_action_conceding_probability"] = pd.to_numeric(
        working["post_action_conceding_probability"], errors="coerce"
    ).clip(0.0, 1.0).where(same_period_next_state)
    working["threat_prevention_delta"] = (
        working["pre_action_conceding_probability"]
        - working["post_action_conceding_probability"]
    )
    working["is_defensive_opportunity"] = (
        working["possession_team"].notna()
        & working["team"].notna()
        & working["team"].astype(str).ne(
            working["possession_team"].astype(str)
        )
    )
    recovered = pd.Series(False, index=working.index)
    for offset in (1, 2, 3):
        future_possession_team = grouped["possession_team"].shift(-offset)
        future_period = pd.to_numeric(
            grouped[period_column].shift(-offset), errors="coerce"
        )
        recovered |= (
            future_period.eq(current_period)
            & future_possession_team.astype(str).eq(
                working["team"].astype(str)
            )
        )
    working["possession_recovered_within_three_actions"] = recovered
    working["defensive_target_scope"] = (
        "all opponent-possession actor actions; "
        "pre p(concede) - team-oriented next-state p(concede)"
    )
    working["event_scope_version"] = EVENT_SCOPE_VERSION
    return working


def _possession_denominators(
    actions: pd.DataFrame,
) -> pd.DataFrame:
    """Count opponent possessions and final-third possessions per match/team."""

    possession_rows = actions.loc[
        actions["possession"].notna()
        & actions["possession_team"].notna()
    ].copy()
    if possession_rows.empty:
        raise ValueError("No possession context for defensive denominators")
    possession_rows["possession_key"] = (
        possession_rows["game_id"].astype(str)
        + ":"
        + possession_rows["possession"].astype(str)
    )
    on_ball = possession_rows["team"].astype(str).eq(
        possession_rows["possession_team"].astype(str)
    )
    start_x = pd.to_numeric(
        possession_rows.get("start_x"), errors="coerce"
    )
    possession_rows["_final_third"] = on_ball & start_x.ge(80.0)
    possessions = (
        possession_rows.groupby(
            ["game_id", "possession_key", "possession_team"],
            as_index=False,
        )
        .agg(opponent_final_third_possession=("_final_third", "max"))
    )
    match_teams = (
        actions.loc[actions["team"].notna(), ["game_id", "team"]]
        .drop_duplicates()
    )
    joined = match_teams.merge(
        possessions,
        on="game_id",
        how="left",
        validate="many_to_many",
    )
    opponent = joined["team"].astype(str).ne(
        joined["possession_team"].astype(str)
    )
    joined = joined.loc[opponent]
    return (
        joined.groupby(["game_id", "team"], as_index=False)
        .agg(
            opponent_possessions=("possession_key", "nunique"),
            opponent_final_third_possessions=(
                "opponent_final_third_possession",
                "sum",
            ),
        )
    )


def _feature_indicators(actions: pd.DataFrame) -> pd.DataFrame:
    """Materialize generalized defensive evidence before aggregation."""

    working = actions.copy()
    event_type = working["type_name"].fillna("").astype(str)
    result = working.get(
        "result_name", pd.Series("", index=working.index)
    ).fillna("").astype(str)
    pre_threat = working["pre_action_conceding_probability"]
    recovered = working["possession_recovered_within_three_actions"].astype(
        bool
    )

    working["_pressure"] = event_type.eq("Pressure")
    working["_interception_block"] = event_type.isin(
        {"Interception", "Block", "Ball Recovery"}
    )
    working["_clearance"] = event_type.eq("Clearance")
    duel_type = working.get(
        "duel_type", pd.Series("", index=working.index)
    ).fillna("").astype(str)
    aerial_metadata = pd.Series(False, index=working.index)
    for column in (
        "clearance_aerial_won",
        "pass_aerial_won",
        "miscontrol_aerial_won",
        "shot_aerial_won",
    ):
        if column in working:
            aerial_metadata |= working[column].notna()
    bodypart = working.get(
        "bodypart_name", pd.Series("", index=working.index)
    ).fillna("").astype(str)
    working["_aerial"] = (
        duel_type.str.contains("Aerial", case=False, na=False)
        | aerial_metadata
        | (
            event_type.isin({"Duel", "50/50", "Clearance"})
            & bodypart.str.contains("Head", case=False, na=False)
        )
    )
    duel_outcome = working.get(
        "duel_outcome", pd.Series("", index=working.index)
    ).fillna("").astype(str)
    aerial_won = pd.Series(False, index=working.index)
    for column in (
        "clearance_aerial_won",
        "pass_aerial_won",
        "miscontrol_aerial_won",
        "shot_aerial_won",
    ):
        if column in working:
            aerial_won |= _truthy(working[column])
    working["_aerial_success"] = working["_aerial"] & (
        result.eq("success")
        | aerial_won
        | duel_outcome.str.contains(
            "Won|Success|Complete", case=False, regex=True, na=False
        )
    )
    penalty = (
        _truthy(working["foul_committed_penalty"])
        if "foul_committed_penalty" in working
        else pd.Series(False, index=working.index)
    )
    working["_error_penalty"] = event_type.eq("Error") | penalty
    working["_foul"] = event_type.eq("Foul Committed")
    working["_failed"] = result.str.lower().eq("fail")
    progression = (
        pd.to_numeric(working.get("end_x"), errors="coerce")
        - pd.to_numeric(working.get("start_x"), errors="coerce")
    ).clip(lower=0.0)
    working["_progression"] = progression.fillna(0.0)
    working["_progressive_action"] = progression.ge(10.0)
    working["_retained"] = recovered
    working["_high_threat"] = pre_threat.ge(0.01)
    start_x = pd.to_numeric(working.get("start_x"), errors="coerce")
    start_y = pd.to_numeric(working.get("start_y"), errors="coerce")
    working["_central_danger"] = start_x.le(40.0) & start_y.between(
        24.0, 56.0
    )
    working["_pre_threat_pressure"] = pre_threat.where(
        working["_pressure"], 0.0
    )
    working["_pre_threat_interception_block"] = pre_threat.where(
        working["_interception_block"], 0.0
    )
    working["_pre_threat_clearance"] = pre_threat.where(
        working["_clearance"], 0.0
    )
    working["_pre_threat_aerial"] = pre_threat.where(
        working["_aerial"], np.nan
    )
    working["_pressure_recovered"] = working["_pressure"] & recovered
    working["_interception_block_retained"] = (
        working["_interception_block"] & recovered
    )
    working["_clearance_retained"] = working["_clearance"] & recovered
    working["_progression_retained"] = (
        working["_progressive_action"] & recovered
    )
    has_360 = pd.to_numeric(
        working.get(
            "role_has_360",
            pd.Series(np.nan, index=working.index),
        ),
        errors="coerce",
    )
    working["_has_360"] = has_360.where(has_360.notna(), 0.0)
    working["_density_360"] = pd.to_numeric(
        working.get(
            "role_defensive_density",
            pd.Series(np.nan, index=working.index),
        ),
        errors="coerce",
    ).where(has_360.eq(1.0))
    working["_behind_ball_360"] = pd.to_numeric(
        working.get(
            "role_defenders_behind_ball",
            pd.Series(np.nan, index=working.index),
        ),
        errors="coerce",
    ).where(has_360.eq(1.0))
    return working


def build_player_match_defensive_samples(
    actions: pd.DataFrame,
    *,
    events: pd.DataFrame | None = None,
    player_context: pd.DataFrame | None = None,
    minimum_minutes: float = 20.0,
) -> pd.DataFrame:
    """Build opportunity-adjusted player-match defensive samples."""

    enriched = (
        attach_defensive_event_context(actions, events)
        if events is not None
        else filter_ordinary_actions(actions)
    )
    missing_context = {"possession", "possession_team"}.difference(
        enriched.columns
    )
    if missing_context:
        raise ValueError(
            "Defensive sample construction requires event possession context: "
            f"{sorted(missing_context)}"
        )
    targeted = build_defensive_action_targets(enriched)
    denominators = _possession_denominators(targeted)
    defensive = targeted.loc[
        targeted["is_defensive_opportunity"]
        & targeted["player_id"].notna()
        & targeted["threat_prevention_delta"].notna()
    ].copy()
    if defensive.empty:
        raise ValueError("No opponent-possession defensive actions")
    defensive = _feature_indicators(defensive)
    group_columns = ["game_id", "team", "player_id"]
    aggregated = (
        defensive.groupby(group_columns, as_index=False)
        .agg(
            threat_prevention_total=("threat_prevention_delta", "sum"),
            defensive_action_count=("threat_prevention_delta", "size"),
            pressure_count=("_pressure", "sum"),
            pressure_recovered=("_pressure_recovered", "sum"),
            pressure_threat=("_pre_threat_pressure", "sum"),
            interception_block_count=("_interception_block", "sum"),
            interception_block_retained=(
                "_interception_block_retained",
                "sum",
            ),
            interception_block_threat=(
                "_pre_threat_interception_block",
                "sum",
            ),
            clearance_count=("_clearance", "sum"),
            clearance_retained=("_clearance_retained", "sum"),
            clearance_threat=("_pre_threat_clearance", "sum"),
            aerial_count=("_aerial", "sum"),
            aerial_success=("_aerial_success", "sum"),
            aerial_mean_threat=("_pre_threat_aerial", "mean"),
            high_threat_count=("_high_threat", "sum"),
            mean_pre_threat=(
                "pre_action_conceding_probability",
                "mean",
            ),
            mean_start_x=("start_x", "mean"),
            central_danger_count=("_central_danger", "sum"),
            has_360=("_has_360", "mean"),
            mean_density_360=("_density_360", "mean"),
            mean_behind_ball_360=("_behind_ball_360", "mean"),
            error_penalty_count=("_error_penalty", "sum"),
            foul_count=("_foul", "sum"),
            failed_count=("_failed", "sum"),
            progression_total=("_progression", "sum"),
            progressive_action_count=("_progressive_action", "sum"),
            progression_retained=("_progression_retained", "sum"),
        )
    )
    samples = aggregated.merge(
        denominators,
        on=["game_id", "team"],
        how="left",
        validate="many_to_one",
    ).rename(columns={"game_id": "match_id"})
    opponent_possessions = samples["opponent_possessions"].clip(lower=1.0)
    opponent_final_third = samples[
        "opponent_final_third_possessions"
    ].clip(lower=1.0)
    samples[TARGET_COLUMN] = (
        100.0 * samples["threat_prevention_total"] / opponent_possessions
    )
    samples["defensive_actions_per100_opponent_possessions"] = (
        100.0 * samples["defensive_action_count"] / opponent_possessions
    )
    samples[
        "defensive_actions_per100_opponent_final_third_possessions"
    ] = 100.0 * samples["defensive_action_count"] / opponent_final_third
    samples["pressures_per100_opponent_possessions"] = (
        100.0 * samples["pressure_count"] / opponent_possessions
    )
    samples["pressure_recovery_rate"] = _safe_divide(
        samples["pressure_recovered"], samples["pressure_count"]
    )
    samples["pressure_threat_exposure_per100"] = (
        100.0 * samples["pressure_threat"] / opponent_possessions
    )
    samples["interceptions_blocks_per100_opponent_possessions"] = (
        100.0 * samples["interception_block_count"] / opponent_possessions
    )
    samples["interception_block_retention_rate"] = _safe_divide(
        samples["interception_block_retained"],
        samples["interception_block_count"],
    )
    samples["interception_block_threat_exposure_per100"] = (
        100.0 * samples["interception_block_threat"] / opponent_possessions
    )
    samples["clearances_per100_opponent_possessions"] = (
        100.0 * samples["clearance_count"] / opponent_possessions
    )
    samples["clearance_retention_rate"] = _safe_divide(
        samples["clearance_retained"], samples["clearance_count"]
    )
    samples["clearance_threat_exposure_per100"] = (
        100.0 * samples["clearance_threat"] / opponent_possessions
    )
    samples["aerial_contests_per100_opponent_possessions"] = (
        100.0 * samples["aerial_count"] / opponent_possessions
    )
    samples["aerial_success_rate"] = _safe_divide(
        samples["aerial_success"], samples["aerial_count"]
    )
    samples["aerial_threat_per_eligible_contest"] = samples[
        "aerial_mean_threat"
    ]
    samples["high_threat_action_share"] = _safe_divide(
        samples["high_threat_count"], samples["defensive_action_count"]
    )
    samples["mean_pre_action_threat"] = samples["mean_pre_threat"]
    samples["mean_defensive_start_x"] = samples["mean_start_x"]
    samples["central_danger_action_share"] = _safe_divide(
        samples["central_danger_count"], samples["defensive_action_count"]
    )
    samples["positioning_360_coverage"] = samples["has_360"]
    samples["mean_defensive_density_360"] = samples["mean_density_360"]
    samples["mean_defenders_behind_ball_360"] = samples[
        "mean_behind_ball_360"
    ]
    samples["errors_penalties_per100_opponent_possessions"] = (
        100.0 * samples["error_penalty_count"] / opponent_possessions
    )
    samples["fouls_per100_opponent_possessions"] = (
        100.0 * samples["foul_count"] / opponent_possessions
    )
    samples["failed_defensive_action_rate"] = _safe_divide(
        samples["failed_count"], samples["defensive_action_count"]
    )
    samples["defensive_progression_per100_opponent_possessions"] = (
        100.0 * samples["progression_total"] / opponent_possessions
    )
    samples["progression_retention_rate"] = _safe_divide(
        samples["progression_retained"],
        samples["progressive_action_count"],
    )

    if player_context is not None:
        context = player_context.copy()
        if "game_id" in context and "match_id" not in context:
            context = context.rename(columns={"game_id": "match_id"})
        context_required = {"match_id", "team", "player_id"}
        missing = context_required.difference(context.columns)
        if missing:
            raise ValueError(
                f"Defensive player context missing: {sorted(missing)}"
            )
        context_columns = ["match_id", "team", "player_id"]
        context_columns.extend(
            column
            for column in ("position_group", "minutes")
            if column in context
        )
        context = context[context_columns].drop_duplicates(
            ["match_id", "team", "player_id"]
        )
        samples = samples.merge(
            context,
            on=["match_id", "team", "player_id"],
            how="left",
            validate="one_to_one",
        )
    if "position_group" in samples:
        samples = samples.loc[
            ~samples["position_group"].eq("Goalkeeper")
        ].copy()
    if "minutes" in samples:
        samples = samples.loc[
            pd.to_numeric(samples["minutes"], errors="coerce").ge(
                minimum_minutes
            )
        ].copy()
    samples["defensive_target_version"] = (
        "conceding-probability-delta-per100-opponent-possessions-v1"
    )
    samples["event_scope_version"] = EVENT_SCOPE_VERSION
    _assert_feature_contract(DEFENSIVE_FEATURES)
    return samples.sort_values(
        ["match_id", "team", "player_id"], kind="mergesort"
    ).reset_index(drop=True)


def _parameter_grid(name: str) -> list[dict[str, Any]]:
    if name == "positive_elastic_net":
        return [
            {"alpha": alpha, "l1_ratio": ratio}
            for alpha in (0.001, 0.01, 0.05)
            for ratio in (0.2, 0.8)
        ]
    if name == "signed_ridge":
        return [{"alpha": alpha} for alpha in (0.1, 1.0, 10.0, 50.0)]
    if name == "signed_elastic_net":
        return [
            {"alpha": alpha, "l1_ratio": ratio}
            for alpha in (0.001, 0.01, 0.05)
            for ratio in (0.2, 0.8)
        ]
    if name == "isotonic_hist_gradient_boosting":
        return [
            {"max_leaf_nodes": leaves, "l2_regularization": penalty}
            for leaves in (7, 15)
            for penalty in (0.1, 1.0)
        ]
    raise ValueError(f"Unknown defensive candidate: {name}")


def _pipeline(name: str, parameters: Mapping[str, Any]) -> Pipeline:
    imputer = SimpleImputer(
        strategy="median",
        keep_empty_features=True,
    )
    if name == "positive_elastic_net":
        model: Any = ElasticNet(
            alpha=float(parameters["alpha"]),
            l1_ratio=float(parameters["l1_ratio"]),
            positive=True,
            max_iter=20_000,
            random_state=RANDOM_STATE,
        )
        return Pipeline(
            [
                ("imputer", imputer),
                ("scaler", StandardScaler()),
                ("model", model),
            ]
        )
    if name == "signed_ridge":
        return Pipeline(
            [
                ("imputer", imputer),
                ("scaler", StandardScaler()),
                ("model", Ridge(alpha=float(parameters["alpha"]))),
            ]
        )
    if name == "signed_elastic_net":
        model = ElasticNet(
            alpha=float(parameters["alpha"]),
            l1_ratio=float(parameters["l1_ratio"]),
            positive=False,
            max_iter=20_000,
            random_state=RANDOM_STATE,
        )
        return Pipeline(
            [
                ("imputer", imputer),
                ("scaler", StandardScaler()),
                ("model", model),
            ]
        )
    if name == "isotonic_hist_gradient_boosting":
        model = HistGradientBoostingRegressor(
            loss="squared_error",
            learning_rate=0.05,
            max_iter=120,
            max_leaf_nodes=int(parameters["max_leaf_nodes"]),
            l2_regularization=float(parameters["l2_regularization"]),
            min_samples_leaf=10,
            early_stopping=False,
            random_state=RANDOM_STATE,
        )
        return Pipeline([("imputer", imputer), ("model", model)])
    raise ValueError(f"Unknown defensive candidate: {name}")


def _splitter(groups: np.ndarray, folds: int) -> GroupKFold:
    unique = np.unique(groups)
    if len(unique) < 2:
        raise ValueError("Defensive validation requires at least two matches")
    return GroupKFold(n_splits=min(folds, len(unique)))


def _select_parameters(
    name: str,
    features: pd.DataFrame,
    target: np.ndarray,
    groups: np.ndarray,
    *,
    inner_folds: int,
) -> dict[str, Any]:
    splitter = _splitter(groups, inner_folds)
    best_parameters: dict[str, Any] | None = None
    best_loss = np.inf
    for parameters in _parameter_grid(name):
        losses: list[float] = []
        for train, validation in splitter.split(features, target, groups):
            model = _pipeline(name, parameters)
            model.fit(features.iloc[train], target[train])
            prediction = model.predict(features.iloc[validation])
            losses.append(
                float(mean_squared_error(target[validation], prediction))
            )
        loss = float(np.mean(losses))
        parameter_key = tuple(sorted(parameters.items()))
        best_key = (
            tuple(sorted(best_parameters.items()))
            if best_parameters is not None
            else ()
        )
        if loss < best_loss - 1e-12 or (
            np.isclose(loss, best_loss)
            and (best_parameters is None or parameter_key < best_key)
        ):
            best_loss = loss
            best_parameters = dict(parameters)
    if best_parameters is None:
        raise RuntimeError("Defensive parameter search produced no model")
    return best_parameters


def _fit_calibrated_nonlinear(
    features: pd.DataFrame,
    target: np.ndarray,
    groups: np.ndarray,
    parameters: Mapping[str, Any],
    *,
    calibration_folds: int,
) -> _CalibratedRegressor:
    splitter = _splitter(groups, calibration_folds)
    raw_oof = np.full(len(features), np.nan)
    for train, validation in splitter.split(features, target, groups):
        model = _pipeline(
            "isotonic_hist_gradient_boosting", parameters
        ).fit(features.iloc[train], target[train])
        raw_oof[validation] = model.predict(features.iloc[validation])
    if not np.isfinite(raw_oof).all():
        raise RuntimeError("Nonlinear calibration OOF coverage is incomplete")
    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(raw_oof, target)
    estimator = _pipeline(
        "isotonic_hist_gradient_boosting", parameters
    ).fit(features, target)
    return _CalibratedRegressor(estimator, calibrator)


def _fit_candidate(
    name: str,
    features: pd.DataFrame,
    target: np.ndarray,
    groups: np.ndarray,
    parameters: Mapping[str, Any],
    *,
    calibration_folds: int,
) -> Pipeline | _CalibratedRegressor:
    if name == "isotonic_hist_gradient_boosting":
        return _fit_calibrated_nonlinear(
            features,
            target,
            groups,
            parameters,
            calibration_folds=calibration_folds,
        )
    return _pipeline(name, parameters).fit(features, target)


def _coefficient_vector(
    fitted: Pipeline | _CalibratedRegressor,
) -> np.ndarray | None:
    estimator = (
        fitted.estimator
        if isinstance(fitted, _CalibratedRegressor)
        else fitted
    )
    model = estimator.named_steps["model"]
    coefficients = getattr(model, "coef_", None)
    return (
        None
        if coefficients is None
        else np.asarray(coefficients, dtype=float)
    )


def _coefficient_stability(
    feature_names: Sequence[str],
    fold_coefficients: list[np.ndarray],
) -> dict[str, dict[str, float | None]]:
    if not fold_coefficients:
        return {
            feature: {
                "mean": None,
                "std": None,
                "nonzero_share": None,
                "sign_agreement": None,
            }
            for feature in feature_names
        }
    matrix = np.vstack(fold_coefficients)
    output: dict[str, dict[str, float | None]] = {}
    for index, feature in enumerate(feature_names):
        values = matrix[:, index]
        nonzero = np.abs(values) > 1e-10
        signs = np.sign(values[nonzero])
        sign_agreement = (
            float(max((signs > 0).mean(), (signs < 0).mean()))
            if len(signs)
            else None
        )
        output[feature] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values, ddof=0)),
            "nonzero_share": float(nonzero.mean()),
            "sign_agreement": sign_agreement,
        }
    return output


def _permutation_summary(
    feature_names: Sequence[str],
    values: Mapping[str, list[float]],
) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for feature in feature_names:
        observations = values.get(feature) or [0.0]
        output[feature] = {
            "rmse_increase_mean": float(np.mean(observations)),
            "rmse_increase_std": float(
                np.std(observations, ddof=0)
            ),
        }
    return output


def _nested_group_oof(
    name: str,
    samples: pd.DataFrame,
    feature_names: Sequence[str],
    *,
    outer_folds: int,
    inner_folds: int,
    fixed_parameters: Mapping[str, Any] | None = None,
    collect_diagnostics: bool = True,
) -> CandidateEvaluation:
    _assert_feature_contract(feature_names)
    matrix = samples.loc[:, feature_names].reset_index(drop=True)
    target = pd.to_numeric(
        samples[TARGET_COLUMN], errors="coerce"
    ).to_numpy(dtype=float)
    groups = samples["match_id"].to_numpy()
    valid = np.isfinite(target)
    matrix = matrix.loc[valid].reset_index(drop=True)
    target = target[valid]
    groups = groups[valid]
    outer = _splitter(groups, outer_folds)
    prediction = np.full(len(matrix), np.nan)
    audits: list[dict[str, Any]] = []
    fold_coefficients: list[np.ndarray] = []
    permutation: dict[str, list[float]] = {
        feature: [] for feature in feature_names
    }
    fold_parameters: list[dict[str, Any]] = []
    rng = np.random.default_rng(RANDOM_STATE)
    for fold, (train, validation) in enumerate(
        outer.split(matrix, target, groups),
        start=1,
    ):
        train_groups = set(groups[train].tolist())
        validation_groups = set(groups[validation].tolist())
        if train_groups.intersection(validation_groups):
            raise RuntimeError("Match leakage in defensive challenger")
        parameters = (
            dict(fixed_parameters)
            if fixed_parameters is not None
            else _select_parameters(
                name,
                matrix.iloc[train],
                target[train],
                groups[train],
                inner_folds=inner_folds,
            )
        )
        fitted = _fit_candidate(
            name,
            matrix.iloc[train],
            target[train],
            groups[train],
            parameters,
            calibration_folds=inner_folds,
        )
        fold_prediction = fitted.predict(matrix.iloc[validation])
        prediction[validation] = fold_prediction
        coefficients = _coefficient_vector(fitted)
        if coefficients is not None:
            if len(coefficients) != len(feature_names):
                raise RuntimeError("Defensive coefficient schema drift")
            fold_coefficients.append(coefficients)
        if collect_diagnostics:
            baseline_rmse = float(
                np.sqrt(
                    mean_squared_error(
                        target[validation], fold_prediction
                    )
                )
            )
            for feature in feature_names:
                shuffled = matrix.iloc[validation].copy()
                shuffled[feature] = rng.permutation(
                    shuffled[feature].to_numpy()
                )
                shuffled_prediction = fitted.predict(shuffled)
                permuted_rmse = float(
                    np.sqrt(
                        mean_squared_error(
                            target[validation], shuffled_prediction
                        )
                    )
                )
                permutation[feature].append(
                    permuted_rmse - baseline_rmse
                )
        audits.append(
            {
                "fold": fold,
                "train_matches": sorted(train_groups),
                "validation_matches": sorted(validation_groups),
                "match_overlap": False,
                "train_rows": int(len(train)),
                "validation_rows": int(len(validation)),
                "parameters": parameters,
                "preprocessing_fit_scope": "outer-training-fold-only",
            }
        )
        fold_parameters.append(parameters)
    if not np.isfinite(prediction).all():
        raise RuntimeError("Defensive OOF prediction coverage incomplete")
    best_parameters = (
        dict(fixed_parameters)
        if fixed_parameters is not None
        else _select_parameters(
            name,
            matrix,
            target,
            groups,
            inner_folds=inner_folds,
        )
    )
    return CandidateEvaluation(
        name=name,
        metrics=_metrics(target, prediction, groups),
        oof_prediction=prediction,
        best_parameters=best_parameters,
        fold_audit=audits,
        coefficient_stability=_coefficient_stability(
            feature_names, fold_coefficients
        ),
        permutation_importance=_permutation_summary(
            feature_names, permutation
        ),
    )


def _bootstrap_comparison(
    samples: pd.DataFrame,
    champion_prediction: np.ndarray,
    challenger_prediction: np.ndarray,
    *,
    draws: int,
) -> dict[str, Any]:
    target = samples[TARGET_COLUMN].to_numpy(dtype=float)
    groups = samples["match_id"].to_numpy()
    unique_groups = np.unique(groups)
    rng = np.random.default_rng(RANDOM_STATE)
    rmse_difference: list[float] = []
    correlation_difference: list[float] = []
    for _ in range(draws):
        selected = rng.choice(
            unique_groups, size=len(unique_groups), replace=True
        )
        indices = np.concatenate(
            [np.flatnonzero(groups == group) for group in selected]
        )
        champion_metrics = _metrics(
            target[indices],
            champion_prediction[indices],
            groups[indices],
        )
        challenger_metrics = _metrics(
            target[indices],
            challenger_prediction[indices],
            groups[indices],
        )
        rmse_difference.append(
            challenger_metrics.rmse - champion_metrics.rmse
        )
        correlation_difference.append(
            challenger_metrics.spearman
            - champion_metrics.spearman
        )
    return {
        "unit": "match bootstrap",
        "draws": draws,
        "rmse_difference_challenger_minus_positive_champion": {
            "estimate": float(
                np.sqrt(
                    mean_squared_error(target, challenger_prediction)
                )
                - np.sqrt(
                    mean_squared_error(target, champion_prediction)
                )
            ),
            "ci_low": float(np.quantile(rmse_difference, 0.025)),
            "ci_high": float(np.quantile(rmse_difference, 0.975)),
        },
        "spearman_difference_challenger_minus_positive_champion": {
            "estimate": float(
                _spearman(target, challenger_prediction)
                - _spearman(target, champion_prediction)
            ),
            "ci_low": float(
                np.quantile(correlation_difference, 0.025)
            ),
            "ci_high": float(
                np.quantile(correlation_difference, 0.975)
            ),
        },
    }


def _leave_one_team_out(
    name: str,
    samples: pd.DataFrame,
    feature_names: Sequence[str],
    parameters: Mapping[str, Any],
    *,
    inner_folds: int,
) -> dict[str, Any]:
    target = samples[TARGET_COLUMN].to_numpy(dtype=float)
    prediction = np.full(len(samples), np.nan)
    fold_audit: list[dict[str, Any]] = []
    teams = sorted(samples["team"].dropna().astype(str).unique())
    for team in teams:
        validation = samples["team"].astype(str).eq(team).to_numpy()
        validation_matches = set(
            samples.loc[validation, "match_id"].tolist()
        )
        train = ~samples["match_id"].isin(validation_matches).to_numpy()
        if train.sum() < 20 or validation.sum() < 1:
            continue
        train_groups = samples.loc[train, "match_id"].to_numpy()
        if len(np.unique(train_groups)) < 2:
            continue
        fitted = _fit_candidate(
            name,
            samples.loc[train, feature_names],
            target[train],
            train_groups,
            parameters,
            calibration_folds=inner_folds,
        )
        prediction[validation] = fitted.predict(
            samples.loc[validation, feature_names]
        )
        fold_audit.append(
            {
                "held_out_team": team,
                "held_out_matches": sorted(validation_matches),
                "train_match_overlap": False,
                "train_rows": int(train.sum()),
                "validation_rows": int(validation.sum()),
            }
        )
    covered = np.isfinite(prediction)
    if covered.sum() < max(20, int(0.8 * len(samples))):
        raise RuntimeError(
            "Leave-one-team-out defensive coverage is incomplete"
        )
    return {
        "metrics": asdict(
            _metrics(
                target[covered],
                prediction[covered],
                samples.loc[covered, "match_id"],
            )
        ),
        "coverage": float(covered.mean()),
        "teams": int(len(fold_audit)),
        "fold_audit": fold_audit,
    }


def _prediction_distribution(
    samples: pd.DataFrame,
    prediction: np.ndarray,
) -> dict[str, Any]:
    frame = pd.DataFrame({"prediction": prediction})
    if "position_group" in samples:
        frame["position_group"] = samples["position_group"].fillna(
            "Unknown"
        ).astype(str)
    else:
        frame["position_group"] = "Unknown"
    cohorts = {
        "all_outfield": pd.Series(True, index=frame.index),
        "center_back": frame["position_group"].eq("Center Back"),
        "fullback_wingback": frame["position_group"].eq(
            "Fullback/Wingback"
        ),
        "defensive_midfield": frame["position_group"].eq(
            "Defensive Midfield"
        ),
    }
    output: dict[str, Any] = {}
    for cohort, mask in cohorts.items():
        values = frame.loc[mask, "prediction"].to_numpy(dtype=float)
        if not len(values):
            output[cohort] = {"rows": 0}
            continue
        rounded = pd.Series(np.round(values, 10))
        output[cohort] = {
            "rows": int(len(values)),
            "mean": float(np.mean(values)),
            "std": float(np.std(values, ddof=0)),
            "minimum": float(np.min(values)),
            "maximum": float(np.max(values)),
            "zero_share": float(np.mean(np.abs(values) <= 1e-12)),
            "largest_constant_share": float(
                rounded.value_counts(normalize=True).iloc[0]
            ),
        }
    return output


def _calibration_slices(
    samples: pd.DataFrame,
    prediction: np.ndarray,
) -> dict[str, Any]:
    frame = samples.copy()
    frame["_prediction"] = prediction
    slices: dict[str, Any] = {}
    if "position_group" in frame:
        position: dict[str, Any] = {}
        for group, rows in frame.groupby("position_group", dropna=False):
            if len(rows) < 3:
                continue
            position[str(group)] = asdict(
                _metrics(
                    rows[TARGET_COLUMN],
                    rows["_prediction"],
                    rows["match_id"],
                )
            ) | {
                "target_mean": float(rows[TARGET_COLUMN].mean()),
                "prediction_mean": float(rows["_prediction"].mean()),
            }
        slices["position_group"] = position
    if "minutes" in frame:
        minute_band = pd.cut(
            pd.to_numeric(frame["minutes"], errors="coerce"),
            bins=[0, 45, 90, np.inf],
            labels=["20-44", "45-89", "90+"],
            right=False,
        )
        minutes: dict[str, Any] = {}
        for band, rows in frame.groupby(minute_band, observed=True):
            if len(rows) < 3:
                continue
            minutes[str(band)] = asdict(
                _metrics(
                    rows[TARGET_COLUMN],
                    rows["_prediction"],
                    rows["match_id"],
                )
            ) | {
                "target_mean": float(rows[TARGET_COLUMN].mean()),
                "prediction_mean": float(rows["_prediction"].mean()),
            }
        slices["minutes_band"] = minutes
    return slices


def _ablation_diagnostics(
    selected_name: str,
    selected: CandidateEvaluation,
    samples: pd.DataFrame,
    *,
    outer_folds: int,
    inner_folds: int,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for group, removed in DEFENSIVE_FEATURE_GROUPS.items():
        features = tuple(
            feature
            for feature in DEFENSIVE_FEATURES
            if feature not in removed
        )
        ablated = _nested_group_oof(
            selected_name,
            samples,
            features,
            outer_folds=outer_folds,
            inner_folds=inner_folds,
            fixed_parameters=selected.best_parameters,
            collect_diagnostics=False,
        )
        output[group] = {
            "removed_features": list(removed),
            "metrics": asdict(ablated.metrics),
            "rmse_change_ablated_minus_full": (
                ablated.metrics.rmse - selected.metrics.rmse
            ),
            "spearman_change_ablated_minus_full": (
                ablated.metrics.spearman - selected.metrics.spearman
            ),
        }
    return output


def evaluate_defensive_challengers(
    samples: pd.DataFrame,
    *,
    champion_reference_correlation: float = (
        CHAMPION_REFERENCE_CORRELATION
    ),
    outer_folds: int = 5,
    inner_folds: int = 4,
    bootstrap_draws: int = 500,
    run_ablations: bool = True,
) -> DefensiveChallengerEvaluation:
    """Compare defensive architectures and apply the declared promotion gate."""

    required = {
        "match_id",
        "team",
        "player_id",
        TARGET_COLUMN,
        *DEFENSIVE_FEATURES,
    }
    missing = required.difference(samples.columns)
    if missing:
        raise ValueError(
            f"Defensive challenger samples missing: {sorted(missing)}"
        )
    if bootstrap_draws < 50:
        raise ValueError("Defensive bootstrap requires at least 50 draws")
    _assert_feature_contract(DEFENSIVE_FEATURES)
    working = samples.loc[
        pd.to_numeric(samples[TARGET_COLUMN], errors="coerce").notna()
    ].reset_index(drop=True)
    if working["match_id"].nunique() < 4:
        raise ValueError("At least four matches are required")

    names = (
        "positive_elastic_net",
        "signed_ridge",
        "signed_elastic_net",
        "isotonic_hist_gradient_boosting",
    )
    evaluations = {
        name: _nested_group_oof(
            name,
            working,
            DEFENSIVE_FEATURES,
            outer_folds=outer_folds,
            inner_folds=inner_folds,
        )
        for name in names
    }
    positive = evaluations["positive_elastic_net"]
    challenger_names = [name for name in names if name != positive.name]
    selected_name = sorted(
        challenger_names,
        key=lambda name: (
            -evaluations[name].metrics.spearman,
            evaluations[name].metrics.rmse,
            name,
        ),
    )[0]
    selected = evaluations[selected_name]
    bootstrap = _bootstrap_comparison(
        working,
        positive.oof_prediction,
        selected.oof_prediction,
        draws=bootstrap_draws,
    )
    positive_loto = _leave_one_team_out(
        positive.name,
        working,
        DEFENSIVE_FEATURES,
        positive.best_parameters,
        inner_folds=inner_folds,
    )
    selected_loto = _leave_one_team_out(
        selected.name,
        working,
        DEFENSIVE_FEATURES,
        selected.best_parameters,
        inner_folds=inner_folds,
    )
    distribution = _prediction_distribution(
        working, selected.oof_prediction
    )
    defensive_cohorts = (
        distribution["center_back"],
        distribution["fullback_wingback"],
        distribution["defensive_midfield"],
    )
    noncollapsed = all(
        cohort.get("rows", 0) < 3
        or (
            cohort["std"] > 1e-8
            and cohort["largest_constant_share"] < 0.80
        )
        for cohort in defensive_cohorts
    )
    rmse_noninferiority_tolerance = max(
        1e-6, 0.02 * positive.metrics.rmse
    )
    rmse_noninferior = bool(
        bootstrap[
            "rmse_difference_challenger_minus_positive_champion"
        ]["ci_high"]
        <= rmse_noninferiority_tolerance
    )
    correlation_material = bool(
        selected.metrics.spearman
        >= champion_reference_correlation + 0.03
    )
    loto_noninferior = bool(
        selected_loto["metrics"]["rmse"]
        <= positive_loto["metrics"]["rmse"] * 1.02
        and selected_loto["metrics"]["spearman"]
        >= positive_loto["metrics"]["spearman"] - 0.01
    )
    forbidden_features_absent = not any(
        fragment in feature.lower()
        for feature in DEFENSIVE_FEATURES
        for fragment in FORBIDDEN_DEFENSIVE_PREDICTOR_FRAGMENTS
    )
    gate_checks = {
        "held_out_rmse_noninferior_by_match_bootstrap": rmse_noninferior,
        "material_correlation_vs_incumbent_reference": (
            correlation_material
        ),
        "cb_fb_dm_predictions_noncollapsed": noncollapsed,
        "attacking_spurious_predictors_absent": (
            forbidden_features_absent
        ),
        "leave_one_team_out_noninferior": loto_noninferior,
    }
    promoted = bool(all(gate_checks.values()))
    active_component = (
        f"defensive_challenger:{selected.name}"
        if promoted
        else "champion_defensive_head"
    )
    ablations = (
        _ablation_diagnostics(
            selected.name,
            selected,
            working,
            outer_folds=outer_folds,
            inner_folds=inner_folds,
        )
        if run_ablations
        else {}
    )
    candidate_diagnostics: dict[str, Any] = {}
    for name, evaluation in evaluations.items():
        candidate_diagnostics[name] = {
            "metrics": asdict(evaluation.metrics),
            "best_parameters": evaluation.best_parameters,
            "fold_audit": evaluation.fold_audit,
            "coefficient_stability": evaluation.coefficient_stability,
            "permutation_importance": evaluation.permutation_importance,
            "model_family": (
                "calibrated nonlinear"
                if name == "isotonic_hist_gradient_boosting"
                else "regularized linear"
            ),
            "signed_coefficients": name != "positive_elastic_net",
        }
    predictions = working[
        [
            column
            for column in (
                "match_id",
                "team",
                "player_id",
                "position_group",
                "minutes",
                TARGET_COLUMN,
            )
            if column in working
        ]
    ].copy()
    for name, evaluation in evaluations.items():
        predictions[f"{name}_oof_prediction"] = (
            evaluation.oof_prediction
        )
    diagnostics = {
        "schema_version": "defensive-challenger-v1",
        "random_seed": RANDOM_STATE,
        "target": {
            "name": TARGET_COLUMN,
            "formula": (
                "100 * sum(pre_action_p_concedes - "
                "team_oriented_next_state_p_concedes) / "
                "opponent_possessions"
            ),
            "event_type_used_to_define_target": False,
            "ordinary_periods": [1, 2, 3, 4],
            "event_scope_version": EVENT_SCOPE_VERSION,
            "rows": int(len(working)),
            "matches": int(working["match_id"].nunique()),
            "teams": int(working["team"].nunique()),
        },
        "feature_contract": {
            "features": list(DEFENSIVE_FEATURES),
            "groups": {
                group: list(features)
                for group, features in DEFENSIVE_FEATURE_GROUPS.items()
            },
            "opportunity_adjusted": True,
            "player_identity_feature_count": 0,
            "team_identity_feature_count": 0,
            "attacking_spurious_feature_count": 0,
            "preprocessing": (
                "median imputation and linear scaling fitted inside folds"
            ),
        },
        "validation": {
            "outer": "match-disjoint GroupKFold",
            "inner": "match-disjoint GroupKFold parameter selection",
            "leave_one_team_out": (
                "held-out team rows; all matches involving that team "
                "removed from training"
            ),
            "bootstrap_unit": "match",
        },
        "incumbent_reference": {
            "correlation": champion_reference_correlation,
            "source": "immutable pre-repair champion snapshot",
            "note": (
                "The incumbent target differs; RMSE non-inferiority is "
                "therefore evaluated against the positive-ElasticNet "
                "architecture on the new target."
            ),
        },
        "candidates": candidate_diagnostics,
        "selected_challenger": selected.name,
        "bootstrap_comparison": bootstrap,
        "leave_one_team_out": {
            positive.name: positive_loto,
            selected.name: selected_loto,
        },
        "prediction_distribution": distribution,
        "direct_threat_prevention_correlation": (
            selected.metrics.spearman
        ),
        "calibration_by_position_and_minutes": _calibration_slices(
            working, selected.oof_prediction
        ),
        "ablations": ablations,
        "promotion_gate": {
            "checks": gate_checks,
            "passed": promoted,
            "active_component": active_component,
            "failed_checks": [
                name for name, passed in gate_checks.items() if not passed
            ],
            "rule": (
                "Retain the incumbent defensive head unless every "
                "predeclared predictive, noncollapse, spurious-feature, "
                "and leave-one-team-out check passes."
            ),
        },
    }
    return DefensiveChallengerEvaluation(
        diagnostics=diagnostics,
        oof_predictions=predictions,
    )
