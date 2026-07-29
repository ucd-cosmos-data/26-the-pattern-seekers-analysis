"""Probabilistic player-role discovery and gated learned valuation.

The module is deliberately independent of the action-level VAEP and xT
estimators.  It consumes their out-of-fold action values, so role experiments
cannot alter the validated probability models.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.spatial import ConvexHull, QhullError
from scipy.stats import spearmanr
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import PCA
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    mean_squared_error,
    silhouette_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.linear_model import Ridge


RANDOM_STATE = 42
ROLE_K_RANGE = range(9, 17)


def _entropy(probabilities: np.ndarray) -> np.ndarray:
    safe = np.clip(probabilities, 1e-12, 1.0)
    return -(safe * np.log(safe)).sum(axis=1)


def _spatial_summary(group: pd.DataFrame) -> pd.Series:
    """Reduce event locations to a compact 2-D spatial fingerprint."""

    points = group[["start_x", "start_y"]].dropna().to_numpy(dtype=float)
    if len(points) == 0:
        return pd.Series(dtype=float)
    x = np.clip(points[:, 0], 0, 120)
    y = np.clip(points[:, 1], 0, 80)
    hist, _, _ = np.histogram2d(
        x, y, bins=(120, 80), range=((0, 120), (0, 80))
    )
    density = gaussian_filter(hist, sigma=3.0)
    density /= max(float(density.sum()), 1.0)
    coarse = density.reshape(12, 10, 8, 10).sum(axis=(1, 3)).ravel()
    occupied = coarse[coarse > 0]
    pitch_entropy = float(-(occupied * np.log(occupied)).sum())
    hull_area = 0.0
    if len(points) >= 3:
        try:
            hull_area = float(ConvexHull(points).volume)
        except QhullError:
            pass
    result: dict[str, float] = {
        "spatial_mean_x": float(x.mean()),
        "spatial_mean_y": float(y.mean()),
        "spatial_std_x": float(x.std()),
        "spatial_std_y": float(y.std()),
        "convex_hull_area": hull_area,
        "occupied_pitch_entropy": pitch_entropy,
        "half_space_share": float(
            (((x >= 60) & (x < 102)) & (
                ((y >= 13.3) & (y < 26.7))
                | ((y > 53.3) & (y <= 66.7))
            )).mean()
        ),
        "zone14_share": float(
            ((x >= 80) & (x < 102) & (y >= 26.7) & (y <= 53.3)).mean()
        ),
        "wide_corridor_share": float(((y < 13.3) | (y > 66.7)).mean()),
        "central_build_up_share": float(
            ((x < 60) & (y >= 26.7) & (y <= 53.3)).mean()
        ),
        "final_third_occupancy": float((x > 80).mean()),
    }
    result.update(
        {f"kde_{index:02d}": float(value) for index, value in enumerate(coarse)}
    )
    return pd.Series(result)


def build_spatial_features(actions: pd.DataFrame) -> pd.DataFrame:
    """Build KDE, zone, hull, and SB360 geometry features by player."""

    required = {"player_id", "start_x", "start_y"}
    missing = required.difference(actions.columns)
    if missing:
        raise ValueError(f"Spatial action columns missing: {sorted(missing)}")
    valid = actions.loc[actions["player_id"].notna()].copy()
    valid["player_id"] = valid["player_id"].astype(int)
    spatial = pd.DataFrame(
        [
            {
                "player_id": int(player_id),
                **_spatial_summary(group).to_dict(),
            }
            for player_id, group in valid.groupby("player_id", sort=False)
        ]
    )
    geometry_columns = [
        "defenders_within_5",
        "nearest_defender_distance",
        "defensive_density",
        "defenders_behind_ball",
    ]
    available = [column for column in geometry_columns if column in valid]
    if available:
        valid["has_360_freeze_frame"] = valid[available].notna().any(axis=1)
        geometry = valid.groupby("player_id", as_index=False).agg(
            mean_defenders_within_5=("defenders_within_5", "mean"),
            mean_nearest_defender_distance=("nearest_defender_distance", "mean"),
            mean_defensive_density=("defensive_density", "mean"),
            mean_defenders_behind_ball=("defenders_behind_ball", "mean"),
            sb360_coverage=("has_360_freeze_frame", "mean"),
        )
        spatial = spatial.merge(geometry, on="player_id", how="left")
    return spatial


def build_passing_network_features(events: pd.DataFrame) -> pd.DataFrame:
    """Build directed passing-network centrality without extra dependencies."""

    required = {
        "match_id",
        "team",
        "type",
        "player_id",
        "pass_recipient_id",
        "pass_outcome",
    }
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(f"Passing-network columns missing: {sorted(missing)}")
    passes = events.loc[
        events["type"].eq("Pass")
        & events["pass_outcome"].isna()
        & events["player_id"].notna()
        & events["pass_recipient_id"].notna()
    ].copy()
    passes["player_id"] = passes["player_id"].astype(int)
    passes["pass_recipient_id"] = passes["pass_recipient_id"].astype(int)
    records: list[dict[str, float | int]] = []
    for (_, _), group in passes.groupby(["match_id", "team"], sort=False):
        players = np.unique(
            np.r_[group["player_id"].to_numpy(), group["pass_recipient_id"].to_numpy()]
        )
        index = {int(player): offset for offset, player in enumerate(players)}
        adjacency = np.zeros((len(players), len(players)), dtype=float)
        for (source, target), count in (
            group.groupby(["player_id", "pass_recipient_id"]).size().items()
        ):
            adjacency[index[int(source)], index[int(target)]] = float(count)
        row_sum = adjacency.sum(axis=1, keepdims=True)
        transition = np.divide(
            adjacency,
            row_sum,
            out=np.full_like(adjacency, 1.0 / max(len(players), 1)),
            where=row_sum > 0,
        )
        pagerank = np.full(len(players), 1.0 / max(len(players), 1))
        for _ in range(100):
            updated = 0.15 / len(players) + 0.85 * transition.T.dot(pagerank)
            if np.max(np.abs(updated - pagerank)) < 1e-10:
                break
            pagerank = updated
        degree = (adjacency > 0).sum(axis=0) + (adjacency > 0).sum(axis=1)
        volume = adjacency.sum(axis=0) + adjacency.sum(axis=1)
        for offset, player in enumerate(players):
            records.append(
                {
                    "player_id": int(player),
                    "network_pagerank": float(pagerank[offset]),
                    "network_degree": float(degree[offset]),
                    "network_pass_volume": float(volume[offset]),
                }
            )
    network = pd.DataFrame(records)
    if network.empty:
        return pd.DataFrame(
            columns=[
                "player_id",
                "network_pagerank",
                "network_degree",
                "network_pass_volume",
            ]
        )
    return network.groupby("player_id", as_index=False).mean(numeric_only=True)


@dataclass
class PlayerRoleFeatureTransformer(BaseEstimator, TransformerMixin):
    """Scikit-learn compatible role-matrix transformer."""

    minimum_non_null_share: float = 0.75

    def fit(self, X: pd.DataFrame, y: Any = None) -> "PlayerRoleFeatureTransformer":
        numeric = X.select_dtypes(include=np.number).replace([np.inf, -np.inf], np.nan)
        self.feature_names_in_ = [
            column
            for column in numeric.columns
            if column != "player_id"
            and numeric[column].notna().mean() >= self.minimum_non_null_share
            and numeric[column].nunique(dropna=True) > 1
        ]
        self.medians_ = numeric[self.feature_names_in_].median()
        filled = numeric[self.feature_names_in_].fillna(self.medians_)
        self.lower_bounds_ = filled.quantile(0.05)
        self.upper_bounds_ = filled.quantile(0.95)
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if not hasattr(self, "feature_names_in_"):
            raise RuntimeError("PlayerRoleFeatureTransformer is not fitted")
        numeric = X[self.feature_names_in_].replace([np.inf, -np.inf], np.nan)
        filled = numeric.fillna(self.medians_)
        return filled.clip(
            lower=self.lower_bounds_,
            upper=self.upper_bounds_,
            axis="columns",
        ).to_numpy(dtype=float)


@dataclass
class ProbabilisticRoleResult:
    """Fitted role discovery outputs and diagnostics."""

    assignments: pd.DataFrame
    model: GaussianMixture
    transformer: PlayerRoleFeatureTransformer
    scaler: RobustScaler
    pca: PCA
    metrics: dict[str, Any]


def _semantic_cluster_labels(
    profiles: pd.DataFrame,
    labels: np.ndarray,
) -> dict[int, str]:
    """Name learned clusters from their observed position/spatial signature."""

    working = profiles.copy()
    working["_cluster"] = labels
    output: dict[int, str] = {}
    for cluster, group in working.groupby("_cluster"):
        position = group["position_group"].mode().iloc[0]
        med = group.median(numeric_only=True)
        if position == "Goalkeeper":
            role = "Goalkeeper"
        elif position == "Center Back":
            role = (
                "Ball-Playing Centre-Back"
                if med.get("progressive_passes_p90", 0) >=
                working["progressive_passes_p90"].median()
                else "Defensive Centre-Back"
            )
        elif position == "Fullback/Wingback":
            role = (
                "Attacking Wingback"
                if med.get("final_third_occupancy", med.get("final_third_share", 0))
                >= working.get("final_third_occupancy", working["final_third_share"]).median()
                else "Two-Way Fullback"
            )
        elif position == "Forward":
            role = (
                "Target Forward"
                if med.get("aerial_dominance_index", 0)
                >= working["aerial_dominance_index"].median()
                else "Mobile Forward"
            )
        elif position == "Attacking Midfield/Wing":
            creative = med.get("key_passes_p90", 0) + med.get(
                "line_breaking_pass_rate", 0
            )
            role = (
                "Roaming Creator"
                if creative >= (
                    working["key_passes_p90"].median()
                    + working["line_breaking_pass_rate"].median()
                )
                else "Progressive Winger"
            )
        elif position == "Defensive Midfield":
            role = (
                "Controlling Midfielder"
                if med.get("progressive_passes_p90", 0)
                >= working["progressive_passes_p90"].median()
                else "Ball-Winning Midfielder"
            )
        else:
            role = (
                "Deep Playmaker"
                if med.get("network_pagerank", 0)
                >= working.get("network_pagerank", pd.Series([0])).median()
                else "Box-to-Box Midfielder"
            )
        output[int(cluster)] = role
    return output


def fit_probabilistic_roles(
    profiles: pd.DataFrame,
    actions: pd.DataFrame,
    events: pd.DataFrame,
    *,
    random_state: int = RANDOM_STATE,
    bootstrap_iterations: int = 500,
) -> ProbabilisticRoleResult:
    """Fit BIC-selected GMM roles and quantify bootstrap stability."""

    spatial = build_spatial_features(actions)
    network = build_passing_network_features(events)
    enriched = profiles.merge(spatial, on="player_id", how="left").merge(
        network, on="player_id", how="left"
    )
    goalkeepers = enriched["position_group"].eq("Goalkeeper")
    outfield = enriched.loc[~goalkeepers].copy()
    # Only rate, spatial, pressure, and graph descriptors belong in role
    # discovery. Tournament totals, minutes, outcomes, valuation fields, and
    # the legacy K-Means label would encode opportunity or the incumbent
    # answer rather than tactical function.
    requested_features = [
        "player_id",
        "aerial_dominance_index",
        "pressing_intensity_index",
        "speed_recovery_index",
        "shots_p90",
        "progressive_carries_p90",
        "dribbles_p90",
        "clearances_p90",
        "progressive_passes_p90",
        "key_passes_p90",
        "crosses_p90",
        "interceptions_p90",
        "turnovers_p90",
        "duel_win_rate",
        "pass_completion",
        "line_breaking_pass_rate",
        "pressure_state_rate",
        "distribution_under_pressure",
        "pass_start_x",
        "pass_start_y",
        "pass_receipt_x",
        "pass_receipt_y",
        "spatial_mean_x",
        "spatial_mean_y",
        "spatial_std_x",
        "spatial_std_y",
        "convex_hull_area",
        "occupied_pitch_entropy",
        "half_space_share",
        "zone14_share",
        "wide_corridor_share",
        "central_build_up_share",
        "final_third_occupancy",
        "mean_defenders_within_5",
        "mean_nearest_defender_distance",
        "mean_defensive_density",
        "mean_defenders_behind_ball",
        "sb360_coverage",
        "network_pagerank",
        "network_degree",
        "network_pass_volume",
    ]
    requested_features.extend(
        column for column in outfield if str(column).startswith("kde_")
    )
    feature_frame = outfield[
        [column for column in requested_features if column in outfield]
    ].copy()
    transformer = PlayerRoleFeatureTransformer().fit(feature_frame)
    raw = transformer.transform(feature_frame)
    scaler = RobustScaler(quantile_range=(10, 90)).fit(raw)
    scaled = scaler.transform(raw)
    # Cap latent dimensionality for 142 tournament players; retaining dozens
    # of weak KDE axes makes covariance estimates unstable and bootstrapping
    # needlessly expensive.
    pca = PCA(
        n_components=min(15, scaled.shape[1], len(outfield) - 1),
        random_state=random_state,
    ).fit(scaled)
    matrix = pca.transform(scaled)
    candidates: list[dict[str, float | int]] = []
    fitted: dict[int, GaussianMixture] = {}
    for k in ROLE_K_RANGE:
        model = GaussianMixture(
            n_components=k,
            covariance_type="tied",
            reg_covar=0.10,
            n_init=10,
            max_iter=500,
            random_state=random_state,
        ).fit(matrix)
        labels = model.predict(matrix)
        counts = np.bincount(labels, minlength=k)
        if counts.min() < 2:
            continue
        fitted[k] = model
        candidates.append(
            {
                "k": k,
                "bic": float(model.bic(matrix)),
                "aic": float(model.aic(matrix)),
                "silhouette": float(silhouette_score(matrix, labels)),
                "davies_bouldin": float(davies_bouldin_score(matrix, labels)),
                "calinski_harabasz": float(
                    calinski_harabasz_score(matrix, labels)
                ),
                "minimum_cluster_size": int(counts.min()),
            }
        )
    if not candidates:
        raise RuntimeError("No valid GMM candidate had at least two players per role")
    candidate_frame = pd.DataFrame(candidates)
    # BIC differences below 50 are weak relative to the large covariance
    # parameter count here. Within that competitive set, prefer the more
    # geometrically separated solution instead of treating the minimum BIC
    # as an absolute oracle.
    competitive = candidate_frame[
        candidate_frame["bic"] <= candidate_frame["bic"].min() + 50.0
    ]
    selected_k = int(
        competitive.sort_values(
            ["silhouette", "bic"], ascending=[False, True]
        ).iloc[0]["k"]
    )
    model = fitted[selected_k]
    labels = model.predict(matrix)
    probabilities = model.predict_proba(matrix)
    rng = np.random.default_rng(random_state)
    stability: list[float] = []
    for iteration in range(bootstrap_iterations):
        sample = rng.integers(0, len(matrix), len(matrix))
        bootstrap = GaussianMixture(
            n_components=selected_k,
            covariance_type="tied",
            reg_covar=0.10,
            n_init=1,
            max_iter=120,
            tol=1e-2,
            random_state=random_state + iteration + 1,
        )
        try:
            bootstrap.fit(matrix[sample])
            stability.append(
                float(adjusted_rand_score(labels, bootstrap.predict(matrix)))
            )
        except ValueError:
            continue
    role_names = _semantic_cluster_labels(outfield, labels)
    assignments = enriched[
        ["player_id", "player", "team", "position_group"]
    ].copy()
    assignments["role_cluster"] = -1
    assignments["probabilistic_role"] = "Goalkeeper"
    assignments["role_entropy"] = 0.0
    assignments["role_max_probability"] = 1.0
    assignments["role_probabilities"] = json.dumps({"Goalkeeper": 1.0})
    outfield_index = assignments.index[~goalkeepers]
    assignments.loc[outfield_index, "role_cluster"] = labels
    assignments.loc[outfield_index, "probabilistic_role"] = [
        role_names[int(label)] for label in labels
    ]
    assignments.loc[outfield_index, "role_entropy"] = _entropy(probabilities)
    assignments.loc[outfield_index, "role_max_probability"] = probabilities.max(
        axis=1
    )
    probability_json = []
    for row in probabilities:
        named: dict[str, float] = {}
        for cluster, value in enumerate(row):
            name = role_names[cluster]
            named[name] = named.get(name, 0.0) + float(value)
        probability_json.append(json.dumps(named, sort_keys=True))
    assignments.loc[outfield_index, "role_probabilities"] = probability_json
    metrics = {
        "selected_k": selected_k,
        "bic": float(model.bic(matrix)),
        "aic": float(model.aic(matrix)),
        "silhouette": float(silhouette_score(matrix, labels)),
        "davies_bouldin": float(davies_bouldin_score(matrix, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(matrix, labels)),
        "bootstrap_iterations_requested": bootstrap_iterations,
        "bootstrap_iterations_completed": len(stability),
        "bootstrap_ari_median": float(np.median(stability)),
        "bootstrap_ari_p05": float(np.quantile(stability, 0.05)),
        "pca_components": int(matrix.shape[1]),
        "pca_explained_variance": float(pca.explained_variance_ratio_.sum()),
        "feature_names": transformer.feature_names_in_,
        "candidates": candidates,
    }
    return ProbabilisticRoleResult(
        assignments=assignments,
        model=model,
        transformer=transformer,
        scaler=scaler,
        pca=pca,
        metrics=metrics,
    )


def evaluate_learned_valuation(
    profiles: pd.DataFrame,
    components: pd.DataFrame,
    actions: pd.DataFrame,
    *,
    random_state: int = RANDOM_STATE,
    bootstrap_iterations: int = 1000,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Challenge the fixed rating with grouped-OOF positive Ridge regression."""

    action_values = actions.loc[actions["player_id"].notna()].copy()
    action_values["player_id"] = action_values["player_id"].astype(int)
    action_values["non_shot_xg"] = np.where(
        ~action_values["type_name"].eq("Shot"),
        action_values["p_scores"],
        0.0,
    )
    match_values = (
        action_values.groupby(["game_id", "player_id"], as_index=False)
        .agg(
            vaep_total=("vaep_value", "sum"),
            xt_total=("xt_value", "sum"),
            total_touches=("touch", "sum"),
            nsxg_total=("non_shot_xg", "sum"),
            xa_total=("xa_value", "sum"),
        )
        .rename(columns={"game_id": "match_id"})
    )
    samples = components.merge(
        match_values, on=["match_id", "player_id"], how="left"
    )
    value_columns = [
        "vaep_total",
        "xt_total",
        "total_touches",
        "nsxg_total",
        "xa_total",
    ]
    samples[value_columns] = samples[value_columns].fillna(0.0)
    samples = samples.loc[samples["minutes"].ge(20)].copy()
    minutes = samples["minutes"].clip(lower=1)
    samples["vaep_total_p90"] = 90 * samples["vaep_total"] / minutes
    samples["vaep_per_touch"] = (
        samples["vaep_total"] / samples["total_touches"].clip(lower=1)
    )
    samples["xt_p90"] = 90 * samples["xt_total"] / minutes
    samples["nsxg_p90"] = 90 * samples["nsxg_total"] / minutes
    samples["chance_creation_target"] = (
        90 * (samples["xg_sum"] + samples["xa_total"]) / minutes
    )
    feature_names = [
        "vaep_total_p90",
        "vaep_per_touch",
        "xt_p90",
        "nsxg_p90",
    ]
    X = samples[feature_names].to_numpy()
    y = samples["chance_creation_target"].to_numpy()
    groups = samples["match_id"].to_numpy()
    baseline = (
        0.50 * samples["vaep_total_p90"]
        + 0.30 * samples["vaep_per_touch"]
        + 0.20 * samples["xt_p90"]
    ).to_numpy()
    best: dict[str, Any] | None = None
    for alpha in (0.01, 0.1, 1.0, 10.0, 100.0):
        prediction = np.zeros(len(samples))
        for train, test in GroupKFold(n_splits=5).split(X, y, groups):
            estimator = make_pipeline(
                StandardScaler(),
                Ridge(alpha=alpha, positive=True),
            )
            estimator.fit(X[train], y[train])
            prediction[test] = estimator.predict(X[test])
        rho = float(spearmanr(prediction, y).statistic)
        record = {
            "alpha": alpha,
            "prediction": prediction,
            "spearman": rho,
            "rmse": float(mean_squared_error(y, prediction) ** 0.5),
        }
        if best is None or rho > best["spearman"]:
            best = record
    assert best is not None
    rng = np.random.default_rng(random_state)
    matches = np.unique(groups)
    differences = []
    for _ in range(bootstrap_iterations):
        sampled_matches = rng.choice(matches, len(matches), replace=True)
        indices = np.concatenate(
            [np.flatnonzero(groups == match) for match in sampled_matches]
        )
        differences.append(
            float(
                spearmanr(best["prediction"][indices], y[indices]).statistic
                - spearmanr(baseline[indices], y[indices]).statistic
            )
        )
    interval = np.quantile(differences, [0.025, 0.975])
    estimator = make_pipeline(
        StandardScaler(),
        Ridge(alpha=float(best["alpha"]), positive=True),
    ).fit(X, y)
    tournament = profiles.copy()
    nsxg = action_values.groupby("player_id")["non_shot_xg"].sum()
    tournament["nsxg_p90"] = (
        90
        * tournament["player_id"].map(nsxg).fillna(0.0)
        / tournament["minutes"].clip(lower=1)
    )
    tournament["learned_rating_raw"] = estimator.predict(
        tournament[feature_names].to_numpy()
    )
    reliability = tournament["minutes"] / (tournament["minutes"] + 450.0)
    prior = tournament.groupby("position_group")[
        "learned_rating_raw"
    ].transform("mean")
    tournament["learned_final_player_rating"] = (
        reliability * tournament["learned_rating_raw"]
        + (1 - reliability) * prior
    )
    tournament["learned_team_rank"] = (
        tournament.groupby("team")["learned_final_player_rating"]
        .rank(method="min", ascending=False)
        .astype(int)
    )
    baseline_rho = float(spearmanr(baseline, y).statistic)
    metrics = {
        "target": "player-match xG plus xA per 90",
        "grouping": "5-fold GroupKFold by match_id",
        "baseline_spearman": baseline_rho,
        "challenger_spearman": float(best["spearman"]),
        "spearman_delta": float(best["spearman"] - baseline_rho),
        "delta_confidence_interval_95": [
            float(interval[0]),
            float(interval[1]),
        ],
        "baseline_rmse": float(mean_squared_error(y, baseline) ** 0.5),
        "challenger_rmse": float(best["rmse"]),
        "selected_alpha": float(best["alpha"]),
        "feature_names": feature_names,
        "coefficients_standardized": estimator[-1].coef_.tolist(),
        "statistically_validated": bool(interval[0] > 0),
    }
    return tournament, metrics
