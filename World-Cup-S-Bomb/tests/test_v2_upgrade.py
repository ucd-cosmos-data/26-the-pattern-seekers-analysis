"""Regression tests for the World-Cup-S-Bomb v2 upgrade."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.defense_disruption import (
    defensive_action_disruption,
    derive_defense_disruption,
)
from src.features.role_vectors import derive_role_channel_weights
from src.models.composite_calibration import calibrate_composite_weights
from src.models.goalkeeper_valuation import calculate_goalkeeper_ratings
from src.models.valuation import calculate_final_player_rating
from src.simulation_engine import _vaep_feature_matrix


def test_role_channel_weights_follow_semantic_roles() -> None:
    profiles = pd.DataFrame(
        {
            "probabilistic_role": [
                "Progressive Winger",
                "Roaming Creator",
                "Ball-Winning Midfielder",
                "Defensive Centre-Back",
            ],
            "position_group": [
                "Forward",
                "Attacking Midfield/Wing",
                "Defensive Midfield",
                "Center Back",
            ],
        }
    )
    weights = derive_role_channel_weights(profiles)
    assert np.allclose(
        weights["role_off_weight"],
        [0.85, 0.55, 0.35, 0.25],
    )
    assert np.allclose(
        weights["role_off_weight"] + weights["role_def_weight"],
        1.0,
    )


def test_final_rating_uses_weighted_vaep_channels_not_hard_max() -> None:
    rows = 16
    profiles = pd.DataFrame(
        {
            "player_id": range(rows),
            "team": ["A"] * 8 + ["B"] * 8,
            "position_group": ["Forward"] * rows,
            "probabilistic_role": ["Progressive Winger"] * rows,
            "minutes": [360.0] * rows,
            "vaep_total_p90": np.linspace(0.0, 1.0, rows),
            "vaep_off_p90": np.linspace(0.0, 1.0, rows),
            "vaep_def_p90": np.linspace(1.0, 0.0, rows),
            "vaep_per_touch": np.linspace(0.0, 0.1, rows),
            "xt_p90": np.linspace(0.0, 0.5, rows),
            "role_adjusted_value": np.linspace(0.2, 0.8, rows),
            "completeness_score": [0.7] * rows,
            "off_ball_score": [0.5] * rows,
        }
    )
    rated = calculate_final_player_rating(profiles)
    expected = (
        0.85 * rated["vaep_off_scaled"]
        + 0.15 * rated["vaep_def_scaled"]
    )
    assert np.allclose(rated["vaep_component"], expected)
    assert (rated["vaep_component"] < 1.0).all()


def test_goalkeeper_weighting_status_and_eligibility() -> None:
    features = pd.DataFrame(
        {
            "player_id": [1, 2, 3],
            "team": ["A", "B", "C"],
            "minutes": [500.0, 200.0, 89.0],
            "goals_prevented_proxy_p90": [0.8, 0.1, 1.0],
            "save_rate": [0.8, 0.6, 1.0],
            "cross_stopping_rate": [0.5, 0.4, 1.0],
            "sweeper_actions_p90": [0.7, 0.2, 1.0],
            "distribution_under_pressure": [0.8, 0.7, 1.0],
            "penalty_save_rate_shrunk": [0.4, np.nan, 1.0],
            "high_leverage_save_pct": [1.0, 0.0, 1.0],
        }
    )
    rated = calculate_goalkeeper_ratings(features)
    assert set(rated["player_id"]) == {1, 2}
    status = rated.set_index("player_id")["GKRankingStatus"]
    assert status.loc[1] == "Ranked (270+ min)"
    assert status.loc[2] == "Ranked (180–269 min)"
    assert rated.set_index("player_id").loc[1, "goalkeeper_rank"] == 1


def test_xd_rewards_high_threat_defensive_actions() -> None:
    actions = pd.DataFrame(
        {
            "player_id": [1, 2],
            "type_name": ["Interception", "Interception"],
            "start_x": [5.0, 110.0],
            "start_y": [40.0, 40.0],
        }
    )
    scored = defensive_action_disruption(actions)
    assert scored.iloc[0]["disruption_score"] > scored.iloc[1][
        "disruption_score"
    ]
    profiles = pd.DataFrame(
        {
            "player_id": [1, 2],
            "minutes": [90.0, 90.0],
            "position_group": ["Center Back", "Center Back"],
        }
    )
    summary = derive_defense_disruption(actions, profiles).set_index(
        "player_id"
    )
    assert summary.loc[1, "xd90_pct"] > summary.loc[2, "xd90_pct"]


def test_contextual_vaep_features_are_pre_action() -> None:
    actions = pd.DataFrame(
        {
            "game_id": [1, 1, 1],
            "period_id": [1, 1, 1],
            "time_seconds": [60.0, 120.0, 180.0],
            "team": ["A", "A", "B"],
            "type_name": ["Shot", "Pass", "Pass"],
            "play_pattern": ["Regular Play"] * 3,
            "position": ["Forward"] * 3,
            "start_x": [110.0, 50.0, 40.0],
            "start_y": [40.0, 40.0, 40.0],
            "goal": [True, False, False],
            "under_pressure_flag": [False, False, False],
            "defenders_within_5": [0.0] * 3,
            "nearest_defender_distance": [0.0] * 3,
            "defensive_density": [0.0] * 3,
            "defenders_behind_ball": [0.0] * 3,
            "opponent_strength": [0.8] * 3,
            "game_phase_knockout": [1] * 3,
        }
    )
    matrix, names = _vaep_feature_matrix(actions)
    assert {
        "goal_diff",
        "match_minute",
        "opponent_strength",
        "game_phase_knockout",
    } <= set(names)
    assert matrix.loc[0, "goal_diff"] == 0.0
    assert matrix.loc[1, "goal_diff"] == 1.0
    assert matrix.loc[2, "goal_diff"] == -1.0


def test_composite_calibration_is_team_disjoint_and_normalized() -> None:
    rng = np.random.default_rng(42)
    rows = 60
    profiles = pd.DataFrame(
        {
            "team": np.repeat([f"T{i}" for i in range(10)], 6),
            "position_group": ["Forward"] * rows,
            "minutes": rng.uniform(45, 700, rows),
            "goals": rng.integers(0, 5, rows),
            "xa_sum": rng.uniform(0, 3, rows),
            "vaep_component": rng.uniform(0, 1, rows),
            "vaep_per_touch": rng.normal(0, 0.1, rows),
            "xt_p90": rng.uniform(0, 1, rows),
            "role_adjusted_value": rng.uniform(0, 1, rows),
            "completeness_score": rng.uniform(0, 1, rows),
            "off_ball_score": rng.uniform(0, 1, rows),
        }
    )
    incumbent = {
        "vaep_90": 0.40,
        "vaep_per_touch": 0.15,
        "xt_90": 0.15,
        "role_adjusted_value": 0.15,
        "completeness_score": 0.10,
        "off_ball_score": 0.05,
    }
    weights, diagnostics = calibrate_composite_weights(
        profiles,
        incumbent,
    )
    assert np.isclose(sum(weights.values()), 1.0)
    for fold in diagnostics["fold_audit"]:
        assert set(fold["training_teams"]).isdisjoint(
            fold["validation_teams"]
        )
