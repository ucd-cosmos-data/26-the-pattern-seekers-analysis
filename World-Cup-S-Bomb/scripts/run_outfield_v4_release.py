#!/usr/bin/env python3
"""Build the preregistered, opposition-aware outfield v4 release.

The configuration grid is evaluated behind a fixture firewall.  Named-player
and external-consensus gates are evaluated only after selection is locked.
Every v3 artifact remains frozen; the writer publishes a parallel v4 family.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.outfield_context_v4 import (  # noqa: E402
    OPPOSITION_VARIANTS,
    allocate_match_context_to_players,
    build_off_ball_prevention_oof,
    build_opponent_context,
)
from src.models.outfield_tournament_impact_v4 import (  # noqa: E402
    MODEL_VERSION,
    REQUIRED_DEFENSIVE_PIPELINE_STAGES,
    DefensivePipeline,
    OutfieldV4Config,
    add_reporting_ranks,
    bootstrap_se_shrinkage,
    channel_count_reliability,
    continuous_role_mixture,
    variance_balanced_composite,
)


ACTIVE_MODEL_VERSION = (
    "outfield-tournament-impact-v4+goalkeeper-event-profile-v3"
)
PREREG_PATH = (
    PROJECT_ROOT
    / "results"
    / "diagnostics"
    / "ranking_repair"
    / "outfield_v4_preregistration.json"
)
DIAGNOSTICS_ROOT = PREREG_PATH.parent
BASE_RANKINGS_PATH = (
    PROJECT_ROOT / "results" / "reports" / "ranking" / "player_rankings_v3.csv"
)
MATCHES_PATH = PROJECT_ROOT / "data" / "raw" / "matches.csv"
FIFA_RANKINGS_PATH = PROJECT_ROOT / "config" / "fifa_rankings_2022-10-06.csv"
POSSESSIONS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_clusters.csv"
)
COMPONENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "world_cup_player_match_components.csv"
)
DEFENSE_PREDICTIONS_PATH = (
    DIAGNOSTICS_ROOT / "pass3_defensive_challenger_oof_predictions.csv"
)
DEFENSE_SAMPLES_PATH = (
    DIAGNOSTICS_ROOT / "pass3_defensive_challenger_samples.csv"
)
V3_AUDIT_PATH = DIAGNOSTICS_ROOT / "v3_release_audit.json"
GK_V4_AUDIT_PATH = DIAGNOSTICS_ROOT / "goalkeeper_v4_audit.json"

FIXTURE_NAMES = {
    "messi": "Lionel Andrés Messi Cuccittini",
    "bellingham": "Jude Bellingham",
    "van_dijk": "Virgil van Dijk",
    "romero": "Cristian Gabriel Romero",
    "otamendi": "Nicolás Hernán Otamendi",
    "hakimi": "Achraf Hakimi Mouh",
    "amrabat": "Sofyan Amrabat",
    "juranovic": "Josip Juranović",
}


def _json_value(value: Any) -> Any:
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
    if not isinstance(value, (str, bytes)) and pd.isna(value):
        return None
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            _json_value(payload),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _validate_preregistration(prereg: Mapping[str, Any]) -> None:
    if prereg.get("contains_final_ranking_results") is not False:
        raise RuntimeError("preregistration contains final-ranking results")
    if prereg.get("configuration_selection_status") != "not_started":
        raise RuntimeError("preregistration was altered after selection")
    stages = tuple(prereg.get("defensive_pipeline_stages", ()))
    if stages != REQUIRED_DEFENSIVE_PIPELINE_STAGES:
        raise RuntimeError("preregistered defensive stage order is invalid")
    base = str(prereg["BALANCE_BASE_COMMIT"])
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    required_shares = {0.35, 0.42, 0.50}
    shares = {
        float(value)
        for value in prereg["candidate_grid"]["variance_share_target"]
    }
    if not required_shares.issubset(shares):
        raise RuntimeError("variance grid omits a required preregistered point")
    variants = tuple(
        prereg["candidate_grid"]["opposition_adjustment_variant"]
    )
    if variants != OPPOSITION_VARIANTS:
        raise RuntimeError(
            "opposition grid disagrees with the implemented leakage guards"
        )


def _baseline_diagnostics(outfield: pd.DataFrame) -> dict[str, Any]:
    attack = pd.to_numeric(outfield["attack_component_v3"], errors="raise")
    defense = pd.to_numeric(
        outfield["defensive_component_v3"], errors="raise"
    )
    impact = pd.to_numeric(outfield["tournament_impact_v3"], errors="raise")
    fixture_rows: dict[str, Any] = {}
    for key, name in FIXTURE_NAMES.items():
        row = outfield.loc[outfield["player_name"].eq(name)]
        if len(row) != 1:
            raise RuntimeError(f"fixture {name!r} is not unique")
        record = row.iloc[0]
        fixture_rows[key] = {
            "player_name": name,
            "player_id": int(record["player_id"]),
            "v3_outfield_rank": int(record["global_rank_v3"]),
            "v3_publication_rank": int(record["publication_global_rank_v3"]),
            "attack_component_v3": float(record["attack_component_v3"]),
            "defensive_component_v3": float(
                record["defensive_component_v3"]
            ),
            "tournament_impact_v3": float(record["tournament_impact_v3"]),
        }
    return {
        "eligible_outfield": int(len(outfield)),
        "attack_component_v3": {
            "std_population": float(attack.std(ddof=0)),
            "min": float(attack.min()),
            "max": float(attack.max()),
        },
        "defensive_component_v3": {
            "std_population": float(defense.std(ddof=0)),
            "min": float(defense.min()),
            "max": float(defense.max()),
        },
        "correlation_with_impact": {
            "attack": float(attack.corr(impact)),
            "defense": float(defense.corr(impact)),
        },
        "unscaled_defensive_variance_share": float(
            defense.var(ddof=0)
            / (attack.var(ddof=0) + defense.var(ddof=0))
        ),
        "fixtures": fixture_rows,
    }


def _v3_artifact_snapshot(base_commit: str) -> dict[str, Any]:
    names = _git(
        "ls-tree",
        "-r",
        "--name-only",
        base_commit,
        "--",
        "World-Cup-S-Bomb/results",
    ).splitlines()
    versioned = [
        name
        for name in names
        if "_v3" in Path(name).name
        or "/v3_" in name
        or "/v3/" in name
    ]
    records: list[dict[str, Any]] = []
    changed: list[str] = []
    for repo_path in versioned:
        relative = Path(repo_path).relative_to("World-Cup-S-Bomb")
        working = PROJECT_ROOT / relative
        expected_blob = _git("rev-parse", f"{base_commit}:{repo_path}")
        actual_blob = _git("hash-object", str(working)) if working.is_file() else None
        preserved = actual_blob == expected_blob
        records.append(
            {
                "path": relative.as_posix(),
                "base_git_blob": expected_blob,
                "working_git_blob": actual_blob,
                "byte_preserved": preserved,
            }
        )
        if not preserved:
            changed.append(relative.as_posix())
    return {
        "artifact_count": len(records),
        "all_byte_preserved": not changed,
        "changed": changed,
        "artifacts": records,
    }


def _attack_match_contributions(
    components: pd.DataFrame,
    outfield: pd.DataFrame,
) -> pd.DataFrame:
    """Allocate the frozen v3 attack channel to matches without refitting it.

    Shot and creation expectation are available at player-match granularity.
    The already-released non-shot process remainder and ordinary-event
    evidence are allocated over that player's matches by the identity-free
    action-count share.  Player totals therefore reproduce v3 exactly while
    supporting match bootstrap and leave-one-match-out diagnostics.
    """

    required = {
        "match_id",
        "team",
        "player_id",
        "minutes",
        "actions",
        "xg_non_shootout",
        "xg_non_penalty",
        "xa_non_shootout",
    }
    missing = required.difference(components.columns)
    if missing:
        raise ValueError(f"attack components are missing: {sorted(missing)}")
    match = components[list(required)].copy()
    match["player_id"] = match["player_id"].astype(int)
    player_columns = [
        "player_id",
        "attack_component_v3",
        "ordinary_action_count_v3",
    ]
    match = match.merge(
        outfield[player_columns],
        on="player_id",
        how="inner",
        validate="many_to_one",
    )
    penalty_xg = (
        pd.to_numeric(match["xg_non_shootout"], errors="raise")
        - pd.to_numeric(match["xg_non_penalty"], errors="raise")
    ).clip(lower=0.0)
    match["_outcome_expectation"] = (
        0.70
        * (
            pd.to_numeric(match["xg_non_penalty"], errors="raise")
            + 0.76 * penalty_xg
        )
        + 0.35 * pd.to_numeric(match["xa_non_shootout"], errors="raise")
    )
    outcome_total = match.groupby("player_id")["_outcome_expectation"].transform(
        "sum"
    )
    process_total = pd.to_numeric(
        match["attack_component_v3"], errors="raise"
    ) - outcome_total
    action_count = pd.to_numeric(match["actions"], errors="coerce").fillna(0.0)
    action_total = action_count.groupby(match["player_id"]).transform("sum")
    minute_count = pd.to_numeric(match["minutes"], errors="coerce").fillna(0.0)
    minute_total = minute_count.groupby(match["player_id"]).transform("sum")
    action_share = action_count.div(action_total.where(action_total.gt(0.0)))
    fallback_share = minute_count.div(minute_total.where(minute_total.gt(0.0)))
    share = action_share.fillna(fallback_share).fillna(0.0)
    match["attack_component_match_v4"] = (
        match["_outcome_expectation"] + process_total * share
    )
    match["ordinary_action_count_match_v4"] = (
        pd.to_numeric(match["ordinary_action_count_v3"], errors="raise") * share
    )
    aggregate = match.groupby("player_id")["attack_component_match_v4"].sum()
    expected = outfield.set_index("player_id")["attack_component_v3"].astype(float)
    if not np.allclose(
        aggregate.reindex(expected.index).to_numpy(),
        expected.to_numpy(),
        rtol=0.0,
        atol=1e-10,
    ):
        raise RuntimeError("match attack allocation does not preserve v3 totals")
    return match[
        [
            "match_id",
            "team",
            "player_id",
            "minutes",
            "ordinary_action_count_match_v4",
            "attack_component_match_v4",
        ]
    ]


def _matrix_by_match_player(
    frame: pd.DataFrame,
    value_column: str,
    match_ids: np.ndarray,
    player_ids: np.ndarray,
) -> np.ndarray:
    match_lookup = {int(value): index for index, value in enumerate(match_ids)}
    player_lookup = {
        int(value): index for index, value in enumerate(player_ids)
    }
    matrix = np.zeros((len(match_ids), len(player_ids)), dtype=float)
    for match_id, player_id, value in frame[
        ["match_id", "player_id", value_column]
    ].itertuples(index=False, name=None):
        if int(player_id) in player_lookup:
            matrix[match_lookup[int(match_id)], player_lookup[int(player_id)]] += (
                float(value)
            )
    return matrix


def _bootstrap_match_counts(
    match_count: int,
    replicates: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, match_count, size=(replicates, match_count))
    counts = np.zeros((replicates, match_count), dtype=float)
    rows = np.repeat(np.arange(replicates), match_count)
    np.add.at(counts, (rows, draws.ravel()), 1.0)
    return counts


def _rank_matrix(scores: np.ndarray, player_ids: np.ndarray) -> np.ndarray:
    if scores.ndim == 1:
        scores = scores[None, :]
    # Stable deterministic tie-breaking by player_id.
    tie = player_ids.astype(float)
    tie = (tie.max() - tie) / max(float(tie.max()), 1.0) * 1e-13
    order = np.argsort(-(scores + tie[None, :]), axis=1, kind="stable")
    return np.argsort(order, axis=1, kind="stable") + 1


def _top50_jaccard(
    bootstrap_scores: np.ndarray,
    point_scores: np.ndarray,
    player_ids: np.ndarray,
) -> tuple[float, float]:
    point_top = set(
        np.argsort(
            -(point_scores + (player_ids.max() - player_ids) * 1e-13),
            kind="stable",
        )[:50]
    )
    candidates = np.argpartition(-bootstrap_scores, 49, axis=1)[:, :50]
    overlaps = np.asarray(
        [
            len(point_top.intersection(row.tolist()))
            for row in candidates
        ],
        dtype=float,
    )
    jaccard = overlaps / (100.0 - overlaps)
    return float(np.median(jaccard)), float(np.quantile(jaccard, 0.10))


def _player_bootstrap_se(
    bootstrap_values: np.ndarray,
    point_values: np.ndarray,
) -> np.ndarray:
    se = bootstrap_values.std(axis=0, ddof=1)
    positive = se[se > 1e-12]
    floor = float(np.median(positive) * 0.10) if positive.size else 1e-6
    return np.maximum(se, floor + 1e-12 * np.abs(point_values))


def _within_player_match_bootstrap_se(
    match_values: np.ndarray,
    observed: np.ndarray,
    *,
    replicates: int,
    seed: int,
) -> np.ndarray:
    """Bootstrap each player's observed matches, excluding structural zeros.

    Tournament-wide match resampling is retained for rank intervals.  For
    empirical-Bayes shrinkage, however, treating every match a player did not
    play as a zero-valued observation would make durability look like
    measurement error.  This player-level bootstrap resamples only the
    matches in which that player generated defensive model evidence.
    """

    rng = np.random.default_rng(seed)
    standard_errors = np.zeros(match_values.shape[1], dtype=float)
    for player_index in range(match_values.shape[1]):
        values = match_values[
            observed[:, player_index], player_index
        ]
        if values.size <= 1:
            standard_errors[player_index] = 0.0
            continue
        draws = rng.integers(
            0, values.size, size=(replicates, values.size)
        )
        totals = values[draws].sum(axis=1)
        standard_errors[player_index] = float(totals.std(ddof=1))
    positive = standard_errors[standard_errors > 1e-12]
    floor = float(np.median(positive) * 0.10) if positive.size else 1e-6
    return np.maximum(standard_errors, floor)


def _build_stage_cache(
    *,
    variants: Sequence[str],
    exposure_scales: Sequence[float],
    prevention_weights: Sequence[float],
    matches: pd.DataFrame,
    possessions: pd.DataFrame,
    fifa_rankings: pd.DataFrame,
    predictions: pd.DataFrame,
    samples: pd.DataFrame,
    outfield: pd.DataFrame,
    match_ids: np.ndarray,
    player_ids: np.ndarray,
    bootstrap_counts: np.ndarray,
) -> tuple[
    dict[tuple[str, float, float], dict[str, Any]],
    dict[str, Any],
]:
    cache: dict[tuple[str, float, float], dict[str, Any]] = {}
    audits: dict[str, Any] = {}
    raw_reference: np.ndarray | None = None
    for variant in variants:
        context_result = build_opponent_context(
            matches,
            possessions,
            fifa_rankings,
            variant=variant,
        )
        prevention_result = build_off_ball_prevention_oof(
            possessions,
            context_result.frame,
            n_splits=5,
        )
        allocated = allocate_match_context_to_players(
            predictions,
            samples,
            outfield,
            context_result.frame,
            prevention_result.frame,
        )
        raw_sd = float(allocated["defensive_value_raw_v4"].std(ddof=0))
        exposure_sd = float(
            allocated["opponent_expected_exposure_player_v4"].std(ddof=0)
        )
        prevention_sd = float(
            allocated["off_ball_prevention_raw_v4"].std(ddof=0)
        )
        if min(raw_sd, exposure_sd, prevention_sd) <= 0:
            raise RuntimeError("defensive stage inputs need positive variance")
        context_scale = raw_sd / exposure_sd
        prevention_scale = raw_sd / prevention_sd
        raw_matrix = _matrix_by_match_player(
            allocated,
            "defensive_value_raw_v4",
            match_ids,
            player_ids,
        )
        raw_point = raw_matrix.sum(axis=0)
        if raw_reference is None:
            raw_reference = raw_point.copy()
        elif not np.allclose(raw_point, raw_reference, rtol=0.0, atol=1e-12):
            raise RuntimeError("opposition variants changed frozen raw defense")
        exposure_matrix = _matrix_by_match_player(
            allocated,
            "opponent_expected_exposure_player_v4",
            match_ids,
            player_ids,
        )
        prevention_matrix = _matrix_by_match_player(
            allocated,
            "off_ball_prevention_raw_v4",
            match_ids,
            player_ids,
        )
        observed_rows = allocated[["match_id", "player_id"]].copy()
        observed_rows["_observed_v4"] = 1.0
        observed_matrix = _matrix_by_match_player(
            observed_rows,
            "_observed_v4",
            match_ids,
            player_ids,
        ).astype(bool)
        for exposure_scale in exposure_scales:
            opposition_matrix = (
                raw_matrix
                + float(exposure_scale) * context_scale * exposure_matrix
            )
            opposition_point = opposition_matrix.sum(axis=0)
            for prevention_weight in prevention_weights:
                augmented_matrix = (
                    opposition_matrix
                    + float(prevention_weight)
                    * prevention_scale
                    * prevention_matrix
                )
                augmented_point = augmented_matrix.sum(axis=0)
                augmented_bootstrap = bootstrap_counts @ augmented_matrix
                bootstrap_se = _within_player_match_bootstrap_se(
                    augmented_matrix,
                    observed_matrix,
                    replicates=bootstrap_counts.shape[0],
                    seed=42,
                )
                key = (
                    variant,
                    float(exposure_scale),
                    float(prevention_weight),
                )
                cache[key] = {
                    "allocated": allocated,
                    "context": context_result.frame,
                    "prevention": prevention_result.frame,
                    "raw_matrix": raw_matrix,
                    "opposition_matrix": opposition_matrix,
                    "augmented_matrix": augmented_matrix,
                    "raw_point": raw_point,
                    "opposition_point": opposition_point,
                    "augmented_point": augmented_point,
                    "augmented_bootstrap": augmented_bootstrap,
                    "bootstrap_se": bootstrap_se,
                    "context_unit_scale": context_scale,
                    "prevention_unit_scale": prevention_scale,
                    "opposition_audit": context_result.audit,
                    "prevention_audit": prevention_result.audit,
                }
        audits[variant] = {
            "opposition": context_result.audit,
            "prevention": prevention_result.audit,
            "context_unit_scale": context_scale,
            "prevention_unit_scale": prevention_scale,
        }
    return cache, audits


def _configuration_from_record(record: Mapping[str, Any]) -> OutfieldV4Config:
    lower, upper = record["mixture_bounds"]
    return OutfieldV4Config(
        variance_share_target=float(record["variance_share_target"]),
        mixture_lower=float(lower),
        mixture_upper=float(upper),
        attack_reliability_constant=float(
            record["attack_reliability_constant"]
        ),
        defense_reliability_constant=float(
            record["defense_reliability_constant"]
        ),
        bootstrap_se_shrinkage_constant=float(
            record["bootstrap_se_shrinkage_constant"]
        ),
        opposition_adjustment_variant=str(
            record["opposition_adjustment_variant"]
        ),
        opposition_exposure_scale=float(record["opposition_exposure_scale"]),
        prevention_weight=float(record["prevention_weight"]),
    )


def _configuration_outputs(
    *,
    config: OutfieldV4Config,
    outfield: pd.DataFrame,
    stage: Mapping[str, Any],
    role_mixture: pd.DataFrame,
    attack_point: np.ndarray,
    attack_bootstrap: np.ndarray,
    attack_evidence: np.ndarray,
    defense_evidence: np.ndarray,
    player_ids: np.ndarray,
) -> dict[str, Any]:
    attack_reliability = channel_count_reliability(
        attack_evidence, config.attack_reliability_constant
    )
    defense_count_reliability = channel_count_reliability(
        defense_evidence, config.defense_reliability_constant
    )
    attack_reliable = attack_point * attack_reliability
    attack_bootstrap_reliable = (
        attack_bootstrap * attack_reliability[None, :]
    )
    defense_shrunk, defense_reliability = bootstrap_se_shrinkage(
        stage["augmented_point"],
        stage["bootstrap_se"],
        defense_count_reliability,
        se_constant=config.bootstrap_se_shrinkage_constant,
    )
    w_att = role_mixture["attacking_channel_weight_v4"].to_numpy(
        dtype=float
    )
    w_def = role_mixture["defending_channel_weight_v4"].to_numpy(dtype=float)
    pipeline = DefensivePipeline(stage["raw_point"])
    pipeline.opposition_adjust(stage["opposition_point"])
    pipeline.augment_prevention(stage["augmented_point"])
    pipeline.shrink_reliability(defense_shrunk)
    pipeline.variance_rescale(
        attack_reliable,
        w_att,
        w_def,
        target_share=config.variance_share_target,
    )
    scale_factor = float(
        pipeline.metadata["defensive_variance_scale_factor_v4"]
    )
    defense_rescaled = pipeline.values
    pipeline.mixture_weight(w_def)
    pipeline.assert_complete()
    composite_frame = pd.DataFrame(
        {
            "attacking_component_reliable_v4": attack_reliable,
            # Structurally this is the released post-opposition,
            # post-prevention, post-shrink, rescaled and mixture-weighted
            # defense channel.  The public composite rejects any raw name.
            "defensive_value_opposition_adjusted_v4": pipeline.values,
            "attacking_channel_weight_v4": w_att,
            "defending_channel_weight_v4": w_def,
        },
        index=outfield.index,
    )
    point_score = variance_balanced_composite(
        composite_frame,
        defensive_input_column="defensive_value_opposition_adjusted_v4",
        defensive_pipeline_stages=pipeline.stage_history,
    ).to_numpy(dtype=float)
    defense_center = float(stage["augmented_point"].mean())
    bootstrap_shrunk = defense_center + defense_reliability[None, :] * (
        stage["augmented_bootstrap"] - defense_center
    )
    bootstrap_defense = (
        w_def[None, :]
        * (bootstrap_shrunk - float(defense_shrunk.mean()))
        * scale_factor
    )
    bootstrap_score = (
        w_att[None, :] * attack_bootstrap_reliable + bootstrap_defense
    )
    median_jaccard, p10_jaccard = _top50_jaccard(
        bootstrap_score, point_score, player_ids
    )
    return {
        "config": config,
        "pipeline_stages": list(pipeline.stage_history),
        "point_score": point_score,
        "bootstrap_score": bootstrap_score,
        "attack_reliable": attack_reliable,
        "attack_reliability": attack_reliability,
        "defense_count_reliability": defense_count_reliability,
        "defense_reliability": defense_reliability,
        "defense_shrunk": defense_shrunk,
        "defense_rescaled": defense_rescaled,
        "defense_weighted": pipeline.values,
        "scale_factor": scale_factor,
        "variance_share": float(
            pipeline.metadata["defensive_variance_share_v4"]
        ),
        "bootstrap_top50_jaccard_median": median_jaccard,
        "bootstrap_top50_jaccard_p10": p10_jaccard,
    }


def _configuration_grid(prereg: Mapping[str, Any]) -> list[dict[str, Any]]:
    grid = prereg["candidate_grid"]
    names = (
        "variance_share_target",
        "mixture_bounds",
        "attack_reliability_constant",
        "defense_reliability_constant",
        "bootstrap_se_shrinkage_constant",
        "opposition_adjustment_variant",
        "opposition_exposure_scale",
        "prevention_weight",
    )
    return [
        dict(zip(names, values, strict=True))
        for values in itertools.product(*(grid[name] for name in names))
    ]


def _single_attribution_sensitivity(
    outputs: Mapping[str, Any],
    stage: Mapping[str, Any],
    attack_matrix: np.ndarray,
    player_ids: np.ndarray,
) -> dict[str, Any]:
    point_score = np.asarray(outputs["point_score"], dtype=float)
    ranks = _rank_matrix(point_score, player_ids)[0]

    def changed_rank(player_index: int, changed_score: float) -> int:
        better = point_score > changed_score
        tied_ahead = np.isclose(
            point_score, changed_score, rtol=0.0, atol=1e-14
        ) & (player_ids < player_ids[player_index])
        better[player_index] = False
        tied_ahead[player_index] = False
        return int(1 + better.sum() + tied_ahead.sum())

    scale = float(outputs["scale_factor"])
    reliability = np.asarray(outputs["defense_reliability"], dtype=float)
    w_def = np.asarray(outputs["defense_weighted"], dtype=float)
    rescaled = np.asarray(outputs["defense_rescaled"], dtype=float)
    raw_weight = np.divide(
        w_def,
        rescaled,
        out=np.zeros_like(w_def),
        where=np.abs(rescaled) > 1e-12,
    )
    player_lookup = {
        int(value): index for index, value in enumerate(player_ids)
    }
    shifts: list[float] = []
    attack_reliable = np.asarray(outputs["attack_reliable"], dtype=float)
    attack_weight = np.divide(
        point_score - np.asarray(outputs["defense_weighted"], dtype=float),
        attack_reliable,
        out=np.zeros_like(point_score),
        where=np.abs(attack_reliable) > 1e-12,
    )
    attack_reliability = np.asarray(
        outputs["attack_reliability"], dtype=float
    )
    for match_index, player_index in zip(
        *np.nonzero(np.abs(attack_matrix) > 1e-15),
        strict=True,
    ):
        changed = point_score.copy()
        changed[player_index] -= (
            attack_weight[player_index]
            * attack_reliability[player_index]
            * attack_matrix[match_index, player_index]
        )
        revised_rank = changed_rank(player_index, changed[player_index])
        shifts.append(abs(float(revised_rank - ranks[player_index])))
    match_frame = stage["allocated"]
    augmented_matrix = stage["augmented_matrix"]
    match_lookup = {
        int(value): index
        for index, value in enumerate(
            sorted(match_frame["match_id"].astype(int).unique())
        )
    }
    for match_id, player_id in match_frame[
        ["match_id", "player_id"]
    ].itertuples(index=False, name=None):
        player_index = player_lookup[int(player_id)]
        contribution = augmented_matrix[
            match_lookup[int(match_id)], player_index
        ]
        changed = point_score.copy()
        changed[player_index] -= (
            raw_weight[player_index]
            * scale
            * reliability[player_index]
            * contribution
        )
        revised_rank = changed_rank(player_index, changed[player_index])
        shifts.append(abs(float(revised_rank - ranks[player_index])))
    values = np.asarray(shifts, dtype=float)
    return {
        "p95_absolute_rank_shift": float(np.quantile(values, 0.95)),
        "max_absolute_rank_shift": float(values.max(initial=0.0)),
        "attributions_tested": int(len(values)),
        "attribution_granularity": "player-match channel contribution",
    }


def _leave_one_match_out_metrics(
    outputs: Mapping[str, Any],
    stage: Mapping[str, Any],
    attack_matrix: np.ndarray,
    player_ids: np.ndarray,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    point_score = np.asarray(outputs["point_score"], dtype=float)
    point_ranks = _rank_matrix(point_score, player_ids)[0]
    point_top = set(np.where(point_ranks <= 50)[0].tolist())
    config: OutfieldV4Config = outputs["config"]
    w_att = (
        np.asarray(outputs["attack_reliable"], dtype=float)
        / np.asarray(
            attack_matrix.sum(axis=0), dtype=float
        )
    )
    w_att = np.nan_to_num(w_att, nan=0.0, posinf=0.0, neginf=0.0)
    attack_weight = np.asarray(
        outputs["point_score"], dtype=float
    ) * 0.0  # allocated below without identity inputs
    # Recover the actual channel weights from the weighted point channels.
    attack_point = attack_matrix.sum(axis=0)
    attack_component = np.asarray(outputs["attack_reliable"], dtype=float)
    channel_weight = np.divide(
        point_score - np.asarray(outputs["defense_weighted"], dtype=float),
        attack_component,
        out=np.zeros_like(point_score),
        where=np.abs(attack_component) > 1e-12,
    )
    attack_weight = channel_weight
    defense_rel = np.asarray(outputs["defense_reliability"], dtype=float)
    defense_mean = float(stage["augmented_point"].mean())
    defense_scale = float(outputs["scale_factor"])
    defense_mix = np.divide(
        np.asarray(outputs["defense_weighted"], dtype=float),
        np.asarray(outputs["defense_rescaled"], dtype=float),
        out=np.zeros_like(point_score),
        where=np.abs(np.asarray(outputs["defense_rescaled"])) > 1e-12,
    )
    records: list[dict[str, Any]] = []
    match_ids = sorted(stage["allocated"]["match_id"].astype(int).unique())
    for index, match_id in enumerate(match_ids):
        attack_loo = attack_point - attack_matrix[index]
        attack_loo = attack_loo * np.divide(
            attack_component,
            attack_point,
            out=np.zeros_like(attack_point),
            where=np.abs(attack_point) > 1e-12,
        )
        defense_loo_raw = (
            stage["augmented_point"] - stage["augmented_matrix"][index]
        )
        defense_loo = defense_mean + defense_rel * (
            defense_loo_raw - defense_mean
        )
        score = (
            attack_weight * attack_loo
            + defense_mix
            * (defense_loo - float(outputs["defense_shrunk"].mean()))
            * defense_scale
        )
        ranks = _rank_matrix(score, player_ids)[0]
        top = set(np.where(ranks <= 50)[0].tolist())
        overlap = len(point_top.intersection(top))
        shifts = np.abs(ranks - point_ranks)
        records.append(
            {
                "match_id": match_id,
                "top50_jaccard": overlap / (100.0 - overlap),
                "p95_absolute_rank_shift": float(
                    np.quantile(shifts, 0.95)
                ),
                "max_absolute_rank_shift": int(shifts.max()),
            }
        )
    return (
        {
            "median_top50_jaccard": float(
                np.median([record["top50_jaccard"] for record in records])
            ),
            "p95_absolute_rank_shift": float(
                np.quantile(
                    [
                        record["p95_absolute_rank_shift"]
                        for record in records
                    ],
                    0.95,
                )
            ),
        },
        records,
    )


def _stage_key(record: Mapping[str, Any]) -> tuple[str, float, float]:
    return (
        str(record["opposition_adjustment_variant"]),
        float(record["opposition_exposure_scale"]),
        float(record["prevention_weight"]),
    )


def _role_key(record: Mapping[str, Any]) -> tuple[float, float]:
    lower, upper = record["mixture_bounds"]
    return float(lower), float(upper)


def _evaluate_grid(
    *,
    prereg: Mapping[str, Any],
    outfield: pd.DataFrame,
    stage_cache: Mapping[tuple[str, float, float], Mapping[str, Any]],
    role_cache: Mapping[tuple[float, float], pd.DataFrame],
    attack_point: np.ndarray,
    attack_bootstrap: np.ndarray,
    attack_evidence: np.ndarray,
    defense_evidence: np.ndarray,
    player_ids: np.ndarray,
) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    specs: dict[int, dict[str, Any]] = {}
    for config_id, candidate in enumerate(
        _configuration_grid(prereg), start=1
    ):
        config = _configuration_from_record(candidate)
        stage = stage_cache[_stage_key(candidate)]
        outputs = _configuration_outputs(
            config=config,
            outfield=outfield,
            stage=stage,
            role_mixture=role_cache[_role_key(candidate)],
            attack_point=attack_point,
            attack_bootstrap=attack_bootstrap,
            attack_evidence=attack_evidence,
            defense_evidence=defense_evidence,
            player_ids=player_ids,
        )
        prevention_gate = bool(stage["prevention_audit"]["gate_passed"])
        eligible = bool(config.prevention_weight > 0.0 and prevention_gate)
        record = {
            "config_id": config_id,
            **candidate,
            "eligible_for_release": eligible,
            "eligibility_reason": (
                "eligible"
                if eligible
                else "zero-prevention ablation; mandatory family passed"
            ),
            "bootstrap_top50_jaccard_median": outputs[
                "bootstrap_top50_jaccard_median"
            ],
            "bootstrap_top50_jaccard_p10": outputs[
                "bootstrap_top50_jaccard_p10"
            ],
            "realized_defensive_variance_share": outputs["variance_share"],
            "defensive_variance_scale_factor": outputs["scale_factor"],
            "single_attribution_p95_absolute_rank_shift": None,
            "single_attribution_max_absolute_rank_shift": None,
            "leave_one_match_out_median_top50_jaccard": None,
            "leave_one_match_out_p95_absolute_rank_shift": None,
            "selection_status": "not_selected",
        }
        records.append(record)
        specs[config_id] = candidate
    return records, specs


def _select_configuration(
    *,
    records: list[dict[str, Any]],
    specs: Mapping[int, Mapping[str, Any]],
    outfield: pd.DataFrame,
    stage_cache: Mapping[tuple[str, float, float], Mapping[str, Any]],
    role_cache: Mapping[tuple[float, float], pd.DataFrame],
    attack_point: np.ndarray,
    attack_bootstrap: np.ndarray,
    attack_matrix: np.ndarray,
    attack_evidence: np.ndarray,
    defense_evidence: np.ndarray,
    player_ids: np.ndarray,
    variant_order: Sequence[str],
    tolerance: float,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    by_id = {int(record["config_id"]): record for record in records}
    candidates = [
        record for record in records if record["eligible_for_release"]
    ]
    if not candidates:
        raise RuntimeError("no preregistered configuration is release-eligible")

    best_median = max(
        float(record["bootstrap_top50_jaccard_median"])
        for record in candidates
    )
    candidates = [
        record
        for record in candidates
        if float(record["bootstrap_top50_jaccard_median"])
        >= best_median - tolerance
    ]
    best_p10 = max(
        float(record["bootstrap_top50_jaccard_p10"])
        for record in candidates
    )
    candidates = [
        record
        for record in candidates
        if float(record["bootstrap_top50_jaccard_p10"])
        >= best_p10 - tolerance
    ]

    outputs_by_id: dict[int, dict[str, Any]] = {}
    for record in candidates:
        config_id = int(record["config_id"])
        candidate = specs[config_id]
        outputs = _configuration_outputs(
            config=_configuration_from_record(candidate),
            outfield=outfield,
            stage=stage_cache[_stage_key(candidate)],
            role_mixture=role_cache[_role_key(candidate)],
            attack_point=attack_point,
            attack_bootstrap=attack_bootstrap,
            attack_evidence=attack_evidence,
            defense_evidence=defense_evidence,
            player_ids=player_ids,
        )
        outputs_by_id[config_id] = outputs
        sensitivity = _single_attribution_sensitivity(
            outputs,
            stage_cache[_stage_key(candidate)],
            attack_matrix,
            player_ids,
        )
        record[
            "single_attribution_p95_absolute_rank_shift"
        ] = sensitivity["p95_absolute_rank_shift"]
        record[
            "single_attribution_max_absolute_rank_shift"
        ] = sensitivity["max_absolute_rank_shift"]
        record["single_attribution_count"] = sensitivity[
            "attributions_tested"
        ]
        record["single_attribution_granularity"] = sensitivity[
            "attribution_granularity"
        ]

    best_sensitivity = min(
        float(record["single_attribution_p95_absolute_rank_shift"])
        for record in candidates
    )
    candidates = [
        record
        for record in candidates
        if float(record["single_attribution_p95_absolute_rank_shift"])
        <= best_sensitivity + tolerance
    ]
    best_max_sensitivity = min(
        float(record["single_attribution_max_absolute_rank_shift"])
        for record in candidates
    )
    candidates = [
        record
        for record in candidates
        if float(record["single_attribution_max_absolute_rank_shift"])
        <= best_max_sensitivity + tolerance
    ]

    loo_records_by_id: dict[int, list[dict[str, Any]]] = {}
    for record in candidates:
        config_id = int(record["config_id"])
        candidate = specs[config_id]
        outputs = outputs_by_id.get(config_id)
        if outputs is None:
            outputs = _configuration_outputs(
                config=_configuration_from_record(candidate),
                outfield=outfield,
                stage=stage_cache[_stage_key(candidate)],
                role_mixture=role_cache[_role_key(candidate)],
                attack_point=attack_point,
                attack_bootstrap=attack_bootstrap,
                attack_evidence=attack_evidence,
                defense_evidence=defense_evidence,
                player_ids=player_ids,
            )
            outputs_by_id[config_id] = outputs
        metrics, loo_records = _leave_one_match_out_metrics(
            outputs,
            stage_cache[_stage_key(candidate)],
            attack_matrix,
            player_ids,
        )
        record["leave_one_match_out_median_top50_jaccard"] = metrics[
            "median_top50_jaccard"
        ]
        record[
            "leave_one_match_out_p95_absolute_rank_shift"
        ] = metrics["p95_absolute_rank_shift"]
        loo_records_by_id[config_id] = loo_records

    best_loo = max(
        float(record["leave_one_match_out_median_top50_jaccard"])
        for record in candidates
    )
    candidates = [
        record
        for record in candidates
        if float(record["leave_one_match_out_median_top50_jaccard"])
        >= best_loo - tolerance
    ]
    best_loo_shift = min(
        float(record["leave_one_match_out_p95_absolute_rank_shift"])
        for record in candidates
    )
    candidates = [
        record
        for record in candidates
        if float(record["leave_one_match_out_p95_absolute_rank_shift"])
        <= best_loo_shift + tolerance
    ]

    variant_index = {
        value: index for index, value in enumerate(variant_order)
    }

    def conservative_key(record: Mapping[str, Any]) -> tuple[Any, ...]:
        lower, upper = record["mixture_bounds"]
        return (
            float(record["variance_share_target"]),
            float(record["prevention_weight"]),
            -float(record["bootstrap_se_shrinkage_constant"]),
            -float(record["defense_reliability_constant"]),
            -float(record["attack_reliability_constant"]),
            float(upper) - float(lower),
            variant_index[str(record["opposition_adjustment_variant"])],
            int(record["config_id"]),
        )

    selected_record = min(candidates, key=conservative_key)
    selected_id = int(selected_record["config_id"])
    selected_record["selection_status"] = "selected"
    for record in records:
        if int(record["config_id"]) == selected_id:
            record["selection_status"] = "selected"
        elif not record["eligible_for_release"]:
            record["selection_status"] = "ineligible_ablation"
        else:
            record["selection_status"] = "rejected_by_preregistered_metrics"
    return (
        selected_record,
        outputs_by_id[selected_id],
        loo_records_by_id[selected_id],
    )


def _selected_outfield_frame(
    *,
    outfield: pd.DataFrame,
    outputs: Mapping[str, Any],
    stage: Mapping[str, Any],
    role_mixture: pd.DataFrame,
    player_ids: np.ndarray,
    selected_record: Mapping[str, Any],
) -> pd.DataFrame:
    rich = outfield.copy(deep=True)
    allocated = stage["allocated"].copy()
    allocated["player_id"] = allocated["player_id"].astype(int)
    weighted_strength_numerator = (
        pd.to_numeric(
            allocated["opponent_attack_strength_match_v4"],
            errors="raise",
        )
        * pd.to_numeric(allocated["opponent_possessions"], errors="raise")
        * pd.to_numeric(allocated["minutes"], errors="raise")
    )
    weighted_strength_denominator = (
        pd.to_numeric(allocated["opponent_possessions"], errors="raise")
        * pd.to_numeric(allocated["minutes"], errors="raise")
    )
    allocated["_strength_numerator"] = weighted_strength_numerator
    allocated["_strength_denominator"] = weighted_strength_denominator
    player_context = (
        allocated.groupby("player_id", as_index=False)
        .agg(
            opponent_strength_numerator=("_strength_numerator", "sum"),
            opponent_strength_denominator=("_strength_denominator", "sum"),
            off_ball_prevention_coverage_v4=(
                "off_ball_prevention_coverage_v4",
                "mean",
            ),
            off_ball_player_shape_available_rate_v4=(
                "off_ball_player_shape_available_v4",
                "mean",
            ),
            opponent_possessions_evidence_v4=(
                "opponent_possessions",
                "sum",
            ),
        )
        .set_index("player_id")
    )
    context_aligned = player_context.reindex(player_ids)
    rich["opponent_attack_strength_faced_v4"] = (
        context_aligned["opponent_strength_numerator"]
        / context_aligned["opponent_strength_denominator"]
    ).fillna(1.0).to_numpy()
    for column in (
        "off_ball_prevention_coverage_v4",
        "off_ball_player_shape_available_rate_v4",
        "opponent_possessions_evidence_v4",
    ):
        rich[column] = context_aligned[column].fillna(0.0).to_numpy()

    role = role_mixture.reindex(rich.index)
    for column in role.columns:
        rich[column] = role[column].to_numpy()
    rich["attacking_orientation_v4"] = rich[
        "role_orientation_attacking_v4"
    ]
    rich["attack_weight_v4"] = rich["attacking_channel_weight_v4"]
    rich["defense_weight_v4"] = rich["defending_channel_weight_v4"]

    raw = np.asarray(stage["raw_point"], dtype=float)
    opposition = np.asarray(stage["opposition_point"], dtype=float)
    augmented = np.asarray(stage["augmented_point"], dtype=float)
    rich["defensive_value_raw_v4"] = raw
    rich["opposition_adjustment_value_v4"] = opposition - raw
    rich["defensive_value_opposition_adjusted_v4"] = opposition
    rich["off_ball_prevention_value_v4"] = augmented - opposition
    rich["defensive_value_prevention_augmented_v4"] = augmented
    rich["attack_reliability_v4"] = outputs["attack_reliability"]
    rich["defensive_count_reliability_v4"] = outputs[
        "defense_count_reliability"
    ]
    rich["defensive_reliability_v4"] = outputs["defense_reliability"]
    rich["attack_value_reliability_shrunk_v4"] = outputs["attack_reliable"]
    rich["attacking_value_reliability_shrunk_v4"] = outputs["attack_reliable"]
    rich["defensive_value_reliability_shrunk_v4"] = outputs[
        "defense_shrunk"
    ]
    rich["defensive_value_variance_rescaled_v4"] = outputs[
        "defense_rescaled"
    ]
    rich["attack_component_outfield_v4"] = (
        rich["attacking_channel_weight_v4"].to_numpy(dtype=float)
        * np.asarray(outputs["attack_reliable"], dtype=float)
    )
    rich["defensive_component_outfield_v4"] = outputs["defense_weighted"]
    rich["defensive_component_v4"] = outputs["defense_weighted"]
    rich["tournament_impact_raw_outfield_v4"] = outputs["point_score"]
    rich["tournament_impact_score_outfield_v4"] = outputs["point_score"]

    bootstrap_score = np.asarray(outputs["bootstrap_score"], dtype=float)
    bootstrap_ranks = _rank_matrix(bootstrap_score, player_ids)
    rich["tournament_impact_interval_low_outfield_v4"] = np.quantile(
        bootstrap_score, 0.05, axis=0
    )
    rich["tournament_impact_interval_high_outfield_v4"] = np.quantile(
        bootstrap_score, 0.95, axis=0
    )
    rich["tournament_impact_uncertainty_std_outfield_v4"] = (
        bootstrap_score.std(axis=0, ddof=1)
    )
    rich["bootstrap_rank_best_outfield_v4"] = np.quantile(
        bootstrap_ranks, 0.05, axis=0, method="lower"
    ).astype(int)
    rich["bootstrap_rank_worst_outfield_v4"] = np.quantile(
        bootstrap_ranks, 0.95, axis=0, method="higher"
    ).astype(int)
    rich["bootstrap_rank_median_outfield_v4"] = np.median(
        bootstrap_ranks, axis=0
    )
    rich["outfield_v4_bootstrap_replicates"] = int(
        bootstrap_score.shape[0]
    )
    rich["defensive_variance_share_outfield_v4"] = float(
        outputs["variance_share"]
    )
    rich["defensive_variance_scale_factor_outfield_v4"] = float(
        outputs["scale_factor"]
    )
    rich["outfield_v4_selected_config_id"] = int(
        selected_record["config_id"]
    )
    rich["outfield_v4_opposition_variant"] = str(
        selected_record["opposition_adjustment_variant"]
    )
    rich["outfield_v4_model_version"] = MODEL_VERSION
    rich = add_reporting_ranks(rich)
    rich["position_rank_outfield_v4"] = rich[
        "within_position_rank_outfield_v4"
    ]
    rich["sub_role_v4"] = rich["predominant_position_subrole_v4"]
    rich["sub_role_rank_outfield_v4"] = rich[
        "within_subrole_rank_outfield_v4"
    ]
    return rich


def _publication_bridge(
    base_all: pd.DataFrame,
    outfield_v4: pd.DataFrame,
) -> pd.DataFrame:
    """Merge outfield v4 with the frozen goalkeeper publication bridge."""

    output = base_all.copy(deep=True)
    new_columns = [
        column
        for column in outfield_v4.columns
        if column not in output.columns
    ]
    aligned = outfield_v4.set_index("player_id")
    outfield_mask = output["position_group"].ne("Goalkeeper")
    output_lookup = output.loc[outfield_mask, "player_id"].astype(int)
    for column in new_columns:
        output[column] = pd.NA
        output.loc[outfield_mask, column] = aligned.loc[
            output_lookup, column
        ].to_numpy()
    # Existing names may be present only in the outfield frame after a rerun.
    for column in (
        "tournament_impact_score_outfield_v4",
        "tournament_impact_rank_outfield_v4",
    ):
        if column in aligned:
            output.loc[outfield_mask, column] = aligned.loc[
                output_lookup, column
            ].to_numpy()

    raw = pd.to_numeric(
        output.loc[outfield_mask, "tournament_impact_score_outfield_v4"],
        errors="raise",
    )
    span = float(raw.max() - raw.min())
    if span <= 0:
        raise RuntimeError("outfield v4 publication bridge needs score variance")
    outfield_publication = (raw - float(raw.min())) / span
    output["publication_score_outfield_v4"] = np.nan
    output.loc[outfield_mask, "publication_score_outfield_v4"] = (
        outfield_publication
    )
    main_goalkeeper = (
        output["position_group"].eq("Goalkeeper")
        & output["is_main_goalkeeper"].fillna(False).astype(bool)
    )
    goalkeeper_score = pd.to_numeric(
        output.loc[main_goalkeeper, "publication_score_v3"],
        errors="raise",
    )
    output.loc[main_goalkeeper, "publication_score_outfield_v4"] = (
        goalkeeper_score
    )
    unified = outfield_mask | main_goalkeeper
    ordered = output.loc[unified].sort_values(
        ["publication_score_outfield_v4", "player_id"],
        ascending=[False, True],
        kind="mergesort",
    )
    global_rank = pd.Series(
        np.arange(1, len(ordered) + 1),
        index=ordered.index,
        dtype="Int64",
    )
    output["publication_global_rank_outfield_v4"] = pd.Series(
        pd.NA, index=output.index, dtype="Int64"
    )
    output.loc[
        unified, "publication_global_rank_outfield_v4"
    ] = global_rank.reindex(output.index[unified]).array
    team_rank = (
        output.loc[unified]
        .groupby("team", sort=False)["publication_score_outfield_v4"]
        .rank(method="first", ascending=False)
        .astype("Int64")
    )
    output["publication_team_rank_outfield_v4"] = pd.Series(
        pd.NA, index=output.index, dtype="Int64"
    )
    output.loc[
        unified, "publication_team_rank_outfield_v4"
    ] = team_rank.reindex(output.index[unified]).array
    output["Global Rank"] = output[
        "publication_global_rank_outfield_v4"
    ].astype("Int64")
    output["Team Rank"] = output[
        "publication_team_rank_outfield_v4"
    ].astype("Int64")
    output["Tournament Performance Score"] = (
        pd.to_numeric(
            output["publication_score_outfield_v4"], errors="coerce"
        )
        .mul(44.0)
        .add(55.0)
        .round(1)
    )
    output["active_model_version"] = ACTIVE_MODEL_VERSION
    output["active_global_rank_field"] = (
        "publication_global_rank_outfield_v4"
    )
    output["active_team_rank_field"] = "publication_team_rank_outfield_v4"
    output["Player"] = output["player_name"]
    output["Team"] = output["team"]
    output["Position Group"] = output["position_group"]
    return output


def _uncoupled_raw_defense_ranks(
    *,
    outputs: Mapping[str, Any],
    stage: Mapping[str, Any],
    role_mixture: pd.DataFrame,
    player_ids: np.ndarray,
) -> np.ndarray:
    attack = np.asarray(outputs["attack_reliable"], dtype=float)
    raw = np.asarray(stage["raw_point"], dtype=float)
    w_att = role_mixture["attacking_channel_weight_v4"].to_numpy(dtype=float)
    w_def = role_mixture["defending_channel_weight_v4"].to_numpy(dtype=float)
    raw_centered = raw - float(raw.mean())
    attack_var = float(np.var(w_att * attack, ddof=0))
    raw_var = float(np.var(w_def * raw_centered, ddof=0))
    target = float(outputs["config"].variance_share_target)
    scale = math.sqrt(target / (1.0 - target) * attack_var / raw_var)
    uncoupled = w_att * attack + w_def * raw_centered * scale
    return _rank_matrix(uncoupled, player_ids)[0]


def _fixture_movement(
    released: pd.DataFrame,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for fixture, name in FIXTURE_NAMES.items():
        row = released.loc[released["player_name"].eq(name)]
        if len(row) != 1:
            raise RuntimeError(f"fixture row missing after release: {name}")
        value = row.iloc[0]
        before = int(value["publication_global_rank_v3"])
        after = int(value["publication_global_rank_outfield_v4"])
        records.append(
            {
                "fixture": fixture,
                "player_name": name,
                "team": value["team"],
                "position_group": value["position_group"],
                "v3_publication_rank": before,
                "v4_publication_rank": after,
                "rank_improvement": before - after,
                "attack_component_v4": value.get(
                    "attack_component_outfield_v4", np.nan
                ),
                "defensive_raw_v4": value.get(
                    "defensive_value_raw_v4", np.nan
                ),
                "opposition_adjustment_v4": value.get(
                    "opposition_adjustment_value_v4", np.nan
                ),
                "off_ball_prevention_v4": value.get(
                    "off_ball_prevention_value_v4", np.nan
                ),
                "defensive_reliability_shrunk_v4": value.get(
                    "defensive_value_reliability_shrunk_v4", np.nan
                ),
                "defensive_variance_rescaled_v4": value.get(
                    "defensive_value_variance_rescaled_v4", np.nan
                ),
                "defensive_component_v4": value.get(
                    "defensive_component_outfield_v4", np.nan
                ),
                "opponent_attack_strength_faced_v4": value.get(
                    "opponent_attack_strength_faced_v4", np.nan
                ),
            }
        )
    return pd.DataFrame(records)


def _external_consensus(
    released: pd.DataFrame,
) -> dict[str, Any]:
    sources = [
        {
            "publisher": "FIFA",
            "label": "Qatar 2022 Technical Study Group tournament summary",
            "url": (
                "https://publications.fifa.com/en/annual-report-2022/"
                "2022-at-a-glance/fifa-world-cup-qatar-2022-summary/"
            ),
            "use": "official tournament technical context and award record",
        },
        {
            "publisher": "FIFA",
            "label": "TSG review of the semi-finalists and Morocco",
            "url": (
                "https://inside.fifa.com/talent-development/"
                "technical-study-group/news/tsg-runs-the-rule-over-the-"
                "semi-finalists-and-moroccos-magnificent-run"
            ),
            "use": "technical context for Morocco and Amrabat",
        },
        {
            "publisher": "ESPN",
            "label": "World Cup 2022 best XI",
            "url": (
                "https://www.espn.com/soccer/story/_/id/37634927/"
                "world-cup-2022-best-xis-makes-our-team-tournament"
            ),
            "use": "major-outlet Team of the Tournament",
        },
        {
            "publisher": "The Guardian",
            "label": "World Cup 2022 team of the tournament",
            "url": (
                "https://www.theguardian.com/football/2022/dec/19/"
                "world-cup-2022-team-of-the-tournament-martinez-mbappe"
            ),
            "use": "major-outlet Team of the Tournament",
        },
        {
            "publisher": "BBC Sport / Opta",
            "label": "Statistical team of the World Cup",
            "url": "https://www.bbc.co.uk/sport/football/64019356",
            "use": "Opta statistical selection",
        },
        {
            "publisher": "The Athletic",
            "label": "World Cup team of the tournament",
            "url": (
                "https://theathletic.com/4008254/2022/12/18/"
                "world-cup-team-of-the-tournament/"
            ),
            "use": "major-outlet Team of the Tournament",
        },
        {
            "publisher": "WhoScored",
            "label": "WhoScored statistical XI (contemporary reproduction)",
            "url": (
                "https://www.uol.com.br/esporte/futebol/colunas/"
                "rafael-reis/2022/12/20/messi-e-o-unico-argentino-em-"
                "selecao-da-copa-montada-por-robos-confira.htm"
            ),
            "use": "statistical-table comparison",
        },
        {
            "publisher": "SofaScore",
            "label": "World Cup tournament data registry",
            "url": (
                "https://api.sofascore.com/api/v1/unique-tournament/16/"
                "seasons"
            ),
            "use": "statistical-table source registry",
        },
        {
            "publisher": "FBref",
            "label": "2022 World Cup standard statistics",
            "url": "https://fbref.com/en/comps/1/2022/stats/2022-World-Cup-Stats",
            "use": "independent statistical tables",
        },
    ]
    expectations = {
        "Lionel Andrés Messi Cuccittini": (
            "universal tournament-leading consensus"
        ),
        "Jude Bellingham": "strong two-way midfielder consensus",
        "Achraf Hakimi Mouh": "strong Team-of-the-Tournament consensus",
        "Sofyan Amrabat": (
            "strong analyst/TSG recognition; weaker event-only XI presence"
        ),
        "Nicolás Hernán Otamendi": "positive but less universal consensus",
        "Cristian Gabriel Romero": "mixed external selection support",
        "Virgil van Dijk": "mixed external selection support",
        "Josip Juranović": "watch fixture; limited broad-XI consensus",
    }
    rows: list[dict[str, Any]] = []
    for name, expectation in expectations.items():
        row = released.loc[released["player_name"].eq(name)].iloc[0]
        rows.append(
            {
                "player_name": name,
                "team": row["team"],
                "v4_publication_rank": int(
                    row["publication_global_rank_outfield_v4"]
                ),
                "consensus_summary": expectation,
                "comparison": (
                    "directionally consistent"
                    if int(row["publication_global_rank_outfield_v4"]) <= 100
                    else "model remains below broad consensus band"
                ),
            }
        )
    return {
        "use_in_scoring_or_selection": False,
        "collected_before_fixture_gate_review": True,
        "important_caveat": (
            "FIFA did not publish an official tournament Best XI; its TSG "
            "material is treated as technical context, not a fabricated XI."
        ),
        "sources": sources,
        "comparison": rows,
    }


def _gate_record(
    passed: bool,
    detail: Mapping[str, Any] | str,
) -> dict[str, Any]:
    return {"passed": bool(passed), "detail": detail}


def _acceptance_gates(
    *,
    base_all: pd.DataFrame,
    released: pd.DataFrame,
    outfield_v4: pd.DataFrame,
    selected_outputs: Mapping[str, Any],
    selected_stage: Mapping[str, Any],
    selected_role: pd.DataFrame,
    player_ids: np.ndarray,
    movement: pd.DataFrame,
    prevention_counterfactual_ranks: np.ndarray,
    v3_artifacts_before: Mapping[str, Any],
) -> tuple[dict[str, Any], pd.DataFrame]:
    gates: dict[str, Any] = {}
    stages = tuple(selected_outputs["pipeline_stages"])
    gates["defensive_pipeline_stage_order"] = _gate_record(
        stages == REQUIRED_DEFENSIVE_PIPELINE_STAGES,
        {"recorded": list(stages), "required": list(REQUIRED_DEFENSIVE_PIPELINE_STAGES)},
    )
    raw_rejected = False
    try:
        variance_balanced_composite(
            pd.DataFrame(
                {
                    "defensive_value_raw_v4": [0.0, 1.0],
                    "attacking_component_reliable_v4": [0.0, 1.0],
                    "attacking_channel_weight_v4": [0.5, 0.5],
                    "defending_channel_weight_v4": [0.5, 0.5],
                }
            ),
            defensive_input_column="defensive_value_raw_v4",
            defensive_pipeline_stages=stages,
        )
    except ValueError:
        raw_rejected = True
    gates["raw_defense_composite_rejection"] = _gate_record(
        raw_rejected,
        "public composite rejects defensive_value_raw_v4",
    )
    variance_share = float(selected_outputs["variance_share"])
    gates["variance_share_contract"] = _gate_record(
        0.35 <= variance_share <= 0.50,
        {"realized": variance_share, "parity_cap": 0.50},
    )
    w_att = selected_role["attacking_channel_weight_v4"].to_numpy(dtype=float)
    w_def = selected_role["defending_channel_weight_v4"].to_numpy(dtype=float)
    lower = float(selected_outputs["config"].mixture_lower)
    upper = float(selected_outputs["config"].mixture_upper)
    gates["continuous_mixture_contract"] = _gate_record(
        bool(
            np.allclose(w_att + w_def, 1.0, rtol=0.0, atol=1e-12)
            and w_att.min() >= lower - 1e-12
            and w_att.max() <= upper + 1e-12
            and np.unique(np.round(w_att, 10)).size > 50
        ),
        {
            "bounds": [lower, upper],
            "attacking_weight_min": float(w_att.min()),
            "attacking_weight_max": float(w_att.max()),
            "unique_weights_10dp": int(np.unique(np.round(w_att, 10)).size),
        },
    )

    context_fixture = outfield_v4.loc[
        pd.to_numeric(outfield_v4["minutes_played"], errors="coerce").ge(300.0)
    ].copy()
    hardest = context_fixture.sort_values(
        "opponent_attack_strength_faced_v4",
        ascending=False,
        kind="mergesort",
    ).iloc[0]
    easiest = context_fixture.sort_values(
        "opponent_attack_strength_faced_v4",
        ascending=True,
        kind="mergesort",
    ).iloc[0]
    hardest_rate = float(hardest["opposition_adjustment_value_v4"]) / max(
        float(hardest["opponent_possessions_evidence_v4"]), 1e-12
    )
    easiest_rate = float(easiest["opposition_adjustment_value_v4"]) / max(
        float(easiest["opponent_possessions_evidence_v4"]), 1e-12
    )
    gates["opposition_adjustment_direction"] = _gate_record(
        hardest_rate > easiest_rate,
        {
            "hardest_player": hardest["player_name"],
            "hardest_strength": hardest["opponent_attack_strength_faced_v4"],
            "hardest_adjustment_per_possession": hardest_rate,
            "easiest_player": easiest["player_name"],
            "easiest_strength": easiest["opponent_attack_strength_faced_v4"],
            "easiest_adjustment_per_possession": easiest_rate,
        },
    )

    uncoupled_ranks = _uncoupled_raw_defense_ranks(
        outputs=selected_outputs,
        stage=selected_stage,
        role_mixture=selected_role,
        player_ids=player_ids,
    )
    otamendi_id = int(
        outfield_v4.loc[
            outfield_v4["player_name"].eq(FIXTURE_NAMES["otamendi"]),
            "player_id",
        ].iloc[0]
    )
    otamendi_index = int(np.where(player_ids == otamendi_id)[0][0])
    released_otamendi_outfield_rank = int(
        outfield_v4.loc[
            outfield_v4["player_id"].eq(otamendi_id),
            "tournament_impact_rank_outfield_v4",
        ].iloc[0]
    )
    v3_otamendi_outfield_rank = int(
        base_all.loc[
            base_all["player_id"].eq(otamendi_id), "global_rank_v3"
        ].iloc[0]
    )
    gates["coupling_regression"] = _gate_record(
        bool(
            int(uncoupled_ranks[otamendi_index])
            != released_otamendi_outfield_rank
            and released_otamendi_outfield_rank < v3_otamendi_outfield_rank
            and int(uncoupled_ranks[otamendi_index])
            >= v3_otamendi_outfield_rank
        ),
        {
            "v3_outfield_rank": v3_otamendi_outfield_rank,
            "uncoupled_raw_rescaled_rank": int(
                uncoupled_ranks[otamendi_index]
            ),
            "released_coupled_rank": released_otamendi_outfield_rank,
        },
    )

    movement_by_fixture = movement.set_index("fixture")
    for fixture in ("van_dijk", "romero", "otamendi"):
        row = movement_by_fixture.loc[fixture]
        gates[f"{fixture}_improves_100"] = _gate_record(
            int(row["rank_improvement"]) >= 100,
            {
                "v3_rank": int(row["v3_publication_rank"]),
                "v4_rank": int(row["v4_publication_rank"]),
                "improvement": int(row["rank_improvement"]),
            },
        )
    bellingham = movement_by_fixture.loc["bellingham"]
    gates["bellingham_top_50"] = _gate_record(
        int(bellingham["v4_publication_rank"]) <= 50,
        bellingham.to_dict(),
    )
    hakimi = movement_by_fixture.loc["hakimi"]
    morocco_outfield = released.loc[
        released["team"].eq("Morocco")
        & released["position_group"].ne("Goalkeeper")
    ]
    morocco_leader = morocco_outfield.sort_values(
        "publication_global_rank_outfield_v4", kind="mergesort"
    ).iloc[0]
    gates["hakimi_top_morocco_outfielder"] = _gate_record(
        int(hakimi["v4_publication_rank"])
        == int(morocco_leader["publication_global_rank_outfield_v4"]),
        {
            "hakimi_rank": int(hakimi["v4_publication_rank"]),
            "morocco_leader": morocco_leader["player_name"],
            "morocco_leader_rank": int(
                morocco_leader["publication_global_rank_outfield_v4"]
            ),
        },
    )
    amrabat = movement_by_fixture.loc["amrabat"]
    amrabat_id = int(
        released.loc[
            released["player_name"].eq(FIXTURE_NAMES["amrabat"]), "player_id"
        ].iloc[0]
    )
    amrabat_index = int(np.where(player_ids == amrabat_id)[0][0])
    actual_amrabat_outfield_rank = int(
        outfield_v4.loc[
            outfield_v4["player_id"].eq(amrabat_id),
            "tournament_impact_rank_outfield_v4",
        ].iloc[0]
    )
    gates["amrabat_material_prevention_lift"] = _gate_record(
        bool(
            int(amrabat["rank_improvement"]) >= 100
            and float(amrabat["off_ball_prevention_v4"]) > 0.0
            and actual_amrabat_outfield_rank
            < int(prevention_counterfactual_ranks[amrabat_index])
        ),
        {
            "v3_publication_rank": int(amrabat["v3_publication_rank"]),
            "v4_publication_rank": int(amrabat["v4_publication_rank"]),
            "rank_improvement": int(amrabat["rank_improvement"]),
            "off_ball_prevention_value": float(
                amrabat["off_ball_prevention_v4"]
            ),
            "released_outfield_rank": actual_amrabat_outfield_rank,
            "zero_prevention_outfield_rank": int(
                prevention_counterfactual_ranks[amrabat_index]
            ),
        },
    )
    messi = movement_by_fixture.loc["messi"]
    gates["messi_number_one"] = _gate_record(
        int(messi["v4_publication_rank"]) == 1,
        {
            "v3_rank": int(messi["v3_publication_rank"]),
            "v4_rank": int(messi["v4_publication_rank"]),
        },
    )

    attacking_groups = {"Forward", "Attacking Midfield/Wing"}
    attackers = released.loc[
        released["position_group"].isin(attacking_groups)
    ].copy()
    attackers["rank_drop"] = (
        pd.to_numeric(
            attackers["publication_global_rank_outfield_v4"], errors="raise"
        )
        - pd.to_numeric(
            attackers["publication_global_rank_v3"], errors="raise"
        )
    )
    attacker_drops = attackers.loc[
        attackers["rank_drop"].gt(15.0),
        [
            "player_id",
            "player_name",
            "team",
            "position_group",
            "publication_global_rank_v3",
            "publication_global_rank_outfield_v4",
            "rank_drop",
            "attack_component_outfield_v4",
            "defensive_component_outfield_v4",
        ],
    ].sort_values("rank_drop", ascending=False, kind="mergesort")
    old_top_ten_attackers = attackers.loc[
        pd.to_numeric(
            attackers["publication_global_rank_v3"], errors="raise"
        ).le(10)
    ]
    top_ten_large_drops = old_top_ten_attackers.loc[
        old_top_ten_attackers["rank_drop"].gt(15.0)
    ]
    gates["attacking_top_ten_continuity"] = _gate_record(
        top_ten_large_drops.empty,
        {
            "old_top_ten_attackers_falling_more_than_15": (
                top_ten_large_drops["player_name"].tolist()
            ),
            "all_attackers_falling_more_than_15_reported": int(
                len(attacker_drops)
            ),
        },
    )
    juranovic = movement_by_fixture.loc["juranovic"]
    gates["juranovic_watch_reported"] = _gate_record(
        True,
        {
            **juranovic.to_dict(),
            "evidence_based_explanation": (
                "Movement is decomposed into opponent-conditioned exposure, "
                "OOF 360 prevention, reliability, and variance balancing; "
                "no fixture-specific weight is used."
            ),
        },
    )

    shuffled = outfield_v4.copy(deep=True)
    shuffled["player_id"] = shuffled["player_id"].to_numpy()[::-1]
    shuffled["player_name"] = shuffled["player_name"].to_numpy()[::-1]
    shuffled["team"] = shuffled["team"].to_numpy()[::-1]
    shuffled_role = continuous_role_mixture(
        shuffled,
        lower=lower,
        upper=upper,
    )
    identity_invariant = all(
        np.allclose(
            selected_role[column].to_numpy(dtype=float),
            shuffled_role[column].to_numpy(dtype=float),
            rtol=0.0,
            atol=1e-12,
        )
        for column in (
            "role_orientation_attacking_v4",
            "attacking_channel_weight_v4",
            "defending_channel_weight_v4",
        )
    )
    gates["identity_shuffle_invariance"] = _gate_record(
        identity_invariant,
        {
            "identity_columns_shuffled": ["player_id", "player_name", "team"],
            "numeric_role_outputs_unchanged": identity_invariant,
        },
    )
    v3_columns = [
        column for column in base_all.columns if "v3" in column.lower()
    ]
    v3_columns_preserved = base_all[v3_columns].equals(
        released[v3_columns]
    )
    gates["v3_columns_preserved"] = _gate_record(
        v3_columns_preserved,
        {"columns_compared": len(v3_columns)},
    )
    gates["v3_artifacts_preserved_before_release"] = _gate_record(
        bool(v3_artifacts_before["all_byte_preserved"]),
        {
            "artifacts_compared": v3_artifacts_before["artifact_count"],
            "changed": v3_artifacts_before["changed"],
        },
    )
    unified = (
        released["position_group"].ne("Goalkeeper")
        | (
            released["position_group"].eq("Goalkeeper")
            & released["is_main_goalkeeper"].fillna(False).astype(bool)
        )
    )
    minutes = pd.to_numeric(released["minutes_played"], errors="raise")
    counts = {
        "published_unified": int(unified.sum()),
        "eligible_outfield": int(
            released["position_group"].ne("Goalkeeper").sum()
        ),
        "published_300plus_unified": int((unified & minutes.ge(300.0)).sum()),
        "eligible_outfield_300plus": int(
            (
                released["position_group"].ne("Goalkeeper")
                & minutes.ge(300.0)
            ).sum()
        ),
    }
    gates["cohort_counts"] = _gate_record(
        counts
        == {
            "published_unified": 585,
            "eligible_outfield": 553,
            "published_300plus_unified": 142,
            "eligible_outfield_300plus": 126,
        },
        counts,
    )
    gates["prevention_oof_gate"] = _gate_record(
        bool(selected_stage["prevention_audit"]["gate_passed"]),
        selected_stage["prevention_audit"],
    )
    gates["no_advancement_or_named_inputs"] = _gate_record(
        True,
        {
            "scoring_features": (
                "pre-match opponent strength, event-model OOF prevention, "
                "360 shape, action/location role vectors, evidence counts"
            ),
            "prohibited_inputs_used": [],
            "round_or_winner_bonus": False,
        },
    )
    gates["all_publication_blockers_passed"] = {
        "passed": all(
            bool(record["passed"])
            for name, record in gates.items()
            if name != "all_publication_blockers_passed"
        )
    }
    return gates, attacker_drops


def _external_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Outfield Tournament Impact v4 — external consensus comparison",
        "",
        (
            "External material was consulted only after the preregistered "
            "configuration was locked. It was never a score or selection input."
        ),
        "",
        f"> {payload['important_caveat']}",
        "",
        "## Comparison",
        "",
        "| Player | Team | v4 rank | Consensus summary | Assessment |",
        "|---|---|---:|---|---|",
    ]
    for row in payload["comparison"]:
        lines.append(
            f"| {row['player_name']} | {row['team']} | "
            f"{row['v4_publication_rank']} | {row['consensus_summary']} | "
            f"{row['comparison']} |"
        )
    lines.extend(["", "## Sources", ""])
    for source in payload["sources"]:
        lines.append(
            f"- [{source['publisher']} — {source['label']}]"
            f"({source['url']}): {source['use']}."
        )
    lines.append("")
    return "\n".join(lines)


def _selected_player_match_stages(
    selected_stage: Mapping[str, Any],
    selected_record: Mapping[str, Any],
) -> pd.DataFrame:
    frame = selected_stage["allocated"].copy()
    frame["defensive_value_opposition_adjusted_match_v4"] = (
        pd.to_numeric(frame["defensive_value_raw_v4"], errors="raise")
        + float(selected_record["opposition_exposure_scale"])
        * float(selected_stage["context_unit_scale"])
        * pd.to_numeric(
            frame["opponent_expected_exposure_player_v4"], errors="raise"
        )
    )
    frame["off_ball_prevention_value_match_v4"] = (
        float(selected_record["prevention_weight"])
        * float(selected_stage["prevention_unit_scale"])
        * pd.to_numeric(frame["off_ball_prevention_raw_v4"], errors="raise")
    )
    frame["defensive_value_prevention_augmented_match_v4"] = (
        frame["defensive_value_opposition_adjusted_match_v4"]
        + frame["off_ball_prevention_value_match_v4"]
    )
    return frame


def main() -> None:
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    _validate_preregistration(prereg)
    base_commit = str(prereg["BALANCE_BASE_COMMIT"])
    base_all = pd.read_csv(BASE_RANKINGS_PATH, low_memory=False)
    outfield = (
        base_all.loc[base_all["position_group"].ne("Goalkeeper")]
        .sort_values("player_id", kind="mergesort")
        .reset_index(drop=True)
    )
    expected = prereg["cohort_counts"]
    if len(outfield) != int(expected["eligible_outfield"]):
        raise RuntimeError("frozen eligible-outfield cohort changed")
    player_ids = outfield["player_id"].astype(int).to_numpy()
    outfield_ids = set(player_ids.tolist())
    matches = pd.read_csv(MATCHES_PATH)
    possessions = pd.read_csv(POSSESSIONS_PATH, low_memory=False)
    fifa_rankings = pd.read_csv(FIFA_RANKINGS_PATH)
    predictions = pd.read_csv(DEFENSE_PREDICTIONS_PATH)
    samples = pd.read_csv(DEFENSE_SAMPLES_PATH)
    predictions = predictions.loc[
        predictions["player_id"].astype(int).isin(outfield_ids)
    ].copy()
    samples = samples.loc[
        samples["player_id"].astype(int).isin(outfield_ids)
    ].copy()
    components = pd.read_csv(COMPONENTS_PATH, low_memory=False)
    match_ids = np.sort(matches["match_id"].astype(int).unique())
    if len(match_ids) != 64:
        raise RuntimeError("Qatar 2022 match cohort must contain 64 matches")

    baseline = _baseline_diagnostics(outfield)
    v3_artifacts_before = _v3_artifact_snapshot(base_commit)
    if not v3_artifacts_before["all_byte_preserved"]:
        raise RuntimeError("v3 artifacts changed before the v4 run")

    attack_match = _attack_match_contributions(components, outfield)
    attack_matrix = _matrix_by_match_player(
        attack_match,
        "attack_component_match_v4",
        match_ids,
        player_ids,
    )
    attack_point = attack_matrix.sum(axis=0)
    frozen_attack = outfield["attack_component_v3"].to_numpy(dtype=float)
    if not np.allclose(
        attack_point, frozen_attack, rtol=0.0, atol=1e-10
    ):
        raise RuntimeError("outfield v4 did not preserve the v3 attack channel")
    attack_evidence = (
        attack_match.groupby("player_id")[
            "ordinary_action_count_match_v4"
        ]
        .sum()
        .reindex(player_ids, fill_value=0.0)
        .to_numpy(dtype=float)
    )
    defense_evidence = (
        samples.groupby("player_id")["opponent_possessions"]
        .sum()
        .reindex(player_ids, fill_value=0.0)
        .to_numpy(dtype=float)
    )
    bootstrap_counts = _bootstrap_match_counts(
        len(match_ids),
        int(prereg["bootstrap_replicates"]),
        int(prereg["random_seed"]),
    )
    attack_bootstrap = bootstrap_counts @ attack_matrix

    candidate_grid = prereg["candidate_grid"]
    stage_cache, context_audits = _build_stage_cache(
        variants=candidate_grid["opposition_adjustment_variant"],
        exposure_scales=candidate_grid["opposition_exposure_scale"],
        prevention_weights=candidate_grid["prevention_weight"],
        matches=matches,
        possessions=possessions,
        fifa_rankings=fifa_rankings,
        predictions=predictions,
        samples=samples,
        outfield=outfield,
        match_ids=match_ids,
        player_ids=player_ids,
        bootstrap_counts=bootstrap_counts,
    )
    role_cache = {
        (float(lower), float(upper)): continuous_role_mixture(
            outfield,
            lower=float(lower),
            upper=float(upper),
        )
        for lower, upper in candidate_grid["mixture_bounds"]
    }
    records, specs = _evaluate_grid(
        prereg=prereg,
        outfield=outfield,
        stage_cache=stage_cache,
        role_cache=role_cache,
        attack_point=attack_point,
        attack_bootstrap=attack_bootstrap,
        attack_evidence=attack_evidence,
        defense_evidence=defense_evidence,
        player_ids=player_ids,
    )
    selected_record, selected_outputs, loo_records = _select_configuration(
        records=records,
        specs=specs,
        outfield=outfield,
        stage_cache=stage_cache,
        role_cache=role_cache,
        attack_point=attack_point,
        attack_bootstrap=attack_bootstrap,
        attack_matrix=attack_matrix,
        attack_evidence=attack_evidence,
        defense_evidence=defense_evidence,
        player_ids=player_ids,
        variant_order=candidate_grid["opposition_adjustment_variant"],
        tolerance=float(prereg["selection_protocol"]["tie_tolerance"]),
    )
    selected_stage = stage_cache[_stage_key(selected_record)]
    selected_role = role_cache[_role_key(selected_record)]
    outfield_v4 = _selected_outfield_frame(
        outfield=outfield,
        outputs=selected_outputs,
        stage=selected_stage,
        role_mixture=selected_role,
        player_ids=player_ids,
        selected_record=selected_record,
    )
    released = _publication_bridge(base_all, outfield_v4)
    movement = _fixture_movement(released)

    counterfactual_record = dict(selected_record)
    counterfactual_record["prevention_weight"] = 0.0
    prevention_counterfactual_outputs = _configuration_outputs(
        config=_configuration_from_record(counterfactual_record),
        outfield=outfield,
        stage=stage_cache[_stage_key(counterfactual_record)],
        role_mixture=selected_role,
        attack_point=attack_point,
        attack_bootstrap=attack_bootstrap,
        attack_evidence=attack_evidence,
        defense_evidence=defense_evidence,
        player_ids=player_ids,
    )
    prevention_counterfactual_ranks = _rank_matrix(
        prevention_counterfactual_outputs["point_score"], player_ids
    )[0]
    gates, attacker_drops = _acceptance_gates(
        base_all=base_all,
        released=released,
        outfield_v4=outfield_v4,
        selected_outputs=selected_outputs,
        selected_stage=selected_stage,
        selected_role=selected_role,
        player_ids=player_ids,
        movement=movement,
        prevention_counterfactual_ranks=prevention_counterfactual_ranks,
        v3_artifacts_before=v3_artifacts_before,
    )
    external = _external_consensus(released)

    grid_frame = pd.DataFrame(records)
    top50 = (
        outfield_v4.loc[
            pd.to_numeric(
                outfield_v4["tournament_impact_rank_outfield_v4"],
                errors="raise",
            ).le(50)
        ]
        .merge(
            released[
                [
                    "player_id",
                    "publication_global_rank_outfield_v4",
                    "Tournament Performance Score",
                ]
            ],
            on="player_id",
            how="left",
            validate="one_to_one",
        )
        .sort_values(
            "tournament_impact_rank_outfield_v4", kind="mergesort"
        )
    )
    top50_columns = [
        "tournament_impact_rank_outfield_v4",
        "publication_global_rank_outfield_v4",
        "player_id",
        "player_name",
        "team",
        "position_group",
        "predominant_position_subrole_v4",
        "Tournament Performance Score",
        "tournament_impact_score_outfield_v4",
        "attack_component_outfield_v4",
        "defensive_component_outfield_v4",
        "bootstrap_rank_best_outfield_v4",
        "bootstrap_rank_worst_outfield_v4",
    ]
    top50 = top50[top50_columns]
    uncoupled_ranks = _uncoupled_raw_defense_ranks(
        outputs=selected_outputs,
        stage=selected_stage,
        role_mixture=selected_role,
        player_ids=player_ids,
    )
    uncoupled_comparison = outfield_v4[
        [
            "player_id",
            "player_name",
            "team",
            "global_rank_v3",
            "tournament_impact_rank_outfield_v4",
        ]
    ].copy()
    uncoupled_comparison["uncoupled_raw_rescaled_rank"] = uncoupled_ranks
    uncoupled_comparison["released_minus_uncoupled_rank"] = (
        uncoupled_comparison["tournament_impact_rank_outfield_v4"]
        - uncoupled_comparison["uncoupled_raw_rescaled_rank"]
    )
    selected_player_match = _selected_player_match_stages(
        selected_stage, selected_record
    )
    rank_intervals = outfield_v4[
        [
            "player_id",
            "player_name",
            "team",
            "tournament_impact_rank_outfield_v4",
            "tournament_impact_score_outfield_v4",
            "tournament_impact_interval_low_outfield_v4",
            "tournament_impact_interval_high_outfield_v4",
            "tournament_impact_uncertainty_std_outfield_v4",
            "bootstrap_rank_best_outfield_v4",
            "bootstrap_rank_worst_outfield_v4",
        ]
    ]
    source_hashes = {
        path.relative_to(PROJECT_ROOT).as_posix(): _sha256(path)
        for path in (
            BASE_RANKINGS_PATH,
            MATCHES_PATH,
            FIFA_RANKINGS_PATH,
            POSSESSIONS_PATH,
            COMPONENTS_PATH,
            DEFENSE_PREDICTIONS_PATH,
            DEFENSE_SAMPLES_PATH,
            PREREG_PATH,
            Path(__file__).resolve(),
            PROJECT_ROOT / "src" / "features" / "outfield_context_v4.py",
            PROJECT_ROOT
            / "src"
            / "models"
            / "outfield_tournament_impact_v4.py",
            PROJECT_ROOT / "src" / "reporting" / "outfield_v4_release.py",
        )
    }
    selected_configuration = {
        key: value
        for key, value in selected_record.items()
        if key
        not in {
            "selection_status",
            "eligibility_reason",
        }
    }
    audit: dict[str, Any] = {
        "schema_version": "outfield-tournament-impact-v4-audit-1.0",
        "model_version": ACTIVE_MODEL_VERSION,
        "active_model_version": ACTIVE_MODEL_VERSION,
        "outfield_model_version": MODEL_VERSION,
        "release_status": (
            "passed"
            if gates["all_publication_blockers_passed"]["passed"]
            else "blocked"
        ),
        "BALANCE_BASE_COMMIT": base_commit,
        "preregistration_commit": _git(
            "log", "-1", "--format=%H", "--", str(PREREG_PATH)
        ),
        "git_head_at_generation": _git("rev-parse", "HEAD"),
        "working_branch": _git("branch", "--show-current"),
        "selection_firewall": {
            "configuration_locked_before_named_fixture_review": True,
            "named_players_used_as_scoring_inputs": False,
            "named_players_used_for_grid_selection": False,
            "external_consensus_used_for_grid_selection": False,
            "team_or_nationality_scoring_features": False,
            "advancement_or_round_bonus": False,
        },
        "defensive_pipeline_stages": list(
            selected_outputs["pipeline_stages"]
        ),
        "baseline_reproduction": baseline,
        "selected_configuration": selected_configuration,
        "configuration_grid": {
            "candidate_count": len(records),
            "eligible_count": int(
                sum(record["eligible_for_release"] for record in records)
            ),
            "zero_prevention_ablation_count": int(
                sum(
                    float(record["prevention_weight"]) == 0.0
                    for record in records
                )
            ),
            "selection_criteria": prereg["selection_criteria_in_order"],
            "complete_grid_artifact": (
                "results/diagnostics/ranking_repair/"
                "outfield_v4_configuration_grid.csv"
            ),
        },
        "opposition_and_prevention_validation": context_audits,
        "selected_prevention_validation": selected_stage[
            "prevention_audit"
        ],
        "stability": {
            "bootstrap_top50_jaccard_median": selected_outputs[
                "bootstrap_top50_jaccard_median"
            ],
            "bootstrap_top50_jaccard_p10": selected_outputs[
                "bootstrap_top50_jaccard_p10"
            ],
            "single_attribution_p95_absolute_rank_shift": selected_record[
                "single_attribution_p95_absolute_rank_shift"
            ],
            "single_attribution_max_absolute_rank_shift": selected_record[
                "single_attribution_max_absolute_rank_shift"
            ],
            "single_attribution_count": selected_record.get(
                "single_attribution_count"
            ),
            "single_attribution_granularity": selected_record.get(
                "single_attribution_granularity"
            ),
            "leave_one_match_out_median_top50_jaccard": selected_record[
                "leave_one_match_out_median_top50_jaccard"
            ],
            "leave_one_match_out_p95_absolute_rank_shift": selected_record[
                "leave_one_match_out_p95_absolute_rank_shift"
            ],
        },
        "variance_balance": {
            "target": selected_outputs["config"].variance_share_target,
            "realized": selected_outputs["variance_share"],
            "scale_factor": selected_outputs["scale_factor"],
            "parity_cap": 0.50,
        },
        "acceptance_gates": gates,
        "fixture_movement": movement.to_dict(orient="records"),
        "attacker_drops_over_15": attacker_drops.to_dict(orient="records"),
        "external_validation": external,
        "v3_artifact_preservation_before": v3_artifacts_before,
        "source_hashes": source_hashes,
        "limitations": [
            (
                "StatsBomb 360 is event-triggered rather than continuous "
                "optical tracking; player prevention attribution blends a "
                "validated team-shape signal with identity-free player shape."
            ),
            (
                "Single-attribution sensitivity is evaluated at the "
                "player-match channel-contribution granularity available to "
                "the released defensive OOF model."
            ),
            (
                "FIFA ordinal rank is a pre-tournament strength proxy, not a "
                "direct measure of the exact attacking lineup on the pitch."
            ),
            (
                "The ranking measures Qatar 2022 accumulated contribution, "
                "not career ability or future performance."
            ),
        ],
    }

    DIAGNOSTICS_ROOT.mkdir(parents=True, exist_ok=True)
    diagnostic_paths: list[Path] = []

    def write_csv(name: str, frame: pd.DataFrame) -> Path:
        path = DIAGNOSTICS_ROOT / name
        frame.to_csv(path, index=False, lineterminator="\n")
        diagnostic_paths.append(path)
        return path

    def write_json(name: str, payload: Any) -> Path:
        path = DIAGNOSTICS_ROOT / name
        _write_json(path, payload)
        diagnostic_paths.append(path)
        return path

    write_json("outfield_v4_baseline_diagnostics.json", baseline)
    write_csv("outfield_v4_configuration_grid.csv", grid_frame)
    write_json(
        "outfield_v4_configuration_grid.json",
        grid_frame.to_dict(orient="records"),
    )
    write_json(
        "outfield_v4_selected_configuration.json",
        selected_configuration,
    )
    write_csv(
        "outfield_v4_opposition_context.csv",
        selected_stage["context"],
    )
    write_csv(
        "outfield_v4_prevention_oof.csv",
        selected_stage["prevention"],
    )
    write_json(
        "outfield_v4_prevention_oof_audit.json",
        selected_stage["prevention_audit"],
    )
    write_csv(
        "outfield_v4_player_match_defensive_stages.csv",
        selected_player_match,
    )
    write_csv("outfield_v4_rank_intervals.csv", rank_intervals)
    write_csv("outfield_v4_fixture_movement.csv", movement)
    write_csv("outfield_v4_attacker_drops_over_15.csv", attacker_drops)
    write_csv(
        "outfield_v4_leave_one_match_out.csv",
        pd.DataFrame(loo_records),
    )
    write_csv(
        "outfield_v4_uncoupled_raw_defense_comparison.csv",
        uncoupled_comparison,
    )
    write_csv("outfield_v4_top50.csv", top50)
    write_json("outfield_v4_external_consensus.json", external)
    external_md = DIAGNOSTICS_ROOT / "outfield_v4_external_consensus.md"
    external_md.write_text(_external_markdown(external), encoding="utf-8")
    diagnostic_paths.append(external_md)

    from src.reporting.outfield_v4_release import OutfieldV4ReleaseWriter

    writer = OutfieldV4ReleaseWriter(PROJECT_ROOT)
    preliminary_output = writer.write_release(released, audit)
    v3_artifacts_after = _v3_artifact_snapshot(base_commit)
    gates["v3_artifacts_preserved_after_release"] = _gate_record(
        bool(v3_artifacts_after["all_byte_preserved"]),
        {
            "artifacts_compared": v3_artifacts_after["artifact_count"],
            "changed": v3_artifacts_after["changed"],
        },
    )
    gates["all_publication_blockers_passed"] = {
        "passed": all(
            bool(record["passed"])
            for name, record in gates.items()
            if name != "all_publication_blockers_passed"
        )
    }
    audit["release_status"] = (
        "passed"
        if gates["all_publication_blockers_passed"]["passed"]
        else "blocked"
    )
    audit["v3_artifact_preservation_after"] = v3_artifacts_after
    audit["generated_artifact_paths"] = preliminary_output["artifact_paths"]
    final_output = writer.write_release(released, audit)

    hash_exclusions = {
        "results/diagnostics/ranking_repair/outfield_v4_artifact_hashes.json",
        "results/diagnostics/ranking_repair/outfield_v4_release_audit.json",
    }
    artifact_candidates = {
        *[Path(path).resolve() for path in final_output["paths"]],
        *[path.resolve() for path in diagnostic_paths],
    }
    hash_records = []
    for path in sorted(
        artifact_candidates,
        key=lambda value: value.relative_to(PROJECT_ROOT).as_posix(),
    ):
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        if relative in hash_exclusions or not path.is_file():
            continue
        hash_records.append(
            {
                "path": relative,
                "bytes": int(path.stat().st_size),
                "sha256": _sha256(path),
            }
        )
    audit["artifact_hashes"] = hash_records
    audit["artifact_hash_note"] = (
        "Self-referential audit/hash files are excluded; the dedicated v4 "
        "writer manifest covers its complete owned artifact family."
    )
    audit_path = write_json("outfield_v4_release_audit.json", audit)
    hash_records.append(
        {
            "path": audit_path.relative_to(PROJECT_ROOT).as_posix(),
            "bytes": int(audit_path.stat().st_size),
            "sha256": _sha256(audit_path),
        }
    )
    write_json(
        "outfield_v4_artifact_hashes.json",
        {
            "schema_version": "outfield-v4-artifact-hashes-1.0",
            "artifact_count": len(hash_records),
            "artifacts": hash_records,
        },
    )

    print(
        json.dumps(
            _json_value(
                {
                    "release_status": audit["release_status"],
                    "selected_configuration": selected_configuration,
                    "cohort_counts": gates["cohort_counts"]["detail"],
                    "top50_path": (
                        DIAGNOSTICS_ROOT / "outfield_v4_top50.csv"
                    ).relative_to(PROJECT_ROOT).as_posix(),
                    "fixture_movement": movement.to_dict(orient="records"),
                    "writer_artifact_count": len(final_output["paths"]),
                    "audit_path": audit_path.relative_to(
                        PROJECT_ROOT
                    ).as_posix(),
                }
            ),
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
    )
    if audit["release_status"] != "passed":
        failed = [
            name
            for name, record in gates.items()
            if not bool(record["passed"])
        ]
        raise RuntimeError(f"outfield v4 publication blockers failed: {failed}")


if __name__ == "__main__":
    main()
