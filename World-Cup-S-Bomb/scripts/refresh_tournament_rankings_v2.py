#!/usr/bin/env python3
"""Refresh Qatar 2022 rankings and every ranking-dependent report.

This fast path consumes the already-validated player feature table.  The
production pipeline calls the same scoring functions before artifact
generation, so a later full run reproduces these outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.tournament_rankings import (  # noqa: E402
    TournamentRankingConfig,
    calculate_tournament_rankings_v2,
    tournament_ranking_audit,
)
from src.reporting.artifacts import (  # noqa: E402
    ArtifactGenerator,
    _atomic_text,
    _json_value,
    _slug,
)
from scripts.unify_tournament_ratings import (  # noqa: E402
    attach_unified_tournament_ratings,
)


def _source_path(project_root: Path) -> Path:
    candidates = (
        project_root / "results/reports/player_evaluations_v5.csv",
        project_root / "results/reports/canonical/player_rankings.csv",
        project_root / "results/reports/ranking/legacy/player_rankings.csv",
        project_root / "results/reports/ranking/player_rankings.csv",
    )
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError("No validated player ranking feature table found")


def _config_payload(
    config: TournamentRankingConfig,
    audit: dict[str, Any],
) -> dict[str, Any]:
    return {
        "scope": "2022 FIFA World Cup only",
        "tournament": "2022_World_Cup",
        "position_groups": ["GK", "CB", "FB", "DM", "CM", "AM", "FW"],
        "component_weights": {
            group: dict(weights)
            for group, weights in config.component_weights.items()
        },
        "goalkeeper_weights": dict(config.goalkeeper_weights),
        "goalkeeper_tournament_impact": {
            "shootout_save_points": 0.20,
            "vaep_percentile_maximum": 0.04,
            "high_leverage_volume_percentile_maximum": 0.02,
            "uses_player_identity": False,
            "uses_team_advancement": False,
        },
        "reliability_minutes": config.reliability_minutes,
        "target_forward_threshold": config.target_forward_threshold,
        "target_forward_maximum_boost": (
            config.target_forward_maximum_boost
        ),
        "audit": audit,
    }


def _archive_legacy_rankings(
    canonical_root: Path,
    ranking_root: Path,
) -> list[Path]:
    """Move verified legacy tables out of canonical without deleting them."""

    legacy_root = ranking_root / "legacy"
    archived: list[Path] = []
    for name in (
        "player_rankings.csv",
        "player_rankings_300plus.csv",
        "player_rankings.json",
    ):
        source = canonical_root / name
        if not source.is_file():
            continue
        legacy_root.mkdir(parents=True, exist_ok=True)
        destination = legacy_root / name
        if destination.exists():
            if hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(
                destination.read_bytes()
            ).digest():
                raise FileExistsError(
                    f"Refusing to overwrite different archive: {destination}"
                )
            source.unlink()
        else:
            source.replace(destination)
        archived.append(destination)
    return archived


def _refresh_release_manifest(
    project_root: Path,
    generated_files: list[Path],
) -> Path:
    """Refresh the active result inventory and remove retired path entries."""

    results_root = project_root / "results"
    manifest_path = results_root / "metadata/artifact_manifest.json"
    prior = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.is_file()
        else {}
    )
    retained = [
        results_root / relative
        for relative in prior.get("files", [])
        if (results_root / relative).is_file()
    ]
    inventory = sorted(
        {
            path.resolve()
            for path in (*retained, *generated_files)
            if path.is_file() and path.resolve().is_relative_to(results_root)
        }
    )
    relative_files = [
        path.relative_to(results_root).as_posix() for path in inventory
    ]
    payload = {
        "output_root": "results",
        "files": relative_files,
        "hashes": {
            relative: hashlib.sha256(
                (results_root / relative).read_bytes()
            ).hexdigest()
            for relative in relative_files
        },
        "schema_version": prior.get(
            "schema_version",
            "5.0-role-attention",
        ),
        "metadata": {
            **prior.get("metadata", {}),
            "active_ranking_root": "reports/ranking",
        },
    }
    _atomic_text(
        manifest_path,
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    )
    return manifest_path


def refresh(
    project_root: Path,
    *,
    archive_legacy_canonical: bool,
) -> dict[str, Any]:
    """Recompute rankings, validate them, and refresh dependent reports."""

    reports_root = project_root / "results/reports"
    canonical_root = reports_root / "canonical"
    ranking_root = reports_root / "ranking"
    source_path = _source_path(project_root)
    source = pd.read_csv(source_path)

    config = TournamentRankingConfig()
    rated = calculate_tournament_rankings_v2(source, config=config)
    audit = tournament_ranking_audit(rated, strict=True)
    rankings = ArtifactGenerator.prepare_rankings(rated)
    rankings = attach_unified_tournament_ratings(rankings)
    unified_validation = rankings.attrs["unified_validation"]
    generator = ArtifactGenerator(reports_root)
    files = generator._write_ranking_artifacts(rankings)

    model_json_path = canonical_root / "model_summary.json"
    model_summary = (
        json.loads(model_json_path.read_text(encoding="utf-8"))
        if model_json_path.is_file()
        else {}
    )
    model_summary["tournament_ranking_v2"] = _config_payload(config, audit)
    model_summary["unified_tournament_rating"] = unified_validation
    model_summary.setdefault("schema_version", "5.0-role-attention")
    _atomic_text(
        model_json_path,
        json.dumps(
            _json_value(model_summary),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
    )
    files.append(model_json_path)
    model_markdown_path = canonical_root / "model_summary.md"
    _atomic_text(
        model_markdown_path,
        generator._model_summary_markdown(model_summary),
    )
    files.append(model_markdown_path)
    for mirror, content in (
        (
            reports_root / "model_summary.json",
            model_json_path.read_text(encoding="utf-8"),
        ),
        (
            reports_root / "model_summary.md",
            model_markdown_path.read_text(encoding="utf-8"),
        ),
        (
            project_root / "results/Summary/model_summary.md",
            model_markdown_path.read_text(encoding="utf-8"),
        ),
    ):
        _atomic_text(mirror, content)
        files.append(mirror)

    team_metrics_path = canonical_root / "data/team_metrics_v2.csv"
    team_metrics = (
        pd.read_csv(team_metrics_path)
        if team_metrics_path.is_file()
        else None
    )
    teams = sorted(rankings["team"].dropna().astype(str).unique())
    final_summary_path = canonical_root / "final_summary.md"
    _atomic_text(
        final_summary_path,
        generator._final_summary(
            rankings,
            model_summary,
            teams=teams,
            team_metrics=team_metrics,
            team_player_pool=None,
        ),
    )
    files.append(final_summary_path)
    final_summary_text = final_summary_path.read_text(encoding="utf-8")
    for mirror in (
        reports_root / "final_summary.md",
        reports_root / "final/world_cup_team_performance_and_top_players.md",
    ):
        _atomic_text(mirror, final_summary_text)
        files.append(mirror)

    coaches_path = canonical_root / "coaches_notebook.md"
    _atomic_text(coaches_path, generator._coaches_notebook(rankings))
    files.append(coaches_path)

    team_metric_lookup = (
        {
            str(row["team"]): row
            for _, row in team_metrics.iterrows()
        }
        if team_metrics is not None and "team" in team_metrics
        else {}
    )
    team_root = reports_root / "team_profiles"
    for team in teams:
        team_players = rankings.loc[rankings["team"].eq(team)]
        path = team_root / f"{_slug(team)}.md"
        _atomic_text(
            path,
            generator._team_profile(
                team,
                team_players,
                team_players,
                team_metric_lookup.get(team),
            ),
        )
        files.append(path)

    player_root = reports_root / "player_profiles"
    for _, player in rankings.iterrows():
        identifier = (
            str(int(player["player_id"]))
            if "player_id" in player and pd.notna(player["player_id"])
            else str(int(player.get("position_rank_v2", 0)))
        )
        path = player_root / (
            f"{_slug(str(player['player_name']))}-{identifier}.md"
        )
        _atomic_text(path, generator._player_profile(player))
        files.append(path)

    files.extend(generator._generate_figures(rankings, model_summary))
    archived = (
        _archive_legacy_rankings(canonical_root, ranking_root)
        if archive_legacy_canonical
        else []
    )
    retained_legacy = sorted(
        {
            *archived,
            *(ranking_root / "legacy").glob("player_rankings*"),
        }
    )

    manifest_payload = {
        "tournament": "2022_World_Cup",
        "source": str(source_path.relative_to(project_root)),
        "players": len(rankings),
        "teams": len(teams),
        "audit_passed": audit["passed"],
        "files": {
            path.relative_to(project_root).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in files
        },
        "archived_legacy_files": [
            path.relative_to(project_root).as_posix()
            for path in retained_legacy
        ],
    }
    manifest_path = ranking_root / "refresh_manifest.json"
    _atomic_text(
        manifest_path,
        json.dumps(manifest_payload, indent=2, ensure_ascii=False) + "\n",
    )
    release_manifest_path = _refresh_release_manifest(
        project_root,
        [*files, manifest_path, *retained_legacy],
    )
    return {
        "status": "complete",
        "source": str(source_path),
        "players": len(rankings),
        "teams": len(teams),
        "audit": audit,
        "archived_legacy_files": manifest_payload[
            "archived_legacy_files"
        ],
        "manifest": str(manifest_path),
        "release_manifest": str(release_manifest_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
    )
    parser.add_argument(
        "--archive-legacy-canonical",
        action="store_true",
        help=(
            "After successful validation, move the old canonical ranking "
            "tables to results/reports/ranking/legacy/."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = refresh(
        args.project_root.resolve(),
        archive_legacy_canonical=args.archive_legacy_canonical,
    )
    print(json.dumps(_json_value(result), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
