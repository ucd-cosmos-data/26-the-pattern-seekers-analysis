"""Generated-artifact contract tests for the active Qatar 2022 v3 release."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd
import pytest

from src.reporting.artifacts import TEAM_CODES
from src.reporting.ranking_repair_release import (
    ACTIVE_MODEL_VERSION,
    REQUIRED_V3_COLUMNS,
    UNIFIED_COLUMNS,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = PROJECT_ROOT / "results"
REPORTS_ROOT = RESULTS_ROOT / "reports"
RANKING_ROOT = REPORTS_ROOT / "ranking"
CATALOG_ACTIVE_MODEL_VERSION = ACTIVE_MODEL_VERSION


@pytest.fixture(scope="module")
def rich() -> pd.DataFrame:
    return pd.read_csv(RANKING_ROOT / "player_rankings.csv")


@pytest.fixture(scope="module")
def unified() -> pd.DataFrame:
    return pd.read_csv(
        RANKING_ROOT / "unified_tournament_rankings.csv"
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _assert_byte_identical(paths: list[Path]) -> None:
    assert all(path.is_file() for path in paths)
    expected = paths[0].read_bytes()
    for path in paths[1:]:
        assert path.read_bytes() == expected, (
            f"{path.relative_to(PROJECT_ROOT)} is not byte-identical to "
            f"{paths[0].relative_to(PROJECT_ROOT)}"
        )


def _assert_portable_path(value: str) -> None:
    assert value
    assert "\\" not in value
    assert not value.startswith("/")
    assert not re.match(r"^[A-Za-z]:", value)
    assert str(PurePosixPath(value)) == value
    assert ".." not in PurePosixPath(value).parts


def _main_goalkeeper_mask(frame: pd.DataFrame) -> pd.Series:
    return (
        frame["is_main_goalkeeper"]
        .fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "1", "yes"})
    )


def test_feature_rich_release_has_v3_fields_and_rank_order(
    rich: pd.DataFrame,
) -> None:
    required = set(REQUIRED_V3_COLUMNS) | {
        "attack_component_v3",
        "defensive_component_v3",
        "other_component_v3",
        "tournament_impact_score_v3",
        "bootstrap_rank_best_v3",
        "bootstrap_rank_worst_v3",
        "ranking_model_version_v3",
        "ranking_schema_version_v3",
        "ranking_release_status_v3",
        "ordinary_event_periods_v3",
        "shootout_outcomes_used_v3",
        "position_normalization_used_for_impact_v3",
        "team_identity_used_for_score_v3",
        "player_identity_used_for_score_v3",
        "uncertainty_used_as_score_penalty_v3",
        "legacy_fields_status_v3",
        "publication_global_rank_v3",
        "publication_team_rank_v3",
        "active_model_version",
        *UNIFIED_COLUMNS,
    }
    assert required <= set(rich.columns)
    assert len(rich) == 593
    assert rich["player_id"].nunique() == 593
    assert rich["team"].nunique() == 32
    assert rich["active_model_version"].eq(ACTIVE_MODEL_VERSION).all()
    assert rich["event_scope_version"].eq(
        "qatar-2022-periods-1-4-v1"
    ).all()

    logical_score_block = [
        "attack_component_v3",
        "defensive_component_v3",
        "other_component_v3",
        "tournament_impact_v3",
        "global_rank_v3",
        "team_rank_v3",
        "role_quality_v3",
        "position_rank_v3",
        "role_rank_v3",
        "uncertainty_low_v3",
        "uncertainty_high_v3",
        "uncertainty_status_v3",
    ]
    indices = [rich.columns.get_loc(column) for column in logical_score_block]
    assert indices == sorted(indices)

    published = rich.loc[rich["Global Rank"].notna()].copy()
    assert len(published) == 553
    assert published["position_group"].ne("Goalkeeper").all()
    np.testing.assert_array_equal(
        published["Global Rank"].to_numpy(dtype=int),
        np.arange(1, len(published) + 1),
    )
    assert rich.loc[len(published) :, "Global Rank"].isna().all()

    outfield = rich.loc[rich["position_group"].ne("Goalkeeper")]
    assert len(outfield) == 553
    np.testing.assert_array_equal(
        outfield["global_rank_v3"].to_numpy(dtype=int),
        np.arange(1, len(outfield) + 1),
    )
    expected_order = (
        outfield.sort_values(
            ["tournament_impact_raw_v3", "player_id"],
            ascending=[False, True],
            kind="mergesort",
        )["player_id"]
        .astype(int)
        .tolist()
    )
    assert outfield["player_id"].astype(int).tolist() == expected_order


def test_unified_table_is_exact_six_field_projection(
    rich: pd.DataFrame,
    unified: pd.DataFrame,
) -> None:
    assert tuple(unified.columns) == UNIFIED_COLUMNS
    assert len(unified) == 553
    assert unified["Position Group"].ne("Goalkeeper").all()
    np.testing.assert_array_equal(
        unified["Global Rank"].to_numpy(dtype=int),
        np.arange(1, len(unified) + 1),
    )
    assert unified["Tournament Performance Score"].is_monotonic_decreasing

    expected = (
        rich.loc[rich["Global Rank"].notna(), list(UNIFIED_COLUMNS)]
        .reset_index(drop=True)
    )
    pd.testing.assert_frame_equal(
        unified,
        expected,
        check_dtype=False,
        check_exact=True,
    )


def test_full_outfield_and_300_minute_cohorts_are_exact(
    rich: pd.DataFrame,
) -> None:
    outfield = pd.read_csv(
        RANKING_ROOT / "global_rankings_outfield.csv"
    )
    ranked_300 = pd.read_csv(
        RANKING_ROOT / "player_rankings_300plus.csv"
    )

    expected_outfield = (
        rich.loc[
            rich["position_group"].ne("Goalkeeper")
            & rich["global_rank_v3"].notna()
        ]
        .sort_values("global_rank_v3", kind="mergesort")
        .reset_index(drop=True)
    )
    expected_outfield_300 = expected_outfield.loc[
        pd.to_numeric(
            expected_outfield["minutes_played"], errors="coerce"
        ).ge(300.0)
    ].reset_index(drop=True)
    pd.testing.assert_frame_equal(
        outfield,
        expected_outfield,
        check_dtype=False,
        check_exact=True,
    )
    pd.testing.assert_frame_equal(
        ranked_300,
        expected_outfield_300,
        check_dtype=False,
        check_exact=True,
    )
    assert len(outfield) == 553
    assert len(ranked_300) == 126
    assert outfield["minutes_played"].lt(300.0).any()
    assert ranked_300["minutes_played"].ge(300.0).all()
    assert outfield["position_group"].ne("Goalkeeper").all()
    assert ranked_300["position_group"].ne("Goalkeeper").all()


def test_all_32_team_tables_match_the_active_sources(
    rich: pd.DataFrame,
    unified: pd.DataFrame,
) -> None:
    assert len(TEAM_CODES) == 32
    expected_codes = set(TEAM_CODES.values())
    by_team_root = RANKING_ROOT / "by_team"
    by_team_unified_root = RANKING_ROOT / "by_team_unified"
    assert {path.stem for path in by_team_root.glob("*.csv")} == (
        expected_codes
    )
    assert {
        path.stem for path in by_team_unified_root.glob("*.csv")
    } == expected_codes

    rich_ids: list[int] = []
    unified_players: list[tuple[str, str]] = []
    for team, code in TEAM_CODES.items():
        actual_rich = pd.read_csv(by_team_root / f"{code}.csv")
        expected_rich = (
            rich.loc[rich["team"].eq(team)]
            .sort_values(
                ["Team Rank", "player_id"],
                na_position="last",
                kind="mergesort",
            )
            .reset_index(drop=True)
        )
        pd.testing.assert_frame_equal(
            actual_rich,
            expected_rich,
            check_dtype=False,
            check_exact=True,
        )
        rich_ids.extend(actual_rich["player_id"].astype(int).tolist())

        actual_unified = pd.read_csv(
            by_team_unified_root / f"{code}.csv"
        )
        expected_unified = (
            unified.loc[unified["Team"].eq(team)]
            .sort_values("Team Rank", kind="mergesort")
            .reset_index(drop=True)
        )
        assert tuple(actual_unified.columns) == UNIFIED_COLUMNS
        pd.testing.assert_frame_equal(
            actual_unified,
            expected_unified,
            check_dtype=False,
            check_exact=True,
        )
        unified_players.extend(
            zip(
                actual_unified["Team"].astype(str),
                actual_unified["Player"].astype(str),
            )
        )

    assert sorted(rich_ids) == sorted(rich["player_id"].astype(int))
    assert len(rich_ids) == len(set(rich_ids)) == 593
    assert sorted(unified_players) == sorted(
        zip(unified["Team"].astype(str), unified["Player"].astype(str))
    )


def test_main_goalkeepers_are_ranked_once_and_backups_are_unranked(
    rich: pd.DataFrame,
) -> None:
    goalkeepers = rich.loc[
        rich["position_group"].eq("Goalkeeper")
    ].copy()
    main = goalkeepers.loc[_main_goalkeeper_mask(goalkeepers)].copy()
    backups = goalkeepers.loc[~_main_goalkeeper_mask(goalkeepers)].copy()
    dedicated_path = RANKING_ROOT / "goalkeeper_rankings.csv"
    dedicated = pd.read_csv(dedicated_path)

    assert len(goalkeepers) == 40
    assert len(main) == main["team"].nunique() == 32
    assert len(backups) == 8
    assert set(main["team"]) == set(TEAM_CODES)
    np.testing.assert_array_equal(
        main.sort_values("gk_rank_v3")["gk_rank_v3"].to_numpy(dtype=int),
        np.arange(1, 33),
    )
    assert main[
        [
            "gk_rank_v3",
            "goalkeeper_rank_v3",
            "dedicated_goalkeeper_score_v3",
            "goalkeeper_consolidated_value_rank_v5",
        ]
    ].notna().all().all()
    assert main[["Global Rank", "Team Rank"]].isna().all().all()
    assert backups[
        [
            "gk_rank_v3",
            "goalkeeper_rank_v3",
            "Global Rank",
            "Team Rank",
            "dedicated_goalkeeper_score_v3",
        ]
    ].isna().all().all()
    assert dedicated["player_id"].astype(int).tolist() == (
        main.sort_values(
            "goalkeeper_consolidated_value_rank_v5"
        )["player_id"].astype(int).tolist()
    )
    assert dedicated["team"].nunique() == len(dedicated) == 32
    assert dedicated["shootout_component_v3"].between(0.0, 0.10).all()
    assert dedicated["percentile_equivalent_placement"].notna().all()


def test_active_alias_families_are_byte_identical() -> None:
    alias_families = [
        [
            REPORTS_ROOT / "canonical" / "model_summary.json",
            REPORTS_ROOT / "model_summary.json",
        ],
        [
            REPORTS_ROOT / "canonical" / "model_summary.md",
            REPORTS_ROOT / "model_summary.md",
            RESULTS_ROOT / "Summary" / "model_summary.md",
        ],
        [
            REPORTS_ROOT / "canonical" / "final_summary.md",
            REPORTS_ROOT / "final_summary.md",
            REPORTS_ROOT
            / "final"
            / "world_cup_team_performance_and_top_players.md",
        ],
        [
            REPORTS_ROOT / "canonical" / "coaches_notebook.md",
            REPORTS_ROOT / "coaches_notebook.md",
            REPORTS_ROOT / "v5_coaches_notebook.md",
        ],
        [
            RESULTS_ROOT / "metadata" / "artifact_manifest.json",
            REPORTS_ROOT / "artifact_manifest.json",
            REPORTS_ROOT / "v5_artifact_manifest.json",
        ],
        [
            RESULTS_ROOT / "metadata" / "pipeline_manifest.json",
            REPORTS_ROOT / "pipeline_manifest.json",
        ],
    ]
    for paths in alias_families:
        _assert_byte_identical(paths)


def test_release_manifests_use_portable_current_paths() -> None:
    master_path = RESULTS_ROOT / "metadata" / "artifact_manifest.json"
    refresh_path = RANKING_ROOT / "refresh_manifest.json"
    master = json.loads(master_path.read_text(encoding="utf-8"))
    refresh = json.loads(refresh_path.read_text(encoding="utf-8"))

    assert master["schema_version"] == (
        "ranking-repair-artifact-manifest-3.0"
    )
    assert refresh["schema_version"] == (
        "ranking-repair-refresh-manifest-3.0"
    )
    assert master["active_model_version"] == CATALOG_ACTIVE_MODEL_VERSION
    assert refresh["active_model_version"] == CATALOG_ACTIVE_MODEL_VERSION
    assert "POSIX" in master["path_contract"]
    assert "POSIX" in refresh["path_contract"]

    excluded = set(master["excluded_self_referential_manifests"])
    for path in excluded:
        _assert_portable_path(path)
    entries = master["artifacts"]
    entry_paths = [entry["path"] for entry in entries]
    assert len(entry_paths) == len(set(entry_paths)) == master[
        "artifact_count"
    ]
    expected_paths = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in RESULTS_ROOT.rglob("*")
        if path.is_file()
        and path.relative_to(PROJECT_ROOT).as_posix() not in excluded
        and "__pycache__" not in path.parts
        and path.suffix.lower() != ".pyc"
    }
    assert set(entry_paths) == expected_paths
    for entry in entries:
        _assert_portable_path(entry["path"])
        path = PROJECT_ROOT / entry["path"]
        assert path.stat().st_size == entry["bytes"]
        assert _sha256(path) == entry["sha256"]

    refresh_entries = refresh["artifacts"]
    refresh_paths = [entry["path"] for entry in refresh_entries]
    expected_refresh = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in RANKING_ROOT.rglob("*")
        if path.is_file() and path != refresh_path
    }
    assert len(refresh_paths) == len(set(refresh_paths)) == refresh[
        "artifact_count"
    ]
    assert set(refresh_paths) == expected_refresh
    for entry in refresh_entries:
        _assert_portable_path(entry["path"])
        path = PROJECT_ROOT / entry["path"]
        assert path.stat().st_size == entry["bytes"]
        assert _sha256(path) == entry["sha256"]

    for source in master["source_hashes"].values():
        _assert_portable_path(source["path"])
        path = PROJECT_ROOT / source["path"]
        assert path.stat().st_size == source["bytes"]
        assert _sha256(path) == source["sha256"]

    pipeline = json.loads(
        (REPORTS_ROOT / "pipeline_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert pipeline["status"] == "complete"
    assert pipeline["active_model_version"] == CATALOG_ACTIVE_MODEL_VERSION
    assert pipeline["paths_are_project_relative_posix"] is True
    for field in ("ranking_manifest", "artifact_manifest"):
        _assert_portable_path(pipeline[field])
        assert (PROJECT_ROOT / pipeline[field]).is_file()


def test_profile_starter_team_and_figure_families_are_complete(
    rich: pd.DataFrame,
) -> None:
    player_ids = set(rich["player_id"].astype(int))
    profiles = sorted(
        (REPORTS_ROOT / "player_profiles").glob("*.md")
    )
    profile_ids = {
        int(match.group(1))
        for path in profiles
        if (
            match := re.search(r"-(\d+)\.md$", path.name)
        )
    }
    assert len(profiles) == len(profile_ids) == len(player_ids) == 593
    assert profile_ids == player_ids

    starter_root = REPORTS_ROOT / "starters"
    starter_markdown = sorted(starter_root.glob("*/*.md"))
    starter_json = sorted(starter_root.glob("*/*.json"))
    assert len(starter_markdown) == len(starter_json) == 593
    assert {path.parent.name for path in starter_markdown} == set(
        TEAM_CODES.values()
    )
    expected_starters = {
        (
            TEAM_CODES[str(row.team)],
            int(row.player_id),
        )
        for row in rich[["team", "player_id"]].itertuples(index=False)
    }
    actual_markdown = {
        (path.parent.name, int(path.name.split("_", 1)[0]))
        for path in starter_markdown
    }
    actual_json = {
        (path.parent.name, int(path.name.split("_", 1)[0]))
        for path in starter_json
    }
    assert actual_markdown == actual_json == expected_starters
    for path in starter_json:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["active_model_version"] == ACTIVE_MODEL_VERSION
        assert payload["identity_used_for_scoring"] is False
        assert payload["ordinary_event_periods"] == [1, 2, 3, 4]

    team_profiles = sorted(
        (REPORTS_ROOT / "team_profiles").glob("*.md")
    )
    team_markdown = sorted((REPORTS_ROOT / "teams").glob("*.md"))
    team_json = sorted((REPORTS_ROOT / "teams").glob("*.json"))
    assert len(team_profiles) == len(team_markdown) == len(team_json) == 32
    assert {path.name[:3] for path in team_markdown} == set(
        TEAM_CODES.values()
    )
    assert {path.name[:3] for path in team_json} == set(
        TEAM_CODES.values()
    )

    expected_figures = {
        "v3_global_outfield_rankings.png",
        "v3_global_outfield_300min.png",
        "v3_representative_team_rankings.png",
        "v3_defensive_feature_importance.png",
        "v3_champion_challenger_movement.png",
        "v3_position_composition_and_stability.png",
    }
    figures = {
        path.name: path
        for path in (REPORTS_ROOT / "v3_figures").glob("*.png")
    }
    assert set(figures) == expected_figures
    assert all(path.stat().st_size > 10_000 for path in figures.values())


def test_active_summaries_describe_outfield_v3_and_goalkeeper_v5() -> None:
    active_paths = [
        REPORTS_ROOT / "canonical" / "model_summary.md",
        REPORTS_ROOT / "canonical" / "final_summary.md",
        RANKING_ROOT / "ranking_methodology.md",
    ]
    texts = {
        path: path.read_text(encoding="utf-8") for path in active_paths
    }
    combined = "\n".join(texts.values())
    for phrase in (
        ACTIVE_MODEL_VERSION,
        "Tournament Impact",
        "Role Quality",
        "Uncertainty",
        "periods 1–4",
        "goalkeeper_consolidated_value_v5",
        "one active metric",
    ):
        assert phrase in combined
    for retired in (
        "shootout_save_points: 0.20",
        "0.20 for every shootout save",
        "two active goalkeeper rankings",
    ):
        assert retired not in combined

    final_summary = texts[
        REPORTS_ROOT / "canonical" / "final_summary.md"
    ]
    for section in (
        "## Global outfield top 20",
        "## Outfield players with 300+ minutes",
        "## Goalkeeper ranking",
        "## Goalkeeper methodology and validation",
    ):
        assert section in final_summary

    payload = json.loads(
        (
            REPORTS_ROOT / "canonical" / "model_summary.json"
        ).read_text(encoding="utf-8")
    )
    assert payload["active_model_version"] == ACTIVE_MODEL_VERSION
    assert payload["goalkeeper_model"] == (
        "goalkeeper_consolidated_value_v5"
    )
    assert payload["single_active_goalkeeper_metric"] is True
    assert payload["hard_gates_all_pass"] is True
