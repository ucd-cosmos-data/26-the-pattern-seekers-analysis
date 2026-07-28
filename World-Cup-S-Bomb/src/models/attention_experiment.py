"""Match-disjoint training and evaluation of the optional attention model."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.config import AttentionConfig
from src.contracts import MetricGateResult
from src.models.attention import CausalSpatialAttentionModel, torch
from src.validation.grouped import assert_group_disjoint
from src.validation.metric_gate import evaluate_attention_metric_gate


@dataclass
class AttentionExperimentResult:
    """OOF predictions, gate decision, fold audit, and feature importance."""

    baseline_probabilities: dict[str, np.ndarray]
    attention_probabilities: dict[str, np.ndarray]
    contextual_head_probabilities: dict[str, np.ndarray]
    gate: MetricGateResult
    fold_audit: list[dict[str, Any]]
    baseline_feature_importance: dict[str, list[float]]
    attention_parameter_count: int


def _baseline_features(
    event_features: np.ndarray,
    tokens: np.ndarray,
    token_padding_mask: np.ndarray,
) -> np.ndarray:
    """Create the non-attention role-aware baseline feature matrix."""

    observed = ~token_padding_mask
    count = observed.sum(axis=1, keepdims=True)
    weighted = np.where(observed[:, :, None], tokens, 0.0)
    mean = np.divide(
        weighted.sum(axis=1),
        count,
        out=np.zeros((len(tokens), tokens.shape[2]), dtype=float),
        where=count > 0,
    )
    centered = np.where(
        observed[:, :, None],
        tokens - mean[:, None, :],
        0.0,
    )
    variance = np.divide(
        np.square(centered).sum(axis=1),
        count,
        out=np.zeros_like(mean),
        where=count > 0,
    )
    coverage = count / max(tokens.shape[1], 1)
    return np.column_stack(
        [event_features, mean, np.sqrt(variance), coverage]
    )


def _internal_match_split(
    indices: np.ndarray,
    groups: np.ndarray,
    random_state: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Reserve complete training matches for early stopping."""

    unique = np.unique(groups[indices])
    shuffled = np.random.default_rng(random_state).permutation(unique)
    validation_count = max(1, int(round(0.2 * len(shuffled))))
    validation_groups = set(shuffled[:validation_count].tolist())
    validation = indices[
        np.isin(groups[indices], list(validation_groups))
    ]
    fit = indices[
        ~np.isin(groups[indices], list(validation_groups))
    ]
    if not len(fit) or not len(validation):
        return indices, indices
    return fit, validation


def _fit_attention_fold(
    event_features: np.ndarray,
    tokens: np.ndarray,
    token_padding_mask: np.ndarray,
    target: np.ndarray,
    auxiliary_targets: dict[str, np.ndarray],
    groups: np.ndarray,
    train_indices: np.ndarray,
    validation_indices: np.ndarray,
    *,
    config: AttentionConfig,
    fold: int,
) -> tuple[np.ndarray, dict[str, np.ndarray], int]:
    """Fit one small model without consulting the outer held-out matches."""

    if torch is None:
        raise ImportError("PyTorch is required to run the attention experiment")
    torch.manual_seed(config.random_state + fold)
    np.random.seed(config.random_state + fold)
    model = CausalSpatialAttentionModel(config)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    loss_function = torch.nn.BCELoss()
    fit_indices, stopping_indices = _internal_match_split(
        train_indices,
        groups,
        config.random_state + fold,
    )
    batch_size = min(256, max(16, len(fit_indices)))
    best_loss = np.inf
    best_state = copy.deepcopy(model.state_dict())
    remaining_patience = config.patience
    generator = torch.Generator().manual_seed(config.random_state + fold)
    dataset = torch.utils.data.TensorDataset(
        torch.as_tensor(event_features[fit_indices], dtype=torch.float32),
        torch.as_tensor(tokens[fit_indices], dtype=torch.float32),
        torch.as_tensor(token_padding_mask[fit_indices], dtype=torch.bool),
        torch.as_tensor(target[fit_indices], dtype=torch.float32),
        torch.as_tensor(
            np.column_stack(
                [
                    auxiliary_targets[name][fit_indices]
                    for name in (
                        "pass_difficulty",
                        "pressure_intensity",
                        "line_breaking_impact",
                        "space_creation",
                    )
                ]
            ),
            dtype=torch.float32,
        ),
    )
    loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=generator,
    )
    stopping_event = torch.as_tensor(
        event_features[stopping_indices, None, :],
        dtype=torch.float32,
    )
    stopping_tokens = torch.as_tensor(
        tokens[stopping_indices, None, :, :],
        dtype=torch.float32,
    )
    stopping_mask = torch.as_tensor(
        token_padding_mask[stopping_indices, None, :],
        dtype=torch.bool,
    )
    stopping_target = torch.as_tensor(
        target[stopping_indices],
        dtype=torch.float32,
    )
    for _ in range(config.maximum_epochs):
        model.train()
        for (
            event_batch,
            token_batch,
            mask_batch,
            target_batch,
            auxiliary_batch,
        ) in loader:
            optimizer.zero_grad()
            predictions = model(
                event_batch[:, None, :],
                token_batch[:, None, :, :],
                token_padding_mask=mask_batch[:, None, :],
            )
            prediction = predictions["positive_value_probability"][:, 0]
            auxiliary_prediction = torch.column_stack(
                [
                    predictions[name][:, 0]
                    for name in (
                        "pass_difficulty",
                        "pressure_intensity",
                        "line_breaking_impact",
                        "space_creation",
                    )
                ]
            )
            loss = loss_function(prediction, target_batch) + (
                config.auxiliary_loss_weight
                * loss_function(auxiliary_prediction, auxiliary_batch)
            )
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
        model.eval()
        with torch.no_grad():
            stopping_prediction = model(
                stopping_event,
                stopping_tokens,
                token_padding_mask=stopping_mask,
            )["positive_value_probability"][:, 0]
            stopping_loss = float(
                loss_function(stopping_prediction, stopping_target)
            )
        if stopping_loss < best_loss - 1e-5:
            best_loss = stopping_loss
            best_state = copy.deepcopy(model.state_dict())
            remaining_patience = config.patience
        else:
            remaining_patience -= 1
            if remaining_patience <= 0:
                break
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        validation_outputs = model(
            torch.as_tensor(
                event_features[validation_indices, None, :],
                dtype=torch.float32,
            ),
            torch.as_tensor(
                tokens[validation_indices, None, :, :],
                dtype=torch.float32,
            ),
            token_padding_mask=torch.as_tensor(
                token_padding_mask[validation_indices, None, :],
                dtype=torch.bool,
            ),
        )
        probability = validation_outputs[
            "positive_value_probability"
        ][:, 0].numpy()
        contextual_probabilities = {
            name: validation_outputs[name][:, 0].numpy()
            for name in (
                "pass_difficulty",
                "pressure_intensity",
                "line_breaking_impact",
                "space_creation",
            )
        }
    parameter_count = int(
        sum(
            parameter.numel()
            for parameter in model.parameters()
            if parameter.requires_grad
        )
    )
    return probability, contextual_probabilities, parameter_count


def run_attention_experiment(
    event_features: np.ndarray,
    freeze_frame_tokens: np.ndarray,
    token_padding_mask: np.ndarray,
    targets: dict[str, np.ndarray],
    match_ids: np.ndarray,
    *,
    auxiliary_targets: dict[str, np.ndarray] | None = None,
    config: AttentionConfig | None = None,
    folds: int = 5,
    legacy_ranking: np.ndarray | None = None,
    attention_ranking: np.ndarray | None = None,
) -> AttentionExperimentResult:
    """Run identical match-disjoint folds for baseline and attention."""

    settings = config or AttentionConfig(enabled=True)
    if not settings.enabled:
        raise ValueError("Attention experiment is disabled in configuration")
    event = np.asarray(event_features, dtype=float)
    tokens = np.asarray(freeze_frame_tokens, dtype=float)
    padding = np.asarray(token_padding_mask, dtype=bool)
    groups = np.asarray(match_ids)
    if event.shape != (len(groups), settings.event_feature_count):
        raise ValueError("Event feature shape does not match AttentionConfig")
    if tokens.shape != (
        len(groups),
        settings.maximum_tokens,
        settings.token_feature_count,
    ):
        raise ValueError("Freeze-frame token shape does not match AttentionConfig")
    if padding.shape != tokens.shape[:2]:
        raise ValueError("Token padding mask shape is invalid")
    if set(targets) != {"retrospective", "prospective"}:
        raise ValueError("Attention requires retrospective and prospective targets")
    auxiliary_names = (
        "pass_difficulty",
        "pressure_intensity",
        "line_breaking_impact",
        "space_creation",
    )
    auxiliary = auxiliary_targets or {
        name: np.zeros(len(groups), dtype=int) for name in auxiliary_names
    }
    if set(auxiliary) != set(auxiliary_names):
        raise ValueError("Attention auxiliary targets are incomplete")
    if any(len(values) != len(groups) for values in auxiliary.values()):
        raise ValueError("Attention auxiliary-target lengths are invalid")
    baseline_matrix = _baseline_features(event, tokens, padding)
    baseline_probabilities = {
        task: np.full(len(groups), np.nan) for task in targets
    }
    attention_probabilities = {
        task: np.full(len(groups), np.nan) for task in targets
    }
    contextual_head_probabilities = {
        name: np.full(len(groups), np.nan) for name in auxiliary_names
    }
    importance: dict[str, list[float]] = {}
    audit: list[dict[str, Any]] = []
    parameter_count = 0
    splitter = GroupKFold(n_splits=min(folds, len(np.unique(groups))))
    for fold, (train, validation) in enumerate(
        splitter.split(event, targets["prospective"], groups)
    ):
        assert_group_disjoint(train, validation, groups)
        fold_record = {
            "fold": fold,
            "train_matches": sorted(set(groups[train].tolist())),
            "validation_matches": sorted(set(groups[validation].tolist())),
            "group_overlap": False,
        }
        for task, task_target in targets.items():
            truth = np.asarray(task_target, dtype=int)
            baseline = make_pipeline(
                StandardScaler(),
                LogisticRegression(
                    C=0.25,
                    class_weight="balanced",
                    max_iter=500,
                    random_state=settings.random_state + fold,
                ),
            )
            baseline.fit(baseline_matrix[train], truth[train])
            baseline_probabilities[task][validation] = baseline.predict_proba(
                baseline_matrix[validation]
            )[:, 1]
            importance.setdefault(task, []).extend(
                np.abs(baseline[-1].coef_[0]).tolist()
            )
            (
                probability,
                contextual_probabilities,
                parameter_count,
            ) = _fit_attention_fold(
                event,
                tokens,
                padding,
                truth,
                auxiliary,
                groups,
                train,
                validation,
                config=settings,
                fold=fold,
            )
            attention_probabilities[task][validation] = probability
            if task == "retrospective":
                for name, values in contextual_probabilities.items():
                    contextual_head_probabilities[name][validation] = values
        audit.append(fold_record)
    for probabilities in (
        baseline_probabilities,
        attention_probabilities,
    ):
        if any(not np.isfinite(values).all() for values in probabilities.values()):
            raise RuntimeError("Attention OOF prediction coverage is incomplete")
    gate = evaluate_attention_metric_gate(
        targets,
        baseline_probabilities,
        attention_probabilities,
        legacy_ranking=legacy_ranking,
        attention_ranking=attention_ranking,
    )
    if any(
        not np.isfinite(values).all()
        for values in contextual_head_probabilities.values()
    ):
        raise RuntimeError("Contextual-head OOF prediction coverage is incomplete")
    return AttentionExperimentResult(
        baseline_probabilities=baseline_probabilities,
        attention_probabilities=attention_probabilities,
        contextual_head_probabilities=contextual_head_probabilities,
        gate=gate,
        fold_audit=audit,
        baseline_feature_importance=importance,
        attention_parameter_count=parameter_count,
    )
