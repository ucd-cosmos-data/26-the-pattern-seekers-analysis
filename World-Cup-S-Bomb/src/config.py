"""Central configuration for the World Cup player analytics pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


RANDOM_STATE = 42
PITCH_LENGTH_UNITS = 120.0
PITCH_WIDTH_UNITS = 80.0
PITCH_LENGTH_METRES = 105.0
PITCH_WIDTH_METRES = 68.0
MIN_PLAYER_MINUTES = 300.0

RATING_WEIGHTS: dict[str, float] = {
    "vaep_90": 0.40,
    "vaep_per_touch": 0.15,
    "xt_90": 0.15,
    "role_adjusted_value": 0.15,
    "completeness_score": 0.10,
    "off_ball_score": 0.05,
}


@dataclass(frozen=True)
class RoleDiscoveryConfig:
    """Configuration for probabilistic role discovery."""

    k_min: int = 9
    k_max: int = 16
    covariance_types: tuple[str, ...] = ("full", "tied", "diag")
    reg_covar: float = 0.1
    n_init: int = 10
    max_iter: int = 500
    minimum_cluster_size: int = 2
    pca_components: int = 15
    bootstrap_iterations: int = 200
    random_state: int = RANDOM_STATE

    def __post_init__(self) -> None:
        if self.k_min < 2 or self.k_max < self.k_min:
            raise ValueError("Invalid probabilistic-role K range")
        allowed = {"full", "tied", "diag"}
        if not self.covariance_types or not set(self.covariance_types) <= allowed:
            raise ValueError("Unsupported GMM covariance type")
        if self.minimum_cluster_size < 1:
            raise ValueError("minimum_cluster_size must be positive")
        if self.bootstrap_iterations < 0:
            raise ValueError("bootstrap_iterations cannot be negative")


@dataclass(frozen=True)
class AttentionConfig:
    """Configuration for the optional lightweight attention model."""

    enabled: bool = False
    event_feature_count: int = 16
    token_feature_count: int = 8
    hidden_dimension: int = 32
    attention_heads: int = 2
    dropout: float = 0.15
    maximum_tokens: int = 22
    maximum_sequence_length: int = 32
    maximum_events: int = 5_000
    cv_folds: int = 5
    learning_rate: float = 1e-3
    weight_decay: float = 1e-3
    maximum_epochs: int = 80
    patience: int = 10
    auxiliary_loss_weight: float = 0.10
    random_state: int = RANDOM_STATE

    def __post_init__(self) -> None:
        if self.hidden_dimension % self.attention_heads:
            raise ValueError(
                "hidden_dimension must be divisible by attention_heads"
            )
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")
        if self.maximum_events < 100 or self.cv_folds < 2:
            raise ValueError("Attention sample/fold configuration is invalid")
        if not 0.0 <= self.auxiliary_loss_weight <= 1.0:
            raise ValueError("auxiliary_loss_weight must be in [0, 1]")


@dataclass(frozen=True)
class RatingConfig:
    """Configuration for composite rating and empirical-Bayes shrinkage."""

    weights: Mapping[str, float] = field(
        default_factory=lambda: dict(RATING_WEIGHTS)
    )
    # Half-weight at 600 minutes (~6.7 matches). The previous 300 gave a
    # 300-minute player half signal, which let three-match per-90 hot streaks
    # crowd the top of the global ranking.
    reliability_minutes: float = 600.0
    minimum_minutes: float = MIN_PLAYER_MINUTES

    def __post_init__(self) -> None:
        expected = set(RATING_WEIGHTS)
        if set(self.weights) != expected:
            raise ValueError(
                f"Rating weights must have exactly these keys: {sorted(expected)}"
            )
        if any(value < 0.0 for value in self.weights.values()):
            raise ValueError("Rating weights must be nonnegative")
        if abs(sum(self.weights.values()) - 1.0) > 1e-12:
            raise ValueError("Rating weights must sum to one")
        if self.reliability_minutes <= 0 or self.minimum_minutes < 0:
            raise ValueError("Minute thresholds are invalid")


@dataclass(frozen=True)
class PipelineConfig:
    """Top-level, serializable pipeline configuration."""

    input_root: Path
    output_root: Path
    rating: RatingConfig = field(default_factory=RatingConfig)
    roles: RoleDiscoveryConfig = field(default_factory=RoleDiscoveryConfig)
    attention: AttentionConfig = field(default_factory=AttentionConfig)
    random_state: int = RANDOM_STATE
