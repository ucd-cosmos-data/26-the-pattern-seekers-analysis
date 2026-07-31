#!/usr/bin/env python3
"""Attach match-sampling uncertainty to the V4 player ratings.

Additive and non-destructive: reads the published player evaluations and the
per-action audit, reconstructs each rating's per-match ingredients exactly, and
runs a match-cluster bootstrap (see ``src/rating_uncertainty.py``) to produce a
standard error, confidence interval, and rank-stability for every rated player —
plus, per team, the probability that the #1 player really outranks the #2.

It changes no grade and writes only new files, so it cannot affect the acceptance
gates. It first asserts that its reconstruction reproduces every published rating
to machine precision; if that fails it errors rather than emit misleading numbers.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rating_uncertainty import (  # noqa: E402
    bootstrap_ratings,
    compute_ratings,
    summarize,
    top_gap_separation,
)

DEFAULT_EVALUATIONS = PROJECT_ROOT / "data" / "processed" / "player_evaluations.csv"
DEFAULT_AUDIT = PROJECT_ROOT / "data" / "processed" / "player_event_value_audit.parquet"
DEFAULT_COMPONENTS = (
    PROJECT_ROOT / "data" / "interim" / "world_cup_player_match_components.csv"
)
DEFAULT_CSV = PROJECT_ROOT / "results" / "reports" / "player_rating_uncertainty.csv"
DEFAULT_MD = (
    PROJECT_ROOT / "results" / "MIscellaneous" / "player_rating_uncertainty.md"
)

MIN_MINUTES = 300.0
WEIGHTS = (0.50, 0.30, 0.20)
TOUCH_TYPES = {"Pass", "Carry", "Dribble", "Shot", "Ball Receipt*", "Miscontrol", "Dispossessed"}
CLEAR_SEPARATION = 0.90  # P(#1 > #2) at or above this = statistically clear top


def build_matrices(
    evaluations: pd.DataFrame, audit: pd.DataFrame, components: pd.DataFrame
) -> dict:
    players = evaluations["player_id"].to_numpy()
    player_index = {int(p): i for i, p in enumerate(players)}
    matches = np.sort(audit["game_id"].unique())
    match_index = {int(m): j for j, m in enumerate(matches)}
    shape = (len(players), len(matches))

    audit = audit[audit["player_id"].isin(player_index)].copy()
    audit["touch"] = audit["type_name"].isin(TOUCH_TYPES) | audit[
        "type_name"
    ].astype(str).str.startswith("Ball Receipt")

    def matrix(frame: pd.DataFrame, id_col: str, match_col: str, value: str) -> np.ndarray:
        out = np.zeros(shape, dtype=float)
        grouped = frame.groupby([id_col, match_col])[value].sum()
        for (pid, mid), val in grouped.items():
            if int(pid) in player_index and int(mid) in match_index:
                out[player_index[int(pid)], match_index[int(mid)]] = val
        return out

    vaep = matrix(audit, "player_id", "game_id", "vaep_value")
    xt = matrix(audit, "player_id", "game_id", "xt_value")
    touches = matrix(audit.assign(touch=audit["touch"].astype(float)), "player_id", "game_id", "touch")
    minutes = matrix(
        components[components["player_id"].isin(player_index)],
        "player_id",
        "match_id",
        "minutes",
    )
    group_id = pd.factorize(evaluations["position_group"])[0]
    team_id = pd.factorize(evaluations["team"])[0]
    return {
        "vaep": vaep, "xt": xt, "touches": touches, "minutes": minutes,
        "group_id": group_id, "team_id": team_id, "team_labels": evaluations["team"].to_numpy(),
    }


def verify_reconstruction(evaluations: pd.DataFrame, m: dict) -> None:
    _, final = compute_ratings(
        m["vaep"].sum(1), m["xt"].sum(1), m["touches"].sum(1), m["minutes"].sum(1),
        m["group_id"], min_minutes=MIN_MINUTES, weights=WEIGHTS,
    )
    published = evaluations["final_player_rating"].to_numpy(dtype=float)
    error = float(np.nanmax(np.abs(final - published)))
    if error > 1e-9:
        raise RuntimeError(
            f"Reconstruction does not match published ratings (max error {error:.2e}); "
            "the per-match decomposition is wrong — refusing to emit uncertainty."
        )
    print(f"Reconstruction matches published ratings (max error {error:.2e}).")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluations", type=Path, default=DEFAULT_EVALUATIONS)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--components", type=Path, default=DEFAULT_COMPONENTS)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--replicates", type=int, default=2000)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def write_summary(path: Path, table: pd.DataFrame, separation: dict, m: dict, replicates: int) -> None:
    team_labels = m["team_labels"]
    team_id = m["team_id"]
    clear = sum(1 for v in separation.values() if np.isfinite(v) and v >= CLEAR_SEPARATION)
    coinflip = sum(1 for v in separation.values() if np.isfinite(v) and v < 0.60)
    median_rel = float(np.nanmedian(table["rating_se"] / table["final_player_rating"].abs()))

    # per-team top-two separation, most-ambiguous first
    rows = []
    for tid, prob in separation.items():
        label = team_labels[np.flatnonzero(team_id == tid)[0]]
        top = table[table["team"] == label].sort_values("team_rank").head(2)
        if len(top) < 2:
            continue
        rows.append((label, top.iloc[0]["player"], top.iloc[1]["player"], prob))
    rows.sort(key=lambda r: (np.inf if not np.isfinite(r[3]) else r[3]))

    lines = [
        "# Player Rating Uncertainty (match-cluster bootstrap)",
        "",
        f"- Replicates: {replicates:,} (whole matches resampled with replacement)",
        "- Scope: match-sampling uncertainty — how much a rating depends on the",
        "  particular matches a player featured in. Per-action VAEP/xT are held fixed.",
        "- No grade is changed; this is an additive companion to `player_evaluations.csv`.",
        f"- Teams with a statistically clear #1 (P(#1 > #2) ≥ {CLEAR_SEPARATION:.2f}): "
        f"**{clear}** of {len(separation)}; effectively a coin-flip (< 0.60): **{coinflip}**.",
        f"- Median rating standard error is {100 * median_rel:.1f}% of the rating.",
        "",
        "## Is each team's #1 statistically separated from its #2?",
        "",
        "| Team | #1 | #2 | P(#1 > #2) | Verdict |",
        "|---|---|---|---:|---|",
    ]
    for label, first, second, prob in rows:
        if not np.isfinite(prob):
            verdict = "n/a"
        elif prob >= CLEAR_SEPARATION:
            verdict = "clear"
        elif prob < 0.60:
            verdict = "coin-flip"
        else:
            verdict = "leaning"
        prob_str = "n/a" if not np.isfinite(prob) else f"{prob:.2f}"
        lines.append(f"| {label} | {first} | {second} | {prob_str} | {verdict} |")

    lines += [
        "",
        "## Most and least certain grades",
        "",
        "| Player | Team | Rating | SE | 95% CI | Rank | P(rank 1) |",
        "|---|---|---:|---:|---|---:|---:|",
    ]
    highlight = pd.concat([
        table.sort_values("team_rank").query("team_rank == 1").head(6),
    ])
    for row in highlight.itertuples(index=False):
        lines.append(
            f"| {row.player} | {row.team} | {row.final_player_rating:.3f} | "
            f"{row.rating_se:.3f} | [{row.rating_ci_low:.3f}, {row.rating_ci_high:.3f}] | "
            f"{int(row.team_rank)} | {row.p_rank1:.2f} |"
        )
    lines += [
        "",
        "Interpretation: a high P(#1 > #2) means the team's top grade is robust to which",
        "matches happened to be played; a low value means the top two are interchangeable",
        "given the sample. This does not change any rating — it says how much to trust each.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    evaluations = pd.read_csv(args.evaluations)
    audit = pd.read_parquet(args.audit)
    components = pd.read_csv(args.components)

    m = build_matrices(evaluations, audit, components)
    verify_reconstruction(evaluations, m)

    final_point, draws = bootstrap_ratings(
        m["vaep"], m["xt"], m["touches"], m["minutes"], m["group_id"],
        min_minutes=MIN_MINUTES, weights=WEIGHTS,
        replicates=args.replicates, random_state=args.random_state,
    )
    stats = summarize(final_point, draws, m["team_id"])
    separation = top_gap_separation(draws, m["team_id"], final_point)

    table = pd.DataFrame(
        {
            "team": evaluations["team"],
            "player_id": evaluations["player_id"],
            "player": evaluations["player"],
            "position_group": evaluations["position_group"],
            "minutes": evaluations["minutes"],
            "final_player_rating": evaluations["final_player_rating"],
            "rating_se": stats["rating_se"],
            "rating_ci_low": stats["rating_ci_low"],
            "rating_ci_high": stats["rating_ci_high"],
            "team_rank": evaluations["team_rank"],
            "mean_rank": stats["mean_rank"],
            "p_rank1": stats["p_rank1"],
            "p_top3": stats["p_top3"],
        }
    )
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output_csv, index=False)
    write_summary(args.output_md, table, separation, m, args.replicates)

    clear = sum(1 for v in separation.values() if np.isfinite(v) and v >= CLEAR_SEPARATION)
    print(f"{clear}/{len(separation)} teams have a statistically clear #1 (P >= {CLEAR_SEPARATION}).")
    print(f"Wrote {args.output_csv}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()
