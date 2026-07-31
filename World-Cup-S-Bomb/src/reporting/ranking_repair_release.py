"""Deterministic publication layer for the Qatar 2022 ranking-repair release.

The analytics modules produce one feature-rich player table plus structured
gate diagnostics.  This module is the only writer for the active v3 ranking,
profile, summary, figure, and manifest families.  Legacy material under
``results/reports/ranking/legacy`` is deliberately left untouched.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
import unicodedata
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.reporting.artifacts import TEAM_CODES


ACTIVE_MODEL_VERSION = "ranking-repair-v3.0-qatar-2022"
UNIFIED_COLUMNS = (
    "Global Rank",
    "Team Rank",
    "Player",
    "Team",
    "Position Group",
    "Tournament Performance Score",
)
REQUIRED_V3_COLUMNS = {
    "player_id",
    "player_name",
    "team",
    "position_group",
    "functional_role",
    "minutes_played",
    "tournament_impact_raw_v3",
    "tournament_impact_v3",
    "role_quality_v3",
    "global_rank_v3",
    "team_rank_v3",
    "position_rank_v3",
    "role_rank_v3",
    "uncertainty_low_v3",
    "uncertainty_high_v3",
    "uncertainty_status_v3",
}


def _json_value(value: Any) -> Any:
    """Convert NumPy/Pandas values to strict JSON-compatible values."""

    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, np.generic):
        return _json_value(value.item())
    if value is pd.NA:
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if pd.isna(value) if not isinstance(value, (str, bytes)) else False:
        return None
    return value


def _atomic_bytes(path: Path, content: bytes) -> None:
    """Atomically replace one generated file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _write_text(path: Path, content: str) -> None:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    if normalized and not normalized.endswith("\n"):
        normalized += "\n"
    _atomic_bytes(path, normalized.encode("utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    content = json.dumps(
        _json_value(payload),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    )
    _write_text(path, content)


def _csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    ).encode("utf-8")


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    _atomic_bytes(path, _csv_bytes(frame))


def _slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", str(value)).encode(
        "ascii",
        "ignore",
    ).decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")


def _markdown_table(
    frame: pd.DataFrame,
    columns: Iterable[str],
    *,
    labels: Mapping[str, str] | None = None,
) -> str:
    selected = [column for column in columns if column in frame]
    if frame.empty or not selected:
        return "_No eligible rows._"
    headings = [
        labels.get(column, column.replace("_", " ").title())
        if labels
        else column.replace("_", " ").title()
        for column in selected
    ]
    lines = [
        "| " + " | ".join(headings) + " |",
        "|" + "|".join("---" for _ in selected) + "|",
    ]
    for values in frame[selected].itertuples(index=False, name=None):
        cells: list[str] = []
        for value in values:
            if pd.isna(value):
                cells.append("—")
            elif isinstance(value, (float, np.floating)):
                cells.append(f"{float(value):.4f}")
            else:
                cells.append(str(value).replace("|", r"\|"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _existing_profile_paths(directory: Path) -> dict[int, Path]:
    mapping: dict[int, Path] = {}
    if not directory.exists():
        return mapping
    for path in directory.glob("*.md"):
        match = re.search(r"-(\d+)\.md$", path.name)
        if match:
            mapping[int(match.group(1))] = path
    return mapping


def _clean_generated_files(
    directory: Path,
    expected: set[Path],
    *,
    suffixes: tuple[str, ...],
) -> None:
    """Remove only stale files from an explicit generated family directory."""

    if not directory.exists():
        return
    resolved_expected = {path.resolve() for path in expected}
    for path in directory.rglob("*"):
        if (
            path.is_file()
            and path.suffix.lower() in suffixes
            and path.resolve() not in resolved_expected
        ):
            path.unlink()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class RankingRepairReleaseWriter:
    """Write all active ranking-dependent v3 release artifacts."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.results_root = self.project_root / "results"
        self.reports_root = self.results_root / "reports"
        self.ranking_root = self.reports_root / "ranking"
        self.diagnostics_root = (
            self.results_root / "diagnostics" / "ranking_repair"
        )

    @staticmethod
    def validate_frame(rankings: pd.DataFrame) -> None:
        missing = REQUIRED_V3_COLUMNS.difference(rankings.columns)
        if missing:
            raise ValueError(f"v3 release fields missing: {sorted(missing)}")
        if rankings["player_id"].duplicated().any():
            raise ValueError("v3 release requires one row per player_id")
        outfield = rankings["position_group"].ne("Goalkeeper")
        if rankings.loc[outfield, "global_rank_v3"].isna().any():
            raise ValueError("Every eligible outfield player needs global_rank_v3")
        if rankings.loc[outfield, "tournament_impact_v3"].isna().any():
            raise ValueError("Every eligible outfield player needs Tournament Impact")
        ordered = rankings.loc[outfield].sort_values(
            ["tournament_impact_raw_v3", "player_id"],
            ascending=[False, True],
            kind="mergesort",
        )
        actual = pd.to_numeric(
            ordered["global_rank_v3"],
            errors="coerce",
        ).to_numpy()
        expected = np.arange(1, len(ordered) + 1, dtype=float)
        if not np.array_equal(actual, expected):
            raise ValueError("global_rank_v3 disagrees with impact ordering")
        mains = rankings.loc[
            rankings["position_group"].eq("Goalkeeper")
            & rankings.get(
                "is_main_goalkeeper",
                pd.Series(False, index=rankings.index),
            ).fillna(False)
        ]
        if len(mains) != 32 or mains["team"].nunique() != 32:
            raise ValueError("Exactly one main goalkeeper per team is required")
        goalkeeper_rows = rankings["position_group"].eq("Goalkeeper")
        backups = rankings.loc[goalkeeper_rows & ~rankings.index.isin(mains.index)]
        bridge_columns = {
            "gk_rank_v3",
            "dedicated_goalkeeper_score_v3",
            "percentile_equivalent_placement",
            "percentile_equivalent_score_v3",
            "publication_score_v3",
            "publication_global_rank_v3",
            "tournament_impact_score_v3",
        }
        missing_bridge = bridge_columns.difference(rankings.columns)
        if missing_bridge:
            raise ValueError(
                "v3 goalkeeper publication bridge fields missing: "
                f"{sorted(missing_bridge)}"
            )
        if (
            pd.to_numeric(backups["gk_rank_v3"], errors="coerce")
            .notna()
            .any()
            or pd.to_numeric(
                backups["publication_global_rank_v3"],
                errors="coerce",
            )
            .notna()
            .any()
        ):
            raise ValueError("Backup goalkeepers must remain unranked")

        goalkeeper_rank = pd.to_numeric(
            mains["gk_rank_v3"],
            errors="coerce",
        )
        if not np.array_equal(
            np.sort(goalkeeper_rank.to_numpy()),
            np.arange(1, 33, dtype=float),
        ):
            raise ValueError(
                "Main-goalkeeper ranks must be exactly 1 through 32"
            )
        expected_placement = (
            32.0 - goalkeeper_rank.to_numpy(dtype=float) + 0.5
        ) / 32.0
        placement = pd.to_numeric(
            mains["percentile_equivalent_placement"],
            errors="coerce",
        ).to_numpy(dtype=float)
        if not np.allclose(
            placement,
            expected_placement,
            rtol=0.0,
            atol=1e-12,
        ):
            raise ValueError(
                "percentile_equivalent_placement disagrees with dedicated "
                "goalkeeper rank"
            )

        outfield_scores = (
            pd.to_numeric(
                rankings.loc[
                    ~goalkeeper_rows,
                    "tournament_impact_score_v3",
                ],
                errors="coerce",
            )
            .dropna()
            .sort_values()
            .to_numpy()
        )
        if outfield_scores.size == 0:
            raise ValueError(
                "Goalkeeper publication bridge requires outfield impact scores"
            )
        expected_equivalent = np.quantile(
            outfield_scores,
            placement,
            method="linear",
        )
        for column in (
            "percentile_equivalent_score_v3",
            "publication_score_v3",
        ):
            actual_equivalent = pd.to_numeric(
                mains[column],
                errors="coerce",
            ).to_numpy(dtype=float)
            if not np.allclose(
                actual_equivalent,
                expected_equivalent,
                rtol=0.0,
                atol=1e-12,
            ):
                raise ValueError(
                    f"{column} is not the corresponding quantile of "
                    "outfield Tournament Impact"
                )

        ordered_goalkeepers = mains.loc[
            goalkeeper_rank.sort_values(kind="mergesort").index
        ]
        if not pd.to_numeric(
            ordered_goalkeepers["dedicated_goalkeeper_score_v3"],
            errors="coerce",
        ).is_monotonic_decreasing:
            raise ValueError(
                "Dedicated goalkeeper ordering disagrees with gk_rank_v3"
            )
        if not pd.to_numeric(
            ordered_goalkeepers["publication_score_v3"],
            errors="coerce",
        ).is_monotonic_decreasing:
            raise ValueError(
                "Goalkeeper publication bridge does not preserve dedicated "
                "ordering"
            )

        publication_rank = pd.to_numeric(
            rankings["publication_global_rank_v3"],
            errors="coerce",
        )
        goalkeeper_top20 = int(
            (goalkeeper_rows & publication_rank.le(20.0)).sum()
        )
        eligible_count = int(publication_rank.notna().sum())
        proportional_tolerance = max(
            2,
            int(
                np.ceil(
                    2.0
                    * 20.0
                    * len(mains)
                    / max(eligible_count, 1)
                )
            ),
        )
        if goalkeeper_top20 > proportional_tolerance:
            raise ValueError(
                "Goalkeepers disproportionately dominate the publication "
                f"top 20 ({goalkeeper_top20} > {proportional_tolerance})"
            )

    @staticmethod
    def _publication_frame(rankings: pd.DataFrame) -> pd.DataFrame:
        output = rankings.copy()
        output["Player"] = output["player_name"]
        output["Team"] = output["team"]
        output["Position Group"] = output["position_group"]
        output["Global Rank"] = pd.to_numeric(
            output.get("publication_global_rank_v3", output["global_rank_v3"]),
            errors="coerce",
        ).astype("Int64")
        output["Team Rank"] = pd.to_numeric(
            output.get("publication_team_rank_v3", output["team_rank_v3"]),
            errors="coerce",
        ).astype("Int64")
        # Publication scale contract: player ratings are published on a
        # FIFA-style 55-99 scale with one decimal place. The transform is a
        # monotone linear map of the model score (55 + 44 x score), so score
        # gaps are preserved rather than flattened into rank percentiles.
        # Raw model columns retain full precision underneath.
        output["Tournament Performance Score"] = (
            pd.to_numeric(
                output.get(
                    "publication_score_v3",
                    output.get(
                        "tournament_impact_score_v3",
                        output["tournament_impact_v3"],
                    ),
                ),
                errors="coerce",
            )
            .mul(44.0)
            .add(55.0)
            .round(1)
        )
        output["active_model_version"] = ACTIVE_MODEL_VERSION
        event_scope = "qatar-2022-periods-1-4-v1"
        if "event_scope_version" in output:
            output["event_scope_version"] = output[
                "event_scope_version"
            ].fillna(event_scope)
        else:
            output["event_scope_version"] = event_scope
        output["active_global_rank_field"] = "global_rank_v3"
        output["active_team_rank_field"] = "team_rank_v3"
        return output

    def write_rankings(
        self,
        rankings: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame, list[Path]]:
        """Write active, versioned, compatibility, team, and GK tables."""

        self.validate_frame(rankings)
        rich = self._publication_frame(rankings)
        rich = rich.sort_values(
            ["Global Rank", "team", "player_id"],
            na_position="last",
            kind="mergesort",
        ).reset_index(drop=True)
        unified = (
            rich.loc[
                rich["Global Rank"].notna(),
                list(UNIFIED_COLUMNS),
            ]
            .sort_values("Global Rank", kind="mergesort")
            .reset_index(drop=True)
        )
        outfield = (
            rich.loc[
                rich["position_group"].ne("Goalkeeper")
                & rich["global_rank_v3"].notna()
            ]
            .sort_values("global_rank_v3", kind="mergesort")
            .reset_index(drop=True)
        )
        outfield_300 = outfield.loc[
            pd.to_numeric(
                outfield["minutes_played"],
                errors="coerce",
            ).ge(300.0)
        ].reset_index(drop=True)
        ranked_300 = rich.loc[
            pd.to_numeric(
                rich["minutes_played"],
                errors="coerce",
            ).ge(300.0)
            & rich["Global Rank"].notna()
        ].reset_index(drop=True)
        goalkeeper = (
            rich.loc[
                rich["position_group"].eq("Goalkeeper")
                & pd.to_numeric(
                    rich.get("gk_rank_v3"),
                    errors="coerce",
                ).notna()
            ]
            .sort_values("gk_rank_v3", kind="mergesort")
            .reset_index(drop=True)
        )
        if len(goalkeeper) != 32 or goalkeeper["team"].nunique() != 32:
            raise ValueError("Dedicated v3 goalkeeper table must have 32 teams")

        paths: list[Path] = []
        csv_aliases = (
            "player_rankings.csv",
            "player_rankings_v3.csv",
            "player_rankings_v2.csv",
            "v5_player_rankings.csv",
        )
        rich_bytes = _csv_bytes(rich)
        for name in csv_aliases:
            path = self.ranking_root / name
            _atomic_bytes(path, rich_bytes)
            paths.append(path)
        json_payload = [
            _json_value(record)
            for record in rich.to_dict(orient="records")
        ]
        json_bytes = (
            json.dumps(
                json_payload,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        for name in (
            "player_rankings.json",
            "player_rankings_v3.json",
            "v5_player_rankings.json",
        ):
            path = self.ranking_root / name
            _atomic_bytes(path, json_bytes)
            paths.append(path)
        table_outputs = {
            "player_rankings_300plus.csv": ranked_300,
            "global_rankings_outfield.csv": outfield,
            "global_rankings_outfield_300min.csv": outfield_300,
            "unified_tournament_rankings.csv": unified,
            "goalkeeper_rankings.csv": goalkeeper,
            "goalkeeper_rankings_unified.csv": goalkeeper,
        }
        for name, frame in table_outputs.items():
            path = self.ranking_root / name
            _write_csv(path, frame)
            paths.append(path)

        by_team_root = self.ranking_root / "by_team"
        by_team_unified_root = self.ranking_root / "by_team_unified"
        expected_rich: set[Path] = set()
        expected_unified: set[Path] = set()
        for team, code in sorted(TEAM_CODES.items(), key=lambda item: item[1]):
            team_rich = (
                rich.loc[rich["team"].eq(team)]
                .sort_values(
                    ["Team Rank", "player_id"],
                    na_position="last",
                    kind="mergesort",
                )
                .reset_index(drop=True)
            )
            if team_rich.empty:
                raise ValueError(f"Missing ranking rows for {team}")
            team_unified = (
                unified.loc[unified["Team"].eq(team)]
                .sort_values("Team Rank", kind="mergesort")
                .reset_index(drop=True)
            )
            rich_path = by_team_root / f"{code}.csv"
            unified_path = by_team_unified_root / f"{code}.csv"
            _write_csv(rich_path, team_rich)
            _write_csv(unified_path, team_unified)
            expected_rich.add(rich_path)
            expected_unified.add(unified_path)
            paths.extend((rich_path, unified_path))
        _clean_generated_files(
            by_team_root,
            expected_rich,
            suffixes=(".csv",),
        )
        _clean_generated_files(
            by_team_unified_root,
            expected_unified,
            suffixes=(".csv",),
        )
        return rich, goalkeeper, paths

    @staticmethod
    def _methodology_markdown(audit: Mapping[str, Any]) -> str:
        selections = audit.get("component_selections", {})
        attack = selections.get("attack", {})
        defense = selections.get("defense", {})
        goalkeeper = selections.get("goalkeeper", {})
        return "\n".join(
            [
                "# Qatar 2022 Player Ranking Methodology — v3",
                "",
                f"Active model: `{ACTIVE_MODEL_VERSION}`.",
                "",
                "## Evidence boundary",
                "",
                "All ordinary outfield and continuous goalkeeper evidence is "
                "restricted to Qatar 2022 regulation and extra time "
                "(StatsBomb periods 1–4). Period 5 is a penalty-shootout "
                "channel. Shootout attempts never enter outfield goals, xG, "
                "xA, xT, VAEP, finishing, or Tournament Impact.",
                "",
                "Player names, team names, reputation, tournament advancement, "
                "awards, and external rankings are excluded from scoring. "
                "External Qatar 2022 analysis may be used only as a post-score "
                "audit.",
                "",
                "## Three separate products",
                "",
                "1. **Tournament Impact** is a signed total in common action-"
                "value units. It determines outfield Global Rank and Team Rank. "
                "No within-position z-score, player identity, role bonus, or "
                "minutes multiplier creates this value.",
                "2. **Role Quality** is one empirical-Bayes posterior rate. A "
                "probabilistic role mixture supplies the prior interpretation; "
                "the evidence is shrunk once and is used only for position and "
                "role leaderboards.",
                "3. **Uncertainty** is a match-bootstrap interval and rank band. "
                "It is reported directly and never becomes another score or "
                "minutes penalty.",
                "",
                "## Offensive value",
                "",
                "The release compares process-only, outcomes-only, process plus "
                "a bounded reliability-shrunk realization residual, and process "
                "plus full outcomes. Non-penalty goals, regular penalties, "
                "assists, xG, xA, expected action value, and realized action "
                "value remain explicit. Because VAEP/action value already "
                "contains realized shot outcomes, full goals and assists are "
                "not added a second time.",
                "",
                f"Active attack selection: `{attack.get('selected', 'not recorded')}` "
                f"({attack.get('decision', 'decision not recorded')}).",
                "",
                "## Defensive value",
                "",
                "The defensive channel targets opportunity-adjusted change in "
                "conceding probability and threat prevention. It tests "
                "interceptions/blocks, pressure-sequence reductions, retained "
                "clearances, location-adjusted aerials, positioning coverage, "
                "and errors as signed evidence. Passing progression remains a "
                "separate contribution channel and is not a proxy for defending.",
                "",
                f"Active defense selection: `{defense.get('selected', 'not recorded')}` "
                f"({defense.get('decision', 'decision not recorded')}). The "
                "legacy one-sided publication lift is not active.",
                "",
                "## Goalkeepers",
                "",
                "Exactly one main goalkeeper per team is ranked. Continuous "
                "shot stopping is calibrated out of fold with match-disjoint "
                "development selection between sigmoid and isotonic "
                "calibration. Continuous component weights are 40% shot "
                "stopping, 15% high-leverage shot stopping, 12% cross/claim "
                "control, 10% sweeping, 10% distribution under pressure, and "
                "13% regular-penalty performance. Those weights form 90% of "
                "the dedicated score; the separate shootout component is capped "
                "at 10%. Missing inputs renormalize the available continuous "
                "weights.",
                "",
                f"Active goalkeeper selection: "
                f"`{goalkeeper.get('selected', 'not recorded')}` "
                f"({goalkeeper.get('decision', 'decision not recorded')}).",
                "",
                "The cross-position goalkeeper fallback is explicitly named "
                "`percentile_equivalent_placement`. It is a publication "
                "placement, not measured absolute common-unit contribution.",
                "",
                "## Compatibility",
                "",
                "`player_rankings_v2.csv` and `v5_player_rankings.csv` are "
                "byte-identical filename compatibility aliases of the active "
                "feature-rich v3 table. Explicit legacy score columns remain "
                "available but are preserved, labelled, and not repurposed. "
                "`ranking/legacy/` remains the historical archive.",
                "",
            ]
        )

    @staticmethod
    def _audit_markdown(audit: Mapping[str, Any]) -> str:
        passes = audit.get("pass_gates", {})
        lines = [
            "# Qatar 2022 Ranking Repair Audit",
            "",
            f"- Active model: `{ACTIVE_MODEL_VERSION}`",
            f"- Generated from player/team identity-free scoring: "
            f"**{'PASS' if audit.get('zero_identity_scoring_confirmed') else 'FAIL'}**",
            f"- Ordinary event scope: "
            f"`{audit.get('event_scope_version', 'not recorded')}`",
            "",
            "## Eight-pass gates",
            "",
            "| Pass | Decision | Active selection or fallback |",
            "|---|---|---|",
        ]
        for number in range(1, 9):
            row = passes.get(str(number), passes.get(number, {}))
            lines.append(
                f"| {number} | {row.get('decision', 'not recorded')} | "
                f"{row.get('selection', row.get('fallback', '—'))} |"
            )
        lines.extend(
            [
                "",
                "## Component decisions",
                "",
                "| Component | Champion | Challenger | Decision | Active |",
                "|---|---|---|---|---|",
            ]
        )
        for component, row in audit.get(
            "component_selections",
            {},
        ).items():
            lines.append(
                f"| {component} | {row.get('champion', '—')} | "
                f"{row.get('challenger', '—')} | "
                f"{row.get('decision', '—')} | "
                f"{row.get('selected', '—')} |"
            )
        comparison = audit.get("champion_challenger", {})
        if comparison:
            lines.extend(
                [
                    "",
                    "## Champion versus challenger",
                    "",
                    _markdown_table(
                        pd.DataFrame(comparison.get("metrics", [])),
                        (
                            "metric",
                            "champion",
                            "challenger",
                            "difference",
                            "ci_low",
                            "ci_high",
                            "gate",
                        ),
                    ),
                ]
            )
        generalized = audit.get("generalized_validity", {})
        if generalized:
            lines.extend(
                [
                    "",
                    "## Generalized football-validity checks",
                    "",
                    "```json",
                    json.dumps(
                        _json_value(generalized),
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True,
                    ),
                    "```",
                ]
            )
        lines.extend(
            [
                "",
                "## Interpretation boundary",
                "",
                "Named players appear only in post-score audit rows. No named "
                "example can promote a component or change a coefficient, "
                "weight, prior, or threshold.",
                "",
            ]
        )
        return "\n".join(lines)

    def write_methodology_and_audits(
        self,
        audit: Mapping[str, Any],
    ) -> list[Path]:
        """Write canonical methodology, audit, and validation aliases."""

        methodology = self.ranking_root / "ranking_methodology.md"
        audit_json = self.ranking_root / "ranking_audit.json"
        audit_markdown = self.ranking_root / "ranking_audit.md"
        _write_text(methodology, self._methodology_markdown(audit))
        _write_json(audit_json, audit)
        _write_text(audit_markdown, self._audit_markdown(audit))

        validation = {
            "schema_version": "ranking-repair-validation-3.0",
            "active_model_version": ACTIVE_MODEL_VERSION,
            "status": audit.get("release_status", "not-recorded"),
            "event_scope_version": audit.get("event_scope_version"),
            "pass_gates": audit.get("pass_gates", {}),
            "component_selections": audit.get("component_selections", {}),
            "ranking": audit.get("ranking", {}),
            "attack": audit.get("attack", {}),
            "defense": audit.get("defense", {}),
            "goalkeeper": audit.get("goalkeeper", {}),
            "zero_identity_scoring_confirmed": audit.get(
                "zero_identity_scoring_confirmed",
                False,
            ),
        }
        v3_validation = (
            self.results_root / "diagnostics" / "v3_validation_summary.json"
        )
        compatibility_validation = (
            self.results_root / "diagnostics" / "v2_validation_summary.json"
        )
        unified_validation = (
            self.results_root
            / "diagnostics"
            / "unified_team_validation.json"
        )
        _write_json(v3_validation, validation)
        _write_json(
            compatibility_validation,
            {
                **validation,
                "compatibility_alias": True,
                "compatibility_note": (
                    "Legacy filename; payload describes the active v3 release."
                ),
            },
        )
        _write_json(
            unified_validation,
            {
                **validation,
                "validation_scope": (
                    "active six-field global and 32-team unified tables"
                ),
            },
        )
        return [
            methodology,
            audit_json,
            audit_markdown,
            v3_validation,
            compatibility_validation,
            unified_validation,
        ]

    @staticmethod
    def _leader_rows(
        rich: pd.DataFrame,
        *,
        limit: int,
        minimum_minutes: float | None = None,
        maximum_minutes: float | None = None,
    ) -> pd.DataFrame:
        mask = rich["position_group"].ne("Goalkeeper")
        minutes = pd.to_numeric(rich["minutes_played"], errors="coerce")
        if minimum_minutes is not None:
            mask &= minutes.ge(minimum_minutes)
        if maximum_minutes is not None:
            mask &= minutes.lt(maximum_minutes)
        return (
            rich.loc[mask]
            .sort_values("global_rank_v3", kind="mergesort")
            .head(limit)
        )

    @staticmethod
    def _model_summary_payload(
        rich: pd.DataFrame,
        audit: Mapping[str, Any],
    ) -> dict[str, Any]:
        outfield = rich.loc[rich["position_group"].ne("Goalkeeper")]
        mains = rich.loc[
            rich["position_group"].eq("Goalkeeper")
            & rich.get(
                "is_main_goalkeeper",
                pd.Series(False, index=rich.index),
            ).fillna(False)
        ]
        return {
            "schema_version": "ranking-repair-model-summary-3.0",
            "active_model_version": ACTIVE_MODEL_VERSION,
            "tournament": "2022 FIFA World Cup (Qatar)",
            "release_status": audit.get("release_status"),
            "component_selections": audit.get("component_selections", {}),
            "event_scope": {
                "ordinary_periods": [1, 2, 3, 4],
                "shootout_period": 5,
                "version": audit.get("event_scope_version"),
            },
            "score_contract": {
                "global_and_team": "Tournament Impact",
                "position_and_role": "Role Quality",
                "confidence": "Uncertainty",
                "within_position_z_used_for_global": False,
                "exposure_cascade_active": False,
                "uncertainty_used_as_penalty": False,
            },
            "cohort": {
                "players": int(len(rich)),
                "eligible_outfield": int(len(outfield)),
                "main_goalkeepers": int(len(mains)),
                "teams": int(rich["team"].nunique()),
            },
            "attack": audit.get("attack", {}),
            "defense": audit.get("defense", {}),
            "goalkeeper": audit.get("goalkeeper", {}),
            "ranking": audit.get("ranking", {}),
            "champion_challenger": audit.get(
                "champion_challenger",
                {},
            ),
            "limitations": audit.get("limitations", []),
            "compatibility": {
                "player_rankings_v2.csv": (
                    "byte-identical filename alias of active v3 table"
                ),
                "v5_player_rankings.csv": (
                    "byte-identical filename alias of active v3 table"
                ),
                "legacy_columns": "preserved and explicitly non-active",
            },
        }

    @staticmethod
    def _model_summary_markdown(payload: Mapping[str, Any]) -> str:
        selections = payload.get("component_selections", {})
        lines = [
            "# Qatar 2022 Ranking Model Summary",
            "",
            f"- Active model: `{payload['active_model_version']}`",
            f"- Release status: **{payload.get('release_status', 'not recorded')}**",
            "- Ordinary performance scope: periods 1–4",
            "- Shootout-only scope: period 5",
            "- Global/team product: Tournament Impact",
            "- Position/role product: Role Quality",
            "- Confidence product: Uncertainty",
            "- Player/team identity scoring features: none",
            "",
            "## Component selections",
            "",
            "| Component | Active | Decision |",
            "|---|---|---|",
        ]
        for component, row in selections.items():
            lines.append(
                f"| {component} | {row.get('selected', '—')} | "
                f"{row.get('decision', '—')} |"
            )
        lines.extend(
            [
                "",
                "## Active architecture",
                "",
                "Tournament Impact is a signed common-unit event-value total. "
                "It has no within-position normalization and no repeated "
                "minutes/exposure multiplier. Role Quality uses one fitted "
                "empirical-Bayes shrinkage step. Uncertainty is a match-"
                "bootstrap interval, not a score penalty.",
                "",
                "Offensive outcomes are separated into non-penalty goals, "
                "regular penalties, assists, xG, xA, expected action value, "
                "and realized value. Period-five conversions are excluded. "
                "A bounded shrunk realization residual is used only when its "
                "generalized held-out gate passes.",
                "",
                "Defensive value is based on opportunity-adjusted threat "
                "prevention and signed errors. The old one-sided defensive "
                "publication lift is retired.",
                "",
                "The dedicated goalkeeper score assigns 90% to continuous "
                "evidence and at most 10% to the separate shootout component. "
                "The cross-position fallback is a percentile-equivalent "
                "placement, not absolute common-unit performance.",
                "",
                "## Validation and limitations",
                "",
                "See `ranking/ranking_audit.json` for confidence intervals, "
                "grouped validation, all eight pass gates, retained fallbacks, "
                "and generalized post-score checks.",
                "",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _final_summary_markdown(
        rich: pd.DataFrame,
        goalkeeper: pd.DataFrame,
        audit: Mapping[str, Any],
    ) -> str:
        leaders = RankingRepairReleaseWriter._leader_rows(
            rich,
            limit=20,
        )
        leaders_300 = RankingRepairReleaseWriter._leader_rows(
            rich,
            limit=20,
            minimum_minutes=300.0,
        )
        short = RankingRepairReleaseWriter._leader_rows(
            rich,
            limit=15,
            maximum_minutes=300.0,
        )
        position_leaders = (
            rich.loc[rich["position_group"].ne("Goalkeeper")]
            .sort_values(
                ["position_group", "position_rank_v3", "player_id"],
                kind="mergesort",
            )
            .groupby("position_group", sort=True)
            .head(3)
        )
        role_leaders = (
            rich.loc[rich["position_group"].ne("Goalkeeper")]
            .sort_values(
                ["functional_role", "role_rank_v3", "player_id"],
                kind="mergesort",
            )
            .groupby("functional_role", sort=True)
            .head(1)
            .sort_values(
                ["role_quality_v3", "player_id"],
                ascending=[False, True],
                kind="mergesort",
            )
            .head(20)
        )
        team_leaders = (
            rich.loc[rich["Team Rank"].eq(1)]
            .sort_values("team", kind="mergesort")
        )
        lines = [
            "# 2022 FIFA World Cup — Player Ranking Final Summary",
            "",
            f"Active release: `{ACTIVE_MODEL_VERSION}` "
            f"(**{audit.get('release_status', 'status not recorded')}**).",
            "",
            "The ranking publishes three different answers. **Tournament "
            "Impact** is the signed total contribution used for global and "
            "team ordering. **Role Quality** is a once-shrunk posterior rate "
            "used for position and role comparisons. **Uncertainty** is a "
            "match-bootstrap interval and rank band; it is not another "
            "minutes penalty.",
            "",
            "Regulation and extra-time evidence uses periods 1–4. Penalty-"
            "shootout events use period 5 and remain outside ordinary goals, "
            "xG, xA, xT, VAEP, and outfield impact.",
            "",
            "## Global outfield leaders",
            "",
            _markdown_table(
                leaders,
                (
                    "global_rank_v3",
                    "player_name",
                    "team",
                    "position_group",
                    "minutes_played",
                    "tournament_impact_raw_v3",
                    "role_quality_v3",
                    "uncertainty_low_v3",
                    "uncertainty_high_v3",
                    "uncertainty_status_v3",
                ),
                labels={
                    "global_rank_v3": "Rank",
                    "tournament_impact_raw_v3": "Tournament Impact",
                    "role_quality_v3": "Role Quality",
                },
            ),
            "",
            "## 300+ minute outfield leaders",
            "",
            _markdown_table(
                leaders_300,
                (
                    "global_rank_v3",
                    "player_name",
                    "team",
                    "position_group",
                    "minutes_played",
                    "tournament_impact_raw_v3",
                    "role_quality_v3",
                    "uncertainty_status_v3",
                ),
            ),
            "",
            "## Below-300-minute high-impact players",
            "",
            "These rows are ordered by total Tournament Impact, while the "
            "uncertainty columns expose their smaller sample.",
            "",
            _markdown_table(
                short,
                (
                    "global_rank_v3",
                    "player_name",
                    "team",
                    "position_group",
                    "minutes_played",
                    "tournament_impact_raw_v3",
                    "role_quality_v3",
                    "bootstrap_rank_best_v3",
                    "bootstrap_rank_worst_v3",
                    "uncertainty_status_v3",
                ),
            ),
            "",
            "## Position leaders by Role Quality",
            "",
            _markdown_table(
                position_leaders,
                (
                    "position_group",
                    "position_rank_v3",
                    "player_name",
                    "team",
                    "role_quality_v3",
                    "tournament_impact_raw_v3",
                    "uncertainty_status_v3",
                ),
            ),
            "",
            "## Role leaders by Role Quality",
            "",
            _markdown_table(
                role_leaders,
                (
                    "functional_role",
                    "role_rank_v3",
                    "player_name",
                    "team",
                    "role_quality_v3",
                    "tournament_impact_raw_v3",
                ),
            ),
            "",
            "## Team leaders",
            "",
            _markdown_table(
                team_leaders,
                (
                    "team",
                    "Team Rank",
                    "player_name",
                    "position_group",
                    "Global Rank",
                    "Tournament Performance Score",
                    "uncertainty_status_v3",
                ),
            ),
            "",
            "## Dedicated goalkeeper leaders",
            "",
            _markdown_table(
                goalkeeper.head(15),
                (
                    "goalkeeper_rank_v3",
                    "player_name",
                    "team",
                    "dedicated_goalkeeper_score_v3",
                    "continuous_goalkeeper_rating_v3",
                    "shootout_component_v3",
                    "goalkeeper_score_interval_low_v3",
                    "goalkeeper_score_interval_high_v3",
                    "goalkeeper_uncertainty_status_v3",
                ),
            ),
            "",
            "The dedicated goalkeeper order combines a 90% continuous "
            "allocation with a separate shootout contribution capped at 10%. "
            "`percentile_equivalent_placement` is used only when a unified "
            "publication placement is required; it is not measured absolute "
            "cross-position contribution.",
            "",
            "## Release gate and limitations",
            "",
            f"Overall release decision: **"
            f"{audit.get('release_status', 'not recorded')}**.",
            "",
        ]
        limitations = audit.get("limitations", [])
        if limitations:
            lines.extend(f"- {item}" for item in limitations)
        else:
            lines.append(
                "- StatsBomb Open Data is event data, not continuous optical "
                "tracking; missing 360 evidence remains missing."
            )
        lines.extend(
            [
                "",
                "All rankings describe Qatar 2022 tournament evidence only. "
                "They are not career-strength, reputation, award, or future-"
                "performance rankings.",
                "",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _coaches_notebook_markdown(
        rich: pd.DataFrame,
        goalkeeper: pd.DataFrame,
    ) -> str:
        team_leaders = (
            rich.loc[rich["Team Rank"].le(3)]
            .sort_values(["team", "Team Rank"], kind="mergesort")
        )
        return "\n".join(
            [
                "# Qatar 2022 Coaches Notebook — Ranking v3",
                "",
                "Use Tournament Impact for total tournament contribution, "
                "Role Quality for rate/role comparisons, and Uncertainty for "
                "confidence. Do not interpret a wide interval as a hidden "
                "penalty or a low total as proof of poor underlying quality.",
                "",
                "## Top three active publication rows by team",
                "",
                _markdown_table(
                    team_leaders,
                    (
                        "team",
                        "Team Rank",
                        "player_name",
                        "position_group",
                        "functional_role",
                        "tournament_impact_raw_v3",
                        "role_quality_v3",
                        "uncertainty_status_v3",
                    ),
                ),
                "",
                "## Main goalkeeper reference",
                "",
                _markdown_table(
                    goalkeeper,
                    (
                        "goalkeeper_rank_v3",
                        "player_name",
                        "team",
                        "continuous_goalkeeper_rating_v3",
                        "shootout_component_v3",
                    ),
                ),
                "",
                "All evidence is Qatar 2022 only; identities, reputation, "
                "advancement, awards, and external lists are not score inputs.",
                "",
            ]
        )

    def write_summaries(
        self,
        rich: pd.DataFrame,
        goalkeeper: pd.DataFrame,
        audit: Mapping[str, Any],
    ) -> list[Path]:
        """Write structured summaries first, then byte-identical mirrors."""

        payload = self._model_summary_payload(rich, audit)
        model_json = json.dumps(
            _json_value(payload),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + "\n"
        model_markdown = self._model_summary_markdown(payload)
        final_markdown = self._final_summary_markdown(
            rich,
            goalkeeper,
            audit,
        )
        coaches_markdown = self._coaches_notebook_markdown(
            rich,
            goalkeeper,
        )
        outputs: list[Path] = []
        for path in (
            self.reports_root / "canonical" / "model_summary.json",
            self.reports_root / "model_summary.json",
        ):
            _atomic_bytes(path, model_json.encode("utf-8"))
            outputs.append(path)
        for path in (
            self.reports_root / "canonical" / "model_summary.md",
            self.reports_root / "model_summary.md",
            self.results_root / "Summary" / "model_summary.md",
        ):
            _write_text(path, model_markdown)
            outputs.append(path)
        for path in (
            self.reports_root / "canonical" / "final_summary.md",
            self.reports_root / "final_summary.md",
            self.reports_root
            / "final"
            / "world_cup_team_performance_and_top_players.md",
        ):
            _write_text(path, final_markdown)
            outputs.append(path)
        for path in (
            self.reports_root / "canonical" / "coaches_notebook.md",
            self.reports_root / "coaches_notebook.md",
            self.reports_root / "v5_coaches_notebook.md",
        ):
            _write_text(path, coaches_markdown)
            outputs.append(path)
        return outputs

    @staticmethod
    def _profile_markdown(row: pd.Series) -> str:
        is_goalkeeper = row["position_group"] == "Goalkeeper"

        def integer(name: str) -> int:
            value = pd.to_numeric(
                pd.Series([row.get(name)]),
                errors="coerce",
            ).iloc[0]
            return 0 if pd.isna(value) else int(value)

        def number(name: str) -> float:
            value = pd.to_numeric(
                pd.Series([row.get(name)]),
                errors="coerce",
            ).iloc[0]
            return 0.0 if pd.isna(value) else float(value)

        lines = [
            f"# {row['player_name']} — Qatar 2022 Player Profile",
            "",
            "This generated profile uses Qatar 2022 event evidence only. "
            "Player identity is displayed after scoring and is never a feature.",
            "",
            "## Tournament Impact, Role Quality, and Uncertainty",
            "",
            f"- Team: {row['team']}",
            f"- Position group: {row['position_group']}",
            f"- Functional role: {row['functional_role']}",
            f"- Minutes: {float(row['minutes_played']):.1f}",
        ]
        if is_goalkeeper:
            lines.extend(
                [
                    f"- Dedicated goalkeeper rank: "
                    f"{_json_value(row.get('goalkeeper_rank_v3')) or 'unranked'}",
                    f"- Dedicated goalkeeper score: "
                    f"{float(row.get('dedicated_goalkeeper_score_v3', np.nan)):.4f}"
                    if pd.notna(row.get("dedicated_goalkeeper_score_v3"))
                    else "- Dedicated goalkeeper score: unranked backup",
                    f"- Continuous goalkeeper score: "
                    f"{float(row.get('continuous_goalkeeper_rating_v3', np.nan)):.4f}"
                    if pd.notna(row.get("continuous_goalkeeper_rating_v3"))
                    else "- Continuous goalkeeper score: unavailable",
                    f"- Separate shootout component: "
                    f"{float(row.get('shootout_component_v3', np.nan)):.4f}"
                    if pd.notna(row.get("shootout_component_v3"))
                    else "- Separate shootout component: unavailable",
                    "- Cross-position field: percentile-equivalent placement "
                    "(publication fallback, not absolute common-unit value)",
                ]
            )
        else:
            lines.extend(
                [
                    f"- Global Rank v3: {int(row['global_rank_v3'])}",
                    f"- Team Rank v3: {int(row['team_rank_v3'])}",
                    f"- Position Rank v3: {int(row['position_rank_v3'])}",
                    f"- Role Rank v3: {int(row['role_rank_v3'])}",
                    f"- Tournament Impact: "
                    f"{float(row['tournament_impact_raw_v3']):.4f}",
                    f"- Role Quality: {float(row['role_quality_v3']):.4f}",
                    f"- Impact interval: "
                    f"[{float(row['uncertainty_low_v3']):.4f}, "
                    f"{float(row['uncertainty_high_v3']):.4f}]",
                    f"- Rank band: "
                    f"{_json_value(row.get('bootstrap_rank_best_v3')) or '—'}"
                    f"–{_json_value(row.get('bootstrap_rank_worst_v3')) or '—'}",
                    f"- Uncertainty status: {row['uncertainty_status_v3']}",
                ]
            )
        lines.extend(
            [
                "",
                "## Decisive outcomes",
                "",
                f"- Non-penalty goals: {integer('non_penalty_goals')}",
                f"- Regular penalty goals: "
                f"{integer('regular_penalty_goals')}",
                f"- Actual assists: {integer('assists')}",
                f"- Non-shootout xG: "
                f"{number('xg_non_shootout'):.4f}",
                f"- Non-shootout xA: "
                f"{number('xa_non_shootout'):.4f}",
                "- Shootout conversions are displayed only in the separate "
                "shootout field and do not enter outfield impact.",
                "",
                "## Active components",
                "",
                _markdown_table(
                    pd.DataFrame(
                        [
                            {
                                "component": "Attack",
                                "value": row.get("attack_component_v3"),
                            },
                            {
                                "component": "Defense",
                                "value": row.get("defensive_component_v3"),
                            },
                            {
                                "component": "Other",
                                "value": row.get("other_component_v3"),
                            },
                        ]
                    ),
                    ("component", "value"),
                ),
                "",
                "## Compatibility",
                "",
                "Older v2/v5 columns are retained for provenance only. They "
                "are not the active ordering described above.",
                "",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _starter_payload(row: pd.Series) -> dict[str, Any]:
        fields = (
            "player_id",
            "player_name",
            "team",
            "position_group",
            "functional_role",
            "minutes_played",
            "global_rank_v3",
            "team_rank_v3",
            "position_rank_v3",
            "role_rank_v3",
            "tournament_impact_raw_v3",
            "tournament_impact_v3",
            "role_quality_v3",
            "uncertainty_low_v3",
            "uncertainty_high_v3",
            "bootstrap_rank_best_v3",
            "bootstrap_rank_worst_v3",
            "uncertainty_status_v3",
            "non_penalty_goals",
            "regular_penalty_goals",
            "assists",
            "xg_non_shootout",
            "xa_non_shootout",
            "attack_component_v3",
            "defensive_component_v3",
            "other_component_v3",
            "goalkeeper_rank_v3",
            "dedicated_goalkeeper_score_v3",
            "continuous_goalkeeper_rating_v3",
            "shootout_component_v3",
            "percentile_equivalent_placement",
        )
        payload = {
            field: _json_value(row.get(field))
            for field in fields
        }
        payload.update(
            {
                "active_model_version": ACTIVE_MODEL_VERSION,
                "ordinary_event_periods": [1, 2, 3, 4],
                "shootout_period": 5,
                "identity_used_for_scoring": False,
                "legacy_fields_status": "compatibility-only",
            }
        )
        return payload

    @staticmethod
    def _team_profile_markdown(team: str, squad: pd.DataFrame) -> str:
        ranked = squad.loc[squad["Team Rank"].notna()].sort_values(
            "Team Rank",
            kind="mergesort",
        )
        outfield = squad.loc[squad["position_group"].ne("Goalkeeper")]
        goalkeeper = squad.loc[
            squad["position_group"].eq("Goalkeeper")
            & pd.to_numeric(
                squad.get("goalkeeper_rank_v3"),
                errors="coerce",
            ).notna()
        ]
        return "\n".join(
            [
                f"# {team} — Qatar 2022 Team Profile",
                "",
                "Tournament Impact orders the team table. Role Quality and "
                "Uncertainty remain separate products.",
                "",
                "## Team leaders",
                "",
                _markdown_table(
                    ranked,
                    (
                        "Team Rank",
                        "Global Rank",
                        "player_name",
                        "position_group",
                        "functional_role",
                        "minutes_played",
                        "tournament_impact_raw_v3",
                        "role_quality_v3",
                        "uncertainty_status_v3",
                    ),
                ),
                "",
                "## Outfield component totals",
                "",
                f"- Attack component total: "
                f"{pd.to_numeric(outfield.get('attack_component_v3'), errors='coerce').sum():.4f}",
                f"- Defensive component total: "
                f"{pd.to_numeric(outfield.get('defensive_component_v3'), errors='coerce').sum():.4f}",
                f"- Regulation/extra-time goals: "
                f"{pd.to_numeric(outfield.get('regulation_extra_time_goals'), errors='coerce').sum():.0f}",
                f"- Shootout goals excluded from ordinary impact: "
                f"{pd.to_numeric(outfield.get('shootout_goals'), errors='coerce').sum():.0f}",
                "",
                "## Main goalkeeper",
                "",
                _markdown_table(
                    goalkeeper,
                    (
                        "goalkeeper_rank_v3",
                        "player_name",
                        "continuous_goalkeeper_rating_v3",
                        "shootout_component_v3",
                        "dedicated_goalkeeper_score_v3",
                    ),
                ),
                "",
                "All rows use Qatar 2022 evidence only. Player/team identity, "
                "advancement, awards, reputation, and external rankings do not "
                "enter any score.",
                "",
            ]
        )

    def write_profiles_and_team_reports(
        self,
        rich: pd.DataFrame,
    ) -> list[Path]:
        """Regenerate all player, starter, team-profile, and team-report files."""

        player_root = self.reports_root / "player_profiles"
        starter_root = self.reports_root / "starters"
        team_profile_root = self.reports_root / "team_profiles"
        team_report_root = self.reports_root / "teams"
        existing_profiles = _existing_profile_paths(player_root)
        expected_player_paths: set[Path] = set()
        expected_starter_paths: set[Path] = set()
        expected_team_profiles: set[Path] = set()
        expected_team_reports: set[Path] = set()
        outputs: list[Path] = []

        for _, row in rich.sort_values("player_id").iterrows():
            player_id = int(row["player_id"])
            profile_path = existing_profiles.get(
                player_id,
                player_root
                / f"{_slug(str(row['player_name']))}-{player_id}.md",
            )
            _write_text(profile_path, self._profile_markdown(row))
            expected_player_paths.add(profile_path)
            outputs.append(profile_path)

            code = TEAM_CODES[str(row["team"])]
            base = starter_root / code / f"{player_id}_starter_report"
            starter_md = base.with_suffix(".md")
            starter_json = base.with_suffix(".json")
            payload = self._starter_payload(row)
            starter_markdown = self._profile_markdown(row).replace(
                "Player Profile",
                "Starter Report",
                1,
            )
            _write_text(starter_md, starter_markdown)
            _write_json(starter_json, payload)
            expected_starter_paths.update((starter_md, starter_json))
            outputs.extend((starter_md, starter_json))

        for team, code in sorted(TEAM_CODES.items(), key=lambda item: item[1]):
            squad = rich.loc[rich["team"].eq(team)].copy()
            markdown = self._team_profile_markdown(team, squad)
            team_profile = team_profile_root / f"{_slug(team)}.md"
            team_report_md = (
                team_report_root / f"{code}_team_coaching_report.md"
            )
            team_report_json = (
                team_report_root / f"{code}_team_coaching_report.json"
            )
            _write_text(team_profile, markdown)
            _write_text(team_report_md, markdown)
            _write_json(
                team_report_json,
                {
                    "active_model_version": ACTIVE_MODEL_VERSION,
                    "team": team,
                    "team_code": code,
                    "score_contract": {
                        "total": "Tournament Impact",
                        "rate": "Role Quality",
                        "confidence": "Uncertainty",
                    },
                    "players": [
                        self._starter_payload(row)
                        for _, row in squad.sort_values(
                            ["Team Rank", "player_id"],
                            na_position="last",
                            kind="mergesort",
                        ).iterrows()
                    ],
                },
            )
            expected_team_profiles.add(team_profile)
            expected_team_reports.update(
                (team_report_md, team_report_json)
            )
            outputs.extend(
                (team_profile, team_report_md, team_report_json)
            )

        _clean_generated_files(
            player_root,
            expected_player_paths,
            suffixes=(".md",),
        )
        _clean_generated_files(
            starter_root,
            expected_starter_paths,
            suffixes=(".md", ".json"),
        )
        _clean_generated_files(
            team_profile_root,
            expected_team_profiles,
            suffixes=(".md",),
        )
        _clean_generated_files(
            team_report_root,
            expected_team_reports,
            suffixes=(".md", ".json"),
        )
        return outputs

    @staticmethod
    def _save_figure(figure: Any, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(
            path,
            dpi=160,
            bbox_inches="tight",
            metadata={
                "Software": "World-Cup-S-Bomb ranking-repair-v3",
                "Title": path.stem,
            },
        )

    def write_figures(
        self,
        rich: pd.DataFrame,
        goalkeeper: pd.DataFrame,
        audit: Mapping[str, Any],
        champion: pd.DataFrame | None = None,
    ) -> list[Path]:
        """Generate the complete active v3 ranking figure family."""

        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.rcParams.update(
            {
                "font.family": "DejaVu Sans",
                "font.size": 9,
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "savefig.facecolor": "white",
            }
        )
        root = self.reports_root / "v3_figures"
        outputs: list[Path] = []

        def horizontal_bar(
            frame: pd.DataFrame,
            value: str,
            title: str,
            filename: str,
            *,
            label: str = "player_name",
            color: str = "#235789",
        ) -> None:
            plotted = frame.dropna(subset=[value]).tail(20)
            figure, axis = plt.subplots(figsize=(9, 7))
            axis.barh(
                plotted[label].astype(str),
                pd.to_numeric(plotted[value], errors="coerce"),
                color=color,
            )
            axis.set_title(title)
            axis.set_xlabel(value.replace("_", " ").title())
            axis.grid(axis="x", alpha=0.2)
            path = root / filename
            self._save_figure(figure, path)
            plt.close(figure)
            outputs.append(path)

        global_rows = (
            rich.loc[rich["position_group"].ne("Goalkeeper")]
            .sort_values("global_rank_v3", ascending=False)
            .tail(20)
        )
        horizontal_bar(
            global_rows,
            "tournament_impact_raw_v3",
            "Qatar 2022 — Global Outfield Tournament Impact",
            "v3_global_outfield_rankings.png",
        )
        rows_300 = (
            rich.loc[
                rich["position_group"].ne("Goalkeeper")
                & pd.to_numeric(
                    rich["minutes_played"],
                    errors="coerce",
                ).ge(300.0)
            ]
            .sort_values("global_rank_v3", ascending=False)
            .tail(20)
        )
        horizontal_bar(
            rows_300,
            "tournament_impact_raw_v3",
            "Qatar 2022 — 300+ Minute Tournament Impact",
            "v3_global_outfield_300min.png",
            color="#2A9D8F",
        )
        horizontal_bar(
            goalkeeper.sort_values(
                "goalkeeper_rank_v3",
                ascending=False,
            ).tail(15),
            "dedicated_goalkeeper_score_v3",
            "Qatar 2022 — Dedicated Main Goalkeeper Ranking",
            "v3_goalkeeper_rankings.png",
            color="#E76F51",
        )

        team_totals = (
            rich.loc[rich["position_group"].ne("Goalkeeper")]
            .groupby("team")["tournament_impact_raw_v3"]
            .sum()
            .sort_values(ascending=False)
        )
        representative_team = str(team_totals.index[0])
        representative = (
            rich.loc[
                rich["team"].eq(representative_team)
                & rich["Team Rank"].notna()
            ]
            .sort_values("Team Rank", ascending=False)
        )
        horizontal_bar(
            representative,
            "Tournament Performance Score",
            f"Representative Team — {representative_team}",
            "v3_representative_team_rankings.png",
            color="#6A4C93",
        )

        importance = (
            audit.get("defense", {})
            .get("selected_model", {})
            .get("permutation_importance", {})
        )
        if not importance:
            importance = audit.get("defense", {}).get(
                "permutation_importance",
                {},
            )
        if isinstance(importance, Mapping) and importance:
            importance_frame = pd.DataFrame(
                {
                    "feature": list(importance),
                    "importance": [
                        float(
                            value.get("mean", value)
                            if isinstance(value, Mapping)
                            else value
                        )
                        for value in importance.values()
                    ],
                }
            ).sort_values("importance").tail(20)
        else:
            component_columns = [
                column
                for column in rich.columns
                if column.endswith("_defensive_evidence_v3")
            ]
            importance_frame = pd.DataFrame(
                {
                    "feature": component_columns,
                    "importance": [
                        float(
                            pd.to_numeric(
                                rich[column],
                                errors="coerce",
                            ).std()
                        )
                        for column in component_columns
                    ],
                }
            ).sort_values("importance").tail(20)
        if importance_frame.empty:
            importance_frame = pd.DataFrame(
                {
                    "feature": ["selected defensive channel"],
                    "importance": [1.0],
                }
            )
        figure, axis = plt.subplots(figsize=(9, 6))
        axis.barh(
            importance_frame["feature"],
            importance_frame["importance"],
            color="#457B9D",
        )
        axis.set_title("Defensive Challenger — Permutation Importance")
        axis.set_xlabel("Held-out importance")
        axis.grid(axis="x", alpha=0.2)
        importance_path = root / "v3_defensive_feature_importance.png"
        self._save_figure(figure, importance_path)
        plt.close(figure)
        outputs.append(importance_path)

        movement_path = root / "v3_champion_challenger_movement.png"
        figure, axis = plt.subplots(figsize=(8, 7))
        if champion is not None and "player_id" in champion:
            champion_rank_column = (
                "Global Rank"
                if "Global Rank" in champion
                else "global_rank_v2"
            )
            movement = rich[
                ["player_id", "player_name", "global_rank_v3"]
            ].merge(
                champion[["player_id", champion_rank_column]],
                on="player_id",
                how="inner",
            )
            movement = movement.dropna().assign(
                _best=lambda frame: frame[
                    ["global_rank_v3", champion_rank_column]
                ].min(axis=1)
            ).nsmallest(50, "_best")
            axis.scatter(
                movement[champion_rank_column],
                movement["global_rank_v3"],
                alpha=0.75,
                color="#F4A261",
            )
            maximum = max(
                float(movement[champion_rank_column].max()),
                float(movement["global_rank_v3"].max()),
            )
            axis.plot([1, maximum], [1, maximum], "--", color="#555555")
            axis.set_xlabel("Champion publication rank")
            axis.set_ylabel("v3 outfield rank")
        else:
            axis.text(
                0.5,
                0.5,
                "Champion table unavailable",
                ha="center",
                va="center",
            )
        axis.set_title("Champion versus v3 Rank Movement")
        axis.invert_xaxis()
        axis.invert_yaxis()
        axis.grid(alpha=0.2)
        self._save_figure(figure, movement_path)
        plt.close(figure)
        outputs.append(movement_path)

        diagnostic_path = (
            root / "v3_position_composition_and_stability.png"
        )
        figure, axes = plt.subplots(1, 2, figsize=(12, 5))
        top100 = (
            rich.loc[rich["position_group"].ne("Goalkeeper")]
            .sort_values("global_rank_v3")
            .head(100)
        )
        counts = top100["position_group"].value_counts().sort_index()
        axes[0].bar(counts.index, counts.values, color="#2A9D8F")
        axes[0].set_title("Position composition — top 100")
        axes[0].tick_params(axis="x", rotation=45)
        axes[0].set_ylabel("Players")
        rank_width = (
            pd.to_numeric(
                rich.get("bootstrap_rank_worst_v3"),
                errors="coerce",
            )
            - pd.to_numeric(
                rich.get("bootstrap_rank_best_v3"),
                errors="coerce",
            )
        )
        axes[1].hist(
            rank_width.dropna(),
            bins=20,
            color="#E9C46A",
            edgecolor="white",
        )
        axes[1].set_title("Match-bootstrap rank-band width")
        axes[1].set_xlabel("Rank places")
        axes[1].set_ylabel("Players")
        self._save_figure(figure, diagnostic_path)
        plt.close(figure)
        outputs.append(diagnostic_path)
        return outputs

    def write_release_reference_files(
        self,
        audit: Mapping[str, Any],
    ) -> list[Path]:
        """Write field definitions and the release README."""

        feature_definitions = {
            "schema_version": "ranking-repair-features-3.0",
            "active_model_version": ACTIVE_MODEL_VERSION,
            "event_scope": {
                "ordinary_periods": [1, 2, 3, 4],
                "shootout_period": 5,
            },
            "fields": {
                "tournament_impact_raw_v3": (
                    "Signed common-unit Qatar 2022 total contribution; active "
                    "outfield global/team ordering field."
                ),
                "tournament_impact_v3": (
                    "Active signed common-unit Tournament Impact; identical "
                    "ordering semantics to tournament_impact_raw_v3."
                ),
                "tournament_impact_score_v3": (
                    "Global monotonic 0–1 display transform used by the six-"
                    "field compatibility publication; never normalized within "
                    "position."
                ),
                "role_quality_v3": (
                    "Single empirical-Bayes posterior contribution rate through "
                    "the probabilistic role mixture."
                ),
                "uncertainty_low_v3": (
                    "Lower match-bootstrap Tournament Impact interval endpoint."
                ),
                "uncertainty_high_v3": (
                    "Upper match-bootstrap Tournament Impact interval endpoint."
                ),
                "bootstrap_rank_best_v3": (
                    "Best endpoint of the match-bootstrap rank band."
                ),
                "bootstrap_rank_worst_v3": (
                    "Worst endpoint of the match-bootstrap rank band."
                ),
                "continuous_goalkeeper_rating_v3": (
                    "Once-reliability-adjusted continuous main-GK score; "
                    "ordinary non-shootout evidence only."
                ),
                "shootout_component_v3": (
                    "Separate goalkeeper shootout contribution capped at 0.10."
                ),
                "dedicated_goalkeeper_score_v3": (
                    "90% continuous allocation plus the bounded separate "
                    "shootout component."
                ),
                "percentile_equivalent_placement": (
                    "Explicit cross-position publication fallback; not measured "
                    "absolute common-unit contribution."
                ),
            },
            "goalkeeper_continuous_weights": {
                "shot_stopping": 0.40,
                "high_leverage_shot_stopping": 0.15,
                "cross_claim_control": 0.12,
                "sweeping": 0.10,
                "distribution_under_pressure": 0.10,
                "regular_penalty_performance": 0.13,
            },
            "goalkeeper_score_allocations": {
                "continuous": 0.90,
                "shootout_maximum": 0.10,
            },
            "retired_active_methods": [
                "within-position z-score as absolute global value",
                "450/180/90-minute repeated exposure cascade",
                "one-sided direct-defensive publication lift",
                "0.20 additive points per goalkeeper shootout save",
                "Blom/percentile bridge described as absolute value",
            ],
            "component_selections": audit.get(
                "component_selections",
                {},
            ),
        }
        feature_path = (
            self.results_root / "metadata" / "feature_definitions.json"
        )
        _write_json(feature_path, feature_definitions)
        readme_path = self.reports_root / "README.md"
        _write_text(
            readme_path,
            "\n".join(
                [
                    "# Qatar 2022 Generated Reports",
                    "",
                    f"Active player-ranking release: "
                    f"`{ACTIVE_MODEL_VERSION}`.",
                    "",
                    "- `ranking/player_rankings.csv` and "
                    "`ranking/player_rankings_v3.csv` are the active feature-"
                    "rich table.",
                    "- `ranking/player_rankings_v2.csv` and "
                    "`ranking/v5_player_rankings.csv` are byte-identical "
                    "filename compatibility aliases of that active table.",
                    "- `ranking/unified_tournament_rankings.csv` is the exact "
                    "six-field publication table.",
                    "- `ranking/legacy/` preserves historical rankings.",
                    "- `v3_figures/` is the active figure family; "
                    "`v5_figures/` is retained historical output.",
                    "- `canonical/model_summary.json` is the structured source "
                    "for synchronized model-summary Markdown aliases.",
                    "",
                    "Tournament Impact, Role Quality, and Uncertainty are "
                    "separate products. Ordinary performance uses periods 1–4; "
                    "period 5 is shootout-only.",
                    "",
                ]
            ),
        )
        return [feature_path, readme_path]

    def write_pass_checklist(
        self,
        audit: Mapping[str, Any],
    ) -> list[Path]:
        """Materialize the eight-pass checklist in JSON and Markdown."""

        payload = {
            "schema_version": "ranking-repair-pass-checklist-3.0",
            "active_model_version": ACTIVE_MODEL_VERSION,
            "release_status": audit.get("release_status"),
            "passes": audit.get("pass_gates", {}),
        }
        json_path = self.diagnostics_root / "pass_checklist.json"
        markdown_path = self.diagnostics_root / "pass_checklist.md"
        _write_json(json_path, payload)
        lines = [
            "# Ranking Repair Eight-Pass Checklist",
            "",
            f"- Active model: `{ACTIVE_MODEL_VERSION}`",
            f"- Release: **{audit.get('release_status', 'not recorded')}**",
            "",
            "| Pass | Decision | Selection/fallback | Tests |",
            "|---|---|---|---|",
        ]
        for number in range(1, 9):
            row = audit.get("pass_gates", {}).get(
                str(number),
                {},
            )
            lines.append(
                f"| {number} | {row.get('decision', 'not recorded')} | "
                f"{row.get('selection', row.get('fallback', '—'))} | "
                f"{row.get('tests', '—')} |"
            )
        _write_text(markdown_path, "\n".join(lines))
        return [json_path, markdown_path]

    def write_stale_content_audit(
        self,
        records: list[Mapping[str, Any]],
    ) -> list[Path]:
        """Write classified stale-formula search results from the runner."""

        payload = {
            "schema_version": "ranking-repair-stale-audit-3.0",
            "active_model_version": ACTIVE_MODEL_VERSION,
            "records": records,
            "classification_counts": (
                pd.Series(
                    [record.get("classification") for record in records],
                    dtype=str,
                )
                .value_counts()
                .sort_index()
                .to_dict()
            ),
            "active_stale_count": sum(
                record.get("classification") == "stale-requires-correction"
                for record in records
            ),
        }
        json_path = self.diagnostics_root / "stale_content_audit.json"
        markdown_path = self.diagnostics_root / "stale_content_audit.md"
        _write_json(json_path, payload)
        lines = [
            "# Ranking Repair Stale-Content Audit",
            "",
            f"- Active stale matches: **{payload['active_stale_count']}**",
            "",
            "| Path | Line | Pattern | Classification | Context |",
            "|---|---:|---|---|---|",
        ]
        for record in records:
            context = str(record.get("context", "")).replace("|", r"\|")
            lines.append(
                f"| `{record.get('path')}` | {record.get('line', '—')} | "
                f"`{record.get('pattern')}` | "
                f"{record.get('classification')} | {context} |"
            )
        _write_text(markdown_path, "\n".join(lines))
        return [json_path, markdown_path]

    def write_manifests(
        self,
        *,
        source_hashes: Mapping[str, Any] | None = None,
        active_model_version: str | None = None,
    ) -> list[Path]:
        """Write portable, deterministic final-state release manifests."""

        manifest_model_version = (
            active_model_version or ACTIVE_MODEL_VERSION
        )
        manifest_paths = {
            self.results_root / "metadata" / "artifact_manifest.json",
            self.reports_root / "artifact_manifest.json",
            self.reports_root / "v5_artifact_manifest.json",
            self.ranking_root / "refresh_manifest.json",
            self.reports_root / "pipeline_manifest.json",
            self.results_root / "metadata" / "pipeline_manifest.json",
        }
        files = sorted(
            (
                path
                for path in self.results_root.rglob("*")
                if path.is_file()
                and path not in manifest_paths
                and "__pycache__" not in path.parts
                and path.suffix.lower() != ".pyc"
            ),
            key=lambda path: path.relative_to(self.project_root).as_posix(),
        )
        entries = [
            {
                "path": path.relative_to(self.project_root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for path in files
        ]
        master = {
            "schema_version": "ranking-repair-artifact-manifest-3.0",
            "active_model_version": manifest_model_version,
            "path_contract": (
                "project-relative POSIX paths; no absolute or Windows paths"
            ),
            "excluded_self_referential_manifests": sorted(
                path.relative_to(self.project_root).as_posix()
                for path in manifest_paths
            ),
            "source_hashes": source_hashes or {},
            "artifact_count": len(entries),
            "artifacts": entries,
        }
        ranking_files = sorted(
            (
                path
                for path in self.ranking_root.rglob("*")
                if path.is_file()
                and path != self.ranking_root / "refresh_manifest.json"
            ),
            key=lambda path: path.relative_to(self.project_root).as_posix(),
        )
        refresh = {
            "schema_version": "ranking-repair-refresh-manifest-3.0",
            "active_model_version": manifest_model_version,
            "path_contract": "project-relative POSIX paths",
            "artifact_count": len(ranking_files),
            "artifacts": [
                {
                    "path": path.relative_to(self.project_root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
                for path in ranking_files
            ],
        }
        metadata_manifest = (
            self.results_root / "metadata" / "artifact_manifest.json"
        )
        report_manifest = self.reports_root / "artifact_manifest.json"
        v5_report_manifest = self.reports_root / "v5_artifact_manifest.json"
        refresh_manifest = self.ranking_root / "refresh_manifest.json"
        _write_json(metadata_manifest, master)
        serialized_master = (
            json.dumps(
                _json_value(master),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        _atomic_bytes(report_manifest, serialized_master)
        _atomic_bytes(v5_report_manifest, serialized_master)
        _write_json(refresh_manifest, refresh)
        pipeline = {
            "schema_version": "ranking-repair-pipeline-3.0",
            "active_model_version": manifest_model_version,
            "status": "complete",
            "ranking_manifest": (
                "results/reports/ranking/refresh_manifest.json"
            ),
            "artifact_manifest": (
                "results/metadata/artifact_manifest.json"
            ),
            "paths_are_project_relative_posix": True,
        }
        report_pipeline = self.reports_root / "pipeline_manifest.json"
        metadata_pipeline = (
            self.results_root / "metadata" / "pipeline_manifest.json"
        )
        _write_json(report_pipeline, pipeline)
        _write_json(metadata_pipeline, pipeline)
        return [
            metadata_manifest,
            report_manifest,
            v5_report_manifest,
            refresh_manifest,
            report_pipeline,
            metadata_pipeline,
        ]
