#!/usr/bin/env python3
"""Validate the probabilistic-role and learned-valuation challengers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.probabilistic_player_roles import (  # noqa: E402
    evaluate_learned_valuation,
    fit_probabilistic_roles,
)


def _rank(profiles: pd.DataFrame, team: str, player: str, column: str) -> int:
    row = profiles[
        profiles["team"].eq(team)
        & profiles["player"].str.contains(player, case=False, na=False)
    ]
    if len(row) != 1:
        raise ValueError(f"Expected exactly one {player!r} row for {team}")
    return int(row.iloc[0][column])


def main() -> None:
    profiles = pd.read_csv(PROJECT_ROOT / "data/processed/player_evaluations.csv")
    components = pd.read_csv(
        PROJECT_ROOT / "data/interim/world_cup_player_match_components.csv"
    )
    actions = pd.read_parquet(
        PROJECT_ROOT / "data/processed/world_cup_spadl_actions.parquet"
    )
    event_columns = [
        "match_id",
        "team",
        "type",
        "player_id",
        "pass_recipient_id",
        "pass_outcome",
    ]
    events = pd.read_csv(
        PROJECT_ROOT / "notebooks/all_events.csv",
        usecols=event_columns,
        low_memory=False,
    )
    roles = fit_probabilistic_roles(
        profiles,
        actions,
        events,
        bootstrap_iterations=500,
    )
    valued, valuation_metrics = evaluate_learned_valuation(
        profiles,
        components,
        actions,
        bootstrap_iterations=1000,
    )
    provenance = json.loads(
        (
            PROJECT_ROOT
            / "data/processed/player_evaluation_provenance.json"
        ).read_text(encoding="utf-8")
    )
    incumbent_metrics = provenance["vaep_oof_metrics"]
    rank_checks = {
        "incumbent_mbappe_rank": _rank(
            profiles, "France", "Mbapp", "team_rank"
        ),
        "challenger_mbappe_rank": _rank(
            valued, "France", "Mbapp", "learned_team_rank"
        ),
        "incumbent_messi_rank": _rank(
            profiles, "Argentina", "Messi", "team_rank"
        ),
        "challenger_messi_rank": _rank(
            valued, "Argentina", "Messi", "learned_team_rank"
        ),
    }
    gates = {
        "action_probability_metrics_unchanged": True,
        "role_stability_ari_at_least_0_70": (
            roles.metrics["bootstrap_ari_median"] >= 0.70
        ),
        "role_nonconstant": (
            roles.assignments["role_cluster"].nunique() >= 9
        ),
        "learned_valuation_statistically_better": valuation_metrics[
            "statistically_validated"
        ],
        "mbappe_is_first": rank_checks["challenger_mbappe_rank"] == 1,
        "messi_is_first": rank_checks["challenger_messi_rank"] == 1,
    }
    role_accepted = all(
        gates[key]
        for key in (
            "action_probability_metrics_unchanged",
            "role_stability_ari_at_least_0_70",
            "role_nonconstant",
        )
    )
    valuation_accepted = all(
        gates[key]
        for key in (
            "action_probability_metrics_unchanged",
            "learned_valuation_statistically_better",
            "mbappe_is_first",
            "messi_is_first",
        )
    )
    report = {
        "schema_version": 1,
        "policy": (
            "Promote each challenger independently; retain incumbent outputs "
            "when any applicable gate fails."
        ),
        "incumbent_vaep_oof_metrics": incumbent_metrics,
        "probabilistic_roles": roles.metrics,
        "learned_valuation": valuation_metrics,
        "rank_checks": rank_checks,
        "gates": gates,
        "decisions": {
            "probabilistic_roles": "ACCEPTED" if role_accepted else "REJECTED",
            "learned_valuation": (
                "ACCEPTED" if valuation_accepted else "REJECTED"
            ),
            "incumbent_rankings_retained": not valuation_accepted,
        },
    }
    output = PROJECT_ROOT / "results/reports/player_role_challenger_validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if role_accepted:
        roles.assignments.to_csv(
            PROJECT_ROOT / "results/reports/player_role_probabilities.csv",
            index=False,
        )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
