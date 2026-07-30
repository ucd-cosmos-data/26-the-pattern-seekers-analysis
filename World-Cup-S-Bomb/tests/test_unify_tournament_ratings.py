"""Tests for the clean unified tournament-rating export."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.unify_tournament_ratings import (
    OUTPUT_COLUMNS,
    attach_unified_tournament_ratings,
    process_world_cup_ratings,
    sample_world_cup_data,
)


def test_output_has_exact_clean_schema() -> None:
    output = process_world_cup_ratings(sample_world_cup_data())

    assert output.columns.tolist() == OUTPUT_COLUMNS
    assert output["Tournament Performance Score"].between(0.0, 1.0).all()
    assert output["Global Rank"].min() == 1
    ranked = output["Global Rank"].dropna().astype(int)
    assert ranked.is_unique
    assert sorted(ranked.tolist()) == list(range(1, len(ranked) + 1))
    assert not any(
        token in column.lower()
        for column in output
        for token in ("raw", "v1", "v2", "shrunk", "z_pos", "vaep")
    )


def test_sample_preserves_star_output_and_team_production_order() -> None:
    output = process_world_cup_ratings(sample_world_cup_data())
    indexed = output.set_index("Player")

    assert output.iloc[0]["Player"] == "Lionel Messi"
    assert indexed.loc["Kylian Mbappé", "Global Rank"] <= 3
    assert (
        indexed.loc["Michy Batshuayi", "Team Rank"]
        < indexed.loc["Low-minute Forward", "Team Rank"]
    )
    assert (
        indexed.loc["Enzo Fernández", "Team Rank"]
        < indexed.loc["Cristian Romero", "Team Rank"]
    )


def test_transform_is_player_name_invariant() -> None:
    source = sample_world_cup_data()
    renamed = source.copy()
    renamed["Player"] = [f"Anonymous {index}" for index in range(len(renamed))]

    original = process_world_cup_ratings(source)
    challenger = process_world_cup_ratings(renamed)

    pd.testing.assert_series_equal(
        original["Tournament Performance Score"],
        challenger["Tournament Performance Score"],
        check_names=False,
    )
    pd.testing.assert_series_equal(
        original["Global Rank"],
        challenger["Global Rank"],
        check_names=False,
    )


def test_each_transformation_records_a_release_gate() -> None:
    output = process_world_cup_ratings(sample_world_cup_data())
    steps = output.attrs["validation"]["steps"]

    assert {
        "adaptive_90_minute_shrinkage",
        "exposure_saturation",
        "defensive_vaep_floor",
        "within_position_z_score",
        "direct_defensive_evidence",
        "upper_tail_cdf",
        "publication_exposure_safeguard",
        "attacking_realization",
        "goalkeeper_quantile_bridge",
    } <= set(steps)
    assert all("accepted" in audit for audit in steps.values())


def test_attach_preserves_feature_table_and_adds_clean_fields() -> None:
    source = sample_world_cup_data()
    enriched = attach_unified_tournament_ratings(source)

    assert set(source.columns) <= set(enriched.columns)
    assert {
        "Global Rank",
        "Team Rank",
        "Tournament Performance Score",
    } <= set(enriched.columns)
    assert enriched["Player"].equals(source["Player"])


def test_attach_is_idempotent() -> None:
    once = attach_unified_tournament_ratings(sample_world_cup_data())
    twice = attach_unified_tournament_ratings(once)

    pd.testing.assert_frame_equal(
        once[
            [
                "Global Rank",
                "Team Rank",
                "Tournament Performance Score",
            ]
        ],
        twice[
            [
                "Global Rank",
                "Team Rank",
                "Tournament Performance Score",
            ]
        ],
    )


def test_production_goalkeeper_bridge_restores_mbappe_and_bounds_gk() -> None:
    source_path = (
        Path(__file__).resolve().parents[1]
        / "results/reports/ranking/player_rankings.csv"
    )
    if not source_path.is_file():
        return
    output = process_world_cup_ratings(pd.read_csv(source_path)).set_index(
        "Player"
    )

    assert int(output.loc["Kylian Mbappé Lottin", "Global Rank"]) == 2
    assert int(output.loc["Dominik Livaković", "Global Rank"]) > 10
    assert (
        int(output.loc["Dominik Livaković", "Global Rank"])
        < int(output.loc["Damián Emiliano Martínez", "Global Rank"])
    )
    validation = output.attrs["validation"]["generalized_validation"]
    assert (
        validation[
            "heavy_defender_share_at_or_above_60th_team_percentile"
        ]
        >= 0.65
    )
    assert (
        validation[
            "heavy_defender_share_in_60th_to_90th_team_percentile"
        ]
        >= 0.40
    )
