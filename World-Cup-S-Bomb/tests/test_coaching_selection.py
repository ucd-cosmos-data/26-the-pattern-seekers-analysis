"""Unit tests for the imbalance-aware selection helpers.

Pure numpy/sklearn, so they run without the training stack (no pandas/xgboost).
Executable directly (``python3 tests/test_coaching_selection.py``) or via pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.coaching_selection import (  # noqa: E402
    bootstrap_average_precision_ci,
    mark_selection,
    operating_point,
)


def _records() -> list[dict]:
    # Empirical best by PR-AUC is the complex ensemble; a simpler model sits
    # within the tie margin and should win the simplicity-aware selection.
    return [
        {"target": "shot", "timing": "Retrospective", "layout": "L", "model": "ensemble",
         "pr_auc": 0.530, "log_loss": 0.248, "model_complexity": 7, "layout_complexity": 4},
        {"target": "shot", "timing": "Retrospective", "layout": "L", "model": "xgboost",
         "pr_auc": 0.527, "log_loss": 0.249, "model_complexity": 3, "layout_complexity": 4},
        {"target": "shot", "timing": "Retrospective", "layout": "L", "model": "logreg",
         "pr_auc": 0.500, "log_loss": 0.256, "model_complexity": 1, "layout_complexity": 4},
        {"target": "shot", "timing": "Prospective", "layout": "Start Context", "model": "logreg",
         "pr_auc": 0.240, "log_loss": 0.354, "model_complexity": 1, "layout_complexity": 1},
    ]


def test_mark_selection_prefers_simpler_within_margin() -> None:
    marked = mark_selection(_records(), margin=0.005, primary_metric="pr_auc")
    by_model = {r["model"]: r for r in marked if r["timing"] == "Retrospective"}

    # Empirical best is the ensemble (highest PR-AUC)...
    assert by_model["ensemble"]["empirical_best"] is True
    # ...but xgboost is within 0.005 and simpler, so it is selected.
    assert by_model["xgboost"]["within_practical_margin"] is True
    assert by_model["xgboost"]["selected"] is True
    assert by_model["ensemble"]["selected"] is False
    # logreg is outside the margin (0.500 < 0.530 - 0.005) and not selectable.
    assert by_model["logreg"]["within_practical_margin"] is False
    # Selection is confined to the selectable timing.
    assert sum(1 for r in marked if r["selected"]) == 1
    # Deltas are relative to the empirical best.
    assert abs(by_model["ensemble"]["delta_primary_vs_best"]) < 1e-12
    assert by_model["xgboost"]["delta_primary_vs_best"] < 0


def test_operating_point_respects_precision_floor() -> None:
    # Deterministic scores with a known best precision of 2/3 (0.667), reached by
    # taking the top three scores {0, 1, 1}. No threshold can beat that.
    score = np.array(
        [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50]
    )
    truth = np.array([0, 1, 1, 0, 1, 0, 0, 0, 0, 0], dtype=float)

    op = operating_point(truth, score, min_precision=0.50)
    assert op["status"] == "ok"
    assert op["precision"] >= 0.50 - 1e-9
    assert 0.0 < op["recall"] <= 1.0
    assert 0.0 <= op["predicted_positive_rate"] <= 1.0

    # A floor above the achievable 0.667 cannot be met; it is flagged, not faked.
    strict = operating_point(truth, score, min_precision=0.90)
    assert strict["status"] == "min_precision_not_met"

    # No positives at all is reported explicitly rather than crashing.
    empty = operating_point(np.zeros(10), score, min_precision=0.30)
    assert empty["status"] == "no_positives"


def test_bootstrap_ap_ci_brackets_point_estimate() -> None:
    rng = np.random.default_rng(1)
    n = 3000
    truth = (rng.random(n) < 0.2).astype(float)
    score = np.clip(0.2 + 0.4 * truth + rng.normal(0, 0.25, n), 0, 1)
    match_ids = rng.integers(0, 40, size=n)  # 40 matches

    result = bootstrap_average_precision_ci(
        truth, score, match_ids, replicates=400, random_state=7
    )
    expected = average_precision_score(truth, score)
    assert abs(result["pr_auc"] - expected) < 1e-9
    # The point estimate falls inside its own bootstrap interval.
    assert result["pr_auc_ci_low"] <= result["pr_auc"] <= result["pr_auc_ci_high"]
    assert result["pr_auc_ci_high"] > result["pr_auc_ci_low"]


def _run() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")


if __name__ == "__main__":
    _run()
    print("All coaching_selection tests passed.")
