"""Match-disjoint cross-validation helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import GroupKFold


def assert_group_disjoint(
    train_indices: np.ndarray,
    validation_indices: np.ndarray,
    groups: np.ndarray,
) -> None:
    """Raise when a match occurs in both sides of a fold."""

    train_groups = set(groups[train_indices].tolist())
    validation_groups = set(groups[validation_indices].tolist())
    overlap = train_groups & validation_groups
    if overlap:
        raise RuntimeError(f"Group leakage detected: {sorted(overlap)}")


def grouped_oof_predict_proba(
    estimator: Any,
    features: pd.DataFrame | np.ndarray,
    target: np.ndarray,
    match_ids: np.ndarray,
    *,
    folds: int = 5,
    fit_callback: Callable[[Any, np.ndarray, np.ndarray], Any] | None = None,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Produce match-disjoint out-of-fold binary probabilities."""

    matrix = (
        features.to_numpy()
        if isinstance(features, pd.DataFrame)
        else np.asarray(features)
    )
    truth = np.asarray(target, dtype=int)
    groups = np.asarray(match_ids)
    if not (len(matrix) == len(truth) == len(groups)):
        raise ValueError("Grouped-OOF arrays must have equal row counts")
    unique_groups = np.unique(groups)
    if len(unique_groups) < 2:
        raise ValueError("At least two matches are required")
    splitter = GroupKFold(n_splits=min(folds, len(unique_groups)))
    probability: np.ndarray = np.full(len(truth), np.nan, dtype=float)
    audit: list[dict[str, Any]] = []
    for fold, (train, validation) in enumerate(
        splitter.split(matrix, truth, groups)
    ):
        assert_group_disjoint(train, validation, groups)
        fitted = clone(estimator)
        if fit_callback is None:
            fitted.fit(matrix[train], truth[train])
        else:
            fitted = fit_callback(fitted, train, validation)
        probability[validation] = fitted.predict_proba(
            matrix[validation]
        )[:, 1]
        audit.append(
            {
                "fold": fold,
                "train_matches": sorted(set(groups[train].tolist())),
                "validation_matches": sorted(
                    set(groups[validation].tolist())
                ),
                "train_rows": int(len(train)),
                "validation_rows": int(len(validation)),
                "group_overlap": False,
            }
        )
    if not np.isfinite(probability).all():
        raise RuntimeError("Grouped OOF prediction coverage is incomplete")
    return probability, audit
