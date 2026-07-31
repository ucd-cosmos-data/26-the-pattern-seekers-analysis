#!/usr/bin/env python3
"""Validate and optionally promote continuous, post-K-Means role refinements."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.simulation_engine import refine_functional_roles  # noqa: E402


SCORE_COLUMNS = [
    "progression_score", "creation_score", "finishing_score",
    "pressing_score", "defensive_score", "ball_security_score",
    "aerial_score", "completeness_score",
]


def _one(frame: pd.DataFrame, pattern: str) -> pd.Series:
    rows = frame[frame["player"].str.contains(pattern, case=False, na=False)]
    if len(rows) != 1:
        raise ValueError(f"Expected one player matching {pattern!r}")
    return rows.iloc[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--promote", action="store_true")
    args = parser.parse_args()
    profile_path = PROJECT_ROOT / "data/processed/player_evaluations.csv"
    profiles = pd.read_csv(profile_path)
    old_ratings = profiles[
        ["player_id", "final_player_rating", "team_rank"]
    ].copy()
    comparison = pd.read_csv(
        PROJECT_ROOT / "results/reports/role_aware_rating_comparison.csv"
    )
    vectors = comparison[["player", *SCORE_COLUMNS]]
    candidate = profiles.merge(
        vectors, on="player", how="left", validate="one_to_one"
    )
    candidate = refine_functional_roles(candidate)
    changed = candidate[
        candidate["functional_role"].ne(candidate["kmeans_functional_role"])
    ].copy()
    unchanged_share = 1.0 - len(changed) / len(candidate)
    benchmarks = {
        "griezmann": _one(candidate, "Griezmann")["functional_role"],
        "tchouameni": _one(candidate, "Tchouam")["functional_role"],
        "theo_hernandez": _one(candidate, "Theo Bernard")["functional_role"],
        "giroud": _one(candidate, "Giroud")["functional_role"],
        "hakimi": _one(candidate, "Hakimi")["functional_role"],
        "modric": _one(candidate, "Modri")["functional_role"],
        "bellingham": _one(candidate, "Bellingham")["functional_role"],
        "amrabat": _one(candidate, "Amrabat")["functional_role"],
    }
    ratings_unchanged = old_ratings.equals(
        candidate[["player_id", "final_player_rating", "team_rank"]]
    )
    gates = {
        "ratings_and_team_ranks_unchanged": ratings_unchanged,
        "change_rate_between_5_and_30_percent": 0.05 <= 1 - unchanged_share <= 0.30,
        "at_least_70_percent_roles_retained": unchanged_share >= 0.70,
        "griezmann_hybrid_creator": benchmarks["griezmann"]
        == "Hybrid Playmaker / Roaming Creator",
        "tchouameni_controlling_midfielder": benchmarks["tchouameni"]
        == "Holding / Controlling Midfielder",
        "theo_attacking_wingback": benchmarks["theo_hernandez"]
        == "Attacking Wingback",
        "hakimi_attacking_wingback": benchmarks["hakimi"]
        == "Attacking Wingback",
        "modric_deep_playmaker": benchmarks["modric"]
        == "Deep Playmaker / Metronome",
        "giroud_penalty_box_anchor": benchmarks["giroud"]
        == "Target Forward / Penalty-Box Anchor",
        "bellingham_engine_midfielder": benchmarks["bellingham"]
        == "Box-to-Box / Engine Midfielder",
        "amrabat_engine_midfielder": benchmarks["amrabat"]
        == "Box-to-Box / Engine Midfielder",
        "goalkeepers_unchanged": bool(
            candidate.loc[
                candidate["position_group"].eq("Goalkeeper"), "functional_role"
            ].eq("Goalkeeper").all()
        ),
    }
    accepted = all(gates.values())
    output_columns = [
        "player_id", "player", "team", "position_group",
        "kmeans_functional_role", "functional_role",
        "role_refinement_applied", "role_refinement_reason", *SCORE_COLUMNS,
    ]
    audit = candidate[output_columns].sort_values(
        ["role_refinement_applied", "team", "player"],
        ascending=[False, True, True],
    )
    audit.to_csv(
        PROJECT_ROOT / "results/reports/role_refinement_comparison.csv",
        index=False,
    )
    report = {
        "schema_version": "continuous-role-refinement-v1",
        "decision": "ACCEPTED" if accepted else "REJECTED",
        "production_promoted": bool(args.promote and accepted),
        "eligible_players": len(candidate),
        "changed_roles": len(changed),
        "unchanged_roles": len(candidate) - len(changed),
        "change_rate": len(changed) / len(candidate),
        "gates": gates,
        "benchmarks": benchmarks,
        "france_changes": changed.loc[
            changed["team"].eq("France"),
            ["player", "kmeans_functional_role", "functional_role",
             "role_refinement_reason"],
        ].to_dict("records"),
    }
    report_path = (
        PROJECT_ROOT / "results/reports/role_refinement_validation.json"
    )
    if args.promote and accepted:
        candidate.to_csv(profile_path, index=False)
        provenance_path = (
            PROJECT_ROOT / "data/processed/player_evaluation_provenance.json"
        )
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        provenance["continuous_role_refinement"] = report
        provenance_path.write_text(
            json.dumps(provenance, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
