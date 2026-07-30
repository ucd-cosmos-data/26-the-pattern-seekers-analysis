"""Qatar 2022 goalkeeper valuation with bounded shootout evidence.

The v3 goalkeeper branch deliberately remains separate from the outfield
common-unit impact model.  It has three explicit boundaries:

* continuous shot stopping is learned only from periods 1--4 and excludes
  every penalty;
* regular penalties and period-five shootouts are independent channels; and
* the only cross-position publication field is explicitly described as a
  percentile-equivalent placement, not measured absolute contribution.

No player name, player identifier, team identity, advancement stage, award, or
external ranking is used as a scoring feature.  Team is used only to select
one main goalkeeper per team.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ORDINARY_MATCH_PERIODS = frozenset({1, 2, 3, 4})
SHOOTOUT_PERIOD = 5

DEFAULT_CONTINUOUS_COMPONENT_WEIGHTS: dict[str, float] = {
    "continuous_shot_stopping": 0.40,
    "high_leverage_shot_stopping": 0.15,
    "cross_claim_control": 0.12,
    "sweeping": 0.10,
    "distribution_under_pressure": 0.10,
    "regular_penalty_performance": 0.13,
}

_COMPONENT_INPUTS: dict[str, tuple[str, ...]] = {
    "continuous_shot_stopping": ("goals_prevented_proxy_p90",),
    "high_leverage_shot_stopping": (
        "high_leverage_save_rate_shrunk",
        "high_leverage_save_pct",
    ),
    "cross_claim_control": ("cross_stopping_rate", "claims_p90"),
    "sweeping": ("sweeper_actions_p90",),
    "distribution_under_pressure": (
        "distribution_under_pressure",
    ),
}

_MATCH_RATE_COLUMNS = tuple(
    dict.fromkeys(
        column
        for inputs in _COMPONENT_INPUTS.values()
        for column in inputs
    )
)
_MATCH_COUNT_COLUMNS = (
    "actions",
    "regular_penalties_faced",
    "regular_penalties_saved",
    "shootout_penalties_faced",
    "shootout_penalties_saved",
)


@dataclass(frozen=True)
class GoalkeeperV3Config:
    """Deterministic goalkeeper scoring and validation settings."""

    continuous_component_weights: Mapping[str, float] = field(
        default_factory=lambda: dict(
            DEFAULT_CONTINUOUS_COMPONENT_WEIGHTS
        )
    )
    shootout_cap: float = 0.10
    reliability_minutes: float = 270.0
    penalty_prior_strength: float = 5.0
    shootout_prior_strength: float = 3.0
    outer_folds: int = 5
    inner_folds: int = 4
    calibration_folds: int = 4
    ece_bins: int = 10
    random_state: int = 42

    def __post_init__(self) -> None:
        expected = set(DEFAULT_CONTINUOUS_COMPONENT_WEIGHTS)
        if set(self.continuous_component_weights) != expected:
            raise ValueError(
                "Continuous goalkeeper weights must cover exactly "
                f"{sorted(expected)}"
            )
        weights = np.asarray(
            list(self.continuous_component_weights.values()),
            dtype=float,
        )
        if not np.isfinite(weights).all() or (weights < 0.0).any():
            raise ValueError(
                "Continuous goalkeeper weights must be finite and nonnegative"
            )
        if not np.isclose(float(weights.sum()), 1.0):
            raise ValueError(
                "Continuous goalkeeper component weights must sum to one"
            )
        if not 0.0 <= self.shootout_cap <= 0.15:
            raise ValueError("shootout_cap must be between 0.00 and 0.15")
        if self.reliability_minutes <= 0.0:
            raise ValueError("reliability_minutes must be positive")
        if self.penalty_prior_strength <= 0.0:
            raise ValueError("penalty_prior_strength must be positive")
        if self.shootout_prior_strength <= 0.0:
            raise ValueError("shootout_prior_strength must be positive")
        if min(
            self.outer_folds,
            self.inner_folds,
            self.calibration_folds,
        ) < 2:
            raise ValueError("All calibration fold counts must be at least 2")
        if self.ece_bins < 2:
            raise ValueError("ece_bins must be at least 2")


@dataclass(frozen=True)
class BinaryCalibrationMetrics:
    """Held-out probability metrics for one calibration candidate."""

    roc_auc: float
    pr_auc: float
    brier_score: float
    expected_calibration_error: float
    rows: int
    positives: int
    matches: int


@dataclass(frozen=True)
class _ConstantCalibrator:
    value: float

    def predict(self, probability: np.ndarray) -> np.ndarray:
        return np.full(len(probability), self.value, dtype=float)


def _truthy(series: pd.Series) -> pd.Series:
    return series.fillna(False).astype(str).str.lower().isin(
        {"true", "1", "yes"}
    )


def _coordinate(value: object, axis: int) -> float:
    if isinstance(value, (list, tuple)) and len(value) > axis:
        return float(value[axis])
    if not isinstance(value, str) or not value.strip():
        return np.nan
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return np.nan
    if not isinstance(parsed, (list, tuple)) or len(parsed) <= axis:
        return np.nan
    return float(parsed[axis])


def _expected_calibration_error(
    target: np.ndarray,
    prediction: np.ndarray,
    *,
    bins: int,
) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    bucket = np.clip(
        np.digitize(prediction, edges[1:-1]),
        0,
        bins - 1,
    )
    error = 0.0
    for index in range(bins):
        mask = bucket == index
        if mask.any():
            error += float(
                mask.mean()
                * abs(
                    float(prediction[mask].mean())
                    - float(target[mask].mean())
                )
            )
    return error


def _probability_metrics(
    target: np.ndarray,
    prediction: np.ndarray,
    groups: np.ndarray,
    *,
    bins: int,
) -> BinaryCalibrationMetrics:
    target = np.asarray(target, dtype=int)
    prediction = np.clip(
        np.asarray(prediction, dtype=float),
        0.0,
        1.0,
    )
    if np.unique(target).size < 2:
        roc_auc = np.nan
        pr_auc = np.nan
    else:
        roc_auc = float(roc_auc_score(target, prediction))
        pr_auc = float(average_precision_score(target, prediction))
    return BinaryCalibrationMetrics(
        roc_auc=roc_auc,
        pr_auc=pr_auc,
        brier_score=float(brier_score_loss(target, prediction)),
        expected_calibration_error=_expected_calibration_error(
            target,
            prediction,
            bins=bins,
        ),
        rows=int(len(target)),
        positives=int(target.sum()),
        matches=int(pd.Series(groups).nunique()),
    )


def _post_shot_feature_frame(
    shots: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str], list[str]]:
    working = shots.copy()
    end_location = working.get(
        "shot_end_location",
        pd.Series(np.nan, index=working.index),
    )
    working["_end_y"] = end_location.map(
        lambda value: _coordinate(value, 1)
    )
    working["_end_z"] = end_location.map(
        lambda value: _coordinate(value, 2)
    )
    working["_distance_from_centre"] = (
        working["_end_y"] - 40.0
    ).abs()
    numeric = [
        "shot_statsbomb_xg",
        "_distance_from_centre",
        "_end_z",
    ]
    for column in ("shot_one_on_one", "shot_first_time"):
        if column in working:
            working[column] = _truthy(working[column]).astype(float)
            numeric.append(column)
    categorical = [
        column
        for column in (
            "shot_body_part",
            "shot_technique",
            "shot_type",
        )
        if column in working
    ]
    return working, numeric, categorical


def _base_post_shot_model(
    numeric: Sequence[str],
    categorical: Sequence[str],
    *,
    random_state: int,
) -> Pipeline:
    transformers: list[tuple[str, Pipeline, Sequence[str]]] = [
        (
            "numeric",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scale", StandardScaler()),
                ]
            ),
            list(numeric),
        )
    ]
    if categorical:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    [
                        (
                            "imputer",
                            SimpleImputer(
                                strategy="constant",
                                fill_value="Missing",
                            ),
                        ),
                        (
                            "encode",
                            OneHotEncoder(
                                handle_unknown="ignore",
                                min_frequency=2,
                            ),
                        ),
                    ]
                ),
                list(categorical),
            )
        )
    return Pipeline(
        [
            (
                "features",
                ColumnTransformer(transformers),
            ),
            (
                "model",
                LogisticRegression(
                    C=0.5,
                    max_iter=2_000,
                    random_state=random_state,
                ),
            ),
        ]
    )


def _fit_base_and_predict(
    features: pd.DataFrame,
    target: np.ndarray,
    train: np.ndarray,
    validation: np.ndarray,
    numeric: Sequence[str],
    categorical: Sequence[str],
    *,
    random_state: int,
) -> np.ndarray:
    train_target = target[train]
    if np.unique(train_target).size < 2:
        return np.full(
            len(validation),
            float(train_target.mean()),
            dtype=float,
        )
    model = _base_post_shot_model(
        numeric,
        categorical,
        random_state=random_state,
    )
    model.fit(features.iloc[train], train_target)
    return model.predict_proba(features.iloc[validation])[:, 1]


def _logit(probability: np.ndarray) -> np.ndarray:
    clipped = np.clip(
        np.asarray(probability, dtype=float),
        1e-6,
        1.0 - 1e-6,
    )
    return np.log(clipped / (1.0 - clipped)).reshape(-1, 1)


def _fit_calibrator(
    method: str,
    probability: np.ndarray,
    target: np.ndarray,
    *,
    random_state: int,
) -> LogisticRegression | IsotonicRegression | _ConstantCalibrator:
    if np.unique(target).size < 2:
        return _ConstantCalibrator(float(np.mean(target)))
    if method == "sigmoid":
        calibrator = LogisticRegression(
            C=1_000.0,
            max_iter=2_000,
            random_state=random_state,
        )
        calibrator.fit(_logit(probability), target)
        return calibrator
    if method == "isotonic":
        calibrator = IsotonicRegression(
            y_min=0.0,
            y_max=1.0,
            out_of_bounds="clip",
        )
        calibrator.fit(
            np.asarray(probability, dtype=float),
            target,
        )
        return calibrator
    raise ValueError(f"Unknown calibration method: {method}")


def _apply_calibrator(
    calibrator: LogisticRegression
    | IsotonicRegression
    | _ConstantCalibrator,
    probability: np.ndarray,
) -> np.ndarray:
    if isinstance(calibrator, LogisticRegression):
        return calibrator.predict_proba(_logit(probability))[:, 1]
    return np.asarray(calibrator.predict(probability), dtype=float)


def _cross_fitted_base_probabilities(
    features: pd.DataFrame,
    target: np.ndarray,
    groups: np.ndarray,
    numeric: Sequence[str],
    categorical: Sequence[str],
    *,
    folds: int,
    random_state: int,
) -> np.ndarray:
    unique_groups = np.unique(groups)
    if unique_groups.size < 2:
        raise ValueError(
            "At least two match groups are required for post-shot calibration"
        )
    splitter = GroupKFold(n_splits=min(folds, unique_groups.size))
    prediction = np.full(len(features), np.nan, dtype=float)
    for fold, (train, validation) in enumerate(
        splitter.split(features, target, groups),
        start=1,
    ):
        prediction[validation] = _fit_base_and_predict(
            features,
            target,
            train,
            validation,
            numeric,
            categorical,
            random_state=random_state + fold,
        )
    if not np.isfinite(prediction).all():
        raise RuntimeError("Cross-fitted post-shot predictions are incomplete")
    return prediction


def _development_calibration_metrics(
    base_probability: np.ndarray,
    target: np.ndarray,
    groups: np.ndarray,
    *,
    folds: int,
    bins: int,
    random_state: int,
) -> tuple[dict[str, BinaryCalibrationMetrics], dict[str, np.ndarray]]:
    unique_groups = np.unique(groups)
    splitter = GroupKFold(n_splits=min(folds, unique_groups.size))
    candidates = {
        "sigmoid": np.full(len(target), np.nan, dtype=float),
        "isotonic": np.full(len(target), np.nan, dtype=float),
    }
    for fold, (train, validation) in enumerate(
        splitter.split(base_probability, target, groups),
        start=1,
    ):
        for method in candidates:
            calibrator = _fit_calibrator(
                method,
                base_probability[train],
                target[train],
                random_state=random_state + fold,
            )
            candidates[method][validation] = _apply_calibrator(
                calibrator,
                base_probability[validation],
            )
    metrics = {
        method: _probability_metrics(
            target,
            prediction,
            groups,
            bins=bins,
        )
        for method, prediction in candidates.items()
    }
    return metrics, candidates


def _calibration_selection_key(
    metrics: BinaryCalibrationMetrics,
    method: str,
) -> tuple[float, float, int]:
    """Prefer calibration and accuracy; use sigmoid as deterministic tie-break."""

    return (
        metrics.brier_score,
        metrics.expected_calibration_error,
        0 if method == "sigmoid" else 1,
    )


def calibrate_post_shot_xg_v3(
    shots: pd.DataFrame,
    *,
    config: GoalkeeperV3Config | None = None,
) -> tuple[pd.Series, dict[str, Any]]:
    """Return nested match-disjoint OOF probabilities for ordinary shots.

    Period-five events and every penalty are removed before any model or
    calibration fit.  In each outer fold, sigmoid versus isotonic calibration
    is selected from cross-fitted development predictions only.  The untouched
    outer fold is used solely for evaluation and OOF feature construction.
    """

    settings = config or GoalkeeperV3Config()
    required = {
        "match_id",
        "period",
        "shot_outcome",
        "shot_statsbomb_xg",
    }
    missing = required.difference(shots.columns)
    if missing:
        raise ValueError(
            f"Post-shot calibration inputs missing: {sorted(missing)}"
        )

    period = pd.to_numeric(shots["period"], errors="coerce")
    shot_type = shots.get(
        "shot_type",
        pd.Series("", index=shots.index),
    ).fillna("").astype(str)
    is_regular_penalty = (
        period.isin(ORDINARY_MATCH_PERIODS)
        & shot_type.str.contains("Penalty", case=False, na=False)
    )
    is_shootout = period.eq(SHOOTOUT_PERIOD)
    on_target = (
        shots["shot_outcome"]
        .fillna("")
        .astype(str)
        .str.contains("Goal|Saved", case=False, na=False)
    )
    ordinary_non_penalty = (
        period.isin(ORDINARY_MATCH_PERIODS)
        & ~is_regular_penalty
        & on_target
    )
    if "type" in shots:
        ordinary_non_penalty &= shots["type"].astype(str).eq("Shot")
    working, numeric, categorical = _post_shot_feature_frame(
        shots.loc[ordinary_non_penalty].copy()
    )
    target = (
        working["shot_outcome"]
        .fillna("")
        .astype(str)
        .str.contains("Goal", case=False, na=False)
        .astype(int)
        .to_numpy()
    )
    groups = working["match_id"].to_numpy()
    unique_groups = np.unique(groups)
    if len(working) < 20 or np.unique(target).size < 2:
        raise ValueError(
            "Post-shot calibration requires at least 20 ordinary "
            "non-penalty shots and both outcomes"
        )
    if unique_groups.size < 4:
        raise ValueError(
            "Post-shot calibration requires at least four matches"
        )

    outer_splitter = GroupKFold(
        n_splits=min(settings.outer_folds, unique_groups.size)
    )
    selected_oof = np.full(len(working), np.nan, dtype=float)
    raw_oof = np.full(len(working), np.nan, dtype=float)
    candidate_oof = {
        "sigmoid": np.full(len(working), np.nan, dtype=float),
        "isotonic": np.full(len(working), np.nan, dtype=float),
    }
    fold_audit: list[dict[str, Any]] = []

    for fold, (development, validation) in enumerate(
        outer_splitter.split(working, target, groups),
        start=1,
    ):
        development_groups = groups[development]
        validation_groups = groups[validation]
        development_matches = sorted(
            pd.unique(development_groups).tolist()
        )
        validation_matches = sorted(
            pd.unique(validation_groups).tolist()
        )
        if set(development_matches).intersection(validation_matches):
            raise RuntimeError(
                "Goalkeeper post-shot outer-fold match leakage detected"
            )
        if pd.Series(development_groups).nunique() < 2:
            raise ValueError(
                "Insufficient development matches for nested calibration"
            )

        development_features = working.iloc[development]
        development_target = target[development]
        inner_raw = _cross_fitted_base_probabilities(
            development_features,
            development_target,
            development_groups,
            numeric,
            categorical,
            folds=settings.inner_folds,
            random_state=settings.random_state + 100 * fold,
        )
        development_metrics, _ = _development_calibration_metrics(
            inner_raw,
            development_target,
            development_groups,
            folds=settings.calibration_folds,
            bins=settings.ece_bins,
            random_state=settings.random_state + 1_000 * fold,
        )
        selected_method = min(
            development_metrics,
            key=lambda method: _calibration_selection_key(
                development_metrics[method],
                method,
            ),
        )

        outer_raw = _fit_base_and_predict(
            working,
            target,
            development,
            validation,
            numeric,
            categorical,
            random_state=settings.random_state + 10_000 + fold,
        )
        raw_oof[validation] = outer_raw
        for method in candidate_oof:
            calibrator = _fit_calibrator(
                method,
                inner_raw,
                development_target,
                random_state=settings.random_state + 20_000 + fold,
            )
            candidate_oof[method][validation] = _apply_calibrator(
                calibrator,
                outer_raw,
            )
        selected_oof[validation] = candidate_oof[selected_method][
            validation
        ]
        fold_audit.append(
            {
                "fold": fold,
                "development_matches": development_matches,
                "validation_matches": validation_matches,
                "match_overlap": [],
                "selected_on": "development_cross_fitted_predictions_only",
                "outer_validation_used_for_selection": False,
                "selected_calibration": selected_method,
                "development_candidate_metrics": {
                    method: asdict(metric)
                    for method, metric in development_metrics.items()
                },
            }
        )

    predictions = {
        "raw_logistic": raw_oof,
        **candidate_oof,
        "selected": selected_oof,
    }
    if any(
        not np.isfinite(prediction).all()
        for prediction in predictions.values()
    ):
        raise RuntimeError("Nested post-shot calibration produced missing OOF")
    method_metrics = {
        method: asdict(
            _probability_metrics(
                target,
                prediction,
                groups,
                bins=settings.ece_bins,
            )
        )
        for method, prediction in predictions.items()
    }
    selected_metrics = method_metrics["selected"]
    absolute_gate_passed = bool(
        selected_metrics["roc_auc"] >= 0.60
        and selected_metrics["pr_auc"] >= 0.40
        and selected_metrics["brier_score"] <= 0.25
        and selected_metrics["expected_calibration_error"] <= 0.15
    )
    selected_counts = (
        pd.Series(
            [row["selected_calibration"] for row in fold_audit],
            dtype=str,
        )
        .value_counts()
        .sort_index()
        .to_dict()
    )
    audit: dict[str, Any] = {
        "model_version": "goalkeeper_v3",
        "event_scope": "Qatar 2022 periods 1-4 only",
        "shootout_period": SHOOTOUT_PERIOD,
        "shootout_rows_excluded": int(is_shootout.sum()),
        "regular_penalty_rows_excluded": int(is_regular_penalty.sum()),
        "off_target_or_blocked_rows_excluded": int(
            (
                period.isin(ORDINARY_MATCH_PERIODS)
                & ~is_regular_penalty
                & ~on_target
            ).sum()
        ),
        "ordinary_non_penalty_rows": int(len(working)),
        "calibration_selection": (
            "nested development-fold selection between sigmoid and isotonic"
        ),
        "method_metrics": method_metrics,
        "absolute_metric_gate": {
            "roc_auc_minimum": 0.60,
            "pr_auc_minimum": 0.40,
            "brier_score_maximum": 0.25,
            "expected_calibration_error_maximum": 0.15,
            "passed": absolute_gate_passed,
        },
        "selected_calibration_counts": selected_counts,
        "fold_audit": fold_audit,
        "oof_match_disjoint": True,
        "identity_features_used": [],
        "feature_columns": [*numeric, *categorical],
    }
    return pd.Series(
        selected_oof,
        index=working.index,
        name="post_shot_goal_probability_oof_v3",
    ), audit


def _numeric(
    frame: pd.DataFrame,
    column: str,
) -> pd.Series:
    if column not in frame:
        return pd.Series(np.nan, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce")


def _first_available_numeric(
    frame: pd.DataFrame,
    columns: Sequence[str],
) -> pd.Series:
    for column in columns:
        values = _numeric(frame, column)
        if values.notna().any():
            return values
    return pd.Series(np.nan, index=frame.index, dtype=float)


def _midrank_unit_percentile(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    available = numeric.notna()
    result = pd.Series(np.nan, index=series.index, dtype=float)
    count = int(available.sum())
    if count == 0:
        return result
    if count == 1:
        result.loc[available] = 0.5
        return result
    ranks = numeric.loc[available].rank(method="average")
    result.loc[available] = (ranks - 1.0) / (count - 1.0)
    return result.clip(0.0, 1.0)


def _select_main_goalkeepers(
    features: pd.DataFrame,
) -> pd.Series:
    if "is_main_goalkeeper" in features:
        supplied = features["is_main_goalkeeper"].fillna(False).astype(bool)
        counts = supplied.groupby(
            features["team"],
            sort=False,
            dropna=False,
        ).sum()
        if counts.eq(1).all():
            return supplied
    selection = features.assign(
        _selection_minutes=_numeric(features, "minutes").fillna(0.0),
        _selection_actions=_numeric(features, "actions").fillna(0.0),
        _selection_order=np.arange(len(features)),
    ).sort_values(
        [
            "team",
            "_selection_minutes",
            "_selection_actions",
            "_selection_order",
        ],
        ascending=[True, False, False, True],
        kind="mergesort",
    )
    main_index = selection.groupby(
        "team",
        sort=False,
        dropna=False,
    ).head(1).index
    return pd.Series(
        features.index.isin(main_index),
        index=features.index,
        dtype=bool,
    )


def _beta_binomial_rate(
    saved: pd.Series,
    faced: pd.Series,
    *,
    prior_rate: float,
    prior_strength: float,
) -> pd.Series:
    saved = pd.to_numeric(saved, errors="coerce").fillna(0.0)
    faced = pd.to_numeric(faced, errors="coerce").fillna(0.0)
    posterior = (
        saved + prior_rate * prior_strength
    ) / (faced + prior_strength)
    return posterior.where(faced.gt(0.0))


def calculate_goalkeeper_ratings_v3(
    goalkeeper_features: pd.DataFrame,
    *,
    config: GoalkeeperV3Config | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Score one main goalkeeper per team with explicit v3 components.

    The input contract deliberately accepts only separately materialized
    regular-penalty and shootout counts.  Legacy combined penalty fields are
    never used.  Missing continuous inputs have their weight renormalized.
    """

    settings = config or GoalkeeperV3Config()
    required = {"team", "minutes"}
    missing = required.difference(goalkeeper_features.columns)
    if missing:
        raise ValueError(
            f"Goalkeeper v3 inputs missing: {sorted(missing)}"
        )
    if goalkeeper_features.empty:
        raise ValueError("Goalkeeper v3 inputs are empty")

    output = goalkeeper_features.copy()
    output["is_main_goalkeeper"] = _select_main_goalkeepers(output)
    main = output.loc[output["is_main_goalkeeper"]].copy()
    if main["team"].duplicated().any():
        raise RuntimeError("More than one main goalkeeper selected per team")

    component_values: dict[str, pd.Series] = {}
    for component, input_columns in _COMPONENT_INPUTS.items():
        if component == "cross_claim_control":
            cross_inputs = [
                _midrank_unit_percentile(_numeric(main, column))
                for column in input_columns
                if _numeric(main, column).notna().any()
            ]
            if cross_inputs:
                component_values[component] = pd.concat(
                    cross_inputs,
                    axis=1,
                ).mean(axis=1, skipna=True)
            else:
                component_values[component] = pd.Series(
                    np.nan,
                    index=main.index,
                    dtype=float,
                )
        else:
            component_values[component] = _midrank_unit_percentile(
                _first_available_numeric(main, input_columns)
            )

    regular_faced = _numeric(
        main,
        "regular_penalties_faced",
    ).fillna(0.0)
    regular_saved = _numeric(
        main,
        "regular_penalties_saved",
    ).fillna(0.0)
    regular_total = float(regular_faced.sum())
    regular_prior = (
        float(regular_saved.sum() / regular_total)
        if regular_total > 0.0
        else 0.20
    )
    main["regular_penalty_rate_posterior_v3"] = _beta_binomial_rate(
        regular_saved,
        regular_faced,
        prior_rate=regular_prior,
        prior_strength=settings.penalty_prior_strength,
    )
    component_values[
        "regular_penalty_performance"
    ] = _midrank_unit_percentile(
        main["regular_penalty_rate_posterior_v3"]
    )

    components = pd.DataFrame(component_values, index=main.index)
    weights = pd.Series(
        settings.continuous_component_weights,
        dtype=float,
    )
    available = components.notna()
    available_weight = available.mul(weights, axis=1).sum(axis=1)
    raw_continuous = (
        components.mul(weights, axis=1).sum(axis=1, skipna=True)
        / available_weight.replace(0.0, np.nan)
    )
    if raw_continuous.notna().sum() == 0:
        raise ValueError(
            "No continuous goalkeeper component is available for scoring"
        )
    continuous_prior = float(raw_continuous.mean())
    minutes = _numeric(main, "minutes").fillna(0.0).clip(lower=0.0)
    minutes_reliability = minutes / (
        minutes + settings.reliability_minutes
    )
    coverage = available_weight.clip(0.0, 1.0)
    reliability = minutes_reliability * coverage
    continuous_rating = (
        reliability * raw_continuous.fillna(continuous_prior)
        + (1.0 - reliability) * continuous_prior
    ).clip(0.0, 1.0)

    shootout_faced = _numeric(
        main,
        "shootout_penalties_faced",
    ).fillna(0.0)
    shootout_saved = _numeric(
        main,
        "shootout_penalties_saved",
    ).fillna(0.0)
    shootout_total = float(shootout_faced.sum())
    shootout_prior = (
        float(shootout_saved.sum() / shootout_total)
        if shootout_total > 0.0
        else 0.20
    )
    shootout_posterior = _beta_binomial_rate(
        shootout_saved,
        shootout_faced,
        prior_rate=shootout_prior,
        prior_strength=settings.shootout_prior_strength,
    )
    shootout_evidence = shootout_faced / (
        shootout_faced + settings.shootout_prior_strength
    )
    shootout_signal = (
        (shootout_posterior.fillna(shootout_prior) - shootout_prior)
        / max(1.0 - shootout_prior, 1e-9)
    ).clip(lower=0.0, upper=1.0)
    shootout_component = (
        settings.shootout_cap
        * shootout_evidence
        * shootout_signal
    ).clip(0.0, settings.shootout_cap)

    main["goalkeeper_component_coverage_v3"] = coverage
    main["goalkeeper_reliability_v3"] = reliability
    main["continuous_goalkeeper_raw_rating_v3"] = raw_continuous
    main["continuous_goalkeeper_rating_v3"] = continuous_rating
    main["shootout_rate_posterior_v3"] = shootout_posterior
    main["shootout_component_v3"] = shootout_component
    main["dedicated_goalkeeper_score_v3"] = (
        (1.0 - settings.shootout_cap) * continuous_rating
        + shootout_component
    ).clip(0.0, 1.0)
    main["goalkeeper_rank_v3"] = (
        main["dedicated_goalkeeper_score_v3"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    cohort_size = len(main)
    main["percentile_equivalent_placement"] = (
        cohort_size
        - pd.to_numeric(main["goalkeeper_rank_v3"], errors="coerce")
        + 0.5
    ) / cohort_size
    main["GKRankingStatus_v3"] = "Ranked (team main goalkeeper)"
    for component in settings.continuous_component_weights:
        main[f"{component}_component_v3"] = components[component]

    publish_columns = [
        "regular_penalty_rate_posterior_v3",
        "goalkeeper_component_coverage_v3",
        "goalkeeper_reliability_v3",
        "continuous_goalkeeper_raw_rating_v3",
        "continuous_goalkeeper_rating_v3",
        "shootout_rate_posterior_v3",
        "shootout_component_v3",
        "dedicated_goalkeeper_score_v3",
        "goalkeeper_rank_v3",
        "percentile_equivalent_placement",
        "GKRankingStatus_v3",
        *(
            f"{component}_component_v3"
            for component in settings.continuous_component_weights
        ),
    ]
    for column in publish_columns:
        if column == "goalkeeper_rank_v3":
            output[column] = pd.Series(
                pd.NA,
                index=output.index,
                dtype="Int64",
            )
        elif column == "GKRankingStatus_v3":
            output[column] = "Unranked (backup goalkeeper)"
        else:
            output[column] = np.nan
        output.loc[main.index, column] = main[column]
    output["goalkeeper_rank_v3"] = pd.to_numeric(
        output["goalkeeper_rank_v3"],
        errors="coerce",
    ).astype("Int64")

    audit: dict[str, Any] = {
        "model_version": "goalkeeper_v3",
        "dedicated_goalkeeper_cohort": int(len(main)),
        "team_count": int(output["team"].nunique(dropna=False)),
        "one_main_goalkeeper_per_team": bool(
            len(main) == output["team"].nunique(dropna=False)
            and main["team"].is_unique
        ),
        "backup_goalkeepers_unranked": bool(
            output.loc[
                ~output["is_main_goalkeeper"],
                "goalkeeper_rank_v3",
            ].isna().all()
        ),
        "continuous_component_weights": dict(
            settings.continuous_component_weights
        ),
        "dedicated_score_maximum_allocations": {
            **{
                component: (
                    (1.0 - settings.shootout_cap) * weight
                )
                for component, weight in (
                    settings.continuous_component_weights.items()
                )
            },
            "shootout_performance": settings.shootout_cap,
        },
        "dedicated_score_formula": (
            f"{1.0 - settings.shootout_cap:.2f} * "
            "continuous_goalkeeper_rating_v3 + shootout_component_v3"
        ),
        "missing_input_weight_renormalization": True,
        "reliability_treatment": (
            "single minutes reliability multiplied by available weight"
        ),
        "reliability_minutes": settings.reliability_minutes,
        "regular_penalty_prior_rate": regular_prior,
        "regular_penalty_prior_strength": (
            settings.penalty_prior_strength
        ),
        "shootout_prior_rate": shootout_prior,
        "shootout_prior_strength": settings.shootout_prior_strength,
        "shootout_cap": settings.shootout_cap,
        "maximum_observed_shootout_component": float(
            shootout_component.max()
        ),
        "continuous_event_scope": "Qatar 2022 periods 1-4; penalties excluded",
        "regular_penalty_scope": (
            "Qatar 2022 periods 1-4, penalty events only"
        ),
        "shootout_scope": "Qatar 2022 period 5 only",
        "cross_position_field": "percentile_equivalent_placement",
        "cross_position_interpretation": (
            "rank-percentile publication bridge only; not measured absolute "
            "common-unit contribution"
        ),
        "identity_features_used": [],
    }
    return output, audit


def aggregate_goalkeeper_match_features_v3(
    match_features: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate ordinary match-level goalkeeper rows for bootstrap scoring."""

    required = {"match_id", "team", "player_id", "minutes"}
    missing = required.difference(match_features.columns)
    if missing:
        raise ValueError(
            f"Goalkeeper match features missing: {sorted(missing)}"
        )
    working = match_features.copy()
    if "period" in working:
        period = pd.to_numeric(working["period"], errors="coerce")
        working = working.loc[period.isin(ORDINARY_MATCH_PERIODS)].copy()
    keys = ["team", "player_id"]
    output = (
        working.groupby(keys, as_index=False, dropna=False)["minutes"]
        .sum()
    )
    minutes = pd.to_numeric(working["minutes"], errors="coerce").fillna(0.0)
    for column in _MATCH_RATE_COLUMNS:
        if column not in working:
            continue
        values = pd.to_numeric(working[column], errors="coerce")
        numerator = (
            values.mul(minutes)
            .groupby([working[key] for key in keys], dropna=False)
            .sum(min_count=1)
            .rename("_numerator")
            .reset_index()
        )
        denominator = (
            minutes.where(values.notna())
            .groupby([working[key] for key in keys], dropna=False)
            .sum(min_count=1)
            .rename("_denominator")
            .reset_index()
        )
        weighted = numerator.merge(denominator, on=keys, how="outer")
        weighted[column] = (
            weighted["_numerator"]
            / weighted["_denominator"].replace(0.0, np.nan)
        )
        output = output.merge(
            weighted[keys + [column]],
            on=keys,
            how="left",
        )
    for column in _MATCH_COUNT_COLUMNS:
        if column not in working:
            continue
        counts = (
            pd.to_numeric(working[column], errors="coerce")
            .fillna(0.0)
            .groupby([working[key] for key in keys], dropna=False)
            .sum()
            .rename(column)
            .reset_index()
        )
        output = output.merge(counts, on=keys, how="left")
    return output


def bootstrap_goalkeeper_uncertainty_v3(
    match_features: pd.DataFrame,
    *,
    config: GoalkeeperV3Config | None = None,
    iterations: int = 500,
    random_state: int = 42,
) -> pd.DataFrame:
    """Return match-cluster bootstrap score and rank intervals.

    `match_features` must contain ordinary-match component values.  If it has a
    period column, period-five rows are removed before the point estimate and
    every draw.  Shootout counts may be attached only as separately named
    aggregate columns.
    """

    if iterations < 20:
        raise ValueError("At least 20 bootstrap iterations are required")
    required = {"match_id", "team", "player_id", "minutes"}
    missing = required.difference(match_features.columns)
    if missing:
        raise ValueError(
            f"Goalkeeper bootstrap inputs missing: {sorted(missing)}"
        )
    settings = config or GoalkeeperV3Config()
    working = match_features.copy()
    if "period" in working:
        period = pd.to_numeric(working["period"], errors="coerce")
        working = working.loc[period.isin(ORDINARY_MATCH_PERIODS)].copy()
    matches = pd.unique(working["match_id"])
    if len(matches) < 2:
        raise ValueError(
            "At least two ordinary matches are required for bootstrap"
        )

    point_features = aggregate_goalkeeper_match_features_v3(working)
    point, _ = calculate_goalkeeper_ratings_v3(
        point_features,
        config=settings,
    )
    point = point.loc[point["is_main_goalkeeper"]].reset_index(drop=True)
    identifiers = point[["team", "player_id"]].copy()
    score_draws = np.full((len(point), iterations), np.nan, dtype=float)
    rank_draws = np.full((len(point), iterations), np.nan, dtype=float)
    lookup = {
        (str(row.team), row.player_id): index
        for index, row in enumerate(
            identifiers.itertuples(index=False)
        )
    }
    generator = np.random.default_rng(random_state)
    for draw in range(iterations):
        sampled_matches = generator.choice(
            matches,
            size=len(matches),
            replace=True,
        )
        pieces = [
            working.loc[working["match_id"].eq(match)].copy()
            for match in sampled_matches
        ]
        sampled = pd.concat(pieces, ignore_index=True)
        aggregated = aggregate_goalkeeper_match_features_v3(sampled)
        rated, _ = calculate_goalkeeper_ratings_v3(
            aggregated,
            config=settings,
        )
        for row in rated.loc[
            rated["is_main_goalkeeper"]
        ].itertuples(index=False):
            key = (str(row.team), row.player_id)
            index = lookup.get(key)
            if index is None:
                continue
            score_draws[index, draw] = float(
                row.dedicated_goalkeeper_score_v3
            )
            rank_draws[index, draw] = float(row.goalkeeper_rank_v3)

    output = identifiers.copy()
    output["goalkeeper_score_point_v3"] = pd.to_numeric(
        point["dedicated_goalkeeper_score_v3"],
        errors="coerce",
    ).to_numpy()
    output["goalkeeper_score_interval_low_v3"] = np.nanquantile(
        score_draws,
        0.05,
        axis=1,
    )
    output["goalkeeper_score_interval_high_v3"] = np.nanquantile(
        score_draws,
        0.95,
        axis=1,
    )
    output["goalkeeper_rank_interval_low_v3"] = np.nanquantile(
        rank_draws,
        0.05,
        axis=1,
    )
    output["goalkeeper_rank_interval_high_v3"] = np.nanquantile(
        rank_draws,
        0.95,
        axis=1,
    )
    output["goalkeeper_bootstrap_coverage_v3"] = np.isfinite(
        score_draws
    ).mean(axis=1)
    output["goalkeeper_uncertainty_status_v3"] = np.select(
        [
            output["goalkeeper_bootstrap_coverage_v3"].ge(0.90)
            & (
                output["goalkeeper_rank_interval_high_v3"]
                - output["goalkeeper_rank_interval_low_v3"]
            ).le(5.0),
            output["goalkeeper_bootstrap_coverage_v3"].ge(0.75),
        ],
        ["stable", "moderate"],
        default="wide",
    )
    output.attrs["bootstrap_iterations"] = iterations
    output.attrs["random_state"] = random_state
    output.attrs["sampling_unit"] = "whole Qatar 2022 match"
    return output
