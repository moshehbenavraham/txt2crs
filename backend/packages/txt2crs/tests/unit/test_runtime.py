# SPDX-License-Identifier: MIT-0

"""Tests for the subscription-only model-runtime boundary."""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from tests.factories import valid_course_data
from txt2crs.ai.codex_runtime import (
    CodexSubscriptionRuntime,
    RuntimePolicyError,
)
from txt2crs.ai.fake_runtime import FakeRuntime, ScriptedTurn
from txt2crs.ai.runtime import CancellationToken, CodexAdapterResult, TurnRequest
from txt2crs.ai.runtime_status import (
    CredentialStatus,
    RuntimeReadinessStatus,
)
from txt2crs.ai.usage import RuntimeUsage, SubscriptionQuotaState
from txt2crs.domain.models import Course


class StubCodexAdapter:
    """Small adapter double used to exercise the runtime policy."""

    def __init__(
        self,
        *,
        account_type: str = "chatgpt",
        models: tuple[str, ...] = ("gpt-5.4",),
    ) -> None:
        self.account_type = account_type
        self.models = models
        self.received_output_schema: dict[str, Any] | None = None

    def inspect_account_type(self) -> str:
        """Return the credential mode reported by app-server."""

        return self.account_type

    def list_model_ids(self) -> tuple[str, ...]:
        """Return only models reported by the runtime."""

        return self.models

    def run_turn(
        self,
        *,
        request: TurnRequest,
        output_schema: dict[str, Any],
        cancellation: CancellationToken,
    ) -> CodexAdapterResult:
        """Record the schema and return a deterministic course."""

        cancellation.raise_if_cancelled()
        self.received_output_schema = output_schema
        return CodexAdapterResult(
            output=valid_course_data(),
            thread_id="thread-1",
            turn_id="turn-1",
            model_id=request.model_id,
            input_tokens=125,
            output_tokens=75,
        )


def course_turn_request(model_id: str = "gpt-5.4") -> TurnRequest:
    """Build the minimum trusted request used by runtime tests."""

    return TurnRequest(
        request_id="request-course",
        stage="write_lessons",
        model_id=model_id,
        prompt_version="course-write-v1",
        trusted_instructions="Create the schema-constrained course.",
        untrusted_data="<learner_input>Python variables</learner_input>",
        timeout_seconds=30,
    )


def test_subscription_runtime_rejects_api_key_accounts() -> None:
    """Subscription mode cannot silently spend a Platform API key."""

    runtime = CodexSubscriptionRuntime(adapter=StubCodexAdapter(account_type="api_key"))

    with pytest.raises(RuntimePolicyError, match="ChatGPT"):
        runtime.run_validated_turn(
            request=course_turn_request(),
            artifact_model=Course,
            cancellation=CancellationToken(),
        )


def test_subscription_runtime_uses_discovered_models_and_json_schema() -> None:
    """The wrapper validates model entitlement and transmits the exact schema."""

    adapter = StubCodexAdapter()
    runtime = CodexSubscriptionRuntime(adapter=adapter)

    result = runtime.run_validated_turn(
        request=course_turn_request(),
        artifact_model=Course,
        cancellation=CancellationToken(),
    )

    assert result.artifact.course_id == "course-python-basics"
    assert adapter.received_output_schema == Course.model_json_schema()
    assert result.usage.billing_source == "chatgpt_subscription"
    assert result.usage.estimated_api_cost is None


def test_subscription_runtime_rejects_an_undiscovered_model() -> None:
    """A configured model cannot be guessed when app-server omits it."""

    runtime = CodexSubscriptionRuntime(adapter=StubCodexAdapter(models=("gpt-5.3",)))

    with pytest.raises(RuntimePolicyError, match="not available"):
        runtime.run_validated_turn(
            request=course_turn_request(model_id="gpt-5.4"),
            artifact_model=Course,
            cancellation=CancellationToken(),
        )


def test_runtime_readiness_keeps_account_model_quota_and_job_state_separate() -> None:
    """A usable provider does not invent quota telemetry or job completion."""

    runtime = CodexSubscriptionRuntime(adapter=StubCodexAdapter())

    readiness = runtime.inspect_readiness(model_id="gpt-5.4")

    assert readiness.status is RuntimeReadinessStatus.ready
    assert readiness.credential_status is CredentialStatus.valid
    assert readiness.model_entitled is True
    assert readiness.subscription_quota_state is SubscriptionQuotaState.unknown
    assert readiness.job_completed is False
    assert any("quota" in warning.casefold() for warning in readiness.warnings)


def test_runtime_readiness_returns_redacted_reauthentication_recovery() -> None:
    """Provider credential failures become a safe recovery state."""

    class ExpiredAdapter(StubCodexAdapter):
        """Raise one credential-shaped provider error without leaking it."""

        def inspect_account_type(self) -> str:
            raise RuntimeError(
                "401 expired credential sk-secret-value at /home/ada/auth.json"
            )

    runtime = CodexSubscriptionRuntime(adapter=ExpiredAdapter())

    readiness = runtime.inspect_readiness(model_id="gpt-5.4")

    assert readiness.status is RuntimeReadinessStatus.unavailable
    assert readiness.credential_status is CredentialStatus.reauthentication_required
    assert readiness.model_entitled is False
    serialized_readiness = readiness.model_dump_json()
    assert "sk-secret-value" not in serialized_readiness
    assert "/home/ada" not in serialized_readiness


def test_runtime_child_environment_removes_platform_api_credentials() -> None:
    """Subscription workers must not inherit API keys from the parent process."""

    parent_environment: Mapping[str, str] = {
        "PATH": "/usr/bin",
        "HOME": "/home/worker",
        "OPENAI_API_KEY": "secret-platform-key",
        "CODEX_API_KEY": "secret-codex-key",
        "TAVILY_API_KEY": "research-secret",
        "openai_api_key": "case-variant-secret",
        "CODEX_HOME": "/home/shared/.codex",
    }

    child_environment = CodexSubscriptionRuntime.build_child_environment(
        parent_environment,
        codex_home=Path("/srv/txt2crs/user-1/codex-home"),
    )

    assert child_environment["PATH"] == "/usr/bin"
    assert child_environment["HOME"] == "/home/worker"
    assert "OPENAI_API_KEY" not in child_environment
    assert "CODEX_API_KEY" not in child_environment
    assert "TAVILY_API_KEY" not in child_environment
    assert "openai_api_key" not in child_environment
    assert child_environment["CODEX_HOME"] == "/srv/txt2crs/user-1/codex-home"


def test_fake_runtime_is_deterministic_and_needs_no_credentials() -> None:
    """Default tests can exercise a full structured turn entirely offline."""

    expected_usage = RuntimeUsage.for_chatgpt_subscription(
        model_id="fake-model",
        input_tokens=20,
        output_tokens=10,
        latency_ms=5,
    )
    runtime = FakeRuntime(
        readiness_status=RuntimeReadinessStatus.ready,
        credential_status=CredentialStatus.valid,
        models=("fake-model",),
        scripted_turns=(
            ScriptedTurn(
                output=valid_course_data(),
                usage=expected_usage,
                thread_id="fake-thread",
                turn_id="fake-turn",
            ),
        ),
    )

    result = runtime.run_validated_turn(
        request=course_turn_request(model_id="fake-model"),
        artifact_model=Course,
        cancellation=CancellationToken(),
    )

    assert result.artifact == Course.model_validate(valid_course_data())
    assert result.usage == expected_usage


def test_cancelled_fake_turn_never_returns_an_artifact() -> None:
    """Cancellation settles before scripted output can be checkpointed."""

    cancellation = CancellationToken()
    cancellation.cancel()
    runtime = FakeRuntime.with_course(valid_course_data(), model_id="fake-model")

    with pytest.raises(RuntimeError, match="cancelled"):
        runtime.run_validated_turn(
            request=course_turn_request(model_id="fake-model"),
            artifact_model=Course,
            cancellation=cancellation,
        )
