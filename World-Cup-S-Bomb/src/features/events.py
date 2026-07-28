"""Vectorized event-derived player contribution features."""

from __future__ import annotations

import ast

import numpy as np
import pandas as pd


def coordinate_axis(series: pd.Series, axis: int) -> pd.Series:
    """Extract one StatsBomb coordinate axis, preserving missing values."""

    def parse(value: object) -> float:
        if isinstance(value, (list, tuple)) and len(value) > axis:
            return float(value[axis])
        if not isinstance(value, str) or not value.strip():
            return np.nan
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return np.nan
        return (
            float(parsed[axis])
            if isinstance(parsed, (list, tuple)) and len(parsed) > axis
            else np.nan
        )

    return series.map(parse)


def add_profile_rates(profiles: pd.DataFrame) -> pd.DataFrame:
    """Add standardized per-90 and rate features from existing totals."""

    output = profiles.copy()
    minutes = pd.to_numeric(output["minutes"], errors="coerce").clip(lower=1.0)
    per_90 = {
        "pressures_p90": "pressures",
        "counterpressures_p90": "counterpressures",
        "recoveries_p90": "recoveries",
        "post_pressure_recoveries_p90": "post_pressure_recoveries",
        "blocks_p90": "blocks",
        "aerial_wins_p90": "aerial_wins",
        "aerial_events_p90": "aerial_events",
        "goals_p90": "goals",
        "box_passes_p90": "box_passes",
        "tackles_p90": "duels_won",
        "dispossessions_p90": "dispossessions",
        "progressive_receptions_p90": "progressive_receptions",
        "dangerous_zone_receptions_p90": "dangerous_zone_receptions",
    }
    for output_column, source in per_90.items():
        if source in output:
            output[output_column] = (
                90.0
                * pd.to_numeric(output[source], errors="coerce").fillna(0.0)
                / minutes
            )
    if {
        "successful_under_pressure_actions",
        "under_pressure_actions",
    } <= set(output):
        output["pressure_resistance"] = (
            pd.to_numeric(
                output["successful_under_pressure_actions"],
                errors="coerce",
            )
            / pd.to_numeric(
                output["under_pressure_actions"],
                errors="coerce",
            ).replace(0, np.nan)
        )
    if {"successful_pressures", "pressures"} <= set(output):
        output["successful_pressure_rate"] = (
            pd.to_numeric(output["successful_pressures"], errors="coerce")
            / pd.to_numeric(output["pressures"], errors="coerce").replace(
                0,
                np.nan,
            )
        )
    if {"shots_on_target", "shots"} <= set(output):
        output["shots_on_target_rate"] = (
            pd.to_numeric(output["shots_on_target"], errors="coerce")
            / pd.to_numeric(output["shots"], errors="coerce").replace(0, np.nan)
        )
    return output


def derive_reception_features(events: pd.DataFrame) -> pd.DataFrame:
    """Derive progressive and dangerous-zone named pass receptions."""

    required = {
        "type",
        "pass_outcome",
        "pass_recipient_id",
        "location",
        "pass_end_location",
    }
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(f"Reception feature columns missing: {sorted(missing)}")
    passes = events.loc[
        events["type"].eq("Pass")
        & events["pass_outcome"].isna()
        & events["pass_recipient_id"].notna()
    ].copy()
    passes["start_x"] = coordinate_axis(passes["location"], 0)
    passes["end_x"] = coordinate_axis(passes["pass_end_location"], 0)
    passes["end_y"] = coordinate_axis(passes["pass_end_location"], 1)
    passes["progressive_reception"] = (
        (passes["end_x"] - passes["start_x"] >= 10.0)
        | ((passes["start_x"] < 80.0) & (passes["end_x"] >= 80.0))
    )
    passes["dangerous_zone_reception"] = (
        (passes["end_x"] >= 80.0)
        & passes["end_y"].between(18.0, 62.0)
    )
    return (
        passes.groupby("pass_recipient_id", as_index=False)
        .agg(
            progressive_receptions=("progressive_reception", "sum"),
            dangerous_zone_receptions=("dangerous_zone_reception", "sum"),
            average_receiving_x=("end_x", "mean"),
            average_receiving_y=("end_y", "mean"),
        )
        .rename(columns={"pass_recipient_id": "player_id"})
        .assign(player_id=lambda frame: frame["player_id"].astype(int))
    )


def derive_pressure_outcomes(
    events: pd.DataFrame,
    *,
    action_window: int = 3,
    time_window_seconds: float = 4.0,
) -> pd.DataFrame:
    """Attribute short-horizon rushed actions and recoveries to named pressers."""

    required = {
        "match_id",
        "index",
        "period",
        "minute",
        "second",
        "team",
        "type",
        "player_id",
        "pass_outcome",
    }
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(f"Pressure-outcome columns missing: {sorted(missing)}")
    ordered = events.sort_values(["match_id", "period", "index"]).copy()
    ordered["_time"] = (
        pd.to_numeric(ordered["minute"], errors="coerce").fillna(0.0) * 60.0
        + pd.to_numeric(ordered["second"], errors="coerce").fillna(0.0)
    )
    is_pressure = ordered["type"].eq("Pressure") & ordered["player_id"].notna()
    forced = pd.Series(False, index=ordered.index)
    recovered = pd.Series(False, index=ordered.index)
    for offset in range(1, action_window + 1):
        future_match = ordered["match_id"].shift(-offset)
        future_period = ordered["period"].shift(-offset)
        future_team = ordered["team"].shift(-offset)
        future_type = ordered["type"].shift(-offset)
        future_outcome = ordered["pass_outcome"].shift(-offset)
        future_time = ordered["_time"].shift(-offset)
        same_sequence = (
            future_match.eq(ordered["match_id"])
            & future_period.eq(ordered["period"])
            & (future_time - ordered["_time"]).between(
                0.0,
                time_window_seconds,
            )
        )
        opponent_action = future_team.ne(ordered["team"])
        rushed_action = (
            future_type.isin(
                {
                    "Clearance",
                    "Miscontrol",
                    "Dispossessed",
                    "Error",
                }
            )
            | (future_type.eq("Pass") & future_outcome.notna())
        )
        team_recovery = future_team.eq(ordered["team"]) & future_type.isin(
            {"Ball Recovery", "Interception", "Duel"}
        )
        forced |= same_sequence & opponent_action & rushed_action
        recovered |= same_sequence & team_recovery
    pressure_rows = ordered.loc[is_pressure].copy()
    pressure_rows["forced_rushed_action"] = forced.loc[is_pressure].astype(int)
    pressure_rows["post_pressure_recovery"] = recovered.loc[is_pressure].astype(
        int
    )
    output = (
        pressure_rows.groupby("player_id", as_index=False)
        .agg(
            pressure_events=("type", "size"),
            forced_rushed_actions=("forced_rushed_action", "sum"),
            post_pressure_recoveries=("post_pressure_recovery", "sum"),
        )
        .assign(player_id=lambda frame: frame["player_id"].astype(int))
    )
    output["forced_rushed_action_rate"] = (
        output["forced_rushed_actions"]
        / output["pressure_events"].replace(0, np.nan)
    )
    return output

