#!/usr/bin/env python3
"""Write the v2 before/after, stability, coverage, and elite audit."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS = PROJECT_ROOT / "results/reports"
DIAGNOSTICS = PROJECT_ROOT / "results/diagnostics"
BASELINE_CANDIDATES = (
    DIAGNOSTICS / "v2_baseline_player_rankings.csv",
    REPORTS / "ranking/legacy/player_rankings.csv",
)


def _rho(left: pd.Series, right: pd.Series) -> float | None:
    mask = left.notna() & right.notna()
    if mask.sum() < 3:
        return None
    value = float(spearmanr(left[mask], right[mask]).statistic)
    return value if np.isfinite(value) else None


def main() -> None:
    DIAGNOSTICS.mkdir(parents=True, exist_ok=True)
    current = pd.read_csv(REPORTS / "ranking/player_rankings.csv")
    baseline_path = next(
        (path for path in BASELINE_CANDIDATES if path.is_file()),
        None,
    )
    if baseline_path is None:
        raise FileNotFoundError(
            "No pre-v2 ranking baseline found in diagnostics or the "
            "ranking/legacy archive"
        )
    baseline = pd.read_csv(baseline_path)
    teams = pd.read_csv(REPORTS / "canonical/data/team_metrics_v2.csv")
    outfield = current.loc[
        current["position_group_360"].ne("GK")
    ].copy()
    all_goalkeepers = current.loc[
        current["position_group_360"].eq("GK")
    ].copy()
    goalkeepers = all_goalkeepers.loc[
        all_goalkeepers["gk_rank_v2"].notna()
    ].copy()
    outfield["minutes_bucket"] = pd.cut(
        outfield["minutes"],
        bins=[45.0, 180.0, 300.0, np.inf],
        right=False,
        include_lowest=True,
        labels=["[45, 180)", "[180, 300)", "[300, inf)"],
    )
    bucket_summary = (
        outfield.groupby("minutes_bucket", observed=False)
        .agg(
            players=("player_name", "size"),
            mean_rating=("final_player_rating_v2", "mean"),
            median_rating=("final_player_rating_v2", "median"),
            rating_std=("final_player_rating_v2", "std"),
        )
        .reset_index()
    )
    bucket_summary.to_csv(
        DIAGNOSTICS / "v2_rating_distribution_by_minutes.csv",
        index=False,
    )
    top_positions = (
        outfield.sort_values(
            ["position_group_360", "final_player_rating_v2"],
            ascending=[True, False],
        )
        .groupby("position_group_360", sort=True)
        .head(10)
    )
    top_positions.to_csv(
        DIAGNOSTICS / "v2_top10_by_position.csv",
        index=False,
    )
    goalkeepers.sort_values("gk_rank_v2").to_csv(
        DIAGNOSTICS / "v2_goalkeeper_ranking.csv",
        index=False,
    )
    join_columns = ["player_id"] if "player_id" in baseline else [
        "player_name",
        "team",
    ]
    before_columns = [
        *join_columns,
        "player_name",
        "team",
        "position_group",
        "functional_role",
        "final_player_rating",
        "global_rank",
        "position_rank",
        "role_rank",
        "team_rank",
        "goalkeeper_rank",
        "minutes",
    ]
    after_columns = [
        *join_columns,
        "player_name",
        "team",
        "position_group_360",
        "functional_role",
        "final_player_rating_v2",
        "global_rank_v2",
        "position_rank_v2",
        "role_rank_v2",
        "team_rank_v2",
        "gk_rating_v2",
        "gk_rank_v2",
        "minutes_played",
    ]
    before_columns = list(dict.fromkeys(before_columns))
    after_columns = list(dict.fromkeys(after_columns))
    comparison = baseline[
        [column for column in before_columns if column in baseline]
    ].merge(
        current[[column for column in after_columns if column in current]],
        on=join_columns,
        how="outer",
        suffixes=("_before", "_after"),
        indicator=True,
    )
    comparison.to_csv(
        DIAGNOSTICS / "v2_before_after_player_ratings.csv",
        index=False,
    )
    target = (
        pd.to_numeric(outfield.get("goals", 0.0), errors="coerce")
        .fillna(0.0)
        + pd.to_numeric(outfield.get("xa_sum", 0.0), errors="coerce")
        .fillna(0.0)
    )
    elite_pattern = (
        "Messi|Mbapp|Griezmann|Álvarez|Alvarez|Di María|Di Maria|"
        "De Bruyne|Vinícius|Vinicius"
    )
    elite = outfield.loc[
        outfield["player_name"].str.contains(
            elite_pattern,
            case=False,
            na=False,
            regex=True,
        )
    ].sort_values("global_rank_v2")
    elite.to_csv(
        DIAGNOSTICS / "v2_named_elite_audit.csv",
        index=False,
    )
    team_fields = [
        "mean_creation_score",
        "mean_defensive_score",
        "mean_ball_security_score",
    ]
    missing_team_means = teams.loc[
        teams[team_fields].isna().any(axis=1),
        ["team", *team_fields],
    ]
    bucket_means = [
        float(value)
        for value in bucket_summary["mean_rating"].to_numpy()
    ]
    model_summary = json.loads(
        (REPORTS / "canonical/model_summary.json").read_text(encoding="utf-8")
    )
    checks = {
        "all_32_teams_present": int(teams["team"].nunique()) == 32,
        "all_team_primary_means_populated": missing_team_means.empty,
        "belgium_means_populated": bool(
            teams.loc[teams["team"].eq("Belgium"), team_fields]
            .notna()
            .all(axis=None)
        ),
        "ecuador_means_populated": bool(
            teams.loc[teams["team"].eq("Ecuador"), team_fields]
            .notna()
            .all(axis=None)
        ),
        "outfield_minimum_minutes": float(outfield["minutes"].min()),
        "goalkeeper_minimum_minutes": float(goalkeepers["minutes"].min()),
        "ranked_main_goalkeepers": int(len(goalkeepers)),
        "ranked_goalkeeper_teams": int(goalkeepers["team"].nunique()),
        "unranked_backup_goalkeepers": int(
            all_goalkeepers["gk_rank_v2"].isna().sum()
        ),
        "outfield_status_counts": (
            outfield["RankingStatus"].value_counts().to_dict()
        ),
        "goalkeeper_status_counts": (
            goalkeepers["GKRankingStatus"].value_counts().to_dict()
        ),
        "rating_spearman_minutes": _rho(
            outfield["final_player_rating_v2"],
            outfield["minutes"],
        ),
        "rating_spearman_goals_plus_xa": _rho(
            outfield["final_player_rating_v2"],
            target,
        ),
        "minutes_bucket_mean_ratings": {
            str(bucket): float(mean)
            for bucket, mean in zip(
                bucket_summary["minutes_bucket"],
                bucket_means,
                strict=True,
            )
        },
        "minutes_bucket_means_non_decreasing": bool(
            all(
                later >= earlier
                for earlier, later in zip(
                    bucket_means,
                    bucket_means[1:],
                )
            )
        ),
        "sub_180_players_in_global_top_20": int(
            outfield.nsmallest(20, "global_rank_v2")["minutes"].lt(180).sum()
        ),
        "contextual_vaep_gate": model_summary.get(
            "metrics",
            {},
        ).get("contextual_vaep_gate", {}),
        "composite_calibration_fallback": bool(
            model_summary.get("composite_calibration", {}).get(
                "fallback_to_incumbent",
                False,
            )
        ),
        "messi_global_rank": (
            int(
                outfield.loc[
                    outfield["player_name"].str.contains(
                        "Messi",
                        case=False,
                        na=False,
                    ),
                    "global_rank_v2",
                ].min()
            )
        ),
        "mbappe_global_rank": (
            int(
                outfield.loc[
                    outfield["player_name"].str.contains(
                        "Mbapp",
                        case=False,
                        na=False,
                    ),
                    "global_rank_v2",
                ].min()
            )
        ),
        "missing_team_means": missing_team_means.to_dict("records"),
    }
    (DIAGNOSTICS / "v2_validation_summary.json").write_text(
        json.dumps(checks, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(checks, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
