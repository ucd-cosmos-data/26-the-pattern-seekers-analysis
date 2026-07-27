"""Unit tests for leakage-free fold-local clustering.

Pure numpy/sklearn, runnable without the training stack. Executable directly
(``python3 tests/test_fold_local_clustering.py``) or via pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.fold_local_clustering import FoldLocalClusterer  # noqa: E402


def _train_test() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(0)
    # Three well-separated blobs for the training rows.
    centers = np.array([[0, 0], [8, 8], [0, 8]], dtype=float)
    train = np.repeat(centers, 80, axis=0) + rng.normal(0, 0.4, (240, 2))
    # Held-out rows drawn from a *shifted* distribution, so a global fit that
    # saw them would learn different clip limits / scaling than a train-only fit.
    test = rng.normal(20, 1.0, (100, 2))
    return train, test


def test_deterministic() -> None:
    train, _ = _train_test()
    a = FoldLocalClusterer(3, random_state=42).fit_predict(train)
    b = FoldLocalClusterer(3, random_state=42).fit_predict(train)
    assert np.array_equal(a, b)
    assert set(np.unique(a)).issubset(set(range(3)))


def test_predict_independent_of_heldout_rows() -> None:
    # The assignment of a held-out row must not depend on which *other* rows are
    # in the batch handed to predict — it is a pure function of the train fit.
    train, test = _train_test()
    clusterer = FoldLocalClusterer(3, random_state=42).fit(train)

    train_only = clusterer.predict(train)
    combined = clusterer.predict(np.vstack([train, test]))
    assert np.array_equal(train_only, combined[: len(train)])

    # Fitting never consults the held-out rows, so re-fitting on train alone
    # yields identical centroids regardless of the test set.
    refit = FoldLocalClusterer(3, random_state=42).fit(train)
    assert np.allclose(clusterer.cluster_centers_, refit.cluster_centers_)


def test_fold_local_excludes_heldout_statistics() -> None:
    # This is the leakage property: a fold-local fit on train must learn
    # different winsor limits than a "global" fit on train+test, proving the
    # held-out distribution never leaks into the transform.
    train, test = _train_test()
    fold_local = FoldLocalClusterer(3, random_state=42).fit(train)
    global_fit = FoldLocalClusterer(3, random_state=42).fit(np.vstack([train, test]))

    # The shifted test rows push the upper clip limit up under a global fit.
    assert np.all(fold_local.upper_ < global_fit.upper_)


def test_input_validation() -> None:
    train, _ = _train_test()
    for bad_k in (0, 1):
        try:
            FoldLocalClusterer(bad_k)
        except ValueError:
            pass
        else:  # pragma: no cover
            raise AssertionError("n_clusters < 2 should raise")

    try:
        FoldLocalClusterer(3).fit(train[:2])  # fewer rows than clusters
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("too-few-rows should raise")

    try:
        FoldLocalClusterer(3).predict(train)  # predict before fit
    except RuntimeError:
        pass
    else:  # pragma: no cover
        raise AssertionError("predict before fit should raise")


def _run() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")


if __name__ == "__main__":
    _run()
    print("All fold_local_clustering tests passed.")
