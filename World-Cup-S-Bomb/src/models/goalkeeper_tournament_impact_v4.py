"""Qatar 2022 Tournament Goalkeeper Impact v4.

Consequence-aware goalkeeper valuation built on the frozen Event Profile v3
release. Every relevant goalkeeper action is valued by the change it causes in
the team's probability of winning the match (group stage) or surviving the tie
(knockout stage), using only information available immediately before the
action. Identity, nationality, awards, and desired ranks are never inputs.

Channels
--------
- ordinary non-penalty shot stopping (periods 1-4, on target), valued as
  (calibrated out-of-fold goal probability - outcome) x pre-action leverage;
- regular penalties (periods 1-4), valued against a Beta-regularized
  conversion prior with the same leverage scale;
- penalty-shootout win-probability-added from an exact recursive shootout
  state model, credited only for goalkeeper-credited saves;
- supporting cross/claim, sweeping, and distribution percentiles carried over
  from the v3 feature set with explicit availability renormalization.

The v3 fields are never mutated; this module only adds ``*_v4`` outputs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Mapping

import numpy as np
import pandas as pd

MODEL_VERSION = "goalkeeper_tournament_impact_v4"

ORDINARY_MATCH_PERIODS = {1, 2, 3, 4}
SHOOTOUT_PERIOD = 5

REGULATION_MINUTES = 90.0
EXTRA_TIME_MINUTES = 120.0
# Non-shootout goals in the tournament (169 shot goals + 3 own goals) over 64
# matches; symmetric split between the two teams by design so that no
# post-event team-strength information leaks into the state model.
TOURNAMENT_GOALS_PER_MATCH = 172.0 / 64.0

KNOCKOUT_STAGES = {
    "Round of 16",
    "Quarter-finals",
    "Semi-finals",
    "3rd Place Final",
    "Final",
}

# Beta prior strengths for conversion expectations. The priors regularize the
# per-kick expectation, never the realized consequence.
REGULAR_PENALTY_PRIOR_STRENGTH = 8.0
SHOOTOUT_CONVERSION_PRIOR_STRENGTH = 8.0
SHOOTOUT_CONVERSION_FALLBACK = 0.75

MAX_POISSON_GOALS = 12


@dataclass(frozen=True)
class GoalkeeperV4Config:
    """Preregistered aggregation settings for the v4 composite."""

    weights: Mapping[str, float] = field(
        default_factory=lambda: {
            "shot_stopping": 0.50,
            "regular_penalty": 0.10,
            "shootout": 0.25,
            "support": 0.15,
        }
    )
    # Absolute cap on |shootout WPA| entering the composite. Raw WPA is
    # always published alongside the bounded value.
    shootout_bound: float = 0.45
    # Exponent applied to the leverage ratio; 1.0 = full consequence
    # weighting, values below 1.0 dampen extreme states.
    leverage_exponent: float = 1.0
    # Channel reliability constants (channel-appropriate evidence counts).
    shot_reliability_count: float = 15.0
    penalty_reliability_count: float = 3.0
    shootout_reliability_count: float = 4.0
    support_reliability_count: float = 20.0

    def __post_init__(self) -> None:
        expected = {"shot_stopping", "regular_penalty", "shootout", "support"}
        if set(self.weights) != expected:
            raise ValueError(
                f"v4 weights must have exactly these keys: {sorted(expected)}"
            )
        if any(
            not np.isfinite(value) or value < 0.0
            for value in self.weights.values()
        ):
            raise ValueError("v4 weights must be finite and nonnegative")
        if abs(sum(self.weights.values()) - 1.0) > 1e-12:
            raise ValueError("v4 weights must sum to one")
        if not 0.0 < self.shootout_bound <= 1.0:
            raise ValueError("shootout_bound must be in (0, 1]")
        if not 0.0 < self.leverage_exponent <= 1.0:
            raise ValueError("leverage_exponent must be in (0, 1]")
        for name in (
            "shot_reliability_count",
            "penalty_reliability_count",
            "shootout_reliability_count",
            "support_reliability_count",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")


# ---------------------------------------------------------------------------
# Match-state consequence model
# ---------------------------------------------------------------------------


@lru_cache(maxsize=100_000)
def _poisson_pmf_vector(rate_milli: int) -> tuple[float, ...]:
    rate = rate_milli / 1000.0
    probs = [math.exp(-rate)]
    for k in range(1, MAX_POISSON_GOALS + 1):
        probs.append(probs[-1] * rate / k)
    return tuple(probs)


@lru_cache(maxsize=200_000)
def _outcome_probabilities(
    score_diff: int, remaining_milli: int
) -> tuple[float, float, float]:
    """P(win), P(draw), P(loss) at regulation/ET end from the team view.

    Goal arrivals for each side follow independent Poisson processes with the
    symmetric tournament-average intensity over the remaining minutes.
    """

    remaining = max(remaining_milli / 1000.0, 0.0)
    per_team_rate = (
        TOURNAMENT_GOALS_PER_MATCH / 2.0
    ) * remaining / REGULATION_MINUTES
    probs = _poisson_pmf_vector(int(round(per_team_rate * 1000)))
    win = draw = loss = 0.0
    for ours in range(MAX_POISSON_GOALS + 1):
        for theirs in range(MAX_POISSON_GOALS + 1):
            final_diff = score_diff + ours - theirs
            p = probs[ours] * probs[theirs]
            if final_diff > 0:
                win += p
            elif final_diff == 0:
                draw += p
            else:
                loss += p
    total = win + draw + loss
    return win / total, draw / total, loss / total


def match_consequence(
    score_diff: int,
    minute: float,
    period: int,
    knockout: bool,
) -> float:
    """Team consequence value at a pre-action state.

    Group stage: expected points scaled to [0, 1] (win=1, draw=1/3).
    Knockout: survival probability, treating a post-extra-time level score as
    an even shootout. In extra time the draw branch resolves through the
    remaining ET window before the shootout coin-flip applies.
    """

    if period <= 2:
        remaining_regulation = max(REGULATION_MINUTES - minute, 0.0)
        win, draw, _ = _outcome_probabilities(
            int(score_diff), int(round(remaining_regulation * 1000))
        )
        if not knockout:
            return win + draw / 3.0
        # Knockout regulation: draws proceed to extra time.
        et_win, et_draw, et_loss = _extra_time_resolution(0)
        return win + draw * (et_win + 0.5 * et_draw)
    # Extra time.
    remaining_extra = max(EXTRA_TIME_MINUTES - minute, 0.0)
    win, draw, _ = _outcome_probabilities(
        int(score_diff), int(round(remaining_extra * 1000))
    )
    return win + 0.5 * draw


@lru_cache(maxsize=64)
def _extra_time_resolution(score_diff: int) -> tuple[float, float, float]:
    """Win/draw/loss probabilities over a full 30-minute extra time."""

    per_team_rate = (
        TOURNAMENT_GOALS_PER_MATCH / 2.0
    ) * 30.0 / REGULATION_MINUTES
    probs = _poisson_pmf_vector(int(round(per_team_rate * 1000)))
    win = draw = loss = 0.0
    for ours in range(MAX_POISSON_GOALS + 1):
        for theirs in range(MAX_POISSON_GOALS + 1):
            diff = score_diff + ours - theirs
            p = probs[ours] * probs[theirs]
            if diff > 0:
                win += p
            elif diff == 0:
                draw += p
            else:
                loss += p
    total = win + draw + loss
    return win / total, draw / total, loss / total


def shot_leverage(
    score_diff: int,
    minute: float,
    period: int,
    knockout: bool,
) -> float:
    """Consequence swing of the pending shot: C(saved) - C(scored)."""

    saved = match_consequence(score_diff, minute, period, knockout)
    scored = match_consequence(score_diff - 1, minute, period, knockout)
    return max(saved - scored, 0.0)


# ---------------------------------------------------------------------------
# Shootout win-probability model
# ---------------------------------------------------------------------------


@lru_cache(maxsize=500_000)
def _shootout_win_probability(
    diff: int,
    kicks_taken_a: int,
    kicks_taken_b: int,
    conversion_milli: int,
) -> float:
    """Exact win probability for team A in a best-of-five shootout.

    ``diff`` is A's score minus B's score. Team A kicks first and teams
    alternate strictly, so the next kicker is fully determined by the kick
    counts. After five kicks each, a level score goes to sudden death; each
    sudden-death round is symmetric under the shared conversion probability,
    so the level-at-five state resolves to exactly one half. The regularized
    conversion probability applies identically to every kicker (no identity
    features).
    """

    q = conversion_milli / 1000.0
    if kicks_taken_a >= 5 and kicks_taken_b >= 5:
        if kicks_taken_a == kicks_taken_b:
            if diff > 0:
                return 1.0
            if diff < 0:
                return 0.0
            return 0.5
        # Mid sudden-death round: the team with fewer kicks is next.
        if kicks_taken_a < kicks_taken_b:
            return q * _shootout_win_probability(
                diff + 1, kicks_taken_a + 1, kicks_taken_b, conversion_milli
            ) + (1 - q) * _shootout_win_probability(
                diff, kicks_taken_a + 1, kicks_taken_b, conversion_milli
            )
        return q * _shootout_win_probability(
            diff - 1, kicks_taken_a, kicks_taken_b + 1, conversion_milli
        ) + (1 - q) * _shootout_win_probability(
            diff, kicks_taken_a, kicks_taken_b + 1, conversion_milli
        )
    remaining_a = 5 - kicks_taken_a
    remaining_b = 5 - kicks_taken_b
    if diff - remaining_b > 0:
        return 1.0
    if -diff - remaining_a > 0:
        return 0.0
    # Strict alternation with A first: A kicks when counts are level.
    if kicks_taken_a == kicks_taken_b:
        return q * _shootout_win_probability(
            diff + 1, kicks_taken_a + 1, kicks_taken_b, conversion_milli
        ) + (1 - q) * _shootout_win_probability(
            diff, kicks_taken_a + 1, kicks_taken_b, conversion_milli
        )
    return q * _shootout_win_probability(
        diff - 1, kicks_taken_a, kicks_taken_b + 1, conversion_milli
    ) + (1 - q) * _shootout_win_probability(
        diff, kicks_taken_a, kicks_taken_b + 1, conversion_milli
    )


def reconstruct_shootout_kicks(
    events: pd.DataFrame,
    match_id: int,
    conversion_probability: float,
) -> pd.DataFrame:
    """Per-kick shootout table with pre/post win probabilities.

    Attribution: the goalkeeper on the paired ``Goal Keeper`` event receives
    the kick's defensive WPA only when that event is ``Penalty Saved``.
    Off-target and woodwork misses (``Shot Faced``) carry zero goalkeeper
    credit; the rule is recorded on every row for the audit.
    """

    frame = events.loc[
        events["match_id"].eq(match_id) & events["period"].eq(SHOOTOUT_PERIOD)
    ].sort_values("index")
    shots = frame.loc[frame["type"].eq("Shot")]
    keepers = frame.loc[frame["type"].eq("Goal Keeper")]
    conversion_milli = int(round(conversion_probability * 1000))

    records: list[dict[str, Any]] = []
    taken: dict[str, int] = {}
    scores: dict[str, int] = {}
    teams: list[str] = []
    for shot in shots.itertuples(index=False):
        team = str(shot.team)
        if team not in teams:
            teams.append(team)
        if len(teams) == 1:
            opponent = None
        else:
            opponent = teams[0] if team == teams[1] else teams[1]
        taken.setdefault(team, 0)
        scores.setdefault(team, 0)
        if opponent is not None:
            taken.setdefault(opponent, 0)
            scores.setdefault(opponent, 0)

        first_team = teams[0]
        diff = scores.get(first_team, 0) - (
            scores.get(teams[1], 0) if len(teams) > 1 else 0
        )
        pre_wp_first = _shootout_win_probability(
            diff,
            taken.get(first_team, 0),
            taken.get(teams[1], 0) if len(teams) > 1 else 0,
            conversion_milli,
        )

        outcome = str(shot.shot_outcome)
        scored = outcome == "Goal"
        gk_rows = keepers.loc[
            keepers["index"].gt(shot.index)
            & keepers["index"].le(shot.index + 4)
        ]
        gk_player_id = (
            int(gk_rows.iloc[0]["player_id"]) if len(gk_rows) else None
        )
        gk_player_name = (
            str(gk_rows.iloc[0]["player"]) if len(gk_rows) else None
        )
        gk_type = (
            str(gk_rows.iloc[0]["goalkeeper_type"]) if len(gk_rows) else None
        )
        goalkeeper_credited = gk_type == "Penalty Saved"

        taken[team] += 1
        if scored:
            scores[team] += 1
        diff_after = scores.get(first_team, 0) - (
            scores.get(teams[1], 0) if len(teams) > 1 else 0
        )
        post_wp_first = _shootout_win_probability(
            diff_after,
            taken.get(first_team, 0),
            taken.get(teams[1], 0) if len(teams) > 1 else 0,
            conversion_milli,
        )

        defending_team = opponent
        # WPA for the DEFENDING team is the negative of the kicking-team view
        # when the defending team is the "first" team, and vice versa.
        delta_first = post_wp_first - pre_wp_first
        defending_wpa = (
            delta_first if defending_team == first_team else -delta_first
        )
        records.append(
            {
                "match_id": match_id,
                "kick_number": len(records) + 1,
                "kicking_team": team,
                "defending_team": defending_team,
                "shot_outcome": outcome,
                "scored": scored,
                "goalkeeper_player_id": gk_player_id,
                "goalkeeper_player_name": gk_player_name,
                "goalkeeper_event_type": gk_type,
                "goalkeeper_credited_save": bool(goalkeeper_credited),
                "pre_kick_win_probability_defending": (
                    pre_wp_first
                    if defending_team == first_team
                    else 1.0 - pre_wp_first
                ),
                "post_kick_win_probability_defending": (
                    post_wp_first
                    if defending_team == first_team
                    else 1.0 - post_wp_first
                ),
                "defending_wpa": defending_wpa,
                "goalkeeper_wpa": (
                    defending_wpa if goalkeeper_credited else 0.0
                ),
                "attribution_rule": (
                    "full-credit-goalkeeper-saved"
                    if goalkeeper_credited
                    else "no-credit-not-goalkeeper-credited"
                ),
            }
        )
    return pd.DataFrame.from_records(records)


# ---------------------------------------------------------------------------
# Event extraction
# ---------------------------------------------------------------------------


def _running_score_before(
    events: pd.DataFrame,
) -> pd.DataFrame:
    """Attach pre-action goal counts for both teams to every shot row."""

    goal_mask = (
        events["type"].eq("Shot")
        & events["shot_outcome"].eq("Goal")
        & events["period"].isin(sorted(ORDINARY_MATCH_PERIODS))
    )
    own_goal_mask = events["type"].eq("Own Goal For")
    scoring = events.loc[goal_mask | own_goal_mask, ["match_id", "index", "team"]]
    scoring = scoring.sort_values(["match_id", "index"])
    return scoring


def extract_shot_events_v4(
    events: pd.DataFrame,
    matches: pd.DataFrame,
    goal_probabilities: pd.Series,
    leverage_exponent: float = 1.0,
) -> pd.DataFrame:
    """Per-shot table (periods 1-4, on target) with consequence leverage.

    ``goal_probabilities`` must be indexed like the events frame and carry
    the calibrated out-of-fold goal probability for eligible ordinary
    non-penalty shots (as produced by ``calibrate_post_shot_xg_v3``).
    """

    stage_by_match = matches.set_index("match_id")["competition_stage"]
    scoring = _running_score_before(events)

    shots = events.loc[
        events["type"].eq("Shot")
        & events["period"].isin(sorted(ORDINARY_MATCH_PERIODS))
        & events["shot_outcome"].isin(["Goal", "Saved"])
    ].copy()
    shot_type = shots.get("shot_type")
    regular_penalty = (
        shot_type.fillna("").astype(str).str.contains("Penalty")
        if shot_type is not None
        else pd.Series(False, index=shots.index)
    )
    shots["is_regular_penalty"] = regular_penalty

    records: list[dict[str, Any]] = []
    for match_id, match_shots in shots.groupby("match_id"):
        stage = str(stage_by_match.get(match_id, "Group Stage"))
        knockout = stage in KNOCKOUT_STAGES
        match_scoring = scoring.loc[scoring["match_id"].eq(match_id)]
        match_events = events.loc[events["match_id"].eq(match_id)]
        team_names = sorted(match_events["team"].dropna().astype(str).unique())
        for shot in match_shots.itertuples():
            attacking = str(shot.team)
            defending_candidates = [
                name for name in team_names if name != attacking
            ]
            defending = defending_candidates[0] if defending_candidates else None
            prior = match_scoring.loc[match_scoring["index"].lt(shot.index)]
            goals_for = int(prior["team"].eq(defending).sum())
            goals_against = int(prior["team"].eq(attacking).sum())
            score_diff = goals_for - goals_against
            minute = float(shot.minute) + float(shot.second) / 60.0
            leverage = shot_leverage(
                score_diff, minute, int(shot.period), knockout
            ) ** leverage_exponent
            goal_probability = float(
                goal_probabilities.get(shot.Index, np.nan)
            )
            records.append(
                {
                    "match_id": match_id,
                    "event_index": int(shot.index),
                    "event_id": getattr(shot, "id", None),
                    "period": int(shot.period),
                    "minute": minute,
                    "competition_stage": stage,
                    "knockout": knockout,
                    "attacking_team": attacking,
                    "defending_team": defending,
                    "pre_shot_score_diff_defending": score_diff,
                    "is_regular_penalty": bool(shot.is_regular_penalty),
                    "shot_outcome": str(shot.shot_outcome),
                    "goal": 1.0 if str(shot.shot_outcome) == "Goal" else 0.0,
                    "goal_probability_v3": goal_probability,
                    "leverage_v4": leverage,
                }
            )
    return pd.DataFrame.from_records(records)


# ---------------------------------------------------------------------------
# Channel aggregation
# ---------------------------------------------------------------------------


def _percentile(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    ranked = numeric.rank(method="average", pct=True)
    return ranked


def calculate_goalkeeper_tournament_impact_v4(
    goalkeeper_base: pd.DataFrame,
    shot_events: pd.DataFrame,
    shootout_kicks: pd.DataFrame,
    *,
    config: GoalkeeperV4Config | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Aggregate consequence-valued channels into the v4 score and rank.

    ``goalkeeper_base`` must contain one row per goalkeeper with at least:
    ``player_id``, ``player_name``, ``team``, ``minutes``,
    ``is_main_goalkeeper``, and the v3 support inputs
    (``cross_stopping_rate``, ``claims_p90``, ``sweeper_actions_p90``,
    ``distribution_under_pressure``).
    """

    settings = config or GoalkeeperV4Config()
    output = goalkeeper_base.copy()
    main_mask = output["is_main_goalkeeper"].fillna(False).astype(bool)

    team_of = output.set_index("team")
    ordinary = shot_events.loc[
        ~shot_events["is_regular_penalty"]
        & shot_events["goal_probability_v3"].notna()
    ]
    penalties = shot_events.loc[shot_events["is_regular_penalty"]]

    mean_leverage = float(ordinary["leverage_v4"].mean()) or 1.0

    # Ordinary shot stopping: (p - outcome) x leverage, summed by team.
    ordinary = ordinary.assign(
        prevention_value=(
            ordinary["goal_probability_v3"] - ordinary["goal"]
        ),
    )
    ordinary = ordinary.assign(
        consequence_value=ordinary["prevention_value"]
        * ordinary["leverage_v4"],
        base_value=ordinary["prevention_value"] * mean_leverage,
    )
    shot_by_team = ordinary.groupby("defending_team").agg(
        ordinary_shot_stopping_value_v4=("consequence_value", "sum"),
        ordinary_shot_stopping_base_v4=("base_value", "sum"),
        ordinary_shots_on_target_v4=("consequence_value", "size"),
    )
    shot_by_team["high_leverage_save_value_v4"] = (
        shot_by_team["ordinary_shot_stopping_value_v4"]
        - shot_by_team["ordinary_shot_stopping_base_v4"]
    )

    # Regular penalties: expectation from a Beta-shrunk conversion prior.
    total_pen = len(penalties)
    scored_pen = float(penalties["goal"].sum()) if total_pen else 0.0
    pen_prior = (
        scored_pen + SHOOTOUT_CONVERSION_FALLBACK * REGULAR_PENALTY_PRIOR_STRENGTH
    ) / (total_pen + REGULAR_PENALTY_PRIOR_STRENGTH)
    penalties = penalties.assign(
        consequence_value=(pen_prior - penalties["goal"])
        * penalties["leverage_v4"],
    )
    pen_by_team = penalties.groupby("defending_team").agg(
        regular_penalty_impact_v4=("consequence_value", "sum"),
        regular_penalties_on_target_v4=("consequence_value", "size"),
    )

    # Shootout WPA by goalkeeper id (event-level attribution).
    so_by_gk = shootout_kicks.groupby("goalkeeper_player_id").agg(
        shootout_win_probability_added_raw_v4=("goalkeeper_wpa", "sum"),
        shootout_kicks_faced_v4=("goalkeeper_wpa", "size"),
        shootout_saves_credited_v4=("goalkeeper_credited_save", "sum"),
    )

    for column in (
        "ordinary_shot_stopping_value_v4",
        "ordinary_shot_stopping_base_v4",
        "high_leverage_save_value_v4",
        "ordinary_shots_on_target_v4",
    ):
        output[column] = output["team"].map(shot_by_team[column])
    for column in (
        "regular_penalty_impact_v4",
        "regular_penalties_on_target_v4",
    ):
        output[column] = output["team"].map(pen_by_team[column])
    output["regular_penalty_impact_v4"] = output[
        "regular_penalty_impact_v4"
    ].fillna(0.0)
    output["regular_penalties_on_target_v4"] = output[
        "regular_penalties_on_target_v4"
    ].fillna(0.0)

    player_ids = pd.to_numeric(output["player_id"], errors="coerce")
    output["shootout_win_probability_added_raw_v4"] = player_ids.map(
        so_by_gk["shootout_win_probability_added_raw_v4"]
    ).fillna(0.0)
    output["shootout_kicks_faced_v4"] = player_ids.map(
        so_by_gk["shootout_kicks_faced_v4"]
    ).fillna(0.0)
    output["shootout_saves_credited_v4"] = player_ids.map(
        so_by_gk["shootout_saves_credited_v4"]
    ).fillna(0.0)
    bound = settings.shootout_bound
    output["shootout_win_probability_added_v4"] = output[
        "shootout_win_probability_added_raw_v4"
    ].clip(-bound, bound)

    # Support channels: percentiles across main goalkeepers with explicit
    # availability renormalization; opportunity-shrunk toward neutral 0.5.
    support_inputs = {
        "cross_claim_value_v4": ["cross_stopping_rate", "claims_p90"],
        "sweeping_value_v4": ["sweeper_actions_p90"],
        "distribution_value_v4": ["distribution_under_pressure"],
    }
    support_scores = pd.DataFrame(index=output.index)
    support_available = pd.DataFrame(index=output.index)
    for name, columns in support_inputs.items():
        percentiles = [
            _percentile(output.loc[main_mask, column]).reindex(output.index)
            for column in columns
            if column in output
        ]
        combined = (
            pd.concat(percentiles, axis=1).mean(axis=1)
            if percentiles
            else pd.Series(np.nan, index=output.index)
        )
        support_scores[name] = combined
        support_available[name] = combined.notna()
        output[name] = combined
    support_weight_matrix = support_available.astype(float)
    support_weight_totals = support_weight_matrix.sum(axis=1)
    support_composite = (
        support_scores.fillna(0.0) * support_weight_matrix
    ).sum(axis=1) / support_weight_totals.replace(0.0, np.nan)
    opportunities = pd.to_numeric(
        output.get("actions", pd.Series(np.nan, index=output.index)),
        errors="coerce",
    ).fillna(0.0)
    support_evidence = opportunities / (
        opportunities + settings.support_reliability_count
    )
    output["support_composite_v4"] = (
        0.5 + support_evidence * (support_composite - 0.5)
    ).fillna(0.5)

    # Channel-appropriate reliabilities (published, not double-applied).
    shots_faced = output["ordinary_shots_on_target_v4"].fillna(0.0)
    output["shot_stopping_reliability_v4"] = shots_faced / (
        shots_faced + settings.shot_reliability_count
    )
    output["penalty_reliability_v4"] = output[
        "regular_penalties_on_target_v4"
    ] / (
        output["regular_penalties_on_target_v4"]
        + settings.penalty_reliability_count
    )
    output["shootout_reliability_v4"] = output["shootout_kicks_faced_v4"] / (
        output["shootout_kicks_faced_v4"]
        + settings.shootout_reliability_count
    )
    output["goalkeeper_reliability_v4"] = (
        output["shot_stopping_reliability_v4"]
    )

    weights = settings.weights
    output["goalkeeper_tournament_impact_raw_v4"] = (
        weights["shot_stopping"] * output["ordinary_shot_stopping_value_v4"].fillna(0.0)
        + weights["regular_penalty"] * output["regular_penalty_impact_v4"]
        + weights["shootout"] * output["shootout_win_probability_added_v4"]
        + weights["support"] * (output["support_composite_v4"] - 0.5)
    )

    raw = output.loc[main_mask, "goalkeeper_tournament_impact_raw_v4"]
    low, high = float(raw.min()), float(raw.max())
    span = (high - low) or 1.0
    score = (output["goalkeeper_tournament_impact_raw_v4"] - low) / span
    output["goalkeeper_tournament_impact_score_v4"] = score.where(
        main_mask, np.nan
    ).clip(0.0, 1.0)
    ranks = (
        output.loc[main_mask, "goalkeeper_tournament_impact_score_v4"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    output["goalkeeper_tournament_impact_rank_v4"] = pd.Series(
        pd.NA, index=output.index, dtype="Int64"
    )
    output.loc[main_mask, "goalkeeper_tournament_impact_rank_v4"] = ranks
    output["ordinary_shot_stopping_value_v4"] = output[
        "ordinary_shot_stopping_value_v4"
    ].fillna(0.0)

    audit = {
        "model_version": MODEL_VERSION,
        "weights": dict(weights),
        "shootout_bound": settings.shootout_bound,
        "leverage_exponent": settings.leverage_exponent,
        "regular_penalty_conversion_prior": pen_prior,
        "mean_ordinary_leverage": mean_leverage,
        "identity_features_used": [],
        "ordinary_shots_valued": int(len(ordinary)),
        "regular_penalties_valued": int(len(penalties)),
        "shootout_kicks_valued": int(len(shootout_kicks)),
        "shootout_saves_credited": int(
            shootout_kicks["goalkeeper_credited_save"].sum()
        ),
        "score_normalization": {
            "raw_min": low,
            "raw_max": high,
        },
    }
    return output, audit
