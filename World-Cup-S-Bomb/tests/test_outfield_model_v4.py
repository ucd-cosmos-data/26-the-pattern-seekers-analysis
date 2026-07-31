from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.models.outfield_tournament_impact_v4 import (
    REQUIRED_DEFENSIVE_PIPELINE_STAGES,
    DefensivePipeline,
    OutfieldV4Config,
    bootstrap_se_shrinkage,
    continuous_role_mixture,
    reject_identity_scoring_columns,
    variance_balanced_composite,
)


def _role_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "player_id": [11, 22, 33, 44],
            "player_name": ["A", "B", "C", "D"],
            "team": ["One", "Two", "Three", "Four"],
            "position_group": ["Forward", "Center Back"] * 2,
            "shots": [8, 0, 3, 1],
            "key_passes": [7, 0, 2, 1],
            "progressive_carries": [6, 0, 2, 1],
            "progressive_passes": [5, 1, 2, 1],
            "interceptions": [0, 8, 2, 4],
            "blocks": [0, 7, 2, 4],
            "clearances": [0, 9, 1, 5],
            "pressures": [1, 8, 4, 6],
            "recoveries": [1, 7, 3, 5],
            "average_x": [84, 31, 60, 45],
            "role_probability_01": [0.8, 0.1, 0.5, 0.3],
            "role_probability_02": [0.2, 0.9, 0.5, 0.7],
        }
    )


def _complete_pipeline(target: float) -> tuple[DefensivePipeline, np.ndarray]:
    raw = np.array([-1.2, -0.4, 0.2, 0.8, 1.5], dtype=float)
    attack = np.array([-0.3, 0.2, 0.8, 1.4, 2.1], dtype=float)
    w_att = np.array([0.35, 0.40, 0.50, 0.60, 0.70], dtype=float)
    w_def = 1.0 - w_att
    pipeline = DefensivePipeline(raw)
    pipeline.opposition_adjust(raw + np.linspace(0.1, 0.5, len(raw)))
    pipeline.augment_prevention(pipeline.values + np.linspace(-0.1, 0.2, len(raw)))
    pipeline.shrink_reliability(pipeline.values * 0.75)
    pipeline.variance_rescale(
        attack,
        w_att,
        w_def,
        target_share=target,
    )
    pipeline.mixture_weight(w_def)
    pipeline.assert_complete()
    return pipeline, attack


@pytest.mark.parametrize("target", [0.35, 0.42, 0.50])
def test_defensive_pipeline_enforces_exact_order_and_variance_share(
    target: float,
) -> None:
    pipeline, _ = _complete_pipeline(target)
    assert tuple(pipeline.stage_history) == REQUIRED_DEFENSIVE_PIPELINE_STAGES
    assert pipeline.metadata["defensive_variance_share_v4"] == pytest.approx(
        target, abs=1e-12
    )
    assert pipeline.metadata["defensive_variance_share_v4"] <= 0.50


def test_defensive_pipeline_rejects_skipped_or_reordered_stage() -> None:
    pipeline = DefensivePipeline(np.array([0.0, 1.0, 2.0]))
    with pytest.raises(RuntimeError, match="opposition_adjusted"):
        pipeline.augment_prevention([0.0, 1.0, 2.0])

    pipeline.opposition_adjust([0.1, 1.1, 2.1])
    with pytest.raises(RuntimeError, match="prevention_augmented"):
        pipeline.shrink_reliability([0.1, 1.1, 2.1])


def test_public_composite_rejects_raw_defense_and_accepts_only_complete_path() -> None:
    pipeline, attack = _complete_pipeline(0.42)
    frame = pd.DataFrame(
        {
            "attacking_component_reliable_v4": attack,
            "defensive_value_opposition_adjusted_v4": pipeline.values,
            "attacking_channel_weight_v4": [0.35, 0.40, 0.50, 0.60, 0.70],
            "defending_channel_weight_v4": [0.65, 0.60, 0.50, 0.40, 0.30],
            "defensive_value_raw_v4": [-1.2, -0.4, 0.2, 0.8, 1.5],
        }
    )
    score = variance_balanced_composite(
        frame,
        defensive_input_column="defensive_value_opposition_adjusted_v4",
        defensive_pipeline_stages=pipeline.stage_history,
    )
    assert np.isfinite(score).all()

    with pytest.raises(ValueError, match="raw defense is rejected"):
        variance_balanced_composite(
            frame,
            defensive_input_column="defensive_value_raw_v4",
            defensive_pipeline_stages=pipeline.stage_history,
        )
    with pytest.raises(ValueError, match="missing or out of order"):
        variance_balanced_composite(
            frame,
            defensive_input_column="defensive_value_opposition_adjusted_v4",
            defensive_pipeline_stages=pipeline.stage_history[:-1],
        )


@pytest.mark.parametrize("bounds", [(0.25, 0.75), (0.30, 0.70)])
def test_continuous_role_mixture_is_bounded_deterministic_and_identity_free(
    bounds: tuple[float, float],
) -> None:
    frame = _role_frame()
    baseline = continuous_role_mixture(
        frame, lower=bounds[0], upper=bounds[1]
    )
    repeated = continuous_role_mixture(
        frame, lower=bounds[0], upper=bounds[1]
    )
    pd.testing.assert_frame_equal(baseline, repeated)
    assert np.allclose(
        baseline["attacking_channel_weight_v4"]
        + baseline["defending_channel_weight_v4"],
        1.0,
        rtol=0.0,
        atol=1e-12,
    )
    assert baseline["attacking_channel_weight_v4"].between(*bounds).all()
    assert baseline["attacking_channel_weight_v4"].nunique() > 2

    shuffled = frame.copy()
    for column in ("player_id", "player_name", "team", "position_group"):
        shuffled[column] = shuffled[column].to_numpy()[::-1]
    changed_labels = continuous_role_mixture(
        shuffled, lower=bounds[0], upper=bounds[1]
    )
    pd.testing.assert_frame_equal(baseline, changed_labels)


def test_identity_and_target_scoring_fields_are_rejected() -> None:
    for column in (
        "player_name",
        "team",
        "nationality",
        "award_winner",
        "desired_rank",
        "round_reached",
    ):
        with pytest.raises(ValueError, match="prohibited"):
            reject_identity_scoring_columns([column, "shots"])


def test_bootstrap_se_and_count_reliability_shrink_toward_mean() -> None:
    values = np.array([-2.0, 0.0, 2.0])
    standard_errors = np.array([0.2, 2.0, 0.2])
    count_reliability = np.array([0.9, 0.9, 0.9])
    shrunk, reliability = bootstrap_se_shrinkage(
        values,
        standard_errors,
        count_reliability,
        se_constant=1.0,
    )
    center = values.mean()
    assert abs(shrunk[1] - center) <= abs(values[1] - center)
    assert reliability[1] < reliability[0]
    assert reliability[1] < reliability[2]
    assert np.all((reliability >= 0.0) & (reliability <= 1.0))


def test_config_rejects_unregistered_or_uncoupled_regions() -> None:
    with pytest.raises(ValueError, match="variance share"):
        OutfieldV4Config(variance_share_target=0.60)
    with pytest.raises(ValueError, match="symmetric"):
        OutfieldV4Config(mixture_lower=0.20, mixture_upper=0.70)
    with pytest.raises(ValueError, match="nonnegative"):
        OutfieldV4Config(prevention_weight=-0.1)


def test_role_mixture_does_not_mutate_v3_inputs() -> None:
    frame = _role_frame()
    frame["attack_component_v3"] = [1.0, 0.2, 0.6, 0.4]
    before = frame.copy(deep=True)
    continuous_role_mixture(frame)
    pd.testing.assert_frame_equal(frame, before)
