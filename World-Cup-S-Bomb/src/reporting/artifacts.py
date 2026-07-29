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
    "RankingStatus",
    "GKRankingStatus",
    "primary_global_rank",
    "primary_goalkeeper_rank",
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
            if pd.isna(value):
                values.append("—")
            elif isinstance(value, float):
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
        ordered = list(RANKING_SCHEMA) + [
            column for column in rankings if column not in RANKING_SCHEMA
        ]
        return rankings[ordered].sort_values(
            ["global_rank", "position_rank", "player_name"],
            na_position="last",
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
            "## Goalkeeper ranking",
            "",
            (
                _markdown_table(
                    rankings.loc[
                        rankings["position_group"].eq("Goalkeeper")
                    ].sort_values("position_rank"),
                    [
                        "position_rank",
                        "player_name",
                        "team",
                        "final_player_rating",
                        "goals_prevented_proxy_p90",
                        "save_rate",
                        "high_leverage_save_pct",
                        "penalty_save_rate_shrunk",
                        "GKRankingStatus",
                    ],
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
                "goals_prevented_proxy_p90",
                "save_rate",
                "claims_p90",
                "cross_stopping_rate",
                "sweeper_actions_p90",
                "distribution_under_pressure",
                "penalty_save_rate_shrunk",
                "high_leverage_save_pct",
                "goalkeeper_feature_coverage",
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
                f"- Position group: {value('position_group')}",
                f"- Functional role: {value('functional_role')}",
                f"- Probabilistic role: {value('probabilistic_role')}",
                f"- Role entropy: {value('role_entropy')}",
                f"- Global rank: {value('global_rank', 0)}",
                f"- Position rank: {value('position_rank', 0)}",
                f"- Role rank: {value('role_rank', 0)}",
                f"- Team rank: {value('team_rank', 0)}",
                f"- Final player rating: {value('final_player_rating')}",
                f"- Ranking status: {value('RankingStatus')}",
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
            ).rstrip()
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

        if team_player_pool is None:
            team_player_pool = rankings.assign(
                selection_priority=0,
                ranking_status="Ranked (300+ min)",
            )
            if "minutes" not in team_player_pool:
                team_player_pool["minutes"] = np.nan
        comparison = pd.DataFrame()
        if "legacy_final_player_rating" in rankings:
            comparison = rankings.loc[
                rankings["global_rank"].notna()
            ].assign(
                legacy_global_rank=rankings[
                    "legacy_final_player_rating"
                ].loc[rankings["global_rank"].notna()]
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
        position_leaders = (
            primary_rankings.sort_values(
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
            covered = team_player_pool.loc[
                team_player_pool["team"].eq(team)
            ].sort_values(
                ["selection_priority", "team_rank", "minutes"],
                ascending=[True, True, False],
                na_position="last",
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
                        int(leader["global_rank"])
                        if leader is not None
                        and pd.notna(leader["global_rank"])
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
        lines = [
            "# World Cup V5 Role-Aware Final Report",
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
            f"The active contribution layer is "
            f"`{model_summary.get('selected_layer', 'unknown')}`. The "
            "experimental attention challenger remains available but affects "
            "rankings only when it passes its match-disjoint metric gate.",
            "",
            "## How to read the player rating",
            "",
            f"The v2 outfield score uses the development-gated "
            f"{context_selection} VAEP feature set and grouped "
            "ElasticNet offense/defense heads with explicit role weights, "
            "VAEP/touch, open-play and set-piece-aware xT, sample-adjusted "
            "completeness, coverage-qualified off-ball value, and xD-style "
            "defensive disruption. Positive ElasticNet calibration selects "
            "the composite weights with team-disjoint folds, followed by "
            "minutes/(minutes+450) position-prior shrinkage.",
            "",
            "Goalkeepers use a separate weighted seven-component matrix and "
            "ranking, including high-leverage saves. "
            "They are excluded from the outfield global ranking because "
            "StatsBomb Open Data does not contain native post-shot xG. "
            "Missing 360 evidence remains missing, and role labels never "
            "award rating points.",
            "",
            "## General player summary",
            "",
            "### Overall leaders",
            "",
            _markdown_table(
                primary_rankings.sort_values(
                    ["primary_global_rank", "primary_goalkeeper_rank"],
                    na_position="last",
                ).head(20),
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
        ]
        for team in teams:
            players = rankings.loc[rankings["team"].eq(team)].sort_values(
                "team_rank"
            )
            covered = team_player_pool.loc[
                team_player_pool["team"].eq(team)
            ].sort_values(
                ["selection_priority", "team_rank", "minutes"],
                ascending=[True, True, False],
                na_position="last",
            ).head(5)
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
                    "### Top five player summary",
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
                            [
                                "team_rank",
                                "global_rank",
                                "player_name",
                                "position_group",
                                "functional_role",
                                "minutes",
                                "final_player_rating",
                                "ranking_status",
                            ],
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
                "## Top five player summary",
                "",
                _markdown_table(
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
                ),
                (
                    ""
                    if covered_players.empty
                    else "_Coverage-only players are ordered by tournament "
                    "minutes. No model rating assigned._"
                    if players.empty
                    else ""
                ),
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

        outfield = rankings.loc[rankings["global_rank"].notna()].head(20)
        figure, axis = plt.subplots(figsize=(10, 7))
        axis.barh(
            outfield["player_name"].iloc[::-1],
            outfield["final_player_rating"].iloc[::-1],
            color="#295f98",
        )
        axis.set_xlabel("V5 final player rating")
        axis.set_title("2022 World Cup — V5 outfield leaders")
        axis.grid(axis="x", alpha=0.2)
        save(figure, "v5_global_outfield_rankings.png")

        france = rankings.loc[rankings["team"].eq("France")].sort_values(
            "team_rank"
        )
        if not france.empty:
            figure, axis = plt.subplots(figsize=(10, 6))
            axis.barh(
                france["player_name"].iloc[::-1],
                france["final_player_rating"].iloc[::-1],
                color="#264653",
            )
            axis.set_xlabel("V5 final player rating")
            axis.set_title("France — updated V5 squad ranking")
            axis.grid(axis="x", alpha=0.2)
            save(figure, "v5_france_team_rankings.png")

        goalkeepers = rankings.loc[
            rankings["position_group"].eq("Goalkeeper")
        ].sort_values("position_rank")
        if not goalkeepers.empty:
            figure, axis = plt.subplots(figsize=(10, 6))
            axis.barh(
                goalkeepers["player_name"].iloc[::-1],
                goalkeepers["final_player_rating"].iloc[::-1],
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

        ranking_csv = rankings.to_csv(index=False)
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
            ("v5_player_rankings.json", ranking_json),
            ("player_rankings.json", ranking_json),
        ):
            path = self.output_root / name
            _atomic_text(path, content)
            files.append(path)

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
