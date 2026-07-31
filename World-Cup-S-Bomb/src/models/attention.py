"""Experimental lightweight causal attention over local 360 context."""

from __future__ import annotations

from typing import Any

from src.config import AttentionConfig, RANDOM_STATE

try:
    import torch
    from torch import Tensor, nn
except ImportError:  # pragma: no cover - exercised in minimal deployments.
    torch = None
    Tensor = Any  # type: ignore[assignment,misc]
    nn = None


if torch is not None:
    torch.manual_seed(RANDOM_STATE)


if nn is not None:

    class CausalSpatialAttentionModel(nn.Module):
        """One-block event-to-freeze-frame attention contextualizer.

        Each event attends only to players visible in its contemporaneous
        freeze frame. A one-layer temporal encoder then uses an upper-triangular
        causal mask, so event ``t`` cannot attend to later events.
        """

        def __init__(self, config: AttentionConfig | None = None) -> None:
            super().__init__()
            self.config = config or AttentionConfig(enabled=True)
            hidden = self.config.hidden_dimension
            self.event_projection = nn.Sequential(
                nn.Linear(self.config.event_feature_count, hidden),
                nn.LayerNorm(hidden),
                nn.GELU(),
            )
            self.token_projection = nn.Sequential(
                nn.Linear(self.config.token_feature_count, hidden),
                nn.LayerNorm(hidden),
                nn.GELU(),
            )
            self.spatial_attention = nn.MultiheadAttention(
                hidden,
                self.config.attention_heads,
                dropout=self.config.dropout,
                batch_first=True,
            )
            temporal_layer = nn.TransformerEncoderLayer(
                d_model=hidden,
                nhead=self.config.attention_heads,
                dim_feedforward=2 * hidden,
                dropout=self.config.dropout,
                activation="gelu",
                batch_first=True,
                norm_first=False,
            )
            self.temporal_encoder = nn.TransformerEncoder(
                temporal_layer,
                num_layers=1,
            )
            self.context_normalization = nn.LayerNorm(hidden)
            self.output_heads = nn.ModuleDict(
                {
                    name: nn.Linear(hidden, 1)
                    for name in (
                        "pass_difficulty",
                        "pressure_intensity",
                        "line_breaking_impact",
                        "space_creation",
                        "positive_value_probability",
                    )
                }
            )

        @staticmethod
        def causal_mask(
            sequence_length: int,
            *,
            device: torch.device,
        ) -> Tensor:
            """Return a mask whose upper triangle blocks future attention."""

            return torch.triu(
                torch.ones(
                    sequence_length,
                    sequence_length,
                    dtype=torch.bool,
                    device=device,
                ),
                diagonal=1,
            )

        def forward(
            self,
            event_features: Tensor,
            freeze_frame_tokens: Tensor,
            *,
            token_padding_mask: Tensor | None = None,
            event_padding_mask: Tensor | None = None,
        ) -> dict[str, Tensor]:
            """Contextualize event sequences without future-event leakage.

            Args:
                event_features: ``[batch, sequence, event_features]``.
                freeze_frame_tokens: ``[batch, sequence, actors, token_features]``.
                token_padding_mask: Boolean ``[batch, sequence, actors]`` with
                    ``True`` for unavailable/padded actor tokens.
                event_padding_mask: Boolean ``[batch, sequence]`` with ``True``
                    for padded events.
            """

            if event_features.ndim != 3 or freeze_frame_tokens.ndim != 4:
                raise ValueError("Attention tensors have invalid dimensions")
            batch, sequence, _ = event_features.shape
            token_batch, token_sequence, actors, _ = freeze_frame_tokens.shape
            if (batch, sequence) != (token_batch, token_sequence):
                raise ValueError("Event and token batch/sequence shapes differ")
            event_embedding = self.event_projection(event_features)
            token_embedding = self.token_projection(freeze_frame_tokens)
            query = event_embedding.reshape(batch * sequence, 1, -1)
            keys = token_embedding.reshape(batch * sequence, actors, -1)
            padding = (
                token_padding_mask.reshape(batch * sequence, actors)
                if token_padding_mask is not None
                else None
            )
            if padding is not None:
                # MultiheadAttention cannot consume a row where every token is
                # masked. Preserve one explicit zero "no visible context" token.
                all_missing = padding.all(dim=1)
                if all_missing.any():
                    padding = padding.clone()
                    keys = keys.clone()
                    padding[all_missing, 0] = False
                    keys[all_missing, 0] = 0.0
            context, _ = self.spatial_attention(
                query,
                keys,
                keys,
                key_padding_mask=padding,
                need_weights=False,
            )
            context = context.reshape(batch, sequence, -1)
            combined = self.context_normalization(event_embedding + context)
            encoded = self.temporal_encoder(
                combined,
                mask=self.causal_mask(sequence, device=combined.device),
                src_key_padding_mask=event_padding_mask,
            )
            return {
                name: torch.sigmoid(head(encoded).squeeze(-1))
                for name, head in self.output_heads.items()
            }

else:

    class CausalSpatialAttentionModel:  # type: ignore[no-redef]  # pragma: no cover
        """Import-time placeholder when PyTorch is intentionally unavailable."""

        def __init__(self, config: AttentionConfig | None = None) -> None:
            raise ImportError(
                "PyTorch is required only when the experimental attention "
                "module is enabled"
            )


def attention_parameter_count(model: Any) -> int:
    """Return the count of trainable attention parameters."""

    if torch is None:
        raise ImportError("PyTorch is not installed")
    return int(
        sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    )
