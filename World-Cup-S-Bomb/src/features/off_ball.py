"""Coverage-aware off-ball contribution scoring."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


ATTACKING_FEATURES = (
    "dangerous_zone_receptions_p90",
    "progressive_receptions_p90",
    "movement_into_available_space_rate",
    "final_third_occupancy",
    "half_space_share",
    "mean_space_received",
    "mean_passing_lane_availability",
    "build_up_involvement_ratio",
)

DEFENSIVE_FEATURES = (
    "pressures_p90",
    "counterpressures_p90",
    "post_pressure_recoveries_p90",
    "forced_rushed_action_rate",
    "defensive_positioning_score",
    "shape_maintenance_score",
)


class OffBallScorer(BaseEstimator, TransformerMixin):
    """Score observed attacking and defensive off-ball proxies.

    Public StatsBomb 360 does not identify non-actor players. Accordingly,
    every input here must be either a named event, named receipt, event-actor
    geometry, or a clearly labeled team-context proxy. Missing observations
    are excluded and low-coverage scores are shrunk toward position priors.
    """

    def __init__(self, *, prior_strength: float = 3.0) -> None:
        self.prior_strength = prior_strength

    def fit(
        self,
        X: pd.DataFrame,
        y: Any = None,
    ) -> "OffBallScorer":
        """Fit empirical CDFs and broad-position priors."""

        if "player_id" not in X:
            raise ValueError("OffBallScorer requires player_id")
        if self.prior_strength < 0:
            raise ValueError("prior_strength must be nonnegative")
        requested = set(ATTACKING_FEATURES + DEFENSIVE_FEATURES)
        self.references_: dict[str, np.ndarray] = {}
        for column in sorted(requested.intersection(X.columns)):
            values = pd.to_numeric(X[column], errors="coerce")
            observed = values[np.isfinite(values)].to_numpy(dtype=float)
            if len(observed):
                lower, upper = np.quantile(observed, [0.01, 0.99])
                self.references_[column] = np.sort(
                    np.clip(observed, lower, upper)
                )
        raw = self._raw_scores(X)
        groups = (
            X["position_group"].fillna("Unknown").astype(str)
            if "position_group" in X
            else pd.Series("Unknown", index=X.index)
        )
        self.global_prior_ = float(
            raw["off_ball_raw"].mean(skipna=True)
            if raw["off_ball_raw"].notna().any()
            else 0.5
        )
        prior_frame = pd.DataFrame(
            {
                "position_group": groups,
                "off_ball_raw": raw["off_ball_raw"],
            }
        )
        self.position_priors_ = (
            prior_frame.groupby("position_group")["off_ball_raw"]
            .mean()
            .fillna(self.global_prior_)
            .to_dict()
        )
        self.feature_names_in_ = tuple(str(column) for column in X.columns)
        return self

    def _percentile(self, series: pd.Series, column: str) -> pd.Series:
        values = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
        output = np.full(len(values), np.nan)
        observed = np.isfinite(values)
        reference = self.references_[column]
        clipped = np.clip(values[observed], reference[0], reference[-1])
        left = np.searchsorted(reference, clipped, side="left")
        right = np.searchsorted(reference, clipped, side="right")
        output[observed] = (left + right) / (2.0 * len(reference))
        return pd.Series(output, index=series.index, dtype=float)

    def _dimension(
        self,
        X: pd.DataFrame,
        columns: tuple[str, ...],
    ) -> tuple[pd.Series, pd.Series]:
        transformed = [
            self._percentile(X[column], column)
            for column in columns
            if column in X and column in self.references_
        ]
        if not transformed:
            return (
                pd.Series(np.nan, index=X.index, dtype=float),
                pd.Series(0, index=X.index, dtype=int),
            )
        matrix = pd.concat(transformed, axis=1)
        return matrix.mean(axis=1, skipna=True), matrix.notna().sum(axis=1)

    def _raw_scores(self, X: pd.DataFrame) -> pd.DataFrame:
        attacking, attacking_count = self._dimension(X, ATTACKING_FEATURES)
        defensive, defensive_count = self._dimension(X, DEFENSIVE_FEATURES)
        dimensions = pd.concat([attacking, defensive], axis=1)
        return pd.DataFrame(
            {
                "attacking_off_ball_score": attacking,
                "defensive_off_ball_score": defensive,
                "attacking_off_ball_evidence": attacking_count,
                "defensive_off_ball_evidence": defensive_count,
                "off_ball_raw": dimensions.mean(axis=1, skipna=True),
                "off_ball_evidence": attacking_count + defensive_count,
            },
            index=X.index,
        )

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return shrunk score, sub-scores, masks, and evidence coverage."""

        if not hasattr(self, "references_"):
            raise RuntimeError("OffBallScorer has not been fitted")
        raw = self._raw_scores(X)
        groups = (
            X["position_group"].fillna("Unknown").astype(str)
            if "position_group" in X
            else pd.Series("Unknown", index=X.index)
        )
        prior = groups.map(self.position_priors_).fillna(self.global_prior_)
        evidence = raw["off_ball_evidence"].astype(float)
        reliability = evidence / (evidence + self.prior_strength)
        observed = raw["off_ball_raw"].notna()
        raw_value = raw["off_ball_raw"].fillna(prior)
        score = reliability * raw_value + (1.0 - reliability) * prior
        result = pd.DataFrame(
            {
                "player_id": pd.to_numeric(
                    X["player_id"],
                    errors="raise",
                ).astype(int),
                **{column: raw[column] for column in raw.columns},
                "off_ball_score": score.clip(0.0, 1.0),
                "off_ball_score_observed": observed,
                "off_ball_reliability": reliability,
                "off_ball_feature_coverage": evidence
                / (len(ATTACKING_FEATURES) + len(DEFENSIVE_FEATURES)),
            },
            index=X.index,
        )
        return result.reset_index(drop=True)

