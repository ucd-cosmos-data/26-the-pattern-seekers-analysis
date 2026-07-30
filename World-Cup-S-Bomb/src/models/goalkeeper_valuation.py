"""Separate goalkeeper valuation for the StatsBomb Open Data sample."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


GOALKEEPER_METRICS: dict[str, bool] = {
    "goals_prevented_proxy_p90": True,
    "save_rate": True,
    "cross_stopping_rate": True,
    "sweeper_actions_p90": True,
    "distribution_under_pressure": True,
    "penalty_save_rate_shrunk": True,
}

# Shot-stopping is the core of the role: an unweighted mean previously gave
# ball-playing and claiming metrics two-thirds of the composite, which let
# low-shot-volume distributors outrank high-volume shot-stoppers.
GOALKEEPER_METRIC_WEIGHTS: dict[str, float] = {
    "goals_prevented_proxy_p90": 0.30,
    "save_rate": 0.20,
    # The penalty channel includes shootout penalties, which decide
    # tournaments; 0.20 lets shootout performances move the ranking
    # while the per-keeper shrunk save rate keeps tiny samples honest.
    "penalty_save_rate_shrunk": 0.20,
    "distribution_under_pressure": 0.12,
    "cross_stopping_rate": 0.09,
    "sweeper_actions_p90": 0.09,
}

# A save percentage on a handful of shots is mostly noise: shot-stopping
# percentiles are shrunk toward the cohort-neutral 0.5 with weight
# SOT / (SOT + SHOT_EVIDENCE_SHRINKAGE).
SHOT_STOPPING_METRICS = ("goals_prevented_proxy_p90", "save_rate")
SHOT_EVIDENCE_SHRINKAGE = 15.0


def _percentile(series: pd.Series, higher: bool) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    percentile = numeric.rank(method="average", pct=True)
    return percentile if higher else 1.0 - percentile


def calculate_goalkeeper_ratings(
    goalkeeper_features: pd.DataFrame,
    *,
    reliability_minutes: float = 600.0,
) -> pd.DataFrame:
    """Calculate a separate, reliability-shrunk goalkeeper leaderboard."""

    if set(GOALKEEPER_METRIC_WEIGHTS) != set(GOALKEEPER_METRICS):
        raise ValueError("Goalkeeper metric weights are out of sync")
    if abs(sum(GOALKEEPER_METRIC_WEIGHTS.values()) - 1.0) > 1e-12:
        raise ValueError("Goalkeeper metric weights must sum to one")
    missing = set(GOALKEEPER_METRICS).difference(
        goalkeeper_features.columns
    )
    if missing:
        raise ValueError(f"Goalkeeper metrics missing: {sorted(missing)}")
    output = goalkeeper_features.copy()
    components = pd.DataFrame(index=output.index)
    availability = pd.DataFrame(index=output.index)
    if "shot_on_target_faced" not in output:
        raise ValueError(
            "Goalkeeper features must include shot_on_target_faced for "
            "shot-evidence shrinkage"
        )
    shots_faced = pd.to_numeric(
        output["shot_on_target_faced"],
        errors="coerce",
    )
    shot_evidence = (
        shots_faced / (shots_faced + SHOT_EVIDENCE_SHRINKAGE)
    ).fillna(0.0)
    for metric, higher in GOALKEEPER_METRICS.items():
        percentile = _percentile(output[metric], higher)
        if metric in SHOT_STOPPING_METRICS:
            percentile = 0.5 + shot_evidence * (percentile - 0.5)
        components[metric] = percentile
        availability[metric] = output[metric].notna()
    evidence = availability.sum(axis=1)
    metric_weights = pd.DataFrame(
        {
            metric: np.where(
                availability[metric],
                GOALKEEPER_METRIC_WEIGHTS[metric],
                0.0,
            )
            for metric in GOALKEEPER_METRICS
        },
        index=output.index,
    )
    weight_totals = metric_weights.sum(axis=1)
    if (weight_totals <= 0).any():
        raise ValueError("A goalkeeper has no available rating metrics")
    score = (
        components.fillna(0.0) * metric_weights
    ).sum(axis=1) / weight_totals
    cohort_prior = float(score.mean())
    feature_reliability = evidence / len(GOALKEEPER_METRICS)
    minutes = pd.to_numeric(
        output["minutes"],
        errors="coerce",
    ).clip(lower=0.0)
    minutes_reliability = minutes / (minutes + reliability_minutes)
    reliability = feature_reliability * minutes_reliability
    output["goalkeeper_raw_rating"] = score
    output["goalkeeper_feature_coverage"] = feature_reliability
    output["goalkeeper_rating_reliability"] = reliability
    output["final_player_rating"] = (
        reliability * score + (1.0 - reliability) * cohort_prior
    ).clip(0.0, 1.0)
    output["goalkeeper_rank"] = output["final_player_rating"].rank(
        method="min",
        ascending=False,
    ).astype(int)
    output["position_rank"] = output["goalkeeper_rank"]
    output["global_rank_eligible"] = False
    output["global_rank"] = pd.Series(
        pd.NA,
        index=output.index,
        dtype="Int64",
    )
    return output


def goalkeeper_model_summary(
    audit: dict[str, Any],
    ratings: pd.DataFrame,
) -> dict[str, Any]:
    """Return report-safe diagnostics for the goalkeeper branch."""

    return {
        **audit,
        "eligible_goalkeepers": int(len(ratings)),
        "rating_feature_coverage_mean": float(
            ratings["goalkeeper_feature_coverage"].mean()
        ),
        "rating_reliability_mean": float(
            ratings["goalkeeper_rating_reliability"].mean()
        ),
    }
