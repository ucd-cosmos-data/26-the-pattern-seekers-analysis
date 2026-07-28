"""Match-level uncertainty for the V4 player ratings.

The production player rating is a point estimate:

    raw    = 0.50*VAEP/90 + 0.30*VAEP-per-touch + 0.20*xT/90
    final  = reliability*raw + (1 - reliability)*position_group_mean(raw)
    reliability = minutes / (minutes + 300)

It carries no uncertainty, so there is no way to tell which ranking gaps are real
and which are sampling noise — a gap the README lists as open ("player-ranking
stability") and which matters because a player is graded on a handful of matches.

This module attaches that uncertainty **without changing any grade**. It reruns
the exact production formula on match-cluster bootstrap resamples (whole matches
resampled with replacement, respecting the within-match correlation the README
flags), recomputing every player's rating — and the position-group prior — on
each resample. The spread of a player's bootstrap ratings is its standard error;
re-ranking each resample gives rank stability and pairwise separation.

Scope: this is *match-sampling* uncertainty (how much a rating depends on the
particular matches played), holding the per-action VAEP/xT values fixed. It is
not model-parameter uncertainty. Pure numpy — no pandas — so it is unit-testable
on plain arrays.
"""

from __future__ import annotations

import numpy as np


def _group_mean(values: np.ndarray, group_id: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Position-group mean of ``values`` over valid players, broadcast per player."""
    size = int(group_id.max()) + 1
    sums = np.bincount(group_id[valid], weights=values[valid], minlength=size)
    counts = np.bincount(group_id[valid], minlength=size)
    means = np.where(counts > 0, sums / np.maximum(counts, 1), np.nan)
    return means[group_id]


def compute_ratings(
    sum_vaep: np.ndarray,
    sum_xt: np.ndarray,
    sum_touches: np.ndarray,
    sum_minutes: np.ndarray,
    group_id: np.ndarray,
    *,
    min_minutes: float = 300.0,
    weights: tuple[float, float, float] = (0.50, 0.30, 0.20),
) -> tuple[np.ndarray, np.ndarray]:
    """The exact production rating, computed from summed per-match ingredients.

    Returns ``(raw_rating, final_rating)``. Players with no sampled minutes/touches
    get NaN (undefined), and are excluded from the position-group prior.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        vaep_p90 = np.where(sum_minutes > 0, sum_vaep / sum_minutes * 90.0, np.nan)
        vaep_per_touch = np.where(sum_touches > 0, sum_vaep / sum_touches, np.nan)
        xt_p90 = np.where(sum_minutes > 0, sum_xt / sum_minutes * 90.0, np.nan)

    raw = weights[0] * vaep_p90 + weights[1] * vaep_per_touch + weights[2] * xt_p90
    valid = np.isfinite(raw)
    role_prior = _group_mean(raw, group_id, valid)
    with np.errstate(divide="ignore", invalid="ignore"):
        reliability = np.where(
            sum_minutes > 0, sum_minutes / (sum_minutes + min_minutes), np.nan
        )
    final = reliability * raw + (1.0 - reliability) * role_prior
    return raw, final


def bootstrap_ratings(
    vaep: np.ndarray,
    xt: np.ndarray,
    touches: np.ndarray,
    minutes: np.ndarray,
    group_id: np.ndarray,
    *,
    min_minutes: float = 300.0,
    weights: tuple[float, float, float] = (0.50, 0.30, 0.20),
    replicates: int = 2000,
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Match-cluster bootstrap of the final rating.

    ``vaep``/``xt``/``touches``/``minutes`` are ``(n_players, n_matches)`` matrices
    of per-player-per-match sums (zero where a player did not feature). Each
    replicate resamples whole matches with replacement and recomputes every
    player's rating. Returns ``(final_point, final_draws)`` where ``final_point``
    is the rating on the observed data and ``final_draws`` is ``(n_players,
    replicates)``.
    """
    if not (vaep.shape == xt.shape == touches.shape == minutes.shape):
        raise ValueError("All per-match matrices must share shape (players, matches)")
    n_players, n_matches = vaep.shape
    rng = np.random.default_rng(random_state)

    _, final_point = compute_ratings(
        vaep.sum(1), xt.sum(1), touches.sum(1), minutes.sum(1), group_id,
        min_minutes=min_minutes, weights=weights,
    )

    draws = np.empty((n_players, replicates), dtype=float)
    for b in range(replicates):
        sampled = rng.integers(0, n_matches, size=n_matches)
        counts = np.bincount(sampled, minlength=n_matches).astype(float)
        _, final_b = compute_ratings(
            vaep @ counts, xt @ counts, touches @ counts, minutes @ counts,
            group_id, min_minutes=min_minutes, weights=weights,
        )
        draws[:, b] = final_b
    return final_point, draws


def rank_within_teams(draws: np.ndarray, team_id: np.ndarray) -> np.ndarray:
    """Descending rank (1 = best) within each team, per replicate.

    ``draws`` is ``(n_players, replicates)``; NaN ratings (player absent from a
    resample) become NaN ranks and do not affect teammates' ranks.
    """
    ranks = np.full(draws.shape, np.nan, dtype=float)
    for team in np.unique(team_id):
        idx = np.flatnonzero(team_id == team)
        block = draws[idx]  # (team_size, replicates)
        filled = np.where(np.isnan(block), -np.inf, block)
        # rank = 1 + number of teammates strictly better this replicate.
        # better[p, j, b] = rating of teammate j exceeds rating of player p.
        better = filled[None, :, :] > filled[:, None, :]
        block_ranks = 1.0 + better.sum(axis=1)
        block_ranks[np.isnan(block)] = np.nan
        ranks[idx] = block_ranks
    return ranks


def summarize(
    final_point: np.ndarray,
    draws: np.ndarray,
    team_id: np.ndarray,
    *,
    lower: float = 2.5,
    upper: float = 97.5,
) -> dict[str, np.ndarray]:
    """Per-player point estimate, standard error, CI, and rank stability."""
    rank_draws = rank_within_teams(draws, team_id)
    with np.errstate(invalid="ignore"):
        se = np.nanstd(draws, axis=1, ddof=1)
        ci_low = np.nanpercentile(draws, lower, axis=1)
        ci_high = np.nanpercentile(draws, upper, axis=1)
        mean_rank = np.nanmean(rank_draws, axis=1)
        p_rank1 = np.nanmean(rank_draws == 1, axis=1)
        p_top3 = np.nanmean(rank_draws <= 3, axis=1)
    return {
        "final_point": final_point,
        "rating_se": se,
        "rating_ci_low": ci_low,
        "rating_ci_high": ci_high,
        "mean_rank": mean_rank,
        "p_rank1": p_rank1,
        "p_top3": p_top3,
    }


def top_gap_separation(draws: np.ndarray, team_id: np.ndarray, final_point: np.ndarray) -> dict[int, float]:
    """P(the point-#1 player really outranks the point-#2 player) per team.

    A joint probability over the same resamples, so it respects the shared-match
    correlation between teammates. ~0.5 means the top two are a coin-flip; ~1.0
    means the #1 is statistically separated.
    """
    result: dict[int, float] = {}
    for team in np.unique(team_id):
        idx = np.flatnonzero(team_id == team)
        if len(idx) < 2:
            result[int(team)] = float("nan")
            continue
        order = idx[np.argsort(-final_point[idx])]
        first, second = order[0], order[1]
        both = np.isfinite(draws[first]) & np.isfinite(draws[second])
        if not both.any():
            result[int(team)] = float("nan")
            continue
        result[int(team)] = float(np.mean(draws[first][both] > draws[second][both]))
    return result
