"""Publication-contract tests for the goalkeeper percentile bridge."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.run_ranking_repair_v3 import _merge_v3_outputs
from src.reporting.ranking_repair_release import (
    RankingRepairReleaseWriter,
)


def _release_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    outfield_count = 553
    outfield_score = np.linspace(1.0, 0.0, outfield_count) ** 3
    outfield = pd.DataFrame(
        {
            "player_id": np.arange(1, outfield_count + 1),
            "player_name": [
                f"Outfield {index}"
                for index in range(1, outfield_count + 1)
            ],
            "team": [
                f"Team {index % 32:02d}"
                for index in range(outfield_count)
            ],
            "position_group": "Forward",
            "functional_role": "Synthetic outfield role",
            "minutes_played": 360.0,
            "tournament_impact_raw_v3": outfield_score,
            "tournament_impact_v3": outfield_score,
            "tournament_impact_score_v3": outfield_score,
            "role_quality_v3": outfield_score,
            "global_rank_v3": np.arange(1, outfield_count + 1),
            "team_rank_v3": 1,
            "position_rank_v3": np.arange(1, outfield_count + 1),
            "role_rank_v3": np.arange(1, outfield_count + 1),
            "uncertainty_low_v3": outfield_score - 0.01,
            "uncertainty_high_v3": outfield_score + 0.01,
            "uncertainty_status_v3": "stable",
            "is_main_goalkeeper": False,
        }
    )

    goalkeeper_rows: list[dict[str, object]] = []
    goalkeeper_ratings: list[dict[str, object]] = []
    first_goalkeeper_id = outfield_count + 1
    for rank in range(1, 33):
        player_id = first_goalkeeper_id + rank - 1
        team = f"GK Team {rank:02d}"
        goalkeeper_rows.append(
            {
                "player_id": player_id,
                "player_name": f"Main Goalkeeper {rank:02d}",
                "team": team,
                "position_group": "Goalkeeper",
                "functional_role": "Goalkeeper",
                "minutes_played": 360.0,
                "tournament_impact_raw_v3": np.nan,
                "tournament_impact_v3": np.nan,
                "tournament_impact_score_v3": np.nan,
                "role_quality_v3": np.nan,
                "global_rank_v3": pd.NA,
                "team_rank_v3": pd.NA,
                "position_rank_v3": pd.NA,
                "role_rank_v3": pd.NA,
                "uncertainty_low_v3": np.nan,
                "uncertainty_high_v3": np.nan,
                "uncertainty_status_v3": "not-estimated",
                "is_main_goalkeeper": True,
            }
        )
        goalkeeper_ratings.append(
            {
                "player_id": player_id,
                "team": team,
                "is_main_goalkeeper": True,
                "goalkeeper_rank_v3": rank,
                "dedicated_goalkeeper_score_v3": 1.0 - rank / 40.0,
                "percentile_equivalent_placement": (
                    32.0 - rank + 0.5
                )
                / 32.0,
                "goalkeeper_score_interval_low_v3": 0.3,
                "goalkeeper_score_interval_high_v3": 0.7,
                "goalkeeper_uncertainty_status_v3": "stable",
            }
        )

    for backup in range(8):
        player_id = first_goalkeeper_id + 32 + backup
        team = f"GK Team {backup + 1:02d}"
        goalkeeper_rows.append(
            {
                "player_id": player_id,
                "player_name": f"Backup Goalkeeper {backup + 1:02d}",
                "team": team,
                "position_group": "Goalkeeper",
                "functional_role": "Goalkeeper",
                "minutes_played": 20.0,
                "tournament_impact_raw_v3": np.nan,
                "tournament_impact_v3": np.nan,
                "tournament_impact_score_v3": np.nan,
                "role_quality_v3": np.nan,
                "global_rank_v3": pd.NA,
                "team_rank_v3": pd.NA,
                "position_rank_v3": pd.NA,
                "role_rank_v3": pd.NA,
                "uncertainty_low_v3": np.nan,
                "uncertainty_high_v3": np.nan,
                "uncertainty_status_v3": "not-estimated",
                "is_main_goalkeeper": False,
            }
        )
        goalkeeper_ratings.append(
            {
                "player_id": player_id,
                "team": team,
                "is_main_goalkeeper": False,
                "goalkeeper_rank_v3": pd.NA,
                "dedicated_goalkeeper_score_v3": np.nan,
                "percentile_equivalent_placement": np.nan,
                "goalkeeper_score_interval_low_v3": np.nan,
                "goalkeeper_score_interval_high_v3": np.nan,
                "goalkeeper_uncertainty_status_v3": (
                    "unranked-backup-goalkeeper"
                ),
            }
        )

    base = pd.concat(
        [outfield, pd.DataFrame(goalkeeper_rows)],
        ignore_index=True,
    )
    return base, outfield, pd.DataFrame(goalkeeper_ratings)


def test_goalkeeper_publication_bridge_uses_outfield_impact_quantiles() -> None:
    base, outfield, goalkeepers = _release_inputs()
    final = _merge_v3_outputs(base, outfield, goalkeepers)
    RankingRepairReleaseWriter.validate_frame(final)

    goalkeeper = final["position_group"].eq("Goalkeeper")
    main = goalkeeper & final["is_main_goalkeeper"].fillna(False)
    backup = goalkeeper & ~main
    ranked = final.loc[main].sort_values("gk_rank_v3")
    outfield_scores = (
        pd.to_numeric(
            final.loc[
                ~goalkeeper,
                "tournament_impact_score_v3",
            ],
            errors="coerce",
        )
        .dropna()
        .sort_values()
        .to_numpy()
    )
    placement = pd.to_numeric(
        ranked["percentile_equivalent_placement"],
        errors="coerce",
    ).to_numpy()
    expected = np.quantile(
        outfield_scores,
        placement,
        method="linear",
    )

    np.testing.assert_allclose(
        ranked["percentile_equivalent_score_v3"],
        expected,
        rtol=0.0,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        ranked["publication_score_v3"],
        expected,
        rtol=0.0,
        atol=1e-12,
    )
    assert np.array_equal(
        ranked["gk_rank_v3"].to_numpy(),
        np.arange(1, 33),
    )
    assert ranked["dedicated_goalkeeper_score_v3"].is_monotonic_decreasing
    assert ranked["publication_score_v3"].is_monotonic_decreasing
    assert ranked["publication_global_rank_v3"].is_monotonic_increasing
    assert ranked["team"].nunique() == 32
    assert final.loc[backup, "gk_rank_v3"].isna().all()
    assert final.loc[
        backup,
        "publication_global_rank_v3",
    ].isna().all()
    goalkeeper_top20 = (
        goalkeeper
        & pd.to_numeric(
            final["publication_global_rank_v3"],
            errors="coerce",
        ).le(20)
    ).sum()
    assert goalkeeper_top20 <= 3


def test_release_validation_rejects_raw_percentile_as_publication_score() -> None:
    base, outfield, goalkeepers = _release_inputs()
    final = _merge_v3_outputs(base, outfield, goalkeepers)
    main = (
        final["position_group"].eq("Goalkeeper")
        & final["is_main_goalkeeper"].fillna(False)
    )
    final.loc[main, "publication_score_v3"] = final.loc[
        main,
        "percentile_equivalent_placement",
    ]

    with pytest.raises(
        ValueError,
        match="corresponding quantile of outfield Tournament Impact",
    ):
        RankingRepairReleaseWriter.validate_frame(final)
