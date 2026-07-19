# SPDX-License-Identifier: MIT-0

"""Bounded AI-runtime helpers used by the txt2crs application services."""

from typing import Any

from txt2crs.ai.budgets import (
    BudgetExceededError,
    RunBudget,
    RunBudgetLimits,
    RunBudgetSnapshot,
)

_JOB_RUNTIME_EXPORTS = frozenset(
    {
        "JobRuntimeResources",
        "JobRuntimeResourcesFactory",
        "ManagedProviderSession",
        "ManagedProviderSessionFactory",
        "ProviderSessionCleanupError",
        "ProviderSessionReadinessError",
    }
)
_MODEL_POLICY_EXPORTS = frozenset(
    {
        "DEFAULT_GPT56_MODEL_ID",
        "REVIEWED_GPT56_MODEL_IDS",
        "Gpt56ModelPolicy",
        "ModelPolicyError",
    }
)


def __getattr__(name: str) -> Any:
    """Load composition contracts lazily to avoid package-import cycles."""

    if name in _JOB_RUNTIME_EXPORTS:
        from txt2crs.ai import job_runtime

        return getattr(job_runtime, name)
    if name in _MODEL_POLICY_EXPORTS:
        from txt2crs.ai import model_policy

        return getattr(model_policy, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BudgetExceededError",
    "DEFAULT_GPT56_MODEL_ID",
    "Gpt56ModelPolicy",
    "JobRuntimeResources",
    "JobRuntimeResourcesFactory",
    "ManagedProviderSession",
    "ManagedProviderSessionFactory",
    "ModelPolicyError",
    "ProviderSessionCleanupError",
    "ProviderSessionReadinessError",
    "REVIEWED_GPT56_MODEL_IDS",
    "RunBudget",
    "RunBudgetLimits",
    "RunBudgetSnapshot",
]
