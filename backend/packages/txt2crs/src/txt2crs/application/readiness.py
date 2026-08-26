# SPDX-License-Identifier: MIT-0

"""Complete browser-safe readiness owned by the engine package boundary."""

from collections.abc import Callable
from enum import StrEnum
from typing import Literal, Protocol, Self

from pydantic import Field, field_validator

from txt2crs.ai.model_policy import ExactModelPolicy
from txt2crs.ai.runtime_status import (
    CredentialStatus,
    RuntimeReadiness,
    RuntimeReadinessStatus,
)
from txt2crs.ai.usage import SubscriptionQuotaState
from txt2crs.domain.models import Identifier, StrictContract
from txt2crs.jobs.quota import AdmissionReservation
from txt2crs.security.redaction import sanitize_public_text

APPLICATION_READINESS_SCHEMA_VERSION: Literal["1.0"] = "1.0"
REQUIRED_P0_INPUT_MODES = frozenset(
    {"prompt", "text", "url", "youtube", "pdf", "document", "slides"}
)


class ApplicationReadinessStatus(StrEnum):
    """Whether every package-owned prerequisite currently passes."""

    ready = "ready"
    unavailable = "unavailable"


class ApplicationReadinessCheckState(StrEnum):
    """Coarse check state that reveals no private failure detail."""

    ready = "ready"
    unavailable = "unavailable"


class ApplicationReadinessChecks(StrictContract):
    """Finite package-owned checks consumed by the shell cache."""

    authentication: ApplicationReadinessCheckState
    model: ApplicationReadinessCheckState
    research: ApplicationReadinessCheckState
    sqlite: ApplicationReadinessCheckState
    artifacts: ApplicationReadinessCheckState
    inputs: ApplicationReadinessCheckState
    admission: ApplicationReadinessCheckState


class ApplicationReadiness(StrictContract):
    """One bounded projection over provider, research, storage, and admission."""

    schema_version: Literal["1.0"] = APPLICATION_READINESS_SCHEMA_VERSION
    status: ApplicationReadinessStatus
    configured_model_id: Identifier
    enabled_input_modes: tuple[Identifier, ...] = Field(max_length=20)
    runtime: RuntimeReadiness
    checks: ApplicationReadinessChecks
    warnings: list[str] = Field(max_length=20)
    recovery_actions: list[str] = Field(max_length=20)

    @field_validator("configured_model_id")
    @classmethod
    def require_safe_exact_model(cls, configured_model_id: str) -> str:
        """Prevent readiness from advertising an unsafe or ambiguous model."""

        ExactModelPolicy(configured_model_id=configured_model_id)
        return configured_model_id

    @classmethod
    def create(
        cls,
        *,
        configured_model_id: str,
        enabled_input_modes: tuple[str, ...],
        runtime: RuntimeReadiness,
        research_ready: bool,
        sqlite_ready: bool,
        artifacts_ready: bool,
        inputs_ready: bool,
        admission_ready: bool,
        warnings: list[str],
        recovery_actions: list[str],
    ) -> Self:
        """Build and sanitize a complete readiness result in one place."""

        authentication_ready = (
            runtime.status is RuntimeReadinessStatus.ready
            and runtime.credential_status is CredentialStatus.valid
        )
        checks = ApplicationReadinessChecks(
            authentication=_check_state(authentication_ready),
            model=_check_state(runtime.model_entitled),
            research=_check_state(research_ready),
            sqlite=_check_state(sqlite_ready),
            artifacts=_check_state(artifacts_ready),
            inputs=_check_state(inputs_ready),
            admission=_check_state(admission_ready),
        )
        status = (
            ApplicationReadinessStatus.ready
            if all(
                check_state is ApplicationReadinessCheckState.ready
                for check_state in checks.model_dump(mode="python").values()
            )
            else ApplicationReadinessStatus.unavailable
        )
        # Sorted unique values make the public capability list stable across
        # dictionary construction order and detach it from mutable callers.
        safe_input_modes = tuple(sorted(set(enabled_input_modes)))[:20]
        return cls(
            status=status,
            configured_model_id=configured_model_id,
            enabled_input_modes=safe_input_modes,
            runtime=runtime,
            checks=checks,
            warnings=[sanitize_public_text(warning) for warning in warnings[:20]],
            recovery_actions=[
                sanitize_public_text(action) for action in recovery_actions[:20]
            ],
        )


class RuntimeReadinessProbe(Protocol):
    """Provider inspection used by the aggregate package coordinator."""

    def inspect_readiness(self) -> RuntimeReadiness:
        """Open, inspect, and close the configured provider graph."""


class SqliteReadinessProbe(Protocol):
    """Narrow local-store behavior required by readiness."""

    def probe_readiness(self) -> bool:
        """Verify current migrations and rollback-only writability."""

    def has_admission_capacity(
        self,
        *,
        reservation: AdmissionReservation,
    ) -> bool:
        """Return whether one conservative request still fits."""


class ArtifactReadinessProbe(Protocol):
    """Narrow private-artifact behavior required by readiness."""

    def probe_readiness(self) -> bool:
        """Atomically write, read, and remove a confined probe."""


class AggregateApplicationReadinessInspector:
    """Combine only safe results from package-owned collaborators."""

    def __init__(
        self,
        *,
        runtime_probe: RuntimeReadinessProbe,
        sqlite_probe: SqliteReadinessProbe,
        artifact_probe: ArtifactReadinessProbe,
        configured_model_id: str,
        enabled_input_modes: tuple[str, ...],
        admission_reservation: AdmissionReservation,
    ) -> None:
        self._runtime_probe = runtime_probe
        self._sqlite_probe = sqlite_probe
        self._artifact_probe = artifact_probe
        self._configured_model_id = configured_model_id
        self._enabled_input_modes = tuple(enabled_input_modes)
        self._admission_reservation = admission_reservation

    def inspect_readiness(self) -> ApplicationReadiness:
        """Run bounded package probes and collapse failures to coarse states."""

        warnings: list[str] = []
        recovery_actions: list[str] = []
        try:
            runtime = self._runtime_probe.inspect_readiness()
        except Exception:
            # Never retain the exception. Provider payloads, local paths, and
            # credential diagnostics are private implementation details.
            runtime = RuntimeReadiness.create(
                status=RuntimeReadinessStatus.unavailable,
                credential_status=CredentialStatus.unknown,
                model_entitled=False,
                subscription_quota_state=SubscriptionQuotaState.unknown,
                warnings=["The configured provider runtime is unavailable."],
                recovery_actions=["Review system authentication and retry readiness."],
            )

        research_ready = runtime.status is RuntimeReadinessStatus.ready
        sqlite_ready = _run_boolean_probe(self._sqlite_probe.probe_readiness)
        artifacts_ready = _run_boolean_probe(self._artifact_probe.probe_readiness)
        admission_ready = _run_boolean_probe(
            lambda: self._sqlite_probe.has_admission_capacity(
                reservation=self._admission_reservation
            )
        )
        inputs_ready = REQUIRED_P0_INPUT_MODES.issubset(self._enabled_input_modes)

        if not sqlite_ready or not artifacts_ready:
            warnings.append("Private application storage is unavailable.")
            recovery_actions.append("Review private storage and retry readiness.")
        if not inputs_ready:
            warnings.append("Required input modes are unavailable.")
            recovery_actions.append("Enable every required input mode.")
        if not admission_ready:
            warnings.append("Job admission capacity is unavailable.")
            recovery_actions.append("Wait for admission capacity and retry.")

        return ApplicationReadiness.create(
            configured_model_id=self._configured_model_id,
            enabled_input_modes=self._enabled_input_modes,
            runtime=runtime,
            research_ready=research_ready,
            sqlite_ready=sqlite_ready,
            artifacts_ready=artifacts_ready,
            inputs_ready=inputs_ready,
            admission_ready=admission_ready,
            warnings=[*runtime.warnings, *warnings],
            recovery_actions=[*runtime.recovery_actions, *recovery_actions],
        )


def _check_state(is_ready: bool) -> ApplicationReadinessCheckState:
    """Translate a private boolean into one safe finite value."""

    return (
        ApplicationReadinessCheckState.ready
        if is_ready
        else ApplicationReadinessCheckState.unavailable
    )


def _run_boolean_probe(probe: Callable[[], bool]) -> bool:
    """Run one callable without retaining its exception."""

    try:
        return probe()
    except Exception:
        return False


__all__ = [
    "APPLICATION_READINESS_SCHEMA_VERSION",
    "AggregateApplicationReadinessInspector",
    "ApplicationReadiness",
    "ApplicationReadinessChecks",
    "ApplicationReadinessCheckState",
    "ApplicationReadinessStatus",
    "REQUIRED_P0_INPUT_MODES",
]
