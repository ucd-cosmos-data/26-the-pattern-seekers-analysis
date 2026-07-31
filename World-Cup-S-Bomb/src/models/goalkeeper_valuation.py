"""Separate goalkeeper valuation for the StatsBomb Open Data sample."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


GOALKEEPER_METRICS: dict[str, tuple[bool, float]] = {
    "goals_prevented_proxy_p90": (True, 0.225),
    "save_rate": (True, 0.135),
    "cross_stopping_rate": (True, 0.135),
    "sweeper_actions_p90": (True, 0.135),
    "distribution_under_pressure": (True, 0.135),
    "penalty_save_rate_shrunk": (True, 0.135),
    "high_leverage_save_pct": (True, 0.100),
}


def _percentile(series: pd.Series, higher: bool) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    percentile = numeric.rank(method="average", pct=True)
    return percentile if higher else 1.0 - percentile


def calculate_goalkeeper_ratings(
    goalkeeper_features: pd.DataFrame,
    *,
    reliability_minutes: float = 450.0,
    minimum_minutes: float = 90.0,
) -> pd.DataFrame:
    """Calculate a separate, reliability-shrunk goalkeeper leaderboard."""

    missing = set(GOALKEEPER_METRICS).difference(
        goalkeeper_features.columns
    )
    if missing:
        raise ValueError(f"Goalkeeper metrics missing: {sorted(missing)}")
    output = goalkeeper_features.loc[
        pd.to_numeric(
            goalkeeper_features["minutes"],
            errors="coerce",
        ).ge(minimum_minutes)
    ].copy()
    if output.empty:
        raise ValueError("No goalkeepers satisfy the 90-minute eligibility rule")
    components = pd.DataFrame(index=output.index)
    availability = pd.DataFrame(index=output.index)
    for metric, (higher, _) in GOALKEEPER_METRICS.items():
        components[metric] = _percentile(output[metric], higher)
        availability[metric] = output[metric].notna()
    evidence = availability.sum(axis=1)
    weights = pd.Series(
        {
            metric: weight
            for metric, (_, weight) in GOALKEEPER_METRICS.items()
        }
    )
    weighted = components.mul(weights, axis=1)
    available_weight = availability.mul(weights, axis=1).sum(axis=1)
    score = weighted.sum(axis=1, skipna=True) / available_weight.replace(
        0.0,
        np.nan,
    )
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
    output["GKRankingStatus"] = np.select(
        [
            minutes.ge(270.0),
            minutes.ge(180.0),
        ],
        [
            "Ranked (270+ min)",
            "Ranked (180–269 min)",
        ],
        default="Coverage only (<180 min)",
    )
    output["primary_goalkeeper_rank"] = pd.Series(
        pd.NA,
        index=output.index,
        dtype="Int64",
    )
    primary = minutes.ge(270.0)
    output.loc[primary, "primary_goalkeeper_rank"] = (
        output.loc[primary, "final_player_rating"]
        .rank(method="min", ascending=False)
        .astype(int)
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
        "eligibility_minutes": 90,
        "primary_ranking_minutes": 270,
        "reliability_minutes": 450,
        "component_weights": {
            metric: weight
            for metric, (_, weight) in GOALKEEPER_METRICS.items()
        },
        "ranking_status_counts": (
            ratings["GKRankingStatus"].value_counts().to_dict()
        ),
    }
