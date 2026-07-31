"""Deterministic publication writer for Tournament Impact v4 (outfield).

The scorer supplies one rich, all-player table.  This module validates that
table and publishes a complete parallel v4 artifact family.  It intentionally
does not import or call the v3 release writer: the only paths outside the
dedicated ``results/reports/v4`` tree are an explicit allow-list of
``*_v4.csv`` and ``*_v4.json`` ranking files.

The writer does not calculate or round the FIFA-style publication rating.
``Tournament Performance Score`` must already contain the supplied 55--99,
one-decimal value, and it is copied unchanged to every surface.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import re
import tempfile
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.reporting.artifacts import TEAM_CODES


MODEL_VERSION = "outfield_tournament_impact_v4"
ACTIVE_MODEL_VERSION = MODEL_VERSION
SCHEMA_VERSION = "outfield-tournament-impact-release-4.0"

EXPECTED_COHORT = {
    "players": 593,
    "outfield": 553,
    "main_goalkeepers": 32,
    "unified": 585,
    "outfield_300plus": 126,
    "unified_300plus": 142,
    "teams": 32,
}

DEFENSIVE_PIPELINE_STAGES = (
    "opposition_adjusted",
    "prevention_augmented",
    "reliability_shrunk",
    "variance_rescaled",
    "mixture_weighted",
)

REQUIRED_COLUMNS = frozenset(
    {
        "player_id",
        "player_name",
        "team",
        "position_group",
        "minutes_played",
        "is_main_goalkeeper",
        "tournament_impact_score_outfield_v4",
        "tournament_impact_rank_outfield_v4",
        "publication_global_rank_outfield_v4",
        "publication_team_rank_outfield_v4",
        "publication_score_outfield_v4",
        "Tournament Performance Score",
        "Global Rank",
        "Team Rank",
        "active_model_version",
    }
)

UNIFIED_COLUMNS = (
    "Global Rank",
    "Team Rank",
    "Player",
    "Team",
    "Position Group",
    "Tournament Performance Score",
)

RANKING_TABLE_STEMS = (
    "player_rankings_v4",
    "outfield_rankings_v4",
    "global_rankings_outfield_v4",
    "global_rankings_outfield_300min_v4",
    "player_rankings_300plus_v4",
    "unified_tournament_rankings_v4",
)

_ATTACK_COLUMNS = (
    "attack_component_outfield_v4",
    "attack_component_v4",
    "attack_value_reliability_shrunk_v4",
    "attacking_value_reliability_shrunk_v4",
    "attack_value_scaled_v4",
)

_DEFENSE_COLUMNS = (
    "defensive_component_outfield_v4",
    "defensive_component_v4",
    "defensive_value_variance_rescaled_v4",
    "defensive_value_reliability_shrunk_v4",
    "defensive_channel_scaled_v4",
)

_PROFILE_V4_PRIORITY = (
    "tournament_impact_raw_outfield_v4",
    "tournament_impact_score_outfield_v4",
    "tournament_impact_rank_outfield_v4",
    "position_rank_outfield_v4",
    "sub_role_rank_outfield_v4",
    "defensive_value_raw_v4",
    "opponent_attack_strength_faced_v4",
    "defensive_value_opposition_adjusted_v4",
    "off_ball_prevention_value_v4",
    "defensive_value_prevention_augmented_v4",
    "attack_reliability_v4",
    "defensive_reliability_v4",
    "attack_value_reliability_shrunk_v4",
    "defensive_value_reliability_shrunk_v4",
    "defensive_value_variance_rescaled_v4",
    "attack_weight_v4",
    "defense_weight_v4",
    "attacking_orientation_v4",
    "sub_role_v4",
    "tournament_impact_interval_low_outfield_v4",
    "tournament_impact_interval_high_outfield_v4",
    "bootstrap_rank_best_outfield_v4",
    "bootstrap_rank_worst_outfield_v4",
    "publication_global_rank_outfield_v4",
    "publication_team_rank_outfield_v4",
    "publication_score_outfield_v4",
)


def _json_value(value: Any) -> Any:
    """Convert pandas/NumPy objects to strict, deterministic JSON values."""

    if isinstance(value, Mapping):
        return {
            str(key): _json_value(item)
            for key, item in value.items()
        }
    if isinstance(value, pd.DataFrame):
        return [
            _json_value(record)
            for record in value.to_dict(orient="records")
        ]
    if isinstance(value, pd.Series):
        return {
            str(key): _json_value(item)
            for key, item in value.items()
        }
    if isinstance(value, np.ndarray):
        return [_json_value(item) for item in value.tolist()]
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [_json_value(item) for item in sorted(value, key=str)]
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return _json_value(value.item())
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (str, bytes, bool, int)) or value is None:
        return value
    try:
        missing = pd.isna(value)
    except (TypeError, ValueError):
        return str(value)
    if isinstance(missing, (bool, np.bool_)) and bool(missing):
        return None
    return value


def _atomic_bytes(path: Path, content: bytes) -> None:
    """Atomically replace one generated artifact."""

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


def _text_bytes(content: str) -> bytes:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    if normalized and not normalized.endswith("\n"):
        normalized += "\n"
    return normalized.encode("utf-8")


def _json_bytes(payload: Any) -> bytes:
    return _text_bytes(
        json.dumps(
            _json_value(payload),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )


def _csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    ).encode("utf-8")


def _slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", str(value)).encode(
        "ascii",
        "ignore",
    ).decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    return slug or "unknown"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bool_series(series: pd.Series) -> pd.Series:
    """Normalize a boolean flag without treating ``"False"`` as true."""

    if pd.api.types.is_bool_dtype(series.dtype):
        return series.fillna(False).astype(bool)
    normalized = series.map(
        lambda value: (
            False
            if pd.isna(value)
            else str(value).strip().lower() in {"1", "true", "yes", "y"}
        )
    )
    return normalized.astype(bool)


def _first_column(
    frame: pd.DataFrame,
    candidates: Sequence[str],
) -> str | None:
    return next(
        (column for column in candidates if column in frame.columns),
        None,
    )


def _markdown_value(value: Any) -> str:
    if value is None or value is pd.NA:
        return "—"
    try:
        if bool(pd.isna(value)):
            return "—"
    except (TypeError, ValueError):
        pass
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.4f}"
    return (
        str(value)
        .replace("|", r"\|")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def _markdown_table(
    frame: pd.DataFrame,
    columns: Iterable[str],
    *,
    labels: Mapping[str, str] | None = None,
) -> str:
    selected = [column for column in columns if column in frame.columns]
    if frame.empty or not selected:
        return "_No eligible rows._"
    headings = [
        (
            labels.get(column, column.replace("_", " ").title())
            if labels is not None
            else column.replace("_", " ").title()
        )
        for column in selected
    ]
    lines = [
        "| " + " | ".join(headings) + " |",
        "|" + "|".join("---" for _ in selected) + "|",
    ]
    for values in frame[selected].itertuples(index=False, name=None):
        lines.append(
            "| "
            + " | ".join(_markdown_value(value) for value in values)
            + " |"
        )
    return "\n".join(lines)


def _find_nested(
    mapping: Mapping[str, Any],
    key: str,
) -> Any:
    """Find the first deterministic occurrence of a key in an audit tree."""

    if key in mapping:
        return mapping[key]
    for child_key in sorted(mapping, key=str):
        child = mapping[child_key]
        if isinstance(child, Mapping):
            found = _find_nested(child, key)
            if found is not None:
                return found
    return None


class OutfieldV4ReleaseWriter:
    """Write the complete, isolated Tournament Impact outfield-v4 release."""

    def __init__(self, project_root: Path | str) -> None:
        self.project_root = Path(project_root).resolve()
        self.results_root = self.project_root / "results"
        self.reports_root = self.results_root / "reports"
        self.ranking_root = self.reports_root / "ranking"
        self.v4_root = self.reports_root / "v4"
        self.v4_ranking_root = self.v4_root / "ranking"
        self._top_level_paths = {
            self.ranking_root / f"{stem}.{suffix}"
            for stem in RANKING_TABLE_STEMS
            for suffix in ("csv", "json")
        }

    def _assert_owned_path(self, path: Path) -> None:
        """Reject any write that could overwrite a pre-v4 artifact."""

        resolved = path.resolve()
        if resolved in {item.resolve() for item in self._top_level_paths}:
            return
        try:
            resolved.relative_to(self.v4_root.resolve())
        except ValueError as error:
            raise ValueError(
                "OutfieldV4ReleaseWriter may write only explicit *_v4 "
                f"ranking files or the v4 report tree: {path}"
            ) from error
        if path.suffix.lower() == ".docx":
            raise ValueError("The outfield-v4 release must not create DOCX")

    def _write_bytes(self, path: Path, content: bytes) -> None:
        self._assert_owned_path(path)
        _atomic_bytes(path, content)

    def _write_text(self, path: Path, content: str) -> None:
        self._write_bytes(path, _text_bytes(content))

    def _write_json(self, path: Path, payload: Any) -> None:
        self._write_bytes(path, _json_bytes(payload))

    def _write_csv(self, path: Path, frame: pd.DataFrame) -> None:
        self._write_bytes(path, _csv_bytes(frame))

    @staticmethod
    def _masks(
        rankings: pd.DataFrame,
    ) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        goalkeeper = rankings["position_group"].eq("Goalkeeper")
        main_goalkeeper = goalkeeper & _bool_series(
            rankings["is_main_goalkeeper"]
        )
        outfield = ~goalkeeper
        unified = outfield | main_goalkeeper
        return outfield, goalkeeper, main_goalkeeper, unified

    @staticmethod
    def _assert_exact_rank(
        series: pd.Series,
        expected_count: int,
        *,
        field: str,
    ) -> None:
        values = pd.to_numeric(series, errors="coerce")
        if values.isna().any():
            raise ValueError(f"{field} has missing or non-numeric ranks")
        ordered = np.sort(values.to_numpy(dtype=float))
        expected = np.arange(1, expected_count + 1, dtype=float)
        if not np.array_equal(ordered, expected):
            raise ValueError(
                f"{field} must be exactly 1 through {expected_count}"
            )

    @classmethod
    def validate_frame(cls, rankings: pd.DataFrame) -> dict[str, int]:
        """Validate the complete supplied 593-row publication table."""

        if not isinstance(rankings, pd.DataFrame):
            raise TypeError("rankings must be a pandas DataFrame")
        missing = REQUIRED_COLUMNS.difference(rankings.columns)
        if missing:
            raise ValueError(
                f"outfield-v4 release fields missing: {sorted(missing)}"
            )
        if len(rankings) != EXPECTED_COHORT["players"]:
            raise ValueError(
                "outfield-v4 release requires exactly "
                f"{EXPECTED_COHORT['players']} players"
            )
        if rankings["player_id"].isna().any():
            raise ValueError("player_id must be present for every player")
        if rankings["player_id"].duplicated().any():
            raise ValueError("outfield-v4 release requires unique player_id")
        player_ids = pd.to_numeric(rankings["player_id"], errors="coerce")
        if (
            player_ids.isna().any()
            or not np.equal(player_ids, np.floor(player_ids)).all()
        ):
            raise ValueError("player_id must be an integer-valued field")
        if rankings["player_name"].isna().any():
            raise ValueError("player_name must be present for every player")
        if set(rankings["team"].astype(str)) != set(TEAM_CODES):
            raise ValueError(
                "The release must contain exactly the 32 Qatar 2022 teams"
            )
        if rankings["team"].nunique() != EXPECTED_COHORT["teams"]:
            raise ValueError("The release must contain exactly 32 teams")

        outfield, goalkeeper, main_goalkeeper, unified = cls._masks(
            rankings
        )
        counts = {
            "players": int(len(rankings)),
            "outfield": int(outfield.sum()),
            "goalkeepers": int(goalkeeper.sum()),
            "main_goalkeepers": int(main_goalkeeper.sum()),
            "unified": int(unified.sum()),
            "outfield_300plus": int(
                (
                    outfield
                    & pd.to_numeric(
                        rankings["minutes_played"], errors="coerce"
                    ).ge(300.0)
                ).sum()
            ),
            "unified_300plus": int(
                (
                    unified
                    & pd.to_numeric(
                        rankings["minutes_played"], errors="coerce"
                    ).ge(300.0)
                ).sum()
            ),
            "teams": int(rankings["team"].nunique()),
        }
        for key, expected in EXPECTED_COHORT.items():
            if counts[key] != expected:
                raise ValueError(
                    f"outfield-v4 cohort {key} must be {expected}, "
                    f"found {counts[key]}"
                )
        if (
            rankings.loc[main_goalkeeper]
            .groupby("team", sort=False)
            .size()
            .ne(1)
            .any()
            or rankings.loc[main_goalkeeper, "team"].nunique() != 32
        ):
            raise ValueError("Exactly one main goalkeeper per team is required")

        minutes = pd.to_numeric(rankings["minutes_played"], errors="coerce")
        if minutes.isna().any() or (minutes < 0.0).any():
            raise ValueError("minutes_played must be finite and nonnegative")

        cls._assert_exact_rank(
            rankings.loc[
                outfield, "tournament_impact_rank_outfield_v4"
            ],
            EXPECTED_COHORT["outfield"],
            field="tournament_impact_rank_outfield_v4",
        )
        cls._assert_exact_rank(
            rankings.loc[
                unified, "publication_global_rank_outfield_v4"
            ],
            EXPECTED_COHORT["unified"],
            field="publication_global_rank_outfield_v4",
        )
        cls._assert_exact_rank(
            rankings.loc[unified, "Global Rank"],
            EXPECTED_COHORT["unified"],
            field="Global Rank",
        )
        if pd.to_numeric(
            rankings.loc[~unified, "publication_global_rank_outfield_v4"],
            errors="coerce",
        ).notna().any():
            raise ValueError(
                "Backup goalkeepers must have null publication global ranks"
            )
        if pd.to_numeric(
            rankings.loc[~unified, "Global Rank"], errors="coerce"
        ).notna().any():
            raise ValueError("Backup goalkeepers must have null Global Rank")
        if pd.to_numeric(
            rankings.loc[~unified, "publication_team_rank_outfield_v4"],
            errors="coerce",
        ).notna().any():
            raise ValueError(
                "Backup goalkeepers must have null publication team ranks"
            )
        if pd.to_numeric(
            rankings.loc[~unified, "Team Rank"], errors="coerce"
        ).notna().any():
            raise ValueError("Backup goalkeepers must have null Team Rank")

        for team, squad in rankings.loc[unified].groupby(
            "team", sort=True
        ):
            cls._assert_exact_rank(
                squad["publication_team_rank_outfield_v4"],
                len(squad),
                field=(
                    "publication_team_rank_outfield_v4 "
                    f"for {team}"
                ),
            )
            cls._assert_exact_rank(
                squad["Team Rank"],
                len(squad),
                field=f"Team Rank for {team}",
            )

        global_rank = pd.to_numeric(
            rankings.loc[unified, "Global Rank"], errors="coerce"
        ).to_numpy(dtype=float)
        publication_global = pd.to_numeric(
            rankings.loc[
                unified, "publication_global_rank_outfield_v4"
            ],
            errors="coerce",
        ).to_numpy(dtype=float)
        if not np.array_equal(global_rank, publication_global):
            raise ValueError(
                "Global Rank must explicitly mirror "
                "publication_global_rank_outfield_v4"
            )
        team_rank = pd.to_numeric(
            rankings.loc[unified, "Team Rank"], errors="coerce"
        ).to_numpy(dtype=float)
        publication_team = pd.to_numeric(
            rankings.loc[
                unified, "publication_team_rank_outfield_v4"
            ],
            errors="coerce",
        ).to_numpy(dtype=float)
        if not np.array_equal(team_rank, publication_team):
            raise ValueError(
                "Team Rank must explicitly mirror "
                "publication_team_rank_outfield_v4"
            )

        outfield_score = pd.to_numeric(
            rankings.loc[
                outfield, "tournament_impact_score_outfield_v4"
            ],
            errors="coerce",
        )
        if (
            outfield_score.isna().any()
            or not np.isfinite(outfield_score.to_numpy()).all()
        ):
            raise ValueError(
                "Every outfielder requires a finite v4 Tournament Impact score"
            )

        publication_score = pd.to_numeric(
            rankings.loc[unified, "publication_score_outfield_v4"],
            errors="coerce",
        )
        display_score = pd.to_numeric(
            rankings.loc[unified, "Tournament Performance Score"],
            errors="coerce",
        )
        if publication_score.isna().any() or display_score.isna().any():
            raise ValueError(
                "Every unified row requires publication and display scores"
            )
        if not display_score.between(55.0, 99.0, inclusive="both").all():
            raise ValueError(
                "Tournament Performance Score must remain on the 55--99 scale"
            )
        scaled = display_score.to_numpy(dtype=float) * 10.0
        if not np.allclose(scaled, np.round(scaled), atol=1e-9, rtol=0.0):
            raise ValueError(
                "Tournament Performance Score must have at most one decimal"
            )
        expected_display = (
            publication_score.mul(44.0).add(55.0).round(1)
        )
        if not np.allclose(
            display_score.to_numpy(dtype=float),
            expected_display.to_numpy(dtype=float),
            atol=1e-9,
            rtol=0.0,
        ):
            raise ValueError(
                "Supplied FIFA-style score must equal "
                "round(55 + 44 * publication_score_outfield_v4, 1)"
            )

        versions = rankings["active_model_version"].dropna().astype(str)
        if len(versions) != len(rankings) or versions.nunique() != 1:
            raise ValueError(
                "active_model_version must be explicit and identical "
                "on all 593 rows"
            )
        if "v4" not in versions.iloc[0].lower():
            raise ValueError("active_model_version must explicitly identify v4")
        return counts

    @classmethod
    def validate_audit(
        cls,
        audit: Mapping[str, Any],
        *,
        model_version: str,
    ) -> tuple[str, ...]:
        """Validate the release-stage coupling recorded by the scorer."""

        if not isinstance(audit, Mapping):
            raise TypeError("audit must be a mapping")
        recorded = _find_nested(audit, "defensive_pipeline_stages")
        if recorded is None:
            raise ValueError(
                "audit must record defensive_pipeline_stages before release"
            )
        stages = tuple(str(stage) for stage in recorded)
        if stages != DEFENSIVE_PIPELINE_STAGES:
            raise ValueError(
                "defensive_pipeline_stages must be exactly "
                f"{list(DEFENSIVE_PIPELINE_STAGES)}"
            )
        audit_version = audit.get(
            "active_model_version",
            audit.get("model_version"),
        )
        if (
            audit_version is not None
            and str(audit_version) != model_version
        ):
            raise ValueError(
                "audit model version does not match the supplied rich table"
            )
        return stages

    @classmethod
    def validate_release(
        cls,
        rankings: pd.DataFrame,
        audit: Mapping[str, Any],
    ) -> dict[str, int]:
        """Validate all publication blockers without writing any file."""

        counts = cls.validate_frame(rankings)
        model_version = str(rankings["active_model_version"].iloc[0])
        cls.validate_audit(audit, model_version=model_version)
        return counts

    @staticmethod
    def _publication_frames(
        rankings: pd.DataFrame,
    ) -> dict[str, pd.DataFrame]:
        """Create deterministic views without mutating supplied rich values."""

        rich = rankings.copy(deep=True)
        rich["_release_sort_rank"] = pd.to_numeric(
            rich["Global Rank"], errors="coerce"
        )
        rich["_release_sort_id"] = pd.to_numeric(
            rich["player_id"], errors="raise"
        )
        rich = (
            rich.sort_values(
                ["_release_sort_rank", "team", "_release_sort_id"],
                na_position="last",
                kind="mergesort",
            )
            .drop(columns=["_release_sort_rank", "_release_sort_id"])
            .reset_index(drop=True)
        )
        rich["Player"] = rich["player_name"]
        rich["Team"] = rich["team"]
        rich["Position Group"] = rich["position_group"]

        outfield_mask, _, main_mask, unified_mask = (
            OutfieldV4ReleaseWriter._masks(rich)
        )
        outfield = (
            rich.loc[outfield_mask]
            .sort_values(
                [
                    "tournament_impact_rank_outfield_v4",
                    "player_id",
                ],
                kind="mergesort",
            )
            .reset_index(drop=True)
        )
        minutes = pd.to_numeric(rich["minutes_played"], errors="coerce")
        outfield_300 = (
            rich.loc[outfield_mask & minutes.ge(300.0)]
            .sort_values(
                [
                    "tournament_impact_rank_outfield_v4",
                    "player_id",
                ],
                kind="mergesort",
            )
            .reset_index(drop=True)
        )
        ranked_300 = (
            rich.loc[unified_mask & minutes.ge(300.0)]
            .sort_values(["Global Rank", "player_id"], kind="mergesort")
            .reset_index(drop=True)
        )
        unified = (
            rich.loc[unified_mask, list(UNIFIED_COLUMNS)]
            .sort_values("Global Rank", kind="mergesort")
            .reset_index(drop=True)
        )
        main_goalkeepers = (
            rich.loc[main_mask]
            .sort_values("Global Rank", kind="mergesort")
            .reset_index(drop=True)
        )
        return {
            "rich": rich,
            "outfield": outfield,
            "outfield_300": outfield_300,
            "ranked_300": ranked_300,
            "unified": unified,
            "main_goalkeepers": main_goalkeepers,
        }

    def _clean_owned_family(
        self,
        root: Path,
        expected: set[Path],
        *,
        suffixes: tuple[str, ...],
    ) -> None:
        """Delete only stale files inside one v4-owned generated family."""

        self._assert_owned_path(root / "_ownership_probe")
        if not root.exists():
            return
        resolved_expected = {path.resolve() for path in expected}
        for path in root.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in suffixes
                and path.resolve() not in resolved_expected
            ):
                path.unlink()

    def write_rankings(
        self,
        rankings: pd.DataFrame,
    ) -> dict[str, Any]:
        """Write all versioned global and per-team CSV/JSON ranking tables."""

        self.validate_frame(rankings)
        frames = self._publication_frames(rankings)
        table_frames = {
            "player_rankings_v4": frames["rich"],
            "outfield_rankings_v4": frames["outfield"],
            "global_rankings_outfield_v4": frames["outfield"],
            "global_rankings_outfield_300min_v4": frames["outfield_300"],
            "player_rankings_300plus_v4": frames["ranked_300"],
            "unified_tournament_rankings_v4": frames["unified"],
        }
        paths: list[Path] = []
        for stem in RANKING_TABLE_STEMS:
            frame = table_frames[stem]
            csv_path = self.ranking_root / f"{stem}.csv"
            json_path = self.ranking_root / f"{stem}.json"
            self._write_csv(csv_path, frame)
            self._write_json(
                json_path,
                frame.to_dict(orient="records"),
            )
            paths.extend((csv_path, json_path))

        rich_root = self.v4_ranking_root / "by_team"
        unified_root = self.v4_ranking_root / "by_team_unified"
        expected_rich: set[Path] = set()
        expected_unified: set[Path] = set()
        for team, code in sorted(TEAM_CODES.items(), key=lambda item: item[1]):
            team_rich = (
                frames["rich"]
                .loc[frames["rich"]["team"].eq(team)]
                .sort_values(
                    ["Team Rank", "player_id"],
                    na_position="last",
                    kind="mergesort",
                )
                .reset_index(drop=True)
            )
            team_unified = (
                frames["unified"]
                .loc[frames["unified"]["Team"].eq(team)]
                .sort_values("Team Rank", kind="mergesort")
                .reset_index(drop=True)
            )
            if team_rich.empty or team_unified.empty:
                raise ValueError(f"Missing v4 publication rows for {team}")
            for suffix, writer in (
                ("csv", self._write_csv),
                ("json", self._write_json),
            ):
                rich_path = rich_root / f"{code}.{suffix}"
                unified_path = unified_root / f"{code}.{suffix}"
                if suffix == "csv":
                    writer(rich_path, team_rich)
                    writer(unified_path, team_unified)
                else:
                    writer(
                        rich_path,
                        team_rich.to_dict(orient="records"),
                    )
                    writer(
                        unified_path,
                        team_unified.to_dict(orient="records"),
                    )
                expected_rich.add(rich_path)
                expected_unified.add(unified_path)
                paths.extend((rich_path, unified_path))
        self._clean_owned_family(
            rich_root,
            expected_rich,
            suffixes=(".csv", ".json"),
        )
        self._clean_owned_family(
            unified_root,
            expected_unified,
            suffixes=(".csv", ".json"),
        )
        return {
            **frames,
            "paths": paths,
        }

    @staticmethod
    def _audit_markdown(
        audit: Mapping[str, Any],
        *,
        model_version: str,
        counts: Mapping[str, int],
    ) -> str:
        release_status = audit.get("release_status", "not-recorded")
        selection = _find_nested(audit, "selected_configuration")
        variance = _find_nested(audit, "defensive_variance_share")
        return "\n".join(
            [
                "# Qatar 2022 Outfield Tournament Impact v4 — Release Audit",
                "",
                f"- Active model: `{model_version}`",
                f"- Release status: **{release_status}**",
                f"- Players: {counts['players']}",
                f"- Eligible outfielders: {counts['outfield']}",
                f"- Main goalkeepers: {counts['main_goalkeepers']}",
                f"- Unified publication rows: {counts['unified']}",
                f"- 300+ minute outfielders: {counts['outfield_300plus']}",
                f"- 300+ minute unified rows: {counts['unified_300plus']}",
                "",
                "## Coupled defensive pipeline",
                "",
                "The release records and validates this exact order:",
                "",
                "1. opposition_adjusted",
                "2. prevention_augmented",
                "3. reliability_shrunk",
                "4. variance_rescaled",
                "5. mixture_weighted",
                "",
                "Raw defense cannot be published through this writer as a "
                "rescaled v4 component.",
                "",
                "## Selected configuration",
                "",
                "```json",
                json.dumps(
                    _json_value(selection or {}),
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                    allow_nan=False,
                ),
                "```",
                "",
                "## Realized defensive variance share",
                "",
                (
                    _markdown_value(variance)
                    if variance is not None
                    else "Not separately recorded."
                ),
                "",
                "## Full structured audit",
                "",
                "See `ranking_audit_v4.json`. Named validation players are "
                "post-score fixtures only and never scoring features.",
                "",
            ]
        )

    @staticmethod
    def _methodology_markdown(model_version: str) -> str:
        return "\n".join(
            [
                "# Qatar 2022 Outfield Tournament Impact v4 — Methodology",
                "",
                f"Active model: `{model_version}`.",
                "",
                "Tournament Impact v4 is an evidence-accumulating tournament "
                "total. It contains no advancement, round-reached, winner, "
                "nationality, identity, award, reputation, or target-rank "
                "feature.",
                "",
                "The defensive channel is opposition-adjusted before adding "
                "validated off-ball prevention. Per-channel reliability then "
                "shrinks limited evidence before variance rescaling. Only the "
                "post-adjustment, post-prevention, post-shrinkage channel may "
                "be rescaled. Continuous attacking and defending orientation "
                "weights sum to one and are bounded away from zero and one.",
                "",
                "Predominant position and continuous sub-role are reporting "
                "frames, not score bonuses. High-minute contribution receives "
                "more evidential support through accumulated actions and "
                "reliability only.",
                "",
                "The six-field publication retains the supplied monotonic "
                "FIFA-style 55--99 score with one decimal. Raw model fields "
                "remain available in the rich tables and player packets.",
                "",
                "Goalkeepers retain their validated v3 publication bridge; "
                "only the 553 eligible outfield rows are rescored by this "
                "outfield-v4 model. Backup goalkeepers remain unranked.",
                "",
            ]
        )

    def write_audit_and_methodology(
        self,
        audit: Mapping[str, Any],
        *,
        model_version: str,
        counts: Mapping[str, int],
    ) -> tuple[dict[str, Any], list[Path]]:
        """Persist the exact structured audit used by every v4 summary."""

        enriched = {
            **dict(audit),
            "schema_version": audit.get(
                "schema_version",
                "outfield-tournament-impact-audit-4.0",
            ),
            "active_model_version": model_version,
            "defensive_pipeline_stages": list(
                DEFENSIVE_PIPELINE_STAGES
            ),
            "cohort_counts": dict(counts),
            "publication_contract": {
                "rich_rows": EXPECTED_COHORT["players"],
                "unified_rows": EXPECTED_COHORT["unified"],
                "fifa_style_score": "55--99, one decimal, supplied unchanged",
                "v3_artifacts_mutated": False,
                "docx_generated": False,
            },
        }
        json_path = self.v4_ranking_root / "ranking_audit_v4.json"
        markdown_path = self.v4_ranking_root / "ranking_audit_v4.md"
        methodology_path = (
            self.v4_ranking_root / "ranking_methodology_v4.md"
        )
        self._write_json(json_path, enriched)
        self._write_text(
            markdown_path,
            self._audit_markdown(
                enriched,
                model_version=model_version,
                counts=counts,
            ),
        )
        self._write_text(
            methodology_path,
            self._methodology_markdown(model_version),
        )
        return enriched, [json_path, markdown_path, methodology_path]

    @staticmethod
    def _v4_detail_fields(row: pd.Series) -> list[str]:
        priority = [
            field for field in _PROFILE_V4_PRIORITY if field in row.index
        ]
        remainder = sorted(
            field
            for field in row.index
            if (
                str(field).endswith("_v4")
                and field not in priority
                and field != "active_model_version"
            )
        )
        return priority + remainder

    @classmethod
    def _profile_markdown(cls, row: pd.Series) -> str:
        is_goalkeeper = str(row["position_group"]) == "Goalkeeper"
        role = row.get(
            "functional_role",
            row.get("sub_role_v4", "not recorded"),
        )
        lines = [
            f"# {row['player_name']} — Qatar 2022 v4 Player Profile",
            "",
            "This profile is generated after scoring. Player and team identity "
            "are labels only and never enter the model.",
            "",
            "## Publication",
            "",
            f"- Active model: `{row['active_model_version']}`",
            f"- Team: {row['team']}",
            f"- Position group: {row['position_group']}",
            f"- Functional/sub-role: {_markdown_value(role)}",
            f"- Minutes: {float(row['minutes_played']):.1f}",
            f"- Unified global rank: {_markdown_value(row.get('Global Rank'))}",
            f"- Team rank: {_markdown_value(row.get('Team Rank'))}",
            "- Tournament Performance Score: "
            f"{_markdown_value(row.get('Tournament Performance Score'))}",
            "",
        ]
        if is_goalkeeper:
            lines.extend(
                [
                    "The outfield v4 scorer does not rescore goalkeepers. Main "
                    "goalkeepers retain the validated goalkeeper publication "
                    "bridge; backup goalkeepers remain unranked.",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "The rank is determined by the opposition-aware, "
                    "positionally balanced outfield-v4 composite.",
                    "",
                ]
            )
        detail_fields = cls._v4_detail_fields(row)
        detail = pd.DataFrame(
            [
                {"field": field, "value": row.get(field)}
                for field in detail_fields
            ]
        )
        lines.extend(
            [
                "## v4 model detail",
                "",
                _markdown_table(detail, ("field", "value")),
                "",
                "## Interpretation boundary",
                "",
                "This is Qatar 2022 tournament evidence, not career quality. "
                "Continuous role weights are reporting/model channels rather "
                "than discrete role-bucket bonuses.",
                "",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _row_payload(row: pd.Series) -> dict[str, Any]:
        payload = {
            str(field): _json_value(value)
            for field, value in row.items()
        }
        payload["artifact_model_version"] = str(
            row["active_model_version"]
        )
        payload["identity_used_for_scoring"] = False
        payload["legacy_v3_fields_status"] = "preserved-source-only"
        return payload

    @staticmethod
    def _team_markdown(team: str, squad: pd.DataFrame) -> str:
        ranked = (
            squad.loc[squad["Team Rank"].notna()]
            .sort_values("Team Rank", kind="mergesort")
            .reset_index(drop=True)
        )
        outfield = squad.loc[
            squad["position_group"].ne("Goalkeeper")
        ]
        columns = [
            "Team Rank",
            "Global Rank",
            "player_name",
            "position_group",
            "functional_role",
            "minutes_played",
            "Tournament Performance Score",
            "tournament_impact_rank_outfield_v4",
        ]
        attack_column = _first_column(outfield, _ATTACK_COLUMNS)
        defense_column = _first_column(outfield, _DEFENSE_COLUMNS)
        attack_total = (
            pd.to_numeric(outfield[attack_column], errors="coerce").sum()
            if attack_column is not None
            else np.nan
        )
        defense_total = (
            pd.to_numeric(outfield[defense_column], errors="coerce").sum()
            if defense_column is not None
            else np.nan
        )
        return "\n".join(
            [
                f"# {team} — Qatar 2022 Outfield-v4 Team Profile",
                "",
                "Rows use the unified v4 publication order. Goalkeepers retain "
                "their existing publication bridge; the new balance model "
                "applies to outfielders.",
                "",
                "## Squad order",
                "",
                _markdown_table(ranked, columns),
                "",
                "## Outfield channel totals",
                "",
                f"- Attack field: `{attack_column or 'not supplied'}`",
                f"- Attack total: {_markdown_value(attack_total)}",
                f"- Defense field: `{defense_column or 'not supplied'}`",
                f"- Defense total: {_markdown_value(defense_total)}",
                "",
                "Identity, nationality, advancement, awards, reputation, and "
                "external rankings are not score inputs.",
                "",
            ]
        )

    def write_profiles_and_team_reports(
        self,
        rich: pd.DataFrame,
    ) -> list[Path]:
        """Write 593 profiles/packets and all 32 v4 team report families."""

        player_root = self.v4_root / "player_profiles"
        starter_root = self.v4_root / "starters"
        team_profile_root = self.v4_root / "team_profiles"
        team_report_root = self.v4_root / "teams"
        expected_players: set[Path] = set()
        expected_starters: set[Path] = set()
        expected_team_profiles: set[Path] = set()
        expected_team_reports: set[Path] = set()
        outputs: list[Path] = []

        for _, row in rich.sort_values("player_id", kind="mergesort").iterrows():
            player_id = int(row["player_id"])
            profile_path = (
                player_root
                / f"{_slug(str(row['player_name']))}-{player_id}.md"
            )
            self._write_text(profile_path, self._profile_markdown(row))
            expected_players.add(profile_path)
            outputs.append(profile_path)

            code = TEAM_CODES[str(row["team"])]
            base = starter_root / code / f"{player_id}_starter_report"
            markdown_path = base.with_suffix(".md")
            json_path = base.with_suffix(".json")
            self._write_text(
                markdown_path,
                self._profile_markdown(row).replace(
                    "Player Profile",
                    "Starter Report",
                    1,
                ),
            )
            self._write_json(json_path, self._row_payload(row))
            expected_starters.update((markdown_path, json_path))
            outputs.extend((markdown_path, json_path))

        for team, code in sorted(TEAM_CODES.items(), key=lambda item: item[1]):
            squad = rich.loc[rich["team"].eq(team)].copy()
            markdown = self._team_markdown(team, squad)
            profile_path = team_profile_root / f"{_slug(team)}.md"
            report_markdown_path = (
                team_report_root / f"{code}_team_coaching_report.md"
            )
            report_json_path = (
                team_report_root / f"{code}_team_coaching_report.json"
            )
            self._write_text(profile_path, markdown)
            self._write_text(report_markdown_path, markdown)
            self._write_json(
                report_json_path,
                {
                    "schema_version": "outfield-v4-team-report-4.0",
                    "active_model_version": str(
                        squad["active_model_version"].iloc[0]
                    ),
                    "team": team,
                    "team_code": code,
                    "identity_used_for_scoring": False,
                    "players": [
                        self._row_payload(row)
                        for _, row in squad.sort_values(
                            ["Team Rank", "player_id"],
                            na_position="last",
                            kind="mergesort",
                        ).iterrows()
                    ],
                },
            )
            expected_team_profiles.add(profile_path)
            expected_team_reports.update(
                (report_markdown_path, report_json_path)
            )
            outputs.extend(
                (profile_path, report_markdown_path, report_json_path)
            )

        self._clean_owned_family(
            player_root,
            expected_players,
            suffixes=(".md",),
        )
        self._clean_owned_family(
            starter_root,
            expected_starters,
            suffixes=(".md", ".json"),
        )
        self._clean_owned_family(
            team_profile_root,
            expected_team_profiles,
            suffixes=(".md",),
        )
        self._clean_owned_family(
            team_report_root,
            expected_team_reports,
            suffixes=(".md", ".json"),
        )
        return outputs

    @staticmethod
    def _top_outfield(rich: pd.DataFrame, limit: int = 50) -> pd.DataFrame:
        return (
            rich.loc[rich["position_group"].ne("Goalkeeper")]
            .sort_values(
                [
                    "tournament_impact_rank_outfield_v4",
                    "player_id",
                ],
                kind="mergesort",
            )
            .head(limit)
            .reset_index(drop=True)
        )

    @staticmethod
    def _summary_columns(frame: pd.DataFrame) -> list[str]:
        columns = [
            "tournament_impact_rank_outfield_v4",
            "Global Rank",
            "player_name",
            "team",
            "position_group",
            "minutes_played",
            "Tournament Performance Score",
        ]
        for candidates in (_ATTACK_COLUMNS, _DEFENSE_COLUMNS):
            column = _first_column(frame, candidates)
            if column is not None:
                columns.append(column)
        columns.extend(
            field
            for field in (
                "attack_weight_v4",
                "defense_weight_v4",
                "tournament_impact_interval_low_outfield_v4",
                "tournament_impact_interval_high_outfield_v4",
            )
            if field in frame.columns
        )
        return columns

    @staticmethod
    def _model_summary_payload(
        rich: pd.DataFrame,
        audit: Mapping[str, Any],
        counts: Mapping[str, int],
    ) -> dict[str, Any]:
        model_version = str(rich["active_model_version"].iloc[0])
        return {
            "schema_version": "outfield-v4-model-summary-4.0",
            "active_model_version": model_version,
            "tournament": "2022 FIFA World Cup (Qatar)",
            "release_status": audit.get("release_status"),
            "cohort": dict(counts),
            "active_fields": {
                "outfield_score": "tournament_impact_score_outfield_v4",
                "outfield_rank": "tournament_impact_rank_outfield_v4",
                "publication_global_rank": (
                    "publication_global_rank_outfield_v4"
                ),
                "publication_team_rank": (
                    "publication_team_rank_outfield_v4"
                ),
                "publication_score": "publication_score_outfield_v4",
                "display_score": "Tournament Performance Score",
            },
            "defensive_pipeline_stages": list(
                DEFENSIVE_PIPELINE_STAGES
            ),
            "publication_contract": {
                "outfield_model": "Tournament Impact v4 (outfield)",
                "goalkeeper_bridge": "preserved v3 bridge",
                "display_scale": "55--99 with one decimal",
                "round_bonus": False,
                "advancement_bonus": False,
                "identity_features": False,
            },
            "selected_configuration": _find_nested(
                audit, "selected_configuration"
            ),
            "validation": {
                "variance_share": _find_nested(
                    audit, "defensive_variance_share"
                ),
                "stability": _find_nested(audit, "stability"),
                "sensitivity": _find_nested(audit, "sensitivity"),
                "face_validity_gates": _find_nested(
                    audit, "face_validity_gates"
                ),
            },
            "limitations": audit.get("limitations", []),
        }

    @staticmethod
    def _model_summary_markdown(payload: Mapping[str, Any]) -> str:
        cohort = payload["cohort"]
        return "\n".join(
            [
                "# Qatar 2022 Outfield Tournament Impact v4 — Model Summary",
                "",
                f"- Active model: `{payload['active_model_version']}`",
                f"- Release status: **"
                f"{payload.get('release_status', 'not-recorded')}**",
                f"- Players: {cohort['players']}",
                f"- Eligible outfielders: {cohort['outfield']}",
                f"- Unified ranked rows: {cohort['unified']}",
                f"- Main goalkeepers: {cohort['main_goalkeepers']}",
                "",
                "## Architecture",
                "",
                "Opposition adjustment precedes off-ball prevention, which "
                "precedes evidence/reliability shrinkage. The shrunk channel "
                "is variance-rescaled before continuous attacking/defending "
                "mixture weights are applied. That order is validated as a "
                "release blocker.",
                "",
                "Tournament totals accumulate evidence. There are no team-"
                "advancement or round bonuses. Identity and external consensus "
                "are excluded from scoring.",
                "",
                "## Publication",
                "",
                "The rich table retains every supplied model field. The six-"
                "field table contains 585 eligible rows. The supplied monotonic "
                "FIFA-style score remains on 55--99 with one decimal.",
                "",
                "Goalkeepers retain the v3 publication bridge and backup "
                "goalkeepers remain unranked.",
                "",
            ]
        )

    @classmethod
    def _final_summary_markdown(
        cls,
        rich: pd.DataFrame,
        audit: Mapping[str, Any],
    ) -> str:
        top = cls._top_outfield(rich, 50)
        fixture_rows = _find_nested(audit, "fixture_movement")
        fixture_frame = (
            pd.DataFrame(fixture_rows)
            if isinstance(fixture_rows, (list, tuple))
            else pd.DataFrame()
        )
        lines = [
            "# Qatar 2022 Outfield Tournament Impact v4 — Final Summary",
            "",
            f"Active model: `{rich['active_model_version'].iloc[0]}`.",
            "",
            "## Final outfield top 50",
            "",
            _markdown_table(top, cls._summary_columns(top)),
            "",
            "## Named post-score fixtures",
            "",
        ]
        if fixture_frame.empty:
            lines.append(
                "Fixture diagnostics are available in the structured release "
                "audit."
            )
        else:
            lines.append(
                _markdown_table(fixture_frame, fixture_frame.columns)
            )
        lines.extend(
            [
                "",
                "## Release interpretation",
                "",
                "Names in fixture diagnostics are evaluation labels only. "
                "They do not select features, weights, shrinkage, variance "
                "targets, or ranks.",
                "",
            ]
        )
        return "\n".join(lines)

    @classmethod
    def _coaches_notebook_markdown(
        cls,
        rich: pd.DataFrame,
    ) -> str:
        team_leaders = (
            rich.loc[rich["Team Rank"].le(3)]
            .sort_values(["team", "Team Rank"], kind="mergesort")
            .reset_index(drop=True)
        )
        columns = [
            "team",
            "Team Rank",
            "Global Rank",
            "player_name",
            "position_group",
            "minutes_played",
            "Tournament Performance Score",
        ]
        return "\n".join(
            [
                "# Qatar 2022 Coaches Notebook — Outfield v4",
                "",
                "Use Tournament Impact for total Qatar 2022 contribution, "
                "within-position/sub-role ranks for contextual comparison, "
                "and interval/reliability fields for confidence.",
                "",
                "## Top three unified publication rows by team",
                "",
                _markdown_table(team_leaders, columns),
                "",
                "A high-minute defender earns stronger evidential support "
                "through accumulated tournament actions and reliability, not "
                "through advancement points.",
                "",
            ]
        )

    def write_summaries(
        self,
        rich: pd.DataFrame,
        audit: Mapping[str, Any],
        counts: Mapping[str, int],
    ) -> list[Path]:
        """Write synchronized canonical Markdown and JSON v4 summaries."""

        canonical_root = self.v4_root / "canonical"
        model_payload = self._model_summary_payload(rich, audit, counts)
        top = self._top_outfield(rich, 50)
        final_payload = {
            "schema_version": "outfield-v4-final-summary-4.0",
            "active_model_version": str(
                rich["active_model_version"].iloc[0]
            ),
            "release_status": audit.get("release_status"),
            "cohort": dict(counts),
            "top_50": top.to_dict(orient="records"),
            "fixture_movement": _find_nested(audit, "fixture_movement"),
            "selected_configuration": _find_nested(
                audit, "selected_configuration"
            ),
            "rejected_grid": _find_nested(audit, "rejected_grid"),
            "limitations": audit.get("limitations", []),
        }
        team_rows: list[dict[str, Any]] = []
        for team, code in sorted(TEAM_CODES.items(), key=lambda item: item[1]):
            leaders = (
                rich.loc[
                    rich["team"].eq(team) & rich["Team Rank"].notna()
                ]
                .sort_values("Team Rank", kind="mergesort")
                .head(3)
            )
            team_rows.append(
                {
                    "team": team,
                    "team_code": code,
                    "leaders": leaders.to_dict(orient="records"),
                }
            )
        coaches_payload = {
            "schema_version": "outfield-v4-coaches-notebook-4.0",
            "active_model_version": str(
                rich["active_model_version"].iloc[0]
            ),
            "usage": {
                "total": "Tournament Impact v4",
                "context": "position and continuous sub-role ranks",
                "confidence": "channel reliability and intervals",
            },
            "teams": team_rows,
        }
        outputs = {
            canonical_root / "model_summary.json": model_payload,
            canonical_root / "model_summary.md": (
                self._model_summary_markdown(model_payload)
            ),
            canonical_root / "final_summary.json": final_payload,
            canonical_root / "final_summary.md": (
                self._final_summary_markdown(rich, audit)
            ),
            canonical_root / "coaches_notebook.json": coaches_payload,
            canonical_root / "coaches_notebook.md": (
                self._coaches_notebook_markdown(rich)
            ),
        }
        for path, payload in outputs.items():
            if path.suffix == ".json":
                self._write_json(path, payload)
            else:
                self._write_text(path, str(payload))
        return list(outputs)

    def _save_figure(self, figure: Any, path: Path) -> None:
        buffer = io.BytesIO()
        figure.savefig(
            buffer,
            format="png",
            dpi=150,
            bbox_inches="tight",
            metadata={
                "Software": MODEL_VERSION,
                "Title": path.stem,
            },
        )
        self._write_bytes(path, buffer.getvalue())

    def write_figures(self, rich: pd.DataFrame) -> list[Path]:
        """Generate four deterministic v4 publication/diagnostic figures."""

        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt

        figure_root = self.v4_root / "figures"
        outputs: list[Path] = []
        expected: set[Path] = set()
        outfield = self._top_outfield(rich, len(rich))

        with plt.rc_context(
            {
                "font.family": "DejaVu Sans",
                "font.size": 9,
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "savefig.facecolor": "white",
            }
        ):
            top = outfield.head(20).iloc[::-1]
            figure, axis = plt.subplots(figsize=(9, 7))
            axis.barh(
                top["player_name"].astype(str),
                pd.to_numeric(
                    top["Tournament Performance Score"],
                    errors="coerce",
                ),
                color="#235789",
            )
            axis.set_title("Qatar 2022 — Outfield Tournament Impact v4")
            axis.set_xlabel("Tournament Performance Score (55–99)")
            axis.grid(axis="x", alpha=0.2)
            path = figure_root / "global_outfield_top20_v4.png"
            self._save_figure(figure, path)
            plt.close(figure)
            outputs.append(path)
            expected.add(path)

            top_300 = (
                outfield.loc[
                    pd.to_numeric(
                        outfield["minutes_played"], errors="coerce"
                    ).ge(300.0)
                ]
                .head(20)
                .iloc[::-1]
            )
            figure, axis = plt.subplots(figsize=(9, 7))
            axis.barh(
                top_300["player_name"].astype(str),
                pd.to_numeric(
                    top_300["Tournament Performance Score"],
                    errors="coerce",
                ),
                color="#2A9D8F",
            )
            axis.set_title("Qatar 2022 — 300+ Minute Outfield v4")
            axis.set_xlabel("Tournament Performance Score (55–99)")
            axis.grid(axis="x", alpha=0.2)
            path = figure_root / "outfield_300min_top20_v4.png"
            self._save_figure(figure, path)
            plt.close(figure)
            outputs.append(path)
            expected.add(path)

            attack_column = _first_column(outfield, _ATTACK_COLUMNS)
            defense_column = _first_column(outfield, _DEFENSE_COLUMNS)
            figure, axis = plt.subplots(figsize=(8, 6))
            if attack_column is not None and defense_column is not None:
                axis.scatter(
                    pd.to_numeric(
                        outfield[attack_column], errors="coerce"
                    ),
                    pd.to_numeric(
                        outfield[defense_column], errors="coerce"
                    ),
                    c=pd.to_numeric(
                        outfield["minutes_played"], errors="coerce"
                    ),
                    cmap="viridis",
                    alpha=0.65,
                    s=20,
                )
                axis.axhline(0.0, color="#777777", linewidth=0.8)
                axis.axvline(0.0, color="#777777", linewidth=0.8)
                axis.set_xlabel(attack_column.replace("_", " ").title())
                axis.set_ylabel(defense_column.replace("_", " ").title())
                axis.set_title(
                    "Outfield v4 — Attack/Defense Channel Balance"
                )
            else:
                axis.scatter(
                    pd.to_numeric(
                        outfield["minutes_played"], errors="coerce"
                    ),
                    pd.to_numeric(
                        outfield["Tournament Performance Score"],
                        errors="coerce",
                    ),
                    color="#6A4C93",
                    alpha=0.65,
                    s=20,
                )
                axis.set_xlabel("Minutes played")
                axis.set_ylabel("Tournament Performance Score")
                axis.set_title("Outfield v4 — Evidence Accumulation")
            axis.grid(alpha=0.2)
            path = figure_root / "channel_balance_v4.png"
            self._save_figure(figure, path)
            plt.close(figure)
            outputs.append(path)
            expected.add(path)

            top100 = outfield.head(100)
            all_counts = (
                outfield["position_group"].value_counts().sort_index()
            )
            top_counts = (
                top100["position_group"]
                .value_counts()
                .reindex(all_counts.index, fill_value=0)
            )
            x = np.arange(len(all_counts))
            width = 0.38
            figure, axis = plt.subplots(figsize=(10, 6))
            axis.bar(
                x - width / 2.0,
                all_counts.to_numpy(),
                width,
                label="All outfielders",
                color="#457B9D",
            )
            axis.bar(
                x + width / 2.0,
                top_counts.to_numpy(),
                width,
                label="Top 100",
                color="#E9C46A",
            )
            axis.set_xticks(x, all_counts.index, rotation=35, ha="right")
            axis.set_ylabel("Players")
            axis.set_title("Outfield v4 — Position Composition")
            axis.legend()
            axis.grid(axis="y", alpha=0.2)
            path = figure_root / "position_composition_v4.png"
            self._save_figure(figure, path)
            plt.close(figure)
            outputs.append(path)
            expected.add(path)

        self._clean_owned_family(
            figure_root,
            expected,
            suffixes=(".png",),
        )
        return outputs

    def write_manifest(
        self,
        paths: Iterable[Path],
        *,
        model_version: str,
        counts: Mapping[str, int],
    ) -> Path:
        """Write a portable, deterministic manifest for only v4 artifacts."""

        manifest_path = self.v4_root / "artifact_manifest.json"
        unique_paths = sorted(
            {
                Path(path).resolve()
                for path in paths
                if Path(path).resolve() != manifest_path.resolve()
            },
            key=lambda path: path.relative_to(
                self.project_root
            ).as_posix(),
        )
        for path in unique_paths:
            self._assert_owned_path(path)
            if not path.is_file():
                raise ValueError(f"Cannot manifest missing artifact: {path}")
            if path.suffix.lower() == ".docx":
                raise ValueError("DOCX is excluded from outfield-v4 release")
        entries = [
            {
                "path": path.relative_to(self.project_root).as_posix(),
                "bytes": int(path.stat().st_size),
                "sha256": _sha256(path),
            }
            for path in unique_paths
        ]
        payload = {
            "schema_version": "outfield-v4-artifact-manifest-4.0",
            "active_model_version": model_version,
            "path_contract": "project-relative POSIX paths",
            "self_referential_manifest_excluded": (
                manifest_path.relative_to(self.project_root).as_posix()
            ),
            "cohort_counts": dict(counts),
            "artifact_count": len(entries),
            "artifacts": entries,
        }
        self._write_json(manifest_path, payload)
        return manifest_path

    def write_release(
        self,
        rankings: pd.DataFrame,
        audit: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Validate and write the complete parallel outfield-v4 release.

        Returns a small API summary.  ``paths`` contains ``Path`` objects for
        every generated file, including the manifest; ``artifact_paths``
        contains the same project-relative values as strings for callers that
        need a JSON-ready response.
        """

        counts = self.validate_release(rankings, audit)
        model_version = str(rankings["active_model_version"].iloc[0])

        ranking_output = self.write_rankings(rankings)
        rich = ranking_output["rich"]
        enriched_audit, audit_paths = self.write_audit_and_methodology(
            audit,
            model_version=model_version,
            counts=counts,
        )
        profile_paths = self.write_profiles_and_team_reports(rich)
        summary_paths = self.write_summaries(
            rich,
            enriched_audit,
            counts,
        )
        figure_paths = self.write_figures(rich)
        generated = [
            *ranking_output["paths"],
            *audit_paths,
            *profile_paths,
            *summary_paths,
            *figure_paths,
        ]
        manifest_path = self.write_manifest(
            generated,
            model_version=model_version,
            counts=counts,
        )
        paths = sorted(
            [*generated, manifest_path],
            key=lambda path: path.relative_to(
                self.project_root
            ).as_posix(),
        )
        return {
            "active_model_version": model_version,
            "schema_version": SCHEMA_VERSION,
            "cohort_counts": counts,
            "manifest": manifest_path,
            "paths": paths,
            "artifacts": paths,
            "artifact_paths": [
                path.relative_to(self.project_root).as_posix()
                for path in paths
            ],
        }

