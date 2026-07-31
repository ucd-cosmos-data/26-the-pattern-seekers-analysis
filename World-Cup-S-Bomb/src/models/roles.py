"""Probabilistic player-role discovery with full model diagnostics."""

from __future__ import annotations

import json
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import PCA
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import RobustScaler

from src.config import RoleDiscoveryConfig
from src.contracts import RoleDiscoveryResult


ROLE_SCORE_COLUMNS = (
    "progression_score",
    "creation_score",
    "finishing_score",
    "pressing_score",
    "defensive_score",
    "ball_security_score",
    "aerial_score",
)

FORBIDDEN_ROLE_FEATURE_TOKENS = (
    "rating",
    "rank",
    "player_name",
    "functional_role",
    "role_cluster",
    "probabilistic_role",
    "minutes",
    "_total",
)


class PlayerRoleFeatureTransformer(BaseEstimator, TransformerMixin):
    """Winsorize numeric role features and append missingness indicators."""

    def __init__(
        self,
        *,
        minimum_non_null_share: float = 0.50,
        include_features: Iterable[str] | None = None,
    ) -> None:
        self.minimum_non_null_share = minimum_non_null_share
        self.include_features = include_features

    def fit(
        self,
        X: pd.DataFrame,
        y: Any = None,
    ) -> "PlayerRoleFeatureTransformer":
        """Fit training-only medians and winsor limits."""

        if not 0.0 < self.minimum_non_null_share <= 1.0:
            raise ValueError("minimum_non_null_share must be in (0, 1]")
        numeric = X.select_dtypes(include=np.number).replace(
            [np.inf, -np.inf],
            np.nan,
        )
        candidates = (
            list(self.include_features)
            if self.include_features is not None
            else list(numeric.columns)
        )
        self.feature_names_in_ = [
            column
            for column in candidates
            if column in numeric
            and column not in {"player_id", "match_id"}
            and not any(
                token in str(column).lower()
                for token in FORBIDDEN_ROLE_FEATURE_TOKENS
            )
            and numeric[column].notna().mean() >= self.minimum_non_null_share
            and numeric[column].nunique(dropna=True) > 1
        ]
        if not self.feature_names_in_:
            raise ValueError("No valid numeric role features were found")
        selected = numeric[self.feature_names_in_]
        self.medians_ = selected.median()
        filled = selected.fillna(self.medians_)
        self.lower_bounds_ = filled.quantile(0.01)
        self.upper_bounds_ = filled.quantile(0.99)
        self.missing_indicator_features_ = [
            column for column in self.feature_names_in_ if selected[column].isna().any()
        ]
        self.output_feature_names_ = [
            *self.feature_names_in_,
            *[
                f"{column}__missing"
                for column in self.missing_indicator_features_
            ],
        ]
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform without converting missing observations to silent zeros."""

        if not hasattr(self, "feature_names_in_"):
            raise RuntimeError("PlayerRoleFeatureTransformer is not fitted")
        selected = X[self.feature_names_in_].apply(
            pd.to_numeric,
            errors="coerce",
        ).replace([np.inf, -np.inf], np.nan)
        missing = selected[self.missing_indicator_features_].isna().astype(float)
        filled = selected.fillna(self.medians_).clip(
            lower=self.lower_bounds_,
            upper=self.upper_bounds_,
            axis="columns",
        )
        if not missing.empty:
            missing.columns = [
                f"{column}__missing" for column in missing.columns
            ]
            filled = pd.concat([filled, missing], axis=1)
        return filled[self.output_feature_names_].to_numpy(dtype=float)

    def get_feature_names_out(
        self,
        input_features: Any = None,
    ) -> np.ndarray:
        """Return fitted output feature names."""

        if not hasattr(self, "output_feature_names_"):
            raise RuntimeError("PlayerRoleFeatureTransformer is not fitted")
        return np.asarray(self.output_feature_names_, dtype=object)


def _normalized_entropy(probabilities: np.ndarray) -> np.ndarray:
    """Return entropy normalized to [0, 1] for the fitted K."""

    safe = np.clip(probabilities, 1e-12, 1.0)
    entropy = -(safe * np.log(safe)).sum(axis=1)
    return entropy / np.log(probabilities.shape[1])


ROLE_DESCRIPTOR_NAMES = {
    "progression_score": "Progressive",
    "creation_score": "Creative",
    "finishing_score": "Finishing",
    "pressing_score": "Pressing",
    "defensive_score": "Defensive",
    "ball_security_score": "Secure",
    "aerial_score": "Aerial",
}

POSITION_ROLE_NAMES = {
    "Goalkeeper": "Goalkeeper",
    "Center Back": "Centre-Back",
    "Fullback/Wingback": "Fullback",
    "Forward": "Forward",
    "Defensive Midfield": "Midfielder",
    "Attacking Midfield/Wing": "Attacker",
    "Central/Wide Midfield": "Midfielder",
}


def build_semantic_role_labels(
    profiles: pd.DataFrame,
    labels: np.ndarray,
) -> dict[int, str]:
    """Name every cluster from its two strongest standardized dimensions."""

    working = profiles.reset_index(drop=True).copy()
    working["_cluster"] = labels
    available = [
        column for column in ROLE_SCORE_COLUMNS if column in working
    ]
    if len(available) < 2:
        raise ValueError("Dynamic role labels require two role dimensions")
    numeric = working[available].apply(pd.to_numeric, errors="coerce")
    means = numeric.mean()
    scales = numeric.std(ddof=0)
    scales = scales.mask(scales.abs().lt(1e-9), 1.0)
    labels_by_cluster: dict[int, str] = {}
    used: set[str] = set()
    for cluster, group in working.groupby("_cluster"):
        position = (
            group["position_group"].mode().iloc[0]
            if "position_group" in group and not group["position_group"].mode().empty
            else "Outfield"
        )
        centroid = group[available].apply(
            pd.to_numeric,
            errors="coerce",
        ).mean()
        z_scores = ((centroid - means) / scales).sort_values(
            ascending=False,
        )
        descriptors = [
            ROLE_DESCRIPTOR_NAMES[column] for column in z_scores.index
        ]
        base = POSITION_ROLE_NAMES.get(str(position), "Outfield Player")
        descriptor_count = 2
        name = f"{'/'.join(descriptors[:descriptor_count])} {base}"
        while name in used and descriptor_count < len(descriptors):
            descriptor_count += 1
            name = f"{'/'.join(descriptors[:descriptor_count])} {base}"
        if name in used:
            name = f"{name} Profile {int(cluster) + 1}"
        used.add(name)
        labels_by_cluster[int(cluster)] = name
    return labels_by_cluster


def _semantic_labels(
    profiles: pd.DataFrame,
    labels: np.ndarray,
) -> dict[int, str]:
    """Backward-compatible wrapper for dynamic semantic labels."""

    return build_semantic_role_labels(profiles, labels)


def fit_probabilistic_roles(
    profiles: pd.DataFrame,
    *,
    config: RoleDiscoveryConfig | None = None,
    feature_names: Iterable[str] | None = None,
) -> RoleDiscoveryResult:
    """Evaluate K and covariance structures, then fit soft GMM roles.

    BIC is the primary selection criterion and AIC is the deterministic
    tie-breaker. Candidates with undersized clusters or failed convergence are
    retained in the diagnostics but are not eligible for selection.
    """

    settings = config or RoleDiscoveryConfig()
    if "player_id" not in profiles:
        raise ValueError("Probabilistic role discovery requires player_id")
    goalkeeper_mask = (
        profiles["position_group"].eq("Goalkeeper")
        if "position_group" in profiles
        else pd.Series(False, index=profiles.index)
    )
    cohort = profiles.loc[~goalkeeper_mask].copy()
    if len(cohort) <= settings.k_max:
        raise ValueError("Too few outfield players for configured role discovery")
    transformer = PlayerRoleFeatureTransformer(
        include_features=feature_names,
    ).fit(cohort)
    raw = transformer.transform(cohort)
    scaler = RobustScaler(quantile_range=(10.0, 90.0)).fit(raw)
    scaled = scaler.transform(raw)
    component_count = min(
        settings.pca_components,
        scaled.shape[1],
        len(cohort) - 1,
    )
    if component_count < 1:
        raise ValueError("Too few players for probabilistic role discovery")
    pca = PCA(
        n_components=component_count,
        random_state=settings.random_state,
    ).fit(scaled)
    matrix = pca.transform(scaled)

    candidates: list[dict[str, Any]] = []
    fitted: dict[tuple[int, str], GaussianMixture] = {}
    for covariance_type in settings.covariance_types:
        for k in range(settings.k_min, settings.k_max + 1):
            record: dict[str, Any] = {
                "k": k,
                "covariance_type": covariance_type,
                "eligible": False,
                "failure": "",
            }
            if k >= len(cohort):
                record["failure"] = "K_NOT_SMALLER_THAN_PLAYER_COUNT"
                candidates.append(record)
                continue
            try:
                model = GaussianMixture(
                    n_components=k,
                    covariance_type=covariance_type,
                    reg_covar=settings.reg_covar,
                    n_init=settings.n_init,
                    max_iter=settings.max_iter,
                    random_state=settings.random_state,
                ).fit(matrix)
                labels = model.predict(matrix)
                counts = np.bincount(labels, minlength=k)
                record.update(
                    {
                        "bic": float(model.bic(matrix)),
                        "aic": float(model.aic(matrix)),
                        "converged": bool(model.converged_),
                        "minimum_cluster_size": int(counts.min()),
                        "silhouette": (
                            float(silhouette_score(matrix, labels))
                            if len(np.unique(labels)) > 1
                            else np.nan
                        ),
                        "davies_bouldin": (
                            float(davies_bouldin_score(matrix, labels))
                            if len(np.unique(labels)) > 1
                            else np.nan
                        ),
                        "calinski_harabasz": (
                            float(calinski_harabasz_score(matrix, labels))
                            if len(np.unique(labels)) > 1
                            else np.nan
                        ),
                    }
                )
                eligible = bool(
                    model.converged_
                    and counts.min() >= settings.minimum_cluster_size
                )
                record["eligible"] = eligible
                if not eligible:
                    record["failure"] = (
                        "NOT_CONVERGED"
                        if not model.converged_
                        else "MINIMUM_CLUSTER_SIZE"
                    )
                else:
                    fitted[(k, covariance_type)] = model
            except (ValueError, np.linalg.LinAlgError) as exc:
                record["failure"] = f"{type(exc).__name__}: {exc}"
            candidates.append(record)

    candidate_metrics = pd.DataFrame(candidates)
    eligible = candidate_metrics.loc[candidate_metrics["eligible"]].copy()
    if eligible.empty:
        raise RuntimeError("No eligible probabilistic-role candidate")
    selected_row = eligible.sort_values(
        ["bic", "aic", "k", "covariance_type"],
        ascending=[True, True, True, True],
    ).iloc[0]
    selected_k = int(selected_row["k"])
    covariance_type = str(selected_row["covariance_type"])
    model = fitted[(selected_k, covariance_type)]
    labels = model.predict(matrix)
    probabilities = model.predict_proba(matrix)
    semantic = _semantic_labels(cohort, labels)
    rng = np.random.default_rng(settings.random_state)
    stability: list[float] = []
    for iteration in range(settings.bootstrap_iterations):
        sample = rng.integers(0, len(matrix), len(matrix))
        bootstrap = GaussianMixture(
            n_components=selected_k,
            covariance_type=covariance_type,
            reg_covar=settings.reg_covar,
            n_init=1,
            max_iter=min(settings.max_iter, 200),
            random_state=settings.random_state + iteration + 1,
        )
        try:
            bootstrap.fit(matrix[sample])
            stability.append(
                float(
                    adjusted_rand_score(
                        labels,
                        bootstrap.predict(matrix),
                    )
                )
            )
        except (ValueError, np.linalg.LinAlgError):
            continue

    assignments = profiles[
        [
            column
            for column in (
                "player_id",
                "player",
                "team",
                "position_group",
                "functional_role",
            )
            if column in profiles
        ]
    ].copy()
    assignments["role_cluster"] = -1
    assignments["probabilistic_role"] = "Goalkeeper"
    assignments["role_entropy"] = 0.0
    assignments["role_max_probability"] = 1.0
    outfield_index = assignments.index[~goalkeeper_mask]
    assignments.loc[outfield_index, "role_cluster"] = labels.astype(int)
    assignments.loc[outfield_index, "probabilistic_role"] = [
        semantic[int(label)] for label in labels
    ]
    assignments.loc[outfield_index, "role_entropy"] = (
        _normalized_entropy(probabilities)
    )
    assignments.loc[outfield_index, "role_max_probability"] = (
        probabilities.max(axis=1)
    )
    for cluster in range(selected_k):
        column = f"role_probability_{cluster + 1:02d}"
        assignments[column] = 0.0
        assignments.loc[outfield_index, column] = probabilities[:, cluster]
    assignments["role_probabilities"] = json.dumps(
        {"Goalkeeper": 1.0},
        sort_keys=True,
    )
    assignments.loc[outfield_index, "role_probabilities"] = [
        json.dumps(
            {
                f"role_{cluster + 1:02d}": float(value)
                for cluster, value in enumerate(row)
            },
            sort_keys=True,
        )
        for row in probabilities
    ]

    diagnostics = {
        "selection_primary": "bic",
        "selection_tie_breaker": "aic",
        "pca_components": int(component_count),
        "pca_explained_variance": float(
            pca.explained_variance_ratio_.sum()
        ),
        "feature_names": transformer.get_feature_names_out().tolist(),
        "role_labels": semantic,
        "goalkeepers_excluded": int(goalkeeper_mask.sum()),
        "stability_method": "player-bootstrap refit; ARI on full cohort",
        "bootstrap_iterations_requested": settings.bootstrap_iterations,
        "bootstrap_iterations_completed": len(stability),
        "bootstrap_ari_median": (
            float(np.median(stability)) if stability else np.nan
        ),
        "bootstrap_ari_p05": (
            float(np.quantile(stability, 0.05)) if stability else np.nan
        ),
    }
    return RoleDiscoveryResult(
        assignments=assignments,
        candidate_metrics=candidate_metrics,
        selected_k=selected_k,
        selected_covariance_type=covariance_type,
        model=model,
        transformer=transformer,
        scaler=scaler,
        pca=pca,
        diagnostics=diagnostics,
    )
