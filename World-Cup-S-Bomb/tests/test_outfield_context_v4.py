from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.features.outfield_context_v4 import (
    PLAYER_SHAPE_360_FEATURES,
    TEAM_SHAPE_360_FEATURES,
    allocate_match_context_to_players,
    build_off_ball_prevention_oof,
    build_opponent_context,
)


def _matches() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "match_id": [1, 2, 3, 4],
            "match_date": [
                "2022-11-20",
                "2022-11-21",
                "2022-11-22",
                "2022-11-23",
            ],
            "kick_off": ["17:00:00"] * 4,
            "home_team": ["Alpha", "Charlie", "Delta", "Bravo"],
            "away_team": ["Bravo", "Alpha", "Alpha", "Charlie"],
        }
    )


def _fifa_rankings() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team": ["Alpha", "Bravo", "Charlie", "Delta"],
            "fifa_rank": [1, 5, 25, 50],
            "ranking_date": ["2022-10-06"] * 4,
            "source": ["FIFA 2022-10-06 frozen snapshot"] * 4,
        }
    )


def _possessions() -> pd.DataFrame:
    attacking_xg = {
        (1, "Alpha"): 0.8,
        (1, "Bravo"): 0.3,
        (2, "Alpha"): 1.1,
        (2, "Charlie"): 0.5,
        (3, "Alpha"): 1.4,
        (3, "Delta"): 0.4,
        (4, "Bravo"): 0.7,
        (4, "Charlie"): 0.9,
    }
    rows: list[dict[str, float | int | str]] = []
    for (match_id, team), xg in attacking_xg.items():
        for index in range(2):
            rows.append(
                {
                    "match_id": match_id,
                    "team": team,
                    "possession_uid": f"{match_id}-{team}-{index}",
                    "xg_generated": xg / 2.0,
                    "entered_final_third": 1,
                    "entered_penalty_area": int(index == 0),
                }
            )
    return pd.DataFrame(rows)


def _ordered_strength(result: object) -> pd.Series:
    frame = result.frame.sort_values(
        ["match_id", "team"], kind="mergesort"
    )
    return frame["opponent_attack_strength_match_v4"].reset_index(drop=True)


@pytest.mark.parametrize(
    "variant", ["fifa_log_rank", "fifa_inverse_sqrt"]
)
def test_fifa_context_is_frozen_before_tournament_and_outcome_invariant(
    variant: str,
) -> None:
    matches = _matches()
    fifa = _fifa_rankings()
    possessions = _possessions()

    baseline = build_opponent_context(
        matches, possessions, fifa, variant=variant
    )
    changed_outcomes = possessions.copy()
    changed_outcomes["xg_generated"] = (
        changed_outcomes["xg_generated"] * 100.0 + 7.0
    )
    changed_outcomes["entered_penalty_area"] = (
        1 - changed_outcomes["entered_penalty_area"]
    )
    changed = build_opponent_context(
        matches, changed_outcomes, fifa, variant=variant
    )

    pd.testing.assert_series_equal(
        _ordered_strength(baseline),
        _ordered_strength(changed),
        check_names=False,
    )
    assert baseline.audit["source"]["ranking_date"] == "2022-10-06"
    assert baseline.audit["source"]["strictly_predates_all_matches"] is True
    assert baseline.audit["source"]["post_event_fields_used"] == []

    leaked = fifa.copy()
    leaked.loc[leaked["team"].eq("Alpha"), "ranking_date"] = "2022-12-01"
    with pytest.raises(ValueError, match="predate every tournament match"):
        build_opponent_context(
            matches, possessions, leaked, variant=variant
        )


def test_cumulative_strength_excludes_current_and_future_matches() -> None:
    matches = _matches()
    fifa = _fifa_rankings()
    possessions = _possessions()
    baseline = build_opponent_context(
        matches,
        possessions,
        fifa,
        variant="cumulative_pre_match_xg",
    )

    current_and_future_changed = possessions.copy()
    mask = current_and_future_changed["team"].eq("Alpha") & (
        current_and_future_changed["match_id"] >= 2
    )
    current_and_future_changed.loc[mask, "xg_generated"] = 1000.0
    unchanged = build_opponent_context(
        matches,
        current_and_future_changed,
        fifa,
        variant="cumulative_pre_match_xg",
    )

    baseline_match_two = baseline.frame.loc[
        baseline.frame["match_id"].eq(2)
        & baseline.frame["opponent"].eq("Alpha"),
        "opponent_attack_strength_match_v4",
    ].iloc[0]
    changed_match_two = unchanged.frame.loc[
        unchanged.frame["match_id"].eq(2)
        & unchanged.frame["opponent"].eq("Alpha"),
        "opponent_attack_strength_match_v4",
    ].iloc[0]
    assert changed_match_two == pytest.approx(baseline_match_two)

    first_match = baseline.frame.loc[
        baseline.frame["match_id"].eq(1)
        & baseline.frame["opponent"].eq("Alpha"),
        "opponent_attack_strength_match_v4",
    ].iloc[0]
    assert first_match == pytest.approx(1.0)

    prior_changed = possessions.copy()
    prior_changed.loc[
        prior_changed["team"].eq("Alpha")
        & prior_changed["match_id"].eq(1),
        "xg_generated",
    ] *= 10.0
    changed_by_prior = build_opponent_context(
        matches,
        prior_changed,
        fifa,
        variant="cumulative_pre_match_xg",
    )
    changed_by_prior_match_two = changed_by_prior.frame.loc[
        changed_by_prior.frame["match_id"].eq(2)
        & changed_by_prior.frame["opponent"].eq("Alpha"),
        "opponent_attack_strength_match_v4",
    ].iloc[0]
    assert changed_by_prior_match_two > baseline_match_two
    assert (
        baseline.audit["source"]["strictly_prior_match_only"] is True
    )
    assert baseline.audit["source"]["post_event_fields_used"] == []


@pytest.mark.parametrize(
    "variant", ["fifa_log_rank", "fifa_inverse_sqrt"]
)
def test_harder_opponents_have_greater_pre_match_strength(
    variant: str,
) -> None:
    context = build_opponent_context(
        _matches(), _possessions(), _fifa_rankings(), variant=variant
    ).frame
    hardest = context.loc[
        context["opponent"].eq("Alpha"),
        "opponent_attack_strength_match_v4",
    ]
    easiest = context.loc[
        context["opponent"].eq("Delta"),
        "opponent_attack_strength_match_v4",
    ]
    assert hardest.min() > easiest.max()


def test_unsupported_opposition_variant_is_rejected() -> None:
    with pytest.raises(ValueError, match="opposition variant"):
        build_opponent_context(
            _matches(),
            _possessions(),
            _fifa_rankings(),
            variant="post_tournament_elo",
        )


def _prevention_inputs(
    *,
    matches: int = 30,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    possession_rows: list[dict[str, float | int | str]] = []
    context_rows: list[dict[str, float | int | str]] = []
    for match_id in range(1, matches + 1):
        for side in range(2):
            latent_prevention = float(rng.normal())
            strength = float(1.0 + 0.18 * rng.normal())
            observed_entry_rate = float(
                0.32
                + 0.055 * strength
                - 0.075 * latent_prevention
                + rng.normal(scale=0.003)
            )
            team = f"T{side}"
            shape = {
                column: float(
                    latent_prevention * (1.0 + index / 50.0)
                    + rng.normal(scale=0.01)
                )
                for index, column in enumerate(TEAM_SHAPE_360_FEATURES)
            }
            possession_rows.append(
                {
                    "match_id": match_id,
                    "defending_team": team,
                    **shape,
                }
            )
            context_rows.append(
                {
                    "match_id": match_id,
                    "team": team,
                    "opponent_attack_strength_match_v4": strength,
                    "opponent_penalty_area_entry_rate_v4": (
                        observed_entry_rate
                    ),
                }
            )
    return pd.DataFrame(possession_rows), pd.DataFrame(context_rows)


def test_off_ball_prevention_passes_match_disjoint_oof_without_events() -> None:
    possessions, context = _prevention_inputs()
    assert "player_id" not in possessions
    assert not {
        "tackles",
        "interceptions",
        "blocks",
        "pressures",
        "defensive_events",
    }.intersection(possessions.columns)

    result = build_off_ball_prevention_oof(
        possessions,
        context,
        ridge_alpha=1.0,
        n_splits=6,
    )

    assert result.audit["gate_passed"] is True
    assert result.audit["oof_group"] == "match_id"
    assert result.audit["match_disjoint"] is True
    assert result.audit["folds"] == 6
    assert (
        result.audit["requires_recorded_player_defensive_events"] is False
    )
    assert result.audit["features"] == list(TEAM_SHAPE_360_FEATURES)
    assert result.audit["oof_spearman"] > 0.0
    assert result.audit["oof_rmse"] < result.audit["null_rmse"]
    assert result.frame["match_id"].nunique() == 30
    assert result.frame["entry_denial_oof_prediction_v4"].std() > 0.0


def _allocation_inputs() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    predictions = pd.DataFrame(
        {
            "match_id": [1, 1, 2],
            "team": ["A", "A", "B"],
            "player_id": [10, 11, 20],
            "minutes": [90.0, 60.0, 90.0],
            "signed_ridge_oof_prediction": [0.2, 0.1, -0.1],
        }
    )
    samples = pd.DataFrame(
        {
            "match_id": [1, 1, 2],
            "team": ["A", "A", "B"],
            "player_id": [10, 11, 20],
            "opponent_possessions": [50.0, 35.0, 55.0],
            "positioning_360_coverage": [0.8, 0.0, 0.7],
        }
    )
    players = pd.DataFrame(
        {
            "player_id": [10, 11, 20],
            PLAYER_SHAPE_360_FEATURES[0]: [0.8, np.nan, 0.2],
            PLAYER_SHAPE_360_FEATURES[1]: [0.7, np.nan, 0.3],
        }
    )
    context = pd.DataFrame(
        {
            "match_id": [1, 2],
            "team": ["A", "B"],
            "opponent": ["B", "A"],
            "opponent_attack_strength_match_v4": [1.2, 0.8],
            "opponent_expected_exposure_v4": [0.6, 0.44],
        }
    )
    prevention = pd.DataFrame(
        {
            "match_id": [1, 2],
            "team": ["A", "B"],
            "entry_denial_target_per100_v4": [1.5, -0.5],
            "entry_denial_oof_prediction_v4": [2.0, -1.0],
        }
    )
    return predictions, samples, players, context, prevention


def test_missing_player_360_is_neutral_flagged_and_not_zero() -> None:
    output = allocate_match_context_to_players(*_allocation_inputs())
    missing = output.loc[output["player_id"].eq(11)].iloc[0]

    assert missing["off_ball_player_shape_available_v4"] == np.bool_(False)
    for column in PLAYER_SHAPE_360_FEATURES:
        assert missing[column] == pytest.approx(0.5)
    assert missing["off_ball_prevention_raw_v4"] != pytest.approx(0.0)
    assert missing["off_ball_prevention_coverage_v4"] == pytest.approx(0.0)


def test_player_allocation_is_deterministic_and_does_not_mutate_inputs() -> None:
    inputs = _allocation_inputs()
    originals = tuple(frame.copy(deep=True) for frame in inputs)

    first = allocate_match_context_to_players(*inputs)
    for frame, original in zip(inputs, originals, strict=True):
        pd.testing.assert_frame_equal(frame, original)

    shuffled = tuple(
        frame.sample(frac=1.0, random_state=7).reset_index(drop=True)
        for frame in inputs
    )
    shuffled_originals = tuple(
        frame.copy(deep=True) for frame in shuffled
    )
    second = allocate_match_context_to_players(*shuffled)

    pd.testing.assert_frame_equal(first, second)
    for frame, original in zip(shuffled, shuffled_originals, strict=True):
        pd.testing.assert_frame_equal(frame, original)
