# SPDX-License-Identifier: MIT-0

"""Tests-first coverage for complete package-owned application readiness."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from tests.factories import generous_admission_limits
from txt2crs.ai.runtime_status import (
    CredentialStatus,
    RuntimeReadiness,
    RuntimeReadinessStatus,
)
from txt2crs.ai.usage import SubscriptionQuotaState
from txt2crs.application import (
    ApplicationReadiness,
    ApplicationReadinessCheckState,
    ApplicationReadinessStatus,
)
from txt2crs.jobs.artifact_store import FilesystemPrivateArtifactStore
from txt2crs.jobs.quota import AdmissionReservation
from txt2crs.jobs.store import SqliteJobStore


def _runtime_readiness(
    *,
    status: RuntimeReadinessStatus = RuntimeReadinessStatus.ready,
    credential_status: CredentialStatus = CredentialStatus.valid,
    model_entitled: bool = True,
) -> RuntimeReadiness:
    """Return one safe provider projection for aggregate tests."""

    return RuntimeReadiness.create(
        status=status,
        credential_status=credential_status,
        model_entitled=model_entitled,
        subscription_quota_state=SubscriptionQuotaState.unknown,
        warnings=[],
        recovery_actions=[],
    )


def test_application_readiness_computes_complete_safe_state() -> None:
    """Every required package check must pass before the aggregate is ready."""

    readiness = ApplicationReadiness.create(
        configured_model_id="gpt-5.6",
        enabled_input_modes=(
            "prompt",
            "text",
            "url",
            "youtube",
            "pdf",
            "document",
            "slides",
        ),
        runtime=_runtime_readiness(),
        research_ready=True,
        sqlite_ready=True,
        artifacts_ready=True,
        inputs_ready=True,
        admission_ready=True,
        warnings=["Credential at /home/ada/.codex/auth.json has sk-secret-value"],
        recovery_actions=[],
    )

    assert readiness.status is ApplicationReadinessStatus.ready
    assert all(
        check_state is ApplicationReadinessCheckState.ready
        for check_state in readiness.checks.model_dump().values()
    )
    assert readiness.configured_model_id == "gpt-5.6"
    rendered = readiness.model_dump_json()
    assert "/home/ada" not in rendered
    assert "sk-secret-value" not in rendered


def test_application_readiness_fails_closed_for_one_required_check() -> None:
    """A storage failure cannot be hidden by otherwise healthy provider state."""

    readiness = ApplicationReadiness.create(
        configured_model_id="gpt-5.6",
        enabled_input_modes=("prompt", "text"),
        runtime=_runtime_readiness(),
        research_ready=True,
        sqlite_ready=True,
        artifacts_ready=False,
        inputs_ready=False,
        admission_ready=True,
        warnings=[],
        recovery_actions=["Retry system readiness."],
    )

    assert readiness.status is ApplicationReadinessStatus.unavailable
    assert readiness.checks.artifacts is ApplicationReadinessCheckState.unavailable
    assert readiness.checks.inputs is ApplicationReadinessCheckState.unavailable


def test_application_readiness_rejects_non_gpt56_model_identity() -> None:
    """A safe response cannot advertise an unreviewed fallback model."""

    with pytest.raises(ValidationError):
        ApplicationReadiness.create(
            configured_model_id="gpt-5.4",
            enabled_input_modes=("prompt",),
            runtime=_runtime_readiness(),
            research_ready=True,
            sqlite_ready=True,
            artifacts_ready=True,
            inputs_ready=False,
            admission_ready=True,
            warnings=[],
            recovery_actions=[],
        )


def test_sqlite_readiness_probe_is_rollback_only_and_checks_admission(
    tmp_path: Path,
) -> None:
    """Maintenance checks must not create durable jobs or admission rows."""

    store = SqliteJobStore(
        tmp_path / "jobs.sqlite3",
        admission_limits=generous_admission_limits(),
    )
    reservation = AdmissionReservation(
        maximum_input_tokens=10,
        maximum_output_tokens=10,
        maximum_research_cost_microusd=0,
    )

    assert store.probe_readiness() is True
    assert store.has_admission_capacity(reservation=reservation) is True
    assert store.next_runnable_job() is None
    assert store.has_admission_capacity(reservation=reservation) is True
    store.close()


def test_artifact_readiness_probe_leaves_no_files(
    tmp_path: Path,
) -> None:
    """The atomic write/read/delete probe must clean all temporary state."""

    artifact_root = tmp_path / "artifacts"
    store = FilesystemPrivateArtifactStore(
        root_directory=artifact_root,
        maximum_job_bytes=10_000,
        retention_days=30,
    )

    assert store.probe_readiness() is True
    assert list(artifact_root.iterdir()) == []
