"""Tests for metric 360 geometry, occupancy, and passing graphs."""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

from src.features.network import build_passing_network_features
from src.features.spatial import (
    SpatialFeatureTransformer,
    build_event_freeze_frame_features,
    build_event_freeze_frame_features_from_csv,
    calculate_freeze_frame_geometry,
    calculate_zone_control,
)


def test_metric_defender_thresholds_and_lane_geometry() -> None:
    actor = np.array([60.0, 40.0])
    # About 2.6m, 4.4m, and 8.8m ahead on the pitch.
    defenders = np.array([[63.0, 40.0], [65.0, 40.0], [70.0, 40.0]])
    geometry = calculate_freeze_frame_geometry(
        actor,
        defenders,
        target_coordinates=np.array([80.0, 40.0]),
    )
    assert geometry.sb360_available
    assert geometry.defenders_within_3m == 1
    assert geometry.defenders_within_5m == 2
    assert geometry.passing_lane_availability == 0.0
    assert geometry.packing_index == 3


def test_missing_360_remains_missing() -> None:
    geometry = calculate_freeze_frame_geometry(None, None)
    assert not geometry.sb360_available
    assert np.isnan(geometry.defenders_within_3m)
    assert np.isnan(geometry.nearest_defender_m)


def test_event_freeze_frame_join_preserves_missingness_and_uuid() -> None:
    events = pd.DataFrame(
        {
            "match_id": [1, 1],
            "id": ["observed", "missing"],
            "location": ["[60, 40]", "[20, 20]"],
            "pass_end_location": ["[80, 40]", "[40, 20]"],
        }
    )
    frames = pd.DataFrame(
        {
            "match_id": [1, 1, 1],
            "event_uuid": ["observed"] * 3,
            "teammate": [True, False, False],
            "actor": [True, False, False],
            "keeper": [False, False, False],
            "x": [60, 63, 70],
            "y": [40, 40, 40],
        }
    )
    geometry = build_event_freeze_frame_features(events, frames)
    assert geometry["event_uuid"].tolist() == ["observed"]
    assert geometry.loc[0, "sb360_available"]
    assert geometry.loc[0, "defenders_within_3m"] == 1


def test_vectorized_360_csv_matches_direct_geometry(tmp_path: Path) -> None:
    events = pd.DataFrame(
        {
            "match_id": [1],
            "id": ["observed"],
            "location": ["[60, 40]"],
            "pass_end_location": ["[80, 40]"],
        }
    )
    frames = pd.DataFrame(
        {
            "match_id": [1, 1, 1],
            "event_uuid": ["observed"] * 3,
            "teammate": [True, False, False],
            "actor": [True, False, False],
            "keeper": [False, False, False],
            "x": [60, 63, 70],
            "y": [40, 40, 40],
        }
    )
    path = tmp_path / "frames.csv"
    frames.to_csv(path, index=False)
    direct = build_event_freeze_frame_features(events, frames).iloc[0]
    vectorized = build_event_freeze_frame_features_from_csv(
        events,
        path,
        chunksize=2,
    ).iloc[0]
    for column in (
        "defenders_within_3m",
        "defenders_within_5m",
        "nearest_defender_m",
        "packing_index",
        "passing_lane_availability",
    ):
        assert np.isclose(direct[column], vectorized[column])


def test_spatial_feature_matrix_has_120x80_kde_reduction() -> None:
    actions = pd.DataFrame(
        {
            "player_id": [1, 1, 1, 2, 2, 2],
            "start_x": [10, 50, 90, 20, 60, 100],
            "start_y": [10, 40, 70, 70, 40, 10],
        }
    )
    transformer = SpatialFeatureTransformer().fit(actions)
    features = transformer.transform(actions)
    kde_columns = [column for column in features if column.startswith("kde_")]
    assert features["player_id"].nunique() == 2
    assert len(kde_columns) == 96
    assert np.allclose(features[kde_columns].sum(axis=1), 1.0)


def test_zone_control_masks_unobserved_pitch() -> None:
    team = np.array([[0.7, 0.2]])
    opponent = np.array([[0.1, 0.5]])
    visible = np.array([[True, False]])
    control = calculate_zone_control(team, opponent, visible)
    assert np.isclose(control[0, 0], 0.6)
    assert np.isnan(control[0, 1])


def test_passing_network_known_chain() -> None:
    events = pd.DataFrame(
        {
            "match_id": [1, 1, 1, 1],
            "index": [1, 2, 3, 4],
            "team": ["A"] * 4,
            "possession": [1] * 4,
            "type": ["Pass"] * 4,
            "player_id": [1, 2, 2, 3],
            "pass_recipient_id": [2, 3, 1, 1],
            "pass_outcome": [np.nan] * 4,
            "location": ["[20,40]", "[40,40]", "[50,40]", "[70,40]"],
            "pass_end_location": [
                "[40,40]",
                "[85,40]",
                "[60,40]",
                "[90,40]",
            ],
        }
    )
    features = build_passing_network_features(events)
    assert set(features["player_id"]) == {1, 2, 3}
    assert features["network_pagerank"].between(0, 1).all()
    assert features["network_entropy"].between(0, 1).all()
    player_two = features.loc[features["player_id"].eq(2)].iloc[0]
    assert player_two["build_up_involvement_ratio"] == 1.0
