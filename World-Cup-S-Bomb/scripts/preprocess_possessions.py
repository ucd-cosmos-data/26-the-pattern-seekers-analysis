#!/usr/bin/env python3
"""Build a validated, possession-level World Cup dataset from StatsBomb events.

The script is intentionally self-contained and uses only Python's standard
library. It never modifies the source CSV. By default, paths are resolved from
the project directory, so the script can be run from anywhere.
"""

from __future__ import annotations

import argparse
import ast
import csv
import math
import statistics
from collections import Counter
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = PROJECT_ROOT / "notebooks" / "all_events.csv"
DEFAULT_MATCHES = PROJECT_ROOT / "data" / "raw" / "matches.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "world_cup_possessions.csv"
DEFAULT_DICTIONARY = PROJECT_ROOT / "data" / "processed" / "possession_data_dictionary.md"
DEFAULT_REPORT = PROJECT_ROOT / "results" / "possession_validation_report.md"

PITCH_LENGTH = 120.0
PITCH_WIDTH = 80.0
FINAL_THIRD_X = 80.0
BOX_X = 102.0
BOX_Y_MIN = 18.0
BOX_Y_MAX = 62.0
PROGRESSIVE_GAIN = 10.0
LONG_ACTION_DISTANCE = 30.0

ADMIN_TYPES = {
    "Starting XI",
    "Half Start",
    "Half End",
    "Substitution",
    "Tactical Shift",
    "Injury Stoppage",
    "Player Off",
    "Player On",
    "Bad Behaviour",
}

# Ball receipts duplicate the receiving endpoint of passes and include a small
# number of period-boundary records with stale timestamps. Excluding them from
# timing and spatial summaries prevents double-counting and false long durations.
NON_ANALYTIC_TYPES = ADMIN_TYPES | {"Ball Receipt*"}

DEFENSIVE_ACTION_TYPES = {
    "Pressure",
    "Duel",
    "Interception",
    "Block",
    "Clearance",
    "Ball Recovery",
    "Foul Committed",
}


def parse_location(value: str) -> tuple[float, float] | None:
    """Parse a StatsBomb location string without executing arbitrary code."""
    if not value:
        return None
    try:
        location = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return None
    if not isinstance(location, (list, tuple)) or len(location) < 2:
        return None
    try:
        x, y = float(location[0]), float(location[1])
    except (TypeError, ValueError):
        return None
    if not (math.isfinite(x) and math.isfinite(y)):
        return None
    return x, y


def as_float(value: str, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def as_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def is_true(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"} if value else False


def distance(start: tuple[float, float] | None, end: tuple[float, float] | None) -> float:
    if start is None or end is None:
        return 0.0
    return math.hypot(end[0] - start[0], end[1] - start[1])


def entered_zone(
    start: tuple[float, float] | None,
    end: tuple[float, float] | None,
    zone: str,
) -> bool:
    if start is None or end is None:
        return False
    if zone == "final_third":
        return start[0] < FINAL_THIRD_X <= end[0]
    if zone == "penalty_area":
        start_in = start[0] >= BOX_X and BOX_Y_MIN <= start[1] <= BOX_Y_MAX
        end_in = end[0] >= BOX_X and BOX_Y_MIN <= end[1] <= BOX_Y_MAX
        return not start_in and end_in
    raise ValueError(f"Unknown zone: {zone}")


def zone_label(location: tuple[float, float] | None) -> str:
    if location is None:
        return "Unknown"
    x, y = location
    third = "Defensive third" if x < 40 else "Middle third" if x < 80 else "Final third"
    channel = "Left" if y < 26.67 else "Central" if y <= 53.33 else "Right"
    return f"{third} - {channel}"


@dataclass
class MatchInfo:
    home_team: str
    away_team: str
    match_date: str
    competition_stage: str

    def opponent(self, team: str) -> str:
        if team == self.home_team:
            return self.away_team
        if team == self.away_team:
            return self.home_team
        return "Unknown"


@dataclass
class PossessionAccumulator:
    match_id: int
    period: int
    possession: int
    possession_team: str
    possession_team_id: int
    match_info: MatchInfo
    event_count: int = 0
    active_event_count: int = 0
    start_time_seconds: float = math.inf
    end_time_seconds: float = -math.inf
    start_minute: int = 0
    end_minute: int = 0
    start_location: tuple[float, float] | None = None
    end_location: tuple[float, float] | None = None
    start_sort_key: tuple[float, int] = (math.inf, 10**9)
    end_sort_key: tuple[float, int] = (-math.inf, -1)
    play_patterns: Counter[str] = field(default_factory=Counter)
    players: set[str] = field(default_factory=set)
    action_times: list[float] = field(default_factory=list)
    attack_ys: list[float] = field(default_factory=list)
    pass_count: int = 0
    completed_pass_count: int = 0
    progressive_pass_count: int = 0
    through_ball_count: int = 0
    long_ball_count: int = 0
    switch_count: int = 0
    cross_count: int = 0
    cutback_count: int = 0
    pass_lengths: list[float] = field(default_factory=list)
    pass_forward_gain: float = 0.0
    carry_count: int = 0
    progressive_carry_count: int = 0
    carry_distances: list[float] = field(default_factory=list)
    carry_forward_gain: float = 0.0
    dribble_count: int = 0
    successful_dribble_count: int = 0
    final_third_entries: int = 0
    penalty_area_entries: int = 0
    under_pressure_actions: int = 0
    opponent_pressure_events: int = 0
    opponent_counterpress_events: int = 0
    opponent_defensive_actions: int = 0
    opponent_defensive_x: list[float] = field(default_factory=list)
    opponent_defensive_y: list[float] = field(default_factory=list)
    shot_count: int = 0
    goal_count: int = 0
    own_goal_count: int = 0
    xg_values: list[float] = field(default_factory=list)
    opponent_transition_shot_count: int = 0
    opponent_transition_goal_count: int = 0
    opponent_transition_xg_values: list[float] = field(default_factory=list)

    def add(self, row: dict[str, str]) -> None:
        event_type = row["type"]
        team = row["team"]
        on_attack = team == self.possession_team
        minute = as_int(row["minute"])
        second = as_float(row["second"])
        event_time = minute * 60.0 + second
        event_end_time = event_time + max(0.0, as_float(row["duration"]))
        event_index = as_int(row["index"])
        location = parse_location(row["location"])

        self.event_count += 1
        if event_type not in NON_ANALYTIC_TYPES:
            self.active_event_count += 1
            self.start_time_seconds = min(self.start_time_seconds, event_time)
            self.end_time_seconds = max(self.end_time_seconds, event_end_time)
            self.start_minute = min(self.start_minute, minute) if self.start_time_seconds != event_time else minute
            self.end_minute = max(self.end_minute, minute)

        if row["play_pattern"]:
            self.play_patterns[row["play_pattern"]] += 1

        if on_attack:
            if row["player"]:
                self.players.add(row["player"])
            if event_type not in NON_ANALYTIC_TYPES:
                self.action_times.append(event_time)
            if location is not None and event_type not in NON_ANALYTIC_TYPES:
                self.attack_ys.append(location[1])
                sort_key = (event_time, event_index)
                if sort_key < self.start_sort_key:
                    self.start_sort_key = sort_key
                    self.start_location = location
                if sort_key > self.end_sort_key:
                    self.end_sort_key = sort_key
                    self.end_location = location
            if is_true(row["under_pressure"]):
                self.under_pressure_actions += 1
            self._add_attacking_event(row, event_type, location)
        else:
            self._add_opponent_event(row, event_type, location)

    def _add_attacking_event(
        self,
        row: dict[str, str],
        event_type: str,
        start: tuple[float, float] | None,
    ) -> None:
        if event_type == "Pass":
            end = parse_location(row["pass_end_location"])
            self.pass_count += 1
            if not row["pass_outcome"]:
                self.completed_pass_count += 1
            pass_distance = as_float(row["pass_length"], distance(start, end))
            self.pass_lengths.append(pass_distance)
            if start is not None and end is not None:
                gain = end[0] - start[0]
                self.pass_forward_gain += max(0.0, gain)
                self.progressive_pass_count += int(gain >= PROGRESSIVE_GAIN)
            self.through_ball_count += int(is_true(row["pass_through_ball"]))
            self.long_ball_count += int(pass_distance >= LONG_ACTION_DISTANCE)
            self.switch_count += int(is_true(row["pass_switch"]))
            self.cross_count += int(is_true(row["pass_cross"]))
            self.cutback_count += int(is_true(row["pass_cut_back"]))
            self.final_third_entries += int(entered_zone(start, end, "final_third"))
            self.penalty_area_entries += int(entered_zone(start, end, "penalty_area"))
            if end is not None:
                self._update_end_location(end, row)

        elif event_type == "Carry":
            end = parse_location(row["carry_end_location"])
            carry_distance = distance(start, end)
            self.carry_count += 1
            self.carry_distances.append(carry_distance)
            if start is not None and end is not None:
                gain = end[0] - start[0]
                self.carry_forward_gain += max(0.0, gain)
                self.progressive_carry_count += int(gain >= PROGRESSIVE_GAIN)
            self.final_third_entries += int(entered_zone(start, end, "final_third"))
            self.penalty_area_entries += int(entered_zone(start, end, "penalty_area"))
            if end is not None:
                self._update_end_location(end, row)

        elif event_type == "Dribble":
            self.dribble_count += 1
            self.successful_dribble_count += int(row["dribble_outcome"] == "Complete")

        elif event_type == "Shot":
            self.shot_count += 1
            self.goal_count += int(row["shot_outcome"] == "Goal")
            if row["shot_statsbomb_xg"]:
                self.xg_values.append(as_float(row["shot_statsbomb_xg"]))

        elif event_type == "Own Goal For":
            self.own_goal_count += 1

    def _update_end_location(self, end: tuple[float, float], row: dict[str, str]) -> None:
        event_time = as_int(row["minute"]) * 60.0 + as_float(row["second"])
        event_end_time = event_time + max(0.0, as_float(row["duration"]))
        sort_key = (event_end_time, as_int(row["index"]))
        if sort_key >= self.end_sort_key:
            self.end_sort_key = sort_key
            self.end_location = end

    def _add_opponent_event(
        self,
        row: dict[str, str],
        event_type: str,
        location: tuple[float, float] | None,
    ) -> None:
        # StatsBomb occasionally keeps a rapid shot after a turnover inside the
        # previous team's possession. Preserve it as a conceded transition
        # outcome instead of incorrectly crediting it to the possession team.
        if event_type == "Shot":
            self.opponent_transition_shot_count += 1
            self.opponent_transition_goal_count += int(row["shot_outcome"] == "Goal")
            if row["shot_statsbomb_xg"]:
                self.opponent_transition_xg_values.append(as_float(row["shot_statsbomb_xg"]))

        self.opponent_pressure_events += int(event_type == "Pressure")
        self.opponent_counterpress_events += int(is_true(row["counterpress"]))
        if event_type in DEFENSIVE_ACTION_TYPES:
            self.opponent_defensive_actions += 1
            if location is not None:
                # Opponent events face the opposite direction. Transform x into
                # the possession team's 120x80 attacking coordinate frame.
                self.opponent_defensive_x.append(PITCH_LENGTH - location[0])
                self.opponent_defensive_y.append(PITCH_WIDTH - location[1])

    def to_row(self) -> dict[str, Any] | None:
        if self.active_event_count == 0 or self.start_location is None:
            return None

        duration = max(0.0, self.end_time_seconds - self.start_time_seconds)
        start_x, start_y = self.start_location
        end_x, end_y = self.end_location or self.start_location
        net_forward = end_x - start_x
        total_movement = sum(self.pass_lengths) + sum(self.carry_distances)
        action_times = sorted(set(self.action_times))
        time_gaps = [b - a for a, b in zip(action_times, action_times[1:]) if b >= a]
        xg = sum(self.xg_values)
        total_goals = self.goal_count + self.own_goal_count

        return {
            "possession_uid": f"{self.match_id}-{self.period}-{self.possession}",
            "match_id": self.match_id,
            "match_date": self.match_info.match_date,
            "competition_stage": self.match_info.competition_stage,
            "period": self.period,
            "possession": self.possession,
            "team_id": self.possession_team_id,
            "team": self.possession_team,
            "opponent": self.match_info.opponent(self.possession_team),
            "play_pattern": self.play_patterns.most_common(1)[0][0] if self.play_patterns else "Unknown",
            "start_minute": int(self.start_time_seconds // 60),
            "end_minute": int(self.end_time_seconds // 60),
            "start_time_seconds": round(self.start_time_seconds, 3),
            "end_time_seconds": round(self.end_time_seconds, 3),
            "duration_seconds": round(duration, 3),
            "average_seconds_between_actions": round(statistics.mean(time_gaps), 3) if time_gaps else 0.0,
            "event_count": self.active_event_count,
            "players_involved": len(self.players),
            "start_x": round(start_x, 3),
            "start_y": round(start_y, 3),
            "end_x": round(end_x, 3),
            "end_y": round(end_y, 3),
            "starting_zone": zone_label(self.start_location),
            "ending_zone": zone_label(self.end_location),
            "net_forward_distance": round(net_forward, 3),
            "total_forward_progression": round(self.pass_forward_gain + self.carry_forward_gain, 3),
            "directness_ratio": round(net_forward / total_movement, 4) if total_movement else 0.0,
            "progression_speed": round(net_forward / duration, 4) if duration else 0.0,
            "pass_count": self.pass_count,
            "completed_pass_count": self.completed_pass_count,
            "pass_completion_pct": round(100 * self.completed_pass_count / self.pass_count, 3) if self.pass_count else 0.0,
            "average_pass_length": round(statistics.mean(self.pass_lengths), 3) if self.pass_lengths else 0.0,
            "progressive_pass_count": self.progressive_pass_count,
            "through_ball_count": self.through_ball_count,
            "long_ball_count": self.long_ball_count,
            "switch_count": self.switch_count,
            "cross_count": self.cross_count,
            "cutback_count": self.cutback_count,
            "carry_count": self.carry_count,
            "progressive_carry_count": self.progressive_carry_count,
            "total_carry_distance": round(sum(self.carry_distances), 3),
            "longest_carry_distance": round(max(self.carry_distances, default=0.0), 3),
            "dribble_count": self.dribble_count,
            "successful_dribble_count": self.successful_dribble_count,
            "final_third_entries": self.final_third_entries,
            "penalty_area_entries": self.penalty_area_entries,
            "average_width_y": round(statistics.mean(self.attack_ys), 3) if self.attack_ys else 0.0,
            "width_std_y": round(statistics.pstdev(self.attack_ys), 3) if len(self.attack_ys) > 1 else 0.0,
            "width_span_y": round(max(self.attack_ys) - min(self.attack_ys), 3) if self.attack_ys else 0.0,
            "under_pressure_actions": self.under_pressure_actions,
            "opponent_pressure_events": self.opponent_pressure_events,
            "opponent_counterpress_events": self.opponent_counterpress_events,
            "opponent_defensive_actions": self.opponent_defensive_actions,
            "opponent_defensive_action_mean_x": round(statistics.mean(self.opponent_defensive_x), 3) if self.opponent_defensive_x else 0.0,
            "opponent_defensive_action_width_std": round(statistics.pstdev(self.opponent_defensive_y), 3) if len(self.opponent_defensive_y) > 1 else 0.0,
            "shot": int(self.shot_count > 0),
            "shot_count": self.shot_count,
            "goal": int(total_goals > 0),
            "goal_count": total_goals,
            "own_goal_count": self.own_goal_count,
            "xg_generated": round(xg, 6),
            "max_shot_xg": round(max(self.xg_values, default=0.0), 6),
            "dangerous_xg_020": int(xg >= 0.20),
            "entered_final_third": int(self.final_third_entries > 0 or end_x >= FINAL_THIRD_X),
            "entered_penalty_area": int(self.penalty_area_entries > 0 or (end_x >= BOX_X and BOX_Y_MIN <= end_y <= BOX_Y_MAX)),
            "opponent_transition_shot": int(self.opponent_transition_shot_count > 0),
            "opponent_transition_shot_count": self.opponent_transition_shot_count,
            "opponent_transition_goal_count": self.opponent_transition_goal_count,
            "opponent_transition_xg": round(sum(self.opponent_transition_xg_values), 6),
        }


def load_matches(path: Path) -> dict[int, MatchInfo]:
    matches: dict[int, MatchInfo] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            match_id = as_int(row["match_id"])
            matches[match_id] = MatchInfo(
                home_team=row["home_team"],
                away_team=row["away_team"],
                match_date=row["match_date"],
                competition_stage=row["competition_stage"],
            )
    return matches


def preprocess(events_path: Path, matches_path: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    matches = load_matches(matches_path)
    accumulators: dict[tuple[int, int, int], PossessionAccumulator] = {}
    source_rows = 0
    excluded_shootout_rows = 0
    invalid_group_rows = 0

    with events_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"match_id", "period", "possession", "possession_team", "possession_team_id", "type"}
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"Missing required columns in {events_path}: {missing}")

        for row in reader:
            source_rows += 1
            match_id = as_int(row["match_id"], -1)
            period = as_int(row["period"], -1)
            possession = as_int(row["possession"], -1)
            if period == 5:
                excluded_shootout_rows += 1
                continue
            if match_id not in matches or period not in {1, 2, 3, 4} or possession < 0:
                invalid_group_rows += 1
                continue

            key = (match_id, period, possession)
            if key not in accumulators:
                accumulators[key] = PossessionAccumulator(
                    match_id=match_id,
                    period=period,
                    possession=possession,
                    possession_team=row["possession_team"],
                    possession_team_id=as_int(row["possession_team_id"]),
                    match_info=matches[match_id],
                )
            accumulator = accumulators[key]
            if row["possession_team"] != accumulator.possession_team:
                raise ValueError(f"Inconsistent possession team for group {key}")
            accumulator.add(row)

    rows = [row for accumulator in accumulators.values() if (row := accumulator.to_row()) is not None]
    rows.sort(key=lambda row: (row["match_id"], row["period"], row["possession"]))
    audit = {
        "source_event_rows": source_rows,
        "excluded_penalty_shootout_rows": excluded_shootout_rows,
        "invalid_group_rows": invalid_group_rows,
        "candidate_possession_groups": len(accumulators),
        "output_possessions": len(rows),
    }
    return rows, audit


def validate(rows: list[dict[str, Any]], audit: dict[str, int]) -> dict[str, Any]:
    if not rows:
        raise ValueError("Preprocessing produced no possession rows")

    uids = [row["possession_uid"] for row in rows]
    matches = {row["match_id"] for row in rows}
    teams = {row["team"] for row in rows}
    duplicate_uids = len(uids) - len(set(uids))
    bad_completion = sum(not 0 <= float(row["pass_completion_pct"]) <= 100 for row in rows)
    negative_duration = sum(float(row["duration_seconds"]) < 0 for row in rows)
    missing_opponents = sum(row["opponent"] == "Unknown" for row in rows)
    period_five_rows = sum(int(row["period"]) == 5 for row in rows)
    goals = sum(int(row["goal_count"]) for row in rows)
    shots = sum(int(row["shot_count"]) for row in rows)
    opponent_transition_goals = sum(int(row["opponent_transition_goal_count"]) for row in rows)
    opponent_transition_shots = sum(int(row["opponent_transition_shot_count"]) for row in rows)
    possessions_with_shot = sum(int(row["shot"]) for row in rows)
    xg = sum(float(row["xg_generated"]) for row in rows)

    checks = {
        "All 64 matches represented": len(matches) == 64,
        "All 32 teams represented": len(teams) == 32,
        "Possession IDs are unique": duplicate_uids == 0,
        "No penalty-shootout rows": period_five_rows == 0,
        "No negative durations": negative_duration == 0,
        "Pass completion is within 0-100": bad_completion == 0,
        "Every team has a known opponent": missing_opponents == 0,
        "All 172 tournament goals are accounted for": goals + opponent_transition_goals == 172,
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ValueError("Validation failed: " + "; ".join(failures))

    return {
        **audit,
        "matches": len(matches),
        "teams": len(teams),
        "duplicate_possession_ids": duplicate_uids,
        "shots": shots,
        "opponent_transition_shots": opponent_transition_shots,
        "possessions_with_shot": possessions_with_shot,
        "possession_team_goals_including_own_goals": goals,
        "opponent_transition_goals": opponent_transition_goals,
        "tournament_goals_accounted_for": goals + opponent_transition_goals,
        "xg_generated": round(xg, 3),
        "checks": checks,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


FEATURE_GROUPS: dict[str, dict[str, str]] = {
    "Identifiers and context": {
        "possession_uid": "Unique key: match-period-possession.",
        "match_id": "StatsBomb match identifier.",
        "match_date": "Match date from matches.csv.",
        "competition_stage": "Tournament stage.",
        "period": "Match period; penalty shootouts (period 5) are excluded.",
        "possession": "StatsBomb possession number.",
        "team_id": "Possession-team identifier.",
        "team": "Team in possession.",
        "opponent": "Opponent derived from match metadata.",
        "play_pattern": "Most frequent StatsBomb play pattern in the possession.",
    },
    "Timing and structure": {
        "start_minute": "Minute of the first non-administrative event.",
        "end_minute": "Minute of the last non-administrative event.",
        "start_time_seconds": "First event time, using StatsBomb's match-minute clock.",
        "end_time_seconds": "Last event time plus its duration.",
        "duration_seconds": "End time minus start time.",
        "average_seconds_between_actions": "Mean gap between unique attacking-action timestamps.",
        "event_count": "Number of non-administrative events in the possession.",
        "players_involved": "Unique possession-team players involved.",
    },
    "Location and progression": {
        "start_x": "First attacking event x-coordinate on a 120x80 pitch.",
        "start_y": "First attacking event y-coordinate.",
        "end_x": "End location of the final attacking action when available.",
        "end_y": "End y-coordinate of the final attacking action.",
        "starting_zone": "Pitch third and lateral channel at possession start.",
        "ending_zone": "Pitch third and lateral channel at possession end.",
        "net_forward_distance": "End x minus start x; may be negative.",
        "total_forward_progression": "Sum of positive x gains from passes and carries.",
        "directness_ratio": "Net forward distance divided by total pass/carry distance.",
        "progression_speed": "Net forward distance per possession second.",
        "final_third_entries": "Passes/carries crossing x=80 into the final third.",
        "penalty_area_entries": "Passes/carries entering x>=102 and y=18..62.",
    },
    "Passing, carrying, and width": {
        "pass_count": "Possession-team passes attempted.",
        "completed_pass_count": "Passes with a null StatsBomb pass outcome.",
        "pass_completion_pct": "Completed passes divided by attempted passes.",
        "average_pass_length": "Mean StatsBomb pass length.",
        "progressive_pass_count": "Passes gaining at least 10 x-coordinate units.",
        "through_ball_count": "Passes flagged as through balls.",
        "long_ball_count": "Passes at least 30 pitch units long.",
        "switch_count": "Passes flagged as switches.",
        "cross_count": "Passes flagged as crosses.",
        "cutback_count": "Passes flagged as cutbacks.",
        "carry_count": "Possession-team carries.",
        "progressive_carry_count": "Carries gaining at least 10 x-coordinate units.",
        "total_carry_distance": "Sum of Euclidean carry distances.",
        "longest_carry_distance": "Longest Euclidean carry distance.",
        "dribble_count": "Dribbles attempted.",
        "successful_dribble_count": "Dribbles with outcome Complete.",
        "average_width_y": "Mean y-coordinate of attacking events.",
        "width_std_y": "Population standard deviation of attacking y-coordinates.",
        "width_span_y": "Maximum minus minimum attacking y-coordinate.",
    },
    "Pressure and event-based defensive proxies": {
        "under_pressure_actions": "Possession-team actions flagged under pressure.",
        "opponent_pressure_events": "Opponent Pressure events during the possession.",
        "opponent_counterpress_events": "Opponent events flagged counterpress.",
        "opponent_defensive_actions": "Opponent pressures, duels, interceptions, blocks, clearances, recoveries, and fouls.",
        "opponent_defensive_action_mean_x": "Mean opponent defensive-action x transformed into the possession team's attacking frame.",
        "opponent_defensive_action_width_std": "Width standard deviation of opponent defensive-action locations; a proxy, not 360 compactness.",
    },
    "Outcomes (exclude from unsupervised clustering)": {
        "shot": "1 when the possession contains at least one shot.",
        "shot_count": "Number of shots in the possession.",
        "goal": "1 when the possession produces a shot goal or own goal.",
        "goal_count": "Shot goals plus Own Goal For events.",
        "own_goal_count": "Own Goal For events.",
        "xg_generated": "Sum of StatsBomb shot xG.",
        "max_shot_xg": "Largest single-shot xG.",
        "dangerous_xg_020": "1 when possession xG is at least 0.20.",
        "entered_final_third": "1 when the possession enters or ends in the final third.",
        "entered_penalty_area": "1 when the possession enters or ends in the penalty area.",
        "opponent_transition_shot": "1 when the opponent shoots immediately after a turnover before StatsBomb changes possession attribution.",
        "opponent_transition_shot_count": "Opponent shots retained inside this StatsBomb possession.",
        "opponent_transition_goal_count": "Goals from those opponent transition shots; a conceded outcome for the possession team.",
        "opponent_transition_xg": "xG from opponent transition shots retained inside this possession.",
    },
}


def write_dictionary(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# World Cup Possession Dataset - Data Dictionary",
        "",
        "Generated by `scripts/preprocess_possessions.py` from `notebooks/all_events.csv`.",
        "Coordinates use StatsBomb's 120x80 pitch. Period 5 penalty-shootout events are excluded.",
        "",
    ]
    for group, definitions in FEATURE_GROUPS.items():
        lines.extend([f"## {group}", "", "| Column | Definition |", "|---|---|"])
        lines.extend(f"| `{column}` | {definition} |" for column, definition in definitions.items())
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, metrics: dict[str, Any], events: Path, output: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Possession Preprocessing Validation Report",
        "",
        f"- Source: `{events.relative_to(PROJECT_ROOT) if events.is_relative_to(PROJECT_ROOT) else events}`",
        f"- Output: `{output.relative_to(PROJECT_ROOT) if output.is_relative_to(PROJECT_ROOT) else output}`",
        f"- Source event rows: {metrics['source_event_rows']:,}",
        f"- Penalty-shootout rows excluded: {metrics['excluded_penalty_shootout_rows']:,}",
        f"- Candidate possession groups: {metrics['candidate_possession_groups']:,}",
        f"- Output possessions: {metrics['output_possessions']:,}",
        f"- Matches: {metrics['matches']}",
        f"- Teams: {metrics['teams']}",
        f"- Shots: {metrics['shots']:,}",
        f"- Opponent transition shots retained by StatsBomb in the prior possession: {metrics['opponent_transition_shots']:,}",
        f"- Possessions with a shot: {metrics['possessions_with_shot']:,}",
        f"- Possession-team goals including own goals: {metrics['possession_team_goals_including_own_goals']}",
        f"- Opponent transition goals: {metrics['opponent_transition_goals']}",
        f"- Tournament goals accounted for: {metrics['tournament_goals_accounted_for']}",
        f"- Total xG: {metrics['xg_generated']:.3f}",
        "",
        "## Validation checks",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    lines.extend(f"| {name} | {'PASS' if passed else 'FAIL'} |" for name, passed in metrics["checks"].items())
    lines.extend(
        [
            "",
            "## Important scope note",
            "",
            "`all_events.csv` does not contain general StatsBomb 360 freeze frames. The defensive columns are event-based pressure/action proxies and must not be labeled as exact defensive-line height or team compactness.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS, help="Input all_events.csv")
    parser.add_argument("--matches", type=Path, default=DEFAULT_MATCHES, help="Input matches.csv")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output possession CSV")
    parser.add_argument("--dictionary", type=Path, default=DEFAULT_DICTIONARY, help="Output data dictionary Markdown")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Output validation report Markdown")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for path in (args.events, args.matches):
        if not path.is_file():
            raise FileNotFoundError(path)

    rows, audit = preprocess(args.events, args.matches)
    metrics = validate(rows, audit)
    write_csv(args.output, rows)
    write_dictionary(args.dictionary)
    write_report(args.report, metrics, args.events, args.output)

    print(f"Wrote {len(rows):,} possessions to {args.output}")
    print(f"Wrote data dictionary to {args.dictionary}")
    print(f"Wrote validation report to {args.report}")


if __name__ == "__main__":
    main()
