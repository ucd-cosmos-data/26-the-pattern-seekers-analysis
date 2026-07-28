"""End-to-end schema and artifact-generation tests."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.reporting.artifacts import ArtifactGenerator, RANKING_SCHEMA


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
        "player_rankings.csv",
        "player_rankings.json",
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
    rankings = pd.read_csv(tmp_path / "player_rankings.csv")
    assert set(RANKING_SCHEMA) <= set(rankings.columns)
    payload = json.loads((tmp_path / "player_rankings.json").read_text())
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
    ArtifactGenerator(tmp_path).generate(
        players,
        model_summary={},
        tournament_teams=teams,
        team_metrics=team_metrics,
    )
    empty_team = (
        tmp_path / "team_profiles" / "team-31.md"
    ).read_text(encoding="utf-8")
    assert "No player from this team reached" in empty_team
    assert "Total xT created: 1.2500" in empty_team
    assert "Pass completion under pressure: 0.7500" in empty_team
