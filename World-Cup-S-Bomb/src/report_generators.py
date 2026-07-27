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
            "obv_per_90": player["obv_per_90"],
            "obv_source": player["obv_source"],
            "final_third_share": player["final_third_share"],
            "role_z_score": player["role_z_score"],
            "player_evaluation_score": player[
                "player_evaluation_score"
            ],
            "heatmap": (
                f"../heatmaps/{TEAM_CODES[player['team']]}/"
                f"{player_id}_heatmap.svg"
            ),
            "top_chemistry_partners": partner_records,
            "recommended_tactical_tweaks": tweaks,
            "cohort_definition": (
                "Tournament players with at least 300 minutes; evaluation "
                "is normalized only against the same functional role"
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
- Risk-adjusted OBV per 90: {player['obv_per_90']:.4f}
- OBV source: `{player['obv_source']}`
- Final-third spatial share: {100 * player['final_third_share']:.1f}%
- Role-relative z-score: {player['role_z_score']:+.3f}
- V4 evaluation score: {player['player_evaluation_score']:.1f}

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
                "obv_per_90",
                "final_third_share",
                "role_z_score",
                "player_evaluation_score",
            ]
            top_players = (
                profiles.loc[
                    profiles["team"].eq(team), available_columns
                ]
                .nlargest(5, "player_evaluation_score")
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
            f"score {float(row['player_evaluation_score']):.1f}, "
            f"role z {float(row['role_z_score']):+.2f}, "
            f"OBV/90 {float(row['obv_per_90']):+.3f}"
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

## V4 role-relative player leaders

{player_lines}

_Only players with at least 300 tournament minutes are ranked. Scores are
standardized within functional role and are not cross-position absolute
quality estimates._

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
            "- Rankings are role-relative; cross-role score comparisons are invalid.",
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
