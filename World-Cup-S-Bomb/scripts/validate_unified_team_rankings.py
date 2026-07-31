#!/usr/bin/env python3
"""Validate unified rankings with cohort and named post-score audits."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RANKING_PATH = (
    PROJECT_ROOT
    / "results/reports/ranking/unified_tournament_rankings.csv"
)
SOURCE_PATH = PROJECT_ROOT / "results/reports/ranking/player_rankings.csv"
OUTPUT_PATH = (
    PROJECT_ROOT / "results/diagnostics/unified_team_validation.json"
)


def _one(frame: pd.DataFrame, pattern: str) -> pd.Series:
    matches = frame.loc[
        frame["Player"].str.contains(pattern, case=False, na=False, regex=True)
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one match for {pattern!r}, found {len(matches)}")
    return matches.iloc[0]


def validate() -> dict[str, Any]:
    """Return general release checks and Belgium/Argentina post-score audits."""

    rankings = pd.read_csv(RANKING_PATH)
    source = pd.read_csv(SOURCE_PATH)
    expected_columns = [
        "Global Rank",
        "Team Rank",
        "Player",
        "Team",
        "Position Group",
        "Tournament Performance Score",
    ]
    main_gk = source.loc[
        source["position_group_360"].eq("GK")
        & source["is_main_goalkeeper"].fillna(False).astype(bool)
    ]
    backups = source.loc[
        source["position_group_360"].eq("GK")
        & ~source["is_main_goalkeeper"].fillna(False).astype(bool)
    ]
    backup_lookup = backups[["player_name", "team"]].rename(
        columns={"player_name": "Player", "team": "Team"}
    )
    scored_backup_count = int(
        rankings.merge(
            backup_lookup,
            on=["Player", "Team"],
            how="inner",
            validate="one_to_one",
        )["Tournament Performance Score"].notna().sum()
    )
    messi = _one(rankings, r"Lionel.*Messi")
    mbappe = _one(rankings, r"Kylian.*Mbapp")
    livakovic = _one(rankings, r"Dominik Livak")
    martinez = _one(rankings, r"Dami.n Emiliano Mart")

    belgium = rankings.loc[rankings["Team"].eq("Belgium")].copy()
    courtois = _one(belgium, "Courtois")
    batshuayi = _one(belgium, "Batshuayi")
    lukaku = _one(belgium, "Lukaku")
    onana = _one(belgium, "Amadou Onana")
    belgium_size = int(belgium["Team Rank"].notna().sum())
    onana_percentile = (
        belgium_size - int(onana["Team Rank"]) + 1
    ) / belgium_size
    belgium_checks = {
        "courtois_in_team_top_five": int(courtois["Team Rank"]) <= 5,
        "batshuayi_above_low_minute_lukaku": (
            int(batshuayi["Team Rank"]) < int(lukaku["Team Rank"])
        ),
        "onana_at_or_above_team_median": onana_percentile >= 0.50,
    }

    argentina = rankings.loc[rankings["Team"].eq("Argentina")].copy()
    enzo = _one(argentina, r"^Enzo Fernandez$")
    mac_allister = _one(argentina, "Mac Allister")
    lautaro = _one(argentina, r"^Lautaro Javier")
    otamendi = _one(argentina, "Otamendi")
    romero = _one(argentina, "Cristian Gabriel Romero")
    argentina_size = int(argentina["Team Rank"].notna().sum())

    def team_percentile(row: pd.Series) -> float:
        return (
            argentina_size - int(row["Team Rank"]) + 1
        ) / argentina_size

    defender_percentiles = {
        "enzo": team_percentile(enzo),
        "otamendi": team_percentile(otamendi),
        "romero": team_percentile(romero),
    }
    argentina_core_checks = {
        "messi_team_rank_one": int(messi["Team Rank"]) == 1,
        "martinez_in_team_top_five": int(martinez["Team Rank"]) <= 5,
        "enzo_above_nonproducing_lautaro": (
            int(enzo["Team Rank"]) < int(lautaro["Team Rank"])
        ),
        "mac_allister_above_nonproducing_lautaro": (
            int(mac_allister["Team Rank"]) < int(lautaro["Team Rank"])
        ),
    }
    argentina_defender_band = {
        name: bool(0.60 <= percentile <= 0.90)
        for name, percentile in defender_percentiles.items()
    }

    general_checks = {
        "exact_clean_schema": rankings.columns.tolist() == expected_columns,
        "all_32_teams_present": rankings["Team"].nunique() == 32,
        "exactly_32_main_goalkeepers_in_source": (
            len(main_gk) == 32 and main_gk["team"].is_unique
        ),
        "backup_goalkeepers_unranked": scored_backup_count == 0,
        "messi_global_rank_one": int(messi["Global Rank"]) == 1,
        "mbappe_global_rank_two": int(mbappe["Global Rank"]) == 2,
        "livakovic_outside_global_top_ten": (
            int(livakovic["Global Rank"]) > 10
        ),
        "livakovic_above_martinez_in_unified_order": (
            int(livakovic["Global Rank"]) < int(martinez["Global Rank"])
        ),
        "scores_bounded_zero_to_one": bool(
            rankings["Tournament Performance Score"]
            .dropna()
            .between(0.0, 1.0)
            .all()
        ),
    }
    return {
        "general_checks": general_checks,
        "general_passed": all(general_checks.values()),
        "belgium": {
            "checks": belgium_checks,
            "passed": all(belgium_checks.values()),
            "team_size_ranked": belgium_size,
            "onana_team_percentile": onana_percentile,
        },
        "argentina": {
            "core_checks": argentina_core_checks,
            "core_passed": all(argentina_core_checks.values()),
            "defender_60_to_90_percentile_checks": argentina_defender_band,
            "defender_band_passed": all(argentina_defender_band.values()),
            "defender_team_percentiles": defender_percentiles,
            "note": (
                "The defender-band audit is diagnostic and never changes a "
                "score or rank."
            ),
        },
        "all_release_critical_checks_passed": bool(
            all(general_checks.values())
            and all(belgium_checks.values())
            and all(argentina_core_checks.values())
        ),
        "named_checks_used_in_scoring": False,
    }


def main() -> None:
    """Write the validation report after all ranking artifacts exist."""

    payload = validate()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if not payload["all_release_critical_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
