#!/usr/bin/env python3
"""Discover tournament-wide attacking styles from possession-level features.

The script compares K-Means solutions, selects a cluster count using internal
validation and stability, fits the final model, and exports assignments,
profiles, diagnostics, a reusable model bundle, and a PCA visualization.
Outcome variables are explicitly excluded from model features.
"""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "world-cup-sbomb-matplotlib"))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "world_cup_possessions.csv"
DEFAULT_ASSIGNMENTS = PROJECT_ROOT / "data" / "processed" / "world_cup_possession_clusters.csv"
DEFAULT_MODEL_SELECTION = PROJECT_ROOT / "results" / "attacking_style_model_selection.csv"
DEFAULT_PROFILES = PROJECT_ROOT / "results" / "attacking_style_profiles.csv"
DEFAULT_SUMMARY = PROJECT_ROOT / "results" / "attacking_style_summary.md"
DEFAULT_MODEL = PROJECT_ROOT / "models" / "attacking_style_kmeans.joblib"
DEFAULT_FIGURE = PROJECT_ROOT / "results" / "figures" / "attacking_style_pca.png"

RANDOM_STATE = 42
K_MIN = 3
K_MAX = 10
SILHOUETTE_SAMPLE = 5_000
STABILITY_SEEDS = (7, 19, 31, 43)

# Every model input describes how the attack develops. Outcome columns such as
# shot, goal, xG, final-third entry, and penalty-area entry are intentionally
# absent to prevent target leakage.
MODEL_FEATURES = [
    "duration_log",
    "players_involved",
    "pass_count_log",
    "pass_completion_pct",
    "average_pass_length",
    "progressive_pass_share",
    "long_ball_share",
    "switch_share",
    "cross_share",
    "carry_count_log",
    "progressive_carry_share",
    "total_carry_distance_log",
    "longest_carry_distance",
    "dribble_count_log",
    "net_forward_distance",
    "total_forward_progression_log",
    "directness_ratio",
    "progression_speed",
    "width_std_y",
    "width_span_y",
    "under_pressure_rate",
    "opponent_pressure_rate",
]

FORBIDDEN_OUTCOME_TOKENS = (
    "shot",
    "goal",
    "xg",
    "dangerous",
    "entered_final",
    "entered_penalty",
    "final_third_entries",
    "penalty_area_entries",
)

DISPLAY_NAMES = {
    "duration_log": "Possession duration",
    "players_involved": "Players involved",
    "pass_count_log": "Pass volume",
    "pass_completion_pct": "Pass completion",
    "average_pass_length": "Pass length",
    "progressive_pass_share": "Progressive-pass share",
    "long_ball_share": "Long-ball share",
    "switch_share": "Switch share",
    "cross_share": "Cross share",
    "carry_count_log": "Carry volume",
    "progressive_carry_share": "Progressive-carry share",
    "total_carry_distance_log": "Carry distance",
    "longest_carry_distance": "Longest carry",
    "dribble_count_log": "Dribble volume",
    "net_forward_distance": "Net progression",
    "total_forward_progression_log": "Total progression",
    "directness_ratio": "Directness",
    "progression_speed": "Progression speed",
    "width_std_y": "Width variation",
    "width_span_y": "Width span",
    "under_pressure_rate": "Under-pressure rate",
    "opponent_pressure_rate": "Opponent pressure rate",
}


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    result = np.divide(
        numerator.to_numpy(dtype=float),
        denominator.to_numpy(dtype=float),
        out=np.zeros(len(numerator), dtype=float),
        where=denominator.to_numpy(dtype=float) > 0,
    )
    return pd.Series(result, index=numerator.index)


def engineer_model_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    # Shots are outcomes for downstream effectiveness models, so they must not
    # affect eligibility or any derived model-input denominator.
    attack_actions = df["pass_count"] + df["carry_count"] + df["dribble_count"]
    eligible = attack_actions > 0
    model = pd.DataFrame(index=df.index)

    model["duration_log"] = np.log1p(df["duration_seconds"])
    model["players_involved"] = df["players_involved"]
    model["pass_count_log"] = np.log1p(df["pass_count"])
    model["pass_completion_pct"] = df["pass_completion_pct"]
    model["average_pass_length"] = df["average_pass_length"]
    model["progressive_pass_share"] = safe_divide(df["progressive_pass_count"], df["pass_count"])
    model["long_ball_share"] = safe_divide(df["long_ball_count"], df["pass_count"])
    model["switch_share"] = safe_divide(df["switch_count"], df["pass_count"])
    model["cross_share"] = safe_divide(df["cross_count"], df["pass_count"])
    model["carry_count_log"] = np.log1p(df["carry_count"])
    model["progressive_carry_share"] = safe_divide(df["progressive_carry_count"], df["carry_count"])
    model["total_carry_distance_log"] = np.log1p(df["total_carry_distance"])
    model["longest_carry_distance"] = df["longest_carry_distance"]
    model["dribble_count_log"] = np.log1p(df["dribble_count"])
    model["net_forward_distance"] = df["net_forward_distance"]
    model["total_forward_progression_log"] = np.log1p(df["total_forward_progression"])
    model["directness_ratio"] = df["directness_ratio"]
    model["progression_speed"] = df["progression_speed"]
    model["width_std_y"] = df["width_std_y"]
    model["width_span_y"] = df["width_span_y"]
    model["under_pressure_rate"] = safe_divide(df["under_pressure_actions"], attack_actions)
    model["opponent_pressure_rate"] = safe_divide(df["opponent_pressure_events"], attack_actions)

    if list(model.columns) != MODEL_FEATURES:
        raise RuntimeError("Engineered feature order differs from MODEL_FEATURES")
    forbidden = [feature for feature in MODEL_FEATURES if any(token in feature.lower() for token in FORBIDDEN_OUTCOME_TOKENS)]
    if forbidden:
        raise ValueError(f"Outcome leakage detected in model features: {forbidden}")
    if model.loc[eligible].isna().any().any():
        raise ValueError("Eligible model features contain missing values")
    return model, eligible


def winsorize(
    features: pd.DataFrame,
    limits: dict[str, tuple[float, float]] | None = None,
) -> tuple[pd.DataFrame, dict[str, tuple[float, float]]]:
    clipped = features.copy()
    if limits is None:
        limits = {}
        for column in features:
            low, high = features[column].quantile([0.01, 0.99])
            limits[column] = (float(low), float(high))
    for column, (low, high) in limits.items():
        clipped[column] = clipped[column].clip(low, high)
    return clipped, limits


def stability_score(matrix: np.ndarray, k: int, reference_labels: np.ndarray) -> float:
    scores = []
    for seed in STABILITY_SEEDS:
        candidate = KMeans(n_clusters=k, random_state=seed, n_init=20).fit_predict(matrix)
        scores.append(adjusted_rand_score(reference_labels, candidate))
    return float(np.mean(scores))


def compare_cluster_counts(matrix: np.ndarray, k_min: int, k_max: int) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    sample_size = min(SILHOUETTE_SAMPLE, len(matrix))
    for k in range(k_min, k_max + 1):
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=30)
        labels = model.fit_predict(matrix)
        counts = np.bincount(labels, minlength=k)
        records.append(
            {
                "k": k,
                "inertia": model.inertia_,
                "silhouette": silhouette_score(
                    matrix,
                    labels,
                    sample_size=sample_size,
                    random_state=RANDOM_STATE,
                ),
                "calinski_harabasz": calinski_harabasz_score(matrix, labels),
                "davies_bouldin": davies_bouldin_score(matrix, labels),
                "stability_ari": stability_score(matrix, k, labels),
                "smallest_cluster_n": int(counts.min()),
                "smallest_cluster_pct": float(100 * counts.min() / len(labels)),
                "largest_cluster_pct": float(100 * counts.max() / len(labels)),
            }
        )

    comparison = pd.DataFrame(records)
    # Rank-based consensus avoids letting differently-scaled diagnostics dominate.
    comparison["rank_silhouette"] = comparison["silhouette"].rank(ascending=False, method="min")
    comparison["rank_calinski_harabasz"] = comparison["calinski_harabasz"].rank(ascending=False, method="min")
    comparison["rank_davies_bouldin"] = comparison["davies_bouldin"].rank(ascending=True, method="min")
    comparison["rank_stability"] = comparison["stability_ari"].rank(ascending=False, method="min")
    comparison["consensus_rank"] = comparison[
        ["rank_silhouette", "rank_calinski_harabasz", "rank_davies_bouldin", "rank_stability"]
    ].mean(axis=1)
    # Avoid selecting a solution with a tiny, hard-to-interpret cluster.
    comparison["eligible_solution"] = comparison["smallest_cluster_pct"] >= 3.0
    return comparison


def select_k(comparison: pd.DataFrame) -> int:
    eligible = comparison.loc[comparison["eligible_solution"]].copy()
    if eligible.empty:
        eligible = comparison.copy()
    best = eligible.sort_values(
        ["consensus_rank", "silhouette", "stability_ari"],
        ascending=[True, False, False],
    ).iloc[0]
    return int(best["k"])


def cluster_profiles(
    raw: pd.DataFrame,
    engineered: pd.DataFrame,
    scaled: np.ndarray,
    labels: np.ndarray,
) -> pd.DataFrame:
    profile_source = engineered.copy()
    profile_source["cluster_id"] = labels
    z_profile = pd.DataFrame(scaled, columns=MODEL_FEATURES, index=engineered.index)
    z_profile["cluster_id"] = labels

    raw_profile_columns = [
        "duration_seconds",
        "players_involved",
        "pass_count",
        "pass_completion_pct",
        "average_pass_length",
        "progressive_pass_count",
        "long_ball_count",
        "switch_count",
        "cross_count",
        "carry_count",
        "progressive_carry_count",
        "total_carry_distance",
        "longest_carry_distance",
        "dribble_count",
        "net_forward_distance",
        "total_forward_progression",
        "directness_ratio",
        "progression_speed",
        "width_std_y",
        "width_span_y",
        "under_pressure_actions",
        "opponent_pressure_events",
        "shot",
        "goal",
        "xg_generated",
        "entered_penalty_area",
    ]
    raw_with_cluster = raw.loc[engineered.index, raw_profile_columns].copy()
    raw_with_cluster["cluster_id"] = labels
    raw_means = raw_with_cluster.groupby("cluster_id").mean()
    z_means = z_profile.groupby("cluster_id")[MODEL_FEATURES].mean().add_prefix("z_")
    counts = pd.Series(labels).value_counts().sort_index().rename("possession_count")
    profiles = pd.concat([counts, raw_means, z_means], axis=1)
    profiles.index.name = "cluster_id"
    profiles = profiles.reset_index()
    profiles["possession_pct"] = 100 * profiles["possession_count"] / len(labels)
    return profiles


def make_style_labels(profiles: pd.DataFrame) -> dict[int, str]:
    """Assign deterministic, descriptive names from each centroid fingerprint."""
    candidates: list[tuple[int, str, float]] = []
    for _, row in profiles.iterrows():
        cluster_id = int(row["cluster_id"])
        scores = {
            "Patient Build-up": np.mean(
                [row["z_duration_log"], row["z_pass_count_log"], row["z_players_involved"], row["z_width_span_y"]]
            ),
            "Fast Vertical": np.mean(
                [row["z_progression_speed"], row["z_directness_ratio"], row["z_net_forward_distance"]]
            ),
            "Direct Long Play": np.mean(
                [row["z_average_pass_length"], row["z_long_ball_share"], row["z_progression_speed"]]
            ),
            "Carry-Oriented": np.mean(
                [row["z_carry_count_log"], row["z_total_carry_distance_log"], row["z_longest_carry_distance"]]
            ),
            "Wide Delivery": np.mean(
                [row["z_cross_share"], row["z_switch_share"], row["z_width_span_y"]]
            ),
            "Short Under Pressure": np.mean(
                [
                    row["z_under_pressure_rate"],
                    row["z_opponent_pressure_rate"],
                    -row["z_duration_log"],
                    -row["z_total_forward_progression_log"],
                ]
            ),
        }
        style, score = max(scores.items(), key=lambda item: item[1])
        candidates.append((cluster_id, style, float(score)))

    labels: dict[int, str] = {}
    grouped: dict[str, list[tuple[int, float]]] = {}
    for cluster_id, style, score in candidates:
        grouped.setdefault(style, []).append((cluster_id, score))
    for style, members in grouped.items():
        members.sort(key=lambda item: item[1], reverse=True)
        for rank, (cluster_id, _) in enumerate(members, start=1):
            labels[cluster_id] = style if len(members) == 1 else f"{style} {rank}"
    return labels


def top_profile_features(profile: pd.Series, count: int = 3) -> str:
    z_values = {feature: float(profile[f"z_{feature}"]) for feature in MODEL_FEATURES}
    ordered = sorted(z_values.items(), key=lambda item: abs(item[1]), reverse=True)[:count]
    return ", ".join(f"{DISPLAY_NAMES[feature]} ({value:+.2f} SD)" for feature, value in ordered)


def write_summary(
    path: Path,
    input_path: Path,
    assignments_path: Path,
    comparison: pd.DataFrame,
    profiles: pd.DataFrame,
    labels: dict[int, str],
    eligible_count: int,
    excluded_count: int,
    selected_k: int,
) -> None:
    selected = comparison.loc[comparison["k"] == selected_k].iloc[0]
    lines = [
        "# Tournament Attacking-Style Clustering",
        "",
        f"- Input: `{input_path.relative_to(PROJECT_ROOT)}`",
        f"- Assignment output: `{assignments_path.relative_to(PROJECT_ROOT)}`",
        f"- Eligible attacking possessions: {eligible_count:,}",
        f"- Excluded records with no attacking action: {excluded_count:,}",
        f"- Selected clusters: {selected_k}",
        f"- Silhouette score: {selected['silhouette']:.4f}",
        f"- Stability ARI: {selected['stability_ari']:.4f}",
        f"- Smallest cluster: {selected['smallest_cluster_pct']:.2f}%",
        "",
        "The labels below are deterministic interpretations of centroid fingerprints, not preassigned tactical classes.",
        "Shot, goal, xG, final-third entries, and penalty-area entries were excluded from model fitting and appear only as post-clustering effectiveness summaries.",
        "",
        "## Discovered styles",
        "",
        "| Cluster | Interpreted style | Possessions | Share | Top distinguishing features | Shot rate | Mean xG |",
        "|---:|---|---:|---:|---|---:|---:|",
    ]
    for _, profile in profiles.sort_values("cluster_id").iterrows():
        cluster_id = int(profile["cluster_id"])
        lines.append(
            f"| {cluster_id} | {labels[cluster_id]} | {int(profile['possession_count']):,} | "
            f"{profile['possession_pct']:.2f}% | {top_profile_features(profile)} | "
            f"{100 * profile['shot']:.2f}% | {profile['xg_generated']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "These are attacking styles discovered from event-derived possession features. General StatsBomb 360 freeze frames are not present in `all_events.csv`, so exact defensive shape and compactness are outside this stage.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def save_pca_figure(
    path: Path,
    matrix: np.ndarray,
    labels: np.ndarray,
    style_labels: dict[int, str],
) -> None:
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    projected = pca.fit_transform(matrix)
    rng = np.random.default_rng(RANDOM_STATE)
    sample = rng.choice(len(projected), size=min(6_000, len(projected)), replace=False)

    fig, ax = plt.subplots(figsize=(12, 8))
    cmap = plt.get_cmap("tab10")
    for cluster_id in sorted(np.unique(labels)):
        mask = labels[sample] == cluster_id
        points = projected[sample][mask]
        ax.scatter(
            points[:, 0],
            points[:, 1],
            s=10,
            alpha=0.35,
            color=cmap(cluster_id % 10),
            label=f"{cluster_id}: {style_labels[cluster_id]}",
            linewidths=0,
        )
    ax.set_title("2022 World Cup Possession Styles - PCA Projection", fontsize=15, weight="bold")
    ax.set_xlabel(f"PC1 ({100 * pca.explained_variance_ratio_[0]:.1f}% variance)")
    ax.set_ylabel(f"PC2 ({100 * pca.explained_variance_ratio_[1]:.1f}% variance)")
    ax.grid(alpha=0.2)
    ax.legend(loc="best", frameon=True, fontsize=9)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def validate_outputs(
    source: pd.DataFrame,
    assignments: pd.DataFrame,
    profiles: pd.DataFrame,
    eligible: pd.Series,
    selected_k: int,
) -> None:
    if len(source) != len(assignments):
        raise ValueError("Assignment output row count differs from source")
    if assignments["possession_uid"].duplicated().any():
        raise ValueError("Assignment output contains duplicate possession IDs")
    if assignments.loc[eligible, "attacking_style_cluster"].lt(0).any():
        raise ValueError("An eligible possession lacks a cluster")
    if assignments.loc[~eligible, "attacking_style_cluster"].ne(-1).any():
        raise ValueError("An excluded possession was assigned to a fitted cluster")
    if profiles["cluster_id"].nunique() != selected_k:
        raise ValueError("Profile count differs from selected cluster count")
    if int(profiles["possession_count"].sum()) != int(eligible.sum()):
        raise ValueError("Profile counts do not sum to eligible possessions")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--model-selection", type=Path, default=DEFAULT_MODEL_SELECTION)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--k-min", type=int, default=K_MIN)
    parser.add_argument("--k-max", type=int, default=K_MAX)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.is_file():
        raise FileNotFoundError(
            f"{args.input} does not exist. Run scripts/preprocess_possessions.py first."
        )
    if args.k_min < 2 or args.k_max < args.k_min:
        raise ValueError("Require 2 <= k-min <= k-max")

    source = pd.read_csv(args.input)
    engineered, eligible = engineer_model_features(source)
    eligible_features = engineered.loc[eligible, MODEL_FEATURES]
    clipped, clip_limits = winsorize(eligible_features)
    scaler = StandardScaler()
    matrix = scaler.fit_transform(clipped)

    comparison = compare_cluster_counts(matrix, args.k_min, args.k_max)
    selected_k = select_k(comparison)
    final_model = KMeans(n_clusters=selected_k, random_state=RANDOM_STATE, n_init=50)
    labels = final_model.fit_predict(matrix)

    profiles = cluster_profiles(source, eligible_features, matrix, labels)
    style_labels = make_style_labels(profiles)
    profiles["style_label"] = profiles["cluster_id"].map(style_labels)

    assignments = source.copy()
    assignments["attacking_style_cluster"] = -1
    assignments["attacking_style"] = "Excluded: no attacking action"
    assignments.loc[eligible, "attacking_style_cluster"] = labels
    assignments.loc[eligible, "attacking_style"] = pd.Series(labels, index=eligible_features.index).map(style_labels)

    validate_outputs(source, assignments, profiles, eligible, selected_k)

    for path in (
        args.assignments,
        args.model_selection,
        args.profiles,
        args.summary,
        args.model,
        args.figure,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)

    assignments.to_csv(args.assignments, index=False)
    comparison.to_csv(args.model_selection, index=False)
    profiles.to_csv(args.profiles, index=False)
    joblib.dump(
        {
            "version": 1,
            "model_features": MODEL_FEATURES,
            "clip_limits": clip_limits,
            "scaler": scaler,
            "kmeans": final_model,
            "style_labels": style_labels,
            "selected_k": selected_k,
            "random_state": RANDOM_STATE,
        },
        args.model,
    )
    write_summary(
        args.summary,
        args.input,
        args.assignments,
        comparison,
        profiles,
        style_labels,
        int(eligible.sum()),
        int((~eligible).sum()),
        selected_k,
    )
    save_pca_figure(args.figure, matrix, labels, style_labels)

    selected = comparison.loc[comparison["k"] == selected_k].iloc[0]
    print(f"Selected K={selected_k} from {args.k_min}..{args.k_max}")
    print(f"Silhouette={selected['silhouette']:.4f}; stability ARI={selected['stability_ari']:.4f}")
    print(f"Wrote assignments to {args.assignments}")
    print(f"Wrote profiles to {args.profiles}")
    print(f"Wrote summary to {args.summary}")
    print(f"Wrote model bundle to {args.model}")
    print(f"Wrote PCA figure to {args.figure}")


if __name__ == "__main__":
    main()
