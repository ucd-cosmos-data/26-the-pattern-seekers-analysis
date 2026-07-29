"""Leakage-safe goalkeeper features from StatsBomb events and lineups."""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass(frozen=True)
class PostShotModelMetrics:
    """OOF metrics for the event-derived post-shot goal model."""

    roc_auc: float
    pr_auc: float
    brier_score: float
    expected_calibration_error: float
    rows: int
    positives: int
    matches: int


def _coordinate(value: object, axis: int) -> float:
    if isinstance(value, (list, tuple)) and len(value) > axis:
        return float(value[axis])
    if not isinstance(value, str) or not value.strip():
        return np.nan
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return np.nan
    if not isinstance(parsed, (list, tuple)) or len(parsed) <= axis:
        return np.nan
    return float(parsed[axis])


def _truthy(series: pd.Series) -> pd.Series:
    return series.fillna(False).astype(str).str.lower().isin(
        {"true", "1", "yes"}
    )


def _ece(target: np.ndarray, prediction: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    bucket = np.clip(np.digitize(prediction, edges[1:-1]), 0, bins - 1)
    error = 0.0
    for index in range(bins):
        mask = bucket == index
        if mask.any():
            error += float(
                mask.mean()
                * abs(prediction[mask].mean() - target[mask].mean())
            )
    return error


def _post_shot_proxy(
    shots: pd.DataFrame,
    *,
    folds: int = 5,
    random_state: int = 42,
) -> tuple[pd.Series, dict[str, Any]]:
    """Return match-grouped OOF goal probabilities for on-target shots."""

    working = shots.copy()
    working["_end_y"] = working["shot_end_location"].map(
        lambda value: _coordinate(value, 1)
    )
    working["_end_z"] = working["shot_end_location"].map(
        lambda value: _coordinate(value, 2)
    )
    working["_distance_from_centre"] = (
        working["_end_y"] - 40.0
    ).abs()
    numeric = [
        "shot_statsbomb_xg",
        "_distance_from_centre",
        "_end_z",
    ]
    for column in ("shot_one_on_one", "shot_first_time"):
        if column in working:
            working[column] = _truthy(working[column]).astype(float)
            numeric.append(column)
    categorical = [
        column
        for column in (
            "shot_body_part",
            "shot_technique",
            "shot_type",
        )
        if column in working
    ]
    target = working["shot_outcome"].astype(str).str.contains(
        "Goal",
        case=False,
        na=False,
    ).astype(int)
    groups = working["match_id"].to_numpy()
    if (
        len(working) < 100
        or target.nunique() < 2
        or len(np.unique(groups)) < 3
    ):
        fallback = pd.to_numeric(
            working["shot_statsbomb_xg"],
            errors="coerce",
        ).fillna(target.mean())
        return fallback.clip(0.0, 1.0), {
            "gate_passed": False,
            "reason": "INSUFFICIENT_POST_SHOT_SAMPLE",
            "metrics": {},
            "fold_audit": [],
        }
    transformer = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        (
                            "imputer",
                            SimpleImputer(
                                strategy="constant",
                                fill_value="Missing",
                            ),
                        ),
                        (
                            "encode",
                            OneHotEncoder(
                                handle_unknown="ignore",
                                min_frequency=2,
                            ),
                        ),
                    ]
                ),
                categorical,
            ),
        ]
    )
    splitter = GroupKFold(
        n_splits=min(folds, len(np.unique(groups)))
    )
    prediction = np.full(len(working), np.nan)
    audit: list[dict[str, Any]] = []
    for fold, (train, validation) in enumerate(
        splitter.split(working, target, groups),
        start=1,
    ):
        model = Pipeline(
            [
                ("features", transformer),
                (
                    "model",
                    LogisticRegression(
                        C=0.5,
                        max_iter=2_000,
                        class_weight="balanced",
                        random_state=random_state + fold,
                    ),
                ),
            ]
        )
        model.fit(working.iloc[train], target.iloc[train])
        prediction[validation] = model.predict_proba(
            working.iloc[validation]
        )[:, 1]
        train_groups = sorted(np.unique(groups[train]).tolist())
        validation_groups = sorted(
            np.unique(groups[validation]).tolist()
        )
        if set(train_groups).intersection(validation_groups):
            raise RuntimeError("Goalkeeper post-shot match leakage detected")
        audit.append(
            {
                "fold": fold,
                "train_matches": train_groups,
                "validation_matches": validation_groups,
            }
        )
    truth = target.to_numpy(dtype=int)
    metrics = PostShotModelMetrics(
        roc_auc=float(roc_auc_score(truth, prediction)),
        pr_auc=float(average_precision_score(truth, prediction)),
        brier_score=float(brier_score_loss(truth, prediction)),
        expected_calibration_error=_ece(truth, prediction),
        rows=int(len(truth)),
        positives=int(truth.sum()),
        matches=int(len(np.unique(groups))),
    )
    gate = bool(
        metrics.roc_auc >= 0.60
        and metrics.brier_score <= 0.25
        and metrics.expected_calibration_error <= 0.15
    )
    return pd.Series(prediction, index=working.index), {
        "gate_passed": gate,
        "reason": "PASS" if gate else "POST_SHOT_MODEL_METRIC_GATE",
        "metrics": asdict(metrics),
        "fold_audit": audit,
    }


def build_goalkeeper_features(
    events: pd.DataFrame,
    player_profiles: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build a goalkeeper-only matrix and return its leakage/model audit."""

    required = {
        "match_id",
        "period",
        "team",
        "player_id",
        "type",
        "shot_outcome",
        "shot_statsbomb_xg",
        "goalkeeper_type",
        "under_pressure",
        "pass_outcome",
        "location",
    }
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(f"Goalkeeper event fields missing: {sorted(missing)}")
    keepers = player_profiles.loc[
        player_profiles["position_group"].eq("Goalkeeper")
    ].copy()
    keeper_ids = set(
        pd.to_numeric(keepers["player_id"], errors="coerce")
        .dropna()
        .astype(int)
    )
    goalkeeper_events = events.loc[
        events["player_id"].isin(keeper_ids)
    ].copy()
    primary = (
        goalkeeper_events.groupby(
            ["match_id", "team", "player_id"],
            as_index=False,
        )
        .size()
        .sort_values("size", ascending=False)
        .drop_duplicates(["match_id", "team"])
    )
    lookup = {
        (int(row.match_id), str(row.team)): int(row.player_id)
        for row in primary.itertuples(index=False)
    }
    match_teams = (
        events[["match_id", "team"]]
        .dropna()
        .drop_duplicates()
        .groupby("match_id")["team"]
        .apply(list)
        .to_dict()
    )
    all_shots = events.loc[events["type"].eq("Shot")].copy()
    shootout = all_shots["period"].eq(5)
    on_target = all_shots["shot_outcome"].astype(str).str.contains(
        "Goal|Saved",
        case=False,
        na=False,
    )
    eligible_shots = all_shots.loc[~shootout & on_target].copy()
    regular_penalty = eligible_shots.get(
        "shot_type",
        pd.Series("", index=eligible_shots.index),
    ).astype(str).str.contains("Penalty", case=False, na=False)
    model_shots = eligible_shots.loc[~regular_penalty].copy()
    proxy, post_shot_audit = _post_shot_proxy(model_shots)
    model_shots["post_shot_xg_model"] = proxy
    eligible_shots["post_shot_xg_model"] = np.nan
    eligible_shots.loc[
        model_shots.index,
        "post_shot_xg_model",
    ] = model_shots["post_shot_xg_model"]
    eligible_shots.loc[
        regular_penalty,
        "post_shot_xg_model",
    ] = pd.to_numeric(
        eligible_shots.loc[regular_penalty, "shot_statsbomb_xg"],
        errors="coerce",
    )
    records: list[dict[str, Any]] = []
    for row in eligible_shots.itertuples(index=False):
        opponents = [
            team
            for team in match_teams.get(int(row.match_id), [])
            if str(team) != str(row.team)
        ]
        if not opponents:
            continue
        player_id = lookup.get((int(row.match_id), str(opponents[0])))
        if player_id is None:
            continue
        records.append(
            {
                "player_id": player_id,
                "post_shot_xg_proxy": float(
                    0.0
                    if pd.isna(row.post_shot_xg_model)
                    else row.post_shot_xg_model
                ),
                "goal_allowed": float(
                    "Goal" in str(row.shot_outcome)
                ),
                "shot_on_target_faced": 1,
                "penalty_faced": int(
                    "Penalty" in str(getattr(row, "shot_type", ""))
                ),
                "high_leverage_shots_on_target": int(
                    float(
                        0.0
                        if pd.isna(row.shot_statsbomb_xg)
                        else row.shot_statsbomb_xg
                    )
                    > 0.30
                ),
                "high_leverage_saves": int(
                    float(
                        0.0
                        if pd.isna(row.shot_statsbomb_xg)
                        else row.shot_statsbomb_xg
                    )
                    > 0.30
                    and "Saved" in str(row.shot_outcome)
                ),
            }
        )
    shots = pd.DataFrame.from_records(records)
    if shots.empty:
        faced = pd.DataFrame({"player_id": list(keeper_ids)})
    else:
        faced = shots.groupby("player_id", as_index=False).sum()

    penalty_mask = (
        all_shots["period"].eq(5)
        | all_shots.get(
            "shot_type",
            pd.Series("", index=all_shots.index),
        ).astype(str).str.contains("Penalty", case=False, na=False)
    ) & on_target
    penalty_records: list[dict[str, Any]] = []
    for row in all_shots.loc[penalty_mask].itertuples(index=False):
        opponents = [
            team
            for team in match_teams.get(int(row.match_id), [])
            if str(team) != str(row.team)
        ]
        if not opponents:
            continue
        player_id = lookup.get((int(row.match_id), str(opponents[0])))
        if player_id is None:
            continue
        penalty_records.append(
            {
                "player_id": player_id,
                "penalties_faced": 1,
                "penalties_saved": int(
                    "Saved" in str(row.shot_outcome)
                ),
            }
        )
    penalty_frame = pd.DataFrame.from_records(penalty_records)
    if not penalty_frame.empty:
        penalty_summary = penalty_frame.groupby(
            "player_id",
            as_index=False,
        ).sum()
        faced = faced.merge(
            penalty_summary,
            on="player_id",
            how="outer",
        )

    cross_records: list[dict[str, Any]] = []
    if "pass_cross" in events:
        crosses = events.loc[
            events["type"].eq("Pass") & _truthy(events["pass_cross"])
        ]
        for row in crosses.itertuples(index=False):
            opponents = [
                team
                for team in match_teams.get(int(row.match_id), [])
                if str(team) != str(row.team)
            ]
            if not opponents:
                continue
            player_id = lookup.get((int(row.match_id), str(opponents[0])))
            if player_id is not None:
                cross_records.append(
                    {"player_id": player_id, "cross_opportunities": 1}
                )
    cross_frame = pd.DataFrame.from_records(cross_records)
    if not cross_frame.empty:
        cross_summary = cross_frame.groupby(
            "player_id",
            as_index=False,
        ).sum()
        faced = faced.merge(cross_summary, on="player_id", how="outer")

    goalkeeper_events["_claim"] = goalkeeper_events[
        "goalkeeper_type"
    ].astype(str).str.contains(
        "Collect|Claim|Punch",
        case=False,
        na=False,
    )
    goalkeeper_events["_sweeper"] = goalkeeper_events[
        "goalkeeper_type"
    ].astype(str).str.contains("Sweeper", case=False, na=False)
    goalkeeper_events["_pressured_pass"] = (
        goalkeeper_events["type"].eq("Pass")
        & _truthy(goalkeeper_events["under_pressure"])
    )
    goalkeeper_events["_completed_pressured_pass"] = (
        goalkeeper_events["_pressured_pass"]
        & goalkeeper_events["pass_outcome"].isna()
    )
    event_summary = goalkeeper_events.groupby(
        "player_id",
        as_index=False,
    ).agg(
        claims=("_claim", "sum"),
        sweeper_actions=("_sweeper", "sum"),
        pressured_passes=("_pressured_pass", "sum"),
        completed_pressured_passes=(
            "_completed_pressured_pass",
            "sum",
        ),
    )
    output = (
        keepers[["player_id", "team", "minutes"]]
        .merge(faced, on="player_id", how="left")
        .merge(event_summary, on="player_id", how="left")
    )
    numeric = [
        "post_shot_xg_proxy",
        "goal_allowed",
        "shot_on_target_faced",
        "penalty_faced",
        "high_leverage_shots_on_target",
        "high_leverage_saves",
        "claims",
        "sweeper_actions",
        "pressured_passes",
        "completed_pressured_passes",
        "penalties_faced",
        "penalties_saved",
        "cross_opportunities",
    ]
    for column in numeric:
        if column not in output:
            output[column] = 0.0
        output[column] = pd.to_numeric(
            output[column],
            errors="coerce",
        ).fillna(0.0)
    minutes = pd.to_numeric(
        output["minutes"],
        errors="coerce",
    ).clip(lower=1.0)
    output["goals_prevented_proxy"] = (
        output["post_shot_xg_proxy"] - output["goal_allowed"]
    )
    output["goals_prevented_proxy_p90"] = (
        90.0 * output["goals_prevented_proxy"] / minutes
    )
    output["save_rate"] = (
        (output["shot_on_target_faced"] - output["goal_allowed"])
        / output["shot_on_target_faced"].replace(0.0, np.nan)
    )
    output["high_leverage_save_pct"] = (
        output["high_leverage_saves"]
        / output["high_leverage_shots_on_target"].replace(0.0, np.nan)
    )
    output["claims_p90"] = 90.0 * output["claims"] / minutes
    output["cross_stopping_rate"] = (
        output["claims"]
        / output["cross_opportunities"].replace(0.0, np.nan)
    ).clip(0.0, 1.0)
    output["sweeper_actions_p90"] = (
        90.0 * output["sweeper_actions"] / minutes
    )
    output["distribution_under_pressure"] = (
        output["completed_pressured_passes"]
        / output["pressured_passes"].replace(0.0, np.nan)
    )
    total_penalties = float(output["penalties_faced"].sum())
    penalty_prior = (
        float(output["penalties_saved"].sum()) / total_penalties
        if total_penalties > 0
        else np.nan
    )
    observed_penalty_rate = (
        output["penalties_saved"]
        / output["penalties_faced"].replace(0.0, np.nan)
    )
    penalty_reliability = output["penalties_faced"] / (
        output["penalties_faced"] + 5.0
    )
    output["penalty_save_rate_shrunk"] = np.where(
        output["penalties_faced"].gt(0.0),
        penalty_reliability * observed_penalty_rate
        + (1.0 - penalty_reliability) * penalty_prior,
        np.nan,
    )
    audit = {
        "shootout_shots_excluded": int(shootout.sum()),
        "shootout_shots_used_only_in_penalty_channel": int(
            (shootout & on_target).sum()
        ),
        "regular_penalties_separated": int(regular_penalty.sum()),
        "high_leverage_xg_threshold": 0.30,
        "high_leverage_shots_on_target": int(
            output["high_leverage_shots_on_target"].sum()
        ),
        "post_shot_model": post_shot_audit,
        "global_ranking_eligible": False,
        "global_ranking_reason": (
            "StatsBomb Open Data has no native PSxG; goalkeepers are "
            "published in a separate calibrated ranking."
        ),
    }
    return output, audit
