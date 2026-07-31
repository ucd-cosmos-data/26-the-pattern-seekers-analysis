"""Evaluation and acceptance gate for the optional attention model."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from numpy.typing import ArrayLike
from scipy.stats import spearmanr
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)

from src.contracts import MetricGateResult, MetricSet


FALLBACK_MESSAGE = (
    "Transformer Attention Model Failed Metric Gate. "
    "Falling back to Role-Aware Layer."
)


def expected_calibration_error(
    truth: ArrayLike,
    probability: ArrayLike,
    *,
    bins: int = 10,
) -> float:
    """Calculate equal-width expected calibration error."""

    target = np.asarray(truth, dtype=int)
    score = np.asarray(probability, dtype=float)
    if len(target) != len(score) or not len(target):
        raise ValueError("Truth and probability must be equal, nonempty arrays")
    if not np.isfinite(score).all() or ((score < 0) | (score > 1)).any():
        raise ValueError("Probabilities must be finite and in [0, 1]")
    edges = np.linspace(0.0, 1.0, bins + 1)
    assignments = np.clip(
        np.digitize(score, edges[1:-1]),
        0,
        bins - 1,
    )
    error = 0.0
    for bin_id in range(bins):
        selected = assignments == bin_id
        if selected.any():
            error += float(selected.mean()) * abs(
                float(target[selected].mean())
                - float(score[selected].mean())
            )
    return float(error)


def probability_metrics(
    truth: ArrayLike,
    probability: ArrayLike,
) -> MetricSet:
    """Return ROC-AUC, ECE, and Brier score for one grouped-OOF task."""

    target = np.asarray(truth, dtype=int)
    score = np.asarray(probability, dtype=float)
    if set(np.unique(target)) != {0, 1}:
        raise ValueError("ROC-AUC requires both target classes")
    return MetricSet(
        roc_auc=float(roc_auc_score(target, score)),
        pr_auc=float(average_precision_score(target, score)),
        expected_calibration_error=expected_calibration_error(target, score),
        brier_score=float(brier_score_loss(target, score)),
        rows=int(len(target)),
        positives=int(target.sum()),
    )


def evaluate_attention_metric_gate(
    truth_by_task: Mapping[str, ArrayLike],
    baseline_probability_by_task: Mapping[str, ArrayLike],
    attention_probability_by_task: Mapping[str, ArrayLike],
    *,
    legacy_ranking: ArrayLike | None = None,
    attention_ranking: ArrayLike | None = None,
    auc_tolerance: float = 0.01,
    ece_tolerance: float = 0.01,
) -> MetricGateResult:
    """Select attention only when every declared task passes the metric gate."""

    tasks = set(truth_by_task)
    if tasks != set(baseline_probability_by_task) or tasks != set(
        attention_probability_by_task
    ):
        raise ValueError("Metric-gate tasks do not align")
    if not {"retrospective", "prospective"} <= tasks:
        raise ValueError(
            "Both retrospective and prospective attention tasks are required"
        )
    results: dict[str, dict[str, MetricSet]] = {}
    decisions: list[bool] = []
    for task in sorted(tasks):
        baseline = probability_metrics(
            truth_by_task[task],
            baseline_probability_by_task[task],
        )
        attention = probability_metrics(
            truth_by_task[task],
            attention_probability_by_task[task],
        )
        results[task] = {
            "baseline": baseline,
            "attention": attention,
        }
        decisions.append(
            attention.roc_auc >= baseline.roc_auc - auc_tolerance
            and attention.expected_calibration_error
            <= baseline.expected_calibration_error + ece_tolerance
        )
    accepted = all(decisions)
    rho: float | None = None
    if legacy_ranking is not None or attention_ranking is not None:
        if legacy_ranking is None or attention_ranking is None:
            raise ValueError("Both rankings are required for Spearman")
        legacy = np.asarray(legacy_ranking, dtype=float)
        challenger = np.asarray(attention_ranking, dtype=float)
        if len(legacy) != len(challenger):
            raise ValueError("Ranking arrays must have equal length")
        rho = float(spearmanr(legacy, challenger).statistic)
    return MetricGateResult(
        accepted=accepted,
        selected_layer=(
            "attention" if accepted else "role_aware_fallback"
        ),
        tasks=results,
        spearman_with_legacy=rho,
        message="" if accepted else FALLBACK_MESSAGE,
    )
