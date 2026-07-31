"""Positionally balanced Qatar 2022 outfield Tournament Impact v4.

This module owns the structural coupling between opposition adjustment,
off-ball prevention, reliability shrinkage, variance balancing, continuous
role mixtures, and the final composite.  It deliberately has no player/team
special cases and never consumes identity, nationality, awards, advancement,
or desired ranks as numerical features.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy.special import expit


MODEL_VERSION = "outfield_tournament_impact_v4"
REQUIRED_DEFENSIVE_PIPELINE_STAGES = (
    "opposition_adjusted",
    "prevention_augmented",
    "reliability_shrunk",
    "variance_rescaled",
    "mixture_weighted",
)

IDENTITY_OR_TARGET_FIELDS = frozenset(
    {
        "player",
        "player_name",
        "player_id",
        "team",
        "team_name",
        "nationality",
        "award",
        "global_rank",
        "global_rank_v3",
        "target_rank",
        "desired_rank",
        "competition_stage",
        "advancement_stage",
        "round_reached",
        "winner",
    }
)

ROLE_PROBABILITY_PREFIX = "role_probability_"


@dataclass(frozen=True)
class OutfieldV4Config:
    """Frozen configuration selected from the preregistered grid."""

    variance_share_target: float = 0.42
    mixture_lower: float = 0.25
    mixture_upper: float = 0.75
    attack_reliability_constant: float = 40.0
    defense_reliability_constant: float = 180.0
    bootstrap_se_shrinkage_constant: float = 1.0
    opposition_adjustment_variant: str = "fifa_inverse_sqrt"
    opposition_exposure_scale: float = 1.5
    prevention_weight: float = 0.5
    random_seed: int = 42
    bootstrap_replicates: int = 500

    def __post_init__(self) -> None:
        if not 0.35 <= self.variance_share_target <= 0.50:
            raise ValueError("defensive variance share must be in [0.35, 0.50]")
        if not 0.0 < self.mixture_lower < self.mixture_upper < 1.0:
            raise ValueError("mixture bounds must be strictly inside (0, 1)")
        if abs(self.mixture_lower + self.mixture_upper - 1.0) > 1e-12:
            raise ValueError("mixture bounds must be symmetric around 0.5")
        for name in (
            "attack_reliability_constant",
            "defense_reliability_constant",
            "bootstrap_se_shrinkage_constant",
            "opposition_exposure_scale",
        ):
            if not np.isfinite(getattr(self, name)) or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if not np.isfinite(self.prevention_weight) or self.prevention_weight < 0:
            raise ValueError("prevention_weight must be finite and nonnegative")
        if self.bootstrap_replicates < 2:
            raise ValueError("bootstrap_replicates must be at least two")


def reject_identity_scoring_columns(columns: Sequence[str]) -> None:
    """Raise when an identity, outcome target, or desired-rank field scores."""

    lowered = {str(column).strip().lower() for column in columns}
    forbidden = IDENTITY_OR_TARGET_FIELDS.intersection(lowered)
    suspicious = {
        column
        for column in lowered
        if any(
            token in column
            for token in (
                "player_name",
                "team_name",
                "nationality",
                "award",
                "target_rank",
                "desired_rank",
                "round_reached",
                "advancement",
                "winner_bonus",
            )
        )
    }
    if forbidden or suspicious:
        raise ValueError(
            "identity/target fields are prohibited from scoring: "
            f"{sorted(forbidden | suspicious)}"
        )


def _robust_standardize(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    median = float(numeric.median())
    mad = float((numeric - median).abs().median())
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = float(numeric.std(ddof=0))
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = 1.0
    return ((numeric.fillna(median) - median) / scale).clip(-6.0, 6.0)


def _log_action_signal(frame: pd.DataFrame, terms: Mapping[str, float]) -> pd.Series:
    total = pd.Series(0.0, index=frame.index, dtype=float)
    for column, weight in terms.items():
        if column not in frame:
            continue
        total = total + weight * pd.to_numeric(
            frame[column], errors="coerce"
        ).fillna(0.0).clip(lower=0.0)
    return _robust_standardize(np.log1p(total))


def continuous_role_mixture(
    frame: pd.DataFrame,
    *,
    lower: float = 0.25,
    upper: float = 0.75,
) -> pd.DataFrame:
    """Derive continuous channel weights from role vectors and action shares.

    Position labels are not inputs.  Probabilistic role-vector components are
    assigned empirical orientation anchors from the same identity-free action
    signal, then blended with the player's continuous action orientation.
    There is no discrete bucketing, within-pool min-max transform, or
    percentile saturation.
    """

    if not 0.0 < lower < upper < 1.0:
        raise ValueError("continuous mixture bounds must be inside (0, 1)")
    if abs(lower + upper - 1.0) > 1e-12:
        raise ValueError("continuous mixture bounds must sum to one")
    attack_signal = _log_action_signal(
        frame,
        {
            "shots": 1.0,
            "key_passes": 0.60,
            "progressive_carries": 0.25,
            "progressive_passes": 0.15,
            "final_third_passes": 0.10,
            "box_passes": 0.20,
        },
    )
    defense_signal = _log_action_signal(
        frame,
        {
            "interceptions": 1.0,
            "blocks": 1.0,
            "clearances": 1.0,
            "pressures": 0.25,
            "recoveries": 0.40,
            "duels_won": 0.30,
            "aerial_wins": 0.20,
        },
    )
    location = (
        _robust_standardize(frame["average_x"])
        if "average_x" in frame
        else pd.Series(0.0, index=frame.index)
    )
    action_logit = 0.75 * (attack_signal - defense_signal) + 0.35 * location
    action_orientation = pd.Series(expit(action_logit), index=frame.index)

    probability_columns = sorted(
        column
        for column in frame.columns
        if column.startswith(ROLE_PROBABILITY_PREFIX)
        and pd.to_numeric(frame[column], errors="coerce").notna().any()
    )
    if probability_columns:
        probabilities = (
            frame[probability_columns]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0.0)
            .clip(lower=0.0)
        )
        row_sum = probabilities.sum(axis=1)
        available = row_sum.gt(0.0)
        probabilities = probabilities.div(row_sum.where(available, 1.0), axis=0)
        denominator = probabilities.sum(axis=0).replace(0.0, np.nan)
        anchors = probabilities.mul(action_orientation, axis=0).sum(
            axis=0
        ).div(denominator).fillna(0.5)
        vector_orientation = probabilities.mul(anchors, axis=1).sum(axis=1)
        vector_orientation = vector_orientation.where(
            available, action_orientation
        )
        orientation = 0.55 * vector_orientation + 0.45 * action_orientation
        source = np.where(
            available,
            "continuous-role-vector-plus-action-shares",
            "continuous-action-shares",
        )
    else:
        orientation = action_orientation
        source = np.full(len(frame), "continuous-action-shares", dtype=object)
    orientation = pd.to_numeric(orientation, errors="raise").clip(0.0, 1.0)
    attacking_weight = lower + (upper - lower) * orientation
    defending_weight = 1.0 - attacking_weight
    if not np.allclose(
        attacking_weight + defending_weight, 1.0, rtol=0.0, atol=1e-12
    ):
        raise RuntimeError("continuous channel weights do not sum to one")
    return pd.DataFrame(
        {
            "role_orientation_attacking_v4": orientation,
            "attacking_channel_weight_v4": attacking_weight,
            "defending_channel_weight_v4": defending_weight,
            "role_mixture_source_v4": source,
        },
        index=frame.index,
    )


def channel_count_reliability(
    evidence: pd.Series | np.ndarray,
    constant: float,
) -> np.ndarray:
    values = np.asarray(evidence, dtype=float)
    if constant <= 0:
        raise ValueError("reliability constant must be positive")
    if np.any(~np.isfinite(values)) or np.any(values < 0):
        raise ValueError("reliability evidence must be finite and nonnegative")
    return values / (values + constant)


def bootstrap_se_shrinkage(
    values: pd.Series | np.ndarray,
    bootstrap_se: pd.Series | np.ndarray,
    evidence_reliability: pd.Series | np.ndarray,
    *,
    se_constant: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Shrink adjusted defense to its mean using evidence and bootstrap SE."""

    signal = np.asarray(values, dtype=float)
    se = np.asarray(bootstrap_se, dtype=float)
    count_rel = np.asarray(evidence_reliability, dtype=float)
    if signal.shape != se.shape or signal.shape != count_rel.shape:
        raise ValueError("shrinkage inputs must have identical shape")
    if (
        np.any(~np.isfinite(signal))
        or np.any(~np.isfinite(se))
        or np.any(se < 0)
        or np.any(~np.isfinite(count_rel))
        or np.any((count_rel < 0) | (count_rel > 1))
    ):
        raise ValueError("invalid bootstrap-SE shrinkage input")
    if se_constant <= 0:
        raise ValueError("se_constant must be positive")
    center = float(signal.mean())
    between = float(np.var(signal, ddof=0))
    if between <= 1e-15:
        se_rel = np.ones_like(signal)
    else:
        se_rel = between / (between + se_constant * np.square(se))
    reliability = np.clip(count_rel * se_rel, 0.0, 1.0)
    shrunk = center + reliability * (signal - center)
    return shrunk, reliability


@dataclass
class DefensivePipeline:
    """State machine that makes the mandatory stage order executable."""

    raw_values: np.ndarray
    _values: np.ndarray = field(init=False, repr=False)
    _cursor: int = field(default=0, init=False, repr=False)
    stage_history: list[str] = field(default_factory=list, init=False)
    metadata: dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        values = np.asarray(self.raw_values, dtype=float)
        if values.ndim != 1 or np.any(~np.isfinite(values)):
            raise ValueError("raw defensive values must be a finite vector")
        self._values = values.copy()

    @property
    def values(self) -> np.ndarray:
        return self._values.copy()

    def _advance(self, stage: str, values: np.ndarray) -> None:
        expected = REQUIRED_DEFENSIVE_PIPELINE_STAGES[self._cursor]
        if stage != expected:
            raise RuntimeError(
                f"defensive pipeline expected {expected!r}, got {stage!r}"
            )
        candidate = np.asarray(values, dtype=float)
        if candidate.shape != self._values.shape or np.any(
            ~np.isfinite(candidate)
        ):
            raise ValueError(f"{stage} output must be a finite matching vector")
        self._values = candidate.copy()
        self.stage_history.append(stage)
        self._cursor += 1

    def opposition_adjust(self, adjusted: Sequence[float]) -> "DefensivePipeline":
        self._advance("opposition_adjusted", np.asarray(adjusted, dtype=float))
        return self

    def augment_prevention(
        self, prevention_augmented: Sequence[float]
    ) -> "DefensivePipeline":
        self._advance(
            "prevention_augmented",
            np.asarray(prevention_augmented, dtype=float),
        )
        return self

    def shrink_reliability(
        self, reliability_shrunk: Sequence[float]
    ) -> "DefensivePipeline":
        self._advance(
            "reliability_shrunk",
            np.asarray(reliability_shrunk, dtype=float),
        )
        return self

    def variance_rescale(
        self,
        attacking_channel: Sequence[float],
        attacking_weight: Sequence[float],
        defending_weight: Sequence[float],
        *,
        target_share: float,
    ) -> "DefensivePipeline":
        attack = np.asarray(attacking_channel, dtype=float)
        w_att = np.asarray(attacking_weight, dtype=float)
        w_def = np.asarray(defending_weight, dtype=float)
        if not (
            attack.shape == w_att.shape == w_def.shape == self._values.shape
        ):
            raise ValueError("variance rescaling inputs must have equal shape")
        if not 0.35 <= target_share <= 0.50:
            raise ValueError("target defensive variance share must be [0.35, .50]")
        centered = self._values - float(self._values.mean())
        attack_var = float(np.var(w_att * attack, ddof=0))
        defense_var = float(np.var(w_def * centered, ddof=0))
        if attack_var <= 0 or defense_var <= 0:
            raise ValueError("both weighted channels need positive variance")
        factor = float(
            np.sqrt(
                target_share
                / (1.0 - target_share)
                * attack_var
                / defense_var
            )
        )
        scaled = centered * factor
        realized_defense = float(np.var(w_def * scaled, ddof=0))
        share = realized_defense / (attack_var + realized_defense)
        if share > 0.500000000001 or abs(share - target_share) > 1e-10:
            raise RuntimeError("defensive channel violated variance-share contract")
        self.metadata.update(
            {
                "defensive_variance_scale_factor_v4": factor,
                "defensive_variance_share_v4": share,
            }
        )
        self._advance("variance_rescaled", scaled)
        return self

    def mixture_weight(self, defending_weight: Sequence[float]) -> "DefensivePipeline":
        weight = np.asarray(defending_weight, dtype=float)
        if weight.shape != self._values.shape:
            raise ValueError("defending mixture weight has wrong shape")
        self._advance("mixture_weighted", weight * self._values)
        return self

    def assert_complete(self) -> None:
        if tuple(self.stage_history) != REQUIRED_DEFENSIVE_PIPELINE_STAGES:
            raise RuntimeError(
                "defensive pipeline incomplete or out of order: "
                f"{self.stage_history}"
            )


def variance_balanced_composite(
    frame: pd.DataFrame,
    *,
    defensive_input_column: str,
    attacking_input_column: str = "attacking_component_reliable_v4",
    attacking_weight_column: str = "attacking_channel_weight_v4",
    defending_weight_column: str = "defending_channel_weight_v4",
    defensive_pipeline_stages: Sequence[str],
) -> pd.Series:
    """Combine only the released, post-adjustment defensive representation."""

    required_name = "defensive_value_opposition_adjusted_v4"
    if defensive_input_column != required_name:
        raise ValueError(
            "composite accepts only defensive_value_opposition_adjusted_v4 "
            "after prevention and reliability shrinkage; raw defense is rejected"
        )
    if tuple(defensive_pipeline_stages) != REQUIRED_DEFENSIVE_PIPELINE_STAGES:
        raise ValueError("defensive pipeline stages are missing or out of order")
    required = {
        defensive_input_column,
        attacking_input_column,
        attacking_weight_column,
        defending_weight_column,
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"composite input is missing: {sorted(missing)}")
    reject_identity_scoring_columns(required)
    attack = pd.to_numeric(
        frame[attacking_input_column], errors="raise"
    ).to_numpy(dtype=float)
    defense_weighted = pd.to_numeric(
        frame[defensive_input_column], errors="raise"
    ).to_numpy(dtype=float)
    w_att = pd.to_numeric(
        frame[attacking_weight_column], errors="raise"
    ).to_numpy(dtype=float)
    w_def = pd.to_numeric(
        frame[defending_weight_column], errors="raise"
    ).to_numpy(dtype=float)
    if not np.allclose(w_att + w_def, 1.0, rtol=0.0, atol=1e-12):
        raise ValueError("channel weights must sum to one")
    # Defense is already mixture-weighted by DefensivePipeline.  Attack is
    # weighted here to keep the public composite incapable of rescaling raw
    # or unadjusted defensive values.
    score = w_att * attack + defense_weighted
    if np.any(~np.isfinite(score)):
        raise ValueError("composite contains non-finite scores")
    return pd.Series(score, index=frame.index, dtype=float)


def add_reporting_ranks(frame: pd.DataFrame) -> pd.DataFrame:
    """Add deterministic global, position, and sub-role ranks."""

    required = {
        "player_id",
        "position_group",
        "role_orientation_attacking_v4",
        "tournament_impact_score_outfield_v4",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"ranking input is missing: {sorted(missing)}")
    output = frame.copy()
    score = pd.to_numeric(
        output["tournament_impact_score_outfield_v4"], errors="raise"
    )
    order = output.assign(_score=score).sort_values(
        ["_score", "player_id"],
        ascending=[False, True],
        kind="mergesort",
    )
    rank = pd.Series(
        np.arange(1, len(order) + 1), index=order.index, dtype="Int64"
    )
    output["tournament_impact_rank_outfield_v4"] = rank.reindex(output.index)
    output["within_position_rank_outfield_v4"] = (
        output.groupby("position_group", dropna=False, sort=False)[
            "tournament_impact_score_outfield_v4"
        ]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )

    def _subrole(group: pd.DataFrame) -> pd.Series:
        orientation = pd.to_numeric(
            group["role_orientation_attacking_v4"], errors="raise"
        )
        percentile = orientation.rank(
            method="average", pct=True, ascending=True
        )
        return pd.Series(
            np.select(
                [percentile.le(1.0 / 3.0), percentile.gt(2.0 / 3.0)],
                ["defensive", "offensive"],
                default="hybrid",
            ),
            index=group.index,
        )

    subroles = pd.Series(index=output.index, dtype="object")
    for _, group in output.groupby(
        "position_group", dropna=False, sort=False
    ):
        subroles.loc[group.index] = _subrole(group)
    output["predominant_position_subrole_v4"] = subroles
    output["within_subrole_rank_outfield_v4"] = (
        output.groupby(
            ["position_group", "predominant_position_subrole_v4"],
            dropna=False,
            sort=False,
        )["tournament_impact_score_outfield_v4"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    return output
