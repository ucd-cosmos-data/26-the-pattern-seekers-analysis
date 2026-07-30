#!/usr/bin/env python3
"""Re-rate players from the saved evaluation table and regenerate artifacts.

The full pipeline recomputes events, VAEP, attention, and role models before
it reaches the rating composite. When only the rating formula changes (for
example the vaep component definition, reliability shrinkage, or the
goalkeeper composite weights), every rating input is already present in
``data/processed/player_evaluations.csv``. This script re-applies the current
rating code to that table and replays the canonical artifact generation so
rankings, profiles, summaries, and aliases stay mutually consistent.

Team-profile threat/defense/pressure metrics and the model-validation
summary are reproduced from the existing canonical artifacts because their
inputs did not change.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RatingConfig  # noqa: E402
from src.models.goalkeeper_valuation import (  # noqa: E402
    calculate_goalkeeper_ratings,
    goalkeeper_model_summary,
)
from src.models.valuation import calculate_final_player_rating  # noqa: E402
from src.reporting.artifacts import ArtifactGenerator  # noqa: E402

EVALUATIONS = PROJECT_ROOT / "data" / "processed" / "player_evaluations.csv"
COMPONENTS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_player_match_components.csv"
)
REPORTS = PROJECT_ROOT / "results" / "reports"

TEAM_METRIC_BULLETS = {
    "Total xT created": "total_xt_created",
    "Total xA created": "total_xa_created",
    "Mean defensive hull area": "defensive_hull_area",
    "Mean defensive density": "defensive_density",
    "Mean defensive width": "defensive_width",
    "Mean defensive depth": "defensive_depth",
    "Pass completion under pressure": "pressure_resistance_rate",
    "Pressured pass sample": "pressured_passes",
}

GOALKEEPER_RECOMPUTED_KEYS = {
    "eligible_goalkeepers",
    "rating_feature_coverage_mean",
    "rating_reliability_mean",
}


def load_team_metrics() -> pd.DataFrame:
    """Rebuild the team metric table from the canonical team profiles."""

    records: list[dict[str, object]] = []
    for path in sorted((REPORTS / "team_profiles").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = re.search(r"^# (.+) Team Profile$", text, re.MULTILINE)
        if not title:
            raise ValueError(f"Unrecognized team profile title in {path}")
        record: dict[str, object] = {"team": title.group(1)}
        for label, column in TEAM_METRIC_BULLETS.items():
            bullet = re.search(
                rf"^- {re.escape(label)}: (.+)$", text, re.MULTILINE
            )
            if bullet and bullet.group(1).strip() != "not available":
                record[column] = float(bullet.group(1))
        records.append(record)
    frame = pd.DataFrame(records)
    if len(frame) != 32:
        raise ValueError(f"Expected 32 team profiles, found {len(frame)}")
    return frame


def load_team_player_pool() -> pd.DataFrame:
    components = pd.read_csv(COMPONENTS, low_memory=False)
    return components.groupby(["player_id", "team"], as_index=False).agg(
        player_name=("player", "first"),
        position_group=("position_group", "first"),
        minutes=("minutes", "sum"),
    )


def rate_players(evaluations: pd.DataFrame) -> pd.DataFrame:
    config = RatingConfig()
    outfield = evaluations.loc[
        ~evaluations["position_group"].eq("Goalkeeper")
    ].copy()
    rated_outfield = calculate_final_player_rating(outfield, config=config)
    rated_outfield["global_rank_eligible"] = True

    goalkeepers = evaluations.loc[
        evaluations["position_group"].eq("Goalkeeper")
    ].copy()
    goalkeeper_ratings = calculate_goalkeeper_ratings(
        goalkeepers,
        reliability_minutes=config.reliability_minutes,
    )
    goalkeeper_ratings["raw_final_player_rating"] = goalkeeper_ratings[
        "goalkeeper_raw_rating"
    ]
    goalkeeper_ratings["rating_minutes_reliability"] = goalkeeper_ratings[
        "goalkeeper_rating_reliability"
    ]
    goalkeeper_ratings["player_evaluation_score"] = goalkeeper_ratings[
        "final_player_rating"
    ]
    goalkeeper_ratings["functional_role"] = "Goalkeeper"
    goalkeeper_ratings["probabilistic_role"] = "Goalkeeper"
    goalkeeper_ratings["role_rank"] = goalkeeper_ratings["goalkeeper_rank"]

    rated = pd.concat(
        [rated_outfield, goalkeeper_ratings], ignore_index=True, sort=False
    )
    rated["team_rank"] = (
        rated.groupby("team")["final_player_rating"]
        .rank(method="min", ascending=False)
        .astype(int)
    )
    return rated


def refresh_model_summary(
    rated: pd.DataFrame,
    goalkeeper_ratings: pd.DataFrame,
) -> dict:
    summary = json.loads(
        (REPORTS / "model_summary.json").read_text(encoding="utf-8")
    )
    summary.pop("schema_version", None)
    eligible = rated["global_rank_eligible"].fillna(False).astype(bool)
    rho = float(
        spearmanr(
            rated.loc[eligible, "legacy_final_player_rating"],
            rated.loc[eligible, "final_player_rating"],
        ).statistic
    )
    summary.setdefault("metrics", {})["spearman_with_legacy_rankings"] = rho
    goalkeeper_section = summary.get("goalkeeper")
    if isinstance(goalkeeper_section, dict):
        audit = {
            key: value
            for key, value in goalkeeper_section.items()
            if key not in GOALKEEPER_RECOMPUTED_KEYS
        }
        summary["goalkeeper"] = goalkeeper_model_summary(
            audit, goalkeeper_ratings
        )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=REPORTS)
    args = parser.parse_args()

    evaluations = pd.read_csv(EVALUATIONS, low_memory=False)
    rated = rate_players(evaluations)
    goalkeeper_rows = rated.loc[rated["position_group"].eq("Goalkeeper")]

    model_summary = refresh_model_summary(rated, goalkeeper_rows)
    validation_comparison = pd.read_csv(
        REPORTS / "rating_validation_comparison.csv"
    )
    team_metrics = load_team_metrics()
    tournament_teams = sorted(team_metrics["team"])
    team_player_pool = load_team_player_pool()

    manifest = ArtifactGenerator(args.output_root).generate(
        rated,
        model_summary=model_summary,
        validation_comparison=validation_comparison,
        tournament_teams=tournament_teams,
        team_metrics=team_metrics,
        team_player_pool=team_player_pool,
    )

    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from run_pipeline import _publish_canonical_aliases  # noqa: E402

    aliases = _publish_canonical_aliases(
        PROJECT_ROOT, args.output_root, rated
    )
    print(f"Regenerated {len(manifest.files)} artifacts")
    print(f"Republished {len(aliases)} canonical aliases")
    top = ArtifactGenerator.prepare_rankings(rated)
    leaders = top.loc[top["global_rank"].notna()].nsmallest(5, "global_rank")
    for _, row in leaders.iterrows():
        print(
            f"  #{int(row['global_rank'])} {row['player_name']} "
            f"({row['team']}) {row['final_player_rating']:.4f}"
        )


if __name__ == "__main__":
    main()
