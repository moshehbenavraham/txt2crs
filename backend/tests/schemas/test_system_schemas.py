"""Strict public HTTP projection tests for system state."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from txt2crs.application import (
    SystemAuthenticationSnapshot,
    SystemAuthenticationState,
)

from app.schemas.system import (
    SystemAuthenticationPublic,
    SystemReadinessChecksPublic,
    SystemReadinessPublic,
)
from app.services.txt2crs_readiness import (
    ReadinessChecks,
    ReadinessCheckState,
    ReadinessSnapshot,
    ReadinessStatus,
)


def _readiness_snapshot() -> ReadinessSnapshot:
    """Return one complete shell snapshot for API projection."""

    return ReadinessSnapshot(
        status=ReadinessStatus.ready,
        accepting_jobs=True,
        configured_model_id="gpt-5.6-sol",
        enabled_input_modes=("prompt", "text", "url"),
        checks=ReadinessChecks(
            authentication=ReadinessCheckState.ready,
            model=ReadinessCheckState.ready,
            research=ReadinessCheckState.ready,
            storage=ReadinessCheckState.ready,
            worker=ReadinessCheckState.ready,
            inputs=ReadinessCheckState.ready,
            admission=ReadinessCheckState.ready,
            runtime_ownership=ReadinessCheckState.ready,
        ),
        warnings=(),
        recovery_actions=(),
        checked_at=datetime(2026, 7, 19, tzinfo=UTC),
        is_fresh=True,
    )


def test_readiness_projection_copies_only_explicit_safe_fields() -> None:
    public = SystemReadinessPublic.from_snapshot(_readiness_snapshot())

    assert set(public.model_dump()) == {
        "schema_version",
        "status",
        "accepting_jobs",
        "configured_model_id",
        "enabled_input_modes",
        "checks",
        "warnings",
        "recovery_actions",
        "checked_at",
        "is_fresh",
    }
    assert set(public.checks.model_dump()) == set(
        SystemReadinessChecksPublic.model_fields
    )


def test_readiness_projection_rejects_unknown_input_and_naive_time() -> None:
    payload = SystemReadinessPublic.from_snapshot(_readiness_snapshot()).model_dump()
    with pytest.raises(ValidationError):
        SystemReadinessPublic.model_validate({**payload, "private_path": "/secret"})
    with pytest.raises(ValidationError, match="checked_at"):
        SystemReadinessPublic.model_validate(
            {**payload, "checked_at": datetime(2026, 7, 19)}
        )


def test_readiness_projection_rejects_a_bare_model_family_label() -> None:
    """The browser contract exposes only exact app-server model identifiers."""

    payload = SystemReadinessPublic.from_snapshot(_readiness_snapshot()).model_dump()

    with pytest.raises(ValidationError, match="configured_model_id"):
        SystemReadinessPublic.model_validate(
            {**payload, "configured_model_id": "gpt-5.6"}
        )


def test_waiting_auth_requires_exact_openai_url_and_short_code() -> None:
    public = SystemAuthenticationPublic.from_snapshot(
        SystemAuthenticationSnapshot(
            state=SystemAuthenticationState.waiting_for_user,
            verification_url="https://auth.openai.com/codex/device",
            user_code="ABCD-1234",
            message="Open the verification page.",
        )
    )

    assert public.verification_url == "https://auth.openai.com/codex/device"
    assert public.user_code == "ABCD-1234"
    assert "expiry" not in public.model_dump()

    for unsafe_url in (
        "http://auth.openai.com/codex/device",
        "https://attacker.example/device",
        "https://user:pass@auth.openai.com/device",
    ):
        with pytest.raises(ValidationError):
            SystemAuthenticationPublic(
                state="waiting_for_user",
                verification_url=unsafe_url,
                user_code="ABCD-1234",
                message="Open the verification page.",
            )


def test_terminal_auth_rejects_challenge_and_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        SystemAuthenticationPublic(
            state="authenticated",
            verification_url="https://auth.openai.com/codex/device",
            user_code="ABCD-1234",
            message="Connected.",
        )
    with pytest.raises(ValidationError):
        SystemAuthenticationPublic.model_validate(
            {
                "state": "signed_out",
                "verification_url": None,
                "user_code": None,
                "message": "Signed out.",
                "account_email": "private@example.com",
            }
        )
