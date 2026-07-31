#!/usr/bin/env python3
"""Create a clean, position-normalized World Cup tournament leaderboard.

The script is intentionally an isolated export layer. It does not replace the
validated VAEP/xT, role-aware, outfield-v2, or goalkeeper-v2 models that
produce its input signal.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


OUTPUT_COLUMNS = [
    "Global Rank",
    "Team Rank",
    "Player",
    "Team",
    "Position Group",
    "Tournament Performance Score",
]
DEFENSIVE_GROUPS = frozenset({"CB", "FB", "DM"})
DIRECT_DEFENSIVE_METRICS = (
    "interceptions_p90",
    "blocks_p90",
    "clearances_p90",
    "pressures_p90",
    "post_pressure_recoveries_p90",
    "aerial_wins_p90",
    "duel_win_rate",
    "defensive_positioning_score",
)
EXPOSURE_SATURATION_SHARE = 0.75
DEFENSIVE_EVIDENCE_LIFT = 1.00
PUBLICATION_EXPOSURE_SHARE = 0.75
ATTACKING_REALIZATION_PENALTY = 0.55
POSITION_ALIASES = {
    "GK": "GK",
    "CB": "CB",
    "FB": "FB",
    "DM": "DM",
    "CM": "CM",
    "AM": "AM",
    "FW": "FW",
    "Goalkeeper": "GK",
    "Center Back": "CB",
    "Centre Back": "CB",
    "Fullback/Wingback": "FB",
    "Defensive Midfield": "DM",
    "Central/Wide Midfield": "CM",
    "Attacking Midfield/Wing": "AM",
    "Forward": "FW",
}


def _first_present(
    frame: pd.DataFrame,
    names: Iterable[str],
) -> pd.Series:
    """Return the first available column, coalescing later aliases by row."""

    output = pd.Series(np.nan, index=frame.index, dtype=object)
    found = False
    for name in names:
        if name not in frame:
            continue
        found = True
        output = output.where(output.notna(), frame[name])
    if not found:
        raise ValueError(f"None of the required aliases are present: {list(names)}")
    return output


def _position_groups(frame: pd.DataFrame) -> pd.Series:
    """Return canonical GK/CB/FB/DM/CM/AM/FW position labels."""

    if "position_group_360" in frame:
        groups = frame["position_group_360"].map(POSITION_ALIASES)
    else:
        groups = _first_present(
            frame,
            ("Position Group", "position_group"),
        ).map(POSITION_ALIASES)
    groups = groups.fillna(
        _first_present(
            frame,
            ("Position Group", "position_group"),
        ).map(POSITION_ALIASES)
    )
    if groups.isna().any():
        unknown = sorted(
            _first_present(
                frame.loc[groups.isna()],
                ("Position Group", "position_group"),
            )
            .astype(str)
            .unique()
        )
        raise ValueError(f"Unable to normalize position groups: {unknown}")
    return groups.astype(str)


def _generalized_validation(
    output: pd.DataFrame,
    minutes: pd.Series,
    source: pd.DataFrame,
) -> dict[str, float | int | bool]:
    """Summarize cohort-level checks without player-specific conditions."""

    aligned = output.copy()
    aligned["_minutes"] = minutes.reindex(output.index).to_numpy()
    squad_size = aligned.groupby("Team")["Player"].transform("size")
    team_percentile = (
        squad_size - aligned["Team Rank"] + 1
    ) / squad_size.clip(lower=1)
    heavy_defender = (
        aligned["Position Group"].isin(DEFENSIVE_GROUPS)
        & aligned["_minutes"].ge(300.0)
    )
    defender_percentiles = team_percentile.loc[heavy_defender]
    in_target_defender_band = defender_percentiles.between(
        0.60,
        0.90,
        inclusive="both",
    )
    variance_imbalance = _variance_imbalance(
        aligned["Tournament Performance Score"],
        aligned["Position Group"],
    )
    validation: dict[str, float | int | bool] = {
        "heavy_defenders_evaluated": int(heavy_defender.sum()),
        "heavy_defender_team_percentile_median": (
            float(defender_percentiles.median())
            if not defender_percentiles.empty
            else math.nan
        ),
        "heavy_defender_share_at_or_above_60th_team_percentile": (
            float(defender_percentiles.ge(0.60).mean())
            if not defender_percentiles.empty
            else math.nan
        ),
        "heavy_defender_share_in_60th_to_90th_team_percentile": (
            float(in_target_defender_band.mean())
            if not defender_percentiles.empty
            else math.nan
        ),
        "final_position_variance_imbalance": variance_imbalance,
        "global_leader_percentile": float(
            (
                len(aligned)
                - aligned["Global Rank"].min()
                + 1
            )
            / len(aligned)
        ),
        "scores_bounded_zero_to_one": bool(
            aligned["Tournament Performance Score"]
            .dropna()
            .between(0.0, 1.0)
            .all()
        ),
    }
    goal_column = next(
        (name for name in ("goals", "Goals") if name in source),
        None,
    )
    assist_column = next(
        (
            name
            for name in ("xa_sum", "assists", "Assists")
            if name in source
        ),
        None,
    )
    if goal_column is not None or assist_column is not None:
        goals = (
            pd.to_numeric(source[goal_column], errors="coerce").fillna(0.0)
            if goal_column is not None
            else pd.Series(0.0, index=source.index)
        ).reindex(output.index)
        assists = (
            pd.to_numeric(source[assist_column], errors="coerce").fillna(0.0)
            if assist_column is not None
            else pd.Series(0.0, index=source.index)
        ).reindex(output.index)
        productive_attacking_starter = (
            aligned["Position Group"].isin({"FW", "AM", "CM"})
            &
            aligned["_minutes"].ge(90.0)
            & goals.add(assists).gt(0.0).to_numpy()
        )
        low_minute_nonproducer = (
            aligned["Position Group"].eq("FW")
            & aligned["_minutes"].lt(90.0)
            & goals.add(assists).eq(0.0).to_numpy()
        )
        pairwise_checks: list[bool] = []
        teams_evaluated = 0
        for _, squad in aligned.groupby("Team"):
            productive_ranks = squad.loc[
                productive_attacking_starter.reindex(squad.index),
                "Team Rank",
            ]
            low_minute_ranks = squad.loc[
                low_minute_nonproducer.reindex(squad.index),
                "Team Rank",
            ]
            if not productive_ranks.empty and not low_minute_ranks.empty:
                teams_evaluated += 1
                pairwise_checks.extend(
                    bool(productive_rank < low_minute_rank)
                    for productive_rank in productive_ranks
                    for low_minute_rank in low_minute_ranks
                )
        validation["productive_vs_low_minute_teams_evaluated"] = (
            teams_evaluated
        )
        validation["productive_attacker_pairwise_ordering_success_rate"] = (
            float(np.mean(pairwise_checks)) if pairwise_checks else math.nan
        )
    return validation


def _raw_performance(frame: pd.DataFrame, groups: pd.Series) -> pd.Series:
    """Resolve the incumbent performance signal without using player names."""

    raw = pd.to_numeric(
        _first_present(
            frame,
            (
                "raw_performance",
                "final_player_rating_v2",
                "final_player_rating",
                "player_evaluation_score",
                "Tournament Performance Score",
            ),
        ),
        errors="coerce",
    )
    if "gk_rating_v2" in frame:
        goalkeeper = groups.eq("GK")
        raw.loc[goalkeeper] = pd.to_numeric(
            frame.loc[goalkeeper, "gk_rating_v2"],
            errors="coerce",
        ).combine_first(raw.loc[goalkeeper])
    return raw


def _rank_correlation(left: pd.Series, right: pd.Series) -> float:
    """Calculate Spearman correlation using only Pandas rank operations."""

    valid = left.notna() & right.notna()
    if valid.sum() < 3:
        return 1.0
    value = left.loc[valid].rank().corr(right.loc[valid].rank())
    return 0.0 if pd.isna(value) else float(value)


def _median_dispersion(values: pd.Series, groups: pd.Series) -> float:
    """Measure structural separation between position-group medians."""

    medians = values.groupby(groups).median().dropna()
    return float(medians.std(ddof=0)) if len(medians) > 1 else 0.0


def _variance_imbalance(values: pd.Series, groups: pd.Series) -> float:
    """Measure how uneven within-position score variances are."""

    variances = values.groupby(groups).var(ddof=0).dropna()
    positive = variances.loc[variances.gt(1e-12)]
    if positive.empty:
        return math.inf
    return float(positive.max() / positive.min())


def _accept_step(
    baseline: pd.Series,
    challenger: pd.Series,
    groups: pd.Series,
    *,
    minimum_spearman: float,
    require_median_improvement: bool,
    maximum_variance_imbalance: float = 4.0,
) -> tuple[bool, dict[str, float | bool]]:
    """Gate one transformation against rank and positional integrity."""

    correlation = _rank_correlation(baseline, challenger)
    before_medians = _median_dispersion(baseline, groups)
    after_medians = _median_dispersion(challenger, groups)
    variance_imbalance = _variance_imbalance(challenger, groups)
    median_ok = (
        not require_median_improvement
        or after_medians <= before_medians + 1e-12
    )
    accepted = bool(
        correlation >= minimum_spearman
        and median_ok
        and variance_imbalance <= maximum_variance_imbalance
    )
    return accepted, {
        "accepted": accepted,
        "spearman_with_incumbent": correlation,
        "position_median_dispersion_before": before_medians,
        "position_median_dispersion_after": after_medians,
        "position_variance_imbalance_after": variance_imbalance,
    }


def _defensive_floor_candidate(
    score: pd.Series,
    frame: pd.DataFrame,
    groups: pd.Series,
) -> tuple[pd.Series, dict[str, float | int | bool]]:
    """Convert a bottom-decile defensive-VAEP floor into a bounded correction."""

    aliases = ("vaep_def_p90", "defensive_vaep", "defensive_vaep_p90")
    available = next((name for name in aliases if name in frame), None)
    if available is None:
        return score.copy(), {
            "available": False,
            "adjusted_players": 0,
        }
    defensive_vaep = pd.to_numeric(frame[available], errors="coerce")
    floor = float(defensive_vaep.quantile(0.10))
    eligible = (
        groups.isin(DEFENSIVE_GROUPS)
        & defensive_vaep.notna()
        & defensive_vaep.lt(floor)
    )
    floored = defensive_vaep.where(~eligible, floor)
    original_percentile = defensive_vaep.rank(method="average", pct=True)
    floored_percentile = floored.rank(method="average", pct=True)
    raw_iqr = float(score.quantile(0.75) - score.quantile(0.25))
    raw_scale = raw_iqr if raw_iqr > 1e-12 else float(score.std(ddof=0))
    if not np.isfinite(raw_scale) or raw_scale <= 1e-12:
        raw_scale = 1.0
    correction = (
        (floored_percentile - original_percentile).fillna(0.0)
        * raw_scale
    )
    return score + correction.where(eligible, 0.0), {
        "available": True,
        "source_column": available,
        "floor_percentile": 0.10,
        "floor_value": floor,
        "adjusted_players": int(eligible.sum()),
    }


def _exposure_saturation_candidate(
    score: pd.Series,
    reliability: pd.Series,
) -> tuple[pd.Series, dict[str, float]]:
    """Apply a bounded exposure safeguard against volatile cameo rankings.

    The factor remains continuous and saturates toward one. It does not award
    actions or use a hard minutes threshold; it only prevents a position-
    normalized short cameo from being published as equivalent to a sustained
    tournament contribution.
    """

    factor = (
        (1.0 - EXPOSURE_SATURATION_SHARE)
        + EXPOSURE_SATURATION_SHARE * reliability
    )
    return score * factor, {
        "exposure_share": EXPOSURE_SATURATION_SHARE,
        "minimum_factor": float(factor.min()),
        "maximum_factor": float(factor.max()),
        "mean_factor": float(factor.mean()),
    }


def _publication_exposure_candidate(
    score: pd.Series,
    reliability: pd.Series,
) -> tuple[pd.Series, dict[str, float]]:
    """Retain a score-tapered minutes safeguard after normalization.

    The uncertainty discount fades continuously for genuinely extreme scores,
    so a small minutes difference cannot reorder the tournament's elite tail.
    """

    uncertainty = (
        (1.0 - reliability)
        * np.sqrt((1.0 - score.clip(0.0, 1.0)).clip(lower=0.0))
    )
    factor = 1.0 - PUBLICATION_EXPOSURE_SHARE * uncertainty
    return score * factor, {
        "exposure_share": PUBLICATION_EXPOSURE_SHARE,
        "minimum_factor": float(factor.min()),
        "maximum_factor": float(factor.max()),
        "mean_factor": float(factor.mean()),
    }


def _attacking_realization_candidate(
    score: pd.Series,
    frame: pd.DataFrame,
    groups: pd.Series,
    reliability: pd.Series,
) -> tuple[pd.Series, dict[str, Any]]:
    """Discount poorly realized attacking volume using observed goals and xG.

    The correction is limited to attacking roles below their positional
    median for goals-minus-xG per 90. It is continuous, evidence-weighted,
    minutes-reliability weighted, and never references player or team identity.
    """

    required = {"goals", "xg_sum"}
    if not required.issubset(frame.columns):
        return score.copy(), {
            "available": False,
            "adjusted_players": 0,
            "missing_columns": sorted(required.difference(frame.columns)),
        }
    attacking = groups.isin({"AM", "FW"})
    goals = pd.to_numeric(frame["goals"], errors="coerce").fillna(0.0)
    expected_goals = pd.to_numeric(
        frame["xg_sum"],
        errors="coerce",
    ).fillna(0.0).clip(lower=0.0)
    minutes = pd.to_numeric(
        _first_present(frame, ("minutes_played", "minutes")),
        errors="coerce",
    ).clip(lower=1.0)
    realization_per_90 = 90.0 * (goals - expected_goals) / minutes
    percentile = realization_per_90.loc[attacking].groupby(
        groups.loc[attacking]
    ).rank(method="average", pct=True)
    underperformance = (
        (0.50 - percentile) / 0.50
    ).clip(lower=0.0, upper=1.0)
    evidence = expected_goals.loc[attacking] / (
        expected_goals.loc[attacking] + 0.75
    )
    penalty = pd.Series(0.0, index=score.index, dtype=float)
    penalty.loc[attacking] = (
        ATTACKING_REALIZATION_PENALTY
        * reliability.loc[attacking].clip(0.0, 1.0)
        * evidence
        * underperformance
    )
    candidate = score * (1.0 - penalty).clip(lower=0.0, upper=1.0)
    return candidate, {
        "available": True,
        "penalty_fraction": ATTACKING_REALIZATION_PENALTY,
        "adjusted_players": int(penalty.gt(1e-12).sum()),
        "maximum_applied_penalty": float(penalty.max()),
        "mean_positive_penalty": (
            float(penalty.loc[penalty.gt(1e-12)].mean())
            if penalty.gt(1e-12).any()
            else 0.0
        ),
        "uses_player_identity": False,
        "uses_team_identity": False,
    }


def _direct_defensive_evidence_candidate(
    normalized: pd.Series,
    frame: pd.DataFrame,
    groups: pd.Series,
    reliability: pd.Series,
) -> tuple[pd.Series, dict[str, Any]]:
    """Lift context-suppressed defenders using direct event-rate evidence.

    The incumbent defensive VAEP channel is a game-state value accumulated on
    defensive events. It can therefore be negative when a player repeatedly
    acts in dangerous states. This safeguard uses direct, position-relative
    event rates and only closes a positive evidence gap. It never lowers a
    player and is attenuated continuously by minutes reliability.
    """

    available = [
        metric
        for metric in DIRECT_DEFENSIVE_METRICS
        if metric in frame
        and pd.to_numeric(frame[metric], errors="coerce").notna().any()
    ]
    if len(available) < 4:
        return normalized.copy(), {
            "available": False,
            "available_metrics": available,
            "adjusted_players": 0,
        }
    percentiles = []
    for metric in available:
        values = pd.to_numeric(frame[metric], errors="coerce")
        percentiles.append(
            values.groupby(groups).rank(method="average", pct=True)
        )
    evidence = pd.concat(percentiles, axis=1).mean(axis=1, skipna=True)
    evidence_mean = evidence.groupby(groups).transform("mean")
    evidence_std = (
        evidence.groupby(groups).transform("std").replace(0.0, np.nan)
    )
    evidence_z = ((evidence - evidence_mean) / evidence_std).fillna(0.0)
    defensive = groups.isin(DEFENSIVE_GROUPS)
    evidence_gap = (evidence_z - normalized).clip(lower=0.0)
    lift = (
        DEFENSIVE_EVIDENCE_LIFT
        * evidence_gap
        * reliability.clip(0.0, 1.0)
    ).where(defensive, 0.0)
    candidate = normalized + lift
    return candidate, {
        "available": True,
        "available_metrics": available,
        "lift_fraction": DEFENSIVE_EVIDENCE_LIFT,
        "adjusted_players": int(lift.gt(1e-12).sum()),
        "mean_positive_lift": (
            float(lift.loc[lift.gt(1e-12)].mean())
            if lift.gt(1e-12).any()
            else 0.0
        ),
        "recentered_within_position": False,
        "uses_player_identity": False,
        "uses_team_identity": False,
    }


def _normal_cdf(values: pd.Series) -> pd.Series:
    """Evaluate the standard normal CDF without a SciPy dependency."""

    finite = values.fillna(0.0).to_numpy(dtype=float)
    transformed = 0.5 * (
        1.0
        + np.fromiter(
            (math.erf(value / math.sqrt(2.0)) for value in finite),
            dtype=float,
            count=len(finite),
        )
    )
    return pd.Series(transformed, index=values.index, dtype=float)


def _upper_tail_scale(z_score: pd.Series) -> pd.Series:
    """Map positional Z-scores to 0-1 and expand genuine Z > 2 outliers."""

    score = _normal_cdf(z_score)
    tail = z_score.gt(2.0)
    expansion = (1.0 - score) * (
        1.0 - np.exp(-(z_score - 2.0).clip(lower=0.0))
    )
    return (score + expansion.where(tail, 0.0)).clip(0.0, 1.0)


def _main_goalkeeper_mask(
    frame: pd.DataFrame,
    groups: pd.Series,
) -> pd.Series:
    """Identify the one ranked goalkeeper per team without using names."""

    goalkeeper = groups.eq("GK")
    if "is_main_goalkeeper" in frame:
        main = frame["is_main_goalkeeper"].fillna(False).astype(bool)
        return goalkeeper & main
    if "gk_rank_v2" in frame:
        return goalkeeper & pd.to_numeric(
            frame["gk_rank_v2"],
            errors="coerce",
        ).notna()
    return goalkeeper


def _goalkeeper_quantile_bridge(
    goalkeeper_rating: pd.Series,
    outfield_score: pd.Series,
) -> tuple[pd.Series, dict[str, float | int | bool]]:
    """Map goalkeeper order statistics onto the outfield score distribution.

    A goalkeeper model is trained and normalized on only 32 team-main
    goalkeepers. Re-standardizing that small cohort exaggerates its maximum.
    The Blom plotting position maps each goalkeeper's within-cohort standing
    to the equivalent outfield tournament percentile while preserving the
    goalkeeper ordering and avoiding an automatic global podium place. Blom's
    finite-sample adjustment is deliberately more conservative than assigning
    the cohort maximum to the 100th percentile.
    """

    valid = goalkeeper_rating.dropna()
    if valid.empty:
        return goalkeeper_rating.copy(), {
            "accepted": True,
            "ranked_goalkeepers": 0,
            "method": "not_applicable",
        }
    if outfield_score.dropna().empty:
        raise ValueError("Goalkeeper calibration requires outfield scores")
    cohort_size = len(valid)
    descending_rank = valid.rank(method="average", ascending=False)
    ascending_rank = cohort_size - descending_rank + 1.0
    plotting_position = (
        ascending_rank - 0.375
    ) / (cohort_size + 0.25)
    tail_threshold = 0.90
    tail_center = 0.965
    tail_weight = (
        (plotting_position - tail_threshold)
        / (1.0 - tail_threshold)
    ).clip(lower=0.0, upper=1.0)
    plotting_position = (
        plotting_position
        + tail_weight * (tail_center - plotting_position)
    )
    reference = outfield_score.dropna().to_numpy(dtype=float)
    mapped = pd.Series(np.nan, index=goalkeeper_rating.index, dtype=float)
    mapped.loc[valid.index] = np.quantile(
        reference,
        plotting_position.to_numpy(dtype=float),
        method="linear",
    )
    ordering = _rank_correlation(valid, mapped.loc[valid.index])
    return mapped, {
        "accepted": bool(ordering >= 0.999),
        "ranked_goalkeepers": cohort_size,
        "method": "blom_empirical_quantile_bridge",
        "goalkeeper_order_spearman": ordering,
        "minimum_target_percentile": float(plotting_position.min()),
        "maximum_target_percentile": float(plotting_position.max()),
        "upper_tail_shrinkage_threshold": tail_threshold,
        "upper_tail_shrinkage_center": tail_center,
    }


def process_world_cup_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Transform player ratings into one clean tournament ranking.

    Args:
        df: Player-level tournament data. The function accepts the repository
            schema or the explicit sample schema used by this module.

    Returns:
        A DataFrame containing exactly the six requested publication columns.

    Raises:
        ValueError: If identifiers, minutes, positions, or incumbent ratings
            are unavailable.
    """

    if df.empty:
        raise ValueError("The player rating dataset is empty")
    working = df.copy()
    player = _first_present(working, ("Player", "player_name", "player"))
    team = _first_present(working, ("Team", "team"))
    groups = _position_groups(working)
    minutes = pd.to_numeric(
        _first_present(working, ("minutes_played", "minutes")),
        errors="coerce",
    )
    raw = _raw_performance(working, groups)
    main_goalkeeper = _main_goalkeeper_mask(working, groups)
    outfield = groups.ne("GK")
    ranked = outfield | main_goalkeeper
    valid = (
        player.notna()
        & team.notna()
        & groups.notna()
        & minutes.notna()
        & minutes.gt(0.0)
        & (raw.notna() | ~ranked)
    )
    if not valid.all():
        invalid = int((~valid).sum())
        raise ValueError(f"{invalid} player rows lack valid ranking inputs")

    diagnostics: dict[str, Any] = {
        "rows": int(len(working)),
        "teams": int(team.nunique()),
        "position_groups": sorted(groups.unique().tolist()),
        "steps": {},
    }

    model_raw = raw.loc[outfield]
    model_groups = groups.loc[outfield]
    model_minutes = minutes.loc[outfield]
    model_frame = working.loc[outfield]
    position_mean = model_raw.groupby(model_groups).transform("mean")
    reliability = model_minutes / (model_minutes + 90.0)
    shrinkage_candidate = (
        reliability * model_raw + (1.0 - reliability) * position_mean
    )
    shrinkage_accepted, shrinkage_gate = _accept_step(
        model_raw,
        shrinkage_candidate,
        model_groups,
        minimum_spearman=0.90,
        require_median_improvement=False,
        maximum_variance_imbalance=20.0,
    )
    diagnostics["steps"]["adaptive_90_minute_shrinkage"] = {
        **shrinkage_gate,
        "half_life_minutes": 90.0,
        "mean_reliability": float(reliability.mean()),
    }
    current = (
        shrinkage_candidate if shrinkage_accepted else model_raw.copy()
    )

    exposure_candidate, exposure_details = _exposure_saturation_candidate(
        current,
        reliability,
    )
    exposure_accepted, exposure_gate = _accept_step(
        current,
        exposure_candidate,
        model_groups,
        minimum_spearman=0.85,
        require_median_improvement=False,
        maximum_variance_imbalance=20.0,
    )
    diagnostics["steps"]["exposure_saturation"] = {
        **exposure_details,
        **exposure_gate,
    }
    if exposure_accepted:
        current = exposure_candidate

    floor_candidate, floor_details = _defensive_floor_candidate(
        current,
        model_frame,
        model_groups,
    )
    floor_accepted, floor_gate = _accept_step(
        current,
        floor_candidate,
        model_groups,
        minimum_spearman=0.98,
        require_median_improvement=False,
        maximum_variance_imbalance=20.0,
    )
    diagnostics["steps"]["defensive_vaep_floor"] = {
        **floor_details,
        **floor_gate,
    }
    if floor_accepted:
        current = floor_candidate

    group_mean = current.groupby(model_groups).transform("mean")
    group_std = (
        current.groupby(model_groups).transform("std").replace(0.0, np.nan)
    )
    z_candidate = ((current - group_mean) / group_std).fillna(0.0)
    z_accepted, z_gate = _accept_step(
        current,
        z_candidate,
        model_groups,
        minimum_spearman=0.65,
        require_median_improvement=False,
        maximum_variance_imbalance=1.05,
    )
    position_mean_dispersion = float(
        z_candidate.groupby(model_groups).mean().std(ddof=0)
    )
    z_accepted = bool(
        z_accepted and position_mean_dispersion <= 1e-10
    )
    z_gate["accepted"] = z_accepted
    z_gate["position_mean_dispersion_after"] = position_mean_dispersion
    diagnostics["steps"]["within_position_z_score"] = z_gate
    if z_accepted:
        normalized = z_candidate
    else:
        global_std = float(current.std(ddof=0))
        normalized = (
            (current - float(current.mean()))
            / (global_std if global_std > 1e-12 else 1.0)
        )

    defensive_candidate, defensive_details = (
        _direct_defensive_evidence_candidate(
            normalized,
            model_frame,
            model_groups,
            reliability,
        )
    )
    defensive_accepted, defensive_gate = _accept_step(
        normalized,
        defensive_candidate,
        model_groups,
        minimum_spearman=0.85,
        require_median_improvement=False,
        maximum_variance_imbalance=4.0,
    )
    defensive_median_dispersion_cap = 0.25
    defensive_accepted = bool(
        defensive_accepted
        and defensive_gate["position_median_dispersion_after"]
        <= defensive_median_dispersion_cap
    )
    defensive_gate["accepted"] = defensive_accepted
    defensive_gate["position_median_dispersion_cap"] = (
        defensive_median_dispersion_cap
    )
    diagnostics["steps"]["direct_defensive_evidence"] = {
        **defensive_details,
        **defensive_gate,
    }
    if defensive_accepted:
        normalized = defensive_candidate

    score_candidate = _upper_tail_scale(normalized)
    raw_leader = model_raw.idxmax()
    top_three = set(score_candidate.nlargest(min(3, len(score_candidate))).index)
    tail_accepted = bool(
        raw_leader in top_three
        and _rank_correlation(normalized, score_candidate) >= 0.999
    )
    diagnostics["steps"]["upper_tail_cdf"] = {
        "accepted": tail_accepted,
        "raw_leader_preserved_in_top_three": raw_leader in top_three,
        "spearman_with_normalized_score": _rank_correlation(
            normalized,
            score_candidate,
        ),
        "expanded_outliers": int(normalized.gt(2.0).sum()),
    }
    if tail_accepted:
        outfield_score = score_candidate
    else:
        outfield_score = _normal_cdf(normalized)

    publication_candidate, publication_details = (
        _publication_exposure_candidate(outfield_score, reliability)
    )
    publication_accepted, publication_gate = _accept_step(
        outfield_score,
        publication_candidate,
        model_groups,
        minimum_spearman=0.95,
        require_median_improvement=False,
        maximum_variance_imbalance=4.0,
    )
    diagnostics["steps"]["publication_exposure_safeguard"] = {
        **publication_details,
        **publication_gate,
    }
    if publication_accepted:
        outfield_score = publication_candidate

    realization_candidate, realization_details = (
        _attacking_realization_candidate(
            outfield_score,
            model_frame,
            model_groups,
            reliability,
        )
    )
    realization_accepted, realization_gate = _accept_step(
        outfield_score,
        realization_candidate,
        model_groups,
        minimum_spearman=0.90,
        require_median_improvement=False,
        maximum_variance_imbalance=4.0,
    )
    diagnostics["steps"]["attacking_realization"] = {
        **realization_details,
        **realization_gate,
    }
    if realization_accepted:
        outfield_score = realization_candidate

    goalkeeper_rating = raw.loc[main_goalkeeper]
    goalkeeper_score, goalkeeper_gate = _goalkeeper_quantile_bridge(
        goalkeeper_rating,
        outfield_score,
    )
    diagnostics["steps"]["goalkeeper_quantile_bridge"] = goalkeeper_gate
    if not goalkeeper_gate["accepted"]:
        raise RuntimeError(
            "Goalkeeper quantile bridge failed its order-preservation gate"
        )
    final_score = pd.Series(np.nan, index=working.index, dtype=float)
    final_score.loc[outfield] = outfield_score
    final_score.loc[main_goalkeeper] = goalkeeper_score

    output = pd.DataFrame(
        {
            "Player": player.astype(str),
            "Team": team.astype(str),
            "Position Group": groups,
            "Tournament Performance Score": final_score,
        },
        index=working.index,
    )
    output["Global Rank"] = (
        output["Tournament Performance Score"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    output["Tournament Performance Score"] = output[
        "Tournament Performance Score"
    ].round(6)
    output["Team Rank"] = (
        output.groupby("Team")["Tournament Performance Score"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    output = output[OUTPUT_COLUMNS].sort_values(
        ["Global Rank", "Player"],
        kind="mergesort",
    )
    diagnostics["final"] = {
        "score_min": float(output["Tournament Performance Score"].min()),
        "score_max": float(output["Tournament Performance Score"].max()),
        "raw_to_final_spearman": _rank_correlation(
            model_raw,
            outfield_score,
        ),
        "unranked_backup_goalkeepers": int((groups.eq("GK") & ~ranked).sum()),
        "top_player": str(output.iloc[0]["Player"]),
    }
    diagnostics["generalized_validation"] = _generalized_validation(
        output,
        minutes,
        working,
    )
    output = output.reset_index(drop=True)
    output.attrs["validation"] = diagnostics
    return output


def attach_unified_tournament_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Attach publication scores and ranks to a feature-rich player table."""

    output = process_world_cup_ratings(df)
    keys = output[["Player", "Team"]]
    if keys.duplicated().any():
        duplicates = keys.loc[keys.duplicated(keep=False)].drop_duplicates()
        raise ValueError(
            "Unified ratings require unique player/team pairs: "
            f"{duplicates.to_dict('records')}"
        )
    lookup = output[
        [
            "Player",
            "Team",
            "Global Rank",
            "Team Rank",
            "Tournament Performance Score",
        ]
    ].rename(
        columns={
            "Player": "_unified_player",
            "Team": "_unified_team",
        }
    )
    player = _first_present(df, ("Player", "player_name", "player")).astype(
        str
    )
    team = _first_present(df, ("Team", "team")).astype(str)
    enriched = df.drop(
        columns=[
            "Global Rank",
            "Team Rank",
            "Tournament Performance Score",
        ],
        errors="ignore",
    ).copy()
    enriched["_unified_player"] = player
    enriched["_unified_team"] = team
    enriched = enriched.merge(
        lookup,
        on=["_unified_player", "_unified_team"],
        how="left",
        validate="one_to_one",
        sort=False,
    ).drop(columns=["_unified_player", "_unified_team"])
    enriched.attrs["unified_validation"] = output.attrs["validation"]
    return enriched


def sample_world_cup_data() -> pd.DataFrame:
    """Return a multi-team example covering attacking and defensive roles."""

    rows = [
        ("Lionel Messi", "Argentina", "AM", 690, 0.98, 0.10),
        ("Alexis Mac Allister", "Argentina", "CM", 555, 0.76, 0.20),
        ("Enzo Fernández", "Argentina", "DM", 600, 0.74, -0.05),
        ("Nicolás Otamendi", "Argentina", "CB", 690, 0.68, -0.25),
        ("Cristian Romero", "Argentina", "CB", 550, 0.61, -0.90),
        ("Kylian Mbappé", "France", "FW", 690, 0.96, 0.05),
        ("Antoine Griezmann", "France", "AM", 650, 0.82, 0.15),
        ("Aurélien Tchouaméni", "France", "DM", 620, 0.72, -0.10),
        ("Dayot Upamecano", "France", "CB", 590, 0.66, -0.45),
        ("Michy Batshuayi", "Belgium", "FW", 150, 0.64, 0.00),
        ("Amadou Onana", "Belgium", "DM", 180, 0.62, -0.70),
        ("Low-minute Forward", "Belgium", "FW", 35, 0.40, 0.00),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "Player",
            "Team",
            "Position Group",
            "minutes_played",
            "raw_performance",
            "defensive_vaep",
        ],
    )


def parse_args() -> argparse.Namespace:
    """Parse CLI options for production and demonstration exports."""

    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root / "results/reports/ranking/player_rankings.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            project_root
            / "results/reports/ranking/unified_tournament_rankings.csv"
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use the embedded multi-team sample instead of --input.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the transformer, export the clean table, and print its gate audit."""

    args = parse_args()
    source = sample_world_cup_data() if args.demo else pd.read_csv(args.input)
    output = process_world_cup_ratings(source)
    diagnostics = output.attrs["validation"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "columns": output.columns.tolist(),
                "validation": diagnostics,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
