#!/usr/bin/env python3
"""Download, cache, flatten, and validate StatsBomb 360 freeze frames.

Raw API responses are stored as one gzip-compressed JSON file per match so the
download is resumable and the source payload remains reproducible. Two combined
CSV tables are then produced: player freeze-frame locations and frame-level
visible areas. Existing valid match caches are never downloaded again unless
--force is supplied.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any

from statsbombpy import sb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATCHES = PROJECT_ROOT / "data" / "raw" / "matches.csv"
DEFAULT_CACHE_DIR = PROJECT_ROOT / "data" / "interim" / "frames360" / "raw"
DEFAULT_ACTORS = PROJECT_ROOT / "data" / "interim" / "world_cup_360_frames.csv"
DEFAULT_VISIBLE = PROJECT_ROOT / "data" / "interim" / "world_cup_360_visible_areas.csv"
DEFAULT_REPORT = PROJECT_ROOT / "results" / "frames_360_validation.md"

ACTOR_FIELDS = ["match_id", "event_uuid", "teammate", "actor", "keeper", "x", "y"]
VISIBLE_FIELDS = ["match_id", "event_uuid", "visible_area"]


def load_match_ids(path: Path) -> list[int]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    unavailable = [row["match_id"] for row in rows if row.get("match_status_360") != "available"]
    if unavailable:
        raise ValueError(f"360 data is not marked available for matches: {unavailable}")
    match_ids = [int(row["match_id"]) for row in rows]
    if len(match_ids) != 64 or len(set(match_ids)) != 64:
        raise ValueError(f"Expected 64 unique World Cup matches, found {len(set(match_ids))}")
    return match_ids


def read_cache(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"Invalid cached payload in {path}")
    return payload


def cache_is_valid(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    try:
        payload = read_cache(path)
    except (OSError, json.JSONDecodeError, ValueError):
        return False
    return bool(payload) and all(isinstance(frame, dict) and frame.get("event_uuid") for frame in payload)


def write_cache_atomic(path: Path, payload: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f"{path.stem}-", suffix=".json.gz", dir=path.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        with gzip.open(temporary, "wt", encoding="utf-8", compresslevel=6) as handle:
            json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def fetch_match(match_id: int, attempts: int = 3) -> list[dict[str, Any]]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            payload = sb.frames(match_id=match_id, fmt="api")
            if not isinstance(payload, list) or not payload:
                raise ValueError(f"Empty or invalid 360 response for match {match_id}")
            return payload
        except Exception as error:  # statsbombpy may raise requests or parsing errors
            last_error = error
            if attempt < attempts:
                time.sleep(2 ** (attempt - 1))
    raise RuntimeError(f"Failed to download match {match_id} after {attempts} attempts") from last_error


def cache_matches(match_ids: list[int], cache_dir: Path, force: bool) -> tuple[int, int]:
    downloaded = 0
    reused = 0
    for position, match_id in enumerate(match_ids, start=1):
        cache_path = cache_dir / f"{match_id}.json.gz"
        if not force and cache_is_valid(cache_path):
            reused += 1
            print(f"[{position:02}/{len(match_ids)}] Reusing match {match_id}")
            continue
        print(f"[{position:02}/{len(match_ids)}] Downloading match {match_id}")
        payload = fetch_match(match_id)
        write_cache_atomic(cache_path, payload)
        downloaded += 1
    return downloaded, reused


def actor_rows(match_id: int, frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for frame in frames:
        event_uuid = frame.get("event_uuid")
        for actor_data in frame.get("freeze_frame") or []:
            location = actor_data.get("location")
            if not isinstance(location, list) or len(location) < 2:
                continue
            rows.append(
                {
                    "match_id": match_id,
                    "event_uuid": event_uuid,
                    "teammate": bool(actor_data.get("teammate", False)),
                    "actor": bool(actor_data.get("actor", False)),
                    "keeper": bool(actor_data.get("keeper", False)),
                    "x": float(location[0]),
                    "y": float(location[1]),
                }
            )
    return rows


def visible_rows(match_id: int, frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "match_id": match_id,
            "event_uuid": frame.get("event_uuid"),
            "visible_area": json.dumps(frame.get("visible_area") or [], separators=(",", ":")),
        }
        for frame in frames
        if frame.get("event_uuid")
    ]


def flatten_caches(
    match_ids: list[int],
    cache_dir: Path,
    actor_output: Path,
    visible_output: Path,
) -> dict[str, Any]:
    actor_output.parent.mkdir(parents=True, exist_ok=True)
    visible_output.parent.mkdir(parents=True, exist_ok=True)
    frame_counts: Counter[int] = Counter()
    actor_counts: Counter[int] = Counter()
    event_keys: set[tuple[int, str]] = set()
    duplicate_frames = 0

    with actor_output.open("w", newline="", encoding="utf-8") as actor_handle, visible_output.open(
        "w", newline="", encoding="utf-8"
    ) as visible_handle:
        actor_writer = csv.DictWriter(actor_handle, fieldnames=ACTOR_FIELDS)
        visible_writer = csv.DictWriter(visible_handle, fieldnames=VISIBLE_FIELDS)
        actor_writer.writeheader()
        visible_writer.writeheader()

        for match_id in match_ids:
            frames = read_cache(cache_dir / f"{match_id}.json.gz")
            actors = actor_rows(match_id, frames)
            visible = visible_rows(match_id, frames)
            actor_writer.writerows(actors)
            visible_writer.writerows(visible)
            frame_counts[match_id] = len(visible)
            actor_counts[match_id] = len(actors)
            for frame in visible:
                key = (match_id, str(frame["event_uuid"]))
                duplicate_frames += int(key in event_keys)
                event_keys.add(key)

    return {
        "matches": len(match_ids),
        "frames": sum(frame_counts.values()),
        "actors": sum(actor_counts.values()),
        "duplicate_frame_keys": duplicate_frames,
        "min_frames_per_match": min(frame_counts.values()),
        "max_frames_per_match": max(frame_counts.values()),
        "min_actors_per_match": min(actor_counts.values()),
        "max_actors_per_match": max(actor_counts.values()),
    }


def validate(metrics: dict[str, Any], match_ids: list[int], cache_dir: Path) -> dict[str, bool]:
    checks = {
        "All 64 matches cached": metrics["matches"] == 64
        and all(cache_is_valid(cache_dir / f"{match_id}.json.gz") for match_id in match_ids),
        "Every match has freeze frames": metrics["min_frames_per_match"] > 0,
        "Every match has player locations": metrics["min_actors_per_match"] > 0,
        "Frame event keys are unique within matches": metrics["duplicate_frame_keys"] == 0,
        "Player rows outnumber frame rows": metrics["actors"] > metrics["frames"],
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ValueError("360 validation failed: " + "; ".join(failures))
    return checks


def write_report(
    path: Path,
    metrics: dict[str, Any],
    checks: dict[str, bool],
    downloaded: int,
    reused: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# StatsBomb 360 Cache Validation",
        "",
        f"- Matches: {metrics['matches']}",
        f"- Matches downloaded this run: {downloaded}",
        f"- Existing match caches reused: {reused}",
        f"- Unique event frames: {metrics['frames']:,}",
        f"- Player-location rows: {metrics['actors']:,}",
        f"- Frames per match: {metrics['min_frames_per_match']:,}–{metrics['max_frames_per_match']:,}",
        f"- Player rows per match: {metrics['min_actors_per_match']:,}–{metrics['max_actors_per_match']:,}",
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
            "## Storage",
            "",
            "- Raw resumable cache: `data/interim/frames360/raw/<match_id>.json.gz`",
            "- Flattened player locations: `data/interim/world_cup_360_frames.csv`",
            "- Frame visible areas: `data/interim/world_cup_360_visible_areas.csv`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matches", type=Path, default=DEFAULT_MATCHES)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--actors-output", type=Path, default=DEFAULT_ACTORS)
    parser.add_argument("--visible-output", type=Path, default=DEFAULT_VISIBLE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true", help="Redownload even when a valid cache exists")
    parser.add_argument("--limit", type=int, help="Process only the first N matches for a smoke test")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    match_ids = load_match_ids(args.matches)
    if args.limit:
        if args.limit < 1:
            raise ValueError("--limit must be positive")
        match_ids = match_ids[: args.limit]

    downloaded, reused = cache_matches(match_ids, args.cache_dir, args.force)
    metrics = flatten_caches(match_ids, args.cache_dir, args.actors_output, args.visible_output)

    if len(match_ids) == 64:
        checks = validate(metrics, match_ids, args.cache_dir)
        write_report(args.report, metrics, checks, downloaded, reused)
        print(f"Wrote validation report to {args.report}")
    else:
        print("Smoke-test mode: full 64-match validation report was not written")

    print(f"Wrote {metrics['frames']:,} event frames to {args.visible_output}")
    print(f"Wrote {metrics['actors']:,} player locations to {args.actors_output}")


if __name__ == "__main__":
    main()
