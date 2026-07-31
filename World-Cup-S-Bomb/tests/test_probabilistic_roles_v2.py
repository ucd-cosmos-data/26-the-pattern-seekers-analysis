"""Tests for K/covariance GMM role discovery."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import RoleDiscoveryConfig
from src.models.roles import fit_probabilistic_roles


def test_gmm_searches_all_requested_structures_and_outputs_probabilities() -> None:
    rng = np.random.default_rng(42)
    rows = []
    for cluster, center in enumerate((0.1, 0.5, 0.9)):
        for offset in range(20):
            rows.append(
                {
                    "player_id": 100 * cluster + offset,
                    "player": f"P{cluster}-{offset}",
                    "team": f"T{offset % 4}",
                    "position_group": "Central/Wide Midfield",
                    "functional_role": "KMeans baseline",
                    "progression_score": np.clip(
                        rng.normal(center, 0.03),
                        0,
                        1,
                    ),
                    "creation_score": np.clip(
                        rng.normal(center, 0.03),
                        0,
                        1,
                    ),
                    "pressing_score": np.clip(
                        rng.normal(1 - center, 0.03),
                        0,
                        1,
                    ),
                    "ball_security_score": np.clip(
                        rng.normal(center, 0.03),
                        0,
                        1,
                    ),
                }
            )
    profiles = pd.DataFrame(rows)
    config = RoleDiscoveryConfig(
        k_min=2,
        k_max=4,
        covariance_types=("full", "tied", "diag"),
        n_init=2,
        minimum_cluster_size=2,
        pca_components=3,
        bootstrap_iterations=5,
    )
    result = fit_probabilistic_roles(profiles, config=config)
    assert len(result.candidate_metrics) == 9
    assert set(result.candidate_metrics["covariance_type"]) == {
        "full",
        "tied",
        "diag",
    }
    probability_columns = [
        column
        for column in result.assignments
        if column.startswith("role_probability_")
    ]
    assert len(probability_columns) == result.selected_k
    assert np.allclose(
        result.assignments[probability_columns].sum(axis=1),
        1.0,
    )
    assert result.assignments["role_entropy"].between(0, 1).all()
    assert "functional_role" in result.assignments
