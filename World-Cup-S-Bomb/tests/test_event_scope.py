"""Qatar 2022 period-boundary and outcome reconciliation tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.run_pipeline import _action_value_splits
from src.features.event_scope import (
    EVENT_SCOPE_VERSION,
    aggregate_player_outcomes,
    filter_ordinary_actions,
    tournament_goal_reconciliation,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_raw_tournament_goals_reconcile_and_shootouts_are_separate() -> None:
    events = pd.read_csv(
        PROJECT_ROOT / "notebooks/all_events.csv",
        low_memory=False,
    )
    audit = tournament_goal_reconciliation(events)

    assert audit == {
        "player_credited_match_goals": 169,
        "own_goals": 3,
        "official_match_goals_including_own_goals": 172,
        "shootout_goals_excluded": 26,
    }


def test_named_goal_totals_follow_general_period_rule() -> None:
    events = pd.read_csv(
        PROJECT_ROOT / "notebooks/all_events.csv",
        low_memory=False,
    )
    outcomes = aggregate_player_outcomes(
        events,
        group_columns=("player", "team", "player_id"),
    ).set_index("player")

    assert outcomes.loc[
        "Lionel Andrés Messi Cuccittini",
        "regulation_extra_time_goals",
    ] == 7
    assert outcomes.loc[
        "Kylian Mbappé Lottin",
        "regulation_extra_time_goals",
    ] == 8
    assert outcomes.loc[
        "Leandro Daniel Paredes",
        "regulation_extra_time_goals",
    ] == 0
    assert outcomes.loc[
        "Gonzalo Ariel Montiel",
        "regulation_extra_time_goals",
    ] == 0
    assert outcomes["event_scope_version"].eq(EVENT_SCOPE_VERSION).all()


def test_period_five_cannot_change_ordinary_action_value_aggregates() -> None:
    actions = pd.DataFrame(
        {
            "period_id": [1, 2, 5],
            "player_id": [7, 7, 7],
            "play_pattern": ["Regular Play", "Regular Play", "Penalty"],
            "action_side": ["offense", "offense", "offense"],
            "vaep_value": [0.1, 0.2, 9.0],
            "xt_value": [0.01, 0.02, 5.0],
            "xa_value": [0.0, 0.1, 4.0],
            "touch": [True, True, True],
        }
    )
    with_shootout = _action_value_splits(
        actions,
        group_columns=("player_id",),
    )
    without_shootout = _action_value_splits(
        filter_ordinary_actions(actions),
        group_columns=("player_id",),
    )

    pd.testing.assert_frame_equal(with_shootout, without_shootout)
    assert with_shootout.loc[0, "vaep_offense"] == pytest.approx(0.3)
    assert with_shootout.loc[0, "xt_total"] == pytest.approx(0.03)
    assert with_shootout.loc[0, "xa_sum"] == pytest.approx(0.1)


def test_outcome_fields_do_not_mix_regular_and_shootout_penalties() -> None:
    events = pd.DataFrame(
        {
            "team": ["A", "A", "A", "A"],
            "player_id": [1, 1, 1, 1],
            "id": ["s1", "s2", "s3", "p1"],
            "period": [1, 2, 5, 1],
            "type": ["Shot", "Shot", "Shot", "Pass"],
            "shot_outcome": ["Goal", "Goal", "Goal", None],
            "shot_type": ["Open Play", "Penalty", "Penalty", None],
            "shot_statsbomb_xg": [0.2, 0.78, 0.78, None],
            "pass_goal_assist": [False, False, False, True],
            "pass_assisted_shot_id": [None, None, None, "s1"],
        }
    )
    row = aggregate_player_outcomes(events).iloc[0]

    assert row["open_play_goals"] == 1
    assert row["non_penalty_goals"] == 1
    assert row["regular_penalty_goals"] == 1
    assert row["regulation_extra_time_goals"] == 2
    assert row["shootout_attempts"] == 1
    assert row["shootout_goals"] == 1
    assert row["assists"] == 1
    assert row["xg_non_shootout"] == pytest.approx(0.98)
    assert row["xg_non_penalty"] == pytest.approx(0.2)
    assert row["xa_non_shootout"] == pytest.approx(0.2)
