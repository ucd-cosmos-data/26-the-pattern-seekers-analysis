from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.models.defensive_challenger import (
    DEFENSIVE_FEATURES,
    TARGET_COLUMN,
    _assert_feature_contract,
    build_defensive_action_targets,
    evaluate_defensive_challengers,
)


def _target_actions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "game_id": [1, 1, 1, 1, 1, 1],
            "action_id": [1, 2, 3, 4, 5, 6],
            "period_id": [1, 1, 1, 1, 1, 5],
            "team": ["A", "B", "B", "A", "A", "A"],
            "player_id": [10, 20, 21, 11, 10, 10],
            "p_scores": [0.05, 0.20, 0.10, 0.04, 0.03, 0.90],
            "p_concedes": [0.20, 0.04, 0.03, 0.10, 0.08, 0.01],
            "possession": [1, 1, 1, 1, 2, 99],
            "possession_team": ["B", "B", "B", "B", "A", "A"],
            "type_name": [
                "Pass",
                "Pressure",
                "Carry",
                "Interception",
                "Pass",
                "Shot",
            ],
        }
    )


def test_target_uses_team_oriented_next_state_and_ordinary_periods() -> None:
    target = build_defensive_action_targets(_target_actions())
    assert target["period_id"].eq(5).sum() == 0
    first = target.loc[target["action_id"].eq(1)].iloc[0]
    assert first["post_action_conceding_probability"] == pytest.approx(0.20)
    assert first["threat_prevention_delta"] == pytest.approx(0.0)
    second = target.loc[target["action_id"].eq(2)].iloc[0]
    assert second["post_action_conceding_probability"] == pytest.approx(0.03)
    assert second["threat_prevention_delta"] == pytest.approx(0.01)
    third = target.loc[target["action_id"].eq(3)].iloc[0]
    assert third["post_action_conceding_probability"] == pytest.approx(0.04)
    assert third["threat_prevention_delta"] == pytest.approx(-0.01)


def test_target_does_not_depend_on_action_type_labels() -> None:
    actions = _target_actions()
    baseline = build_defensive_action_targets(actions)[
        "threat_prevention_delta"
    ]
    permuted = actions.copy()
    permuted["type_name"] = list(reversed(actions["type_name"]))
    changed = build_defensive_action_targets(permuted)[
        "threat_prevention_delta"
    ]
    pd.testing.assert_series_equal(
        baseline.reset_index(drop=True),
        changed.reset_index(drop=True),
        check_names=False,
    )


def test_target_does_not_bridge_period_boundaries() -> None:
    actions = _target_actions().loc[
        lambda frame: frame["period_id"].ne(5)
    ].copy()
    actions.loc[actions["action_id"].eq(4), "period_id"] = 2
    target = build_defensive_action_targets(actions)
    end_of_period = target.loc[target["action_id"].eq(3)].iloc[0]
    assert pd.isna(end_of_period["post_action_conceding_probability"])
    assert pd.isna(end_of_period["threat_prevention_delta"])


def test_identity_and_attacking_fields_are_rejected() -> None:
    _assert_feature_contract(DEFENSIVE_FEATURES)
    with pytest.raises(ValueError, match="Identity"):
        _assert_feature_contract([*DEFENSIVE_FEATURES, "player_id"])
    with pytest.raises(ValueError, match="Spurious"):
        _assert_feature_contract([*DEFENSIVE_FEATURES, "shots_p90"])


def _model_samples(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, float | int | str]] = []
    teams = [f"T{index}" for index in range(8)]
    positions = [
        "Center Back",
        "Fullback/Wingback",
        "Defensive Midfield",
        "Central/Wide Midfield",
    ]
    match_id = 100
    for round_index in range(4):
        pairings = [
            (teams[(index + round_index) % 8], teams[(7 - index) % 8])
            for index in range(4)
        ]
        for left, right in pairings:
            for team in (left, right):
                for player_slot in range(4):
                    values = rng.normal(size=len(DEFENSIVE_FEATURES))
                    record = {
                        feature: float(value)
                        for feature, value in zip(
                            DEFENSIVE_FEATURES, values
                        )
                    }
                    signed_signal = (
                        0.22 * values[0]
                        - 0.30 * values[1]
                        + 0.18 * values[6]
                        - 0.12 * values[-3]
                        + 0.08 * values[-1]
                    )
                    record.update(
                        {
                            "match_id": match_id,
                            "team": team,
                            "player_id": (
                                1000
                                + teams.index(team) * 10
                                + player_slot
                            ),
                            "position_group": positions[player_slot],
                            "minutes": 90.0,
                            TARGET_COLUMN: float(
                                signed_signal
                                + rng.normal(scale=0.035)
                            ),
                        }
                    )
                    rows.append(record)
            match_id += 1
    return pd.DataFrame(rows)


def test_nested_validation_is_match_disjoint_and_gate_is_explicit() -> None:
    samples = _model_samples()
    result = evaluate_defensive_challengers(
        samples,
        champion_reference_correlation=0.20,
        outer_folds=4,
        inner_folds=3,
        bootstrap_draws=60,
        run_ablations=False,
    )
    diagnostics = result.diagnostics
    assert set(diagnostics["candidates"]) == {
        "positive_elastic_net",
        "signed_ridge",
        "signed_elastic_net",
        "isotonic_hist_gradient_boosting",
    }
    for candidate in diagnostics["candidates"].values():
        assert all(
            fold["match_overlap"] is False
            for fold in candidate["fold_audit"]
        )
        assert all(
            fold["preprocessing_fit_scope"]
            == "outer-training-fold-only"
            for fold in candidate["fold_audit"]
        )
    assert diagnostics["selected_challenger"] in {
        "signed_ridge",
        "signed_elastic_net",
        "isotonic_hist_gradient_boosting",
    }
    assert set(diagnostics["promotion_gate"]["checks"]) == {
        "held_out_rmse_noninferior_by_match_bootstrap",
        "material_correlation_vs_incumbent_reference",
        "cb_fb_dm_predictions_noncollapsed",
        "attacking_spurious_predictors_absent",
        "leave_one_team_out_noninferior",
    }
    assert diagnostics["feature_contract"]["player_identity_feature_count"] == 0
    assert diagnostics["feature_contract"]["team_identity_feature_count"] == 0


def test_name_and_team_label_permutation_does_not_change_oof_scores() -> None:
    samples = _model_samples()
    baseline = evaluate_defensive_challengers(
        samples,
        champion_reference_correlation=0.20,
        outer_folds=4,
        inner_folds=3,
        bootstrap_draws=50,
        run_ablations=False,
    )
    renamed = samples.copy()
    renamed["player_id"] = renamed["player_id"] + 90_000
    team_map = {
        team: f"renamed-{index}"
        for index, team in enumerate(sorted(renamed["team"].unique()))
    }
    renamed["team"] = renamed["team"].map(team_map)
    changed = evaluate_defensive_challengers(
        renamed,
        champion_reference_correlation=0.20,
        outer_folds=4,
        inner_folds=3,
        bootstrap_draws=50,
        run_ablations=False,
    )
    score_columns = [
        column
        for column in baseline.oof_predictions
        if column.endswith("_oof_prediction")
    ]
    np.testing.assert_allclose(
        baseline.oof_predictions[score_columns],
        changed.oof_predictions[score_columns],
        rtol=0.0,
        atol=1e-12,
    )
