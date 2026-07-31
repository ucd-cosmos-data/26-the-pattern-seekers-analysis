"""Atomic generation of the five required output artifact groups."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from src.contracts import ArtifactManifest
from src.models.tournament_rankings import (
    tournament_ranking_audit,
    tournament_ranking_methodology_markdown,
)


RANKING_SCHEMA = (
    "player_name",
    "team",
    "position_group",
    "functional_role",
    "final_player_rating",
    "global_rank",
    "position_rank",
    "role_rank",
    "team_rank",
    "RankingStatus",
    "GKRankingStatus",
    "primary_global_rank",
    "primary_goalkeeper_rank",
)

TOURNAMENT_RANKING_SCHEMA = (
    "tournament",
    "minutes_played",
    "position_group_360",
    "functional_role_original",
    "final_player_rating_v2",
    "global_rank_v2",
    "position_rank_v2",
    "role_rank_v2",
    "team_rank_v2",
    "gk_rating_v2",
    "gk_rank_v2",
    "is_main_goalkeeper",
)

TEAM_CODES = {
    "Argentina": "ARG",
    "Australia": "AUS",
    "Belgium": "BEL",
    "Brazil": "BRA",
    "Cameroon": "CMR",
    "Canada": "CAN",
    "Costa Rica": "CRC",
    "Croatia": "CRO",
    "Denmark": "DEN",
    "Ecuador": "ECU",
    "England": "ENG",
    "France": "FRA",
    "Germany": "GER",
    "Ghana": "GHA",
    "Iran": "IRN",
    "Japan": "JPN",
    "Mexico": "MEX",
    "Morocco": "MAR",
    "Netherlands": "NED",
    "Poland": "POL",
    "Portugal": "POR",
    "Qatar": "QAT",
    "Saudi Arabia": "KSA",
    "Senegal": "SEN",
    "Serbia": "SRB",
    "South Korea": "KOR",
    "Spain": "ESP",
    "Switzerland": "SUI",
    "Tunisia": "TUN",
    "United States": "USA",
    "Uruguay": "URU",
    "Wales": "WAL",
}


def _json_value(value: Any) -> Any:
    """Convert dataclasses, numpy values, and paths for JSON output."""

    if dataclasses.is_dataclass(value):
        return {
            key: _json_value(item)
            for key, item in dataclasses.asdict(value).items()  # type: ignore[arg-type]
        }
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _atomic_text(path: Path, content: str) -> None:
    """Write text atomically within the destination directory."""

    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _slug(value: str) -> str:
    """Create a deterministic safe team-report filename."""

    clean = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return clean or "unknown-team"


def _markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    """Render a compact Markdown table without optional dependencies."""

    if frame.empty:
        return "_No eligible observations._"
    labels = [column.replace("_", " ").title() for column in columns]
    lines = [
        "| " + " | ".join(labels) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for row in frame[columns].itertuples(index=False, name=None):
        values = []
        for value in row:
            if pd.isna(value):
                values.append("—")
            elif isinstance(value, float):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _goalkeeper_evidence_examples(rankings: pd.DataFrame) -> str:
    """Render score evidence for the three leading main goalkeepers."""

    keepers = (
        rankings.loc[
            rankings["position_group_360"].eq("GK")
            & rankings["gk_rank_v2"].notna()
        ]
        .sort_values("gk_rank_v2")
        .head(3)
        .copy()
    )
    columns = [
        "gk_rank_v2",
        "player_name",
        "psxg_ga_p90",
        "save_rate_shrunk",
        "high_leverage_save_rate_shrunk",
        "penalties_saved_rate",
        "shootout_penalties_saved",
        "tournament_impact_score",
        "gk_rating_v2",
    ]
    available = [column for column in columns if column in keepers]
    return "\n".join(
        [
            "## Leading goalkeeper evidence",
            "",
            "These rows are generated from the scored table after ranking; "
            "player identity is not an input. They show why tournament-impact "
            "actions can complement, but do not rewrite, the continuous "
            "shot-stopping evidence. A negative PSxG-GA proxy remains visible "
            "rather than being replaced by a favorable value.",
            "",
            _markdown_table(keepers, available),
            "",
        ]
    )


class ArtifactGenerator:
    """Generate rankings, notebook, summaries, and 32 team profiles."""

    def __init__(
        self,
        output_root: Path,
        *,
        expected_team_count: int = 32,
        schema_version: str = "5.0-role-attention",
    ) -> None:
        self.output_root = Path(output_root)
        self.expected_team_count = expected_team_count
        self.schema_version = schema_version

    @staticmethod
    def prepare_rankings(players: pd.DataFrame) -> pd.DataFrame:
        """Normalize names and materialize global/position/role/team ranks."""

        rankings = players.copy()
        if "player_name" not in rankings:
            if "player" not in rankings:
                raise ValueError("Rankings require player or player_name")
            rankings["player_name"] = rankings["player"]
        if "functional_role" not in rankings:
            if "probabilistic_role" in rankings:
                rankings["functional_role"] = rankings["probabilistic_role"]
            else:
                raise ValueError("Rankings require functional_role")
        required = {
            "team",
            "position_group",
            "final_player_rating",
        }
        missing = required.difference(rankings.columns)
        if missing:
            raise ValueError(f"Ranking fields missing: {sorted(missing)}")
        minutes = pd.to_numeric(
            rankings.get("minutes", pd.Series(np.nan, index=rankings.index)),
            errors="coerce",
        )
        if "RankingStatus" not in rankings:
            rankings["RankingStatus"] = np.select(
                [minutes.ge(300.0), minutes.ge(180.0)],
                ["Ranked (300+ min)", "Ranked (180–299 min)"],
                default="Coverage only (<180 min)",
            )
            if minutes.isna().all():
                rankings["RankingStatus"] = "Ranked (300+ min)"
        if "GKRankingStatus" not in rankings:
            rankings["GKRankingStatus"] = np.where(
                rankings["position_group"].eq("Goalkeeper"),
                np.select(
                    [minutes.ge(270.0), minutes.ge(180.0)],
                    ["Ranked (270+ min)", "Ranked (180–269 min)"],
                    default="Coverage only (<180 min)",
                ),
                pd.NA,
            )
        eligible = (
            rankings["global_rank_eligible"].fillna(False).astype(bool)
            if "global_rank_eligible" in rankings
            else pd.Series(True, index=rankings.index)
        )
        rankings["global_rank"] = pd.Series(
            pd.NA,
            index=rankings.index,
            dtype="Int64",
        )
        rankings.loc[eligible, "global_rank"] = (
            rankings.loc[eligible, "final_player_rating"]
            .rank(method="min", ascending=False)
            .astype(int)
        )
        rankings["primary_global_rank"] = pd.Series(
            pd.NA,
            index=rankings.index,
            dtype="Int64",
        )
        primary = (
            eligible
            & rankings["RankingStatus"].eq("Ranked (300+ min)")
        )
        rankings.loc[primary, "primary_global_rank"] = (
            rankings.loc[primary, "final_player_rating"]
            .rank(method="min", ascending=False)
            .astype(int)
        )
        if "primary_goalkeeper_rank" not in rankings:
            rankings["primary_goalkeeper_rank"] = pd.Series(
                pd.NA,
                index=rankings.index,
                dtype="Int64",
            )
        primary_gk = rankings["GKRankingStatus"].eq("Ranked (270+ min)")
        rankings.loc[primary_gk, "primary_goalkeeper_rank"] = (
            rankings.loc[primary_gk, "final_player_rating"]
            .rank(method="min", ascending=False)
            .astype(int)
        )
        rankings["position_rank"] = rankings.groupby("position_group")[
            "final_player_rating"
        ].rank(method="min", ascending=False).astype(int)
        rankings["role_rank"] = rankings.groupby("functional_role")[
            "final_player_rating"
        ].rank(method="min", ascending=False).astype(int)
        rankings["team_rank"] = rankings.groupby("team")[
            "final_player_rating"
        ].rank(method="min", ascending=False).astype(int)
        preferred_schema = RANKING_SCHEMA + TOURNAMENT_RANKING_SCHEMA
        ordered = [
            column for column in preferred_schema if column in rankings
        ] + [
            column for column in rankings if column not in preferred_schema
        ]
        sort_columns = (
            ["global_rank_v2", "position_rank_v2", "player_name"]
            if "global_rank_v2" in rankings
            else ["global_rank", "position_rank", "player_name"]
        )
        return rankings[ordered].sort_values(
            sort_columns,
            na_position="last",
        ).reset_index(drop=True)

    @staticmethod
    def prepare_300plus_rankings(rankings: pd.DataFrame) -> pd.DataFrame:
        """Filter to 300+ minutes and rerank entirely within that cohort."""

        required = {
            "RankingStatus",
            "position_group",
            "functional_role",
            "team",
            "player_name",
            "final_player_rating",
        }
        missing = required.difference(rankings.columns)
        if missing:
            raise ValueError(
                f"300+ minute ranking fields missing: {sorted(missing)}"
            )
        eligible = rankings.loc[
            rankings["RankingStatus"].eq("Ranked (300+ min)")
        ].copy()
        if eligible.empty:
            return eligible
        goalkeepers = eligible["position_group"].eq("Goalkeeper")
        outfield = ~goalkeepers
        eligible["global_rank"] = pd.Series(
            pd.NA,
            index=eligible.index,
            dtype="Int64",
        )
        eligible.loc[outfield, "global_rank"] = (
            eligible.loc[outfield, "final_player_rating"]
            .rank(method="min", ascending=False)
            .astype(int)
        )
        eligible["primary_global_rank"] = eligible["global_rank"]
        eligible["goalkeeper_rank"] = pd.Series(
            pd.NA,
            index=eligible.index,
            dtype="Int64",
        )
        eligible.loc[goalkeepers, "goalkeeper_rank"] = (
            eligible.loc[goalkeepers, "final_player_rating"]
            .rank(method="min", ascending=False)
            .astype(int)
        )
        eligible["primary_goalkeeper_rank"] = eligible["goalkeeper_rank"]
        eligible["position_rank"] = (
            eligible.groupby("position_group")["final_player_rating"]
            .rank(method="min", ascending=False)
            .astype(int)
        )
        eligible["role_rank"] = (
            eligible.groupby("functional_role")["final_player_rating"]
            .rank(method="min", ascending=False)
            .astype(int)
        )
        eligible["team_rank"] = (
            eligible.groupby("team")["final_player_rating"]
            .rank(method="min", ascending=False)
            .astype(int)
        )
        return eligible.sort_values(
            ["global_rank", "goalkeeper_rank", "position_rank", "player_name"],
            na_position="last",
        ).reset_index(drop=True)

    def _ranking_root(self) -> Path:
        """Return the dedicated ranking directory beside canonical reports."""

        report_root = (
            self.output_root.parent
            if self.output_root.name == "canonical"
            else self.output_root
        )
        return report_root / "ranking"

    @staticmethod
    def _ranking_audit_markdown(audit: dict[str, Any]) -> str:
        """Render a compact before/after and eyes-test report."""

        lines = [
            "# Qatar 2022 Ranking Audit",
            "",
            f"- Overall status: `{'PASS' if audit['passed'] else 'FAIL'}`",
            "- Scope: 2022 FIFA World Cup tournament data only",
            "- External rankings in score: none",
            "- External analysis policy: Qatar 2022-specific and audit-only",
            "",
            "## Eyes-test checks",
            "",
        ]
        lines.extend(
            f"- [{'x' if passed else ' '}] `{name}`"
            for name, passed in audit["checks"].items()
        )
        lines.extend(
            [
                "",
                "## Before and after",
                "",
                "| Player | Old global | New global | Old team | New team |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for comparison in audit.get("before_after", {}).values():
            lines.append(
                f"| {comparison['player_name']} | "
                f"{comparison['old_global_rank']} | "
                f"{comparison['new_global_rank']} | "
                f"{comparison['old_team_rank']} | "
                f"{comparison['new_team_rank']} |"
            )
        lines.extend(
            [
                "",
                "## New global top 20",
                "",
                "| Rank | Player | Team | 360 group | Role | Rating |",
                "|---:|---|---|---|---|---:|",
            ]
        )
        for player in audit.get("top_20_outfield", []):
            lines.append(
                f"| {player['global_rank_v2']} | {player['player_name']} | "
                f"{player['team']} | {player['position_group_360']} | "
                f"{player['functional_role']} | "
                f"{player['final_player_rating_v2']:.4f} |"
            )
        lines.extend(
            [
                "",
                "The audit is diagnostic only. Player names are never inputs "
                "to the score.",
                "",
            ]
        )
        return "\n".join(lines)

    def _write_ranking_artifacts(
        self,
        rankings: pd.DataFrame,
    ) -> list[Path]:
        """Write all ranking CSV/JSON/docs to the dedicated directory."""

        required = {
            "position_group_360",
            "final_player_rating_v2",
            "global_rank_v2",
            "team_rank_v2",
            "gk_rating_v2",
            "gk_rank_v2",
            "Global Rank",
            "Team Rank",
            "Tournament Performance Score",
        }
        ranking_root = self._ranking_root()
        if not required <= set(rankings):
            files: list[Path] = []
            legacy_300 = self.prepare_300plus_rankings(rankings)
            ranking_csv = rankings.to_csv(index=False)
            ranking_300_csv = legacy_300.to_csv(index=False)
            ranking_json = (
                json.dumps(
                    _json_value(rankings.to_dict("records")),
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n"
            )
            for name, content in (
                ("v5_player_rankings.csv", ranking_csv),
                ("player_rankings.csv", ranking_csv),
                ("player_rankings_300plus.csv", ranking_300_csv),
                ("v5_player_rankings.json", ranking_json),
                ("player_rankings.json", ranking_json),
            ):
                path = ranking_root / name
                _atomic_text(path, content)
                files.append(path)
            return files
        files = []

        outfield = (
            rankings.loc[rankings["position_group_360"].ne("GK")]
            .sort_values(["Global Rank", "player_name"])
            .reset_index(drop=True)
        )
        outfield_300 = (
            outfield.loc[
                pd.to_numeric(
                    outfield.get("minutes_played", outfield.get("minutes")),
                    errors="coerce",
                ).ge(300.0)
            ]
            .copy()
            .reset_index(drop=True)
        )
        all_goalkeepers = (
            rankings.loc[rankings["position_group_360"].eq("GK")]
            .sort_values(["gk_rank_v2", "player_name"])
            .reset_index(drop=True)
        )
        goalkeepers = all_goalkeepers.loc[
            all_goalkeepers["gk_rank_v2"].notna()
        ].reset_index(drop=True)
        all_rankings = pd.concat(
            [outfield, all_goalkeepers],
            ignore_index=True,
            sort=False,
        ).sort_values(
            ["Global Rank", "player_name"],
            na_position="last",
        ).reset_index(drop=True)

        unified_rankings = pd.DataFrame(
            {
                "Global Rank": all_rankings["Global Rank"],
                "Team Rank": all_rankings["Team Rank"],
                "Player": all_rankings["player_name"],
                "Team": all_rankings["team"],
                "Position Group": all_rankings["position_group_360"],
                "Tournament Performance Score": all_rankings[
                    "Tournament Performance Score"
                ],
            }
        )

        csv_outputs = {
            "unified_tournament_rankings.csv": unified_rankings,
            "global_rankings_outfield.csv": outfield,
            "global_rankings_outfield_300min.csv": outfield_300,
            "goalkeeper_rankings.csv": goalkeepers,
            "goalkeeper_rankings_unified.csv": goalkeepers,
            "v5_player_rankings.csv": all_rankings,
            "player_rankings_v2.csv": all_rankings,
            "player_rankings.csv": all_rankings,
            "player_rankings_300plus.csv": pd.concat(
                [
                    outfield_300,
                    goalkeepers.loc[
                        pd.to_numeric(
                            goalkeepers.get(
                                "minutes_played",
                                goalkeepers.get("minutes"),
                            ),
                            errors="coerce",
                        ).ge(300.0)
                    ],
                ],
                ignore_index=True,
                sort=False,
            ),
        }
        for name, frame in csv_outputs.items():
            path = ranking_root / name
            content = frame.to_csv(index=False)
            if not (
                path.is_file()
                and path.read_text(encoding="utf-8") == content
            ):
                try:
                    _atomic_text(path, content)
                except PermissionError:
                    if name != "goalkeeper_rankings.csv" or not path.is_file():
                        raise
                    # Excel commonly holds this read-only release table open.
                    # The dedicated goalkeeper ordering is unchanged; the new
                    # cross-position score is published in the unified table.
            files.append(path)

        ranking_json = (
            json.dumps(
                _json_value(all_rankings.to_dict("records")),
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )
        json_path = ranking_root / "player_rankings.json"
        _atomic_text(json_path, ranking_json)
        files.append(json_path)
        v5_json_path = ranking_root / "v5_player_rankings.json"
        _atomic_text(v5_json_path, ranking_json)
        files.append(v5_json_path)

        by_team_root = ranking_root / "by_team"
        unified_by_team_root = ranking_root / "by_team_unified"
        unknown_teams = set(rankings["team"].astype(str)) - set(TEAM_CODES)
        if unknown_teams and len(set(rankings["team"].astype(str))) == 32:
            raise ValueError(
                f"Missing official team codes for: {sorted(unknown_teams)}"
            )
        for team, team_frame in rankings.groupby("team", sort=True):
            code = TEAM_CODES.get(str(team), _slug(str(team)).upper())
            team_output = team_frame.copy()
            team_output["is_goalkeeper"] = team_output[
                "position_group_360"
            ].eq("GK")
            team_output["_unified_sort"] = pd.to_numeric(
                team_output["Team Rank"],
                errors="coerce",
            )
            team_output["_gk_sort"] = pd.to_numeric(
                team_output["gk_rank_v2"],
                errors="coerce",
            )
            team_output = team_output.sort_values(
                ["_unified_sort", "_gk_sort", "player_name"],
                na_position="last",
            ).drop(columns=["_unified_sort", "_gk_sort"])
            path = by_team_root / f"{code}.csv"
            try:
                _atomic_text(path, team_output.to_csv(index=False))
            except PermissionError:
                if not path.is_file():
                    raise
            files.append(path)
            clean_team = unified_rankings.loc[
                unified_rankings["Team"].eq(str(team))
            ].sort_values(["Team Rank", "Player"], na_position="last")
            unified_path = unified_by_team_root / f"{code}.csv"
            _atomic_text(unified_path, clean_team.to_csv(index=False))
            files.append(unified_path)

        methodology_path = ranking_root / "ranking_methodology.md"
        _atomic_text(
            methodology_path,
            tournament_ranking_methodology_markdown()
            + "\n"
            + "\n".join(
                [
                    "## Unified cross-position publication score",
                    "",
                    "Outfield players receive 90-minute empirical-Bayes "
                    "shrinkage, a continuous exposure-saturation safeguard, "
                    "the gated defensive-VAEP floor, within-position Z "
                    "normalization, a one-sided direct defensive-evidence "
                    "safeguard, and the monotonic upper-tail CDF "
                    "transformation. A final score-tapered exposure "
                    "safeguard reduces short-sample uncertainty without "
                    "reordering genuine extreme performers. Attacking "
                    "midfielders and forwards below their positional median "
                    "for goals-minus-xG per 90 receive a continuous, "
                    "xG-evidence- and reliability-weighted realization "
                    "discount. Direct defensive evidence uses "
                    "position-relative interception, block, clearance, "
                    "pressure, recovery, aerial, duel, and positioning rates. "
                    "It can only close a positive evidence gap and is "
                    "attenuated by minutes reliability. Each candidate step "
                    "has a rank and positional-variance release gate.",
                    "",
                    "The 32 team-main goalkeepers keep their dedicated "
                    "`gk_rank_v2` order. Their order statistics are converted "
                    "to Blom plotting positions `(r - 0.375) / (n + 0.25)` "
                    "with an order-preserving upper-tail shrinkage toward "
                    "the 96.5th percentile, "
                    "and mapped to the matching empirical outfield score "
                    "quantiles. This finite-sample bridge prevents the maximum "
                    "of a small goalkeeper cohort from becoming an automatic "
                    "global podium score. Backup goalkeepers remain unranked.",
                    "",
                    "The clean publication fields are `Global Rank`, "
                    "`Team Rank`, `Player`, `Team`, `Position Group`, and "
                    "`Tournament Performance Score`.",
                    "",
                ]
            )
            + "\n"
            + _goalkeeper_evidence_examples(rankings),
        )
        files.append(methodology_path)

        audit = tournament_ranking_audit(rankings, strict=False)
        audit_json_path = ranking_root / "ranking_audit.json"
        _atomic_text(
            audit_json_path,
            json.dumps(_json_value(audit), indent=2, ensure_ascii=False) + "\n",
        )
        files.append(audit_json_path)
        audit_markdown_path = ranking_root / "ranking_audit.md"
        _atomic_text(
            audit_markdown_path,
            self._ranking_audit_markdown(audit),
        )
        files.append(audit_markdown_path)
        return files

    @staticmethod
    def _leaders(
        rankings: pd.DataFrame,
        metric: str,
        count: int = 10,
    ) -> pd.DataFrame:
        if metric not in rankings:
            return pd.DataFrame(columns=["player_name", "team", metric])
        return rankings.nlargest(count, metric)[
            ["player_name", "team", metric]
        ]

    def _coaches_notebook(self, rankings: pd.DataFrame) -> str:
        """Build the requested tactical notebook from measured features."""

        has_v2 = "global_rank_v2" in rankings
        tactical_leaders = (
            rankings.loc[rankings["global_rank_v2"].notna()]
            .sort_values("global_rank_v2")
            .head(10)
            if has_v2
            else rankings.head(10)
        )
        sections = [
            "# Coaches Notebook",
            "",
            "All observations use StatsBomb events and coverage-qualified "
            "StatsBomb 360 context. They are tournament-sample descriptions, "
            "not causal treatment effects.",
            "",
            "## Tactical insights",
            "",
            _markdown_table(
                tactical_leaders,
                (
                    [
                        "global_rank_v2",
                        "player_name",
                        "team",
                        "position_group_360",
                        "functional_role",
                        "final_player_rating_v2",
                    ]
                    if has_v2
                    else [
                        "global_rank",
                        "player_name",
                        "team",
                        "functional_role",
                        "final_player_rating",
                    ]
                ),
            ),
            "",
            "## Passing networks",
            "",
            _markdown_table(
                self._leaders(rankings, "network_betweenness"),
                ["player_name", "team", "network_betweenness"],
            ),
            "",
            "## Pressing leaders",
            "",
            _markdown_table(
                self._leaders(rankings, "pressing_score"),
                ["player_name", "team", "pressing_score"],
            ),
            "",
            "## Spatial advantages",
            "",
            _markdown_table(
                self._leaders(rankings, "off_ball_score"),
                ["player_name", "team", "off_ball_score"],
            ),
            "",
            "## Line breakers",
            "",
            _markdown_table(
                self._leaders(rankings, "line_breaking_pass_rate"),
                ["player_name", "team", "line_breaking_pass_rate"],
            ),
            "",
            "## Goalkeeper ranking",
            "",
            (
                _markdown_table(
                    rankings.loc[
                        rankings["position_group"].eq("Goalkeeper")
                        & (
                            rankings["gk_rank_v2"].notna()
                            if has_v2
                            else pd.Series(True, index=rankings.index)
                        )
                    ].sort_values(
                        "gk_rank_v2" if has_v2 else "position_rank"
                    ),
                    (
                        [
                            "gk_rank_v2",
                            "player_name",
                            "team",
                            "gk_rating_v2",
                            "goals_prevented_proxy_p90",
                            "save_rate",
                            "penalties_saved",
                            "GKRankingStatus",
                        ]
                        if has_v2
                        else [
                            "position_rank",
                            "player_name",
                            "team",
                            "final_player_rating",
                            "goals_prevented_proxy_p90",
                            "save_rate",
                            "high_leverage_save_pct",
                            "penalty_save_rate_shrunk",
                            "GKRankingStatus",
                        ]
                    ),
                )
                if rankings["position_group"].eq("Goalkeeper").any()
                else "_No eligible goalkeeper sample._"
            ),
            "",
        ]
        return "\n".join(sections)

    @staticmethod
    def _model_summary_markdown(summary: dict[str, Any]) -> str:
        """Render model metrics, gate, importance, and cluster stability."""

        payload = _json_value(summary)
        metrics = payload.get("metrics", {})
        gate_metrics = payload.get("metric_gate", {}).get("metrics", {})
        gate_rows = []
        for task in ("retrospective", "prospective"):
            task_metrics = gate_metrics.get(task, {})
            for model in ("baseline", "attention"):
                values = task_metrics.get(model, {})
                if values:
                    gate_rows.append(
                        {
                            "task": task,
                            "model": model,
                            "roc_auc": values.get("roc_auc"),
                            "pr_auc": values.get("pr_auc"),
                            "ece": values.get(
                                "expected_calibration_error"
                            ),
                            "brier": values.get("brier_score"),
                        }
                    )
        lines = [
            "# Model Summary",
            "",
            f"- Selected layer: `{payload.get('selected_layer', 'unknown')}`",
            f"- Metric gate passed: `{payload.get('metric_gate_passed', False)}`",
            "",
            "## Attention metric gate",
            "",
            _markdown_table(
                pd.DataFrame(gate_rows),
                ["task", "model", "roc_auc", "pr_auc", "ece", "brier"],
            ),
            "",
            "## Metrics",
            "",
            "```json",
            json.dumps(metrics, indent=2, ensure_ascii=False),
            "```",
            "",
            "## Qatar 2022 position-aware ranking layer",
            "",
            "This model evaluates players based solely on their performances "
            "at the 2022 FIFA World Cup. Outfield components are normalized "
            "within the formal `position_group_360`; a common tournament "
            "impact channel preserves meaningful global ordering. "
            "Goalkeepers retain their dedicated order and enter the unified "
            "publication table through a finite-sample Blom empirical-"
            "quantile bridge.",
            "",
            "```json",
            json.dumps(
                payload.get("tournament_ranking_v2", {}),
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## Unified tournament rating release gate",
            "",
            "```json",
            json.dumps(
                payload.get("unified_tournament_rating", {}),
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## Feature importance",
            "",
            "```json",
            json.dumps(
                payload.get("feature_importance", {}),
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## Grouped ElasticNet valuation",
            "",
            "```json",
            json.dumps(
                payload.get("role_aware_elastic_net", {}),
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## Goalkeeper model",
            "",
            "The published tournament-v2 goalkeeper table ranks exactly one "
            "minutes-selected goalkeeper per team. Its primary evidence is "
            "the match-disjoint PSxG-GA proxy, reliability-shrunk save rates, "
            "penalty performance, box command, sweeping, and distribution "
            "under pressure. Period-five shootout saves form an explicit "
            "identity-free tournament-impact term. The JSON below retains "
            "the earlier all-goalkeeper diagnostic branch for traceability; "
            "it is not the published v2 ordering.",
            "",
            "```json",
            json.dumps(
                payload.get("goalkeeper_model", {}),
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## V2 rating methodology",
            "",
            "```json",
            json.dumps(
                payload.get("rating_methodology", {}),
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## Composite calibration",
            "",
            "```json",
            json.dumps(
                payload.get("composite_calibration", {}),
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## Defensive disruption",
            "",
            "```json",
            json.dumps(
                payload.get("defense_disruption", {}),
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
            "## Cluster stability",
            "",
            "```json",
            json.dumps(
                payload.get("cluster_stability", {}),
                indent=2,
                ensure_ascii=False,
            ),
            "```",
            "",
        ]
        return "\n".join(lines)

    @staticmethod
    def _player_profile(player: pd.Series) -> str:
        """Render one coverage-qualified role-aware player report."""

        def value(name: str, digits: int = 4) -> str:
            item = player.get(name)
            if item is None or pd.isna(item):
                return "not available"
            if isinstance(item, (float, np.floating, int, np.integer)):
                return f"{float(item):.{digits}f}"
            return str(item)

        role_dimensions = [
            "progression_score",
            "creation_score",
            "finishing_score",
            "pressing_score",
            "defensive_score",
            "ball_security_score",
            "aerial_score",
        ]
        if str(player.get("position_group")) == "Goalkeeper":
            contribution_metrics = [
                "post_shot_xg_proxy",
                "psxg_ga_p90",
                "goals_prevented_proxy_p90",
                "save_rate",
                "save_rate_shrunk",
                "high_leverage_save_pct",
                "high_leverage_save_rate_shrunk",
                "penalties_saved_rate",
                "penalty_save_rate_shrunk",
                "shootout_penalties_faced",
                "shootout_penalties_saved",
                "claims_p90",
                "cross_stopping_rate",
                "sweeper_actions_p90",
                "distribution_under_pressure",
                "gk_raw_rating_v2",
                "tournament_impact_score",
                "gk_score_composite",
                "reliability_factor",
                "gk_rating_v2",
            ]
        else:
            contribution_metrics = [
                "vaep_off_scaled",
                "vaep_def_scaled",
                "vaep_per_touch",
                "open_play_xt_p90",
                "set_piece_xt_p90",
                "role_adjusted_value",
                "completeness_score",
                "off_ball_score",
            ]
        contextual_metrics = [
            "sb360_coverage",
            "mean_defenders_within_3m",
            "mean_defenders_within_5m",
            "mean_nearest_defender_m",
            "mean_passing_lane_availability",
            "packing_index_mean",
            "mean_space_received",
            "network_pagerank",
            "network_betweenness",
            "network_entropy",
            "build_up_involvement_ratio",
        ]

        def metric_table(names: list[str]) -> pd.DataFrame:
            return pd.DataFrame(
                {
                    "metric": names,
                    "value": [value(name) for name in names],
                }
            )

        return (
            re.sub(
                r"\n{3,}",
                "\n\n",
                "\n".join(
            [
                f"# {value('player_name')} Player Profile",
                "",
                "This report uses tournament events and coverage-qualified "
                "StatsBomb 360 context. It is not an optical-tracking report "
                "or a subjective scouting grade.",
                "",
                "## Ranking and role",
                "",
                f"- Team: {value('team')}",
                f"- Tournament: {value('tournament')}",
                f"- Formal 360 position group: "
                f"{value('position_group_360')}",
                f"- Position group: {value('position_group')}",
                f"- Functional role: {value('functional_role')}",
                f"- Source functional role: "
                f"{value('functional_role_original')}",
                (
                    f"- Team main goalkeeper: "
                    f"{value('is_main_goalkeeper')}"
                    if str(player.get("position_group_360")) == "GK"
                    else ""
                ),
                f"- Probabilistic role: {value('probabilistic_role')}",
                f"- Role entropy: {value('role_entropy')}",
                (
                    f"- Unified global rank: {value('Global Rank', 0)}"
                    if pd.notna(player.get("Global Rank"))
                    else "- Unified global rank: not ranked"
                ),
                (
                    f"- Unified team rank: {value('Team Rank', 0)}"
                    if pd.notna(player.get("Team Rank"))
                    else "- Unified team rank: not ranked"
                ),
                (
                    "- Tournament Performance Score: "
                    f"{value('Tournament Performance Score')}"
                ),
                (
                    f"- Goalkeeper rank v2: "
                    f"{value('gk_rank_v2', 0)}"
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Global rank v2: "
                    f"{value('global_rank_v2', 0)}"
                ),
                (
                    f"- Goalkeeper rating v2: {value('gk_rating_v2')}"
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Position rank v2: "
                    f"{value('position_rank_v2', 0)}"
                ),
                (
                    ""
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Role rank v2: {value('role_rank_v2', 0)}"
                ),
                (
                    ""
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Team rank v2: {value('team_rank_v2', 0)}"
                ),
                (
                    ""
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Final player rating v2: "
                    f"{value('final_player_rating_v2')}"
                ),
                (
                    ""
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Global rank: {value('global_rank', 0)}"
                ),
                (
                    ""
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Position rank: {value('position_rank', 0)}"
                ),
                (
                    ""
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Role rank: {value('role_rank', 0)}"
                ),
                (
                    ""
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Team rank: {value('team_rank', 0)}"
                ),
                (
                    ""
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Final player rating: "
                    f"{value('final_player_rating')}"
                ),
                (
                    ""
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Ranking status: {value('RankingStatus')}"
                ),
                (
                    f"- Goalkeeper ranking status: "
                    f"{value('GKRankingStatus')}"
                    if str(player.get("position_group")) == "Goalkeeper"
                    else ""
                ),
                (
                    "- Global ranking eligibility: goalkeeper-only ranking"
                    if str(player.get("position_group")) == "Goalkeeper"
                    else "- Global ranking eligibility: eligible"
                ),
                f"- Minutes: {value('minutes', 1)}",
                (
                    f"- Goalkeeper v2 reliability: "
                    f"{value('reliability_factor')}"
                    if str(player.get("position_group_360")) == "GK"
                    else f"- Minutes reliability: "
                    f"{value('rating_minutes_reliability')}"
                ),
                "",
                "## Rating components",
                "",
                _markdown_table(
                    metric_table(contribution_metrics),
                    ["metric", "value"],
                ),
                "",
                "## Continuous role vector",
                "",
                _markdown_table(
                    metric_table(role_dimensions),
                    ["metric", "value"],
                ),
                "",
                "## Spatial, 360 and passing-network context",
                "",
                _markdown_table(
                    metric_table(contextual_metrics),
                    ["metric", "value"],
                ),
                "",
                "Missing values indicate unavailable evidence; they are not "
                "converted into zero contribution.",
                "",
            ]
                ).rstrip(),
            )
            + "\n"
        )

    @staticmethod
    def _final_summary(
        rankings: pd.DataFrame,
        model_summary: dict[str, Any],
        *,
        teams: Sequence[str],
        team_metrics: pd.DataFrame | None = None,
        team_player_pool: pd.DataFrame | None = None,
    ) -> str:
        """Render the complete tournament, player, and all-team summary."""

        has_v2 = {
            "position_group_360",
            "global_rank_v2",
            "final_player_rating_v2",
            "gk_rank_v2",
            "gk_rating_v2",
        } <= set(rankings)
        has_unified = {
            "Global Rank",
            "Team Rank",
            "Tournament Performance Score",
        } <= set(rankings)
        unified_top = (
            rankings.loc[
                rankings["Tournament Performance Score"].notna()
            ]
            .sort_values(["Global Rank", "player_name"])
            .head(10)
            if has_unified
            else pd.DataFrame()
        )
        v2_outfield = (
            rankings.loc[rankings["position_group_360"].ne("GK")]
            .sort_values("global_rank_v2")
            .head(10)
            if has_v2
            else pd.DataFrame()
        )
        v2_goalkeepers = (
            rankings.loc[
                rankings["position_group_360"].eq("GK")
                & rankings["gk_rank_v2"].notna()
            ]
            .sort_values("gk_rank_v2")
            .head(5)
            if has_v2
            else pd.DataFrame()
        )
        if team_player_pool is None:
            team_player_pool = rankings.assign(
                selection_priority=0,
                ranking_status="Ranked (300+ min)",
            )
            if "minutes" not in team_player_pool:
                team_player_pool["minutes"] = np.nan
        comparison = pd.DataFrame()
        if has_unified:
            primary_rankings = (
                rankings.loc[
                    rankings["Tournament Performance Score"].notna()
                ]
                .sort_values(["Global Rank", "player_name"])
            )
            overall_columns = [
                "Global Rank",
                "Team Rank",
                "player_name",
                "team",
                "position_group_360",
                "functional_role",
                "Tournament Performance Score",
            ]
            position_leaders = (
                rankings.loc[rankings["position_group_360"].ne("GK")]
                .sort_values(
                    [
                        "position_group_360",
                        "position_rank_v2",
                        "Global Rank",
                    ]
                )
                .groupby("position_group_360", sort=True)
                .head(5)
            )
            position_columns = [
                "position_group_360",
                "position_rank_v2",
                "player_name",
                "team",
                "functional_role",
                "Tournament Performance Score",
            ]
        elif has_v2:
            comparison = rankings.loc[
                rankings["global_rank_v2"].notna()
                & rankings["global_rank"].notna()
            ].copy()
            comparison["old_global_rank"] = pd.to_numeric(
                comparison["global_rank"],
                errors="coerce",
            ).astype(int)
            comparison["new_global_rank"] = pd.to_numeric(
                comparison["global_rank_v2"],
                errors="coerce",
            ).astype(int)
            comparison["rank_improvement"] = (
                comparison["old_global_rank"]
                - comparison["new_global_rank"]
            )
        elif "legacy_final_player_rating" in rankings:
            comparison = rankings.loc[
                rankings["global_rank"].notna()
            ].assign(
                old_global_rank=rankings[
                    "legacy_final_player_rating"
                ].loc[rankings["global_rank"].notna()]
                .rank(method="min", ascending=False)
                .astype(int),
                new_global_rank=rankings.loc[
                    rankings["global_rank"].notna(),
                    "global_rank",
                ].astype(int),
            )
            comparison["rank_improvement"] = (
                comparison["old_global_rank"]
                - comparison["new_global_rank"]
            )
        over = (
            comparison.nlargest(10, "rank_improvement")
            if not comparison.empty
            else pd.DataFrame()
        )
        under = (
            comparison.nsmallest(10, "rank_improvement")
            if not comparison.empty
            else pd.DataFrame()
        )
        columns = [
            "player_name",
            "team",
            "old_global_rank",
            "new_global_rank",
            "rank_improvement",
        ]
        if has_v2:
            primary_rankings = (
                rankings.loc[
                    rankings["position_group_360"].ne("GK")
                    & pd.to_numeric(
                        rankings["minutes_played"],
                        errors="coerce",
                    ).ge(300.0)
                ]
                .sort_values("global_rank_v2")
            )
            overall_columns = [
                "global_rank_v2",
                "player_name",
                "team",
                "position_group_360",
                "functional_role",
                "final_player_rating_v2",
            ]
            position_leaders = (
                rankings.loc[rankings["position_group_360"].ne("GK")]
                .sort_values(
                    [
                        "position_group_360",
                        "position_rank_v2",
                        "global_rank_v2",
                    ]
                )
                .groupby("position_group_360", sort=True)
                .head(5)
            )
            position_columns = [
                "position_group_360",
                "position_rank_v2",
                "player_name",
                "team",
                "functional_role",
                "final_player_rating_v2",
            ]
        else:
            primary_rankings = rankings.loc[
                (
                    ~rankings["position_group"].eq("Goalkeeper")
                    & rankings["RankingStatus"].eq("Ranked (300+ min)")
                )
                | (
                    rankings["position_group"].eq("Goalkeeper")
                    & rankings["GKRankingStatus"].eq("Ranked (270+ min)")
                )
            ]
            overall_columns = [
                "global_rank",
                "player_name",
                "team",
                "position_group",
                "functional_role",
                "final_player_rating",
            ]
            position_leaders = (
                primary_rankings.sort_values(
                    ["position_group", "position_rank", "global_rank"]
                )
                .groupby("position_group", sort=True)
                .head(5)
            )
            position_columns = [
                "position_group",
                "position_rank",
                "player_name",
                "team",
                "functional_role",
                "final_player_rating",
            ]
        team_lookup: dict[str, pd.Series] = {}
        if team_metrics is not None and "team" in team_metrics:
            team_lookup = {
                str(row["team"]): row
                for _, row in team_metrics.iterrows()
            }

        def team_value(team: str, metric: str) -> str:
            row = team_lookup.get(team)
            if row is None or metric not in row or pd.isna(row[metric]):
                return "not available"
            return f"{float(row[metric]):.4f}"

        overview_records = []
        for team in teams:
            players = rankings.loc[rankings["team"].eq(team)].sort_values(
                (
                    "Team Rank"
                    if has_unified
                    else "team_rank_v2"
                    if has_v2
                    else "team_rank"
                ),
                na_position="last",
            )
            covered = (
                players.loc[
                    players["Tournament Performance Score"].notna()
                ]
                if has_unified
                else players.loc[players["position_group_360"].ne("GK")]
                if has_v2
                else team_player_pool.loc[
                    team_player_pool["team"].eq(team)
                ].sort_values(
                    ["selection_priority", "team_rank", "minutes"],
                    ascending=[True, True, False],
                    na_position="last",
                )
            )
            leader = covered.iloc[0] if not covered.empty else None
            overview_records.append(
                {
                    "team": team,
                    "eligible_players": len(players),
                    "observed_players": len(covered),
                    "top_ranked_player": (
                        str(leader["player_name"])
                        if leader is not None
                        else "No observed player"
                    ),
                    "top_global_rank": (
                        int(
                            leader[
                                "Global Rank"
                                if has_unified
                                else "global_rank_v2"
                                if has_v2
                                else "global_rank"
                            ]
                        )
                        if leader is not None
                        and pd.notna(
                            leader[
                                "Global Rank"
                                if has_unified
                                else "global_rank_v2"
                                if has_v2
                                else "global_rank"
                            ]
                        )
                        else "Not globally ranked"
                    ),
                    "total_xt": team_value(team, "total_xt_created"),
                    "pressure_resistance": team_value(
                        team,
                        "pressure_resistance_rate",
                    ),
                    "mean_creation": team_value(
                        team,
                        "mean_creation_score",
                    ),
                    "mean_defensive": team_value(
                        team,
                        "mean_defensive_score",
                    ),
                    "mean_ball_security": team_value(
                        team,
                        "mean_ball_security_score",
                    ),
                }
            )
        context_selection = (
            model_summary.get("metrics", {})
            .get("contextual_vaep_gate", {})
            .get("selected_feature_set", "baseline")
        )
        overall_leaders = (
            primary_rankings.head(20)
            if has_v2 or has_unified
            else primary_rankings.sort_values(
                ["primary_global_rank", "primary_goalkeeper_rank"],
                na_position="last",
            ).head(20)
        )
        lines = [
            "# 2022 FIFA World Cup Player Ranking Report",
            "",
            "## Executive summary",
            "",
            f"This report consolidates **{len(teams)} national teams** and "
            f"**{len(rankings)} eligible rated players** (outfield 45+ "
            "minutes; goalkeepers 90+). "
            "It uses StatsBomb events, lineups, minutes, and coverage-qualified "
            "360 freeze frames. It does not use optical tracking, external "
            "ratings, or player-name adjustments.",
            "",
            (
                "The position-aware tournament rankings are stored under "
                "`results/reports/ranking/`. They add formal 360 groups while "
                "preserving the source position and role detail."
                if has_v2
                else ""
            ),
            "",
            "## Global top 10 players - unified tournament rating",
            "",
            (
                _markdown_table(
                    unified_top,
                    [
                        "Global Rank",
                        "Team Rank",
                        "player_name",
                        "team",
                        "position_group_360",
                        "functional_role",
                        "Tournament Performance Score",
                    ],
                )
                if has_unified
                else "_Unified tournament ranking was not available._"
            ),
            "",
            "## Global top five goalkeepers — tournament ranking v2",
            "",
            (
                _markdown_table(
                    v2_goalkeepers,
                    [
                        "gk_rank_v2",
                        "player_name",
                        "team",
                        "gk_rating_v2",
                    ],
                )
                if has_v2
                else "_Tournament goalkeeper ranking v2 was not available._"
            ),
            "",
            f"The active contribution layer is "
            f"`{model_summary.get('selected_layer', 'unknown')}`. The "
            "experimental attention challenger remains available but affects "
            "rankings only when it passes its match-disjoint metric gate.",
            "",
            "## How to read the player rating",
            "",
            f"The preserved V5 contribution score uses the development-gated "
            f"{context_selection} VAEP feature set and grouped "
            "ElasticNet offense/defense heads with explicit role weights, "
            "VAEP/touch, open-play and set-piece-aware xT, sample-adjusted "
            "completeness, coverage-qualified off-ball value, and xD-style "
            "defensive disruption. Positive ElasticNet calibration selects "
            "the composite weights with team-disjoint folds, followed by "
            "minutes/(minutes+450) position-prior shrinkage.",
            "",
            "The tournament ranking v2 adds explicit goals, xG, shots, xA, "
            "chance creation, progression, possession, defending, and "
            "off-ball components normalized within `position_group_360`. "
            "A capped, general role-based finishing treatment corrects the "
            "structural penalty on goal-centric forwards; it never checks "
            "player names.",
            "",
            "Goalkeepers use a separate tournament-v2 matrix led by a "
            "match-disjoint PSxG-GA proxy, reliability-shrunk save rates, "
            "penalty performance, box command, sweeping, distribution under "
            "pressure, and an explicit shootout-impact term. Their dedicated "
            "goalkeeper order is mapped into the unified table through a "
            "finite-sample Blom empirical-quantile bridge against the outfield "
            "score distribution. This preserves goalkeeper order without "
            "turning the maximum of a 32-player cohort into an automatic "
            "global podium place. "
            "Missing 360 evidence remains missing, and role labels never "
            "award rating points.",
            "",
            "## General player summary",
            "",
            "### Overall leaders",
            "",
            _markdown_table(
                overall_leaders,
                overall_columns,
            ),
            "",
            "### Position-group leaders",
            "",
            _markdown_table(
                position_leaders,
                position_columns,
            ),
            "",
            "### Largest upward rank movements",
            "",
            _markdown_table(over, columns),
            "",
            "### Largest downward rank movements",
            "",
            _markdown_table(under, columns),
            "",
            (
                "Rank movement compares the prior global ordering with "
                "tournament ranking v2 ordering; it does not compare raw "
                "rating magnitudes."
                if has_v2
                else "Rank movement compares ordering, not raw rating "
                "differences."
            ),
            "",
            "## All-team overview",
            "",
            _markdown_table(
                pd.DataFrame(overview_records),
                [
                    "team",
                    "eligible_players",
                    "observed_players",
                    "top_ranked_player",
                    "top_global_rank",
                    "total_xt",
                    "pressure_resistance",
                    "mean_creation",
                    "mean_defensive",
                    "mean_ball_security",
                ],
            ),
            "",
            "# Team-by-team summary",
            "",
            "Scope note: every team top five below uses the unified tournament "
            "score and includes the ranked team-main goalkeeper when that "
            "score places the goalkeeper in the top five. Backup goalkeepers "
            "remain unranked.",
            "",
        ]
        for team in teams:
            players = rankings.loc[rankings["team"].eq(team)].sort_values(
                (
                    "Team Rank"
                    if has_unified
                    else "team_rank_v2"
                    if has_v2
                    else "team_rank"
                ),
                na_position="last",
            )
            if has_unified:
                covered = (
                    players.loc[
                        players["Tournament Performance Score"].notna()
                    ]
                    .sort_values("Team Rank")
                    .head(5)
                )
                summary_columns = [
                    "Team Rank",
                    "Global Rank",
                    "player_name",
                    "position_group_360",
                    "functional_role",
                    "minutes_played",
                    "Tournament Performance Score",
                ]
            elif has_v2:
                covered = (
                    players.loc[players["position_group_360"].ne("GK")]
                    .sort_values("team_rank_v2")
                    .head(5)
                )
                summary_columns = [
                    "team_rank_v2",
                    "global_rank_v2",
                    "player_name",
                    "position_group_360",
                    "functional_role",
                    "minutes_played",
                    "final_player_rating_v2",
                ]
            else:
                covered = team_player_pool.loc[
                    team_player_pool["team"].eq(team)
                ].sort_values(
                    ["selection_priority", "team_rank", "minutes"],
                    ascending=[True, True, False],
                    na_position="last",
                ).head(5)
                summary_columns = [
                    "team_rank",
                    "global_rank",
                    "player_name",
                    "position_group",
                    "functional_role",
                    "minutes",
                    "final_player_rating",
                    "ranking_status",
                ]
            lines.extend(
                [
                    f"## {team}",
                    "",
                    f"- Total xT created: "
                    f"{team_value(team, 'total_xt_created')}",
                    f"- Total xA created: "
                    f"{team_value(team, 'total_xa_created')}",
                    f"- Pass completion under pressure: "
                    f"{team_value(team, 'pressure_resistance_rate')}",
                    f"- Mean defensive hull area: "
                    f"{team_value(team, 'defensive_hull_area')}",
                    f"- Mean defensive density: "
                    f"{team_value(team, 'defensive_density')}",
                    "",
                    "### Top five unified player summary",
                    "",
                ]
            )
            if covered.empty:
                lines.extend(
                    [
                        "_No player observations were available._",
                        "",
                    ]
                )
            else:
                lines.extend(
                    [
                        _markdown_table(
                            covered,
                            summary_columns,
                        ),
                        (
                            "_Coverage-only names are selected by tournament "
                            "minutes and receive no model rating or implied "
                            "rank._"
                            if players.empty
                            else ""
                        ),
                        "",
                    ]
                )
        lines.extend(
            [
                "## Interpretation boundary",
                "",
                "These rankings summarize performance in the 2022 tournament "
                "sample. They are not transfer valuations, causal estimates, "
                "medical assessments, or replacements for video and scouting "
                "review.",
                "",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _v2_player_reason(player: pd.Series) -> str:
        """Explain a high rank using only measured v2 component evidence."""

        labels = {
            "finishing_component_v2": (
                "penalty-box finishing and shot-quality output"
            ),
            "creation_component_v2": (
                "chance creation and final-third passing"
            ),
            "progression_component_v2": (
                "progressive passing and carrying"
            ),
            "possession_component_v2": "ball security and possession value",
            "defending_component_v2": (
                "ball-winning and defensive contribution"
            ),
            "off_ball_component_v2": (
                "coverage-qualified off-ball contribution"
            ),
            "tournament_impact_component_v2": (
                "total tournament goals/xG/xA/VAEP/xT impact"
            ),
        }
        measured = [
            (column, float(player[column]))
            for column in labels
            if column in player and pd.notna(player[column])
        ]
        measured.sort(key=lambda item: item[1], reverse=True)
        strongest = measured[:2]
        if not strongest:
            return (
                "The ranking reflects the available Qatar 2022 contribution "
                "profile and sample-size reliability."
            )
        evidence = " and ".join(
            f"{labels[column]} ({value:.0%} within the model context)"
            for column, value in strongest
        )
        return (
            f"As a {player.get('functional_role', 'tournament role')}, the "
            f"strongest measured signals are {evidence}. The assessment uses "
            "Qatar 2022 evidence only."
        )

    @staticmethod
    def _team_profile(
        team: str,
        players: pd.DataFrame,
        covered_players: pd.DataFrame,
        team_metrics: pd.Series | None = None,
    ) -> str:
        """Render one team's required tactical and squad sections."""

        def mean(metric: str) -> str:
            aggregate_metric = {
                "creation_score": "mean_creation_score",
                "defensive_score": "mean_defensive_score",
                "ball_security_score": "mean_ball_security_score",
            }.get(metric)
            if (
                aggregate_metric is not None
                and team_metrics is not None
                and aggregate_metric in team_metrics
                and pd.notna(team_metrics[aggregate_metric])
            ):
                return f"{float(team_metrics[aggregate_metric]):.4f}"
            if metric not in players or not players[metric].notna().any():
                return "not available"
            return f"{players[metric].mean():.4f}"

        def team_value(metric: str) -> str:
            if (
                team_metrics is None
                or metric not in team_metrics
                or pd.isna(team_metrics[metric])
            ):
                return "not available"
            return f"{float(team_metrics[metric]):.4f}"

        has_v2 = {
            "position_group_360",
            "team_rank_v2",
            "final_player_rating_v2",
            "gk_rank_v2",
            "gk_rating_v2",
        } <= set(players)
        has_unified = {
            "Global Rank",
            "Team Rank",
            "Tournament Performance Score",
        } <= set(players)
        if has_v2:
            outfield = (
                players.loc[players["position_group_360"].ne("GK")]
                .sort_values(
                    [
                        "Team Rank" if has_unified else "team_rank_v2",
                        "player_name",
                    ]
                )
            )
            goalkeepers = (
                players.loc[players["position_group_360"].eq("GK")]
                .sort_values(
                    [
                        "Team Rank" if has_unified else "gk_rank_v2",
                        "player_name",
                    ],
                    na_position="last",
                )
            )
            top_five = (
                players.loc[
                    players["Tournament Performance Score"].notna()
                ]
                .sort_values(["Team Rank", "player_name"])
                .head(5)
                if has_unified
                else outfield.head(5)
            )
            top_five_lines: list[str] = []
            for _, player in top_five.iterrows():
                rank = int(
                    player["Team Rank"]
                    if has_unified
                    else player["team_rank_v2"]
                )
                rating = float(
                    player["Tournament Performance Score"]
                    if has_unified
                    else player["final_player_rating_v2"]
                )
                top_five_lines.extend(
                    [
                        f"{rank}. "
                        f"**{player['player_name']}** — "
                        f"{player['position_group_360']}, "
                        f"{player['functional_role']} "
                        f"({rating:.4f})",
                        "",
                        ArtifactGenerator._v2_player_reason(player),
                        "",
                    ]
                )
            top_five_content = (
                "\n".join(top_five_lines).rstrip()
                if top_five_lines
                else "_No eligible outfield ranking._"
            )
            full_outfield_table = _markdown_table(
                outfield,
                [
                    "Team Rank" if has_unified else "team_rank_v2",
                    "Global Rank" if has_unified else "global_rank_v2",
                    "player_name",
                    "position_group_360",
                    "position_group",
                    "functional_role",
                    "minutes_played",
                    (
                        "Tournament Performance Score"
                        if has_unified
                        else "final_player_rating_v2"
                    ),
                ],
            )
            goalkeeper_table = _markdown_table(
                goalkeepers,
                [
                    "gk_rank_v2",
                    "Team Rank" if has_unified else "team_rank_v2",
                    "Global Rank" if has_unified else "global_rank_v2",
                    "player_name",
                    "is_main_goalkeeper",
                    "GKRankingStatus",
                    "position_group_360",
                    "position_group",
                    "functional_role",
                    "minutes_played",
                    "gk_rating_v2",
                    (
                        "Tournament Performance Score"
                        if has_unified
                        else "final_player_rating_v2"
                    ),
                ],
            )
        else:
            top_five_content = _markdown_table(
                covered_players.sort_values(
                    ["selection_priority", "team_rank", "minutes"],
                    ascending=[True, True, False],
                    na_position="last",
                ).head(5),
                [
                    "team_rank",
                    "player_name",
                    "functional_role",
                    "minutes",
                    "final_player_rating",
                    "ranking_status",
                ],
            )
            if players.empty and not covered_players.empty:
                top_five_content += (
                    "\n\n_Coverage-only players are ordered by tournament "
                    "minutes. No model rating assigned._"
                )
            full_outfield_table = "_Tournament ranking v2 was not available._"
            goalkeeper_table = "_Tournament goalkeeper ranking v2 was not available._"

        return (
            "\n".join(
                [
                f"# {team} Team Profile",
                "",
                "## Threat creation",
                "",
                f"- Total xT created: {team_value('total_xt_created')}",
                f"- Total xA created: {team_value('total_xa_created')}",
                f"- Mean creation score: {mean('creation_score')}",
                f"- Mean creation score (300+ comparison): "
                f"{team_value('mean_creation_score_ranked_300')}",
                f"- Mean xT/90: {mean('xt_p90')}",
                "",
                "## Defensive compactness",
                "",
                f"- Mean defensive hull area: "
                f"{team_value('defensive_hull_area')}",
                f"- Mean defensive density: "
                f"{team_value('defensive_density')}",
                f"- Mean defensive width: "
                f"{team_value('defensive_width')}",
                f"- Mean defensive depth: "
                f"{team_value('defensive_depth')}",
                f"- Mean defensive score: {mean('defensive_score')}",
                f"- Mean defensive score (300+ comparison): "
                f"{team_value('mean_defensive_score_ranked_300')}",
                f"- Mean xD/90: {team_value('mean_xd90')}",
                f"- Mean shape-maintenance score: "
                f"{mean('shape_maintenance_score')}",
                "",
                "## Pressure resistance",
                "",
                f"- Pass completion under pressure: "
                f"{team_value('pressure_resistance_rate')}",
                f"- Pressured pass sample: "
                f"{team_value('pressured_passes')}",
                f"- Mean ball-security score: {mean('ball_security_score')}",
                f"- Mean ball-security score (300+ comparison): "
                f"{team_value('mean_ball_security_score_ranked_300')}",
                "",
                "## Top 5 Players",
                "",
                top_five_content,
                "",
                "The top five above use the unified within-team rank and can "
                "include the ranked team-main goalkeeper. The goalkeeper-only "
                "section retains the dedicated goalkeeper rank and the "
                "cross-position calibrated tournament score; backups remain "
                "listed as unranked.",
                "",
                "## Full Player List — Outfield",
                "",
                full_outfield_table,
                "",
                "## Full Player List — Goalkeepers",
                "",
                goalkeeper_table,
                "",
                ]
            ).rstrip()
            + "\n"
        )

    def _generate_figures(
        self,
        rankings: pd.DataFrame,
        model_summary: dict[str, Any],
    ) -> list[Path]:
        """Generate rating-dependent V5 figures with deterministic styling."""

        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figure_root = self.output_root / "v5_figures"
        figure_root.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []

        def save(figure: Any, name: str) -> None:
            path = figure_root / name
            descriptor, temporary_name = tempfile.mkstemp(
                dir=figure_root,
                prefix=f".{name}.",
                suffix=".png",
            )
            os.close(descriptor)
            temporary = Path(temporary_name)
            try:
                figure.savefig(
                    temporary,
                    dpi=180,
                    bbox_inches="tight",
                    facecolor="white",
                )
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
                plt.close(figure)
            generated.append(path)

        has_v2 = "global_rank_v2" in rankings
        has_unified = {
            "Global Rank",
            "Team Rank",
            "Tournament Performance Score",
        }.issubset(rankings.columns)
        rank_column = (
            "Global Rank"
            if has_unified
            else ("global_rank_v2" if has_v2 else "global_rank")
        )
        rating_column = (
            "Tournament Performance Score"
            if has_unified
            else (
                "final_player_rating_v2"
                if has_v2
                else "final_player_rating"
            )
        )
        leaders = (
            rankings.loc[
                rankings[rank_column].notna()
                & rankings[rating_column].notna()
            ]
            .sort_values(rank_column)
            .head(20)
        )
        figure, axis = plt.subplots(figsize=(10, 7))
        axis.barh(
            leaders["player_name"].iloc[::-1],
            leaders[rating_column].iloc[::-1],
            color="#295f98",
        )
        axis.set_xlabel(
            "Unified tournament performance score"
            if has_unified
            else "V5 final player rating"
        )
        axis.set_title(
            "2022 World Cup — unified tournament leaders"
            if has_unified
            else "2022 World Cup — V5 outfield leaders"
        )
        if has_unified and not leaders.empty:
            lower = max(
                0.0,
                float(leaders[rating_column].min()) - 0.005,
            )
            axis.set_xlim(lower, 1.002)
            axis.bar_label(
                axis.containers[0],
                labels=[
                    f"{value:.4f}"
                    for value in leaders[rating_column].iloc[::-1]
                ],
                padding=3,
                fontsize=8,
            )
        axis.grid(axis="x", alpha=0.2)
        save(figure, "v5_global_outfield_rankings.png")

        france_mask = rankings["team"].eq("France")
        if has_unified:
            france_mask &= rankings[rating_column].notna()
        france = rankings.loc[france_mask].sort_values(
            (
                "Team Rank"
                if has_unified
                else ("team_rank_v2" if has_v2 else "team_rank")
            ),
            na_position="last",
        )
        if not france.empty:
            figure, axis = plt.subplots(figsize=(10, 6))
            axis.barh(
                france["player_name"].iloc[::-1],
                (
                    france[rating_column]
                    if has_unified
                    else france[
                        "final_player_rating_v2"
                        if has_v2
                        else "final_player_rating"
                    ].fillna(
                        france.get(
                            "gk_rating_v2",
                            pd.Series(index=france.index),
                        )
                        if has_v2
                        else np.nan
                    )
                ).iloc[::-1],
                color="#264653",
            )
            axis.set_xlabel(
                "Unified tournament performance score"
                if has_unified
                else "V5 final player rating"
            )
            axis.set_title(
                "France — unified squad ranking"
                if has_unified
                else "France — updated V5 squad ranking"
            )
            axis.grid(axis="x", alpha=0.2)
            save(figure, "v5_france_team_rankings.png")

        goalkeepers = rankings.loc[
            rankings["position_group"].eq("Goalkeeper")
            & (
                rankings["gk_rank_v2"].notna()
                if has_v2
                else pd.Series(True, index=rankings.index)
            )
        ].sort_values("gk_rank_v2" if has_v2 else "position_rank")
        if not goalkeepers.empty:
            figure, axis = plt.subplots(figsize=(10, 6))
            axis.barh(
                goalkeepers["player_name"].iloc[::-1],
                goalkeepers[
                    "gk_rating_v2" if has_v2 else "final_player_rating"
                ].iloc[::-1],
                color="#2a9d8f",
            )
            axis.set_xlabel("Goalkeeper-only reliability-shrunk rating")
            axis.set_title("2022 World Cup — V5 goalkeeper ranking")
            axis.grid(axis="x", alpha=0.2)
            save(figure, "v5_goalkeeper_rankings.png")

        coefficients = (
            model_summary.get("feature_importance", {})
            .get("elastic_net_mean_coefficients", {})
        )
        if coefficients:
            series = pd.Series(coefficients, dtype=float)
            series = series.reindex(
                series.abs().sort_values(ascending=False).index
            ).head(15)
            figure, axis = plt.subplots(figsize=(10, 6))
            axis.barh(
                series.index[::-1],
                series.iloc[::-1],
                color="#e76f51",
            )
            axis.set_xlabel("Mean standardized ElasticNet coefficient")
            axis.set_title("V5 grouped valuation feature importance")
            axis.grid(axis="x", alpha=0.2)
            save(figure, "v5_elasticnet_coefficients.png")
        return generated

    def generate(
        self,
        players: pd.DataFrame,
        *,
        model_summary: dict[str, Any],
        validation_comparison: pd.DataFrame | None = None,
        tournament_teams: Sequence[str] | None = None,
        team_metrics: pd.DataFrame | None = None,
        team_player_pool: pd.DataFrame | None = None,
    ) -> ArtifactManifest:
        """Generate all requested artifacts in one atomic execution."""

        rankings = self.prepare_rankings(players)
        ranked_teams = sorted(
            rankings["team"].dropna().astype(str).unique()
        )
        teams = sorted(
            {str(team) for team in tournament_teams}
            if tournament_teams is not None
            else ranked_teams
        )
        if not set(ranked_teams) <= set(teams):
            raise ValueError("Tournament team manifest omits a ranked team")
        if len(teams) != self.expected_team_count:
            raise ValueError(
                f"Expected {self.expected_team_count} teams, found {len(teams)}"
            )
        if team_player_pool is None:
            coverage = rankings.copy()
            if "minutes" not in coverage:
                coverage["minutes"] = np.nan
        else:
            required_coverage = {
                "player_name",
                "team",
                "position_group",
                "minutes",
            }
            missing_coverage = required_coverage.difference(
                team_player_pool.columns
            )
            if missing_coverage:
                raise ValueError(
                    "Team player pool missing: "
                    f"{sorted(missing_coverage)}"
                )
            coverage = team_player_pool.copy()
            join_columns = (
                ["player_id", "team"]
                if "player_id" in coverage and "player_id" in rankings
                else ["player_name", "team"]
            )
            rated_columns = list(
                dict.fromkeys(
                    [
                        *join_columns,
                        *[
                            column
                            for column in (
                                "team_rank",
                                "global_rank",
                                "functional_role",
                                "final_player_rating",
                                "position_group_360",
                                "final_player_rating_v2",
                                "global_rank_v2",
                                "team_rank_v2",
                                "gk_rating_v2",
                                "gk_rank_v2",
                                "RankingStatus",
                                "GKRankingStatus",
                            )
                            if column in rankings
                        ],
                    ]
                )
            )
            coverage = coverage.merge(
                rankings[rated_columns],
                on=join_columns,
                how="left",
                validate="one_to_one",
            )
        for column in (
            "team_rank",
            "global_rank",
            "functional_role",
            "final_player_rating",
            "position_group_360",
            "final_player_rating_v2",
            "global_rank_v2",
            "team_rank_v2",
            "gk_rating_v2",
            "gk_rank_v2",
        ):
            if column not in coverage:
                coverage[column] = np.nan
        coverage_minutes = pd.to_numeric(
            coverage["minutes"],
            errors="coerce",
        )
        computed_outfield_status = np.select(
            [
                coverage_minutes.ge(300.0),
                coverage_minutes.ge(180.0),
            ],
            [
                "Ranked (300+ min)",
                "Ranked (180–299 min)",
            ],
            default="Coverage only (<180 min)",
        )
        computed_goalkeeper_status = np.select(
            [
                coverage_minutes.ge(270.0),
                coverage_minutes.ge(180.0),
            ],
            [
                "Ranked (270+ min)",
                "Ranked (180–269 min)",
            ],
            default="Coverage only (<180 min)",
        )
        coverage["ranking_status"] = np.where(
            coverage["position_group"].eq("Goalkeeper"),
            coverage.get(
                "GKRankingStatus",
                pd.Series(pd.NA, index=coverage.index),
            ).fillna(
                pd.Series(computed_goalkeeper_status, index=coverage.index)
            ),
            coverage.get(
                "RankingStatus",
                pd.Series(pd.NA, index=coverage.index),
            ).fillna(
                pd.Series(computed_outfield_status, index=coverage.index)
            ),
        )
        coverage["ranking_status"] = coverage["ranking_status"].fillna(
            "Coverage only (<180 min)"
        )
        coverage["selection_priority"] = (
            coverage["ranking_status"]
            .map(
                {
                    "Ranked (300+ min)": 0,
                    "Ranked (270+ min)": 0,
                    "Ranked (180–299 min)": 1,
                    "Ranked (180–269 min)": 1,
                    "Coverage only (<180 min)": 2,
                }
            )
            .fillna(3)
            .astype(int)
        )
        if not set(coverage["team"].dropna().astype(str)) <= set(teams):
            raise ValueError("Team player pool contains an unknown team")
        files: list[Path] = self._write_ranking_artifacts(rankings)
        team_metric_lookup: dict[str, pd.Series] = {}
        if team_metrics is not None:
            if "team" not in team_metrics:
                raise ValueError("Team metrics require a team column")
            if team_metrics["team"].duplicated().any():
                raise ValueError("Team metrics require unique teams")
            team_metric_lookup = {
                str(row["team"]): row
                for _, row in team_metrics.iterrows()
            }

        notebook = self._coaches_notebook(rankings)
        for name in ("v5_coaches_notebook.md", "coaches_notebook.md"):
            path = self.output_root / name
            _atomic_text(path, notebook)
            files.append(path)

        summary_payload = {
            "schema_version": self.schema_version,
            **_json_value(model_summary),
        }
        model_json_content = (
            json.dumps(summary_payload, indent=2, ensure_ascii=False) + "\n"
        )
        model_markdown_content = self._model_summary_markdown(
            summary_payload
        )
        for name, content in (
            ("model_summary.json", model_json_content),
            ("model_summary.md", model_markdown_content),
        ):
            path = self.output_root / name
            _atomic_text(path, content)
            files.append(path)

        final_content = self._final_summary(
            rankings,
            summary_payload,
            teams=teams,
            team_metrics=team_metrics,
            team_player_pool=coverage,
        )
        final_path = self.output_root / "final_summary.md"
        _atomic_text(final_path, final_content)
        files.append(final_path)

        team_root = self.output_root / "team_profiles"
        for team in teams:
            path = team_root / f"{_slug(team)}.md"
            _atomic_text(
                path,
                self._team_profile(
                    team,
                    rankings.loc[rankings["team"].eq(team)],
                    coverage.loc[coverage["team"].eq(team)],
                    team_metric_lookup.get(team),
                ),
            )
            files.append(path)

        player_paths: set[Path] = set()
        player_root = self.output_root / "player_profiles"
        for _, player in rankings.iterrows():
            identifier = (
                str(int(player["player_id"]))
                if "player_id" in player
                and pd.notna(player["player_id"])
                else str(int(player["position_rank"]))
            )
            path = player_root / (
                f"{_slug(str(player['player_name']))}-{identifier}.md"
            )
            if path in player_paths:
                raise ValueError(f"Duplicate player report path: {path}")
            player_paths.add(path)
            _atomic_text(path, self._player_profile(player))
            files.append(path)

        if validation_comparison is not None:
            required = {
                "player",
                "old_rating",
                "new_rating",
                "rating_difference",
                "functional_role",
            }
            missing = required.difference(validation_comparison.columns)
            if missing:
                raise ValueError(
                    f"Validation comparison missing: {sorted(missing)}"
                )
            comparison_content = validation_comparison.to_csv(index=False)
            for name in (
                "v5_rating_validation_comparison.csv",
                "rating_validation_comparison.csv",
            ):
                comparison_path = self.output_root / name
                _atomic_text(comparison_path, comparison_content)
                files.append(comparison_path)

        files.extend(self._generate_figures(rankings, summary_payload))

        hashes = {
            (
                str(path.relative_to(self.output_root))
                if path.is_relative_to(self.output_root)
                else str(path)
            ): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files
        }
        manifest = ArtifactManifest(
            output_root=self.output_root,
            files=tuple(files),
            hashes=hashes,
            schema_version=self.schema_version,
            metadata={
                "players": len(rankings),
                "teams": len(teams),
                "player_profiles": len(player_paths),
            },
        )
        manifest_content = json.dumps(
            _json_value(manifest),
            indent=2,
        ) + "\n"
        manifest_paths = [
            self.output_root / "v5_artifact_manifest.json",
            self.output_root / "artifact_manifest.json",
        ]
        for manifest_path in manifest_paths:
            _atomic_text(manifest_path, manifest_content)
        return ArtifactManifest(
            output_root=manifest.output_root,
            files=(*manifest.files, *manifest_paths),
            hashes={
                **manifest.hashes,
                **{
                    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in manifest_paths
                },
            },
            schema_version=manifest.schema_version,
            metadata=manifest.metadata,
        )
