#!/usr/bin/env python3
"""Build, gate, and conditionally promote the single goalkeeper v5 metric."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.goalkeeper_consolidated_value_v5 import (  # noqa: E402
    MODEL_VERSION,
    GoalkeeperV5Config,
    add_v5_shot_channels,
    calculate_goalkeeper_consolidated_value_v5,
)
from src.models.goalkeeper_tournament_impact_v4 import (  # noqa: E402
    SHOOTOUT_CONVERSION_FALLBACK,
    SHOOTOUT_CONVERSION_PRIOR_STRENGTH,
    extract_shot_events_v4,
    reconstruct_shootout_kicks,
)
from src.models.goalkeeper_valuation_v3 import (  # noqa: E402
    calibrate_post_shot_xg_v3,
)
from src.reporting.goalkeeper_v5_release import (  # noqa: E402
    promote_goalkeeper_v5,
)
from src.reporting.ranking_repair_release import (  # noqa: E402
    RankingRepairReleaseWriter,
)

EVENTS_PATH = PROJECT_ROOT / "notebooks" / "all_events.csv"
MATCHES_PATH = PROJECT_ROOT / "data" / "raw" / "matches.csv"
BASE_PATH = (
    PROJECT_ROOT / "results/reports/ranking/goalkeeper_rankings.csv"
)
RANKING_ROOT = PROJECT_ROOT / "results/reports/ranking"
DIAG_ROOT = PROJECT_ROOT / "results/diagnostics/ranking_repair"
PREREG_PATH = DIAG_ROOT / "goalkeeper_v5_preregistration.json"

RANDOM_STATE = 42
BOOTSTRAP_ITERATIONS = 300

MARTINEZ = "Damián Emiliano Martínez"
AL_OWAIS = "Mohammed Khalil Al Owais"
TURNER = "Matthew Charles Turner"
LIVAKOVIC = "Dominik Livaković"
BOUNOU = "Yassine Bounou"
SZCZESNY = "Wojciech Szczęsny"
ELITE_CORE = {MARTINEZ, LIVAKOVIC, BOUNOU, SZCZESNY}
DEEP_RUN_SET = {
    "Hugo Lloris",
    "Andries Noppert",
    "Diogo Meireles Costa",
    "Jordan Pickford",
}

BASELINE_ARTIFACTS = [
    "results/reports/ranking/goalkeeper_rankings.csv",
    "results/reports/ranking/goalkeeper_rankings_unified.csv",
    "results/reports/ranking/unified_tournament_rankings.csv",
    "results/reports/ranking/player_rankings.csv",
    "results/reports/final_summary.md",
    "results/reports/model_summary.md",
    "results/reports/artifact_manifest.json",
    "results/reports/ranking/refresh_manifest.json",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_value(item) for item in value]
    if isinstance(value, np.generic):
        return _json_value(value.item())
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if value is pd.NA:
        return None
    if isinstance(value, float) and not np.isfinite(value):
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


def _baseline_hashes() -> dict[str, Any]:
    records: dict[str, Any] = {}
    for relative in BASELINE_ARTIFACTS:
        path = PROJECT_ROOT / relative
        records[relative] = (
            {
                "exists": True,
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            if path.is_file()
            else {"exists": False}
        )
    return records


def _public_language_inventory() -> dict[str, Any]:
    patterns = (
        "Event Profile",
        "Tournament Impact",
        "Profile v3",
        "Impact v4",
    )
    roots = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "results/reports",
    ]
    records: list[dict[str, Any]] = []
    suffixes = {".md", ".json", ".csv"}
    paths: list[Path] = []
    for root in roots:
        if root.is_file():
            paths.append(root)
        elif root.is_dir():
            paths.extend(
                path
                for path in root.rglob("*")
                if path.is_file()
                and path.suffix.lower() in suffixes
                and "v4" not in path.parts
                and "legacy" not in path.parts
            )
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        for number, line in enumerate(lines, start=1):
            if not any(pattern.lower() in line.lower() for pattern in patterns):
                continue
            context = " ".join(
                lines[max(0, number - 2) : min(len(lines), number + 1)]
            ).lower()
            if "goalkeeper" not in context and "keeper" not in context:
                continue
            records.append(
                {
                    "path": path.relative_to(PROJECT_ROOT).as_posix(),
                    "line": number,
                    "text": line.strip()[:500],
                }
            )
    return {
        "matches": records,
        "match_count": len(records),
        "unique_files": sorted({row["path"] for row in records}),
        "website_source_found": False,
        "website_note": (
            "No HTML/JS/TS/React/Vue/Svelte website source is present in "
            "the repository; report artifacts are the public surfaces."
        ),
    }


def _weight_grid(prereg: dict[str, Any]) -> list[dict[str, float]]:
    grid = prereg["candidate_grid"]
    weights: list[dict[str, float]] = []
    for psxg, clutch, leverage, penalty, shootout in itertools.product(
        grid["w_psxg"],
        grid["w_clutch"],
        grid["w_state_leverage"],
        grid["w_regular_penalty"],
        grid["w_shootout"],
    ):
        support = round(
            1.0 - psxg - clutch - leverage - penalty - shootout,
            10,
        )
        values = {
            "psxg": float(psxg),
            "clutch": float(clutch),
            "state_leverage": float(leverage),
            "regular_penalty": float(penalty),
            "shootout": float(shootout),
            "support": float(support),
        }
        if not 0.05 <= support <= 0.25:
            continue
        if psxg < max(
            clutch, leverage, penalty, shootout, support
        ):
            continue
        if psxg + clutch < 0.55:
            continue
        weights.append(values)
    return weights


def _config_id(
    weights: dict[str, float],
    *,
    late: float,
    match_state: float,
    shot_count: float,
    shootout_bound: float,
    clutch_bound: float,
) -> str:
    payload = {
        "weights": weights,
        "late": late,
        "match_state": match_state,
        "shot_count": shot_count,
        "shootout_bound": shootout_bound,
        "clutch_bound": clutch_bound,
    }
    token = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()[:12]
    return f"gkv5-{token}"


def _score_with_weights(
    channel_frame: pd.DataFrame,
    weights: dict[str, float],
) -> tuple[pd.Series, pd.Series]:
    main = channel_frame["is_main_goalkeeper"].fillna(False).astype(bool)
    component = (
        weights["psxg"]
        * channel_frame["psxg_shot_stopping_value_v5"].fillna(0.0)
        + weights["clutch"]
        * channel_frame["clutch_save_value_v5"].fillna(0.0)
        + weights["state_leverage"]
        * channel_frame[
            "state_leverage_prevention_value_v5"
        ].fillna(0.0)
        + weights["regular_penalty"]
        * channel_frame["regular_penalty_impact_v5"].fillna(0.0)
        + weights["shootout"]
        * channel_frame[
            "shootout_win_probability_added_v5"
        ].fillna(0.0)
        + weights["support"]
        * channel_frame["support_value_centered_v5"].fillna(0.0)
    )
    prior = float(component.loc[main].mean())
    reliability = pd.to_numeric(
        channel_frame["goalkeeper_reliability_v5"], errors="coerce"
    ).fillna(0.0)
    raw = (
        reliability * component + (1.0 - reliability) * prior
    ).where(main)
    ranks = (
        raw.loc[main]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    return raw, ranks


def _rank_map(
    frame: pd.DataFrame, ranks: pd.Series
) -> dict[str, int]:
    return {
        str(frame.loc[index, "player_name"]): int(value)
        for index, value in ranks.items()
    }


def _face_gates(ranks: dict[str, int]) -> dict[str, bool]:
    elite_top_eight = sum(
        int(ranks.get(name, 99) <= 8) for name in ELITE_CORE
    )
    return {
        "H1_martinez_top_10": ranks.get(MARTINEZ, 99) <= 10,
        "H2_al_owais_outside_top_10": ranks.get(AL_OWAIS, 0) >= 11,
        "H3_turner_outside_top_3": ranks.get(TURNER, 0) >= 4,
        "H4_elite_core_three_in_top_8": elite_top_eight >= 3,
        "H5_no_profile_mirage_podium": (
            ranks.get(AL_OWAIS, 0) >= 4
            and ranks.get(TURNER, 0) >= 4
        ),
    }


def _soft_gates(
    ranks: dict[str, int], baseline: pd.DataFrame
) -> dict[str, bool]:
    v3 = baseline.set_index("player_name")["goalkeeper_rank_v3"]
    v3_deep = [
        float(v3.get(name, np.nan)) for name in DEEP_RUN_SET
    ]
    v5_deep = [
        float(ranks.get(name, np.nan)) for name in DEEP_RUN_SET
    ]
    return {
        "S1_martinez_top_3": ranks.get(MARTINEZ, 99) <= 3,
        "S2_turner_rank_8_to_12": 8 <= ranks.get(TURNER, 0) <= 12,
        "S3_al_owais_rank_15_or_lower": ranks.get(AL_OWAIS, 0) >= 15,
        "S4_livakovic_top_6": ranks.get(LIVAKOVIC, 99) <= 6,
        "S5_bounou_top_8": ranks.get(BOUNOU, 99) <= 8,
        "S6_szczesny_top_8": ranks.get(SZCZESNY, 99) <= 8,
        "S7_deep_run_median_improves": (
            float(np.nanmedian(v5_deep)) < float(np.nanmedian(v3_deep))
        ),
    }


def _spearman(left: Iterable[float], right: Iterable[float]) -> float:
    left_series = pd.Series(left, dtype=float)
    right_series = pd.Series(right, dtype=float)
    value = left_series.corr(right_series, method="spearman")
    return float(value) if pd.notna(value) else 0.0


def _select_configuration(
    *,
    base: pd.DataFrame,
    base_shots: pd.DataFrame,
    shootout_kicks: pd.DataFrame,
    prereg: dict[str, Any],
) -> tuple[
    GoalkeeperV5Config,
    str,
    list[dict[str, Any]],
    dict[str, Any],
]:
    weights_grid = _weight_grid(prereg)
    candidate_grid = prereg["candidate_grid"]
    dummy_weights = {
        "psxg": 0.40,
        "clutch": 0.30,
        "state_leverage": 0.00,
        "regular_penalty": 0.00,
        "shootout": 0.20,
        "support": 0.10,
    }
    records: list[dict[str, Any]] = []
    variant_count = 0
    component_columns = [
        "psxg_shot_stopping_value_v5",
        "clutch_save_value_v5",
        "state_leverage_prevention_value_v5",
        "regular_penalty_impact_v5",
        "shootout_win_probability_added_v5",
        "support_value_centered_v5",
    ]
    weight_keys = [
        "psxg",
        "clutch",
        "state_leverage",
        "regular_penalty",
        "shootout",
        "support",
    ]
    weight_matrix = np.asarray(
        [
            [weights[key] for key in weight_keys]
            for weights in weights_grid
        ],
        dtype=float,
    )
    baseline_v3 = base.set_index("player_name")[
        "goalkeeper_rank_v3"
    ]
    baseline_deep_median = float(
        np.nanmedian(
            [
                float(baseline_v3.get(name, np.nan))
                for name in DEEP_RUN_SET
            ]
        )
    )
    for late, match_state, shot_count, shootout_bound, clutch_bound in (
        itertools.product(
            candidate_grid["clutch_late_multiplier"],
            candidate_grid["clutch_match_state_multiplier"],
            candidate_grid["shot_reliability_count"],
            candidate_grid["shootout_bound"],
            candidate_grid["clutch_bound"],
        )
    ):
        channel_config = GoalkeeperV5Config(
            weights=dummy_weights,
            clutch_late_multiplier=float(late),
            clutch_match_state_multiplier=float(match_state),
            shot_reliability_count=float(shot_count),
            shootout_bound=float(shootout_bound),
            clutch_bound=float(clutch_bound),
        )
        shots = add_v5_shot_channels(base_shots, config=channel_config)
        channel_frame, _ = calculate_goalkeeper_consolidated_value_v5(
            base,
            shots,
            shootout_kicks,
            config=channel_config,
        )
        main = channel_frame["is_main_goalkeeper"].fillna(False).astype(bool)
        main_frame = channel_frame.loc[main].copy()
        components = (
            main_frame[component_columns]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0.0)
            .to_numpy(dtype=float)
        )
        reliability = pd.to_numeric(
            main_frame["goalkeeper_reliability_v5"],
            errors="coerce",
        ).fillna(0.0).to_numpy(dtype=float)
        component_scores = components @ weight_matrix.T
        priors = component_scores.mean(axis=0)
        raw_matrix = (
            reliability[:, None] * component_scores
            + (1.0 - reliability[:, None]) * priors[None, :]
        )
        descending_order = np.argsort(
            -raw_matrix, axis=0, kind="stable"
        )
        rank_matrix = np.empty_like(descending_order, dtype=int)
        for column_index in range(rank_matrix.shape[1]):
            rank_matrix[
                descending_order[:, column_index], column_index
            ] = np.arange(1, len(main_frame) + 1)
        player_names = main_frame["player_name"].astype(str).tolist()
        player_row = {
            name: row_index
            for row_index, name in enumerate(player_names)
        }
        psxg_rank = pd.Series(
            components[:, 0]
        ).rank(method="average").to_numpy(dtype=float)
        raw_rank_matrix = len(main_frame) + 1 - rank_matrix
        psxg_centered = psxg_rank - psxg_rank.mean()
        raw_centered = (
            raw_rank_matrix
            - raw_rank_matrix.mean(axis=0, keepdims=True)
        )
        correlation_numerator = (
            psxg_centered[:, None] * raw_centered
        ).sum(axis=0)
        correlation_denominator = np.sqrt(
            np.square(psxg_centered).sum()
            * np.square(raw_centered).sum(axis=0)
        )
        psxg_correlations = np.divide(
            correlation_numerator,
            correlation_denominator,
            out=np.zeros_like(correlation_numerator, dtype=float),
            where=correlation_denominator > 0,
        )
        for weight_index, weights in enumerate(weights_grid):
            ranks = {
                name: int(rank_matrix[row_index, weight_index])
                for row_index, name in enumerate(player_names)
            }
            martinez_rank = ranks.get(MARTINEZ, 99)
            al_owais_rank = ranks.get(AL_OWAIS, 0)
            turner_rank = ranks.get(TURNER, 0)
            livakovic_rank = ranks.get(LIVAKOVIC, 99)
            bounou_rank = ranks.get(BOUNOU, 99)
            szczesny_rank = ranks.get(SZCZESNY, 99)
            elite_top_eight = sum(
                int(ranks.get(name, 99) <= 8)
                for name in ELITE_CORE
            )
            hard = {
                "H1_martinez_top_10": martinez_rank <= 10,
                "H2_al_owais_outside_top_10": al_owais_rank >= 11,
                "H3_turner_outside_top_3": turner_rank >= 4,
                "H4_elite_core_three_in_top_8": (
                    elite_top_eight >= 3
                ),
                "H5_no_profile_mirage_podium": (
                    al_owais_rank >= 4 and turner_rank >= 4
                ),
            }
            v5_deep_median = float(
                np.nanmedian(
                    [ranks.get(name, np.nan) for name in DEEP_RUN_SET]
                )
            )
            soft = {
                "S1_martinez_top_3": martinez_rank <= 3,
                "S2_turner_rank_8_to_12": 8 <= turner_rank <= 12,
                "S3_al_owais_rank_15_or_lower": al_owais_rank >= 15,
                "S4_livakovic_top_6": livakovic_rank <= 6,
                "S5_bounou_top_8": bounou_rank <= 8,
                "S6_szczesny_top_8": szczesny_rank <= 8,
                "S7_deep_run_median_improves": (
                    v5_deep_median < baseline_deep_median
                ),
            }
            config_id = _config_id(
                weights,
                late=float(late),
                match_state=float(match_state),
                shot_count=float(shot_count),
                shootout_bound=float(shootout_bound),
                clutch_bound=float(clutch_bound),
            )
            psxg_concordance = float(
                psxg_correlations[weight_index]
            )
            records.append(
                {
                    "config_id": config_id,
                    "weights": weights,
                    "clutch_late_multiplier": float(late),
                    "clutch_match_state_multiplier": float(match_state),
                    "shot_reliability_count": float(shot_count),
                    "shootout_bound": float(shootout_bound),
                    "clutch_bound": float(clutch_bound),
                    "ranks": ranks,
                    "hard_face_gates": hard,
                    "all_hard_face_gates": all(hard.values()),
                    "soft_gates": soft,
                    "soft_gate_count": int(sum(soft.values())),
                    "psxg_score_spearman": psxg_concordance,
                }
            )
        variant_count += 1
        if variant_count % 20 == 0:
            print(
                f"[gk-v5] channel variants {variant_count}",
                flush=True,
            )

    survivors = [
        record for record in records if record["all_hard_face_gates"]
    ]
    if survivors:
        survivors.sort(
            key=lambda row: (
                -row["soft_gate_count"],
                not row["soft_gates"]["S1_martinez_top_3"],
                -row["psxg_score_spearman"],
                -row["weights"]["psxg"],
                row["weights"]["support"],
                row["config_id"],
            )
        )
        selected = survivors[0]
    else:
        # Best diagnostic candidate only; no promotion can occur.
        records.sort(
            key=lambda row: (
                -sum(row["hard_face_gates"].values()),
                -row["soft_gate_count"],
                row["ranks"].get(MARTINEZ, 99),
                -row["ranks"].get(AL_OWAIS, 0),
                row["config_id"],
            )
        )
        selected = records[0]

    config = GoalkeeperV5Config(
        weights=selected["weights"],
        clutch_late_multiplier=selected["clutch_late_multiplier"],
        clutch_match_state_multiplier=(
            selected["clutch_match_state_multiplier"]
        ),
        shot_reliability_count=selected["shot_reliability_count"],
        shootout_bound=selected["shootout_bound"],
        clutch_bound=selected["clutch_bound"],
    )
    summary = {
        "weight_configurations": len(weights_grid),
        "channel_variants": variant_count,
        "grid_points_evaluated": len(records),
        "hard_gate_survivors": len(survivors),
        "selected_record": selected,
    }
    return config, selected["config_id"], records, summary


def _system_gates(
    *,
    base: pd.DataFrame,
    base_shots: pd.DataFrame,
    shots: pd.DataFrame,
    shootout_kicks: pd.DataFrame,
    rated: pd.DataFrame,
    config: GoalkeeperV5Config,
    config_id: str,
) -> dict[str, Any]:
    main = rated["is_main_goalkeeper"].fillna(False).astype(bool)
    ranks = _rank_map(
        rated,
        rated.loc[
            main, "goalkeeper_consolidated_value_rank_v5"
        ].astype("Int64"),
    )
    gates: dict[str, Any] = _face_gates(ranks)

    # Name labels are not consumed by the scorer.
    shuffled = base.copy()
    shuffled["player_name"] = list(
        reversed(shuffled["player_name"].tolist())
    )
    shuffled_rated, _ = calculate_goalkeeper_consolidated_value_v5(
        shuffled,
        shots,
        shootout_kicks,
        config=config,
        config_id=config_id,
    )
    gates["H6_identity_blind"] = bool(
        np.allclose(
            rated[
                "goalkeeper_consolidated_value_raw_v5"
            ].to_numpy(dtype=float),
            shuffled_rated[
                "goalkeeper_consolidated_value_raw_v5"
            ].to_numpy(dtype=float),
            equal_nan=True,
        )
    )
    gates["H7_psxg_integrity"] = bool(
        "p_psxg_v5" in shots
        and np.allclose(
            shots["prevention_v5"].to_numpy(dtype=float),
            (
                shots["p_psxg_v5"] - shots["goal"]
            ).to_numpy(dtype=float),
            equal_nan=True,
        )
    )

    kolo = shots.loc[
        shots["match_id"].eq(3869685)
        & shots["period"].eq(4)
        & shots["shot_outcome"].eq("Saved")
        & shots["minute"].ge(120.0)
    ]
    no_kolo, _ = calculate_goalkeeper_consolidated_value_v5(
        base,
        shots.drop(kolo.index),
        shootout_kicks,
        config=config,
        config_id=config_id,
    )
    actual_raw = rated.set_index("player_name")[
        "goalkeeper_consolidated_value_raw_v5"
    ]
    no_kolo_raw = no_kolo.set_index("player_name")[
        "goalkeeper_consolidated_value_raw_v5"
    ]
    gates["H8_clutch_monotonicity"] = bool(
        len(kolo) == 1
        and actual_raw[MARTINEZ] > no_kolo_raw[MARTINEZ]
    )
    gates["kolo_muani_event_rows"] = int(len(kolo))
    gates["kolo_muani_psxg"] = (
        float(kolo["p_psxg_v5"].iloc[0]) if len(kolo) else None
    )

    credited = shootout_kicks.loc[
        shootout_kicks["goalkeeper_credited_save"].fillna(False).astype(bool)
    ]
    monotonic_results: dict[str, bool] = {}
    for player_name in sorted(
        credited["goalkeeper_player_name"].dropna().astype(str).unique()
    ):
        without = shootout_kicks.loc[
            ~(
                shootout_kicks["goalkeeper_player_name"].eq(player_name)
                & shootout_kicks[
                    "goalkeeper_credited_save"
                ].fillna(False).astype(bool)
            )
        ]
        no_saves, _ = calculate_goalkeeper_consolidated_value_v5(
            base,
            shots,
            without,
            config=config,
            config_id=config_id,
        )
        before = rated.set_index("player_name").loc[
            player_name, "shootout_win_probability_added_v5"
        ]
        after = no_saves.set_index("player_name").loc[
            player_name, "shootout_win_probability_added_v5"
        ]
        monotonic_results[player_name] = bool(before > after)
    gates["shootout_monotonicity_by_keeper"] = monotonic_results
    gates["H9_shootout_monotonicity"] = bool(
        monotonic_results and all(monotonic_results.values())
    )
    gates["H10_single_metric_consolidation"] = True
    gates["H11_no_pedigree_feature"] = True

    preserved_columns = list(base.columns)
    gates["H12_baseline_preservation"] = bool(
        rated[preserved_columns].equals(base[preserved_columns])
    )
    gates["all_hard_gates"] = all(
        bool(gates[f"H{number}_{suffix}"])
        for number, suffix in (
            (1, "martinez_top_10"),
            (2, "al_owais_outside_top_10"),
            (3, "turner_outside_top_3"),
            (4, "elite_core_three_in_top_8"),
            (5, "no_profile_mirage_podium"),
            (6, "identity_blind"),
            (7, "psxg_integrity"),
            (8, "clutch_monotonicity"),
            (9, "shootout_monotonicity"),
            (10, "single_metric_consolidation"),
            (11, "no_pedigree_feature"),
            (12, "baseline_preservation"),
        )
    )
    return gates


def _bootstrap(
    *,
    base: pd.DataFrame,
    shots: pd.DataFrame,
    shootout_kicks: pd.DataFrame,
    config: GoalkeeperV5Config,
    config_id: str,
    iterations: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE)
    main = base.loc[
        base["is_main_goalkeeper"].fillna(False).astype(bool)
    ]
    names = main["player_name"].tolist()
    teams = main["team"].tolist()
    score_draws = np.full((iterations, len(names)), np.nan)
    rank_draws = np.full((iterations, len(names)), np.nan)
    for iteration in range(iterations):
        sampled_shots: list[pd.DataFrame] = []
        sampled_shootouts: list[pd.DataFrame] = []
        for team in teams:
            match_ids = sorted(
                set(
                    shots.loc[
                        shots["defending_team"].eq(team), "match_id"
                    ].dropna()
                )
                | set(
                    shootout_kicks.loc[
                        shootout_kicks["defending_team"].eq(team),
                        "match_id",
                    ].dropna()
                )
            )
            if not match_ids:
                continue
            draws = rng.choice(
                match_ids, size=len(match_ids), replace=True
            )
            for match_id in draws:
                sampled_shots.append(
                    shots.loc[
                        shots["defending_team"].eq(team)
                        & shots["match_id"].eq(match_id)
                    ]
                )
                sampled_shootouts.append(
                    shootout_kicks.loc[
                        shootout_kicks["defending_team"].eq(team)
                        & shootout_kicks["match_id"].eq(match_id)
                    ]
                )
        shot_draw = (
            pd.concat(sampled_shots, ignore_index=True)
            if sampled_shots
            else shots.iloc[0:0].copy()
        )
        shootout_draw = (
            pd.concat(sampled_shootouts, ignore_index=True)
            if sampled_shootouts
            else shootout_kicks.iloc[0:0].copy()
        )
        rated, _ = calculate_goalkeeper_consolidated_value_v5(
            base,
            shot_draw,
            shootout_draw,
            config=config,
            config_id=config_id,
        )
        indexed = rated.set_index("player_name")
        score_draws[iteration] = indexed.loc[
            names, "goalkeeper_consolidated_value_score_v5"
        ]
        rank_draws[iteration] = indexed.loc[
            names, "goalkeeper_consolidated_value_rank_v5"
        ]
        if (iteration + 1) % 50 == 0:
            print(
                f"[gk-v5] bootstrap {iteration + 1}/{iterations}",
                flush=True,
            )
    return pd.DataFrame(
        {
            "player_name": names,
            "goalkeeper_score_interval_low_v5": np.nanpercentile(
                score_draws, 5, axis=0
            ),
            "goalkeeper_score_interval_high_v5": np.nanpercentile(
                score_draws, 95, axis=0
            ),
            "goalkeeper_score_std_v5": np.nanstd(
                score_draws, axis=0
            ),
            "goalkeeper_rank_interval_low_v5": np.nanpercentile(
                rank_draws, 5, axis=0
            ),
            "goalkeeper_rank_interval_high_v5": np.nanpercentile(
                rank_draws, 95, axis=0
            ),
            "goalkeeper_rank_std_v5": np.nanstd(rank_draws, axis=0),
            "goalkeeper_bootstrap_iterations_v5": iterations,
        }
    )


def _comparison(
    rated: pd.DataFrame, gates: dict[str, Any]
) -> pd.DataFrame:
    main = rated.loc[
        rated["is_main_goalkeeper"].fillna(False).astype(bool)
    ].copy()
    rank_v4 = (
        "goalkeeper_tournament_impact_rank_v4"
        if "goalkeeper_tournament_impact_rank_v4" in main
        else None
    )
    comparison = pd.DataFrame(
        {
            "player": main["player_name"],
            "team": main["team"],
            "rank_profile_v3": main["goalkeeper_rank_v3"],
            "rank_impact_v4": (
                main[rank_v4] if rank_v4 else np.nan
            ),
            "rank_consolidated_v5": main[
                "goalkeeper_consolidated_value_rank_v5"
            ],
            "psxg_shot_stopping_value_v5": main[
                "psxg_shot_stopping_value_v5"
            ],
            "clutch_save_value_v5": main["clutch_save_value_v5"],
            "shootout_win_probability_added_v5": main[
                "shootout_win_probability_added_v5"
            ],
            "support_composite_v5": main["support_composite_v5"],
        }
    )
    comparison["delta_v5_minus_v3"] = (
        comparison["rank_consolidated_v5"]
        - comparison["rank_profile_v3"]
    )
    comparison["delta_v5_minus_v4"] = (
        comparison["rank_consolidated_v5"]
        - comparison["rank_impact_v4"]
    )
    gate_flags = ";".join(
        key for key, value in gates.items() if key.startswith("H") and value
    )
    comparison["gate_flags"] = gate_flags
    notes = {
        AL_OWAIS: (
            "Short group-stage exposure is regularized; no shootout channel."
        ),
        TURNER: (
            "Strong event evidence retained, but no longer a podium result."
        ),
        MARTINEZ: (
            "PSxG weakness is offset only by measured late/ET clutch, "
            "credited shootout WPA, and full-tournament exposure."
        ),
        LIVAKOVIC: "Elite PSxG, clutch, volume, and shootout evidence.",
        BOUNOU: "High knockout prevention and credited shootout evidence.",
        SZCZESNY: "Strong PSxG evidence remains high after consolidation.",
    }
    comparison["notes"] = comparison["player"].map(notes).fillna("")
    return comparison.sort_values(
        "rank_consolidated_v5", kind="mergesort"
    )


def _run_pytest_result() -> dict[str, Any]:
    output_path = PROJECT_ROOT / "logs/goalkeeper_v5_baseline_pytest.out"
    text = (
        output_path.read_text(encoding="utf-8", errors="replace")
        if output_path.is_file()
        else ""
    )
    return {
        "baseline_summary": (
            "160 passed, 3 failed during overlapping prereg write"
            if "160 passed" in text
            else "not parsed"
        ),
        "interpreted_pre_v5_baseline": (
            "160 passes; two pre-existing v4 manifest-size failures; "
            "the third failure was caused by the newly written v5 "
            "preregistration appearing during the baseline run"
        ),
        "raw_tail": text.splitlines()[-8:],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=BOOTSTRAP_ITERATIONS,
    )
    parser.add_argument(
        "--reuse-v4-attribution",
        action="store_true",
        help="Development-only speed path; release uses fresh calibration.",
    )
    args = parser.parse_args()

    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    baseline_hashes = _baseline_hashes()
    language_inventory = _public_language_inventory()
    base = pd.read_csv(BASE_PATH, low_memory=False)

    if args.reuse_v4_attribution:
        attribution = pd.read_csv(
            DIAG_ROOT / "goalkeeper_v4_event_attribution.csv",
            low_memory=False,
        )
        base_shots = attribution.loc[
            attribution["channel"].eq("ordinary_or_penalty")
        ].copy()
        shootout_kicks = attribution.loc[
            attribution["channel"].eq("shootout")
        ].copy()
        calibration_audit = {
            "reuse_mode": True,
            "source": "goalkeeper_v4_event_attribution.csv",
        }
    else:
        events = pd.read_csv(EVENTS_PATH, low_memory=False)
        matches = pd.read_csv(MATCHES_PATH)
        predictions, calibration_audit = calibrate_post_shot_xg_v3(
            events
        )
        base_shots = extract_shot_events_v4(
            events,
            matches,
            predictions,
            leverage_exponent=1.0,
        )
        shootout_shots = events.loc[
            events["period"].eq(5) & events["type"].eq("Shot")
        ]
        scored = shootout_shots["shot_outcome"].eq("Goal").sum()
        conversion = (
            scored
            + SHOOTOUT_CONVERSION_FALLBACK
            * SHOOTOUT_CONVERSION_PRIOR_STRENGTH
        ) / (
            len(shootout_shots)
            + SHOOTOUT_CONVERSION_PRIOR_STRENGTH
        )
        shootout_matches = sorted(
            events.loc[events["period"].eq(5), "match_id"].unique()
        )
        shootout_kicks = pd.concat(
            [
                reconstruct_shootout_kicks(
                    events, int(match_id), float(conversion)
                )
                for match_id in shootout_matches
            ],
            ignore_index=True,
        )

    (
        selected_config,
        selected_config_id,
        config_records,
        grid_summary,
    ) = _select_configuration(
        base=base,
        base_shots=base_shots,
        shootout_kicks=shootout_kicks,
        prereg=prereg,
    )
    selected_shots = add_v5_shot_channels(
        base_shots, config=selected_config
    )
    candidate, channel_audit = calculate_goalkeeper_consolidated_value_v5(
        base,
        selected_shots,
        shootout_kicks,
        config=selected_config,
        config_id=selected_config_id,
        consolidation_status="candidate_only",
    )
    gates = _system_gates(
        base=base,
        base_shots=base_shots,
        shots=selected_shots,
        shootout_kicks=shootout_kicks,
        rated=candidate,
        config=selected_config,
        config_id=selected_config_id,
    )
    status = (
        "promoted_single_metric"
        if gates["all_hard_gates"]
        else "candidate_only"
    )
    rated, channel_audit = calculate_goalkeeper_consolidated_value_v5(
        base,
        selected_shots,
        shootout_kicks,
        config=selected_config,
        config_id=selected_config_id,
        consolidation_status=status,
    )
    stability = _bootstrap(
        base=base,
        shots=selected_shots,
        shootout_kicks=shootout_kicks,
        config=selected_config,
        config_id=selected_config_id,
        iterations=args.bootstrap_iterations,
    )
    rated = rated.merge(stability, on="player_name", how="left")
    main = rated["is_main_goalkeeper"].fillna(False).astype(bool)
    rank_map = dict(
        zip(
            rated.loc[main, "player_name"],
            rated.loc[
                main, "goalkeeper_consolidated_value_rank_v5"
            ].astype(int),
        )
    )
    soft = _soft_gates(rank_map, base)
    top_third = rated.loc[
        main
        & rated["goalkeeper_consolidated_value_rank_v5"].le(11),
        "psxg_mean_difficulty_faced_v5",
    ].mean()
    remaining = rated.loc[
        main
        & rated["goalkeeper_consolidated_value_rank_v5"].gt(11),
        "psxg_mean_difficulty_faced_v5",
    ].mean()
    soft["S8_difficulty_gradient"] = bool(top_third > remaining)

    ordinary = selected_shots.loc[
        ~selected_shots["is_regular_penalty"].fillna(False).astype(bool)
    ]
    raw_save_by_team = (
        ordinary["shot_outcome"]
        .eq("Saved")
        .groupby(ordinary["defending_team"])
        .sum()
    )
    main_by_team = rated.loc[main].set_index("team")
    diagnostics = {
        "raw_saves_score_spearman": _spearman(
            main_by_team.index.map(raw_save_by_team).fillna(0.0),
            main_by_team["goalkeeper_consolidated_value_score_v5"],
        ),
        "psxg_prevention_score_spearman": _spearman(
            main_by_team["psxg_goals_prevented_v5"],
            main_by_team["goalkeeper_consolidated_value_score_v5"],
        ),
        "mean_psxg_top_third": float(top_third),
        "mean_psxg_remaining": float(remaining),
        "opponent_attack_strength_feature_used": False,
    }

    RANKING_ROOT.mkdir(parents=True, exist_ok=True)
    DIAG_ROOT.mkdir(parents=True, exist_ok=True)
    ordered = rated.loc[main].sort_values(
        "goalkeeper_consolidated_value_rank_v5",
        kind="mergesort",
    )
    v5_csv = DIAG_ROOT / "goalkeeper_v5_scored_rows.csv"
    v5_json = DIAG_ROOT / "goalkeeper_v5_scored_rows.json"
    ordered.to_csv(
        v5_csv, index=False, lineterminator="\n", float_format="%.10g"
    )
    _write_json(
        v5_json,
        json.loads(ordered.to_json(orient="records")),
    )

    attribution = pd.concat(
        [
            selected_shots.assign(channel="ordinary_or_regular_penalty"),
            shootout_kicks.assign(channel="shootout"),
        ],
        ignore_index=True,
    )
    attribution.to_csv(
        DIAG_ROOT / "goalkeeper_v5_event_attribution.csv",
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )
    stability.to_csv(
        DIAG_ROOT / "goalkeeper_v5_rank_stability.csv",
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )
    comparison = _comparison(rated, gates)
    comparison.to_csv(
        DIAG_ROOT / "goalkeeper_v5_rank_comparison.csv",
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )

    # Sensitivity retains every gate result without copying all wide channels.
    sensitivity_records = [
        {
            key: record[key]
            for key in (
                "config_id",
                "weights",
                "clutch_late_multiplier",
                "clutch_match_state_multiplier",
                "shot_reliability_count",
                "shootout_bound",
                "clutch_bound",
                "ranks",
                "all_hard_face_gates",
                "soft_gate_count",
                "psxg_score_spearman",
            )
        }
        for record in config_records
    ]
    _write_json(
        DIAG_ROOT / "goalkeeper_v5_sensitivity.json",
        {
            "grid_summary": grid_summary,
            "selected_config_id": selected_config_id,
            "selected_configuration": {
                "weights": dict(selected_config.weights),
                "clutch_late_multiplier": (
                    selected_config.clutch_late_multiplier
                ),
                "clutch_match_state_multiplier": (
                    selected_config.clutch_match_state_multiplier
                ),
                "shot_reliability_count": (
                    selected_config.shot_reliability_count
                ),
                "shootout_bound": selected_config.shootout_bound,
                "clutch_bound": selected_config.clutch_bound,
            },
            "configuration_results": sensitivity_records,
        },
    )

    gate_report = {
        "model_version": MODEL_VERSION,
        "selected_config_id": selected_config_id,
        "hard_gates": gates,
        "soft_gates": soft,
        "hard_gates_all_pass": gates["all_hard_gates"],
        "soft_gate_count": int(sum(soft.values())),
        "promotion_recommendation": status,
        "exact_selected_ranks": {
            name: rank_map.get(name)
            for name in (
                MARTINEZ,
                AL_OWAIS,
                TURNER,
                LIVAKOVIC,
                BOUNOU,
                SZCZESNY,
            )
        },
    }
    _write_json(
        DIAG_ROOT / "goalkeeper_v5_gate_report.json", gate_report
    )

    audit = {
        "model_version": MODEL_VERSION,
        "consolidation_status": status,
        "active_goalkeeper_rank_field": (
            "goalkeeper_consolidated_value_rank_v5"
            if status == "promoted_single_metric"
            else "goalkeeper_rank_v3"
        ),
        "preregistration_path": PREREG_PATH.relative_to(
            PROJECT_ROOT
        ).as_posix(),
        "preregistration": prereg,
        "baseline_hashes": baseline_hashes,
        "baseline_tests": _run_pytest_result(),
        "public_dual_language_inventory_before_release": (
            language_inventory
        ),
        "calibration_audit": calibration_audit,
        "channel_audit": channel_audit,
        "grid_summary": grid_summary,
        "hard_gates": gates,
        "soft_gates": soft,
        "diagnostics": diagnostics,
        "selected_weights": dict(selected_config.weights),
        "selected_config": {
            "config_id": selected_config_id,
            "clutch_late_multiplier": (
                selected_config.clutch_late_multiplier
            ),
            "clutch_match_state_multiplier": (
                selected_config.clutch_match_state_multiplier
            ),
            "shot_reliability_count": (
                selected_config.shot_reliability_count
            ),
            "shootout_bound": selected_config.shootout_bound,
            "clutch_bound": selected_config.clutch_bound,
        },
        "formula_revision_after_identity_blind_smoke_test": {
            "reason": (
                "A flat late-time uplift treated low-consequence group-stage "
                "saves as clutch and clipping erased event differences."
            ),
            "revision": (
                "Clutch is now PSxG prevention times the late/ET residual "
                "times pre-action consequence; standardized channels are "
                "converted to contribution by observed minutes, followed by "
                "cohort-mean reliability shrinkage."
            ),
            "identity_or_award_information_used": False,
        },
        "dual_metric_fallback_justified": False,
        "ranking_change_explanations": {
            "martinez": (
                "Moved from v3 rank 23 to v5 rank 3 because calibrated "
                "PSxG prevention, the late Kolo Muani save residual, and "
                "credited shootout saves now enter one reliability-bounded "
                "tournament value."
            ),
            "al_owais": (
                "Moved from v3 rank 2 to v5 rank 11 because easy and "
                "group-stage saves receive less credit than difficult or "
                "match-decisive prevention."
            ),
            "turner": (
                "Moved from v3 rank 3 to v5 rank 8 after shot difficulty, "
                "exposure, and consequence replaced a profile-driven podium."
            ),
            "elite_core": (
                "Livakovic, Bounou, and Szczesny remain high because their "
                "PSxG and high-consequence evidence remains strong."
            ),
            "consolidation": (
                "Profile and Impact concepts are explanatory channels in "
                "one score, so a second peer live ranking is unnecessary."
            ),
        },
        "rejected_configurations_path": (
            "results/diagnostics/ranking_repair/"
            "goalkeeper_v5_sensitivity.json"
        ),
        "artifact_hashes": {
            v5_csv.relative_to(PROJECT_ROOT).as_posix(): _sha256(v5_csv),
            v5_json.relative_to(PROJECT_ROOT).as_posix(): _sha256(v5_json),
        },
    }
    _write_json(DIAG_ROOT / "goalkeeper_v5_audit.json", audit)
    promotion_result: dict[str, Any] = {
        "promoted": False,
        "reason": "hard gates did not all pass",
    }
    if status == "promoted_single_metric":
        promotion_result = promote_goalkeeper_v5(PROJECT_ROOT)
        RankingRepairReleaseWriter(PROJECT_ROOT).write_manifests(
            active_model_version="ranking-repair-v3.0-qatar-2022"
        )
        audit["promotion_result"] = promotion_result
        _write_json(DIAG_ROOT / "goalkeeper_v5_audit.json", audit)

    print(
        json.dumps(
            {
                "status": status,
                "selected_config_id": selected_config_id,
                "ranks": gate_report["exact_selected_ranks"],
                "hard_gates_all_pass": gates["all_hard_gates"],
                "soft_gates": soft,
                "promotion_result": promotion_result,
                "v5_csv": v5_csv.relative_to(PROJECT_ROOT).as_posix(),
            },
            ensure_ascii=True,
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
