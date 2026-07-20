# SPDX-License-Identifier: MIT-0

"""Deterministic credential-free runtime for tests and local demonstrations."""

from collections import deque
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from txt2crs.ai.codex_runtime import (
    InvalidModelOutputError,
    RuntimePolicyError,
    ValidatedTurnResult,
)
from txt2crs.ai.runtime import CancellationToken, TurnRequest
from txt2crs.ai.runtime_status import CredentialStatus, RuntimeReadinessStatus
from txt2crs.ai.usage import RuntimeUsage

ArtifactType = TypeVar("ArtifactType", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class ScriptedTurn:
    """One output or error consumed in FIFO order by :class:`FakeRuntime`."""

    output: dict[str, Any] | None = None
    usage: RuntimeUsage | None = None
    thread_id: str = "fake-thread"
    turn_id: str = "fake-turn"
    # BaseException allows a test to model abrupt process replacement with
    # ``SystemExit``. Production code never uses this deterministic fake.
    error: BaseException | None = None


class FakeRuntime:
    """Return fixture-selected artifacts while preserving production checks."""

    def __init__(
        self,
        *,
        readiness_status: RuntimeReadinessStatus,
        credential_status: CredentialStatus,
        models: tuple[str, ...],
        scripted_turns: tuple[ScriptedTurn, ...],
        request_sink: list[TurnRequest] | None = None,
    ) -> None:
        self.readiness_status = readiness_status
        self.credential_status = credential_status
        self.models = models
        self._scripted_turns = deque(scripted_turns)
        self._request_sink = request_sink

    @classmethod
    def with_course(
        cls,
        course_data: dict[str, Any],
        *,
        model_id: str,
    ) -> "FakeRuntime":
        """Build the common one-course fixture with truthful fake usage."""

        return cls(
            readiness_status=RuntimeReadinessStatus.ready,
            credential_status=CredentialStatus.valid,
            models=(model_id,),
            scripted_turns=(
                ScriptedTurn(
                    output=course_data,
                    usage=RuntimeUsage.for_chatgpt_subscription(
                        model_id=model_id,
                        input_tokens=1,
                        output_tokens=1,
                        latency_ms=0,
                    ),
                ),
            ),
        )

    def run_validated_turn(
        self,
        *,
        request: TurnRequest,
        artifact_model: type[ArtifactType],
        cancellation: CancellationToken,
    ) -> ValidatedTurnResult[ArtifactType]:
        """Consume one scripted result and validate it like production output."""

        cancellation.raise_if_cancelled()
        if self._request_sink is not None:
            self._request_sink.append(request)
        if self.readiness_status is RuntimeReadinessStatus.unavailable:
            raise RuntimePolicyError("The fake runtime is unavailable.")
        if self.credential_status is not CredentialStatus.valid:
            raise RuntimePolicyError("The fake credential is not valid.")
        if request.model_id not in self.models:
            raise RuntimePolicyError(
                f"Requested model {request.model_id!r} is unavailable."
            )
        if not self._scripted_turns:
            raise RuntimePolicyError("No scripted fake turn remains.")

        scripted_turn = self._scripted_turns.popleft()
        if scripted_turn.error is not None:
            raise scripted_turn.error
        if scripted_turn.output is None or scripted_turn.usage is None:
            raise RuntimePolicyError("The scripted turn has no usable artifact.")
        cancellation.raise_if_cancelled()
        try:
            artifact = artifact_model.model_validate(scripted_turn.output)
        except ValidationError as validation_error:
            raise InvalidModelOutputError(
                "The scripted output is invalid.",
                usage=scripted_turn.usage,
            ) from validation_error
        return ValidatedTurnResult(
            artifact=artifact,
            usage=scripted_turn.usage,
            thread_id=scripted_turn.thread_id,
            turn_id=scripted_turn.turn_id,
        )
