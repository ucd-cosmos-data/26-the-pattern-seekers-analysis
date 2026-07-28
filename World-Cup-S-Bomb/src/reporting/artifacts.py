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
)


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
            if isinstance(value, float):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


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
        rankings["global_rank"] = rankings["final_player_rating"].rank(
            method="min",
            ascending=False,
        ).astype(int)
        rankings["position_rank"] = rankings.groupby("position_group")[
            "final_player_rating"
        ].rank(method="min", ascending=False).astype(int)
        rankings["role_rank"] = rankings.groupby("functional_role")[
            "final_player_rating"
        ].rank(method="min", ascending=False).astype(int)
        rankings["team_rank"] = rankings.groupby("team")[
            "final_player_rating"
        ].rank(method="min", ascending=False).astype(int)
        ordered = list(RANKING_SCHEMA) + [
            column for column in rankings if column not in RANKING_SCHEMA
        ]
        return rankings[ordered].sort_values(
            ["global_rank", "player_name"]
        ).reset_index(drop=True)

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
                rankings.head(10),
                [
                    "global_rank",
                    "player_name",
                    "team",
                    "functional_role",
                    "final_player_rating",
                ],
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
        contribution_metrics = [
            "vaep_total_p90",
            "vaep_per_touch",
            "xt_p90",
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

        return "\n".join(
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
                f"- Position group: {value('position_group')}",
                f"- Functional role: {value('functional_role')}",
                f"- Probabilistic role: {value('probabilistic_role')}",
                f"- Role entropy: {value('role_entropy')}",
                f"- Global rank: {value('global_rank', 0)}",
                f"- Position rank: {value('position_rank', 0)}",
                f"- Role rank: {value('role_rank', 0)}",
                f"- Team rank: {value('team_rank', 0)}",
                f"- Final player rating: {value('final_player_rating')}",
                f"- Minutes: {value('minutes', 1)}",
                f"- Minutes reliability: "
                f"{value('rating_minutes_reliability')}",
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
        )

    @staticmethod
    def _final_summary(
        rankings: pd.DataFrame,
        model_summary: dict[str, Any],
        *,
        teams: Sequence[str],
        team_metrics: pd.DataFrame | None = None,
    ) -> str:
        """Render the complete tournament, player, and all-team summary."""

        comparison = pd.DataFrame()
        if "legacy_final_player_rating" in rankings:
            comparison = rankings.assign(
                legacy_global_rank=rankings[
                    "legacy_final_player_rating"
                ]
                .rank(method="min", ascending=False)
                .astype(int)
            )
            comparison["rank_improvement"] = (
                comparison["legacy_global_rank"]
                - comparison["global_rank"]
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
            "legacy_global_rank",
            "global_rank",
            "rank_improvement",
        ]
        position_leaders = (
            rankings.sort_values(
                ["position_group", "position_rank", "global_rank"]
            )
            .groupby("position_group", sort=True)
            .head(5)
        )
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
                "team_rank"
            )
            leader = players.iloc[0] if not players.empty else None
            overview_records.append(
                {
                    "team": team,
                    "eligible_players": len(players),
                    "top_ranked_player": (
                        str(leader["player_name"])
                        if leader is not None
                        else "No player at 300-minute cutoff"
                    ),
                    "top_global_rank": (
                        int(leader["global_rank"])
                        if leader is not None
                        else "—"
                    ),
                    "total_xt": team_value(team, "total_xt_created"),
                    "pressure_resistance": team_value(
                        team,
                        "pressure_resistance_rate",
                    ),
                }
            )
        lines = [
            "# World Cup V5 Role-Aware Final Report",
            "",
            "## Executive summary",
            "",
            f"This report consolidates **{len(teams)} national teams** and "
            f"**{len(rankings)} players meeting the 300-minute cutoff**. "
            "It uses StatsBomb events, lineups, minutes, and coverage-qualified "
            "360 freeze frames. It does not use optical tracking, external "
            "ratings, or player-name adjustments.",
            "",
            f"The active contribution layer is "
            f"`{model_summary.get('selected_layer', 'unknown')}`. The "
            "experimental attention challenger remains available but affects "
            "rankings only when it passes its match-disjoint metric gate.",
            "",
            "## How to read the player rating",
            "",
            "The V5 score combines 40% VAEP/90, 15% VAEP/touch, 15% xT/90, "
            "15% continuous role-adjusted value, 10% completeness, and 5% "
            "coverage-qualified off-ball contribution. It is then shrunk "
            "toward the broad position-group mean according to tournament "
            "minutes.",
            "",
            "Missing 360 evidence remains missing. Roles modulate the weights "
            "applied to observed contribution; neither functional nor "
            "probabilistic role labels directly award rating points.",
            "",
            "## General player summary",
            "",
            "### Overall leaders",
            "",
            _markdown_table(
                rankings.head(20),
                [
                    "global_rank",
                    "player_name",
                    "team",
                    "position_group",
                    "functional_role",
                    "final_player_rating",
                ],
            ),
            "",
            "### Position-group leaders",
            "",
            _markdown_table(
                position_leaders,
                [
                    "position_group",
                    "position_rank",
                    "player_name",
                    "team",
                    "functional_role",
                    "final_player_rating",
                ],
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
            "Rank movement compares ordering, not raw rating differences, "
            "because the V4 and V5 rating scales are different.",
            "",
            "## All-team overview",
            "",
            _markdown_table(
                pd.DataFrame(overview_records),
                [
                    "team",
                    "eligible_players",
                    "top_ranked_player",
                    "top_global_rank",
                    "total_xt",
                    "pressure_resistance",
                ],
            ),
            "",
            "# Team-by-team summary",
            "",
        ]
        for team in teams:
            players = rankings.loc[rankings["team"].eq(team)].sort_values(
                "team_rank"
            )
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
                    "### Top five eligible players",
                    "",
                ]
            )
            if players.empty:
                lines.extend(
                    [
                        "_No player from this team reached the configured "
                        "300-minute ranking cutoff. No lower-minute player is "
                        "promoted as a substitute ranking._",
                        "",
                    ]
                )
            else:
                lines.extend(
                    [
                        _markdown_table(
                            players.head(5),
                            [
                                "team_rank",
                                "global_rank",
                                "player_name",
                                "position_group",
                                "functional_role",
                                "final_player_rating",
                            ],
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
    def _team_profile(
        team: str,
        players: pd.DataFrame,
        team_metrics: pd.Series | None = None,
    ) -> str:
        """Render one team's required tactical and squad sections."""

        def mean(metric: str) -> str:
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

        return "\n".join(
            [
                f"# {team} Team Profile",
                "",
                "## Threat creation",
                "",
                f"- Total xT created: {team_value('total_xt_created')}",
                f"- Total xA created: {team_value('total_xa_created')}",
                f"- Mean creation score: {mean('creation_score')}",
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
                "",
                "## Squad ratings",
                "",
                _markdown_table(
                    players.sort_values("team_rank"),
                    [
                        "team_rank",
                        "player_name",
                        "functional_role",
                        "final_player_rating",
                    ],
                ),
                (
                    ""
                    if not players.empty
                    else "_No player from this team reached the configured "
                    "300-minute ranking cutoff._"
                ),
                "",
            ]
        )

    def generate(
        self,
        players: pd.DataFrame,
        *,
        model_summary: dict[str, Any],
        validation_comparison: pd.DataFrame | None = None,
        tournament_teams: Sequence[str] | None = None,
        team_metrics: pd.DataFrame | None = None,
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
        files: list[Path] = []
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

        csv_path = self.output_root / "player_rankings.csv"
        _atomic_text(csv_path, rankings.to_csv(index=False))
        files.append(csv_path)

        json_path = self.output_root / "player_rankings.json"
        _atomic_text(
            json_path,
            json.dumps(
                _json_value(rankings.to_dict("records")),
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
        )
        files.append(json_path)

        notebook_path = self.output_root / "coaches_notebook.md"
        _atomic_text(notebook_path, self._coaches_notebook(rankings))
        files.append(notebook_path)

        model_json = self.output_root / "model_summary.json"
        summary_payload = {
            "schema_version": self.schema_version,
            **_json_value(model_summary),
        }
        _atomic_text(
            model_json,
            json.dumps(summary_payload, indent=2, ensure_ascii=False) + "\n",
        )
        files.append(model_json)

        model_markdown = self.output_root / "model_summary.md"
        _atomic_text(
            model_markdown,
            self._model_summary_markdown(summary_payload),
        )
        files.append(model_markdown)

        final_path = self.output_root / "final_summary.md"
        _atomic_text(
            final_path,
            self._final_summary(
                rankings,
                summary_payload,
                teams=teams,
                team_metrics=team_metrics,
            ),
        )
        files.append(final_path)

        team_root = self.output_root / "team_profiles"
        for team in teams:
            path = team_root / f"{_slug(team)}.md"
            _atomic_text(
                path,
                self._team_profile(
                    team,
                    rankings.loc[rankings["team"].eq(team)],
                    team_metric_lookup.get(team),
                ),
            )
            files.append(path)

        player_root = self.output_root / "player_profiles"
        player_paths: set[Path] = set()
        for _, player in rankings.iterrows():
            identifier = (
                str(int(player["player_id"]))
                if "player_id" in player and pd.notna(player["player_id"])
                else str(int(player["global_rank"]))
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
            comparison_path = (
                self.output_root / "rating_validation_comparison.csv"
            )
            _atomic_text(
                comparison_path,
                validation_comparison.to_csv(index=False),
            )
            files.append(comparison_path)

        hashes = {
            str(path.relative_to(self.output_root)): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
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
        manifest_path = self.output_root / "artifact_manifest.json"
        _atomic_text(
            manifest_path,
            json.dumps(_json_value(manifest), indent=2) + "\n",
        )
        return ArtifactManifest(
            output_root=manifest.output_root,
            files=(*manifest.files, manifest_path),
            hashes={
                **manifest.hashes,
                "artifact_manifest.json": hashlib.sha256(
                    manifest_path.read_bytes()
                ).hexdigest(),
            },
            schema_version=manifest.schema_version,
            metadata=manifest.metadata,
        )
