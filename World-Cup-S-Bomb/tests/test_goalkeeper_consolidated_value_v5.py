from __future__ import annotations

import inspect
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.run_goalkeeper_v5_release import _face_gates, _soft_gates
from src.models.goalkeeper_consolidated_value_v5 import (
    GoalkeeperV5Config,
    add_v5_shot_channels,
    calculate_goalkeeper_consolidated_value_v5,
    clutch_multiplier,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTICS = (
    PROJECT_ROOT / "results/diagnostics/ranking_repair"
)
RANKING = PROJECT_ROOT / "results/reports/ranking"


def _config(
    *,
    status_weights: dict[str, float] | None = None,
) -> GoalkeeperV5Config:
    return GoalkeeperV5Config(
        weights=status_weights
        or {
            "psxg": 0.45,
            "clutch": 0.25,
            "state_leverage": 0.05,
            "regular_penalty": 0.05,
            "shootout": 0.15,
            "support": 0.05,
        }
    )


def _base() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "player_id": [1, 2],
            "player_name": ["Keeper A", "Keeper B"],
            "team": ["A", "B"],
            "minutes": [600.0, 300.0],
            "is_main_goalkeeper": [True, True],
            "actions": [50, 50],
            "cross_stopping_rate": [0.5, 0.5],
            "claims_p90": [1.0, 1.0],
            "sweeper_actions_p90": [0.5, 0.5],
            "distribution_under_pressure": [0.7, 0.7],
            "dedicated_goalkeeper_score_v3": [0.6, 0.5],
            "goalkeeper_rank_v3": [1, 2],
        }
    )


def _shot(
    *,
    team: str,
    probability: float,
    goal: float,
    minute: float = 20.0,
    period: int = 1,
    score_diff: int = 0,
    knockout: bool = False,
    leverage: float = 0.2,
    match_id: int = 1,
    event_index: int = 1,
) -> dict[str, object]:
    return {
        "match_id": match_id,
        "event_index": event_index,
        "period": period,
        "minute": minute,
        "competition_stage": "Final" if knockout else "Group Stage",
        "knockout": knockout,
        "attacking_team": "Opponent",
        "defending_team": team,
        "pre_shot_score_diff_defending": score_diff,
        "is_regular_penalty": False,
        "shot_outcome": "Goal" if goal else "Saved",
        "goal": goal,
        "goal_probability_v3": probability,
        "leverage_v4": leverage,
    }


def test_psxg_prevention_aggregation_on_synthetic_shots() -> None:
    config = _config()
    shots = add_v5_shot_channels(
        pd.DataFrame(
            [
                _shot(team="A", probability=0.8, goal=0.0),
                _shot(
                    team="A",
                    probability=0.2,
                    goal=1.0,
                    event_index=2,
                ),
                _shot(team="B", probability=0.4, goal=0.0),
            ]
        ),
        config=config,
    )
    rated, audit = calculate_goalkeeper_consolidated_value_v5(
        _base(),
        shots,
        pd.DataFrame(),
        config=config,
    )
    indexed = rated.set_index("team")
    assert indexed.loc["A", "psxg_goals_prevented_v5"] == pytest.approx(0.0)
    assert indexed.loc["B", "psxg_goals_prevented_v5"] == pytest.approx(0.4)
    assert audit["ordinary_shots_valued"] == 3


def test_easy_save_is_worth_less_than_hard_save() -> None:
    shots = add_v5_shot_channels(
        pd.DataFrame(
            [
                _shot(team="A", probability=0.1, goal=0.0),
                _shot(
                    team="B",
                    probability=0.8,
                    goal=0.0,
                    event_index=2,
                ),
            ]
        ),
        config=_config(),
    )
    assert shots.loc[0, "prevention_v5"] < shots.loc[1, "prevention_v5"]


def test_clutch_uplift_is_psxg_checked_and_late_monotonic() -> None:
    config = _config()
    early = clutch_multiplier(
        minute=20.0,
        period=1,
        score_diff_defending=0,
        knockout=True,
        state_leverage=0.5,
        config=config,
    )
    late = clutch_multiplier(
        minute=121.0,
        period=4,
        score_diff_defending=0,
        knockout=True,
        state_leverage=0.5,
        config=config,
    )
    assert early == 1.0
    assert late > early
    shots = add_v5_shot_channels(
        pd.DataFrame(
            [
                _shot(
                    team="A",
                    probability=0.1,
                    goal=0.0,
                    minute=121.0,
                    period=4,
                    knockout=True,
                    leverage=0.5,
                ),
                _shot(
                    team="B",
                    probability=0.8,
                    goal=0.0,
                    minute=121.0,
                    period=4,
                    knockout=True,
                    leverage=0.5,
                    event_index=2,
                ),
            ]
        ),
        config=config,
    )
    assert (
        shots.loc[0, "clutch_prevention_residual_v5"]
        < shots.loc[1, "clutch_prevention_residual_v5"]
    )


def test_identity_labels_do_not_change_scores() -> None:
    config = _config()
    shots = add_v5_shot_channels(
        pd.DataFrame(
            [
                _shot(team="A", probability=0.8, goal=0.0),
                _shot(team="B", probability=0.4, goal=1.0),
            ]
        ),
        config=config,
    )
    original, _ = calculate_goalkeeper_consolidated_value_v5(
        _base(), shots, pd.DataFrame(), config=config
    )
    renamed = _base()
    renamed["player_name"] = ["Renamed One", "Renamed Two"]
    changed, _ = calculate_goalkeeper_consolidated_value_v5(
        renamed, shots, pd.DataFrame(), config=config
    )
    assert np.allclose(
        original["goalkeeper_consolidated_value_raw_v5"],
        changed["goalkeeper_consolidated_value_raw_v5"],
    )


def test_named_acceptance_fixtures_are_not_in_scoring_path() -> None:
    source = inspect.getsource(
        calculate_goalkeeper_consolidated_value_v5
    ).lower()
    for forbidden in (
        "martínez",
        "martinez",
        "al owais",
        "turner",
        "livaković",
        "bounou",
        "szczęsny",
        "golden glove",
    ):
        assert forbidden not in source


def test_gate_helpers_encode_hard_and_soft_contract() -> None:
    ranks = {
        "Damián Emiliano Martínez": 3,
        "Mohammed Khalil Al Owais": 15,
        "Matthew Charles Turner": 9,
        "Dominik Livaković": 1,
        "Yassine Bounou": 4,
        "Wojciech Szczęsny": 7,
        "Hugo Lloris": 10,
        "Andries Noppert": 5,
        "Diogo Meireles Costa": 6,
        "Jordan Pickford": 12,
    }
    assert all(_face_gates(ranks).values())
    baseline = pd.DataFrame(
        {
            "player_name": list(ranks),
            "goalkeeper_rank_v3": [
                23,
                2,
                3,
                5,
                4,
                1,
                22,
                6,
                8,
                20,
            ],
        }
    )
    soft = _soft_gates(ranks, baseline)
    assert soft["S1_martinez_top_3"]
    assert soft["S2_turner_rank_8_to_12"]
    assert soft["S3_al_owais_rank_15_or_lower"]


def test_mocked_promotion_activates_only_consolidated_rank() -> None:
    config = _config()
    shots = add_v5_shot_channels(
        pd.DataFrame(
            [
                _shot(team="A", probability=0.8, goal=0.0),
                _shot(team="B", probability=0.4, goal=1.0),
            ]
        ),
        config=config,
    )
    rated, _ = calculate_goalkeeper_consolidated_value_v5(
        _base(),
        shots,
        pd.DataFrame(),
        config=config,
        consolidation_status="promoted_single_metric",
    )
    assert rated["active_goalkeeper_rank_field"].eq(
        "goalkeeper_consolidated_value_rank_v5"
    ).all()
    assert rated["goalkeeper_rank_v3"].tolist() == [1, 2]


def test_release_artifacts_report_kolo_and_every_gate() -> None:
    gate_path = DIAGNOSTICS / "goalkeeper_v5_gate_report.json"
    audit_path = DIAGNOSTICS / "goalkeeper_v5_audit.json"
    if not gate_path.is_file() or not audit_path.is_file():
        pytest.skip("v5 release artifacts have not been generated")
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert set(
        key for key in gate["hard_gates"] if key.startswith("H")
    ) >= {f"H{number}_{suffix}" for number, suffix in (
        (1, "martinez_top_10"),
        (2, "al_owais_outside_top_10"),
        (3, "turner_outside_top_3"),
        (4, "elite_core_three_in_top_8"),
        (5, "no_profile_mirage_podium"),
        (6, "identity_blind"),
        (7, "psxg_integrity"),
        (8, "clutch_monotonicity"),
        (9, "shootout_monotonicity"),
        (10, "single_metric_consolidation"),
        (11, "no_pedigree_feature"),
        (12, "baseline_preservation"),
    )}
    assert gate["hard_gates"]["kolo_muani_event_rows"] == 1
    assert audit["soft_gates"].get("S1_martinez_top_3") in (True, False)


def test_candidate_table_has_one_main_goalkeeper_per_team() -> None:
    path = (
        PROJECT_ROOT
        / "results"
        / "diagnostics"
        / "ranking_repair"
        / "goalkeeper_v5_scored_rows.csv"
    )
    if not path.is_file():
        pytest.skip("v5 candidate table has not been generated")
    table = pd.read_csv(path)
    assert len(table) == 32
    assert table["team"].nunique() == 32
    assert sorted(
        table["goalkeeper_consolidated_value_rank_v5"].astype(int)
    ) == list(range(1, 33))
