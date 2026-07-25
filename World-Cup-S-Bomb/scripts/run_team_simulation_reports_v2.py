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

from src.report_generators_v2 import (  # noqa: E402
    generate_full_team_coaching_reports,
    generate_individual_starter_reports,
)
from src.simulation_engine_v2 import (  # noqa: E402
    EmpiricalHurdleModel,
    build_lineup_matchup_features,
    calculate_expected_vs_actual_deltas,
    compute_player_synergy_matrix,
    cluster_player_playstyles,
    derive_physicality_metrics,
    identify_recurrent_tactical_mistakes,
    select_starter_cohort,
    simulate_starter_replacement_impact,
    simulate_tactical_style_outcomes,
)
from track_pipeline_eta import PipelineTimer  # noqa: E402


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
V2_HURDLE = PROJECT_ROOT / "models/coaching_model_benchmark_v2.joblib"


def _load_inputs() -> dict[str, pd.DataFrame]:
    LOGGER.info("Loading player, lineup, recommendation, and event inputs")
    components = pd.read_csv(COMPONENTS)
    intervals = pd.read_csv(INTERVALS)
    lineups = pd.read_csv(LINEUPS)
    recommendations = pd.read_csv(RECOMMENDATIONS, low_memory=False)
    defensive = pd.read_csv(
        DEFENSIVE,
        usecols=[
            "possession_uid",
            "defensive_style",
            "opponent_transition_shot",
            "opponent_transition_xg",
        ],
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
            "location",
            "pass_end_location",
            "under_pressure",
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


def load_model_bundle(
    path: Path = V2_HURDLE,
    *,
    allow_empirical_fallback: bool = False,
) -> tuple[dict[str, object] | None, str, str]:
    """Load a schema-checked v2 bundle; fallback must be explicitly enabled."""

    try:
        bundle = joblib.load(path)
    except Exception as exc:
        if allow_empirical_fallback:
            return None, "regularized_empirical_fallback", f"{type(exc).__name__}: {exc}"
        raise RuntimeError(
            f"Required v2 model bundle could not be loaded from {path}: {exc}. "
            "Run benchmark_coaching_models_v2.py first or explicitly enable fallback."
        ) from exc
    required = {
        "schema_version",
        "model_version",
        "target",
        "feature_names",
        "model",
        "calibrator",
        "threshold_status",
        "split_matches",
    }
    missing = sorted(required - set(bundle))
    if missing:
        raise ValueError(f"V2 bundle is missing required keys: {missing}")
    if bundle["target"] != "transition_conceded":
        raise ValueError(f"Unexpected model target: {bundle['target']}")
    return bundle, "calibrated_classifier_bundle", ""


def _run_pipeline_original(project_root: Path = PROJECT_ROOT) -> dict[str, object]:
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


def run_pipeline(
    project_root: Path = PROJECT_ROOT,
    *,
    model_path: Path = V2_HURDLE,
) -> dict[str, object]:
    """Run v2 on disjoint matches with the calibrated canonical classifier."""

    timer = PipelineTimer(pipeline="run_team_simulation_reports_v2")
    with timer.stage("load_inputs_and_model", total=2, unit="source") as update:
        data = _load_inputs()
        update(1)
        bundle, model_source, model_warning = load_model_bundle(model_path)
        update(2, model_source)
    assert bundle is not None

    raw = data["recommendations"]
    defensive = data["defensive"].drop_duplicates("possession_uid")
    split_matches = bundle["split_matches"]
    train = (
        raw[
            ~raw["is_test_fold"].astype(bool)
            & raw["match_id"].isin(split_matches["train"])
        ]
        .sort_values(["possession_uid", "validation_fold"])
        .drop_duplicates("possession_uid")
    )
    test = (
        raw[
            raw["is_test_fold"].astype(bool)
            & raw["match_id"].isin(split_matches["test"])
        ]
        .drop_duplicates("possession_uid")
    )
    train = train.merge(defensive, on="possession_uid", validate="one_to_one")
    test = test.merge(defensive, on="possession_uid", validate="one_to_one")
    for frame in (train, test):
        frame["transition_conceded"] = frame["opponent_transition_shot"].astype(int)
        frame["defensive_style"] = frame["defensive_style"].fillna("Unknown")
    if set(train["match_id"]) & set(test["match_id"]):
        raise RuntimeError("Train/test match leakage detected")

    components = data["components"]
    intervals = data["intervals"]
    with timer.stage("player_profiles", total=342, unit="player") as update:
        cohort_ids = select_starter_cohort(
            components, intervals, count=342
        )["player_id"].astype(int).tolist()
        all_profiles = derive_physicality_metrics(components)
        cohort_profiles = cluster_player_playstyles(
            derive_physicality_metrics(components, cohort_ids), data["events"]
        )
        profile_path = (
            project_root / "data/processed/player_physicality_profiles_v2.csv"
        )
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        cohort_profiles.to_csv(profile_path, index=False)
        update(342)

    with timer.stage("player_synergy", total=342 * 342, unit="pair") as update:
        all_ids = all_profiles["player_id"].astype(int).tolist()
        full_synergy = compute_player_synergy_matrix(
            components, data["events"], intervals, all_ids
        )
        cohort_synergy = full_synergy[
            full_synergy["row_player_id"].isin(cohort_ids)
            & full_synergy["column_player_id"].isin(cohort_ids)
        ].copy()
        cohort_synergy.to_parquet(
            project_root / "data/processed/player_synergy_matrix_v2.parquet",
            index=False,
        )
        update(len(cohort_synergy))

    matchup = build_lineup_matchup_features(
        data["lineups"], all_profiles, full_synergy
    )
    matchup.to_csv(
        project_root / "data/processed/lineup_matchup_features_v2.csv", index=False
    )
    matchup_join = matchup.drop(
        columns=["match_id", "attacking_team", "defending_team"], errors="ignore"
    )
    with timer.stage(
        "calibrated_tactical_scenarios", total=len(test), unit="possession"
    ) as update:
        hurdle = EmpiricalHurdleModel().fit(train).attach_transition_bundle(bundle)
        train_joined = train.merge(
            matchup_join, on="possession_uid", validate="one_to_one"
        )
        hurdle.fit_physical_adjustments(train_joined)
        contexts = test.merge(matchup_join, on="possession_uid", validate="one_to_one")
        contexts["actual_style"] = contexts["attacking_style"]
        tactical = simulate_tactical_style_outcomes(contexts, hurdle)
        simulation_dir = project_root / "results/simulations/v2"
        simulation_dir.mkdir(parents=True, exist_ok=True)
        tactical.to_parquet(
            simulation_dir / "tactical_style_simulations_v2.parquet", index=False
        )
        update(len(test))

    with timer.stage("constrained_substitutions", total=32, unit="team") as update:
        substitutions, optimized = simulate_starter_replacement_impact(
            components, all_profiles, full_synergy, hurdle
        )
        if substitutions.empty:
            substitutions = pd.DataFrame(
                columns=[
                    "team",
                    "starter_player_id",
                    "starter_player",
                    "bench_player_id",
                    "bench_player",
                    "optimal_style",
                    "baseline_expected_net_xg",
                    "substitution_expected_net_xg",
                    "expected_net_xg_gain",
                    "gain_ci_low",
                    "gain_ci_high",
                    "recommended_substitution_minute",
                    "position_compatible",
                    "starter_war_vs_average_bench",
                    "is_best_team_substitution",
                ]
            )
        substitutions.to_parquet(
            simulation_dir / "substitution_optimization_v2.parquet", index=False
        )
        optimized.to_csv(
            simulation_dir / "optimized_starting_lineups_v2.csv", index=False
        )
        update(32)

    eva_detail, team_summary = calculate_expected_vs_actual_deltas(tactical)
    recurrent = identify_recurrent_tactical_mistakes(eva_detail, defensive)
    audit_dir = project_root / "results/audit/v2"
    audit_dir.mkdir(parents=True, exist_ok=True)
    team_summary.to_csv(
        audit_dir / "expected_vs_actual_team_summary_v2.csv", index=False
    )
    eva_detail.to_parquet(
        audit_dir / "expected_vs_actual_possessions_v2.parquet", index=False
    )
    recurrent.to_csv(
        audit_dir / "recurrent_tactical_mistakes_v2.csv", index=False
    )

    metadata = {
        key: bundle.get(key)
        for key in [
            "model_version",
            "target",
            "calibration_method",
            "threshold",
            "threshold_status",
            "holdout_metrics",
        ]
    }
    metadata["runtime"] = timer.summary()
    reports_root = project_root / "results/reports/v2"
    expected_reports = 342 + int(team_summary["team"].nunique())
    with timer.stage(
        "dynamic_reports", total=expected_reports, unit="report"
    ) as update:
        starter_count = generate_individual_starter_reports(
            cohort_profiles, cohort_synergy, reports_root / "starters"
        )
        team_count = generate_full_team_coaching_reports(
            team_summary,
            optimized,
            substitutions,
            matchup,
            recurrent,
            reports_root / "teams",
            model_metadata=metadata,
            synergy=cohort_synergy,
            profiles=cohort_profiles,
        )
        update(starter_count + team_count)

    checks = {
        "train_test_matches_disjoint": not bool(
            set(split_matches["train"]) & set(split_matches["test"])
        ),
        "canonical_target": bundle["target"] == "transition_conceded",
        "profiles": len(cohort_profiles) == 342,
        "synergy": len(cohort_synergy) == 342 * 342,
        "three_styles": len(tactical) == 3 * len(test),
        "substitution_floor": substitutions.empty
        or bool(
            substitutions["expected_net_xg_gain"].gt(0.005).all()
            and substitutions["gain_ci_low"].gt(0).all()
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(
            "V2 checks failed: "
            + ", ".join(name for name, passed in checks.items() if not passed)
        )
    manifest = {
        "schema_version": 2,
        "status": "complete",
        "model_source": model_source,
        "model_warning": model_warning,
        **metadata,
        "fold_assignment_hash": bundle["fold_assignment_hash"],
        "dataset_size": bundle["dataset_size"],
        "positive_count": bundle["positive_count"],
        "split_matches": split_matches,
        "counts": {
            "train_possessions": len(train),
            "test_possessions": len(test),
            "tactical_scenarios": len(tactical),
            "eligible_substitutions": len(substitutions),
            "starter_reports": starter_count,
            "team_reports": team_count,
        },
        "checks": checks,
        "runtime": timer.summary(),
    }
    manifest_path = reports_root / "pipeline_manifest_v2.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
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
