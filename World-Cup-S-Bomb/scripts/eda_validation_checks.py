"""Acceptance and regression tests for the consolidated V4 football pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import kendalltau

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import generate_final_tournament_report as baseline_report  # noqa: E402
from benchmark_coaching_models_v2 import predict_bundle_probability  # noqa: E402
from src.report_generators import load_prospective_validation  # noqa: E402

DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "eda_validation_report.json"
ORIGINAL_FILES = [
    PROJECT_ROOT / "scripts/run_team_simulation_reports.py",
    PROJECT_ROOT / "src/simulation_engine.py",
    PROJECT_ROOT / "scripts/benchmark_coaching_models.py",
    PROJECT_ROOT / "scripts/generate_final_tournament_report.py",
    PROJECT_ROOT / "src/report_generators.py",
]


def calculate_variance_ratio(
    frame: pd.DataFrame,
    *,
    value_column: str = "vaep_total_p90",
    minute_cutoff: float = 300.0,
) -> float:
    """Calculate substitute-to-starter variance for a player value."""

    substitutes = frame.loc[frame["minutes"].lt(minute_cutoff), value_column]
    starters = frame.loc[frame["minutes"].ge(minute_cutoff), value_column]
    starter_variance = float(starters.var(ddof=1))
    if not np.isfinite(starter_variance) or starter_variance <= 0:
        return float("nan")
    return float(substitutes.var(ddof=1) / starter_variance)


def top_ten_kendall_tau(
    baseline: pd.DataFrame,
    updated: pd.DataFrame,
) -> dict[str, float]:
    """Compare position-specific top tens using union-rank Kendall tau."""

    results: dict[str, float] = {}
    for position in sorted(set(baseline["position_group"]) & set(updated["position_group"])):
        before = baseline[baseline["position_group"].eq(position)].nlargest(
            10, "position_score"
        )["player_id"].astype(int).tolist()
        after = updated[updated["position_group"].eq(position)].nlargest(
            10, "position_score"
        )["player_id"].astype(int).tolist()
        players = sorted(set(before) | set(after))
        before_rank = {player: rank for rank, player in enumerate(before, start=1)}
        after_rank = {player: rank for rank, player in enumerate(after, start=1)}
        fallback = 11
        statistic = kendalltau(
            [before_rank.get(player, fallback) for player in players],
            [after_rank.get(player, fallback) for player in players],
            variant="b",
        ).statistic
        results[position] = 0.0 if pd.isna(statistic) else float(statistic)
    return results


def prediction_variance_checks(predictions: pd.DataFrame) -> dict[str, Any]:
    """Fail a fold when calibrated probabilities collapse to one value."""

    fold_results: dict[str, Any] = {}
    for fold, frame in predictions.groupby("fold", dropna=False):
        probabilities = frame["calibrated_probability"].to_numpy(dtype=float)
        unique = int(np.unique(np.round(probabilities, 12)).size)
        fold_results[str(fold)] = {
            "rows": int(len(frame)),
            "unique_probabilities": unique,
            "variance": float(np.var(probabilities)),
            "predicted_positive_rate": float(frame["predicted_positive"].mean()),
            "predicted_positives": int(frame["predicted_positive"].sum()),
            "passed": unique > 1 and float(np.var(probabilities)) > 0,
        }
    return fold_results


def artifact_regression_test(
    bundle_path: Path,
    features_path: Path,
) -> dict[str, Any]:
    """Check loading, schema, probability bounds, replay, and split isolation."""

    bundle = joblib.load(bundle_path)
    required = {
        "schema_version",
        "feature_names",
        "model",
        "calibrator",
        "split_matches",
        "replay_sample",
        "replay_probabilities",
    }
    missing = sorted(required - set(bundle))
    features = pd.read_csv(features_path, nrows=50, low_memory=False)
    missing_features = set(bundle.get("feature_names", [])) - set(features)
    schema_compatible = not bool(
        missing_features - set(bundle.get("feature_defaults", {}))
    )
    replay_frame = pd.DataFrame(bundle["replay_sample"])
    replay = predict_bundle_probability(bundle, replay_frame)
    expected = np.asarray(bundle["replay_probabilities"], dtype=float)
    split_sets = {
        name: set(values) for name, values in bundle["split_matches"].items()
    }
    names = list(split_sets)
    disjoint = not any(
        split_sets[names[left]] & split_sets[names[right]]
        for left in range(len(names))
        for right in range(left + 1, len(names))
    )
    return {
        "missing_bundle_keys": missing,
        "schema_compatible": schema_compatible,
        "probability_bounds": bool(((replay >= 0) & (replay <= 1)).all()),
        "replay_exact": bool(np.allclose(replay, expected, atol=1e-12)),
        "match_splits_disjoint": disjoint,
        "partition_match_counts": {
            name: len(values) for name, values in split_sets.items()
        },
        "passed": (
            not missing
            and schema_compatible
            and bool(((replay >= 0) & (replay <= 1)).all())
            and bool(np.allclose(replay, expected, atol=1e-12))
            and disjoint
        ),
    }


def sha256(path: Path) -> str:
    """Hash a source file for no-overwrite provenance."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_validation_v2(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Run all objective v2 acceptance checks."""

    raw_profiles = pd.read_csv(
        project_root / "data/processed/player_physicality_profiles_v2.csv"
    )
    updated_profiles = pd.read_csv(
        project_root / "data/processed/player_physicality_profiles_smoothed_v2.csv"
    )
    baseline_profiles = baseline_report.add_position_scores(
        raw_profiles,
        weights_by_position=baseline_report.BASELINE_POSITION_WEIGHTS,
    )
    variance_before = calculate_variance_ratio(raw_profiles)
    variance_after = calculate_variance_ratio(updated_profiles)
    taus = top_ten_kendall_tau(baseline_profiles, updated_profiles)
    mean_tau = float(np.mean(list(taus.values())))

    predictions_path = (
        project_root
        / "data/interim/world_cup_coaching_model_predictions_v2.csv"
    )
    predictions = pd.read_csv(predictions_path)
    prediction_checks = prediction_variance_checks(predictions)
    artifact = artifact_regression_test(
        project_root / "models/coaching_model_benchmark_v2.joblib",
        project_root / "data/processed/world_cup_recommendation_features.csv",
    )
    bundle = joblib.load(
        project_root / "models/coaching_model_benchmark_v2.joblib"
    )
    substitutions = pd.read_parquet(
        project_root
        / "results/simulations/v2/substitution_optimization_v2.parquet"
    )
    substitution_pass = substitutions.empty or bool(
        substitutions["expected_net_xg_gain"].gt(0.005).all()
        and substitutions["gain_ci_low"].gt(0).all()
    )
    eta_path = project_root / "logs/pipeline_execution_eta.json"
    eta_payload = json.loads(eta_path.read_text(encoding="utf-8"))
    runtime_pass = bool(eta_payload.get("stages")) and eta_payload.get(
        "elapsed_seconds", 0
    ) >= 0
    threshold_pass = (
        bundle.get("threshold_status") == "no validated threshold"
        or (
            bundle.get("threshold") is not None
            and bundle.get("holdout_metrics", {}).get("precision", 0) >= 0.30
        )
    )
    gates = {
        "runtime_eta_tracking": runtime_pass,
        "data_integrity": artifact["match_splits_disjoint"],
        "smoothing_variance_ratio": bool(
            np.isfinite(variance_after)
            and abs(variance_after - 1.0) < abs(variance_before - 1.0)
            and 0.5 <= variance_after <= 1.5
        ),
        "rank_correlation": min(taus.values()) >= 0.60,
        "prediction_variance": all(
            result["passed"] for result in prediction_checks.values()
        ),
        "threshold_validation_or_abstention": threshold_pass,
        "counterfactual_floor": substitution_pass,
        "artifact_loading_and_replay": artifact["passed"],
    }
    return {
        "schema_version": 1,
        "status": "PASS" if all(gates.values()) else "FAIL",
        "gates": gates,
        "smoothing": {
            "variance_ratio_before": variance_before,
            "variance_ratio_after": variance_after,
            "target": "approximately 1.0",
        },
        "rank_correlation": {
            "kendall_tau_by_position": taus,
            "mean_kendall_tau": mean_tau,
            "minimum_position_kendall_tau": float(min(taus.values())),
            "minimum_required": 0.60,
        },
        "prediction_variance": prediction_checks,
        "threshold": {
            "status": bundle.get("threshold_status"),
            "threshold": bundle.get("threshold"),
            "candidate_threshold": bundle.get("candidate_threshold"),
            "holdout_metrics": bundle.get("holdout_metrics"),
        },
        "counterfactuals": {
            "eligible_substitutions": int(len(substitutions)),
            "minimum_gain": (
                None
                if substitutions.empty
                else float(substitutions["expected_net_xg_gain"].min())
            ),
            "minimum_ci_low": (
                None if substitutions.empty else float(substitutions["gain_ci_low"].min())
            ),
        },
        "artifact_regression": artifact,
        "runtime_eta": eta_payload,
        "original_source_hashes": {
            str(path.relative_to(project_root)): sha256(path)
            for path in ORIGINAL_FILES
        },
    }


def _report_metrics(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    dynamic_lines = [
        line for line in text.splitlines() if line.startswith("**Dynamic tactical summary:**")
    ]
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "words": len(text.split()),
        "nan_count": len(re.findall(r"\bnan\b", text, flags=re.IGNORECASE)),
        "team_sections": len(re.findall(r"^## .+ \([A-Z]{3}\)$", text, flags=re.MULTILINE)),
        "dynamic_summary_count": len(dynamic_lines),
        "unique_dynamic_summaries": len(set(dynamic_lines)),
        "reason_code_mentions": len(
            re.findall(
                r"GAIN_BELOW_THRESHOLD|CONFIDENCE_INTERVAL_OVERLAPS_ZERO|"
                r"CLASSIFIER_ABSTAINED|POSITIONAL_INCOMPATIBILITY",
                text,
            )
        ),
        "no_substitution_callouts": text.count(
            "No bench substitution met the +0.0050 Net xG floor"
        ),
    }


def run_validation(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Compare v1/v2/v3 and enforce strict tournament-wide v3 gates."""

    v1_report = _report_metrics(
        project_root
        / "results/reports/final/world_cup_team_performance_and_top_players.md"
    )
    v2_report = _report_metrics(
        project_root
        / "results/reports/final_v2/world_cup_team_performance_and_top_players_v2.md"
    )
    v3_report = _report_metrics(
        project_root
        / "results/reports/final_v3/world_cup_team_performance_and_top_players_v3.md"
    )
    raw_profiles = pd.read_csv(
        project_root / "data/processed/player_physicality_profiles_v2.csv"
    )
    v3_profiles = pd.read_csv(
        project_root / "data/processed/player_physicality_profiles_smoothed_v3.csv"
    )
    baseline_profiles = baseline_report.add_position_scores(
        raw_profiles,
        weights_by_position=baseline_report.BASELINE_POSITION_WEIGHTS,
    )
    variance_before = calculate_variance_ratio(raw_profiles)
    variance_after = calculate_variance_ratio(v3_profiles)
    taus = top_ten_kendall_tau(baseline_profiles, v3_profiles)

    audit = pd.read_csv(
        project_root
        / "results/audit/v3/expected_vs_actual_team_summary_oof_v3.csv"
    )
    integrity = pd.read_csv(
        project_root / "results/simulations/v3/oof_fold_integrity_v3.csv"
    )
    substitutions = pd.read_parquet(
        project_root
        / "results/simulations/v3/substitution_optimization_v3.parquet"
    )
    suppressions = pd.read_parquet(
        project_root
        / "results/simulations/v3/substitution_suppressions_v3.parquet"
    )
    manifest = json.loads(
        (
            project_root / "results/reports/v3/pipeline_manifest_v3.json"
        ).read_text(encoding="utf-8")
    )
    v2_validation = json.loads(
        (
            project_root / "results/eda_validation_report_v2.json"
        ).read_text(encoding="utf-8")
    )
    bundle = joblib.load(
        project_root / "models/coaching_model_benchmark_v2.joblib"
    )
    artifact = artifact_regression_test(
        project_root / "models/coaching_model_benchmark_v2.joblib",
        project_root / "data/processed/world_cup_recommendation_features.csv",
    )
    eta = json.loads(
        (
            project_root / "logs/pipeline_execution_eta_v3.json"
        ).read_text(encoding="utf-8")
    )
    teams_without_substitution = 32 - int(
        substitutions["team"].nunique() if not substitutions.empty else 0
    )
    tactical_reason_coverage = (
        len(audit) == 32
        and audit["tactical_reason_code"].notna().all()
    )
    suppression_reason_coverage = (
        not suppressions.empty and suppressions["reason_code"].notna().all()
    )
    statistical_safety = substitutions.empty or bool(
        substitutions["expected_net_xg_gain"].gt(0.005).all()
        and substitutions["gain_ci_low"].gt(0).all()
    )
    v2_metrics_preserved = (
        v2_validation.get("status") == "PASS"
        and manifest["locked_v2_holdout_metrics"] == bundle["holdout_metrics"]
    )
    gates = {
        "zero_nans": v3_report["nan_count"] == 0,
        "complete_oof_team_coverage": (
            len(audit) == 32
            and v3_report["team_sections"] == 32
            and not audit[
                [
                    "total_wasted_net_xg",
                    "mean_eva_gap",
                    "actual_expected_net_xg",
                    "optimal_expected_net_xg",
                ]
            ].isna().any().any()
        ),
        "all_64_matches_leakage_safe": (
            len(integrity) == 64
            and integrity["heldout_excluded"].astype(bool).all()
            and integrity["development_matches"].eq(63).all()
        ),
        "no_silent_suppressions": (
            tactical_reason_coverage
            and suppression_reason_coverage
            and v3_report["no_substitution_callouts"] == teams_without_substitution
        ),
        "dynamic_summary_integration": (
            v3_report["dynamic_summary_count"] == 32
            and v3_report["unique_dynamic_summaries"] == 32
        ),
        "statistical_safety": statistical_safety,
        "v2_metrics_preserved": v2_metrics_preserved,
        "smoothing_variance_ratio": (
            np.isfinite(variance_after) and 0.5 <= variance_after <= 1.5
        ),
        "rank_stability_every_position": min(taus.values()) >= 0.60,
        "artifact_loading_and_replay": artifact["passed"],
        "runtime_eta_tracking": bool(eta.get("stages")),
    }
    return {
        "schema_version": 3,
        "status": "PASS" if all(gates.values()) else "FAIL",
        "gates": gates,
        "report_comparison": {"v1": v1_report, "v2": v2_report, "v3": v3_report},
        "coverage": {
            "oof_matches": int(len(integrity)),
            "oof_teams": int(len(audit)),
            "oof_possessions": manifest["counts"]["oof_possessions"],
            "heldout_excluded_all_folds": bool(
                integrity["heldout_excluded"].astype(bool).all()
            ),
        },
        "reason_codes": {
            "tactical_team_coverage": int(
                audit["tactical_reason_code"].notna().sum()
            ),
            "suppressed_substitution_rows": int(len(suppressions)),
            "suppression_rows_with_reason": int(
                suppressions["reason_code"].notna().sum()
            ),
            "teams_without_validated_substitution": teams_without_substitution,
            "report_no_substitution_callouts": v3_report[
                "no_substitution_callouts"
            ],
            "reason_distribution": suppressions["reason_code"].value_counts().to_dict(),
        },
        "preserved_v2_metrics": {
            "v2_validation_status": v2_validation.get("status"),
            "holdout_metrics_equal": (
                manifest["locked_v2_holdout_metrics"]
                == bundle["holdout_metrics"]
            ),
            "holdout_metrics": bundle["holdout_metrics"],
            "variance_ratio_v3": variance_after,
            "kendall_tau_by_position_v3": taus,
        },
        "v3_oof_metrics": manifest["tournament_oof_metrics"],
        "counterfactuals": {
            "eligible_substitutions": int(len(substitutions)),
            "minimum_gain": (
                None
                if substitutions.empty
                else float(substitutions["expected_net_xg_gain"].min())
            ),
            "minimum_ci_low": (
                None if substitutions.empty else float(substitutions["gain_ci_low"].min())
            ),
        },
        "artifact_regression": artifact,
        "runtime_eta": eta,
    }


def run_v4_validation(
    project_root: Path = PROJECT_ROOT,
    *,
    staging: bool,
) -> dict[str, Any]:
    """Validate V4 rankings, spatial joins, reports, and locked V3 safeguards."""

    artifact_root = (
        project_root / "results/v4_staging"
        if staging
        else project_root / "results"
    )
    player_root = (
        artifact_root / "player"
        if staging
        else project_root / "data/processed"
    )
    report_root = artifact_root / "reports"
    profiles = pd.read_csv(player_root / "player_evaluations.csv")
    heatmap_cells = pd.read_csv(
        player_root / "player_heatmap_cells.csv"
    )
    event_values = pd.read_parquet(
        player_root / "player_event_value_audit.parquet"
    )
    provenance = json.loads(
        (
            player_root / "player_evaluation_provenance.json"
        ).read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (report_root / "pipeline_manifest.json").read_text(encoding="utf-8")
    )
    integrity = pd.read_csv(
        artifact_root / "simulations/oof_fold_integrity.csv"
    )
    audit = pd.read_csv(
        artifact_root / "audit/expected_vs_actual_team_summary_oof.csv"
    )
    substitutions = pd.read_parquet(
        artifact_root / "simulations/substitution_optimization.parquet"
    )
    suppressions = pd.read_parquet(
        artifact_root / "simulations/substitution_suppressions.parquet"
    )
    summary_path = (
        artifact_root / "Summary/v4_model_explanation_summary.md"
        if staging
        else project_root
        / "results/Summary/v4_model_explanation_summary.md"
    )
    summary = summary_path.read_text(encoding="utf-8")
    compiled_files = sorted((report_root / "compiled").glob("*.md"))
    compiled_text = "\n".join(
        path.read_text(encoding="utf-8") for path in compiled_files
    )
    heatmaps = list((report_root / "heatmaps").glob("*/*_heatmap.svg"))

    required_metrics = [
        "minutes",
        "vaep_off_p90",
        "vaep_def_p90",
        "vaep_total_p90",
        "vaep_per_touch",
        "xt_p90",
        "final_player_rating",
        "team_rank",
        "final_third_share",
    ]
    no_metric_nan = not profiles[required_metrics].isna().any().any()
    no_report_nan = re.search(
        r"(?i)(?<![A-Za-z])nan(?![A-Za-z])", compiled_text
    ) is None
    under_300 = profiles["minutes"].lt(300)
    fullbacks = profiles["position_group"].eq("Fullback/Wingback")
    high_fullbacks = fullbacks & profiles["final_third_share"].gt(0.35)
    target_players = profiles[
        profiles["player"].str.contains(
            "Hakimi|Dest|Mbapp|Giroud|Kolo", case=False, na=False
        )
    ]
    protected_wide_players = target_players[
        target_players["player"].str.contains(
            "Hakimi|Dest", case=False, na=False
        )
    ]
    mbappe = profiles[
        profiles["player"].str.contains("Mbapp", case=False, na=False)
    ]
    giroud = profiles[
        profiles["player"].str.contains("Giroud", case=False, na=False)
    ]
    kolo = profiles[
        profiles["player"].str.contains("Kolo", case=False, na=False)
    ]

    required_event_value_columns = {
        "original_event_id",
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
    }
    event_value_schema = required_event_value_columns.issubset(event_values.columns)
    frame_matches = int(
        pd.read_csv(
            project_root
            / "data/interim/world_cup_360_frame_metrics.csv",
            usecols=["match_id"],
        )["match_id"].nunique()
    )
    bundle = joblib.load(
        project_root / "models/coaching_model_benchmark_v2.joblib"
    )
    artifact = artifact_regression_test(
        project_root / "models/coaching_model_benchmark_v2.joblib",
        project_root
        / "data/processed/world_cup_recommendation_features.csv",
    )
    vaep_bundle_path = project_root / "models/vaep_360_xt.joblib"
    vaep_bundle = joblib.load(vaep_bundle_path)
    final_validation = pd.read_csv(report_root / "final_validation.csv")
    selected_validation = final_validation.sort_values("rank_overall").iloc[0]
    prospective_validation = load_prospective_validation(
        report_root / "prospective_model_validation.csv"
    )
    vaep_artifact = {
        "schema_compatible": {
            "schema_version",
            "selected_model_name",
            "score_model",
            "concede_model",
            "feature_names",
            "xt_grid",
            "test_truth",
            "test_probability",
        }.issubset(vaep_bundle),
        "probability_bounds": bool(
            np.asarray(vaep_bundle["test_probability"]).min() >= 0
            and np.asarray(vaep_bundle["test_probability"]).max() <= 1
        ),
        "xt_shape": list(np.asarray(vaep_bundle["xt_grid"]).shape) == [12, 16],
    }
    substitution_safety = substitutions.empty or bool(
        substitutions["expected_net_xg_gain"].gt(0.005).all()
        and substitutions["gain_ci_low"].gt(0).all()
    )
    gates = {
        "zero_nans": bool(no_metric_nan and no_report_nan),
        "complete_oof_team_coverage": bool(
            len(audit) == 32
            and manifest["counts"]["oof_teams"] == 32
            and manifest["counts"]["oof_matches"] == 64
        ),
        "all_64_matches_leakage_safe": bool(
            len(integrity) == 64
            and integrity["heldout_excluded"].astype(bool).all()
            and integrity["development_matches"].eq(63).all()
        ),
        "minutes_cutoff": bool(
            not under_300.any()
            and kolo.empty
            and profiles["minutes"].min() >= 300
        ),
        "fullback_spatial_roles": bool(
            len(protected_wide_players) == 2
            and not protected_wide_players["functional_role"]
            .eq("Holding Anchor")
            .any()
            and not profiles.loc[fullbacks, "functional_role"]
            .eq("Holding Anchor")
            .any()
            and profiles.loc[
                high_fullbacks, "functional_role"
            ].eq("Attacking Wingback").all()
        ),
        "mbappe_france_top_two": bool(
            len(mbappe) == 1 and int(mbappe.iloc[0]["team_rank"]) <= 2
        ),
        "messi_argentina_first": bool(
            len(
                profiles[
                    profiles["player"].str.contains(
                        "Messi", case=False, na=False
                    )
                    & profiles["team"].eq("Argentina")
                    & profiles["team_rank"].eq(1)
                ]
            )
            == 1
        ),
        "unified_rating_formula": bool(
            "raw_final_player_rating" in profiles
            and "rating_minutes_reliability" in profiles
            and np.allclose(
                profiles["raw_final_player_rating"],
                0.50 * profiles["vaep_total_p90"]
                + 0.30 * profiles["vaep_per_touch"]
                + 0.20 * profiles["xt_p90"],
                rtol=0,
                atol=1e-12,
            )
            and np.allclose(
                profiles["rating_minutes_reliability"],
                profiles["minutes"] / (profiles["minutes"] + 450.0),
                rtol=0,
                atol=1e-12,
            )
            and np.allclose(
                profiles["final_player_rating"],
                profiles["rating_minutes_reliability"]
                * profiles["raw_final_player_rating"]
                + (1.0 - profiles["rating_minutes_reliability"])
                * profiles.groupby("position_group")[
                    "raw_final_player_rating"
                ].transform("mean"),
                rtol=0,
                atol=1e-12,
            )
        ),
        "all_player_actions_cross_fitted": bool(
            event_values["p_scores"].notna().all()
            and event_values["p_concedes"].notna().all()
            and event_values["vaep_scoring_partition"]
            .isin({"development_oof", "untouched_test"})
            .all()
            and event_values["xt_scoring_partition"]
            .str.match(r"^(development_oof_fold_\d+|untouched_test)$")
            .all()
        ),
        "legacy_unshrunk_formula_removed": bool(
            not np.allclose(
                profiles["final_player_rating"],
                0.50 * profiles["vaep_total_p90"]
                + 0.30 * profiles["vaep_per_touch"]
                + 0.20 * profiles["xt_p90"],
                rtol=0,
                atol=1e-12,
            )
        ),
        "pre_action_feature_contract": bool(
            provenance["target_window_offsets"] == [1, 2, 3]
            and provenance["pre_action_features_only"]
            and provenance["test_used_for_model_selection"] is False
            and provenance["xt_cross_fitted_by_match"]
            and not {
                "end_x",
                "end_y",
                "successful_action",
                "shot_xg",
                "result",
            }.intersection(provenance["vaep_feature_names"])
        ),
        "legacy_base_formula_reconstructs_raw": bool(
            np.allclose(
                profiles["raw_final_player_rating"],
                0.50 * profiles["vaep_total_p90"]
                + 0.30 * profiles["vaep_per_touch"]
                + 0.20 * profiles["xt_p90"],
                rtol=0,
                atol=1e-12,
            )
        ),
        "event_value_schema": bool(event_value_schema),
        "sb360_spatial_coverage": bool(
            frame_matches == 64
            and provenance["freeze_frame_actor_points"] > 0
            and provenance["events_with_360_context"]
            / provenance["event_rows"]
            >= 0.80
            and heatmap_cells["player_id"].nunique() == len(profiles)
        ),
        "vaep_xt_provenance_explicit": bool(
            provenance["valuation_system"]
            == "360-Augmented VAEP and xT (applied concurrently)"
            and provenance["original_event_id_preserved"]
            and provenance["xt_not_in_vaep_features"]
        ),
        "vaep_metric_targets": bool(
            float(selected_validation["brier_score"]) < 0.12
            and float(selected_validation["roc_auc"]) > 0.82
        ),
        "vaep_artifact": bool(all(vaep_artifact.values())),
        "prospective_harm_prevention": bool(
            prospective_validation is not None
            and prospective_validation["overall_status"]
            == "PARTIAL_PASS_ROLLBACK"
            and prospective_validation["artifact_written"] is False
            and prospective_validation["targets"]["box_entry"]["status"]
            == "PASSED"
            and prospective_validation["targets"]["shot"]["status"]
            == "REJECTED"
        ),
        "compiled_reports_in_place": bool(
            len(compiled_files) == 64
            and not any("_v4" in path.name.lower() for path in compiled_files)
            and "Unified 360-VAEP + xT player leaders" in compiled_text
            and compiled_text.count("PROSPECTIVE_VALIDATION_START") == 64
        ),
        "heatmaps_complete": len(heatmaps) == len(profiles),
        "summary_complete": bool(
            "## V4 Model Explanations" in summary
            and "StatsBomb 360" in summary
            and "360-Augmented VAEP and xT" in summary
            and "final_validation.csv" in summary
            and "freeze-frame snapshots, not continuous" in summary
            and "## Known limitations" in summary
        ),
        "counterfactual_safety": bool(
            substitution_safety
            and not suppressions.empty
            and suppressions["reason_code"].notna().all()
        ),
        "locked_classifier_preserved": bool(
            manifest["locked_v2_holdout_metrics"]
            == bundle["holdout_metrics"]
            and artifact["passed"]
        ),
    }
    return {
        "schema_version": 4,
        "status": "PASS" if all(gates.values()) else "FAIL",
        "staging": staging,
        "gates": gates,
        "player_metrics": {
            "players_before_cutoff": provenance["players_before_cutoff"],
            "eligible_players": len(profiles),
            "players_dropped": provenance["players_dropped"],
            "minimum_minutes": float(profiles["minutes"].min()),
            "functional_roles": profiles["Functional role"].value_counts().to_dict(),
            "attacking_wingbacks": int(
                profiles["functional_role"].eq("Attacking Wingback").sum()
            ),
            "valuation_system": provenance["valuation_system"],
            "mbappe_team_rank": int(mbappe.iloc[0]["team_rank"]),
            "mbappe_final_player_rating": float(
                mbappe.iloc[0]["final_player_rating"]
            ),
            "giroud_final_player_rating": float(
                giroud.iloc[0]["final_player_rating"]
            ),
            "hakimi_role": str(
                protected_wide_players[
                    protected_wide_players["player"].str.contains(
                        "Hakimi", case=False
                    )
                ].iloc[0]["functional_role"]
            ),
            "dest_role": str(
                protected_wide_players[
                    protected_wide_players["player"].str.contains(
                        "Dest", case=False
                    )
                ].iloc[0]["functional_role"]
            ),
            "france_top_three": profiles[
                profiles["team"].eq("France")
            ].nsmallest(3, "team_rank")[
                ["player", "team_rank", "final_player_rating"]
            ].to_dict("records"),
            "argentina_top_three": profiles[
                profiles["team"].eq("Argentina")
            ].nsmallest(3, "team_rank")[
                ["player", "team_rank", "final_player_rating"]
            ].to_dict("records"),
        },
        "spatial_metrics": {
            "sb360_matches": frame_matches,
            "successful_action_points": provenance[
                "successful_action_points"
            ],
            "freeze_frame_actor_points": provenance[
                "freeze_frame_actor_points"
            ],
            "events_with_360_context": provenance[
                "events_with_360_context"
            ],
            "heatmaps": len(heatmaps),
        },
        "model_metrics": {
            "legacy_transition": manifest["tournament_oof_metrics"],
            "vaep_selected": selected_validation.to_dict(),
            "prospective_possession_challenger": prospective_validation,
        },
        "report_metrics": {
            "compiled_files": len(compiled_files),
            "team_reports": len(
                list(
                    (report_root / "compiled").glob(
                        "*_team_coaching_report.md"
                    )
                )
            ),
            "player_packets": len(
                list(
                    (report_root / "compiled").glob(
                        "*_compiled_player_reports.md"
                    )
                )
            ),
            "nan_tokens": len(
                re.findall(
                    r"(?i)(?<![A-Za-z])nan(?![A-Za-z])",
                    compiled_text,
                )
            ),
        },
        "counterfactuals": {
            "eligible_substitutions": int(len(substitutions)),
            "suppressed_substitutions": int(len(suppressions)),
        },
        "artifact_regression": {
            "legacy_transition": artifact,
            "vaep_xt": vaep_artifact,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_staging = Path(__file__).stem.endswith("_v4")
    parser.add_argument(
        "--staging",
        dest="staging",
        action="store_true",
        default=default_staging,
    )
    parser.add_argument(
        "--final",
        dest="staging",
        action="store_false",
        help="Validate the unversioned production artifacts.",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_v4_validation(staging=args.staging)
    output = args.output or (
        PROJECT_ROOT / "results/v4_staging/eda_validation_report.json"
        if args.staging
        else PROJECT_ROOT / "results/eda_validation_report.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(
        report,
        indent=2,
        default=lambda value: (
            value.item() if isinstance(value, np.generic) else str(value)
        ),
    )
    output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    print(f"Wrote full validation report to {output}")
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
