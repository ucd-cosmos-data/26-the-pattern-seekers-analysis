"""End-to-end schema and artifact-generation tests."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.reporting.artifacts import ArtifactGenerator, RANKING_SCHEMA
from scripts.run_pipeline import _purge_obsolete_v4_summaries


def _players() -> pd.DataFrame:
    records = []
    for team_index in range(32):
        for player_index in range(2):
            records.append(
                {
                    "player": f"Player {team_index}-{player_index}",
                    "team": f"Team {team_index:02d}",
                    "position_group": "Midfield",
                    "functional_role": "Box-to-Box",
                    "final_player_rating": (
                        1.0 - team_index / 100 - player_index / 1000
                    ),
                    "legacy_final_player_rating": 0.5,
                    "creation_score": 0.6,
                    "defensive_score": 0.5,
                    "ball_security_score": 0.7,
                    "pressing_score": 0.6,
                    "xt_p90": 0.4,
                    "off_ball_score": 0.5,
                    "line_breaking_pass_rate": 0.2,
                    "network_betweenness": 0.1,
                }
            )
    return pd.DataFrame(records)


def test_all_required_artifacts_and_32_team_profiles(tmp_path: Path) -> None:
    comparison = pd.DataFrame(
        {
            "player": ["Player 0-0"],
            "old_rating": [0.5],
            "new_rating": [1.0],
            "rating_difference": [0.5],
            "functional_role": ["Box-to-Box"],
        }
    )
    manifest = ArtifactGenerator(tmp_path).generate(
        _players(),
        model_summary={
            "selected_layer": "role_aware_fallback",
            "metric_gate_passed": False,
            "metrics": {},
            "feature_importance": {},
            "cluster_stability": {},
        },
        validation_comparison=comparison,
    )
    for name in (
        "ranking/v5_player_rankings.csv",
        "ranking/v5_player_rankings.json",
        "v5_coaches_notebook.md",
        "v5_artifact_manifest.json",
        "ranking/player_rankings.csv",
        "ranking/player_rankings_300plus.csv",
        "ranking/player_rankings.json",
        "coaches_notebook.md",
        "model_summary.json",
        "model_summary.md",
        "final_summary.md",
        "artifact_manifest.json",
        "rating_validation_comparison.csv",
    ):
        assert (tmp_path / name).is_file()
    assert len(list((tmp_path / "team_profiles").glob("*.md"))) == 32
    assert len(list((tmp_path / "player_profiles").glob("*.md"))) == 64
    assert not (tmp_path / "v5_team_profiles").exists()
    assert not (tmp_path / "v5_player_profiles").exists()
    assert not (tmp_path / "v5_final_summary.md").exists()
    assert not (tmp_path / "v5_role_aware_model_summary.md").exists()
    assert not (tmp_path / "v5_role_aware_model_summary.json").exists()
    assert (
        tmp_path / "v5_figures/v5_global_outfield_rankings.png"
    ).is_file()
    rankings = pd.read_csv(tmp_path / "ranking/player_rankings.csv")
    assert set(RANKING_SCHEMA) <= set(rankings.columns)
    rankings_300plus = pd.read_csv(
        tmp_path / "ranking/player_rankings_300plus.csv"
    )
    assert len(rankings_300plus) == len(rankings)
    assert rankings_300plus["RankingStatus"].eq(
        "Ranked (300+ min)"
    ).all()
    payload = json.loads(
        (tmp_path / "ranking/player_rankings.json").read_text()
    )
    assert len(payload) == len(rankings)
    assert manifest.metadata["teams"] == 32
    assert manifest.metadata["player_profiles"] == 64
    final_report = (tmp_path / "final_summary.md").read_text(
        encoding="utf-8"
    )
    assert "# Team-by-team summary" in final_report
    assert "## Team 00" in final_report
    assert "## Team 31" in final_report
    assert "Player 0-0" in final_report


def test_300plus_ranking_excludes_lower_minutes_and_reranks() -> None:
    players = pd.DataFrame(
        {
            "player_name": ["High sample", "Low sample", "Goalkeeper"],
            "team": ["A", "B", "A"],
            "position_group": ["Forward", "Forward", "Goalkeeper"],
            "functional_role": ["Creator", "Creator", "Goalkeeper"],
            "final_player_rating": [0.80, 0.99, 0.70],
            "minutes": [301.0, 299.0, 450.0],
            "RankingStatus": [
                "Ranked (300+ min)",
                "Ranked (180â€“299 min)",
                "Ranked (300+ min)",
            ],
            "global_rank_eligible": [True, True, False],
        }
    )

    rankings = ArtifactGenerator.prepare_rankings(players)
    eligible = ArtifactGenerator.prepare_300plus_rankings(rankings)

    assert eligible["player_name"].tolist() == [
        "High sample",
        "Goalkeeper",
    ]
    high_sample = eligible.set_index("player_name").loc["High sample"]
    goalkeeper = eligible.set_index("player_name").loc["Goalkeeper"]
    assert high_sample["global_rank"] == 1
    assert pd.isna(goalkeeper["global_rank"])
    assert goalkeeper["goalkeeper_rank"] == 1


def test_team_manifest_can_include_teams_without_ranked_players(
    tmp_path: Path,
) -> None:
    players = _players().loc[lambda frame: frame["team"].eq("Team 00")]
    teams = [f"Team {index:02d}" for index in range(32)]
    team_metrics = pd.DataFrame(
        {
            "team": teams,
            "total_xt_created": [1.25] * 32,
            "pressure_resistance_rate": [0.75] * 32,
            "defensive_hull_area": [300.0] * 32,
        }
    )
    coverage_players = pd.DataFrame(
        {
            "player_id": range(100, 106),
            "player_name": [f"Observed {index}" for index in range(6)],
            "team": ["Team 31"] * 6,
            "position_group": ["Midfield"] * 6,
            "minutes": [270.0, 240.0, 210.0, 180.0, 150.0, 120.0],
        }
    )
    ArtifactGenerator(tmp_path).generate(
        players,
        model_summary={},
        tournament_teams=teams,
        team_metrics=team_metrics,
        team_player_pool=coverage_players,
    )
    empty_team = (
        tmp_path / "team_profiles" / "team-31.md"
    ).read_text(encoding="utf-8")
    assert "Observed 0" in empty_team
    assert "Observed 4" in empty_team
    assert "Observed 5" not in empty_team
    assert "Ranked (180–299 min)" in empty_team
    assert "Coverage only (<180 min)" in empty_team
    assert "No model rating assigned" in empty_team
    assert "Total xT created: 1.2500" in empty_team
    assert "Pass completion under pressure: 0.7500" in empty_team
    final_report = (tmp_path / "final_summary.md").read_text(
        encoding="utf-8"
    )
    team_section = final_report.split("## Team 31", maxsplit=1)[1]
    assert "Observed 0" in team_section
    assert "Observed 4" in team_section
    assert "Observed 5" not in team_section


def test_v4_cleanup_requires_complete_v5_publication(
    tmp_path: Path,
) -> None:
    obsolete = (
        tmp_path / "results/Summary/v4_model_explanation_summary.md"
    )
    obsolete.parent.mkdir(parents=True)
    obsolete.write_text("obsolete", encoding="utf-8")
    with pytest.raises(RuntimeError):
        _purge_obsolete_v4_summaries(tmp_path)
    assert obsolete.is_file()


def test_v4_cleanup_is_allowlisted_and_post_publication(
    tmp_path: Path,
) -> None:
    report_root = tmp_path / "results/reports"
    ArtifactGenerator(report_root).generate(
        _players(),
        model_summary={},
    )
    obsolete = (
        tmp_path / "results/Summary/v4_model_explanation_summary.md"
    )
    retained = tmp_path / "results/Summary/tactical_history.md"
    obsolete.parent.mkdir(parents=True)
    obsolete.write_text("obsolete", encoding="utf-8")
    retained.write_text("retain", encoding="utf-8")
    manifest = _purge_obsolete_v4_summaries(tmp_path)
    assert not obsolete.exists()
    assert retained.is_file()
    assert manifest.is_file()
