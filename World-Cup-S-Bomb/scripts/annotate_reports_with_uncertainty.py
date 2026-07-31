#!/usr/bin/env python3
"""Annotate the compiled team markdowns with player-rating uncertainty.

Adds the match-sampling uncertainty from
``results/reports/player_rating_uncertainty.csv`` (produced by
``scripts/quantify_player_rating_uncertainty.py``) into the delivered team
reports, so a reader sees not just each grade but how much to trust it. It
changes no grade — only appends confidence lines — and is idempotent, so it can
be re-run after the reports are regenerated.

Two edit sites:
  * ``*_compiled_player_reports.md`` — per player, a 95% CI and rank-stability
    line right after ``Team rank:`` (players matched by the id in the
    ``PLAYER_REPORT`` comment).
  * ``*_team_coaching_report.md`` — each "player leaders" entry gets its rating's
    95% CI, and the list gets a one-line note on how confident the #1 rank is.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UNCERTAINTY = (
    PROJECT_ROOT / "results" / "reports" / "player_rating_uncertainty.csv"
)
DEFAULT_COMPILED = PROJECT_ROOT / "results" / "reports" / "compiled"

CI_SENTINEL = "- Rating 95% CI:"
LEADER_SENTINEL = "[95% CI"
PLAYER_REPORT_RE = re.compile(r"PLAYER_REPORT\s+\d+:\s+(\d+)_")
TEAM_RANK_RE = re.compile(r"^-\s*Team rank:\s*#\d+")
LEADER_RE = re.compile(r"^(\d+)\.\s+(.+?)\s+—\s+.*;\s+rating\s+[\d.]+")


def uncertainty_lines(row: pd.Series) -> list[str]:
    return [
        f"{CI_SENTINEL} [{row.rating_ci_low:.4f}, {row.rating_ci_high:.4f}] "
        f"(bootstrap SE {row.rating_se:.4f})",
        f"- Rank stability: bootstrap mean rank {row.mean_rank:.1f}; "
        f"P(team #1) {row.p_rank1:.0%}, P(top 3) {row.p_top3:.0%}",
    ]


def annotate_player_report(text: str, by_id: dict[int, pd.Series]) -> tuple[str, int]:
    lines = text.splitlines()
    out: list[str] = []
    current_id: int | None = None
    updated = 0
    for i, line in enumerate(lines):
        out.append(line)
        match = PLAYER_REPORT_RE.search(line)
        if match:
            current_id = int(match.group(1))
            continue
        if TEAM_RANK_RE.match(line) and current_id in by_id:
            already = i + 1 < len(lines) and lines[i + 1].startswith(CI_SENTINEL)
            if not already:
                out.extend(uncertainty_lines(by_id[current_id]))
                updated += 1
            current_id = None
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), updated


def annotate_team_coaching(text: str, by_name: dict[str, pd.Series]) -> tuple[str, int]:
    lines = text.splitlines()
    out: list[str] = []
    updated = 0
    leader_block: list[tuple[str, pd.Series]] = []
    for line in lines:
        match = LEADER_RE.match(line)
        if match and LEADER_SENTINEL not in line:
            name = match.group(2).strip()
            row = by_name.get(name)
            if row is not None:
                line = f"{line} [95% CI {row.rating_ci_low:.4f}–{row.rating_ci_high:.4f}]"
                updated += 1
                if match.group(1) == "1":
                    leader_block = [(name, row)]
        out.append(line)
    # Add a rank-confidence note directly under the leaders heading's list.
    if leader_block:
        name, row = leader_block[0]
        note = (
            f"- Rank confidence: P({name} is the team's true #1) "
            f"= {row.p_rank1:.0%} (2,000-sample match bootstrap)."
        )
        if note not in out:
            # insert after the last consecutive leader line
            last = max(i for i, ln in enumerate(out) if LEADER_RE.match(ln))
            out.insert(last + 1, note)
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), updated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uncertainty", type=Path, default=DEFAULT_UNCERTAINTY)
    parser.add_argument("--compiled-dir", type=Path, default=DEFAULT_COMPILED)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    unc = pd.read_csv(args.uncertainty)
    by_id = {int(r.player_id): r for r in unc.itertuples(index=False)}
    dupes = unc["player"].duplicated().sum()
    if dupes:
        print(f"WARNING: {dupes} duplicate player names; leader matches may be ambiguous")
    by_name = {r.player: r for r in unc.itertuples(index=False)}

    players_updated = leaders_updated = 0
    for path in sorted(args.compiled_dir.glob("*_compiled_player_reports.md")):
        text = path.read_text(encoding="utf-8")
        new, n = annotate_player_report(text, by_id)
        if n:
            path.write_text(new, encoding="utf-8")
        players_updated += n
    for path in sorted(args.compiled_dir.glob("*_team_coaching_report.md")):
        text = path.read_text(encoding="utf-8")
        new, n = annotate_team_coaching(text, by_name)
        if new != text:
            path.write_text(new, encoding="utf-8")
        leaders_updated += n

    print(f"Annotated {players_updated} player blocks and {leaders_updated} leader entries.")


if __name__ == "__main__":
    main()
