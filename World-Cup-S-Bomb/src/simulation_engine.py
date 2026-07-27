"""Vectorized physicality, chemistry, hurdle, and simulation primitives."""

from __future__ import annotations

import ast
import itertools
import time
import warnings
from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from scipy.optimize import linear_sum_assignment
from sklearn.base import clone
from sklearn.cluster import KMeans
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier


ATTACKING_STYLES = (
    "Patient Build-up",
    "Short Under Pressure",
    "Direct Long Play",
)
CANONICAL_TRANSITION_TARGET = "transition_conceded"
MIN_SUBSTITUTION_NET_XG_GAIN = 0.0050
V4_MIN_PLAYER_MINUTES = 300.0
V4_FINAL_THIRD_X = 80.0
V4_ATTACKING_WINGBACK_SHARE = 0.35
XT_GRID_COLUMNS = 16
XT_GRID_ROWS = 12
VAEP_ACTION_WINDOW = 3
VAEP_CV_FOLDS = 5
VAEP_TEST_MATCH_FRACTION = 0.16
REASON_GAIN_BELOW_THRESHOLD = "GAIN_BELOW_THRESHOLD"
REASON_CI_OVERLAPS_ZERO = "CONFIDENCE_INTERVAL_OVERLAPS_ZERO"
REASON_CLASSIFIER_ABSTAINED = "CLASSIFIER_ABSTAINED"
REASON_POSITIONAL_INCOMPATIBILITY = "POSITIONAL_INCOMPATIBILITY"
ROLE_PROTOTYPES: dict[str, dict[str, float]] = {
    "Target Forward": {"aerial_dominance_index": 2, "shots_p90": 2},
    "Ball-Winner": {"pressing_intensity_index": 3, "duel_win_rate": 1},
    "Progressive Winger": {
        "progressive_carries_p90": 2,
        "dribbles_p90": 2,
    },
    "Sweeper CB": {"clearances_p90": 2, "pass_completion": 1},
    "Deep Playmaker": {
        "progressive_passes_p90": 2,
        "pass_completion": 1,
    },
    "Box-to-Box Runner": {
        "speed_recovery_index": 2,
        "progressive_carries_p90": 1,
    },
    "Wide Creator": {"key_passes_p90": 2, "crosses_p90": 2},
    "Holding Anchor": {
        "interceptions_p90": 2,
        "pass_completion": 1,
        "turnovers_p90": -1,
    },
}

ATTACKING_POSITION_GROUPS = {
    "Forward",
    "Attacking Midfield/Wing",
    "Central/Wide Midfield",
    "Fullback/Wingback",
}


def _safe_rate(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.div(denominator.replace(0, np.nan)).fillna(0.0)


def aggregate_player_components(components_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate match components to one row per team/player."""

    numeric = components_df.select_dtypes(include=np.number).columns.difference(
        ["match_id", "player_id"]
    )
    totals = (
        components_df.groupby(["team", "player_id"], as_index=False)[
            numeric.tolist()
        ]
        .sum()
    )
    labels = (
        components_df.sort_values("minutes", ascending=False)
        .drop_duplicates(["team", "player_id"])
        [["team", "player_id", "player", "position", "position_group"]]
    )
    return totals.merge(labels, on=["team", "player_id"], validate="one_to_one")


def select_starter_cohort(
    components_df: pd.DataFrame,
    intervals_df: pd.DataFrame,
    *,
    count: int = 342,
) -> pd.DataFrame:
    """Select the exact requested cohort by starts, then tournament minutes."""

    totals = aggregate_player_components(components_df)
    starters = set(
        intervals_df.loc[intervals_df["start_minute"].eq(0), "player_id"].astype(
            int
        )
    )
    cohort = totals[totals["player_id"].astype(int).isin(starters)].copy()
    cohort = cohort.sort_values(
        ["minutes", "actions", "player_id"], ascending=[False, False, True]
    ).head(count)
    if len(cohort) != count:
        raise ValueError(f"Expected {count} starter-cohort players, found {len(cohort)}")
    return cohort


def derive_physicality_metrics(
    components_df: pd.DataFrame,
    player_ids: Iterable[int] | None = None,
) -> pd.DataFrame:
    """Compute physical indices and supporting per-90 role features."""

    profiles = aggregate_player_components(components_df)
    if player_ids is not None:
        wanted = {int(value) for value in player_ids}
        profiles = profiles[profiles["player_id"].astype(int).isin(wanted)].copy()
    minutes = profiles["minutes"].clip(lower=1)
    tackle_proxy = (
        profiles["duels_won"] - profiles["aerial_wins"]
    ).clip(lower=0)
    profiles["aerial_dominance_index"] = _safe_rate(
        profiles["aerial_wins"], profiles["aerial_events"]
    )
    profiles["pressing_intensity_index"] = (
        90
        * (tackle_proxy + profiles["interceptions"] + profiles["pressures"])
        / minutes
    )
    # The source has recoveries but no tracking-derived recovery-run field.
    profiles["speed_recovery_index"] = 90 * profiles["recoveries"] / minutes
    per90 = {
        "shots_p90": "shots",
        "progressive_carries_p90": "progressive_carries",
        "dribbles_p90": "dribbles",
        "clearances_p90": "clearances",
        "progressive_passes_p90": "progressive_passes",
        "key_passes_p90": "key_passes",
        "crosses_p90": "crosses",
        "interceptions_p90": "interceptions",
        "turnovers_p90": "turnovers",
        "xg_p90": "xg_sum",
    }
    for output, source in per90.items():
        profiles[output] = 90 * profiles[source] / minutes
    profiles["duel_win_rate"] = _safe_rate(
        profiles["duels_won"], profiles["duels"]
    )
    profiles["pass_completion"] = _safe_rate(
        profiles["completed_passes"], profiles["passes"]
    )
    for metric in (
        "aerial_dominance_index",
        "pressing_intensity_index",
        "speed_recovery_index",
    ):
        profiles[f"{metric}_percentile"] = profiles[metric].rank(pct=True) * 100
    return profiles.reset_index(drop=True)


def derive_individual_playstyle_clusters(
    profiles_df: pd.DataFrame,
    *,
    random_state: int = 42,
) -> pd.DataFrame:
    """Assign K=8 functional roles with deterministic prototype labeling."""

    features = sorted(
        {feature for weights in ROLE_PROTOTYPES.values() for feature in weights}
    )
    matrix = profiles_df[features].replace([np.inf, -np.inf], 0).fillna(0)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)
    model = KMeans(n_clusters=8, n_init=50, random_state=random_state)
    clusters = model.fit_predict(scaled)
    centroid_frame = pd.DataFrame(
        scaler.inverse_transform(model.cluster_centers_), columns=features
    )
    standardized_centroids = pd.DataFrame(
        model.cluster_centers_, columns=features
    )
    roles = list(ROLE_PROTOTYPES)
    score_matrix = np.zeros((8, 8))
    for cluster in range(8):
        for role_index, role in enumerate(roles):
            score_matrix[cluster, role_index] = sum(
                standardized_centroids.loc[cluster, feature] * weight
                for feature, weight in ROLE_PROTOTYPES[role].items()
            )
    row_index, column_index = linear_sum_assignment(-score_matrix)
    labels = {
        int(cluster): roles[int(role)]
        for cluster, role in zip(row_index, column_index, strict=True)
    }
    output = profiles_df.copy()
    output["playstyle_cluster"] = clusters
    output["functional_role"] = output["playstyle_cluster"].map(labels)
    output.attrs["cluster_centroids"] = centroid_frame
    return output


def _coordinate(value: object) -> tuple[float, float] | None:
    """Parse a StatsBomb coordinate stored as a list or string."""

    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return float(value[0]), float(value[1])
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return None
    if isinstance(parsed, (list, tuple)) and len(parsed) >= 2:
        return float(parsed[0]), float(parsed[1])
    return None


def derive_spatial_role_vectors(events_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate pass-receipt, line-breaking, and pressure-state role vectors."""

    passes = events_df[events_df["type"].eq("Pass")].copy()
    passes = passes[passes["player_id"].notna()]
    starts = passes["location"].map(_coordinate)
    ends = passes["pass_end_location"].map(_coordinate)
    passes["start_x"] = starts.map(lambda value: np.nan if value is None else value[0])
    passes["start_y"] = starts.map(lambda value: np.nan if value is None else value[1])
    passes["receipt_x"] = ends.map(lambda value: np.nan if value is None else value[0])
    passes["receipt_y"] = ends.map(lambda value: np.nan if value is None else value[1])
    passes["line_breaking_pass"] = (
        (passes["receipt_x"] - passes["start_x"] >= 15)
        | ((passes["start_x"] < 80) & (passes["receipt_x"] >= 80))
    ).astype(float)
    passes["under_pressure_flag"] = (
        passes["under_pressure"].astype(str).str.lower().isin(["true", "1"])
    ).astype(float)
    passes["completed_flag"] = passes["pass_outcome"].isna().astype(float)
    passes["completed_under_pressure"] = (
        passes["completed_flag"] * passes["under_pressure_flag"]
    )

    passer = (
        passes.groupby("player_id", as_index=False)
        .agg(
            pass_start_x=("start_x", "mean"),
            pass_start_y=("start_y", "mean"),
            line_breaking_pass_rate=("line_breaking_pass", "mean"),
            pressure_state_rate=("under_pressure_flag", "mean"),
            completed_under_pressure=("completed_under_pressure", "sum"),
            pressured_passes=("under_pressure_flag", "sum"),
        )
    )
    passer["distribution_under_pressure"] = _safe_rate(
        passer.pop("completed_under_pressure"), passer.pop("pressured_passes")
    )
    receiver = (
        passes[passes["pass_recipient_id"].notna()]
        .groupby("pass_recipient_id", as_index=False)
        .agg(
            pass_receipt_x=("receipt_x", "mean"),
            pass_receipt_y=("receipt_y", "mean"),
        )
        .rename(columns={"pass_recipient_id": "player_id"})
    )
    output = passer.merge(receiver, on="player_id", how="outer")
    output["player_id"] = output["player_id"].astype(int)
    return output


def cluster_player_playstyles(
    profiles_df: pd.DataFrame,
    events_df: pd.DataFrame,
    *,
    random_state: int = 42,
) -> pd.DataFrame:
    """Cluster spatially enriched outfield roles and isolate goalkeepers."""

    spatial = derive_spatial_role_vectors(events_df)
    enriched = profiles_df.merge(spatial, on="player_id", how="left")
    spatial_features = [
        "pass_start_x",
        "pass_start_y",
        "pass_receipt_x",
        "pass_receipt_y",
        "line_breaking_pass_rate",
        "pressure_state_rate",
        "distribution_under_pressure",
    ]
    base_features = sorted(
        {feature for weights in ROLE_PROTOTYPES.values() for feature in weights}
    )
    features = base_features + spatial_features
    enriched[spatial_features] = enriched[spatial_features].fillna(
        enriched[spatial_features].median(numeric_only=True)
    ).fillna(0)
    goalkeeper = enriched["position_group"].eq("Goalkeeper")
    outfield = enriched.loc[~goalkeeper].copy()
    if len(outfield) < 7:
        raise ValueError("At least seven outfield players are required for role clustering")
    scaler = StandardScaler()
    scaled = scaler.fit_transform(
        outfield[features].replace([np.inf, -np.inf], 0).fillna(0)
    )
    model = KMeans(n_clusters=7, n_init=40, random_state=random_state)
    clusters = model.fit_predict(scaled)
    centers = pd.DataFrame(model.cluster_centers_, columns=features)
    roles = list(ROLE_PROTOTYPES)
    scores = np.zeros((7, len(roles)))
    for cluster in range(7):
        for role_index, role in enumerate(roles):
            scores[cluster, role_index] = sum(
                centers.loc[cluster, feature] * weight
                for feature, weight in ROLE_PROTOTYPES[role].items()
            )
    rows, columns = linear_sum_assignment(-scores)
    labels = {
        int(cluster): roles[int(role)]
        for cluster, role in zip(rows, columns, strict=True)
    }
    enriched["playstyle_cluster"] = 7
    enriched["functional_role"] = "Goalkeeper"
    enriched.loc[outfield.index, "playstyle_cluster"] = clusters
    enriched.loc[outfield.index, "functional_role"] = pd.Series(
        clusters, index=outfield.index
    ).map(labels)
    enriched["playstyle_cluster"] = enriched["playstyle_cluster"].astype(int)
    enriched.attrs["spatial_features"] = spatial_features
    return enriched


def _truthy(series: pd.Series) -> pd.Series:
    """Return a null-safe boolean mask for StatsBomb CSV boolean fields."""

    return series.fillna(False).astype(str).str.lower().isin(
        {"true", "1", "yes"}
    )


def _coordinate_axis(series: pd.Series, axis: int) -> pd.Series:
    """Extract one coordinate axis from serialized StatsBomb locations."""

    return series.map(_coordinate).map(
        lambda value: np.nan if value is None else float(value[axis])
    )


def _successful_on_ball_mask(events: pd.DataFrame) -> pd.Series:
    """Identify completed on-ball actions used for spatial role footprints."""

    event_type = events["type"].fillna("")
    pass_success = event_type.eq("Pass") & events["pass_outcome"].isna()
    carry_success = event_type.eq("Carry")
    dribble_success = event_type.eq("Dribble") & events[
        "dribble_outcome"
    ].fillna("").eq("Complete")
    shot_action = event_type.eq("Shot")
    receipt_success = event_type.str.startswith("Ball Receipt") & events[
        "ball_receipt_outcome"
    ].isna()
    return (
        pass_success
        | carry_success
        | dribble_success
        | shot_action
        | receipt_success
    )


def _turnover_mask(events: pd.DataFrame) -> pd.Series:
    """Identify incomplete or possession-losing on-ball events."""

    event_type = events["type"].fillna("")
    incomplete_pass = event_type.eq("Pass") & events["pass_outcome"].notna()
    failed_dribble = event_type.eq("Dribble") & ~events[
        "dribble_outcome"
    ].fillna("").eq("Complete")
    failed_receipt = event_type.str.startswith("Ball Receipt") & events[
        "ball_receipt_outcome"
    ].notna()
    explicit_loss = event_type.isin({"Dispossessed", "Miscontrol"})
    return incomplete_pass | failed_dribble | failed_receipt | explicit_loss


def convert_statsbomb_events_to_spadl(events_df: pd.DataFrame) -> pd.DataFrame:
    """Convert the cached flattened StatsBomb export to a SPADL-compatible table.

    The installed ``socceraction`` dependency is preferred by the pipeline
    runner when importable. This converter is the deterministic local fallback
    for flattened CSV caches. It intentionally retains ``original_event_id`` so
    StatsBomb 360 context can be joined without positional assumptions.
    """

    required = {
        "id",
        "match_id",
        "index",
        "period",
        "minute",
        "second",
        "team",
        "team_id",
        "player_id",
        "type",
        "location",
    }
    missing = sorted(required - set(events_df.columns))
    if missing:
        raise ValueError(f"StatsBomb-to-SPADL conversion lacks columns: {missing}")

    actions = events_df.copy()
    actions["original_event_id"] = actions["id"].astype(str)
    actions["game_id"] = pd.to_numeric(actions["match_id"], errors="raise").astype(int)
    actions["action_id"] = (
        actions.sort_values(["game_id", "period", "index"])
        .groupby("game_id")
        .cumcount()
        .reindex(actions.index)
        .astype(int)
    )
    actions["period_id"] = pd.to_numeric(actions["period"], errors="coerce").fillna(1).astype(int)
    actions["time_seconds"] = (
        60 * pd.to_numeric(actions["minute"], errors="coerce").fillna(0)
        + pd.to_numeric(actions["second"], errors="coerce").fillna(0)
    )
    actions["start_x"] = _coordinate_axis(actions["location"], 0)
    actions["start_y"] = _coordinate_axis(actions["location"], 1)
    pass_end_x = _coordinate_axis(actions.get("pass_end_location", pd.Series(index=actions.index, dtype=object)), 0)
    pass_end_y = _coordinate_axis(actions.get("pass_end_location", pd.Series(index=actions.index, dtype=object)), 1)
    carry_end_x = _coordinate_axis(actions.get("carry_end_location", pd.Series(index=actions.index, dtype=object)), 0)
    carry_end_y = _coordinate_axis(actions.get("carry_end_location", pd.Series(index=actions.index, dtype=object)), 1)
    shot_end_x = _coordinate_axis(actions.get("shot_end_location", pd.Series(index=actions.index, dtype=object)), 0)
    shot_end_y = _coordinate_axis(actions.get("shot_end_location", pd.Series(index=actions.index, dtype=object)), 1)
    actions["end_x"] = (
        pass_end_x.combine_first(carry_end_x)
        .combine_first(shot_end_x)
        .combine_first(actions["start_x"])
    )
    actions["end_y"] = (
        pass_end_y.combine_first(carry_end_y)
        .combine_first(shot_end_y)
        .combine_first(actions["start_y"])
    )
    actions["type_name"] = actions["type"].fillna("Unknown").astype(str)
    actions["result_name"] = "success"
    pass_failed = actions["type_name"].eq("Pass") & actions.get(
        "pass_outcome", pd.Series(index=actions.index, dtype=object)
    ).notna()
    dribble_failed = actions["type_name"].eq("Dribble") & ~actions.get(
        "dribble_outcome", pd.Series(index=actions.index, dtype=object)
    ).fillna("").eq("Complete")
    receipt_failed = actions["type_name"].str.startswith("Ball Receipt") & actions.get(
        "ball_receipt_outcome", pd.Series(index=actions.index, dtype=object)
    ).notna()
    actions.loc[pass_failed | dribble_failed | receipt_failed, "result_name"] = "fail"
    actions["bodypart_name"] = (
        actions.get("pass_body_part", pd.Series(index=actions.index, dtype=object))
        .combine_first(actions.get("shot_body_part", pd.Series(index=actions.index, dtype=object)))
        .fillna("other")
        .astype(str)
    )
    actions["goal"] = (
        actions["type_name"].eq("Shot")
        & actions.get("shot_outcome", pd.Series(index=actions.index, dtype=object))
        .fillna("")
        .eq("Goal")
    )
    actions["under_pressure_flag"] = _truthy(
        actions.get("under_pressure", pd.Series(False, index=actions.index))
    )
    keep = [
        "game_id",
        "action_id",
        "original_event_id",
        "period_id",
        "time_seconds",
        "team",
        "team_id",
        "player",
        "player_id",
        "position",
        "play_pattern",
        "type_name",
        "result_name",
        "bodypart_name",
        "start_x",
        "start_y",
        "end_x",
        "end_y",
        "goal",
        "under_pressure_flag",
        "shot_statsbomb_xg",
        "pass_assisted_shot_id",
    ]
    for column in keep:
        if column not in actions:
            actions[column] = np.nan
    return (
        actions[keep]
        .sort_values(["game_id", "action_id"])
        .reset_index(drop=True)
    )


def _three_action_labels(actions: pd.DataFrame) -> pd.DataFrame:
    """Label goals strictly after the current action, never at offset zero."""

    labeled = actions.copy()
    scores = pd.Series(False, index=labeled.index)
    concedes = pd.Series(False, index=labeled.index)
    for _, indices in labeled.groupby("game_id", sort=False).groups.items():
        index = pd.Index(indices)
        game = labeled.loc[index]
        acting_team = game["team"].astype(str)
        game_score = game["goal"].astype(bool)
        goal_team = game["team"].astype(str)
        score_window = pd.Series(False, index=index)
        concede_window = pd.Series(False, index=index)
        for offset in range(1, VAEP_ACTION_WINDOW + 1):
            future_goal = game_score.shift(-offset, fill_value=False)
            future_team = goal_team.shift(-offset)
            score_window |= future_goal & future_team.eq(acting_team)
            concede_window |= future_goal & future_team.ne(acting_team)
        scores.loc[index] = score_window
        concedes.loc[index] = concede_window
    labeled["scores"] = scores.astype(int)
    labeled["concedes"] = concedes.astype(int)
    return labeled


def _fit_expected_threat_grid(
    training_actions: pd.DataFrame,
    scoring_actions: pd.DataFrame | None = None,
) -> tuple[np.ndarray, pd.Series]:
    """Fit xT on one match partition and score a disjoint partition."""

    scoring_actions = (
        training_actions if scoring_actions is None else scoring_actions
    )
    progression = training_actions["type_name"].isin({"Pass", "Carry"}) & training_actions[
        "result_name"
    ].eq("success")
    valid = progression & training_actions[
        ["start_x", "start_y", "end_x", "end_y"]
    ].notna().all(axis=1)
    moves = training_actions.loc[valid].copy()
    if moves.empty:
        raise ValueError("No successful pass/carry actions are available for xT")
    moves["start_col"] = np.floor(
        moves["start_x"].clip(0, 119.999) / (120 / XT_GRID_COLUMNS)
    ).astype(int)
    moves["start_row"] = np.floor(
        moves["start_y"].clip(0, 79.999) / (80 / XT_GRID_ROWS)
    ).astype(int)
    global_rate = float(moves["scores"].mean())
    cell = moves.groupby(["start_row", "start_col"])["scores"].agg(["sum", "count"])
    prior_actions = 40.0
    threat = np.full((XT_GRID_ROWS, XT_GRID_COLUMNS), global_rate, dtype=float)
    for (row, column), values in cell.iterrows():
        threat[int(row), int(column)] = (
            float(values["sum"]) + prior_actions * global_rate
        ) / (float(values["count"]) + prior_actions)
    # Light spatial smoothing reduces sparse-cell jumps without introducing
    # shots or defensive actions into xT fitting.
    padded = np.pad(threat, 1, mode="edge")
    smoothed = np.zeros_like(threat)
    for row in range(XT_GRID_ROWS):
        for column in range(XT_GRID_COLUMNS):
            smoothed[row, column] = padded[row : row + 3, column : column + 3].mean()
    scoring_progression = scoring_actions["type_name"].isin(
        {"Pass", "Carry"}
    ) & scoring_actions["result_name"].eq("success")
    scoring_valid = scoring_progression & scoring_actions[
        ["start_x", "start_y", "end_x", "end_y"]
    ].notna().all(axis=1)
    start_col = np.floor(
        scoring_actions["start_x"].fillna(0).clip(0, 119.999)
        / (120 / XT_GRID_COLUMNS)
    ).astype(int)
    start_row = np.floor(
        scoring_actions["start_y"].fillna(40).clip(0, 79.999)
        / (80 / XT_GRID_ROWS)
    ).astype(int)
    end_col = np.floor(
        scoring_actions["end_x"]
        .fillna(scoring_actions["start_x"])
        .fillna(0)
        .clip(0, 119.999)
        / (120 / XT_GRID_COLUMNS)
    ).astype(int)
    end_row = np.floor(
        scoring_actions["end_y"]
        .fillna(scoring_actions["start_y"])
        .fillna(40)
        .clip(0, 79.999)
        / (80 / XT_GRID_ROWS)
    ).astype(int)
    delta = pd.Series(0.0, index=scoring_actions.index)
    delta.loc[scoring_valid] = (
        smoothed[end_row[scoring_valid], end_col[scoring_valid]]
        - smoothed[start_row[scoring_valid], start_col[scoring_valid]]
    )
    return smoothed, delta


def _expected_calibration_error(
    truth: np.ndarray, probability: np.ndarray, bins: int = 10
) -> float:
    """Return equal-width expected calibration error."""

    edges = np.linspace(0.0, 1.0, bins + 1)
    assignments = np.clip(np.digitize(probability, edges[1:-1]), 0, bins - 1)
    error = 0.0
    for bin_id in range(bins):
        mask = assignments == bin_id
        if mask.any():
            error += float(mask.mean()) * abs(
                float(truth[mask].mean()) - float(probability[mask].mean())
            )
    return float(error)


@dataclass
class _PrefitProbabilityCalibrator:
    """Small sklearn-agnostic wrapper for a fitted binary classifier."""

    estimator: object
    calibrator: object
    method: str

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        raw = self.estimator.predict_proba(features)[:, 1]
        if self.method == "isotonic":
            calibrated = self.calibrator.predict(raw)
        else:
            calibrated = self.calibrator.predict_proba(
                raw.reshape(-1, 1)
            )[:, 1]
        calibrated = np.clip(calibrated, 0.0, 1.0)
        return np.column_stack([1.0 - calibrated, calibrated])


def _calibrate_prefit(
    estimator: object,
    features: np.ndarray,
    truth: np.ndarray,
    method: str,
) -> object:
    """Calibrate probabilities without refitting or sklearn estimator tags."""

    raw = estimator.predict_proba(features)[:, 1]
    if method == "isotonic":
        calibrator = IsotonicRegression(
            out_of_bounds="clip", y_min=0.0, y_max=1.0
        )
        calibrator.fit(raw, truth)
    elif method == "sigmoid":
        calibrator = LogisticRegression(
            C=1e6, solver="lbfgs", max_iter=500, random_state=42
        )
        calibrator.fit(raw.reshape(-1, 1), truth)
    else:
        raise ValueError(f"Unknown probability calibration method: {method}")
    return _PrefitProbabilityCalibrator(estimator, calibrator, method)


def _vaep_feature_matrix(actions: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Build a deterministic pre-action state matrix.

    Current-action results, endpoints, completion flags, and shot xG belong to
    the post-action audit table and are deliberately excluded here.
    """

    state = pd.DataFrame(index=actions.index)
    numeric = {
        "period_id": actions["period_id"],
        "time_seconds": actions["time_seconds"],
        "start_x": actions["start_x"],
        "start_y": actions["start_y"],
        "under_pressure": actions["under_pressure_flag"].astype(int),
        "defenders_within_5": actions["defenders_within_5"],
        "nearest_defender_distance": actions["nearest_defender_distance"],
        "defensive_density": actions["defensive_density"],
        "defenders_behind_ball": actions["defenders_behind_ball"],
    }
    for name, values in numeric.items():
        state[name] = pd.to_numeric(values, errors="coerce")
    state["same_team_previous_1"] = (
        actions["team"].eq(actions.groupby("game_id")["team"].shift(1)).astype(int)
    )
    state["same_team_previous_2"] = (
        actions["team"].eq(actions.groupby("game_id")["team"].shift(2)).astype(int)
    )
    categorical = pd.DataFrame(
        {
            "action_type": actions["type_name"].fillna("Unknown"),
            "play_pattern": actions["play_pattern"].fillna("Unknown"),
            "position": actions["position"].fillna("Unknown"),
            "previous_type_1": actions.groupby("game_id")["type_name"]
            .shift(1)
            .fillna("None"),
            "previous_type_2": actions.groupby("game_id")["type_name"]
            .shift(2)
            .fillna("None"),
        },
        index=actions.index,
    )
    # Fixed-width hashing avoids learning a category vocabulary from the
    # untouched test partition.
    for column in categorical:
        buckets = (
            pd.util.hash_pandas_object(
                categorical[column].astype(str), index=False
            ).to_numpy(dtype=np.uint64)
            % 16
        )
        for bucket in range(16):
            state[f"{column}_hash_{bucket:02d}"] = (
                buckets == bucket
            ).astype(np.float32)
    state = state.replace([np.inf, -np.inf], np.nan)
    state = state.fillna(
        {
            "period_id": 1.0,
            "time_seconds": 0.0,
            "start_x": 0.0,
            "start_y": 40.0,
        }
    ).fillna(0.0)
    prohibited = {
        "end_x",
        "end_y",
        "delta_x",
        "delta_y",
        "action_distance",
        "successful_action",
        "shot_xg",
        "result",
        "goal",
        "xt_value",
    }
    leaked = sorted(prohibited.intersection(state.columns))
    if leaked or any(column.startswith("xt") for column in state.columns):
        raise RuntimeError(f"Post-action leakage in VAEP features: {leaked}")
    return state.astype(np.float32), state.columns.tolist()


def _match_partitions(actions: pd.DataFrame) -> dict[str, list[int]]:
    """Create a deterministic test split without inspecting any target values."""

    matches = np.array(sorted(actions["game_id"].unique()), dtype=int)
    if len(matches) < 12:
        raise ValueError("At least 12 matches are required for VAEP partitions")
    shuffled = np.random.default_rng(42).permutation(matches)
    test_count = max(2, int(round(VAEP_TEST_MATCH_FRACTION * len(matches))))
    return {
        "development": shuffled[test_count:].tolist(),
        "test": shuffled[:test_count].tolist(),
    }


def _development_match_folds(
    development_matches: Sequence[int],
    folds: int = VAEP_CV_FOLDS,
) -> list[list[int]]:
    """Return identical deterministic match folds for every architecture."""

    shuffled = np.random.default_rng(314159).permutation(
        np.asarray(development_matches, dtype=int)
    )
    return [
        part.astype(int).tolist()
        for part in np.array_split(shuffled, min(folds, len(shuffled)))
        if len(part)
    ]


def _fit_calibration_split(
    training_matches: Sequence[int],
) -> tuple[list[int], list[int]]:
    """Split an outer-training match set without consulting labels."""

    shuffled = np.random.default_rng(271828).permutation(
        np.asarray(training_matches, dtype=int)
    )
    calibration_count = max(2, int(round(0.20 * len(shuffled))))
    return (
        shuffled[calibration_count:].astype(int).tolist(),
        shuffled[:calibration_count].astype(int).tolist(),
    )


def _cross_fit_expected_threat(
    actions: pd.DataFrame,
    partitions: dict[str, list[int]],
) -> tuple[np.ndarray, pd.Series, pd.Series]:
    """Score xT with grids that never saw the action's match."""

    development_matches = list(partitions["development"])
    test_matches = list(partitions["test"])
    folds = _development_match_folds(development_matches)
    values = pd.Series(np.nan, index=actions.index, dtype=float)
    sources = pd.Series("", index=actions.index, dtype=object)
    for fold_id, validation_matches in enumerate(folds):
        training_matches = sorted(
            set(development_matches) - set(validation_matches)
        )
        training = actions[actions["game_id"].isin(training_matches)]
        validation_mask = actions["game_id"].isin(validation_matches)
        _, fold_values = _fit_expected_threat_grid(
            training, actions.loc[validation_mask]
        )
        values.loc[validation_mask] = fold_values
        sources.loc[validation_mask] = f"development_oof_fold_{fold_id}"
    development = actions[actions["game_id"].isin(development_matches)]
    final_grid, test_values = _fit_expected_threat_grid(
        development, actions[actions["game_id"].isin(test_matches)]
    )
    test_mask = actions["game_id"].isin(test_matches)
    values.loc[test_mask] = test_values
    sources.loc[test_mask] = "untouched_test"
    if values.isna().any() or sources.eq("").any():
        raise RuntimeError("Cross-fitted xT coverage is incomplete")
    return final_grid, values, sources


def _model_specifications(
    score_weight: float, concede_weight: float
) -> list[dict[str, object]]:
    """Return baseline VAEP classifiers for architecture comparison."""

    return [
        {
            "name": "Baseline Logistic 360-VAEP",
            "algorithm": "LogisticRegression",
            "calibration": "isotonic",
            "score_model": make_pipeline(
                StandardScaler(),
                LogisticRegression(
                    C=0.5,
                    class_weight="balanced",
                    max_iter=500,
                    tol=1e-4,
                    random_state=42,
                ),
            ),
            "concede_model": make_pipeline(
                StandardScaler(),
                LogisticRegression(
                    C=0.5,
                    class_weight="balanced",
                    max_iter=500,
                    tol=1e-4,
                    random_state=42,
                ),
            ),
        },
        {
            "name": "XGBoost 360-VAEP",
            "algorithm": "XGBClassifier",
            "calibration": "isotonic",
            "score_model": XGBClassifier(
                n_estimators=160,
                max_depth=3,
                learning_rate=0.05,
                min_child_weight=6,
                subsample=0.85,
                colsample_bytree=0.85,
                reg_lambda=3.0,
                scale_pos_weight=score_weight,
                objective="binary:logistic",
                eval_metric="logloss",
                tree_method="hist",
                n_jobs=2,
                random_state=42,
            ),
            "concede_model": XGBClassifier(
                n_estimators=160,
                max_depth=3,
                learning_rate=0.05,
                min_child_weight=6,
                subsample=0.85,
                colsample_bytree=0.85,
                reg_lambda=3.0,
                scale_pos_weight=concede_weight,
                objective="binary:logistic",
                eval_metric="logloss",
                tree_method="hist",
                n_jobs=2,
                random_state=43,
            ),
        },
        {
            "name": "CatBoost 360-VAEP",
            "algorithm": "CatBoostClassifier",
            "calibration": "isotonic",
            "score_model": CatBoostClassifier(
                iterations=180,
                depth=5,
                learning_rate=0.05,
                loss_function="Logloss",
                auto_class_weights="Balanced",
                verbose=False,
                allow_writing_files=False,
                thread_count=2,
                random_seed=42,
            ),
            "concede_model": CatBoostClassifier(
                iterations=180,
                depth=5,
                learning_rate=0.05,
                loss_function="Logloss",
                auto_class_weights="Balanced",
                verbose=False,
                allow_writing_files=False,
                thread_count=2,
                random_seed=43,
            ),
        },
    ]


def _tuned_model_specifications(
    score_weight: float, concede_weight: float
) -> list[dict[str, object]]:
    """Return bounded tuning candidates when initial holdout targets are missed."""

    candidates: list[dict[str, object]] = []
    for depth, learning_rate, regularization, calibration in (
        (2, 0.03, 5.0, "isotonic"),
        (4, 0.03, 5.0, "sigmoid"),
        (3, 0.08, 8.0, "sigmoid"),
    ):
        common = dict(
            n_estimators=220,
            max_depth=depth,
            learning_rate=learning_rate,
            min_child_weight=8,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=regularization,
            objective="binary:logistic",
            eval_metric="logloss",
            tree_method="hist",
            n_jobs=2,
            random_state=100 + depth,
        )
        candidates.append(
            {
                "name": (
                    f"Tuned XGBoost d{depth} lr{learning_rate:g} "
                    f"{calibration} 360-VAEP"
                ),
                "algorithm": "XGBClassifier",
                "calibration": calibration,
                "score_model": XGBClassifier(
                    **common, scale_pos_weight=score_weight
                ),
                "concede_model": XGBClassifier(
                    **{**common, "random_state": 200 + depth},
                    scale_pos_weight=concede_weight,
                ),
            }
        )
    for depth, learning_rate, calibration in (
        (4, 0.04, "sigmoid"),
        (6, 0.04, "isotonic"),
    ):
        common = dict(
            iterations=240,
            depth=depth,
            learning_rate=learning_rate,
            loss_function="Logloss",
            auto_class_weights="Balanced",
            verbose=False,
            allow_writing_files=False,
            thread_count=2,
        )
        candidates.append(
            {
                "name": f"Tuned CatBoost d{depth} {calibration} 360-VAEP",
                "algorithm": "CatBoostClassifier",
                "calibration": calibration,
                "score_model": CatBoostClassifier(**common, random_seed=300 + depth),
                "concede_model": CatBoostClassifier(**common, random_seed=400 + depth),
            }
        )
    return candidates


def _fit_vaep_candidates(
    features: pd.DataFrame,
    actions: pd.DataFrame,
    partitions: dict[str, list[int]],
) -> tuple[pd.DataFrame, dict[str, object], list[str]]:
    """Compare candidates by development OOF metrics, then touch test once."""

    development_matches = list(partitions["development"])
    test_matches = list(partitions["test"])
    development_mask = actions["game_id"].isin(development_matches).to_numpy()
    test_mask = actions["game_id"].isin(test_matches).to_numpy()
    train_scores = actions.loc[development_mask, "scores"].to_numpy(dtype=int)
    train_concedes = actions.loc[
        development_mask, "concedes"
    ].to_numpy(dtype=int)
    score_weight = min(
        float((len(train_scores) - train_scores.sum()) / max(train_scores.sum(), 1)),
        250.0,
    )
    concede_weight = min(
        float(
            (len(train_concedes) - train_concedes.sum())
            / max(train_concedes.sum(), 1)
        ),
        250.0,
    )
    specifications = _model_specifications(score_weight, concede_weight)
    records: list[dict[str, object]] = []
    candidate_oof: dict[str, dict[str, np.ndarray]] = {}
    failures: list[str] = []
    folds = _development_match_folds(development_matches)
    partitions["cv_validation_folds"] = folds

    def fit_specification(specification: dict[str, object]) -> None:
        started = time.perf_counter()
        try:
            oof_by_target: dict[str, np.ndarray] = {
                "scores": np.full(len(actions), np.nan),
                "concedes": np.full(len(actions), np.nan),
            }
            latency = 0.0
            for target, model_key in (
                ("scores", "score_model"),
                ("concedes", "concede_model"),
            ):
                truth = actions[target].to_numpy(dtype=int)
                for validation_matches in folds:
                    outer_train_matches = sorted(
                        set(development_matches) - set(validation_matches)
                    )
                    fit_matches, calibration_matches = _fit_calibration_split(
                        outer_train_matches
                    )
                    fit_mask = actions["game_id"].isin(fit_matches).to_numpy()
                    calibration_mask = actions["game_id"].isin(
                        calibration_matches
                    ).to_numpy()
                    validation_mask = actions["game_id"].isin(
                        validation_matches
                    ).to_numpy()
                    estimator = clone(specification[model_key])
                    estimator.fit(
                        features.loc[fit_mask].to_numpy(), truth[fit_mask]
                    )
                    method = str(specification["calibration"])
                    calibrated = _calibrate_prefit(
                        estimator,
                        features.loc[calibration_mask].to_numpy(),
                        truth[calibration_mask],
                        method,
                    )
                    predict_started = time.perf_counter()
                    oof_by_target[target][validation_mask] = (
                        calibrated.predict_proba(
                            features.loc[validation_mask].to_numpy()
                        )[:, 1]
                    )
                    latency += time.perf_counter() - predict_started
            if any(
                np.isnan(probability[development_mask]).any()
                for probability in oof_by_target.values()
            ):
                raise RuntimeError("OOF prediction coverage is incomplete")
            oof_truth = np.concatenate(
                [
                    actions.loc[development_mask, target].to_numpy(dtype=int)
                    for target in ("scores", "concedes")
                ]
            )
            oof_probability = np.concatenate(
                [
                    oof_by_target[target][development_mask]
                    for target in ("scores", "concedes")
                ]
            )
            brier = float(brier_score_loss(oof_truth, oof_probability))
            roc_auc = float(roc_auc_score(oof_truth, oof_probability))
            pr_auc = float(
                average_precision_score(oof_truth, oof_probability)
            )
            ece = _expected_calibration_error(oof_truth, oof_probability)
            name = str(specification["name"])
            records.append(
                {
                    "model_name": name,
                    "algorithm_type": str(specification["algorithm"]),
                    "brier_score": brier,
                    "roc_auc": roc_auc,
                    "pr_auc": pr_auc,
                    "calibration_error": ece,
                    "latency_sec": float(latency),
                    "evaluation_scope": "development_match_oof",
                    "rows": int(len(oof_truth)),
                    "selected": False,
                }
            )
            candidate_oof[name] = oof_by_target
        except Exception as exc:
            failures.append(
                f"{specification['name']}: {type(exc).__name__}: {exc}"
            )

    for specification in specifications:
        fit_specification(specification)
    if not records:
        raise RuntimeError("All VAEP candidates failed: " + "; ".join(failures))
    validation = pd.DataFrame(records)
    validation["rank_brier"] = validation["brier_score"].rank(
        method="min", ascending=True
    ).astype(int)
    validation["rank_roc_auc"] = validation["roc_auc"].rank(
        method="min", ascending=False
    ).astype(int)
    rank_pr = validation["pr_auc"].rank(method="min", ascending=False)
    rank_calibration = validation["calibration_error"].rank(
        method="min", ascending=True
    )
    aggregate_rank = (
        validation["rank_brier"]
        + validation["rank_roc_auc"]
        + rank_pr
        + rank_calibration
    )
    validation["rank_overall"] = aggregate_rank.rank(
        method="min", ascending=True
    ).astype(int)
    validation = validation.sort_values(
        ["rank_overall", "brier_score", "roc_auc"],
        ascending=[True, True, False],
    ).reset_index(drop=True)
    selected_name = str(validation.iloc[0]["model_name"])
    validation.loc[
        validation["model_name"].eq(selected_name), "selected"
    ] = True
    selected_specification = next(
        specification
        for specification in specifications
        if specification["name"] == selected_name
    )
    final_fit_matches, final_calibration_matches = _fit_calibration_split(
        development_matches
    )
    partitions["final_fit"] = final_fit_matches
    partitions["final_calibration"] = final_calibration_matches
    final_models: dict[str, object] = {}
    scored_probabilities = candidate_oof[selected_name]
    test_truth_parts: list[np.ndarray] = []
    test_probability_parts: list[np.ndarray] = []
    for target, model_key in (
        ("scores", "score_model"),
        ("concedes", "concede_model"),
    ):
        truth = actions[target].to_numpy(dtype=int)
        fit_mask = actions["game_id"].isin(final_fit_matches).to_numpy()
        calibration_mask = actions["game_id"].isin(
            final_calibration_matches
        ).to_numpy()
        estimator = clone(selected_specification[model_key])
        estimator.fit(features.loc[fit_mask].to_numpy(), truth[fit_mask])
        calibrated = _calibrate_prefit(
            estimator,
            features.loc[calibration_mask].to_numpy(),
            truth[calibration_mask],
            str(selected_specification["calibration"]),
        )
        final_models[target] = calibrated
        scored_probabilities[target][test_mask] = calibrated.predict_proba(
            features.loc[test_mask].to_numpy()
        )[:, 1]
        test_truth_parts.append(truth[test_mask])
        test_probability_parts.append(scored_probabilities[target][test_mask])
    test_truth = np.concatenate(test_truth_parts)
    test_probability = np.concatenate(test_probability_parts)
    if np.isnan(
        np.column_stack(
            [
                scored_probabilities["scores"],
                scored_probabilities["concedes"],
            ]
        )
    ).any():
        raise RuntimeError("Some player actions lack OOF or held-out predictions")
    test_metrics = {
        "brier_score": float(brier_score_loss(test_truth, test_probability)),
        "roc_auc": float(roc_auc_score(test_truth, test_probability)),
        "pr_auc": float(average_precision_score(test_truth, test_probability)),
        "calibration_error": _expected_calibration_error(
            test_truth, test_probability
        ),
    }
    selected = {
        "model_name": selected_name,
        "algorithm_type": str(validation.iloc[0]["algorithm_type"]),
        "models": final_models,
        "calibration_method": str(selected_specification["calibration"]),
        "fit_elapsed_sec": np.nan,
        "test_truth": test_truth,
        "test_probability": test_probability,
        "test_metrics": test_metrics,
        "action_probabilities": scored_probabilities,
    }
    return validation, selected, failures


def build_v4_player_evaluations(
    components_df: pd.DataFrame,
    events_df: pd.DataFrame,
    frame_actors_df: pd.DataFrame,
    frame_metrics_df: pd.DataFrame,
    *,
    min_minutes: float = V4_MIN_PLAYER_MINUTES,
    legacy_validation_metrics: dict[str, object] | None = None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, object],
    dict[str, object],
]:
    """Build unified team rankings from independent xT and 360-VAEP systems."""

    base_profiles = derive_physicality_metrics(components_df)
    profiles = base_profiles.loc[base_profiles["minutes"].ge(min_minutes)].copy()
    if profiles.empty:
        raise ValueError("No players satisfy the V4 minutes cutoff")

    actions = convert_statsbomb_events_to_spadl(events_df)
    actions = actions[actions["player_id"].notna()].copy()
    actions["player_id"] = actions["player_id"].astype(int)
    actions = _three_action_labels(actions)

    frame_metrics = (
        frame_metrics_df.drop_duplicates(["match_id", "event_uuid"])
        .rename(columns={"match_id": "game_id", "event_uuid": "original_event_id"})
        .copy()
    )
    frame_metrics["original_event_id"] = frame_metrics[
        "original_event_id"
    ].astype(str)
    spatial_columns = [
        "game_id",
        "original_event_id",
        "defenders_within_5",
        "nearest_defender_distance",
        "defensive_density",
        "defenders_behind_ball",
    ]
    for column in spatial_columns:
        if column not in frame_metrics:
            frame_metrics[column] = np.nan
    actions = actions.merge(
        frame_metrics[spatial_columns],
        on=["game_id", "original_event_id"],
        how="left",
        validate="many_to_one",
    )
    joined_360 = int(actions["nearest_defender_distance"].notna().sum())
    merge_warning = None
    if joined_360 == 0:
        merge_warning = (
            "StatsBomb 360 event IDs did not match; standard VAEP state "
            "features were used with neutral spatial defaults."
        )
        warnings.warn(merge_warning, RuntimeWarning)
    for column in spatial_columns[2:]:
        numeric = pd.to_numeric(actions[column], errors="coerce")
        # Zero is the documented neutral/missing 360 context. No statistic is
        # learned from the held-out matches.
        actions[column] = numeric.fillna(0.0)

    partitions = _match_partitions(actions)
    xt_grid, actions["xt_value"], actions["xt_scoring_partition"] = (
        _cross_fit_expected_threat(actions, partitions)
    )
    vaep_features, feature_names = _vaep_feature_matrix(actions)
    validation, selected, failures = _fit_vaep_candidates(
        vaep_features, actions, partitions
    )
    for target, output in (
        ("scores", "p_scores"),
        ("concedes", "p_concedes"),
    ):
        actions[output] = selected["action_probabilities"][target]
    actions["vaep_scoring_partition"] = np.where(
        actions["game_id"].isin(partitions["test"]),
        "untouched_test",
        "development_oof",
    )
    actions["vaep_value"] = actions["p_scores"] - actions["p_concedes"]
    shot_xg_lookup = (
        actions.loc[
            actions["type_name"].eq("Shot"),
            ["original_event_id", "shot_statsbomb_xg"],
        ]
        .drop_duplicates("original_event_id")
        .set_index("original_event_id")["shot_statsbomb_xg"]
    )
    actions["xa_value"] = (
        actions["pass_assisted_shot_id"]
        .astype(str)
        .map(pd.to_numeric(shot_xg_lookup, errors="coerce"))
        .fillna(0.0)
    )

    defensive_types = {
        "Pressure",
        "Duel",
        "Interception",
        "Block",
        "Clearance",
        "Ball Recovery",
        "Goal Keeper",
        "Foul Committed",
        "Shield",
        "Error",
    }
    actions["action_side"] = np.where(
        actions["type_name"].isin(defensive_types), "defense", "offense"
    )
    touch_types = {
        "Pass",
        "Carry",
        "Dribble",
        "Shot",
        "Ball Receipt*",
        "Miscontrol",
        "Dispossessed",
    }
    actions["touch"] = (
        actions["type_name"].isin(touch_types)
        | actions["type_name"].str.startswith("Ball Receipt")
    )
    values = (
        actions.groupby("player_id", as_index=False)
        .agg(
            vaep_total=("vaep_value", "sum"),
            vaep_offense=(
                "vaep_value",
                lambda series: float(
                    series[actions.loc[series.index, "action_side"].eq("offense")].sum()
                ),
            ),
            vaep_defense=(
                "vaep_value",
                lambda series: float(
                    series[actions.loc[series.index, "action_side"].eq("defense")].sum()
                ),
            ),
            total_touches=("touch", "sum"),
            xt_total=("xt_value", "sum"),
            xa_sum=("xa_value", "sum"),
            events_with_360_context=(
                "nearest_defender_distance",
                "count",
            ),
        )
    )
    profiles = profiles.merge(values, on="player_id", how="left")
    value_columns = [
        "vaep_total",
        "vaep_offense",
        "vaep_defense",
        "total_touches",
        "xt_total",
        "xa_sum",
        "events_with_360_context",
    ]
    profiles[value_columns] = profiles[value_columns].fillna(0.0)
    minutes = profiles["minutes"].clip(lower=1.0)
    profiles["vaep_off_p90"] = 90 * profiles["vaep_offense"] / minutes
    profiles["vaep_def_p90"] = 90 * profiles["vaep_defense"] / minutes
    profiles["vaep_total_p90"] = 90 * profiles["vaep_total"] / minutes
    profiles["vaep_per_touch"] = _safe_rate(
        profiles["vaep_total"], profiles["total_touches"]
    )
    profiles["xt_p90"] = 90 * profiles["xt_total"] / minutes
    profiles["xa_p90"] = 90 * profiles["xa_sum"] / minutes
    profiles["raw_final_player_rating"] = (
        0.50 * profiles["vaep_total_p90"]
        + 0.30 * profiles["vaep_per_touch"]
        + 0.20 * profiles["xt_p90"]
    )
    # Preserve the established role-relative hierarchy while protecting the
    # 300-minute boundary from volatile per-90 estimates. This is an
    # evaluation-only empirical-Bayes shrinkage, never a model input.
    role_prior = profiles.groupby("position_group")[
        "raw_final_player_rating"
    ].transform("mean")
    profiles["rating_minutes_reliability"] = minutes / (minutes + 300.0)
    profiles["final_player_rating"] = (
        profiles["rating_minutes_reliability"]
        * profiles["raw_final_player_rating"]
        + (1.0 - profiles["rating_minutes_reliability"]) * role_prior
    )
    profiles["team_rank"] = (
        profiles.groupby("team")["final_player_rating"]
        .rank(method="min", ascending=False)
        .astype(int)
    )
    # Compatibility for simulation routines; all reporting and ranking uses
    # the cross-role unified rating and team_rank.
    profiles["player_evaluation_score"] = profiles["final_player_rating"]

    profiles = cluster_player_playstyles(profiles, events_df)
    successful = actions[
        actions["type_name"].isin({"Pass", "Carry", "Dribble", "Shot"})
        & actions["result_name"].eq("success")
    ][["game_id", "original_event_id", "player_id", "end_x", "end_y"]].dropna()
    action_points = successful.rename(
        columns={
            "game_id": "match_id",
            "original_event_id": "id",
            "end_x": "x",
            "end_y": "y",
        }
    )
    action_points["spatial_source"] = "standard_event_endpoint"
    actors = frame_actors_df[_truthy(frame_actors_df["actor"])].rename(
        columns={"event_uuid": "id"}
    )
    action_identity = actions[
        ["game_id", "original_event_id", "player_id"]
    ].rename(columns={"game_id": "match_id", "original_event_id": "id"})
    actor_points = actors.merge(
        action_identity.drop_duplicates(["match_id", "id"]),
        on=["match_id", "id"],
        how="inner",
        validate="many_to_one",
    )[["match_id", "id", "player_id", "x", "y"]].dropna()
    actor_points["spatial_source"] = "statsbomb_360_actor_snapshot"
    eligible_ids = set(profiles["player_id"].astype(int))
    action_points = action_points[action_points["player_id"].isin(eligible_ids)]
    actor_points = actor_points[actor_points["player_id"].isin(eligible_ids)]
    spatial_points = pd.concat([action_points, actor_points], ignore_index=True)
    spatial_points["final_third"] = spatial_points["x"].gt(V4_FINAL_THIRD_X)
    spatial_summary = (
        spatial_points.groupby("player_id", as_index=False)
        .agg(
            spatial_point_count=("x", "size"),
            final_third_share=("final_third", "mean"),
            average_spatial_x=("x", "mean"),
            average_spatial_y=("y", "mean"),
        )
    )
    profiles = profiles.merge(spatial_summary, on="player_id", how="left")
    profiles[
        [
            "spatial_point_count",
            "final_third_share",
            "average_spatial_x",
            "average_spatial_y",
        ]
    ] = profiles[
        [
            "spatial_point_count",
            "final_third_share",
            "average_spatial_x",
            "average_spatial_y",
        ]
    ].fillna(0.0)
    fullback = profiles["position_group"].eq("Fullback/Wingback")
    attacking_wingback = fullback & profiles["final_third_share"].gt(
        V4_ATTACKING_WINGBACK_SHARE
    )
    profiles.loc[attacking_wingback, "functional_role"] = "Attacking Wingback"
    profiles.loc[
        fullback & profiles["functional_role"].eq("Holding Anchor"),
        "functional_role",
    ] = "Two-Way Fullback"
    profiles["Functional role"] = profiles["functional_role"]

    spatial_points["x_bin"] = np.floor(
        spatial_points["x"].clip(0, 119.999) / 10
    ).astype(int)
    spatial_points["y_bin"] = np.floor(
        spatial_points["y"].clip(0, 79.999) / 10
    ).astype(int)
    heatmap_cells = (
        spatial_points.groupby(["player_id", "x_bin", "y_bin"], as_index=False)
        .agg(
            point_count=("x", "size"),
            standard_event_points=(
                "spatial_source",
                lambda values: int(values.eq("standard_event_endpoint").sum()),
            ),
            freeze_frame_points=(
                "spatial_source",
                lambda values: int(
                    values.eq("statsbomb_360_actor_snapshot").sum()
                ),
            ),
        )
    )
    heatmap_cells["density"] = heatmap_cells["point_count"].div(
        heatmap_cells.groupby("player_id")["point_count"].transform("sum")
    )

    finite = [
        "vaep_off_p90",
        "vaep_def_p90",
        "vaep_total_p90",
        "vaep_per_touch",
        "xt_p90",
        "final_player_rating",
    ]
    if not np.isfinite(profiles[finite].to_numpy()).all():
        raise ValueError("VAEP/xT player evaluation produced non-finite metrics")
    best_metrics = validation.loc[validation["selected"]].iloc[0]
    if legacy_validation_metrics is not None:
        validation = pd.concat(
            [
                validation,
                pd.DataFrame(
                    [
                        {
                            "model_name": "Legacy transition classifier",
                            "algorithm_type": "LegacyTransitionClassifier",
                            "brier_score": float(
                                legacy_validation_metrics["brier"]
                            ),
                            "roc_auc": float(
                                legacy_validation_metrics["roc_auc"]
                            ),
                            "pr_auc": float(
                                legacy_validation_metrics["pr_auc"]
                            ),
                            "calibration_error": np.nan,
                            "latency_sec": np.nan,
                            "evaluation_scope": (
                                "legacy_transition_tournament_oof"
                            ),
                            "rows": int(
                                legacy_validation_metrics.get("rows", 0)
                            ),
                            "selected": False,
                            "rank_brier": np.nan,
                            "rank_roc_auc": np.nan,
                            "rank_overall": np.nan,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    provenance: dict[str, object] = {
        "schema_version": 4,
        "valuation_system": "360-Augmented VAEP and xT (applied concurrently)",
        "spadl_converter": "local_flattened_statsbomb_fallback",
        "socceraction_import_issue": (
            "pandera/multimethod incompatibility; no remote fetch required"
        ),
        "original_event_id_preserved": True,
        "xt_grid_shape": [XT_GRID_ROWS, XT_GRID_COLUMNS],
        "xt_training_action_types": ["successful Pass", "successful Carry"],
        "xt_not_in_vaep_features": True,
        "vaep_action_window": VAEP_ACTION_WINDOW,
        "vaep_feature_names": feature_names,
        "vaep_selected_model": selected["model_name"],
        "vaep_selected_algorithm": selected["algorithm_type"],
        "vaep_calibration_method": selected["calibration_method"],
        "vaep_oof_metrics": {
            "brier_score": float(best_metrics["brier_score"]),
            "roc_auc": float(best_metrics["roc_auc"]),
            "pr_auc": float(best_metrics["pr_auc"]),
            "calibration_error": float(best_metrics["calibration_error"]),
        },
        "vaep_final_test_metrics": selected["test_metrics"],
        # Compatibility alias retained for downstream consumers; its contents
        # now refer only to the single final untouched-test evaluation.
        "vaep_holdout_metrics": selected["test_metrics"],
        "candidate_selection_scope": "development_match_oof_only",
        "test_used_for_model_selection": False,
        "action_scoring_policy": "development OOF plus final untouched test",
        "target_window_offsets": list(range(1, VAEP_ACTION_WINDOW + 1)),
        "pre_action_features_only": True,
        "post_action_fields_excluded": [
            "result_name",
            "end_x",
            "end_y",
            "shot_statsbomb_xg",
            "goal",
        ],
        "xt_cross_fitted_by_match": True,
        "vaep_model_comparison": validation.to_dict("records"),
        "model_failures": failures,
        "partitions": partitions,
        "minutes_cutoff": float(min_minutes),
        "players_before_cutoff": int(len(base_profiles)),
        "players_after_cutoff": int(len(profiles)),
        "players_dropped": int(len(base_profiles) - len(profiles)),
        "event_rows": int(len(actions)),
        "events_with_360_context": joined_360,
        "360_join_rate": float(joined_360 / max(len(actions), 1)),
        "360_merge_warning": merge_warning,
        "successful_action_points": int(len(action_points)),
        "freeze_frame_actor_points": int(len(actor_points)),
        "heatmap_cells": int(len(heatmap_cells)),
        "attacking_wingbacks": int(attacking_wingback.sum()),
        "ranking_formula": (
            "role-relative minutes shrinkage of "
            "(0.50*vaep_total_p90 + 0.30*vaep_per_touch + 0.20*xt_p90), "
            "reliability=minutes/(minutes+300)"
        ),
    }
    model_bundle = {
        "schema_version": "4.1-vaep-xt",
        "selected_model_name": selected["model_name"],
        "selected_algorithm": selected["algorithm_type"],
        "calibration_method": selected["calibration_method"],
        "score_model": selected["models"]["scores"],
        "concede_model": selected["models"]["concedes"],
        "feature_names": feature_names,
        "xt_grid": xt_grid,
        "xt_grid_shape": [XT_GRID_ROWS, XT_GRID_COLUMNS],
        "partitions": partitions,
        "test_truth": selected["test_truth"],
        "test_probability": selected["test_probability"],
        "validation_records": validation.to_dict("records"),
    }
    return (
        profiles.sort_values(
            ["team", "team_rank", "player"], ascending=[True, True, True]
        ).reset_index(drop=True),
        heatmap_cells,
        actions,
        provenance,
        model_bundle,
    )


def compute_player_synergy_matrix(
    components_df: pd.DataFrame,
    passes_df: pd.DataFrame,
    intervals_df: pd.DataFrame,
    player_ids: Sequence[int],
) -> pd.DataFrame:
    """Build a complete long-form 342×342 shared-minutes/pass matrix."""

    ids = pd.Index([int(value) for value in player_ids], name="row_player_id")
    full = pd.MultiIndex.from_product(
        [ids, ids], names=["row_player_id", "column_player_id"]
    ).to_frame(index=False)
    intervals = intervals_df[
        intervals_df["player_id"].astype(int).isin(ids)
    ].copy()
    intervals["player_id"] = intervals["player_id"].astype(int)
    left = intervals.rename(
        columns={
            "player_id": "row_player_id",
            "start_minute": "row_start",
            "end_minute": "row_end",
        }
    )
    right = intervals.rename(
        columns={
            "player_id": "column_player_id",
            "start_minute": "column_start",
            "end_minute": "column_end",
        }
    )
    overlap = left.merge(right, on=["match_id", "team"], how="inner")
    overlap["shared_minutes"] = (
        np.minimum(overlap["row_end"], overlap["column_end"])
        - np.maximum(overlap["row_start"], overlap["column_start"])
    ).clip(lower=0)
    shared = (
        overlap.groupby(["row_player_id", "column_player_id"], as_index=False)[
            "shared_minutes"
        ]
        .sum()
    )

    passes = passes_df[
        passes_df["player_id"].notna()
        & passes_df["pass_recipient_id"].notna()
    ].copy()
    passes["row_player_id"] = passes["player_id"].astype(int)
    passes["column_player_id"] = passes["pass_recipient_id"].astype(int)
    passes = passes[
        passes["row_player_id"].isin(ids)
        & passes["column_player_id"].isin(ids)
    ]
    passes["pair_low"] = passes[
        ["row_player_id", "column_player_id"]
    ].min(axis=1)
    passes["pair_high"] = passes[
        ["row_player_id", "column_player_id"]
    ].max(axis=1)
    passes["completed"] = passes["pass_outcome"].isna().astype(int)
    pass_pairs = (
        passes.groupby(["pair_low", "pair_high"], as_index=False)
        .agg(joint_passes=("completed", "size"), completed_joint_passes=("completed", "sum"))
    )
    reverse = pass_pairs.rename(
        columns={"pair_low": "row_player_id", "pair_high": "column_player_id"}
    )
    mirrored = reverse[
        reverse["row_player_id"].ne(reverse["column_player_id"])
    ].rename(
        columns={
            "row_player_id": "column_player_id",
            "column_player_id": "row_player_id",
        }
    )
    directed_passes = pd.concat([reverse, mirrored], ignore_index=True)
    matrix = full.merge(
        shared, on=["row_player_id", "column_player_id"], how="left"
    ).merge(
        directed_passes,
        on=["row_player_id", "column_player_id"],
        how="left",
    )
    matrix[["shared_minutes", "joint_passes", "completed_joint_passes"]] = (
        matrix[
            ["shared_minutes", "joint_passes", "completed_joint_passes"]
        ].fillna(0)
    )
    global_completion = float(passes["completed"].mean()) if len(passes) else 0.75
    matrix["joint_pass_completion_rate"] = (
        matrix["completed_joint_passes"] + 5 * global_completion
    ) / (matrix["joint_passes"] + 5)
    reliability = 1 - np.exp(-matrix["shared_minutes"] / 270)
    matrix["synergy_score"] = (
        matrix["joint_pass_completion_rate"] * reliability
    ).clip(0, 1)
    diagonal = matrix["row_player_id"].eq(matrix["column_player_id"])
    matrix.loc[diagonal, ["joint_pass_completion_rate", "synergy_score"]] = 1.0
    return matrix


def _parse_lineup(value: object) -> list[int]:
    if isinstance(value, list):
        return [int(item) for item in value]
    return [int(item) for item in ast.literal_eval(str(value))]


def _lineup_physical_aggregates(
    lineup_series: pd.Series,
    profiles: pd.DataFrame,
    synergy_lookup: dict[tuple[int, int], float],
    prefix: str,
) -> pd.DataFrame:
    profile_index = profiles.set_index("player_id")
    records: list[dict[str, float | str]] = []
    cache: dict[str, dict[str, float]] = {}
    for raw in lineup_series.astype(str):
        if raw not in cache:
            ids = _parse_lineup(raw)
            available = profile_index.reindex(ids)
            pair_scores = [
                synergy_lookup.get((left, right), 0.0)
                for left, right in itertools.combinations(ids, 2)
            ]
            cache[raw] = {
                f"{prefix}_avg_aerial_dominance": float(
                    available["aerial_dominance_index"].fillna(0).mean()
                ),
                f"{prefix}_max_pressing_rate": float(
                    available["pressing_intensity_index"].fillna(0).max()
                ),
                f"{prefix}_min_recovery_speed": float(
                    available["speed_recovery_index"].fillna(0).min()
                ),
                f"{prefix}_overall_lineup_chemistry_score": float(
                    np.mean(pair_scores) if pair_scores else 0
                ),
                f"{prefix}_weakest_link_chemistry": float(
                    np.min(pair_scores) if pair_scores else 0
                ),
            }
        records.append({"lineup_key": raw, **cache[raw]})
    return pd.DataFrame(records, index=lineup_series.index).drop(
        columns="lineup_key"
    )


def build_lineup_matchup_features(
    lineups_df: pd.DataFrame,
    profiles_df: pd.DataFrame,
    synergy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate physicality/chemistry and compute direct lineup deltas."""

    lookup = {
        (int(row.row_player_id), int(row.column_player_id)): float(
            row.synergy_score
        )
        for row in synergy_df.itertuples(index=False)
    }
    attacking = _lineup_physical_aggregates(
        lineups_df["attacking_player_ids"], profiles_df, lookup, "lineup"
    )
    defending = _lineup_physical_aggregates(
        lineups_df["defending_player_ids"], profiles_df, lookup, "opponent"
    )
    output = pd.concat(
        [lineups_df.reset_index(drop=True), attacking, defending], axis=1
    )
    output["delta_aerial"] = (
        output["lineup_avg_aerial_dominance"]
        - output["opponent_avg_aerial_dominance"]
    )
    output["delta_pressing"] = (
        output["lineup_max_pressing_rate"]
        - output["opponent_max_pressing_rate"]
    )
    output["delta_recovery"] = (
        output["lineup_min_recovery_speed"]
        - output["opponent_min_recovery_speed"]
    )
    return output


def build_lineup_physicality_features(
    lineups_df: pd.DataFrame,
    profiles_df: pd.DataFrame,
) -> pd.DataFrame:
    """Return the three requested physical aggregates for each lineup."""

    empty_synergy = pd.DataFrame(
        columns=["row_player_id", "column_player_id", "synergy_score"]
    )
    output = build_lineup_matchup_features(
        lineups_df, profiles_df, empty_synergy
    )
    return output[
        [
            "possession_uid",
            "lineup_avg_aerial_dominance",
            "lineup_max_pressing_rate",
            "lineup_min_recovery_speed",
        ]
    ]


def build_lineup_chemistry_features(
    lineups_df: pd.DataFrame,
    profiles_df: pd.DataFrame,
    synergy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Return overall and weakest-link chemistry for each lineup."""

    output = build_lineup_matchup_features(
        lineups_df, profiles_df, synergy_df
    )
    return output[
        [
            "possession_uid",
            "lineup_overall_lineup_chemistry_score",
            "lineup_weakest_link_chemistry",
        ]
    ]


def compute_matchup_physical_deltas(features_df: pd.DataFrame) -> pd.DataFrame:
    """Compute attacking-minus-defending physical mismatches."""

    output = features_df.copy()
    output["delta_aerial"] = (
        output["lineup_avg_aerial_dominance"]
        - output["opponent_avg_aerial_dominance"]
    )
    output["delta_pressing"] = (
        output["lineup_max_pressing_rate"]
        - output["opponent_max_pressing_rate"]
    )
    output["delta_recovery"] = (
        output["lineup_min_recovery_speed"]
        - output["opponent_min_recovery_speed"]
    )
    return output


@dataclass
class EmpiricalHurdleModel:
    """Regularized style/team hurdle used when the stored model is unavailable."""

    prior_possessions: float = 100.0
    conditional_prior_events: float = 10.0
    global_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    team_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    physical_net_model: Ridge | None = None
    transition_physical_model: Ridge | None = None
    transition_bundle: dict[str, object] | None = None
    physical_columns: tuple[str, ...] = (
        "lineup_avg_aerial_dominance",
        "lineup_max_pressing_rate",
        "lineup_min_recovery_speed",
        "lineup_overall_lineup_chemistry_score",
        "lineup_weakest_link_chemistry",
        "delta_aerial",
        "delta_pressing",
        "delta_recovery",
    )

    def fit(self, recommendation_df: pd.DataFrame) -> "EmpiricalHurdleModel":
        data = recommendation_df.copy()
        if CANONICAL_TRANSITION_TARGET not in data:
            raise ValueError(
                f"Missing canonical transition target: {CANONICAL_TRANSITION_TARGET}"
            )
        grouped = data.groupby("attacking_style", observed=True)
        global_rows = []
        for style, group in grouped:
            shot_events = float(group["shot"].sum())
            transition_events = float(group[CANONICAL_TRANSITION_TARGET].sum())
            global_rows.append(
                {
                    "attacking_style": style,
                    "attack_probability": shot_events / len(group),
                    "attack_conditional_xg": (
                        group["xg_generated"].sum() / max(shot_events, 1)
                    ),
                    "transition_probability": transition_events / len(group),
                    "transition_conditional_xg": (
                        group["opponent_transition_xg"].sum()
                        / max(transition_events, 1)
                    ),
                }
            )
        self.global_table = pd.DataFrame(global_rows).set_index(
            "attacking_style"
        )
        team_rows = []
        for (team, style), group in data.groupby(
            ["team", "attacking_style"], observed=True
        ):
            prior = self.global_table.loc[style]
            n = len(group)
            shots = float(group["shot"].sum())
            transitions = float(group[CANONICAL_TRANSITION_TARGET].sum())
            team_rows.append(
                {
                    "team": team,
                    "attacking_style": style,
                    "attack_probability": (
                        shots
                        + self.prior_possessions * prior.attack_probability
                    )
                    / (n + self.prior_possessions),
                    "attack_conditional_xg": (
                        group["xg_generated"].sum()
                        + self.conditional_prior_events
                        * prior.attack_conditional_xg
                    )
                    / (shots + self.conditional_prior_events),
                    "transition_probability": (
                        transitions
                        + self.prior_possessions
                        * prior.transition_probability
                    )
                    / (n + self.prior_possessions),
                    "transition_conditional_xg": (
                        group["opponent_transition_xg"].sum()
                        + self.conditional_prior_events
                        * prior.transition_conditional_xg
                    )
                    / (transitions + self.conditional_prior_events),
                }
            )
        self.team_table = pd.DataFrame(team_rows).set_index(
            ["team", "attacking_style"]
        )
        return self

    def attach_transition_bundle(
        self, bundle: dict[str, object]
    ) -> "EmpiricalHurdleModel":
        """Use the calibrated canonical classifier for transition probability."""

        if bundle.get("target") != CANONICAL_TRANSITION_TARGET:
            raise ValueError(
                f"Bundle target {bundle.get('target')!r} does not match "
                f"{CANONICAL_TRANSITION_TARGET!r}"
            )
        self.transition_bundle = bundle
        return self

    def fit_physical_adjustments(
        self, joined_df: pd.DataFrame
    ) -> "EmpiricalHurdleModel":
        features = joined_df[list(self.physical_columns)].fillna(0)
        baseline = self.predict(joined_df[["team", "attacking_style"]])
        residual = joined_df["net_xg_15"].to_numpy() - baseline["expected_net_xg"]
        self.physical_net_model = Ridge(alpha=100.0).fit(features, residual)
        transition_residual = (
            joined_df["opponent_transition_xg"].to_numpy()
            - baseline["expected_transition_xg"]
        )
        self.transition_physical_model = Ridge(alpha=100.0).fit(
            features, transition_residual
        )
        return self

    def predict(self, contexts: pd.DataFrame) -> pd.DataFrame:
        """Predict attack, transition, and net xG for context/style rows."""

        rows = []
        for row in contexts.itertuples(index=False):
            team = str(getattr(row, "team"))
            style = str(getattr(row, "attacking_style"))
            key = (team, style)
            if key in self.team_table.index:
                values = self.team_table.loc[key]
            else:
                values = self.global_table.loc[style]
            record = {
                "attack_probability": float(values.attack_probability),
                "attack_conditional_xg": float(values.attack_conditional_xg),
                "transition_probability": float(values.transition_probability),
                "transition_conditional_xg": float(
                    values.transition_conditional_xg
                ),
            }
            record["expected_attack_xg"] = (
                record["attack_probability"] * record["attack_conditional_xg"]
            )
            record["expected_transition_xg"] = (
                record["transition_probability"]
                * record["transition_conditional_xg"]
            )
            record["expected_net_xg"] = (
                record["expected_attack_xg"]
                - record["expected_transition_xg"]
            )
            rows.append(record)
        output = pd.DataFrame(rows, index=contexts.index)
        if self.transition_bundle is not None:
            feature_names = list(self.transition_bundle["feature_names"])
            missing = sorted(set(feature_names) - set(contexts.columns))
            prediction_context = contexts.copy()
            defaults = dict(self.transition_bundle.get("feature_defaults", {}))
            for column in missing:
                if column not in defaults:
                    raise ValueError(
                        "Simulation context is missing classifier feature with "
                        f"no serialized default: {column}"
                    )
                prediction_context[column] = defaults[column]
            raw = self.transition_bundle["model"].predict_proba(
                prediction_context[feature_names]
            )[:, 1]
            calibrator = self.transition_bundle["calibrator"]
            method = str(calibrator["method"])
            model = calibrator["model"]
            clipped = np.clip(raw, 1e-6, 1 - 1e-6)
            if method == "isotonic":
                calibrated = model.predict(raw)
            else:
                calibration_features = (
                    np.log(clipped / (1 - clipped)).reshape(-1, 1)
                    if method == "platt"
                    else np.column_stack(
                        [np.log(clipped), -np.log1p(-clipped)]
                    )
                )
                calibrated = model.predict_proba(calibration_features)[:, 1]
            threshold = self.transition_bundle.get("threshold")
            output["calibrated_transition_probability"] = calibrated
            output["transition_threshold"] = (
                np.nan if threshold is None else float(threshold)
            )
            output["transition_probability"] = (
                np.zeros(len(calibrated))
                if threshold is None
                else np.where(calibrated >= float(threshold), calibrated, 0.0)
            )
            output["expected_transition_xg"] = (
                output["transition_probability"]
                * output["transition_conditional_xg"]
            )
            output["expected_net_xg"] = (
                output["expected_attack_xg"]
                - output["expected_transition_xg"]
            )
        else:
            output["calibrated_transition_probability"] = output[
                "transition_probability"
            ]
            output["transition_threshold"] = np.nan
        if self.physical_net_model is not None and set(
            self.physical_columns
        ).issubset(contexts.columns):
            physical = contexts[list(self.physical_columns)].fillna(0)
            adjustment = self.physical_net_model.predict(physical)
            output["physical_net_adjustment"] = adjustment
            output["expected_net_xg"] += adjustment
        else:
            output["physical_net_adjustment"] = 0.0
        return output

    def transition_after_pressing_boost(
        self, contexts: pd.DataFrame, boost: float = 0.15
    ) -> tuple[np.ndarray, np.ndarray]:
        baseline = self.predict(contexts)["expected_transition_xg"].to_numpy()
        if self.transition_physical_model is None:
            return baseline, baseline
        boosted = contexts[list(self.physical_columns)].fillna(0).copy()
        boosted["lineup_max_pressing_rate"] *= 1 + boost
        delta = self.transition_physical_model.predict(boosted) - (
            self.transition_physical_model.predict(
                contexts[list(self.physical_columns)].fillna(0)
            )
        )
        # Sensitivity is a risk-reduction scenario; adverse learned association
        # is treated conservatively as no benefit.
        after = np.clip(baseline + np.minimum(delta, 0), 0, None)
        return baseline, after


def simulate_tactical_style_outcomes(
    possession_context: pd.DataFrame,
    hurdle_model: EmpiricalHurdleModel,
) -> pd.DataFrame:
    """Vectorize all three tactical counterfactuals per possession."""

    repeated = possession_context.loc[
        possession_context.index.repeat(len(ATTACKING_STYLES))
    ].reset_index(drop=True)
    repeated["simulated_style"] = np.tile(
        ATTACKING_STYLES, len(possession_context)
    )
    repeated["attacking_style"] = repeated["simulated_style"]
    predictions = hurdle_model.predict(repeated)
    baseline, boosted = hurdle_model.transition_after_pressing_boost(repeated)
    output_columns = [
        "possession_uid",
        "match_id",
        "team",
        "opponent",
        "actual_style",
        "simulated_style",
    ]
    output = repeated[output_columns].copy()
    for column in predictions:
        output[column] = predictions[column].to_numpy()
    output["baseline_transition_xg"] = baseline
    output["transition_xg_after_pressing_boost"] = boosted
    output["pressing_boost_transition_xg_reduction"] = baseline - boosted
    return output


def simulate_physicality_boost_sensitivity(
    possession_context: pd.DataFrame,
    hurdle_model: EmpiricalHurdleModel,
    *,
    pressing_boost: float = 0.15,
) -> pd.DataFrame:
    """Measure transition-xG reduction under a pressing-intensity boost."""

    baseline, boosted = hurdle_model.transition_after_pressing_boost(
        possession_context, boost=pressing_boost
    )
    return pd.DataFrame(
        {
            "baseline_transition_xg": baseline,
            "transition_xg_after_pressing_boost": boosted,
            "transition_xg_reduction": baseline - boosted,
        },
        index=possession_context.index,
    )


def roster_lineup_features(
    player_ids: Sequence[int],
    profiles: pd.DataFrame,
    synergy_lookup: dict[tuple[int, int], float],
) -> dict[str, float]:
    """Aggregate a roster into the physical columns used by the hurdle model."""

    indexed = profiles.set_index("player_id").reindex(player_ids)
    pair_scores = [
        synergy_lookup.get((int(left), int(right)), 0.0)
        for left, right in itertools.combinations(player_ids, 2)
    ]
    return {
        "lineup_avg_aerial_dominance": float(
            indexed["aerial_dominance_index"].fillna(0).mean()
        ),
        "lineup_max_pressing_rate": float(
            indexed["pressing_intensity_index"].fillna(0).max()
        ),
        "lineup_min_recovery_speed": float(
            indexed["speed_recovery_index"].fillna(0).min()
        ),
        "lineup_overall_lineup_chemistry_score": float(
            np.mean(pair_scores) if pair_scores else 0
        ),
        "lineup_weakest_link_chemistry": float(
            np.min(pair_scores) if pair_scores else 0
        ),
        "delta_aerial": 0.0,
        "delta_pressing": 0.0,
        "delta_recovery": 0.0,
    }


def _match_bootstrap_substitution_interval(
    components_df: pd.DataFrame,
    team: str,
    starter: int,
    substitute: int,
    model_gain: float,
    *,
    samples: int = 500,
) -> tuple[float, float]:
    """Add match-level player-value variability to a modeled swap estimate."""

    columns = [
        "match_id",
        "player_id",
        "minutes",
        "xg_sum",
    ]
    team_rows = components_df.loc[
        components_df["team"].eq(team) & components_df["player_id"].isin([starter, substitute]),
        columns,
    ].copy()
    if team_rows.empty or team_rows["match_id"].nunique() < 2:
        return model_gain, model_gain
    minutes = team_rows["minutes"].clip(lower=1)
    # Raw xG is retained only as a descriptive match-level uncertainty signal;
    # it is not part of the unified VAEP+xT player rating.
    team_rows["match_value_p90"] = 90 * team_rows["xg_sum"] / minutes
    pivot = team_rows.pivot_table(
        index="match_id",
        columns="player_id",
        values="match_value_p90",
        aggfunc="sum",
        fill_value=0,
    )
    difference = (
        pivot.get(substitute, pd.Series(0.0, index=pivot.index))
        - pivot.get(starter, pd.Series(0.0, index=pivot.index))
    ).to_numpy()
    if len(difference) < 2:
        return model_gain, model_gain
    # Scale the observed role-value difference to the possession-level Net xG
    # range while preserving match-to-match sign and uncertainty.
    centered = 0.01 * (difference - np.mean(difference))
    rng = np.random.default_rng((starter * 1009 + substitute * 9176) % (2**32))
    draws = model_gain + np.array(
        [rng.choice(centered, size=len(centered), replace=True).mean() for _ in range(samples)]
    )
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def _formation_constrained_selection(squad: pd.DataFrame) -> pd.DataFrame:
    """Select eleven players while preserving a plausible positional skeleton."""

    requirements = {
        "Goalkeeper": 1,
        "Center Back": 2,
        "Fullback/Wingback": 2,
        "Defensive Midfield": 1,
        "Central/Wide Midfield": 2,
        "Attacking Midfield/Wing": 1,
        "Forward": 1,
    }
    chosen: list[int] = []
    for group, count in requirements.items():
        candidates = squad[
            squad["position_group"].eq(group) & ~squad.index.isin(chosen)
        ].nlargest(count, "optimization_score")
        chosen.extend(int(index) for index in candidates.index)
    remaining = squad[~squad.index.isin(chosen)].nlargest(
        max(11 - len(chosen), 0), "optimization_score"
    )
    chosen.extend(int(index) for index in remaining.index)
    return squad.loc[chosen[:11]].sort_values(
        "optimization_score", ascending=False
    )


def simulate_starter_replacement_impact(
    components_df: pd.DataFrame,
    profiles_df: pd.DataFrame,
    synergy_df: pd.DataFrame,
    hurdle_model: EmpiricalHurdleModel,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Evaluate every starter/bench swap and derive optimized elevens."""

    totals = aggregate_player_components(components_df).sort_values(
        ["team", "minutes"], ascending=[True, False]
    )
    lookup = {
        (int(row.row_player_id), int(row.column_player_id)): float(
            row.synergy_score
        )
        for row in synergy_df.itertuples(index=False)
    }
    profile_lookup = profiles_df.set_index("player_id")
    records = []
    suppression_records = []
    optimized_rows = []
    for team, squad in totals.groupby("team", sort=True):
        squad = squad.sort_values("minutes", ascending=False)
        starters = squad.head(11)["player_id"].astype(int).tolist()
        bench = squad.iloc[11:]["player_id"].astype(int).tolist()
        base_features = roster_lineup_features(
            starters, profiles_df, lookup
        )
        style_scores = []
        for style in ATTACKING_STYLES:
            context = pd.DataFrame(
                [{"team": team, "attacking_style": style, **base_features}]
            )
            style_scores.append(
                (style, float(hurdle_model.predict(context).expected_net_xg.iloc[0]))
            )
        optimal_style, baseline_value = max(style_scores, key=lambda item: item[1])
        team_records = []
        for starter in starters:
            for substitute in bench:
                starter_position = str(profile_lookup.loc[starter, "position_group"])
                substitute_position = str(
                    profile_lookup.loc[substitute, "position_group"]
                )
                substitute_minutes = float(profile_lookup.loc[substitute, "minutes"])
                if starter_position != substitute_position:
                    suppression_records.append(
                        {
                            "team": team,
                            "starter_player_id": starter,
                            "bench_player_id": substitute,
                            "reason_code": REASON_POSITIONAL_INCOMPATIBILITY,
                            "expected_net_xg_gain": np.nan,
                            "gain_ci_low": np.nan,
                            "gain_ci_high": np.nan,
                        }
                    )
                    continue
                if substitute_minutes < V4_MIN_PLAYER_MINUTES:
                    suppression_records.append(
                        {
                            "team": team,
                            "starter_player_id": starter,
                            "bench_player_id": substitute,
                            "reason_code": "INSUFFICIENT_MINUTES",
                            "expected_net_xg_gain": np.nan,
                            "gain_ci_low": np.nan,
                            "gain_ci_high": np.nan,
                        }
                    )
                    continue
                candidate = [
                    substitute if player == starter else player
                    for player in starters
                ]
                features = roster_lineup_features(
                    candidate, profiles_df, lookup
                )
                context = pd.DataFrame(
                    [
                        {
                            "team": team,
                            "attacking_style": optimal_style,
                            **features,
                        }
                    ]
                )
                value = float(
                    hurdle_model.predict(context).expected_net_xg.iloc[0]
                )
                gain = value - baseline_value
                if gain <= MIN_SUBSTITUTION_NET_XG_GAIN:
                    suppression_records.append(
                        {
                            "team": team,
                            "starter_player_id": starter,
                            "bench_player_id": substitute,
                            "reason_code": REASON_GAIN_BELOW_THRESHOLD,
                            "expected_net_xg_gain": gain,
                            "gain_ci_low": np.nan,
                            "gain_ci_high": np.nan,
                        }
                    )
                    continue
                interval_low, interval_high = _match_bootstrap_substitution_interval(
                    components_df,
                    team,
                    starter,
                    substitute,
                    gain,
                )
                if interval_low <= 0:
                    suppression_records.append(
                        {
                            "team": team,
                            "starter_player_id": starter,
                            "bench_player_id": substitute,
                            "reason_code": REASON_CI_OVERLAPS_ZERO,
                            "expected_net_xg_gain": gain,
                            "gain_ci_low": interval_low,
                            "gain_ci_high": interval_high,
                        }
                    )
                    continue
                team_records.append(
                    {
                        "team": team,
                        "starter_player_id": starter,
                        "starter_player": profile_lookup.loc[
                            starter, "player"
                        ],
                        "bench_player_id": substitute,
                        "bench_player": profile_lookup.loc[
                            substitute, "player"
                        ],
                        "optimal_style": optimal_style,
                        "baseline_expected_net_xg": baseline_value,
                        "substitution_expected_net_xg": value,
                        "expected_net_xg_gain": gain,
                        "gain_ci_low": interval_low,
                        "gain_ci_high": interval_high,
                        "recommended_substitution_minute": (
                            60 if substitute_minutes >= 180 else 70
                        ),
                        "position_compatible": True,
                    }
                )
        team_frame = pd.DataFrame(team_records)
        if not team_frame.empty:
            average_by_starter = team_frame.groupby(
                "starter_player_id"
            )["substitution_expected_net_xg"].mean()
            team_frame["starter_war_vs_average_bench"] = team_frame[
                "starter_player_id"
            ].map(baseline_value - average_by_starter)
            best_index = team_frame["expected_net_xg_gain"].idxmax()
            team_frame["is_best_team_substitution"] = False
            team_frame.loc[best_index, "is_best_team_substitution"] = True
            records.extend(team_frame.to_dict("records"))
        squad_profile = profile_lookup.reindex(squad["player_id"].astype(int))
        centrality = []
        squad_ids = squad["player_id"].astype(int).tolist()
        for player in squad_ids:
            scores = [
                lookup.get((player, other), 0.0)
                for other in squad_ids
                if other != player
            ]
            centrality.append(float(np.mean(scores) if scores else 0))
        squad = squad.copy()
        squad["chemistry_centrality"] = centrality
        value_column = "player_evaluation_score"
        squad["player_value"] = squad["player_id"].map(
            profile_lookup[value_column]
        ).fillna(0)
        squad["optimization_score"] = (
            squad["player_value"].rank(pct=True)
            + squad["chemistry_centrality"].rank(pct=True)
            + squad["minutes"].rank(pct=True)
        )
        constrained_lineup = _formation_constrained_selection(squad)
        for rank, row in enumerate(
            constrained_lineup.itertuples(index=False), start=1
        ):
            optimized_rows.append(
                {
                    "team": team,
                    "rank": rank,
                    "player_id": int(row.player_id),
                    "player": row.player,
                    "position_group": row.position_group,
                    "optimization_score": float(row.optimization_score),
                }
            )
    return (
        pd.DataFrame(records),
        pd.DataFrame(optimized_rows),
        pd.DataFrame(suppression_records),
    )


def calculate_expected_vs_actual_deltas(
    tactical_simulations: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute possession EvA and a 32-team aggregate."""

    simulations = tactical_simulations.copy()
    best = simulations.loc[
        simulations.groupby("possession_uid")["expected_net_xg"].idxmax()
    ][["possession_uid", "simulated_style", "expected_net_xg"]].rename(
        columns={
            "simulated_style": "optimal_style",
            "expected_net_xg": "optimal_expected_net_xg",
        }
    )
    actual = simulations[
        simulations["simulated_style"].eq(simulations["actual_style"])
    ][
        [
            "possession_uid",
            "team",
            "opponent",
            "actual_style",
            "expected_net_xg",
        ]
    ].rename(columns={"expected_net_xg": "actual_expected_net_xg"})
    detail = actual.merge(best, on="possession_uid", validate="one_to_one")
    detail["raw_eva_gap"] = (
        detail["optimal_expected_net_xg"]
        - detail["actual_expected_net_xg"]
    ).clip(lower=0)
    meaningful = detail["raw_eva_gap"].gt(MIN_SUBSTITUTION_NET_XG_GAIN)
    detail.loc[~meaningful, "optimal_style"] = "No meaningful change"
    detail.loc[~meaningful, "optimal_expected_net_xg"] = detail.loc[
        ~meaningful, "actual_expected_net_xg"
    ]
    detail["eva_gap"] = np.where(meaningful, detail["raw_eva_gap"], 0.0)
    detail["recommendation_is_meaningful"] = meaningful
    detail["tactical_reason_code"] = np.where(
        meaningful, "SUPPORTED_CHANGE", REASON_GAIN_BELOW_THRESHOLD
    )
    summary = (
        detail.groupby("team", as_index=False)
        .agg(
            possessions=("possession_uid", "size"),
            total_wasted_net_xg=("eva_gap", "sum"),
            mean_eva_gap=("eva_gap", "mean"),
            actual_expected_net_xg=("actual_expected_net_xg", "sum"),
            optimal_expected_net_xg=("optimal_expected_net_xg", "sum"),
        )
    )
    preferred = (
        detail.groupby(["team", "optimal_style"]).size().rename("count").reset_index()
        .sort_values(["team", "count"], ascending=[True, False])
        .drop_duplicates("team")
        .rename(columns={"optimal_style": "most_common_optimal_style"})
    )
    summary = summary.merge(
        preferred[["team", "most_common_optimal_style"]],
        on="team",
        validate="one_to_one",
    )
    return detail, summary


def identify_recurrent_tactical_mistakes(
    eva_detail: pd.DataFrame,
    defensive_styles: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate wasted net xG by team and opponent defensive shape."""

    mapping = defensive_styles[
        ["possession_uid", "defensive_style"]
    ].drop_duplicates("possession_uid")
    detail = eva_detail.merge(mapping, on="possession_uid", how="left")
    detail["defensive_style"] = detail["defensive_style"].fillna("Unknown")
    return (
        detail.groupby(
            ["team", "defensive_style", "actual_style", "optimal_style"],
            as_index=False,
        )
        .agg(
            possessions=("possession_uid", "size"),
            wasted_net_xg=("eva_gap", "sum"),
            mean_eva_gap=("eva_gap", "mean"),
        )
        .sort_values(["team", "wasted_net_xg"], ascending=[True, False])
    )
