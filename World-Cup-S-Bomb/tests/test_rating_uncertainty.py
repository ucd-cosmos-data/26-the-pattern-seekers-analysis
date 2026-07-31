"""Unit tests for match-level player-rating uncertainty (pure numpy)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rating_uncertainty import (  # noqa: E402
    bootstrap_ratings,
    compute_ratings,
    rank_within_teams,
    summarize,
    top_gap_separation,
)


def test_compute_ratings_matches_hand_formula() -> None:
    # Two players in one position group; work the exact formula by hand.
    sum_v = np.array([10.0, 2.0])
    sum_x = np.array([5.0, 1.0])
    sum_t = np.array([100.0, 50.0])
    sum_m = np.array([900.0, 450.0])
    group = np.array([0, 0])
    raw, final = compute_ratings(sum_v, sum_x, sum_t, sum_m, group)

    assert np.allclose(raw, [0.63, 0.252])
    prior = np.mean([0.63, 0.252])  # shared position-group prior
    rel = sum_m / (sum_m + 450.0)
    expected = rel * raw + (1 - rel) * prior
    assert np.allclose(final, expected)


def test_bootstrap_point_equals_direct_and_shapes() -> None:
    # Each player split evenly across two matches so the row-sums reproduce above.
    vaep = np.array([[5.0, 5.0], [1.0, 1.0]])
    xt = np.array([[2.5, 2.5], [0.5, 0.5]])
    touches = np.array([[50.0, 50.0], [25.0, 25.0]])
    minutes = np.array([[450.0, 450.0], [225.0, 225.0]])
    group = np.array([0, 0])

    point, draws = bootstrap_ratings(
        vaep, xt, touches, minutes, group, replicates=200, random_state=0
    )
    _, direct = compute_ratings(
        vaep.sum(1), xt.sum(1), touches.sum(1), minutes.sum(1), group
    )
    assert np.allclose(point, direct)
    assert draws.shape == (2, 200)
    assert np.all(np.isfinite(draws))  # both players feature in every 2-match resample
    # Determinism.
    point2, draws2 = bootstrap_ratings(
        vaep, xt, touches, minutes, group, replicates=200, random_state=0
    )
    assert np.array_equal(draws, draws2)


def test_rank_and_separation() -> None:
    # Player 0 strictly dominates player 1 on every replicate; player 2 (other team) alone.
    draws = np.array([
        [0.9, 0.8, 0.7],
        [0.4, 0.5, 0.3],
        [0.6, 0.6, 0.6],
    ])
    team = np.array([0, 0, 1])
    ranks = rank_within_teams(draws, team)
    assert np.array_equal(ranks[0], [1, 1, 1])
    assert np.array_equal(ranks[1], [2, 2, 2])
    assert np.array_equal(ranks[2], [1, 1, 1])  # alone on its team

    final_point = draws.mean(axis=1)
    sep = top_gap_separation(draws, team, final_point)
    assert sep[0] == 1.0  # #1 beats #2 every replicate
    assert np.isnan(sep[1])  # single-player team has no pair

    stats = summarize(final_point, draws, team)
    assert np.isclose(stats["p_rank1"][0], 1.0)
    assert np.isclose(stats["p_rank1"][1], 0.0)


def test_coinflip_separation() -> None:
    # Top two swap the lead on exactly half the replicates -> ~0.5 separation.
    draws = np.array([
        [1.0, 0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 1.0],
    ])
    team = np.array([0, 0])
    final_point = np.array([0.51, 0.49])  # player 0 nominally #1
    sep = top_gap_separation(draws, team, final_point)
    assert np.isclose(sep[0], 0.5)


def test_absent_player_handled() -> None:
    # A player with no minutes in any resample gets NaN, not a crash.
    vaep = np.array([[5.0, 5.0], [0.0, 0.0]])
    xt = np.array([[2.5, 2.5], [0.0, 0.0]])
    touches = np.array([[50.0, 50.0], [0.0, 0.0]])
    minutes = np.array([[450.0, 450.0], [0.0, 0.0]])  # player 1 never played
    group = np.array([0, 0])
    point, draws = bootstrap_ratings(vaep, xt, touches, minutes, group, replicates=50, random_state=1)
    assert np.isnan(point[1])
    assert np.all(np.isnan(draws[1]))
    assert np.all(np.isfinite(draws[0]))


def _run() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")


if __name__ == "__main__":
    _run()
    print("All rating_uncertainty tests passed.")
