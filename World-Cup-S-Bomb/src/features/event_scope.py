"""Authoritative Qatar 2022 ordinary-match and shootout event boundaries."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


ORDINARY_MATCH_PERIODS = frozenset({1, 2, 3, 4})
SHOOTOUT_PERIOD = 5
EVENT_SCOPE_VERSION = "qatar-2022-periods-1-4-v1"


def _periods(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame:
        raise ValueError(f"Event scope requires {column!r}")
    return pd.to_numeric(frame[column], errors="coerce")


def ordinary_event_mask(
    frame: pd.DataFrame,
    *,
    period_column: str = "period",
) -> pd.Series:
    """Return the periods 1–4 mask for StatsBomb event tables."""

    return _periods(frame, period_column).isin(ORDINARY_MATCH_PERIODS)


def shootout_event_mask(
    frame: pd.DataFrame,
    *,
    period_column: str = "period",
) -> pd.Series:
    """Return the period-five penalty-shootout mask."""

    return _periods(frame, period_column).eq(SHOOTOUT_PERIOD)


def ordinary_action_mask(frame: pd.DataFrame) -> pd.Series:
    """Return the periods 1–4 mask for SPADL/action-value tables."""

    column = "period_id" if "period_id" in frame else "period"
    return ordinary_event_mask(frame, period_column=column)


def filter_ordinary_events(
    frame: pd.DataFrame,
    *,
    period_column: str = "period",
) -> pd.DataFrame:
    """Copy only regulation and extra-time events."""

    return frame.loc[
        ordinary_event_mask(frame, period_column=period_column)
    ].copy()


def filter_ordinary_actions(frame: pd.DataFrame) -> pd.DataFrame:
    """Copy only regulation and extra-time action-value rows."""

    return frame.loc[ordinary_action_mask(frame)].copy()


def _truthy(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return (
        series.fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "1", "yes"})
    )


def aggregate_player_outcomes(
    events: pd.DataFrame,
    *,
    group_columns: Sequence[str] = ("team", "player_id"),
) -> pd.DataFrame:
    """Aggregate ordinary outcomes and shootout outcomes into separate fields."""

    required = {
        *group_columns,
        "id",
        "period",
        "type",
        "shot_outcome",
        "shot_type",
        "shot_statsbomb_xg",
        "pass_goal_assist",
        "pass_assisted_shot_id",
    }
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(f"Outcome aggregation missing: {sorted(missing)}")

    working = events.loc[
        events[list(group_columns)].notna().all(axis=1)
    ].copy()
    ordinary = ordinary_event_mask(working)
    shootout = shootout_event_mask(working)
    shot = working["type"].eq("Shot")
    goal = shot & working["shot_outcome"].eq("Goal")
    penalty = working["shot_type"].astype(str).str.contains(
        "Penalty",
        case=False,
        na=False,
    )
    open_play = working["shot_type"].astype(str).str.contains(
        "Open Play",
        case=False,
        na=False,
    )
    assist = (
        working["type"].eq("Pass")
        & ordinary
        & _truthy(working["pass_goal_assist"])
    )
    xg = pd.to_numeric(working["shot_statsbomb_xg"], errors="coerce").fillna(
        0.0
    )
    shot_xg = (
        working.loc[shot, ["id", "shot_statsbomb_xg"]]
        .drop_duplicates("id")
        .set_index("id")["shot_statsbomb_xg"]
    )
    assisted_xg = pd.to_numeric(
        working["pass_assisted_shot_id"].astype(str).map(shot_xg),
        errors="coerce",
    ).fillna(0.0)

    fields = {
        "open_play_goals": goal & ordinary & open_play,
        "non_penalty_goals": goal & ordinary & ~penalty,
        "regular_penalty_goals": goal & ordinary & penalty,
        "regulation_extra_time_goals": goal & ordinary,
        "assists": assist,
        "xg_non_shootout": xg.where(shot & ordinary, 0.0),
        "xg_non_penalty": xg.where(shot & ordinary & ~penalty, 0.0),
        "xa_non_shootout": assisted_xg.where(
            working["type"].eq("Pass") & ordinary,
            0.0,
        ),
        "shootout_attempts": shot & shootout,
        "shootout_goals": goal & shootout,
    }
    for name, values in fields.items():
        working[name] = (
            values.astype(int)
            if pd.api.types.is_bool_dtype(values)
            else pd.to_numeric(values, errors="coerce").fillna(0.0)
        )

    output = (
        working.groupby(list(group_columns), as_index=False)[list(fields)]
        .sum()
        .sort_values(list(group_columns), kind="mergesort")
        .reset_index(drop=True)
    )
    for column in (
        "open_play_goals",
        "non_penalty_goals",
        "regular_penalty_goals",
        "regulation_extra_time_goals",
        "assists",
        "shootout_attempts",
        "shootout_goals",
    ):
        output[column] = output[column].astype(int)
    output["ordinary_event_periods"] = "1-4"
    output["shootout_event_period"] = "5"
    output["event_scope_version"] = EVENT_SCOPE_VERSION
    return output


def tournament_goal_reconciliation(events: pd.DataFrame) -> dict[str, int]:
    """Return official-scope goal counts for the Qatar 2022 audit."""

    ordinary = ordinary_event_mask(events)
    shot_goals = (
        ordinary
        & events["type"].eq("Shot")
        & events["shot_outcome"].eq("Goal")
    )
    own_goals = ordinary & events["type"].astype(str).str.contains(
        "Own Goal Against",
        case=False,
        na=False,
    )
    shootout_goals = (
        shootout_event_mask(events)
        & events["type"].eq("Shot")
        & events["shot_outcome"].eq("Goal")
    )
    return {
        "player_credited_match_goals": int(shot_goals.sum()),
        "own_goals": int(own_goals.sum()),
        "official_match_goals_including_own_goals": int(
            shot_goals.sum() + own_goals.sum()
        ),
        "shootout_goals_excluded": int(shootout_goals.sum()),
    }
