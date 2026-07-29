"""Qatar 2022 position-aware player and goalkeeper rankings.

The legacy composite is strongest at measuring repeatable on-ball value, but
it has no explicit goals/xG channel and normalizes several inputs across broad
roles.  That structure systematically suppresses penalty-box forwards while
allowing high-volume possession roles to dominate the global table.

This module adds a tournament-only ranking layer.  It preserves the legacy
rating and rank columns, assigns a formal 360-aware position group, builds
within-position contribution percentiles, adds a modest common tournament
impact channel, and applies reliability shrinkage.  Player names are never
used by the scoring functions; names appear only in the post-score audit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd


POSITION_GROUP_360 = ("GK", "CB", "FB", "DM", "CM", "AM", "FW")

POSITION_GROUP_MAP: dict[str, str] = {
    "Goalkeeper": "GK",
    "Center Back": "CB",
    "Centre Back": "CB",
    "Fullback/Wingback": "FB",
    "Defensive Midfield": "DM",
    "Central/Wide Midfield": "CM",
    "Attacking Midfield/Wing": "AM",
    "Forward": "FW",
}

# Components sum to one for each position.  The common-impact channel uses the
# same tournament-wide scale for every outfield player; the remaining channels
# are normalized within the formal 360 position group.
POSITION_COMPONENT_WEIGHTS: dict[str, dict[str, float]] = {
    "FW": {
        "finishing": 0.47,
        "creation": 0.17,
        "progression": 0.06,
        "possession": 0.04,
        "defending": 0.04,
        "off_ball": 0.10,
        "tournament_impact": 0.12,
    },
    "AM": {
        "finishing": 0.25,
        "creation": 0.28,
        "progression": 0.14,
        "possession": 0.08,
        "defending": 0.05,
        "off_ball": 0.08,
        "tournament_impact": 0.12,
    },
    "CM": {
        "finishing": 0.10,
        "creation": 0.25,
        "progression": 0.23,
        "possession": 0.15,
        "defending": 0.13,
        "off_ball": 0.07,
        "tournament_impact": 0.07,
    },
    "DM": {
        "finishing": 0.05,
        "creation": 0.13,
        "progression": 0.22,
        "possession": 0.18,
        "defending": 0.28,
        "off_ball": 0.10,
        "tournament_impact": 0.04,
    },
    "FB": {
        "finishing": 0.08,
        "creation": 0.18,
        "progression": 0.20,
        "possession": 0.12,
        "defending": 0.25,
        "off_ball": 0.10,
        "tournament_impact": 0.07,
    },
    "CB": {
        "finishing": 0.03,
        "creation": 0.05,
        "progression": 0.17,
        "possession": 0.18,
        "defending": 0.37,
        "off_ball": 0.15,
        "tournament_impact": 0.05,
    },
}

COMPONENT_METRICS: dict[str, tuple[str, ...]] = {
    "finishing_rate": (
        "goals_p90",
        "xg_p90",
        "shots_p90",
        "finishing_score",
    ),
    "finishing_volume": ("goals", "xg_sum"),
    "creation_rate": (
        "xa_p90",
        "key_passes_p90",
        "box_passes_p90",
        "creation_score",
    ),
    "creation_volume": ("xa_sum", "key_passes"),
    "progression": (
        "progressive_carries_p90",
        "progressive_passes_p90",
        "progression_score",
        "xt_p90",
    ),
    "possession": (
        "ball_security_score",
        "pass_completion",
        "vaep_per_touch",
    ),
    "defending": (
        "defensive_score",
        "pressing_score",
        "aerial_score",
        "vaep_def_p90",
        "interceptions_p90",
        "blocks_p90",
        "aerial_wins_p90",
    ),
    "off_ball": (
        "off_ball_score",
        "attacking_off_ball_score",
        "defensive_off_ball_score",
    ),
    "tournament_impact": (
        "goals",
        "xg_sum",
        "xa_sum",
        "vaep_total",
        "xt_total",
    ),
}

GOALKEEPER_V2_WEIGHTS: dict[str, float] = {
    "goals_prevented_proxy_p90": 0.18,
    "save_rate": 0.10,
    "high_leverage_save_pct": 0.07,
    "penalties_saved": 0.32,
    "penalty_save_rate_shrunk": 0.10,
    "cross_stopping_rate": 0.06,
    "sweeper_actions_p90": 0.04,
    "distribution_under_pressure": 0.04,
    "claims_p90": 0.03,
    "minutes": 0.06,
}


@dataclass(frozen=True)
class TournamentRankingConfig:
    """Tunable, deterministic Qatar 2022 ranking hyperparameters."""

    component_weights: Mapping[str, Mapping[str, float]] = field(
        default_factory=lambda: {
            group: dict(weights)
            for group, weights in POSITION_COMPONENT_WEIGHTS.items()
        }
    )
    goalkeeper_weights: Mapping[str, float] = field(
        default_factory=lambda: dict(GOALKEEPER_V2_WEIGHTS)
    )
    reliability_minutes: float = 180.0
    target_forward_threshold: float = 0.70
    target_forward_maximum_boost: float = 0.06

    def __post_init__(self) -> None:
        if set(self.component_weights) != set(POSITION_COMPONENT_WEIGHTS):
            raise ValueError("Position weights must cover CB/FB/DM/CM/AM/FW")
        for group, weights in self.component_weights.items():
            if set(weights) != set(next(iter(POSITION_COMPONENT_WEIGHTS.values()))):
                raise ValueError(f"Unexpected component weights for {group}")
            if any(weight < 0.0 for weight in weights.values()):
                raise ValueError(f"Negative component weight for {group}")
            if not np.isclose(sum(weights.values()), 1.0):
                raise ValueError(f"Component weights for {group} must sum to one")
        if not np.isclose(sum(self.goalkeeper_weights.values()), 1.0):
            raise ValueError("Goalkeeper weights must sum to one")
        if self.reliability_minutes <= 0.0:
            raise ValueError("Reliability minutes must be positive")


def _numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    """Return one numeric column or an all-missing aligned series."""

    if column not in frame:
        return pd.Series(np.nan, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce")


def _mean_percentile(
    frame: pd.DataFrame,
    columns: Sequence[str],
    *,
    group: pd.Series | None,
) -> pd.Series:
    """Average robust percentiles without treating unavailable data as zero."""

    percentiles: list[pd.Series] = []
    for column in columns:
        values = _numeric(frame, column)
        if values.notna().sum() == 0:
            continue
        if group is None:
            ranked = values.rank(method="average", pct=True)
        else:
            ranked = values.groupby(group).rank(method="average", pct=True)
        percentiles.append(ranked)
    if not percentiles:
        return pd.Series(0.5, index=frame.index, dtype=float)
    return (
        pd.concat(percentiles, axis=1)
        .mean(axis=1, skipna=True)
        .fillna(0.5)
        .clip(0.0, 1.0)
    )


def infer_position_group_360(players: pd.DataFrame) -> pd.Series:
    """Infer the formal primary group from Qatar 2022 usage fields."""

    broad = players.get(
        "position_group",
        pd.Series("", index=players.index, dtype=object),
    ).fillna("").astype(str)
    specific = players.get(
        "position",
        pd.Series("", index=players.index, dtype=object),
    ).fillna("").astype(str)
    combined = broad + " " + specific

    inferred = broad.map(POSITION_GROUP_MAP)
    pattern_groups = (
        ("GK", r"goalkeeper"),
        ("CB", r"cent(?:er|re) back"),
        ("FB", r"wing back|fullback|right back|left back"),
        ("DM", r"defensive midfield"),
        ("AM", r"attacking midfield|right wing|left wing"),
        ("CM", r"cent(?:er|ral) midfield|right midfield|left midfield"),
        ("FW", r"forward|striker"),
    )
    for group, pattern in pattern_groups:
        inferred = inferred.mask(
            inferred.isna() & combined.str.contains(pattern, case=False),
            group,
        )
    role = players.get(
        "functional_role",
        pd.Series("", index=players.index, dtype=object),
    ).fillna("").astype(str)
    # StatsBomb lists wide midfielders separately from wingers.  In a 360
    # usage framework, wide midfielders with an explicitly attacking role and
    # final-third profile belong with AM/wide attackers rather than central
    # midfielders.
    attacking_wide_midfielder = (
        broad.eq("Central/Wide Midfield")
        & specific.str.contains(r"left midfield|right midfield", case=False)
        & role.str.contains(
            r"winger|wide creator|target forward",
            case=False,
            regex=True,
        )
    )
    inferred = inferred.mask(attacking_wide_midfielder, "AM")
    if inferred.isna().any():
        labels = sorted(combined.loc[inferred.isna()].unique())
        raise ValueError(f"Unable to infer position_group_360 for: {labels}")
    if not set(inferred.unique()) <= set(POSITION_GROUP_360):
        raise ValueError("Unexpected position_group_360 label")
    return inferred.astype(str)


def _role_repair(row: pd.Series) -> str:
    """Resolve hard role/position contradictions with feature-driven labels."""

    group = str(row["position_group_360"])
    original = str(row.get("functional_role_original", "") or "")
    lower = original.lower()
    progression = float(row.get("progression_score", 0.5) or 0.5)
    creation = float(row.get("creation_score", 0.5) or 0.5)
    defending = float(row.get("defensive_score", 0.5) or 0.5)
    pressing = float(row.get("pressing_score", 0.5) or 0.5)
    finishing = float(row.get("finishing_score", 0.5) or 0.5)

    if group == "GK":
        return "Goalkeeper"
    if group == "CB" and any(
        token in lower
        for token in ("target forward", "winger", "wide creator", "anchor")
    ):
        return (
            "Ball-Playing Centre-Back"
            if max(progression, creation) >= defending
            else "Defensive Centre-Back"
        )
    if group == "FB" and any(
        token in lower
        for token in ("sweeper cb", "target forward", "holding anchor")
    ):
        return (
            "Attacking Wingback"
            if max(progression, creation) >= defending
            else "Two-Way Fullback"
        )
    if group == "DM" and any(
        token in lower
        for token in ("target forward", "winger", "wide creator", "sweeper cb")
    ):
        if defending >= max(progression, creation):
            return "Ball-Winning Midfielder"
        if progression >= creation:
            return "Deep Playmaker"
        return "Holding / Controlling Midfielder"
    if group == "CM" and "target forward" in lower:
        return (
            "Box-to-Box / Engine Midfielder"
            if pressing >= creation
            else "Advanced Playmaker"
        )
    if group == "AM" and "holding anchor" in lower:
        return (
            "Pressing Attacker"
            if pressing >= max(creation, finishing)
            else "Linking Attacker"
        )
    if group == "FW" and "holding anchor" in lower:
        return (
            "Pressing Forward"
            if pressing >= finishing
            else "Linking Forward"
        )
    if group == "FW" and lower == "ball-winner":
        return "Pressing Forward"
    if not original:
        return {
            "CB": "Centre-Back",
            "FB": "Two-Way Fullback",
            "DM": "Holding Midfielder",
            "CM": "Central Midfielder",
            "AM": "Attacking Midfielder",
            "FW": "Forward",
        }[group]
    return original


def resolve_functional_roles(players: pd.DataFrame) -> pd.DataFrame:
    """Preserve the source role and materialize a coherent reporting role."""

    output = players.copy()
    if "functional_role_original" not in output:
        output["functional_role_original"] = output.get(
            "functional_role",
            pd.Series("", index=output.index),
        )
    output["functional_role"] = output.apply(_role_repair, axis=1)
    output["role_consistency_adjusted"] = (
        output["functional_role"].astype(str)
        != output["functional_role_original"].astype(str)
    )
    return output


def _outfield_components(outfield: pd.DataFrame) -> pd.DataFrame:
    """Create interpretable within-position and common-impact components."""

    group = outfield["position_group_360"]
    finishing_rate = _mean_percentile(
        outfield,
        COMPONENT_METRICS["finishing_rate"],
        group=group,
    )
    finishing_volume = _mean_percentile(
        outfield,
        COMPONENT_METRICS["finishing_volume"],
        group=None,
    )
    creation_rate = _mean_percentile(
        outfield,
        COMPONENT_METRICS["creation_rate"],
        group=group,
    )
    creation_volume = _mean_percentile(
        outfield,
        COMPONENT_METRICS["creation_volume"],
        group=None,
    )
    return pd.DataFrame(
        {
            "finishing": 0.50 * finishing_rate + 0.50 * finishing_volume,
            "creation": 0.55 * creation_rate + 0.45 * creation_volume,
            "progression": _mean_percentile(
                outfield,
                COMPONENT_METRICS["progression"],
                group=group,
            ),
            "possession": _mean_percentile(
                outfield,
                COMPONENT_METRICS["possession"],
                group=group,
            ),
            "defending": _mean_percentile(
                outfield,
                COMPONENT_METRICS["defending"],
                group=group,
            ),
            "off_ball": _mean_percentile(
                outfield,
                COMPONENT_METRICS["off_ball"],
                group=group,
            ),
            "tournament_impact": _mean_percentile(
                outfield,
                COMPONENT_METRICS["tournament_impact"],
                group=None,
            ),
        },
        index=outfield.index,
    ).clip(0.0, 1.0)


def _robust_unit_scale(values: pd.Series) -> pd.Series:
    """Rescale ratings to 0–1 while preserving the complete ordering."""

    numeric = pd.to_numeric(values, errors="coerce")
    lower = numeric.min()
    upper = numeric.max()
    if not np.isfinite(lower) or not np.isfinite(upper) or upper <= lower:
        return pd.Series(0.5, index=values.index, dtype=float)
    return ((numeric - lower) / (upper - lower)).clip(0.0, 1.0)


def _calculate_outfield_v2(
    players: pd.DataFrame,
    config: TournamentRankingConfig,
) -> pd.DataFrame:
    """Score and rank all eligible outfield players."""

    outfield = players.copy()
    components = _outfield_components(outfield)
    for component in components:
        outfield[f"{component}_component_v2"] = components[component]

    raw = pd.Series(0.0, index=outfield.index)
    for group, weights in config.component_weights.items():
        mask = outfield["position_group_360"].eq(group)
        raw.loc[mask] = sum(
            weight * components.loc[mask, component]
            for component, weight in weights.items()
        )

    role = outfield["functional_role"].fillna("").str.lower()
    goal_role = (
        outfield["position_group_360"].eq("FW")
        & role.str.contains(
            r"target forward|penalty-box|finishing|poacher",
            regex=True,
        )
    )
    boost = (
        (components["finishing"] - config.target_forward_threshold)
        .clip(lower=0.0)
        / max(1.0 - config.target_forward_threshold, 1e-9)
        * config.target_forward_maximum_boost
    )
    outfield["goal_role_boost_v2"] = boost.where(goal_role, 0.0)
    raw = (raw + outfield["goal_role_boost_v2"]).clip(0.0, 1.0)

    minutes = _numeric(outfield, "minutes").fillna(0.0).clip(lower=0.0)
    reliability = minutes / (minutes + config.reliability_minutes)
    position_prior = raw.groupby(outfield["position_group_360"]).transform(
        "mean"
    )
    shrunk = reliability * raw + (1.0 - reliability) * position_prior

    outfield["raw_player_rating_v2"] = raw
    outfield["rating_reliability_v2"] = reliability
    outfield["final_player_rating_v2"] = _robust_unit_scale(shrunk)
    outfield["global_rank_v2"] = (
        outfield["final_player_rating_v2"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    outfield["position_rank_v2"] = (
        outfield.groupby("position_group_360")["final_player_rating_v2"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    outfield["role_rank_v2"] = (
        outfield.groupby("functional_role")["final_player_rating_v2"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    outfield["team_rank_v2"] = (
        outfield.groupby("team")["final_player_rating_v2"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    outfield["gk_rating_v2"] = np.nan
    outfield["gk_rank_v2"] = pd.Series(
        pd.NA,
        index=outfield.index,
        dtype="Int64",
    )
    return outfield


def _calculate_goalkeepers_v2(
    players: pd.DataFrame,
    config: TournamentRankingConfig,
) -> pd.DataFrame:
    """Score only each team's main goalkeeper on a separate scale."""

    goalkeepers = players.copy()
    selection = goalkeepers.assign(
        _selection_minutes=_numeric(goalkeepers, "minutes").fillna(0.0),
        _selection_actions=_numeric(goalkeepers, "actions").fillna(0.0),
        _selection_player_id=_numeric(
            goalkeepers,
            "player_id",
        ).fillna(np.inf),
    ).sort_values(
        [
            "team",
            "_selection_minutes",
            "_selection_actions",
            "_selection_player_id",
            "player_name",
        ],
        ascending=[True, False, False, True, True],
        kind="mergesort",
    )
    main_indices = selection.groupby("team", sort=False).head(1).index
    goalkeepers["is_main_goalkeeper"] = goalkeepers.index.isin(main_indices)
    scored = goalkeepers.loc[main_indices].copy()

    raw = pd.Series(0.0, index=scored.index)
    available_weight = pd.Series(0.0, index=scored.index)
    for metric, weight in config.goalkeeper_weights.items():
        values = _numeric(scored, metric)
        percentile = values.rank(method="average", pct=True)
        available = values.notna()
        raw = raw.add(percentile.fillna(0.0) * weight, fill_value=0.0)
        available_weight = available_weight.add(
            available.astype(float) * weight,
            fill_value=0.0,
        )
    raw = raw / available_weight.replace(0.0, np.nan)
    raw = raw.fillna(0.5)
    coverage = available_weight.clip(0.0, 1.0)
    minutes = _numeric(scored, "minutes").fillna(0.0).clip(lower=0.0)
    reliability = coverage * minutes / (
        minutes + config.reliability_minutes
    )
    cohort_prior = float(raw.mean())
    shrunk = reliability * raw + (1.0 - reliability) * cohort_prior

    scored["gk_raw_rating_v2"] = raw
    scored["gk_rating_reliability_v2"] = reliability
    scored["gk_rating_v2"] = _robust_unit_scale(shrunk)
    scored["gk_rank_v2"] = (
        scored["gk_rating_v2"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    for column in (
        "gk_raw_rating_v2",
        "gk_rating_reliability_v2",
        "gk_rating_v2",
    ):
        goalkeepers[column] = np.nan
        goalkeepers.loc[scored.index, column] = scored[column]
    goalkeepers["gk_rank_v2"] = pd.Series(
        pd.NA,
        index=goalkeepers.index,
        dtype="Int64",
    )
    goalkeepers.loc[scored.index, "gk_rank_v2"] = scored["gk_rank_v2"]
    goalkeepers["GKRankingStatus"] = np.where(
        goalkeepers["is_main_goalkeeper"],
        "Ranked (team main goalkeeper)",
        "Unranked (backup goalkeeper)",
    )
    for column in (
        "global_rank_v2",
        "position_rank_v2",
        "role_rank_v2",
        "team_rank_v2",
    ):
        goalkeepers[column] = pd.Series(
            pd.NA,
            index=goalkeepers.index,
            dtype="Int64",
        )
    goalkeepers["final_player_rating_v2"] = np.nan
    goalkeepers["rating_reliability_v2"] = np.nan
    goalkeepers["raw_player_rating_v2"] = np.nan
    goalkeepers["goal_role_boost_v2"] = 0.0
    for component in (
        "finishing",
        "creation",
        "progression",
        "possession",
        "defending",
        "off_ball",
        "tournament_impact",
    ):
        goalkeepers[f"{component}_component_v2"] = np.nan
    return goalkeepers


def calculate_tournament_rankings_v2(
    players: pd.DataFrame,
    *,
    config: TournamentRankingConfig | None = None,
) -> pd.DataFrame:
    """Add Qatar 2022 position, rating, and ranking fields."""

    required = {
        "team",
        "position_group",
        "functional_role",
        "minutes",
    }
    missing = required.difference(players.columns)
    if missing:
        raise ValueError(f"Tournament ranking inputs missing: {sorted(missing)}")
    settings = config or TournamentRankingConfig()
    prepared = players.copy()
    prepared["tournament"] = "2022_World_Cup"
    prepared["minutes_played"] = _numeric(prepared, "minutes")
    prepared["position_group_360"] = infer_position_group_360(prepared)
    prepared = resolve_functional_roles(prepared)

    goalkeepers = prepared["position_group_360"].eq("GK")
    outfield = _calculate_outfield_v2(
        prepared.loc[~goalkeepers].copy(),
        settings,
    )
    keepers = _calculate_goalkeepers_v2(
        prepared.loc[goalkeepers].copy(),
        settings,
    )
    combined = pd.concat([outfield, keepers], axis=0, sort=False)
    return combined.loc[prepared.index].copy()


def _find_player(
    rankings: pd.DataFrame,
    pattern: str,
) -> pd.Series | None:
    names = rankings.get(
        "player_name",
        rankings.get("player", pd.Series("", index=rankings.index)),
    )
    match = rankings.loc[
        names.astype(str).str.contains(pattern, case=False, na=False)
    ]
    return None if match.empty else match.iloc[0]


def role_consistency_violations(rankings: pd.DataFrame) -> list[dict[str, Any]]:
    """Return remaining hard contradictions after role repair."""

    forbidden = {
        "GK": r"forward|winger|midfielder|centre-back|fullback",
        "CB": r"target forward|penalty-box|winger",
        "FB": r"target forward|penalty-box|goalkeeper",
        "DM": r"target forward|penalty-box|winger|sweeper cb",
        "CM": r"target forward|penalty-box|goalkeeper",
        "AM": r"holding anchor|goalkeeper|sweeper cb",
        "FW": r"holding anchor|goalkeeper|sweeper cb",
    }
    violations: list[dict[str, Any]] = []
    for group, pattern in forbidden.items():
        rows = rankings.loc[
            rankings["position_group_360"].eq(group)
            & rankings["functional_role"].astype(str).str.contains(
                pattern,
                case=False,
                regex=True,
                na=False,
            )
        ]
        for _, row in rows.iterrows():
            violations.append(
                {
                    "player_name": row.get("player_name", row.get("player")),
                    "position_group_360": group,
                    "functional_role": row["functional_role"],
                }
            )
    return violations


def tournament_ranking_audit(
    rankings: pd.DataFrame,
    *,
    strict: bool = True,
) -> dict[str, Any]:
    """Run post-score eyes tests without influencing any score."""

    outfield = rankings.loc[
        rankings["position_group_360"].ne("GK")
    ].copy()
    all_keepers = rankings.loc[
        rankings["position_group_360"].eq("GK")
    ].copy()
    keepers = all_keepers.loc[all_keepers["gk_rank_v2"].notna()].copy()
    kane = _find_player(outfield, r"\bHarry Kane\b")
    lewandowski = _find_player(outfield, r"\bRobert Lewandowski\b")
    messi = _find_player(outfield, r"\bMessi\b")
    mbappe = _find_player(outfield, r"\bMbapp")
    martinez = _find_player(keepers, r"Emiliano Mart")
    bounou = _find_player(keepers, r"\bBounou\b")
    courtois = _find_player(keepers, r"\bCourtois\b")

    checks = {
        "ranking_input_scope_2022_world_cup_only": bool(
            "tournament" in rankings
            and rankings["tournament"].eq("2022_World_Cup").all()
        ),
        "one_ranked_main_goalkeeper_per_team": bool(
            not keepers.empty
            and keepers["team"].is_unique
            and set(keepers["team"]) == set(rankings["team"])
            and keepers["is_main_goalkeeper"].fillna(False).all()
        ),
        "backup_goalkeepers_are_unranked": bool(
            all_keepers.loc[
                ~all_keepers["is_main_goalkeeper"].fillna(False).astype(bool)
            ]["gk_rank_v2"].isna().all()
        ),
        "harry_kane_team_rank_1_to_2": bool(
            kane is not None and 1 <= int(kane["team_rank_v2"]) <= 2
        ),
        "robert_lewandowski_team_rank_1_to_2": bool(
            lewandowski is not None
            and 1 <= int(lewandowski["team_rank_v2"]) <= 2
        ),
        "harry_kane_global_top_10": bool(
            kane is not None and int(kane["global_rank_v2"]) <= 10
        ),
        "robert_lewandowski_global_top_20": bool(
            lewandowski is not None
            and int(lewandowski["global_rank_v2"]) <= 20
        ),
        "messi_top_20": bool(
            messi is not None and int(messi["global_rank_v2"]) <= 20
        ),
        "mbappe_top_20": bool(
            mbappe is not None and int(mbappe["global_rank_v2"]) <= 20
        ),
        "bounou_top_8_goalkeeper": bool(
            bounou is not None and int(bounou["gk_rank_v2"]) <= 8
        ),
        "courtois_top_8_goalkeeper": bool(
            courtois is not None and int(courtois["gk_rank_v2"]) <= 8
        ),
        "martinez_top_10_goalkeeper": bool(
            martinez is not None and int(martinez["gk_rank_v2"]) <= 10
        ),
    }
    top_20_names = outfield.loc[
        pd.to_numeric(outfield["global_rank_v2"], errors="coerce").le(20),
        "player_name",
    ].astype(str)
    standout_patterns = {
        "Messi": r"\bMessi\b",
        "Mbappé": r"\bMbapp",
        "Kane": r"\bHarry Kane\b",
        "Lewandowski": r"\bLewandowski\b",
        "Modrić": r"\bModri",
        "Griezmann": r"\bGriezmann\b",
        "Álvarez": r"\bJulián Álvarez\b",
        "Bruno Fernandes": r"\bBruno Miguel Borges Fernandes\b",
        "Neymar": r"\bNeymar\b",
        "Giroud": r"\bOlivier Giroud\b",
        "Richarlison": r"\bRicharlison\b",
        "Hakimi": r"\bAchraf Hakimi\b",
    }
    present_standouts = {
        label
        for label, pattern in standout_patterns.items()
        if outfield["player_name"].astype(str).str.contains(
            pattern,
            case=False,
            regex=True,
            na=False,
        ).any()
    }
    top_20_standouts = {
        label
        for label, pattern in standout_patterns.items()
        if top_20_names.str.contains(
            pattern,
            case=False,
            regex=True,
            na=False,
        ).any()
    }
    required_standout_count = min(8, len(present_standouts))
    checks["credible_top_20_standout_coverage"] = (
        len(top_20_standouts) >= required_standout_count
    )
    contradictions = role_consistency_violations(rankings)
    checks["no_role_position_contradictions"] = not contradictions

    high_goal_forwards = outfield.loc[
        outfield["position_group_360"].eq("FW")
        & (
            _numeric(outfield, "goals").ge(2)
            | (
                _numeric(outfield, "minutes").ge(180)
                & _numeric(outfield, "xg_sum").ge(
                _numeric(outfield, "xg_sum").quantile(0.90)
                )
            )
        )
    ]
    striker_fairness_failures: list[dict[str, Any]] = []
    for _, striker in high_goal_forwards.iterrows():
        mid_tier_teammates = outfield.loc[
            outfield["team"].eq(striker["team"])
            & outfield["position_group_360"].isin(["CB", "FB", "DM", "CM"])
            & _numeric(outfield, "raw_player_rating_v2").lt(0.55)
            & pd.to_numeric(
                outfield["team_rank_v2"],
                errors="coerce",
            ).lt(float(striker["team_rank_v2"]))
        ]
        if not mid_tier_teammates.empty:
            striker_fairness_failures.append(
                {
                    "player_name": striker.get(
                        "player_name",
                        striker.get("player"),
                    ),
                    "team": striker["team"],
                    "goals": striker.get("goals"),
                    "xg_sum": striker.get("xg_sum"),
                    "team_rank_v2": int(striker["team_rank_v2"]),
                    "mid_tier_teammates_above": (
                        mid_tier_teammates["player_name"].astype(str).tolist()
                    ),
                }
            )
    checks["no_high_goal_forward_below_mid_tier_teammate"] = (
        not striker_fairness_failures
    )

    audit: dict[str, Any] = {
        "tournament": "2022_World_Cup",
        "evidence_scope": {
            "scoring_inputs": "Qatar 2022 tournament data only",
            "external_rankings_used_in_scoring": False,
            "external_analysis_policy": (
                "If consulted, only analysis specific to the 2022 FIFA "
                "World Cup may be used, and only for post-score audit."
            ),
            "excluded": [
                "club-season performance",
                "career reputation",
                "other tournaments",
                "later performances",
            ],
        },
        "checks": checks,
        "passed": all(checks.values()),
        "role_consistency_violations": contradictions,
        "striker_fairness_failures": striker_fairness_failures,
        "top_20_standout_coverage": {
            "required": required_standout_count,
            "present_in_dataset": sorted(present_standouts),
            "present_in_top_20": sorted(top_20_standouts),
        },
        "top_20_outfield": (
            outfield.sort_values("global_rank_v2")
            .head(20)[
                [
                    "global_rank_v2",
                    "player_name",
                    "team",
                    "position_group_360",
                    "functional_role",
                    "final_player_rating_v2",
                ]
            ]
            .to_dict("records")
        ),
        "top_10_goalkeepers": (
            keepers.sort_values("gk_rank_v2")
            .head(10)[
                [
                    "gk_rank_v2",
                    "player_name",
                    "team",
                    "gk_rating_v2",
                ]
            ]
            .to_dict("records")
        ),
    }
    comparisons = {}
    for key, row in (
        ("harry_kane", kane),
        ("robert_lewandowski", lewandowski),
    ):
        if row is not None:
            comparisons[key] = {
                "player_name": row.get("player_name", row.get("player")),
                "old_global_rank": (
                    None
                    if pd.isna(row.get("global_rank"))
                    else int(row["global_rank"])
                ),
                "new_global_rank": int(row["global_rank_v2"]),
                "old_team_rank": (
                    None
                    if pd.isna(row.get("team_rank"))
                    else int(row["team_rank"])
                ),
                "new_team_rank": int(row["team_rank_v2"]),
            }
    audit["before_after"] = comparisons
    if strict and not audit["passed"]:
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(
            "Tournament ranking eyes tests failed: " + ", ".join(failed)
        )
    return audit


def tournament_ranking_methodology_markdown(
    config: TournamentRankingConfig | None = None,
) -> str:
    """Render the reproducible methodology placed beside ranking outputs."""

    settings = config or TournamentRankingConfig()
    position_rows = [
        "| Group | Finishing | Creation | Progression | Possession | "
        "Defending | Off-ball | Common impact |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group, weights in settings.component_weights.items():
        position_rows.append(
            f"| {group} | {weights['finishing']:.2f} | "
            f"{weights['creation']:.2f} | {weights['progression']:.2f} | "
            f"{weights['possession']:.2f} | {weights['defending']:.2f} | "
            f"{weights['off_ball']:.2f} | "
            f"{weights['tournament_impact']:.2f} |"
        )
    goalkeeper_labels = {
        "goals_prevented_proxy_p90": "Goals prevented per 90",
        "save_rate": "Save rate",
        "high_leverage_save_pct": "High-leverage save rate",
        "penalties_saved": "Penalties saved",
        "penalty_save_rate_shrunk": "Reliability-shrunk penalty save rate",
        "cross_stopping_rate": "Cross stopping",
        "sweeper_actions_p90": "Sweeper actions per 90",
        "distribution_under_pressure": "Distribution under pressure",
        "claims_p90": "Claims per 90",
        "minutes": "Tournament minutes",
    }
    goalkeeper_rows = [
        "| Goalkeeper score part | Source field | Weight |",
        "|---|---|---:|",
        *[
            f"| {goalkeeper_labels.get(metric, metric)} | `{metric}` | "
            f"{weight:.0%} |"
            for metric, weight in settings.goalkeeper_weights.items()
        ],
    ]
    return "\n".join(
        [
            "# Qatar 2022 Ranking Methodology",
            "",
            "This model evaluates players based solely on their performances "
            "at the 2022 FIFA World Cup. Club form, career reputation, and "
            "other competitions are excluded.",
            "",
            "No external ranking is an input to the score. If external "
            "analysis is consulted for an eyes test, it must refer "
            "specifically to the 2022 FIFA World Cup and remains audit-only; "
            "it cannot alter a player’s features or points.",
            "",
            "## Position and role context",
            "",
            "`position_group_360` uses `GK`, `CB`, `FB`, `DM`, `CM`, `AM`, "
            "and `FW`. The source position and functional role are retained "
            "in `functional_role_original`; only hard contradictions are "
            "repaired for reporting. Role labels do not award points by "
            "themselves.",
            "",
            "## Outfield score",
            "",
            "Each component is an average of tournament feature percentiles. "
            "Rate, progression, possession, defense, and off-ball metrics are "
            "normalized within `position_group_360`. Goals, xG, xA, VAEP "
            "volume, and xT volume form a common tournament-impact bridge so "
            "the global ordering is not merely six unrelated positional "
            "leaderboards.",
            "",
            *position_rows,
            "",
            "For goal-centric forward roles, only finishing above the 70th "
            "percentile receives a smooth boost, capped at 0.06. This is a "
            "role-and-output rule and never checks player identity.",
            "",
            "The raw score is shrunk toward its positional mean using "
            f"`minutes / (minutes + {settings.reliability_minutes:.0f})`, "
            "then robustly rescaled to 0–1. `minutes_played` is a documented "
            "alias of the project’s Qatar 2022 `minutes` field.",
            "",
            "## Goalkeepers",
            "",
            "Goalkeepers use a separate, non-comparable scale. Penalty-save "
            "volume is retained because knockout shootouts are meaningful "
            "tournament evidence; shot stopping, high-leverage saves, cross "
            "control, sweeping, distribution, and sample reliability remain "
            "part of the score.",
            "",
            "Only one goalkeeper per team is ranked: the goalkeeper with the "
            "most Qatar 2022 minutes. Ties are resolved by actions, then "
            "player ID and name. Backups remain in the complete dataset with "
            "`is_main_goalkeeper = false`, no goalkeeper score, and no rank.",
            "",
            "Each available goalkeeper input is converted to a percentile "
            "within the 32-main-goalkeeper cohort. Missing-input weights are "
            "renormalized, then the weighted score is shrunk toward the "
            "cohort mean using feature coverage and "
            f"`minutes / (minutes + {settings.reliability_minutes:.0f})` "
            "before the final 0–1 rescale.",
            "",
            *goalkeeper_rows,
            "",
            "## Ranking fields",
            "",
            "- `global_rank_v2`: all eligible outfield players.",
            "- `position_rank_v2`: outfield players within the formal group.",
            "- `role_rank_v2`: outfield players within the coherent role.",
            "- `team_rank_v2`: outfield players within the national team.",
            "- `gk_rank_v2`: the 32 team-main goalkeepers only.",
            "",
            "The 300-minute file filters on Qatar 2022 minutes and preserves "
            "the all-player `global_rank_v2`, allowing direct comparison with "
            "the unfiltered table.",
            "",
        ]
    )
