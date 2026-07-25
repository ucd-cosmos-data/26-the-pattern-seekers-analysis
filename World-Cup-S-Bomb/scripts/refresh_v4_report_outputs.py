"""Refresh V4 player, starter, team, compiled, and final_v3 reports.

This intentionally reuses the validated 64-match OOF audit artifacts. It
recomputes only the player/spatial layer and report outputs, so ranking changes
do not waste time refitting the unchanged rare-event classifier folds.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_final_tournament_report import generate_report
from scripts.run_team_simulation_reports import (
    _load_inputs,
    _write_v4_model_summary,
)
from src.report_generators import (
    compile_v4_report_packets,
    generate_full_team_coaching_reports,
    generate_individual_starter_reports,
    generate_player_heatmap_svgs,
)
from src.simulation_engine import build_v4_player_evaluations


def refresh_reports(project_root: Path = PROJECT_ROOT) -> dict[str, object]:
    """Rebuild player-facing V4 outputs without refitting OOF models."""

    data = _load_inputs()
    profiles, heatmap_cells, event_audit, provenance = (
        build_v4_player_evaluations(
            data["components"],
            data["events"],
            data["frame_actors"],
            data["frame_metrics"],
        )
    )
    processed = project_root / "data/processed"
    profiles.to_csv(processed / "player_evaluations.csv", index=False)
    heatmap_cells.to_csv(processed / "player_heatmap_cells.csv", index=False)
    event_audit[
        [
            "match_id",
            "id",
            "player_id",
            "type",
            "turnover",
            "event_under_pressure",
            "freeze_frame_pressure",
            "pressure_augmented",
            "standard_turnover_penalty",
            "turnover_penalty_multiplier",
            "applied_turnover_penalty",
            "raw_on_ball_value",
            "risk_adjusted_on_ball_value",
        ]
    ].to_parquet(processed / "player_event_value_audit.parquet", index=False)
    (processed / "player_evaluation_provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )

    synergy = pd.read_parquet(processed / "player_synergy_matrix_v2.parquet")
    eligible = set(profiles["player_id"].astype(int))
    synergy = synergy[
        synergy["row_player_id"].isin(eligible)
        & synergy["column_player_id"].isin(eligible)
    ]
    audit = pd.read_csv(
        project_root / "results/audit/expected_vs_actual_team_summary_oof.csv"
    )
    recurrent = pd.read_csv(
        project_root / "results/audit/recurrent_tactical_mistakes_oof.csv"
    )
    optimized = pd.read_csv(
        project_root / "results/simulations/optimized_starting_lineups.csv"
    )
    substitutions = pd.read_parquet(
        project_root / "results/simulations/substitution_optimization.parquet"
    )
    suppressions = pd.read_parquet(
        project_root / "results/simulations/substitution_suppressions.parquet"
    )
    matchup = pd.read_csv(processed / "lineup_matchup_features_v2.csv")

    manifest_path = project_root / "results/reports/pipeline_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["player_evaluation_provenance"] = provenance
    manifest["counts"]["eligible_player_evaluations"] = len(profiles)
    manifest["checks"]["mbappe_first_forward"] = bool(
        profiles.loc[
            profiles["player"].str.contains("Mbapp", case=False, na=False),
            "position_rank",
        ].eq(1).all()
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    metadata = {
        "schema_version": 4,
        "model_version": manifest["model_version"],
        "target": manifest["target"],
        "calibration_method": manifest["calibration_method"],
        "threshold": manifest["threshold"],
        "threshold_status": manifest["threshold_status"],
        "holdout_metrics": manifest["locked_v2_holdout_metrics"],
        "oof_metrics": manifest["tournament_oof_metrics"],
        "player_evaluation": provenance,
    }

    reports = project_root / "results/reports"
    heatmaps = generate_player_heatmap_svgs(
        profiles, heatmap_cells, reports / "heatmaps", clear_existing=True
    )
    starters = generate_individual_starter_reports(
        profiles,
        synergy,
        reports / "starters",
        clear_existing=True,
    )
    teams = generate_full_team_coaching_reports(
        audit,
        optimized,
        substitutions,
        matchup,
        recurrent,
        reports / "teams",
        model_metadata=metadata,
        synergy=synergy,
        profiles=profiles,
        suppression_reasons=suppressions,
        clear_existing=True,
    )
    compiled = compile_v4_report_packets(
        reports / "teams", reports / "starters", reports / "compiled"
    )

    # Keep the established final_v3 delivery paths, but replace their stale V3
    # player layer with the current V4 evaluation and spatial roles.
    v3_teams = generate_full_team_coaching_reports(
        audit,
        optimized,
        substitutions,
        matchup,
        recurrent,
        reports / "v3/teams",
        model_metadata=metadata,
        synergy=synergy,
        profiles=profiles,
        suppression_reasons=suppressions,
        clear_existing=True,
    )
    (reports / "v3/pipeline_manifest_v3.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    _write_v4_model_summary(
        project_root / "results/Summary/v4_model_explanation_summary.md",
        provenance=provenance,
        profiles=profiles,
        oof_metrics=manifest["tournament_oof_metrics"],
        compiled_checks=compiled,
    )
    final_report = generate_report(
        project_root,
        Path(
            "results/reports/final_v3/"
            "world_cup_team_performance_and_top_players_v3.md"
        ),
    )
    mbappe = profiles[
        profiles["player"].str.contains("Mbapp", case=False, na=False)
    ].iloc[0]
    targets = profiles[
        profiles["player"].str.contains(
            "Mbapp|Hakimi|Dest", case=False, na=False
        )
    ][
        [
            "player",
            "functional_role",
            "position_rank",
            "position_impact_score",
        ]
    ].to_dict("records")
    return {
        "eligible_players": len(profiles),
        "heatmaps": heatmaps,
        "starter_reports": starters,
        "team_reports": teams,
        "v3_team_reports": v3_teams,
        "compiled_reports": compiled,
        "final_report": str(final_report),
        "mbappe_forward_rank": int(mbappe["position_rank"]),
        "target_players": targets,
    }


if __name__ == "__main__":
    print(json.dumps(refresh_reports(), indent=2, ensure_ascii=False))
