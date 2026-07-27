#!/usr/bin/env python3
"""Run physicality, chemistry, simulation, audit, and reporting Steps 1–5."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import joblib
import matplotlib
import numpy as np
import pandas as pd
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.calibration import calibration_curve
from sklearn.base import clone
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from tqdm import tqdm


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.report_generators import (  # noqa: E402
    compile_v4_report_packets,
    generate_full_team_coaching_reports,
    generate_individual_starter_reports,
    generate_player_heatmap_svgs,
    refresh_player_role_validation_reporting,
    refresh_prospective_validation_reporting,
)
from src.simulation_engine import (  # noqa: E402
    EmpiricalHurdleModel,
    build_v4_player_evaluations,
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
from benchmark_coaching_models_v2 import (  # noqa: E402
    V2_CATEGORICAL_FEATURES,
    V2_NUMERIC_FEATURES,
    apply_calibrator,
    fit_calibrator,
)


LOGGER = logging.getLogger("team-simulation")
COMPONENTS = PROJECT_ROOT / "data/interim/world_cup_player_match_components.csv"
INTERVALS = PROJECT_ROOT / "data/interim/world_cup_lineup_intervals.csv"
LINEUPS = PROJECT_ROOT / "data/interim/world_cup_possession_lineups.csv"
EVENTS = PROJECT_ROOT / "notebooks/all_events.csv"
FRAMES_360 = PROJECT_ROOT / "data/interim/world_cup_360_frames.csv"
FRAME_METRICS_360 = (
    PROJECT_ROOT / "data/interim/world_cup_360_frame_metrics.csv"
)
RECOMMENDATIONS = (
    PROJECT_ROOT / "data/processed/world_cup_recommendation_features.csv"
)
DEFENSIVE = PROJECT_ROOT / "data/processed/world_cup_defensive_clusters.csv"
STORED_HURDLE = PROJECT_ROOT / "models/coaching_model_benchmark.joblib"
V2_HURDLE = PROJECT_ROOT / "models/coaching_model_benchmark_v2.joblib"
V4_EVENT_COLUMNS = {
    "id",
    "index",
    "match_id",
    "period",
    "minute",
    "second",
    "team",
    "team_id",
    "type",
    "player",
    "player_id",
    "position",
    "play_pattern",
    "pass_recipient_id",
    "pass_outcome",
    "pass_body_part",
    "pass_assisted_shot_id",
    "dribble_outcome",
    "ball_receipt_outcome",
    "location",
    "pass_end_location",
    "carry_end_location",
    "shot_end_location",
    "shot_outcome",
    "shot_body_part",
    "under_pressure",
    "shot_statsbomb_xg",
}


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
    available_event_columns = set(
        pd.read_csv(EVENTS, nrows=0).columns
    )
    event_columns = sorted(V4_EVENT_COLUMNS & available_event_columns)
    events = pd.read_csv(EVENTS, usecols=event_columns, low_memory=False)
    missing_required = sorted(
        {
            "id",
            "index",
            "match_id",
            "period",
            "minute",
            "second",
            "team",
            "team_id",
            "type",
            "player",
            "player_id",
            "position",
            "play_pattern",
            "pass_recipient_id",
            "pass_outcome",
            "dribble_outcome",
            "ball_receipt_outcome",
            "location",
            "pass_end_location",
            "carry_end_location",
            "under_pressure",
            "shot_statsbomb_xg",
        }
        - set(events.columns)
    )
    if missing_required:
        raise ValueError(
            f"StatsBomb event export lacks V4 fields: {missing_required}"
        )
    actor_chunks = []
    for chunk in pd.read_csv(
        FRAMES_360,
        usecols=[
            "match_id",
            "event_uuid",
            "actor",
            "x",
            "y",
        ],
        chunksize=250_000,
    ):
        actor = chunk["actor"].astype(str).str.lower().isin(["true", "1"])
        actor_chunks.append(chunk.loc[actor])
    frame_actors = pd.concat(actor_chunks, ignore_index=True)
    frame_metrics = pd.read_csv(
        FRAME_METRICS_360,
        usecols=[
            "match_id",
            "event_uuid",
            "defensive_density",
            "nearest_defender_distance",
            "defenders_within_5",
            "defenders_behind_ball",
        ],
        low_memory=False,
    )
    return {
        "components": components,
        "intervals": intervals,
        "lineups": lineups,
        "recommendations": recommendations,
        "defensive": defensive,
        "events": events,
        "frame_actors": frame_actors,
        "frame_metrics": frame_metrics,
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


def _run_pipeline_v2_base(
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


def _calibration_matches_for_fold(
    canonical: pd.DataFrame,
    held_out_match: int,
    *,
    count: int = 10,
) -> list[int]:
    """Choose a deterministic internal calibration set excluding the OOF match."""

    stats = canonical.groupby("match_id")["transition_conceded"].sum()
    positive = [
        int(match)
        for match in stats[stats.gt(0)].sort_values(ascending=False).index
        if int(match) != held_out_match
    ]
    negative = [
        int(match)
        for match in stats[stats.eq(0)].sort_index().index
        if int(match) != held_out_match
    ]
    selected = positive[:2] + negative[: max(count - 2, 0)]
    if len(selected) < count:
        extras = [
            int(match)
            for match in stats.index
            if int(match) != held_out_match and int(match) not in selected
        ]
        selected.extend(extras[: count - len(selected)])
    return sorted(selected)


def _write_v4_model_summary(
    path: Path,
    *,
    provenance: dict[str, object],
    profiles: pd.DataFrame,
    oof_metrics: dict[str, object],
    compiled_checks: dict[str, int],
) -> None:
    """Refresh the generated validation section without erasing the audit guide."""

    marker = "## Latest generated VAEP/xT validation"
    existing = path.read_text(encoding="utf-8") if path.exists() else (
        "# V4 Model Explanations\n\n"
        "## V4 Model Explanations\n\n"
        "This pipeline applies 360-Augmented VAEP and xT concurrently without "
        "feeding xT into the VAEP feature matrix.\n"
    )
    existing = existing.split(marker, maxsplit=1)[0].rstrip()
    top_rows = profiles.sort_values(
        ["final_player_rating", "minutes"], ascending=False
    ).head(10)
    top_table = "\n".join(
        f"| {index} | {row.player} | {row.team} | {row.minutes:.0f} | "
        f"{row.vaep_total_p90:+.4f} | {row.vaep_per_touch:+.5f} | "
        f"{row.xt_p90:+.4f} | {row.final_player_rating:+.4f} |"
        for index, row in enumerate(top_rows.itertuples(index=False), start=1)
    )
    comparison_rows = provenance["vaep_model_comparison"]
    comparison_table = "\n".join(
        f"| {row['model_name']} | {row['evaluation_scope']} | "
        f"{float(row['roc_auc']):.6f} | {float(row['pr_auc']):.6f} | "
        f"{float(row['brier_score']):.6f} | "
        f"{'yes' if bool(row['selected']) else 'no'} |"
        for row in comparison_rows
    )
    lines = [
        existing,
        "",
        marker,
        "",
        f"- Selected model: `{provenance['vaep_selected_model']}`.",
        f"- Calibration: `{provenance['vaep_calibration_method']}`.",
        (
            f"- Selected-architecture development OOF: Brier "
            f"{provenance['vaep_oof_metrics']['brier_score']:.6f}, "
            f"ROC-AUC {provenance['vaep_oof_metrics']['roc_auc']:.6f}, "
            f"PR-AUC {provenance['vaep_oof_metrics']['pr_auc']:.6f}."
        ),
        (
            f"- Final untouched test pass: Brier "
            f"{provenance['vaep_final_test_metrics']['brier_score']:.6f}, "
            f"ROC-AUC {provenance['vaep_final_test_metrics']['roc_auc']:.6f}, "
            f"PR-AUC {provenance['vaep_final_test_metrics']['pr_auc']:.6f}."
        ),
        (
            f"- StatsBomb 360 join coverage: "
            f"{100 * provenance['360_join_rate']:.1f}%."
        ),
        (
            f"- Eligible players: {provenance['players_after_cutoff']} of "
            f"{provenance['players_before_cutoff']}; "
            f"{provenance['players_dropped']} excluded below 300 minutes."
        ),
        (
            f"- Legacy transition OOF: Brier {float(oof_metrics['brier']):.6f}, "
            f"ROC-AUC {float(oof_metrics['roc_auc']):.6f}, "
            f"PR-AUC {float(oof_metrics['pr_auc']):.6f}."
        ),
        (
            f"- Reports: {compiled_checks['markdown_files']} compiled Markdown "
            f"files and {compiled_checks['compiled_player_sections']} player sections."
        ),
        "",
        "### Leak-free model comparison",
        "",
        "| Model | Evaluation scope | ROC-AUC | PR-AUC | Brier | Selected |",
        "|---|---|---:|---:|---:|---|",
        comparison_table,
        "",
        "All new architectures use identical match-level development folds. "
        "The final test partition was opened once, after OOF model selection. "
        "The legacy row predicts a different transition target and is included "
        "as a reporting baseline, not as a VAEP selection candidate.",
        "",
        "### Unified tournament leaders",
        "",
        "| Rank | Player | Team | Minutes | VAEP/90 | VAEP/touch | xT/90 | Final rating |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
        top_table,
        "",
        "The base rating remains "
        "`0.50*vaep_total_p90 + 0.30*vaep_per_touch + 0.20*xt_p90`; "
        "the final hierarchy applies the V4 role-relative minutes reliability "
        "adjustment `minutes/(minutes+300)` to stabilize the 300-minute edge.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_vaep_xt_diagnostics(
    profiles: pd.DataFrame,
    model_bundle: dict[str, object],
    figure_root: Path,
) -> dict[str, str]:
    """Write the required headless-safe VAEP/xT and calibration figures."""

    figure_root.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    scatter_path = figure_root / "vaep_vs_xt_scatter.png"
    figure, axis = plt.subplots(figsize=(10, 7))
    sns.scatterplot(
        data=profiles,
        x="xt_p90",
        y="vaep_total_p90",
        hue="position_group",
        size="minutes",
        sizes=(25, 180),
        alpha=0.75,
        ax=axis,
    )
    axis.set_title("360-Augmented VAEP vs. spatial xT")
    axis.set_xlabel("xT per 90")
    axis.set_ylabel("VAEP total per 90")
    axis.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    figure.tight_layout()
    figure.savefig(scatter_path, dpi=180)
    plt.close(figure)

    calibration_path = figure_root / "calibrated_brier_curve.png"
    truth = np.asarray(model_bundle["test_truth"], dtype=int)
    probability = np.asarray(model_bundle["test_probability"], dtype=float)
    observed, predicted = calibration_curve(
        truth, probability, n_bins=10, strategy="quantile"
    )
    figure, axis = plt.subplots(figsize=(7, 7))
    axis.plot([0, 1], [0, 1], linestyle="--", color="black", label="Perfect")
    axis.plot(predicted, observed, marker="o", label="Selected calibrated VAEP")
    axis.set_title("Calibrated event-probability reliability")
    axis.set_xlabel("Mean predicted probability")
    axis.set_ylabel("Observed event rate")
    axis.legend()
    figure.tight_layout()
    figure.savefig(calibration_path, dpi=180)
    plt.close(figure)

    france_path = figure_root / "france_team_rankings.png"
    france = profiles[profiles["team"].eq("France")].sort_values("team_rank")
    figure, axis = plt.subplots(figsize=(10, 7))
    sns.barplot(
        data=france,
        x="final_player_rating",
        y="player",
        color="#1f77b4",
        ax=axis,
    )
    axis.set_title("France unified VAEP + xT player rankings")
    axis.set_xlabel("Final player rating")
    axis.set_ylabel("")
    figure.tight_layout()
    figure.savefig(france_path, dpi=180)
    plt.close(figure)
    return {
        "vaep_vs_xt_scatter": str(scatter_path),
        "calibrated_brier_curve": str(calibration_path),
        "france_team_rankings": str(france_path),
    }


def run_pipeline(
    project_root: Path = PROJECT_ROOT,
    *,
    model_path: Path = V2_HURDLE,
    staging: bool = True,
    reuse_validated_oof: bool = False,
) -> dict[str, object]:
    """Build V4 OOF audits and player reports in staging or final paths."""

    artifact_root = (
        project_root / "results/v4_staging"
        if staging
        else project_root / "results"
    )
    timer = PipelineTimer(
        log_path=(
            artifact_root / "pipeline_execution_eta.json"
            if staging
            else project_root / "logs/pipeline_execution_eta.json"
        ),
        pipeline="run_team_simulation_reports_v4",
    )
    with timer.stage("load_v4_inputs", total=4, unit="source") as update:
        data = _load_inputs()
        update(1, "events, player metadata, and 360 tables")
        bundle, model_source, model_warning = load_model_bundle(model_path)
        assert bundle is not None
        update(2, "locked v2 classifier")
        matchup = pd.read_csv(
            project_root / "data/processed/lineup_matchup_features_v2.csv"
        )
        update(3, "v2 descriptive matchup features")
        update(4, "validated 360 actor and density context")

    raw = data["recommendations"]
    defensive = data["defensive"].drop_duplicates("possession_uid")
    canonical = (
        raw[raw["is_test_fold"].astype(bool)]
        .drop_duplicates("possession_uid")
        .merge(defensive, on="possession_uid", validate="one_to_one")
    )
    canonical["transition_conceded"] = canonical[
        "opponent_transition_shot"
    ].astype(int)
    canonical["defensive_style"] = canonical["defensive_style"].fillna("Unknown")
    feature_names = list(bundle["feature_names"])
    matchup_join = matchup.drop(
        columns=["match_id", "attacking_team", "defending_team"], errors="ignore"
    )
    canonical = canonical.merge(
        matchup_join, on="possession_uid", validate="one_to_one"
    )
    all_matches = sorted(int(value) for value in canonical["match_id"].unique())
    simulation_dir = artifact_root / "simulations"
    simulation_dir.mkdir(parents=True, exist_ok=True)
    tactical_path = simulation_dir / "tactical_style_simulations_oof.parquet"
    integrity_path = simulation_dir / "oof_fold_integrity.csv"
    if reuse_validated_oof:
        if not tactical_path.exists() or not integrity_path.exists():
            raise FileNotFoundError(
                "--reuse-validated-oof requires existing tactical and integrity artifacts"
            )
        tactical = pd.read_parquet(tactical_path)
        leakage_records = pd.read_csv(integrity_path).to_dict("records")
    else:
        tactical_folds: list[pd.DataFrame] = []
        leakage_records: list[dict[str, object]] = []
        for held_out_match in timer.progress(
            all_matches,
            name="leave_one_match_out_audit",
            total=len(all_matches),
            unit="match",
        ):
            calibration_matches = _calibration_matches_for_fold(
                canonical, held_out_match
            )
            model_train = canonical[
                ~canonical["match_id"].isin(calibration_matches + [held_out_match])
            ].copy()
            calibration = canonical[
                canonical["match_id"].isin(calibration_matches)
            ].copy()
            evaluation = canonical[
                canonical["match_id"].eq(held_out_match)
            ].copy()
            if held_out_match in set(model_train["match_id"]) | set(
                calibration["match_id"]
            ):
                raise RuntimeError(f"OOF leakage detected for match {held_out_match}")

            fold_model = clone(bundle["model"])
            fold_model.fit(
                model_train[feature_names],
                model_train["transition_conceded"].astype(int),
            )
            raw_calibration = fold_model.predict_proba(
                calibration[feature_names]
            )[:, 1]
            fold_calibrator = fit_calibrator(
                raw_calibration,
                calibration["transition_conceded"].to_numpy(dtype=int),
                "platt",
            )
            fold_bundle = dict(bundle)
            fold_bundle.update(
                {
                    "model": fold_model,
                    "calibrator": fold_calibrator,
                    "calibration_method": "platt",
                    "threshold": bundle["threshold"],
                    "feature_defaults": {
                        column: (
                            float(
                                pd.to_numeric(
                                    model_train[column], errors="coerce"
                                ).median()
                            )
                            if column in V2_NUMERIC_FEATURES
                            else str(model_train[column].dropna().mode().iloc[0])
                        )
                        for column in feature_names
                    },
                }
            )
            hurdle = (
                EmpiricalHurdleModel()
                .fit(model_train)
                .attach_transition_bundle(fold_bundle)
            )
            hurdle.fit_physical_adjustments(model_train)
            evaluation["actual_style"] = evaluation["attacking_style"]
            fold_tactical = simulate_tactical_style_outcomes(evaluation, hurdle)
            fold_tactical["oof_fold_match_id"] = held_out_match
            fold_tactical["oof_model_train_matches"] = int(
                model_train["match_id"].nunique()
            )
            fold_tactical["oof_calibration_matches"] = len(calibration_matches)
            fold_tactical["oof_development_match_count"] = (
                int(model_train["match_id"].nunique()) + len(calibration_matches)
            )
            tactical_folds.append(fold_tactical)
            leakage_records.append(
                {
                    "held_out_match": held_out_match,
                    "evaluation_rows": len(evaluation),
                    "model_train_matches": int(model_train["match_id"].nunique()),
                    "calibration_matches": len(calibration_matches),
                    "development_matches": int(model_train["match_id"].nunique())
                    + len(calibration_matches),
                    "heldout_excluded": True,
                }
            )
        tactical = pd.concat(tactical_folds, ignore_index=True)
        tactical.to_parquet(tactical_path, index=False)
        pd.DataFrame(leakage_records).to_csv(integrity_path, index=False)

    actual_probabilities = tactical[
        tactical["simulated_style"].eq(tactical["actual_style"])
    ][
        [
            "possession_uid",
            "calibrated_transition_probability",
            "oof_fold_match_id",
        ]
    ].merge(
        canonical[["possession_uid", "transition_conceded"]],
        on="possession_uid",
        validate="one_to_one",
    )
    truth = actual_probabilities["transition_conceded"].to_numpy(dtype=int)
    probability = actual_probabilities[
        "calibrated_transition_probability"
    ].to_numpy(dtype=float)
    oof_metrics = {
        "rows": len(actual_probabilities),
        "matches": int(actual_probabilities["oof_fold_match_id"].nunique()),
        "teams": int(canonical["team"].nunique()),
        "positives": int(truth.sum()),
        "brier": float(brier_score_loss(truth, probability)),
        "pr_auc": float(average_precision_score(truth, probability)),
        "roc_auc": float(roc_auc_score(truth, probability)),
        "unique_probabilities": int(np.unique(np.round(probability, 12)).size),
    }

    eva_detail, team_summary = calculate_expected_vs_actual_deltas(tactical)
    dominant_reason = (
        eva_detail.groupby(["team", "tactical_reason_code"])
        .size()
        .rename("count")
        .reset_index()
        .sort_values(["team", "count"], ascending=[True, False])
        .drop_duplicates("team")
        [["team", "tactical_reason_code"]]
    )
    team_summary = team_summary.merge(
        dominant_reason, on="team", how="left", validate="one_to_one"
    )
    recurrent = identify_recurrent_tactical_mistakes(eva_detail, defensive)
    audit_dir = artifact_root / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    team_summary.to_csv(
        audit_dir / "expected_vs_actual_team_summary_oof.csv", index=False
    )
    eva_detail.to_parquet(
        audit_dir / "expected_vs_actual_possessions_oof.parquet", index=False
    )
    recurrent.to_csv(
        audit_dir / "recurrent_tactical_mistakes_oof.csv", index=False
    )

    components = data["components"]
    intervals = data["intervals"]
    with timer.stage(
        "v4_player_spatial_evaluation", total=4, unit="layer"
    ) as update:
        (
            v4_profiles,
            heatmap_cells,
            event_value_audit,
            player_provenance,
            vaep_model_bundle,
        ) = build_v4_player_evaluations(
            components,
            data["events"],
            data["frame_actors"],
            data["frame_metrics"],
            legacy_validation_metrics=oof_metrics,
        )
        update(4, "SPADL + xT + calibrated 360-VAEP + unified rankings")
    player_output_dir = (
        artifact_root / "player"
        if staging
        else project_root / "data/processed"
    )
    player_output_dir.mkdir(parents=True, exist_ok=True)
    v4_profiles.to_csv(
        player_output_dir / "player_evaluations.csv", index=False
    )
    heatmap_cells.to_csv(
        player_output_dir / "player_heatmap_cells.csv", index=False
    )
    event_value_audit.to_parquet(
        player_output_dir / "world_cup_spadl_actions.parquet", index=False
    )
    event_value_audit[
        [
            "game_id",
            "original_event_id",
            "player_id",
            "type_name",
            "result_name",
            "scores",
            "concedes",
            "p_scores",
            "p_concedes",
            "vaep_scoring_partition",
            "vaep_value",
            "xt_value",
            "xt_scoring_partition",
            "defenders_within_5",
            "nearest_defender_distance",
            "defensive_density",
            "defenders_behind_ball",
        ]
    ].to_parquet(
        player_output_dir / "player_event_value_audit.parquet",
        index=False,
    )
    (player_output_dir / "player_evaluation_provenance.json").write_text(
        json.dumps(player_provenance, indent=2) + "\n",
        encoding="utf-8",
    )
    reports_root = artifact_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    validation_columns = [
        "model_name",
        "algorithm_type",
        "brier_score",
        "roc_auc",
        "pr_auc",
        "calibration_error",
        "latency_sec",
        "rank_brier",
        "rank_roc_auc",
        "rank_overall",
        "evaluation_scope",
        "rows",
        "selected",
    ]
    final_validation = pd.DataFrame(
        vaep_model_bundle["validation_records"]
    )[validation_columns]
    final_validation.to_csv(
        reports_root / "final_validation.csv", index=False
    )
    model_output = (
        artifact_root / "models/vaep_360_xt.joblib"
        if staging
        else project_root / "models/vaep_360_xt.joblib"
    )
    model_output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vaep_model_bundle, model_output)
    leaderboard = (
        v4_profiles[
            [
                "player",
                "team",
                "position",
                "minutes",
                "vaep_off_p90",
                "vaep_def_p90",
                "vaep_per_touch",
                "xt_p90",
                "final_player_rating",
                "team_rank",
            ]
        ]
        .rename(columns={"player": "player_name"})
        .sort_values(["team", "team_rank", "player_name"])
    )
    leaderboard.to_csv(
        player_output_dir / "player_leaderboard.csv", index=False
    )
    leaderboard.to_csv(
        reports_root / "player_leaderboard.csv", index=False
    )
    leaderboard.to_csv(
        reports_root / "team_player_leaderboards.csv", index=False
    )
    figure_paths = _write_vaep_xt_diagnostics(
        v4_profiles,
        vaep_model_bundle,
        artifact_root / "figures",
    )
    cohort_ids = v4_profiles["player_id"].astype(int).tolist()
    all_profiles = derive_physicality_metrics(components)
    new_profile_columns = [
        "player_id",
        "player_evaluation_score",
        "final_player_rating",
        "vaep_total_p90",
        "vaep_per_touch",
        "xt_p90",
        "final_third_share",
    ]
    simulation_profiles = all_profiles.merge(
        v4_profiles[new_profile_columns],
        on="player_id",
        how="left",
        validate="one_to_one",
    )
    simulation_profiles["player_evaluation_score"] = simulation_profiles[
        "player_evaluation_score"
    ].fillna(0.0)
    full_synergy = compute_player_synergy_matrix(
        components,
        data["events"],
        intervals,
        all_profiles["player_id"].astype(int).tolist(),
    )
    cohort_synergy = full_synergy[
        full_synergy["row_player_id"].isin(cohort_ids)
        & full_synergy["column_player_id"].isin(cohort_ids)
    ].copy()
    full_hurdle = (
        EmpiricalHurdleModel().fit(canonical).attach_transition_bundle(bundle)
    )
    full_hurdle.fit_physical_adjustments(canonical)
    with timer.stage("reason_coded_substitutions", total=32, unit="team") as update:
        substitutions, optimized, suppressions = (
            simulate_starter_replacement_impact(
                components, simulation_profiles, full_synergy, full_hurdle
            )
        )
        update(32)
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
        simulation_dir / "substitution_optimization.parquet", index=False
    )
    suppressions.to_parquet(
        simulation_dir / "substitution_suppressions.parquet", index=False
    )
    optimized.to_csv(
        simulation_dir / "optimized_starting_lineups.csv", index=False
    )

    metadata = {
        "schema_version": 4,
        "model_version": bundle["model_version"],
        "target": bundle["target"],
        "calibration_method": bundle["calibration_method"],
        "threshold": bundle["threshold"],
        "threshold_status": bundle["threshold_status"],
        "holdout_metrics": bundle["holdout_metrics"],
        "oof_metrics": oof_metrics,
        "oof_provenance": "64-match leave-one-match-out; held-out match excluded",
        "player_evaluation": player_provenance,
    }
    heatmap_count = generate_player_heatmap_svgs(
        v4_profiles,
        heatmap_cells,
        reports_root / "heatmaps",
        clear_existing=True,
    )
    player_report_count = generate_individual_starter_reports(
        v4_profiles,
        cohort_synergy,
        reports_root / "starters",
        clear_existing=True,
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
        profiles=v4_profiles,
        suppression_reasons=suppressions,
        clear_existing=True,
    )
    compiled_checks = compile_v4_report_packets(
        reports_root / "teams",
        reports_root / "starters",
        reports_root / "compiled",
    )
    summary_path = (
        artifact_root / "Summary/v4_model_explanation_summary.md"
        if staging
        else project_root
        / "results/Summary/v4_model_explanation_summary.md"
    )
    _write_v4_model_summary(
        summary_path,
        provenance=player_provenance,
        profiles=v4_profiles,
        oof_metrics=oof_metrics,
        compiled_checks=compiled_checks,
    )
    checks = {
        "all_64_matches_oof": len(leakage_records) == 64,
        "all_32_teams_audited": len(team_summary) == 32,
        "heldout_excluded_every_fold": all(
            bool(record["heldout_excluded"]) for record in leakage_records
        ),
        "development_uses_63_matches": all(
            int(record["development_matches"]) == 63
            for record in leakage_records
        ),
        "canonical_target": bundle["target"] == "transition_conceded",
        "substitution_floor": substitutions.empty
        or bool(
            substitutions["expected_net_xg_gain"].gt(0.005).all()
            and substitutions["gain_ci_low"].gt(0).all()
        ),
        "suppression_reason_coverage": not suppressions.empty
        and bool(suppressions["reason_code"].notna().all()),
        "team_reports": team_count == 32,
        "minutes_cutoff": bool(v4_profiles["minutes"].ge(300).all()),
        "fullback_role_safeguard": not bool(
            v4_profiles.loc[
                v4_profiles["position_group"].eq("Fullback/Wingback"),
                "functional_role",
            ]
            .eq("Holding Anchor")
            .any()
        ),
        "attacking_wingback_threshold": bool(
            v4_profiles.loc[
                v4_profiles["position_group"].eq("Fullback/Wingback")
                & v4_profiles["final_third_share"].gt(0.35),
                "functional_role",
            ]
            .eq("Attacking Wingback")
            .all()
        ),
        "heatmaps": heatmap_count == len(v4_profiles),
        "player_reports": player_report_count == len(v4_profiles),
        "compiled_reports": compiled_checks["markdown_files"] == 64,
        "summary": summary_path.is_file(),
        "final_validation": (
            reports_root / "final_validation.csv"
        ).is_file(),
        "diagnostic_figures": all(Path(path).is_file() for path in figure_paths.values()),
        "mbappe_france_top_two": bool(
            v4_profiles.loc[
                v4_profiles["player"].str.contains("Mbapp", case=False, na=False)
                & v4_profiles["team"].eq("France"),
                "team_rank",
            ].le(2).all()
        ),
        "messi_argentina_first": bool(
            v4_profiles.loc[
                v4_profiles["player"].str.contains("Messi", case=False, na=False)
                & v4_profiles["team"].eq("Argentina"),
                "team_rank",
            ].eq(1).all()
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(
            "V4 pipeline checks failed: "
            + ", ".join(name for name, passed in checks.items() if not passed)
        )
    manifest = {
        "schema_version": 4,
        "status": "complete",
        "model_source": model_source,
        "model_warning": model_warning,
        "model_version": bundle["model_version"],
        "target": bundle["target"],
        "calibration_method": bundle["calibration_method"],
        "threshold": bundle["threshold"],
        "threshold_status": bundle["threshold_status"],
        "locked_v2_holdout_metrics": bundle["holdout_metrics"],
        "tournament_oof_metrics": oof_metrics,
        "player_evaluation_provenance": player_provenance,
        "vaep_xt_model": {
            "artifact": str(model_output),
            "selected_model": vaep_model_bundle["selected_model_name"],
            "selected_algorithm": vaep_model_bundle["selected_algorithm"],
            "calibration_method": vaep_model_bundle["calibration_method"],
            "validation": final_validation.iloc[0].to_dict(),
            "diagnostic_figures": figure_paths,
        },
        "fold_assignment_hash": bundle["fold_assignment_hash"],
        "counts": {
            "oof_matches": 64,
            "oof_teams": 32,
            "oof_possessions": len(canonical),
            "tactical_scenarios": len(tactical),
            "eligible_substitutions": len(substitutions),
            "suppressed_substitutions": len(suppressions),
            "team_reports": team_count,
            "eligible_player_evaluations": len(v4_profiles),
            "player_heatmaps": heatmap_count,
            "compiled_reports": compiled_checks["markdown_files"],
        },
        "checks": checks,
        "runtime": timer.summary(),
    }
    manifest_path = reports_root / "pipeline_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if not staging:
        from generate_final_tournament_report import generate_report

        final_report = (
            project_root
            / "results/reports/final/world_cup_team_performance_and_top_players.md"
        )
        generate_report(project_root, final_report)
        prospective_validation = (
            project_root
            / "results/reports/prospective_model_validation.csv"
        )
        if prospective_validation.is_file():
            refresh_prospective_validation_reporting(
                project_root, prospective_validation
            )
        player_role_validation = (
            project_root
            / "results/reports/player_role_challenger_validation.json"
        )
        if player_role_validation.is_file():
            refresh_player_role_validation_reporting(
                project_root, player_role_validation
            )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING"],
        default="INFO",
    )
    parser.add_argument(
        "--staging",
        action="store_true",
        help="Write to the isolated V4 staging paths instead of production.",
    )
    parser.add_argument(
        "--reuse-validated-oof",
        action="store_true",
        help="Reuse existing leakage-audited 64-match tactical OOF artifacts.",
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
        manifest = run_pipeline(
            staging=args.staging,
            reuse_validated_oof=args.reuse_validated_oof,
        )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
