#!/usr/bin/env python3
"""Build player-match skill components and active-lineup inputs from StatsBomb events."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = PROJECT_ROOT / "notebooks" / "all_events.csv"
DEFAULT_POSSESSIONS = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_clusters.csv"
)
DEFAULT_COMPONENTS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_player_match_components.csv"
)
DEFAULT_INTERVALS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_lineup_intervals.csv"
)
DEFAULT_LINEUPS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_possession_lineups.csv"
)
DEFAULT_VALIDATION = PROJECT_ROOT / "results" / "player_skill_input_validation.md"

EVENT_COLUMNS = [
    "match_id",
    "id",
    "type",
    "team",
    "player",
    "player_id",
    "position",
    "period",
    "minute",
    "second",
    "possession",
    "possession_team",
    "tactics",
    "substitution_replacement",
    "substitution_replacement_id",
    "location",
    "pass_end_location",
    "carry_end_location",
    "pass_outcome",
    "pass_length",
    "pass_cross",
    "pass_switch",
    "pass_through_ball",
    "pass_shot_assist",
    "pass_goal_assist",
    "dribble_outcome",
    "duel_outcome",
    "duel_type",
    "interception_outcome",
    "ball_recovery_recovery_failure",
    "shot_statsbomb_xg",
    "shot_outcome",
    "under_pressure",
    "counterpress",
    "ball_receipt_outcome",
    "pass_aerial_won",
    "clearance_aerial_won",
    "shot_aerial_won",
]

COUNT_COLUMNS = [
    "actions",
    "passes",
    "completed_passes",
    "progressive_passes",
    "final_third_passes",
    "box_passes",
    "key_passes",
    "crosses",
    "switches",
    "through_balls",
    "carries",
    "progressive_carries",
    "dribbles",
    "successful_dribbles",
    "shots",
    "goals",
    "under_pressure_actions",
    "successful_under_pressure_actions",
    "turnovers",
    "pressures",
    "counterpressures",
    "duels",
    "duels_won",
    "interceptions",
    "interceptions_won",
    "recoveries",
    "blocks",
    "clearances",
    "dribbled_past",
    "fouls",
    "aerial_events",
    "aerial_wins",
]

SUM_COLUMNS = [
    "pass_progression_sum",
    "carry_progression_sum",
    "xg_sum",
]


def parse_sequence(value: object) -> list[object]:
    if isinstance(value, (list, tuple)):
        return list(value)
    if pd.isna(value):
        return []
    try:
        parsed = ast.literal_eval(str(value))
    except (ValueError, SyntaxError):
        return []
    return list(parsed) if isinstance(parsed, (list, tuple)) else []


def parse_mapping(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    if pd.isna(value):
        return {}
    try:
        parsed = ast.literal_eval(str(value))
    except (ValueError, SyntaxError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def truthy(series: pd.Series) -> pd.Series:
    return series.fillna(False).astype(str).str.lower().eq("true")


def coordinate(series: pd.Series, index: int) -> pd.Series:
    return series.map(
        lambda value: float(values[index])
        if len(values := parse_sequence(value)) > index
        else np.nan
    )


def position_group(position: object) -> str:
    text = "" if pd.isna(position) else str(position)
    if "Goalkeeper" in text:
        return "Goalkeeper"
    if "Back" in text:
        return "Center Back" if "Center Back" in text else "Fullback/Wingback"
    if "Defensive Midfield" in text:
        return "Defensive Midfield"
    if "Center Midfield" in text or text in {"Left Midfield", "Right Midfield"}:
        return "Central/Wide Midfield"
    if "Attacking Midfield" in text or "Wing" in text:
        return "Attacking Midfield/Wing"
    if "Forward" in text:
        return "Forward"
    return "Unknown"


def mode_or_unknown(series: pd.Series) -> str:
    clean = series.dropna().astype(str)
    return clean.mode().iloc[0] if not clean.empty else "Unknown"


def build_lineup_intervals(events: pd.DataFrame) -> pd.DataFrame:
    playing_events = events[events["period"].fillna(0).between(1, 4)].copy()
    playing_events["elapsed"] = (
        playing_events["minute"].fillna(0) + playing_events["second"].fillna(0) / 60
    )
    match_end = playing_events.groupby("match_id")["elapsed"].max().clip(lower=90)
    observed_positions = (
        events.dropna(subset=["player_id"])
        .groupby(["match_id", "team", "player_id"])["position"]
        .agg(mode_or_unknown)
        .to_dict()
    )
    observed_names = (
        events.dropna(subset=["player_id"])
        .groupby(["match_id", "team", "player_id"])["player"]
        .agg(mode_or_unknown)
        .to_dict()
    )
    records: list[dict[str, object]] = []
    starting_rows = events[events["type"].eq("Starting XI")]
    for (match_id, team), group in starting_rows.groupby(["match_id", "team"]):
        end_time = float(match_end.get(match_id, 90.0))
        active: dict[int, tuple[str, float, str]] = {}
        for value in group["tactics"]:
            lineup = parse_mapping(value).get("lineup", [])
            for member in lineup if isinstance(lineup, list) else []:
                player = member.get("player", {})
                position = member.get("position", {})
                if "id" not in player:
                    continue
                player_id = int(player["id"])
                active[player_id] = (
                    str(player.get("name", player_id)),
                    0.0,
                    str(position.get("name", "Unknown")),
                )

        substitutions = events[
            events["match_id"].eq(match_id)
            & events["team"].eq(team)
            & events["type"].eq("Substitution")
        ].copy()
        substitutions["elapsed"] = (
            substitutions["minute"].fillna(0)
            + substitutions["second"].fillna(0) / 60
        )
        substitutions = substitutions.sort_values(["elapsed", "id"])
        for row in substitutions.itertuples(index=False):
            elapsed = min(float(row.elapsed), end_time)
            if pd.notna(row.player_id):
                outgoing_id = int(row.player_id)
                if outgoing_id in active:
                    name, start, initial_position = active.pop(outgoing_id)
                    records.append(
                        {
                            "match_id": match_id,
                            "team": team,
                            "player_id": outgoing_id,
                            "player": name,
                            "start_minute": start,
                            "end_minute": elapsed,
                            "minutes": max(0.0, elapsed - start),
                            "position": observed_positions.get(
                                (match_id, team, outgoing_id), initial_position
                            ),
                        }
                    )
            if pd.notna(row.substitution_replacement_id):
                incoming_id = int(row.substitution_replacement_id)
                active[incoming_id] = (
                    str(row.substitution_replacement),
                    elapsed,
                    observed_positions.get((match_id, team, incoming_id), "Unknown"),
                )

        for player_id, (name, start, initial_position) in active.items():
            records.append(
                {
                    "match_id": match_id,
                    "team": team,
                    "player_id": player_id,
                    "player": name,
                    "start_minute": start,
                    "end_minute": end_time,
                    "minutes": max(0.0, end_time - start),
                    "position": observed_positions.get(
                        (match_id, team, player_id), initial_position
                    ),
                }
            )

    intervals = pd.DataFrame(records)
    intervals["position_group"] = intervals["position"].map(position_group)
    intervals["player"] = intervals.apply(
        lambda row: observed_names.get(
            (row["match_id"], row["team"], row["player_id"]), row["player"]
        ),
        axis=1,
    )
    return intervals.sort_values(["match_id", "team", "start_minute", "player_id"])


def build_player_match_components(
    events: pd.DataFrame, intervals: pd.DataFrame
) -> pd.DataFrame:
    actors = events.dropna(subset=["player_id", "team"]).copy()
    actors["player_id"] = actors["player_id"].astype(int)
    actors["x"] = coordinate(actors["location"], 0)
    actors["end_pass_x"] = coordinate(actors["pass_end_location"], 0)
    actors["end_pass_y"] = coordinate(actors["pass_end_location"], 1)
    actors["end_carry_x"] = coordinate(actors["carry_end_location"], 0)
    actors["pass_progression"] = (actors["end_pass_x"] - actors["x"]).clip(lower=0)
    actors["carry_progression"] = (actors["end_carry_x"] - actors["x"]).clip(lower=0)

    is_pass = actors["type"].eq("Pass")
    is_carry = actors["type"].eq("Carry")
    is_dribble = actors["type"].eq("Dribble")
    is_shot = actors["type"].eq("Shot")
    completed_pass = is_pass & actors["pass_outcome"].isna()
    progressive_pass = completed_pass & actors["pass_progression"].ge(10)
    progressive_carry = is_carry & actors["carry_progression"].ge(10)
    successful_duel = actors["duel_outcome"].isin(
        ["Won", "Success In Play", "Success Out"]
    )
    successful_interception = actors["interception_outcome"].isin(
        ["Won", "Success In Play", "Success Out"]
    )
    pressure_eligible = actors["type"].isin(
        ["Pass", "Carry", "Dribble", "Ball Receipt*"]
    ) & truthy(actors["under_pressure"])
    pressure_success = pressure_eligible & ~(
        (is_pass & ~completed_pass)
        | (is_dribble & ~actors["dribble_outcome"].eq("Complete"))
        | (
            actors["type"].eq("Ball Receipt*")
            & actors["ball_receipt_outcome"].notna()
        )
    )
    aerial_events = (
        actors["pass_aerial_won"].notna()
        | actors["clearance_aerial_won"].notna()
        | actors["shot_aerial_won"].notna()
        | actors["duel_type"].astype(str).str.contains("Aerial", na=False)
    )
    aerial_wins = (
        truthy(actors["pass_aerial_won"])
        | truthy(actors["clearance_aerial_won"])
        | truthy(actors["shot_aerial_won"])
        | (
            actors["duel_type"].astype(str).str.contains("Aerial", na=False)
            & successful_duel
        )
    )

    flags = {
        "actions": actors["type"].isin(
            [
                "Pass",
                "Carry",
                "Dribble",
                "Shot",
                "Ball Receipt*",
                "Pressure",
                "Duel",
                "Interception",
                "Ball Recovery",
                "Block",
                "Clearance",
            ]
        ),
        "passes": is_pass,
        "completed_passes": completed_pass,
        "progressive_passes": progressive_pass,
        "final_third_passes": completed_pass
        & actors["x"].lt(80)
        & actors["end_pass_x"].ge(80),
        "box_passes": completed_pass
        & actors["end_pass_x"].ge(102)
        & actors["end_pass_y"].between(18, 62),
        "key_passes": is_pass
        & (
            truthy(actors["pass_shot_assist"])
            | truthy(actors["pass_goal_assist"])
        ),
        "crosses": is_pass & truthy(actors["pass_cross"]),
        "switches": is_pass & truthy(actors["pass_switch"]),
        "through_balls": is_pass & truthy(actors["pass_through_ball"]),
        "carries": is_carry,
        "progressive_carries": progressive_carry,
        "dribbles": is_dribble,
        "successful_dribbles": is_dribble
        & actors["dribble_outcome"].eq("Complete"),
        "shots": is_shot,
        "goals": is_shot & actors["shot_outcome"].eq("Goal"),
        "under_pressure_actions": pressure_eligible,
        "successful_under_pressure_actions": pressure_success,
        "turnovers": actors["type"].isin(["Miscontrol", "Dispossessed"])
        | (is_pass & ~completed_pass),
        "pressures": actors["type"].eq("Pressure"),
        "counterpressures": truthy(actors["counterpress"]),
        "duels": actors["type"].eq("Duel"),
        "duels_won": actors["type"].eq("Duel") & successful_duel,
        "interceptions": actors["type"].eq("Interception"),
        "interceptions_won": actors["type"].eq("Interception")
        & successful_interception,
        "recoveries": actors["type"].eq("Ball Recovery")
        & ~truthy(actors["ball_recovery_recovery_failure"]),
        "blocks": actors["type"].eq("Block"),
        "clearances": actors["type"].eq("Clearance"),
        "dribbled_past": actors["type"].eq("Dribbled Past"),
        "fouls": actors["type"].eq("Foul Committed"),
        "aerial_events": aerial_events,
        "aerial_wins": aerial_wins,
    }
    for name, values in flags.items():
        actors[name] = values.astype(int)
    actors["pass_progression_sum"] = actors["pass_progression"].where(is_pass, 0)
    actors["carry_progression_sum"] = actors["carry_progression"].where(is_carry, 0)
    actors["xg_sum"] = actors["shot_statsbomb_xg"].fillna(0)

    keys = ["match_id", "team", "player_id"]
    components = actors.groupby(keys)[COUNT_COLUMNS + SUM_COLUMNS].sum().reset_index()
    identity = (
        actors.groupby(keys)
        .agg(
            player=("player", mode_or_unknown),
            position=("position", mode_or_unknown),
            average_x=("x", "mean"),
            average_y=("location", lambda values: coordinate(values, 1).mean()),
        )
        .reset_index()
    )
    minutes = intervals.groupby(keys)["minutes"].sum().reset_index()
    components = components.merge(identity, on=keys, how="left").merge(
        minutes, on=keys, how="left"
    )
    components["minutes"] = components["minutes"].fillna(0)
    components["position_group"] = components["position"].map(position_group)
    return components.sort_values(keys)


def build_possession_lineups(
    possessions: pd.DataFrame, intervals: pd.DataFrame
) -> pd.DataFrame:
    interval_lookup = {
        (match_id, team): group
        for (match_id, team), group in intervals.groupby(["match_id", "team"])
    }

    def active_players(match_id: int, team: str, minute: float) -> list[int]:
        group = interval_lookup.get((match_id, team))
        if group is None:
            return []
        active = group[
            group["start_minute"].le(minute) & group["end_minute"].gt(minute)
        ]["player_id"]
        return sorted(active.astype(int).unique().tolist())

    records = []
    for row in possessions[
        ["possession_uid", "match_id", "team", "opponent", "start_minute"]
    ].itertuples(index=False):
        minute = float(row.start_minute)
        records.append(
            {
                "possession_uid": row.possession_uid,
                "match_id": row.match_id,
                "attacking_team": row.team,
                "defending_team": row.opponent,
                "attacking_player_ids": json.dumps(
                    active_players(row.match_id, row.team, minute)
                ),
                "defending_player_ids": json.dumps(
                    active_players(row.match_id, row.opponent, minute)
                ),
            }
        )
    return pd.DataFrame(records)


def write_validation(
    path: Path,
    events: pd.DataFrame,
    components: pd.DataFrame,
    intervals: pd.DataFrame,
    lineups: pd.DataFrame,
) -> None:
    attack_sizes = lineups["attacking_player_ids"].map(lambda value: len(json.loads(value)))
    defense_sizes = lineups["defending_player_ids"].map(lambda value: len(json.loads(value)))
    checks = {
        "All 64 matches have lineup intervals": intervals["match_id"].nunique() == 64,
        "All possession IDs remain unique": lineups["possession_uid"].is_unique,
        "At least 99% of possessions have 11 attackers": (attack_sizes == 11).mean()
        >= 0.99,
        "At least 99% of possessions have 11 defenders": (defense_sizes == 11).mean()
        >= 0.99,
        "Player-match components cover at least 650 players": components[
            "player_id"
        ].nunique()
        >= 650,
        "Player minutes are non-negative": components["minutes"].ge(0).all(),
    }
    lines = [
        "# Player Skill Input Validation",
        "",
        f"- Events: {len(events):,}",
        f"- Matches: {events['match_id'].nunique():,}",
        f"- Player-match component rows: {len(components):,}",
        f"- Unique players: {components['player_id'].nunique():,}",
        f"- Lineup intervals: {len(intervals):,}",
        f"- Possession lineups: {len(lineups):,}",
        f"- Possessions with 11 attackers: {(attack_sizes == 11).mean():.2%}",
        f"- Possessions with 11 defenders: {(defense_sizes == 11).mean():.2%}",
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    lines.extend(
        f"| {name} | {'PASS' if passed else 'FAIL'} |"
        for name, passed in checks.items()
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"Player input validation failed: {failed}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--possessions", type=Path, default=DEFAULT_POSSESSIONS)
    parser.add_argument("--components-output", type=Path, default=DEFAULT_COMPONENTS)
    parser.add_argument("--intervals-output", type=Path, default=DEFAULT_INTERVALS)
    parser.add_argument("--lineups-output", type=Path, default=DEFAULT_LINEUPS)
    parser.add_argument("--validation-output", type=Path, default=DEFAULT_VALIDATION)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    events = pd.read_csv(args.events, usecols=EVENT_COLUMNS, low_memory=False)
    possessions = pd.read_csv(args.possessions, low_memory=False)
    intervals = build_lineup_intervals(events)
    components = build_player_match_components(events, intervals)
    lineups = build_possession_lineups(possessions, intervals)
    for path in [
        args.components_output,
        args.intervals_output,
        args.lineups_output,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    components.to_csv(args.components_output, index=False)
    intervals.to_csv(args.intervals_output, index=False)
    lineups.to_csv(args.lineups_output, index=False)
    write_validation(
        args.validation_output, events, components, intervals, lineups
    )
    print(f"Wrote player-match components to {args.components_output}")
    print(f"Wrote lineup intervals to {args.intervals_output}")
    print(f"Wrote possession lineups to {args.lineups_output}")
    print(f"Wrote validation report to {args.validation_output}")


if __name__ == "__main__":
    main()
