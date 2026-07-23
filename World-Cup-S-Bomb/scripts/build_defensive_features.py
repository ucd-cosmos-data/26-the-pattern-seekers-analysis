#!/usr/bin/env python3
"""Build 360-derived defensive possession and named-player features.

Freeze-frame coordinates are normalized into the possession team's attacking
direction. Off-ball players in public StatsBomb 360 data are anonymous; named
player profiles therefore cover defensive event actors, while anonymous player
locations describe the surrounding team shape.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from itertools import groupby
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull, QhullError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = PROJECT_ROOT / "notebooks" / "all_events.csv"
DEFAULT_POSSESSIONS = PROJECT_ROOT / "data" / "processed" / "world_cup_possession_clusters.csv"
DEFAULT_FRAMES = PROJECT_ROOT / "data" / "interim" / "world_cup_360_frames.csv"
DEFAULT_VISIBLE = PROJECT_ROOT / "data" / "interim" / "world_cup_360_visible_areas.csv"
DEFAULT_FRAME_METRICS = PROJECT_ROOT / "data" / "interim" / "world_cup_360_frame_metrics.csv"
DEFAULT_DEFENSIVE_POSSESSIONS = PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_features.csv"
DEFAULT_PLAYERS = PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_players.csv"
DEFAULT_REPORT = PROJECT_ROOT / "results" / "defensive_feature_validation.md"

PITCH_LENGTH = 120.0
PITCH_WIDTH = 80.0

DEFENSIVE_ACTIONS = {
    "Pressure",
    "Duel",
    "Interception",
    "Block",
    "Clearance",
    "Ball Recovery",
    "Foul Committed",
    "50/50",
    "Shield",
}

FRAME_FIELDS = [
    "match_id",
    "event_uuid",
    "possession_uid",
    "attacking_team",
    "defending_team",
    "event_type",
    "event_minute",
    "ball_x",
    "ball_y",
    "visible_area",
    "observed_defenders",
    "observed_outfield_defenders",
    "defensive_centroid_x",
    "defensive_centroid_y",
    "back_line_height",
    "defensive_hull_area",
    "defensive_width",
    "defensive_depth",
    "defenders_behind_ball",
    "central_defenders",
    "defenders_within_5",
    "defenders_within_10",
    "nearest_defender_distance",
    "mean_defender_distance",
    "defensive_density",
    "keeper_x",
    "keeper_y",
    "defensive_actor",
    "actor_x",
    "actor_y",
    "actor_distance_from_centroid",
]


def parse_location(value: str) -> tuple[float, float] | None:
    if not value:
        return None
    try:
        location = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return None
    if not isinstance(location, (list, tuple)) or len(location) < 2:
        return None
    try:
        return float(location[0]), float(location[1])
    except (TypeError, ValueError):
        return None


def is_true(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"} if value else False


def mirror(location: tuple[float, float]) -> tuple[float, float]:
    return PITCH_LENGTH - location[0], PITCH_WIDTH - location[1]


def polygon_area(flat_coordinates: list[float]) -> float:
    if len(flat_coordinates) < 6 or len(flat_coordinates) % 2:
        return 0.0
    points = np.asarray(flat_coordinates, dtype=float).reshape(-1, 2)
    x, y = points[:, 0], points[:, 1]
    return float(abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))) / 2.0)


@dataclass(frozen=True)
class EventInfo:
    match_id: int
    event_uuid: str
    period: int
    possession: int
    possession_team: str
    event_team: str
    event_type: str
    player: str
    minute: int
    location: tuple[float, float] | None
    counterpress: bool

    @property
    def possession_uid(self) -> str:
        return f"{self.match_id}-{self.period}-{self.possession}"


@dataclass
class RunningMetrics:
    values: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    frame_count: int = 0

    def add(self, frame: dict[str, Any]) -> None:
        self.frame_count += 1
        for column in (
            "visible_area",
            "observed_defenders",
            "observed_outfield_defenders",
            "defensive_centroid_x",
            "defensive_centroid_y",
            "back_line_height",
            "defensive_hull_area",
            "defensive_width",
            "defensive_depth",
            "defenders_behind_ball",
            "central_defenders",
            "defenders_within_5",
            "defenders_within_10",
            "nearest_defender_distance",
            "mean_defender_distance",
            "defensive_density",
            "keeper_x",
        ):
            value = frame.get(column)
            if value is not None and math.isfinite(float(value)):
                self.values[column].append(float(value))

    def summarize(self) -> dict[str, Any]:
        output: dict[str, Any] = {"spatial_frame_count": self.frame_count}
        for column, values in self.values.items():
            output[f"avg_{column}"] = statistics.mean(values) if values else np.nan
        line_values = self.values.get("back_line_height", [])
        output["std_back_line_height"] = statistics.pstdev(line_values) if len(line_values) > 1 else 0.0
        output["median_back_line_height"] = statistics.median(line_values) if line_values else np.nan
        return output


@dataclass
class PlayerMetrics:
    team: str
    player: str
    matches: set[int] = field(default_factory=set)
    actions: Counter[str] = field(default_factory=Counter)
    counterpress_actions: int = 0
    actor_frame_count: int = 0
    context: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    def add_action(self, event: EventInfo) -> None:
        self.matches.add(event.match_id)
        self.actions[event.event_type] += 1
        self.counterpress_actions += int(event.counterpress)

    def add_context(self, frame: dict[str, Any]) -> None:
        self.actor_frame_count += 1
        for column in (
            "actor_x",
            "actor_y",
            "actor_distance_from_centroid",
            "back_line_height",
            "defensive_hull_area",
            "defenders_behind_ball",
            "defenders_within_5",
            "defenders_within_10",
            "visible_area",
        ):
            value = frame.get(column)
            if value is not None and math.isfinite(float(value)):
                self.context[column].append(float(value))

    def to_row(self) -> dict[str, Any]:
        total = sum(self.actions.values())
        row: dict[str, Any] = {
            "team": self.team,
            "player": self.player,
            "matches_with_defensive_action": len(self.matches),
            "defensive_actions": total,
            "pressure_actions": self.actions["Pressure"],
            "counterpress_actions": self.counterpress_actions,
            "duels": self.actions["Duel"],
            "interceptions": self.actions["Interception"],
            "blocks": self.actions["Block"],
            "clearances": self.actions["Clearance"],
            "ball_recoveries": self.actions["Ball Recovery"],
            "fouls_committed": self.actions["Foul Committed"],
            "fifty_fifties": self.actions["50/50"],
            "actor_frame_count": self.actor_frame_count,
        }
        for column, values in self.context.items():
            row[f"avg_{column}_when_acting"] = statistics.mean(values) if values else np.nan
        return row


def load_events(path: Path) -> tuple[dict[tuple[int, str], EventInfo], dict[tuple[str, str], PlayerMetrics]]:
    events: dict[tuple[int, str], EventInfo] = {}
    players: dict[tuple[str, str], PlayerMetrics] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            location = parse_location(row["location"])
            event = EventInfo(
                match_id=int(row["match_id"]),
                event_uuid=row["id"],
                period=int(row["period"]),
                possession=int(row["possession"]),
                possession_team=row["possession_team"],
                event_team=row["team"],
                event_type=row["type"],
                player=row["player"],
                minute=int(row["minute"]),
                location=location,
                counterpress=is_true(row["counterpress"]),
            )
            events[(event.match_id, event.event_uuid)] = event
            if (
                event.event_type in DEFENSIVE_ACTIONS
                and event.event_team != event.possession_team
                and event.player
            ):
                key = (event.event_team, event.player)
                players.setdefault(key, PlayerMetrics(*key)).add_action(event)
    return events, players


def load_visible_areas(path: Path) -> dict[tuple[int, str], float]:
    areas: dict[tuple[int, str], float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                coordinates = json.loads(row["visible_area"])
            except (json.JSONDecodeError, TypeError):
                coordinates = []
            areas[(int(row["match_id"]), row["event_uuid"])] = polygon_area(coordinates)
    return areas


def frame_group_key(row: dict[str, str]) -> tuple[int, str]:
    return int(row["match_id"]), row["event_uuid"]


def compute_frame_metrics(
    event: EventInfo,
    actor_rows: list[dict[str, str]],
    visible_area: float,
) -> dict[str, Any] | None:
    if event.location is None:
        return None
    event_is_attack = event.event_team == event.possession_team
    ball = event.location if event_is_attack else mirror(event.location)

    defenders: list[dict[str, Any]] = []
    for row in actor_rows:
        teammate = is_true(row["teammate"])
        is_defender = not teammate if event_is_attack else teammate
        if not is_defender:
            continue
        location = (float(row["x"]), float(row["y"]))
        normalized = location if event_is_attack else mirror(location)
        defenders.append(
            {
                "x": normalized[0],
                "y": normalized[1],
                "keeper": is_true(row["keeper"]),
                "actor": is_true(row["actor"]),
            }
        )
    if not defenders:
        return None

    outfield = [defender for defender in defenders if not defender["keeper"]]
    shape_players = outfield if len(outfield) >= 3 else defenders
    coordinates = np.asarray([(player["x"], player["y"]) for player in shape_players], dtype=float)
    xs, ys = coordinates[:, 0], coordinates[:, 1]
    centroid_x, centroid_y = float(xs.mean()), float(ys.mean())
    hull_area = 0.0
    if len(coordinates) >= 3:
        try:
            # In a 2D SciPy hull, .volume is enclosed area; .area is perimeter.
            hull_area = float(ConvexHull(coordinates).volume)
        except QhullError:
            hull_area = 0.0

    deepest_x = sorted((player["x"] for player in outfield), reverse=True)[:3]
    back_line_height = PITCH_LENGTH - statistics.median(deepest_x) if deepest_x else np.nan
    distances = [math.hypot(player["x"] - ball[0], player["y"] - ball[1]) for player in outfield]
    keepers = [player for player in defenders if player["keeper"]]
    actor = next((player for player in defenders if player["actor"]), None)
    actor_distance = (
        math.hypot(actor["x"] - centroid_x, actor["y"] - centroid_y) if actor is not None else np.nan
    )

    return {
        "match_id": event.match_id,
        "event_uuid": event.event_uuid,
        "possession_uid": event.possession_uid,
        "attacking_team": event.possession_team,
        "defending_team": event.event_team if not event_is_attack else "",
        "event_type": event.event_type,
        "event_minute": event.minute,
        "ball_x": ball[0],
        "ball_y": ball[1],
        "visible_area": visible_area,
        "observed_defenders": len(defenders),
        "observed_outfield_defenders": len(outfield),
        "defensive_centroid_x": centroid_x,
        "defensive_centroid_y": centroid_y,
        "back_line_height": back_line_height,
        "defensive_hull_area": hull_area,
        "defensive_width": float(ys.max() - ys.min()),
        "defensive_depth": float(xs.max() - xs.min()),
        "defenders_behind_ball": sum(player["x"] >= ball[0] for player in outfield),
        "central_defenders": sum(18.0 <= player["y"] <= 62.0 for player in outfield),
        "defenders_within_5": sum(distance <= 5.0 for distance in distances),
        "defenders_within_10": sum(distance <= 10.0 for distance in distances),
        "nearest_defender_distance": min(distances) if distances else np.nan,
        "mean_defender_distance": statistics.mean(distances) if distances else np.nan,
        "defensive_density": len(shape_players) / hull_area if hull_area > 0 else np.nan,
        "keeper_x": keepers[0]["x"] if keepers else np.nan,
        "keeper_y": keepers[0]["y"] if keepers else np.nan,
        "defensive_actor": event.player if actor is not None and not event_is_attack else "",
        "actor_x": actor["x"] if actor is not None else np.nan,
        "actor_y": actor["y"] if actor is not None else np.nan,
        "actor_distance_from_centroid": actor_distance,
    }


def process_frames(
    frame_path: Path,
    events: dict[tuple[int, str], EventInfo],
    visible_areas: dict[tuple[int, str], float],
    frame_output: Path,
    players: dict[tuple[str, str], PlayerMetrics],
    defending_teams: dict[str, str],
) -> tuple[dict[str, RunningMetrics], dict[str, int]]:
    possession_metrics: dict[str, RunningMetrics] = {}
    counters = Counter()
    frame_output.parent.mkdir(parents=True, exist_ok=True)
    with frame_path.open(newline="", encoding="utf-8") as handle, frame_output.open(
        "w", newline="", encoding="utf-8"
    ) as output_handle:
        reader = csv.DictReader(handle)
        writer = csv.DictWriter(output_handle, fieldnames=FRAME_FIELDS)
        writer.writeheader()
        for key, group in groupby(reader, key=frame_group_key):
            counters["input_frames"] += 1
            event = events.get(key)
            if event is None:
                counters["unmatched_events"] += 1
                continue
            metric = compute_frame_metrics(event, list(group), visible_areas.get(key, 0.0))
            if metric is None:
                counters["frames_without_metrics"] += 1
                continue
            metric["defending_team"] = defending_teams.get(
                event.possession_uid, metric["defending_team"]
            )
            writer.writerow(metric)
            counters["output_frames"] += 1
            possession_metrics.setdefault(event.possession_uid, RunningMetrics()).add(metric)
            if metric["defensive_actor"] and event.event_team != event.possession_team:
                player = players.get((event.event_team, event.player))
                if player is not None:
                    player.add_context(metric)
    return possession_metrics, dict(counters)


def write_defensive_possessions(
    source_path: Path,
    output_path: Path,
    possession_metrics: dict[str, RunningMetrics],
) -> pd.DataFrame:
    source = pd.read_csv(source_path)
    spatial_rows = [
        {"possession_uid": possession_uid, **metrics.summarize()}
        for possession_uid, metrics in possession_metrics.items()
    ]
    spatial = pd.DataFrame(spatial_rows)
    output = source.merge(spatial, on="possession_uid", how="left", validate="one_to_one")
    output["defending_team"] = output["opponent"]
    output["spatial_frame_count"] = output["spatial_frame_count"].fillna(0).astype(int)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)
    return output


def write_players(path: Path, players: dict[tuple[str, str], PlayerMetrics]) -> pd.DataFrame:
    rows = [player.to_row() for player in players.values()]
    output = pd.DataFrame(rows).sort_values(
        ["defensive_actions", "actor_frame_count"], ascending=False
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(path, index=False)
    return output


def validate(
    possessions: pd.DataFrame,
    players: pd.DataFrame,
    counters: dict[str, int],
) -> tuple[dict[str, Any], dict[str, bool]]:
    covered = possessions["spatial_frame_count"] > 0
    metrics = {
        **counters,
        "possession_rows": len(possessions),
        "possessions_with_spatial_frames": int(covered.sum()),
        "possession_coverage_pct": float(100 * covered.mean()),
        "matches_with_spatial_frames": int(possessions.loc[covered, "match_id"].nunique()),
        "teams_with_spatial_frames": int(possessions.loc[covered, "team"].nunique()),
        "named_defensive_players": len(players),
        "players_with_actor_context": int((players["actor_frame_count"] > 0).sum()),
    }
    checks = {
        "All 64 matches have spatial possession features": metrics["matches_with_spatial_frames"] == 64,
        "All 32 attacking teams have spatial possession features": metrics["teams_with_spatial_frames"] == 32,
        "At least 90% of possessions have a 360 frame": metrics["possession_coverage_pct"] >= 90,
        "At least 95% of cached frames produced metrics": counters["output_frames"]
        >= 0.95 * counters["input_frames"],
        "Named defensive players were identified": metrics["named_defensive_players"] > 500,
        "Most named defensive players have actor context": metrics["players_with_actor_context"]
        >= 0.8 * metrics["named_defensive_players"],
        "Possession IDs remain unique": possessions["possession_uid"].is_unique,
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ValueError("Defensive feature validation failed: " + "; ".join(failures))
    return metrics, checks


def write_report(
    path: Path,
    metrics: dict[str, Any],
    checks: dict[str, bool],
) -> None:
    lines = [
        "# Defensive Spatial Feature Validation",
        "",
        f"- Input 360 event frames: {metrics['input_frames']:,}",
        f"- Frames with derived spatial metrics: {metrics['output_frames']:,}",
        f"- Possession rows: {metrics['possession_rows']:,}",
        f"- Possessions with spatial frames: {metrics['possessions_with_spatial_frames']:,} ({metrics['possession_coverage_pct']:.2f}%)",
        f"- Matches covered: {metrics['matches_with_spatial_frames']}",
        f"- Teams covered: {metrics['teams_with_spatial_frames']}",
        f"- Named defensive players: {metrics['named_defensive_players']:,}",
        f"- Named players with 360 actor context: {metrics['players_with_actor_context']:,}",
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    lines.extend(f"| {name} | {'PASS' if passed else 'FAIL'} |" for name, passed in checks.items())
    lines.extend(
        [
            "",
            "## Method notes",
            "",
            "- Coordinates are normalized into the possession team's attacking direction.",
            "- `back_line_height` is the median distance from the defending goal of the three deepest observed outfield defenders.",
            "- Defensive footprint uses `scipy.spatial.ConvexHull.volume`, which is enclosed area in two dimensions.",
            "- Off-ball public 360 players are anonymous; named profiles cover defensive event actors only.",
            "- Visible-area and observed-player counts are retained so downstream models can control for partial pitch visibility.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--possessions", type=Path, default=DEFAULT_POSSESSIONS)
    parser.add_argument("--frames", type=Path, default=DEFAULT_FRAMES)
    parser.add_argument("--visible", type=Path, default=DEFAULT_VISIBLE)
    parser.add_argument("--frame-metrics", type=Path, default=DEFAULT_FRAME_METRICS)
    parser.add_argument("--defensive-possessions", type=Path, default=DEFAULT_DEFENSIVE_POSSESSIONS)
    parser.add_argument("--players", type=Path, default=DEFAULT_PLAYERS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for path in (args.events, args.possessions, args.frames, args.visible):
        if not path.is_file():
            raise FileNotFoundError(path)

    print("Loading event and named-player context...")
    events, players = load_events(args.events)
    possession_context = pd.read_csv(
        args.possessions, usecols=["possession_uid", "opponent"]
    )
    defending_teams = dict(
        zip(possession_context["possession_uid"], possession_context["opponent"])
    )
    print("Loading visible-area coverage...")
    visible_areas = load_visible_areas(args.visible)
    print("Deriving frame and possession spatial metrics...")
    possession_metrics, counters = process_frames(
        args.frames,
        events,
        visible_areas,
        args.frame_metrics,
        players,
        defending_teams,
    )
    possessions = write_defensive_possessions(
        args.possessions, args.defensive_possessions, possession_metrics
    )
    player_output = write_players(args.players, players)
    metrics, checks = validate(possessions, player_output, counters)
    write_report(args.report, metrics, checks)

    print(f"Wrote frame metrics to {args.frame_metrics}")
    print(f"Wrote defensive possession features to {args.defensive_possessions}")
    print(f"Wrote defensive player profiles to {args.players}")
    print(f"Wrote validation report to {args.report}")


if __name__ == "__main__":
    main()
