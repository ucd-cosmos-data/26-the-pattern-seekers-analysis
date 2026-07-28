"""Causality test for the optional PyTorch contextualizer."""

from __future__ import annotations

import importlib.util

import pytest


torch_available = importlib.util.find_spec("torch") is not None


@pytest.mark.skipif(not torch_available, reason="PyTorch is optional")
def test_future_event_change_does_not_change_past_output() -> None:
    import torch

    from src.config import AttentionConfig
    from src.models.attention import CausalSpatialAttentionModel

    torch.manual_seed(42)
    config = AttentionConfig(
        enabled=True,
        event_feature_count=4,
        token_feature_count=3,
        hidden_dimension=8,
        attention_heads=2,
        dropout=0.0,
    )
    model = CausalSpatialAttentionModel(config).eval()
    events = torch.randn(1, 4, 4)
    tokens = torch.randn(1, 4, 5, 3)
    with torch.no_grad():
        original = model(events, tokens)["positive_value_probability"]
        changed_events = events.clone()
        changed_tokens = tokens.clone()
        changed_events[:, 3] += 100
        changed_tokens[:, 3] -= 100
        changed = model(
            changed_events,
            changed_tokens,
        )["positive_value_probability"]
    assert torch.allclose(original[:, :3], changed[:, :3], atol=1e-6)
    assert {
        "pass_difficulty",
        "pressure_intensity",
        "line_breaking_impact",
        "space_creation",
        "positive_value_probability",
    } == set(model(events, tokens))
