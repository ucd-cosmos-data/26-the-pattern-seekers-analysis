#!/usr/bin/env python3
"""Regenerate player-facing outputs after an accepted role-only refinement."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.report_generators import (  # noqa: E402
    TEAM_CODES,
    compile_v4_report_packets,
    generate_individual_starter_reports,
    generate_player_heatmap_svgs,
)


def main() -> None:
    profiles = pd.read_csv(
        PROJECT_ROOT / "data/processed/player_evaluations.csv"
    )
    synergy = pd.read_parquet(
        PROJECT_ROOT / "data/processed/player_synergy_matrix.parquet"
    )
    heatmaps = pd.read_csv(
        PROJECT_ROOT / "data/processed/player_heatmap_cells.csv"
    )
    starter_root = PROJECT_ROOT / "results/reports/starters"
    generate_individual_starter_reports(
        profiles, synergy, starter_root, clear_existing=False
    )
    generate_player_heatmap_svgs(
        profiles,
        heatmaps,
        PROJECT_ROOT / "results/reports/heatmaps",
        clear_existing=False,
    )

    inverse_codes = {code: team for team, code in TEAM_CODES.items()}
    team_root = PROJECT_ROOT / "results/reports/teams"
    for path in sorted(team_root.glob("*_team_coaching_report.md")):
        team = inverse_codes[path.name[:3]]
        top = profiles[profiles["team"].eq(team)].nsmallest(5, "team_rank")
        player_lines = "\n".join(
            f"{rank}. {row.player} — {row.functional_role}; "
            f"rating {row.final_player_rating:.4f}, "
            f"VAEP/90 {row.vaep_total_p90:+.3f}, xT/90 {row.xt_p90:+.3f}"
            for rank, row in enumerate(top.itertuples(index=False), start=1)
        )
        text = path.read_text(encoding="utf-8")
        text, replacements = re.subn(
            r"(## Unified 360-VAEP \+ xT player leaders\s*\n\n).*?"
            r"(\n\n_Only players)",
            lambda match: match.group(1) + player_lines + match.group(2),
            text,
            count=1,
            flags=re.DOTALL,
        )
        if replacements != 1:
            raise ValueError(f"Could not update player leaders in {path}")
        path.write_text(text, encoding="utf-8")
        json_path = path.with_suffix(".json")
        if json_path.is_file():
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            payload["top_v4_player_evaluations"] = top[
                [
                    "player_id", "player", "functional_role", "vaep_total_p90",
                    "vaep_per_touch", "xt_p90", "final_player_rating",
                    "team_rank", "final_third_share",
                ]
            ].to_dict("records")
            json_path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    compiled = compile_v4_report_packets(
        team_root,
        starter_root,
        PROJECT_ROOT / "results/reports/compiled",
    )
    print(
        json.dumps(
            {
                "starter_reports": len(profiles),
                "heatmaps": len(profiles),
                "team_reports": 32,
                **compiled,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
