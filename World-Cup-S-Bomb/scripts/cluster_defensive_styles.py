#!/usr/bin/env python3
"""Discover event-and-360-derived defensive response styles by possession."""

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
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_features.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_clusters.csv"
DEFAULT_SELECTION = PROJECT_ROOT / "results" / "defensive_style_model_selection.csv"
DEFAULT_PROFILES = PROJECT_ROOT / "results" / "defensive_style_profiles.csv"
DEFAULT_SUMMARY = PROJECT_ROOT / "results" / "defensive_style_summary.md"
DEFAULT_MODEL = PROJECT_ROOT / "models" / "defensive_style_kmeans.joblib"
DEFAULT_FIGURE = PROJECT_ROOT / "results" / "figures" / "defensive_style_fingerprints.png"

RANDOM_STATE = 42
STABILITY_SEEDS = (7, 19, 31, 43)

MODEL_FEATURES = [
    "back_line_height",
    "line_height_stability",
    "hull_area_per_defender_log",
    "defensive_width",
    "defensive_depth",
    "behind_ball_share",
    "central_defender_share",
    "near_ball_5_share",
    "near_ball_10_share",
    "nearest_defender_distance",
    "mean_defender_distance",
    "pressure_rate",
    "counterpress_rate",
    "defensive_action_rate",
]

DISPLAY_NAMES = {
    "back_line_height": "Line height",
    "line_height_stability": "Line variation",
    "hull_area_per_defender_log": "Space per defender",
    "defensive_width": "Defensive width",
    "defensive_depth": "Defensive depth",
    "behind_ball_share": "Behind-ball share",
    "central_defender_share": "Central protection",
    "near_ball_5_share": "Immediate proximity",
    "near_ball_10_share": "Close support",
    "nearest_defender_distance": "Nearest pressure distance",
    "mean_defender_distance": "Mean ball distance",
    "pressure_rate": "Pressure-event rate",
    "counterpress_rate": "Counterpress rate",
    "defensive_action_rate": "Defensive-action rate",
}


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    result = np.divide(
        numerator.to_numpy(dtype=float),
        denominator.to_numpy(dtype=float),
        out=np.zeros(len(numerator), dtype=float),
        where=denominator.to_numpy(dtype=float) > 0,
    )
    return pd.Series(result, index=numerator.index)


def engineer_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    attacking_actions = df["pass_count"] + df["carry_count"] + df["dribble_count"] + df["shot_count"]
    observed = df["avg_observed_outfield_defenders"]
    features = pd.DataFrame(index=df.index)
    features["back_line_height"] = df["avg_back_line_height"]
    features["line_height_stability"] = df["std_back_line_height"]
    features["hull_area_per_defender_log"] = np.log1p(
        safe_divide(df["avg_defensive_hull_area"], observed)
    )
    features["defensive_width"] = df["avg_defensive_width"]
    features["defensive_depth"] = df["avg_defensive_depth"]
    features["behind_ball_share"] = safe_divide(df["avg_defenders_behind_ball"], observed)
    features["central_defender_share"] = safe_divide(df["avg_central_defenders"], observed)
    features["near_ball_5_share"] = safe_divide(df["avg_defenders_within_5"], observed)
    features["near_ball_10_share"] = safe_divide(df["avg_defenders_within_10"], observed)
    features["nearest_defender_distance"] = df["avg_nearest_defender_distance"]
    features["mean_defender_distance"] = df["avg_mean_defender_distance"]
    features["pressure_rate"] = safe_divide(df["opponent_pressure_events"], attacking_actions)
    features["counterpress_rate"] = safe_divide(df["opponent_counterpress_events"], attacking_actions)
    features["defensive_action_rate"] = safe_divide(df["opponent_defensive_actions"], attacking_actions)

    eligible = (
        (df["spatial_frame_count"] >= 3)
        & (df["avg_visible_area"] >= 1_000)
        & (observed >= 3)
        & (attacking_actions > 0)
        & features.notna().all(axis=1)
    )
    return features, eligible


def winsorize(
    features: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, tuple[float, float]]]:
    clipped = features.copy()
    limits: dict[str, tuple[float, float]] = {}
    for column in features:
        low, high = features[column].quantile([0.01, 0.99])
        limits[column] = (float(low), float(high))
        clipped[column] = features[column].clip(low, high)
    return clipped, limits


def stability(matrix: np.ndarray, k: int, reference: np.ndarray) -> float:
    scores = []
    for seed in STABILITY_SEEDS:
        labels = KMeans(n_clusters=k, n_init=20, random_state=seed).fit_predict(matrix)
        scores.append(adjusted_rand_score(reference, labels))
    return float(np.mean(scores))


def compare_k(matrix: np.ndarray, k_min: int, k_max: int) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for k in range(k_min, k_max + 1):
        model = KMeans(n_clusters=k, n_init=30, random_state=RANDOM_STATE)
        labels = model.fit_predict(matrix)
        counts = np.bincount(labels, minlength=k)
        records.append(
            {
                "k": k,
                "inertia": model.inertia_,
                "silhouette": silhouette_score(
                    matrix,
                    labels,
                    sample_size=min(5_000, len(matrix)),
                    random_state=RANDOM_STATE,
                ),
                "calinski_harabasz": calinski_harabasz_score(matrix, labels),
                "davies_bouldin": davies_bouldin_score(matrix, labels),
                "stability_ari": stability(matrix, k, labels),
                "smallest_cluster_n": int(counts.min()),
                "smallest_cluster_pct": float(100 * counts.min() / len(labels)),
                "largest_cluster_pct": float(100 * counts.max() / len(labels)),
            }
        )
    output = pd.DataFrame(records)
    output["rank_silhouette"] = output["silhouette"].rank(ascending=False, method="min")
    output["rank_calinski_harabasz"] = output["calinski_harabasz"].rank(
        ascending=False, method="min"
    )
    output["rank_davies_bouldin"] = output["davies_bouldin"].rank(ascending=True, method="min")
    output["rank_stability"] = output["stability_ari"].rank(ascending=False, method="min")
    output["consensus_rank"] = output[
        ["rank_silhouette", "rank_calinski_harabasz", "rank_davies_bouldin", "rank_stability"]
    ].mean(axis=1)
    output["eligible_solution"] = output["smallest_cluster_pct"] >= 3.0
    return output


def choose_k(comparison: pd.DataFrame) -> int:
    candidates = comparison.loc[comparison["eligible_solution"]]
    if candidates.empty:
        candidates = comparison
    return int(
        candidates.sort_values(
            ["consensus_rank", "silhouette", "stability_ari"],
            ascending=[True, False, False],
        ).iloc[0]["k"]
    )


def profiles(
    source: pd.DataFrame,
    features: pd.DataFrame,
    matrix: np.ndarray,
    labels: np.ndarray,
) -> pd.DataFrame:
    raw_columns = [
        "avg_back_line_height",
        "std_back_line_height",
        "avg_defensive_hull_area",
        "avg_defensive_width",
        "avg_defensive_depth",
        "avg_defenders_behind_ball",
        "avg_central_defenders",
        "avg_defenders_within_5",
        "avg_defenders_within_10",
        "avg_nearest_defender_distance",
        "avg_mean_defender_distance",
        "opponent_pressure_events",
        "opponent_counterpress_events",
        "opponent_defensive_actions",
        "shot",
        "goal",
        "xg_generated",
        "entered_penalty_area",
    ]
    raw = source.loc[features.index, raw_columns].copy()
    raw["cluster_id"] = labels
    z = pd.DataFrame(matrix, columns=MODEL_FEATURES, index=features.index)
    z["cluster_id"] = labels
    counts = pd.Series(labels).value_counts().sort_index().rename("possession_count")
    output = pd.concat(
        [
            counts,
            raw.groupby("cluster_id").mean(),
            z.groupby("cluster_id")[MODEL_FEATURES].mean().add_prefix("z_"),
        ],
        axis=1,
    )
    output.index.name = "cluster_id"
    output = output.reset_index()
    output["possession_pct"] = 100 * output["possession_count"] / len(labels)
    return output


def style_labels(profile: pd.DataFrame) -> dict[int, str]:
    candidates: list[tuple[int, str, float]] = []
    for _, row in profile.iterrows():
        scores = {
            "High-Intensity Press": np.mean(
                [
                    row["z_back_line_height"],
                    row["z_pressure_rate"],
                    row["z_counterpress_rate"],
                    row["z_near_ball_5_share"],
                    -row["z_nearest_defender_distance"],
                ]
            ),
            "Set-Piece Compact Shape": np.mean(
                [
                    row["z_nearest_defender_distance"],
                    row["z_mean_defender_distance"],
                    row["z_line_height_stability"],
                    -row["z_hull_area_per_defender_log"],
                ]
            ),
            "Compact Pressure Block": np.mean(
                [
                    row["z_near_ball_5_share"],
                    row["z_near_ball_10_share"],
                    row["z_pressure_rate"],
                    -row["z_defensive_width"],
                    -row["z_hull_area_per_defender_log"],
                ]
            ),
            "Wide Retreating Block": np.mean(
                [
                    row["z_defensive_width"],
                    row["z_hull_area_per_defender_log"],
                    row["z_behind_ball_share"],
                    -row["z_near_ball_5_share"],
                ]
            ),
        }
        label, score = max(scores.items(), key=lambda item: item[1])
        candidates.append((int(row["cluster_id"]), label, float(score)))

    result: dict[int, str] = {}
    grouped: dict[str, list[tuple[int, float]]] = {}
    for cluster_id, label, score in candidates:
        grouped.setdefault(label, []).append((cluster_id, score))
    for label, members in grouped.items():
        members.sort(key=lambda item: item[1], reverse=True)
        for rank, (cluster_id, _) in enumerate(members, start=1):
            result[cluster_id] = label if len(members) == 1 else f"{label} {rank}"
    return result


def top_features(row: pd.Series, count: int = 4) -> str:
    values = {feature: float(row[f"z_{feature}"]) for feature in MODEL_FEATURES}
    strongest = sorted(values.items(), key=lambda item: abs(item[1]), reverse=True)[:count]
    return ", ".join(f"{DISPLAY_NAMES[key]} ({value:+.2f} SD)" for key, value in strongest)


def save_figure(path: Path, profile: pd.DataFrame, labels: dict[int, str]) -> None:
    ordered = profile.sort_values("cluster_id")
    selected_features = [
        "back_line_height",
        "hull_area_per_defender_log",
        "defensive_width",
        "behind_ball_share",
        "near_ball_5_share",
        "pressure_rate",
        "counterpress_rate",
        "defensive_action_rate",
    ]
    values = ordered[[f"z_{feature}" for feature in selected_features]].to_numpy()
    limit = max(1.5, float(np.abs(values).max()))
    fig, ax = plt.subplots(figsize=(13, 6.5))
    image = ax.imshow(values, cmap="RdBu_r", vmin=-limit, vmax=limit, aspect="auto")
    ax.set_xticks(
        range(len(selected_features)),
        [DISPLAY_NAMES[feature] for feature in selected_features],
        rotation=25,
        ha="right",
    )
    ax.set_yticks(
        range(len(ordered)),
        [labels[int(cluster_id)] for cluster_id in ordered["cluster_id"]],
    )
    for row_index in range(values.shape[0]):
        for column_index in range(values.shape[1]):
            value = values[row_index, column_index]
            ax.text(
                column_index,
                row_index,
                f"{value:+.2f}",
                ha="center",
                va="center",
                color="white" if abs(value) > 0.65 * limit else "#17212b",
            )
    ax.set_title("2022 World Cup Defensive Style Fingerprints", fontsize=15, weight="bold")
    colorbar = fig.colorbar(image, ax=ax, pad=0.02)
    colorbar.set_label("Standard deviations from tournament average")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_summary(
    path: Path,
    comparison: pd.DataFrame,
    profile: pd.DataFrame,
    labels: dict[int, str],
    selected_k: int,
    eligible_count: int,
    excluded_count: int,
) -> None:
    selected = comparison.loc[comparison["k"] == selected_k].iloc[0]
    lines = [
        "# Tournament Defensive-Style Clustering",
        "",
        f"- Eligible possessions: {eligible_count:,}",
        f"- Excluded for insufficient spatial coverage: {excluded_count:,}",
        f"- Selected clusters: {selected_k}",
        f"- Silhouette score: {selected['silhouette']:.4f}",
        f"- Stability ARI: {selected['stability_ari']:.4f}",
        "",
        "Labels are deterministic interpretations of event-and-360 centroid fingerprints.",
        "Attacking outcomes were excluded from model fitting and are shown only for evaluation.",
        "",
        "| Cluster | Defensive style | Possessions | Share | Strongest distinctions | Shot allowed | Mean xG allowed |",
        "|---:|---|---:|---:|---|---:|---:|",
    ]
    for _, row in profile.sort_values("cluster_id").iterrows():
        cluster_id = int(row["cluster_id"])
        lines.append(
            f"| {cluster_id} | {labels[cluster_id]} | {int(row['possession_count']):,} | "
            f"{row['possession_pct']:.2f}% | {top_features(row)} | "
            f"{100 * row['shot']:.2f}% | {row['xg_generated']:.4f} |"
        )
    lines.extend(
        [
            "",
            "Spatial features are normalized into the attacking team's coordinate direction.",
            "Visible-area and observed-player thresholds reduce camera-coverage artifacts.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--k-min", type=int, default=3)
    parser.add_argument("--k-max", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = pd.read_csv(args.input)
    features, eligible = engineer_features(source)
    eligible_features = features.loc[eligible, MODEL_FEATURES]
    clipped, limits = winsorize(eligible_features)
    scaler = StandardScaler()
    matrix = scaler.fit_transform(clipped)
    comparison = compare_k(matrix, args.k_min, args.k_max)
    selected_k = choose_k(comparison)
    model = KMeans(n_clusters=selected_k, n_init=50, random_state=RANDOM_STATE)
    cluster_ids = model.fit_predict(matrix)
    profile = profiles(source, eligible_features, matrix, cluster_ids)
    labels = style_labels(profile)
    profile["style_label"] = profile["cluster_id"].map(labels)

    output = source.copy()
    output["defensive_style_cluster"] = -1
    output["defensive_style"] = "Excluded: insufficient spatial coverage"
    output.loc[eligible, "defensive_style_cluster"] = cluster_ids
    output.loc[eligible, "defensive_style"] = pd.Series(
        cluster_ids, index=eligible_features.index
    ).map(labels)

    if output["possession_uid"].duplicated().any():
        raise ValueError("Duplicate possession IDs in defensive cluster output")
    if profile["possession_count"].sum() != eligible.sum():
        raise ValueError("Profile counts do not reconcile with eligible possessions")

    for path in (
        args.output,
        args.selection,
        args.profiles,
        args.summary,
        args.model,
        args.figure,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    comparison.to_csv(args.selection, index=False)
    profile.to_csv(args.profiles, index=False)
    joblib.dump(
        {
            "version": 1,
            "features": MODEL_FEATURES,
            "clip_limits": limits,
            "scaler": scaler,
            "kmeans": model,
            "style_labels": labels,
            "selected_k": selected_k,
        },
        args.model,
    )
    write_summary(
        args.summary,
        comparison,
        profile,
        labels,
        selected_k,
        int(eligible.sum()),
        int((~eligible).sum()),
    )
    save_figure(args.figure, profile, labels)

    selected = comparison.loc[comparison["k"] == selected_k].iloc[0]
    print(f"Selected K={selected_k}; silhouette={selected['silhouette']:.4f}; stability={selected['stability_ari']:.4f}")
    print(f"Wrote defensive clusters to {args.output}")
    print(f"Wrote defensive profiles to {args.profiles}")
    print(f"Wrote defensive model to {args.model}")


if __name__ == "__main__":
    main()
