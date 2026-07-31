"""Single-metric Qatar 2022 goalkeeper valuation (PSxG + clutch v5).

The scorer is deliberately identity blind.  Player and team labels are join
keys only; they never enter a feature matrix or a scoring rule.  The public
estimand combines:

* calibrated post-shot expected-goal prevention on ordinary on-target shots;
* an explicit late / extra-time and match-preserving clutch residual;
* a mutually exclusive non-clutch state-leverage residual;
* separately regularized regular penalties;
* credited-save shootout win-probability added;
* bounded cross/claim, sweeping, and pressured-distribution support.

Anti-double-count rule
----------------------
Every ordinary shot contributes ``p_psxg - goal`` exactly once to the primary
PSxG channel.  A saved late shot can additionally contribute only the
``multiplier - 1`` residual to the clutch channel.  Non-late shots can
additionally contribute only the positive leverage residual to the state
channel.  A shot is therefore never in both clutch and state residuals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np
import pandas as pd

from src.models.goalkeeper_tournament_impact_v4 import (
    REGULAR_PENALTY_PRIOR_STRENGTH,
    SHOOTOUT_CONVERSION_FALLBACK,
    extract_shot_events_v4,
)

MODEL_VERSION = "goalkeeper_consolidated_value_v5"

REQUIRED_WEIGHT_KEYS = {
    "psxg",
    "clutch",
    "state_leverage",
    "regular_penalty",
    "shootout",
    "support",
}


@dataclass(frozen=True)
class GoalkeeperV5Config:
    """Preregistered settings for one consolidated goalkeeper score."""

    weights: Mapping[str, float] = field(
        default_factory=lambda: {
            "psxg": 0.45,
            "clutch": 0.25,
            "state_leverage": 0.05,
            "regular_penalty": 0.05,
            "shootout": 0.15,
            "support": 0.05,
        }
    )
    shootout_bound: float = 0.35
    clutch_bound: float = 0.75
    clutch_late_multiplier: float = 2.0
    clutch_match_state_multiplier: float = 1.5
    shot_reliability_count: float = 18.0
    penalty_reliability_count: float = 3.0
    shootout_reliability_count: float = 4.0
    support_reliability_count: float = 20.0
    minutes_reliability_constant: float = 450.0
    easy_psxg_threshold: float = 0.20
    hard_psxg_threshold: float = 0.50

    def __post_init__(self) -> None:
        if set(self.weights) != REQUIRED_WEIGHT_KEYS:
            raise ValueError(
                "v5 weights must have exactly "
                f"{sorted(REQUIRED_WEIGHT_KEYS)}"
            )
        if any(
            (not np.isfinite(value)) or value < 0.0
            for value in self.weights.values()
        ):
            raise ValueError("v5 weights must be finite and nonnegative")
        if abs(sum(self.weights.values()) - 1.0) > 1e-10:
            raise ValueError("v5 weights must sum to one")
        if self.weights["psxg"] < max(
            value
            for key, value in self.weights.items()
            if key != "psxg"
        ):
            raise ValueError("PSxG must be the largest single v5 weight")
        if self.weights["psxg"] + self.weights["clutch"] < 0.55:
            raise ValueError("PSxG plus clutch weight must be at least 0.55")
        if self.weights["shootout"] > 0.20:
            raise ValueError("Shootout weight must not exceed 0.20")
        if self.weights["support"] > 0.25:
            raise ValueError("Support weight must not exceed 0.25")
        if self.weights["regular_penalty"] > 0.10:
            raise ValueError("Regular-penalty weight must not exceed 0.10")
        if not 0.0 < self.shootout_bound <= 1.0:
            raise ValueError("shootout_bound must be in (0, 1]")
        if not 0.0 < self.clutch_bound <= 2.0:
            raise ValueError("clutch_bound must be in (0, 2]")
        for name in (
            "clutch_late_multiplier",
            "clutch_match_state_multiplier",
        ):
            if getattr(self, name) < 1.0:
                raise ValueError(f"{name} cannot reduce a clutch save")
        for name in (
            "shot_reliability_count",
            "penalty_reliability_count",
            "shootout_reliability_count",
            "support_reliability_count",
            "minutes_reliability_constant",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")


def is_late_or_extra_time(minute: float, period: int) -> bool:
    """Whether an action belongs to the preregistered clutch time window."""

    return bool(period in (3, 4) or (period in (1, 2) and minute >= 75.0))


def clutch_multiplier(
    *,
    minute: float,
    period: int,
    score_diff_defending: int,
    knockout: bool,
    state_leverage: float = 0.0,
    config: GoalkeeperV5Config,
) -> float:
    """Difficulty-preserving multiplier for a saved shot.

    The match-state increment is available only in the late/extra-time window.
    A level or one-goal-leading state is match preserving.  Knockout status is
    a pre-action state modifier, not a bonus for subsequently advancing.
    """

    if not is_late_or_extra_time(minute, period):
        return 1.0
    leverage_factor = 0.25 + 0.75 * float(
        np.clip(state_leverage / 0.5, 0.0, 1.5)
    )
    late_residual = (
        config.clutch_late_multiplier - 1.0
    ) * leverage_factor
    if knockout:
        # Small state-only uplift: the action occurs in an elimination match;
        # no credit depends on whether the team later advances.
        late_residual *= 1.10
    match_state_residual = 0.0
    if score_diff_defending in (0, 1):
        match_state_residual = (
            config.clutch_match_state_multiplier - 1.0
        ) * leverage_factor
    return float(1.0 + late_residual + match_state_residual)


def extract_shot_events_v5(
    events: pd.DataFrame,
    matches: pd.DataFrame,
    goal_probabilities: pd.Series,
    *,
    config: GoalkeeperV5Config,
) -> pd.DataFrame:
    """Materialize ordinary/penalty shots and mutually exclusive residuals."""

    shots = extract_shot_events_v4(
        events,
        matches,
        goal_probabilities,
        leverage_exponent=1.0,
    ).copy()
    return add_v5_shot_channels(shots, config=config)


def add_v5_shot_channels(
    shot_events: pd.DataFrame,
    *,
    config: GoalkeeperV5Config,
) -> pd.DataFrame:
    """Add v5 channel attribution to an extracted v4-compatible shot table."""

    shots = shot_events.copy()
    probability = pd.to_numeric(
        shots["goal_probability_v3"], errors="coerce"
    )
    goal = pd.to_numeric(shots["goal"], errors="coerce")
    shots["p_psxg_v5"] = probability
    shots["prevention_v5"] = probability - goal
    shots["late_or_extra_time_v5"] = [
        is_late_or_extra_time(float(minute), int(period))
        for minute, period in zip(shots["minute"], shots["period"])
    ]
    knockout_values = _as_bool(shots["knockout"])
    shots["clutch_multiplier_v5"] = [
        clutch_multiplier(
            minute=float(minute),
            period=int(period),
            score_diff_defending=int(score_diff),
            knockout=bool(knockout),
            state_leverage=float(leverage),
            config=config,
        )
        for minute, period, score_diff, knockout, leverage in zip(
            shots["minute"],
            shots["period"],
            shots["pre_shot_score_diff_defending"],
            knockout_values,
            shots["leverage_v4"],
        )
    ]
    saved_prevention = shots["prevention_v5"].clip(lower=0.0)
    regular_penalty_mask = _as_bool(shots["is_regular_penalty"])
    clutch_mask = (
        shots["late_or_extra_time_v5"]
        & shots["shot_outcome"].eq("Saved")
        & ~regular_penalty_mask
    )
    leverage_factor = 0.25 + 0.75 * (
        pd.to_numeric(shots["leverage_v4"], errors="coerce").fillna(0.0)
        / 0.5
    ).clip(0.0, 1.5)
    knockout_factor = np.where(_as_bool(shots["knockout"]), 1.10, 1.0)
    shots["late_game_prevention_residual_v5"] = np.where(
        clutch_mask,
        saved_prevention
        * (config.clutch_late_multiplier - 1.0)
        * leverage_factor
        * knockout_factor,
        0.0,
    )
    match_state_mask = (
        pd.to_numeric(
            shots["pre_shot_score_diff_defending"], errors="coerce"
        )
        .fillna(-99)
        .isin([0, 1])
    )
    shots["match_winning_save_residual_v5"] = np.where(
        clutch_mask & match_state_mask,
        saved_prevention
        * (config.clutch_match_state_multiplier - 1.0)
        * leverage_factor,
        0.0,
    )
    shots["clutch_prevention_residual_v5"] = (
        shots["late_game_prevention_residual_v5"]
        + shots["match_winning_save_residual_v5"]
    )

    ordinary = ~regular_penalty_mask
    ordinary_mean_leverage = float(
        shots.loc[ordinary, "leverage_v4"].mean()
    )
    if not np.isfinite(ordinary_mean_leverage) or ordinary_mean_leverage <= 0:
        ordinary_mean_leverage = 1.0
    leverage_ratio = (
        pd.to_numeric(shots["leverage_v4"], errors="coerce")
        / ordinary_mean_leverage
    )
    non_clutch = ordinary & ~clutch_mask
    shots["state_leverage_prevention_residual_v5"] = np.where(
        non_clutch,
        shots["prevention_v5"]
        * (leverage_ratio - 1.0).clip(lower=0.0),
        0.0,
    )
    shots["v5_channel_membership"] = np.select(
        [
            regular_penalty_mask,
            clutch_mask,
            ordinary,
        ],
        [
            "regular_penalty",
            "psxg_plus_clutch_residual",
            "psxg_plus_nonclutch_state_residual",
        ],
        default="excluded",
    )
    return shots


def _safe_numeric(
    frame: pd.DataFrame, column: str, default: float = np.nan
) -> pd.Series:
    if column not in frame:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce")


def _as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False).astype(bool)
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "1", "yes"})
    )


def _midrank_percentile(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.rank(method="average", pct=True)


def _signed_scale(series: pd.Series) -> pd.Series:
    """Scale a zero-anchored value without converting missingness to success."""

    numeric = pd.to_numeric(series, errors="coerce")
    finite = numeric[np.isfinite(numeric)]
    if finite.empty:
        return pd.Series(np.nan, index=series.index, dtype=float)
    scale = float(np.quantile(np.abs(finite), 0.90))
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = float(np.abs(finite).max())
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = 1.0
    return (numeric / scale).clip(-1.0, 1.0)


def _signed_rank_scale(series: pd.Series) -> pd.Series:
    """Identity-free zero-anchored midranks in [-0.5, 0.5]."""

    numeric = pd.to_numeric(series, errors="coerce")
    result = pd.Series(np.nan, index=series.index, dtype=float)
    positive = numeric.gt(0.0)
    negative = numeric.lt(0.0)
    zero = numeric.eq(0.0)
    if positive.any():
        result.loc[positive] = (
            numeric.loc[positive].rank(method="average", pct=True) * 0.5
        )
    if negative.any():
        result.loc[negative] = -(
            numeric.loc[negative]
            .abs()
            .rank(method="average", pct=True)
            * 0.5
        )
    result.loc[zero] = 0.0
    return result


def _support_channels(
    output: pd.DataFrame,
    main_mask: pd.Series,
    config: GoalkeeperV5Config,
) -> pd.DataFrame:
    support_inputs = {
        "cross_claim_value_v5": [
            "cross_stopping_rate",
            "claims_p90",
        ],
        "sweeping_value_v5": ["sweeper_actions_p90"],
        "distribution_value_v5": ["distribution_under_pressure"],
    }
    components = pd.DataFrame(index=output.index)
    available = pd.DataFrame(index=output.index)
    for published, columns in support_inputs.items():
        percentiles = []
        for column in columns:
            values = _safe_numeric(output.loc[main_mask], column)
            if values.notna().any():
                percentiles.append(
                    _midrank_percentile(values).reindex(output.index)
                )
        combined = (
            pd.concat(percentiles, axis=1).mean(axis=1, skipna=True)
            if percentiles
            else pd.Series(np.nan, index=output.index, dtype=float)
        )
        output[published] = combined
        components[published] = combined
        available[published] = combined.notna()
    denominator = available.astype(float).sum(axis=1)
    raw = (
        components.fillna(0.0) * available.astype(float)
    ).sum(axis=1) / denominator.replace(0.0, np.nan)
    evidence_count = _safe_numeric(output, "actions", 0.0).fillna(0.0)
    reliability = evidence_count / (
        evidence_count + config.support_reliability_count
    )
    output["support_feature_coverage_v5"] = (
        denominator / len(support_inputs)
    ).clip(0.0, 1.0)
    output["support_composite_v5"] = (
        0.5 + reliability * (raw - 0.5)
    ).fillna(0.5)
    return output


def calculate_goalkeeper_consolidated_value_v5(
    goalkeeper_base: pd.DataFrame,
    shot_events: pd.DataFrame,
    shootout_kicks: pd.DataFrame,
    *,
    config: GoalkeeperV5Config,
    config_id: str = "unselected",
    consolidation_status: str = "candidate_only",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Aggregate all v5 channels and rank one main goalkeeper per team."""

    required = {
        "player_id",
        "player_name",
        "team",
        "minutes",
        "is_main_goalkeeper",
    }
    missing = required.difference(goalkeeper_base.columns)
    if missing:
        raise ValueError(f"v5 goalkeeper base missing {sorted(missing)}")
    output = goalkeeper_base.copy()
    main_mask = _as_bool(output["is_main_goalkeeper"])
    if output.loc[main_mask, "team"].duplicated().any():
        raise ValueError("v5 requires exactly one main goalkeeper per team")

    regular_penalty_mask = _as_bool(shot_events["is_regular_penalty"])
    ordinary = shot_events.loc[
        ~regular_penalty_mask
        & shot_events["p_psxg_v5"].notna()
    ].copy()
    penalties = shot_events.loc[
        regular_penalty_mask
    ].copy()

    by_team = ordinary.groupby("defending_team").agg(
        psxg_goals_prevented_v5=("prevention_v5", "sum"),
        ordinary_shots_on_target_v5=("prevention_v5", "size"),
        psxg_mean_difficulty_faced_v5=("p_psxg_v5", "mean"),
        clutch_save_value_raw_v5=(
            "clutch_prevention_residual_v5",
            "sum",
        ),
        late_game_prevention_value_raw_v5=(
            "late_game_prevention_residual_v5",
            "sum",
        ),
        match_winning_save_value_raw_v5=(
            "match_winning_save_residual_v5",
            "sum",
        ),
        state_leverage_prevention_value_raw_v5=(
            "state_leverage_prevention_residual_v5",
            "sum",
        ),
    )
    easy = ordinary["p_psxg_v5"].le(config.easy_psxg_threshold)
    hard = ordinary["p_psxg_v5"].ge(config.hard_psxg_threshold)
    by_team["psxg_easy_shot_share_faced_v5"] = (
        easy.groupby(ordinary["defending_team"]).mean()
    )
    by_team["psxg_hard_shot_share_faced_v5"] = (
        hard.groupby(ordinary["defending_team"]).mean()
    )
    easy_saved = easy & ordinary["shot_outcome"].eq("Saved")
    hard_saved = hard & ordinary["shot_outcome"].eq("Saved")
    by_team["psxg_easy_save_rate_v5"] = (
        easy_saved.groupby(ordinary["defending_team"]).sum()
        / easy.groupby(ordinary["defending_team"]).sum().replace(0, np.nan)
    )
    by_team["psxg_hard_save_rate_v5"] = (
        hard_saved.groupby(ordinary["defending_team"]).sum()
        / hard.groupby(ordinary["defending_team"]).sum().replace(0, np.nan)
    )

    for column in by_team:
        output[column] = output["team"].map(by_team[column])
    count = output["ordinary_shots_on_target_v5"].fillna(0.0)
    shot_reliability = count / (count + config.shot_reliability_count)
    output["shot_stopping_reliability_v5"] = shot_reliability
    output["psxg_shot_stopping_value_raw_v5"] = output[
        "psxg_goals_prevented_v5"
    ].fillna(0.0)
    psxg_rank_signal = _signed_rank_scale(
        output.loc[main_mask, "psxg_shot_stopping_value_raw_v5"]
    )
    output["psxg_shot_stopping_value_v5"] = (
        psxg_rank_signal
        * shot_reliability.loc[main_mask]
    ).reindex(output.index)

    clutch_raw = output["clutch_save_value_raw_v5"].fillna(0.0)
    clutch_rank = _signed_rank_scale(clutch_raw.loc[main_mask])
    clutch_magnitude = np.tanh(
        clutch_raw.loc[main_mask].abs() / config.clutch_bound
    )
    output["clutch_save_value_v5"] = (
        clutch_rank * clutch_magnitude
    ).reindex(output.index).fillna(0.0)
    for raw_name, published in (
        (
            "late_game_prevention_value_raw_v5",
            "late_game_prevention_value_v5",
        ),
        (
            "match_winning_save_value_raw_v5",
            "match_winning_save_value_v5",
        ),
        (
            "state_leverage_prevention_value_raw_v5",
            "state_leverage_prevention_value_v5",
        ),
    ):
        raw_channel = output.loc[main_mask, raw_name].fillna(0.0)
        output[published] = (
            _signed_rank_scale(raw_channel)
            * np.tanh(raw_channel.abs() / 0.5)
        ).reindex(output.index).fillna(0.0)

    total_penalties = len(penalties)
    scored_penalties = (
        float(penalties["goal"].sum()) if total_penalties else 0.0
    )
    penalty_prior = (
        scored_penalties
        + SHOOTOUT_CONVERSION_FALLBACK
        * REGULAR_PENALTY_PRIOR_STRENGTH
    ) / (total_penalties + REGULAR_PENALTY_PRIOR_STRENGTH)
    penalties["regular_penalty_prevention_v5"] = (
        penalty_prior - penalties["goal"]
    )
    pen_by_team = penalties.groupby("defending_team").agg(
        regular_penalty_impact_raw_v5=(
            "regular_penalty_prevention_v5",
            "sum",
        ),
        regular_penalties_on_target_v5=(
            "regular_penalty_prevention_v5",
            "size",
        ),
    )
    output["regular_penalty_impact_raw_v5"] = (
        output["team"]
        .map(pen_by_team["regular_penalty_impact_raw_v5"])
        .fillna(0.0)
    )
    output["regular_penalties_on_target_v5"] = (
        output["team"]
        .map(pen_by_team["regular_penalties_on_target_v5"])
        .fillna(0.0)
    )
    pen_count = output["regular_penalties_on_target_v5"]
    output["penalty_reliability_v5"] = pen_count / (
        pen_count + config.penalty_reliability_count
    )
    output["regular_penalty_impact_v5"] = _signed_rank_scale(
        (
            output.loc[main_mask, "regular_penalty_impact_raw_v5"]
            * output.loc[main_mask, "penalty_reliability_v5"]
        )
    ).reindex(output.index).fillna(0.0)

    if shootout_kicks.empty:
        so_by_gk = pd.DataFrame(
            columns=[
                "shootout_win_probability_added_raw_v5",
                "shootout_kicks_faced_v5",
                "shootout_saves_credited_v5",
            ]
        )
    else:
        so_by_gk = shootout_kicks.groupby("goalkeeper_player_id").agg(
            shootout_win_probability_added_raw_v5=("goalkeeper_wpa", "sum"),
            shootout_kicks_faced_v5=("goalkeeper_wpa", "size"),
            shootout_saves_credited_v5=(
                "goalkeeper_credited_save",
                "sum",
            ),
        )
    player_id = pd.to_numeric(output["player_id"], errors="coerce")
    for column in (
        "shootout_win_probability_added_raw_v5",
        "shootout_kicks_faced_v5",
        "shootout_saves_credited_v5",
    ):
        output[column] = player_id.map(so_by_gk[column]).fillna(0.0)
    so_count = output["shootout_kicks_faced_v5"]
    output["shootout_reliability_v5"] = so_count / (
        so_count + config.shootout_reliability_count
    )
    bounded_so = output[
        "shootout_win_probability_added_raw_v5"
    ].clip(-config.shootout_bound, config.shootout_bound)
    output["shootout_win_probability_added_v5"] = (
        0.5
        * bounded_so.loc[main_mask]
        / config.shootout_bound
        * output.loc[main_mask, "shootout_reliability_v5"]
    ).reindex(output.index).fillna(0.0)

    output = _support_channels(output, main_mask, config)
    output["support_value_centered_v5"] = (
        output["support_composite_v5"] - 0.5
    )

    minutes = _safe_numeric(output, "minutes", 0.0).fillna(0.0)
    maximum_main_minutes = float(minutes.loc[main_mask].max()) or 1.0
    output["tournament_exposure_v5"] = (
        minutes / maximum_main_minutes
    ).clip(0.0, 1.0)
    minutes_reliability = minutes / (
        minutes + config.minutes_reliability_constant
    )
    output["goalkeeper_reliability_v5"] = minutes_reliability.clip(
        0.0, 1.0
    )

    # Convert standardized performance signals into tournament contribution
    # signals using observed minutes.  This is exposure, not a round-reached
    # or team-pedigree bonus: two keepers with the same event evidence and
    # minutes receive the same value regardless of identity or team.
    exposure_adjusted = (
        "psxg_shot_stopping_value_v5",
        "clutch_save_value_v5",
        "state_leverage_prevention_value_v5",
        "regular_penalty_impact_v5",
        "support_value_centered_v5",
    )
    for column in exposure_adjusted:
        output[f"{column}_before_exposure"] = output[column]
        output[column] = (
            output[column] * output["tournament_exposure_v5"]
        )

    weights = config.weights
    component_sum = (
        weights["psxg"]
        * output["psxg_shot_stopping_value_v5"].fillna(0.0)
        + weights["clutch"] * output["clutch_save_value_v5"]
        + weights["state_leverage"]
        * output["state_leverage_prevention_value_v5"]
        + weights["regular_penalty"]
        * output["regular_penalty_impact_v5"]
        + weights["shootout"]
        * output["shootout_win_probability_added_v5"]
        + weights["support"] * output["support_value_centered_v5"]
    )
    component_prior = float(component_sum.loc[main_mask].mean())
    # Reliability is shrinkage toward the cohort mean, not a team-progress
    # bonus and not shrinkage toward a favorable zero.
    output["goalkeeper_consolidated_value_raw_v5"] = (
        output["goalkeeper_reliability_v5"] * component_sum
        + (1.0 - output["goalkeeper_reliability_v5"]) * component_prior
    ).where(main_mask)

    raw = output.loc[
        main_mask, "goalkeeper_consolidated_value_raw_v5"
    ]
    low = float(raw.min())
    high = float(raw.max())
    span = (high - low) or 1.0
    output["goalkeeper_consolidated_value_score_v5"] = (
        (output["goalkeeper_consolidated_value_raw_v5"] - low) / span
    ).where(main_mask).clip(0.0, 1.0)
    ranks = (
        output.loc[main_mask, "goalkeeper_consolidated_value_score_v5"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    output["goalkeeper_consolidated_value_rank_v5"] = pd.Series(
        pd.NA, index=output.index, dtype="Int64"
    )
    output.loc[
        main_mask, "goalkeeper_consolidated_value_rank_v5"
    ] = ranks

    output["opponent_attack_strength_faced_v5"] = np.nan
    output["v5_selected_config_id"] = config_id
    output["v5_consolidation_status"] = consolidation_status
    output["active_goalkeeper_rank_field"] = (
        "goalkeeper_consolidated_value_rank_v5"
        if consolidation_status == "promoted_single_metric"
        else "goalkeeper_rank_v3"
    )
    output["goalkeeper_event_profile_score_v3"] = _safe_numeric(
        output, "dedicated_goalkeeper_score_v3"
    )

    audit = {
        "model_version": MODEL_VERSION,
        "weights": dict(weights),
        "config": {
            "shootout_bound": config.shootout_bound,
            "clutch_bound": config.clutch_bound,
            "clutch_late_multiplier": config.clutch_late_multiplier,
            "clutch_match_state_multiplier": (
                config.clutch_match_state_multiplier
            ),
            "shot_reliability_count": config.shot_reliability_count,
        },
        "anti_double_count_rule": (
            "PSxG contains prevention once; clutch is multiplier-minus-one "
            "on late saved shots; state leverage is multiplier-minus-one "
            "on non-clutch shots only"
        ),
        "ordinary_shots_valued": int(len(ordinary)),
        "regular_penalties_valued": int(len(penalties)),
        "shootout_kicks_valued": int(len(shootout_kicks)),
        "identity_features_used": [],
        "pedigree_features_used": [],
        "opponent_attack_strength_feature_used": False,
        "opponent_difficulty_treatment": (
            "calibrated PSxG and pre-action match/knockout state only"
        ),
        "score_normalization": {"raw_min": low, "raw_max": high},
    }
    return output, audit
