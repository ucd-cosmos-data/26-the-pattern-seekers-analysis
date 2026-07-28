"""Tests for attention acceptance and fallback behavior."""

from __future__ import annotations

import numpy as np

from src.validation.metric_gate import (
    FALLBACK_MESSAGE,
    evaluate_attention_metric_gate,
)


def _truth() -> dict[str, np.ndarray]:
    target = np.array([0, 0, 0, 1, 1, 1])
    return {"retrospective": target, "prospective": target}


def test_attention_gate_accepts_noninferior_calibrated_model() -> None:
    truth = _truth()
    baseline = {
        task: np.array([0.05, 0.1, 0.2, 0.7, 0.8, 0.9])
        for task in truth
    }
    attention = {
        task: np.array([0.04, 0.1, 0.2, 0.72, 0.82, 0.91])
        for task in truth
    }
    result = evaluate_attention_metric_gate(truth, baseline, attention)
    assert result.accepted
    assert result.selected_layer == "attention"
    assert result.message == ""
    assert result.tasks["retrospective"]["attention"].pr_auc == 1.0


def test_attention_gate_falls_back_with_exact_message() -> None:
    truth = _truth()
    baseline = {
        task: np.array([0.05, 0.1, 0.2, 0.7, 0.8, 0.9])
        for task in truth
    }
    failed = {
        task: np.array([0.5, 0.6, 0.4, 0.4, 0.5, 0.6])
        for task in truth
    }
    result = evaluate_attention_metric_gate(truth, baseline, failed)
    assert not result.accepted
    assert result.selected_layer == "role_aware_fallback"
    assert result.message == FALLBACK_MESSAGE
