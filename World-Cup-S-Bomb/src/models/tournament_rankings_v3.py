"""Qatar 2022 v3 tournament-impact, role-quality, and uncertainty products.

This module is deliberately independent of the legacy position-normalized
publication layer.  It implements three separate products:

``Tournament Impact``
    A signed total in common contribution units.  No player identity, team
    identity, reporting position, role label, or minutes multiplier enters
    this score.

``Role Quality``
    One empirical-Bayes posterior rate.  Role probabilities affect the prior
    interpretation only; they never add value to Tournament Impact.  Evidence
    is shrunk exactly once.

``Uncertainty``
    Match-bootstrap score and rank intervals.  The interval is descriptive and
    is never converted into another score penalty.

Only periods 1--4 are eligible for ordinary outfield outcomes.  Period-five
shootout attempts are retained by :mod:`src.features.event_scope`, but none of
the fields used here can consume them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

from src.features.event_scope import (
    EVENT_SCOPE_VERSION,
    aggregate_player_outcomes,
)


V3_MODEL_VERSION = "qatar-2022-ranking-v3"
V3_SCHEMA_VERSION = "3.0.0"

NON_SHOOTOUT_OUTCOME_FIELDS = (
    "open_play_goals",
    "non_penalty_goals",
    "regular_penalty_goals",
    "regulation_extra_time_goals",
    "assists",
    "xg_non_shootout",
    "xg_non_penalty",
    "xa_non_shootout",
)

SHOOTOUT_AUDIT_FIELDS = ("shootout_attempts", "shootout_goals")

CORE_ATTACK_ABLATIONS = (
    "process_only",
    "outcomes_only",
    "process_plus_shrunk_residual",
    "process_plus_full_outcomes",
)

IDENTITY_FIELDS_EXCLUDED_FROM_SCORING = frozenset(
    {
        "player",
        "player_name",
        "player_id",
        "team",
        "team_name",
        "position",
        "position_group",
        "position_group_360",
        "functional_role",
        "role",
        "award",
        "advancement_stage",
    }
)

V3_COMPATIBILITY_FIELDS: Mapping[str, str] = {
    "Global Rank v3": "global_rank_v3",
    "Team Rank v3": "team_rank_v3",
    "Position Rank v3": "position_rank_v3",
    "Role Rank v3": "role_rank_v3",
    "Tournament Impact v3": "tournament_impact_v3",
    "Role Quality v3": "role_quality_v3",
    "Uncertainty Low v3": "uncertainty_low_v3",
    "Uncertainty High v3": "uncertainty_high_v3",
}


@dataclass(frozen=True)
class TournamentRankingV3Config:
    """Deterministic, identity-free v3 scoring settings.

    Process, defense, and other value columns must already be in compatible
    event-value units.  Every weight is non-negative so increasing a positive
    contribution cannot reduce Tournament Impact.  Errors enter as negative
    values in the same signed columns.
    """

    process_value_columns: tuple[str, ...] = (
        "expected_action_value_non_shootout",
    )
    process_value_weights: tuple[float, ...] = (1.0,)
    xt_vaep_overlap_columns: tuple[str, ...] = ()
    xt_vaep_overlap_weights: tuple[float, ...] = ()
    defensive_value_columns: tuple[str, ...] = (
        "defensive_value_non_shootout",
    )
    defensive_value_weights: tuple[float, ...] = (1.0,)
    other_value_columns: tuple[str, ...] = ()
    other_value_weights: tuple[float, ...] = ()
    selected_attack_candidate: str = "process_plus_shrunk_residual"
    process_includes_realized_outcomes: bool = True
    regular_penalty_weight: float = 0.76
    assist_value: float = 0.35
    goal_residual_cap: float = 1.25
    assist_residual_cap: float = 0.75
    residual_prior_opportunities: float = 2.0
    role_probability_columns: tuple[str, ...] = ()
    role_prior_strength: float = 3.0
    role_prior_strength_grid: tuple[float, ...] = (
        0.25,
        0.5,
        1.0,
        2.0,
        3.0,
        5.0,
        8.0,
        12.0,
    )
    role_quality_evidence_column: str = (
        "positive_contribution_value_non_shootout"
    )
    bootstrap_replicates: int = 500
    bootstrap_confidence: float = 0.90
    random_seed: int = 42
    attack_cv_splits: int = 5
    attack_noninferiority_margin: float = 0.02
    attack_correlation_margin: float = 0.02
    attack_bootstrap_replicates: int = 500

    def __post_init__(self) -> None:
        _validate_weight_contract(
            self.process_value_columns,
            self.process_value_weights,
            "process",
            require_nonempty=True,
        )
        _validate_weight_contract(
            self.xt_vaep_overlap_columns,
            self.xt_vaep_overlap_weights,
            "xT/VAEP overlap",
        )
        _validate_weight_contract(
            self.defensive_value_columns,
            self.defensive_value_weights,
            "defense",
        )
        _validate_weight_contract(
            self.other_value_columns,
            self.other_value_weights,
            "other",
        )
        if self.selected_attack_candidate not in CORE_ATTACK_ABLATIONS:
            raise ValueError(
                "selected_attack_candidate must be one of "
                f"{CORE_ATTACK_ABLATIONS}"
            )
        if not 0.0 <= self.regular_penalty_weight <= 1.0:
            raise ValueError("regular_penalty_weight must be within [0, 1]")
        if self.assist_value < 0.0:
            raise ValueError("assist_value cannot be negative")
        if self.goal_residual_cap <= 0.0:
            raise ValueError("goal_residual_cap must be positive")
        if self.assist_residual_cap <= 0.0:
            raise ValueError("assist_residual_cap must be positive")
        if self.residual_prior_opportunities <= 0.0:
            raise ValueError(
                "residual_prior_opportunities must be positive"
            )
        if self.role_prior_strength < 0.0:
            raise ValueError("role_prior_strength cannot be negative")
        if not self.role_prior_strength_grid:
            raise ValueError("role_prior_strength_grid cannot be empty")
        if any(value < 0.0 for value in self.role_prior_strength_grid):
            raise ValueError("role prior grid cannot contain negative values")
        if self.bootstrap_replicates < 2:
            raise ValueError("bootstrap_replicates must be at least two")
        if not 0.0 < self.bootstrap_confidence < 1.0:
            raise ValueError("bootstrap_confidence must be within (0, 1)")
        if self.attack_cv_splits < 2:
            raise ValueError("attack_cv_splits must be at least two")
        if self.attack_noninferiority_margin < 0.0:
            raise ValueError(
                "attack_noninferiority_margin cannot be negative"
            )
        if self.attack_correlation_margin < 0.0:
            raise ValueError(
                "attack_correlation_margin cannot be negative"
            )
        if self.attack_bootstrap_replicates < 2:
            raise ValueError(
                "attack_bootstrap_replicates must be at least two"
            )


def _validate_weight_contract(
    columns: Sequence[str],
    weights: Sequence[float],
    label: str,
    *,
    require_nonempty: bool = False,
) -> None:
    if require_nonempty and not columns:
        raise ValueError(f"{label} value columns cannot be empty")
    if len(columns) != len(weights):
        raise ValueError(f"{label} columns and weights must have equal length")
    if len(set(columns)) != len(columns):
        raise ValueError(f"{label} value columns must be unique")
    if any(not np.isfinite(weight) or weight < 0.0 for weight in weights):
        raise ValueError(f"{label} weights must be finite and non-negative")
    forbidden = IDENTITY_FIELDS_EXCLUDED_FROM_SCORING.intersection(columns)
    if forbidden:
        raise ValueError(
            f"{label} scoring columns include identity fields: "
            f"{sorted(forbidden)}"
        )


def _numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame:
        raise ValueError(f"v3 ranking input is missing {column!r}")
    values = pd.to_numeric(frame[column], errors="coerce")
    if values.isna().any():
        raise ValueError(f"v3 ranking input {column!r} contains missing values")
    if not np.isfinite(values.to_numpy(dtype=float)).all():
        raise ValueError(
            f"v3 ranking input {column!r} contains non-finite values"
        )
    return values.astype(float)


def _optional_weighted_sum(
    frame: pd.DataFrame,
    columns: Sequence[str],
    weights: Sequence[float],
) -> pd.Series:
    total = pd.Series(0.0, index=frame.index, dtype=float)
    for column, weight in zip(columns, weights, strict=True):
        total = total + weight * _numeric(frame, column)
    return total


def aggregate_non_shootout_outcomes(
    events: pd.DataFrame,
    *,
    group_columns: Sequence[str] = ("team", "player_id"),
) -> pd.DataFrame:
    """Materialize the v3 outcome contract through the shared scope helper."""

    outcomes = aggregate_player_outcomes(
        events,
        group_columns=group_columns,
    )
    if not outcomes["event_scope_version"].eq(EVENT_SCOPE_VERSION).all():
        raise AssertionError("Unexpected event-scope version")
    return outcomes


def validate_non_shootout_outcome_contract(frame: pd.DataFrame) -> None:
    """Reject implicit or shootout-contaminated ordinary outcome inputs."""

    missing = set(NON_SHOOTOUT_OUTCOME_FIELDS).difference(frame.columns)
    if missing:
        raise ValueError(
            "v3 ranking requires explicit non-shootout outcomes: "
            f"{sorted(missing)}"
        )
    for column in NON_SHOOTOUT_OUTCOME_FIELDS:
        values = _numeric(frame, column)
        if (values < 0.0).any():
            raise ValueError(f"{column!r} cannot contain negative values")
    goals = _numeric(frame, "regulation_extra_time_goals")
    split_goals = _numeric(frame, "non_penalty_goals") + _numeric(
        frame,
        "regular_penalty_goals",
    )
    if not np.allclose(goals, split_goals, atol=1e-10, rtol=0.0):
        raise ValueError(
            "regulation_extra_time_goals must equal non-penalty plus "
            "regular-penalty goals"
        )
    if (
        _numeric(frame, "open_play_goals")
        > _numeric(frame, "non_penalty_goals")
    ).any():
        raise ValueError("open_play_goals cannot exceed non_penalty_goals")
    if (
        _numeric(frame, "xg_non_penalty")
        > _numeric(frame, "xg_non_shootout") + 1e-10
    ).any():
        raise ValueError("xg_non_penalty cannot exceed xg_non_shootout")
    if "event_scope_version" in frame and not frame[
        "event_scope_version"
    ].astype(str).eq(EVENT_SCOPE_VERSION).all():
        raise ValueError(
            "v3 ordinary outcomes must use the authoritative event scope"
        )


def build_attack_ablation_scores(
    frame: pd.DataFrame,
    *,
    config: TournamentRankingV3Config | None = None,
) -> pd.DataFrame:
    """Build identity-free offensive candidates without shootout outcomes.

    The shrunk-residual candidate is the safe default when realized action
    value already includes shot outcomes.  The full-outcomes candidate remains
    available as an explicit double-counting diagnostic in that case.
    """

    settings = config or TournamentRankingV3Config()
    validate_non_shootout_outcome_contract(frame)

    process = _optional_weighted_sum(
        frame,
        settings.process_value_columns,
        settings.process_value_weights,
    )
    overlap = _optional_weighted_sum(
        frame,
        settings.xt_vaep_overlap_columns,
        settings.xt_vaep_overlap_weights,
    )
    process_without_overlap = process - overlap

    non_penalty_goals = _numeric(frame, "non_penalty_goals")
    penalty_goals = _numeric(frame, "regular_penalty_goals")
    assists = _numeric(frame, "assists")
    xg_non_penalty = _numeric(frame, "xg_non_penalty")
    xg_non_shootout = _numeric(frame, "xg_non_shootout")
    xa_non_shootout = _numeric(frame, "xa_non_shootout")
    penalty_xg = (xg_non_shootout - xg_non_penalty).clip(lower=0.0)

    outcomes_no_penalties = (
        non_penalty_goals + settings.assist_value * assists
    )
    outcomes = (
        outcomes_no_penalties
        + settings.regular_penalty_weight * penalty_goals
    )

    goal_residual = (non_penalty_goals - xg_non_penalty).clip(
        lower=-settings.goal_residual_cap,
        upper=settings.goal_residual_cap,
    )
    penalty_residual = (penalty_goals - penalty_xg).clip(
        lower=-settings.goal_residual_cap,
        upper=settings.goal_residual_cap,
    )
    assist_residual = (assists - xa_non_shootout).clip(
        lower=-settings.assist_residual_cap,
        upper=settings.assist_residual_cap,
    )
    residual_opportunities = pd.concat(
        [
            xg_non_shootout + xa_non_shootout,
            non_penalty_goals + penalty_goals + assists,
        ],
        axis=1,
    ).max(axis=1)
    residual_reliability = residual_opportunities / (
        residual_opportunities + settings.residual_prior_opportunities
    )
    shrunk_residual_no_penalties = residual_reliability * (
        goal_residual + settings.assist_value * assist_residual
    )
    shrunk_residual = residual_reliability * (
        goal_residual
        + settings.regular_penalty_weight * penalty_residual
        + settings.assist_value * assist_residual
    )

    scores = pd.DataFrame(index=frame.index)
    scores["attack_process_value_v3"] = process
    scores["attack_outcome_value_v3"] = outcomes
    scores["attack_outcome_value_no_penalties_v3"] = outcomes_no_penalties
    scores["attack_realization_residual_v3"] = (
        goal_residual
        + settings.regular_penalty_weight * penalty_residual
        + settings.assist_value * assist_residual
    )
    scores["attack_residual_reliability_v3"] = residual_reliability
    scores["attack_shrunk_realization_residual_v3"] = shrunk_residual

    scores["process_only"] = process
    scores["outcomes_only"] = outcomes
    scores["process_plus_shrunk_residual"] = process + shrunk_residual
    scores["process_plus_full_outcomes"] = process + outcomes
    scores["outcomes_only_no_penalties"] = outcomes_no_penalties
    scores["process_plus_shrunk_residual_no_penalties"] = (
        process + shrunk_residual_no_penalties
    )
    scores["process_plus_full_outcomes_no_penalties"] = (
        process + outcomes_no_penalties
    )
    if settings.xt_vaep_overlap_columns:
        scores["process_only_without_xt_vaep_overlap"] = (
            process_without_overlap
        )
        scores[
            "process_plus_shrunk_residual_without_xt_vaep_overlap"
        ] = process_without_overlap + shrunk_residual
        scores[
            "process_plus_full_outcomes_without_xt_vaep_overlap"
        ] = process_without_overlap + outcomes

    scores["attack_process_includes_realized_outcomes_v3"] = bool(
        settings.process_includes_realized_outcomes
    )
    scores["ordinary_event_periods_v3"] = "1-4"
    scores["shootout_outcomes_used_in_attack_score_v3"] = False
    return scores


def _role_probability_matrix(
    frame: pd.DataFrame,
    settings: TournamentRankingV3Config,
) -> tuple[pd.DataFrame, str]:
    explicit = list(settings.role_probability_columns)
    if not explicit:
        explicit = [
            column
            for column in frame.columns
            if column.startswith(("role_probability_", "role_prob_"))
            and column
            not in {
                "role_probability_coverage",
                "role_probability_entropy",
            }
        ]
    if explicit:
        missing = set(explicit).difference(frame.columns)
        if missing:
            raise ValueError(
                f"role probability columns missing: {sorted(missing)}"
            )
        probabilities = frame[explicit].apply(
            pd.to_numeric,
            errors="coerce",
        ).fillna(0.0)
        if (probabilities < 0.0).any().any():
            raise ValueError("role probabilities cannot be negative")
        row_sum = probabilities.sum(axis=1)
        zero = row_sum.le(0.0)
        probabilities = probabilities.div(
            row_sum.replace(0.0, np.nan),
            axis=0,
        )
        if zero.any():
            probabilities.loc[zero, :] = 1.0 / len(explicit)
        probabilities.columns = [
            column.removeprefix("role_probability_").removeprefix(
                "role_prob_"
            )
            for column in explicit
        ]
        return probabilities.astype(float), "probabilistic-role-columns"

    label_column = next(
        (
            column
            for column in (
                "functional_role",
                "position_group_360",
                "position_group",
            )
            if column in frame
        ),
        None,
    )
    if label_column is None:
        return (
            pd.DataFrame({"overall": 1.0}, index=frame.index),
            "overall-prior-fallback",
        )
    labels = frame[label_column].fillna("Unknown").astype(str)
    probabilities = pd.get_dummies(labels, dtype=float)
    probabilities.index = frame.index
    return probabilities, f"degenerate-probability:{label_column}"


def _role_prior_rates(
    evidence: pd.Series,
    exposure: pd.Series,
    probabilities: pd.DataFrame,
) -> tuple[pd.Series, pd.Series]:
    global_exposure = float(exposure.sum())
    global_prior = (
        float(evidence.sum() / global_exposure)
        if global_exposure > 0.0
        else 0.0
    )
    role_rates: dict[str, float] = {}
    for column in probabilities:
        weights = probabilities[column]
        denominator = float((weights * exposure).sum())
        numerator = float((weights * evidence).sum())
        role_rates[column] = (
            numerator / denominator if denominator > 0.0 else global_prior
        )
    rate_series = pd.Series(role_rates, dtype=float)
    mixture = probabilities.mul(rate_series, axis=1).sum(axis=1)
    return rate_series, mixture


def calculate_role_quality(
    frame: pd.DataFrame,
    tournament_impact: pd.Series,
    *,
    prior_strength: float,
    config: TournamentRankingV3Config,
) -> pd.DataFrame:
    """Apply exactly one empirical-Bayes rate shrinkage.

    Role-quality evidence is required to be non-negative.  If a dedicated
    opportunity-quality numerator is unavailable, positive common-unit impact
    is used as a transparent fallback.  Because both evidence and role priors
    are non-negative, adding exposure with no evidence cannot improve the
    posterior rate.
    """

    minutes = _numeric(frame, "minutes").clip(lower=0.0)
    exposure = minutes / 90.0
    if config.role_quality_evidence_column in frame:
        evidence = _numeric(
            frame,
            config.role_quality_evidence_column,
        )
        source = config.role_quality_evidence_column
    else:
        evidence = tournament_impact.clip(lower=0.0)
        source = "positive_tournament_impact_fallback"
    if (evidence < 0.0).any():
        raise ValueError("Role-quality evidence cannot be negative")

    probabilities, mixture_source = _role_probability_matrix(frame, config)
    role_rates, mixture_prior = _role_prior_rates(
        evidence,
        exposure,
        probabilities,
    )
    denominator = exposure + prior_strength
    posterior = (
        evidence + prior_strength * mixture_prior
    ) / denominator.replace(0.0, np.nan)
    posterior = posterior.fillna(mixture_prior).fillna(0.0)

    output = pd.DataFrame(index=frame.index)
    output["role_quality_v3"] = posterior
    output["role_quality_observed_rate_v3"] = (
        evidence / exposure.replace(0.0, np.nan)
    )
    output["role_quality_prior_rate_v3"] = mixture_prior
    output["role_quality_exposure_v3"] = exposure
    output["role_quality_evidence_v3"] = evidence
    output["role_quality_prior_strength_v3"] = float(prior_strength)
    output["role_quality_reliability_v3"] = (
        exposure / denominator.replace(0.0, np.nan)
    ).fillna(0.0)
    output["role_quality_evidence_source_v3"] = source
    output["role_mixture_source_v3"] = mixture_source
    output["role_quality_shrinkage_count_v3"] = 1
    output.attrs["role_prior_rates"] = role_rates.to_dict()
    return output


def fit_role_prior_strength_match_disjoint(
    match_frame: pd.DataFrame,
    *,
    config: TournamentRankingV3Config | None = None,
    player_column: str = "player_id",
    match_column: str = "match_id",
    minutes_column: str = "minutes",
    evidence_column: str | None = None,
) -> dict[str, Any]:
    """Select the one EB prior strength with leave-one-match-out prediction."""

    settings = config or TournamentRankingV3Config()
    required = {player_column, match_column, minutes_column}
    missing = required.difference(match_frame.columns)
    if missing:
        raise ValueError(
            f"role-prior CV input is missing: {sorted(missing)}"
        )
    if match_frame[match_column].nunique() < 2:
        raise ValueError("role-prior CV requires at least two matches")

    working = match_frame.copy()
    if evidence_column is None:
        evidence_column = settings.role_quality_evidence_column
    evidence = _numeric(working, evidence_column)
    if (evidence < 0.0).any():
        raise ValueError("role-prior CV evidence cannot be negative")
    exposure = _numeric(working, minutes_column).clip(lower=0.0) / 90.0
    working["_role_quality_evidence"] = evidence
    working["_role_quality_exposure"] = exposure
    probabilities, mixture_source = _role_probability_matrix(
        working,
        settings,
    )
    probability_columns = list(probabilities.columns)
    probability_values = probabilities.to_numpy(dtype=float)
    unique_matches = pd.unique(working[match_column])

    candidate_rows: list[dict[str, float]] = []
    for strength in settings.role_prior_strength_grid:
        predictions = np.zeros(len(working), dtype=float)
        for held_out_match in unique_matches:
            test_mask = working[match_column].eq(held_out_match).to_numpy()
            train_mask = ~test_mask
            train_probabilities = pd.DataFrame(
                probability_values[train_mask],
                columns=probability_columns,
            )
            role_rates, _ = _role_prior_rates(
                working.loc[
                    train_mask,
                    "_role_quality_evidence",
                ].reset_index(drop=True),
                working.loc[
                    train_mask,
                    "_role_quality_exposure",
                ].reset_index(drop=True),
                train_probabilities,
            )
            test_probabilities = pd.DataFrame(
                probability_values[test_mask],
                columns=probability_columns,
            )
            test_prior = test_probabilities.mul(
                role_rates,
                axis=1,
            ).sum(axis=1).to_numpy(dtype=float)

            train_history = (
                working.loc[train_mask]
                .groupby(player_column, sort=False)[
                    [
                        "_role_quality_evidence",
                        "_role_quality_exposure",
                    ]
                ]
                .sum()
            )
            test_players = working.loc[
                test_mask,
                player_column,
            ]
            historical_evidence = (
                test_players.map(
                    train_history["_role_quality_evidence"]
                )
                .fillna(0.0)
                .to_numpy(dtype=float)
            )
            historical_exposure = (
                test_players.map(
                    train_history["_role_quality_exposure"]
                )
                .fillna(0.0)
                .to_numpy(dtype=float)
            )
            posterior_rate = (
                historical_evidence + strength * test_prior
            ) / np.where(
                historical_exposure + strength > 0.0,
                historical_exposure + strength,
                1.0,
            )
            predictions[test_mask] = (
                posterior_rate
                * working.loc[
                    test_mask,
                    "_role_quality_exposure",
                ].to_numpy(dtype=float)
            )
        residual = predictions - evidence.to_numpy(dtype=float)
        candidate_rows.append(
            {
                "prior_strength": float(strength),
                "rmse": float(np.sqrt(np.mean(np.square(residual)))),
                "mae": float(np.mean(np.abs(residual))),
            }
        )

    candidates = sorted(
        candidate_rows,
        key=lambda row: (
            row["rmse"],
            row["mae"],
            row["prior_strength"],
        ),
    )
    selected = candidates[0]
    return {
        "selected_prior_strength": selected["prior_strength"],
        "selection_metric": "leave-one-match-out-rmse",
        "match_disjoint": True,
        "n_matches": int(len(unique_matches)),
        "n_rows": int(len(working)),
        "role_mixture_source": mixture_source,
        "candidates": candidate_rows,
    }


def bootstrap_match_uncertainty(
    match_contributions: pd.DataFrame,
    *,
    all_player_ids: Sequence[Any] | None = None,
    player_column: str = "player_id",
    match_column: str = "match_id",
    contribution_column: str = "tournament_impact_match_v3",
    replicates: int = 500,
    confidence: float = 0.90,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Return deterministic match-bootstrap total-impact and rank intervals."""

    required = {player_column, match_column, contribution_column}
    missing = required.difference(match_contributions.columns)
    if missing:
        raise ValueError(
            f"bootstrap input is missing: {sorted(missing)}"
        )
    if replicates < 2:
        raise ValueError("replicates must be at least two")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be within (0, 1)")

    working = match_contributions[
        [player_column, match_column, contribution_column]
    ].copy()
    working[contribution_column] = _numeric(
        working,
        contribution_column,
    )
    matches = pd.Index(pd.unique(working[match_column]))
    if matches.empty:
        raise ValueError("bootstrap input contains no matches")
    players = (
        pd.Index(pd.unique(working[player_column]))
        if all_player_ids is None
        else pd.Index(all_player_ids)
    )
    if players.has_duplicates:
        players = players.drop_duplicates()

    pivot = (
        working.groupby(
            [match_column, player_column],
            sort=False,
        )[contribution_column]
        .sum()
        .unstack(player_column, fill_value=0.0)
        .reindex(index=matches, columns=players, fill_value=0.0)
    )
    matrix = pivot.to_numpy(dtype=float)
    rng = np.random.default_rng(random_seed)
    draw_indices = rng.integers(
        0,
        len(matches),
        size=(replicates, len(matches)),
    )
    sampled_totals = matrix[draw_indices, :].sum(axis=1)

    order = np.argsort(-sampled_totals, axis=1, kind="stable")
    sampled_ranks = np.empty_like(order, dtype=float)
    row_indices = np.arange(replicates)[:, None]
    sampled_ranks[row_indices, order] = (
        np.arange(len(players), dtype=float) + 1.0
    )

    alpha = (1.0 - confidence) / 2.0
    impact_low = np.quantile(sampled_totals, alpha, axis=0)
    impact_high = np.quantile(sampled_totals, 1.0 - alpha, axis=0)
    rank_best = np.quantile(sampled_ranks, alpha, axis=0)
    rank_worst = np.quantile(sampled_ranks, 1.0 - alpha, axis=0)
    rank_width = rank_worst - rank_best
    status = np.select(
        [rank_width <= 5.0, rank_width <= 15.0],
        ["stable", "moderate"],
        default="wide",
    )
    return pd.DataFrame(
        {
            player_column: players,
            "uncertainty_low_v3": impact_low,
            "uncertainty_high_v3": impact_high,
            "uncertainty_std_v3": sampled_totals.std(axis=0, ddof=1),
            "bootstrap_rank_best_v3": np.floor(rank_best).astype(int),
            "bootstrap_rank_worst_v3": np.ceil(rank_worst).astype(int),
            "uncertainty_status_v3": status,
            "uncertainty_method_v3": "match-bootstrap",
            "uncertainty_replicates_v3": int(replicates),
            "uncertainty_confidence_v3": float(confidence),
        }
    )


def _rank_descending(values: pd.Series) -> pd.Series:
    return values.rank(method="min", ascending=False).astype("Int64")


def _spearman(left: pd.Series, right: pd.Series) -> float:
    joined = pd.concat(
        [
            pd.to_numeric(left, errors="coerce"),
            pd.to_numeric(right, errors="coerce"),
        ],
        axis=1,
    ).dropna()
    if len(joined) < 2:
        return float("nan")
    if joined.iloc[:, 0].nunique() < 2 or joined.iloc[:, 1].nunique() < 2:
        return float("nan")
    return float(joined.iloc[:, 0].corr(joined.iloc[:, 1], method="spearman"))


def calculate_tournament_rankings_v3(
    players: pd.DataFrame,
    *,
    match_contributions: pd.DataFrame | None = None,
    config: TournamentRankingV3Config | None = None,
    selected_attack_candidate: str | None = None,
) -> pd.DataFrame:
    """Calculate shadow v3 rankings without repurposing legacy columns."""

    settings = config or TournamentRankingV3Config()
    required = {"player_id", "team", "minutes"}
    missing = required.difference(players.columns)
    if missing:
        raise ValueError(f"v3 ranking input is missing: {sorted(missing)}")
    if players["player_id"].duplicated().any():
        raise ValueError("v3 ranking input requires one row per player_id")

    attack = build_attack_ablation_scores(players, config=settings)
    candidate = (
        selected_attack_candidate or settings.selected_attack_candidate
    )
    if candidate not in CORE_ATTACK_ABLATIONS:
        raise ValueError(
            f"selected attack candidate must be one of {CORE_ATTACK_ABLATIONS}"
        )
    defense = _optional_weighted_sum(
        players,
        settings.defensive_value_columns,
        settings.defensive_value_weights,
    )
    other = _optional_weighted_sum(
        players,
        settings.other_value_columns,
        settings.other_value_weights,
    )
    impact = attack[candidate] + defense + other

    output = players.copy()
    for column in (
        "attack_process_value_v3",
        "attack_outcome_value_v3",
        "attack_realization_residual_v3",
        "attack_residual_reliability_v3",
        "attack_shrunk_realization_residual_v3",
    ):
        output[column] = attack[column]
    output["attack_component_v3"] = attack[candidate]
    output["attack_model_v3"] = candidate
    output["defensive_component_v3"] = defense
    output["other_component_v3"] = other
    output["tournament_impact_v3"] = impact
    output["tournament_impact_common_units_v3"] = impact
    output["tournament_impact_percentile_v3"] = impact.rank(
        method="average",
        pct=True,
    )
    output["global_rank_v3"] = _rank_descending(impact)
    output["team_rank_v3"] = (
        output.groupby("team", sort=False)["tournament_impact_v3"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )

    prior_strength = settings.role_prior_strength
    prior_selection: dict[str, Any] | None = None
    if match_contributions is not None:
        evidence_column = settings.role_quality_evidence_column
        if evidence_column in match_contributions:
            role_cv_frame = match_contributions.copy()
            if settings.role_probability_columns:
                missing_role_probabilities = set(
                    settings.role_probability_columns
                ).difference(role_cv_frame.columns)
                if missing_role_probabilities:
                    role_columns = [
                        "player_id",
                        *sorted(missing_role_probabilities),
                    ]
                    role_cv_frame = role_cv_frame.merge(
                        players[role_columns],
                        on="player_id",
                        how="left",
                        validate="many_to_one",
                    )
            prior_selection = fit_role_prior_strength_match_disjoint(
                role_cv_frame,
                config=settings,
                evidence_column=evidence_column,
            )
            prior_strength = float(
                prior_selection["selected_prior_strength"]
            )
    role_quality = calculate_role_quality(
        players,
        impact,
        prior_strength=prior_strength,
        config=settings,
    )
    for column in role_quality:
        output[column] = role_quality[column]

    position_column = next(
        (
            column
            for column in ("position_group_360", "position_group", "position")
            if column in output
        ),
        None,
    )
    role_column = next(
        (
            column
            for column in ("functional_role", "role")
            if column in output
        ),
        None,
    )
    if position_column is None:
        output["position_rank_v3"] = _rank_descending(
            output["role_quality_v3"]
        )
    else:
        output["position_rank_v3"] = (
            output.groupby(position_column, dropna=False, sort=False)[
                "role_quality_v3"
            ]
            .rank(method="min", ascending=False)
            .astype("Int64")
        )
    if role_column is None:
        output["role_rank_v3"] = _rank_descending(
            output["role_quality_v3"]
        )
    else:
        output["role_rank_v3"] = (
            output.groupby(role_column, dropna=False, sort=False)[
                "role_quality_v3"
            ]
            .rank(method="min", ascending=False)
            .astype("Int64")
        )

    if match_contributions is None:
        output["uncertainty_low_v3"] = np.nan
        output["uncertainty_high_v3"] = np.nan
        output["uncertainty_std_v3"] = np.nan
        output["bootstrap_rank_best_v3"] = pd.Series(
            pd.NA,
            index=output.index,
            dtype="Int64",
        )
        output["bootstrap_rank_worst_v3"] = pd.Series(
            pd.NA,
            index=output.index,
            dtype="Int64",
        )
        output["uncertainty_status_v3"] = "not-estimated"
        output["uncertainty_method_v3"] = "match-input-required"
        output["uncertainty_replicates_v3"] = 0
        output["uncertainty_confidence_v3"] = (
            settings.bootstrap_confidence
        )
    else:
        match_values = match_contributions.copy()
        if "tournament_impact_match_v3" not in match_values:
            match_attack = build_attack_ablation_scores(
                match_values,
                config=settings,
            )
            match_defense = _optional_weighted_sum(
                match_values,
                settings.defensive_value_columns,
                settings.defensive_value_weights,
            )
            match_other = _optional_weighted_sum(
                match_values,
                settings.other_value_columns,
                settings.other_value_weights,
            )
            match_values["tournament_impact_match_v3"] = (
                match_attack[candidate] + match_defense + match_other
            )
        uncertainty = bootstrap_match_uncertainty(
            match_values,
            all_player_ids=output["player_id"].tolist(),
            replicates=settings.bootstrap_replicates,
            confidence=settings.bootstrap_confidence,
            random_seed=settings.random_seed,
        ).set_index("player_id")
        for column in uncertainty:
            output[column] = output["player_id"].map(uncertainty[column])
        for column in (
            "bootstrap_rank_best_v3",
            "bootstrap_rank_worst_v3",
        ):
            output[column] = output[column].astype("Int64")

    output["ranking_model_version_v3"] = V3_MODEL_VERSION
    output["ranking_schema_version_v3"] = V3_SCHEMA_VERSION
    output["ranking_release_status_v3"] = "shadow"
    output["ordinary_event_periods_v3"] = "1-4"
    output["shootout_outcomes_used_v3"] = False
    output["position_normalization_used_for_impact_v3"] = False
    output["team_identity_used_for_score_v3"] = False
    output["player_identity_used_for_score_v3"] = False
    output["uncertainty_used_as_score_penalty_v3"] = False
    output["legacy_fields_status_v3"] = "preserved-not-repurposed"
    output["role_prior_selection_method_v3"] = (
        prior_selection["selection_metric"]
        if prior_selection is not None
        else "configured-fallback-no-match-evidence"
    )
    for compatibility, source in V3_COMPATIBILITY_FIELDS.items():
        output[compatibility] = output[source]
    output.attrs["role_prior_selection"] = prior_selection
    output.attrs["score_feature_contract"] = score_feature_contract(settings)
    return output


def score_feature_contract(
    config: TournamentRankingV3Config | None = None,
) -> dict[str, Any]:
    """Return a structured audit of all columns allowed to affect impact."""

    settings = config or TournamentRankingV3Config()
    scoring_columns = [
        *settings.process_value_columns,
        *settings.xt_vaep_overlap_columns,
        *settings.defensive_value_columns,
        *settings.other_value_columns,
        *NON_SHOOTOUT_OUTCOME_FIELDS,
    ]
    return {
        "model_version": V3_MODEL_VERSION,
        "schema_version": V3_SCHEMA_VERSION,
        "ordinary_event_periods": [1, 2, 3, 4],
        "shootout_period": 5,
        "shootout_used_in_outfield_score": False,
        "scoring_columns": list(dict.fromkeys(scoring_columns)),
        "identity_fields_excluded": sorted(
            IDENTITY_FIELDS_EXCLUDED_FROM_SCORING
        ),
        "position_normalization_used_for_tournament_impact": False,
        "reliability_treatments_for_role_quality": 1,
        "uncertainty_used_as_score_penalty": False,
    }


def ranking_gate_diagnostics(ranked: pd.DataFrame) -> dict[str, Any]:
    """Return generalized, identity-free diagnostics for a shadow v3 table."""

    required = {
        "tournament_impact_v3",
        "global_rank_v3",
        "team_rank_v3",
        "role_quality_v3",
        "minutes",
    }
    missing = required.difference(ranked.columns)
    if missing:
        raise ValueError(f"v3 diagnostics input is missing: {sorted(missing)}")
    expected_global = _rank_descending(ranked["tournament_impact_v3"])
    global_order_agrees = expected_global.equals(
        ranked["global_rank_v3"].astype("Int64")
    )
    expected_team = (
        ranked.groupby("team", sort=False)["tournament_impact_v3"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    team_order_agrees = expected_team.equals(
        ranked["team_rank_v3"].astype("Int64")
    )
    goals_column = (
        "regulation_extra_time_goals"
        if "regulation_extra_time_goals" in ranked
        else None
    )
    position_column = next(
        (
            column
            for column in ("position_group_360", "position_group", "position")
            if column in ranked
        ),
        None,
    )
    composition: dict[str, dict[str, int]] = {}
    if position_column is not None:
        ordered = ranked.sort_values(
            ["global_rank_v3"],
            kind="mergesort",
        )
        for k in (20, 50, 100):
            composition[str(k)] = {
                str(label): int(count)
                for label, count in ordered.head(k)[position_column]
                .fillna("Unknown")
                .value_counts()
                .sort_index()
                .items()
            }
    checks = {
        "global_rank_order_agrees": bool(global_order_agrees),
        "team_rank_order_agrees": bool(team_order_agrees),
        "shootout_outcomes_used": bool(
            ranked.get(
                "shootout_outcomes_used_v3",
                pd.Series(True, index=ranked.index),
            ).astype(bool).any()
        ),
        "player_identity_used": bool(
            ranked.get(
                "player_identity_used_for_score_v3",
                pd.Series(True, index=ranked.index),
            ).astype(bool).any()
        ),
        "team_identity_used": bool(
            ranked.get(
                "team_identity_used_for_score_v3",
                pd.Series(True, index=ranked.index),
            ).astype(bool).any()
        ),
        "position_normalization_used": bool(
            ranked.get(
                "position_normalization_used_for_impact_v3",
                pd.Series(True, index=ranked.index),
            ).astype(bool).any()
        ),
        "uncertainty_used_as_score_penalty": bool(
            ranked.get(
                "uncertainty_used_as_score_penalty_v3",
                pd.Series(True, index=ranked.index),
            ).astype(bool).any()
        ),
    }
    return {
        "model_version": V3_MODEL_VERSION,
        "passed": bool(
            checks["global_rank_order_agrees"]
            and checks["team_rank_order_agrees"]
            and not checks["shootout_outcomes_used"]
            and not checks["player_identity_used"]
            and not checks["team_identity_used"]
            and not checks["position_normalization_used"]
            and not checks["uncertainty_used_as_score_penalty"]
        ),
        "checks": checks,
        "score_minutes_spearman": _spearman(
            ranked["tournament_impact_v3"],
            ranked["minutes"],
        ),
        "score_goals_spearman": (
            _spearman(
                ranked["tournament_impact_v3"],
                ranked[goals_column],
            )
            if goals_column is not None
            else float("nan")
        ),
        "position_composition": composition,
    }


def _fit_linear_calibration(
    score: np.ndarray,
    target: np.ndarray,
) -> tuple[float, float]:
    variance = float(np.var(score))
    if variance <= 1e-15:
        return 0.0, float(np.mean(target))
    slope = float(
        np.mean((score - score.mean()) * (target - target.mean()))
        / variance
    )
    intercept = float(target.mean() - slope * score.mean())
    return slope, intercept


def _cluster_bootstrap_rmse_delta(
    challenger_residual: np.ndarray,
    champion_residual: np.ndarray,
    groups: np.ndarray,
    *,
    replicates: int,
    confidence: float,
    random_seed: int,
) -> tuple[float, float]:
    unique_groups = pd.unique(groups)
    group_indices = {
        group: np.flatnonzero(groups == group)
        for group in unique_groups
    }
    rng = np.random.default_rng(random_seed)
    deltas = np.empty(replicates, dtype=float)
    for replicate in range(replicates):
        sampled = rng.choice(
            unique_groups,
            size=len(unique_groups),
            replace=True,
        )
        indices = np.concatenate([group_indices[group] for group in sampled])
        challenger_rmse = float(
            np.sqrt(np.mean(np.square(challenger_residual[indices])))
        )
        champion_rmse = float(
            np.sqrt(np.mean(np.square(champion_residual[indices])))
        )
        deltas[replicate] = challenger_rmse - champion_rmse
    alpha = (1.0 - confidence) / 2.0
    return (
        float(np.quantile(deltas, alpha)),
        float(np.quantile(deltas, 1.0 - alpha)),
    )


def _leave_one_group_rank_stability(
    frame: pd.DataFrame,
    score_column: str,
    *,
    player_column: str,
    group_column: str,
) -> float:
    full = frame.groupby(player_column, sort=False)[score_column].sum()
    correlations: list[float] = []
    for group in pd.unique(frame[group_column]):
        reduced = frame.loc[~frame[group_column].eq(group)]
        reduced_scores = reduced.groupby(
            player_column,
            sort=False,
        )[score_column].sum()
        common = full.index.intersection(reduced_scores.index)
        if len(common) < 3:
            continue
        correlation = _spearman(full.loc[common], reduced_scores.loc[common])
        if np.isfinite(correlation):
            correlations.append(correlation)
    return float(np.mean(correlations)) if correlations else float("nan")


def evaluate_attack_ablations(
    frame: pd.DataFrame,
    *,
    target_column: str,
    group_column: str = "match_id",
    player_column: str = "player_id",
    champion_candidate: str = "process_only",
    config: TournamentRankingV3Config | None = None,
) -> dict[str, Any]:
    """Evaluate attack candidates with match-disjoint OOF calibration.

    Promotion is generalized: a candidate must be RMSE-noninferior by a
    cluster-bootstrap interval and correlation-noninferior.  Among passing
    candidates, the lowest OOF RMSE wins; identity fields never participate.
    """

    settings = config or TournamentRankingV3Config()
    required = {target_column, group_column, player_column, "minutes"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(
            f"attack-ablation input is missing: {sorted(missing)}"
        )
    scores = build_attack_ablation_scores(frame, config=settings)
    candidate_columns = [
        column
        for column in scores.columns
        if column in CORE_ATTACK_ABLATIONS
        or column.startswith(
            (
                "outcomes_only_no_",
                "process_only_without_",
                "process_plus_shrunk_residual_no_",
                "process_plus_shrunk_residual_without_",
                "process_plus_full_outcomes_no_",
                "process_plus_full_outcomes_without_",
            )
        )
    ]
    if champion_candidate not in candidate_columns:
        raise ValueError(
            f"champion candidate {champion_candidate!r} is unavailable"
        )
    target = _numeric(frame, target_column).to_numpy(dtype=float)
    groups = frame[group_column].to_numpy()
    unique_groups = pd.unique(groups)
    n_splits = min(settings.attack_cv_splits, len(unique_groups))
    if n_splits < 2:
        raise ValueError("attack ablation requires at least two matches")
    splitter = GroupKFold(n_splits=n_splits)

    prediction_by_candidate: dict[str, np.ndarray] = {}
    residual_by_candidate: dict[str, np.ndarray] = {}
    metrics: dict[str, dict[str, Any]] = {}
    for candidate in candidate_columns:
        values = scores[candidate].to_numpy(dtype=float)
        predictions = np.empty(len(frame), dtype=float)
        fold_slopes: list[float] = []
        for train_indices, test_indices in splitter.split(
            values,
            target,
            groups,
        ):
            slope, intercept = _fit_linear_calibration(
                values[train_indices],
                target[train_indices],
            )
            predictions[test_indices] = (
                slope * values[test_indices] + intercept
            )
            fold_slopes.append(slope)
        residual = predictions - target
        prediction_by_candidate[candidate] = predictions
        residual_by_candidate[candidate] = residual

        aggregate = pd.DataFrame(
            {
                player_column: frame[player_column].to_numpy(),
                "score": values,
                "goals": _numeric(
                    frame,
                    "regulation_extra_time_goals",
                ).to_numpy(dtype=float),
                "minutes": _numeric(
                    frame,
                    "minutes",
                ).to_numpy(dtype=float),
            }
        ).groupby(player_column, sort=False).sum()
        metrics[candidate] = {
            "oof_rmse": float(np.sqrt(np.mean(np.square(residual)))),
            "oof_mae": float(np.mean(np.abs(residual))),
            "oof_spearman": _spearman(
                pd.Series(predictions),
                pd.Series(target),
            ),
            "oof_pearson": (
                float(np.corrcoef(predictions, target)[0, 1])
                if np.std(predictions) > 0.0 and np.std(target) > 0.0
                else float("nan")
            ),
            "fold_calibration_slope_mean": float(np.mean(fold_slopes)),
            "score_goals_spearman": _spearman(
                aggregate["score"],
                aggregate["goals"],
            ),
            "score_minutes_spearman": _spearman(
                aggregate["score"],
                aggregate["minutes"],
            ),
            "leave_one_match_out_rank_spearman": (
                _leave_one_group_rank_stability(
                    pd.concat(
                        [
                            frame[
                                [player_column, group_column]
                            ].reset_index(drop=True),
                            scores[[candidate]].reset_index(drop=True),
                        ],
                        axis=1,
                    ),
                    candidate,
                    player_column=player_column,
                    group_column=group_column,
                )
            ),
        }

    champion = metrics[champion_candidate]
    champion_residual = residual_by_candidate[champion_candidate]
    for index, candidate in enumerate(candidate_columns):
        lower, upper = _cluster_bootstrap_rmse_delta(
            residual_by_candidate[candidate],
            champion_residual,
            groups,
            replicates=settings.attack_bootstrap_replicates,
            confidence=settings.bootstrap_confidence,
            random_seed=settings.random_seed + index,
        )
        noninferiority_limit = (
            champion["oof_rmse"] * settings.attack_noninferiority_margin
        )
        rmse_noninferior = upper <= noninferiority_limit + 1e-12
        candidate_correlation = metrics[candidate]["oof_spearman"]
        champion_correlation = champion["oof_spearman"]
        correlation_noninferior = (
            (
                not np.isfinite(champion_correlation)
                and not np.isfinite(candidate_correlation)
            )
            or (
                np.isfinite(candidate_correlation)
                and candidate_correlation
                >= champion_correlation
                - settings.attack_correlation_margin
            )
        )
        metrics[candidate].update(
            {
                "rmse_delta_vs_champion": float(
                    metrics[candidate]["oof_rmse"]
                    - champion["oof_rmse"]
                ),
                "rmse_delta_ci_low": lower,
                "rmse_delta_ci_high": upper,
                "rmse_noninferior": bool(rmse_noninferior),
                "correlation_noninferior": bool(
                    correlation_noninferior
                ),
                "gate_passed": bool(
                    rmse_noninferior and correlation_noninferior
                ),
            }
        )

    passing = [
        candidate
        for candidate in candidate_columns
        if metrics[candidate]["gate_passed"]
    ]
    selected = min(
        passing,
        key=lambda candidate: (
            metrics[candidate]["oof_rmse"],
            -np.nan_to_num(
                metrics[candidate]["oof_spearman"],
                nan=-np.inf,
            ),
            candidate,
        ),
    )
    decision = (
        "retain_champion"
        if selected == champion_candidate
        else "promote_challenger"
    )
    return {
        "selected_candidate": selected,
        "champion_candidate": champion_candidate,
        "gate_decision": decision,
        "match_disjoint": True,
        "n_splits": int(n_splits),
        "n_matches": int(len(unique_groups)),
        "n_rows": int(len(frame)),
        "bootstrap_confidence": settings.bootstrap_confidence,
        "noninferiority_margin_fraction": (
            settings.attack_noninferiority_margin
        ),
        "correlation_margin": settings.attack_correlation_margin,
        "identity_features_used": False,
        "shootout_outcomes_used": False,
        "metrics": metrics,
    }
