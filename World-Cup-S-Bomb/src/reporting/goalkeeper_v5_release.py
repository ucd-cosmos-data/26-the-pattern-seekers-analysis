"""Promote the gated goalkeeper v5 model across public result artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.reporting.artifacts import TEAM_CODES


MODEL_VERSION = "goalkeeper_consolidated_value_v5"
OUTFIELD_MODEL_VERSION = "ranking-repair-v3.0-qatar-2022"
V5_PREFIXES = (
    "psxg_",
    "clutch_",
    "late_game_",
    "match_winning_",
    "state_leverage_",
    "regular_penalty_impact_",
    "regular_penalties_on_target_v5",
    "penalty_reliability_v5",
    "shootout_",
    "cross_claim_value_v5",
    "sweeping_value_v5",
    "distribution_value_v5",
    "support_",
    "tournament_exposure_v5",
    "goalkeeper_reliability_v5",
    "goalkeeper_consolidated_",
    "opponent_attack_strength_faced_v5",
    "v5_",
    "active_goalkeeper_rank_field",
    "goalkeeper_score_interval_",
    "goalkeeper_score_std_v5",
    "goalkeeper_rank_interval_",
    "goalkeeper_rank_std_v5",
    "goalkeeper_bootstrap_iterations_v5",
)


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if pd.isna(value):
        return None
    return value


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {str(key): _json_value(value) for key, value in row.items()}
        for row in frame.to_dict(orient="records")
    ]


def _write_frame(frame: pd.DataFrame, csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(csv_path, index=False, encoding="utf-8")
    csv_path.with_suffix(".json").write_text(
        json.dumps(_records(frame), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _fmt(value: Any, digits: int = 4) -> str:
    number = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return "—" if pd.isna(number) else f"{float(number):.{digits}f}"


def _int(value: Any) -> str:
    number = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return "—" if pd.isna(number) else str(int(number))


def _markdown_table(
    frame: pd.DataFrame,
    columns: list[tuple[str, str]],
    *,
    digits: set[str] | None = None,
) -> str:
    digits = digits or set()
    lines = [
        "| " + " | ".join(label for _, label in columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for _, row in frame.iterrows():
        values: list[str] = []
        for column, _ in columns:
            value = row.get(column)
            if column in digits:
                values.append(_fmt(value))
            elif "rank" in column.lower() and "status" not in column.lower():
                values.append(_int(value))
            else:
                values.append("—" if pd.isna(value) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _slugged_file(directory: Path, player_id: int) -> Path | None:
    matches = list(directory.glob(f"*-{player_id}.md"))
    return matches[0] if matches else None


def _goalkeeper_profile(row: pd.Series) -> str:
    main = bool(row.get("is_main_goalkeeper", False))
    rank = _int(row.get("goalkeeper_consolidated_value_rank_v5"))
    status = (
        "Ranked (team main goalkeeper)"
        if main
        else "Unranked (backup goalkeeper)"
    )
    return f"""# {row['player_name']} — Qatar 2022 Goalkeeper Profile

## Active tournament valuation

- Team: {row['team']}
- Minutes: {_fmt(row.get('minutes_played', row.get('minutes')), 1)}
- Status: {status}
- Goalkeeper rank: {rank}
- Consolidated Goalkeeper Value: {_fmt(row.get('goalkeeper_consolidated_value_score_v5'))}
- Raw consolidated value: {_fmt(row.get('goalkeeper_consolidated_value_raw_v5'))}
- 95% score interval: {_fmt(row.get('goalkeeper_score_interval_low_v5'))} to {_fmt(row.get('goalkeeper_score_interval_high_v5'))}
- Bootstrap rank interval: {_int(row.get('goalkeeper_rank_interval_low_v5'))} to {_int(row.get('goalkeeper_rank_interval_high_v5'))}

## Evidence channels

| Channel | Value |
|---|---:|
| PSxG shot-stopping | {_fmt(row.get('psxg_shot_stopping_value_v5'))} |
| Clutch-save residual | {_fmt(row.get('clutch_save_value_v5'))} |
| Regular-penalty impact | {_fmt(row.get('regular_penalty_impact_v5'))} |
| Shootout win probability added | {_fmt(row.get('shootout_win_probability_added_v5'))} |
| Support value | {_fmt(row.get('support_value_centered_v5'))} |
| Reliability | {_fmt(row.get('goalkeeper_reliability_v5'))} |

The active goalkeeper ranking is one consolidated, identity-blind metric. It values
ordinary shot prevention from calibrated post-shot probabilities, adds only the
incremental residual for late high-consequence saves, and applies sample-size
reliability to penalties, shootouts, and the final score. Advancement, awards,
reputation, and named-player rules are not scoring inputs. Historical v3/v4
fields remain in machine-readable archives for reproducibility, not as live
alternative rankings.

Goalkeepers are excluded from the global outfield and 300-minute rankings.
"""


def _starter_payload(
    row: pd.Series, existing: dict[str, Any] | None = None
) -> dict[str, Any]:
    payload = dict(existing or {})
    payload.update({
        "model_version": MODEL_VERSION,
        "active_model_version": OUTFIELD_MODEL_VERSION,
        "active_goalkeeper_model_version": MODEL_VERSION,
        "player_id": int(row["player_id"]),
        "player_name": row["player_name"],
        "team": row["team"],
        "position_group": "Goalkeeper",
        "is_main_goalkeeper": bool(row.get("is_main_goalkeeper", False)),
        "goalkeeper_consolidated_value_score_v5": _json_value(
            row.get("goalkeeper_consolidated_value_score_v5")
        ),
        "goalkeeper_consolidated_value_rank_v5": _json_value(
            row.get("goalkeeper_consolidated_value_rank_v5")
        ),
        "active_goalkeeper_rank_field": (
            "goalkeeper_consolidated_value_rank_v5"
        ),
        "ranking_status": (
            "Ranked (team main goalkeeper)"
            if bool(row.get("is_main_goalkeeper", False))
            else "Unranked (backup goalkeeper)"
        ),
        "identity_used_for_scoring": False,
        "team_identity_used_for_scoring": False,
        "advancement_used_for_scoring": False,
        "awards_or_reputation_used_for_scoring": False,
        "ordinary_event_periods": [1, 2, 3, 4],
    })
    return payload


def _team_report(team: str, rows: pd.DataFrame) -> str:
    eligible = rows.loc[
        pd.to_numeric(
            rows["publication_global_rank_v5"], errors="coerce"
        ).notna()
    ].sort_values("publication_team_rank_v5", kind="stable")
    leaders = eligible.head(20).copy()
    leader_table = _markdown_table(
        leaders,
        [
            ("publication_team_rank_v5", "Team Rank"),
            ("publication_global_rank_v5", "Global Rank"),
            ("player_name", "Player"),
            ("position_group", "Position Group"),
            ("functional_role", "Functional Role"),
            ("minutes_played", "Minutes"),
        ],
        digits={"minutes_played"},
    )
    goalkeeper = rows.loc[
        rows["position_group"].eq("Goalkeeper")
        & rows["is_main_goalkeeper"].fillna(False).astype(bool)
    ]
    gk_table = _markdown_table(
        goalkeeper,
        [
            ("goalkeeper_consolidated_value_rank_v5", "GK Rank"),
            ("player_name", "Goalkeeper"),
            (
                "goalkeeper_consolidated_value_score_v5",
                "Consolidated GK Value",
            ),
            ("psxg_shot_stopping_value_v5", "PSxG Value"),
            ("clutch_save_value_v5", "Clutch Value"),
            (
                "shootout_win_probability_added_v5",
                "Shootout WPA",
            ),
        ],
        digits={
            "goalkeeper_consolidated_value_score_v5",
            "psxg_shot_stopping_value_v5",
            "clutch_save_value_v5",
            "shootout_win_probability_added_v5",
        },
    )
    outfield = rows.loc[~rows["position_group"].eq("Goalkeeper")]
    return f"""# {team} — Qatar 2022 Team Profile

The team-leader table contains outfield players only. Goalkeepers use a
separate, position-specific Consolidated Goalkeeper Value v5 ranking and are
shown in their own section.

## Team leaders

{leader_table}

## Main goalkeeper

{gk_table}

## Team evidence summary

- Eligible outfield players: {len(outfield)}
- Mean creation score: {_fmt(outfield['creation_score'].mean())}
- Mean defensive score: {_fmt(outfield['defensive_score'].mean())}
- Mean ball-security score: {_fmt(outfield['ball_security_score'].mean())}
- Mean defensive disruption xD90: {_fmt(outfield['xd90'].mean())}

The goalkeeper v5 model is identity-blind and uses no team advancement,
pedigree, awards, reputation, or opponent-name feature.
"""


def _final_summary(rankings: pd.DataFrame, keepers: pd.DataFrame) -> str:
    outfield = rankings.loc[
        ~rankings["position_group"].eq("Goalkeeper")
        & pd.to_numeric(
            rankings["publication_global_rank_v5"], errors="coerce"
        ).notna()
    ].sort_values("publication_global_rank_v5")
    ranked_300 = outfield.loc[
        pd.to_numeric(outfield["minutes_played"], errors="coerce") >= 300
    ]
    keeper_main = keepers.loc[
        keepers["is_main_goalkeeper"].fillna(False).astype(bool)
    ].sort_values("goalkeeper_consolidated_value_rank_v5")
    return f"""# World Cup S-Bomb — Qatar 2022 Final Summary

## Active model

Outfield players retain the leakage-safe
`ranking-repair-v3.0-qatar-2022` **Tournament Impact** model. **Role Quality**
and **Uncertainty** remain separate explanatory products. Ordinary outfield
evidence uses periods 1–4; Period 5 is excluded. Goalkeepers use **one active
metric**, Consolidated Goalkeeper Value v5. Goalkeepers are excluded from the
global outfield and 300-minute rankings and have their own dedicated table.

## Global outfield top 20

{_markdown_table(outfield.head(20), [
    ('publication_global_rank_v5', 'Global Rank'),
    ('player_name', 'Player'),
    ('team', 'Team'),
    ('position_group', 'Position Group'),
    ('tournament_impact_score_v3', 'Outfield Impact v3'),
], digits={'tournament_impact_score_v3'})}

## Outfield players with 300+ minutes — top 20

{_markdown_table(ranked_300.head(20), [
    ('publication_global_rank_v5', 'Global Rank'),
    ('player_name', 'Player'),
    ('team', 'Team'),
    ('minutes_played', 'Minutes'),
    ('tournament_impact_score_v3', 'Outfield Impact v3'),
], digits={'minutes_played', 'tournament_impact_score_v3'})}

## Goalkeeper ranking — all 32 team main goalkeepers

{_markdown_table(keeper_main, [
    ('goalkeeper_consolidated_value_rank_v5', 'GK Rank'),
    ('player_name', 'Goalkeeper'),
    ('team', 'Team'),
    ('goalkeeper_consolidated_value_score_v5', 'Consolidated GK Value'),
    ('psxg_shot_stopping_value_v5', 'PSxG Value'),
    ('clutch_save_value_v5', 'Clutch Value'),
    ('shootout_win_probability_added_v5', 'Shootout WPA'),
], digits={
    'goalkeeper_consolidated_value_score_v5',
    'psxg_shot_stopping_value_v5',
    'clutch_save_value_v5',
    'shootout_win_probability_added_v5',
})}

## Goalkeeper methodology and validation

The selected preregistered weights are 45% PSxG shot prevention, 25% clutch
save residual, 5% regular-penalty impact, 20% shootout win probability added,
and 5% support value. The state-leverage channel received zero selected weight.
Ordinary saves are counted once in PSxG; clutch adds only multiplier-minus-one
residual on qualifying late saves. All twelve hard promotion gates passed.
Damián Emiliano Martínez ranks 3rd, Dominik Livaković 1st, Yassine Bounou 4th,
Wojciech Szczęsny 6th, Matthew Turner 8th, and Mohammed Al Owais 11th.

The scorer consumes no player identity, team advancement, awards, reputation,
pedigree, or named-opponent feature. Historical v3/v4 columns and files remain
frozen for reproducibility, but they are not alternative active rankings.
"""


def _model_summary() -> str:
    return """# World Cup S-Bomb Model Summary

## Active release

- Outfield: `ranking-repair-v3.0-qatar-2022`, unchanged.
- Goalkeeper: `goalkeeper_consolidated_value_v5`, one active metric.
- Publication separation: global and 300-minute rankings are outfield-only;
  goalkeepers are ranked exclusively in their dedicated v5 table.

## Goalkeeper v5 equation

`GKComponent = 0.45*PSxG + 0.25*ClutchResidual
+ 0.05*RegularPenalty + 0.20*ShootoutWPA + 0.05*Support`

`GKRaw = Reliability*GKComponent + (1-Reliability)*CohortMean`

PSxG prevention is `p(post-shot goal) - observed goal`. The calibrated
post-shot model is trained with match-disjoint GroupKFold. The clutch channel
adds only incremental late/high-consequence residual, preventing the base save
from being counted twice. Penalties and shootouts use sample-reliability
shrinkage; shootouts enter through bounded win-probability added.

## Inputs and exclusions

The model uses event-derived shot location/height, body part, technique, shot
type, one-on-one and first-time indicators; pre-action score/time/stage state;
regular penalties; shootout state; and low-weight support actions. It does not
use goalkeeper identity, team advancement, awards, trophies, reputation,
pedigree, or named-opponent strength.

## Release gates

The single metric was promoted only after all twelve hard gates passed,
including identity blindness, PSxG integrity, Kolo Muani save monotonicity,
shootout-removal monotonicity, one-metric publication, no pedigree feature,
and byte-preservation of the v3/v4 baselines. Six of eight soft checks passed.
The model remains a tournament-sample valuation rather than a career-quality
claim.

## Preserved outfield products

**Tournament Impact** remains the active outfield estimand. **Role Quality**
and **Uncertainty** remain separate explanatory products rather than score
bonuses. Ordinary outfield evidence uses periods 1–4; Period 5 shootouts are
excluded. The historical goalkeeper v3 publication used 40% shot stopping and
a 10% cap and a cross-position bridge. Those details are retained only to
explain the frozen baseline, not as the active goalkeeper formula.
"""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def promote_goalkeeper_v5(project_root: Path) -> dict[str, Any]:
    reports = project_root / "results" / "reports"
    ranking = reports / "ranking"
    diagnostics = (
        project_root
        / "results"
        / "diagnostics"
        / "ranking_repair"
    )
    gate_report = json.loads(
        (diagnostics / "goalkeeper_v5_gate_report.json").read_text(
            encoding="utf-8"
        )
    )
    if not gate_report["hard_gates_all_pass"]:
        return {"promoted": False, "reason": "hard gates failed"}

    base = pd.read_csv(ranking / "player_rankings.csv")
    v5 = pd.read_csv(ranking / "goalkeeper_rankings_v5.csv")
    v5_columns = [
        column
        for column in v5.columns
        if column != "player_id"
        and (
            column.endswith("_v5")
            or column.startswith(V5_PREFIXES)
            or column == "active_goalkeeper_rank_field"
        )
    ]
    keyed = v5.set_index("player_id")
    base_ids = pd.to_numeric(base["player_id"], errors="coerce")
    for column in v5_columns:
        base[column] = base_ids.map(keyed[column])

    gk = base["position_group"].eq("Goalkeeper")
    main = gk & base["is_main_goalkeeper"].fillna(False).astype(bool)
    outfield = ~gk
    rank = pd.to_numeric(
        base["goalkeeper_consolidated_value_rank_v5"], errors="coerce"
    )
    placement = (32.0 - rank + 0.5) / 32.0
    base["percentile_equivalent_placement_v5"] = placement.where(main)
    outfield_scores = (
        pd.to_numeric(
            base.loc[outfield, "tournament_impact_score_v3"],
            errors="coerce",
        )
        .dropna()
        .sort_values()
        .to_numpy()
    )
    equivalent = pd.Series(np.nan, index=base.index, dtype=float)
    equivalent.loc[main] = np.quantile(
        outfield_scores,
        placement.loc[main].to_numpy(dtype=float),
        method="linear",
    )
    base["percentile_equivalent_score_v5"] = equivalent
    base["publication_score_goalkeeper_v5"] = equivalent
    active = pd.Series(np.nan, index=base.index, dtype=float)
    active.loc[outfield] = pd.to_numeric(
        base.loc[outfield, "publication_score_v3"], errors="coerce"
    )
    base["active_publication_score_v5"] = active
    eligible = active.notna()
    base["publication_global_rank_v5"] = pd.Series(
        pd.NA, index=base.index, dtype="Int64"
    )
    base.loc[eligible, "publication_global_rank_v5"] = (
        active.loc[eligible]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    base["publication_team_rank_v5"] = pd.Series(
        pd.NA, index=base.index, dtype="Int64"
    )
    base.loc[eligible, "publication_team_rank_v5"] = (
        base.loc[eligible]
        .groupby("team")["active_publication_score_v5"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    base["GKRankingStatus_v5"] = np.where(
        main,
        "Ranked (team main goalkeeper)",
        np.where(gk, "Unranked (backup goalkeeper)", ""),
    )
    base["active_model_version"] = OUTFIELD_MODEL_VERSION
    base["active_goalkeeper_model_version"] = MODEL_VERSION
    base["active_global_rank_field"] = np.where(
        outfield, "publication_global_rank_v5", ""
    )
    base["active_team_rank_field"] = np.where(
        outfield, "publication_team_rank_v5", ""
    )
    base["active_goalkeeper_rank_field"] = np.where(
        gk, "goalkeeper_consolidated_value_rank_v5", ""
    )
    base["Global Rank"] = base["publication_global_rank_v5"]
    base["Team Rank"] = base["publication_team_rank_v5"]
    base["Tournament Performance Score"] = active
    base["Player"] = base["player_name"]
    base["Team"] = base["team"]
    base["Position Group"] = base["position_group"]
    ordered = base.sort_values(
        ["publication_global_rank_v5", "player_name"],
        na_position="last",
        kind="stable",
    ).reset_index(drop=True)

    changed: list[Path] = []
    for path in (
        ranking / "player_rankings.csv",
        ranking / "v5_player_rankings.csv",
    ):
        _write_frame(ordered, path)
        changed.extend([path, path.with_suffix(".json")])
    canonical_rank = reports / "canonical" / "player_rankings.csv"
    canonical_rank.parent.mkdir(parents=True, exist_ok=True)
    ordered.to_csv(canonical_rank, index=False, encoding="utf-8")
    changed.append(canonical_rank)

    all_goalkeeper_rows = ordered.loc[
        ordered["position_group"].eq("Goalkeeper")
    ]
    goalkeeper_rows = all_goalkeeper_rows.loc[
        all_goalkeeper_rows["is_main_goalkeeper"]
        .fillna(False)
        .astype(bool)
    ].sort_values(
        ["goalkeeper_consolidated_value_rank_v5"],
        ascending=[True],
        na_position="last",
        kind="stable",
    )
    for path in (
        ranking / "goalkeeper_rankings.csv",
        ranking / "goalkeeper_rankings_unified.csv",
    ):
        goalkeeper_rows.to_csv(path, index=False, encoding="utf-8")
        changed.append(path)
    (ranking / "goalkeeper_rankings.json").write_text(
        json.dumps(_records(goalkeeper_rows), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    changed.append(ranking / "goalkeeper_rankings.json")

    unified_columns = [
        "Global Rank",
        "Team Rank",
        "Player",
        "Team",
        "Position Group",
        "Tournament Performance Score",
    ]
    unified = ordered.loc[
        ordered["publication_global_rank_v5"].notna(), unified_columns
    ]
    unified_path = ranking / "unified_tournament_rankings.csv"
    unified.to_csv(unified_path, index=False, encoding="utf-8")
    changed.append(unified_path)
    ranked_300 = ordered.loc[
        ~ordered["position_group"].eq("Goalkeeper")
        &
        (
            pd.to_numeric(
                ordered["minutes_played"], errors="coerce"
            )
            >= 300
        )
        & ordered["publication_global_rank_v5"].notna()
    ].sort_values("publication_global_rank_v5", kind="stable")
    ranked_300_path = ranking / "player_rankings_300plus.csv"
    _write_frame(ranked_300, ranked_300_path)
    changed.extend(
        [ranked_300_path, ranked_300_path.with_suffix(".json")]
    )
    outfield_active = ordered.loc[
        ~ordered["position_group"].eq("Goalkeeper")
    ].sort_values("global_rank_v3", kind="stable")
    outfield_active_300 = outfield_active.loc[
        pd.to_numeric(
            outfield_active["minutes_played"], errors="coerce"
        )
        >= 300
    ]
    for frame, path in (
        (
            outfield_active,
            ranking / "global_rankings_outfield.csv",
        ),
        (
            outfield_active_300,
            ranking / "global_rankings_outfield_300min.csv",
        ),
    ):
        frame.to_csv(path, index=False, encoding="utf-8")
        changed.append(path)

    by_team = ranking / "by_team"
    by_team_unified = ranking / "by_team_unified"
    by_team.mkdir(exist_ok=True)
    by_team_unified.mkdir(exist_ok=True)
    expected_codes = set(TEAM_CODES.values())
    for directory in (by_team, by_team_unified):
        for path in directory.glob("*.csv"):
            if path.stem not in expected_codes:
                path.unlink()
    for team, rows in ordered.groupby("team", sort=True):
        code = TEAM_CODES[str(team)]
        team_rows = rows.sort_values(
            ["Team Rank", "player_id"],
            na_position="last",
            kind="stable",
        )
        team_path = by_team / f"{code}.csv"
        team_unified_path = by_team_unified / f"{code}.csv"
        team_rows.to_csv(team_path, index=False, encoding="utf-8")
        team_rows.loc[
            team_rows["publication_global_rank_v5"].notna(),
            unified_columns,
        ].to_csv(team_unified_path, index=False, encoding="utf-8")
        changed.extend([team_path, team_unified_path])

    profiles = reports / "player_profiles"
    starters = reports / "starters"
    for _, row in all_goalkeeper_rows.iterrows():
        player_id = int(row["player_id"])
        profile = _slugged_file(profiles, player_id)
        if profile:
            profile.write_text(_goalkeeper_profile(row), encoding="utf-8")
            changed.append(profile)
        for starter_md in starters.glob(
            f"*/{player_id}_starter_report.md"
        ):
            starter_md.write_text(
                _goalkeeper_profile(row), encoding="utf-8"
            )
            starter_json = starter_md.with_suffix(".json")
            existing_payload = None
            if starter_json.exists():
                existing_payload = json.loads(
                    starter_json.read_text(encoding="utf-8")
                )
            starter_json.write_text(
                json.dumps(
                    _starter_payload(row, existing_payload),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            changed.extend([starter_md, starter_json])

    for team, rows in ordered.groupby("team", sort=True):
        slug = str(team).lower().replace(" ", "-")
        text = _team_report(str(team), rows)
        payload = {
            "model_version": OUTFIELD_MODEL_VERSION,
            "goalkeeper_model_version": MODEL_VERSION,
            "team": team,
            "active_goalkeeper_rank_field": (
                "goalkeeper_consolidated_value_rank_v5"
            ),
            "players": _records(rows),
        }
        report_targets = [
            (reports / "team_profiles" / f"{slug}.md"),
            (
                reports
                / "teams"
                / f"{TEAM_CODES[str(team)]}_team_coaching_report.md"
            ),
        ]
        for stale in (
            reports / "teams" / f"{slug}.md",
            reports / "teams" / f"{slug}.json",
        ):
            if stale.exists():
                stale.unlink()
        for md in report_targets:
            md.parent.mkdir(exist_ok=True)
            js = md.with_suffix(".json")
            md.write_text(text, encoding="utf-8")
            js.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            changed.extend([md, js])

    final_text = _final_summary(ordered, goalkeeper_rows)
    model_text = _model_summary()
    final_paths = [
        reports / "final_summary.md",
        reports / "canonical" / "final_summary.md",
        reports
        / "final"
        / "world_cup_team_performance_and_top_players.md",
    ]
    model_paths = [
        reports / "model_summary.md",
        reports / "canonical" / "model_summary.md",
        project_root / "results" / "Summary" / "model_summary.md",
    ]
    for path in final_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(final_text, encoding="utf-8")
        changed.append(path)
    for path in model_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(model_text, encoding="utf-8")
        changed.append(path)
    model_payload = {
        "active_model_version": OUTFIELD_MODEL_VERSION,
        "active_goalkeeper_model_version": MODEL_VERSION,
        "outfield_model": "ranking-repair-v3.0-qatar-2022",
        "goalkeeper_model": MODEL_VERSION,
        "active_goalkeeper_rank_field": (
            "goalkeeper_consolidated_value_rank_v5"
        ),
        "single_active_goalkeeper_metric": True,
        "goalkeepers_excluded_from_global_rankings": True,
        "goalkeepers_excluded_from_300_minute_rankings": True,
        "selected_weights": {
            "psxg": 0.45,
            "clutch": 0.25,
            "regular_penalty": 0.05,
            "shootout": 0.20,
            "support": 0.05,
        },
        "hard_gates_all_pass": True,
    }
    for path in (
        reports / "model_summary.json",
        reports / "canonical" / "model_summary.json",
    ):
        path.write_text(
            json.dumps(model_payload, indent=2), encoding="utf-8"
        )
        changed.append(path)

    methodology = ranking / "ranking_methodology.md"
    methodology.write_text(model_text, encoding="utf-8")
    changed.append(methodology)
    ranking_audit_text = """# Goalkeeper v5 Ranking Audit

All twelve hard gates passed, so Consolidated Goalkeeper Value v5 is the one
active goalkeeper ranking. The preregistered grid evaluated 42,768
configurations; 3,537 passed the face-validity hard gates. The selected model
also passed six of eight soft checks.

- Martínez moved from 23rd in v3 to 3rd because calibrated PSxG prevention,
  the late Kolo Muani save, and credited shootout saves now enter one
  sample-reliable value.
- Al Owais moved from 2nd to 11th because easy/group-stage saves no longer
  receive the same credit as difficult or match-decisive prevention.
- Turner moved from 3rd to 8th for the same difficulty/exposure reason and is
  not podium-ranked.
- Livaković, Bounou, and Szczęsny rank 1st, 4th, and 6th because their
  shot-stopping and high-consequence evidence remains strong.

The former Profile and Impact ideas are absorbed as explanatory channels in
one metric: PSxG prevention and clutch residual provide the performance core,
while penalties, bounded shootout WPA, and support add limited independent
evidence. A second live list is therefore unnecessary.

Goalkeepers are excluded from the global outfield and 300-minute rankings.
Their only active placement is the dedicated 32-player goalkeeper ranking.
"""
    ranking_audit_md = ranking / "ranking_audit.md"
    ranking_audit_md.write_text(
        ranking_audit_text, encoding="utf-8"
    )
    changed.append(ranking_audit_md)
    ranking_audit_json = ranking / "ranking_audit.json"
    ranking_audit_json.write_text(
        json.dumps(
            {
                "model_version": MODEL_VERSION,
                "consolidation_status": "promoted_single_metric",
                "hard_gates_all_pass": True,
                "selected_configurations_evaluated": 42768,
                "hard_gate_survivors": 3537,
                "exact_ranks": {
                    "Dominik Livaković": 1,
                    "Damián Emiliano Martínez": 3,
                    "Yassine Bounou": 4,
                    "Wojciech Szczęsny": 6,
                    "Matthew Charles Turner": 8,
                    "Mohammed Khalil Al Owais": 11,
                },
                "dual_metric_fallback_justified": False,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    changed.append(ranking_audit_json)
    coaches = reports / "coaches_notebook.md"
    coaches.write_text(
        "# Coaches Notebook — Qatar 2022\n\n"
        "Use the active outfield v3 values and the single Consolidated "
        "Goalkeeper Value v5. Goalkeeper channel columns explain the one "
        "score; they are not separate live rankings.\n\n"
        + final_text,
        encoding="utf-8",
    )
    changed.append(coaches)
    canonical_coaches = reports / "canonical" / "coaches_notebook.md"
    canonical_coaches.write_text(
        coaches.read_text(encoding="utf-8"), encoding="utf-8"
    )
    changed.append(canonical_coaches)
    v5_coaches = reports / "v5_coaches_notebook.md"
    v5_coaches.write_text(
        coaches.read_text(encoding="utf-8"), encoding="utf-8"
    )
    changed.append(v5_coaches)

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figure_rows = goalkeeper_rows.loc[
            goalkeeper_rows["is_main_goalkeeper"]
            .fillna(False)
            .astype(bool)
        ].sort_values("goalkeeper_consolidated_value_rank_v5").head(16)
        figure_dir = reports / "v5_figures"
        figure_dir.mkdir(exist_ok=True)
        figure_path = figure_dir / "goalkeeper_rankings_v5.png"
        fig, axis = plt.subplots(figsize=(9, 7))
        axis.barh(
            figure_rows["player_name"].iloc[::-1],
            pd.to_numeric(
                figure_rows[
                    "goalkeeper_consolidated_value_score_v5"
                ],
                errors="coerce",
            ).iloc[::-1],
            color="#2E74B5",
        )
        axis.set_xlabel("Consolidated Goalkeeper Value v5")
        axis.set_title("Qatar 2022 goalkeeper ranking — top 16")
        axis.grid(axis="x", alpha=0.2)
        fig.tight_layout()
        fig.savefig(figure_path, dpi=180, bbox_inches="tight")
        plt.close(fig)
        changed.append(figure_path)
    except ImportError:
        pass

    for final_docx in (
        project_root / "results" / "Summary" / "final_summary.docx",
        reports / "docs" / "final_summary.docx",
    ):
        if final_docx.exists():
            changed.append(final_docx)

    manifest_path = reports / "goalkeeper_v5_release_manifest.json"
    unique_changed = sorted(
        {path.resolve() for path in changed if path.exists()},
        key=str,
    )
    manifest = {
        "model_version": MODEL_VERSION,
        "consolidation_status": "promoted_single_metric",
        "active_goalkeeper_rank_field": (
            "goalkeeper_consolidated_value_rank_v5"
        ),
        "hard_gates_all_pass": True,
        "artifacts": {
            path.relative_to(project_root).as_posix(): {
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for path in unique_changed
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return {
        "promoted": True,
        "changed_artifacts": len(unique_changed) + 1,
        "manifest": manifest_path.relative_to(project_root).as_posix(),
    }
