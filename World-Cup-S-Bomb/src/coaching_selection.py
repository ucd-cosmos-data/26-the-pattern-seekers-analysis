"""Imbalance-aware selection and operating-threshold utilities.

These helpers make **average precision (PR-AUC)** the primary model-selection
metric for the rare-positive shot / box_entry outcome models, and report how a
selected model performs at a concrete decision threshold. Under heavy class
imbalance (shot fires ~12% of the time, the next-action targets far less),
ROC-AUC and log loss are optimistic; average precision and precision/recall at
an operating point describe the behaviour that actually matters.

The module deliberately depends only on ``numpy`` and ``scikit-learn`` (no
pandas), so it can be unit-tested directly on out-of-fold prediction arrays
without the heavy training stack. ``scripts/select_coaching_models.py`` builds
plain records / arrays and delegates the tricky numerics here.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
from sklearn.metrics import average_precision_score


def _finite_mask(truth: np.ndarray, probability: np.ndarray) -> np.ndarray:
    return np.isfinite(truth) & np.isfinite(probability)


def match_resample_indices(
    match_ids: np.ndarray,
    replicates: int,
    random_state: int,
    matches: np.ndarray | None = None,
    samples: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(matches, samples)`` for a match-cluster bootstrap.

    Resampling whole matches (with replacement) preserves within-match
    correlation, matching the resampling unit used elsewhere in the selection
    pipeline. Callers may pass a pre-drawn ``matches``/``samples`` pair so the
    average-precision intervals reuse the very same match draws as the
    log-loss / Brier intervals.
    """

    if matches is None:
        matches = np.asarray(sorted(np.unique(match_ids)))
    if samples is None:
        rng = np.random.default_rng(random_state)
        samples = rng.integers(0, len(matches), size=(replicates, len(matches)))
    return matches, samples


def bootstrap_average_precision_ci(
    truth: Sequence[float],
    probability: Sequence[float],
    match_ids: Sequence[Any],
    *,
    replicates: int = 5_000,
    random_state: int = 42,
    matches: np.ndarray | None = None,
    samples: np.ndarray | None = None,
    lower: float = 0.025,
    upper: float = 0.975,
) -> dict[str, float]:
    """Point estimate and bootstrap CI for average precision (PR-AUC).

    Average precision is a set-level metric, so unlike a per-row mean it must be
    recomputed on each resampled match set. Degenerate resamples that contain a
    single class are dropped (average precision is undefined there).
    """

    truth = np.asarray(truth, dtype=float)
    probability = np.asarray(probability, dtype=float)
    match_ids = np.asarray(match_ids)

    keep = _finite_mask(truth, probability)
    truth, probability, match_ids = truth[keep], probability[keep], match_ids[keep]
    if truth.size == 0 or truth.min() == truth.max():
        return {"pr_auc": float("nan"), "pr_auc_ci_low": float("nan"), "pr_auc_ci_high": float("nan")}

    point = float(average_precision_score(truth, probability))
    matches, samples = match_resample_indices(
        match_ids, replicates, random_state, matches, samples
    )
    rows_by_match = {match: np.flatnonzero(match_ids == match) for match in matches}
    ordered_rows = [rows_by_match[match] for match in matches]

    values: list[float] = []
    for draw in samples:
        idx = np.concatenate([ordered_rows[j] for j in draw])
        resampled_truth = truth[idx]
        if resampled_truth.min() == resampled_truth.max():
            continue
        values.append(average_precision_score(resampled_truth, probability[idx]))

    if not values:
        return {"pr_auc": point, "pr_auc_ci_low": float("nan"), "pr_auc_ci_high": float("nan")}
    distribution = np.asarray(values, dtype=float)
    return {
        "pr_auc": point,
        "pr_auc_ci_low": float(np.quantile(distribution, lower)),
        "pr_auc_ci_high": float(np.quantile(distribution, upper)),
    }


def operating_point(
    truth: Sequence[float],
    probability: Sequence[float],
    *,
    min_precision: float = 0.30,
    beta: float = 0.5,
    grid: Sequence[float] | None = None,
) -> dict[str, float | str]:
    """Choose a decision threshold and report precision/recall there.

    The threshold maximises F-beta (beta < 1 favours precision) subject to a
    minimum-precision floor. If no threshold reaches the floor, the best
    unconstrained F-beta threshold is returned with a status flag so callers can
    surface that the floor was not met rather than reporting a silent number.
    """

    truth = np.asarray(truth, dtype=float)
    probability = np.asarray(probability, dtype=float)
    keep = _finite_mask(truth, probability)
    truth, probability = truth[keep], probability[keep]
    if truth.size == 0 or truth.sum() == 0:
        return {"status": "no_positives", "threshold": float("nan")}

    if grid is None:
        grid = np.linspace(0.01, 0.99, 197)
    beta_sq = beta * beta
    base_rate = float(truth.mean())

    candidates: list[dict[str, float]] = []
    for threshold in grid:
        predicted = probability >= threshold
        true_pos = float(np.sum(predicted & (truth == 1)))
        false_pos = float(np.sum(predicted & (truth == 0)))
        false_neg = float(np.sum(~predicted & (truth == 1)))
        precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) else 0.0
        recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) else 0.0
        denom = beta_sq * precision + recall
        f_beta = (1 + beta_sq) * precision * recall / denom if denom else 0.0
        candidates.append(
            {
                "threshold": float(threshold),
                "precision": precision,
                "recall": recall,
                "f_beta": f_beta,
                "predicted_positive_rate": float(predicted.mean()),
            }
        )

    within_floor = [c for c in candidates if c["precision"] >= min_precision]
    if within_floor:
        best = max(within_floor, key=lambda c: c["f_beta"])
        status = "ok"
    else:
        best = max(candidates, key=lambda c: c["f_beta"])
        status = "min_precision_not_met"

    return {
        "status": status,
        "beta": float(beta),
        "min_precision": float(min_precision),
        "base_rate": base_rate,
        **best,
    }


def mark_selection(
    records: Sequence[Mapping[str, Any]],
    *,
    primary_metric: str = "pr_auc",
    margin: float,
    higher_is_better: bool = True,
    complexity_keys: Sequence[str] = ("model_complexity", "layout_complexity"),
    secondary_metric: str = "log_loss",
    secondary_higher_is_better: bool = False,
    selectable_timing: str = "Retrospective",
) -> list[dict[str, Any]]:
    """Flag the empirical best, near-ties, and the parsimonious final pick.

    Returns a copy of ``records`` with ``empirical_best``,
    ``within_practical_margin``, ``delta_primary_vs_best`` and ``selected``
    added. Selection keeps the least-complex model whose primary metric is
    within ``margin`` of the empirical best, matching the existing
    simplicity-aware rule but keyed on the imbalance-aware metric.
    """

    rows = [dict(record) for record in records]
    for row in rows:
        row["empirical_best"] = False
        row["within_practical_margin"] = False
        row["delta_primary_vs_best"] = float("nan")
        row["selected"] = False

    sign = 1.0 if higher_is_better else -1.0

    def group_key(row: Mapping[str, Any]) -> tuple[Any, Any]:
        return (row["target"], row["timing"])

    for key in {group_key(row) for row in rows}:
        group = [row for row in rows if group_key(row) == key]
        best = max(group, key=lambda row: sign * row[primary_metric])
        best_value = best[primary_metric]
        best["empirical_best"] = True
        for row in group:
            row["delta_primary_vs_best"] = row[primary_metric] - best_value
            if higher_is_better:
                row["within_practical_margin"] = row[primary_metric] >= best_value - margin
            else:
                row["within_practical_margin"] = row[primary_metric] <= best_value + margin

    for target in {row["target"] for row in rows}:
        candidates = [
            row
            for row in rows
            if row["target"] == target
            and row["timing"] == selectable_timing
            and row["within_practical_margin"]
        ]
        if not candidates:
            continue
        secondary_sign = 1.0 if secondary_higher_is_better else -1.0

        def sort_key(row: Mapping[str, Any]) -> tuple:
            return (
                *[row[key] for key in complexity_keys],
                -sign * row[primary_metric],
                -secondary_sign * row[secondary_metric],
            )

        winner = min(candidates, key=sort_key)
        winner["selected"] = True

    return rows
