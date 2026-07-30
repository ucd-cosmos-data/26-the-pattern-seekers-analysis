#!/usr/bin/env python3
"""Run the legacy foundation and the extended role-aware artifact pipeline."""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

# Running a script inside ``scripts/`` otherwise exposes only that directory
# on sys.path. Add the repository root once so ``src`` is importable and the
# editor can resolve the sibling legacy runner without a dynamic path hack.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.config import (
    AttentionConfig,
    MIN_GOALKEEPER_MINUTES,
    MIN_PLAYER_MINUTES,
    PipelineConfig,
)
from src.features.attention import build_attention_arrays_from_csv
from src.features.events import (
    add_profile_rates,
    derive_pressure_outcomes,
    derive_reception_features,
)
from src.features.goalkeepers import build_goalkeeper_features
from src.features.defense_disruption import derive_defense_disruption
from src.features.network import build_passing_network_features
from src.features.off_ball import OffBallScorer
from src.features.role_vectors import (
    derive_role_channel_weights,
    derive_role_vector,
)
from src.features.spatial import (
    SpatialFeatureTransformer,
    build_event_freeze_frame_features_from_csv,
)
from src.models.attention_experiment import run_attention_experiment
from src.models.composite_calibration import calibrate_composite_weights
from src.models.goalkeeper_valuation import (
    calculate_goalkeeper_ratings,
    goalkeeper_model_summary,
)
from src.models.roles import fit_probabilistic_roles
from src.models.tournament_rankings import (
    TournamentRankingConfig,
    calculate_tournament_rankings_v2,
    tournament_ranking_audit,
)
from src.models.valuation import (
    DEFAULT_METRIC_DIRECTIONS,
    ContributionMetricTransformer,
    GroupedElasticNetValuator,
    IndependentValueScaler,
    calculate_completeness_score,
    calculate_final_player_rating,
    calculate_role_adjusted_value,
)
from src.reporting.artifacts import ArtifactGenerator
from src.validation.metric_gate import FALLBACK_MESSAGE
from scripts.unify_tournament_ratings import attach_unified_tournament_ratings


EVENT_COLUMNS = {
    "id",
    "index",
    "match_id",
    "period",
    "minute",
    "second",
    "team",
    "type",
    "player_id",
    "possession",
    "pass_recipient_id",
    "pass_outcome",
    "pass_cross",
    "location",
    "pass_end_location",
    "carry_end_location",
    "shot_end_location",
    "shot_outcome",
    "shot_statsbomb_xg",
    "shot_type",
    "shot_body_part",
    "shot_technique",
    "shot_one_on_one",
    "shot_first_time",
    "goalkeeper_type",
    "position",
    "under_pressure",
}


def _run_legacy_foundation(
    project_root: Path,
    *,
    reuse_validated_oof: bool,
) -> None:
    """Execute the preserved VAEP/xT/K-Means production foundation."""

    from run_team_simulation_reports import run_pipeline as legacy_pipeline

    legacy_pipeline(
        project_root=project_root,
        staging=False,
        reuse_validated_oof=reuse_validated_oof,
    )


def _merge_player_features(
    profiles: pd.DataFrame,
    features: pd.DataFrame,
) -> pd.DataFrame:
    """Merge one-row-per-player features, replacing stale duplicate columns."""

    if features.empty:
        return profiles
    if "player_id" not in features or features["player_id"].duplicated().any():
        raise ValueError("Player features require unique player_id")
    overlap = set(profiles).intersection(features) - {"player_id"}
    return profiles.drop(columns=sorted(overlap)).merge(
        features,
        on="player_id",
        how="left",
        validate="one_to_one",
    )


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    """Write a CSV atomically so downstream readers never see a partial file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        frame.to_csv(temporary, index=False)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_copy_text(source: Path, destination: Path) -> None:
    """Atomically copy one generated UTF-8 report to a canonical alias."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.write_text(
            source.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_json(payload: dict[str, Any], path: Path) -> None:
    """Write a JSON compatibility artifact atomically."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _update_pipeline_manifest_goalkeepers(
    project_root: Path,
    *,
    goalkeeper_summary: dict[str, Any],
    ranking_audit: dict[str, Any],
) -> Path:
    """Record the active goalkeeper-v2 release in pipeline provenance."""

    path = project_root / "results/metadata/pipeline_manifest.json"
    payload = (
        json.loads(path.read_text(encoding="utf-8"))
        if path.is_file()
        else {}
    )
    payload["goalkeeper_ranking_v2"] = {
        "tournament": "2022_World_Cup",
        "ranking_path": "results/reports/ranking/goalkeeper_rankings.csv",
        "player_table_path": (
            "results/reports/ranking/player_rankings_v2.csv"
        ),
        "ranked_goalkeepers": 32,
        "selection": (
            "maximum tournament minutes per team; actions, player_id, and "
            "player_name are deterministic tie-breakers"
        ),
        "post_shot_validation": goalkeeper_summary.get(
            "post_shot_model",
            {},
        ),
        "audit_passed": bool(ranking_audit.get("passed", False)),
        "uses_player_identity_in_scoring": False,
        "uses_team_advancement_in_scoring": False,
    }
    _atomic_json(payload, path)
    return path


def _atomic_copy_bytes(source: Path, destination: Path) -> None:
    """Copy a binary artifact atomically."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.write_bytes(source.read_bytes())
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def _publish_validation_aliases(
    project_root: Path,
    output_root: Path,
    rankings: pd.DataFrame,
) -> list[Path]:
    """Replace superseded V4 role/valuation validation summaries."""

    report_root = project_root / "results/reports"
    summary = json.loads(
        (output_root / "model_summary.json").read_text(encoding="utf-8")
    )
    comparison_source = output_root / "rating_validation_comparison.csv"
    comparison_destination = (
        report_root / "role_aware_rating_comparison.csv"
    )
    _atomic_copy_text(comparison_source, comparison_destination)

    selection = summary["probabilistic_role_selection"]
    stability = summary["cluster_stability"]
    gate = summary["metric_gate"]
    role_payload = {
        "schema_version": "5.0-role-attention",
        "policy": (
            "K-Means remains the functional-role baseline; probabilistic "
            "roles are active descriptors and never award value directly."
        ),
        "probabilistic_roles": {
            "selected_k": selection["selected_k"],
            "selected_covariance_type": selection[
                "selected_covariance_type"
            ],
            "bootstrap_iterations": stability[
                "bootstrap_iterations_completed"
            ],
            "bootstrap_ari_median": stability["bootstrap_ari_median"],
            "bootstrap_ari_p05": stability["bootstrap_ari_p05"],
            "pca_explained_variance": stability[
                "pca_explained_variance"
            ],
        },
        "decisions": {
            "incumbent_rankings_retained": False,
            "kmeans_baseline_retained": True,
            "probabilistic_roles": "ACTIVE_DESCRIPTIVE",
            "role_aware_valuation": "ACTIVE",
            "attention": (
                "ACTIVE"
                if gate["metric_gate_passed"]
                else "REJECTED_ROLE_AWARE_FALLBACK"
            ),
        },
    }
    role_path = report_root / "player_role_challenger_validation.json"
    _atomic_json(role_payload, role_path)

    valuation_payload = {
        "schema_version": "5.0-role-attention",
        "decision": "PROMOTED_ROLE_AWARE_FALLBACK",
        "production_promoted": True,
        "selected_layer": summary["selected_layer"],
        "attention_metric_gate_passed": summary["metric_gate_passed"],
        "rating_weights": summary["rating_weights"],
        "spearman_rank_correlation": summary["metrics"][
            "spearman_with_legacy_rankings"
        ],
        "attention_metrics": summary["metrics"]["attention"],
        "benchmarks": {
            "messi_global_rank": int(
                rankings.loc[
                    rankings["player_name"].str.contains(
                        "Messi",
                        case=False,
                        na=False,
                    ),
                    "global_rank",
                ].iloc[0]
            ),
            "mbappe_global_rank": int(
                rankings.loc[
                    rankings["player_name"].str.contains(
                        "Mbapp",
                        case=False,
                        na=False,
                    ),
                    "global_rank",
                ].iloc[0]
            ),
        },
        "comparison_csv": (
            "results/reports/role_aware_rating_comparison.csv"
        ),
    }
    valuation_path = (
        report_root / "role_aware_valuation_validation.json"
    )
    _atomic_json(valuation_payload, valuation_path)

    changed_roles = int(
        (
            rankings["functional_role"]
            != rankings["kmeans_functional_role"]
        ).sum()
    )
    refinement_payload = {
        "schema_version": "5.0-role-attention",
        "decision": "PRESERVED_IN_V5",
        "production_promoted": True,
        "eligible_players": len(rankings),
        "changed_roles": changed_roles,
        "unchanged_roles": len(rankings) - changed_roles,
        "change_rate": changed_roles / len(rankings),
        "gates": {
            "legacy_rating_column_preserved": True,
            "v5_rating_active": True,
            "functional_roles_preserved": True,
            "kmeans_baseline_preserved": True,
        },
    }
    refinement_path = (
        report_root / "role_refinement_validation.json"
    )
    _atomic_json(refinement_payload, refinement_path)
    return [
        comparison_destination,
        role_path,
        valuation_path,
        refinement_path,
    ]


def _mark_historical_rating_reports(project_root: Path) -> list[Path]:
    """Label retained V4 packets whose player ratings are superseded."""

    candidates = [
        *sorted(
            (
                project_root / "results/reports/compiled"
            ).glob("*_compiled_player_reports.md")
        ),
        project_root / "results/MIscellaneous/player_rating_uncertainty.md",
    ]
    marker = "<!-- V5_CANONICAL_NOTICE -->"
    notice = "\n".join(
        [
            marker,
            "> **Historical V4 player-rating packet.** Player ratings, ranks, "
            "role-challenger decisions, and rating uncertainty below are "
            "superseded by `results/reports/ranking/player_rankings.csv`, "
            "`results/reports/player_profiles/`, and "
            "`results/reports/canonical/model_summary.md`. Possession, "
            "tactical, and match-bootstrap material remains a historical V4 "
            "result.",
            "",
        ]
    )
    updated: list[Path] = []
    for path in candidates:
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        refreshed = content.replace(
            "- Rankings use the role-aware contextual VAEP/xT/xD model.",
            "- Rankings use the role-aware, development-gated "
            "VAEP/xT/xD model.",
        )
        if marker in refreshed:
            if refreshed == content:
                continue
            temporary_source = path.with_suffix(".v5.tmp")
            temporary_source.write_text(refreshed, encoding="utf-8")
            try:
                _atomic_copy_text(temporary_source, path)
            finally:
                temporary_source.unlink(missing_ok=True)
            updated.append(path)
            continue
        lines = refreshed.splitlines()
        insertion = 1 if lines and lines[0].startswith("#") else 0
        lines[insertion:insertion] = ["", notice]
        temporary_source = path.with_suffix(".v5.tmp")
        temporary_source.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )
        try:
            _atomic_copy_text(temporary_source, path)
        finally:
            temporary_source.unlink(missing_ok=True)
        updated.append(path)
    return updated


def _purge_obsolete_v4_summaries(project_root: Path) -> Path:
    """Delete only allowlisted V4 summary files after V5 publication."""

    results_root = (project_root / "results").resolve()
    report_root = results_root / "reports"
    ranking_root = report_root / "ranking"
    required_publication = {
        ranking_root / "v5_player_rankings.csv",
        ranking_root / "v5_player_rankings.json",
        report_root / "v5_coaches_notebook.md",
        report_root / "model_summary.json",
        report_root / "model_summary.md",
        report_root / "final_summary.md",
        report_root / "v5_artifact_manifest.json",
        report_root / "team_profiles",
        report_root / "player_profiles",
    }
    missing = sorted(
        str(path.relative_to(project_root))
        for path in required_publication
        if not path.exists()
    )
    if missing:
        raise RuntimeError(
            "Refusing V4 cleanup before complete V5 publication: "
            + ", ".join(missing)
        )
    candidates = {
        results_root / "Summary/v4_model_explanation_summary.md",
        *results_root.rglob("v4_final_summary.md"),
    }
    deleted: list[str] = []
    for candidate in sorted(candidates):
        resolved = candidate.resolve()
        if results_root not in resolved.parents:
            raise RuntimeError(f"Unsafe V4 cleanup target: {resolved}")
        if resolved.is_file():
            resolved.unlink()
            deleted.append(str(resolved.relative_to(project_root)))
    manifest_path = (
        project_root / "results/reports/v5_cleanup_manifest.json"
    )
    _atomic_json(
        {
            "schema_version": "5.0-role-attention",
            "cleanup_executed_after_v5_artifact_validation": True,
            "deleted": deleted,
            "allowlist": [
                "results/Summary/v4_model_explanation_summary.md",
                "results/**/v4_final_summary.md",
            ],
        },
        manifest_path,
    )
    return manifest_path


def _refresh_detailed_team_rating_sections(
    project_root: Path,
    rankings: pd.DataFrame,
) -> list[Path]:
    """Replace V4 player-rating blocks inside detailed coaching reports."""

    updated: list[Path] = []
    model_summary = json.loads(
        (
            project_root / "results/reports/model_summary.json"
        ).read_text(encoding="utf-8")
    )
    selection = model_summary["probabilistic_role_selection"]
    stability = model_summary["cluster_stability"]
    gate = model_summary["metric_gate"]
    gate_metrics = gate.get("metrics", {})
    role_validation_block = "\n".join(
        [
            "<!-- PLAYER_ROLE_VALIDATION_START -->",
            "## V5 probabilistic role validation",
            "",
            f"The production role model selected **K={selection['selected_k']} "
            f"with `{selection['selected_covariance_type']}` covariance by "
            "BIC with AIC tie-breaking. K-Means functional roles remain the "
            "published baseline; GMM probabilities and entropy are additive "
            "descriptors.",
            "",
            f"- Bootstrap ARI median: "
            f"{stability['bootstrap_ari_median']:.4f}",
            f"- Bootstrap ARI fifth percentile: "
            f"{stability['bootstrap_ari_p05']:.4f}",
            f"- PCA explained variance: "
            f"{stability['pca_explained_variance']:.4f}",
            "",
            "Roles do not award points directly. Continuous role dimensions "
            "only modulate the weights applied to observed contributions.",
            "<!-- PLAYER_ROLE_VALIDATION_END -->",
        ]
    )
    attention_lines: list[str]
    if {"retrospective", "prospective"}.issubset(gate_metrics):
        retrospective = gate_metrics["retrospective"]
        prospective = gate_metrics["prospective"]
        attention_lines = [
            "The experimental attention challenger was evaluated "
            "match-disjoint and rejected because its discrimination was "
            "materially worse, despite better calibration.",
            "",
            "| Task | Model | ROC-AUC | PR-AUC | ECE | Brier |",
            "|---|---|---:|---:|---:|---:|",
            *[
                "| "
                f"{task.title()} | {model.title()} | "
                f"{metrics['roc_auc']:.4f} | "
                f"{metrics['pr_auc']:.4f} | "
                f"{metrics['expected_calibration_error']:.4f} | "
                f"{metrics['brier_score']:.4f} |"
                for task, task_metrics in (
                    ("retrospective", retrospective),
                    ("prospective", prospective),
                )
                for model, metrics in task_metrics.items()
            ],
        ]
    else:
        attention_lines = [
            "The optional attention experiment was disabled for this "
            "canonical run, so the interpretable role-aware fallback remains "
            "active without publishing unevaluated attention metrics.",
        ]
    role_aware_block = "\n".join(
        [
            "<!-- ROLE_AWARE_VALUATION_START -->",
            "## V5 role-aware valuation and attention gate",
            "",
            "**Production decision: `ROLE_AWARE_FALLBACK`.** The role-aware "
            "layer is active.",
            *attention_lines,
            "",
            f"New-versus-legacy ranking Spearman correlation: "
            f"{gate['spearman_with_legacy_rankings']:.4f}.",
            "<!-- ROLE_AWARE_VALUATION_END -->",
        ]
    )
    refinement_block = "\n".join(
        [
            "<!-- CONTINUOUS_ROLE_REFINEMENT_START -->",
            "## Functional-role compatibility",
            "",
            "The accepted functional-role refinements remain available beside "
            "the original K-Means label. V5 adds continuous seven-dimensional "
            "role vectors and probabilistic roles; neither system contains "
            "player-name rules or discrete role bonuses.",
            "<!-- CONTINUOUS_ROLE_REFINEMENT_END -->",
        ]
    )
    marker_replacements = {
        "PLAYER_ROLE_VALIDATION": role_validation_block,
        "ROLE_AWARE_VALUATION": role_aware_block,
        "CONTINUOUS_ROLE_REFINEMENT": refinement_block,
    }
    section_pattern = re.compile(
        r"## (?:Unified 360-VAEP \+ xT player leaders|"
        r"V5 role-aware player leaders).*?"
        r"(?=## Recurrent tactical mistakes)",
        flags=re.DOTALL,
    )
    markdown_paths = [
        *sorted(
            (
                project_root / "results/reports/teams"
            ).glob("*_team_coaching_report.md")
        ),
        *sorted(
            (
                project_root / "results/reports/compiled"
            ).glob("*_team_coaching_report.md")
        ),
    ]
    for markdown_path in markdown_paths:
        first_line = markdown_path.read_text(encoding="utf-8").splitlines()[0]
        team = first_line.removeprefix("# ").split(" — ", maxsplit=1)[0]
        players = rankings.loc[rankings["team"].eq(team)].sort_values(
            "team_rank"
        )
        lines = [
            "## V5 role-aware player leaders",
            "",
        ]
        if players.empty:
            lines.append(
                "_No player reached the 45-minute outfield or 90-minute "
                "goalkeeper eligibility floor._"
            )
        else:
            for row in players.head(5).itertuples(index=False):
                lines.append(
                    f"{int(row.team_rank)}. {row.player_name} — "
                    f"{row.functional_role}; rating "
                    f"{float(row.final_player_rating):.4f}, "
                    f"VAEP/90 {float(row.vaep_total_p90):+.3f}, "
                    f"xT/90 {float(row.xt_p90):+.3f}, "
                    f"role-adjusted {float(row.role_adjusted_value):.3f}"
                )
        lines.extend(
            [
                "",
                "_Ratings include eligible outfield players from 45 minutes "
                "and goalkeepers from 90 minutes. The 300-minute threshold is "
                "a high-reliability label. V2 evaluates contextual VAEP "
                "behind a development-OOF non-inferiority gate, then uses "
                "the accepted feature set with role-weighted offense/defense "
                "channels, calibrated composite weights, xD-style "
                "disruption, and 450-minute shrinkage._",
                "",
            ]
        )
        content = markdown_path.read_text(encoding="utf-8")
        replacement = "\n".join(lines) + "\n"
        refreshed, count = section_pattern.subn(replacement, content)
        if count != 1:
            raise RuntimeError(
                f"Expected one legacy player section in {markdown_path}"
            )
        for marker, marker_replacement in marker_replacements.items():
            marker_pattern = re.compile(
                rf"<!-- {marker}_START -->.*?"
                rf"<!-- {marker}_END -->",
                flags=re.DOTALL,
            )
            refreshed, marker_count = marker_pattern.subn(
                marker_replacement,
                refreshed,
            )
            if marker_count == 0:
                refreshed = (
                    refreshed.rstrip()
                    + "\n\n"
                    + marker_replacement
                    + "\n"
                )
            elif marker_count != 1:
                raise RuntimeError(
                    f"Expected one {marker} block in {markdown_path}"
                )
        temporary_source = markdown_path.with_suffix(".v5.tmp")
        temporary_source.write_text(refreshed, encoding="utf-8")
        try:
            _atomic_copy_text(temporary_source, markdown_path)
        finally:
            temporary_source.unlink(missing_ok=True)
        updated.append(markdown_path)

        json_path = markdown_path.with_suffix(".json")
        if json_path.is_file():
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            records = []
            record_columns = [
                "player_id",
                "player_name",
                "functional_role",
                "probabilistic_role",
                "vaep_total_p90",
                "vaep_per_touch",
                "xt_p90",
                "role_adjusted_value",
                "completeness_score",
                "off_ball_score",
                "final_player_rating",
                "global_rank",
                "team_rank",
            ]
            for record in players.head(5)[record_columns].to_dict("records"):
                records.append(
                    {
                        key: (
                            None
                            if pd.isna(value)
                            else value.item()
                            if isinstance(value, np.generic)
                            else value
                        )
                        for key, value in record.items()
                    }
                )
            payload["player_rating_schema"] = "5.0-role-attention"
            payload["top_v5_player_evaluations"] = records
            payload.pop("top_v4_player_evaluations", None)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{json_path.name}.",
                suffix=".tmp",
                dir=json_path.parent,
            )
            os.close(descriptor)
            temporary_json = Path(temporary_name)
            try:
                temporary_json.write_text(
                    json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                os.replace(temporary_json, json_path)
            finally:
                temporary_json.unlink(missing_ok=True)
            updated.append(json_path)
    return updated


def _publish_canonical_aliases(
    project_root: Path,
    output_root: Path,
    rated: pd.DataFrame,
) -> list[Path]:
    """Replace superseded player tables and legacy report entry points."""

    rankings = ArtifactGenerator.prepare_rankings(rated)
    destinations = [
        project_root / "data/processed/player_evaluations.csv",
        project_root / "data/processed/player_leaderboard.csv",
        project_root / "results/reports/player_leaderboard.csv",
    ]
    _atomic_csv(rated, destinations[0])
    _atomic_csv(rankings, destinations[1])
    _atomic_csv(rankings, destinations[2])
    team_table = rankings.sort_values(
        ["team", "team_rank", "global_rank"]
    )
    team_destination = (
        project_root / "results/reports/team_player_leaderboards.csv"
    )
    _atomic_csv(team_table, team_destination)
    destinations.append(team_destination)

    report_aliases = [
        (
            output_root / "final_summary.md",
            project_root
            / "results/reports/final/"
            "world_cup_team_performance_and_top_players.md",
        ),
        (
            output_root / "final_summary.md",
            project_root / "results/reports/canonical/final_summary.md",
        ),
        (
            output_root / "model_summary.md",
            project_root
            / "results/Summary/model_summary.md",
        ),
        (
            output_root / "model_summary.md",
            project_root / "results/reports/canonical/model_summary.md",
        ),
        (
            output_root / "model_summary.json",
            project_root
            / "data/processed/player_evaluation_v5_provenance.json",
        ),
        (
            output_root / "model_summary.json",
            project_root / "results/reports/canonical/model_summary.json",
        ),
        (
            output_root / "coaches_notebook.md",
            project_root / "results/reports/canonical/coaches_notebook.md",
        ),
    ]
    for source, destination in report_aliases:
        _atomic_copy_text(source, destination)
        destinations.append(destination)
    figure_root = project_root / "results/figures"
    for source in sorted((output_root / "v5_figures").glob("*.png")):
        destination = figure_root / source.name
        _atomic_copy_bytes(source, destination)
        destinations.append(destination)
    france_v5 = figure_root / "v5_france_team_rankings.png"
    if france_v5.is_file():
        france_legacy = figure_root / "france_team_rankings.png"
        _atomic_copy_bytes(france_v5, france_legacy)
        destinations.append(france_legacy)
    destinations.extend(
        _publish_validation_aliases(
            project_root,
            output_root,
            rankings,
        )
    )
    destinations.extend(
        _refresh_detailed_team_rating_sections(
            project_root,
            rankings,
        )
    )
    destinations.extend(_mark_historical_rating_reports(project_root))
    destinations.append(_purge_obsolete_v4_summaries(project_root))
    return destinations


def _load_events(path: Path) -> pd.DataFrame:
    """Read only event columns used by the extension."""

    available = set(pd.read_csv(path, nrows=0).columns)
    missing = {
        "id",
        "index",
        "match_id",
        "period",
        "minute",
        "second",
        "team",
        "type",
        "player_id",
        "possession",
        "pass_recipient_id",
        "pass_outcome",
        "location",
        "pass_end_location",
    }.difference(available)
    if missing:
        raise ValueError(f"StatsBomb event columns missing: {sorted(missing)}")
    return pd.read_csv(
        path,
        usecols=sorted(EVENT_COLUMNS & available),
        low_memory=False,
    )


def _geometry_player_summary(
    actions: pd.DataFrame,
    geometry: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate only observed actor geometry and retain coverage."""

    if geometry.empty:
        return pd.DataFrame(columns=["player_id"])
    joined = actions[
        [
            "game_id",
            "original_event_id",
            "player_id",
            "type_name",
        ]
    ].merge(
        geometry,
        left_on=["game_id", "original_event_id"],
        right_on=["match_id", "event_uuid"],
        how="left",
        validate="many_to_one",
    )
    joined = joined.loc[joined["player_id"].notna()].copy()
    joined["player_id"] = joined["player_id"].astype(int)
    joined["_geometry_observed"] = joined["sb360_available"].fillna(False)
    joined["_available_space_reception"] = np.where(
        joined["type_name"].astype(str).str.startswith("Ball Receipt"),
        joined["space_received"],
        np.nan,
    )
    summary = joined.groupby("player_id", as_index=False).agg(
        sb360_coverage=("_geometry_observed", "mean"),
        sb360_observations=("_geometry_observed", "sum"),
        mean_defenders_within_3m=("defenders_within_3m", "mean"),
        mean_defenders_within_5m=("defenders_within_5m", "mean"),
        mean_nearest_defender_m=("nearest_defender_m", "mean"),
        mean_passing_lane_availability=(
            "passing_lane_availability",
            "mean",
        ),
        packing_index_mean=("packing_index", "mean"),
        mean_space_received=("_available_space_reception", "mean"),
        actor_shape_deviation_m=("actor_shape_deviation_m", "mean"),
    )
    movement = (
        joined.loc[
            joined["_available_space_reception"].notna()
        ]
        .assign(
            moved_into_available_space=lambda frame: frame[
                "_available_space_reception"
            ].ge(0.5)
        )
        .groupby("player_id", as_index=False)
        .agg(
            movement_into_available_space_rate=(
                "moved_into_available_space",
                "mean",
            )
        )
    )
    summary = summary.merge(movement, on="player_id", how="left")
    observed_shape = summary["actor_shape_deviation_m"].notna()
    summary["shape_maintenance_score"] = np.nan
    summary.loc[observed_shape, "shape_maintenance_score"] = (
        1.0
        - summary.loc[observed_shape, "actor_shape_deviation_m"].rank(
            pct=True,
            method="average",
        )
    )
    summary["defensive_positioning_score"] = summary[
        "shape_maintenance_score"
    ]
    return summary


def _role_feature_names(profiles: pd.DataFrame) -> list[str]:
    """Select rate, role, spatial, graph, geometry, and mask descriptors."""

    explicit = {
        "aerial_dominance_index",
        "pressing_intensity_index",
        "speed_recovery_index",
        "shots_p90",
        "progressive_carries_p90",
        "progressive_passes_p90",
        "key_passes_p90",
        "crosses_p90",
        "interceptions_p90",
        "turnovers_p90",
        "duel_win_rate",
        "pass_completion",
        "line_breaking_pass_rate",
        "pressure_state_rate",
        "distribution_under_pressure",
        "pass_start_x",
        "pass_start_y",
        "pass_receipt_x",
        "pass_receipt_y",
        "average_receiving_x",
        "average_receiving_y",
        "progressive_receptions_p90",
        "dangerous_zone_receptions_p90",
        "mean_defenders_within_3m",
        "mean_defenders_within_5m",
        "mean_nearest_defender_m",
        "mean_passing_lane_availability",
        "packing_index_mean",
        "mean_space_received",
        "sb360_coverage",
        "network_pagerank",
        "network_betweenness",
        "network_eigenvector",
        "network_closeness",
        "network_entropy",
        "build_up_involvement_ratio",
        *(
            "progression_score",
            "creation_score",
            "finishing_score",
            "pressing_score",
            "defensive_score",
            "ball_security_score",
            "aerial_score",
        ),
    }
    return [
        column
        for column in profiles
        if column in explicit
        or column.startswith("kde_")
        or column
        in {
            "occupancy_entropy",
            "convex_hull_area",
            "final_third_occupancy",
            "zone14_share",
            "half_space_share",
            "wide_corridor_share",
        }
    ]


def _derive_team_profile_metrics(
    actions: pd.DataFrame,
    events: pd.DataFrame,
    defensive_features_path: Path,
) -> pd.DataFrame:
    """Aggregate event and 360 team descriptors for all tournament teams."""

    threat = (
        actions.groupby("team", as_index=False)
        .agg(
            total_xt_created=("xt_value", "sum"),
            total_xa_created=("xa_value", "sum"),
        )
        .rename(columns={"team": "team"})
    )
    pressure_passes = events.loc[
        events["type"].eq("Pass") & events["under_pressure"].notna()
    ].copy()
    pressure_passes["_under_pressure"] = (
        pressure_passes["under_pressure"]
        .fillna(False)
        .astype(str)
        .str.lower()
        .isin({"true", "1", "yes"})
    )
    pressure_passes = pressure_passes.loc[
        pressure_passes["_under_pressure"]
    ]
    pressure_passes["_completed"] = pressure_passes[
        "pass_outcome"
    ].isna()
    resistance = (
        pressure_passes.groupby("team", as_index=False)
        .agg(
            pressured_passes=("id", "size"),
            pressure_resistance_rate=("_completed", "mean"),
        )
    )
    team_metrics = threat.merge(
        resistance,
        on="team",
        how="outer",
        validate="one_to_one",
    )
    if defensive_features_path.is_file():
        defensive = pd.read_csv(
            defensive_features_path,
            usecols=[
                "defending_team",
                "avg_defensive_hull_area",
                "avg_defensive_density",
                "avg_defensive_width",
                "avg_defensive_depth",
            ],
            low_memory=False,
        )
        compactness = (
            defensive.groupby("defending_team", as_index=False)
            .agg(
                defensive_hull_area=(
                    "avg_defensive_hull_area",
                    "mean",
                ),
                defensive_density=("avg_defensive_density", "mean"),
                defensive_width=("avg_defensive_width", "mean"),
                defensive_depth=("avg_defensive_depth", "mean"),
            )
            .rename(columns={"defending_team": "team"})
        )
        team_metrics = team_metrics.merge(
            compactness,
            on="team",
            how="outer",
            validate="one_to_one",
        )
    return team_metrics


def _action_value_splits(
    actions: pd.DataFrame,
    *,
    group_columns: tuple[str, ...],
) -> pd.DataFrame:
    """Aggregate VAEP/xT channels and separate open-play from set pieces."""

    required = {
        *group_columns,
        "play_pattern",
        "action_side",
        "vaep_value",
        "xt_value",
        "xa_value",
        "touch",
    }
    missing = required.difference(actions.columns)
    if missing:
        raise ValueError(f"Action value fields missing: {sorted(missing)}")
    working = actions.loc[actions["player_id"].notna()].copy()
    set_piece = working["play_pattern"].astype(str).str.contains(
        "Corner|Free Kick|Throw",
        case=False,
        na=False,
    )
    working["_vaep_off"] = np.where(
        working["action_side"].eq("offense"),
        working["vaep_value"],
        0.0,
    )
    working["_vaep_def"] = np.where(
        working["action_side"].eq("defense"),
        working["vaep_value"],
        0.0,
    )
    working["_open_play_xt"] = np.where(
        ~set_piece,
        working["xt_value"],
        0.0,
    )
    working["_set_piece_xt"] = np.where(
        set_piece,
        working["xt_value"],
        0.0,
    )
    return working.groupby(list(group_columns), as_index=False).agg(
        vaep_offense=("_vaep_off", "sum"),
        vaep_defense=("_vaep_def", "sum"),
        xt_total=("xt_value", "sum"),
        open_play_xt_total=("_open_play_xt", "sum"),
        set_piece_xt_total=("_set_piece_xt", "sum"),
        xa_sum=("xa_value", "sum"),
        total_touches=("touch", "sum"),
    )


def _add_match_valuation_rates(samples: pd.DataFrame) -> pd.DataFrame:
    """Derive opportunity and per-90 metrics for grouped valuation."""

    output = samples.copy()
    minutes = pd.to_numeric(
        output["minutes"],
        errors="coerce",
    ).clip(lower=1.0)
    per_90_sources = {
        "progressive_carries_p90": "progressive_carries",
        "progressive_passes_p90": "progressive_passes",
        "key_passes_p90": "key_passes",
        "shots_p90": "shots",
        "xg_p90": "xg_sum",
        "goals_p90": "goals",
        "pressures_p90": "pressures",
        "counterpressures_p90": "counterpressures",
        "recoveries_p90": "recoveries",
        "interceptions_p90": "interceptions",
        "turnovers_p90": "turnovers",
        "aerial_wins_p90": "aerial_wins",
        "xt_p90": "xt_total",
        "open_play_xt_p90": "open_play_xt_total",
        "set_piece_xt_p90": "set_piece_xt_total",
        "xa_p90": "xa_sum",
        "vaep_off_p90": "vaep_offense",
        "vaep_def_p90": "vaep_defense",
    }
    for destination, source in per_90_sources.items():
        if source in output:
            output[destination] = (
                90.0
                * pd.to_numeric(output[source], errors="coerce")
                / minutes
            )
    ratios = {
        "line_breaking_pass_rate": (
            "progressive_passes",
            "passes",
        ),
        "pass_completion": ("completed_passes", "passes"),
        "pressure_resistance": (
            "successful_under_pressure_actions",
            "under_pressure_actions",
        ),
        "duel_win_rate": ("duels_won", "duels"),
        "aerial_dominance_index": ("aerial_wins", "aerial_events"),
    }
    for destination, (numerator, denominator) in ratios.items():
        output[destination] = (
            pd.to_numeric(output[numerator], errors="coerce")
            / pd.to_numeric(
                output[denominator],
                errors="coerce",
            ).replace(0.0, np.nan)
        )
    output["vaep_per_touch"] = (
        output["vaep_offense"] + output["vaep_defense"]
    ) / pd.to_numeric(
        output["total_touches"],
        errors="coerce",
    ).replace(0.0, np.nan)
    return output


def _build_match_valuation_samples(
    components: pd.DataFrame,
    actions: pd.DataFrame,
) -> pd.DataFrame:
    """Build one leakage-auditable player-match contribution table."""

    values = _action_value_splits(
        actions,
        group_columns=("game_id", "player_id"),
    ).rename(columns={"game_id": "match_id"})
    samples = components.merge(
        values,
        on=["match_id", "player_id"],
        how="left",
        validate="one_to_one",
    )
    value_columns = [
        "vaep_offense",
        "vaep_defense",
        "xt_total",
        "open_play_xt_total",
        "set_piece_xt_total",
        "xa_sum",
        "total_touches",
    ]
    samples[value_columns] = samples[value_columns].fillna(0.0)
    samples = samples.loc[
        pd.to_numeric(samples["minutes"], errors="coerce").ge(20.0)
        & ~samples["position_group"].eq("Goalkeeper")
    ].copy()
    return _add_match_valuation_rates(samples)


def _fit_grouped_role_valuation(
    match_samples: pd.DataFrame,
    profiles: pd.DataFrame,
    *,
    random_state: int,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, GroupedElasticNetValuator]]:
    """Fit separate match-grouped offensive and defensive ElasticNet heads."""

    candidates = (
        "open_play_xt_p90",
        "set_piece_xt_p90",
        "progressive_carries_p90",
        "progressive_passes_p90",
        "line_breaking_pass_rate",
        "key_passes_p90",
        "xa_p90",
        "shots_p90",
        "xg_p90",
        "goals_p90",
        "pressures_p90",
        "counterpressures_p90",
        "recoveries_p90",
        "interceptions_p90",
        "duel_win_rate",
        "pass_completion",
        "pressure_resistance",
        "turnovers_p90",
        "aerial_dominance_index",
        "aerial_wins_p90",
        "attention_context_value",
    )
    feature_names = tuple(
        feature
        for feature in candidates
        if feature in match_samples and feature in profiles
    )
    if len(feature_names) < 8:
        raise ValueError("Too few common grouped valuation features")
    models: dict[str, GroupedElasticNetValuator] = {}
    raw_predictions: dict[str, np.ndarray] = {}
    diagnostics: dict[str, Any] = {
        "grouping": "nested GroupKFold by match_id",
        "feature_names": list(feature_names),
        "heads": {},
    }
    for head, target in (
        ("offense", "vaep_off_p90"),
        ("defense", "vaep_def_p90"),
    ):
        model = GroupedElasticNetValuator(
            feature_names=feature_names,
            random_state=random_state,
        ).fit(
            match_samples,
            match_samples[target],
            match_samples["match_id"],
        )
        models[head] = model
        raw_predictions[head] = model.predict(profiles)
        coefficients = model.coefficient_series()
        diagnostics["heads"][head] = {
            "metrics": dataclasses.asdict(model.metrics_),
            "best_alpha": model.best_alpha_,
            "best_l1_ratio": model.best_l1_ratio_,
            "coefficients": coefficients.to_dict(),
            "nonzero_coefficients": int(coefficients.ne(0.0).sum()),
            "coefficient_std": float(coefficients.std(ddof=0)),
            "fold_audit": model.fold_audit_,
        }
    predicted = pd.DataFrame(
        {
            "position_group": profiles["position_group"].to_numpy(),
            "vaep_off_p90": raw_predictions["offense"],
            "vaep_def_p90": raw_predictions["defense"],
        },
        index=profiles.index,
    )
    scaled = IndependentValueScaler(
        minimum_group_size=12,
    ).fit_transform(predicted)
    channel_weights = derive_role_channel_weights(profiles)
    score = (
        channel_weights["role_off_weight"] * scaled["vaep_off_scaled"]
        + channel_weights["role_def_weight"] * scaled["vaep_def_scaled"]
    ).rename("role_adjusted_value")
    role_outputs = pd.DataFrame(
        {
            "role_off_scaled": scaled["vaep_off_scaled"],
            "role_def_scaled": scaled["vaep_def_scaled"],
            "role_adjusted_value": score,
            "role_off_weight": channel_weights["role_off_weight"],
            "role_def_weight": channel_weights["role_def_weight"],
            "role_weight_source": channel_weights["role_weight_source"],
        },
        index=profiles.index,
    )
    all_coefficients = pd.concat(
        [model.coefficient_series() for model in models.values()],
        axis=1,
    )
    diagnostics["coefficient_dispersion_gate"] = bool(
        all_coefficients.std(axis=0, ddof=0).gt(0.005).all()
        and all_coefficients.ne(0.0).sum(axis=0).ge(2).all()
    )
    if not diagnostics["coefficient_dispersion_gate"]:
        raise RuntimeError(
            "Grouped ElasticNet coefficient dispersion gate failed"
        )
    diagnostics["combination"] = {
        "formula": (
            "role_off_weight * role_off_scaled + "
            "role_def_weight * role_def_scaled"
        ),
        "role_weight_source_counts": (
            channel_weights["role_weight_source"].value_counts().to_dict()
        ),
    }
    return role_outputs, diagnostics, models


def _validation_regression_gate(
    previous: dict[str, Any],
    current: dict[str, Any],
    *,
    include_attention: bool,
    tolerance: float = 0.01,
) -> dict[str, Any]:
    """Reject material degradation in comparable validation metrics."""

    higher_is_better = {"roc_auc", "pr_auc"}
    lower_is_better = {
        "brier_score",
        "calibration_error",
        "expected_calibration_error",
    }
    comparisons: list[dict[str, Any]] = []

    def compare(
        old: Any,
        new: Any,
        path: tuple[str, ...],
    ) -> None:
        if isinstance(old, dict) and isinstance(new, dict):
            for key in sorted(set(old).intersection(new)):
                compare(old[key], new[key], (*path, str(key)))
            return
        if not path or path[-1] not in higher_is_better | lower_is_better:
            return
        if not isinstance(old, (int, float)) or not isinstance(
            new,
            (int, float),
        ):
            return
        metric = path[-1]
        passed = (
            float(new) >= float(old) - tolerance
            if metric in higher_is_better
            else float(new) <= float(old) + tolerance
        )
        required_for_gate = not (
            include_attention
            and path
            and path[0] == "attention"
            and "baseline" in path
        )
        comparisons.append(
            {
                "metric_path": ".".join(path),
                "previous": float(old),
                "current": float(new),
                "tolerance": tolerance,
                "passed": bool(passed),
                "required_for_gate": required_for_gate,
            }
        )

    compare(
        previous.get("legacy_vaep_oof", {}),
        current.get("legacy_vaep_oof", {}),
        ("legacy_vaep_oof",),
    )
    compare(
        previous.get("legacy_vaep_test", {}),
        current.get("legacy_vaep_test", {}),
        ("legacy_vaep_test",),
    )
    if include_attention:
        compare(
            previous.get("attention", {}),
            current.get("attention", {}),
            ("attention",),
        )
    required = [
        item for item in comparisons if item["required_for_gate"]
    ]
    passed = bool(required) and all(
        item["passed"] for item in required
    )
    return {
        "passed": passed,
        "tolerance": tolerance,
        "comparisons": comparisons,
        "attention_compared": include_attention,
    }


def run_extended_pipeline(
    config: PipelineConfig,
    *,
    skip_legacy_foundation: bool = False,
    reuse_validated_oof: bool = False,
    recompute_metric_360: bool = True,
) -> dict[str, Any]:
    """Build all role-aware artifacts while preserving legacy outputs."""

    project_root = config.input_root
    output_root = config.output_root
    output_root.mkdir(parents=True, exist_ok=True)
    if not skip_legacy_foundation:
        _run_legacy_foundation(
            project_root,
            reuse_validated_oof=reuse_validated_oof,
        )

    profile_path = project_root / "data/processed/player_evaluations.csv"
    actions_path = project_root / "data/processed/world_cup_spadl_actions.parquet"
    components_path = (
        project_root / "data/interim/world_cup_player_match_components.csv"
    )
    events_path = project_root / "notebooks/all_events.csv"
    frames_path = project_root / "data/interim/world_cup_360_frames.csv"
    provenance_path = (
        project_root / "data/processed/player_evaluation_provenance.json"
    )
    for path in (
        profile_path,
        actions_path,
        components_path,
        events_path,
        provenance_path,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)

    profiles = pd.read_csv(profile_path)
    profiles["player_id"] = profiles["player_id"].astype(int)
    profiles = profiles.loc[
        (
            ~profiles["position_group"].eq("Goalkeeper")
            & pd.to_numeric(profiles["minutes"], errors="coerce").ge(
                MIN_PLAYER_MINUTES
            )
        )
        | (
            profiles["position_group"].eq("Goalkeeper")
            & pd.to_numeric(profiles["minutes"], errors="coerce").ge(
                MIN_GOALKEEPER_MINUTES
            )
        )
    ].copy()
    actions = pd.read_parquet(actions_path)
    actions["original_event_id"] = actions["original_event_id"].astype(str)
    events = _load_events(events_path)
    components = pd.read_csv(components_path, low_memory=False)
    components["player_id"] = components["player_id"].astype(int)

    player_value_splits = _action_value_splits(
        actions,
        group_columns=("player_id",),
    )
    player_value_splits["player_id"] = player_value_splits[
        "player_id"
    ].astype(int)
    player_value_splits = player_value_splits.merge(
        profiles[["player_id", "minutes"]],
        on="player_id",
        how="inner",
        validate="one_to_one",
    )
    split_minutes = player_value_splits["minutes"].clip(lower=1.0)
    player_value_splits["open_play_xt_p90"] = (
        90.0
        * player_value_splits["open_play_xt_total"]
        / split_minutes
    )
    player_value_splits["set_piece_xt_p90"] = (
        90.0
        * player_value_splits["set_piece_xt_total"]
        / split_minutes
    )
    profiles = _merge_player_features(
        profiles,
        player_value_splits[
            ["player_id", "open_play_xt_p90", "set_piece_xt_p90"]
        ],
    )

    reception = derive_reception_features(events)
    pressure = derive_pressure_outcomes(events)
    profiles = _merge_player_features(profiles, reception)
    profiles = _merge_player_features(profiles, pressure)
    profiles = add_profile_rates(profiles)

    spatial = SpatialFeatureTransformer().fit(actions).transform(actions)
    profiles = _merge_player_features(profiles, spatial)
    network = build_passing_network_features(events)
    profiles = _merge_player_features(profiles, network)
    defense_disruption = derive_defense_disruption(actions, profiles)
    profiles = _merge_player_features(profiles, defense_disruption)

    geometry_cache = (
        project_root
        / "data/interim/role_aware_metric_360_event_features.parquet"
    )
    geometry = pd.DataFrame()
    if geometry_cache.is_file():
        geometry = pd.read_parquet(geometry_cache)
    elif recompute_metric_360:
        if not frames_path.is_file():
            raise FileNotFoundError(frames_path)
        geometry = build_event_freeze_frame_features_from_csv(
            events,
            frames_path,
        )
        geometry_cache.parent.mkdir(parents=True, exist_ok=True)
        geometry.to_parquet(geometry_cache, index=False)
    if not geometry.empty:
        profiles = _merge_player_features(
            profiles,
            _geometry_player_summary(actions, geometry),
        )

    role_vectors = derive_role_vector(profiles)
    profiles = _merge_player_features(profiles, role_vectors)
    profiles["completeness_score"] = calculate_completeness_score(profiles)

    probabilistic = fit_probabilistic_roles(
        profiles,
        config=config.roles,
        feature_names=_role_feature_names(profiles),
    )
    role_assignment_columns = [
        column
        for column in probabilistic.assignments
        if column
        not in {
            "player",
            "team",
            "position_group",
            "functional_role",
        }
    ]
    profiles = _merge_player_features(
        profiles,
        probabilistic.assignments[role_assignment_columns],
    )

    off_ball = OffBallScorer().fit(profiles).transform(profiles)
    profiles = _merge_player_features(profiles, off_ball)
    match_valuation_samples = _build_match_valuation_samples(
        components,
        actions,
    )
    match_valuation_samples = match_valuation_samples.loc[
        match_valuation_samples["player_id"].isin(
            profiles.loc[
                ~profiles["position_group"].eq("Goalkeeper"),
                "player_id",
            ]
        )
    ].copy()
    role_outputs, role_valuation_summary, role_models = (
        _fit_grouped_role_valuation(
            match_valuation_samples,
            profiles,
            random_state=config.random_state,
        )
    )
    for column in role_outputs:
        profiles[column] = role_outputs[column]

    attention_summary: dict[str, Any] = {
        "enabled": config.attention.enabled,
        "selected_layer": "role_aware_fallback",
        "metric_gate_passed": False,
        "message": "Attention experiment disabled by configuration.",
    }
    if config.attention.enabled:
        arrays = build_attention_arrays_from_csv(
            actions,
            profiles,
            frames_path,
            maximum_tokens=config.attention.maximum_tokens,
            maximum_events=config.attention.maximum_events,
            random_state=config.attention.random_state,
        )
        attention_config = dataclasses.replace(
            config.attention,
            enabled=True,
            event_feature_count=arrays.event_features.shape[1],
            token_feature_count=arrays.tokens.shape[2],
        )
        experiment = run_attention_experiment(
            arrays.event_features,
            arrays.tokens,
            arrays.token_padding_mask,
            arrays.targets,
            arrays.match_ids,
            auxiliary_targets=arrays.auxiliary_targets,
            config=attention_config,
            folds=attention_config.cv_folds,
        )
        attention_summary = {
            "enabled": True,
            "selected_layer": experiment.gate.selected_layer,
            "metric_gate_passed": experiment.gate.accepted,
            "message": experiment.gate.message,
            "metrics": experiment.gate.tasks,
            "fold_audit": experiment.fold_audit,
            "parameter_count": experiment.attention_parameter_count,
            "contextual_head_means": {
                name: float(np.mean(values))
                for name, values in (
                    experiment.contextual_head_probabilities.items()
                )
            },
            "feature_importance": experiment.baseline_feature_importance,
        }
        if experiment.gate.accepted:
            action_context = pd.DataFrame(
                {
                    "action_index": arrays.action_indices,
                    "attention_context_value": experiment.attention_probabilities[
                        "retrospective"
                    ],
                }
            )
            action_context = action_context.merge(
                actions[["game_id", "player_id"]],
                left_on="action_index",
                right_index=True,
                how="left",
                validate="one_to_one",
            )
            player_context = (
                action_context.dropna(subset=["player_id"])
                .assign(player_id=lambda frame: frame["player_id"].astype(int))
                .groupby("player_id", as_index=False)
                .agg(
                    attention_context_value=(
                        "attention_context_value",
                        "mean",
                    ),
                    attention_context_actions=(
                        "attention_context_value",
                        "size",
                    ),
                )
            )
            profiles = _merge_player_features(profiles, player_context)
            match_context = (
                action_context.dropna(subset=["player_id"])
                .assign(
                    player_id=lambda frame: frame["player_id"].astype(int),
                    match_id=lambda frame: frame["game_id"].astype(int),
                )
                .groupby(["match_id", "player_id"], as_index=False)
                .agg(
                    attention_context_value=(
                        "attention_context_value",
                        "mean",
                    )
                )
            )
            match_valuation_samples = match_valuation_samples.merge(
                match_context,
                on=["match_id", "player_id"],
                how="left",
                validate="one_to_one",
            )
            role_outputs, role_valuation_summary, role_models = (
                _fit_grouped_role_valuation(
                    match_valuation_samples,
                    profiles,
                    random_state=config.random_state,
                )
            )
            for column in role_outputs:
                profiles[column] = role_outputs[column]
        else:
            print(FALLBACK_MESSAGE)

    outfield_profiles = profiles.loc[
        ~profiles["position_group"].eq("Goalkeeper")
        & pd.to_numeric(profiles["minutes"], errors="coerce").ge(
            MIN_PLAYER_MINUTES
        )
    ].copy()
    baseline_outfield = calculate_final_player_rating(
        outfield_profiles,
        config=config.rating,
    )
    calibrated_weights, composite_calibration = (
        calibrate_composite_weights(
            baseline_outfield,
            config.rating.weights,
            random_state=config.random_state,
        )
    )
    calibrated_rating_config = dataclasses.replace(
        config.rating,
        weights=calibrated_weights,
    )
    rated_outfield = calculate_final_player_rating(
        baseline_outfield,
        config=calibrated_rating_config,
    )
    rated_outfield["global_rank_eligible"] = True
    goalkeeper_features, goalkeeper_audit = build_goalkeeper_features(
        events,
        profiles,
    )
    goalkeeper_ratings = calculate_goalkeeper_ratings(
        goalkeeper_features,
        reliability_minutes=config.rating.reliability_minutes,
    )
    goalkeeper_profiles = profiles.loc[
        profiles["position_group"].eq("Goalkeeper")
        & profiles["player_id"].isin(goalkeeper_ratings["player_id"])
    ].copy()
    goalkeeper_columns = [
        column
        for column in goalkeeper_ratings
        if column not in {"team", "minutes"}
    ]
    goalkeeper_profiles = goalkeeper_profiles.drop(
        columns=[
            column
            for column in goalkeeper_columns
            if column in goalkeeper_profiles and column != "player_id"
        ]
    ).merge(
        goalkeeper_ratings[goalkeeper_columns],
        on="player_id",
        how="left",
        validate="one_to_one",
    )
    goalkeeper_profiles["raw_final_player_rating"] = goalkeeper_profiles[
        "goalkeeper_raw_rating"
    ]
    goalkeeper_profiles["rating_minutes_reliability"] = (
        goalkeeper_profiles["goalkeeper_rating_reliability"]
    )
    goalkeeper_profiles["player_evaluation_score"] = goalkeeper_profiles[
        "final_player_rating"
    ]
    goalkeeper_profiles["functional_role"] = "Goalkeeper"
    goalkeeper_profiles["probabilistic_role"] = "Goalkeeper"
    goalkeeper_profiles["role_rank"] = goalkeeper_profiles[
        "goalkeeper_rank"
    ]
    goalkeeper_profiles["RankingStatus"] = np.select(
        [
            pd.to_numeric(
                goalkeeper_profiles["minutes"],
                errors="coerce",
            ).ge(300.0),
            pd.to_numeric(
                goalkeeper_profiles["minutes"],
                errors="coerce",
            ).ge(180.0),
        ],
        [
            "Ranked (300+ min)",
            "Ranked (180–299 min)",
        ],
        default="Coverage only (<180 min)",
    )
    rated = pd.concat(
        [rated_outfield, goalkeeper_profiles],
        ignore_index=True,
        sort=False,
    )
    rated["team_rank"] = rated.groupby("team")[
        "final_player_rating"
    ].rank(method="min", ascending=False).astype(int)
    tournament_ranking_config = TournamentRankingConfig()
    rated = calculate_tournament_rankings_v2(
        rated,
        config=tournament_ranking_config,
    )
    tournament_rank_audit = tournament_ranking_audit(
        rated,
        strict=True,
    )
    rated = attach_unified_tournament_ratings(rated)
    unified_validation = rated.attrs["unified_validation"]
    goalkeeper_summary = goalkeeper_model_summary(
        goalkeeper_audit,
        goalkeeper_ratings,
    )
    legacy_column = (
        "legacy_final_player_rating"
        if "legacy_final_player_rating" in rated
        else "final_player_rating"
    )
    rank_rho = float(
        spearmanr(
            rated.loc[
                rated["global_rank_eligible"].fillna(False),
                legacy_column,
            ],
            rated.loc[
                rated["global_rank_eligible"].fillna(False),
                "final_player_rating",
            ],
        ).statistic
    )
    attention_summary["spearman_with_legacy_rankings"] = rank_rho

    coefficient_frame = pd.concat(
        {
            head: model.coefficient_series()
            for head, model in role_models.items()
        },
        axis=1,
    )
    mean_weights = coefficient_frame.mean(axis=1).sort_values(
        ascending=False
    )
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))

    def plain(value: Any) -> Any:
        if dataclasses.is_dataclass(value) and not isinstance(value, type):
            return {
                field.name: plain(getattr(value, field.name))
                for field in dataclasses.fields(value)
            }
        if isinstance(value, dict):
            return {str(key): plain(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [plain(item) for item in value]
        return value

    current_validation_metrics = {
        "legacy_vaep_oof": provenance.get("vaep_oof_metrics", {}),
        "legacy_vaep_test": provenance.get(
            "vaep_final_test_metrics",
            {},
        ),
        "contextual_vaep_gate": provenance.get(
            "contextual_vaep_gate",
            {},
        ),
        "attention": plain(attention_summary.get("metrics", {})),
    }
    previous_summary_path = (
        project_root / "results/reports/model_summary.json"
    )
    previous_metrics: dict[str, Any] = {}
    if previous_summary_path.is_file():
        previous_metrics = json.loads(
            previous_summary_path.read_text(encoding="utf-8")
        ).get("metrics", {})
    regression_gate = _validation_regression_gate(
        previous_metrics,
        current_validation_metrics,
        include_attention=config.attention.enabled,
    )
    if previous_metrics and not regression_gate["passed"]:
        _atomic_json(
            regression_gate,
            output_root / "validation_regression_failure.json",
        )
        raise RuntimeError(
            "Validation metric regression gate failed; canonical artifacts "
            "will not be updated."
        )
    model_summary = {
        "selected_layer": attention_summary["selected_layer"],
        "metric_gate_passed": attention_summary["metric_gate_passed"],
        "metrics": {
            **current_validation_metrics,
            "role_aware_elastic_net": {
                head: details["metrics"]
                for head, details in role_valuation_summary[
                    "heads"
                ].items()
            },
            "goalkeeper_post_shot": goalkeeper_summary.get(
                "post_shot_model",
                {},
            ).get("metrics", {}),
            "spearman_with_legacy_rankings": rank_rho,
        },
        "metric_gate": attention_summary,
        "validation_regression_gate": regression_gate,
        "feature_importance": {
            "elastic_net_mean_coefficients": mean_weights.to_dict(),
            "elastic_net_head_coefficients": {
                head: model.coefficient_series().to_dict()
                for head, model in role_models.items()
            },
            "attention_or_baseline": attention_summary.get(
                "feature_importance",
                {},
            ),
        },
        "role_aware_elastic_net": role_valuation_summary,
        "goalkeeper_model": goalkeeper_summary,
        "cluster_stability": probabilistic.diagnostics,
        "probabilistic_role_selection": {
            "selected_k": probabilistic.selected_k,
            "selected_covariance_type": (
                probabilistic.selected_covariance_type
            ),
            "candidates": probabilistic.candidate_metrics.to_dict("records"),
        },
        "rating_weights": dict(calibrated_weights),
        "tournament_ranking_v2": {
            "scope": "2022 FIFA World Cup only",
            "tournament": "2022_World_Cup",
            "position_groups": [
                "GK",
                "CB",
                "FB",
                "DM",
                "CM",
                "AM",
                "FW",
            ],
            "component_weights": {
                group: dict(weights)
                for group, weights in (
                    tournament_ranking_config.component_weights.items()
                )
            },
            "goalkeeper_weights": dict(
                tournament_ranking_config.goalkeeper_weights
            ),
            "goalkeeper_tournament_impact": {
                "shootout_save_points": 0.20,
                "vaep_percentile_maximum": 0.04,
                "high_leverage_volume_percentile_maximum": 0.02,
                "uses_player_identity": False,
                "uses_team_advancement": False,
            },
            "reliability_minutes": (
                tournament_ranking_config.reliability_minutes
            ),
            "target_forward_threshold": (
                tournament_ranking_config.target_forward_threshold
            ),
            "target_forward_maximum_boost": (
                tournament_ranking_config.target_forward_maximum_boost
            ),
            "audit": tournament_rank_audit,
        },
        "unified_tournament_rating": unified_validation,
        "composite_calibration": composite_calibration,
        "rating_methodology": {
            "outfield_eligibility_minutes": 45,
            "goalkeeper_eligibility_minutes": 90,
            "outfield_primary_ranking_minutes": 300,
            "goalkeeper_primary_ranking_minutes": 270,
            "outfield_reliability": "minutes / (minutes + 450)",
            "goalkeeper_reliability": (
                "feature_coverage * minutes / (minutes + 450)"
            ),
            "outfield_ranking_statuses": [
                "Ranked (300+ min)",
                "Ranked (180–299 min)",
                "Coverage only (<180 min)",
            ],
            "goalkeeper_ranking_statuses": [
                "Ranked (270+ min)",
                "Ranked (180–269 min)",
                "Coverage only (<180 min)",
            ],
            "role_channel_formula": (
                "w_off(role) * offense_scaled + "
                "w_def(role) * defense_scaled"
            ),
            "completeness_formula": (
                "0.6 * quality_adjusted_top3_completeness + "
                "0.4 * minutes_factor"
            ),
            "contextual_vaep_features": [
                "pre_action_goal_diff",
                "match_minute",
                "pre_tournament_opponent_strength",
                "group_stage_vs_knockout",
            ],
            "contextual_vaep_grouping": (
                "context features are accepted only by a match-disjoint "
                "development-OOF non-inferiority gate; the untouched test "
                "is opened once for the selected feature set"
            ),
        },
        "defense_disruption": {
            "grid": "6 columns x 8 rows",
            "formula": (
                "BaseThreat(zone) * ActionImpactFactor, aggregated per 90"
            ),
            "position_group_percentile": "xd90_pct",
            "defensive_dimension_integration": (
                "seventh evidence-aware defensive role input"
            ),
        },
    }

    player_output = output_root / "player_evaluations_v5.csv"
    rated.to_csv(player_output, index=False)
    defense_disruption.to_csv(
        output_root / "defense_disruption.csv",
        index=False,
    )
    old_global_rank = (
        rated[legacy_column]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    new_global_rank = rated["global_rank"]
    comparison = pd.DataFrame(
        {
            "player": rated.get("player", rated.get("player_name")),
            "old_rating": rated[legacy_column],
            "new_rating": rated["final_player_rating"],
            "rating_difference": (
                rated["final_player_rating"] - rated[legacy_column]
            ),
            "functional_role": rated["functional_role"],
            "old_global_rank": old_global_rank,
            "new_global_rank": new_global_rank,
            "rank_improvement": old_global_rank - new_global_rank,
        }
    )
    team_metrics = _derive_team_profile_metrics(
        actions,
        events,
        project_root
        / "data/processed/world_cup_defensive_features.csv",
    )
    team_composites = (
        rated_outfield.groupby("team", as_index=False)
        .agg(
            mean_creation_score=("creation_score", "mean"),
            mean_defensive_score=("defensive_score", "mean"),
            mean_ball_security_score=("ball_security_score", "mean"),
            mean_xd90=("xd90", "mean"),
        )
    )
    high_reliability = rated_outfield.loc[
        pd.to_numeric(
            rated_outfield["minutes"],
            errors="coerce",
        ).ge(300.0)
    ]
    ranked_composites = (
        high_reliability.groupby("team", as_index=False)
        .agg(
            mean_creation_score_ranked_300=("creation_score", "mean"),
            mean_defensive_score_ranked_300=("defensive_score", "mean"),
            mean_ball_security_score_ranked_300=(
                "ball_security_score",
                "mean",
            ),
        )
    )
    team_metrics = (
        team_metrics.merge(
            team_composites,
            on="team",
            how="left",
            validate="one_to_one",
        )
        .merge(
            ranked_composites,
            on="team",
            how="left",
            validate="one_to_one",
        )
    )
    team_metrics.to_csv(
        output_root / "team_metrics_v2.csv",
        index=False,
    )
    team_player_pool = (
        components.groupby(["player_id", "team"], as_index=False)
        .agg(
            player_name=("player", "first"),
            position_group=("position_group", "first"),
            minutes=("minutes", "sum"),
        )
    )
    team_player_pool = team_player_pool.loc[
        (
            ~team_player_pool["position_group"].eq("Goalkeeper")
            & team_player_pool["minutes"].ge(MIN_PLAYER_MINUTES)
        )
        | (
            team_player_pool["position_group"].eq("Goalkeeper")
            & team_player_pool["minutes"].ge(MIN_GOALKEEPER_MINUTES)
        )
    ].copy()
    manifest = ArtifactGenerator(output_root).generate(
        rated,
        model_summary=model_summary,
        validation_comparison=comparison,
        tournament_teams=sorted(events["team"].dropna().astype(str).unique()),
        team_metrics=team_metrics,
        team_player_pool=team_player_pool,
    )
    _update_pipeline_manifest_goalkeepers(
        project_root,
        goalkeeper_summary=goalkeeper_summary,
        ranking_audit=tournament_rank_audit,
    )
    canonical_files: list[Path] = []
    canonical_report_root = (
        project_root / "results/reports"
    ).resolve()
    if output_root.resolve() == canonical_report_root:
        canonical_files = _publish_canonical_aliases(
            project_root,
            output_root,
            rated,
        )
    return {
        "status": "complete",
        "output_root": str(output_root),
        "players": len(rated),
        "teams": int(manifest.metadata["teams"]),
        "selected_layer": attention_summary["selected_layer"],
        "metric_gate_passed": attention_summary["metric_gate_passed"],
        "probabilistic_roles": {
            "k": probabilistic.selected_k,
            "covariance_type": probabilistic.selected_covariance_type,
        },
        "spearman_with_legacy_rankings": rank_rho,
        "artifact_files": [str(path) for path in manifest.files],
        "canonical_aliases": [str(path) for path in canonical_files],
    }


def parse_args() -> argparse.Namespace:
    """Parse the production and isolated-validation CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
    )
    parser.add_argument("--output-root", type=Path)
    parser.add_argument(
        "--skip-legacy-foundation",
        action="store_true",
        help="Read validated legacy artifacts without regenerating them.",
    )
    parser.add_argument("--reuse-validated-oof", action="store_true")
    parser.add_argument("--skip-metric-360", action="store_true")
    parser.add_argument("--enable-attention", action="store_true")
    parser.add_argument(
        "--attention-maximum-events",
        type=int,
        default=5_000,
    )
    parser.add_argument("--attention-epochs", type=int, default=40)
    parser.add_argument("--attention-folds", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    """Run the complete pipeline and print its artifact manifest."""

    args = parse_args()
    project_root = args.project_root.resolve()
    output_root = (
        args.output_root.resolve()
        if args.output_root is not None
        else project_root / "results/reports"
    )
    attention = AttentionConfig(
        enabled=args.enable_attention,
        maximum_events=args.attention_maximum_events,
        maximum_epochs=args.attention_epochs,
        cv_folds=args.attention_folds,
    )
    config = PipelineConfig(
        input_root=project_root,
        output_root=output_root,
        attention=attention,
    )
    result = run_extended_pipeline(
        config,
        skip_legacy_foundation=args.skip_legacy_foundation,
        reuse_validated_oof=args.reuse_validated_oof,
        recompute_metric_360=not args.skip_metric_360,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
