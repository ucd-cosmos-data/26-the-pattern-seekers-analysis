"""Build one coach-readable tournament report from the simulation artifacts.

The report combines descriptive team performance, model-based tactical audit
results, substitution scenarios, and position-specific player leaderboards.
It intentionally separates observed metrics from predictive scenario outputs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.report_generators import TEAM_CODES  # noqa: E402


POSITION_WEIGHTS: dict[str, dict[str, float]] = {
    "Goalkeeper": {
        "minutes": 0.40,
        "pass_completion": 0.30,
        "pass_progression_per_pass": 0.20,
        "speed_recovery_index": 0.10,
    },
    "Center Back": {
        "aerial_dominance_index": 0.25,
        "pressing_intensity_index": 0.15,
        "speed_recovery_index": 0.20,
        "net_xg_contribution_p90": 0.15,
        "pass_progression_per_pass": 0.15,
        "minutes": 0.10,
    },
    "Fullback/Wingback": {
        "aerial_dominance_index": 0.10,
        "pressing_intensity_index": 0.20,
        "speed_recovery_index": 0.20,
        "net_xg_contribution_p90": 0.20,
        "progressive_passes_p90": 0.15,
        "key_passes_p90": 0.05,
        "minutes": 0.10,
    },
    "Defensive Midfield": {
        "aerial_dominance_index": 0.10,
        "pressing_intensity_index": 0.20,
        "speed_recovery_index": 0.20,
        "net_xg_contribution_p90": 0.20,
        "progressive_passes_p90": 0.15,
        "pass_completion": 0.05,
        "minutes": 0.10,
    },
    "Central/Wide Midfield": {
        "pressing_intensity_index": 0.20,
        "speed_recovery_index": 0.15,
        "net_xg_contribution_p90": 0.25,
        "progressive_passes_p90": 0.20,
        "key_passes_p90": 0.10,
        "minutes": 0.10,
    },
    "Attacking Midfield/Wing": {
        "pressing_intensity_index": 0.15,
        "speed_recovery_index": 0.10,
        "net_xg_contribution_p90": 0.30,
        "progressive_carries_p90": 0.15,
        "key_passes_p90": 0.15,
        "xg_p90": 0.05,
        "minutes": 0.10,
    },
    "Forward": {
        "aerial_dominance_index": 0.15,
        "pressing_intensity_index": 0.10,
        "net_xg_contribution_p90": 0.30,
        "shots_p90": 0.15,
        "xg_p90": 0.20,
        "minutes": 0.10,
    },
}


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
        default=Path("results/reports/final/world_cup_team_performance_and_top_players.md"),
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


def add_position_scores(profiles: pd.DataFrame) -> pd.DataFrame:
    """Calculate transparent, position-specific tournament role scores."""

    scored = profiles.copy()
    scored["player"] = scored["player"].map(clean_text)
    scored["position"] = scored["position"].map(clean_text)
    scored["functional_role"] = scored["functional_role"].map(clean_text)
    scored["position_score"] = np.nan

    for position_group, weights in POSITION_WEIGHTS.items():
        mask = scored["position_group"].eq(position_group)
        group = scored.loc[mask]
        if group.empty:
            continue
        score = pd.Series(0.0, index=group.index)
        for column, weight in weights.items():
            numeric = pd.to_numeric(group[column], errors="coerce")
            percentiles = numeric.rank(method="average", pct=True).fillna(0.5)
            score = score.add(percentiles * weight, fill_value=0.0)
        scored.loc[mask, "position_score"] = 100.0 * score

    return scored


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
    """Return Markdown-ready rows for a team's highest role scores."""

    leaders = players.sort_values(
        ["position_score", "minutes"], ascending=False
    ).head(count)
    return [
        [
            rank,
            row["player"],
            row["position_group"],
            row["functional_role"],
            f"{row['minutes']:.0f}",
            f"{row['position_score']:.1f}",
            f"{row['net_xg_contribution_p90']:.3f}",
        ]
        for rank, (_, row) in enumerate(leaders.iterrows(), start=1)
    ]


def generate_report(project_root: Path, output_path: Path) -> Path:
    """Load pipeline outputs and write the combined final report."""

    required = {
        "possessions": project_root / "data/processed/world_cup_defensive_clusters.csv",
        "profiles": project_root / "data/processed/player_physicality_profiles.csv",
        "audit": project_root / "results/audit/expected_vs_actual_team_summary.csv",
        "mistakes": project_root / "results/audit/recurrent_tactical_mistakes.csv",
        "substitutions": project_root
        / "results/simulations/substitution_optimization.parquet",
        "matchup": project_root / "data/processed/lineup_matchup_features.csv",
    }
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Cannot generate final report; missing required artifacts:\n- "
            + "\n- ".join(missing)
        )

    possessions = pd.read_csv(required["possessions"])
    profiles = add_position_scores(pd.read_csv(required["profiles"]))
    audit = pd.read_csv(required["audit"])
    mistakes = pd.read_csv(required["mistakes"])
    substitutions = pd.read_parquet(required["substitutions"])
    matchup = pd.read_csv(required["matchup"])

    if set(TEAM_CODES) - set(possessions["team"].dropna().unique()):
        absent = sorted(set(TEAM_CODES) - set(possessions["team"].dropna().unique()))
        raise ValueError(f"Possession data is missing expected teams: {absent}")
    unknown_positions = sorted(set(profiles["position_group"]) - set(POSITION_WEIGHTS))
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
            "- **Position score (0–100):** a within-position, tournament-only composite of "
            "role-relevant percentiles. It cannot compare players across position groups."
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

        lines.extend(
            [
                f"## {team} ({TEAM_CODES[team]})",
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
                "### Tactical and matchup read",
                "",
                (
                    f"The scenario evaluator selected **{row['recommended_style']}** most "
                    f"often. Observed expected net xG was {row['actual_expected_net_xg']:.2f}; "
                    f"the possession-level scenario ceiling summed to "
                    f"{row['optimal_expected_net_xg']:.2f}, producing "
                    f"{row['wasted_net_xg']:.2f} modeled cumulative net xG of review "
                    f"opportunity and a {row['mean_eva_gap']:.4f} mean EvA gap."
                ),
                "",
                (
                    f"Average lineup matchup deltas were **{row['delta_aerial']:+.3f} aerial**, "
                    f"**{row['delta_pressing']:+.3f} pressing**, and "
                    f"**{row['delta_recovery']:+.3f} recovery**. These are relative proxies, "
                    "so the signs are more useful for matchup planning than the raw magnitudes."
                ),
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
                        "Treat this as a video and training-ground hypothesis; the simulation "
                        "does not encode fatigue, injury, match state, or all role constraints."
                    ),
                    "",
                ]
            )

        lines.extend(
            [
                "### Leading tournament-role profiles",
                "",
                markdown_table(
                    [
                        "Rank",
                        "Player",
                        "Position group",
                        "Functional role",
                        "Minutes",
                        "Role score",
                        "Net xG/90",
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
            ]
        )

    lines.extend(
        [
            "# Top tournament-role players by position",
            "",
            (
                "These leaderboards rank only the analyzed tournament cohort and use "
                "different weights for different roles. A score of 80 means a strong blend "
                "of the selected within-position indicators; it does not mean an 80% chance "
                "of success. Sample size, team tactics, opponent quality, and role assignment "
                "all affect the component metrics."
            ),
            "",
            "## Position-score construction",
            "",
        ]
    )
    for group, weights in POSITION_WEIGHTS.items():
        weight_text = ", ".join(
            f"{column.replace('_', ' ')} {100 * weight:.0f}%"
            for column, weight in weights.items()
        )
        lines.append(f"- **{group}:** {weight_text}.")
    lines.extend(
        [
            "",
            (
                "**Goalkeeper warning:** the source features do not provide a complete "
                "post-shot shot-stopping evaluation. The goalkeeper list therefore reflects "
                "minutes, distribution, progression, and a recovery proxy—not overall "
                "goalkeeping quality. Do not use it to make goalkeeper selection decisions "
                "without save-quality, cross-claim, sweeping, and error data."
            ),
            "",
        ]
    )

    for group in POSITION_WEIGHTS:
        group_players = profiles[profiles["position_group"].eq(group)].sort_values(
            ["position_score", "minutes"], ascending=False
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
                        "Score",
                        "Net xG/90",
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
                            f"{row['position_score']:.1f}",
                            f"{row['net_xg_contribution_p90']:.3f}",
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
                "- The underlying serialized coaching benchmark was unavailable, so the "
                "downstream scenario pipeline used the documented regularized empirical "
                "hurdle fallback. Results should be revalidated when a healthy calibrated "
                "model bundle is available."
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
                "- Player rankings cover the 342-player tournament-minute cohort used by the "
                "pipeline, not every registered player and not performance outside this competition."
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
