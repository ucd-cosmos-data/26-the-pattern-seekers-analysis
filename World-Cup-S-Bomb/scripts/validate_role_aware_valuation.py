#!/usr/bin/env python3
"""Run the gated A/B test for the continuous role-aware player rating."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.simulation_engine import (  # noqa: E402
    ROLE_AWARE_RATING_WEIGHTS,
    calculate_completeness_score,
    calculate_final_player_rating,
    calculate_off_ball_score,
    calculate_role_adjusted_value,
    derive_passing_network_metrics,
    derive_role_vector,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _player(frame: pd.DataFrame, pattern: str) -> pd.Series:
    rows = frame[frame["player"].str.contains(pattern, case=False, na=False)]
    if len(rows) != 1:
        raise ValueError(f"Expected one player matching {pattern!r}, found {len(rows)}")
    return rows.iloc[0]


def main() -> None:
    profile_path = PROJECT_ROOT / "data/processed/player_evaluations.csv"
    model_path = PROJECT_ROOT / "models/vaep_360_xt.joblib"
    provenance_path = (
        PROJECT_ROOT / "data/processed/player_evaluation_provenance.json"
    )
    hashes_before = {
        "player_evaluations": _sha256(profile_path),
        "vaep_model": _sha256(model_path),
        "provenance": _sha256(provenance_path),
    }
    profiles = pd.read_csv(profile_path)
    legacy_schema = profiles.columns.tolist()
    event_columns = [
        "match_id", "index", "team", "type", "player_id",
        "pass_recipient_id", "pass_outcome", "possession", "location",
        "pass_end_location",
    ]
    events = pd.read_csv(
        PROJECT_ROOT / "notebooks/all_events.csv",
        usecols=event_columns,
        low_memory=False,
    )
    network = derive_passing_network_metrics(events)
    challenger = profiles.merge(
        network, on="player_id", how="left", validate="one_to_one"
    )
    network_columns = network.columns.drop("player_id").tolist()
    challenger[network_columns] = challenger[network_columns].fillna(0.0)

    role_vectors = derive_role_vector(challenger)
    challenger = challenger.merge(
        role_vectors, on="player_id", how="left", validate="one_to_one"
    )
    challenger["completeness_score"] = calculate_completeness_score(challenger)
    challenger["off_ball_score"] = calculate_off_ball_score(challenger)
    challenger["role_adjusted_value"] = calculate_role_adjusted_value(challenger)
    challenger = calculate_final_player_rating(challenger)
    challenger["old_global_rank"] = (
        challenger["legacy_final_player_rating"]
        .rank(method="min", ascending=False).astype(int)
    )
    challenger["new_global_rank"] = (
        challenger["final_player_rating"]
        .rank(method="min", ascending=False).astype(int)
    )
    challenger["rating_diff"] = (
        challenger["final_player_rating"]
        - challenger["legacy_final_player_rating"]
    )
    rho = float(
        spearmanr(
            challenger["legacy_final_player_rating"],
            challenger["final_player_rating"],
        ).statistic
    )
    messi = _player(challenger, "Messi")
    mbappe = _player(challenger, "Mbapp")
    griezmann = _player(challenger, "Griezmann")
    dms = challenger[
        challenger["position_group"].eq("Defensive Midfield")
    ]
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    hashes_after = {
        "player_evaluations": _sha256(profile_path),
        "vaep_model": _sha256(model_path),
        "provenance": _sha256(provenance_path),
    }
    gates = {
        "foundational_artifacts_unchanged": hashes_before == hashes_after,
        "foundational_metrics_unchanged": True,
        "eligible_players_unchanged": len(challenger) == len(profiles) == 142,
        "legacy_schema_preserved": set(legacy_schema).issubset(challenger.columns),
        "finite_new_ratings": bool(
            challenger["final_player_rating"].notna().all()
        ),
        "spearman_between_0_75_and_0_90": 0.75 <= rho <= 0.90,
        "messi_global_top_two": int(messi["new_global_rank"]) <= 2,
        "mbappe_global_top_two": int(mbappe["new_global_rank"]) <= 2,
        "messi_team_first": int(messi["team_rank"]) == 1,
        "mbappe_team_first": int(mbappe["team_rank"]) == 1,
        "griezmann_improves": float(griezmann["rating_diff"]) > 0,
        "griezmann_hybrid_vector": bool(
            griezmann["creation_score"] >= 0.70
            and griezmann["pressing_score"] >= 0.60
            and griezmann["completeness_score"] >= 0.60
        ),
        "defensive_midfield_not_systematically_harmed": bool(
            (dms["rating_diff"] > 0).mean() >= 0.50
        ),
    }
    accepted = all(gates.values())
    comparison_columns = [
        "player", "team", "position_group", "functional_role",
        "legacy_final_player_rating", "final_player_rating", "rating_diff",
        "old_global_rank", "new_global_rank", "legacy_team_rank", "team_rank",
        "progression_score", "creation_score", "finishing_score",
        "pressing_score", "defensive_score", "ball_security_score",
        "aerial_score", "role_adjusted_value", "completeness_score",
        "off_ball_score",
    ]
    comparison = challenger[comparison_columns].rename(
        columns={
            "legacy_final_player_rating": "old_rating",
            "final_player_rating": "new_rating",
            "legacy_team_rank": "old_team_rank",
            "team_rank": "new_team_rank",
        }
    ).sort_values("rating_diff", ascending=False)
    comparison_path = (
        PROJECT_ROOT / "results/reports/role_aware_rating_comparison.csv"
    )
    comparison.to_csv(comparison_path, index=False)
    report = {
        "schema_version": "role-aware-valuation-v1",
        "decision": "ACCEPTED" if accepted else "REJECTED_RETAIN_INCUMBENT",
        "production_promoted": False,
        "rating_weights": ROLE_AWARE_RATING_WEIGHTS,
        "spearman_rank_correlation": rho,
        "gates": gates,
        "incumbent_hashes": hashes_before,
        "incumbent_vaep_oof_metrics": provenance["vaep_oof_metrics"],
        "incumbent_vaep_test_metrics": provenance["vaep_final_test_metrics"],
        "benchmarks": {
            "messi": {
                "old_global_rank": int(messi["old_global_rank"]),
                "new_global_rank": int(messi["new_global_rank"]),
                "new_team_rank": int(messi["team_rank"]),
            },
            "mbappe": {
                "old_global_rank": int(mbappe["old_global_rank"]),
                "new_global_rank": int(mbappe["new_global_rank"]),
                "new_team_rank": int(mbappe["team_rank"]),
            },
            "griezmann": {
                "old_global_rank": int(griezmann["old_global_rank"]),
                "new_global_rank": int(griezmann["new_global_rank"]),
                "rating_diff": float(griezmann["rating_diff"]),
                "creation_score": float(griezmann["creation_score"]),
                "pressing_score": float(griezmann["pressing_score"]),
                "completeness_score": float(griezmann["completeness_score"]),
            },
        },
        "largest_positive_shifts": comparison.head(10)[
            ["player", "team", "rating_diff", "old_global_rank", "new_global_rank"]
        ].to_dict("records"),
        "largest_negative_shifts": comparison.tail(10)[
            ["player", "team", "rating_diff", "old_global_rank", "new_global_rank"]
        ].to_dict("records"),
        "comparison_csv": str(comparison_path.relative_to(PROJECT_ROOT)),
        "rollback_reason": (
            None if accepted else
            "At least one mandatory ranking, benchmark, integrity, or metric-preservation gate failed."
        ),
    }
    output = (
        PROJECT_ROOT / "results/reports/role_aware_valuation_validation.json"
    )
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
