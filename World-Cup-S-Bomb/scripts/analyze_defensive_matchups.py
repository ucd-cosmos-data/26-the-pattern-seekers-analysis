#!/usr/bin/env python3
"""Analyze attack-defense matchups, team profiles, and defensive player roles."""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "world-cup-sbomb-matplotlib"))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POSSESSIONS = PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_clusters.csv"
DEFAULT_PLAYERS = PROJECT_ROOT / "data" / "processed" / "world_cup_defensive_players.csv"
DEFAULT_MATCHUPS = PROJECT_ROOT / "results" / "style_matchup_effectiveness.csv"
DEFAULT_TEAM_PROFILES = PROJECT_ROOT / "results" / "team_defensive_style_profiles.csv"
DEFAULT_PLAYER_ROLES = PROJECT_ROOT / "results" / "defensive_player_roles.csv"
DEFAULT_SUMMARY = PROJECT_ROOT / "results" / "defensive_matchup_summary.md"
DEFAULT_FIGURE = PROJECT_ROOT / "results" / "figures" / "attacking_defensive_matchups.png"

PLAYER_FEATURES = [
    "pressure_share",
    "counterpress_share",
    "duel_share",
    "interception_share",
    "block_share",
    "clearance_share",
    "recovery_share",
    "foul_share",
    "actor_x",
    "lateral_distance",
]


def wilson_interval(successes: int, observations: int, z: float = 1.96) -> tuple[float, float]:
    if observations == 0:
        return np.nan, np.nan
    p = successes / observations
    denominator = 1 + z**2 / observations
    center = (p + z**2 / (2 * observations)) / denominator
    margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * observations)) / observations) / denominator
    return center - margin, center + margin


def build_matchups(source: pd.DataFrame) -> pd.DataFrame:
    eligible = source[
        (source["attacking_style_cluster"] >= 0) & (source["defensive_style_cluster"] >= 0)
    ].copy()
    records = []
    for (attack, defense), group in eligible.groupby(["attacking_style", "defensive_style"]):
        shot_successes = int(group["shot"].sum())
        shot_low, shot_high = wilson_interval(shot_successes, len(group))
        records.append(
            {
                "attacking_style": attack,
                "defensive_style": defense,
                "possessions": len(group),
                "teams_attacking": group["team"].nunique(),
                "matches": group["match_id"].nunique(),
                "shot_rate": group["shot"].mean(),
                "shot_rate_ci_low": shot_low,
                "shot_rate_ci_high": shot_high,
                "goal_rate": group["goal"].mean(),
                "mean_xg": group["xg_generated"].mean(),
                "total_xg": group["xg_generated"].sum(),
                "penalty_area_entry_rate": group["entered_penalty_area"].mean(),
                "final_third_entry_rate": group["entered_final_third"].mean(),
                "mean_duration_seconds": group["duration_seconds"].mean(),
            }
        )
    return pd.DataFrame(records).sort_values(["defensive_style", "attacking_style"])


def build_team_profiles(source: pd.DataFrame) -> pd.DataFrame:
    eligible = source[source["defensive_style_cluster"] >= 0].copy()
    counts = (
        eligible.groupby(["defending_team", "defensive_style"])
        .size()
        .rename("possessions")
        .reset_index()
    )
    counts["style_share"] = counts["possessions"] / counts.groupby("defending_team")[
        "possessions"
    ].transform("sum")
    pivot = counts.pivot(
        index="defending_team", columns="defensive_style", values="style_share"
    ).fillna(0)
    pivot["defensive_style_entropy"] = -(
        pivot.where(pivot > 0).apply(np.log).mul(pivot).sum(axis=1)
    )
    pivot["dominant_defensive_style"] = pivot.drop(
        columns=["defensive_style_entropy"]
    ).idxmax(axis=1)
    return pivot.reset_index()


def player_features(players: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    total = players["defensive_actions"].replace(0, np.nan)
    features = pd.DataFrame(index=players.index)
    features["pressure_share"] = players["pressure_actions"] / total
    features["counterpress_share"] = players["counterpress_actions"] / total
    features["duel_share"] = players["duels"] / total
    features["interception_share"] = players["interceptions"] / total
    features["block_share"] = players["blocks"] / total
    features["clearance_share"] = players["clearances"] / total
    features["recovery_share"] = players["ball_recoveries"] / total
    features["foul_share"] = players["fouls_committed"] / total
    features["actor_x"] = players["avg_actor_x_when_acting"]
    features["lateral_distance"] = abs(players["avg_actor_y_when_acting"] - 40.0)
    eligible = (
        (players["defensive_actions"] >= 20)
        & (players["actor_frame_count"] >= 10)
        & features.notna().all(axis=1)
    )
    return features, eligible


def choose_player_k(matrix: np.ndarray) -> tuple[int, pd.DataFrame]:
    records = []
    for k in range(3, 7):
        model = KMeans(n_clusters=k, random_state=42, n_init=30)
        labels = model.fit_predict(matrix)
        counts = np.bincount(labels, minlength=k)
        records.append(
            {
                "k": k,
                "silhouette": silhouette_score(matrix, labels),
                "smallest_cluster_pct": 100 * counts.min() / len(labels),
            }
        )
    comparison = pd.DataFrame(records)
    eligible = comparison[comparison["smallest_cluster_pct"] >= 5]
    if eligible.empty:
        eligible = comparison
    return int(eligible.sort_values("silhouette", ascending=False).iloc[0]["k"]), comparison


def player_role_labels(centers: pd.DataFrame) -> dict[int, str]:
    candidates = []
    for cluster_id, row in centers.iterrows():
        scores = {
            "Pressing Disruptor": np.mean(
                [row["pressure_share"], row["counterpress_share"], -row["actor_x"]]
            ),
            "Deep Stopper": np.mean(
                [row["clearance_share"], row["block_share"], row["actor_x"]]
            ),
            "Ball Winner": np.mean(
                [row["duel_share"], row["interception_share"], row["recovery_share"]]
            ),
            "Wide Enforcer": np.mean(
                [row["lateral_distance"], row["duel_share"], row["pressure_share"]]
            ),
        }
        label, score = max(scores.items(), key=lambda item: item[1])
        candidates.append((int(cluster_id), label, float(score)))
    result = {}
    grouped: dict[str, list[tuple[int, float]]] = {}
    for cluster_id, label, score in candidates:
        grouped.setdefault(label, []).append((cluster_id, score))
    for label, members in grouped.items():
        members.sort(key=lambda item: item[1], reverse=True)
        for rank, (cluster_id, _) in enumerate(members, start=1):
            result[cluster_id] = label if len(members) == 1 else f"{label} {rank}"
    return result


def build_player_roles(players: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    features, eligible = player_features(players)
    clipped = features.loc[eligible].copy()
    for column in clipped:
        low, high = clipped[column].quantile([0.01, 0.99])
        clipped[column] = clipped[column].clip(low, high)
    scaler = StandardScaler()
    matrix = scaler.fit_transform(clipped)
    k, comparison = choose_player_k(matrix)
    model = KMeans(n_clusters=k, random_state=42, n_init=50)
    labels = model.fit_predict(matrix)
    centers = pd.DataFrame(
        model.cluster_centers_, columns=PLAYER_FEATURES, index=range(k)
    )
    roles = player_role_labels(centers)

    output = players.copy()
    output["player_role_cluster"] = -1
    output["defensive_player_role"] = "Excluded: limited defensive sample"
    output.loc[eligible, "player_role_cluster"] = labels
    output.loc[eligible, "defensive_player_role"] = pd.Series(
        labels, index=features.loc[eligible].index
    ).map(roles)
    metrics = {
        "eligible_players": int(eligible.sum()),
        "excluded_players": int((~eligible).sum()),
        "selected_k": k,
        "silhouette": float(
            comparison.loc[comparison["k"] == k, "silhouette"].iloc[0]
        ),
    }
    return output, metrics


def save_matchup_figure(path: Path, matchups: pd.DataFrame) -> None:
    attack_order = ["Patient Build-up", "Short Under Pressure", "Direct Long Play"]
    defense_order = sorted(matchups["defensive_style"].unique())
    xg = matchups.pivot(
        index="attacking_style", columns="defensive_style", values="mean_xg"
    ).reindex(index=attack_order, columns=defense_order)
    box = matchups.pivot(
        index="attacking_style",
        columns="defensive_style",
        values="penalty_area_entry_rate",
    ).reindex(index=attack_order, columns=defense_order)
    counts = matchups.pivot(
        index="attacking_style", columns="defensive_style", values="possessions"
    ).reindex(index=attack_order, columns=defense_order)

    fig, axes = plt.subplots(1, 2, figsize=(17, 6.5))
    for ax, values, title, format_string in (
        (axes[0], xg, "Mean xG per possession", ".4f"),
        (axes[1], 100 * box, "Penalty-area entry rate (%)", ".1f"),
    ):
        image = ax.imshow(values.to_numpy(), cmap="YlGnBu", aspect="auto")
        ax.set_xticks(range(len(defense_order)), defense_order, rotation=28, ha="right")
        ax.set_yticks(range(len(attack_order)), attack_order)
        for row in range(len(attack_order)):
            for column in range(len(defense_order)):
                value = values.iloc[row, column]
                n = int(counts.iloc[row, column])
                text = f"{value:{format_string}}\nn={n:,}"
                ax.text(column, row, text, ha="center", va="center", fontsize=9)
        ax.set_title(title, fontsize=13, weight="bold")
        fig.colorbar(image, ax=ax, shrink=0.78, pad=0.02)
    fig.suptitle(
        "2022 World Cup: Attacking Style × Defensive Style Outcomes",
        fontsize=16,
        weight="bold",
    )
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_summary(
    path: Path,
    matchups: pd.DataFrame,
    team_profiles: pd.DataFrame,
    player_roles: pd.DataFrame,
    player_metrics: dict[str, float],
) -> None:
    reliable = matchups[matchups["possessions"] >= 100].copy()
    best = (
        reliable.sort_values(["defensive_style", "mean_xg"], ascending=[True, False])
        .groupby("defensive_style")
        .head(1)
    )
    lines = [
        "# Defensive Styles, Matchups, and Player Roles",
        "",
        "## Best observed attacking matchup by defensive style",
        "",
        "These are observational tournament results, not yet causal coaching recommendations.",
        "",
        "| Defensive style | Highest-xG attacking style | Possessions | Mean xG | Shot rate | Box-entry rate |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for _, row in best.iterrows():
        lines.append(
            f"| {row['defensive_style']} | {row['attacking_style']} | {int(row['possessions']):,} | "
            f"{row['mean_xg']:.4f} | {100 * row['shot_rate']:.2f}% | "
            f"{100 * row['penalty_area_entry_rate']:.2f}% |"
        )
    lines.extend(
        [
            "",
            "## Defensive player roles",
            "",
            f"- Eligible named players: {int(player_metrics['eligible_players']):,}",
            f"- Excluded for limited samples: {int(player_metrics['excluded_players']):,}",
            f"- Selected player-role clusters: {int(player_metrics['selected_k'])}",
            f"- Player-role silhouette: {player_metrics['silhouette']:.4f}",
            "",
            "| Player role | Players | Example high-volume actors |",
            "|---|---:|---|",
        ]
    )
    eligible_players = player_roles[player_roles["player_role_cluster"] >= 0]
    for role, group in eligible_players.groupby("defensive_player_role"):
        examples = ", ".join(
            f"{row.player} ({row.team})"
            for row in group.nlargest(3, "defensive_actions").itertuples()
        )
        lines.append(f"| {role} | {len(group)} | {examples} |")
    lines.extend(
        [
            "",
            "Player roles use defensive action mix and 360 actor location. Counts are not per-90 because lineup-minute normalization has not yet been added.",
            "",
            f"Team defensive profiles cover {team_profiles['defending_team'].nunique()} teams.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--possessions", type=Path, default=DEFAULT_POSSESSIONS)
    parser.add_argument("--players", type=Path, default=DEFAULT_PLAYERS)
    parser.add_argument("--matchups", type=Path, default=DEFAULT_MATCHUPS)
    parser.add_argument("--team-profiles", type=Path, default=DEFAULT_TEAM_PROFILES)
    parser.add_argument("--player-roles", type=Path, default=DEFAULT_PLAYER_ROLES)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    possessions = pd.read_csv(args.possessions)
    players = pd.read_csv(args.players)
    matchups = build_matchups(possessions)
    team_profiles = build_team_profiles(possessions)
    player_roles, player_metrics = build_player_roles(players)

    if len(matchups) != (
        possessions.loc[
            (possessions["attacking_style_cluster"] >= 0)
            & (possessions["defensive_style_cluster"] >= 0),
            ["attacking_style", "defensive_style"],
        ]
        .drop_duplicates()
        .shape[0]
    ):
        raise ValueError("Matchup rows do not reconcile with observed style pairs")
    if team_profiles["defending_team"].nunique() != 32:
        raise ValueError("Team defensive profiles do not cover all 32 teams")

    for path in (
        args.matchups,
        args.team_profiles,
        args.player_roles,
        args.summary,
        args.figure,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
    matchups.to_csv(args.matchups, index=False)
    team_profiles.to_csv(args.team_profiles, index=False)
    player_roles.to_csv(args.player_roles, index=False)
    save_matchup_figure(args.figure, matchups)
    write_summary(
        args.summary, matchups, team_profiles, player_roles, player_metrics
    )
    print(f"Wrote {len(matchups)} matchup cells to {args.matchups}")
    print(f"Wrote {len(team_profiles)} team profiles to {args.team_profiles}")
    print(f"Wrote {len(player_roles)} player profiles to {args.player_roles}")
    print(f"Wrote summary to {args.summary}")
    print(f"Wrote figure to {args.figure}")


if __name__ == "__main__":
    main()
