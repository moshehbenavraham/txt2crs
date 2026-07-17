# SPDX-License-Identifier: MIT-0

"""Explicit accepted, degraded, failed, and cancelled stage outcomes."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self

from txt2crs.security.redaction import sanitize_public_text


class StageStatus(StrEnum):
    """Every possible terminal state for a pipeline stage."""

    accepted = "accepted"
    degraded = "degraded"
    failed = "failed"
    cancelled = "cancelled"


@dataclass(frozen=True, slots=True)
class StageResult:
    """A stage terminal result with safe public recovery information."""

    status: StageStatus
    artifact: Any | None
    issue_code: str | None
    repair_count: int
    public_message: str
    private_diagnostic_reference: str | None = None

    def __post_init__(self) -> None:
        """Reject contradictory outcomes before they enter job state."""

        if self.repair_count < 0 or self.repair_count > 1:
            raise ValueError("repair_count must be zero or one")
        if self.status is StageStatus.accepted and self.artifact is None:
            raise ValueError("accepted stages require an artifact")
        if self.status in {StageStatus.failed, StageStatus.cancelled} and (
            self.artifact is not None
        ):
            raise ValueError("failed and cancelled stages cannot carry artifacts")
        object.__setattr__(
            self,
            "public_message",
            sanitize_public_text(self.public_message),
        )

    @classmethod
    def accepted(cls, *, artifact: Any, repair_count: int = 0) -> Self:
        """Return a checkpoint-eligible accepted artifact."""

        return cls(
            status=StageStatus.accepted,
            artifact=artifact,
            issue_code=None,
            repair_count=repair_count,
            public_message="Stage completed and validated.",
        )

    @classmethod
    def degraded(
        cls,
        *,
        artifact: Any,
        issue_code: str,
        public_message: str,
        repair_count: int = 0,
    ) -> Self:
        """Return a valid but explicitly limited optional artifact."""

        return cls(
            status=StageStatus.degraded,
            artifact=artifact,
            issue_code=issue_code,
            repair_count=repair_count,
            public_message=public_message,
        )

    @classmethod
    def failed(
        cls,
        *,
        issue_code: str,
        public_message: str,
        repair_count: int = 0,
    ) -> Self:
        """Return a terminal failure with no checkpointable artifact."""

        return cls(
            status=StageStatus.failed,
            artifact=None,
            issue_code=issue_code,
            repair_count=repair_count,
            public_message=public_message,
        )

    @classmethod
    def cancelled(cls, *, public_message: str) -> Self:
        """Return settled cancellation without partial output."""

        return cls(
            status=StageStatus.cancelled,
            artifact=None,
            issue_code="cancelled",
            repair_count=0,
            public_message=public_message,
        )

    def can_checkpoint(self, *, required_stage: bool) -> bool:
        """Allow accepted output, plus explicit degradation only when optional."""

        if self.status is StageStatus.accepted:
            return True
        return self.status is StageStatus.degraded and not required_stage
