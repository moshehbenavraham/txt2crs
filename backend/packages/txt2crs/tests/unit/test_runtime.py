# SPDX-License-Identifier: MIT-0

"""Tests for the Codex model-runtime boundary."""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from tests.factories import valid_course_data, valid_review_pack_data
from txt2crs.ai.codex_runtime import (
    CodexRuntime,
    RuntimePolicyError,
)
from txt2crs.ai.fake_runtime import FakeRuntime, ScriptedTurn
from txt2crs.ai.model_policy import ExactModelPolicy
from txt2crs.ai.runtime import (
    CancellationReason,
    CancellationToken,
    CodexAdapterResult,
    TurnRequest,
)
from txt2crs.ai.runtime_status import (
    CredentialStatus,
    RuntimeReadinessStatus,
)
from txt2crs.ai.usage import RuntimeUsage, SubscriptionQuotaState
from txt2crs.domain.models import Course, ReviewPack


class StubCodexAdapter:
    """Small adapter double used to exercise the runtime policy."""

    def __init__(
        self,
        *,
        account_type: str = "chatgpt",
        models: tuple[str, ...] = ("gpt-5.6-sol",),
        result_model_id: str | None = None,
        result_output: dict[str, Any] | None = None,
    ) -> None:
        self.account_type = account_type
        self.models = models
        self.result_model_id = result_model_id
        self.result_output = result_output or valid_course_data()
        self.received_request: TurnRequest | None = None
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
        output_schema: dict[str, Any] | None,
        cancellation: CancellationToken,
    ) -> CodexAdapterResult:
        """Record the schema and return a deterministic course."""

        cancellation.raise_if_cancelled()
        self.received_request = request
        self.received_output_schema = output_schema
        return CodexAdapterResult(
            output=self.result_output,
            thread_id="thread-1",
            turn_id="turn-1",
            model_id=self.result_model_id or request.model_id,
            input_tokens=125,
            output_tokens=75,
        )


def course_turn_request(model_id: str = "gpt-5.6-sol") -> TurnRequest:
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


def test_runtime_accepts_api_key_accounts_with_truthful_billing_source() -> None:
    """Post-event operators may choose Platform API authentication."""

    runtime = CodexRuntime(
        adapter=StubCodexAdapter(account_type="api_key"),
        model_policy=ExactModelPolicy(),
    )

    result = runtime.run_validated_turn(
        request=course_turn_request(),
        artifact_model=Course,
        cancellation=CancellationToken(),
    )

    assert result.usage.billing_source == "platform_api"
    assert result.usage.estimated_api_cost is None


def test_subscription_runtime_uses_discovered_models_and_json_schema() -> None:
    """The wrapper transmits a strict-compatible schema for constrained output."""

    adapter = StubCodexAdapter()
    runtime = CodexRuntime(
        adapter=adapter,
        model_policy=ExactModelPolicy(),
    )

    result = runtime.run_validated_turn(
        request=course_turn_request(),
        artifact_model=Course,
        cancellation=CancellationToken(),
    )

    assert result.artifact.course_id == "course-python-basics"
    assert adapter.received_output_schema is not None
    learning_objective_schema = adapter.received_output_schema["$defs"][
        "LearningObjective"
    ]
    assert learning_objective_schema["required"] == list(
        learning_objective_schema["properties"]
    )
    assert "default" not in learning_objective_schema["properties"]["assessed"]
    assert result.usage.billing_source == "chatgpt_subscription"
    assert result.usage.estimated_api_cost is None


def test_subscription_runtime_uses_local_validation_for_unsupported_schema() -> None:
    """Map-shaped fields use a trusted schema prompt and exact local validation."""

    adapter = StubCodexAdapter(result_output=valid_review_pack_data())
    runtime = CodexRuntime(
        adapter=adapter,
        model_policy=ExactModelPolicy(),
    )

    result = runtime.run_validated_turn(
        request=course_turn_request(),
        artifact_model=ReviewPack,
        cancellation=CancellationToken(),
    )

    assert result.artifact.review_pack_id == "review-python-basics"
    assert adapter.received_output_schema is None
    assert adapter.received_request is not None
    assert "JSON Schema" in adapter.received_request.trusted_instructions
    assert '"section_summaries"' in adapter.received_request.trusted_instructions


def test_subscription_runtime_rejects_an_undiscovered_model() -> None:
    """A configured model cannot be guessed when app-server omits it."""

    runtime = CodexRuntime(
        adapter=StubCodexAdapter(models=("gpt-5.4", "gpt-5.6-terra")),
        model_policy=ExactModelPolicy(),
    )

    with pytest.raises(RuntimePolicyError, match="not available"):
        runtime.run_validated_turn(
            request=course_turn_request(),
            artifact_model=Course,
            cancellation=CancellationToken(),
        )


def test_runtime_readiness_keeps_account_model_quota_and_job_state_separate() -> None:
    """A usable provider does not invent quota telemetry or job completion."""

    runtime = CodexRuntime(
        adapter=StubCodexAdapter(),
        model_policy=ExactModelPolicy(),
    )

    readiness = runtime.inspect_readiness()

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

    runtime = CodexRuntime(
        adapter=ExpiredAdapter(),
        model_policy=ExactModelPolicy(),
    )

    readiness = runtime.inspect_readiness()

    assert readiness.status is RuntimeReadinessStatus.unavailable
    assert readiness.credential_status is CredentialStatus.reauthentication_required
    assert readiness.model_entitled is False
    serialized_readiness = readiness.model_dump_json()
    assert "sk-secret-value" not in serialized_readiness
    assert "/home/ada" not in serialized_readiness


def test_subscription_runtime_rejects_adapter_model_substitution() -> None:
    """A provider result cannot silently claim a different or older model."""

    runtime = CodexRuntime(
        adapter=StubCodexAdapter(result_model_id="gpt-5.4"),
        model_policy=ExactModelPolicy(),
    )

    with pytest.raises(RuntimePolicyError, match="configured model"):
        runtime.run_validated_turn(
            request=course_turn_request(),
            artifact_model=Course,
            cancellation=CancellationToken(),
        )


def test_runtime_child_environment_preserves_codex_auth_but_removes_research_key() -> (
    None
):
    """Codex may authenticate either way without receiving the Tavily secret."""

    parent_environment: Mapping[str, str] = {
        "PATH": "/usr/bin",
        "HOME": "/home/worker",
        "OPENAI_API_KEY": "secret-platform-key",
        "CODEX_API_KEY": "secret-codex-key",
        "TAVILY_API_KEY": "research-secret",
        "openai_api_key": "case-variant-secret",
        "CODEX_HOME": "/home/shared/.codex",
    }

    child_environment = CodexRuntime.build_child_environment(
        parent_environment,
        codex_home=Path("/srv/txt2crs/user-1/codex-home"),
    )

    assert child_environment["PATH"] == "/usr/bin"
    assert child_environment["HOME"] == "/home/worker"
    assert child_environment["OPENAI_API_KEY"] == "secret-platform-key"
    assert child_environment["CODEX_API_KEY"] == "secret-codex-key"
    assert "TAVILY_API_KEY" not in child_environment
    assert child_environment["openai_api_key"] == "case-variant-secret"
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


def test_cancellation_token_records_user_request_by_default() -> None:
    """Existing direct cancellation keeps its terminal user-action meaning."""

    cancellation = CancellationToken()

    cancellation.cancel()

    assert cancellation.is_cancelled is True
    assert cancellation.reason is CancellationReason.user_requested


@pytest.mark.parametrize(
    ("first_action", "expected_reason"),
    [
        ("user", CancellationReason.user_requested),
        ("shutdown", CancellationReason.application_shutdown),
    ],
)
def test_cancellation_token_keeps_the_first_authoritative_reason(
    first_action: str,
    expected_reason: CancellationReason,
) -> None:
    """A later cleanup path cannot rewrite why active work was interrupted."""

    cancellation = CancellationToken()

    if first_action == "user":
        cancellation.cancel()
        cancellation.interrupt_for_shutdown()
    else:
        cancellation.interrupt_for_shutdown()
        cancellation.cancel()

    assert cancellation.reason is expected_reason
