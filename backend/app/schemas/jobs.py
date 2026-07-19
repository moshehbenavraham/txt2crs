"""Strict browser-to-shell contracts for durable course-job submission.

These models intentionally contain only learner-selectable values. Owner
identity, provider model, budgets, policy flags, filesystem paths, and
admission reservations are server-owned and therefore cannot appear here.
"""

import json
from enum import StrEnum
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictStr,
    field_validator,
    model_validator,
)

IdempotencyKey = Annotated[
    StrictStr,
    Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9._:-]{1,128}$",
    ),
]
JobIdentifier = Annotated[
    StrictStr,
    Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$",
    ),
]
PromptText = Annotated[StrictStr, Field(min_length=3, max_length=10_000)]
PastedText = Annotated[StrictStr, Field(min_length=1, max_length=200_000)]
HttpsUrlText = Annotated[StrictStr, Field(min_length=9, max_length=2_048)]
OptionalAudience = Annotated[StrictStr, Field(min_length=1, max_length=500)] | None
OptionalPriorKnowledge = (
    Annotated[StrictStr, Field(min_length=1, max_length=2_000)] | None
)
LearningGoal = Annotated[StrictStr, Field(min_length=3, max_length=500)]
LanguageIntent = Annotated[StrictStr, Field(min_length=2, max_length=35)]
StatusUrl = Annotated[
    StrictStr,
    Field(
        min_length=14,
        max_length=160,
        pattern=r"^/api/v1/jobs/[A-Za-z0-9][A-Za-z0-9._:-]*$",
    ),
]


class _StrictFrozenModel(BaseModel):
    """Reject unknown fields, trim strings, and detach immutable values."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )


class PromptJobInput(_StrictFrozenModel):
    """A short topic or course-generation instruction."""

    type: Literal["prompt"]
    value: PromptText


class TextJobInput(_StrictFrozenModel):
    """Finite learner-pasted source text."""

    type: Literal["text"]
    value: PastedText


class _HttpsJobInput(_StrictFrozenModel):
    """Shared shape-only HTTPS validation for package-owned URL handling."""

    value: HttpsUrlText

    @field_validator("value")
    @classmethod
    def require_absolute_public_shape(cls, value: str) -> str:
        """Accept HTTPS syntax without duplicating package host/DNS policy."""

        try:
            parsed_url = urlsplit(value)
            # Reading ``port`` forces malformed bracket/port syntax to fail.
            _parsed_port = parsed_url.port
        except ValueError:
            raise ValueError("URL must be a valid absolute HTTPS URL.") from None
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname is None
            or parsed_url.username is not None
            or parsed_url.password is not None
            or parsed_url.fragment
        ):
            raise ValueError(
                "URL must be absolute HTTPS without credentials or fragments."
            )
        return value


class UrlJobInput(_HttpsJobInput):
    """A public URL whose safety and retrieval remain package-owned."""

    type: Literal["url"]


class YouTubeJobInput(_HttpsJobInput):
    """YouTube intent routed through the package URL adapter."""

    type: Literal["youtube"]


JobInput = Annotated[
    PromptJobInput | TextJobInput | UrlJobInput | YouTubeJobInput,
    Field(discriminator="type"),
]


class JobLearningLevel(StrEnum):
    """Reviewed P0 learner-selectable depth intent."""

    auto = "auto"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    mixed = "mixed"


class JobLearnerAgeGroup(StrEnum):
    """Privacy-minimized age context passed to package policy."""

    minor = "minor"
    adult = "adult"
    not_provided = "not_provided"


class JobPreferences(_StrictFrozenModel):
    """Finite learning intent; all other generation defaults are server-owned."""

    level: JobLearningLevel
    audience: OptionalAudience
    prior_knowledge: OptionalPriorKnowledge
    learning_goals: tuple[LearningGoal, ...] = Field(max_length=10)
    language: LanguageIntent

    @model_validator(mode="after")
    def require_unique_learning_goals(self) -> Self:
        """Reject goals whose text differs only by case or whitespace."""

        normalized_goals = tuple(
            " ".join(learning_goal.casefold().split())
            for learning_goal in self.learning_goals
        )
        if len(normalized_goals) != len(set(normalized_goals)):
            raise ValueError("Learning goals must be unique.")
        return self


class _JobSubmissionMetadata(_StrictFrozenModel):
    """Fields shared by JSON and multipart submissions."""

    preferences: JobPreferences
    consent_to_ai_processing: Literal[True]
    learner_age_group: JobLearnerAgeGroup

    @field_validator("consent_to_ai_processing", mode="before")
    @classmethod
    def require_exact_boolean_true(cls, value: object) -> object:
        """Reject truthy integers or strings instead of coercing consent."""

        if value is not True:
            raise ValueError("Explicit AI processing consent is required.")
        return value


class JobSubmissionRequest(_JobSubmissionMetadata):
    """Strict JSON request with one discriminated source input."""

    input: JobInput


class JobUploadMetadata(_JobSubmissionMetadata):
    """Strict multipart metadata with no file or server-owned fields."""


class JobAcceptedPublic(_StrictFrozenModel):
    """Allowlisted response returned only after a durable package commit."""

    schema_version: Literal["1.0"]
    job_id: JobIdentifier
    status: Literal["accepted"]
    revision: int = Field(ge=0)
    status_url: StatusUrl


def parse_job_upload_metadata(
    metadata_json: str,
    *,
    maximum_metadata_bytes: int = 262_144,
) -> JobUploadMetadata:
    """Parse bounded JSON while rejecting duplicate keys at every object level.

    Python's normal JSON decoder silently keeps the last duplicate key. That
    behavior is unsafe for consent and generation-affecting fields, so this
    parser detects duplicates before Pydantic validates the resulting object.
    """

    try:
        metadata_bytes = metadata_json.encode("utf-8")
    except UnicodeError:
        # Invalid Unicode can arrive from direct Python callers even though a
        # conforming HTTP client cannot encode a lone surrogate as UTF-8.
        raise ValueError("Upload metadata is invalid.") from None

    if maximum_metadata_bytes <= 0 or len(metadata_bytes) > maximum_metadata_bytes:
        raise ValueError("Upload metadata is invalid.")

    def reject_duplicate_keys(
        object_pairs: list[tuple[str, object]],
    ) -> dict[str, object]:
        parsed_object: dict[str, object] = {}
        for key, value in object_pairs:
            if key in parsed_object:
                raise ValueError("duplicate JSON object key")
            parsed_object[key] = value
        return parsed_object

    try:
        parsed_metadata = json.loads(
            metadata_json,
            object_pairs_hook=reject_duplicate_keys,
        )
        if not isinstance(parsed_metadata, dict):
            raise ValueError
        return JobUploadMetadata.model_validate(parsed_metadata)
    except RecursionError, UnicodeError, ValueError:
        # Raise outside the decoder's error text so learner values and keys do
        # not survive in a public exception chain.
        pass
    raise ValueError("Upload metadata is invalid.")


__all__ = [
    "IdempotencyKey",
    "JobAcceptedPublic",
    "JobInput",
    "JobLearnerAgeGroup",
    "JobLearningLevel",
    "JobPreferences",
    "JobSubmissionRequest",
    "JobUploadMetadata",
    "PromptJobInput",
    "TextJobInput",
    "UrlJobInput",
    "YouTubeJobInput",
    "parse_job_upload_metadata",
]
