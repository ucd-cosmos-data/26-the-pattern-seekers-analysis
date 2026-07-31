"""Leakage-safe prospective possession model challenger.

This module is intentionally isolated from the repository's VAEP/xT, player
rating, transition, retrospective possession, and tactical clustering systems.
It only writes a prospective challenger artifact when *both* possession
targets clear every discrimination, calibration, and statistical-improvement
gate. Otherwise, it records the rejected experiment and leaves any stable
artifact untouched.

The default event input is the repository's non-lossy flattened StatsBomb
event cache. A StatsBomb JSON/JSON.GZ file or directory is also supported.
The 360 precondition requires the raw freeze-frame JSON/JSON.GZ source even
though the flattened actor cache is used for memory-efficient feature joins.
"""

from __future__ import annotations

import argparse
import ast
import gzip
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = PROJECT_ROOT / "notebooks" / "all_events.csv"
DEFAULT_360_SOURCE = PROJECT_ROOT / "data" / "interim" / "frames360" / "raw"
DEFAULT_360_ACTORS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_360_frames.csv"
)
DEFAULT_MATCHES = PROJECT_ROOT / "data" / "raw" / "matches.csv"
DEFAULT_POSSESSIONS = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_possessions.csv"
)
DEFAULT_VALIDATION = (
    PROJECT_ROOT / "results" / "reports" / "prospective_model_validation.csv"
)
DEFAULT_ARTIFACT = PROJECT_ROOT / "models" / "prospective_possession_models.joblib"
DEFAULT_LOG = PROJECT_ROOT / "logs" / "prospective_model_improvement.log"

SENTINEL = -999.0
N_SPLITS = 5
RANDOM_STATE = 2026
BOOTSTRAP_REPLICATES = 1_000

TARGETS = {
    "box_entry": "entered_penalty_area",
    "shot": "shot",
}
BASELINES = {
    "box_entry": {
        "roc_auc": 0.6888,
        "brier": 0.1847,
        "ece": 0.02617067486945598,
    },
    "shot": {
        "roc_auc": 0.6642,
        "brier": 0.1031,
        "ece": 0.011622484252209481,
    },
}

BASE_NUMERIC = ["period", "start_minute", "start_x", "start_y"]
BASE_CATEGORICAL = ["play_pattern", "competition_stage"]
SPATIAL_FEATURES = [
    "has_360_freeze_frame",
    "opponent_x_compactness",
    "opponent_y_compactness",
    "opponents_within_3",
    "opponents_within_5",
    "opponents_within_10",
    "local_numerical_superiority",
    "opposition_defensive_line_height",
]
TEMPORAL_FEATURES = [
    "seconds_since_prior_recovery",
    "possession_starting_velocity",
]
ROLLING_FEATURES = [
    "team_rolling_build_up_speed",
    "opponent_rolling_ppda",
    "relative_build_speed_minus_ppda",
    "time_remaining_minutes",
    "score_state_time_interaction",
]
CONTEXT_CATEGORICAL = ["previous_possession_outcome", "score_state"]

POST_START_PROHIBITED = {
    "duration_seconds",
    "end_x",
    "end_y",
    "progression_speed",
    "pass_count",
    "completed_pass_count",
    "shot_count",
    "xg_generated",
    "entered_penalty_area",
    "shot",
    "goal",
}


class PreconditionError(RuntimeError):
    """Raised before data processing when a mandatory source is unavailable."""


@dataclass(frozen=True)
class FeatureLayout:
    """Named prospective feature set used by one challenger."""

    name: str
    numeric: tuple[str, ...]
    categorical: tuple[str, ...]


@dataclass
class ProbabilityCalibrator:
    """Small serializable post-hoc calibrator around a fitted estimator."""

    estimator: Any
    calibrator: Any
    method: str

    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        """Return calibrated two-column class probabilities."""

        raw = self.estimator.predict_proba(features)[:, 1]
        if self.method == "isotonic":
            probability = self.calibrator.predict(raw)
        else:
            probability = self.calibrator.predict_proba(raw.reshape(-1, 1))[
                :, 1
            ]
        probability = np.clip(probability, 0.0, 1.0)
        return np.column_stack([1.0 - probability, probability])


def configure_logging(path: Path) -> logging.Logger:
    """Create console and file logging for accepted and rejected iterations."""

    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("prospective_model_challenger")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def _source_files(path: Path, suffixes: Sequence[str]) -> list[Path]:
    """Return nonempty supported files from a file or directory source."""

    if path.is_file():
        lower = path.name.lower()
        return [path] if path.stat().st_size > 0 and any(
            lower.endswith(suffix) for suffix in suffixes
        ) else []
    if not path.is_dir():
        return []
    return [
        candidate
        for candidate in path.rglob("*")
        if candidate.is_file()
        and candidate.stat().st_size > 0
        and any(candidate.name.lower().endswith(suffix) for suffix in suffixes)
    ]


def validate_preconditions(
    event_source: Path,
    frame_source: Path,
    match_metadata: Path,
    *,
    logger: logging.Logger,
    prompt: bool = True,
) -> dict[str, list[Path]]:
    """Halt before processing unless all three mandatory real sources exist.

    No synthetic-data fallback is permitted. The repository's flattened event
    CSV is accepted because it is a direct, non-synthetic cache of the original
    StatsBomb event stream.
    """

    assets = {
        "StatsBomb event streams": _source_files(
            event_source, (".json", ".json.gz", ".csv")
        ),
        "StatsBomb 360 freeze frames": _source_files(
            frame_source, (".json", ".json.gz")
        ),
        "match metadata": _source_files(
            match_metadata, (".json", ".json.gz", ".csv")
        ),
    }
    missing = [name for name, files in assets.items() if not files]
    if missing:
        message = (
            "Mandatory prospective-model assets are missing or empty: "
            + ", ".join(missing)
            + ". Supply the real StatsBomb sources before proceeding."
        )
        logger.critical(message)
        print(f"CRITICAL: {message}", file=sys.stderr)
        if prompt and sys.stdin.isatty():
            input("Supply the missing asset(s), then press Enter to exit: ")
        raise PreconditionError(message)
    logger.info(
        "Precondition PASS | events=%d | 360 files=%d | metadata=%d",
        len(assets["StatsBomb event streams"]),
        len(assets["StatsBomb 360 freeze frames"]),
        len(assets["match metadata"]),
    )
    return assets


def _read_json_records(path: Path) -> pd.DataFrame:
    """Read a StatsBomb JSON or JSON.GZ list into a DataFrame."""

    opener = gzip.open if path.name.lower().endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list) or not payload:
        raise ValueError(f"Event source is empty or not a record list: {path}")
    frame = pd.json_normalize(payload, sep="_")
    if "match_id" not in frame:
        identifier = path.name.split(".", maxsplit=1)[0]
        if identifier.isdigit():
            frame["match_id"] = int(identifier)
    return frame


def load_event_stream(source: Path) -> pd.DataFrame:
    """Load only columns required for prospective feature construction."""

    columns = [
        "id",
        "match_id",
        "period",
        "possession",
        "index",
        "minute",
        "second",
        "timestamp",
        "team",
        "possession_team",
        "type",
        "location",
        "duration",
        "pass_end_location",
        "carry_end_location",
        "pass_outcome",
        "pass_type",
        "play_pattern",
        "counterpress",
    ]
    if source.is_file() and source.suffix.lower() == ".csv":
        header = pd.read_csv(source, nrows=0).columns
        frame = pd.read_csv(
            source,
            usecols=[column for column in columns if column in header],
            low_memory=False,
        )
    else:
        files = _source_files(source, (".json", ".json.gz"))
        parts = [_read_json_records(path) for path in files]
        frame = pd.concat(parts, ignore_index=True, sort=False)
        frame = frame[[column for column in columns if column in frame]]
    required = {"id", "match_id", "period", "possession", "type", "location"}
    missing = sorted(required - set(frame.columns))
    if missing or frame.empty:
        raise ValueError(f"Event stream missing required columns: {missing}")
    for column in columns:
        if column not in frame:
            frame[column] = np.nan
    frame["event_seconds"] = (
        60 * pd.to_numeric(frame["minute"], errors="coerce").fillna(0)
        + pd.to_numeric(frame["second"], errors="coerce").fillna(0)
    )
    frame["match_id"] = pd.to_numeric(frame["match_id"], errors="raise").astype(
        int
    )
    frame["possession"] = pd.to_numeric(
        frame["possession"], errors="coerce"
    ).fillna(-1).astype(int)
    frame["period"] = pd.to_numeric(
        frame["period"], errors="coerce"
    ).fillna(1).astype(int)
    frame["index"] = pd.to_numeric(
        frame["index"], errors="coerce"
    ).fillna(0).astype(int)
    return frame.sort_values(
        ["match_id", "period", "event_seconds", "index"]
    ).reset_index(drop=True)


def load_match_metadata(source: Path) -> pd.DataFrame:
    """Load CSV or JSON match metadata after the mandatory source gate."""

    if source.is_file() and source.suffix.lower() == ".csv":
        matches = pd.read_csv(source, low_memory=False)
    else:
        files = _source_files(source, (".json", ".json.gz"))
        matches = pd.concat(
            [_read_json_records(path) for path in files],
            ignore_index=True,
            sort=False,
        )
    if matches.empty or "match_id" not in matches:
        raise ValueError("Match metadata is empty or lacks match_id")
    matches["match_id"] = pd.to_numeric(
        matches["match_id"], errors="raise"
    ).astype(int)
    return matches


def _coordinate(value: Any, axis: int) -> float:
    """Extract one coordinate from a StatsBomb list-like value."""

    if isinstance(value, (list, tuple, np.ndarray)) and len(value) > axis:
        return float(value[axis])
    if isinstance(value, str) and value.strip():
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, (list, tuple)) and len(parsed) > axis:
                return float(parsed[axis])
        except (SyntaxError, ValueError, TypeError):
            pass
    return np.nan


def _event_end_coordinates(row: pd.Series) -> tuple[float, float]:
    """Return an event endpoint without using any future event."""

    for column in ("pass_end_location", "carry_end_location"):
        x = _coordinate(row.get(column), 0)
        y = _coordinate(row.get(column), 1)
        if np.isfinite(x) and np.isfinite(y):
            return x, y
    return _coordinate(row.get("location"), 0), _coordinate(
        row.get("location"), 1
    )


def possession_start_events(events: pd.DataFrame) -> pd.DataFrame:
    """Return the exact t=0 event for every event-stream possession."""

    starts = (
        events.sort_values(["match_id", "period", "event_seconds", "index"])
        .groupby(["match_id", "period", "possession"], as_index=False)
        .first()
    )
    starts["possession_uid"] = (
        starts["match_id"].astype(str)
        + "-"
        + starts["period"].astype(str)
        + "-"
        + starts["possession"].astype(str)
    )
    starts = starts.rename(
        columns={
            "id": "start_event_id",
            "event_seconds": "verified_start_seconds",
        }
    )
    return starts[
        [
            "possession_uid",
            "match_id",
            "period",
            "possession",
            "start_event_id",
            "verified_start_seconds",
        ]
    ]


def _classify_previous_outcome(row: pd.Series) -> str:
    """Map the preceding possession's final event to a compact category."""

    event_type = str(row.get("type", "Unknown"))
    pass_type = str(row.get("pass_type", ""))
    pattern = str(row.get("play_pattern", ""))
    if "Throw" in pass_type or "Throw" in pattern:
        return "throw_in"
    if "Goal Kick" in pass_type or "Goal Kick" in pattern:
        return "goal_kick"
    if event_type in {"Dispossessed", "Miscontrol"}:
        return "turnover"
    if event_type in {"Interception", "Ball Recovery"}:
        return (
            "high_press_turnover"
            if bool(row.get("counterpress", False))
            else "recovery"
        )
    if event_type == "Clearance":
        return "clearance"
    if event_type == "Pass" and pd.notna(row.get("pass_outcome")):
        return "incomplete_pass"
    return event_type.lower().replace(" ", "_") or "unknown"


def prior_event_features(events: pd.DataFrame) -> pd.DataFrame:
    """Build prior-only event context with explicit match-grouped shift(1)."""

    ordered = events.sort_values(
        ["match_id", "period", "event_seconds", "index"]
    ).copy()
    final = (
        ordered.groupby(
            ["match_id", "period", "possession"], as_index=False
        )
        .last()
        .sort_values(["match_id", "period", "event_seconds", "index"])
    )
    final["outcome_observation"] = final.apply(
        _classify_previous_outcome, axis=1
    )
    final["end_x"] = final.apply(
        lambda row: _event_end_coordinates(row)[0], axis=1
    )
    final["end_y"] = final.apply(
        lambda row: _event_end_coordinates(row)[1], axis=1
    )
    final["start_x_event"] = final["location"].map(
        lambda value: _coordinate(value, 0)
    )
    final["start_y_event"] = final["location"].map(
        lambda value: _coordinate(value, 1)
    )
    duration = pd.to_numeric(final["duration"], errors="coerce")
    distance = np.hypot(
        final["end_x"] - final["start_x_event"],
        final["end_y"] - final["start_y_event"],
    )
    final["velocity_observation"] = np.where(
        duration.gt(0), distance / duration, SENTINEL
    )
    grouped = final.groupby("match_id", sort=False)
    # Mandatory prospective guardrail: every inherited value is shift(1).
    final["previous_possession_outcome"] = grouped[
        "outcome_observation"
    ].shift(1)
    final["possession_starting_velocity"] = grouped[
        "velocity_observation"
    ].shift(1)
    final["prior_event_seconds"] = grouped["event_seconds"].shift(1)
    final["prior_period"] = grouped["period"].shift(1)
    final["possession_uid"] = (
        final["match_id"].astype(str)
        + "-"
        + final["period"].astype(str)
        + "-"
        + final["possession"].astype(str)
    )
    return final[
        [
            "possession_uid",
            "previous_possession_outcome",
            "possession_starting_velocity",
            "prior_event_seconds",
            "prior_period",
        ]
    ]


def recovery_window_features(
    events: pd.DataFrame, starts: pd.DataFrame
) -> pd.DataFrame:
    """Measure recovery timing from events strictly before possession t=0."""

    recovery_types = {"Ball Recovery", "Interception"}
    output: list[dict[str, Any]] = []
    by_match = {
        int(match_id): frame.sort_values(["period", "event_seconds", "index"])
        for match_id, frame in events.groupby("match_id", sort=False)
    }
    for row in starts.itertuples(index=False):
        match = by_match[int(row.match_id)]
        prior = match[
            match["period"].eq(int(row.period))
            & match["event_seconds"].lt(float(row.verified_start_seconds))
            & match["event_seconds"].ge(
                float(row.verified_start_seconds) - 5.0
            )
        ]
        recoveries = prior[prior["type"].isin(recovery_types)]
        seconds = SENTINEL
        source_time = np.nan
        if not recoveries.empty:
            source_time = float(recoveries["event_seconds"].max())
            seconds = float(row.verified_start_seconds) - source_time
        output.append(
            {
                "possession_uid": row.possession_uid,
                "seconds_since_prior_recovery": seconds,
                "recovery_source_seconds": source_time,
            }
        )
    result = pd.DataFrame(output)
    joined = starts[
        ["possession_uid", "verified_start_seconds"]
    ].merge(result, on="possession_uid", validate="one_to_one")
    invalid = joined["recovery_source_seconds"].notna() & ~joined[
        "recovery_source_seconds"
    ].lt(joined["verified_start_seconds"])
    if invalid.any():
        raise RuntimeError("Recovery feature consumed an event at or after t=0")
    return result


def spatial_start_features(
    start_events: pd.DataFrame, actors_path: Path
) -> pd.DataFrame:
    """Compute t=0 spatial features from exact start-event freeze frames."""

    required_ids = set(start_events["start_event_id"].dropna().astype(str))
    usecols = ["match_id", "event_uuid", "teammate", "actor", "x", "y"]
    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(
        actors_path, usecols=usecols, chunksize=250_000, low_memory=False
    ):
        selected = chunk[chunk["event_uuid"].astype(str).isin(required_ids)]
        if not selected.empty:
            chunks.append(selected)
    actors = (
        pd.concat(chunks, ignore_index=True)
        if chunks
        else pd.DataFrame(columns=usecols)
    )
    rows: list[dict[str, Any]] = []
    for (match_id, event_id), frame in actors.groupby(
        ["match_id", "event_uuid"], sort=False
    ):
        frame = frame.copy()
        teammate = frame["teammate"].astype(str).str.lower().eq("true")
        actor = frame["actor"].astype(str).str.lower().eq("true")
        carrier = frame[actor]
        if carrier.empty:
            continue
        ball_x = float(carrier.iloc[0]["x"])
        ball_y = float(carrier.iloc[0]["y"])
        opponents = frame[~teammate]
        teammates = frame[teammate & ~actor]
        opponent_distance = np.hypot(
            opponents["x"] - ball_x, opponents["y"] - ball_y
        )
        teammate_distance = np.hypot(
            teammates["x"] - ball_x, teammates["y"] - ball_y
        )
        deepest = opponents["x"].nlargest(min(4, len(opponents)))
        rows.append(
            {
                "match_id": int(match_id),
                "start_event_id": str(event_id),
                "has_360_freeze_frame": 1,
                "opponent_x_compactness": float(
                    opponents["x"].std(ddof=0)
                ),
                "opponent_y_compactness": float(
                    opponents["y"].std(ddof=0)
                ),
                "opponents_within_3": int((opponent_distance <= 3).sum()),
                "opponents_within_5": int((opponent_distance <= 5).sum()),
                "opponents_within_10": int((opponent_distance <= 10).sum()),
                "local_numerical_superiority": float(
                    (teammate_distance <= 10).sum()
                    / max(int((opponent_distance <= 10).sum()), 1)
                ),
                "opposition_defensive_line_height": float(deepest.median()),
            }
        )
    metrics = pd.DataFrame(rows)
    merged = start_events[
        ["possession_uid", "match_id", "start_event_id"]
    ].merge(
        metrics,
        on=["match_id", "start_event_id"],
        how="left",
        validate="one_to_one",
    )
    merged["has_360_freeze_frame"] = merged[
        "has_360_freeze_frame"
    ].fillna(0).astype(int)
    for column in SPATIAL_FEATURES[1:]:
        merged[column] = pd.to_numeric(
            merged[column], errors="coerce"
        ).fillna(SENTINEL)
    return merged[["possession_uid", *SPATIAL_FEATURES]]


def _expanding_prior(series: pd.Series) -> pd.Series:
    """Return an expanding mean containing only earlier rows."""

    return series.shift(1).expanding(min_periods=1).mean()


def add_rolling_and_match_state(possessions: pd.DataFrame) -> pd.DataFrame:
    """Add strictly shifted team/opponent histories and t=0 match state."""

    data = possessions.sort_values(
        ["match_id", "period", "start_time_seconds", "possession"]
    ).copy()
    data["team_rolling_build_up_speed"] = data.groupby(
        ["match_id", "team"], sort=False
    )["progression_speed"].transform(_expanding_prior)
    ppda_observation = (
        pd.to_numeric(data["completed_pass_count"], errors="coerce").fillna(0)
        / pd.to_numeric(
            data["opponent_defensive_actions"], errors="coerce"
        )
        .fillna(0)
        .clip(lower=1)
    )
    data["_ppda_observation"] = ppda_observation
    data["opponent_rolling_ppda"] = data.groupby(
        ["match_id", "opponent"], sort=False
    )["_ppda_observation"].transform(_expanding_prior)
    data["relative_build_speed_minus_ppda"] = (
        data["team_rolling_build_up_speed"] - data["opponent_rolling_ppda"]
    )

    score_state: dict[int, dict[str, int]] = {}
    states: list[str] = []
    differences: list[int] = []
    for row in data.itertuples():
        match_score = score_state.setdefault(int(row.match_id), {})
        team_score = match_score.get(str(row.team), 0)
        opponent_score = match_score.get(str(row.opponent), 0)
        difference = team_score - opponent_score
        differences.append(difference)
        states.append(
            "leading"
            if difference > 0
            else "trailing"
            if difference < 0
            else "level"
        )
        match_score[str(row.team)] = team_score + int(row.goal_count)
    data["score_difference_at_start"] = differences
    data["score_state"] = states
    state_number = data["score_state"].map(
        {"trailing": -1.0, "level": 0.0, "leading": 1.0}
    )
    regulation_seconds = np.where(data["period"].le(2), 90 * 60, 120 * 60)
    data["time_remaining_minutes"] = np.maximum(
        regulation_seconds - data["start_time_seconds"], 0
    ) / 60
    data["score_state_time_interaction"] = (
        state_number * data["time_remaining_minutes"]
    )
    for column in ROLLING_FEATURES:
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(
            SENTINEL
        )
    return data.drop(columns=["_ppda_observation"])


def build_prospective_table(
    possessions_path: Path,
    matches_path: Path,
    events: pd.DataFrame,
    actors_path: Path,
) -> pd.DataFrame:
    """Build the isolated t=0 feature table and enforce leakage contracts."""

    possessions = pd.read_csv(possessions_path, low_memory=False)
    matches = load_match_metadata(matches_path)
    if possessions.empty or matches.empty:
        raise ValueError("Possession or match metadata input is empty")
    required_possessions = {
        "possession_uid",
        "match_id",
        "period",
        "possession",
        "team",
        "opponent",
        "competition_stage",
        "play_pattern",
        "start_minute",
        "start_time_seconds",
        "start_x",
        "start_y",
        "progression_speed",
        "completed_pass_count",
        "opponent_defensive_actions",
        "goal_count",
        *TARGETS.values(),
    }
    missing = sorted(required_possessions - set(possessions.columns))
    if missing:
        raise ValueError(f"Possession table missing columns: {missing}")
    if matches["match_id"].nunique() != 64:
        raise ValueError("Match metadata must contain all 64 World Cup matches")
    possessions = add_rolling_and_match_state(possessions)
    starts = possession_start_events(events)
    prior = prior_event_features(events)
    recovery = recovery_window_features(events, starts)
    spatial = spatial_start_features(starts, actors_path)
    data = (
        possessions.merge(
            starts,
            on=["possession_uid", "match_id", "period", "possession"],
            how="left",
            validate="one_to_one",
        )
        .merge(prior, on="possession_uid", how="left", validate="one_to_one")
        .merge(
            recovery, on="possession_uid", how="left", validate="one_to_one"
        )
        .merge(spatial, on="possession_uid", how="left", validate="one_to_one")
    )
    data["previous_possession_outcome"] = data[
        "previous_possession_outcome"
    ].fillna("no_prior_possession")
    valid_prior_window = (
        data["prior_period"].eq(data["period"])
        & data["prior_event_seconds"].lt(data["verified_start_seconds"])
        & data["prior_event_seconds"].ge(
            data["verified_start_seconds"] - 5.0
        )
    )
    data.loc[
        ~valid_prior_window, "possession_starting_velocity"
    ] = SENTINEL
    for column in TEMPORAL_FEATURES:
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(
            SENTINEL
        )
    for column in SPATIAL_FEATURES:
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(
            0 if column == "has_360_freeze_frame" else SENTINEL
        )
    invalid_prior_time = valid_prior_window & ~data[
        "prior_event_seconds"
    ].lt(data["verified_start_seconds"])
    if invalid_prior_time.any():
        raise RuntimeError("Prior-possession feature timestamp exceeds t=0")
    return data


def feature_layouts() -> list[FeatureLayout]:
    """Return bounded, additive challenger layouts."""

    return [
        FeatureLayout(
            "start_plus_360",
            tuple(BASE_NUMERIC + SPATIAL_FEATURES),
            tuple(BASE_CATEGORICAL),
        ),
        FeatureLayout(
            "start_plus_360_prior5s",
            tuple(BASE_NUMERIC + SPATIAL_FEATURES + TEMPORAL_FEATURES),
            tuple(BASE_CATEGORICAL + ["previous_possession_outcome"]),
        ),
        FeatureLayout(
            "full_pre_possession",
            tuple(
                BASE_NUMERIC
                + SPATIAL_FEATURES
                + TEMPORAL_FEATURES
                + ROLLING_FEATURES
            ),
            tuple(BASE_CATEGORICAL + CONTEXT_CATEGORICAL),
        ),
    ]


def assert_prospective_layout(layout: FeatureLayout) -> None:
    """Reject a layout containing any completed-possession field."""

    overlap = POST_START_PROHIBITED.intersection(
        {*layout.numeric, *layout.categorical}
    )
    if overlap:
        raise RuntimeError(
            f"Prospective feature leakage detected in {layout.name}: "
            f"{sorted(overlap)}"
        )


def _preprocessor(
    numeric: Sequence[str],
    categorical: Sequence[str],
    *,
    scale_numeric: bool,
) -> ColumnTransformer:
    """Create a fold-fitted transformer without global statistics."""

    numeric_steps: list[Any] = [
        SimpleImputer(strategy="constant", fill_value=SENTINEL)
    ]
    if scale_numeric:
        numeric_steps.append(StandardScaler())
    return ColumnTransformer(
        [
            ("numeric", make_pipeline(*numeric_steps), list(numeric)),
            (
                "categorical",
                make_pipeline(
                    SimpleImputer(
                        strategy="constant", fill_value="__MISSING__"
                    ),
                    OneHotEncoder(
                        handle_unknown="ignore", sparse_output=False
                    ),
                ),
                list(categorical),
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def baseline_estimator(layout: FeatureLayout) -> Any:
    """Return the stable prospective Logistic Regression reference."""

    return make_pipeline(
        _preprocessor(layout.numeric, layout.categorical, scale_numeric=True),
        LogisticRegression(
            C=1.0,
            class_weight="balanced",
            max_iter=600,
            random_state=RANDOM_STATE,
        ),
    )


def catboost_estimator(
    layout: FeatureLayout, *, depth: int, seed: int
) -> Any:
    """Return one constrained CatBoost challenger."""

    return make_pipeline(
        _preprocessor(layout.numeric, layout.categorical, scale_numeric=False),
        CatBoostClassifier(
            iterations=300,
            depth=depth,
            learning_rate=0.035,
            l2_leaf_reg=8.0,
            random_strength=0.5,
            rsm=0.75,
            bootstrap_type="Bernoulli",
            subsample=0.8,
            auto_class_weights="Balanced",
            loss_function="Logloss",
            eval_metric="AUC",
            verbose=False,
            allow_writing_files=False,
            thread_count=2,
            random_seed=seed,
        ),
    )


def calibrate_prefit(
    estimator: Any,
    features: pd.DataFrame,
    truth: np.ndarray,
    method: str,
) -> ProbabilityCalibrator:
    """Fit isotonic or Platt calibration on a dedicated match subset."""

    raw = estimator.predict_proba(features)[:, 1]
    if method == "isotonic":
        calibrator: Any = IsotonicRegression(
            out_of_bounds="clip", y_min=0.0, y_max=1.0
        )
        calibrator.fit(raw, truth)
    elif method == "sigmoid":
        calibrator = LogisticRegression(
            C=1e6, solver="lbfgs", max_iter=500, random_state=RANDOM_STATE
        )
        calibrator.fit(raw.reshape(-1, 1), truth)
    else:
        raise ValueError(f"Unsupported calibration method: {method}")
    return ProbabilityCalibrator(estimator, calibrator, method)


def expected_calibration_error(
    truth: np.ndarray, probability: np.ndarray, bins: int = 10
) -> float:
    """Return equal-width expected calibration error."""

    edges = np.linspace(0.0, 1.0, bins + 1)
    assignment = np.clip(
        np.digitize(probability, edges[1:-1]), 0, bins - 1
    )
    error = 0.0
    for bin_id in range(bins):
        selected = assignment == bin_id
        if selected.any():
            error += float(selected.mean()) * abs(
                float(truth[selected].mean())
                - float(probability[selected].mean())
            )
    return float(error)


def metric_row(truth: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    """Calculate discrimination and calibration metrics."""

    probability = np.clip(probability, 1e-9, 1 - 1e-9)
    return {
        "log_loss": float(log_loss(truth, probability)),
        "brier": float(brier_score_loss(truth, probability)),
        "roc_auc": float(roc_auc_score(truth, probability)),
        "pr_auc": float(average_precision_score(truth, probability)),
        "ece": expected_calibration_error(truth, probability),
    }


def _nested_calibration_matches(
    training_matches: Sequence[int], fold: int
) -> tuple[list[int], list[int]]:
    """Split outer-training matches without looking at labels."""

    shuffled = np.random.default_rng(RANDOM_STATE + fold).permutation(
        np.asarray(training_matches, dtype=int)
    )
    count = max(2, int(round(0.20 * len(shuffled))))
    return shuffled[count:].tolist(), shuffled[:count].tolist()


def oof_predict(
    data: pd.DataFrame,
    target: str,
    layout: FeatureLayout,
    estimator_factory: Any,
    calibration: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Return five-fold match-disjoint, nested-calibrated OOF predictions."""

    assert_prospective_layout(layout)
    features = data[[*layout.numeric, *layout.categorical]]
    truth = data[target].astype(int).to_numpy()
    groups = data["match_id"].astype(int).to_numpy()
    probability = np.full(len(data), np.nan)
    fold_id = np.full(len(data), -1, dtype=int)
    splitter = GroupKFold(n_splits=N_SPLITS)
    for fold, (outer_train, validation) in enumerate(
        splitter.split(features, truth, groups)
    ):
        outer_matches = sorted(set(groups[outer_train]))
        fit_matches, calibration_matches = _nested_calibration_matches(
            outer_matches, fold
        )
        fit_mask = np.isin(groups, fit_matches)
        calibration_mask = np.isin(groups, calibration_matches)
        if set(groups[fit_mask]).intersection(groups[calibration_mask]):
            raise RuntimeError("Fit/calibration match leakage detected")
        if set(groups[outer_train]).intersection(groups[validation]):
            raise RuntimeError("Outer train/validation match leakage detected")
        estimator = estimator_factory(fold)
        estimator.fit(features.loc[fit_mask], truth[fit_mask])
        calibrated = calibrate_prefit(
            estimator,
            features.loc[calibration_mask],
            truth[calibration_mask],
            calibration,
        )
        probability[validation] = calibrated.predict_proba(
            features.iloc[validation]
        )[:, 1]
        fold_id[validation] = fold
    if np.isnan(probability).any() or (fold_id < 0).any():
        raise RuntimeError("OOF prediction coverage is incomplete")
    return probability, fold_id


def paired_match_bootstrap_delta(
    truth: np.ndarray,
    baseline: np.ndarray,
    challenger: np.ndarray,
    matches: np.ndarray,
    *,
    replicates: int,
) -> tuple[float, float, float]:
    """Return paired match-bootstrap ROC delta and 90% interval.

    The lower bound is the one-sided 95% significance boundary.
    """

    rng = np.random.default_rng(RANDOM_STATE)
    unique_matches = np.unique(matches)
    deltas: list[float] = []
    indices = {
        match: np.flatnonzero(matches == match) for match in unique_matches
    }
    for _ in range(replicates):
        sampled = rng.choice(
            unique_matches, size=len(unique_matches), replace=True
        )
        selected = np.concatenate([indices[match] for match in sampled])
        sample_truth = truth[selected]
        if np.unique(sample_truth).size < 2:
            continue
        deltas.append(
            float(
                roc_auc_score(sample_truth, challenger[selected])
                - roc_auc_score(sample_truth, baseline[selected])
            )
        )
    if not deltas:
        raise RuntimeError("Paired bootstrap produced no class-complete samples")
    observed = float(
        roc_auc_score(truth, challenger) - roc_auc_score(truth, baseline)
    )
    return (
        observed,
        float(np.quantile(deltas, 0.05)),
        float(np.quantile(deltas, 0.95)),
    )


def evaluate_challengers(
    data: pd.DataFrame,
    *,
    bootstrap_replicates: int,
    logger: logging.Logger,
) -> tuple[pd.DataFrame, dict[str, dict[str, Any]]]:
    """Evaluate bounded challengers and accept only fully safe improvements."""

    records: list[dict[str, Any]] = []
    accepted: dict[str, dict[str, Any]] = {}
    baseline_layout = FeatureLayout(
        "stable_start_context",
        tuple(BASE_NUMERIC),
        tuple(BASE_CATEGORICAL),
    )
    baseline_predictions: dict[str, np.ndarray] = {}
    for label, target in TARGETS.items():
        probability, _ = oof_predict(
            data,
            target,
            baseline_layout,
            lambda fold: baseline_estimator(baseline_layout),
            "sigmoid",
        )
        baseline_predictions[label] = probability
        metrics = metric_row(data[target].to_numpy(dtype=int), probability)
        records.append(
            {
                "target": label,
                "candidate": "recomputed_logistic_reference",
                "layout": baseline_layout.name,
                "depth": np.nan,
                "calibration": "sigmoid",
                **metrics,
                "roc_delta_vs_reference": 0.0,
                "roc_delta_ci_low": 0.0,
                "roc_delta_ci_high": 0.0,
                "passes_gate": False,
                "decision": "REFERENCE_ONLY",
            }
        )

    specifications = [
        (3, "sigmoid"),
        (4, "sigmoid"),
        (4, "isotonic"),
        (5, "sigmoid"),
    ]
    for layout in feature_layouts():
        assert_prospective_layout(layout)
        for depth, calibration in specifications:
            for label, target in TARGETS.items():
                started = time.perf_counter()
                truth = data[target].to_numpy(dtype=int)
                probability, _ = oof_predict(
                    data,
                    target,
                    layout,
                    lambda fold, d=depth: catboost_estimator(
                        layout, depth=d, seed=RANDOM_STATE + fold
                    ),
                    calibration,
                )
                metrics = metric_row(truth, probability)
                delta, ci_low, ci_high = paired_match_bootstrap_delta(
                    truth,
                    baseline_predictions[label],
                    probability,
                    data["match_id"].to_numpy(dtype=int),
                    replicates=bootstrap_replicates,
                )
                gate = (
                    metrics["roc_auc"] > BASELINES[label]["roc_auc"]
                    and metrics["brier"] <= BASELINES[label]["brier"]
                    and metrics["ece"]
                    <= BASELINES[label]["ece"] + 0.005
                    and delta > 0
                    and ci_low > 0
                )
                reason = (
                    "ACCEPTED"
                    if gate
                    else "REJECTED: "
                    + ", ".join(
                        [
                            name
                            for name, passed in {
                                "ROC threshold": metrics["roc_auc"]
                                > BASELINES[label]["roc_auc"],
                                "Brier safety": metrics["brier"]
                                <= BASELINES[label]["brier"],
                                "ECE safety": metrics["ece"]
                                <= BASELINES[label]["ece"] + 0.005,
                                "positive paired delta": delta > 0,
                                "significant paired delta": ci_low > 0,
                            }.items()
                            if not passed
                        ]
                    )
                )
                record = {
                    "target": label,
                    "candidate": f"CatBoost_depth_{depth}_{calibration}",
                    "layout": layout.name,
                    "depth": depth,
                    "calibration": calibration,
                    **metrics,
                    "roc_delta_vs_reference": delta,
                    "roc_delta_ci_low": ci_low,
                    "roc_delta_ci_high": ci_high,
                    "latency_sec": time.perf_counter() - started,
                    "passes_gate": gate,
                    "decision": reason,
                }
                records.append(record)
                if gate and (
                    label not in accepted
                    or metrics["roc_auc"]
                    > accepted[label]["record"]["roc_auc"]
                ):
                    accepted[label] = {
                        "record": record,
                        "layout": layout,
                        "probability": probability,
                    }
                log = logger.info if gate else logger.warning
                log(
                    "%s | %s | ROC=%.4f Brier=%.4f ECE=%.4f "
                    "paired_delta=%.4f [%.4f, %.4f]",
                    reason,
                    label,
                    metrics["roc_auc"],
                    metrics["brier"],
                    metrics["ece"],
                    delta,
                    ci_low,
                    ci_high,
                )
    return pd.DataFrame(records), accepted


def fit_deployment_model(
    data: pd.DataFrame,
    target: str,
    layout: FeatureLayout,
    *,
    depth: int,
    calibration: str,
) -> ProbabilityCalibrator:
    """Fit the accepted architecture with a disjoint calibration match set."""

    matches = np.array(sorted(data["match_id"].unique()), dtype=int)
    fit_matches, calibration_matches = _nested_calibration_matches(matches, 99)
    fit_mask = data["match_id"].isin(fit_matches)
    calibration_mask = data["match_id"].isin(calibration_matches)
    features = data[[*layout.numeric, *layout.categorical]]
    truth = data[target].astype(int).to_numpy()
    estimator = catboost_estimator(
        layout, depth=depth, seed=RANDOM_STATE
    )
    estimator.fit(features.loc[fit_mask], truth[fit_mask])
    return calibrate_prefit(
        estimator,
        features.loc[calibration_mask],
        truth[calibration_mask],
        calibration,
    )


def print_comparison(validation: pd.DataFrame) -> None:
    """Print baseline and best challenger side by side for each target."""

    print("\nProspective model validation")
    print("=" * 88)
    for label in TARGETS:
        candidates = validation[
            validation["target"].eq(label)
            & validation["candidate"].ne("recomputed_logistic_reference")
        ].sort_values("roc_auc", ascending=False)
        best = candidates.iloc[0]
        baseline = BASELINES[label]
        print(
            f"{label:10s} | baseline ROC={baseline['roc_auc']:.4f} "
            f"Brier={baseline['brier']:.4f} ECE={baseline['ece']:.4f}"
        )
        print(
            f"{'':10s} | best     ROC={best['roc_auc']:.4f} "
            f"Brier={best['brier']:.4f} ECE={best['ece']:.4f} "
            f"| {best['decision']}"
        )


def run(args: argparse.Namespace) -> int:
    """Execute the guarded prospective challenger workflow."""

    logger = configure_logging(args.log)
    try:
        validate_preconditions(
            args.events,
            args.frames,
            args.matches,
            logger=logger,
            prompt=not args.no_prompt,
        )
    except PreconditionError:
        return 2

    if not args.possessions.is_file() or args.possessions.stat().st_size == 0:
        logger.critical(
            "Derived possession table missing or empty: %s", args.possessions
        )
        return 2
    if (
        not args.frame_actors.is_file()
        or args.frame_actors.stat().st_size == 0
    ):
        logger.critical(
            "Flattened 360 actor cache missing or empty: %s",
            args.frame_actors,
        )
        return 2

    started = time.perf_counter()
    events = load_event_stream(args.events)
    data = build_prospective_table(
        args.possessions, args.matches, events, args.frame_actors
    )
    if data["match_id"].nunique() != 64:
        raise RuntimeError("Prospective table does not cover all 64 matches")
    validation, accepted = evaluate_challengers(
        data,
        bootstrap_replicates=args.bootstrap_replicates,
        logger=logger,
    )
    args.validation.parent.mkdir(parents=True, exist_ok=True)
    validation.to_csv(args.validation, index=False)
    print_comparison(validation)

    if set(accepted) != set(TARGETS):
        rejected = sorted(set(TARGETS) - set(accepted))
        logger.error(
            "ROLLBACK: no artifact written; targets without a fully valid "
            "challenger: %s",
            ", ".join(rejected),
        )
        print(
            "\nREJECTED: At least one target failed the complete gate. "
            "The stable prospective state remains unchanged."
        )
        return 3

    models: dict[str, Any] = {}
    metadata: dict[str, Any] = {}
    for label, target in TARGETS.items():
        choice = accepted[label]
        record = choice["record"]
        layout = choice["layout"]
        models[label] = fit_deployment_model(
            data,
            target,
            layout,
            depth=int(record["depth"]),
            calibration=str(record["calibration"]),
        )
        metadata[label] = {
            "target": target,
            "layout": layout.name,
            "numeric_features": list(layout.numeric),
            "categorical_features": list(layout.categorical),
            "validation": record,
        }
    bundle = {
        "schema_version": "prospective-possession-v1",
        "created_unix": time.time(),
        "validation_scheme": "5-fold GroupKFold by match with nested calibration",
        "temporal_contract": "all inputs available at or before possession t=0",
        "sentinel": SENTINEL,
        "models": models,
        "metadata": metadata,
    }
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.artifact.with_suffix(args.artifact.suffix + ".candidate")
    joblib.dump(bundle, temporary)
    replay = joblib.load(temporary)
    if replay["schema_version"] != bundle["schema_version"]:
        temporary.unlink(missing_ok=True)
        raise RuntimeError("Candidate artifact replay failed")
    temporary.replace(args.artifact)
    logger.info(
        "ACCEPTED artifact=%s elapsed=%.1fs",
        args.artifact,
        time.perf_counter() - started,
    )
    print(f"\nACCEPTED: wrote {args.artifact}")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command-line paths and bounded evaluation options."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--frames", type=Path, default=DEFAULT_360_SOURCE)
    parser.add_argument("--frame-actors", type=Path, default=DEFAULT_360_ACTORS)
    parser.add_argument("--matches", type=Path, default=DEFAULT_MATCHES)
    parser.add_argument("--possessions", type=Path, default=DEFAULT_POSSESSIONS)
    parser.add_argument("--validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument(
        "--bootstrap-replicates",
        type=int,
        default=BOOTSTRAP_REPLICATES,
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Exit immediately on a missing precondition in noninteractive runs.",
    )
    args = parser.parse_args()
    if args.bootstrap_replicates < 200:
        parser.error("--bootstrap-replicates must be at least 200")
    return args


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
