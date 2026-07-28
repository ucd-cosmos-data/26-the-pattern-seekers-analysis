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


def _percentile(series: pd.Series, higher: bool) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    percentile = numeric.rank(method="average", pct=True)
    return percentile if higher else 1.0 - percentile


def calculate_goalkeeper_ratings(
    goalkeeper_features: pd.DataFrame,
    *,
    reliability_minutes: float = 300.0,
) -> pd.DataFrame:
    """Calculate a separate, reliability-shrunk goalkeeper leaderboard."""

    missing = set(GOALKEEPER_METRICS).difference(
        goalkeeper_features.columns
    )
    if missing:
        raise ValueError(f"Goalkeeper metrics missing: {sorted(missing)}")
    output = goalkeeper_features.copy()
    components = pd.DataFrame(index=output.index)
    availability = pd.DataFrame(index=output.index)
    for metric, higher in GOALKEEPER_METRICS.items():
        components[metric] = _percentile(output[metric], higher)
        availability[metric] = output[metric].notna()
    evidence = availability.sum(axis=1)
    score = components.mean(axis=1, skipna=True)
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
