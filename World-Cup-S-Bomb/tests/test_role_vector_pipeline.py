"""Tests for continuous role vectors and completeness."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.role_vectors import RoleVectorTransformer, derive_role_vector
from src.models.valuation import calculate_completeness_score


def _profiles() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "player_id": range(1, 7),
            "progressive_carries_p90": [0, 1, 2, 3, 4, 5],
            "progressive_passes_p90": [0, 1, 2, 3, 4, 5],
            "line_breaking_pass_rate": [0, 0.1, 0.2, 0.3, 0.4, 0.5],
            "xt_p90": [0, 1, 2, 3, 4, 5],
            "key_passes_p90": [0, 1, 2, 3, 4, 5],
            "xa_p90": [0, 1, 2, 3, 4, 5],
            "shots_p90": [0, 1, 2, 3, 4, 5],
            "xg_p90": [0, 1, 2, 3, 4, 5],
            "pressing_intensity_index": [5, 4, 3, 2, 1, 0],
            "counterpressures_p90": [5, 4, 3, 2, 1, 0],
            "interceptions_p90": [5, 4, 3, 2, 1, 0],
            "vaep_def_p90": [5, 4, 3, 2, 1, 0],
            "pass_completion": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            "turnovers_p90": [5, 4, 3, 2, 1, 0],
            "aerial_dominance_index": [0, 0.2, 0.4, 0.6, 0.8, 1],
            "aerial_wins_p90": [0, 1, 2, 3, 4, 5],
            "pass_receipt_x": [20, 30, 40, 50, 60, 70],
            "pass_start_x": [10, 20, 30, 40, 50, 60],
        }
    )


def test_role_vectors_are_bounded_and_evidence_aware() -> None:
    profiles = _profiles()
    vectors = derive_role_vector(profiles)
    score_columns = [column for column in vectors if column.endswith("_score")]
    assert score_columns
    assert vectors[score_columns].ge(0).all().all()
    assert vectors[score_columns].le(1).all().all()
    assert vectors["progression_score_evidence_count"].gt(0).all()
    assert vectors["average_receiving_x_available"].all()


def test_role_transformer_uses_training_reference() -> None:
    train = _profiles().iloc[:5]
    held_out = _profiles().iloc[[5]].copy()
    transformer = RoleVectorTransformer().fit(train)
    isolated = transformer.transform(held_out)
    combined = transformer.transform(pd.concat([held_out, held_out]))
    assert np.allclose(
        isolated["progression_score"],
        combined["progression_score"].iloc[:1],
    )


def test_missing_role_input_is_not_fake_zero() -> None:
    profiles = _profiles()
    profiles.loc[0, ["shots_p90", "xg_p90"]] = np.nan
    vectors = derive_role_vector(profiles)
    assert np.isnan(vectors.loc[0, "finishing_score"])
    assert vectors.loc[0, "finishing_score_evidence_count"] == 0


def test_completeness_is_top_k_quality_adjusted() -> None:
    balanced = pd.DataFrame(
        {
            column: [0.5, value, low]
            for column, value, low in zip(
                (
                    "progression_score",
                    "creation_score",
                    "finishing_score",
                    "pressing_score",
                    "defensive_score",
                    "ball_security_score",
                ),
                (1.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                (0.2, 0.2, 0.2, 0.2, 0.2, 0.2),
                strict=True,
            )
        }
    )
    score = calculate_completeness_score(balanced)
    assert np.isclose(score.iloc[0], 0.5)
    assert score.iloc[1] == 0.0
    assert np.isclose(score.iloc[2], 0.2)
