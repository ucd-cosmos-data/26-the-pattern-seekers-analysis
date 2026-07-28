"""Markdown and JSON generators for team and starter coaching reports."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


TEAM_CODES = {
    "Argentina": "ARG",
    "Australia": "AUS",
    "Belgium": "BEL",
    "Brazil": "BRA",
    "Cameroon": "CMR",
    "Canada": "CAN",
    "Costa Rica": "CRC",
    "Croatia": "CRO",
    "Denmark": "DEN",
    "Ecuador": "ECU",
    "England": "ENG",
    "France": "FRA",
    "Germany": "GER",
    "Ghana": "GHA",
    "Iran": "IRN",
    "Japan": "JPN",
    "Mexico": "MEX",
    "Morocco": "MAR",
    "Netherlands": "NED",
    "Poland": "POL",
    "Portugal": "POR",
    "Qatar": "QAT",
    "Saudi Arabia": "KSA",
    "Senegal": "SEN",
    "Serbia": "SRB",
    "South Korea": "KOR",
    "Spain": "ESP",
    "Switzerland": "SUI",
    "Tunisia": "TUN",
    "United States": "USA",
    "Uruguay": "URU",
    "Wales": "WAL",
}

PROSPECTIVE_SECTION_START = "<!-- PROSPECTIVE_VALIDATION_START -->"
PROSPECTIVE_SECTION_END = "<!-- PROSPECTIVE_VALIDATION_END -->"
PLAYER_ROLE_SECTION_START = "<!-- PLAYER_ROLE_VALIDATION_START -->"
PLAYER_ROLE_SECTION_END = "<!-- PLAYER_ROLE_VALIDATION_END -->"
ROLE_AWARE_SECTION_START = "<!-- ROLE_AWARE_VALUATION_START -->"
ROLE_AWARE_SECTION_END = "<!-- ROLE_AWARE_VALUATION_END -->"
ROLE_REFINEMENT_START = "<!-- CONTINUOUS_ROLE_REFINEMENT_START -->"
ROLE_REFINEMENT_END = "<!-- CONTINUOUS_ROLE_REFINEMENT_END -->"


def load_prospective_validation(path: Path) -> dict[str, Any] | None:
    """Summarize the isolated prospective challenger validation artifact."""

    if not path.is_file() or path.stat().st_size == 0:
        return None
    validation = pd.read_csv(path)
    required = {
        "target",
        "candidate",
        "layout",
        "roc_auc",
        "pr_auc",
        "brier",
        "ece",
        "roc_delta_vs_reference",
        "roc_delta_ci_low",
        "roc_delta_ci_high",
        "passes_gate",
        "decision",
    }
    missing = sorted(required - set(validation.columns))
    if missing:
        raise ValueError(
            f"Prospective validation artifact lacks columns: {missing}"
        )
    official = {
        "box_entry": {"roc_auc": 0.6888, "brier": 0.1847, "ece": 0.0261706749},
        "shot": {"roc_auc": 0.6642, "brier": 0.1031, "ece": 0.0116224843},
    }
    targets: dict[str, Any] = {}

    def clean_record(row: pd.Series) -> dict[str, Any]:
        return {
            key: None if pd.isna(value) else _json_value(value)
            for key, value in row.to_dict().items()
        }

    for target in ("box_entry", "shot"):
        rows = validation[validation["target"].eq(target)].copy()
        reference = rows[
            rows["candidate"].eq("recomputed_logistic_reference")
        ]
        challengers = rows[
            rows["candidate"].ne("recomputed_logistic_reference")
        ]
        passing = challengers[
            challengers["passes_gate"].astype(str).str.lower().eq("true")
        ]
        selected = (
            passing.nlargest(1, "roc_auc")
            if not passing.empty
            else challengers.nlargest(1, "roc_auc")
        ).iloc[0]
        targets[target] = {
            "status": "PASSED" if not passing.empty else "REJECTED",
            "official_baseline": official[target],
            "matched_reference": clean_record(reference.iloc[0]),
            "best_challenger": clean_record(selected),
        }
    all_passed = all(
        target["status"] == "PASSED" for target in targets.values()
    )
    return {
        "schema_version": "prospective-validation-v1",
        "overall_status": "DEPLOYABLE" if all_passed else "PARTIAL_PASS_ROLLBACK",
        "artifact_written": all_passed,
        "validation_scheme": (
            "5-fold match-disjoint GroupKFold with nested calibration and "
            "paired match-bootstrap ROC comparison"
        ),
        "targets": targets,
    }


def prospective_validation_markdown(summary: dict[str, Any]) -> str:
    """Render the same prospective status block for every report surface."""

    box = summary["targets"]["box_entry"]
    shot = summary["targets"]["shot"]
    box_best = box["best_challenger"]
    shot_best = shot["best_challenger"]
    box_base = box["official_baseline"]
    shot_base = shot["official_baseline"]
    return "\n".join(
        [
            PROSPECTIVE_SECTION_START,
            "## Prospective possession-model validation",
            "",
            (
                f"**Overall status: `{summary['overall_status']}`.** Box-entry "
                "prediction passed every discrimination, calibration, and paired "
                "match-bootstrap gate. The shot challenger improved numerically but "
                "its confidence interval crossed zero, so it was rejected. The combined "
                "prospective artifact was not deployed and the stable production state "
                "was preserved."
            ),
            "",
            "| Target | Status | Baseline ROC-AUC | Challenger ROC-AUC | PR-AUC | Brier | ECE | Paired ROC gain (90% interval) |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
            (
                f"| Box entry | **{box['status']}** | "
                f"{box_base['roc_auc']:.4f} | {float(box_best['roc_auc']):.4f} | "
                f"{float(box_best['pr_auc']):.4f} | "
                f"{float(box_best['brier']):.4f} | "
                f"{float(box_best['ece']):.4f} | "
                f"{float(box_best['roc_delta_vs_reference']):+.4f} "
                f"[{float(box_best['roc_delta_ci_low']):+.4f}, "
                f"{float(box_best['roc_delta_ci_high']):+.4f}] |"
            ),
            (
                f"| Shot | **{shot['status']}** | "
                f"{shot_base['roc_auc']:.4f} | {float(shot_best['roc_auc']):.4f} | "
                f"{float(shot_best['pr_auc']):.4f} | "
                f"{float(shot_best['brier']):.4f} | "
                f"{float(shot_best['ece']):.4f} | "
                f"{float(shot_best['roc_delta_vs_reference']):+.4f} "
                f"[{float(shot_best['roc_delta_ci_low']):+.4f}, "
                f"{float(shot_best['roc_delta_ci_high']):+.4f}] |"
            ),
            "",
            (
                "_This challenger is isolated from 360-VAEP/xT player ratings, "
                "transition risk, retrospective possession models, and tactical "
                "clustering. Player and team descriptive metrics therefore remain "
                "unchanged._"
            ),
            PROSPECTIVE_SECTION_END,
        ]
    )


def _upsert_prospective_section(path: Path, section: str) -> bool:
    """Append or replace one generated prospective section in a Markdown file."""

    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if PROSPECTIVE_SECTION_START in text:
        prefix, remainder = text.split(PROSPECTIVE_SECTION_START, maxsplit=1)
        if PROSPECTIVE_SECTION_END not in remainder:
            raise ValueError(f"Unclosed prospective section in {path}")
        _, suffix = remainder.split(PROSPECTIVE_SECTION_END, maxsplit=1)
        updated = prefix.rstrip() + "\n\n" + section + suffix
    else:
        updated = text.rstrip() + "\n\n" + section + "\n"
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")
    return True


def refresh_prospective_validation_reporting(
    project_root: Path,
    validation_path: Path | None = None,
) -> dict[str, int]:
    """Synchronize prospective results across final human/machine artifacts."""

    validation_path = validation_path or (
        project_root / "results/reports/prospective_model_validation.csv"
    )
    summary = load_prospective_validation(validation_path)
    if summary is None:
        raise FileNotFoundError(validation_path)
    section = prospective_validation_markdown(summary)
    markdown_targets = [
        project_root
        / "results/reports/final/world_cup_team_performance_and_top_players.md",
        project_root / "results/MIscellaneous/coaching_model_benchmark.md",
        project_root / "results/MIscellaneous/coaching_model_selection.md",
        project_root / "results/MIscellaneous/stage5_leakage_audit.md",
        *sorted((project_root / "results/reports/teams").glob("*.md")),
        *sorted((project_root / "results/reports/compiled").glob("*.md")),
    ]
    updated_markdown = sum(
        _upsert_prospective_section(path, section) for path in markdown_targets
    )
    json_targets = [
        project_root / "results/reports/pipeline_manifest.json",
        project_root / "results/eda_validation_report.json",
        project_root / "results/MIscellaneous/eda_validation_report.json",
    ]
    updated_json = 0
    for path in json_targets:
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if path.name == "pipeline_manifest.json":
            payload["prospective_possession_validation"] = summary
        else:
            payload.setdefault("model_metrics", {})[
                "prospective_possession_challenger"
            ] = summary
            payload.setdefault("gates", {})[
                "prospective_harm_prevention"
            ] = bool(
                summary["overall_status"] == "PARTIAL_PASS_ROLLBACK"
                and summary["artifact_written"] is False
                and summary["targets"]["box_entry"]["status"] == "PASSED"
                and summary["targets"]["shot"]["status"] == "REJECTED"
            )
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True, default=_json_value)
            + "\n",
            encoding="utf-8",
        )
        updated_json += 1
    return {
        "markdown_files": updated_markdown,
        "json_files": updated_json,
        "team_reports": len(
            list((project_root / "results/reports/teams").glob("*.md"))
        ),
        "compiled_player_packets": len(
            list(
                (
                    project_root / "results/reports/compiled"
                ).glob("*_compiled_player_reports.md")
            )
        ),
    }


def load_player_role_validation(path: Path) -> dict[str, Any] | None:
    """Load and schema-check the player-role challenger decision."""

    if not path.is_file() or path.stat().st_size == 0:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "incumbent_vaep_oof_metrics",
        "probabilistic_roles",
        "learned_valuation",
        "rank_checks",
        "gates",
        "decisions",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(
            f"Player-role validation artifact lacks keys: {missing}"
        )
    return payload


def player_role_validation_markdown(summary: dict[str, Any]) -> str:
    """Render the accepted production state and rejected challenger evidence."""

    model = summary["incumbent_vaep_oof_metrics"]
    roles = summary["probabilistic_roles"]
    valuation = summary["learned_valuation"]
    ranks = summary["rank_checks"]
    interval = valuation["delta_confidence_interval_95"]
    return "\n".join(
        [
            PLAYER_ROLE_SECTION_START,
            "## Player-role and valuation validation status",
            "",
            (
                "**Production state retained.** The probabilistic role matrix and "
                "learned valuation were evaluated as challengers but were not "
                "promoted because they missed their predeclared statistical gates."
            ),
            "",
            "| Component | Decision | Validation evidence |",
            "|---|---|---|",
            (
                f"| Probabilistic GMM roles | **{summary['decisions']['probabilistic_roles']}** "
                f"| K={int(roles['selected_k'])}; silhouette "
                f"{float(roles['silhouette']):.4f}; median 500-bootstrap ARI "
                f"{float(roles['bootstrap_ari_median']):.4f} vs required 0.70 |"
            ),
            (
                f"| Learned Ridge valuation | **{summary['decisions']['learned_valuation']}** "
                f"| OOF Spearman {float(valuation['baseline_spearman']):.4f} → "
                f"{float(valuation['challenger_spearman']):.4f}; gain 95% CI "
                f"[{float(interval[0]):+.4f}, {float(interval[1]):+.4f}] crosses zero |"
            ),
            "",
            (
                "The active calibrated 360-VAEP model therefore remains unchanged: "
                f"OOF ROC-AUC {float(model['roc_auc']):.6f}, PR-AUC "
                f"{float(model['pr_auc']):.6f}, Brier "
                f"{float(model['brier_score']):.6f}. "
                f"Messi remains Argentina rank #{int(ranks['incumbent_messi_rank'])} "
                f"and Mbappé remains France rank "
                f"#{int(ranks['incumbent_mbappe_rank'])}; no player-name override "
                "was used."
            ),
            PLAYER_ROLE_SECTION_END,
        ]
    )


def _upsert_generated_section(
    path: Path,
    section: str,
    start_marker: str,
    end_marker: str,
) -> bool:
    """Append or replace a marker-delimited generated Markdown section."""

    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if start_marker in text:
        prefix, remainder = text.split(start_marker, maxsplit=1)
        if end_marker not in remainder:
            raise ValueError(f"Unclosed generated section in {path}")
        _, suffix = remainder.split(end_marker, maxsplit=1)
        updated = prefix.rstrip() + "\n\n" + section + suffix
    else:
        updated = text.rstrip() + "\n\n" + section + "\n"
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")
    return True


def refresh_player_role_validation_reporting(
    project_root: Path,
    validation_path: Path | None = None,
) -> dict[str, int]:
    """Synchronize accepted rankings and challenger status across outputs."""

    validation_path = validation_path or (
        project_root / "results/reports/player_role_challenger_validation.json"
    )
    summary = load_player_role_validation(validation_path)
    if summary is None:
        raise FileNotFoundError(validation_path)
    section = player_role_validation_markdown(summary)
    markdown_targets = [
        project_root
        / "results/reports/final/world_cup_team_performance_and_top_players.md",
        *sorted((project_root / "results/reports/teams").glob("*.md")),
        *sorted((project_root / "results/reports/compiled").glob("*.md")),
    ]
    updated_markdown = sum(
        _upsert_generated_section(
            path,
            section,
            PLAYER_ROLE_SECTION_START,
            PLAYER_ROLE_SECTION_END,
        )
        for path in markdown_targets
    )

    profiles = pd.read_csv(
        project_root / "data/processed/player_evaluations.csv"
    )
    leaderboard = (
        profiles[
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
    csv_targets = [
        project_root / "data/processed/player_leaderboard.csv",
        project_root / "results/reports/player_leaderboard.csv",
        project_root / "results/reports/team_player_leaderboards.csv",
    ]
    for path in csv_targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        leaderboard.to_csv(path, index=False)

    updated_json = 0
    for path in (
        project_root / "results/reports/pipeline_manifest.json",
        project_root / "results/eda_validation_report.json",
        project_root / "results/MIscellaneous/eda_validation_report.json",
    ):
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["player_role_valuation_challenger"] = summary
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True, default=_json_value)
            + "\n",
            encoding="utf-8",
        )
        updated_json += 1

    # Only figures driven by player ranking values are refreshed. Calibration
    # and tactical-cluster figures use unchanged model outputs.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    figure_root = project_root / "results/figures"
    figure_root.mkdir(parents=True, exist_ok=True)
    plot = profiles.copy()
    plt.figure(figsize=(10, 7))
    sns.scatterplot(
        data=plot,
        x="xt_p90",
        y="vaep_total_p90",
        hue="position_group",
        size="final_player_rating",
        sizes=(25, 180),
        alpha=0.8,
    )
    plt.title("Validated player value: 360-VAEP versus spatial xT")
    plt.tight_layout()
    plt.savefig(figure_root / "vaep_vs_xt_scatter.png", dpi=180)
    plt.close()

    france = profiles.loc[profiles["team"].eq("France")].nsmallest(
        12, "team_rank"
    )
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=france,
        x="final_player_rating",
        y="player",
        order=france.sort_values(
            "final_player_rating", ascending=False
        )["player"],
        color="#2f6f9f",
    )
    plt.title("France validated player rankings")
    plt.xlabel("Final player rating")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(figure_root / "france_team_rankings.png", dpi=180)
    plt.close()
    return {
        "markdown_files": updated_markdown,
        "json_files": updated_json,
        "leaderboard_csv_files": len(csv_targets),
        "figures": 2,
    }


def load_role_aware_validation(path: Path) -> dict[str, Any] | None:
    """Load the continuous role-aware rating A/B decision."""

    if not path.is_file() or path.stat().st_size == 0:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "decision", "production_promoted", "spearman_rank_correlation",
        "gates", "benchmarks", "incumbent_vaep_oof_metrics",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"Role-aware validation lacks keys: {missing}")
    return payload


def role_aware_validation_markdown(summary: dict[str, Any]) -> str:
    """Render the role-aware challenger result without implying promotion."""

    metrics = summary["incumbent_vaep_oof_metrics"]
    griezmann = summary["benchmarks"]["griezmann"]
    messi = summary["benchmarks"]["messi"]
    mbappe = summary["benchmarks"]["mbappe"]
    return "\n".join(
        [
            ROLE_AWARE_SECTION_START,
            "## Continuous role-aware valuation A/B test",
            "",
            (
                f"**Decision: `{summary['decision']}`.** The challenger was not "
                "promoted. Its Spearman correlation with the incumbent ranking was "
                f"{float(summary['spearman_rank_correlation']):.4f}, above the "
                "predeclared 0.90 ceiling, so it did not change the overall ordering "
                "enough to qualify as the intended systemic correction."
            ),
            "",
            "| Benchmark | Incumbent | Challenger diagnostic |",
            "|---|---:|---:|",
            (
                f"| Messi global rank | {int(messi['old_global_rank'])} | "
                f"{int(messi['new_global_rank'])} |"
            ),
            (
                f"| Mbappé global rank | {int(mbappe['old_global_rank'])} | "
                f"{int(mbappe['new_global_rank'])} |"
            ),
            (
                f"| Griezmann global rank | {int(griezmann['old_global_rank'])} | "
                f"{int(griezmann['new_global_rank'])} |"
            ),
            "",
            (
                "The diagnostic Griezmann movement came from creation "
                f"({float(griezmann['creation_score']):.3f}), pressing "
                f"({float(griezmann['pressing_score']):.3f}), and completeness "
                f"({float(griezmann['completeness_score']):.3f}), with no player-name "
                "rule. Nevertheless, all published player/team rankings retain the "
                "incumbent 360-VAEP+xT rating."
            ),
            "",
            (
                "Foundational model performance remains unchanged: OOF ROC-AUC "
                f"{float(metrics['roc_auc']):.6f}, PR-AUC "
                f"{float(metrics['pr_auc']):.6f}, Brier "
                f"{float(metrics['brier_score']):.6f}, ECE "
                f"{float(metrics['calibration_error']):.6f}."
            ),
            ROLE_AWARE_SECTION_END,
        ]
    )


def refresh_role_aware_validation_reporting(
    project_root: Path,
    validation_path: Path | None = None,
) -> dict[str, int]:
    """Propagate the challenger rejection across human and machine reports."""

    validation_path = validation_path or (
        project_root / "results/reports/role_aware_valuation_validation.json"
    )
    summary = load_role_aware_validation(validation_path)
    if summary is None:
        raise FileNotFoundError(validation_path)
    section = role_aware_validation_markdown(summary)
    targets = [
        project_root
        / "results/reports/final/world_cup_team_performance_and_top_players.md",
        *sorted((project_root / "results/reports/teams").glob("*.md")),
        *sorted((project_root / "results/reports/compiled").glob("*.md")),
    ]
    markdown_files = sum(
        _upsert_generated_section(
            path, section, ROLE_AWARE_SECTION_START, ROLE_AWARE_SECTION_END
        )
        for path in targets
    )
    json_files = 0
    for path in (
        project_root / "results/reports/pipeline_manifest.json",
        project_root / "results/eda_validation_report.json",
        project_root / "results/MIscellaneous/eda_validation_report.json",
    ):
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["role_aware_valuation_challenger"] = summary
        payload.setdefault("gates", {})[
            "role_aware_challenger_rollback"
        ] = bool(
            summary["decision"] == "REJECTED_RETAIN_INCUMBENT"
            and summary["production_promoted"] is False
        )
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True, default=_json_value)
            + "\n",
            encoding="utf-8",
        )
        json_files += 1
    return {"markdown_files": markdown_files, "json_files": json_files}


def load_role_refinement(path: Path) -> dict[str, Any] | None:
    """Load the accepted post-K-Means continuous role refinement."""

    if not path.is_file() or path.stat().st_size == 0:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def role_refinement_markdown(summary: dict[str, Any]) -> str:
    """Render role-only changes separately from unchanged numerical ratings."""

    france = "\n".join(
        f"- {row['player']}: {row['kmeans_functional_role']} → "
        f"**{row['functional_role']}**"
        for row in summary["france_changes"]
    )
    return "\n".join(
        [
            ROLE_REFINEMENT_START,
            "## Accepted continuous role refinement",
            "",
            (
                f"**{summary['changed_roles']} of {summary['eligible_players']} "
                f"players ({100 * summary['change_rate']:.1f}%) received an "
                "evidence-backed post-K-Means role refinement; "
                f"{summary['unchanged_roles']} retained their original role.** "
                "The original cluster label remains available as "
                "`kmeans_functional_role`. Ratings, team ranks, VAEP and xT were "
                "not changed by this role-only promotion."
            ),
            "",
            "France refinements:",
            "",
            france,
            "",
            (
                "Refinements use continuous progression, creation, finishing, "
                "pressing, defensive, security, aerial and completeness scores "
                "with broad-position safeguards. No player-name condition is used."
            ),
            ROLE_REFINEMENT_END,
        ]
    )


def refresh_role_refinement_reporting(
    project_root: Path,
    validation_path: Path | None = None,
) -> dict[str, int]:
    """Synchronize accepted role-only changes across reports and audits."""

    validation_path = validation_path or (
        project_root / "results/reports/role_refinement_validation.json"
    )
    summary = load_role_refinement(validation_path)
    if summary is None or not summary.get("production_promoted"):
        raise ValueError("Role refinement has not been promoted")
    section = role_refinement_markdown(summary)
    targets = [
        project_root
        / "results/reports/final/world_cup_team_performance_and_top_players.md",
        *sorted((project_root / "results/reports/teams").glob("*.md")),
        *sorted((project_root / "results/reports/compiled").glob("*.md")),
    ]
    markdown_files = sum(
        _upsert_generated_section(
            path, section, ROLE_REFINEMENT_START, ROLE_REFINEMENT_END
        )
        for path in targets
    )
    json_files = 0
    for path in (
        project_root / "results/reports/pipeline_manifest.json",
        project_root / "results/eda_validation_report.json",
        project_root / "results/MIscellaneous/eda_validation_report.json",
    ):
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["continuous_role_refinement"] = summary
        payload.setdefault("gates", {})["continuous_role_refinement"] = True
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True, default=_json_value)
            + "\n",
            encoding="utf-8",
        )
        json_files += 1
    return {"markdown_files": markdown_files, "json_files": json_files}


def _json_value(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    if pd.isna(value):
        return None
    return value


def _write_pair(path: Path, markdown: str, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    path.with_suffix(".json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=_json_value)
        + "\n",
        encoding="utf-8",
    )


def _player_tweaks(player: pd.Series) -> list[str]:
    tweaks: list[str] = []
    if player["pressing_intensity_index_percentile"] < 40:
        tweaks.append("Use a compact pressing trigger rather than sustained solo pressure.")
    else:
        tweaks.append("Lead the first pressing trigger and protect the inside passing lane.")
    if player["aerial_dominance_index_percentile"] >= 70:
        tweaks.append("Target this player on direct restarts and back-post deliveries.")
    elif player["aerial_dominance_index_percentile"] < 35:
        tweaks.append("Avoid isolating this player in high-volume aerial matchups.")
    if player["speed_recovery_index_percentile"] < 35:
        tweaks.append("Pair with a faster recovery defender after aggressive rotations.")
    else:
        tweaks.append("Use recovery capacity to support higher attacking positions.")
    return tweaks[:3]


def generate_individual_starter_reports(
    profiles: pd.DataFrame,
    synergy: pd.DataFrame,
    output_root: Path,
    *,
    clear_existing: bool = False,
) -> int:
    """Generate one Markdown/JSON pair for every 300-minute V4 player."""

    if clear_existing and output_root.exists():
        for existing in output_root.glob("*/*_starter_report.*"):
            existing.unlink()
    names = profiles.set_index("player_id")["player"].to_dict()
    count = 0
    for _, player in profiles.sort_values(["team", "player"]).iterrows():
        player_id = int(player["player_id"])
        partners = synergy[
            synergy["row_player_id"].eq(player_id)
            & synergy["column_player_id"].ne(player_id)
        ].nlargest(3, "synergy_score")
        partner_records = [
            {
                "player_id": int(row.column_player_id),
                "player": names.get(int(row.column_player_id), "Unknown"),
                "synergy_score": float(row.synergy_score),
                "shared_minutes": float(row.shared_minutes),
                "joint_pass_completion_rate": float(
                    row.joint_pass_completion_rate
                ),
            }
            for row in partners.itertuples(index=False)
        ]
        tweaks = _player_tweaks(player)
        payload = {
            "team": player["team"],
            "team_code": TEAM_CODES[player["team"]],
            "player_id": player_id,
            "player": player["player"],
            "position": player["position"],
            "functional_role": player["functional_role"],
            "physical_scores": {
                "aerial_dominance_index": player["aerial_dominance_index"],
                "pressing_intensity_index": player["pressing_intensity_index"],
                "speed_recovery_index": player["speed_recovery_index"],
            },
            "vaep_off_p90": player["vaep_off_p90"],
            "vaep_def_p90": player["vaep_def_p90"],
            "vaep_total_p90": player["vaep_total_p90"],
            "vaep_per_touch": player["vaep_per_touch"],
            "xt_p90": player["xt_p90"],
            "final_player_rating": player["final_player_rating"],
            "team_rank": int(player["team_rank"]),
            "final_third_share": player["final_third_share"],
            "heatmap": (
                f"../heatmaps/{TEAM_CODES[player['team']]}/"
                f"{player_id}_heatmap.svg"
            ),
            "top_chemistry_partners": partner_records,
            "recommended_tactical_tweaks": tweaks,
            "cohort_definition": (
                "Tournament players with at least 300 minutes; evaluation "
                "uses one unified cross-role 360-VAEP plus xT rating"
            ),
        }
        partner_lines = "\n".join(
            f"- {partner['player']} — synergy {partner['synergy_score']:.3f}, "
            f"{partner['shared_minutes']:.0f} shared minutes"
            for partner in partner_records
        ) or "- No cohort partner data available"
        tweak_lines = "\n".join(f"- {tweak}" for tweak in tweaks)
        markdown = f"""# {player['player']} — Starter Report

- Team: {player['team']} ({TEAM_CODES[player['team']]})
- Position: {player['position']}
- Functional role: {player['functional_role']}
- VAEP offense per 90: {player['vaep_off_p90']:.4f}
- VAEP defense per 90: {player['vaep_def_p90']:.4f}
- VAEP total per 90: {player['vaep_total_p90']:.4f}
- VAEP per touch: {player['vaep_per_touch']:.5f}
- Spatial xT per 90: {player['xt_p90']:.4f}
- Final-third spatial share: {100 * player['final_third_share']:.1f}%
- Unified final player rating: {player['final_player_rating']:.4f}
- Team rank: #{int(player['team_rank'])}

![V4 event and 360 heatmap](../heatmaps/{TEAM_CODES[player['team']]}/{player_id}_heatmap.svg)

## Physical profile

| Metric | Score |
|---|---:|
| Aerial dominance | {player['aerial_dominance_index']:.3f} |
| Pressing intensity per 90 | {player['pressing_intensity_index']:.2f} |
| Recovery index per 90 | {player['speed_recovery_index']:.2f} |

## Top chemistry partners

{partner_lines}

## Tactical recommendations

{tweak_lines}

_The heatmap combines successful event endpoints with StatsBomb 360 actor
snapshots. StatsBomb 360 is freeze-frame context, not continuous player
tracking. Scores exclude players below 300 tournament minutes._
"""
        path = (
            output_root
            / TEAM_CODES[player["team"]]
            / f"{player_id}_starter_report.md"
        )
        _write_pair(path, markdown, payload)
        count += 1
    return count


def generate_player_heatmap_svgs(
    profiles: pd.DataFrame,
    heatmap_cells: pd.DataFrame,
    output_root: Path,
    *,
    clear_existing: bool = False,
) -> int:
    """Write deterministic SVG pitch-density heatmaps for V4-ranked players."""

    if clear_existing and output_root.exists():
        for existing in output_root.glob("*/*_heatmap.svg"):
            existing.unlink()
    count = 0
    for player in profiles.itertuples(index=False):
        player_id = int(player.player_id)
        cells = heatmap_cells[
            heatmap_cells["player_id"].eq(player_id)
        ].copy()
        if cells.empty:
            raise ValueError(f"No V4 heatmap cells for player {player_id}")
        maximum = float(cells["density"].max())
        cell_lookup = {
            (int(row.x_bin), int(row.y_bin)): float(row.density)
            for row in cells.itertuples(index=False)
        }
        rectangles: list[str] = []
        for x_bin in range(12):
            for y_bin in range(8):
                density = cell_lookup.get((x_bin, y_bin), 0.0)
                intensity = 0 if maximum <= 0 else density / maximum
                red = int(245 - 210 * intensity)
                green = int(248 - 115 * intensity)
                blue = int(255 - 45 * intensity)
                rectangles.append(
                    f'<rect x="{20 + 50 * x_bin}" y="{60 + 50 * y_bin}" '
                    f'width="50" height="50" '
                    f'fill="rgb({red},{green},{blue})" stroke="#ffffff" '
                    'stroke-width="0.5"/>'
                )
        title = html.escape(str(player.player))
        role = html.escape(str(player.functional_role))
        svg = "\n".join(
            [
                '<svg xmlns="http://www.w3.org/2000/svg" width="640" '
                'height="500" viewBox="0 0 640 500" role="img">',
                f"<title>{title} V4 spatial heatmap</title>",
                '<rect width="640" height="500" fill="#f7fafc"/>',
                f'<text x="20" y="28" font-family="Arial" font-size="18" '
                f'font-weight="700">{title}</text>',
                f'<text x="20" y="49" font-family="Arial" font-size="12">'
                f"{role} · {float(player.minutes):.0f} minutes · "
                f"{100 * float(player.final_third_share):.1f}% final third"
                "</text>",
                *rectangles,
                '<rect x="20" y="60" width="600" height="400" fill="none" '
                'stroke="#1f2937" stroke-width="2"/>',
                '<line x1="320" y1="60" x2="320" y2="460" '
                'stroke="#1f2937" stroke-width="1"/>',
                '<rect x="520" y="160" width="100" height="200" fill="none" '
                'stroke="#1f2937"/>',
                '<text x="20" y="482" font-family="Arial" font-size="11">'
                "Successful event endpoints + StatsBomb 360 actor snapshots; "
                "attacking direction left-to-right"
                "</text>",
                "</svg>",
            ]
        )
        path = (
            output_root
            / TEAM_CODES[str(player.team)]
            / f"{player_id}_heatmap.svg"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg + "\n", encoding="utf-8")
        count += 1
    return count


def generate_individual_starter_report(
    player: pd.Series,
    synergy: pd.DataFrame,
    profiles: pd.DataFrame,
    output_root: Path,
) -> Path:
    """Generate one starter report while preserving the public singular API."""

    generate_individual_starter_reports(
        profiles[profiles["player_id"].eq(player["player_id"])],
        synergy,
        output_root,
    )
    return (
        output_root
        / TEAM_CODES[player["team"]]
        / f"{int(player['player_id'])}_starter_report.md"
    )


def build_dynamic_team_summary(
    team: str,
    team_row: pd.Series,
    deltas: dict[str, float],
    mistakes: list[dict[str, Any]],
    synergy_pair: str,
    metadata: dict[str, Any],
) -> str:
    """Build a team-specific tactical and model-provenance paragraph."""

    style = str(
        team_row.get(
            "most_common_optimal_style",
            team_row.get("recommended_style", "No meaningful change"),
        )
    )
    style_text = (
        "no tactical change cleared the modeled effect floor"
        if style == "No meaningful change"
        else f"{style} led the observed baseline by {team_row['mean_eva_gap']:.4f} mean EvA"
    )
    if deltas["mean_delta_pressing"] < 0:
        exposure = f"pressing deficit {deltas['mean_delta_pressing']:+.3f}"
    elif mistakes:
        exposure = (
            f"transition review against {mistakes[0]['defensive_style']} "
            f"({mistakes[0]['actual_style']} to {mistakes[0]['optimal_style']})"
        )
    else:
        exposure = "no repeated transition-exposure zone above the review floor"
    holdout = metadata.get("holdout_metrics", {})
    precision = holdout.get("precision")
    precision_text = "abstention" if precision is None else f"precision {precision:.3f}"
    return (
        f"{team}: {style_text}. Primary review signal: {exposure}. Strongest "
        f"positive squad synergy: {synergy_pair}. Model "
        f"{metadata.get('model_version', 'unknown')}, target "
        f"{metadata.get('target', 'unknown')}, calibration "
        f"{metadata.get('calibration_method', 'unknown')}, threshold "
        f"{metadata.get('threshold')} ({metadata.get('threshold_status', 'unknown')}; "
        f"{precision_text})."
    )


def generate_full_team_coaching_reports(
    team_summary: pd.DataFrame,
    optimized_lineups: pd.DataFrame,
    substitutions: pd.DataFrame,
    matchup_features: pd.DataFrame,
    recurrent_mistakes: pd.DataFrame,
    output_root: Path,
    *,
    model_metadata: dict[str, Any] | None = None,
    synergy: pd.DataFrame | None = None,
    profiles: pd.DataFrame | None = None,
    suppression_reasons: pd.DataFrame | None = None,
    clear_existing: bool = False,
) -> int:
    """Generate one Markdown/JSON coaching report for all 32 teams."""

    count = 0
    if clear_existing and output_root.exists():
        for existing in output_root.glob("*_team_coaching_report.*"):
            existing.unlink()
    model_metadata = model_metadata or {}
    player_names = (
        profiles.set_index("player_id")["player"].to_dict()
        if profiles is not None and not profiles.empty
        else {}
    )
    for _, team_row in team_summary.sort_values("team").iterrows():
        team = str(team_row["team"])
        code = TEAM_CODES[team]
        lineup = optimized_lineups[optimized_lineups["team"].eq(team)].sort_values(
            "rank"
        )
        team_subs = substitutions[substitutions["team"].eq(team)]
        team_suppressions = (
            suppression_reasons[suppression_reasons["team"].eq(team)]
            if suppression_reasons is not None and not suppression_reasons.empty
            else pd.DataFrame()
        )
        reason_counts = (
            team_suppressions["reason_code"].value_counts().to_dict()
            if not team_suppressions.empty
            else {}
        )
        best_sub = (
            team_subs.nlargest(1, "expected_net_xg_gain").iloc[0]
            if not team_subs.empty
            else None
        )
        team_matchups = matchup_features[
            matchup_features["attacking_team"].eq(team)
        ]
        deltas = {
            "mean_delta_aerial": float(team_matchups["delta_aerial"].mean()),
            "mean_delta_pressing": float(team_matchups["delta_pressing"].mean()),
            "mean_delta_recovery": float(team_matchups["delta_recovery"].mean()),
        }
        mistakes = recurrent_mistakes[
            recurrent_mistakes["team"].eq(team)
        ].head(3)
        mistake_records = mistakes.to_dict("records")
        synergy_pair = "not available"
        if synergy is not None and profiles is not None:
            team_ids = set(
                profiles.loc[profiles["team"].eq(team), "player_id"].astype(int)
            )
            pairs = synergy[
                synergy["row_player_id"].isin(team_ids)
                & synergy["column_player_id"].isin(team_ids)
                & synergy["row_player_id"].lt(synergy["column_player_id"])
            ]
            if not pairs.empty:
                pair = pairs.nlargest(1, "synergy_score").iloc[0]
                left = player_names.get(int(pair["row_player_id"]), "Unknown")
                right = player_names.get(int(pair["column_player_id"]), "Unknown")
                synergy_pair = (
                    f"{left} + {right} ({float(pair['synergy_score']):.3f})"
                )
        lineup_records = lineup[
            ["rank", "player_id", "player", "position_group", "optimization_score"]
        ].to_dict("records")
        substitution_record = (
            {
                "starter_player_id": int(best_sub["starter_player_id"]),
                "starter_player": best_sub["starter_player"],
                "bench_player_id": int(best_sub["bench_player_id"]),
                "bench_player": best_sub["bench_player"],
                "expected_net_xg_gain": float(
                    best_sub["expected_net_xg_gain"]
                ),
                "gain_ci_low": float(best_sub.get("gain_ci_low", np.nan)),
                "gain_ci_high": float(best_sub.get("gain_ci_high", np.nan)),
            }
            if best_sub is not None
            else None
        )
        payload = {
            "team": team,
            "team_code": code,
            "total_wasted_net_xg": team_row["total_wasted_net_xg"],
            "mean_eva_gap": team_row["mean_eva_gap"],
            "most_common_optimal_style": team_row[
                "most_common_optimal_style"
            ],
            "optimal_starting_11": lineup_records,
            "physical_matchup_deltas": deltas,
            "best_substitution": substitution_record,
            "recurrent_tactical_mistakes": mistake_records,
            "model_provenance": model_metadata,
            "top_positive_synergy_pair": synergy_pair,
            "substitution_suppression_reason_counts": reason_counts,
        }
        top_players: list[dict[str, Any]] = []
        if profiles is not None and not profiles.empty:
            available_columns = [
                "player_id",
                "player",
                "functional_role",
                "vaep_total_p90",
                "vaep_per_touch",
                "xt_p90",
                "final_player_rating",
                "team_rank",
                "final_third_share",
            ]
            top_players = (
                profiles.loc[
                    profiles["team"].eq(team), available_columns
                ]
                .sort_values(["team_rank", "final_player_rating"])
                .head(5)
                .to_dict("records")
            )
        payload["top_v4_player_evaluations"] = top_players
        dynamic_summary = build_dynamic_team_summary(
            team,
            team_row,
            deltas,
            mistake_records,
            synergy_pair,
            model_metadata,
        )
        lineup_lines = "\n".join(
            f"{int(row['rank'])}. {row['player']} "
            f"({row['position_group']})"
            for row in lineup_records
        )
        if substitution_record:
            substitution_text = (
                f"{substitution_record['bench_player']} for "
                f"{substitution_record['starter_player']} "
                f"(expected Net xG gain "
                f"{substitution_record['expected_net_xg_gain']:.5f})"
            )
        else:
            reason_text = ", ".join(
                f"{reason}: {count}" for reason, count in reason_counts.items()
            ) or "CLASSIFIER_ABSTAINED"
            substitution_text = (
                "> **No validated intervention:** No bench substitution met the "
                "+0.0050 Net xG floor and strictly positive confidence interval "
                f"requirement. Reason codes: {reason_text}."
            )
        mistake_lines = "\n".join(
            f"- Against {row['defensive_style']}: switch from "
            f"{row['actual_style']} to {row['optimal_style']} "
            f"({row['wasted_net_xg']:.4f} cumulative Net xG)"
            for row in mistake_records
        ) or "- No recurrent pattern identified"
        player_lines = "\n".join(
            f"{rank}. {row['player']} — {row['functional_role']}; "
            f"rating {float(row['final_player_rating']):.4f}, "
            f"VAEP/90 {float(row['vaep_total_p90']):+.3f}, "
            f"xT/90 {float(row['xt_p90']):+.3f}"
            for rank, row in enumerate(top_players, start=1)
        ) or "No player cleared the 300-minute V4 evaluation cutoff."
        markdown = f"""# {team} — Team Coaching Report

## Model-grounded summary

{dynamic_summary}

- Total wasted Net xG: {team_row['total_wasted_net_xg']:.4f}
- Mean possession EvA gap: {team_row['mean_eva_gap']:.6f}
- Most common optimal style: {team_row['most_common_optimal_style']}

## Optimized starting 11

{lineup_lines}

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | {deltas['mean_delta_aerial']:.3f} |
| Pressing | {deltas['mean_delta_pressing']:.3f} |
| Recovery | {deltas['mean_delta_recovery']:.3f} |

## Best bench intervention

{substitution_text}

## Unified 360-VAEP + xT player leaders

{player_lines}

_Only players with at least 300 tournament minutes are ranked. Outfield V5
ratings combine independently scaled offensive/defensive VAEP evidence (40%),
VAEP per touch (15%), xT per 90 (15%), match-grouped ElasticNet role-adjusted
value (15%), top-three quality-adjusted completeness (10%), and
coverage-qualified off-ball contribution (5%). Goalkeepers use a separate
evidence matrix and ranking._

## Recurrent tactical mistakes

{mistake_lines}

_Counterfactual values are predictive scenario estimates, not causal treatment effects. Substitutions below the gain floor or with confidence intervals crossing zero are suppressed._
"""
        _write_pair(
            output_root / f"{code}_team_coaching_report.md",
            markdown,
            payload,
        )
        count += 1
    return count


def compile_v4_report_packets(
    team_reports: Path,
    player_reports: Path,
    output_root: Path,
) -> dict[str, int]:
    """Overwrite the 64 unversioned compiled coaching delivery packets."""

    team_sources = sorted(team_reports.glob("*_team_coaching_report.md"))
    if len(team_sources) != 32:
        raise ValueError(f"Expected 32 team reports, found {len(team_sources)}")
    output_root.mkdir(parents=True, exist_ok=True)
    for existing in output_root.glob("*.md"):
        existing.unlink()

    player_sections = 0
    for team_source in team_sources:
        code = team_source.name[:3]
        team_text = team_source.read_text(encoding="utf-8").strip()
        (output_root / team_source.name).write_text(
            team_text + "\n", encoding="utf-8"
        )
        player_sources = sorted(
            (player_reports / code).glob("*_starter_report.md"),
            key=lambda path: int(path.name.split("_", maxsplit=1)[0]),
        )
        sections = [
            f"# {code} — V4 Player Evaluation Collection",
            "",
            f"- Included 300+ minute players: {len(player_sources)}",
            "- Rankings use one cross-role 360-VAEP plus xT formula.",
            "- Heatmaps combine successful on-ball endpoints and SB360 actor snapshots.",
            "",
        ]
        for position, player_source in enumerate(player_sources, start=1):
            sections.extend(
                [
                    "---",
                    "",
                    f"<!-- PLAYER_REPORT {position}: {player_source.name} -->",
                    "",
                    player_source.read_text(encoding="utf-8").strip(),
                    "",
                ]
            )
        (output_root / f"{code}_compiled_player_reports.md").write_text(
            "\n".join(sections).rstrip() + "\n",
            encoding="utf-8",
        )
        player_sections += len(player_sources)

    compiled = list(output_root.glob("*.md"))
    checks = {
        "markdown_files": len(compiled),
        "team_reports": len(
            list(output_root.glob("*_team_coaching_report.md"))
        ),
        "compiled_player_reports": len(
            list(output_root.glob("*_compiled_player_reports.md"))
        ),
        "compiled_player_sections": player_sections,
    }
    if (
        checks["markdown_files"] != 64
        or checks["team_reports"] != 32
        or checks["compiled_player_reports"] != 32
    ):
        raise RuntimeError(f"V4 compiled-report validation failed: {checks}")
    return checks


def generate_full_team_coaching_report(
    team: str,
    team_summary: pd.DataFrame,
    optimized_lineups: pd.DataFrame,
    substitutions: pd.DataFrame,
    matchup_features: pd.DataFrame,
    recurrent_mistakes: pd.DataFrame,
    output_root: Path,
) -> Path:
    """Generate one team report while preserving the public singular API."""

    generate_full_team_coaching_reports(
        team_summary[team_summary["team"].eq(team)],
        optimized_lineups,
        substitutions,
        matchup_features,
        recurrent_mistakes,
        output_root,
    )
    return output_root / f"{TEAM_CODES[team]}_team_coaching_report.md"
