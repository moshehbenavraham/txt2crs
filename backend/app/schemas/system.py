"""Strict browser-safe response schemas for system readiness and authentication."""

from enum import StrEnum
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    model_validator,
)
from txt2crs.application import (
    SystemAuthenticationSnapshot,
    SystemAuthenticationState,
)

from app.services.txt2crs_readiness import (
    ReadinessChecks,
    ReadinessCheckState,
    ReadinessSnapshot,
    ReadinessStatus,
)

SafeStatusText = Annotated[str, Field(min_length=1, max_length=500)]
ReviewedModelId = Literal[
    "gpt-5.6",
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-5.6-luna",
]
REVIEWED_MODEL_ID_ADAPTER: TypeAdapter[ReviewedModelId] = TypeAdapter(ReviewedModelId)


class SystemInputMode(StrEnum):
    """Finite P0 input modes the generated client may display."""

    prompt = "prompt"
    text = "text"
    url = "url"
    youtube = "youtube"
    pdf = "pdf"
    document = "document"
    slides = "slides"


class _StrictPublicModel(BaseModel):
    """Reject accidental response fields and detach immutable route values."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class SystemReadinessChecksPublic(_StrictPublicModel):
    """Coarse dimensions with no infrastructure or provider detail."""

    authentication: ReadinessCheckState
    model: ReadinessCheckState
    research: ReadinessCheckState
    storage: ReadinessCheckState
    worker: ReadinessCheckState
    inputs: ReadinessCheckState
    admission: ReadinessCheckState
    runtime_ownership: ReadinessCheckState

    @classmethod
    def from_checks(
        cls,
        checks: ReadinessChecks,
    ) -> SystemReadinessChecksPublic:
        """Copy every reviewed coarse check explicitly."""

        return cls(
            authentication=checks.authentication,
            model=checks.model,
            research=checks.research,
            storage=checks.storage,
            worker=checks.worker,
            inputs=checks.inputs,
            admission=checks.admission,
            runtime_ownership=checks.runtime_ownership,
        )


class SystemReadinessPublic(_StrictPublicModel):
    """HTTP projection of one immutable side-effect-free readiness snapshot."""

    schema_version: Literal["1.0"]
    status: ReadinessStatus
    accepting_jobs: bool
    configured_model_id: ReviewedModelId
    enabled_input_modes: tuple[SystemInputMode, ...] = Field(max_length=20)
    checks: SystemReadinessChecksPublic
    warnings: tuple[SafeStatusText, ...] = Field(max_length=20)
    recovery_actions: tuple[SafeStatusText, ...] = Field(max_length=20)
    checked_at: AwareDatetime
    is_fresh: bool

    @classmethod
    def from_snapshot(cls, snapshot: ReadinessSnapshot) -> SystemReadinessPublic:
        """Copy only the safe fields approved by the system API contract."""

        return cls(
            schema_version="1.0",
            status=snapshot.status,
            accepting_jobs=snapshot.accepting_jobs,
            configured_model_id=REVIEWED_MODEL_ID_ADAPTER.validate_python(
                snapshot.configured_model_id
            ),
            enabled_input_modes=tuple(
                SystemInputMode(mode) for mode in snapshot.enabled_input_modes
            ),
            checks=SystemReadinessChecksPublic.from_checks(snapshot.checks),
            warnings=tuple(snapshot.warnings),
            recovery_actions=tuple(snapshot.recovery_actions),
            checked_at=snapshot.checked_at,
            is_fresh=snapshot.is_fresh,
        )


class SystemAuthenticationPublic(_StrictPublicModel):
    """Validated challenge or terminal state with no account/token data."""

    state: SystemAuthenticationState
    verification_url: Annotated[str, Field(max_length=2_048)] | None
    user_code: (
        Annotated[
            str,
            Field(min_length=4, max_length=64, pattern=r"^[A-Za-z0-9-]+$"),
        ]
        | None
    )
    message: SafeStatusText

    @model_validator(mode="after")
    def _validate_challenge_shape(self) -> Self:
        """Allow URL/code only for a valid waiting challenge."""

        is_waiting = self.state is SystemAuthenticationState.waiting_for_user
        if is_waiting and (self.verification_url is None or self.user_code is None):
            raise ValueError("Waiting authentication requires a URL and user code.")
        if not is_waiting and (
            self.verification_url is not None or self.user_code is not None
        ):
            raise ValueError("Terminal authentication cannot expose a challenge.")

        if self.verification_url is not None:
            parsed_url = urlsplit(self.verification_url)
            if (
                parsed_url.scheme != "https"
                or parsed_url.hostname != "auth.openai.com"
                or parsed_url.username is not None
                or parsed_url.password is not None
                or parsed_url.fragment
            ):
                raise ValueError("Authentication URL is not an approved OpenAI URL.")
        return self

    @classmethod
    def from_snapshot(
        cls,
        snapshot: SystemAuthenticationSnapshot,
    ) -> SystemAuthenticationPublic:
        """Copy only the package's already-sanitized browser fields."""

        return cls(
            state=snapshot.state,
            verification_url=snapshot.verification_url,
            user_code=snapshot.user_code,
            message=snapshot.message,
        )


__all__ = [
    "SystemAuthenticationPublic",
    "SystemInputMode",
    "SystemReadinessChecksPublic",
    "SystemReadinessPublic",
]
