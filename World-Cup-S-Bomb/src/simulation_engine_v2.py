"""Vectorized physicality, chemistry, hurdle, and simulation primitives."""

from __future__ import annotations

import ast
import itertools
from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


ATTACKING_STYLES = (
    "Patient Build-up",
    "Short Under Pressure",
    "Direct Long Play",
)
CANONICAL_TRANSITION_TARGET = "transition_conceded"
MIN_SUBSTITUTION_NET_XG_GAIN = 0.0050
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
        "pass_progression_per_pass": 2,
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
    profiles["pass_progression_per_pass"] = _safe_rate(
        profiles["pass_progression_sum"], profiles["passes"]
    )
    for metric in (
        "aerial_dominance_index",
        "pressing_intensity_index",
        "speed_recovery_index",
    ):
        profiles[f"{metric}_percentile"] = profiles[metric].rank(pct=True) * 100
    profiles["net_xg_contribution_p90"] = (
        profiles["xg_p90"]
        + 0.015 * profiles["key_passes_p90"]
        + 0.004 * profiles["progressive_passes_p90"]
        + 0.003 * profiles["progressive_carries_p90"]
        + 0.002 * profiles["interceptions_p90"]
        - 0.002 * profiles["turnovers_p90"]
    )
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
        "key_passes",
        "progressive_passes",
        "progressive_carries",
        "interceptions",
        "turnovers",
    ]
    team_rows = components_df.loc[
        components_df["team"].eq(team) & components_df["player_id"].isin([starter, substitute]),
        columns,
    ].copy()
    if team_rows.empty or team_rows["match_id"].nunique() < 2:
        return model_gain, model_gain
    minutes = team_rows["minutes"].clip(lower=1)
    team_rows["match_value_p90"] = 90 * (
        team_rows["xg_sum"]
        + 0.015 * team_rows["key_passes"]
        + 0.004 * team_rows["progressive_passes"]
        + 0.003 * team_rows["progressive_carries"]
        + 0.002 * team_rows["interceptions"]
        - 0.002 * team_rows["turnovers"]
    ) / minutes
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
) -> tuple[pd.DataFrame, pd.DataFrame]:
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
                if starter_position != substitute_position or substitute_minutes < 45:
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
                    continue
                interval_low, interval_high = _match_bootstrap_substitution_interval(
                    components_df,
                    team,
                    starter,
                    substitute,
                    gain,
                )
                if interval_low <= 0:
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
        squad["player_value"] = squad["player_id"].map(
            profile_lookup["net_xg_contribution_p90"]
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
    return pd.DataFrame(records), pd.DataFrame(optimized_rows)


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
