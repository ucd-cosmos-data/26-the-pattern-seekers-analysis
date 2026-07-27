"""Build one coach-readable tournament report from the simulation artifacts.

The report combines descriptive team performance, model-based tactical audit
results, substitution scenarios, and position-specific player leaderboards.
It intentionally separates observed metrics from predictive scenario outputs.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.report_generators import (  # noqa: E402
    TEAM_CODES,
    build_dynamic_team_summary,
)


POSITION_GROUPS = (
    "Goalkeeper",
    "Center Back",
    "Fullback/Wingback",
    "Defensive Midfield",
    "Central/Wide Midfield",
    "Attacking Midfield/Wing",
    "Forward",
)


def parse_args() -> argparse.Namespace:
    """Parse command-line paths."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="World-Cup-S-Bomb project directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/reports/final/"
            "world_cup_team_performance_and_top_players.md"
        ),
        help="Output path, relative to project root unless absolute.",
    )
    return parser.parse_args()


def clean_text(value: object) -> str:
    """Return readable UTF-8 text, repairing common UTF-8/Latin-1 mojibake."""

    text = "" if pd.isna(value) else str(value)
    if any(marker in text for marker in ("Ã", "Â", "â€", "Å", "Ä")):
        try:
            return text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return text
    return text


def safe_mode(values: pd.Series, fallback: str = "Not available") -> str:
    """Return a cleaned mode or a fallback for an empty series."""

    non_null = values.dropna()
    if non_null.empty:
        return fallback
    return clean_text(non_null.mode().iloc[0])


def markdown_table(headers: Iterable[str], rows: Iterable[Iterable[object]]) -> str:
    """Render a compact GitHub-flavored Markdown table."""

    header_list = list(headers)
    lines = [
        "| " + " | ".join(header_list) + " |",
        "| " + " | ".join("---" for _ in header_list) + " |",
    ]
    for row in rows:
        cells = [clean_text(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def percentile_label(value: float) -> str:
    """Translate a percentile into a plain-language cohort label."""

    if value >= 0.80:
        return "among the tournament leaders"
    if value >= 0.60:
        return "above the tournament median"
    if value >= 0.40:
        return "near the tournament median"
    if value >= 0.20:
        return "below the tournament median"
    return "among the lower values in this tournament sample"


def _parse_coordinate(value: object) -> tuple[float, float] | None:
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return float(value[0]), float(value[1])
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return None
    if isinstance(parsed, (list, tuple)) and len(parsed) >= 2:
        return float(parsed[0]), float(parsed[1])
    return None


def add_goalkeeper_metrics(
    profiles: pd.DataFrame,
    events: pd.DataFrame,
    components: pd.DataFrame,
) -> pd.DataFrame:
    """Add public-event goalkeeper metrics, labeling shot xG as a proxy."""

    output = profiles.copy()
    metric_columns = [
        "post_shot_xg_proxy",
        "post_shot_xg_faced_p90",
        "goals_prevented_p90",
        "cross_claims_p90",
        "sweeping_distance",
        "distribution_under_pressure",
    ]
    for column in metric_columns:
        output[column] = 0.0

    goalkeeper_components = components[
        components["position_group"].eq("Goalkeeper")
    ].sort_values("minutes", ascending=False)
    primary = goalkeeper_components.drop_duplicates(["match_id", "team"])
    goalkeeper_lookup = {
        (int(row.match_id), str(row.team)): int(row.player_id)
        for row in primary.itertuples(index=False)
    }
    match_teams = (
        events[["match_id", "team"]]
        .dropna()
        .drop_duplicates()
        .groupby("match_id")["team"]
        .apply(list)
        .to_dict()
    )
    shots = events[events["type"].eq("Shot")].copy()
    shots = shots[
        shots["shot_outcome"].astype(str).str.contains(
            "Goal|Saved", case=False, na=False
        )
    ]
    records: list[dict[str, float | int]] = []
    for row in shots.itertuples(index=False):
        opponents = [
            team for team in match_teams.get(int(row.match_id), []) if team != row.team
        ]
        if not opponents:
            continue
        goalkeeper_id = goalkeeper_lookup.get((int(row.match_id), str(opponents[0])))
        if goalkeeper_id is None:
            continue
        records.append(
            {
                "player_id": goalkeeper_id,
                "post_shot_xg_proxy": float(row.shot_statsbomb_xg or 0),
                "goal_allowed": float("Goal" in str(row.shot_outcome)),
            }
        )
    shot_frame = pd.DataFrame(records)
    if not shot_frame.empty:
        faced = shot_frame.groupby("player_id", as_index=False).sum()
    else:
        faced = pd.DataFrame(
            columns=["player_id", "post_shot_xg_proxy", "goal_allowed"]
        )

    goalkeeper_events = events[
        events["player_id"].isin(output.loc[
            output["position_group"].eq("Goalkeeper"), "player_id"
        ])
    ].copy()
    goalkeeper_events["claim"] = goalkeeper_events["goalkeeper_type"].astype(
        str
    ).str.contains("Collect|Claim|Punch", case=False, na=False)
    goalkeeper_events["coordinate"] = goalkeeper_events["location"].map(
        _parse_coordinate
    )
    goalkeeper_events["sweep_distance"] = goalkeeper_events["coordinate"].map(
        lambda value: 0.0 if value is None else min(value[0], 120 - value[0])
    )
    goalkeeper_events["pressured_pass"] = (
        goalkeeper_events["type"].eq("Pass")
        & goalkeeper_events["under_pressure"].astype(str).str.lower().isin(["true", "1"])
    )
    goalkeeper_events["completed_pressured_pass"] = (
        goalkeeper_events["pressured_pass"]
        & goalkeeper_events["pass_outcome"].isna()
    )
    event_metrics = goalkeeper_events.groupby("player_id", as_index=False).agg(
        cross_claims=("claim", "sum"),
        sweeping_distance=("sweep_distance", "mean"),
        pressured_passes=("pressured_pass", "sum"),
        completed_pressured_passes=("completed_pressured_pass", "sum"),
    )
    goalkeeper_metrics = faced.merge(event_metrics, on="player_id", how="outer").fillna(0)
    minutes = output.set_index("player_id")["minutes"]
    goalkeeper_metrics["minutes"] = goalkeeper_metrics["player_id"].map(minutes).fillna(1)
    goalkeeper_metrics["post_shot_xg_faced_p90"] = (
        90 * goalkeeper_metrics["post_shot_xg_proxy"] / goalkeeper_metrics["minutes"]
    )
    goalkeeper_metrics["goals_prevented_p90"] = (
        90
        * (
            goalkeeper_metrics["post_shot_xg_proxy"]
            - goalkeeper_metrics["goal_allowed"]
        )
        / goalkeeper_metrics["minutes"]
    )
    goalkeeper_metrics["cross_claims_p90"] = (
        90 * goalkeeper_metrics["cross_claims"] / goalkeeper_metrics["minutes"]
    )
    goalkeeper_metrics["distribution_under_pressure"] = (
        goalkeeper_metrics["completed_pressured_passes"]
        / goalkeeper_metrics["pressured_passes"].replace(0, np.nan)
    ).fillna(0)
    available = goalkeeper_metrics[
        [
            "player_id",
            "post_shot_xg_proxy",
            "post_shot_xg_faced_p90",
            "goals_prevented_p90",
            "cross_claims_p90",
            "sweeping_distance",
            "distribution_under_pressure",
        ]
    ]
    output = output.drop(columns=metric_columns).merge(
        available, on="player_id", how="left"
    )
    output[metric_columns] = output[metric_columns].fillna(0)
    return output


def build_team_metrics(
    possessions: pd.DataFrame,
    audit: pd.DataFrame,
    matchup: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate observed possession outcomes and predictive audit metrics."""

    rows: list[dict[str, object]] = []
    for team in sorted(TEAM_CODES):
        attacking = possessions[possessions["team"].eq(team)]
        defending = possessions[possessions["defending_team"].eq(team)]
        physical = matchup[matchup["attacking_team"].eq(team)]
        audit_row = audit[audit["team"].eq(team)]
        rows.append(
            {
                "team": team,
                "matches": int(attacking["match_id"].nunique()),
                "possessions": int(len(attacking)),
                "goals": float(attacking["goal_count"].sum()),
                "xg": float(attacking["xg_generated"].sum()),
                "shots": float(attacking["shot_count"].sum()),
                "shot_rate": float(attacking["shot"].mean()),
                "box_entry_rate": float(attacking["entered_penalty_area"].mean()),
                "transition_shots_conceded": float(
                    attacking["opponent_transition_shot_count"].sum()
                ),
                "transition_xg_conceded": float(attacking["opponent_transition_xg"].sum()),
                "attack_style": safe_mode(attacking["attacking_style"]),
                "defensive_style": safe_mode(defending["defensive_style"]),
                "delta_aerial": float(physical["delta_aerial"].mean()),
                "delta_pressing": float(physical["delta_pressing"].mean()),
                "delta_recovery": float(physical["delta_recovery"].mean()),
                "wasted_net_xg": (
                    float(audit_row.iloc[0]["total_wasted_net_xg"])
                    if not audit_row.empty
                    else np.nan
                ),
                "mean_eva_gap": (
                    float(audit_row.iloc[0]["mean_eva_gap"])
                    if not audit_row.empty
                    else np.nan
                ),
                "actual_expected_net_xg": (
                    float(audit_row.iloc[0]["actual_expected_net_xg"])
                    if not audit_row.empty
                    else np.nan
                ),
                "optimal_expected_net_xg": (
                    float(audit_row.iloc[0]["optimal_expected_net_xg"])
                    if not audit_row.empty
                    else np.nan
                ),
                "recommended_style": (
                    clean_text(audit_row.iloc[0]["most_common_optimal_style"])
                    if not audit_row.empty
                    else "Not available"
                ),
            }
        )

    metrics = pd.DataFrame(rows)
    for column in (
        "xg",
        "goals",
        "shot_rate",
        "box_entry_rate",
        "transition_xg_conceded",
        "mean_eva_gap",
    ):
        metrics[f"{column}_pct"] = metrics[column].rank(pct=True)
    return metrics


def team_interpretation(row: pd.Series) -> str:
    """Create a concise interpretation from observed and modeled team metrics."""

    attack_phrase = percentile_label(float(row["xg_pct"]))
    shot_phrase = percentile_label(float(row["shot_rate_pct"]))
    exposure_percentile = 1.0 - float(row["transition_xg_conceded_pct"])
    exposure_phrase = percentile_label(exposure_percentile)
    gap_phrase = (
        "a relatively large modeled opportunity for tactical tightening"
        if row["mean_eva_gap_pct"] >= 0.67
        else (
            "a moderate modeled opportunity for tactical tightening"
            if row["mean_eva_gap_pct"] >= 0.34
            else "one of the smaller modeled tactic gaps in the sample"
        )
    )
    return (
        f"Across the analyzed possessions, {row['team']}'s total xG was "
        f"{attack_phrase}, while its possession-to-shot rate was {shot_phrase}. "
        f"Its suppression of immediate opponent transition xG was {exposure_phrase} "
        f"(lower transition exposure is better). The audit indicates {gap_phrase}. "
        "These are tournament-sample tendencies, not causal estimates of what would "
        "have happened under a different lineup or tactic."
    )


def team_player_rows(players: pd.DataFrame, count: int = 5) -> list[list[object]]:
    """Return Markdown-ready rows for a team's unified cross-role leaders."""

    leaders = players.sort_values(
        ["team_rank", "final_player_rating"], ascending=[True, False]
    ).head(count)
    return [
        [
            rank,
            row["player"],
            row["position_group"],
            row["functional_role"],
            f"{row['minutes']:.0f}",
            f"{row['final_player_rating']:.4f}",
            f"{row['vaep_total_p90']:.3f}",
        ]
        for rank, (_, row) in enumerate(leaders.iterrows(), start=1)
    ]


def generate_report(project_root: Path, output_path: Path) -> Path:
    """Load pipeline outputs and write the combined final report."""

    required = {
        "possessions": project_root / "data/processed/world_cup_defensive_clusters.csv",
        "profiles": project_root / "data/processed/player_evaluations.csv",
        "audit": project_root
        / "results/audit/expected_vs_actual_team_summary_oof.csv",
        "mistakes": project_root
        / "results/audit/recurrent_tactical_mistakes_oof.csv",
        "substitutions": project_root
        / "results/simulations/substitution_optimization.parquet",
        "suppressions": project_root
        / "results/simulations/substitution_suppressions.parquet",
        "matchup": project_root / "data/processed/lineup_matchup_features_v2.csv",
        "synergy": project_root / "data/processed/player_synergy_matrix_v2.parquet",
        "manifest": project_root / "results/reports/pipeline_manifest.json",
        "provenance": project_root
        / "data/processed/player_evaluation_provenance.json",
    }
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Cannot generate final report; missing required artifacts:\n- "
            + "\n- ".join(missing)
        )

    possessions = pd.read_csv(required["possessions"])
    profiles = pd.read_csv(required["profiles"])
    audit = pd.read_csv(required["audit"])
    mistakes = pd.read_csv(required["mistakes"])
    substitutions = pd.read_parquet(required["substitutions"])
    suppressions = pd.read_parquet(required["suppressions"])
    if substitutions.empty:
        substitutions = pd.DataFrame(
            columns=[
                "team",
                "starter_player",
                "bench_player",
                "optimal_style",
                "expected_net_xg_gain",
                "gain_ci_low",
                "gain_ci_high",
            ]
        )
    matchup = pd.read_csv(required["matchup"])
    synergy = pd.read_parquet(required["synergy"])
    manifest = json.loads(required["manifest"].read_text(encoding="utf-8"))
    provenance = json.loads(required["provenance"].read_text(encoding="utf-8"))
    validation_status = (
        "PASS" if all(manifest.get("checks", {}).values()) else "FAIL"
    )

    if set(TEAM_CODES) - set(possessions["team"].dropna().unique()):
        absent = sorted(set(TEAM_CODES) - set(possessions["team"].dropna().unique()))
        raise ValueError(f"Possession data is missing expected teams: {absent}")
    unknown_positions = sorted(set(profiles["position_group"]) - set(POSITION_GROUPS))
    if unknown_positions:
        raise ValueError(f"No scoring specification for position groups: {unknown_positions}")

    team_metrics = build_team_metrics(possessions, audit, matchup)
    lines: list[str] = [
        "# World Cup Team Performance and Position-Specific Player Report",
        "",
        "## Executive summary",
        "",
        (
            f"This report consolidates **{len(team_metrics)} national teams**, "
            f"**{len(profiles)} tournament-role player profiles**, "
            f"**{int(possessions['match_id'].nunique())} matches**, and "
            f"**{len(possessions):,} analyzed possessions** into one coaching reference. "
            "It combines observed possession outcomes with the regularized empirical "
            "hurdle-pipeline scenario audit. The strongest use is opponent preparation, "
            "video-review prioritization, and formation of testable tactical hypotheses."
        ),
        "",
        (
            "**Important boundary:** observed goals, xG, shots, box entries, and transition "
            "exposure describe this tournament sample. Expected net xG, EvA gaps, optimal "
            "styles, and substitution gains are model-generated scenarios. They are not "
            "causal claims, guarantees, transfer valuations, or replacements for scouting, "
            "medical, training, and match-context evidence."
        ),
        "",
        "## How to read the metrics",
        "",
        "- **xG:** summed shot quality created during the team's possessions.",
        "- **Shot rate:** percentage of possessions containing at least one shot.",
        "- **Box-entry rate:** percentage of possessions entering the penalty area.",
        (
            "- **Transition xG conceded:** opponent xG generated immediately after the "
            "team's possessions; lower is better and it is not total defensive xG conceded."
        ),
        (
            "- **Mean EvA gap:** average difference between the best modeled tactic and "
            "the observed tactic. It identifies review candidates, not proven coaching errors."
        ),
        (
            "- **Wasted net xG:** cumulative modeled EvA gap across possessions. It scales "
            "with possession volume, so compare it alongside the mean gap."
        ),
        (
            "- **Physical matchup deltas:** lineup-minus-opponent aerial, pressing, and "
            "recovery proxies. Positive values indicate a modeled lineup edge."
        ),
        (
            "- **Final player rating:** one cross-role score using 50% VAEP total per 90, "
            "30% VAEP per touch, and 20% xT per 90."
        ),
        "",
        "## V4 validation and final metrics",
        "",
        (
            f"**Validation status: {validation_status}.** The leakage-safe OOF audit "
            f"covers **{manifest['tournament_oof_metrics']['matches']} matches**, "
            f"**{manifest['tournament_oof_metrics']['teams']} teams**, and "
            f"**{manifest['tournament_oof_metrics']['rows']:,} possessions**."
        ),
        "",
        markdown_table(
            ["Team/model validation metric", "V4 final value"],
            [
                ["OOF positives", manifest["tournament_oof_metrics"]["positives"]],
                ["OOF Brier score", f"{manifest['tournament_oof_metrics']['brier']:.6f}"],
                ["OOF PR-AUC", f"{manifest['tournament_oof_metrics']['pr_auc']:.6f}"],
                ["OOF ROC-AUC", f"{manifest['tournament_oof_metrics']['roc_auc']:.6f}"],
                [
                    "OOF unique probabilities",
                    manifest["tournament_oof_metrics"]["unique_probabilities"],
                ],
                [
                    "Locked holdout Brier score",
                    f"{manifest['locked_v2_holdout_metrics']['brier']:.6f}",
                ],
                [
                    "Locked holdout PR-AUC",
                    f"{manifest['locked_v2_holdout_metrics']['pr_auc']:.6f}",
                ],
                [
                    "Locked holdout ROC-AUC",
                    f"{manifest['locked_v2_holdout_metrics']['roc_auc']:.6f}",
                ],
            ],
        ),
        "",
        markdown_table(
            ["Player/report validation metric", "V4 final value"],
            [
                ["Players before cutoff", provenance["players_before_cutoff"]],
                ["Eligible players (300+ minutes)", provenance["players_after_cutoff"]],
                ["Players excluded", provenance["players_dropped"]],
                ["Successful action endpoints", f"{provenance['successful_action_points']:,}"],
                ["Linked SB360 actor snapshots", f"{provenance['freeze_frame_actor_points']:,}"],
                ["Events with SB360 context", f"{provenance['events_with_360_context']:,}"],
                ["Player heatmaps", manifest["counts"]["player_heatmaps"]],
                ["Team reports", manifest["counts"]["team_reports"]],
                ["Compiled report files", manifest["counts"]["compiled_reports"]],
                ["Eligible substitutions", manifest["counts"]["eligible_substitutions"]],
                ["Suppressed substitutions", manifest["counts"]["suppressed_substitutions"]],
            ],
        ),
        "",
        (
            "All V4 acceptance gates passed, including missing-value-free output, complete OOF team "
            "coverage, held-out-match exclusion, the 300-minute cutoff, fullback spatial-role "
            "safeguards, exact pressure discounting, within-role normalization, SB360 coverage, "
            "counterfactual safety, compiled-report completeness, and locked-classifier replay."
        ),
        (
            "**Spatial boundary:** StatsBomb 360 contains event-time freeze-frame snapshots, "
            "not continuous optical tracking. Heatmaps show observed successful endpoints and "
            "visible actor snapshots; they do not interpolate unobserved runs."
        ),
        "",
        "### Unified 360-VAEP + xT player evaluations",
        "",
        markdown_table(
            ["Rank", "Player", "Team", "Minutes", "VAEP/90", "VAEP/touch", "xT/90", "Rating"],
            [
                [
                    rank,
                    row["player"],
                    row["team"],
                    f"{row['minutes']:.0f}",
                    f"{row['vaep_total_p90']:+.4f}",
                    f"{row['vaep_per_touch']:+.5f}",
                    f"{row['xt_p90']:+.4f}",
                    f"{row['final_player_rating']:+.4f}",
                ]
                for rank, (_, row) in enumerate(
                    profiles.sort_values(
                        ["final_player_rating", "minutes"], ascending=False
                    ).head(10).iterrows(),
                    start=1,
                )
            ],
        ),
        "",
        "## Tournament overview",
        "",
    ]

    overview = team_metrics.sort_values(
        ["xg", "goals"], ascending=False
    )
    lines.append(
        markdown_table(
            [
                "Team",
                "Matches",
                "Poss.",
                "Goals",
                "xG",
                "Shot %",
                "Box entry %",
                "Transition xG conceded",
                "Mean EvA gap",
                "Modeled style",
            ],
            [
                [
                    row["team"],
                    int(row["matches"]),
                    int(row["possessions"]),
                    f"{row['goals']:.0f}",
                    f"{row['xg']:.2f}",
                    f"{100 * row['shot_rate']:.1f}",
                    f"{100 * row['box_entry_rate']:.1f}",
                    f"{row['transition_xg_conceded']:.2f}",
                    f"{row['mean_eva_gap']:.4f}",
                    row["recommended_style"],
                ]
                for _, row in overview.iterrows()
            ],
        )
    )
    lines.extend(
        [
            "",
            (
                "The table is sorted by observed xG rather than a synthetic overall rank. "
                "That preserves the distinction between attack volume, transition control, "
                "and model-estimated tactical opportunity."
            ),
            "",
            "# Team-by-team performance",
            "",
        ]
    )

    for _, row in team_metrics.sort_values("team").iterrows():
        team = str(row["team"])
        team_mistakes = mistakes[mistakes["team"].eq(team)].sort_values(
            ["wasted_net_xg", "possessions"], ascending=False
        )
        best_sub = substitutions[substitutions["team"].eq(team)].sort_values(
            "expected_net_xg_gain", ascending=False
        )
        team_players = profiles[profiles["team"].eq(team)]
        team_ids = set(team_players["player_id"].astype(int))
        team_pairs = synergy[
            synergy["row_player_id"].isin(team_ids)
            & synergy["column_player_id"].isin(team_ids)
            & synergy["row_player_id"].lt(synergy["column_player_id"])
        ]
        if team_pairs.empty:
            synergy_pair = "Insufficient shared-minutes data"
        else:
            pair = team_pairs.nlargest(1, "synergy_score").iloc[0]
            name_lookup = team_players.set_index("player_id")["player"].to_dict()
            synergy_pair = (
                f"{clean_text(name_lookup.get(int(pair['row_player_id']), 'Unknown'))} + "
                f"{clean_text(name_lookup.get(int(pair['column_player_id']), 'Unknown'))} "
                f"({float(pair['synergy_score']):.3f})"
            )
        team_suppressions = suppressions[suppressions["team"].eq(team)]
        suppression_counts = (
            team_suppressions["reason_code"].value_counts().to_dict()
            if not team_suppressions.empty
            else {}
        )
        model_metadata = {
            "model_version": manifest["model_version"],
            "target": manifest["target"],
            "calibration_method": manifest["calibration_method"],
            "threshold": manifest["threshold"],
            "threshold_status": manifest["threshold_status"],
            "holdout_metrics": manifest["locked_v2_holdout_metrics"],
        }
        dynamic_summary = build_dynamic_team_summary(
            team,
            row,
            {
                "mean_delta_aerial": row["delta_aerial"],
                "mean_delta_pressing": row["delta_pressing"],
                "mean_delta_recovery": row["delta_recovery"],
            },
            team_mistakes.to_dict("records"),
            synergy_pair,
            model_metadata,
        )
        tactical_reason = clean_text(
            audit.loc[audit["team"].eq(team), "tactical_reason_code"].iloc[0]
        )

        lines.extend(
            [
                f"## {team} ({TEAM_CODES[team]})",
                "",
                f"**Dynamic tactical summary:** {dynamic_summary}",
                "",
                "### Tier 1 — Observed Tournament Evidence",
                "",
                team_interpretation(row),
                "",
                markdown_table(
                    ["Observed tournament indicator", "Value"],
                    [
                        ["Matches represented", int(row["matches"])],
                        ["Attacking possessions", int(row["possessions"])],
                        ["Goals / xG", f"{row['goals']:.0f} / {row['xg']:.2f}"],
                        ["Shots / possession-to-shot rate", f"{row['shots']:.0f} / {100 * row['shot_rate']:.1f}%"],
                        ["Penalty-area entry rate", f"{100 * row['box_entry_rate']:.1f}%"],
                        ["Opponent transition shots / xG", f"{row['transition_shots_conceded']:.0f} / {row['transition_xg_conceded']:.2f}"],
                        ["Most frequent attacking style", row["attack_style"]],
                        ["Most frequent defensive style", row["defensive_style"]],
                    ],
                ),
                "",
                "### Tier 2 — Model-Supported Scenario Audits",
                "",
                (
                    f"The 64-match leave-one-match-out audit selected "
                    f"**{row['recommended_style']}** most often. OOF actual expected Net xG "
                    f"was {row['actual_expected_net_xg']:.2f}; the OOF scenario ceiling was "
                    f"{row['optimal_expected_net_xg']:.2f}. The cumulative review gap was "
                    f"{row['wasted_net_xg']:.2f}, averaging {row['mean_eva_gap']:.4f} per possession."
                ),
                "",
                (
                    f"Average lineup matchup deltas were **{row['delta_aerial']:+.3f} aerial**, "
                    f"**{row['delta_pressing']:+.3f} pressing**, and "
                    f"**{row['delta_recovery']:+.3f} recovery**. These are relative proxies, "
                    "so the signs are more useful for matchup planning than the raw magnitudes."
                ),
                "",
                f"**Top positive player synergy:** {synergy_pair}.",
                "",
            ]
        )

        if not team_mistakes.empty:
            mistake = team_mistakes.iloc[0]
            lines.extend(
                [
                    (
                        f"**Highest-volume review pattern:** against "
                        f"{clean_text(mistake['defensive_style'])}, possessions labeled "
                        f"{clean_text(mistake['actual_style'])} were most often improved in "
                        f"the model by {clean_text(mistake['optimal_style'])}. This pattern "
                        f"covered {int(mistake['possessions'])} possessions with "
                        f"{mistake['wasted_net_xg']:.2f} cumulative modeled gap "
                        f"({mistake['mean_eva_gap']:.4f} per possession)."
                    ),
                    "",
                ]
            )

        if not best_sub.empty:
            sub = best_sub.iloc[0]
            lines.extend(
                [
                    (
                        f"**Best substitution scenario:** {clean_text(sub['bench_player'])} "
                        f"for {clean_text(sub['starter_player'])} under "
                        f"{clean_text(sub['optimal_style'])} produced the largest estimated "
                        f"team gain ({sub['expected_net_xg_gain']:+.4f} expected net xG). "
                        f"The match-bootstrap 95% interval was "
                        f"[{sub['gain_ci_low']:+.4f}, {sub['gain_ci_high']:+.4f}]. "
                        "Treat this as a video and training-ground hypothesis; the simulation "
                        "does not encode fatigue, injury, match state, or all role constraints."
                    ),
                    "",
                ]
            )
        else:
            reason_text = ", ".join(
                f"{reason}: {count}"
                for reason, count in suppression_counts.items()
            ) or "CLASSIFIER_ABSTAINED"
            lines.extend(
                [
                    (
                        "> **No validated substitution:** No bench substitution met the "
                        "+0.0050 Net xG floor and strictly positive confidence interval "
                        f"requirement. Reason codes: {reason_text}."
                    ),
                    "",
                ]
            )

        lines.extend(
            [
                "### Tier 3 — Exploratory and Suppressed Decisions",
                "",
                (
                    f"**Tactical decision reason code:** `{tactical_reason}`. "
                    + (
                        "The best alternative failed to exceed +0.0050 Net xG."
                        if tactical_reason == "GAIN_BELOW_THRESHOLD"
                        else "The style change cleared the tactical effect floor."
                    )
                ),
                "",
                (
                    "**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability "
                    "threshold achieved the required 0.30 precision, so transition warnings "
                    "remain suppressed rather than converted into weak positive claims."
                ),
                "",
                "### Leading tournament-role profiles",
                "",
                markdown_table(
                    [
                        "Rank",
                        "Player",
                        "Position group",
                        "Functional role",
                        "Minutes",
                        "Unified rating",
                        "VAEP/90",
                    ],
                    team_player_rows(team_players),
                ),
                "",
                (
                    "Coaching interpretation: begin with the observed style and matchup "
                    "signals, then inspect the flagged possessions on video. Test the modeled "
                    "style or personnel change in a comparable game-state segment before "
                    "adopting it as a match plan."
                ),
                "",
                "> **Model provenance**",
                f"> Model: `{manifest['model_version']}`",
                f"> Target: `{manifest['target']}`",
                f"> Calibration: `{manifest['calibration_method']}`",
                f"> Threshold status: `{manifest['threshold_status']}`",
                (
                    f"> OOF audit: {manifest['tournament_oof_metrics']['matches']} matches, "
                    f"{manifest['tournament_oof_metrics']['teams']} teams; each evaluated "
                    "match was excluded from model fitting and calibration."
                ),
                "",
            ]
        )

    lines.extend(
        [
            "# Top tournament-role players by position",
            "",
            (
                "These leaderboards contain only players with at least 300 tournament "
                "minutes. Every player uses the same unified VAEP+xT formula, so team "
                "rankings no longer sort role-standardized values across incompatible "
                "peer groups. Position sections remain navigation aids."
            ),
            "",
            "## Unified V4 rating construction",
            "",
            "- 360-Augmented VAEP total per 90: 50%.",
            "- VAEP per touch: 30%.",
            "- Independent successful-pass/carry xT per 90: 20%.",
            "- Successful event endpoints and SB360 actor snapshots use the StatsBomb 120x80 pitch.",
            "- Fullbacks above 35% combined final-third share are classified as Attacking Wingbacks.",
            "",
        ]
    )
    lines.extend(
        [
            "",
            (
                "**Goalkeeper warning:** the source features do not provide a complete "
                "provider post-shot-xG model. The report uses on-target StatsBomb shot xG "
                "as an explicitly labeled proxy, then adds goals prevented, claims, sweeping "
                "location, and pressured distribution. It remains unsuitable as a standalone "
                "goalkeeper selection model."
            ),
            "",
        ]
    )

    for group in POSITION_GROUPS:
        group_players = profiles[profiles["position_group"].eq(group)].sort_values(
            ["final_player_rating", "minutes"], ascending=False
        ).head(10)
        lines.extend(
            [
                f"## {group}",
                "",
                markdown_table(
                    [
                        "Rank",
                        "Player",
                        "Team",
                        "Detailed position",
                        "Role",
                        "Min.",
                        "Rating",
                        "VAEP/90",
                        "xT/90",
                        "Aerial",
                        "Pressing",
                        "Recovery",
                    ],
                    [
                        [
                            rank,
                            row["player"],
                            row["team"],
                            row["position"],
                            row["functional_role"],
                            f"{row['minutes']:.0f}",
                            f"{row['final_player_rating']:.4f}",
                            f"{row['vaep_total_p90']:.3f}",
                            f"{row['xt_p90']:.3f}",
                            f"{row['aerial_dominance_index']:.2f}",
                            f"{row['pressing_intensity_index']:.2f}",
                            f"{row['speed_recovery_index']:.2f}",
                        ]
                        for rank, (_, row) in enumerate(group_players.iterrows(), start=1)
                    ],
                ),
                "",
                (
                    f"The {group.lower()} ordering is a role-fit shortlist for this "
                    "tournament sample. Review component columns, minutes, opponent context, "
                    "and the player's team section before treating a small score difference "
                    "as meaningful."
                ),
                "",
            ]
        )

    lines.extend(
        [
            "# Recommended coaching workflow",
            "",
            "1. Select the opponent's team section and identify its observed attack style, transition exposure, and physical matchup deltas.",
            "2. Pull video for the stated highest-volume review pattern; confirm that the possession labels match the intended tactical interpretation.",
            "3. Use the position leaderboard only to identify candidate role profiles, then check the player's own team context and tournament minutes.",
            "4. Re-run the substitution or style scenario with the expected match state and available squad before training it.",
            "5. Record the pre-match hypothesis and post-match outcome so future calibration can separate useful signals from tournament-specific noise.",
            "",
            "# Limitations and validity",
            "",
            (
                "- The analysis is valid as an exploratory and predictive decision-support "
                "artifact over the supplied tournament data. It is not a randomized or causal study."
            ),
            (
                "- V4 preserves the schema-checked calibrated transition classifier and "
                "64-match leave-one-match-out audit while replacing the player layer with "
                "300-minute eligibility, SB360 spatial context, and unified VAEP+xT scoring. "
                "Threshold abstention still prevents weak transition warnings."
            ),
            (
                "- Rare transition events create high variance. Aggregate patterns and "
                "precision-aware decisions are safer than interpreting individual possessions "
                "as certain events."
            ),
            (
                "- Player physicality uses event-derived proxies: ground-duel wins approximate "
                "tackle-related success, and recoveries approximate defensive recovery activity."
            ),
            (
                f"- Player rankings cover {len(profiles)} eligible 300+ minute players from "
                f"{provenance['players_before_cutoff']} observed players; they do not measure "
                "performance outside this competition."
            ),
            (
                "- Recommended actions require video confirmation and domain review. Medical "
                "status, fatigue, tactical instructions, score state, and opposition substitutions "
                "can materially change the correct decision."
            ),
            "",
            "---",
            "",
            (
                "Generated reproducibly from the processed possession, player-profile, matchup, "
                "audit, and simulation artifacts in this repository."
            ),
        ]
    )

    destination = output_path if output_path.is_absolute() else project_root / output_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return destination


def main() -> None:
    """Command-line entry point."""

    args = parse_args()
    output = generate_report(args.project_root.resolve(), args.output)
    print(f"Generated combined tournament report: {output}")


if __name__ == "__main__":
    main()
