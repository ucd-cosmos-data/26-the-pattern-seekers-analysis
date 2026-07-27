"""Leakage-free, fold-local style clustering.

The tournament-wide style clusters (attacking and defensive) are currently fit
once on every possession and then used as features by the outcome models. That
makes the Stage-5 benchmark *transductive*: information from the validation
matches leaks into the clusters the model trains on.

``FoldLocalClusterer`` reproduces the production clustering recipe —
winsorize (1st/99th percentile clip) -> ``StandardScaler`` -> ``KMeans`` — but
fits every step on the training rows only and merely *assigns* held-out rows to
the nearest fitted centroid. Used inside an outer cross-validation loop (see
``scripts/validate_nested_coaching_models.py``) it removes the validation-match
leakage while keeping cluster identities consistent within each fold.

Pure numpy/sklearn (no pandas) so it can be unit-tested without the data stack.
"""

from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class FoldLocalClusterer:
    """Winsorize + standardize + KMeans, all fit on training rows only.

    Parameters mirror the production cluster scripts: 1st/99th percentile
    winsorization, ``StandardScaler``, and ``KMeans`` with a high ``n_init``.
    ``fit`` learns the clip limits, scaler, and centroids from the training
    matrix; ``predict`` applies the *same* learned transform to any rows.
    """

    def __init__(
        self,
        n_clusters: int,
        *,
        winsor_lower: float = 0.01,
        winsor_upper: float = 0.99,
        random_state: int = 42,
        n_init: int = 50,
    ) -> None:
        if n_clusters < 2:
            raise ValueError("n_clusters must be at least 2")
        if not 0.0 <= winsor_lower < winsor_upper <= 1.0:
            raise ValueError("Require 0 <= winsor_lower < winsor_upper <= 1")
        self.n_clusters = n_clusters
        self.winsor_lower = winsor_lower
        self.winsor_upper = winsor_upper
        self.random_state = random_state
        self.n_init = n_init

    def fit(self, matrix: np.ndarray) -> "FoldLocalClusterer":
        matrix = np.asarray(matrix, dtype=float)
        if matrix.ndim != 2:
            raise ValueError("Expected a 2-D feature matrix")
        if len(matrix) < self.n_clusters:
            raise ValueError("Fewer training rows than requested clusters")
        # Clip limits are learned from the training rows only.
        self.lower_ = np.quantile(matrix, self.winsor_lower, axis=0)
        self.upper_ = np.quantile(matrix, self.winsor_upper, axis=0)
        clipped = np.clip(matrix, self.lower_, self.upper_)
        self.scaler_ = StandardScaler().fit(clipped)
        scaled = self.scaler_.transform(clipped)
        self.kmeans_ = KMeans(
            n_clusters=self.n_clusters,
            n_init=self.n_init,
            random_state=self.random_state,
        ).fit(scaled)
        self.cluster_centers_ = self.kmeans_.cluster_centers_
        return self

    def _transform(self, matrix: np.ndarray) -> np.ndarray:
        matrix = np.asarray(matrix, dtype=float)
        clipped = np.clip(matrix, self.lower_, self.upper_)
        return self.scaler_.transform(clipped)

    def predict(self, matrix: np.ndarray) -> np.ndarray:
        """Assign rows to the nearest training-fitted centroid."""
        if not hasattr(self, "kmeans_"):
            raise RuntimeError("FoldLocalClusterer must be fit before predict")
        return self.kmeans_.predict(self._transform(matrix))

    def fit_predict(self, matrix: np.ndarray) -> np.ndarray:
        return self.fit(matrix).predict(matrix)
