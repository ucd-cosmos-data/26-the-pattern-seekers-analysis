"""Regression tests for the Qatar 2022 position-aware ranking layer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models.tournament_rankings import (
    calculate_tournament_rankings_v2,
    role_consistency_violations,
    tournament_ranking_audit,
)
from src.reporting.artifacts import ArtifactGenerator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _canonical_source() -> Path:
    candidates = (
        PROJECT_ROOT / "results/reports/ranking/player_rankings.csv",
        PROJECT_ROOT / "results/reports/canonical/player_rankings.csv",
    )
    return next(path for path in candidates if path.is_file())


def test_qatar_2022_eyes_tests_pass_without_name_based_scoring() -> None:
    source = pd.read_csv(_canonical_source())
    ranked = calculate_tournament_rankings_v2(source)
    audit = tournament_ranking_audit(ranked, strict=True)

    assert audit["passed"]
    assert audit["before_after"]["harry_kane"]["new_team_rank"] <= 2
    assert audit["before_after"]["harry_kane"]["new_global_rank"] <= 10
    assert audit["before_after"]["robert_lewandowski"]["new_team_rank"] <= 2
    assert audit["before_after"]["robert_lewandowski"]["new_global_rank"] <= 20
    assert not role_consistency_violations(ranked)
    assert ranked["tournament"].eq("2022_World_Cup").all()
    assert ranked["position_group_360"].isin(
        ["GK", "CB", "FB", "DM", "CM", "AM", "FW"]
    ).all()
    goalkeepers = ranked.loc[ranked["position_group_360"].eq("GK")]
    ranked_goalkeepers = goalkeepers.loc[
        goalkeepers["gk_rank_v2"].notna()
    ]
    assert len(ranked_goalkeepers) == 32
    assert ranked_goalkeepers["team"].is_unique
    assert ranked_goalkeepers["is_main_goalkeeper"].all()
    assert goalkeepers.loc[
        ~goalkeepers["is_main_goalkeeper"].astype(bool)
    ]["gk_rank_v2"].isna().all()
    required_gk_columns = {
        "psxg_ga_p90",
        "psxg_ga_p90_percentile",
        "penalties_saved_rate",
        "penalties_saved_rate_percentile",
        "save_rate_shrunk",
        "high_leverage_save_rate_shrunk",
        "tournament_impact_score",
        "gk_score_composite",
        "reliability_factor",
    }
    assert required_gk_columns <= set(ranked_goalkeepers.columns)
    assert ranked_goalkeepers["gk_rating_v2"].between(0.0, 1.0).all()


def test_player_name_does_not_change_v2_score() -> None:
    source = pd.read_csv(_canonical_source())
    kane = source.loc[
        source["player_name"].eq("Harry Kane")
    ].iloc[0]
    clone = kane.copy()
    clone["player_name"] = "Anonymous Tournament Forward"
    clone["player"] = "Anonymous Tournament Forward"
    clone["player_id"] = -999
    clone["team"] = "Synthetic Team"
    comparison = pd.DataFrame([kane, clone]).reset_index(drop=True)

    ranked = calculate_tournament_rankings_v2(comparison)

    assert ranked.loc[0, "raw_player_rating_v2"] == ranked.loc[
        1, "raw_player_rating_v2"
    ]
    assert ranked.loc[0, "goal_role_boost_v2"] == ranked.loc[
        1, "goal_role_boost_v2"
    ]


def test_goalkeeper_name_does_not_change_v2_score() -> None:
    source = pd.read_csv(_canonical_source())
    keeper = source.loc[
        source["position_group"].eq("Goalkeeper")
        & source["minutes"].ge(300.0)
    ].iloc[0]
    clone = keeper.copy()
    clone["player_name"] = "Anonymous Tournament Goalkeeper"
    clone["player"] = "Anonymous Tournament Goalkeeper"
    clone["player_id"] = -998
    clone["team"] = "Synthetic Team"
    comparison = pd.DataFrame([keeper, clone]).reset_index(drop=True)

    ranked = calculate_tournament_rankings_v2(comparison)

    assert ranked.loc[0, "gk_raw_rating_v2"] == ranked.loc[
        1, "gk_raw_rating_v2"
    ]
    assert ranked.loc[0, "tournament_impact_score"] == ranked.loc[
        1, "tournament_impact_score"
    ]


def test_300_minute_source_is_explicit_tournament_alias() -> None:
    source = pd.read_csv(_canonical_source()).head(25)
    ranked = calculate_tournament_rankings_v2(source)

    pd.testing.assert_series_equal(
        ranked["minutes_played"],
        pd.to_numeric(ranked["minutes"], errors="coerce"),
        check_names=False,
    )


def test_dedicated_ranking_artifacts_and_32_team_files(
    tmp_path: Path,
) -> None:
    source = pd.read_csv(_canonical_source())
    ranked = calculate_tournament_rankings_v2(source)

    files = ArtifactGenerator(tmp_path)._write_ranking_artifacts(ranked)

    required = {
        tmp_path / "ranking/global_rankings_outfield.csv",
        tmp_path / "ranking/global_rankings_outfield_300min.csv",
        tmp_path / "ranking/goalkeeper_rankings.csv",
        tmp_path / "ranking/ranking_methodology.md",
        tmp_path / "ranking/ranking_audit.md",
        tmp_path / "ranking/ranking_audit.json",
    }
    assert required <= set(files)
    assert len(list((tmp_path / "ranking/by_team").glob("*.csv"))) == 32
    outfield = pd.read_csv(
        tmp_path / "ranking/global_rankings_outfield.csv"
    )
    goalkeepers = pd.read_csv(
        tmp_path / "ranking/goalkeeper_rankings.csv"
    )
    assert outfield["position_group_360"].ne("GK").all()
    assert goalkeepers["position_group_360"].eq("GK").all()
    assert len(goalkeepers) == 32
    assert goalkeepers["team"].is_unique
    assert goalkeepers["is_main_goalkeeper"].all()
