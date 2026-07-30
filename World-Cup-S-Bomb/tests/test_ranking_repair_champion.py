"""Regression contract for the immutable pre-repair ranking champion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHAMPION_ROOT = (
    PROJECT_ROOT / "results/diagnostics/ranking_repair/champion"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _snapshot() -> dict:
    return json.loads(
        (CHAMPION_ROOT / "champion_snapshot.json").read_text(
            encoding="utf-8"
        )
    )


def test_champion_copies_match_frozen_hashes() -> None:
    snapshot = _snapshot()
    assert snapshot["immutable"] is True
    for name, record in snapshot["artifact_hashes"].items():
        suffix = Path(record["path"]).suffix
        frozen = CHAMPION_ROOT / f"{name}{suffix}"
        assert frozen.is_file()
        assert _sha256(frozen) == record["sha256"]


def test_frozen_unified_schema_and_rank_order_are_consistent() -> None:
    unified = pd.read_csv(CHAMPION_ROOT / "unified_rankings.csv")
    assert unified.columns.tolist() == [
        "Global Rank",
        "Team Rank",
        "Player",
        "Team",
        "Position Group",
        "Tournament Performance Score",
    ]
    ranked = unified.loc[unified["Global Rank"].notna()].copy()
    expected = ranked["Tournament Performance Score"].rank(
        method="min",
        ascending=False,
    )
    pd.testing.assert_series_equal(
        ranked["Global Rank"].astype(float),
        expected,
        check_names=False,
    )
    expected_team = ranked.groupby("Team")[
        "Tournament Performance Score"
    ].rank(method="min", ascending=False)
    pd.testing.assert_series_equal(
        ranked["Team Rank"].astype(float),
        expected_team,
        check_names=False,
    )


def test_frozen_feature_rich_ranks_and_backup_goalkeepers() -> None:
    rankings = pd.read_csv(CHAMPION_ROOT / "player_rankings.csv")
    outfield = rankings.loc[rankings["position_group_360"].ne("GK")]
    expected_global = outfield["final_player_rating_v2"].rank(
        method="min",
        ascending=False,
    )
    pd.testing.assert_series_equal(
        outfield["global_rank_v2"].astype(float),
        expected_global,
        check_names=False,
    )
    keepers = rankings.loc[rankings["position_group_360"].eq("GK")]
    main = keepers["is_main_goalkeeper"].fillna(False).astype(bool)
    assert int(main.sum()) == 32
    assert keepers.loc[main, "team"].is_unique
    assert keepers.loc[~main, "gk_rank_v2"].isna().all()


def test_snapshot_contains_required_regression_diagnostics() -> None:
    snapshot = _snapshot()
    assert {
        "source_hashes",
        "artifact_hashes",
        "schemas",
        "model_metrics",
        "score_correlations",
        "position_composition",
        "ranked_minutes_bands",
        "stability",
    } <= set(snapshot)
    assert snapshot["stability"]["bootstrap_match_draws"] >= 200
    assert (
        snapshot["stability"]["leave_one_match_out_rank_spearman"]["minimum"]
        > 0.0
    )
