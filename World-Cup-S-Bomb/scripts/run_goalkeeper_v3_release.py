#!/usr/bin/env python3
"""Generate the isolated Pass-7 goalkeeper-v3 release inputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_ranking_repair_v3 import (  # noqa: E402
    ACTIVE_RANKINGS_PATH,
    COMPONENTS_PATH,
    EVENTS_PATH,
    MATCHES_PATH,
    PASS3_ROOT,
    _clean_json,
    _goalkeeper_v3,
)


RATINGS_PATH = PASS3_ROOT / "pass7_goalkeeper_ratings.csv"
AUDIT_PATH = PASS3_ROOT / "pass7_goalkeeper_v3.json"
MATCH_FEATURES_PATH = PASS3_ROOT / "pass7_goalkeeper_match_features.csv"


def main() -> None:
    event_columns = [
        "match_id",
        "period",
        "type",
        "team",
        "shot_type",
        "shot_outcome",
        "shot_statsbomb_xg",
        "shot_end_location",
        "shot_body_part",
        "shot_technique",
        "shot_one_on_one",
        "shot_first_time",
    ]
    events = pd.read_csv(
        EVENTS_PATH,
        usecols=event_columns,
        low_memory=False,
    )
    events = events.loc[
        events["type"].astype(str).str.contains(
            r"Shot|Own Goal",
            case=False,
            na=False,
        )
    ].copy()
    matches = pd.read_csv(MATCHES_PATH)
    components = pd.read_csv(COMPONENTS_PATH)
    base = pd.read_csv(ACTIVE_RANKINGS_PATH, low_memory=False)
    ratings, audit, match_features = _goalkeeper_v3(
        base,
        events,
        matches,
        components,
    )
    PASS3_ROOT.mkdir(parents=True, exist_ok=True)
    ratings.to_csv(
        RATINGS_PATH,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )
    match_features.to_csv(
        MATCH_FEATURES_PATH,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )
    AUDIT_PATH.write_text(
        json.dumps(
            _clean_json(audit),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "ratings": RATINGS_PATH.relative_to(PROJECT_ROOT).as_posix(),
                "audit": AUDIT_PATH.relative_to(PROJECT_ROOT).as_posix(),
                "match_features": (
                    MATCH_FEATURES_PATH.relative_to(PROJECT_ROOT).as_posix()
                ),
                "main_goalkeepers": int(
                    ratings["goalkeeper_rank_v3"].notna().sum()
                ),
                "gate_passed": audit["gate_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
