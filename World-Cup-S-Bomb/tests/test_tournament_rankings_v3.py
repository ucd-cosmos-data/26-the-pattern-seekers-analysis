"""Tests for the Qatar 2022 three-product v3 ranking architecture."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.features.event_scope import EVENT_SCOPE_VERSION
from src.models.tournament_rankings_v3 import (
    CORE_ATTACK_ABLATIONS,
    TournamentRankingV3Config,
    bootstrap_match_uncertainty,
    build_attack_ablation_scores,
    calculate_tournament_rankings_v3,
    evaluate_attack_ablations,
    fit_role_prior_strength_match_disjoint,
    ranking_gate_diagnostics,
    score_feature_contract,
)


def _players() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "player_id": [1, 2, 3, 4],
            "player_name": ["A", "B", "C", "D"],
            "team": ["X", "X", "Y", "Y"],
            "position_group_360": ["FW", "CB", "FW", "CB"],
            "functional_role": ["Finisher", "Stopper", "Finisher", "Stopper"],
            "minutes": [360.0, 360.0, 180.0, 180.0],
            "expected_action_value_non_shootout": [1.2, 0.4, 0.8, 0.2],
            "defensive_value_non_shootout": [0.0, 0.8, 0.0, 0.4],
            "positive_contribution_value_non_shootout": [2.0, 1.8, 1.4, 0.9],
            "open_play_goals": [2, 0, 1, 0],
            "non_penalty_goals": [2, 0, 1, 0],
            "regular_penalty_goals": [1, 0, 0, 0],
            "regulation_extra_time_goals": [3, 0, 1, 0],
            "assists": [1, 0, 0, 0],
            "xg_non_shootout": [2.4, 0.0, 0.7, 0.0],
            "xg_non_penalty": [1.6, 0.0, 0.7, 0.0],
            "xa_non_shootout": [0.6, 0.0, 0.2, 0.0],
            "shootout_attempts": [0, 0, 0, 0],
            "shootout_goals": [0, 0, 0, 0],
            "event_scope_version": [EVENT_SCOPE_VERSION] * 4,
            "role_probability_attack": [0.9, 0.1, 0.8, 0.2],
            "role_probability_defense": [0.1, 0.9, 0.2, 0.8],
        }
    )


def _config(**overrides: object) -> TournamentRankingV3Config:
    settings: dict[str, object] = {
        "bootstrap_replicates": 80,
        "attack_bootstrap_replicates": 80,
        "role_probability_columns": (
            "role_probability_attack",
            "role_probability_defense",
        ),
    }
    settings.update(overrides)
    return TournamentRankingV3Config(**settings)


def test_v3_publishes_three_separate_products_and_compatibility_fields() -> None:
    ranked = calculate_tournament_rankings_v3(
        _players(),
        config=_config(),
    )

    assert {
        "tournament_impact_v3",
        "role_quality_v3",
        "uncertainty_low_v3",
        "uncertainty_high_v3",
        "global_rank_v3",
        "team_rank_v3",
        "position_rank_v3",
        "role_rank_v3",
        "Global Rank v3",
        "Team Rank v3",
        "Tournament Impact v3",
        "Role Quality v3",
        "Uncertainty Low v3",
        "Uncertainty High v3",
    } <= set(ranked.columns)
    assert ranked["ranking_release_status_v3"].eq("shadow").all()
    assert ranked["legacy_fields_status_v3"].eq(
        "preserved-not-repurposed"
    ).all()
    assert ranked["role_quality_shrinkage_count_v3"].eq(1).all()
    assert ranked["uncertainty_used_as_score_penalty_v3"].eq(False).all()
    assert ranked["shootout_outcomes_used_v3"].eq(False).all()
    assert ranked["uncertainty_status_v3"].eq("not-estimated").all()
    assert ranking_gate_diagnostics(ranked)["passed"]


def test_reporting_position_and_role_cannot_change_tournament_impact() -> None:
    players = _players()
    changed = players.copy()
    changed["position_group_360"] = ["DM", "AM", "CB", "FW"]
    changed["functional_role"] = ["R1", "R2", "R3", "R4"]
    ranked = calculate_tournament_rankings_v3(players, config=_config())
    reranked = calculate_tournament_rankings_v3(changed, config=_config())

    np.testing.assert_allclose(
        ranked["tournament_impact_v3"],
        reranked["tournament_impact_v3"],
    )
    pd.testing.assert_series_equal(
        ranked["global_rank_v3"],
        reranked["global_rank_v3"],
        check_names=False,
    )


def test_player_and_team_name_permutations_leave_scores_unchanged() -> None:
    players = _players()
    ranked = calculate_tournament_rankings_v3(players, config=_config())
    renamed = players.copy()
    renamed["player_name"] = ["Z", "Y", "W", "V"]
    renamed["team"] = ["Other 1", "Other 1", "Other 2", "Other 2"]
    reranked = calculate_tournament_rankings_v3(renamed, config=_config())

    for column in (
        "tournament_impact_v3",
        "role_quality_v3",
        "global_rank_v3",
    ):
        pd.testing.assert_series_equal(
            ranked[column],
            reranked[column],
            check_names=False,
        )
    contract = score_feature_contract(_config())
    assert "player_name" not in contract["scoring_columns"]
    assert "team" not in contract["scoring_columns"]
    assert "player_name" in contract["identity_fields_excluded"]
    assert "team" in contract["identity_fields_excluded"]


def test_positive_and_negative_action_values_are_monotonic() -> None:
    baseline = _players().iloc[[0]].copy()
    positive = baseline.copy()
    positive["expected_action_value_non_shootout"] += 0.25
    error = baseline.copy()
    error["defensive_value_non_shootout"] -= 0.25

    baseline_score = calculate_tournament_rankings_v3(
        baseline,
        config=_config(),
    )["tournament_impact_v3"].iloc[0]
    positive_score = calculate_tournament_rankings_v3(
        positive,
        config=_config(),
    )["tournament_impact_v3"].iloc[0]
    error_score = calculate_tournament_rankings_v3(
        error,
        config=_config(),
    )["tournament_impact_v3"].iloc[0]

    assert positive_score == pytest.approx(baseline_score + 0.25)
    assert error_score == pytest.approx(baseline_score - 0.25)


def test_empty_minutes_cannot_improve_role_quality() -> None:
    baseline = _players()
    more_empty_minutes = baseline.copy()
    more_empty_minutes.loc[0, "minutes"] += 180.0
    original = calculate_tournament_rankings_v3(
        baseline,
        config=_config(),
    )
    changed = calculate_tournament_rankings_v3(
        more_empty_minutes,
        config=_config(),
    )

    assert changed.loc[0, "role_quality_v3"] <= original.loc[
        0,
        "role_quality_v3",
    ]
    assert changed.loc[0, "tournament_impact_v3"] == original.loc[
        0,
        "tournament_impact_v3",
    ]


def test_shootout_fields_never_change_outfield_scores() -> None:
    players = _players()
    changed = players.copy()
    changed["shootout_attempts"] = [5, 4, 3, 2]
    changed["shootout_goals"] = [5, 3, 2, 0]
    ranked = calculate_tournament_rankings_v3(players, config=_config())
    reranked = calculate_tournament_rankings_v3(changed, config=_config())

    for column in (
        "attack_component_v3",
        "tournament_impact_v3",
        "role_quality_v3",
        "global_rank_v3",
    ):
        pd.testing.assert_series_equal(
            ranked[column],
            reranked[column],
            check_names=False,
        )


def test_attack_ablation_contract_separates_process_and_outcomes() -> None:
    players = _players()
    scores = build_attack_ablation_scores(players, config=_config())

    assert set(CORE_ATTACK_ABLATIONS) <= set(scores.columns)
    np.testing.assert_allclose(
        scores["process_only"],
        players["expected_action_value_non_shootout"],
    )
    np.testing.assert_allclose(
        scores["process_plus_shrunk_residual"],
        scores["process_only"]
        + scores["attack_shrunk_realization_residual_v3"],
    )
    np.testing.assert_allclose(
        scores["process_plus_full_outcomes"],
        scores["process_only"] + scores["outcomes_only"],
    )
    assert scores["shootout_outcomes_used_in_attack_score_v3"].eq(False).all()


def _match_frame() -> pd.DataFrame:
    rng = np.random.default_rng(9)
    rows: list[dict[str, float | int | str]] = []
    for match_id in range(1, 9):
        for player_id in range(1, 7):
            process = (
                0.15 * player_id
                + 0.03 * match_id
                + rng.normal(0.0, 0.03)
            )
            goal = int((player_id + match_id) % 5 == 0)
            xg = 0.12 + 0.05 * ((player_id + match_id) % 4)
            xa = 0.04 + 0.02 * (player_id % 3)
            assist = int((2 * player_id + match_id) % 9 == 0)
            residual = (goal - xg) + 0.35 * (assist - xa)
            opportunity = max(xg + xa, goal + assist)
            reliability = opportunity / (opportunity + 2.0)
            target = (
                process
                + reliability * residual
                + rng.normal(0.0, 0.015)
            )
            rows.append(
                {
                    "match_id": match_id,
                    "player_id": player_id,
                    "team": f"T{player_id % 2}",
                    "minutes": 90.0,
                    "expected_action_value_non_shootout": process,
                    "defensive_value_non_shootout": 0.0,
                    "positive_contribution_value_non_shootout": max(
                        target,
                        0.0,
                    ),
                    "open_play_goals": goal,
                    "non_penalty_goals": goal,
                    "regular_penalty_goals": 0,
                    "regulation_extra_time_goals": goal,
                    "assists": assist,
                    "xg_non_shootout": xg,
                    "xg_non_penalty": xg,
                    "xa_non_shootout": xa,
                    "event_scope_version": EVENT_SCOPE_VERSION,
                    "role_probability_attack": 0.6,
                    "role_probability_defense": 0.4,
                    "heldout_target": target,
                }
            )
    return pd.DataFrame(rows)


def test_attack_ablation_gate_is_match_disjoint_and_generalized() -> None:
    audit = evaluate_attack_ablations(
        _match_frame(),
        target_column="heldout_target",
        config=_config(attack_noninferiority_margin=0.05),
    )

    assert audit["match_disjoint"]
    assert audit["n_matches"] == 8
    assert not audit["identity_features_used"]
    assert not audit["shootout_outcomes_used"]
    assert set(CORE_ATTACK_ABLATIONS) <= set(audit["metrics"])
    assert audit["selected_candidate"] in audit["metrics"]
    assert audit["metrics"][audit["selected_candidate"]]["gate_passed"]
    assert audit["metrics"]["process_plus_full_outcomes"][
        "oof_rmse"
    ] > audit["metrics"]["process_plus_shrunk_residual"]["oof_rmse"]


def test_match_disjoint_prior_selection_and_bootstrap_are_deterministic() -> None:
    matches = _match_frame()
    selection = fit_role_prior_strength_match_disjoint(
        matches,
        config=_config(),
    )
    assert selection["match_disjoint"]
    assert selection["n_matches"] == 8
    assert selection["selected_prior_strength"] in {
        row["prior_strength"] for row in selection["candidates"]
    }

    match_impact = matches.assign(
        tournament_impact_match_v3=matches["heldout_target"]
    )
    first = bootstrap_match_uncertainty(
        match_impact,
        replicates=80,
        random_seed=42,
    )
    second = bootstrap_match_uncertainty(
        match_impact,
        replicates=80,
        random_seed=42,
    )
    pd.testing.assert_frame_equal(first, second)
    assert first["uncertainty_low_v3"].le(
        first["uncertainty_high_v3"]
    ).all()
    assert first["bootstrap_rank_best_v3"].le(
        first["bootstrap_rank_worst_v3"]
    ).all()


def test_integrated_match_bootstrap_does_not_change_point_score() -> None:
    players = _players()
    rows: list[pd.Series] = []
    for match_id in (1, 2, 3):
        split = players.copy()
        value_columns = [
            "expected_action_value_non_shootout",
            "defensive_value_non_shootout",
            "positive_contribution_value_non_shootout",
            *[
                column
                for column in (
                    "open_play_goals",
                    "non_penalty_goals",
                    "regular_penalty_goals",
                    "regulation_extra_time_goals",
                    "assists",
                    "xg_non_shootout",
                    "xg_non_penalty",
                    "xa_non_shootout",
                )
            ],
        ]
        split[value_columns] = split[value_columns] / 3.0
        split["minutes"] = split["minutes"] / 3.0
        split["match_id"] = match_id
        rows.extend(row for _, row in split.iterrows())
    matches = pd.DataFrame(rows)

    without_bootstrap = calculate_tournament_rankings_v3(
        players,
        config=_config(),
    )
    with_bootstrap = calculate_tournament_rankings_v3(
        players,
        match_contributions=matches,
        config=_config(),
    )

    np.testing.assert_allclose(
        without_bootstrap["tournament_impact_v3"],
        with_bootstrap["tournament_impact_v3"],
    )
    assert with_bootstrap["uncertainty_status_v3"].ne(
        "not-estimated"
    ).all()
    assert with_bootstrap["uncertainty_method_v3"].eq(
        "match-bootstrap"
    ).all()


def test_outcome_contract_rejects_implicit_or_inconsistent_totals() -> None:
    missing = _players().drop(columns=["xg_non_penalty"])
    with pytest.raises(ValueError, match="explicit non-shootout outcomes"):
        calculate_tournament_rankings_v3(missing, config=_config())

    inconsistent = _players()
    inconsistent.loc[0, "regulation_extra_time_goals"] = 99
    with pytest.raises(
        ValueError,
        match="must equal non-penalty plus regular-penalty goals",
    ):
        calculate_tournament_rankings_v3(inconsistent, config=_config())


def test_scoring_configuration_rejects_identity_columns() -> None:
    with pytest.raises(ValueError, match="identity fields"):
        TournamentRankingV3Config(
            process_value_columns=("player_name",),
            process_value_weights=(1.0,),
        )
