"""Leakage-auditable calibration of the outfield composite weights."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


COMPONENTS = (
    "vaep_90",
    "vaep_per_touch",
    "xt_90",
    "role_adjusted_value",
    "completeness_score",
    "off_ball_score",
)


def _percentile(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").rank(
        method="average",
        pct=True,
    )


def _component_matrix(profiles: pd.DataFrame) -> pd.DataFrame:
    required = {
        "vaep_component",
        "vaep_per_touch",
        "xt_p90",
        "role_adjusted_value",
        "completeness_score",
        "off_ball_score",
        "position_group",
    }
    missing = required.difference(profiles.columns)
    if missing:
        raise ValueError(
            f"Composite calibration inputs missing: {sorted(missing)}"
        )
    matrix = pd.DataFrame(
        {
            "vaep_90": profiles["vaep_component"],
            "vaep_per_touch": _percentile(profiles["vaep_per_touch"]),
            "xt_90": _percentile(profiles["xt_p90"]),
            "role_adjusted_value": profiles["role_adjusted_value"],
            "completeness_score": profiles["completeness_score"],
            "off_ball_score": profiles["off_ball_score"],
        },
        index=profiles.index,
    ).apply(pd.to_numeric, errors="coerce")
    for column in matrix:
        position_prior = matrix.groupby(
            profiles["position_group"]
        )[column].transform("mean")
        matrix[column] = (
            matrix[column]
            .fillna(position_prior)
            .fillna(matrix[column].mean())
            .fillna(0.5)
        )
    return matrix


def _team_importance_target(profiles: pd.DataFrame) -> pd.Series:
    minutes = pd.to_numeric(
        profiles["minutes"],
        errors="coerce",
    ).fillna(0.0)
    minutes_share = minutes / minutes.groupby(profiles["team"]).transform(
        "sum"
    ).replace(0.0, np.nan)
    goals = (
        profiles["goals"]
        if "goals" in profiles
        else pd.Series(0.0, index=profiles.index)
    )
    xa = (
        profiles["xa_sum"]
        if "xa_sum" in profiles
        else pd.Series(0.0, index=profiles.index)
    )
    outcome = pd.to_numeric(
        goals,
        errors="coerce",
    ).fillna(0.0) + pd.to_numeric(
        xa,
        errors="coerce",
    ).fillna(0.0)
    outcome_share = outcome / outcome.groupby(profiles["team"]).transform(
        "sum"
    ).replace(0.0, np.nan)
    target = (
        0.65 * _percentile(minutes_share.fillna(0.0))
        + 0.35 * _percentile(outcome_share.fillna(0.0))
    )
    return target.clip(0.0, 1.0)


def calibrate_composite_weights(
    profiles: pd.DataFrame,
    default_weights: Mapping[str, float],
    *,
    random_state: int = 42,
    tolerance: float = 0.01,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Tune positive ElasticNet weights with team-disjoint cross-validation."""

    matrix = _component_matrix(profiles)
    target = _team_importance_target(profiles)
    groups = profiles["team"].astype(str)
    folds = GroupKFold(n_splits=min(5, groups.nunique()))
    candidates = [
        (alpha, l1_ratio)
        for alpha in (0.001, 0.01, 0.05, 0.10)
        for l1_ratio in (0.10, 0.50, 0.90)
    ]
    best: dict[str, Any] | None = None
    for alpha, l1_ratio in candidates:
        prediction = np.full(len(profiles), np.nan, dtype=float)
        fold_audit: list[dict[str, Any]] = []
        for fold_id, (train, validation) in enumerate(
            folds.split(matrix, target, groups)
        ):
            model = make_pipeline(
                StandardScaler(),
                ElasticNet(
                    alpha=alpha,
                    l1_ratio=l1_ratio,
                    positive=True,
                    max_iter=20_000,
                    random_state=random_state,
                ),
            )
            model.fit(matrix.iloc[train], target.iloc[train])
            prediction[validation] = model.predict(
                matrix.iloc[validation]
            )
            fold_audit.append(
                {
                    "fold": fold_id,
                    "training_teams": sorted(groups.iloc[train].unique()),
                    "validation_teams": sorted(
                        groups.iloc[validation].unique()
                    ),
                }
            )
        rho = float(spearmanr(target, prediction).statistic)
        record = {
            "alpha": alpha,
            "l1_ratio": l1_ratio,
            "oof_spearman": rho,
            "prediction": prediction,
            "fold_audit": fold_audit,
        }
        if best is None or rho > best["oof_spearman"]:
            best = record
    if best is None:
        raise RuntimeError("Composite calibration produced no candidate")
    default_prediction = sum(
        float(default_weights[column]) * matrix[column]
        for column in COMPONENTS
    )
    default_rho = float(
        spearmanr(target, default_prediction).statistic
    )
    selected_model = make_pipeline(
        StandardScaler(),
        ElasticNet(
            alpha=float(best["alpha"]),
            l1_ratio=float(best["l1_ratio"]),
            positive=True,
            max_iter=20_000,
            random_state=random_state,
        ),
    ).fit(matrix, target)
    scaler = selected_model.named_steps["standardscaler"]
    elastic_net = selected_model.named_steps["elasticnet"]
    coefficients = np.maximum(
        elastic_net.coef_ / scaler.scale_,
        0.0,
    )
    if coefficients.sum() <= 1e-12:
        learned = dict(default_weights)
        coefficient_gate = False
    else:
        learned = {
            column: float(value / coefficients.sum())
            for column, value in zip(
                COMPONENTS,
                coefficients,
                strict=True,
            )
        }
        # A one-component solution is predictive of the chosen proxy but is
        # not a defensible player-value model: here it simply reconstructs
        # minutes through Completeness. Require a minimally diversified,
        # interpretable composite before promotion.
        active_component_count = sum(
            weight >= 0.05 for weight in learned.values()
        )
        maximum_component_weight = max(learned.values())
        coefficient_gate = bool(
            active_component_count >= 3
            and maximum_component_weight <= 0.65
        )
    non_inferior = bool(
        best["oof_spearman"] >= default_rho - tolerance
    )
    selected = learned if coefficient_gate and non_inferior else dict(
        default_weights
    )
    diagnostics = {
        "target": (
            "0.65 * within-tournament minutes-share percentile + "
            "0.35 * goals-plus-xA-share percentile"
        ),
        "grouping": "GroupKFold by team",
        "best_alpha": best["alpha"],
        "best_l1_ratio": best["l1_ratio"],
        "oof_spearman": best["oof_spearman"],
        "incumbent_spearman": default_rho,
        "non_inferiority_tolerance": tolerance,
        "non_inferior": non_inferior,
        "coefficient_gate": coefficient_gate,
        "coefficient_gate_rule": (
            "at least three normalized weights >= 0.05 and no weight > 0.65"
        ),
        "active_component_count": int(
            sum(weight >= 0.05 for weight in learned.values())
        ),
        "maximum_component_weight": float(max(learned.values())),
        "learned_normalized_weights": learned,
        "selected_weights": selected,
        "fallback_to_incumbent": not (
            coefficient_gate and non_inferior
        ),
        "fold_audit": best["fold_audit"],
    }
    return selected, diagnostics
