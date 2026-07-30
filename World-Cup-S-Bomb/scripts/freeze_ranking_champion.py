#!/usr/bin/env python3
"""Freeze the pre-repair ranking champion and its regression diagnostics.

The command is deliberately write-once.  A second invocation verifies the
stored snapshot byte-for-byte and refuses to replace a differing champion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_ROOT = (
    PROJECT_ROOT / "results/diagnostics/ranking_repair/champion"
)
SNAPSHOT_PATH = DIAGNOSTIC_ROOT / "champion_snapshot.json"
SEED = 42

CHAMPION_ARTIFACTS = {
    "player_rankings": (
        PROJECT_ROOT / "results/reports/ranking/player_rankings.csv"
    ),
    "unified_rankings": (
        PROJECT_ROOT
        / "results/reports/ranking/unified_tournament_rankings.csv"
    ),
    "goalkeeper_rankings": (
        PROJECT_ROOT / "results/reports/ranking/goalkeeper_rankings.csv"
    ),
    "model_summary": (
        PROJECT_ROOT / "results/reports/canonical/model_summary.json"
    ),
    "ranking_audit": (
        PROJECT_ROOT / "results/reports/ranking/ranking_audit.json"
    ),
}

SOURCE_DATA = {
    "events": PROJECT_ROOT / "notebooks/all_events.csv",
    "spadl_actions": (
        PROJECT_ROOT / "data/processed/world_cup_spadl_actions.parquet"
    ),
    "player_evaluations": (
        PROJECT_ROOT / "data/processed/player_evaluations.csv"
    ),
    "player_match_components": (
        PROJECT_ROOT
        / "data/interim/world_cup_player_match_components.csv"
    ),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def _spearman(left: pd.Series, right: pd.Series) -> float | None:
    values = pd.DataFrame(
        {
            "left": pd.to_numeric(left, errors="coerce"),
            "right": pd.to_numeric(right, errors="coerce"),
        }
    ).dropna()
    if len(values) < 3:
        return None
    correlation = values["left"].rank().corr(values["right"].rank())
    return None if pd.isna(correlation) else float(correlation)


def _bootstrap_spearman(
    left: pd.Series,
    right: pd.Series,
    *,
    draws: int = 500,
) -> dict[str, float | int | None]:
    values = pd.DataFrame(
        {
            "left": pd.to_numeric(left, errors="coerce"),
            "right": pd.to_numeric(right, errors="coerce"),
        }
    ).dropna()
    if len(values) < 3:
        return {"estimate": None, "ci_low": None, "ci_high": None, "draws": 0}
    rng = np.random.default_rng(SEED)
    correlations: list[float] = []
    for _ in range(draws):
        indices = rng.integers(0, len(values), size=len(values))
        sample = values.iloc[indices]
        value = sample["left"].rank().corr(sample["right"].rank())
        if pd.notna(value):
            correlations.append(float(value))
    return {
        "estimate": _spearman(values["left"], values["right"]),
        "ci_low": float(np.quantile(correlations, 0.025)),
        "ci_high": float(np.quantile(correlations, 0.975)),
        "draws": len(correlations),
    }


def _table_schema(path: Path) -> dict[str, Any]:
    frame = pd.read_csv(path, nrows=100)
    return {
        "columns": frame.columns.tolist(),
        "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
    }


def _score_column(rankings: pd.DataFrame) -> str:
    for column in (
        "Tournament Performance Score",
        "final_player_rating_v2",
        "final_player_rating",
    ):
        if column in rankings:
            return column
    raise ValueError("Champion rankings contain no recognized score")


def _position_column(rankings: pd.DataFrame) -> str:
    for column in ("Position Group", "position_group_360", "position_group"):
        if column in rankings:
            return column
    raise ValueError("Champion rankings contain no recognized position group")


def _rank_column(rankings: pd.DataFrame) -> str:
    for column in ("Global Rank", "global_rank_v2", "global_rank"):
        if column in rankings:
            return column
    raise ValueError("Champion rankings contain no recognized global rank")


def _position_composition(
    rankings: pd.DataFrame,
    rank_column: str,
    position_column: str,
) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = {}
    for top_k in (20, 50, 100):
        rows = rankings.loc[
            pd.to_numeric(rankings[rank_column], errors="coerce").le(top_k)
        ]
        output[str(top_k)] = {
            str(group): int(count)
            for group, count in rows[position_column].value_counts().items()
        }
    return output


def _action_stability(actions: pd.DataFrame) -> dict[str, Any]:
    working = actions.loc[
        actions["player_id"].notna()
        & actions["game_id"].notna()
        & actions["vaep_value"].notna()
    ].copy()
    working["player_id"] = working["player_id"].astype(int)
    player_match = (
        working.groupby(["player_id", "game_id"], as_index=False)["vaep_value"]
        .sum()
        .rename(columns={"vaep_value": "match_value"})
    )
    full = player_match.groupby("player_id")["match_value"].sum()
    full_rank = full.rank(method="average", ascending=False)
    full_top = set(full.nlargest(min(20, len(full))).index)
    correlations: list[float] = []
    top_jaccard: list[float] = []
    for _, match_rows in player_match.groupby("game_id"):
        held_out = full.copy()
        deductions = match_rows.set_index("player_id")["match_value"]
        held_out.loc[deductions.index] = (
            held_out.loc[deductions.index] - deductions
        )
        correlation = full_rank.corr(
            held_out.rank(method="average", ascending=False)
        )
        if pd.notna(correlation):
            correlations.append(float(correlation))
        held_top = set(held_out.nlargest(min(20, len(held_out))).index)
        union = full_top | held_top
        top_jaccard.append(
            float(len(full_top & held_top) / len(union)) if union else 1.0
        )

    matches = sorted(player_match["game_id"].unique().tolist())
    rng = np.random.default_rng(SEED)
    players = full.index.to_numpy()
    rank_draws = np.empty((250, len(players)), dtype=float)
    match_tables = {
        match_id: rows.set_index("player_id")["match_value"]
        for match_id, rows in player_match.groupby("game_id")
    }
    for draw in range(len(rank_draws)):
        sampled = rng.choice(matches, size=len(matches), replace=True)
        totals = pd.Series(0.0, index=players)
        for match_id in sampled:
            values = match_tables[match_id]
            totals.loc[values.index] = totals.loc[values.index] + values
        rank_draws[draw] = totals.rank(
            method="average",
            ascending=False,
        ).to_numpy()
    intervals = pd.DataFrame(
        {
            "player_id": players,
            "rank_ci_low": np.quantile(rank_draws, 0.025, axis=0),
            "rank_median": np.quantile(rank_draws, 0.50, axis=0),
            "rank_ci_high": np.quantile(rank_draws, 0.975, axis=0),
        }
    ).sort_values("rank_median")
    return {
        "leave_one_match_out_rank_spearman": {
            "mean": float(np.mean(correlations)),
            "minimum": float(np.min(correlations)),
            "p05": float(np.quantile(correlations, 0.05)),
        },
        "leave_one_match_out_top20_jaccard": {
            "mean": float(np.mean(top_jaccard)),
            "minimum": float(np.min(top_jaccard)),
        },
        "bootstrap_rank_intervals": intervals.to_dict("records"),
        "bootstrap_match_draws": int(len(rank_draws)),
    }


def build_snapshot() -> dict[str, Any]:
    missing = [
        str(path)
        for path in (*CHAMPION_ARTIFACTS.values(), *SOURCE_DATA.values())
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError("Champion inputs missing: " + ", ".join(missing))

    rankings = pd.read_csv(CHAMPION_ARTIFACTS["player_rankings"])
    unified = pd.read_csv(CHAMPION_ARTIFACTS["unified_rankings"])
    goalkeepers = pd.read_csv(CHAMPION_ARTIFACTS["goalkeeper_rankings"])
    model_summary = json.loads(
        CHAMPION_ARTIFACTS["model_summary"].read_text(encoding="utf-8")
    )
    score_column = _score_column(rankings)
    position_column = _position_column(rankings)
    rank_column = _rank_column(rankings)
    outfield = rankings.loc[
        ~rankings[position_column].astype(str).isin(["GK", "Goalkeeper"])
    ].copy()
    correlations: dict[str, Any] = {}
    for metric in (
        "minutes",
        "goals",
        "xg_sum",
        "xa_sum",
        "vaep_total",
        "vaep_def_p90",
        "interceptions_p90",
        "pressures_p90",
        "aerial_wins_p90",
    ):
        if metric in outfield:
            correlations[metric] = _bootstrap_spearman(
                outfield[score_column],
                outfield[metric],
            )

    unified_lookup = unified.rename(
        columns={
            "Player": "player_name",
            "Team": "team",
        }
    )
    comparison = rankings.merge(
        unified_lookup[
            [
                "player_name",
                "team",
                "Global Rank",
                "Tournament Performance Score",
            ]
        ],
        on=["player_name", "team"],
        how="left",
        validate="one_to_one",
        suffixes=("", "_unified"),
    )
    unified_outfield = comparison.loc[
        ~comparison[position_column].astype(str).isin(["GK", "Goalkeeper"])
    ]
    model_metrics = model_summary.get("metrics", {})
    role_metrics = model_metrics.get("role_aware_elastic_net", {})
    gk_metrics = model_metrics.get("goalkeeper_post_shot", {})

    score_distributions = (
        rankings.groupby(position_column)[score_column]
        .agg(["count", "mean", "std", "min", "median", "max"])
        .reset_index()
        .to_dict("records")
    )
    rank_fields = [
        column
        for column in (
            "player_id",
            "player_name",
            "team",
            position_column,
            score_column,
            rank_column,
            "team_rank_v2",
            "position_rank_v2",
            "role_rank_v2",
            "gk_rank_v2",
        )
        if column in rankings
    ]
    actions = pd.read_parquet(
        SOURCE_DATA["spadl_actions"],
        columns=["game_id", "player_id", "period_id", "vaep_value"],
    )
    git_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {
        "schema_version": "ranking-repair-champion-1.0",
        "label": "champion",
        "immutable": True,
        "git_commit": git_commit,
        "random_seed": SEED,
        "source_hashes": {
            name: {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
            for name, path in SOURCE_DATA.items()
        },
        "artifact_hashes": {
            name: {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "sha256": _sha256(path),
            }
            for name, path in CHAMPION_ARTIFACTS.items()
        },
        "schemas": {
            name: _table_schema(path)
            for name, path in CHAMPION_ARTIFACTS.items()
            if path.suffix == ".csv"
        },
        "model_metrics": {
            "offense": role_metrics.get("offense", {}),
            "defense": role_metrics.get("defense", {}),
            "goalkeeper": gk_metrics,
        },
        "score_distributions_by_position": score_distributions,
        "score_correlations": correlations,
        "raw_to_unified_rank_spearman": _spearman(
            unified_outfield[rank_column],
            unified_outfield["Global Rank"],
        ),
        "unified_score_correlations": {
            metric: _bootstrap_spearman(
                unified_outfield["Tournament Performance Score"],
                unified_outfield[metric],
            )
            for metric in ("minutes", "goals", "xg_sum", "xa_sum")
            if metric in unified_outfield
        },
        "position_composition": {
            "tournament_v2": _position_composition(
                rankings,
                rank_column,
                position_column,
            ),
            "unified": _position_composition(
                unified,
                "Global Rank",
                "Position Group",
            ),
        },
        "ranked_minutes_bands": {
            "below_90": int(
                pd.to_numeric(outfield["minutes"], errors="coerce").lt(90).sum()
            ),
            "below_180": int(
                pd.to_numeric(outfield["minutes"], errors="coerce").lt(180).sum()
            ),
            "below_300": int(
                pd.to_numeric(outfield["minutes"], errors="coerce").lt(300).sum()
            ),
        },
        "goalkeeper_count": int(len(goalkeepers)),
        "goalkeeper_teams": int(goalkeepers["team"].nunique()),
        "rankings": rankings[rank_fields].to_dict("records"),
        "stability": _action_stability(actions),
    }


def freeze() -> dict[str, Any]:
    snapshot = _json_value(build_snapshot())
    content = json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"
    if SNAPSHOT_PATH.is_file():
        existing = SNAPSHOT_PATH.read_text(encoding="utf-8")
        if existing != content:
            raise RuntimeError(
                "Refusing to overwrite a differing immutable champion snapshot"
            )
        return snapshot

    DIAGNOSTIC_ROOT.mkdir(parents=True, exist_ok=True)
    for name, source in CHAMPION_ARTIFACTS.items():
        destination = DIAGNOSTIC_ROOT / f"{name}{source.suffix}"
        if destination.exists():
            raise FileExistsError(destination)
        shutil.copy2(source, destination)
    SNAPSHOT_PATH.write_text(content, encoding="utf-8")
    return snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the stored snapshot instead of initializing it.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.verify and not SNAPSHOT_PATH.is_file():
        raise FileNotFoundError(SNAPSHOT_PATH)
    snapshot = freeze()
    print(
        json.dumps(
            {
                "status": "verified" if args.verify else "frozen",
                "snapshot": str(SNAPSHOT_PATH),
                "git_commit": snapshot["git_commit"],
                "players": len(snapshot["rankings"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
