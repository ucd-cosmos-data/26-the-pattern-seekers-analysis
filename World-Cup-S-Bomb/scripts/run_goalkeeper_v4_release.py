#!/usr/bin/env python3
"""Tournament Goalkeeper Impact v4 release driver.

Loads the frozen Pass-8 inputs, values every relevant goalkeeper action with
the preregistered consequence model, evaluates the preregistered candidate
grid, selects weights by the preregistered criteria, and only then reveals
the final ranking and evaluates the publication gates. v3 fields are carried
through untouched.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.goalkeeper_valuation_v3 import (  # noqa: E402
    calibrate_post_shot_xg_v3,
)
from src.models.goalkeeper_tournament_impact_v4 import (  # noqa: E402
    MODEL_VERSION,
    GoalkeeperV4Config,
    SHOOTOUT_CONVERSION_FALLBACK,
    SHOOTOUT_CONVERSION_PRIOR_STRENGTH,
    calculate_goalkeeper_tournament_impact_v4,
    extract_shot_events_v4,
    reconstruct_shootout_kicks,
)

EVENTS_PATH = PROJECT_ROOT / "notebooks" / "all_events.csv"
MATCHES_PATH = PROJECT_ROOT / "data" / "raw" / "matches.csv"
PASS7_RATINGS = (
    PROJECT_ROOT
    / "results/diagnostics/ranking_repair/pass7_goalkeeper_ratings.csv"
)
RANKING_ROOT = PROJECT_ROOT / "results" / "reports" / "ranking"
DIAG_ROOT = PROJECT_ROOT / "results" / "diagnostics" / "ranking_repair"
PREREG_PATH = DIAG_ROOT / "goalkeeper_v4_preregistration.json"

RANDOM_STATE = 42
BOOTSTRAP_ITERATIONS = 500

CONSENSUS_SET = {
    "Damián Emiliano Martínez",
    "Dominik Livaković",
    "Yassine Bounou",
    "Wojciech Szczęsny",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _grid(prereg: dict) -> list[GoalkeeperV4Config]:
    grid = prereg["candidate_grid"]
    combos: list[GoalkeeperV4Config] = []
    for w_ss in grid["w_shot_stopping"]:
        for w_pen in grid["w_regular_penalty"]:
            for w_so in grid["w_shootout"]:
                w_sup = round(1.0 - w_ss - w_pen - w_so, 10)
                if w_sup < 0.05:
                    continue
                for bound in grid["shootout_bound"]:
                    for exponent in grid["leverage_exponent"]:
                        combos.append(
                            GoalkeeperV4Config(
                                weights={
                                    "shot_stopping": w_ss,
                                    "regular_penalty": w_pen,
                                    "shootout": w_so,
                                    "support": w_sup,
                                },
                                shootout_bound=bound,
                                leverage_exponent=exponent,
                            )
                        )
    return combos


def _rank_series(frame: pd.DataFrame) -> pd.Series:
    main = frame["is_main_goalkeeper"].fillna(False).astype(bool)
    return frame.loc[main].set_index("player_name")[
        "goalkeeper_tournament_impact_rank_v4"
    ]


def _per_match_channel_sums(
    base: pd.DataFrame,
    shot_events: pd.DataFrame,
    shootout_kicks: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, list[tuple[float, float, float]]]]:
    """Per-(team, match) sums for the three consequence channels.

    Returns the main-goalkeeper frame and, per team, the list of
    (shot_sum, pen_sum, shootout_sum) triples for each match involving that
    team's goalkeeper. Support percentiles are tournament-level rates and are
    held fixed under resampling (documented in the audit).
    """

    main = base.loc[base["is_main_goalkeeper"].fillna(False).astype(bool)]
    ordinary = shot_events.loc[
        ~shot_events["is_regular_penalty"]
        & shot_events["goal_probability_v3"].notna()
    ]
    ordinary = ordinary.assign(
        value=(ordinary["goal_probability_v3"] - ordinary["goal"])
        * ordinary["leverage_v4"]
    )
    penalties = shot_events.loc[shot_events["is_regular_penalty"]]
    total_pen = len(penalties)
    scored_pen = float(penalties["goal"].sum()) if total_pen else 0.0
    pen_prior = (
        scored_pen
        + SHOOTOUT_CONVERSION_FALLBACK * 8.0
    ) / (total_pen + 8.0)
    penalties = penalties.assign(
        value=(pen_prior - penalties["goal"]) * penalties["leverage_v4"]
    )
    shot_sums = ordinary.groupby(["defending_team", "match_id"])["value"].sum()
    pen_sums = penalties.groupby(["defending_team", "match_id"])["value"].sum()
    so_sums = shootout_kicks.groupby(["defending_team", "match_id"])[
        "goalkeeper_wpa"
    ].sum()
    tables: dict[str, list[tuple[float, float, float]]] = {}
    for team in main["team"]:
        matches = sorted(
            {m for (t2, m) in shot_sums.index if t2 == team}
            | {m for (t2, m) in pen_sums.index if t2 == team}
            | {m for (t2, m) in so_sums.index if t2 == team}
        )
        tables[team] = [
            (
                float(shot_sums.get((team, m), 0.0)),
                float(pen_sums.get((team, m), 0.0)),
                float(so_sums.get((team, m), 0.0)),
            )
            for m in matches
        ]
    return main, tables


def _vectorized_bootstrap(
    main: pd.DataFrame,
    tables: dict[str, list[tuple[float, float, float]]],
    support_centered: np.ndarray,
    combos: list[dict],
    point_ranks: dict[int, pd.Series],
) -> tuple[list[float], dict[int, np.ndarray]]:
    """Match-resampled ranks for every combo from shared channel draws."""

    rng = np.random.default_rng(RANDOM_STATE)
    teams = list(main["team"])
    team_by_player = dict(zip(main["player_name"], main["team"]))
    n_teams = len(teams)
    shot_mat = np.zeros((BOOTSTRAP_ITERATIONS, n_teams))
    pen_mat = np.zeros((BOOTSTRAP_ITERATIONS, n_teams))
    so_mat = np.zeros((BOOTSTRAP_ITERATIONS, n_teams))
    for column, team in enumerate(teams):
        rows = np.asarray(tables[team], dtype=float)
        if rows.size == 0:
            continue
        n_matches = rows.shape[0]
        draws = rng.integers(
            0, n_matches, size=(BOOTSTRAP_ITERATIONS, n_matches)
        )
        sampled = rows[draws]  # (reps, matches, 3)
        sums = sampled.sum(axis=1)
        shot_mat[:, column] = sums[:, 0]
        pen_mat[:, column] = sums[:, 1]
        so_mat[:, column] = sums[:, 2]
    stabilities: list[float] = []
    rank_matrices: dict[int, np.ndarray] = {}
    for position, combo in enumerate(combos):
        weights = combo["weights"]
        bound = combo["shootout_bound"]
        scores = (
            weights["shot_stopping"] * shot_mat
            + weights["regular_penalty"] * pen_mat
            + weights["shootout"] * np.clip(so_mat, -bound, bound)
            + weights["support"] * support_centered[None, :]
        )
        order = (-scores).argsort(axis=1, kind="stable")
        ranks = order.argsort(axis=1) + 1
        point = point_ranks[position]
        top_point = {
            teams.index(team_by_player[name])
            for name, value in point.items()
            if value <= 5
        }
        top_hits = np.isin(
            order[:, :5], sorted(top_point)
        ).sum(axis=1)
        stabilities.append(float(top_hits.mean() / 5.0))
        rank_matrices[position] = ranks
    return stabilities, rank_matrices


def main() -> None:
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    events = pd.read_csv(EVENTS_PATH, low_memory=False)
    matches = pd.read_csv(MATCHES_PATH)
    base = pd.read_csv(PASS7_RATINGS)
    v3_snapshot = base.copy(deep=True)

    predictions, calibration_audit = calibrate_post_shot_xg_v3(events)

    shootout_total = events.loc[
        events["period"].eq(5) & events["type"].eq("Shot")
    ]
    scored = shootout_total["shot_outcome"].eq("Goal").sum()
    conversion = (
        scored + SHOOTOUT_CONVERSION_FALLBACK * SHOOTOUT_CONVERSION_PRIOR_STRENGTH
    ) / (len(shootout_total) + SHOOTOUT_CONVERSION_PRIOR_STRENGTH)

    shootout_matches = sorted(
        events.loc[events["period"].eq(5), "match_id"].unique()
    )
    shootout_kicks = pd.concat(
        [
            reconstruct_shootout_kicks(events, match_id, conversion)
            for match_id in shootout_matches
        ],
        ignore_index=True,
    )

    shot_events_by_exponent = {
        exponent: extract_shot_events_v4(
            events, matches, predictions, leverage_exponent=exponent
        )
        for exponent in prereg["candidate_grid"]["leverage_exponent"]
    }

    # ---- grid evaluation (selection before revealing the winner) ----
    combos = _grid(prereg)
    records = []
    point_ranks: dict[int, pd.Series] = {}
    support_centered_by_exponent: dict[float, np.ndarray] = {}
    for position, config in enumerate(combos):
        shots = shot_events_by_exponent[config.leverage_exponent]
        rated, _ = calculate_goalkeeper_tournament_impact_v4(
            base, shots, shootout_kicks, config=config
        )
        ranks = _rank_series(rated)
        point_ranks[position] = ranks
        if config.leverage_exponent not in support_centered_by_exponent:
            main_rows = rated.loc[
                rated["is_main_goalkeeper"].fillna(False).astype(bool)
            ]
            support_centered_by_exponent[config.leverage_exponent] = (
                main_rows["support_composite_v4"].to_numpy(dtype=float) - 0.5
            )
        decisive_weight = (
            config.weights["shot_stopping"]
            + config.weights["regular_penalty"]
            + config.weights["shootout"]
        )
        records.append(
            {
                "position": position,
                "weights": dict(config.weights),
                "shootout_bound": config.shootout_bound,
                "leverage_exponent": config.leverage_exponent,
                "decisive_weight": decisive_weight,
                "passes_dominance": decisive_weight >= 0.60,
                "ranks": {name: int(value) for name, value in ranks.items()},
                "config": config,
            }
        )

    eligible = [r for r in records if r["passes_dominance"]]
    stability_by_position: dict[int, float] = {}
    rank_matrix_by_position: dict[int, np.ndarray] = {}
    main_frame = None
    for exponent, shots in shot_events_by_exponent.items():
        group = [r for r in eligible if r["leverage_exponent"] == exponent]
        if not group:
            continue
        main_frame, tables = _per_match_channel_sums(
            base, shots, shootout_kicks
        )
        stabilities, rank_matrices = _vectorized_bootstrap(
            main_frame,
            tables,
            support_centered_by_exponent[exponent],
            [
                {
                    "weights": r["weights"],
                    "shootout_bound": r["shootout_bound"],
                }
                for r in group
            ],
            {i: point_ranks[r["position"]] for i, r in enumerate(group)},
        )
        for i, record in enumerate(group):
            stability_by_position[record["position"]] = stabilities[i]
            rank_matrix_by_position[record["position"]] = rank_matrices[i]

    eligible.sort(
        key=lambda r: (
            -stability_by_position[r["position"]],
            -r["decisive_weight"],
        )
    )
    selected = eligible[0]
    best_overlap = stability_by_position[selected["position"]]
    config = selected["config"]
    shots = shot_events_by_exponent[config.leverage_exponent]
    selected_matrix = rank_matrix_by_position[selected["position"]]
    main_frame, _ = _per_match_channel_sums(base, shots, shootout_kicks)
    team_names = list(main_frame["team"])
    name_by_team = dict(zip(main_frame["team"], main_frame["player_name"]))
    point = point_ranks[selected["position"]]
    stability = pd.DataFrame(
        {
            "player_name": [name_by_team[team] for team in team_names],
            "rank_point": [
                int(point[name_by_team[team]]) for team in team_names
            ],
            "rank_p05": np.percentile(selected_matrix, 5, axis=0),
            "rank_p95": np.percentile(selected_matrix, 95, axis=0),
            "rank_std": selected_matrix.std(axis=0),
        }
    )

    # ---- final computation under the selected configuration ----
    rated, audit = calculate_goalkeeper_tournament_impact_v4(
        base, shots, shootout_kicks, config=config
    )

    # ---- gates ----
    main_mask = rated["is_main_goalkeeper"].fillna(False).astype(bool)
    ranks = _rank_series(rated)
    martinez = "Damián Emiliano Martínez"
    gate_results: dict[str, object] = {}
    gate_results["martinez_rank"] = int(ranks.get(martinez, -1))
    gate_results["martinez_first"] = gate_results["martinez_rank"] == 1
    top_five = set(ranks.loc[ranks.le(5)].index)
    gate_results["consensus_in_top_five"] = sorted(top_five & CONSENSUS_SET)
    gate_results["consensus_gate"] = len(top_five & CONSENSUS_SET) >= 3

    # identity shuffle invariance
    shuffled = base.copy()
    shuffled["player_name"] = list(reversed(shuffled["player_name"].tolist()))
    rated_shuffled, _ = calculate_goalkeeper_tournament_impact_v4(
        shuffled, shots, shootout_kicks, config=config
    )
    gate_results["identity_shuffle_invariant"] = bool(
        np.allclose(
            rated["goalkeeper_tournament_impact_raw_v4"].to_numpy(),
            rated_shuffled["goalkeeper_tournament_impact_raw_v4"].to_numpy(),
            equal_nan=True,
        )
    )

    # event-removal monotonicity: Kolo Muani save and shootout events.
    kolo = shots.loc[
        shots["match_id"].eq(3869685)
        & shots["period"].eq(4)
        & shots["shot_outcome"].eq("Saved")
        & shots["minute"].ge(120.0)
    ]
    gate_results["kolo_muani_event_rows"] = int(len(kolo))
    without_kolo = shots.drop(kolo.index)
    rated_no_kolo, _ = calculate_goalkeeper_tournament_impact_v4(
        base, without_kolo, shootout_kicks, config=config
    )

    def _raw(frame: pd.DataFrame, name: str) -> float:
        row = frame.loc[frame["player_name"].eq(name)]
        return float(row["goalkeeper_tournament_impact_raw_v4"].iloc[0])

    gate_results["kolo_muani_removal_lowers_score"] = _raw(
        rated, martinez
    ) > _raw(rated_no_kolo, martinez)
    without_so = shootout_kicks.loc[
        ~shootout_kicks["goalkeeper_player_name"].eq(martinez)
    ]
    rated_no_so, _ = calculate_goalkeeper_tournament_impact_v4(
        base, shots, without_so, config=config
    )
    gate_results["shootout_removal_lowers_score"] = _raw(
        rated, martinez
    ) > _raw(rated_no_so, martinez)

    # v3 preservation: every original column byte-identical.
    v3_columns = [c for c in v3_snapshot.columns]
    gate_results["v3_columns_preserved"] = bool(
        rated[v3_columns].equals(v3_snapshot[v3_columns])
    )

    gate_results["all_gates_pass"] = all(
        [
            gate_results["martinez_first"],
            gate_results["consensus_gate"],
            gate_results["identity_shuffle_invariant"],
            gate_results["kolo_muani_removal_lowers_score"],
            gate_results["shootout_removal_lowers_score"],
            gate_results["v3_columns_preserved"],
        ]
    )

    # ---- artifacts ----
    RANKING_ROOT.mkdir(parents=True, exist_ok=True)
    DIAG_ROOT.mkdir(parents=True, exist_ok=True)
    rated_out = rated.copy()
    rated_out["goalkeeper_event_profile_score_v3"] = rated_out[
        "dedicated_goalkeeper_score_v3"
    ]
    rated_out["model_version_v4"] = MODEL_VERSION
    ordered = rated_out.sort_values(
        "goalkeeper_tournament_impact_rank_v4", na_position="last"
    )
    csv_path = RANKING_ROOT / "goalkeeper_rankings_v4.csv"
    ordered.to_csv(csv_path, index=False, lineterminator="\n")
    json_path = RANKING_ROOT / "goalkeeper_rankings_v4.json"
    json_path.write_text(
        json.dumps(
            json.loads(ordered.to_json(orient="records")), indent=2
        )
        + "\n",
        encoding="utf-8",
    )

    attribution = pd.concat(
        [
            shots.assign(channel="ordinary_or_penalty"),
            shootout_kicks.assign(channel="shootout"),
        ],
        ignore_index=True,
    )
    attribution.to_csv(
        DIAG_ROOT / "goalkeeper_v4_event_attribution.csv",
        index=False,
        lineterminator="\n",
    )
    stability.to_csv(
        DIAG_ROOT / "goalkeeper_v4_rank_stability.csv",
        index=False,
        lineterminator="\n",
    )

    martinez_region = [
        {
            "weights": r["weights"],
            "shootout_bound": r["shootout_bound"],
            "leverage_exponent": r["leverage_exponent"],
            "martinez_rank": r["ranks"].get(martinez),
            "passes_dominance": r["passes_dominance"],
        }
        for r in records
    ]
    sensitivity = {
        "grid_points_evaluated": len(records),
        "grid_points_eligible": len(eligible),
        "selected": {
            "weights": selected["weights"],
            "shootout_bound": selected["shootout_bound"],
            "leverage_exponent": selected["leverage_exponent"],
            "bootstrap_top_five_stability": best_overlap,
        },
        "martinez_rank_across_grid": martinez_region,
        "martinez_rank_distribution": {
            str(rank): sum(
                1
                for r in martinez_region
                if r["martinez_rank"] == rank
            )
            for rank in sorted(
                {r["martinez_rank"] for r in martinez_region}
            )
        },
        "robustness_verdict": (
            "robust"
            if all(
                r["martinez_rank"] == 1
                for r in martinez_region
                if r["passes_dominance"]
            )
            else "not-uniform-across-grid"
        ),
    }
    (DIAG_ROOT / "goalkeeper_v4_sensitivity.json").write_text(
        json.dumps(sensitivity, indent=2) + "\n", encoding="utf-8"
    )

    audit_payload = {
        "model_version": MODEL_VERSION,
        "preregistration": prereg,
        "calibration_audit_carried_from_v3": {
            key: calibration_audit.get(key)
            for key in (
                "ordinary_non_penalty_rows",
                "shootout_rows_excluded",
                "regular_penalty_rows_excluded",
                "gate_passed",
            )
        },
        "shootout_conversion_probability": float(conversion),
        "channel_audit": audit,
        "selected_configuration": sensitivity["selected"],
        "gates": gate_results,
        "artifact_hashes": {
            str(csv_path.relative_to(PROJECT_ROOT)): _sha256(csv_path),
            str(json_path.relative_to(PROJECT_ROOT)): _sha256(json_path),
        },
    }
    (DIAG_ROOT / "goalkeeper_v4_audit.json").write_text(
        json.dumps(audit_payload, indent=2) + "\n", encoding="utf-8"
    )

    print(f"grid: {len(records)} points, {len(eligible)} eligible")
    print(
        "selected:",
        selected["weights"],
        "bound",
        selected["shootout_bound"],
        "exponent",
        selected["leverage_exponent"],
        f"stability {best_overlap:.3f}",
    )
    print("gates:", {k: v for k, v in gate_results.items() if k != "consensus_in_top_five"})
    top = ordered.loc[main_mask].head(10)
    for _, row in top.iterrows():
        print(
            f"  v4 #{int(row['goalkeeper_tournament_impact_rank_v4']):>2} "
            f"{row['player_name'][:28]:28s} {row['team'][:14]:14s} "
            f"score {row['goalkeeper_tournament_impact_score_v4']:.4f} "
            f"(v3 #{int(row['goalkeeper_rank_v3'])})"
        )


if __name__ == "__main__":
    main()
