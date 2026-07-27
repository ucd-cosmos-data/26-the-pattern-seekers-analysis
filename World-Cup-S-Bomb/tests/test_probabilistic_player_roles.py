"""Regression tests for the rejected-by-default role/valuation challengers."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.probabilistic_player_roles import (
    PlayerRoleFeatureTransformer,
    build_spatial_features,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_spatial_fingerprint_shape_and_finiteness() -> None:
    actions = pd.DataFrame(
        {
            "player_id": [1, 1, 1, 2, 2, 2],
            "start_x": [10, 50, 90, 20, 60, 100],
            "start_y": [10, 40, 70, 70, 40, 10],
            "defenders_within_5": [0, 1, 2, 0, 2, 3],
            "nearest_defender_distance": [8, 4, 2, 9, 3, 1],
            "defensive_density": [0.01, 0.02, 0.03, 0.01, 0.03, 0.04],
            "defenders_behind_ball": [8, 6, 3, 9, 5, 2],
        }
    )
    features = build_spatial_features(actions)
    assert features["player_id"].nunique() == 2
    assert len([column for column in features if column.startswith("kde_")]) == 96
    assert np.isfinite(
        features.select_dtypes(include=np.number).to_numpy()
    ).all()


def test_transformer_winsorizes_and_returns_stable_shape() -> None:
    frame = pd.DataFrame(
        {
            "player_id": [1, 2, 3, 4],
            "rate": [0.0, 1.0, 2.0, 10_000.0],
            "constant": [1.0, 1.0, 1.0, 1.0],
        }
    )
    transformer = PlayerRoleFeatureTransformer().fit(frame)
    transformed = transformer.transform(frame)
    assert transformed.shape == (4, 1)
    assert np.isfinite(transformed).all()
    assert transformed[-1, 0] < 10_000.0


def test_rejected_challengers_do_not_replace_incumbent_rankings() -> None:
    report = json.loads(
        (
            PROJECT_ROOT
            / "results/reports/player_role_challenger_validation.json"
        ).read_text(encoding="utf-8")
    )
    profiles = pd.read_csv(
        PROJECT_ROOT / "data/processed/player_evaluations.csv"
    )
    assert report["decisions"]["incumbent_rankings_retained"] is True
    assert report["decisions"]["probabilistic_roles"] == "REJECTED"
    assert report["decisions"]["learned_valuation"] == "REJECTED"
    mbappe = profiles[
        profiles["team"].eq("France")
        & profiles["player"].str.contains("Mbapp", case=False, na=False)
    ].iloc[0]
    messi = profiles[
        profiles["team"].eq("Argentina")
        & profiles["player"].str.contains("Messi", case=False, na=False)
    ].iloc[0]
    assert int(mbappe["team_rank"]) == 1
    assert int(messi["team_rank"]) == 1
