"""Markdown and JSON generators for team and starter coaching reports."""

from __future__ import annotations

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
) -> int:
    """Generate one Markdown/JSON pair for every starter-cohort player."""

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
            "net_xg_contribution_per_90": player[
                "net_xg_contribution_p90"
            ],
            "top_chemistry_partners": partner_records,
            "recommended_tactical_tweaks": tweaks,
            "cohort_definition": (
                "Top 342 tournament-minute players among players with at "
                "least one start"
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
- Net xG contribution per 90: {player['net_xg_contribution_p90']:.4f}

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

_The recovery index uses event recoveries as the available proxy for tracking-derived recovery runs._
"""
        path = (
            output_root
            / TEAM_CODES[player["team"]]
            / f"{player_id}_starter_report.md"
        )
        _write_pair(path, markdown, payload)
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


def generate_full_team_coaching_reports(
    team_summary: pd.DataFrame,
    optimized_lineups: pd.DataFrame,
    substitutions: pd.DataFrame,
    matchup_features: pd.DataFrame,
    recurrent_mistakes: pd.DataFrame,
    output_root: Path,
) -> int:
    """Generate one Markdown/JSON coaching report for all 32 teams."""

    count = 0
    for _, team_row in team_summary.sort_values("team").iterrows():
        team = str(team_row["team"])
        code = TEAM_CODES[team]
        lineup = optimized_lineups[optimized_lineups["team"].eq(team)].sort_values(
            "rank"
        )
        team_subs = substitutions[substitutions["team"].eq(team)]
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
            "model_source": "regularized empirical hurdle fallback",
        }
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
            substitution_text = "No eligible bench substitution"
        mistake_lines = "\n".join(
            f"- Against {row['defensive_style']}: switch from "
            f"{row['actual_style']} to {row['optimal_style']} "
            f"({row['wasted_net_xg']:.4f} cumulative Net xG)"
            for row in mistake_records
        ) or "- No recurrent pattern identified"
        markdown = f"""# {team} — Team Coaching Report

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

## Recurrent tactical mistakes

{mistake_lines}

_Counterfactual values are predictive scenario estimates, not causal treatment effects. The corrupted stored coaching bundle was not used; this report uses the documented empirical hurdle fallback._
"""
        _write_pair(
            output_root / f"{code}_team_coaching_report.md",
            markdown,
            payload,
        )
        count += 1
    return count


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
