"""Preparation of causal event queries and anonymous 360 actor tokens."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.models.valuation import ROLE_DIMENSIONS


@dataclass(frozen=True)
class AttentionArrays:
    """Dense arrays consumed by the lightweight attention experiment."""

    event_features: np.ndarray
    tokens: np.ndarray
    token_padding_mask: np.ndarray
    targets: dict[str, np.ndarray]
    auxiliary_targets: dict[str, np.ndarray]
    match_ids: np.ndarray
    action_indices: np.ndarray
    event_feature_names: tuple[str, ...]
    token_feature_names: tuple[str, ...]


def _truthy(series: pd.Series) -> pd.Series:
    return series.fillna(False).astype(str).str.lower().isin(
        {"true", "1", "yes"}
    )


def build_attention_arrays_from_csv(
    actions: pd.DataFrame,
    player_roles: pd.DataFrame,
    frame_path: Path,
    *,
    maximum_tokens: int = 22,
    maximum_events: int = 20_000,
    random_state: int = 42,
    chunksize: int = 250_000,
) -> AttentionArrays:
    """Build pass queries and contemporaneous anonymous freeze-frame tokens."""

    required_actions = {
        "game_id",
        "original_event_id",
        "player_id",
        "type_name",
        "result_name",
        "start_x",
        "start_y",
        "end_x",
        "end_y",
        "time_seconds",
        "under_pressure_flag",
        "vaep_value",
        "xt_value",
    }
    missing = required_actions.difference(actions.columns)
    if missing:
        raise ValueError(f"Attention action columns missing: {sorted(missing)}")
    role_missing = {"player_id", *ROLE_DIMENSIONS}.difference(
        player_roles.columns
    )
    if role_missing:
        raise ValueError(f"Attention role columns missing: {sorted(role_missing)}")
    passes = actions.loc[
        actions["type_name"].eq("Pass")
        & actions["player_id"].notna()
        & actions[["start_x", "start_y", "end_x", "end_y"]]
        .notna()
        .all(axis=1)
    ].copy()
    passes["player_id"] = passes["player_id"].astype(int)
    passes = passes.merge(
        player_roles[["player_id", *ROLE_DIMENSIONS]],
        on="player_id",
        how="inner",
        validate="many_to_one",
    )
    passes["_event_key"] = list(
        zip(
            passes["game_id"].astype(int),
            passes["original_event_id"].astype(str),
            strict=True,
        )
    )
    if len(passes) > maximum_events:
        rng = np.random.default_rng(random_state)
        selected = np.sort(
            rng.choice(passes.index.to_numpy(), maximum_events, replace=False)
        )
        passes = passes.loc[selected].copy()
    passes = passes.reset_index().rename(columns={"index": "_action_index"})
    lookup = {
        key: offset
        for offset, key in enumerate(passes["_event_key"].tolist())
    }
    desired_keys = set(lookup)
    token_names = (
        "x",
        "y",
        "relative_x",
        "relative_y",
        "distance",
        "teammate",
        "keeper",
        "actor",
    )
    tokens: np.ndarray = np.zeros(
        (len(passes), maximum_tokens, len(token_names)),
        dtype=np.float32,
    )
    padding: np.ndarray = np.ones(
        (len(passes), maximum_tokens),
        dtype=bool,
    )

    usecols = [
        "match_id",
        "event_uuid",
        "teammate",
        "actor",
        "keeper",
        "x",
        "y",
    ]
    carry = pd.DataFrame(columns=usecols)

    def consume(grouped_rows: pd.DataFrame) -> None:
        if grouped_rows.empty:
            return
        keys = list(
            zip(
                grouped_rows["match_id"].astype(int),
                grouped_rows["event_uuid"].astype(str),
                strict=True,
            )
        )
        grouped_rows = grouped_rows.loc[
            [key in desired_keys for key in keys]
        ]
        for (match_id, event_uuid), group in grouped_rows.groupby(
            ["match_id", "event_uuid"],
            sort=False,
        ):
            offset = lookup.get((int(match_id), str(event_uuid)))
            if offset is None:
                continue
            actor_x = float(passes.loc[offset, "start_x"])
            actor_y = float(passes.loc[offset, "start_y"])
            group = group.dropna(subset=["x", "y"]).head(maximum_tokens)
            if group.empty:
                continue
            x = pd.to_numeric(group["x"], errors="coerce").to_numpy(dtype=float)
            y = pd.to_numeric(group["y"], errors="coerce").to_numpy(dtype=float)
            teammate = _truthy(group["teammate"]).to_numpy(dtype=float)
            keeper = _truthy(group["keeper"]).to_numpy(dtype=float)
            actor = _truthy(group["actor"]).to_numpy(dtype=float)
            count = len(group)
            tokens[offset, :count] = np.column_stack(
                [
                    x / 120.0,
                    y / 80.0,
                    (x - actor_x) / 120.0,
                    (y - actor_y) / 80.0,
                    np.hypot(
                        (x - actor_x) * 105.0 / 120.0,
                        (y - actor_y) * 68.0 / 80.0,
                    )
                    / 30.0,
                    teammate,
                    keeper,
                    actor,
                ]
            )
            padding[offset, :count] = False

    for chunk in pd.read_csv(
        frame_path,
        usecols=usecols,
        chunksize=chunksize,
        low_memory=False,
    ):
        combined = pd.concat([carry, chunk], ignore_index=True)
        last_match = combined.iloc[-1]["match_id"]
        last_event = combined.iloc[-1]["event_uuid"]
        is_last = combined["match_id"].eq(last_match) & combined[
            "event_uuid"
        ].eq(last_event)
        consume(combined.loc[~is_last])
        carry = combined.loc[is_last].copy()
    if not carry.empty:
        consume(carry)

    has_context = ~padding.all(axis=1)
    passes = passes.loc[has_context].reset_index(drop=True)
    tokens = tokens[has_context]
    padding = padding[has_context]
    event_names = (
        "start_x",
        "start_y",
        "end_x",
        "end_y",
        "time",
        "under_pressure",
        *ROLE_DIMENSIONS,
    )
    event_matrix = np.column_stack(
        [
            passes["start_x"].to_numpy(dtype=float) / 120.0,
            passes["start_y"].to_numpy(dtype=float) / 80.0,
            passes["end_x"].to_numpy(dtype=float) / 120.0,
            passes["end_y"].to_numpy(dtype=float) / 80.0,
            passes["time_seconds"].to_numpy(dtype=float) / (120.0 * 60.0),
            passes["under_pressure_flag"].astype(float).to_numpy(),
            *[
                passes[column].to_numpy(dtype=float)
                for column in ROLE_DIMENSIONS
            ],
        ]
    ).astype(np.float32)
    targets = {
        "retrospective": (
            passes["vaep_value"].to_numpy(dtype=float)
            + passes["xt_value"].to_numpy(dtype=float)
            > 0
        ).astype(int),
        "prospective": passes["result_name"].eq("success").astype(int).to_numpy(),
    }
    successful = targets["prospective"]
    auxiliary_targets = {
        # Observable event outcomes supervise the contextual heads. They are
        # explicitly experimental proxies, not manually awarded player value.
        "pass_difficulty": 1 - successful,
        "pressure_intensity": passes["under_pressure_flag"]
        .fillna(False)
        .astype(int)
        .to_numpy(),
        "line_breaking_impact": (
            (passes["end_x"] - passes["start_x"]).ge(10.0)
            & passes["end_x"].ge(80.0)
        )
        .astype(int)
        .to_numpy(),
        "space_creation": (
            passes["xt_value"].fillna(0.0).gt(0.0)
            & passes["end_x"].gt(passes["start_x"])
        )
        .astype(int)
        .to_numpy(),
    }
    return AttentionArrays(
        event_features=event_matrix,
        tokens=tokens,
        token_padding_mask=padding,
        targets=targets,
        auxiliary_targets=auxiliary_targets,
        match_ids=passes["game_id"].astype(int).to_numpy(),
        action_indices=passes["_action_index"].to_numpy(dtype=int),
        event_feature_names=event_names,
        token_feature_names=token_names,
    )
