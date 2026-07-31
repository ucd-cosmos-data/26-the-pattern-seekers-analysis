"""Continuous role-aware contribution and composite player valuation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import RATING_WEIGHTS, RatingConfig
from src.features.role_vectors import derive_role_channel_weights


COMPLETENESS_DIMENSIONS = (
    "progression_score",
    "creation_score",
    "finishing_score",
    "pressing_score",
    "defensive_score",
    "ball_security_score",
)

ROLE_DIMENSIONS = (*COMPLETENESS_DIMENSIONS, "aerial_score")

DEFAULT_METRIC_DIRECTIONS: dict[str, bool] = {
    "progressive_carries_p90": True,
    "progressive_passes_p90": True,
    "line_breaking_pass_rate": True,
    "xt_p90": True,
    "key_passes_p90": True,
    "xa_p90": True,
    "shots_p90": True,
    "shots_on_target_rate": True,
    "xg_p90": True,
    "goals_p90": True,
    "pressures_p90": True,
    "counterpressures_p90": True,
    "post_pressure_recoveries_p90": True,
    "forced_rushed_action_rate": True,
    "vaep_def_p90": True,
    "interceptions_p90": True,
    "recoveries_p90": True,
    "duel_win_rate": True,
    "pass_completion": True,
    "pressure_resistance": True,
    "turnovers_p90": False,
    "aerial_dominance_index": True,
    "aerial_wins_p90": True,
    "network_betweenness": True,
    "build_up_involvement_ratio": True,
}

METRIC_ROLE_MAP: dict[str, str] = {
    "progressive_carries_p90": "progression_score",
    "progressive_passes_p90": "progression_score",
    "line_breaking_pass_rate": "progression_score",
    "xt_p90": "progression_score",
    "key_passes_p90": "creation_score",
    "xa_p90": "creation_score",
    "network_betweenness": "creation_score",
    "build_up_involvement_ratio": "creation_score",
    "shots_p90": "finishing_score",
    "shots_on_target_rate": "finishing_score",
    "xg_p90": "finishing_score",
    "goals_p90": "finishing_score",
    "pressures_p90": "pressing_score",
    "counterpressures_p90": "pressing_score",
    "post_pressure_recoveries_p90": "pressing_score",
    "forced_rushed_action_rate": "pressing_score",
    "vaep_def_p90": "defensive_score",
    "interceptions_p90": "defensive_score",
    "recoveries_p90": "defensive_score",
    "duel_win_rate": "defensive_score",
    "pass_completion": "ball_security_score",
    "pressure_resistance": "ball_security_score",
    "turnovers_p90": "ball_security_score",
    "aerial_dominance_index": "aerial_score",
    "aerial_wins_p90": "aerial_score",
}


def calculate_completeness_score(
    role_vectors: pd.DataFrame,
    *,
    top_k: int = 3,
    epsilon: float = 1e-9,
    alpha: float = 0.6,
) -> pd.Series:
    """Calculate quality-adjusted balance over a player's strongest dimensions.

    Missing dimensions remain missing instead of being interpreted as zero.
    Multiplication by the top-dimension mean prevents uniformly mediocre
    profiles from receiving a perfect completeness score. Completeness is a
    bounded positive component and never suppresses specialist value.
    """

    missing = set(COMPLETENESS_DIMENSIONS).difference(role_vectors.columns)
    if missing:
        raise ValueError(f"Completeness dimensions missing: {sorted(missing)}")
    if not 2 <= top_k <= len(COMPLETENESS_DIMENSIONS):
        raise ValueError("top_k must be between 2 and the dimension count")
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("Completeness alpha must be in [0, 1]")
    values = role_vectors[list(COMPLETENESS_DIMENSIONS)].apply(
        pd.to_numeric,
        errors="coerce",
    )
    sufficient = values.notna().sum(axis=1).ge(top_k)
    ordered = np.sort(
        values.fillna(-np.inf).to_numpy(dtype=float),
        axis=1,
    )
    top = ordered[:, -top_k:]
    top[~np.isfinite(top)] = np.nan
    mean = pd.Series(np.nanmean(top, axis=1), index=values.index)
    deviation = pd.Series(np.nanstd(top, axis=1), index=values.index)
    variation = deviation / (mean + epsilon)
    balance = (1.0 - variation.clip(upper=1.0)).clip(0.0, 1.0)
    score = (mean.clip(0.0, 1.0) * balance).clip(0.0, 1.0)
    score.loc[~sufficient] = np.nan
    if "minutes" in role_vectors:
        minutes = pd.to_numeric(
            role_vectors["minutes"],
            errors="coerce",
        ).fillna(0.0)
        minute_factor = pd.Series(
            np.select(
                [
                    minutes.lt(90.0),
                    minutes.lt(180.0),
                    minutes.lt(300.0),
                ],
                [0.50, 0.75, 0.90],
                default=1.00,
            ),
            index=role_vectors.index,
            dtype=float,
        )
        score = alpha * score + (1.0 - alpha) * minute_factor
    return score.rename("completeness_score")


class IndependentValueScaler(BaseEstimator, TransformerMixin):
    """Scale offensive and defensive VAEP channels independently.

    Group-specific bounds are used only where the fitted sample is large
    enough. Every transform is clipped to fitted training bounds, so held-out
    observations cannot alter the reference distribution.
    """

    channels = {
        "vaep_off_p90": "vaep_off_scaled",
        "vaep_def_p90": "vaep_def_scaled",
    }

    def __init__(
        self,
        *,
        group_column: str = "position_group",
        minimum_group_size: int = 20,
        lower_quantile: float = 0.01,
        upper_quantile: float = 0.99,
    ) -> None:
        self.group_column = group_column
        self.minimum_group_size = minimum_group_size
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile

    @staticmethod
    def _bounds(values: pd.Series, lower: float, upper: float) -> tuple[float, float]:
        observed = pd.to_numeric(values, errors="coerce").dropna()
        if observed.empty:
            return (0.0, 1.0)
        low, high = observed.quantile([lower, upper]).to_numpy(dtype=float)
        if not np.isfinite(low) or not np.isfinite(high) or high <= low:
            high = low + 1.0
        return float(low), float(high)

    def fit(
        self,
        X: pd.DataFrame,
        y: Any = None,
    ) -> "IndependentValueScaler":
        """Fit global and optional position-specific winsorized ranges."""

        if self.minimum_group_size < 2:
            raise ValueError("minimum_group_size must be at least two")
        if not 0.0 <= self.lower_quantile < self.upper_quantile <= 1.0:
            raise ValueError("Invalid scaling quantiles")
        missing = set(self.channels).difference(X.columns)
        if missing:
            raise ValueError(f"VAEP channels missing: {sorted(missing)}")
        self.global_bounds_ = {
            channel: self._bounds(
                X[channel],
                self.lower_quantile,
                self.upper_quantile,
            )
            for channel in self.channels
        }
        self.group_bounds_: dict[str, dict[str, tuple[float, float]]] = {}
        if self.group_column in X:
            for group, rows in X.groupby(self.group_column, dropna=False):
                if len(rows) < self.minimum_group_size:
                    continue
                self.group_bounds_[str(group)] = {
                    channel: self._bounds(
                        rows[channel],
                        self.lower_quantile,
                        self.upper_quantile,
                    )
                    for channel in self.channels
                }
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform both VAEP channels to fitted [0, 1] scales."""

        if not hasattr(self, "global_bounds_"):
            raise RuntimeError("IndependentValueScaler is not fitted")
        output = pd.DataFrame(index=X.index)
        groups = (
            X[self.group_column].astype(str)
            if self.group_column in X
            else pd.Series("", index=X.index)
        )
        for channel, destination in self.channels.items():
            numeric = pd.to_numeric(X[channel], errors="coerce")
            scaled = pd.Series(np.nan, index=X.index, dtype=float)
            for group in groups.unique():
                mask = groups.eq(group)
                low, high = self.group_bounds_.get(
                    group,
                    self.global_bounds_,
                )[channel]
                clipped = numeric.loc[mask].clip(lower=low, upper=high)
                scaled.loc[mask] = (clipped - low) / (high - low)
            output[destination] = scaled.clip(0.0, 1.0)
        return output


@dataclass(frozen=True)
class ElasticNetFoldMetrics:
    """Leakage-safe grouped OOF regression diagnostics."""

    rmse: float
    mae: float
    correlation: float
    rows: int
    groups: int


class GroupedElasticNetValuator(BaseEstimator):
    """Positive ElasticNet with nested match-grouped model selection."""

    def __init__(
        self,
        *,
        feature_names: Sequence[str],
        outer_folds: int = 5,
        inner_folds: int = 4,
        alphas: Sequence[float] = (0.001, 0.01, 0.05, 0.1),
        l1_ratios: Sequence[float] = (0.2, 0.5, 0.8, 0.95),
        random_state: int = 42,
    ) -> None:
        self.feature_names = feature_names
        self.outer_folds = outer_folds
        self.inner_folds = inner_folds
        self.alphas = alphas
        self.l1_ratios = l1_ratios
        self.random_state = random_state

    def _pipeline(self, alpha: float, l1_ratio: float) -> Pipeline:
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "model",
                    ElasticNet(
                        alpha=alpha,
                        l1_ratio=l1_ratio,
                        positive=True,
                        max_iter=20_000,
                        random_state=self.random_state,
                    ),
                ),
            ]
        )

    @staticmethod
    def _splits(groups: np.ndarray, requested: int) -> GroupKFold:
        count = len(np.unique(groups))
        folds = min(requested, count)
        if folds < 2:
            raise ValueError("Grouped valuation requires at least two matches")
        return GroupKFold(n_splits=folds)

    def _select(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        groups: np.ndarray,
    ) -> tuple[float, float]:
        best: tuple[float, float] | None = None
        best_loss = np.inf
        splitter = self._splits(groups, self.inner_folds)
        for alpha in self.alphas:
            for l1_ratio in self.l1_ratios:
                losses: list[float] = []
                for train, validation in splitter.split(X, y, groups):
                    model = self._pipeline(float(alpha), float(l1_ratio))
                    model.fit(X.iloc[train], y[train])
                    prediction = model.predict(X.iloc[validation])
                    losses.append(
                        float(np.mean(np.square(prediction - y[validation])))
                    )
                loss = float(np.mean(losses))
                candidate = (float(alpha), float(l1_ratio))
                if loss < best_loss - 1e-12 or (
                    np.isclose(loss, best_loss)
                    and (best is None or candidate < best)
                ):
                    best_loss = loss
                    best = candidate
        if best is None:
            raise RuntimeError("ElasticNet parameter search produced no model")
        return best

    def fit(
        self,
        X: pd.DataFrame,
        y: Sequence[float],
        groups: Sequence[int],
    ) -> "GroupedElasticNetValuator":
        """Fit nested grouped OOF predictions and a final deployment model."""

        self.feature_names_ = tuple(self.feature_names)
        missing = set(self.feature_names_).difference(X.columns)
        if missing:
            raise ValueError(f"ElasticNet features missing: {sorted(missing)}")
        matrix = X.loc[:, self.feature_names_].reset_index(drop=True)
        target = np.asarray(y, dtype=float)
        match_groups = np.asarray(groups)
        if len(matrix) != len(target) or len(matrix) != len(match_groups):
            raise ValueError("Features, targets, and groups must align")
        valid = np.isfinite(target)
        matrix = matrix.loc[valid].reset_index(drop=True)
        target = target[valid]
        match_groups = match_groups[valid]
        outer = self._splits(match_groups, self.outer_folds)
        prediction = np.full(len(matrix), np.nan)
        self.fold_audit_: list[dict[str, Any]] = []
        self.fold_parameters_: list[dict[str, float]] = []
        for fold, (train, validation) in enumerate(
            outer.split(matrix, target, match_groups),
            start=1,
        ):
            alpha, l1_ratio = self._select(
                matrix.iloc[train],
                target[train],
                match_groups[train],
            )
            model = self._pipeline(alpha, l1_ratio)
            model.fit(matrix.iloc[train], target[train])
            prediction[validation] = model.predict(matrix.iloc[validation])
            train_groups = sorted(np.unique(match_groups[train]).tolist())
            validation_groups = sorted(
                np.unique(match_groups[validation]).tolist()
            )
            if set(train_groups).intersection(validation_groups):
                raise RuntimeError("Match leakage detected in grouped valuation")
            self.fold_audit_.append(
                {
                    "fold": fold,
                    "train_groups": train_groups,
                    "validation_groups": validation_groups,
                    "train_rows": int(len(train)),
                    "validation_rows": int(len(validation)),
                }
            )
            self.fold_parameters_.append(
                {"alpha": alpha, "l1_ratio": l1_ratio}
            )
        if not np.isfinite(prediction).all():
            raise RuntimeError("Grouped OOF prediction is incomplete")
        self.oof_prediction_ = prediction
        self.oof_target_ = target
        error = prediction - target
        correlation = float(pd.Series(prediction).corr(pd.Series(target)))
        self.metrics_ = ElasticNetFoldMetrics(
            rmse=float(np.sqrt(np.mean(np.square(error)))),
            mae=float(np.mean(np.abs(error))),
            correlation=correlation,
            rows=int(len(target)),
            groups=int(len(np.unique(match_groups))),
        )
        alpha, l1_ratio = self._select(matrix, target, match_groups)
        self.best_alpha_ = alpha
        self.best_l1_ratio_ = l1_ratio
        self.model_ = self._pipeline(alpha, l1_ratio).fit(matrix, target)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict bounded contribution value with the final fitted model."""

        if not hasattr(self, "model_"):
            raise RuntimeError("GroupedElasticNetValuator is not fitted")
        values = self.model_.predict(X.loc[:, self.feature_names_])
        return np.clip(values, 0.0, 1.0)

    def coefficient_series(self) -> pd.Series:
        """Return deployment coefficients on the standardized feature space."""

        if not hasattr(self, "model_"):
            raise RuntimeError("GroupedElasticNetValuator is not fitted")
        estimator = self.model_.named_steps["model"]
        return pd.Series(
            estimator.coef_,
            index=self.feature_names_,
            name="elastic_net_coefficient",
        )


class ContributionMetricTransformer(BaseEstimator, TransformerMixin):
    """Convert contribution metrics to benefit-oriented training percentiles."""

    def __init__(
        self,
        *,
        metric_directions: Mapping[str, bool] | None = None,
    ) -> None:
        self.metric_directions = metric_directions

    def fit(
        self,
        X: pd.DataFrame,
        y: Any = None,
    ) -> "ContributionMetricTransformer":
        """Fit empirical CDFs on the training partition."""

        directions = dict(
            self.metric_directions or DEFAULT_METRIC_DIRECTIONS
        )
        self.metric_names_ = [
            metric for metric in directions if metric in X
        ]
        if not self.metric_names_:
            raise ValueError("No role-adjusted contribution metrics available")
        self.directions_ = {
            metric: directions[metric] for metric in self.metric_names_
        }
        self.references_: dict[str, np.ndarray] = {}
        for metric in self.metric_names_:
            values = pd.to_numeric(X[metric], errors="coerce")
            observed = values[np.isfinite(values)].to_numpy(dtype=float)
            if not len(observed):
                continue
            lower, upper = np.quantile(observed, [0.01, 0.99])
            self.references_[metric] = np.sort(
                np.clip(observed, lower, upper)
            )
        self.metric_names_ = [
            metric for metric in self.metric_names_
            if metric in self.references_
        ]
        if not self.metric_names_:
            raise ValueError("All contribution metrics are missing")
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return [0, 1] metrics while preserving missing observations."""

        if not hasattr(self, "references_"):
            raise RuntimeError("ContributionMetricTransformer is not fitted")
        output = pd.DataFrame(index=X.index)
        for metric in self.metric_names_:
            values = pd.to_numeric(X[metric], errors="coerce").to_numpy(
                dtype=float
            )
            transformed = np.full(len(values), np.nan)
            observed = np.isfinite(values)
            reference = self.references_[metric]
            clipped = np.clip(values[observed], reference[0], reference[-1])
            left = np.searchsorted(reference, clipped, side="left")
            right = np.searchsorted(reference, clipped, side="right")
            percentile = (left + right) / (2.0 * len(reference))
            if not self.directions_[metric]:
                percentile = 1.0 - percentile
            transformed[observed] = percentile
            output[metric] = transformed
        return output


class ContinuousRoleAwareValuator(BaseEstimator):
    """Learn continuous role-conditioned metric weights.

    The contribution metrics create value; the role vector only changes their
    relative weights. Softmax weights are nonnegative, continuous in the role
    vector, and sum to one for every player.
    """

    def __init__(
        self,
        *,
        metric_names: Sequence[str] | None = None,
        role_dimensions: Sequence[str] = ROLE_DIMENSIONS,
        alignment_strength: float = 2.5,
        l2_penalty: float = 5.0,
        maximum_iterations: int = 500,
    ) -> None:
        self.metric_names = metric_names
        self.role_dimensions = role_dimensions
        self.alignment_strength = alignment_strength
        self.l2_penalty = l2_penalty
        self.maximum_iterations = maximum_iterations

    def _initial_parameters(self) -> np.ndarray:
        metric_count = len(self.metric_names_)
        role_count = len(self.role_dimensions_)
        if self.alignment_strength < 0:
            raise ValueError("alignment_strength must be nonnegative")
        coefficients = np.zeros((metric_count, role_count + 1))
        role_index = {
            role: index for index, role in enumerate(self.role_dimensions_)
        }
        for metric_index, metric in enumerate(self.metric_names_):
            aligned = METRIC_ROLE_MAP.get(metric)
            if aligned in role_index:
                coefficients[
                    metric_index,
                    role_index[aligned] + 1,
                ] = self.alignment_strength
        return coefficients

    @staticmethod
    def _weights(
        metrics: np.ndarray,
        roles: np.ndarray,
        coefficients: np.ndarray,
    ) -> np.ndarray:
        design = np.column_stack([np.ones(len(roles)), roles])
        logits = design.dot(coefficients.T)
        observed = np.isfinite(metrics)
        logits = np.where(observed, logits, -np.inf)
        maximum = np.max(logits, axis=1, keepdims=True)
        maximum[~np.isfinite(maximum)] = 0.0
        exponent = np.where(observed, np.exp(logits - maximum), 0.0)
        denominator = exponent.sum(axis=1, keepdims=True)
        return np.divide(
            exponent,
            denominator,
            out=np.zeros_like(exponent),
            where=denominator > 0,
        )

    def fit(
        self,
        X: pd.DataFrame,
        y: Sequence[float] | None = None,
    ) -> "ContinuousRoleAwareValuator":
        """Fit optional regularized weights or retain monotonic aligned priors."""

        requested_metrics = list(
            self.metric_names or DEFAULT_METRIC_DIRECTIONS
        )
        self.metric_names_ = [
            metric for metric in requested_metrics if metric in X
        ]
        self.role_dimensions_ = [
            role for role in self.role_dimensions if role in X
        ]
        if not self.metric_names_ or len(self.role_dimensions_) < 1:
            raise ValueError("Role-aware valuation inputs are incomplete")
        metrics = X[self.metric_names_].to_numpy(dtype=float)
        roles = X[self.role_dimensions_].to_numpy(dtype=float)
        if not np.isfinite(roles).all():
            raise ValueError("Role dimensions must be observed before valuation")
        initial = self._initial_parameters()
        self.optimization_result_ = None
        if y is not None:
            target = np.asarray(y, dtype=float)
            valid = np.isfinite(target) & np.isfinite(metrics).any(axis=1)
            if valid.sum() < max(20, len(self.metric_names_) + 1):
                raise ValueError("Too few valid rows to learn valuation weights")

            def objective(flat: np.ndarray) -> float:
                coefficients = flat.reshape(initial.shape)
                weights = self._weights(
                    metrics[valid],
                    roles[valid],
                    coefficients,
                )
                filled = np.nan_to_num(metrics[valid], nan=0.0)
                prediction = np.sum(weights * filled, axis=1)
                error = np.mean(np.square(prediction - target[valid]))
                penalty = self.l2_penalty * np.mean(
                    np.square(coefficients - initial)
                )
                return float(error + penalty)

            result = minimize(
                objective,
                initial.ravel(),
                method="L-BFGS-B",
                options={"maxiter": self.maximum_iterations},
            )
            self.optimization_result_ = result
            self.coefficients_ = result.x.reshape(initial.shape)
        else:
            self.coefficients_ = initial
        return self

    def metric_weights(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return continuous player-specific metric weights."""

        if not hasattr(self, "coefficients_"):
            raise RuntimeError("ContinuousRoleAwareValuator is not fitted")
        metrics = X[self.metric_names_].to_numpy(dtype=float)
        roles = X[self.role_dimensions_].to_numpy(dtype=float)
        weights = self._weights(metrics, roles, self.coefficients_)
        return pd.DataFrame(
            weights,
            index=X.index,
            columns=[f"weight_{metric}" for metric in self.metric_names_],
        )

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Calculate role-adjusted contribution values in [0, 1]."""

        weights = self.metric_weights(X).to_numpy(dtype=float)
        metrics = X[self.metric_names_].to_numpy(dtype=float)
        prediction = np.sum(weights * np.nan_to_num(metrics, nan=0.0), axis=1)
        no_evidence = ~np.isfinite(metrics).any(axis=1)
        prediction[no_evidence] = np.nan
        return np.clip(prediction, 0.0, 1.0)


def calculate_role_adjusted_value(
    contribution_metrics: pd.DataFrame,
    role_vectors: pd.DataFrame,
    *,
    target: Sequence[float] | None = None,
    metric_transformer: ContributionMetricTransformer | None = None,
    valuator: ContinuousRoleAwareValuator | None = None,
) -> tuple[pd.Series, ContributionMetricTransformer, ContinuousRoleAwareValuator]:
    """Calculate role-aware value and return fitted reusable components."""

    transformer = metric_transformer or ContributionMetricTransformer().fit(
        contribution_metrics
    )
    metrics = transformer.transform(contribution_metrics)
    combined = pd.concat(
        [
            metrics.reset_index(drop=True),
            role_vectors[list(ROLE_DIMENSIONS)].reset_index(drop=True),
        ],
        axis=1,
    )
    model = valuator or ContinuousRoleAwareValuator(
        metric_names=list(metrics.columns)
    ).fit(combined, target)
    values = pd.Series(
        model.predict(combined),
        index=contribution_metrics.index,
        name="role_adjusted_value",
    )
    return values, transformer, model


def _training_percentile(series: pd.Series) -> pd.Series:
    """Return a deterministic robust tournament percentile."""

    values = pd.to_numeric(series, errors="coerce")
    observed = values[np.isfinite(values)]
    if observed.empty:
        return pd.Series(np.nan, index=series.index)
    lower, upper = observed.quantile([0.01, 0.99])
    return values.clip(lower=lower, upper=upper).rank(
        pct=True,
        method="average",
    )


def calculate_final_player_rating(
    profiles: pd.DataFrame,
    *,
    config: RatingConfig | None = None,
) -> pd.DataFrame:
    """Apply the configured composite and broad-position shrinkage."""

    settings = config or RatingConfig()
    required = {
        "player_id",
        "team",
        "position_group",
        "minutes",
        "vaep_total_p90",
        "vaep_per_touch",
        "xt_p90",
        "role_adjusted_value",
        "completeness_score",
        "off_ball_score",
    }
    missing = required.difference(profiles.columns)
    if missing:
        raise ValueError(f"Rating inputs missing: {sorted(missing)}")
    output = profiles.copy()
    if (
        "raw_final_player_rating" in output
        and "legacy_raw_final_player_rating" not in output
    ):
        output["legacy_raw_final_player_rating"] = output[
            "raw_final_player_rating"
        ]
    if (
        "final_player_rating" in output
        and "legacy_final_player_rating" not in output
    ):
        output["legacy_final_player_rating"] = output["final_player_rating"]
    if "team_rank" in output:
        output["legacy_team_rank"] = output["team_rank"]

    if {"vaep_off_p90", "vaep_def_p90"} <= set(output):
        stable_channels = output[
            [
                "position_group",
                "vaep_off_p90",
                "vaep_def_p90",
            ]
        ].copy()
        channel_reliability = (
            pd.to_numeric(output["minutes"], errors="coerce")
            .fillna(0.0)
            .clip(lower=0.0)
        )
        channel_reliability = channel_reliability / (
            channel_reliability + 450.0
        )
        for channel in ("vaep_off_p90", "vaep_def_p90"):
            values = pd.to_numeric(
                stable_channels[channel],
                errors="coerce",
            )
            position_prior = values.groupby(
                stable_channels["position_group"]
            ).transform("mean")
            stable_channels[channel] = (
                channel_reliability * values
                + (1.0 - channel_reliability) * position_prior
            )
        value_channels = IndependentValueScaler(
            minimum_group_size=12,
        ).fit_transform(stable_channels)
        output[value_channels.columns] = value_channels
        channel_weights = derive_role_channel_weights(output)
        output[channel_weights.columns] = channel_weights
        vaep_value = (
            channel_weights["role_off_weight"]
            * value_channels["vaep_off_scaled"]
            + channel_weights["role_def_weight"]
            * value_channels["vaep_def_scaled"]
        )
        output["vaep_component"] = vaep_value
    else:
        vaep_value = _training_percentile(output["vaep_total_p90"])

    components = pd.DataFrame(
        {
            "vaep_90": vaep_value,
            "vaep_per_touch": _training_percentile(output["vaep_per_touch"]),
            "xt_90": _training_percentile(output["xt_p90"]),
            "role_adjusted_value": pd.to_numeric(
                output["role_adjusted_value"],
                errors="coerce",
            ),
            "completeness_score": pd.to_numeric(
                output["completeness_score"],
                errors="coerce",
            ),
            "off_ball_score": pd.to_numeric(
                output["off_ball_score"],
                errors="coerce",
            ),
        },
        index=output.index,
    )
    for component in components:
        output[f"{component}_missing"] = components[component].isna()
        prior = components.groupby(output["position_group"])[component].transform(
            "mean"
        )
        components[component] = components[component].fillna(prior)
        components[component] = components[component].fillna(
            components[component].mean()
        )
    output["raw_final_player_rating"] = sum(
        settings.weights[column] * components[column]
        for column in RATING_WEIGHTS
    )
    minutes = pd.to_numeric(output["minutes"], errors="coerce").clip(lower=0.0)
    reliability = minutes / (minutes + settings.reliability_minutes)
    position_prior = output.groupby("position_group")[
        "raw_final_player_rating"
    ].transform("mean")
    output["rating_minutes_reliability"] = reliability
    output["final_player_rating"] = (
        reliability * output["raw_final_player_rating"]
        + (1.0 - reliability) * position_prior
    )
    output["global_rank"] = output["final_player_rating"].rank(
        method="min",
        ascending=False,
    ).astype(int)
    output["position_rank"] = output.groupby("position_group")[
        "final_player_rating"
    ].rank(method="min", ascending=False).astype(int)
    role_column = (
        "probabilistic_role"
        if "probabilistic_role" in output
        else "functional_role"
    )
    if role_column in output:
        output["role_rank"] = output.groupby(role_column)[
            "final_player_rating"
        ].rank(method="min", ascending=False).astype(int)
    else:
        output["role_rank"] = output["global_rank"]
    output["team_rank"] = output.groupby("team")[
        "final_player_rating"
    ].rank(method="min", ascending=False).astype(int)
    output["player_evaluation_score"] = output["final_player_rating"]
    output["RankingStatus"] = np.select(
        [
            minutes.ge(300.0),
            minutes.ge(180.0),
        ],
        [
            "Ranked (300+ min)",
            "Ranked (180–299 min)",
        ],
        default="Coverage only (<180 min)",
    )
    output["primary_global_rank"] = pd.Series(
        pd.NA,
        index=output.index,
        dtype="Int64",
    )
    primary = minutes.ge(300.0)
    output.loc[primary, "primary_global_rank"] = (
        output.loc[primary, "final_player_rating"]
        .rank(method="min", ascending=False)
        .astype(int)
    )
    return output
