"""Missingness-aware spatial and StatsBomb 360 feature engineering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.spatial import ConvexHull, QhullError
from sklearn.base import BaseEstimator, TransformerMixin

from src.config import (
    PITCH_LENGTH_METRES,
    PITCH_LENGTH_UNITS,
    PITCH_WIDTH_METRES,
    PITCH_WIDTH_UNITS,
)
from src.features.events import coordinate_axis


def to_metric_coordinates(coordinates: np.ndarray) -> np.ndarray:
    """Convert StatsBomb 120×80 coordinates to a 105×68 metre pitch."""

    values = np.asarray(coordinates, dtype=float)
    if values.shape[-1] != 2:
        raise ValueError("Coordinates must have a final dimension of two")
    scale = np.asarray(
        [
            PITCH_LENGTH_METRES / PITCH_LENGTH_UNITS,
            PITCH_WIDTH_METRES / PITCH_WIDTH_UNITS,
        ],
        dtype=float,
    )
    return values * scale


def _segment_clearance(
    origin: np.ndarray,
    target: np.ndarray,
    defenders: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return projection and perpendicular distance to a pass segment."""

    vector = target - origin
    squared_length = float(np.dot(vector, vector))
    if squared_length <= 1e-12 or not len(defenders):
        return np.empty(0), np.empty(0)
    relative = defenders - origin
    projection = relative.dot(vector) / squared_length
    closest = origin + projection[:, None] * vector
    clearance = np.linalg.norm(defenders - closest, axis=1)
    return projection, clearance


@dataclass(frozen=True)
class FreezeFrameGeometry:
    """Actor-centric geometry from one visible freeze frame."""

    sb360_available: bool
    defenders_within_3m: float
    defenders_within_5m: float
    nearest_defender_m: float
    mean_defender_m: float
    passing_lane_availability: float
    packing_index: float
    space_received: float
    visible_defender_count: int


def calculate_freeze_frame_geometry(
    actor_coordinates: np.ndarray | None,
    defender_coordinates: np.ndarray | None,
    *,
    target_coordinates: np.ndarray | None = None,
    attacking_right: bool = True,
    lane_width_metres: float = 1.5,
) -> FreezeFrameGeometry:
    """Calculate metric actor pressure, passing-lane, and packing features.

    Missing frames remain explicit NaNs. Counts are zero only when a valid
    frame was observed and no defender met the relevant geometric condition.
    """

    if actor_coordinates is None or defender_coordinates is None:
        return FreezeFrameGeometry(
            False,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            0,
        )
    actor = to_metric_coordinates(np.asarray(actor_coordinates, dtype=float))
    defenders = to_metric_coordinates(
        np.asarray(defender_coordinates, dtype=float).reshape(-1, 2)
    )
    defenders = defenders[np.isfinite(defenders).all(axis=1)]
    if actor.shape != (2,) or not np.isfinite(actor).all() or not len(defenders):
        return FreezeFrameGeometry(
            False,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            0,
        )
    distances = np.linalg.norm(defenders - actor, axis=1)
    nearest = float(distances.min())
    lane_availability = np.nan
    packing = np.nan
    if target_coordinates is not None:
        target = to_metric_coordinates(
            np.asarray(target_coordinates, dtype=float)
        )
        if target.shape == (2,) and np.isfinite(target).all():
            projection, clearance = _segment_clearance(
                actor,
                target,
                defenders,
            )
            in_corridor = (projection > 0.0) & (projection < 1.0)
            lane_availability = (
                1.0
                if not in_corridor.any()
                else float(
                    np.clip(
                        clearance[in_corridor].min() / lane_width_metres,
                        0.0,
                        1.0,
                    )
                )
            )
            direction = 1.0 if attacking_right else -1.0
            advances = direction * (target[0] - actor[0]) > 0
            if advances:
                start_progress = direction * actor[0]
                end_progress = direction * target[0]
                defender_progress = direction * defenders[:, 0]
                packing = float(
                    (
                        (defender_progress >= start_progress)
                        & (defender_progress < end_progress)
                    ).sum()
                )
            else:
                packing = 0.0
    return FreezeFrameGeometry(
        True,
        float((distances <= 3.0).sum()),
        float((distances <= 5.0).sum()),
        nearest,
        float(distances.mean()),
        lane_availability,
        packing,
        float(np.clip(nearest / 10.0, 0.0, 1.0)),
        int(len(defenders)),
    )


def _occupancy_summary(group: pd.DataFrame, sigma: float) -> pd.Series:
    """Summarize one player's observed location distribution."""

    points = group[["start_x", "start_y"]].apply(
        pd.to_numeric,
        errors="coerce",
    ).dropna()
    if points.empty:
        return pd.Series(dtype=float)
    coordinates = points.to_numpy(dtype=float, copy=True)
    coordinates[:, 0] = np.clip(coordinates[:, 0], 0.0, 119.999)
    coordinates[:, 1] = np.clip(coordinates[:, 1], 0.0, 79.999)
    grid, _, _ = np.histogram2d(
        coordinates[:, 0],
        coordinates[:, 1],
        bins=(120, 80),
        range=((0.0, 120.0), (0.0, 80.0)),
    )
    density = gaussian_filter(grid, sigma=sigma)
    density /= max(float(density.sum()), 1.0)
    occupied = density[density > 0]
    entropy = float(-(occupied * np.log(occupied)).sum())
    hull_area = 0.0
    if len(coordinates) >= 3:
        try:
            hull_area = float(ConvexHull(coordinates).volume)
        except QhullError:
            hull_area = 0.0
    x = coordinates[:, 0]
    y = coordinates[:, 1]
    coarse = density.reshape(12, 10, 8, 10).sum(axis=(1, 3))
    result: dict[str, float] = {
        "occupancy_entropy": entropy,
        "convex_hull_area": hull_area,
        "average_spatial_x": float(x.mean()),
        "average_spatial_y": float(y.mean()),
        "final_third_occupancy": float((x >= 80.0).mean()),
        "zone14_share": float(
            ((x >= 80.0) & (x < 102.0) & (y >= 26.7) & (y <= 53.3)).mean()
        ),
        "half_space_share": float(
            (
                (x >= 60.0)
                & (x < 102.0)
                & (
                    ((y >= 13.3) & (y < 26.7))
                    | ((y > 53.3) & (y <= 66.7))
                )
            ).mean()
        ),
        "wide_corridor_share": float(((y < 13.3) | (y > 66.7)).mean()),
        "spatial_observation_count": float(len(coordinates)),
    }
    result.update(
        {
            f"kde_{row:02d}_{column:02d}": float(coarse[row, column])
            for row in range(12)
            for column in range(8)
        }
    )
    return pd.Series(result)


class SpatialFeatureTransformer(BaseEstimator, TransformerMixin):
    """Aggregate 120×80 KDE occupancy and actor-centric 360 geometry."""

    def __init__(self, *, kde_sigma: float = 3.0) -> None:
        self.kde_sigma = kde_sigma

    def fit(
        self,
        X: pd.DataFrame,
        y: Any = None,
    ) -> "SpatialFeatureTransformer":
        """Validate input schema; the spatial aggregation is stateless."""

        required = {"player_id", "start_x", "start_y"}
        missing = required.difference(X.columns)
        if missing:
            raise ValueError(f"Spatial inputs missing: {sorted(missing)}")
        if self.kde_sigma <= 0:
            raise ValueError("kde_sigma must be positive")
        self.feature_names_in_ = tuple(str(column) for column in X.columns)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return player occupancy and coverage-aware geometry summaries."""

        if not hasattr(self, "feature_names_in_"):
            raise RuntimeError("SpatialFeatureTransformer has not been fitted")
        valid = X.loc[X["player_id"].notna()].copy()
        valid["player_id"] = pd.to_numeric(
            valid["player_id"],
            errors="raise",
        ).astype(int)
        records = [
            {
                "player_id": int(player_id),
                **_occupancy_summary(group, self.kde_sigma).to_dict(),
            }
            for player_id, group in valid.groupby("player_id", sort=False)
        ]
        output = pd.DataFrame(records)
        geometry = [
            column
            for column in (
                "defenders_within_3m",
                "defenders_within_5m",
                "nearest_defender_m",
                "passing_lane_availability",
                "packing_index",
                "space_received",
            )
            if column in valid
        ]
        if geometry:
            available = (
                valid["sb360_available"].fillna(False).astype(bool)
                if "sb360_available" in valid
                else valid[geometry].notna().any(axis=1)
            )
            valid = valid.assign(_sb360_available=available)
            aggregations: dict[str, tuple[str, str]] = {
                f"mean_{column}": (column, "mean") for column in geometry
            }
            aggregations.update(
                {
                    "sb360_observations": ("_sb360_available", "sum"),
                    "sb360_coverage": ("_sb360_available", "mean"),
                }
            )
            summary = valid.groupby("player_id", as_index=False).agg(
                **aggregations
            )
            output = output.merge(summary, on="player_id", how="left")
        return output


def calculate_zone_control(
    team_density: np.ndarray,
    opponent_density: np.ndarray,
    visibility_mask: np.ndarray,
) -> np.ndarray:
    """Return visibility-masked team-minus-opponent spatial control."""

    team = np.asarray(team_density, dtype=float)
    opponent = np.asarray(opponent_density, dtype=float)
    visible = np.asarray(visibility_mask, dtype=bool)
    if team.shape != opponent.shape or team.shape != visible.shape:
        raise ValueError("Zone-control arrays must have identical shapes")
    output = np.full(team.shape, np.nan, dtype=float)
    output[visible] = team[visible] - opponent[visible]
    return output


def build_event_freeze_frame_features(
    events: pd.DataFrame,
    freeze_frames: pd.DataFrame,
) -> pd.DataFrame:
    """Build actor-centric metric geometry for every matched 360 event.

    Args:
        events: StatsBomb events with ``match_id``, ``id``, ``location``, and
            available action endpoint columns.
        freeze_frames: Long-form StatsBomb 360 player rows with teammate,
            actor, keeper, x, and y fields.

    Returns:
        One row per matched event. Unmatched events are intentionally absent;
        callers must left join and add an explicit availability mask.
    """

    event_required = {"match_id", "id", "location"}
    frame_required = {
        "match_id",
        "event_uuid",
        "teammate",
        "actor",
        "keeper",
        "x",
        "y",
    }
    event_missing = event_required.difference(events.columns)
    frame_missing = frame_required.difference(freeze_frames.columns)
    if event_missing or frame_missing:
        raise ValueError(
            "360 event/frame columns missing: "
            f"events={sorted(event_missing)}, frames={sorted(frame_missing)}"
        )
    event_table = events.copy()
    event_table["event_uuid"] = event_table["id"].astype(str)
    event_table["actor_x"] = coordinate_axis(event_table["location"], 0)
    event_table["actor_y"] = coordinate_axis(event_table["location"], 1)
    target_columns = [
        column
        for column in (
            "pass_end_location",
            "carry_end_location",
            "shot_end_location",
        )
        if column in event_table
    ]
    event_table["target_x"] = np.nan
    event_table["target_y"] = np.nan
    for column in target_columns:
        x = coordinate_axis(event_table[column], 0)
        y = coordinate_axis(event_table[column], 1)
        event_table["target_x"] = event_table["target_x"].fillna(x)
        event_table["target_y"] = event_table["target_y"].fillna(y)
    lookup = (
        event_table[
            [
                "match_id",
                "event_uuid",
                "actor_x",
                "actor_y",
                "target_x",
                "target_y",
            ]
        ]
        .drop_duplicates(["match_id", "event_uuid"])
        .set_index(["match_id", "event_uuid"])
    )
    frames = freeze_frames.copy()
    frames["event_uuid"] = frames["event_uuid"].astype(str)
    frames["teammate"] = frames["teammate"].fillna(False).astype(str).str.lower().isin(
        {"true", "1", "yes"}
    )
    frames["actor"] = frames["actor"].fillna(False).astype(str).str.lower().isin(
        {"true", "1", "yes"}
    )
    frames["x"] = pd.to_numeric(frames["x"], errors="coerce")
    frames["y"] = pd.to_numeric(frames["y"], errors="coerce")
    records: list[dict[str, Any]] = []
    for key, group in frames.groupby(
        ["match_id", "event_uuid"],
        sort=False,
    ):
        if key not in lookup.index:
            continue
        event = lookup.loc[key]
        actor_rows = group.loc[group["actor"], ["x", "y"]].dropna()
        actor = (
            actor_rows.iloc[0].to_numpy(dtype=float)
            if not actor_rows.empty
            else event[["actor_x", "actor_y"]].to_numpy(dtype=float)
        )
        defender_coordinates = group.loc[
            ~group["teammate"],
            ["x", "y"],
        ].dropna().to_numpy(dtype=float)
        target_values = event[["target_x", "target_y"]].to_numpy(dtype=float)
        target = target_values if np.isfinite(target_values).all() else None
        geometry = calculate_freeze_frame_geometry(
            actor,
            defender_coordinates,
            target_coordinates=target,
        )
        teammate_coordinates = group.loc[
            group["teammate"] & ~group["actor"],
            ["x", "y"],
        ].dropna().to_numpy(dtype=float)
        shape_deviation = np.nan
        if len(teammate_coordinates) and np.isfinite(actor).all():
            actor_metric = to_metric_coordinates(actor)
            teammate_metric = to_metric_coordinates(teammate_coordinates)
            shape_deviation = float(
                np.linalg.norm(actor_metric - teammate_metric.mean(axis=0))
            )
        records.append(
            {
                "match_id": int(key[0]),
                "event_uuid": str(key[1]),
                **dataclass_to_dict(geometry),
                "actor_shape_deviation_m": shape_deviation,
                "space_created_proxy": np.nan,
                "space_created_proxy_available": False,
            }
        )
    return pd.DataFrame(records)


def dataclass_to_dict(instance: Any) -> dict[str, Any]:
    """Convert a small feature dataclass without importing reporting helpers."""

    return {
        name: getattr(instance, name)
        for name in instance.__dataclass_fields__
    }


def build_event_freeze_frame_features_from_csv(
    events: pd.DataFrame,
    frame_path: Path,
    *,
    chunksize: int = 250_000,
) -> pd.DataFrame:
    """Stream and vectorize the large flattened 360 CSV.

    Chunk-level sufficient statistics are combined by event after the final
    chunk. This avoids per-event Python loops while remaining exact when one
    freeze-frame group crosses a chunk boundary.
    """

    usecols = [
        "match_id",
        "event_uuid",
        "teammate",
        "actor",
        "keeper",
        "x",
        "y",
    ]
    event_table = events.copy()
    event_table["event_uuid"] = event_table["id"].astype(str)
    event_table["actor_x"] = coordinate_axis(event_table["location"], 0)
    event_table["actor_y"] = coordinate_axis(event_table["location"], 1)
    event_table["target_x"] = np.nan
    event_table["target_y"] = np.nan
    for column in (
        "pass_end_location",
        "carry_end_location",
        "shot_end_location",
    ):
        if column in event_table:
            event_table["target_x"] = event_table["target_x"].fillna(
                coordinate_axis(event_table[column], 0)
            )
            event_table["target_y"] = event_table["target_y"].fillna(
                coordinate_axis(event_table[column], 1)
            )
    lookup = event_table[
        [
            "match_id",
            "event_uuid",
            "actor_x",
            "actor_y",
            "target_x",
            "target_y",
        ]
    ].drop_duplicates(["match_id", "event_uuid"])
    defender_chunks: list[pd.DataFrame] = []
    teammate_chunks: list[pd.DataFrame] = []
    x_scale = PITCH_LENGTH_METRES / PITCH_LENGTH_UNITS
    y_scale = PITCH_WIDTH_METRES / PITCH_WIDTH_UNITS

    for chunk in pd.read_csv(
        frame_path,
        usecols=usecols,
        chunksize=chunksize,
        low_memory=False,
    ):
        chunk["event_uuid"] = chunk["event_uuid"].astype(str)
        chunk["teammate"] = (
            chunk["teammate"].fillna(False).astype(str).str.lower().isin(
                {"true", "1", "yes"}
            )
        )
        chunk["actor"] = (
            chunk["actor"].fillna(False).astype(str).str.lower().isin(
                {"true", "1", "yes"}
            )
        )
        chunk["x"] = pd.to_numeric(chunk["x"], errors="coerce")
        chunk["y"] = pd.to_numeric(chunk["y"], errors="coerce")
        joined = chunk.merge(
            lookup,
            on=["match_id", "event_uuid"],
            how="inner",
            validate="many_to_one",
        ).dropna(subset=["x", "y", "actor_x", "actor_y"])
        if joined.empty:
            continue
        keys = ["match_id", "event_uuid"]
        defenders = joined.loc[~joined["teammate"]].copy()
        if not defenders.empty:
            dx = (defenders["x"] - defenders["actor_x"]) * x_scale
            dy = (defenders["y"] - defenders["actor_y"]) * y_scale
            defenders["_distance"] = np.hypot(dx, dy)
            defenders["_within_3"] = defenders["_distance"].le(3.0).astype(int)
            defenders["_within_5"] = defenders["_distance"].le(5.0).astype(int)
            defenders["_target_available"] = defenders[
                ["target_x", "target_y"]
            ].notna().all(axis=1)
            vx = (defenders["target_x"] - defenders["actor_x"]) * x_scale
            vy = (defenders["target_y"] - defenders["actor_y"]) * y_scale
            squared_length = vx * vx + vy * vy
            projection = np.divide(
                dx * vx + dy * vy,
                squared_length,
                out=np.full(len(defenders), np.nan),
                where=squared_length.to_numpy() > 1e-12,
            )
            closest_dx = projection * vx
            closest_dy = projection * vy
            clearance = np.hypot(dx - closest_dx, dy - closest_dy)
            in_corridor = (
                defenders["_target_available"]
                & pd.Series(projection, index=defenders.index).between(
                    0.0,
                    1.0,
                    inclusive="neither",
                )
            )
            defenders["_lane_clearance"] = np.where(
                in_corridor,
                clearance,
                np.nan,
            )
            advances = defenders["target_x"] > defenders["actor_x"]
            defenders["_packed"] = (
                advances
                & defenders["x"].ge(defenders["actor_x"])
                & defenders["x"].lt(defenders["target_x"])
            ).astype(int)
            defender_chunks.append(
                defenders.groupby(keys, as_index=False).agg(
                    visible_defender_count=("_distance", "size"),
                    defenders_within_3m=("_within_3", "sum"),
                    defenders_within_5m=("_within_5", "sum"),
                    nearest_defender_m=("_distance", "min"),
                    defender_distance_sum=("_distance", "sum"),
                    target_available=("_target_available", "max"),
                    lane_clearance_min=("_lane_clearance", "min"),
                    packing_index=("_packed", "sum"),
                )
            )
        teammates = joined.loc[joined["teammate"] & ~joined["actor"]]
        if not teammates.empty:
            teammate_chunks.append(
                teammates.groupby(keys, as_index=False).agg(
                    teammate_x_sum=("x", "sum"),
                    teammate_y_sum=("y", "sum"),
                    teammate_count=("x", "size"),
                )
            )
    if not defender_chunks:
        return pd.DataFrame(
            columns=["match_id", "event_uuid", "sb360_available"]
        )
    keys = ["match_id", "event_uuid"]
    defenders = (
        pd.concat(defender_chunks, ignore_index=True)
        .groupby(keys, as_index=False)
        .agg(
            visible_defender_count=("visible_defender_count", "sum"),
            defenders_within_3m=("defenders_within_3m", "sum"),
            defenders_within_5m=("defenders_within_5m", "sum"),
            nearest_defender_m=("nearest_defender_m", "min"),
            defender_distance_sum=("defender_distance_sum", "sum"),
            target_available=("target_available", "max"),
            lane_clearance_min=("lane_clearance_min", "min"),
            packing_index=("packing_index", "sum"),
        )
    )
    defenders["mean_defender_m"] = (
        defenders["defender_distance_sum"]
        / defenders["visible_defender_count"].replace(0, np.nan)
    )
    defenders["passing_lane_availability"] = np.where(
        defenders["target_available"],
        np.where(
            defenders["lane_clearance_min"].notna(),
            (
                defenders["lane_clearance_min"] / 1.5
            ).clip(0.0, 1.0),
            1.0,
        ),
        np.nan,
    )
    defenders["space_received"] = (
        defenders["nearest_defender_m"] / 10.0
    ).clip(0.0, 1.0)
    defenders["sb360_available"] = True
    result = defenders.merge(
        lookup,
        on=keys,
        how="left",
        validate="one_to_one",
    )
    result["actor_shape_deviation_m"] = np.nan
    if teammate_chunks:
        teammates = (
            pd.concat(teammate_chunks, ignore_index=True)
            .groupby(keys, as_index=False)
            .agg(
                teammate_x_sum=("teammate_x_sum", "sum"),
                teammate_y_sum=("teammate_y_sum", "sum"),
                teammate_count=("teammate_count", "sum"),
            )
        )
        teammates["teammate_centroid_x"] = (
            teammates["teammate_x_sum"]
            / teammates["teammate_count"].replace(0, np.nan)
        )
        teammates["teammate_centroid_y"] = (
            teammates["teammate_y_sum"]
            / teammates["teammate_count"].replace(0, np.nan)
        )
        result = result.merge(
            teammates[
                keys + ["teammate_centroid_x", "teammate_centroid_y"]
            ],
            on=keys,
            how="left",
            validate="one_to_one",
        )
        result["actor_shape_deviation_m"] = np.hypot(
            (result["actor_x"] - result["teammate_centroid_x"]) * x_scale,
            (result["actor_y"] - result["teammate_centroid_y"]) * y_scale,
        )
    result["space_created_proxy"] = np.nan
    result["space_created_proxy_available"] = False
    return result[
        [
            "match_id",
            "event_uuid",
            "sb360_available",
            "defenders_within_3m",
            "defenders_within_5m",
            "nearest_defender_m",
            "mean_defender_m",
            "passing_lane_availability",
            "packing_index",
            "space_received",
            "visible_defender_count",
            "actor_shape_deviation_m",
            "space_created_proxy",
            "space_created_proxy_available",
        ]
    ]
