"""Team-match passing-network and build-up involvement features."""

from __future__ import annotations

import ast
import json
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


def _coordinate_x(value: object) -> float:
    """Extract an x coordinate without inventing a missing location."""

    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return float(value[0])
    if not isinstance(value, str) or not value.strip():
        return np.nan
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return np.nan
    return (
        float(parsed[0])
        if isinstance(parsed, (list, tuple)) and len(parsed) >= 2
        else np.nan
    )


def _normalized_entropy(weights: np.ndarray) -> float:
    """Return normalized Shannon entropy for outgoing pass weights."""

    values = np.asarray(weights, dtype=float)
    values = values[values > 0]
    if len(values) <= 1:
        return 0.0
    probability = values / values.sum()
    return float(
        -(probability * np.log(probability)).sum() / np.log(len(probability))
    )


def _parse_player_ids(value: object) -> set[int]:
    """Parse a JSON/list lineup into a player-ID set."""

    if isinstance(value, (list, tuple, set)):
        return {int(item) for item in value}
    if not isinstance(value, str) or not value.strip():
        return set()
    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(value)
        except (TypeError, ValueError, SyntaxError, json.JSONDecodeError):
            continue
        if isinstance(parsed, (list, tuple, set)):
            return {int(item) for item in parsed}
    return set()


def _team_match_network(group: pd.DataFrame) -> list[dict[str, float | int]]:
    """Calculate centralities for one team in one match."""

    graph = nx.DiGraph()
    edge_counts = (
        group.groupby(["player_id", "pass_recipient_id"], sort=False)
        .size()
        .rename("count")
    )
    for (source, target), count in edge_counts.items():
        graph.add_edge(
            int(source),
            int(target),
            weight=float(count),
            distance=1.0 / float(count),
        )
    if graph.number_of_nodes() == 0:
        return []
    pagerank = nx.pagerank(graph, weight="weight")
    betweenness = nx.betweenness_centrality(
        graph,
        weight="distance",
        normalized=True,
    )
    closeness = nx.closeness_centrality(graph, distance="distance")
    try:
        eigenvector = nx.eigenvector_centrality(
            graph,
            weight="weight",
            max_iter=1_000,
        )
    except nx.PowerIterationFailedConvergence:
        eigenvector = {node: np.nan for node in graph}

    records: list[dict[str, float | int]] = []
    for player in graph:
        outgoing = np.asarray(
            [attributes["weight"] for attributes in graph[player].values()],
            dtype=float,
        )
        records.append(
            {
                "player_id": int(player),
                "network_pagerank": float(pagerank[player]),
                "network_betweenness": float(betweenness[player]),
                "network_eigenvector": float(eigenvector[player]),
                "network_closeness": float(closeness[player]),
                "network_entropy": _normalized_entropy(outgoing),
                "network_completed_passes": float(outgoing.sum()),
            }
        )
    return records


def _build_up_involvement(
    events: pd.DataFrame,
    possession_lineups: pd.DataFrame | None,
) -> pd.DataFrame:
    """Calculate involvement before the first final-third entry."""

    ordered = events.sort_values(["match_id", "index"]).copy()
    ordered["_start_x"] = ordered["location"].map(_coordinate_x)
    ordered["_end_x"] = ordered["pass_end_location"].map(_coordinate_x)
    ordered["_furthest_x"] = ordered[["_start_x", "_end_x"]].max(axis=1)
    numerator: dict[int, float] = {}
    denominator: dict[int, float] = {}

    lineup_lookup: dict[tuple[int, str, object], set[int]] = {}
    if possession_lineups is not None and not possession_lineups.empty:
        required = {
            "match_id",
            "attacking_team",
            "possession",
            "attacking_player_ids",
        }
        if required <= set(possession_lineups):
            lineup_lookup = {
                (
                    int(row.match_id),
                    str(row.attacking_team),
                    row.possession,
                ): _parse_player_ids(row.attacking_player_ids)
                for row in possession_lineups.itertuples(index=False)
            }

    grouped = ordered.groupby(
        ["match_id", "team", "possession"],
        sort=False,
    )
    for (match_id, team, possession), chain in grouped:
        entries = np.flatnonzero(chain["_furthest_x"].to_numpy() >= 80.0)
        if not len(entries):
            continue
        before_entry = chain.iloc[: entries[0] + 1]
        contributors = set(
            before_entry["player_id"].dropna().astype(int).tolist()
        )
        contributors.update(
            before_entry["pass_recipient_id"].dropna().astype(int).tolist()
        )
        eligible = lineup_lookup.get(
            (int(match_id), str(team), possession),
            set(
                chain["player_id"].dropna().astype(int).tolist()
                + chain["pass_recipient_id"].dropna().astype(int).tolist()
            ),
        )
        for player in eligible:
            denominator[player] = denominator.get(player, 0.0) + 1.0
        for player in contributors & eligible:
            numerator[player] = numerator.get(player, 0.0) + 1.0
    players = sorted(denominator)
    return pd.DataFrame(
        {
            "player_id": players,
            "build_up_involvement_ratio": [
                numerator.get(player, 0.0) / denominator[player]
                for player in players
            ],
            "build_up_eligible_possessions": [
                denominator[player] for player in players
            ],
        }
    )


def build_passing_network_features(
    events: pd.DataFrame,
    *,
    possession_lineups: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build team-match graph topology and build-up involvement.

    Completed passes form directed, weighted team-match graphs. Centralities
    are calculated within each graph before being averaged across matches, so
    teams with more tournament matches do not simply accumulate larger totals.
    """

    required = {
        "match_id",
        "index",
        "team",
        "possession",
        "type",
        "player_id",
        "pass_recipient_id",
        "pass_outcome",
        "location",
        "pass_end_location",
    }
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(f"Passing-network inputs missing: {sorted(missing)}")
    passes = events.loc[
        events["type"].eq("Pass")
        & events["pass_outcome"].isna()
        & events["player_id"].notna()
        & events["pass_recipient_id"].notna()
    ].copy()
    passes["player_id"] = pd.to_numeric(
        passes["player_id"],
        errors="raise",
    ).astype(int)
    passes["pass_recipient_id"] = pd.to_numeric(
        passes["pass_recipient_id"],
        errors="raise",
    ).astype(int)
    records: list[dict[str, float | int]] = []
    for _, group in passes.groupby(["match_id", "team"], sort=False):
        records.extend(_team_match_network(group))
    if not records:
        return pd.DataFrame(columns=["player_id"])
    per_match = pd.DataFrame(records)
    network = per_match.groupby("player_id", as_index=False).agg(
        network_pagerank=("network_pagerank", "mean"),
        network_betweenness=("network_betweenness", "mean"),
        network_eigenvector=("network_eigenvector", "mean"),
        network_closeness=("network_closeness", "mean"),
        network_entropy=("network_entropy", "mean"),
        network_completed_passes_per_match=(
            "network_completed_passes",
            "mean",
        ),
        network_matches=("network_pagerank", "size"),
    )
    build_up = _build_up_involvement(events, possession_lineups)
    return network.merge(build_up, on="player_id", how="left")


class PassingNetworkTransformer(BaseEstimator, TransformerMixin):
    """Scikit-learn compatible wrapper for passing-network aggregation."""

    def fit(
        self,
        X: pd.DataFrame,
        y: Any = None,
    ) -> "PassingNetworkTransformer":
        """Validate the event schema."""

        build_passing_network_features(X.head(0).copy())
        self.feature_names_in_ = tuple(str(column) for column in X.columns)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Build graph features from the supplied events."""

        if not hasattr(self, "feature_names_in_"):
            raise RuntimeError("PassingNetworkTransformer has not been fitted")
        return build_passing_network_features(X)

