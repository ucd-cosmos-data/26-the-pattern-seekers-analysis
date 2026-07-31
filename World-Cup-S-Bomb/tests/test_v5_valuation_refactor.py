"""Leakage and mathematical regression tests for the V5 valuation repair."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.models.roles import build_semantic_role_labels
from src.models.valuation import (
    GroupedElasticNetValuator,
    IndependentValueScaler,
    calculate_final_player_rating,
)
from scripts.run_pipeline import _validation_regression_gate


def test_independent_value_scaler_equalizes_channel_extrema() -> None:
    frame = pd.DataFrame(
        {
            "position_group": ["Forward"] * 4,
            "vaep_off_p90": [0.0, 1.0, 2.0, 4.0],
            "vaep_def_p90": [0.00, 0.01, 0.02, 0.04],
        }
    )
    scaled = IndependentValueScaler(minimum_group_size=2).fit_transform(frame)
    assert np.isclose(scaled["vaep_off_scaled"].max(), 1.0)
    assert np.isclose(scaled["vaep_def_scaled"].max(), 1.0)
    assert np.isclose(scaled["vaep_off_scaled"].min(), 0.0)
    assert np.isclose(scaled["vaep_def_scaled"].min(), 0.0)


def test_independent_value_scaler_does_not_refit_on_holdout() -> None:
    train = pd.DataFrame(
        {
            "position_group": ["Midfield"] * 4,
            "vaep_off_p90": [0.0, 1.0, 2.0, 3.0],
            "vaep_def_p90": [0.0, 0.1, 0.2, 0.3],
        }
    )
    holdout = pd.DataFrame(
        {
            "position_group": ["Midfield"],
            "vaep_off_p90": [100.0],
            "vaep_def_p90": [100.0],
        }
    )
    scaler = IndependentValueScaler(minimum_group_size=2).fit(train)
    isolated = scaler.transform(holdout)
    repeated = scaler.transform(pd.concat([holdout, holdout]))
    assert np.allclose(isolated.iloc[0], repeated.iloc[0])
    assert isolated["vaep_off_scaled"].iloc[0] == 1.0
    assert isolated["vaep_def_scaled"].iloc[0] == 1.0


def test_final_rating_replaces_existing_scaled_channels() -> None:
    profiles = pd.DataFrame(
        {
            "player_id": range(20),
            "team": ["A"] * 10 + ["B"] * 10,
            "position_group": ["Forward"] * 20,
            "minutes": [400.0] * 20,
            "vaep_total_p90": np.linspace(0.1, 1.0, 20),
            "vaep_off_p90": np.linspace(0.1, 1.0, 20),
            "vaep_def_p90": np.linspace(1.0, 0.1, 20),
            "vaep_off_scaled": [-1.0] * 20,
            "vaep_def_scaled": [-1.0] * 20,
            "vaep_per_touch": np.linspace(0.01, 0.1, 20),
            "xt_p90": np.linspace(0.0, 0.5, 20),
            "role_adjusted_value": np.linspace(0.2, 0.8, 20),
            "completeness_score": [0.5] * 20,
            "off_ball_score": [0.4] * 20,
        }
    )
    rated = calculate_final_player_rating(profiles)
    assert rated.columns.is_unique
    assert rated["vaep_off_scaled"].between(0.0, 1.0).all()
    assert rated["vaep_def_scaled"].between(0.0, 1.0).all()


def test_grouped_elastic_net_never_mixes_matches() -> None:
    rng = np.random.default_rng(42)
    rows = 120
    groups = np.repeat(np.arange(12), 10)
    frame = pd.DataFrame(
        {
            "high_value": rng.normal(size=rows),
            "volume": rng.normal(size=rows),
        }
    )
    target = 2.5 * frame["high_value"] + 0.05 * frame["volume"]
    result = GroupedElasticNetValuator(
        feature_names=("high_value", "volume"),
        outer_folds=4,
        inner_folds=3,
        alphas=(0.001, 0.01, 0.1),
        l1_ratios=(0.2, 0.8),
    ).fit(frame, target, groups)
    assert result.fold_audit_
    for fold in result.fold_audit_:
        assert set(fold["train_groups"]).isdisjoint(fold["validation_groups"])
    coefficients = result.coefficient_series()
    assert coefficients["high_value"] > coefficients["volume"]
    assert coefficients.std() > 0.01


def test_dynamic_role_labels_are_unique_and_feature_driven() -> None:
    profiles = pd.DataFrame(
        {
            "position_group": ["Center Back"] * 6,
            "aerial_score": [0.9, 0.8, 0.7, 0.1, 0.2, 0.1],
            "defensive_score": [0.8, 0.9, 0.8, 0.3, 0.2, 0.3],
            "progression_score": [0.1, 0.2, 0.1, 0.9, 0.8, 0.9],
            "ball_security_score": [0.2, 0.2, 0.3, 0.8, 0.9, 0.8],
            "creation_score": [0.1] * 6,
            "finishing_score": [0.1] * 6,
            "pressing_score": [0.2] * 6,
        }
    )
    labels = np.asarray([0, 0, 0, 1, 1, 1])
    names = build_semantic_role_labels(profiles, labels)
    assert len(set(names.values())) == 2
    assert "Aerial" in names[0] or "Defensive" in names[0]
    assert "Progressive" in names[1] or "Secure" in names[1]


def test_validation_regression_gate_rejects_metric_degradation() -> None:
    previous = {
        "legacy_vaep_oof": {
            "roc_auc": 0.90,
            "pr_auc": 0.50,
            "brier_score": 0.10,
        }
    }
    current = {
        "legacy_vaep_oof": {
            "roc_auc": 0.88,
            "pr_auc": 0.50,
            "brier_score": 0.10,
        }
    }
    result = _validation_regression_gate(
        previous,
        current,
        include_attention=False,
        tolerance=0.01,
    )
    assert not result["passed"]


def test_nonproduction_attention_baseline_is_informational() -> None:
    previous = {
        "legacy_vaep_oof": {"roc_auc": 0.90},
        "attention": {
            "retrospective": {
                "baseline": {"roc_auc": 0.90},
                "attention": {"roc_auc": 0.70},
            }
        },
    }
    current = {
        "legacy_vaep_oof": {"roc_auc": 0.90},
        "attention": {
            "retrospective": {
                "baseline": {"roc_auc": 0.80},
                "attention": {"roc_auc": 0.75},
            }
        },
    }
    result = _validation_regression_gate(
        previous,
        current,
        include_attention=True,
        tolerance=0.01,
    )
    assert result["passed"]
    baseline = next(
        item
        for item in result["comparisons"]
        if ".baseline." in item["metric_path"]
    )
    assert not baseline["required_for_gate"]
