"""Lightweight spatial defensive-disruption (xD-style) features."""

from __future__ import annotations

import numpy as np
import pandas as pd


GRID_COLUMNS = 6
GRID_ROWS = 8
ACTION_IMPACT_FACTORS: dict[str, float] = {
    "Interception": 1.0,
    "Clearance": 1.0,
    "Duel": 0.7,
    "Tackle": 0.7,
    "Block": 0.7,
    "Pressure": 0.4,
    "Ball Recovery": 0.4,
    "Goal Keeper": 0.7,
}


def _base_threat(
    start_x: pd.Series,
    start_y: pd.Series,
) -> pd.Series:
    """Return coarse-grid threat from the defending team's perspective."""

    x = pd.to_numeric(start_x, errors="coerce").clip(0.0, 119.999)
    y = pd.to_numeric(start_y, errors="coerce").clip(0.0, 79.999)
    column = np.floor(x / (120.0 / GRID_COLUMNS)).astype("Int64")
    row = np.floor(y / (80.0 / GRID_ROWS)).astype("Int64")
    zone_x = (column.astype(float) + 0.5) / GRID_COLUMNS
    zone_y = (row.astype(float) + 0.5) / GRID_ROWS
    own_goal_proximity = np.square(1.0 - zone_x)
    centrality = 1.0 - 2.0 * np.abs(zone_y - 0.5)
    threat = 0.15 + 0.65 * own_goal_proximity + 0.20 * centrality
    return pd.Series(
        np.clip(threat, 0.0, 1.0),
        index=start_x.index,
        dtype=float,
    )


def defensive_action_disruption(actions: pd.DataFrame) -> pd.DataFrame:
    """Score eligible defensive actions using zone threat and action impact."""

    required = {"player_id", "type_name", "start_x", "start_y"}
    missing = required.difference(actions.columns)
    if missing:
        raise ValueError(f"xD action fields missing: {sorted(missing)}")
    eligible = actions["type_name"].isin(ACTION_IMPACT_FACTORS)
    scored = actions.loc[
        eligible & actions["player_id"].notna()
    ].copy()
    scored["xd_zone_threat"] = _base_threat(
        scored["start_x"],
        scored["start_y"],
    )
    scored["xd_action_impact"] = scored["type_name"].map(
        ACTION_IMPACT_FACTORS
    )
    scored["disruption_score"] = (
        scored["xd_zone_threat"] * scored["xd_action_impact"]
    )
    return scored


def derive_defense_disruption(
    actions: pd.DataFrame,
    player_profiles: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate xD per 90 and broad-position percentiles for every player."""

    required_profiles = {"player_id", "minutes", "position_group"}
    missing = required_profiles.difference(player_profiles.columns)
    if missing:
        raise ValueError(f"xD profile fields missing: {sorted(missing)}")
    scored = defensive_action_disruption(actions)
    totals = (
        scored.groupby("player_id", as_index=False)
        .agg(
            xd_total=("disruption_score", "sum"),
            xd_actions=("disruption_score", "size"),
            xd_mean_action_threat=("xd_zone_threat", "mean"),
        )
    )
    output = player_profiles[
        ["player_id", "minutes", "position_group"]
    ].drop_duplicates("player_id").merge(
        totals,
        on="player_id",
        how="left",
        validate="one_to_one",
    )
    output["xd_total"] = output["xd_total"].fillna(0.0)
    output["xd_actions"] = output["xd_actions"].fillna(0).astype(int)
    minutes = pd.to_numeric(
        output["minutes"],
        errors="coerce",
    ).clip(lower=1.0)
    output["xd90"] = 90.0 * output["xd_total"] / minutes
    output["xd90_pct"] = output.groupby("position_group")["xd90"].rank(
        method="average",
        pct=True,
    )
    return output.drop(columns=["minutes", "position_group"])
