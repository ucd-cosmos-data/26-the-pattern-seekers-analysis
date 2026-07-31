"""Tests for continuous role-aware weighting and final rating."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.off_ball import OffBallScorer
from src.models.valuation import (
    ContinuousRoleAwareValuator,
    calculate_final_player_rating,
)


def _role_aware_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "progressive_passes_p90": [0.9, 0.1],
            "key_passes_p90": [0.2, 0.8],
            "pressures_p90": [0.1, 0.9],
            "progression_score": [0.9, 0.1],
            "creation_score": [0.2, 0.8],
            "finishing_score": [0.1, 0.1],
            "pressing_score": [0.1, 0.9],
            "defensive_score": [0.2, 0.7],
            "ball_security_score": [0.7, 0.5],
            "aerial_score": [0.1, 0.1],
        }
    )


def test_role_aware_weights_are_continuous_nonnegative_and_normalized() -> None:
    frame = _role_aware_frame()
    model = ContinuousRoleAwareValuator(
        metric_names=[
            "progressive_passes_p90",
            "key_passes_p90",
            "pressures_p90",
        ]
    ).fit(frame)
    weights = model.metric_weights(frame)
    assert weights.ge(0).all().all()
    assert np.allclose(weights.sum(axis=1), 1.0)
    assert weights.iloc[0]["weight_progressive_passes_p90"] > weights.iloc[1][
        "weight_progressive_passes_p90"
    ]
    assert weights.iloc[1]["weight_pressures_p90"] > weights.iloc[0][
        "weight_pressures_p90"
    ]


def test_off_ball_missingness_shrinks_to_prior_not_zero() -> None:
    profiles = pd.DataFrame(
        {
            "player_id": [1, 2, 3],
            "position_group": ["Forward"] * 3,
            "dangerous_zone_receptions_p90": [1.0, 2.0, np.nan],
            "pressures_p90": [1.0, 2.0, np.nan],
        }
    )
    score = OffBallScorer().fit(profiles).transform(profiles)
    assert score.loc[2, "off_ball_feature_coverage"] == 0
    assert not score.loc[2, "off_ball_score_observed"]
    assert score.loc[2, "off_ball_score"] > 0


def test_final_rating_preserves_legacy_and_adds_all_ranks() -> None:
    profiles = pd.DataFrame(
        {
            "player_id": [1, 2, 3, 4],
            "player": ["A", "B", "C", "D"],
            "team": ["X", "X", "Y", "Y"],
            "position_group": ["Forward", "Forward", "Midfield", "Midfield"],
            "functional_role": ["F", "F", "M", "M"],
            "minutes": [600, 450, 600, 450],
            "vaep_total_p90": [1.0, 0.5, 0.8, 0.3],
            "vaep_per_touch": [0.1, 0.05, 0.08, 0.03],
            "xt_p90": [0.9, 0.4, 0.7, 0.2],
            "role_adjusted_value": [0.9, 0.4, 0.8, 0.3],
            "completeness_score": [0.5, 0.4, 0.9, 0.8],
            "off_ball_score": [0.7, 0.4, 0.8, 0.5],
            "raw_final_player_rating": [10, 9, 8, 7],
            "final_player_rating": [10, 9, 8, 7],
            "team_rank": [1, 2, 1, 2],
        }
    )
    output = calculate_final_player_rating(profiles)
    for column in (
        "legacy_final_player_rating",
        "global_rank",
        "position_rank",
        "role_rank",
        "team_rank",
    ):
        assert column in output
    assert output["final_player_rating"].between(0, 1).all()

