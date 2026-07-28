"""Goalkeeper bifurcation and leakage tests."""

from __future__ import annotations

import pandas as pd

from src.features.goalkeepers import build_goalkeeper_features


def test_goalkeeper_features_exclude_shootouts_and_outfield_dimensions() -> None:
    events = pd.DataFrame(
        {
            "match_id": [1, 1, 1, 1, 1, 1],
            "period": [1, 1, 1, 1, 5, 1],
            "team": ["A", "B", "B", "A", "B", "A"],
            "player_id": [10, 20, 21, 10, 21, 10],
            "position": ["Goalkeeper", "Forward", "Goalkeeper", "Goalkeeper", "Forward", "Goalkeeper"],
            "type": ["Pass", "Shot", "Goal Keeper", "Goal Keeper", "Shot", "Pass"],
            "shot_outcome": [None, "Saved", None, None, "Goal", None],
            "shot_statsbomb_xg": [None, 0.4, None, None, 0.76, None],
            "shot_type": [None, "Open Play", None, None, "Penalty", None],
            "shot_end_location": [None, "[119, 40, 1]", None, None, "[120, 40, 1]", None],
            "shot_body_part": [None, "Right Foot", None, None, "Right Foot", None],
            "shot_technique": [None, "Normal", None, None, "Normal", None],
            "goalkeeper_type": [None, None, "Shot Saved", "Collected", None, None],
            "under_pressure": [False, False, False, False, False, True],
            "pass_outcome": [None, None, None, None, None, None],
            "location": ["[10, 40]", "[100, 40]", "[10, 40]", "[8, 40]", "[100, 40]", "[10, 40]"],
        }
    )
    keepers = pd.DataFrame(
        {
            "player_id": [10, 21],
            "position_group": ["Goalkeeper", "Goalkeeper"],
            "minutes": [90.0, 90.0],
            "team": ["A", "B"],
        }
    )
    features, audit = build_goalkeeper_features(events, keepers)
    assert audit["shootout_shots_excluded"] == 1
    assert not {
        "xg_p90",
        "xa_p90",
        "finishing_score",
        "final_third_occupancy",
    }.intersection(features.columns)
    assert set(features["player_id"]) == {10, 21}
