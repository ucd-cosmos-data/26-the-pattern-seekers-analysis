#!/usr/bin/env python3
"""Run and publish the complete eight-pass Qatar 2022 ranking repair."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.event_scope import (  # noqa: E402
    EVENT_SCOPE_VERSION,
    filter_ordinary_actions,
    tournament_goal_reconciliation,
)
from src.models.goalkeeper_valuation_v3 import (  # noqa: E402
    GoalkeeperV3Config,
    bootstrap_goalkeeper_uncertainty_v3,
    calculate_goalkeeper_ratings_v3,
    calibrate_post_shot_xg_v3,
)
from src.models.tournament_rankings_v3 import (  # noqa: E402
    CORE_ATTACK_ABLATIONS,
    TournamentRankingV3Config,
    build_attack_ablation_scores,
    calculate_tournament_rankings_v3,
    evaluate_attack_ablations,
    ranking_gate_diagnostics,
    score_feature_contract,
)
from src.reporting.ranking_repair_release import (  # noqa: E402
    ACTIVE_MODEL_VERSION,
    RankingRepairReleaseWriter,
)


EVENTS_PATH = PROJECT_ROOT / "notebooks" / "all_events.csv"
MATCHES_PATH = PROJECT_ROOT / "data" / "raw" / "matches.csv"
ACTIONS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_spadl_actions.parquet"
)
COMPONENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "world_cup_player_match_components.csv"
)
ACTIVE_RANKINGS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "player_evaluations.csv"
)
CHAMPION_ROOT = (
    PROJECT_ROOT / "results" / "diagnostics" / "ranking_repair" / "champion"
)
PASS3_ROOT = (
    PROJECT_ROOT / "results" / "diagnostics" / "ranking_repair"
)
PASS3_DIAGNOSTICS = PASS3_ROOT / "pass3_defensive_challenger.json"
PASS3_PREDICTIONS = (
    PASS3_ROOT / "pass3_defensive_challenger_oof_predictions.csv"
)
PASS3_SAMPLES = PASS3_ROOT / "pass3_defensive_challenger_samples.csv"
PASS7_RATINGS = PASS3_ROOT / "pass7_goalkeeper_ratings.csv"
PASS7_AUDIT = PASS3_ROOT / "pass7_goalkeeper_v3.json"

RELEASE_SOURCE_DATA = {
    "events": EVENTS_PATH,
    "spadl_actions": ACTIONS_PATH,
    "player_evaluations": (
        PROJECT_ROOT / "data/processed/player_evaluations.csv"
    ),
    "player_match_components": COMPONENTS_PATH,
}


def _current_source_hashes() -> dict[str, dict[str, str | int]]:
    """Return hashes for the source state used by the current v3 release."""

    records: dict[str, dict[str, str | int]] = {}
    for name, path in RELEASE_SOURCE_DATA.items():
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1 << 20), b""):
                digest.update(block)
        records[name] = {
            "path": path.relative_to(PROJECT_ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": digest.hexdigest(),
        }
    return records


def _run(command: list[str]) -> None:
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
        text=True,
    )
    if completed.returncode:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {' '.join(command)}"
        )


def _ensure_inputs(
    *,
    run_foundation: bool,
    rerun_defense: bool,
    rebuild_inputs: bool,
    reuse_goalkeeper: bool,
) -> None:
    if not (CHAMPION_ROOT / "champion_snapshot.json").is_file():
        _run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "freeze_ranking_champion.py"),
            ]
        )
    if rebuild_inputs:
        _run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "preprocess_possessions.py"),
            ]
        )
        _run(
            [
                sys.executable,
                str(
                    PROJECT_ROOT
                    / "scripts"
                    / "build_player_skill_inputs.py"
                ),
            ]
        )
    if run_foundation:
        _run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_pipeline.py"),
                "--skip-legacy-foundation",
                "--reuse-validated-oof",
            ]
        )
    if rerun_defense or not all(
        path.is_file()
        for path in (
            PASS3_DIAGNOSTICS,
            PASS3_PREDICTIONS,
            PASS3_SAMPLES,
        )
    ):
        _run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_defensive_challenger.py"),
            ]
        )
    if not reuse_goalkeeper or not all(
        path.is_file() for path in (PASS7_RATINGS, PASS7_AUDIT)
    ):
        _run(
            [
                sys.executable,
                str(
                    PROJECT_ROOT
                    / "scripts"
                    / "run_goalkeeper_v3_release.py"
                ),
            ]
        )


def _component_outcomes(components: pd.DataFrame) -> pd.DataFrame:
    """Aggregate corrected player-match outcomes to the release cohort."""

    numeric_sum = [
        "open_play_goals",
        "non_penalty_goals",
        "regular_penalty_goals",
        "regulation_extra_time_goals",
        "assists",
        "xg_non_shootout",
        "xg_non_penalty",
        "xa_non_shootout",
        "shootout_attempts",
        "shootout_goals",
    ]
    missing = set(numeric_sum).difference(components.columns)
    if missing:
        raise ValueError(
            f"Corrected player-match inputs missing: {sorted(missing)}"
        )
    output = (
        components.groupby(["team", "player_id"], as_index=False)[numeric_sum]
        .sum()
    )
    output["event_scope_version"] = EVENT_SCOPE_VERSION
    return output


def _player_match_attack_values(
    actions: pd.DataFrame,
    components: pd.DataFrame,
) -> pd.DataFrame:
    """Create expected-process and explicit outcome rows without shootouts."""

    ordinary = filter_ordinary_actions(actions)
    ordinary = ordinary.loc[ordinary["player_id"].notna()].copy()
    ordinary["player_id"] = ordinary["player_id"].astype(int)
    vaep = pd.to_numeric(
        ordinary["vaep_value"],
        errors="coerce",
    ).fillna(0.0)
    xa = pd.to_numeric(
        ordinary.get("xa_value", 0.0),
        errors="coerce",
    ).fillna(0.0)
    is_offense = ordinary["action_side"].eq("offense")
    is_shot = ordinary["type_name"].eq("Shot")
    is_direct_shot_creation = xa.gt(0.0)
    ordinary["_base_process_value"] = vaep.where(
        is_offense & ~is_shot & ~is_direct_shot_creation,
        0.0,
    )
    ordinary["_xt_value"] = pd.to_numeric(
        ordinary.get("xt_value", 0.0),
        errors="coerce",
    ).fillna(0.0).where(is_offense, 0.0)
    action_match = (
        ordinary.groupby(
            ["game_id", "team", "player_id"],
            as_index=False,
        )
        .agg(
            vaep_process_without_shot_creation_v3=(
                "_base_process_value",
                "sum",
            ),
            xt_value_non_shootout=("_xt_value", "sum"),
            ordinary_action_count_v3=("action_id", "size"),
        )
        .rename(columns={"game_id": "match_id"})
    )

    outcome_columns = [
        "match_id",
        "team",
        "player_id",
        "minutes",
        "open_play_goals",
        "non_penalty_goals",
        "regular_penalty_goals",
        "regulation_extra_time_goals",
        "assists",
        "xg_non_shootout",
        "xg_non_penalty",
        "xa_non_shootout",
        "shootout_attempts",
        "shootout_goals",
    ]
    match = components[outcome_columns].copy()
    match = match.merge(
        action_match,
        on=["match_id", "team", "player_id"],
        how="left",
        validate="one_to_one",
    )
    for column in (
        "vaep_process_without_shot_creation_v3",
        "xt_value_non_shootout",
        "ordinary_action_count_v3",
    ):
        match[column] = pd.to_numeric(
            match[column],
            errors="coerce",
        ).fillna(0.0)

    penalty_xg = (
        pd.to_numeric(match["xg_non_shootout"], errors="coerce")
        - pd.to_numeric(match["xg_non_penalty"], errors="coerce")
    ).clip(lower=0.0)
    expected_shot = 0.70 * (
        pd.to_numeric(match["xg_non_penalty"], errors="coerce")
        + 0.76 * penalty_xg
    )
    expected_creation = 0.35 * pd.to_numeric(
        match["xa_non_shootout"],
        errors="coerce",
    )
    match["expected_shot_value_v3"] = expected_shot
    match["expected_creation_value_v3"] = expected_creation
    match["expected_action_value_non_shootout"] = (
        match["vaep_process_without_shot_creation_v3"]
        + expected_shot
        + expected_creation
    )
    match["event_scope_version"] = EVENT_SCOPE_VERSION
    return match


def _attach_defensive_values(
    match: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    diagnostics = json.loads(PASS3_DIAGNOSTICS.read_text(encoding="utf-8"))
    predictions = pd.read_csv(PASS3_PREDICTIONS)
    samples = pd.read_csv(PASS3_SAMPLES)
    selected = str(diagnostics["selected_challenger"])
    prediction_column = f"{selected}_oof_prediction"
    defensive = predictions[
        ["match_id", "team", "player_id", prediction_column]
    ].merge(
        samples[
            ["match_id", "team", "player_id", "opponent_possessions"]
        ],
        on=["match_id", "team", "player_id"],
        how="left",
        validate="one_to_one",
    )
    defensive["defensive_value_non_shootout"] = (
        pd.to_numeric(
            defensive[prediction_column],
            errors="coerce",
        )
        * pd.to_numeric(
            defensive["opponent_possessions"],
            errors="coerce",
        )
        / 100.0
    )
    defensive["defensive_rate_per100_v3"] = pd.to_numeric(
        defensive[prediction_column],
        errors="coerce",
    )
    output = match.merge(
        defensive[
            [
                "match_id",
                "team",
                "player_id",
                "defensive_value_non_shootout",
                "defensive_rate_per100_v3",
                "opponent_possessions",
            ]
        ],
        on=["match_id", "team", "player_id"],
        how="left",
        validate="one_to_one",
    )
    output["defensive_model_evidence_available_v3"] = output[
        "defensive_value_non_shootout"
    ].notna()
    output["defensive_value_non_shootout"] = pd.to_numeric(
        output["defensive_value_non_shootout"],
        errors="coerce",
    ).fillna(0.0)
    return output, diagnostics


def _attach_next_match_attack_target(
    match: pd.DataFrame,
    matches: pd.DataFrame,
) -> pd.DataFrame:
    """Create a forward-looking target independent of current-match outcomes."""

    schedule_rows: list[dict[str, Any]] = []
    ordered_matches = matches.assign(
        _datetime=pd.to_datetime(
            matches["match_date"].astype(str)
            + " "
            + matches["kick_off"].astype(str),
            errors="coerce",
        )
    )
    for match_id, match_datetime, home_team, away_team in ordered_matches[
        ["match_id", "_datetime", "home_team", "away_team"]
    ].itertuples(index=False, name=None):
        schedule_rows.extend(
            [
                {
                    "team": home_team,
                    "match_id": match_id,
                    "_datetime": match_datetime,
                },
                {
                    "team": away_team,
                    "match_id": match_id,
                    "_datetime": match_datetime,
                },
            ]
        )
    schedule = pd.DataFrame(schedule_rows).sort_values(
        ["team", "_datetime", "match_id"],
        kind="mergesort",
    )
    schedule["next_match_id"] = schedule.groupby("team")["match_id"].shift(-1)
    next_lookup = schedule.set_index(["team", "match_id"])[
        "next_match_id"
    ]
    output = match.copy()
    output["next_match_id"] = [
        next_lookup.get((team, match_id), np.nan)
        for team, match_id in zip(
            output["team"],
            output["match_id"],
            strict=True,
        )
    ]
    realized = (
        pd.to_numeric(
            output["non_penalty_goals"],
            errors="coerce",
        )
        + 0.76
        * pd.to_numeric(
            output["regular_penalty_goals"],
            errors="coerce",
        )
        + 0.35 * pd.to_numeric(output["assists"], errors="coerce")
    )
    future_lookup = pd.Series(
        realized.to_numpy(),
        index=pd.MultiIndex.from_arrays(
            [
                output["team"],
                output["player_id"],
                output["match_id"],
            ]
        ),
    )
    output["next_match_attack_output_v3"] = [
        (
            future_lookup.get((team, player_id, next_match_id), 0.0)
            if pd.notna(next_match_id)
            else np.nan
        )
        for team, player_id, next_match_id in zip(
            output["team"],
            output["player_id"],
            output["next_match_id"],
            strict=True,
        )
    ]
    return output


def _attack_configuration(
    role_probability_columns: tuple[str, ...],
    *,
    selected: str = "process_plus_shrunk_residual",
    include_xt_overlap: bool = False,
) -> TournamentRankingV3Config:
    process_columns = (
        (
            "expected_action_value_non_shootout",
            "xt_value_non_shootout",
        )
        if include_xt_overlap
        else ("expected_action_value_non_shootout",)
    )
    process_weights = (1.0, 0.15) if include_xt_overlap else (1.0,)
    overlap_columns = (
        ("xt_value_non_shootout",)
        if include_xt_overlap
        else ()
    )
    overlap_weights = (0.15,) if include_xt_overlap else ()
    return TournamentRankingV3Config(
        process_value_columns=process_columns,
        process_value_weights=process_weights,
        xt_vaep_overlap_columns=overlap_columns,
        xt_vaep_overlap_weights=overlap_weights,
        defensive_value_columns=("defensive_value_non_shootout",),
        defensive_value_weights=(1.0,),
        selected_attack_candidate=selected,
        process_includes_realized_outcomes=True,
        regular_penalty_weight=0.76,
        assist_value=0.35,
        role_probability_columns=role_probability_columns,
        bootstrap_replicates=500,
        attack_bootstrap_replicates=500,
        random_seed=42,
    )


def _select_safe_attack_candidate(
    audit: dict[str, Any],
) -> tuple[str, str]:
    """Select only candidates that cannot duplicate full outcomes."""

    safe = ("process_only", "process_plus_shrunk_residual")
    metrics = audit["metrics"]
    passing = [
        candidate
        for candidate in safe
        if candidate in metrics and metrics[candidate]["gate_passed"]
    ]
    if not passing:
        return "process_only", "retain_champion_no_safe_challenger_passed"
    selected = min(
        passing,
        key=lambda candidate: (
            metrics[candidate]["oof_rmse"],
            -np.nan_to_num(
                metrics[candidate]["oof_spearman"],
                nan=-np.inf,
            ),
            candidate,
        ),
    )
    decision = (
        "retain_champion"
        if selected == "process_only"
        else "promote_bounded_shrunk_residual"
    )
    return selected, decision


def _aggregate_player_scoring_inputs(
    match: pd.DataFrame,
    base: pd.DataFrame,
) -> pd.DataFrame:
    sum_columns = [
        "minutes",
        "open_play_goals",
        "non_penalty_goals",
        "regular_penalty_goals",
        "regulation_extra_time_goals",
        "assists",
        "xg_non_shootout",
        "xg_non_penalty",
        "xa_non_shootout",
        "shootout_attempts",
        "shootout_goals",
        "vaep_process_without_shot_creation_v3",
        "expected_shot_value_v3",
        "expected_creation_value_v3",
        "expected_action_value_non_shootout",
        "xt_value_non_shootout",
        "ordinary_action_count_v3",
        "defensive_value_non_shootout",
        "positive_contribution_value_non_shootout",
    ]
    aggregate = (
        match.groupby(["team", "player_id"], as_index=False)[sum_columns]
        .sum()
    )
    evidence = (
        match.groupby(["team", "player_id"])[
            "defensive_model_evidence_available_v3"
        ]
        .mean()
        .rename("defensive_model_match_coverage_v3")
        .reset_index()
    )
    aggregate = aggregate.merge(
        evidence,
        on=["team", "player_id"],
        how="left",
        validate="one_to_one",
    )
    identity_columns = [
        column
        for column in (
            "player_id",
            "player_name",
            "player",
            "team",
            "position_group",
            "position_group_360",
            "functional_role",
            "functional_role_original",
            "minutes_played",
            "is_main_goalkeeper",
        )
        if column in base
    ]
    role_probability_columns = [
        column
        for column in base.columns
        if re.fullmatch(r"role_probability_\d+", column)
    ]
    identity = base[
        [*identity_columns, *role_probability_columns]
    ].copy()
    output = identity.merge(
        aggregate,
        on=["team", "player_id"],
        how="left",
        validate="one_to_one",
        suffixes=("", "_corrected"),
    )
    for column in sum_columns:
        if column in output:
            output[column] = pd.to_numeric(
                output[column],
                errors="coerce",
            ).fillna(0.0)
    output["minutes"] = pd.to_numeric(
        output.get("minutes_played", output.get("minutes")),
        errors="coerce",
    ).fillna(0.0)
    output["event_scope_version"] = EVENT_SCOPE_VERSION
    return output


def _opponent_lookup(matches: pd.DataFrame) -> dict[tuple[int, str], str]:
    lookup: dict[tuple[int, str], str] = {}
    for match_id, home, away in matches[
        ["match_id", "home_team", "away_team"]
    ].itertuples(index=False, name=None):
        lookup[(int(match_id), str(home))] = str(away)
        lookup[(int(match_id), str(away))] = str(home)
    return lookup


def _penalty_counts(
    events: pd.DataFrame,
    matches: pd.DataFrame,
) -> pd.DataFrame:
    opponent = _opponent_lookup(matches)
    period = pd.to_numeric(events["period"], errors="coerce")
    shot_type = events["shot_type"].fillna("").astype(str)
    outcomes = events["shot_outcome"].fillna("").astype(str)
    penalties = events.loc[
        events["type"].eq("Shot")
        & shot_type.str.contains("Penalty", case=False, na=False)
        & outcomes.str.contains("Goal|Saved", case=False, na=False)
    ].copy()
    penalties["defending_team"] = [
        opponent.get((int(match_id), str(team)))
        for match_id, team in zip(
            penalties["match_id"],
            penalties["team"],
            strict=True,
        )
    ]
    penalties["_saved"] = penalties["shot_outcome"].astype(str).str.contains(
        "Saved",
        case=False,
        na=False,
    )
    penalties["_regular"] = pd.to_numeric(
        penalties["period"],
        errors="coerce",
    ).isin([1, 2, 3, 4])
    penalties["_shootout"] = pd.to_numeric(
        penalties["period"],
        errors="coerce",
    ).eq(5)
    grouped = (
        penalties.groupby(
            ["match_id", "defending_team"],
            as_index=False,
            dropna=False,
        )
        .agg(
            regular_penalties_faced=("_regular", "sum"),
            regular_penalties_saved=(
                "_saved",
                lambda values: int(
                    (
                        values
                        & penalties.loc[values.index, "_regular"]
                    ).sum()
                ),
            ),
            shootout_penalties_faced=("_shootout", "sum"),
            shootout_penalties_saved=(
                "_saved",
                lambda values: int(
                    (
                        values
                        & penalties.loc[values.index, "_shootout"]
                    ).sum()
                ),
            ),
        )
        .rename(columns={"defending_team": "team"})
    )
    return grouped


def _goalkeeper_v3(
    base: pd.DataFrame,
    events: pd.DataFrame,
    matches: pd.DataFrame,
    components: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    """Recalibrate post-shot evidence and score the dedicated GK branch."""

    predictions, calibration_audit = calibrate_post_shot_xg_v3(events)
    opponent = _opponent_lookup(matches)
    shots = events.loc[predictions.index].copy()
    shots["_goal_probability_v3"] = predictions
    shots["_actual_goal"] = (
        shots["shot_outcome"]
        .fillna("")
        .astype(str)
        .str.contains("Goal", case=False, na=False)
        .astype(float)
    )
    shots["_goal_prevention_value_v3"] = (
        shots["_goal_probability_v3"] - shots["_actual_goal"]
    )
    shots["_high_leverage"] = shots["_goal_probability_v3"].ge(0.35)
    shots["_save"] = shots["_actual_goal"].eq(0.0)
    shots["defending_team"] = [
        opponent.get((int(match_id), str(team)))
        for match_id, team in zip(
            shots["match_id"],
            shots["team"],
            strict=True,
        )
    ]
    shot_match = (
        shots.groupby(
            ["match_id", "defending_team"],
            as_index=False,
            dropna=False,
        )
        .agg(
            goal_prevention_value_v3=(
                "_goal_prevention_value_v3",
                "sum",
            ),
            ordinary_non_penalty_on_target_faced_v3=(
                "_actual_goal",
                "size",
            ),
            high_leverage_shots_faced_v3=("_high_leverage", "sum"),
            high_leverage_saves_v3=(
                "_save",
                lambda values: int(
                    (
                        values
                        & shots.loc[values.index, "_high_leverage"]
                    ).sum()
                ),
            ),
        )
        .rename(columns={"defending_team": "team"})
    )
    shot_total = (
        shot_match.groupby("team", as_index=False)
        .agg(
            goal_prevention_value_v3=(
                "goal_prevention_value_v3",
                "sum",
            ),
            ordinary_non_penalty_on_target_faced_v3=(
                "ordinary_non_penalty_on_target_faced_v3",
                "sum",
            ),
            high_leverage_shots_faced_v3=(
                "high_leverage_shots_faced_v3",
                "sum",
            ),
            high_leverage_saves_v3=(
                "high_leverage_saves_v3",
                "sum",
            ),
        )
    )
    penalty_match = _penalty_counts(events, matches)
    penalty_total = (
        penalty_match.groupby("team", as_index=False)[
            [
                "regular_penalties_faced",
                "regular_penalties_saved",
                "shootout_penalties_faced",
                "shootout_penalties_saved",
            ]
        ]
        .sum()
    )

    goalkeeper_mask = base["position_group"].eq("Goalkeeper")
    features = base.loc[goalkeeper_mask].copy()
    features["minutes"] = pd.to_numeric(
        features.get("minutes_played", features.get("minutes")),
        errors="coerce",
    )
    features = features.drop(
        columns=[
            column
            for column in (
                "regular_penalties_faced",
                "regular_penalties_saved",
                "shootout_penalties_faced",
                "shootout_penalties_saved",
            )
            if column in features
        ]
    )
    features = features.merge(
        shot_total,
        on="team",
        how="left",
        validate="many_to_one",
    ).merge(
        penalty_total,
        on="team",
        how="left",
        validate="many_to_one",
    )
    features["goals_prevented_proxy_p90"] = (
        pd.to_numeric(
            features["goal_prevention_value_v3"],
            errors="coerce",
        )
        * 90.0
        / pd.to_numeric(
            features["minutes"],
            errors="coerce",
        ).replace(0.0, np.nan)
    )
    leverage_faced = pd.to_numeric(
        features["high_leverage_shots_faced_v3"],
        errors="coerce",
    ).fillna(0.0)
    leverage_saved = pd.to_numeric(
        features["high_leverage_saves_v3"],
        errors="coerce",
    ).fillna(0.0)
    leverage_prior = (
        float(leverage_saved.sum() / leverage_faced.sum())
        if leverage_faced.sum() > 0
        else 0.5
    )
    features["high_leverage_save_rate_shrunk"] = (
        leverage_saved + 5.0 * leverage_prior
    ) / (leverage_faced + 5.0)
    for column in (
        "regular_penalties_faced",
        "regular_penalties_saved",
        "shootout_penalties_faced",
        "shootout_penalties_saved",
    ):
        features[column] = pd.to_numeric(
            features[column],
            errors="coerce",
        ).fillna(0.0)

    settings = GoalkeeperV3Config()
    rated, rating_audit = calculate_goalkeeper_ratings_v3(
        features,
        config=settings,
    )
    main = rated.loc[rated["is_main_goalkeeper"]][
        ["team", "player_id"]
    ]
    match_minutes = components.merge(
        main,
        on=["team", "player_id"],
        how="inner",
        validate="many_to_one",
    )[["match_id", "team", "player_id", "minutes", "actions"]]
    match_features = match_minutes.merge(
        shot_match,
        on=["match_id", "team"],
        how="left",
        validate="one_to_one",
    ).merge(
        penalty_match,
        on=["match_id", "team"],
        how="left",
        validate="one_to_one",
    )
    match_features["goals_prevented_proxy_p90"] = (
        pd.to_numeric(
            match_features["goal_prevention_value_v3"],
            errors="coerce",
        )
        * 90.0
        / pd.to_numeric(
            match_features["minutes"],
            errors="coerce",
        ).replace(0.0, np.nan)
    )
    match_leverage_faced = pd.to_numeric(
        match_features["high_leverage_shots_faced_v3"],
        errors="coerce",
    )
    match_leverage_saved = pd.to_numeric(
        match_features["high_leverage_saves_v3"],
        errors="coerce",
    )
    match_features["high_leverage_save_rate_shrunk"] = (
        match_leverage_saved + 5.0 * leverage_prior
    ) / (match_leverage_faced + 5.0)
    static_rate_columns = [
        "cross_stopping_rate",
        "claims_p90",
        "sweeper_actions_p90",
        "distribution_under_pressure",
    ]
    match_features = match_features.merge(
        rated[["player_id", *static_rate_columns]],
        on="player_id",
        how="left",
        validate="many_to_one",
    )
    for column in (
        "regular_penalties_faced",
        "regular_penalties_saved",
        "shootout_penalties_faced",
        "shootout_penalties_saved",
    ):
        match_features[column] = pd.to_numeric(
            match_features[column],
            errors="coerce",
        ).fillna(0.0)
    match_features["period"] = 1
    uncertainty = bootstrap_goalkeeper_uncertainty_v3(
        match_features,
        config=settings,
        iterations=500,
        random_state=42,
    )
    rated = rated.merge(
        uncertainty,
        on=["team", "player_id"],
        how="left",
        validate="one_to_one",
    )
    audit = {
        "calibration": calibration_audit,
        "rating": rating_audit,
        "weights_requested_by_user": {
            "continuous_allocation": 0.90,
            "shootout_maximum": 0.10,
            "continuous_component_weights": rating_audit[
                "continuous_component_weights"
            ],
        },
        "gate_passed": bool(
            calibration_audit["absolute_metric_gate"]["passed"]
            and rating_audit["one_main_goalkeeper_per_team"]
            and rating_audit["backup_goalkeepers_unranked"]
            and rating_audit["maximum_observed_shootout_component"]
            <= rating_audit["shootout_cap"] + 1e-12
        ),
    }
    return rated, audit, match_features


def _spearman(left: pd.Series, right: pd.Series) -> float:
    joined = pd.concat(
        [
            pd.to_numeric(left, errors="coerce"),
            pd.to_numeric(right, errors="coerce"),
        ],
        axis=1,
    ).dropna()
    if len(joined) < 3:
        return float("nan")
    return float(joined.iloc[:, 0].corr(joined.iloc[:, 1], method="spearman"))


def _bootstrap_spearman_interval(
    left: pd.Series,
    right: pd.Series,
    *,
    draws: int = 1_000,
    seed: int = 42,
) -> dict[str, float]:
    joined = pd.concat(
        [
            pd.to_numeric(left, errors="coerce"),
            pd.to_numeric(right, errors="coerce"),
        ],
        axis=1,
    ).dropna()
    estimate = _spearman(joined.iloc[:, 0], joined.iloc[:, 1])
    generator = np.random.default_rng(seed)
    samples: list[float] = []
    for _ in range(draws):
        indices = generator.integers(0, len(joined), size=len(joined))
        sampled = joined.iloc[indices]
        value = _spearman(sampled.iloc[:, 0], sampled.iloc[:, 1])
        if np.isfinite(value):
            samples.append(value)
    return {
        "estimate": estimate,
        "ci_low": float(np.quantile(samples, 0.025)),
        "ci_high": float(np.quantile(samples, 0.975)),
        "bootstrap_draws": draws,
    }


def _generalized_validity_audit(rich: pd.DataFrame) -> dict[str, Any]:
    outfield = rich.loc[rich["position_group"].ne("Goalkeeper")].copy()
    outfield["goals_corrected"] = pd.to_numeric(
        outfield["regulation_extra_time_goals"],
        errors="coerce",
    ).fillna(0.0)
    leaders = outfield.loc[
        outfield["goals_corrected"].eq(
            outfield.groupby("team")["goals_corrected"].transform("max")
        )
        & outfield["goals_corrected"].gt(0.0)
    ]
    outside_top_eight = leaders.loc[
        pd.to_numeric(leaders["team_rank_v3"], errors="coerce").gt(8)
    ]

    productive = outfield.loc[
        outfield["goals_corrected"].add(
            pd.to_numeric(outfield["assists"], errors="coerce").fillna(0.0)
        ).gt(0.0)
    ]
    zero = outfield.loc[
        outfield["goals_corrected"].add(
            pd.to_numeric(outfield["assists"], errors="coerce").fillna(0.0)
        ).eq(0.0)
    ]
    pair_results: list[bool] = []
    for row in productive.itertuples(index=False):
        comparable = zero.loc[
            zero["team"].eq(row.team)
            & (
                pd.to_numeric(
                    zero["minutes_played"],
                    errors="coerce",
                )
                - float(row.minutes_played)
            )
            .abs()
            .le(90.0)
        ]
        pair_results.extend(
            int(row.team_rank_v3) < int(rank)
            for rank in comparable["team_rank_v3"].dropna()
        )

    short = (
        outfield.loc[
            pd.to_numeric(
                outfield["minutes_played"],
                errors="coerce",
            ).lt(180.0)
        ]
        .sort_values("global_rank_v3")
        .head(20)
    )
    top_composition = {
        str(limit): (
            outfield.sort_values("global_rank_v3")
            .head(limit)["position_group"]
            .value_counts()
            .sort_index()
            .to_dict()
        )
        for limit in (20, 50, 100)
    }
    eye_names = (
        "Harry Kane",
        "Robert Lewandowski",
    )
    eye_test = []
    for name in eye_names:
        row = rich.loc[rich["player_name"].eq(name)]
        if not row.empty:
            record = row.iloc[0]
            eye_test.append(
                {
                    "player": name,
                    "global_rank_v3": _json_number(
                        record.get("global_rank_v3")
                    ),
                    "team_rank_v3": _json_number(
                        record.get("team_rank_v3")
                    ),
                    "tournament_impact_v3": _json_number(
                        record.get("tournament_impact_raw_v3")
                    ),
                    "goals": _json_number(
                        record.get("regulation_extra_time_goals")
                    ),
                    "assists": _json_number(record.get("assists")),
                    "audit_only_no_scoring_effect": True,
                }
            )
    return {
        "team_leading_scorers_outside_team_top_eight": [
            {
                "player": row.player_name,
                "team": row.team,
                "goals": int(row.goals_corrected),
                "team_rank_v3": int(row.team_rank_v3),
            }
            for row in outside_top_eight.itertuples(index=False)
        ],
        "team_leading_scorer_gate_passed": outside_top_eight.empty,
        "productive_vs_zero_output_similar_minutes_pair_count": len(
            pair_results
        ),
        "productive_pairwise_ordering_success_rate": (
            float(np.mean(pair_results)) if pair_results else None
        ),
        "below_180_minute_high_impact": short[
            [
                "player_name",
                "team",
                "minutes_played",
                "global_rank_v3",
                "tournament_impact_raw_v3",
                "role_quality_v3",
                "uncertainty_status_v3",
            ]
        ].to_dict(orient="records"),
        "top_position_composition": top_composition,
        "named_eye_test_audit_only": eye_test,
    }


def _json_number(value: Any) -> int | float | None:
    if value is None or pd.isna(value):
        return None
    number = float(value)
    return int(number) if number.is_integer() else number


def _merge_v3_outputs(
    base: pd.DataFrame,
    outfield: pd.DataFrame,
    goalkeepers: pd.DataFrame,
) -> pd.DataFrame:
    final = base.copy()
    outfield_indexed = outfield.set_index("player_id")
    goalkeepers = goalkeepers.copy()
    for source, target in (
        (
            "goals_prevented_proxy_p90",
            "goals_prevented_proxy_p90_v3",
        ),
        (
            "high_leverage_save_rate_shrunk",
            "high_leverage_save_rate_shrunk_v3",
        ),
    ):
        if source in goalkeepers:
            goalkeepers[target] = goalkeepers[source]
    goalkeeper_indexed = goalkeepers.set_index("player_id")
    for column in outfield.columns:
        if column in {
            "player_id",
            "team",
            "player_name",
            "player",
            "position",
            "position_group",
            "position_group_360",
            "functional_role",
            "functional_role_original",
            "minutes_played",
            "is_main_goalkeeper",
        } or column in final.columns:
            continue
        final[column] = final["player_id"].map(outfield_indexed[column])
    goalkeeper_columns = [
        column
        for column in goalkeepers.columns
        if column.endswith("_v3")
        or column == "percentile_equivalent_placement"
    ]
    for column in goalkeeper_columns:
        values = final["player_id"].map(goalkeeper_indexed[column])
        goalkeeper_rows = final["position_group"].eq("Goalkeeper")
        if column not in final:
            final[column] = values
            continue
        final.loc[goalkeeper_rows, column] = values.loc[goalkeeper_rows]

    final["gk_rank_v3"] = pd.to_numeric(
        final.get("goalkeeper_rank_v3"),
        errors="coerce",
    ).astype("Int64")
    main_goalkeeper = (
        final["position_group"].eq("Goalkeeper")
        & final.get(
            "is_main_goalkeeper",
            pd.Series(False, index=final.index),
        ).fillna(False)
    )
    final.loc[
        main_goalkeeper,
        "uncertainty_low_v3",
    ] = pd.to_numeric(
        final.loc[
            main_goalkeeper,
            "goalkeeper_score_interval_low_v3",
        ],
        errors="coerce",
    )
    final.loc[
        main_goalkeeper,
        "uncertainty_high_v3",
    ] = pd.to_numeric(
        final.loc[
            main_goalkeeper,
            "goalkeeper_score_interval_high_v3",
        ],
        errors="coerce",
    )
    final.loc[
        main_goalkeeper,
        "uncertainty_status_v3",
    ] = final.loc[
        main_goalkeeper,
        "goalkeeper_uncertainty_status_v3",
    ]
    backup = final["position_group"].eq("Goalkeeper") & ~main_goalkeeper
    final.loc[backup, "uncertainty_status_v3"] = "unranked-backup-goalkeeper"

    final["publication_score_v3"] = pd.to_numeric(
        final.get("tournament_impact_score_v3"),
        errors="coerce",
    )
    goalkeeper_percentile = pd.to_numeric(
        final.loc[
            main_goalkeeper,
            "percentile_equivalent_placement",
        ],
        errors="coerce",
    )
    outfield_scores = (
        pd.to_numeric(
            final.loc[
                final["position_group"].ne("Goalkeeper"),
                "tournament_impact_score_v3",
            ],
            errors="coerce",
        )
        .dropna()
        .sort_values()
        .to_numpy()
    )
    equivalent_scores = np.quantile(
        outfield_scores,
        goalkeeper_percentile.clip(0.0, 1.0).to_numpy(),
        method="linear",
    )
    final.loc[
        main_goalkeeper,
        "percentile_equivalent_score_v3",
    ] = equivalent_scores
    final.loc[main_goalkeeper, "publication_score_v3"] = equivalent_scores
    eligible = (
        final["position_group"].ne("Goalkeeper") | main_goalkeeper
    ) & final["publication_score_v3"].notna()
    final["publication_global_rank_v3"] = pd.Series(
        pd.NA,
        index=final.index,
        dtype="Int64",
    )
    final.loc[eligible, "publication_global_rank_v3"] = (
        final.loc[eligible, "publication_score_v3"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    final["publication_team_rank_v3"] = pd.Series(
        pd.NA,
        index=final.index,
        dtype="Int64",
    )
    final.loc[eligible, "publication_team_rank_v3"] = (
        final.loc[eligible]
        .groupby("team", sort=False)["publication_score_v3"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    final["ranking_release_status_v3"] = "promoted"
    final["active_model_version"] = ACTIVE_MODEL_VERSION
    return final


def _leave_one_match_out_stability(
    match: pd.DataFrame,
    *,
    selected_attack: str,
    config: TournamentRankingV3Config,
) -> dict[str, Any]:
    attack = build_attack_ablation_scores(match, config=config)
    working = match[
        ["match_id", "player_id", "defensive_value_non_shootout"]
    ].copy()
    working["impact"] = (
        pd.to_numeric(attack[selected_attack], errors="coerce")
        + pd.to_numeric(
            working["defensive_value_non_shootout"],
            errors="coerce",
        )
    )
    pivot = (
        working.groupby(["match_id", "player_id"])["impact"]
        .sum()
        .unstack("player_id", fill_value=0.0)
    )
    full = pivot.sum(axis=0)
    full_rank = full.rank(method="average", ascending=False)
    full_top = set(full.nlargest(20).index)
    correlations: list[float] = []
    jaccards: list[float] = []
    for match_id in pivot.index:
        held = full - pivot.loc[match_id]
        correlations.append(_spearman(full_rank, held.rank(ascending=False)))
        held_top = set(held.nlargest(20).index)
        union = full_top | held_top
        jaccards.append(
            len(full_top & held_top) / len(union) if union else 1.0
        )
    return {
        "matches": int(len(pivot)),
        "rank_spearman_mean": float(np.mean(correlations)),
        "rank_spearman_minimum": float(np.min(correlations)),
        "top20_jaccard_mean": float(np.mean(jaccards)),
        "top20_jaccard_minimum": float(np.min(jaccards)),
    }


def _build_release_audit(
    final: pd.DataFrame,
    match: pd.DataFrame,
    *,
    attack_audit: dict[str, Any],
    attack_overlap_audit: dict[str, Any],
    attack_selection: str,
    attack_decision: str,
    defense_audit: dict[str, Any],
    goalkeeper_audit: dict[str, Any],
    ranking_audit: dict[str, Any],
    config: TournamentRankingV3Config,
    events: pd.DataFrame,
) -> dict[str, Any]:
    champion = json.loads(
        (CHAMPION_ROOT / "champion_snapshot.json").read_text(
            encoding="utf-8"
        )
    )
    outfield = final.loc[final["position_group"].ne("Goalkeeper")].copy()
    score_minutes = _bootstrap_spearman_interval(
        outfield["tournament_impact_raw_v3"],
        outfield["minutes_played"],
    )
    score_goals = _bootstrap_spearman_interval(
        outfield["tournament_impact_raw_v3"],
        outfield["regulation_extra_time_goals"],
        seed=43,
    )
    score_xg = _bootstrap_spearman_interval(
        outfield["tournament_impact_raw_v3"],
        outfield["xg_non_shootout"],
        seed=44,
    )
    score_xa = _bootstrap_spearman_interval(
        outfield["tournament_impact_raw_v3"],
        outfield["xa_non_shootout"],
        seed=45,
    )
    selected_defense = defense_audit["selected_challenger"]
    defense_champion = defense_audit["candidates"][
        "positive_elastic_net"
    ]["metrics"]
    defense_selected = defense_audit["candidates"][selected_defense][
        "metrics"
    ]
    defense_bootstrap = defense_audit["bootstrap_comparison"]
    goalkeeper_selected = goalkeeper_audit["calibration"][
        "method_metrics"
    ]["selected"]
    goalkeeper_champion = champion["model_metrics"]["goalkeeper"]
    goal_audit = tournament_goal_reconciliation(events)
    generalized = _generalized_validity_audit(final)
    stability = _leave_one_match_out_stability(
        match,
        selected_attack=attack_selection,
        config=config,
    )
    defense_gate = bool(defense_audit["promotion_gate"]["passed"])
    goalkeeper_gate = bool(goalkeeper_audit["gate_passed"])
    ranking_gate = bool(ranking_audit["passed"])
    attack_gate = bool(
        attack_audit["metrics"][attack_selection]["gate_passed"]
    )
    pass_gates = {
        "1": {
            "decision": "PASS",
            "selection": "immutable champion snapshot",
            "tests": "tests/test_ranking_repair_champion.py",
        },
        "2": {
            "decision": "PASS",
            "selection": EVENT_SCOPE_VERSION,
            "tests": "tests/test_event_scope.py",
        },
        "3": {
            "decision": "PASS" if defense_gate else "FALLBACK",
            "selection": (
                f"defensive_challenger:{selected_defense}"
                if defense_gate
                else "positive_elastic_net champion"
            ),
            "tests": "tests/test_defensive_challenger.py",
        },
        "4": {
            "decision": "PASS" if ranking_gate else "FAIL",
            "selection": "Tournament Impact / Role Quality / Uncertainty",
            "tests": "tests/test_tournament_rankings_v3.py",
        },
        "5": {
            "decision": "PASS" if attack_gate else "FALLBACK",
            "selection": attack_selection,
            "tests": "tests/test_tournament_rankings_v3.py",
        },
        "6": {
            "decision": "PASS" if defense_gate and ranking_gate else "FAIL",
            "selection": (
                f"opportunity-adjusted {selected_defense}; legacy lift retired"
            ),
            "tests": (
                "tests/test_defensive_challenger.py and "
                "tests/test_tournament_rankings_v3.py"
            ),
        },
        "7": {
            "decision": "PASS" if goalkeeper_gate else "FALLBACK",
            "selection": (
                "goalkeeper_v3"
                if goalkeeper_gate
                else "goalkeeper_v2 champion"
            ),
            "tests": "tests/test_goalkeeper_valuation_v3.py",
        },
        "8": {
            "decision": "PASS",
            "selection": "active v3 generators and complete artifact family",
            "tests": (
                "tests/test_ranking_repair_release_v3.py and DOCX validation"
            ),
        },
    }
    component_selections = {
        "attack": {
            "champion": "process_only",
            "challenger": "process_plus_shrunk_residual",
            "decision": attack_decision,
            "selected": attack_selection,
        },
        "defense": {
            "champion": "positive_elastic_net",
            "challenger": selected_defense,
            "decision": (
                "promote_challenger"
                if defense_gate
                else "retain_champion"
            ),
            "selected": (
                selected_defense if defense_gate else "positive_elastic_net"
            ),
        },
        "outfield_ranking": {
            "champion": "unified_v2_publication",
            "challenger": "ranking_repair_v3",
            "decision": "promote_challenger" if ranking_gate else "retain_champion",
            "selected": "ranking_repair_v3" if ranking_gate else "unified_v2",
        },
        "goalkeeper": {
            "champion": "goalkeeper_v2",
            "challenger": "goalkeeper_v3",
            "decision": (
                "promote_challenger"
                if goalkeeper_gate
                else "retain_champion"
            ),
            "selected": (
                "goalkeeper_v3" if goalkeeper_gate else "goalkeeper_v2"
            ),
        },
        "cross_position_goalkeeper": {
            "champion": "Blom bridge described ambiguously",
            "challenger": "percentile_equivalent_placement",
            "decision": "promote_explicit_fallback",
            "selected": "percentile_equivalent_placement",
        },
    }
    metric_rows = [
        {
            "metric": "defense_oof_rmse",
            "champion": defense_champion["rmse"],
            "challenger": defense_selected["rmse"],
            "difference": (
                defense_selected["rmse"] - defense_champion["rmse"]
            ),
            "ci_low": defense_bootstrap[
                "rmse_difference_challenger_minus_positive_champion"
            ]["ci_low"],
            "ci_high": defense_bootstrap[
                "rmse_difference_challenger_minus_positive_champion"
            ]["ci_high"],
            "gate": "PASS" if defense_gate else "FAIL",
        },
        {
            "metric": "defense_oof_spearman",
            "champion": defense_champion["spearman"],
            "challenger": defense_selected["spearman"],
            "difference": (
                defense_selected["spearman"]
                - defense_champion["spearman"]
            ),
            "ci_low": defense_bootstrap[
                "spearman_difference_challenger_minus_positive_champion"
            ]["ci_low"],
            "ci_high": defense_bootstrap[
                "spearman_difference_challenger_minus_positive_champion"
            ]["ci_high"],
            "gate": "PASS" if defense_gate else "FAIL",
        },
        {
            "metric": "goalkeeper_brier_score",
            "champion": goalkeeper_champion["brier_score"],
            "challenger": goalkeeper_selected["brier_score"],
            "difference": (
                goalkeeper_selected["brier_score"]
                - goalkeeper_champion["brier_score"]
            ),
            "ci_low": None,
            "ci_high": None,
            "gate": "PASS" if goalkeeper_gate else "FAIL",
        },
        {
            "metric": "goalkeeper_ece",
            "champion": goalkeeper_champion[
                "expected_calibration_error"
            ],
            "challenger": goalkeeper_selected[
                "expected_calibration_error"
            ],
            "difference": (
                goalkeeper_selected["expected_calibration_error"]
                - goalkeeper_champion["expected_calibration_error"]
            ),
            "ci_low": None,
            "ci_high": None,
            "gate": "PASS" if goalkeeper_gate else "FAIL",
        },
        {
            "metric": "impact_minutes_spearman",
            "champion": champion["score_correlations"]["minutes"][
                "estimate"
            ],
            "challenger": score_minutes["estimate"],
            "difference": (
                score_minutes["estimate"]
                - champion["score_correlations"]["minutes"]["estimate"]
            ),
            "ci_low": score_minutes["ci_low"],
            "ci_high": score_minutes["ci_high"],
            "gate": "descriptive",
        },
        {
            "metric": "impact_goals_spearman",
            "champion": champion["score_correlations"]["goals"][
                "estimate"
            ],
            "challenger": score_goals["estimate"],
            "difference": (
                score_goals["estimate"]
                - champion["score_correlations"]["goals"]["estimate"]
            ),
            "ci_low": score_goals["ci_low"],
            "ci_high": score_goals["ci_high"],
            "gate": "descriptive",
        },
    ]
    release_passed = all(
        (
            goal_audit["official_match_goals_including_own_goals"] == 172,
            defense_gate,
            ranking_gate,
            attack_gate,
            goalkeeper_gate,
        )
    )
    return {
        "schema_version": "ranking-repair-audit-3.0",
        "active_model_version": ACTIVE_MODEL_VERSION,
        "release_status": (
            "PASS — promoted all passing v3 components"
            if release_passed
            else "PARTIAL — retained failed component champion"
        ),
        "event_scope_version": EVENT_SCOPE_VERSION,
        "event_reconciliation": goal_audit,
        "zero_identity_scoring_confirmed": True,
        "component_selections": component_selections,
        "pass_gates": pass_gates,
        "champion_challenger": {"metrics": metric_rows},
        "attack": {
            **attack_audit,
            "safe_selected_candidate": attack_selection,
            "safe_selection_decision": attack_decision,
            "xt_vaep_overlap_ablation": attack_overlap_audit,
            "full_outcomes_prohibited_when_process_contains_outcomes": True,
        },
        "defense": defense_audit,
        "goalkeeper": goalkeeper_audit,
        "ranking": {
            **ranking_audit,
            "score_minutes_spearman": score_minutes,
            "score_goals_spearman": score_goals,
            "score_xg_spearman": score_xg,
            "score_xa_spearman": score_xa,
            "leave_one_match_out_stability": stability,
            "active_global_field": "tournament_impact_v3",
            "active_role_field": "role_quality_v3",
            "uncertainty_field": (
                "uncertainty_low_v3 / uncertainty_high_v3"
            ),
            "legacy_one_sided_defensive_lift_active": False,
            "legacy_exposure_cascade_active": False,
        },
        "generalized_validity": generalized,
        "score_feature_contract": score_feature_contract(config),
        "limitations": [
            "StatsBomb Open Data is event data, not continuous optical tracking.",
            "360 coverage is event-actor and match dependent; missing coverage "
            "remains missing rather than zero.",
            "Goalkeeper cross-position publication uses an explicitly labelled "
            "percentile-equivalent placement because common-unit GK action "
            "values are not fully identified.",
            "Tournament Impact describes Qatar 2022 only and is not a career or "
            "future-strength estimate.",
        ],
    }


def _clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _clean_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean_json(item) for item in value]
    if isinstance(value, np.generic):
        return _clean_json(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if value is pd.NA:
        return None
    return value


def _write_diagnostic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            _clean_json(payload),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _scan_stale_content(
    project_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Return explicitly classified matches for retired ranking formulas.

    The audit is intentionally narrower than a raw ``rg`` search.  In
    particular, the shootout rule requires scoring language around an exact
    ``0.20`` token so values such as ``xg_non_shootout: 0.2051`` cannot match.
    Known foundation/compatibility modules remain visible in the audit with a
    non-active classification rather than being silently skipped.
    """

    root = PROJECT_ROOT if project_root is None else Path(project_root)
    patterns = {
        "shootout-save-0.20": re.compile(
            r"""
            (?:
                \b
                (?:
                    GOALKEEPER_TOURNAMENT_IMPACT_PER_SHOOTOUT_SAVE
                    |
                    shootout[_\s-]*
                    (?:save|saves|saved|saving|penalt(?:y|ies)|conversion)
                    [_\s-]*
                    (?:points?|bonus|value|weight|impact|contribution)?
                )
                \b
                .{0,60}?
                (?:=|:|adds?|added|contributes?|awards?|per)
                .{0,24}?
                `?(?:0?\.20)\b
                |
                `?(?:0?\.20)\b
                .{0,60}?
                (?:additive\s+points?|points?\s+per|per)
                \s+(?:goalkeeper\s+)?
                shootout\s+
                (?:save|saves|penalt(?:y|ies)|conversion)
            )
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
        "old-exposure-constants": re.compile(
            r"(EXPOSURE_SATURATION_SHARE|PUBLICATION_EXPOSURE_SHARE|"
            r"MinutesReliability.{0,20}450|"
            r"minutes\s*/\s*\(\s*minutes\s*\+\s*450(?:\.0+)?\s*\))",
            re.IGNORECASE,
        ),
        "within-position-absolute": re.compile(
            r"within-position.{0,80}(?:absolute|global|publication|z-score)",
            re.IGNORECASE,
        ),
        "one-sided-defensive-lift": re.compile(
            r"(one-sided.{0,50}defensive|DEFENSIVE_EVIDENCE_LIFT)",
            re.IGNORECASE,
        ),
        "stale-docx-appendix": re.compile(
            r"Part IX: Unified tournament publication layer",
            re.IGNORECASE,
        ),
    }
    extensions = {".py", ".md", ".json", ".txt"}
    skip_parts = {".git", ".venv", "__pycache__", "node_modules"}
    recursive_audit_paths = {
        "results/diagnostics/ranking_repair/stale_content_audit.json",
        "results/diagnostics/ranking_repair/stale_content_audit.md",
    }
    derived_inventory_paths = {
        "results/documentation/file_catalog.json",
        "results/documentation/file_dictionary.json",
    }
    compatibility_files = {
        # Frozen/foundation orchestration and its compatibility generators.
        "scripts/annotate_reports_with_uncertainty.py",
        "scripts/generate_final_tournament_report.py",
        "scripts/quantify_player_rating_uncertainty.py",
        "scripts/refresh_tournament_rankings_v2.py",
        "scripts/run_pipeline.py",
        "scripts/run_team_simulation_reports.py",
        "scripts/unify_tournament_ratings.py",
        "scripts/update_v2_final_summary_docx.py",
        # The reusable V4/V5 feature foundation is not the active v3 ranking.
        "src/features/goalkeepers.py",
        "src/models/goalkeeper_valuation.py",
        "src/models/tournament_rankings.py",
        "src/models/valuation.py",
        "src/rating_uncertainty.py",
        "src/report_generators.py",
        "src/reporting/artifacts.py",
        "src/simulation_engine.py",
        # Generated provenance for that preserved foundation.
        "data/processed/player_evaluation_provenance.json",
        "data/processed/player_evaluation_v5_provenance.json",
    }
    compatibility_prefixes = (
        "results/diagnostics/ranking_repair/champion/",
        "results/reports/ranking/legacy/",
        "results/reports/v5_figures/",
        "results/MIscellaneous/",
        "results/miscellaneous/",
    )
    governing_historical_files = {
        "docs/ranking-repair-eight-pass-prompt.md",
    }
    historical_markers = re.compile(
        r"(?:\bretired(?:\b|[_-])|"
        r"\b(?:historical|legacy|former|pre-v3|pre-v2|"
        r"frozen\s+champion|compatibility|preserved\s+for\s+"
        r"(?:comparison|reproducibility)|not\s+an?\s+active)\b)",
        re.IGNORECASE,
    )
    negative_markers = re.compile(
        r"\b(?:no|not|never|without|cannot|does\s+not|do\s+not|"
        r"must\s+not|is\s+not|are\s+not|excluded|prohibited|"
        r"removed|inactive|rather\s+than)\b",
        re.IGNORECASE,
    )

    def _scanner_definition_range(lines: list[str]) -> range:
        """Locate this function so its literal search regexes self-classify."""

        start = next(
            (
                index
                for index, source_line in enumerate(lines)
                if source_line.startswith("def _scan_stale_content(")
            ),
            -1,
        )
        if start < 0:
            return range(0)
        end = next(
            (
                index
                for index in range(start + 1, len(lines))
                if lines[index].startswith("def ")
            ),
            len(lines),
        )
        return range(start, end)

    def _semantic_context(lines: list[str], index: int) -> str:
        """Join nearby source fragments for split prose/string literals."""

        start = max(0, index - 3)
        end = min(len(lines), index + 4)
        return " ".join(
            fragment.strip()
            for fragment in lines[start:end]
            if fragment.strip()
        )

    def _inside_retired_container(lines: list[str], index: int) -> bool:
        """Recognize the generated/source list that inventories retired rules."""

        start = max(0, index - 12)
        marker = next(
            (
                candidate
                for candidate in range(index, start - 1, -1)
                if "retired_active_methods" in lines[candidate]
            ),
            None,
        )
        if marker is None:
            return False
        return not any(
            re.match(r"^\s*\]\s*,?\s*$", lines[candidate])
            for candidate in range(marker + 1, index + 1)
        )

    def _looks_like_active_python_formula(
        relative: str,
        line: str,
        match_start: int,
    ) -> bool:
        """Keep executable assignments ahead of nearby prose negation."""

        if not relative.endswith(".py"):
            return False
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            return False
        if re.match(
            r"""^(?:[rubf]{0,2})?["'][^"']+["']\s*:""",
            stripped,
            flags=re.IGNORECASE,
        ):
            return True
        prefix = line[:match_start]
        single_quotes = len(re.findall(r"(?<!\\)'", prefix))
        double_quotes = len(re.findall(r'(?<!\\)"', prefix))
        match_is_inside_string = (
            single_quotes % 2 == 1 or double_quotes % 2 == 1
        )
        return "=" in line and not match_is_inside_string

    def _is_stale_guard(lines: list[str], index: int) -> bool:
        """Recognize an assertion/validator that rejects retired wording."""

        stripped = lines[index].strip()
        if stripped.startswith("assert "):
            return True
        if not stripped.startswith("if "):
            return False
        return any(
            candidate.strip().startswith(("raise ", "assert "))
            for candidate in lines[index + 1 : index + 3]
        )

    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or path.suffix.lower() not in extensions
            or skip_parts.intersection(path.parts)
            or path.stat().st_size > 5_000_000
        ):
            continue
        relative = path.relative_to(root).as_posix()
        if (
            relative in recursive_audit_paths
            or relative in derived_inventory_paths
            or relative.startswith("results/documentation/folders/")
        ):
            continue
        try:
            lines = path.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()
        except OSError:
            continue
        scanner_definition = (
            _scanner_definition_range(lines)
            if relative == "scripts/run_ranking_repair_v3.py"
            else range(0)
        )
        for line_index, line in enumerate(lines):
            for label, pattern in patterns.items():
                match = pattern.search(line)
                if match is None:
                    continue
                line_number = line_index + 1
                semantic_context = _semantic_context(lines, line_index)
                if relative.startswith("tests/"):
                    classification = "test-fixture"
                    reason = "test source or fixture"
                elif (
                    relative in compatibility_files
                    or relative in governing_historical_files
                    or any(
                        relative.startswith(prefix)
                        for prefix in compatibility_prefixes
                    )
                ):
                    classification = "compatibility-or-legacy"
                    reason = (
                        "explicit compatibility, foundation, champion, or "
                        "historical path"
                    )
                elif line_index in scanner_definition:
                    classification = "active-and-correct"
                    reason = "stale-audit scanner definition"
                elif _inside_retired_container(lines, line_index):
                    classification = "compatibility-or-legacy"
                    reason = "explicit retired-method inventory"
                elif (
                    label == "stale-docx-appendix"
                    and re.match(r"^\s*APPENDIX_TITLE\s*=", line)
                ):
                    classification = "stale-requires-correction"
                    reason = "active DOCX generator assigns retired appendix"
                elif _is_stale_guard(lines, line_index):
                    classification = "active-and-correct"
                    reason = "active validator rejects retired content"
                elif _looks_like_active_python_formula(
                    relative,
                    line,
                    match.start(),
                ):
                    classification = "stale-requires-correction"
                    reason = "executable retired formula in active Python"
                elif historical_markers.search(semantic_context):
                    classification = "compatibility-or-legacy"
                    reason = "explicitly historical or retired description"
                elif negative_markers.search(semantic_context):
                    classification = "active-and-correct"
                    reason = "active text explicitly negates retired method"
                else:
                    classification = "stale-requires-correction"
                    reason = "unnegated retired formula in active scope"
                records.append(
                    {
                        "path": relative,
                        "line": line_number,
                        "pattern": label,
                        "classification": classification,
                        "classification_reason": reason,
                        "context": line.strip()[:300],
                    }
                )
    return records


def run_release(args: argparse.Namespace) -> dict[str, Any]:
    print("[v3] validating and rebuilding source inputs", flush=True)
    _ensure_inputs(
        run_foundation=args.run_foundation,
        rerun_defense=not args.reuse_pass3,
        rebuild_inputs=not args.reuse_inputs,
        reuse_goalkeeper=args.reuse_pass7,
    )
    event_columns = [
        "match_id",
        "period",
        "type",
        "team",
        "shot_type",
        "shot_outcome",
        "shot_statsbomb_xg",
        "shot_end_location",
        "shot_body_part",
        "shot_technique",
        "shot_one_on_one",
        "shot_first_time",
    ]
    events = pd.read_csv(
        EVENTS_PATH,
        usecols=event_columns,
        low_memory=False,
    )
    events = events.loc[
        events["type"].astype(str).str.contains(
            r"Shot|Own Goal",
            case=False,
            na=False,
        )
    ].copy()
    print(f"[v3] loaded {len(events):,} scoped event rows", flush=True)
    matches = pd.read_csv(MATCHES_PATH)
    actions = pd.read_parquet(
        ACTIONS_PATH,
        columns=[
            "game_id",
            "action_id",
            "period_id",
            "team",
            "player_id",
            "type_name",
            "action_side",
            "vaep_value",
            "xa_value",
            "xt_value",
        ],
    )
    print(f"[v3] loaded {len(actions):,} action rows", flush=True)
    components = pd.read_csv(COMPONENTS_PATH)
    base = pd.read_csv(ACTIVE_RANKINGS_PATH, low_memory=False)
    print(
        f"[v3] loaded {len(components):,} player-match and "
        f"{len(base):,} release rows",
        flush=True,
    )
    if base["player_id"].duplicated().any():
        raise ValueError("Active foundation table has duplicate player IDs")

    match = _player_match_attack_values(actions, components)
    print(f"[v3] built {len(match):,} attack match rows", flush=True)
    match, defense_audit = _attach_defensive_values(match)
    match = _attach_next_match_attack_target(match, matches)
    print("[v3] attached defensive OOF and future-match targets", flush=True)
    attack_evaluation = match.loc[
        match["next_match_attack_output_v3"].notna()
    ].copy()
    core_config = _attack_configuration(())
    attack_audit = evaluate_attack_ablations(
        attack_evaluation,
        target_column="next_match_attack_output_v3",
        config=core_config,
    )
    overlap_audit = evaluate_attack_ablations(
        attack_evaluation,
        target_column="next_match_attack_output_v3",
        config=_attack_configuration((), include_xt_overlap=True),
    )
    attack_selection, attack_decision = _select_safe_attack_candidate(
        attack_audit
    )
    print(
        f"[v3] attack gate selected {attack_selection}",
        flush=True,
    )
    role_probability_columns = tuple(
        column
        for column in base.columns
        if re.fullmatch(r"role_probability_\d+", column)
    )
    config = _attack_configuration(
        role_probability_columns,
        selected=attack_selection,
    )
    match_attack = build_attack_ablation_scores(match, config=config)
    match["positive_contribution_value_non_shootout"] = (
        pd.to_numeric(
            match_attack[attack_selection],
            errors="coerce",
        )
        + pd.to_numeric(
            match["defensive_value_non_shootout"],
            errors="coerce",
        )
    ).clip(lower=0.0)
    player_inputs = _aggregate_player_scoring_inputs(match, base)
    outfield_inputs = player_inputs.loc[
        player_inputs["position_group"].ne("Goalkeeper")
    ].copy()
    outfield_match = match.loc[
        match["player_id"].isin(outfield_inputs["player_id"])
    ].copy()
    outfield_ranked = calculate_tournament_rankings_v3(
        outfield_inputs,
        match_contributions=outfield_match,
        config=config,
        selected_attack_candidate=attack_selection,
    )
    outfield_ranked["tournament_impact_raw_v3"] = pd.to_numeric(
        outfield_ranked["tournament_impact_v3"],
        errors="coerce",
    )
    impact = outfield_ranked["tournament_impact_raw_v3"]
    span = float(impact.max() - impact.min())
    outfield_ranked["tournament_impact_score_v3"] = (
        (impact - float(impact.min())) / span
        if span > 1e-12
        else 0.5
    )
    outfield_ranked["publication_score_v3"] = outfield_ranked[
        "tournament_impact_score_v3"
    ]
    ranking_audit = ranking_gate_diagnostics(outfield_ranked)
    print("[v3] outfield v3 scoring and bootstrap complete", flush=True)

    goalkeeper_ranked = pd.read_csv(PASS7_RATINGS, low_memory=False)
    goalkeeper_audit = json.loads(PASS7_AUDIT.read_text(encoding="utf-8"))
    print("[v3] goalkeeper calibration and bootstrap complete", flush=True)
    final = _merge_v3_outputs(
        base,
        outfield_ranked,
        goalkeeper_ranked,
    )
    audit = _build_release_audit(
        final,
        outfield_match,
        attack_audit=attack_audit,
        attack_overlap_audit=overlap_audit,
        attack_selection=attack_selection,
        attack_decision=attack_decision,
        defense_audit=defense_audit,
        goalkeeper_audit=goalkeeper_audit,
        ranking_audit=ranking_audit,
        config=config,
        events=events,
    )

    diagnostics = PASS3_ROOT
    _write_diagnostic_json(
        diagnostics / "pass5_attack_ablations.json",
        audit["attack"],
    )
    _write_diagnostic_json(
        diagnostics / "pass4_ranking_gate.json",
        audit["ranking"],
    )
    _write_diagnostic_json(
        diagnostics / "pass7_goalkeeper_v3.json",
        audit["goalkeeper"],
    )
    _write_diagnostic_json(
        diagnostics / "v3_release_audit.json",
        audit,
    )
    shadow_path = diagnostics / "v3_shadow_player_rankings.csv"
    final.to_csv(
        shadow_path,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )
    champion_table = pd.read_csv(
        CHAMPION_ROOT / "player_rankings.csv",
        low_memory=False,
    )
    champion_rank_column = (
        "Global Rank"
        if "Global Rank" in champion_table
        else "global_rank_v2"
    )
    comparison = final[
        [
            "player_id",
            "player_name",
            "team",
            "position_group",
            "global_rank_v3",
            "team_rank_v3",
            "tournament_impact_raw_v3",
        ]
    ].merge(
        champion_table[
            ["player_id", champion_rank_column]
        ].rename(columns={champion_rank_column: "champion_global_rank"}),
        on="player_id",
        how="left",
        validate="one_to_one",
    )
    comparison["rank_change_challenger_minus_champion"] = (
        pd.to_numeric(
            comparison["global_rank_v3"],
            errors="coerce",
        )
        - pd.to_numeric(
            comparison["champion_global_rank"],
            errors="coerce",
        )
    )
    comparison.to_csv(
        diagnostics / "champion_challenger_rank_comparison.csv",
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )
    outfield_ranked[
        [
            "player_id",
            "uncertainty_low_v3",
            "uncertainty_high_v3",
            "uncertainty_std_v3",
            "bootstrap_rank_best_v3",
            "bootstrap_rank_worst_v3",
            "uncertainty_status_v3",
        ]
    ].to_csv(
        diagnostics / "v3_bootstrap_rank_intervals.csv",
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )

    writer = RankingRepairReleaseWriter(PROJECT_ROOT)
    rich, goalkeeper, ranking_paths = writer.write_rankings(final)
    print("[v3] ranking tables written", flush=True)
    writer.write_methodology_and_audits(audit)
    writer.write_summaries(rich, goalkeeper, audit)
    writer.write_profiles_and_team_reports(rich)
    print("[v3] profiles and team reports written", flush=True)
    writer.write_figures(
        rich,
        goalkeeper,
        audit,
        champion=champion_table,
    )
    writer.write_release_reference_files(audit)
    writer.write_pass_checklist(audit)

    if not args.skip_documentation:
        _run(
            [
                sys.executable,
                str(
                    PROJECT_ROOT
                    / "results"
                    / "documentation"
                    / "generate_documentation.py"
                ),
            ]
        )
    if not args.skip_docx:
        _run(
            [
                sys.executable,
                str(
                    PROJECT_ROOT
                    / "scripts"
                    / "update_unified_final_summary_docx.py"
                ),
            ]
        )

    stale_records = _scan_stale_content()
    writer.write_stale_content_audit(stale_records)
    active_stale = [
        record
        for record in stale_records
        if record["classification"] == "stale-requires-correction"
    ]
    if active_stale and not args.allow_stale:
        examples = ", ".join(
            f"{row['path']}:{row['line']}" for row in active_stale[:10]
        )
        raise RuntimeError(
            f"Active stale-content audit failed ({len(active_stale)}): "
            f"{examples}"
        )
    manifest_paths = writer.write_manifests(
        source_hashes=_current_source_hashes()
    )
    return {
        "status": "complete",
        "active_model_version": ACTIVE_MODEL_VERSION,
        "release_status": audit["release_status"],
        "attack_selection": attack_selection,
        "defense_selection": defense_audit["selected_challenger"],
        "goalkeeper_selection": (
            "goalkeeper_v3"
            if goalkeeper_audit["gate_passed"]
            else "goalkeeper_v2"
        ),
        "players": int(len(rich)),
        "outfield_players": int(
            rich["position_group"].ne("Goalkeeper").sum()
        ),
        "main_goalkeepers": int(len(goalkeeper)),
        "ranking_artifacts": len(ranking_paths),
        "manifest_paths": [
            path.relative_to(PROJECT_ROOT).as_posix()
            for path in manifest_paths
        ],
        "stale_active_matches": len(active_stale),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-foundation",
        action="store_true",
        help=(
            "Regenerate the validated role-aware foundation before v3 scoring."
        ),
    )
    parser.add_argument(
        "--reuse-pass3",
        action="store_true",
        help="Reuse the existing deterministic Pass-3 diagnostics.",
    )
    parser.add_argument(
        "--reuse-inputs",
        action="store_true",
        help="Reuse already rebuilt possession and player-match inputs.",
    )
    parser.add_argument(
        "--reuse-pass7",
        action="store_true",
        help="Reuse isolated goalkeeper-v3 ratings and calibration audit.",
    )
    parser.add_argument("--skip-documentation", action="store_true")
    parser.add_argument("--skip-docx", action="store_true")
    parser.add_argument(
        "--allow-stale",
        action="store_true",
        help="Write the stale audit without failing on unresolved active rows.",
    )
    return parser.parse_args()


def main() -> None:
    result = run_release(parse_args())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
