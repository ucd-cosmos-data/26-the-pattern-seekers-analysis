"""Focused gates for the Qatar 2022 goalkeeper-v3 branch."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.models.goalkeeper_valuation_v3 import (
    DEFAULT_CONTINUOUS_COMPONENT_WEIGHTS,
    GoalkeeperV3Config,
    bootstrap_goalkeeper_uncertainty_v3,
    calculate_goalkeeper_ratings_v3,
    calibrate_post_shot_xg_v3,
)


def _ordinary_shots() -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for match_id in range(1, 13):
        for shot_number in range(8):
            xg = 0.06 + 0.10 * shot_number
            goal = (
                shot_number >= 6
                or (shot_number == 5 and match_id % 2 == 0)
            )
            records.append(
                {
                    "match_id": match_id,
                    "period": 1 + shot_number % 4,
                    "type": "Shot",
                    "shot_type": "Open Play",
                    "shot_outcome": "Goal" if goal else "Saved",
                    "shot_statsbomb_xg": xg,
                    "shot_end_location": [
                        120.0,
                        35.0 + shot_number,
                        0.4 + 0.15 * shot_number,
                    ],
                    "shot_body_part": (
                        "Head" if shot_number % 3 == 0 else "Right Foot"
                    ),
                    "shot_technique": (
                        "Volley" if shot_number % 4 == 0 else "Normal"
                    ),
                    "shot_one_on_one": shot_number >= 6,
                    "shot_first_time": shot_number % 2 == 0,
                }
            )
    return pd.DataFrame.from_records(records)


def _goalkeeper_features() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for team_index, team in enumerate(("A", "B", "C", "D")):
        rows.extend(
            [
                {
                    "player_id": 100 + team_index,
                    "player_name": f"Main {team}",
                    "team": team,
                    "minutes": 360.0 + 45.0 * team_index,
                    "actions": 80.0 + team_index,
                    "goals_prevented_proxy_p90": (
                        -0.05 + 0.12 * team_index
                    ),
                    "high_leverage_save_rate_shrunk": (
                        0.45 + 0.08 * team_index
                    ),
                    "cross_stopping_rate": 0.04 + 0.02 * team_index,
                    "claims_p90": 0.4 + 0.1 * team_index,
                    "sweeper_actions_p90": 0.2 + 0.2 * team_index,
                    "distribution_under_pressure": (
                        0.55 + 0.07 * team_index
                    ),
                    "regular_penalties_faced": float(team_index % 2),
                    "regular_penalties_saved": float(
                        team_index == 3
                    ),
                    "shootout_penalties_faced": float(
                        1 if team_index < 3 else 2
                    ),
                    "shootout_penalties_saved": float(
                        team_index == 2
                    ),
                },
                {
                    "player_id": 200 + team_index,
                    "player_name": f"Backup {team}",
                    "team": team,
                    "minutes": 20.0,
                    "actions": 5.0,
                    "goals_prevented_proxy_p90": 2.0,
                    "high_leverage_save_rate_shrunk": 1.0,
                    "cross_stopping_rate": 1.0,
                    "claims_p90": 2.0,
                    "sweeper_actions_p90": 2.0,
                    "distribution_under_pressure": 1.0,
                    "regular_penalties_faced": 0.0,
                    "regular_penalties_saved": 0.0,
                    "shootout_penalties_faced": 0.0,
                    "shootout_penalties_saved": 0.0,
                },
            ]
        )
    return pd.DataFrame.from_records(rows)


def _goalkeeper_match_features() -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for match_id in range(1, 9):
        for team_index, team in enumerate(("A", "B", "C", "D")):
            records.append(
                {
                    "match_id": match_id,
                    "period": 1 + match_id % 4,
                    "team": team,
                    "player_id": 100 + team_index,
                    "minutes": 90.0,
                    "actions": 18.0 + team_index,
                    "goals_prevented_proxy_p90": (
                        -0.10
                        + 0.10 * team_index
                        + 0.02 * (match_id % 3)
                    ),
                    "high_leverage_save_rate_shrunk": (
                        0.42 + 0.08 * team_index
                    ),
                    "cross_stopping_rate": 0.04 + 0.01 * team_index,
                    "claims_p90": 0.35 + 0.10 * team_index,
                    "sweeper_actions_p90": 0.20 + 0.15 * team_index,
                    "distribution_under_pressure": (
                        0.55 + 0.06 * team_index
                    ),
                    "regular_penalties_faced": float(
                        match_id == team_index + 1
                    ),
                    "regular_penalties_saved": float(
                        match_id == team_index + 1 and team_index >= 2
                    ),
                    "shootout_penalties_faced": 0.0,
                    "shootout_penalties_saved": 0.0,
                }
            )
    return pd.DataFrame.from_records(records)


def test_nested_calibration_compares_sigmoid_and_isotonic_out_of_fold() -> None:
    shots = _ordinary_shots()
    prediction, audit = calibrate_post_shot_xg_v3(shots)

    assert prediction.index.equals(shots.index)
    assert prediction.between(0.0, 1.0).all()
    assert {
        "raw_logistic",
        "sigmoid",
        "isotonic",
        "selected",
    } == set(audit["method_metrics"])
    for metrics in audit["method_metrics"].values():
        assert {
            "roc_auc",
            "pr_auc",
            "brier_score",
            "expected_calibration_error",
        } <= set(metrics)
        assert 0.0 <= metrics["brier_score"] <= 1.0
        assert 0.0 <= metrics["expected_calibration_error"] <= 1.0
    for fold in audit["fold_audit"]:
        assert set(fold["development_matches"]).isdisjoint(
            fold["validation_matches"]
        )
        assert not fold["outer_validation_used_for_selection"]
        assert (
            fold["selected_on"]
            == "development_cross_fitted_predictions_only"
        )
        assert fold["selected_calibration"] in {"sigmoid", "isotonic"}


def test_period_five_and_regular_penalties_never_enter_continuous_calibration() -> None:
    ordinary = _ordinary_shots()
    extra = pd.DataFrame(
        [
            {
                **ordinary.iloc[0].to_dict(),
                "match_id": 100,
                "period": 5,
                "shot_type": "Penalty",
                "shot_outcome": "Goal",
                "shot_statsbomb_xg": 0.95,
            },
            {
                **ordinary.iloc[1].to_dict(),
                "match_id": 101,
                "period": 2,
                "shot_type": "Penalty",
                "shot_outcome": "Saved",
                "shot_statsbomb_xg": 0.76,
            },
        ],
        index=[10_000, 10_001],
    )
    expanded = pd.concat([ordinary, extra])

    baseline, _ = calibrate_post_shot_xg_v3(ordinary)
    challenger, audit = calibrate_post_shot_xg_v3(expanded)

    pd.testing.assert_series_equal(
        baseline,
        challenger.loc[baseline.index],
    )
    assert 10_000 not in challenger.index
    assert 10_001 not in challenger.index
    assert audit["shootout_rows_excluded"] == 1
    assert audit["regular_penalty_rows_excluded"] == 1
    assert audit["ordinary_non_penalty_rows"] == len(ordinary)


def test_only_main_goalkeepers_are_ranked_and_weights_are_explicit() -> None:
    features = _goalkeeper_features()
    rated, audit = calculate_goalkeeper_ratings_v3(features)
    main = rated.loc[rated["is_main_goalkeeper"]]
    backups = rated.loc[~rated["is_main_goalkeeper"]]

    assert len(main) == features["team"].nunique()
    assert main["team"].is_unique
    assert main["goalkeeper_rank_v3"].notna().all()
    assert backups["goalkeeper_rank_v3"].isna().all()
    assert backups["dedicated_goalkeeper_score_v3"].isna().all()
    assert audit["one_main_goalkeeper_per_team"]
    assert audit["backup_goalkeepers_unranked"]
    assert (
        audit["continuous_component_weights"]
        == DEFAULT_CONTINUOUS_COMPONENT_WEIGHTS
    )
    assert sum(audit["continuous_component_weights"].values()) == pytest.approx(
        1.0
    )
    assert sum(
        audit["dedicated_score_maximum_allocations"].values()
    ) == pytest.approx(1.0)


def test_shootout_save_is_bounded_and_cannot_change_continuous_rating() -> None:
    features = _goalkeeper_features()
    baseline, _ = calculate_goalkeeper_ratings_v3(features)
    changed = features.copy()
    target = changed["player_id"].eq(100)
    changed.loc[target, "shootout_penalties_faced"] += 1.0
    changed.loc[target, "shootout_penalties_saved"] += 1.0
    challenger, audit = calculate_goalkeeper_ratings_v3(changed)

    columns = [
        "continuous_shot_stopping_component_v3",
        "continuous_goalkeeper_raw_rating_v3",
        "continuous_goalkeeper_rating_v3",
        "regular_penalty_rate_posterior_v3",
    ]
    pd.testing.assert_frame_equal(
        baseline.loc[:, columns],
        challenger.loc[:, columns],
    )
    assert challenger["shootout_component_v3"].max() <= 0.10 + 1e-12
    delta = (
        challenger.loc[target, "dedicated_goalkeeper_score_v3"].iloc[0]
        - baseline.loc[target, "dedicated_goalkeeper_score_v3"].iloc[0]
    )
    assert 0.0 <= delta <= 0.10
    assert audit["shootout_cap"] == pytest.approx(0.10)


def test_names_are_not_features_and_bridge_is_percentile_equivalent_only() -> None:
    features = _goalkeeper_features()
    baseline, audit = calculate_goalkeeper_ratings_v3(features)
    renamed = features.copy()
    renamed["player_name"] = list(reversed(renamed["player_name"].tolist()))
    challenger, _ = calculate_goalkeeper_ratings_v3(renamed)

    score_columns = [
        "continuous_goalkeeper_rating_v3",
        "shootout_component_v3",
        "dedicated_goalkeeper_score_v3",
        "goalkeeper_rank_v3",
        "percentile_equivalent_placement",
    ]
    pd.testing.assert_frame_equal(
        baseline.loc[:, score_columns],
        challenger.loc[:, score_columns],
    )
    main = baseline.loc[baseline["is_main_goalkeeper"]].sort_values(
        "dedicated_goalkeeper_score_v3"
    )
    assert main["percentile_equivalent_placement"].is_monotonic_increasing
    assert audit["identity_features_used"] == []
    assert audit["cross_position_field"] == (
        "percentile_equivalent_placement"
    )
    assert "not measured absolute" in audit[
        "cross_position_interpretation"
    ]
    assert "global_rank_v3" not in baseline.columns


def test_match_bootstrap_intervals_are_reproducible_and_ordered() -> None:
    match_features = _goalkeeper_match_features()
    first = bootstrap_goalkeeper_uncertainty_v3(
        match_features,
        iterations=40,
        random_state=9,
    )
    second = bootstrap_goalkeeper_uncertainty_v3(
        match_features,
        iterations=40,
        random_state=9,
    )

    pd.testing.assert_frame_equal(first, second)
    assert (
        first["goalkeeper_score_interval_low_v3"]
        <= first["goalkeeper_score_point_v3"]
    ).all()
    assert (
        first["goalkeeper_score_point_v3"]
        <= first["goalkeeper_score_interval_high_v3"]
    ).all()
    assert (
        first["goalkeeper_rank_interval_low_v3"]
        <= first["goalkeeper_rank_interval_high_v3"]
    ).all()
    assert first["goalkeeper_bootstrap_coverage_v3"].between(
        0.0,
        1.0,
    ).all()
    assert first.attrs["sampling_unit"] == "whole Qatar 2022 match"


def test_shootout_cap_configuration_is_hard_bounded() -> None:
    with pytest.raises(ValueError, match="shootout_cap"):
        GoalkeeperV3Config(shootout_cap=0.16)
