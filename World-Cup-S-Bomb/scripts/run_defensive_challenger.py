#!/usr/bin/env python3
"""Build and evaluate the Pass-3 Qatar 2022 defensive challenger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.defensive_challenger import (  # noqa: E402
    CHAMPION_REFERENCE_CORRELATION,
    build_player_match_defensive_samples,
    evaluate_defensive_challengers,
)


DEFAULT_ACTIONS = (
    PROJECT_ROOT / "data/processed/world_cup_spadl_actions.parquet"
)
DEFAULT_EVENTS = PROJECT_ROOT / "notebooks/all_events.csv"
DEFAULT_CONTEXT = (
    PROJECT_ROOT / "data/interim/world_cup_player_match_components.csv"
)
DEFAULT_CHAMPION = (
    PROJECT_ROOT
    / "results/diagnostics/ranking_repair/champion/champion_snapshot.json"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "results/diagnostics/ranking_repair/pass3_defensive_challenger.json"
)


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _json_value(item) for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def _champion_correlation(path: Path) -> float:
    if not path.is_file():
        return CHAMPION_REFERENCE_CORRELATION
    payload = json.loads(path.read_text(encoding="utf-8"))
    return float(
        payload.get("model_metrics", {})
        .get("defense", {})
        .get("correlation", CHAMPION_REFERENCE_CORRELATION)
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    actions = pd.read_parquet(args.actions)
    event_columns = [
        "id",
        "match_id",
        "period",
        "possession",
        "possession_team",
        "duel_type",
        "duel_outcome",
        "clearance_aerial_won",
        "pass_aerial_won",
        "miscontrol_aerial_won",
        "shot_aerial_won",
        "foul_committed_penalty",
        "interception_outcome",
        "ball_recovery_recovery_failure",
    ]
    available = pd.read_csv(args.events, nrows=0).columns
    events = pd.read_csv(
        args.events,
        usecols=[column for column in event_columns if column in available],
        low_memory=False,
    )
    context = pd.read_csv(args.context)
    samples = build_player_match_defensive_samples(
        actions,
        events=events,
        player_context=context,
    )
    evaluation = evaluate_defensive_challengers(
        samples,
        champion_reference_correlation=_champion_correlation(
            args.champion
        ),
        outer_folds=args.outer_folds,
        inner_folds=args.inner_folds,
        bootstrap_draws=args.bootstrap_draws,
        run_ablations=not args.skip_ablations,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            _json_value(evaluation.diagnostics),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    predictions_path = args.output.with_name(
        f"{args.output.stem}_oof_predictions.csv"
    )
    evaluation.oof_predictions.to_csv(predictions_path, index=False)
    samples_path = args.output.with_name(
        f"{args.output.stem}_samples.csv"
    )
    samples.to_csv(samples_path, index=False)
    gate = evaluation.diagnostics["promotion_gate"]
    return {
        "diagnostics": str(args.output),
        "predictions": str(predictions_path),
        "samples": str(samples_path),
        "selected_challenger": evaluation.diagnostics[
            "selected_challenger"
        ],
        "gate_passed": gate["passed"],
        "active_component": gate["active_component"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actions", type=Path, default=DEFAULT_ACTIONS)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--context", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--champion", type=Path, default=DEFAULT_CHAMPION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--outer-folds", type=int, default=5)
    parser.add_argument("--inner-folds", type=int, default=4)
    parser.add_argument("--bootstrap-draws", type=int, default=500)
    parser.add_argument("--skip-ablations", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
