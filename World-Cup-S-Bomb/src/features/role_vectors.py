"""Continuous, evidence-aware player role vectors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


@dataclass(frozen=True)
class RoleInput:
    """One observable contributing to a role dimension."""

    column: str
    higher_is_better: bool = True


ROLE_DIMENSIONS: dict[str, tuple[RoleInput, ...]] = {
    "progression_score": (
        RoleInput("progressive_carries_p90"),
        RoleInput("progressive_passes_p90"),
        RoleInput("line_breaking_pass_rate"),
        RoleInput("progressive_receptions_p90"),
        RoleInput("packing_index_mean"),
        RoleInput("xt_p90"),
        RoleInput("build_up_involvement_ratio"),
    ),
    "creation_score": (
        RoleInput("key_passes_p90"),
        RoleInput("xa_p90"),
        RoleInput("xt_creation_p90"),
        RoleInput("line_breaking_pass_rate"),
        RoleInput("box_passes_p90"),
        RoleInput("network_betweenness"),
    ),
    "finishing_score": (
        RoleInput("shots_p90"),
        RoleInput("shots_on_target_rate"),
        RoleInput("xg_p90"),
        RoleInput("goals_p90"),
    ),
    "pressing_score": (
        RoleInput("pressures_p90"),
        RoleInput("pressing_intensity_index"),
        RoleInput("successful_pressure_rate"),
        RoleInput("counterpressures_p90"),
        RoleInput("post_pressure_recoveries_p90"),
        RoleInput("forced_rushed_action_rate"),
    ),
    "defensive_score": (
        RoleInput("tackles_p90"),
        RoleInput("interceptions_p90"),
        RoleInput("recoveries_p90"),
        RoleInput("blocks_p90"),
        RoleInput("vaep_def_p90"),
        RoleInput("duel_win_rate"),
        RoleInput("xd90_pct"),
    ),
    "ball_security_score": (
        RoleInput("pass_completion"),
        RoleInput("distribution_under_pressure"),
        RoleInput("pressure_resistance"),
        RoleInput("turnovers_p90", higher_is_better=False),
        RoleInput("dispossessions_p90", higher_is_better=False),
        RoleInput("network_entropy"),
    ),
    "aerial_score": (
        RoleInput("aerial_dominance_index"),
        RoleInput("aerial_wins_p90"),
        RoleInput("aerial_events_p90"),
    ),
}

SPATIAL_DESCRIPTOR_ALIASES: dict[str, tuple[str, ...]] = {
    "average_receiving_x": ("pass_receipt_x", "average_receiving_x"),
    "average_receiving_y": ("pass_receipt_y", "average_receiving_y"),
    "average_passing_x": ("pass_start_x", "average_passing_x"),
    "average_passing_y": ("pass_start_y", "average_passing_y"),
    "final_third_involvement": (
        "final_third_share",
        "final_third_occupancy",
    ),
    "half_space_occupation": ("half_space_share",),
    "wide_corridor_occupation": ("wide_corridor_share",),
    "zone14_occupation": ("zone14_share",),
}


ROLE_CHANNEL_WEIGHTS: dict[str, tuple[float, float]] = {
    "Progressive Winger": (0.85, 0.15),
    "Target Forward": (0.85, 0.15),
    "Mobile Forward": (0.85, 0.15),
    "Attacking Wingback": (0.70, 0.30),
    "Wide Creator": (0.70, 0.30),
    "Hybrid Playmaker": (0.55, 0.45),
    "Roaming Creator": (0.55, 0.45),
    "Deep Playmaker": (0.55, 0.45),
    "Controlling Midfielder": (0.55, 0.45),
    "Box-to-Box Midfielder": (0.55, 0.45),
    "Ball-Winner": (0.35, 0.65),
    "Ball-Winning Midfielder": (0.35, 0.65),
    "Defensive Midfielder": (0.35, 0.65),
    "Centre-Back": (0.25, 0.75),
    "Center Back": (0.25, 0.75),
    "Fullback": (0.25, 0.75),
    "Defensive Centre-Back": (0.25, 0.75),
    "Ball-Playing Centre-Back": (0.25, 0.75),
    "Two-Way Fullback": (0.25, 0.75),
}

POSITION_CHANNEL_WEIGHTS: dict[str, tuple[float, float]] = {
    "Forward": (0.85, 0.15),
    "Attacking Midfield/Wing": (0.70, 0.30),
    "Central/Wide Midfield": (0.55, 0.45),
    "Defensive Midfield": (0.35, 0.65),
    "Fullback/Wingback": (0.25, 0.75),
    "Center Back": (0.25, 0.75),
}


def derive_role_channel_weights(profiles: pd.DataFrame) -> pd.DataFrame:
    """Return symmetric offense/defense weights from role evidence.

    The mapping is player-agnostic. Probabilistic roles take precedence,
    functional roles are the fallback, and broad position supplies a
    deterministic default when neither label is recognized.
    """

    role_columns = [
        column
        for column in ("probabilistic_role", "functional_role")
        if column in profiles
    ]
    weights: list[tuple[float, float]] = []
    sources: list[str] = []
    for _, row in profiles.iterrows():
        pair: tuple[float, float] | None = None
        source = "position_group"
        for column in role_columns:
            label = str(row.get(column, ""))
            if label in ROLE_CHANNEL_WEIGHTS:
                pair = ROLE_CHANNEL_WEIGHTS[label]
                source = column
                break
            lower = label.lower()
            if "centre-back" in lower or "center back" in lower:
                pair = (0.25, 0.75)
            elif "attacking wingback" in lower or "wide creator" in lower:
                pair = (0.70, 0.30)
            elif "winger" in lower or "forward" in lower:
                pair = (0.85, 0.15)
            elif "ball-winn" in lower or "defensive midfield" in lower:
                pair = (0.35, 0.65)
            elif (
                "playmaker" in lower
                or "creator" in lower
                or "box-to-box" in lower
                or "midfielder" in lower
            ):
                pair = (0.55, 0.45)
            elif "fullback" in lower:
                pair = (0.25, 0.75)
            if pair is not None:
                source = column
                break
        if pair is None:
            pair = POSITION_CHANNEL_WEIGHTS.get(
                str(row.get("position_group", "")),
                (0.50, 0.50),
            )
        weights.append(pair)
        sources.append(source)
    result = pd.DataFrame(
        weights,
        columns=["role_off_weight", "role_def_weight"],
        index=profiles.index,
        dtype=float,
    )
    result["role_weight_source"] = sources
    return result


class RoleVectorTransformer(BaseEstimator, TransformerMixin):
    """Build continuous role dimensions using fold-fitted empirical CDFs.

    Missing observables are excluded from a player's dimension rather than
    converted to zero. The accompanying evidence count and coverage columns
    allow downstream layers to shrink low-information estimates.
    """

    dimensions: ClassVar[dict[str, tuple[RoleInput, ...]]] = ROLE_DIMENSIONS

    def __init__(
        self,
        *,
        lower_quantile: float = 0.01,
        upper_quantile: float = 0.99,
    ) -> None:
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile

    def fit(
        self,
        X: pd.DataFrame,
        y: Any = None,
    ) -> "RoleVectorTransformer":
        """Fit winsor limits and empirical distributions on training rows."""

        if not 0.0 <= self.lower_quantile < self.upper_quantile <= 1.0:
            raise ValueError("Invalid role-vector quantile limits")
        requested = {
            item.column
            for inputs in self.dimensions.values()
            for item in inputs
        }
        self.reference_: dict[str, np.ndarray] = {}
        self.bounds_: dict[str, tuple[float, float]] = {}
        for column in sorted(requested.intersection(X.columns)):
            numeric = pd.to_numeric(X[column], errors="coerce")
            observed = numeric[np.isfinite(numeric)].to_numpy(dtype=float)
            if not len(observed):
                continue
            lower, upper = np.quantile(
                observed,
                [self.lower_quantile, self.upper_quantile],
            )
            clipped = np.clip(observed, lower, upper)
            self.bounds_[column] = (float(lower), float(upper))
            self.reference_[column] = np.sort(clipped)
        self.feature_names_in_ = tuple(str(column) for column in X.columns)
        return self

    def _percentile(
        self,
        series: pd.Series,
        column: str,
        *,
        higher_is_better: bool,
    ) -> pd.Series:
        """Transform observed values against a training empirical CDF."""

        values = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
        output: np.ndarray = np.full(len(values), np.nan, dtype=float)
        observed = np.isfinite(values)
        reference = self.reference_[column]
        lower, upper = self.bounds_[column]
        clipped = np.clip(values[observed], lower, upper)
        left = np.searchsorted(reference, clipped, side="left")
        right = np.searchsorted(reference, clipped, side="right")
        percentile = (left + right) / (2.0 * len(reference))
        if not higher_is_better:
            percentile = 1.0 - percentile
        output[observed] = np.clip(percentile, 0.0, 1.0)
        return pd.Series(output, index=series.index, dtype=float)

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return role scores, evidence counts, coverage, and descriptors."""

        if not hasattr(self, "reference_"):
            raise RuntimeError("RoleVectorTransformer has not been fitted")
        if "player_id" not in X:
            raise ValueError("Role-vector input requires player_id")
        result = pd.DataFrame(
            {"player_id": pd.to_numeric(X["player_id"], errors="raise").astype(int)},
            index=X.index,
        )
        for dimension, inputs in self.dimensions.items():
            transformed: list[pd.Series] = []
            for item in inputs:
                if item.column not in X or item.column not in self.reference_:
                    continue
                transformed.append(
                    self._percentile(
                        X[item.column],
                        item.column,
                        higher_is_better=item.higher_is_better,
                    )
                )
            if transformed:
                matrix = pd.concat(transformed, axis=1)
                result[dimension] = matrix.mean(axis=1, skipna=True)
                count = matrix.notna().sum(axis=1).astype(int)
            else:
                result[dimension] = np.nan
                count = pd.Series(0, index=X.index, dtype=int)
            result[f"{dimension}_evidence_count"] = count
            result[f"{dimension}_coverage"] = count / max(len(inputs), 1)

        for output, aliases in SPATIAL_DESCRIPTOR_ALIASES.items():
            source = next((name for name in aliases if name in X), None)
            result[output] = (
                pd.to_numeric(X[source], errors="coerce")
                if source is not None
                else np.nan
            )
            result[f"{output}_available"] = result[output].notna()
        return result.reset_index(drop=True)

    def get_feature_names_out(
        self,
        input_features: Any = None,
    ) -> np.ndarray:
        """Return deterministic output names for sklearn compatibility."""

        names: list[str] = ["player_id"]
        for dimension in self.dimensions:
            names.extend(
                [
                    dimension,
                    f"{dimension}_evidence_count",
                    f"{dimension}_coverage",
                ]
            )
        for descriptor in SPATIAL_DESCRIPTOR_ALIASES:
            names.extend([descriptor, f"{descriptor}_available"])
        return np.asarray(names, dtype=object)


def derive_role_vector(
    profiles: pd.DataFrame,
    *,
    transformer: RoleVectorTransformer | None = None,
) -> pd.DataFrame:
    """Create continuous role vectors from player contribution profiles.

    Args:
        profiles: One row per player with rates and spatial descriptors.
        transformer: Optional transformer fitted only on training data. When
            omitted, a descriptive tournament-wide transformer is fitted.

    Returns:
        Player identifiers, seven role dimensions, evidence metadata, and
        spatial descriptors.
    """

    fitted = transformer or RoleVectorTransformer().fit(profiles)
    return fitted.transform(profiles)
