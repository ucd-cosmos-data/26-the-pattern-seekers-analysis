from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd
import pytest

from src.models.outfield_tournament_impact_v4 import (
    REQUIRED_DEFENSIVE_PIPELINE_STAGES,
    DefensivePipeline,
    OutfieldV4Config,
    add_reporting_ranks,
    bootstrap_se_shrinkage,
    channel_count_reliability,
    continuous_role_mixture,
    reject_identity_scoring_columns,
    variance_balanced_composite,
)


def _mixture_input() -> pd.DataFrame:
    rows = 9
    frame = pd.DataFrame(
        {
            "player_id": np.arange(100, 100 + rows),
            "player_name": [f"Player {index}" for index in range(rows)],
            "team": [f"Team {index % 3}" for index in range(rows)],
            "nationality": [f"Nation {index % 4}" for index in range(rows)],
            "position_group": ["Center Back"] * rows,
            "shots": np.linspace(0.0, 18.0, rows),
            "key_passes": np.linspace(0.0, 12.0, rows),
            "progressive_carries": np.linspace(1.0, 20.0, rows),
            "progressive_passes": np.linspace(2.0, 28.0, rows),
            "final_third_passes": np.linspace(1.0, 32.0, rows),
            "box_passes": np.linspace(0.0, 10.0, rows),
            "interceptions": np.linspace(18.0, 0.0, rows),
            "blocks": np.linspace(15.0, 0.0, rows),
            "clearances": np.linspace(30.0, 1.0, rows),
            "pressures": np.linspace(40.0, 8.0, rows),
            "recoveries": np.linspace(35.0, 5.0, rows),
            "duels_won": np.linspace(28.0, 4.0, rows),
            "aerial_wins": np.linspace(20.0, 1.0, rows),
            "average_x": np.linspace(25.0, 85.0, rows),
        }
    )
    frame["role_probability_01"] = np.linspace(0.90, 0.10, rows)
    frame["role_probability_02"] = 1.0 - frame["role_probability_01"]
    for role in range(3, 17):
        frame[f"role_probability_{role:02d}"] = 0.0
    return frame


def _pipeline_before_scaling(values: np.ndarray) -> DefensivePipeline:
    return (
        DefensivePipeline(values)
        .opposition_adjust(values + 0.15)
        .augment_prevention(values + 0.25)
        .shrink_reliability(values * 0.75)
    )


def test_config_is_frozen_and_strictly_validated() -> None:
    config = OutfieldV4Config()

    assert dataclasses.is_dataclass(config)
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.variance_share_target = 0.50  # type: ignore[misc]
    with pytest.raises(ValueError, match="variance share"):
        OutfieldV4Config(variance_share_target=0.51)
    with pytest.raises(ValueError, match="symmetric"):
        OutfieldV4Config(mixture_lower=0.20, mixture_upper=0.70)
    with pytest.raises(ValueError, match="positive"):
        OutfieldV4Config(defense_reliability_constant=0.0)


def test_defensive_pipeline_enforces_the_exact_stage_order() -> None:
    values = np.array([-1.0, -0.2, 0.4, 1.2])
    pipeline = DefensivePipeline(values)

    with pytest.raises(RuntimeError, match="expected 'opposition_adjusted'"):
        pipeline.augment_prevention(values)
    assert pipeline.stage_history == []
    with pytest.raises(RuntimeError, match="incomplete or out of order"):
        pipeline.assert_complete()

    w_att = np.array([0.65, 0.55, 0.45, 0.35])
    w_def = 1.0 - w_att
    attack = np.array([-0.5, 0.1, 0.8, 1.7])
    (
        pipeline.opposition_adjust(values + 0.10)
        .augment_prevention(values + 0.20)
        .shrink_reliability(values * 0.80)
        .variance_rescale(
            attack,
            w_att,
            w_def,
            target_share=0.42,
        )
        .mixture_weight(w_def)
    )

    pipeline.assert_complete()
    assert tuple(pipeline.stage_history) == REQUIRED_DEFENSIVE_PIPELINE_STAGES


@pytest.mark.parametrize("target", [0.35, 0.42, 0.50])
def test_variance_scaling_hits_each_preregistered_share(target: float) -> None:
    defense = np.array([-1.5, -0.6, -0.1, 0.4, 0.9, 1.8])
    attack = np.array([-0.7, -0.2, 0.3, 0.9, 1.4, 2.2])
    w_att = np.array([0.70, 0.62, 0.56, 0.48, 0.38, 0.28])
    w_def = 1.0 - w_att
    pipeline = _pipeline_before_scaling(defense)

    pipeline.variance_rescale(
        attack,
        w_att,
        w_def,
        target_share=target,
    )
    assert pipeline.metadata["defensive_variance_share_v4"] == pytest.approx(
        target, abs=1e-12
    )
    pipeline.mixture_weight(w_def)
    weighted_defense = pipeline.values
    attack_variance = np.var(w_att * attack, ddof=0)
    defense_variance = np.var(weighted_defense, ddof=0)
    realized = defense_variance / (attack_variance + defense_variance)

    assert realized == pytest.approx(target, abs=1e-12)
    assert realized <= 0.50 + 1e-12
    pipeline.assert_complete()


def test_composite_rejects_raw_or_out_of_order_defense() -> None:
    frame = pd.DataFrame(
        {
            "defensive_value_raw_v4": [0.1, 0.2],
            "defensive_value_opposition_adjusted_v4": [0.05, 0.15],
            "attacking_component_reliable_v4": [0.5, 1.0],
            "attacking_channel_weight_v4": [0.6, 0.4],
            "defending_channel_weight_v4": [0.4, 0.6],
        }
    )

    with pytest.raises(ValueError, match="raw defense is rejected"):
        variance_balanced_composite(
            frame,
            defensive_input_column="defensive_value_raw_v4",
            defensive_pipeline_stages=REQUIRED_DEFENSIVE_PIPELINE_STAGES,
        )
    with pytest.raises(ValueError, match="missing or out of order"):
        variance_balanced_composite(
            frame,
            defensive_input_column="defensive_value_opposition_adjusted_v4",
            defensive_pipeline_stages=tuple(
                reversed(REQUIRED_DEFENSIVE_PIPELINE_STAGES)
            ),
        )


def test_continuous_mixture_is_bounded_sums_to_one_and_identity_invariant() -> None:
    frame = _mixture_input()
    snapshot = frame.copy(deep=True)

    first = continuous_role_mixture(frame, lower=0.25, upper=0.75)
    second = continuous_role_mixture(frame, lower=0.25, upper=0.75)
    changed_identity = frame.copy()
    changed_identity["player_id"] = changed_identity["player_id"][::-1].to_numpy()
    changed_identity["player_name"] = changed_identity["player_name"][
        ::-1
    ].to_numpy()
    changed_identity["team"] = "Completely Different Team"
    changed_identity["nationality"] = "Completely Different Nation"
    identity_result = continuous_role_mixture(
        changed_identity, lower=0.25, upper=0.75
    )

    pd.testing.assert_frame_equal(first, second)
    pd.testing.assert_frame_equal(first, identity_result)
    pd.testing.assert_frame_equal(frame, snapshot)
    assert first["attacking_channel_weight_v4"].between(0.25, 0.75).all()
    assert first["defending_channel_weight_v4"].between(0.25, 0.75).all()
    np.testing.assert_allclose(
        first["attacking_channel_weight_v4"]
        + first["defending_channel_weight_v4"],
        1.0,
        rtol=0.0,
        atol=1e-12,
    )
    assert first["role_orientation_attacking_v4"].nunique() > 3


@pytest.mark.parametrize(
    "column",
    ["player_name", "team", "nationality", "target_rank", "winner_bonus"],
)
def test_identity_and_target_columns_are_rejected_from_scoring(
    column: str,
) -> None:
    with pytest.raises(ValueError, match="prohibited"):
        reject_identity_scoring_columns([column])


def test_bootstrap_se_and_evidence_control_shrinkage_toward_mean() -> None:
    values = np.array([-2.0, 0.0, 2.0])
    center = values.mean()
    low_evidence = channel_count_reliability(
        np.array([1.0, 1.0, 1.0]), constant=100.0
    )
    high_evidence = channel_count_reliability(
        np.array([1000.0, 1000.0, 1000.0]), constant=100.0
    )
    low_quality, low_reliability = bootstrap_se_shrinkage(
        values,
        np.array([2.0, 2.0, 2.0]),
        low_evidence,
        se_constant=1.0,
    )
    high_quality, high_reliability = bootstrap_se_shrinkage(
        values,
        np.array([0.05, 0.05, 0.05]),
        high_evidence,
        se_constant=1.0,
    )

    assert np.all(high_reliability > low_reliability)
    assert abs(high_quality[0] - center) > abs(low_quality[0] - center)
    assert abs(high_quality[2] - center) > abs(low_quality[2] - center)
    zero_evidence = channel_count_reliability(
        np.zeros(3), constant=100.0
    )
    fully_shrunk, reliability = bootstrap_se_shrinkage(
        values,
        np.zeros(3),
        zero_evidence,
        se_constant=1.0,
    )
    np.testing.assert_allclose(fully_shrunk, center)
    np.testing.assert_allclose(reliability, 0.0)


def test_core_operations_do_not_mutate_v3_columns() -> None:
    frame = _mixture_input().iloc[:6].copy()
    frame["attack_component_v3"] = np.linspace(0.2, 1.2, len(frame))
    frame["defensive_component_v3"] = np.linspace(-0.2, 0.3, len(frame))
    frame["global_rank_v3"] = np.arange(1, len(frame) + 1)
    v3_columns = [column for column in frame if column.endswith("_v3")]
    v3_snapshot = frame[v3_columns].copy(deep=True)

    mixture = continuous_role_mixture(frame)
    scoring = frame.join(mixture)
    defense = np.linspace(-1.0, 1.0, len(frame))
    pipeline = _pipeline_before_scaling(defense)
    pipeline.variance_rescale(
        scoring["attack_component_v3"],
        scoring["attacking_channel_weight_v4"],
        scoring["defending_channel_weight_v4"],
        target_share=0.42,
    ).mixture_weight(scoring["defending_channel_weight_v4"])
    pipeline.assert_complete()
    scoring["attacking_component_reliable_v4"] = scoring[
        "attack_component_v3"
    ]
    scoring["defensive_value_opposition_adjusted_v4"] = pipeline.values
    scoring["tournament_impact_score_outfield_v4"] = (
        variance_balanced_composite(
            scoring,
            defensive_input_column=(
                "defensive_value_opposition_adjusted_v4"
            ),
            defensive_pipeline_stages=pipeline.stage_history,
        )
    )
    ranked = add_reporting_ranks(scoring)

    pd.testing.assert_frame_equal(frame[v3_columns], v3_snapshot)
    pd.testing.assert_frame_equal(ranked[v3_columns], v3_snapshot)

