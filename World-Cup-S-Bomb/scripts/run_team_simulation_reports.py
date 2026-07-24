#!/usr/bin/env python3
"""Run physicality, chemistry, simulation, audit, and reporting Steps 1–5."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import joblib
import pandas as pd
from tqdm import tqdm


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.report_generators import (  # noqa: E402
    generate_full_team_coaching_reports,
    generate_individual_starter_reports,
)
from src.simulation_engine import (  # noqa: E402
    EmpiricalHurdleModel,
    build_lineup_matchup_features,
    calculate_expected_vs_actual_deltas,
    compute_player_synergy_matrix,
    derive_individual_playstyle_clusters,
    derive_physicality_metrics,
    identify_recurrent_tactical_mistakes,
    select_starter_cohort,
    simulate_starter_replacement_impact,
    simulate_tactical_style_outcomes,
)


LOGGER = logging.getLogger("team-simulation")
COMPONENTS = PROJECT_ROOT / "data/interim/world_cup_player_match_components.csv"
INTERVALS = PROJECT_ROOT / "data/interim/world_cup_lineup_intervals.csv"
LINEUPS = PROJECT_ROOT / "data/interim/world_cup_possession_lineups.csv"
EVENTS = PROJECT_ROOT / "notebooks/all_events.csv"
RECOMMENDATIONS = (
    PROJECT_ROOT / "data/processed/world_cup_recommendation_features.csv"
)
DEFENSIVE = PROJECT_ROOT / "data/processed/world_cup_defensive_clusters.csv"
STORED_HURDLE = PROJECT_ROOT / "models/coaching_model_benchmark.joblib"


def _load_inputs() -> dict[str, pd.DataFrame]:
    LOGGER.info("Loading player, lineup, recommendation, and event inputs")
    components = pd.read_csv(COMPONENTS)
    intervals = pd.read_csv(INTERVALS)
    lineups = pd.read_csv(LINEUPS)
    recommendations = pd.read_csv(RECOMMENDATIONS, low_memory=False)
    recommendations = recommendations[
        recommendations["is_test_fold"].astype(bool)
    ].drop_duplicates("possession_uid")
    defensive = pd.read_csv(
        DEFENSIVE,
        usecols=["possession_uid", "defensive_style"],
        low_memory=False,
    )
    events = pd.read_csv(
        EVENTS,
        usecols=[
            "match_id",
            "team",
            "type",
            "player_id",
            "pass_recipient_id",
            "pass_outcome",
        ],
        low_memory=False,
    )
    events = events[events["type"].eq("Pass")]
    return {
        "components": components,
        "intervals": intervals,
        "lineups": lineups,
        "recommendations": recommendations,
        "defensive": defensive,
        "events": events,
    }


def _stored_model_status() -> tuple[str, str]:
    try:
        joblib.load(STORED_HURDLE)
    except Exception as exc:
        return "regularized_empirical_fallback", f"{type(exc).__name__}: {exc}"
    return (
        "regularized_empirical_fallback",
        "Stored benchmark loaded but has no stable downstream hurdle interface",
    )


def run_pipeline(project_root: Path = PROJECT_ROOT) -> dict[str, object]:
    """Execute Steps 1–5 and return the validated artifact manifest."""

    data = _load_inputs()
    components = data["components"]
    intervals = data["intervals"]
    recommendations = data["recommendations"]

    LOGGER.info("STEP 1/5 — physicality profiles, K=8 roles, synergy")
    cohort_seed = select_starter_cohort(components, intervals, count=342)
    cohort_ids = cohort_seed["player_id"].astype(int).tolist()
    all_profiles = derive_physicality_metrics(components)
    cohort_profiles = derive_physicality_metrics(components, cohort_ids)
    cohort_profiles = derive_individual_playstyle_clusters(cohort_profiles)
    profile_output = project_root / "data/processed/player_physicality_profiles.csv"
    profile_output.parent.mkdir(parents=True, exist_ok=True)
    cohort_profiles.to_csv(profile_output, index=False)
    LOGGER.info("Wrote %s player profiles", f"{len(cohort_profiles):,}")

    # Compute all-player chemistry for lineup simulations, then export the exact
    # requested 342×342 cohort lookup.
    all_ids = all_profiles["player_id"].astype(int).tolist()
    full_synergy = compute_player_synergy_matrix(
        components, data["events"], intervals, all_ids
    )
    cohort_synergy = full_synergy[
        full_synergy["row_player_id"].isin(cohort_ids)
        & full_synergy["column_player_id"].isin(cohort_ids)
    ].copy()
    synergy_output = project_root / "data/processed/player_synergy_matrix.parquet"
    cohort_synergy.to_parquet(synergy_output, index=False)
    LOGGER.info("Wrote %s synergy cells", f"{len(cohort_synergy):,}")

    LOGGER.info("STEP 2/5 — lineup chemistry and physical matchup deltas")
    matchup = build_lineup_matchup_features(
        data["lineups"], all_profiles, full_synergy
    )
    matchup_output = project_root / "data/processed/lineup_matchup_features.csv"
    matchup.to_csv(matchup_output, index=False)
    LOGGER.info("Wrote %s lineup matchup rows", f"{len(matchup):,}")

    LOGGER.info("STEP 3/5 — tactical and roster counterfactual simulations")
    model_source, model_warning = _stored_model_status()
    LOGGER.warning("Hurdle source: %s (%s)", model_source, model_warning)
    hurdle = EmpiricalHurdleModel().fit(recommendations)
    joined = recommendations.merge(
        matchup.drop(
            columns=["match_id", "attacking_team", "defending_team"],
            errors="ignore",
        ),
        on="possession_uid",
        how="left",
        validate="one_to_one",
    )
    hurdle.fit_physical_adjustments(joined)
    contexts = joined.copy()
    contexts["actual_style"] = contexts["attacking_style"]
    tactical = simulate_tactical_style_outcomes(contexts, hurdle)
    simulation_dir = project_root / "results/simulations"
    simulation_dir.mkdir(parents=True, exist_ok=True)
    tactical_output = simulation_dir / "tactical_style_simulations.parquet"
    tactical.to_parquet(tactical_output, index=False)
    LOGGER.info("Wrote %s tactical scenarios", f"{len(tactical):,}")

    substitutions, optimized_lineups = simulate_starter_replacement_impact(
        components, all_profiles, full_synergy, hurdle
    )
    substitution_output = simulation_dir / "substitution_optimization.parquet"
    substitutions.to_parquet(substitution_output, index=False)
    optimized_lineups.to_csv(
        simulation_dir / "optimized_starting_lineups.csv", index=False
    )
    LOGGER.info("Wrote %s substitution scenarios", f"{len(substitutions):,}")

    LOGGER.info("STEP 4/5 — expected-vs-actual performance audit")
    eva_detail, team_summary = calculate_expected_vs_actual_deltas(tactical)
    recurrent = identify_recurrent_tactical_mistakes(
        eva_detail, data["defensive"]
    )
    audit_dir = project_root / "results/audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    team_summary_output = audit_dir / "expected_vs_actual_team_summary.csv"
    team_summary.to_csv(team_summary_output, index=False)
    eva_detail.to_parquet(audit_dir / "expected_vs_actual_possessions.parquet")
    recurrent.to_csv(audit_dir / "recurrent_tactical_mistakes.csv", index=False)
    LOGGER.info("Wrote audit summaries for %s teams", len(team_summary))

    LOGGER.info("STEP 5/5 — team and starter Markdown/JSON reports")
    reports_root = project_root / "results/reports"
    starter_count = generate_individual_starter_reports(
        cohort_profiles,
        cohort_synergy,
        reports_root / "starters",
    )
    team_count = generate_full_team_coaching_reports(
        team_summary,
        optimized_lineups,
        substitutions,
        matchup,
        recurrent,
        reports_root / "teams",
    )
    checks = {
        "physical_profile_rows": len(cohort_profiles) == 342,
        "synergy_matrix_cells": len(cohort_synergy) == 342 * 342,
        "all_32_teams_in_matchups": matchup["attacking_team"].nunique() == 32,
        "three_styles_per_possession": len(tactical)
        == 3 * recommendations["possession_uid"].nunique(),
        "team_audit_rows": len(team_summary) == 32,
        "starter_report_pairs": starter_count == 342,
        "team_report_pairs": team_count == 32,
        "optimized_lineup_rows": len(optimized_lineups) == 32 * 11,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError("Pipeline validation failed: " + ", ".join(failed))
    manifest: dict[str, object] = {
        "status": "complete",
        "model_source": model_source,
        "model_warning": model_warning,
        "cohort_definition": (
            "Top 342 tournament-minute players among players with at least one start"
        ),
        "tracking_proxies": {
            "tackles": "ground duel wins (duels_won - aerial_wins)",
            "defensive_recovery_runs": "event recoveries",
        },
        "counts": {
            "player_profiles": len(cohort_profiles),
            "synergy_cells": len(cohort_synergy),
            "lineup_matchups": len(matchup),
            "tactical_scenarios": len(tactical),
            "substitution_scenarios": len(substitutions),
            "team_audits": len(team_summary),
            "starter_report_pairs": starter_count,
            "team_report_pairs": team_count,
        },
        "checks": checks,
    }
    (reports_root / "pipeline_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    LOGGER.info("All Steps 1–5 passed artifact validation")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING"],
        default="INFO",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    for _ in tqdm(range(1), desc="World Cup reporting pipeline", unit="run"):
        manifest = run_pipeline()
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
