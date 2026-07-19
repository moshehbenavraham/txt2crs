# SPDX-License-Identifier: MIT-0

"""Immutable generation-request and execution-profile contracts.

The application accepts work before a long-running generation process starts.
That acknowledgement is trustworthy only when every value that can affect the
result is validated and stored together. These contracts deliberately contain
plain configuration values, not live clients, clocks, budgets, or other
process-owned resources.
"""

import base64
import binascii
import json
from enum import StrEnum
from hashlib import sha256
from math import isfinite
from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, field_validator, model_validator

from txt2crs.domain.models import (
    HashValue,
    Identifier,
    SchemaVersion,
    StrictContract,
)
from txt2crs.ingestion.models import InputPayload

AudienceIntent = Annotated[str, Field(min_length=1, max_length=500)]
PreferenceText = Annotated[str, Field(min_length=1, max_length=2_000)]
LearningGoalText = Annotated[str, Field(min_length=3, max_length=500)]
LanguageIntent = Annotated[str, Field(min_length=2, max_length=35)]
RequestContractVersion = Literal["generation-request-v1"]


class FrozenStrictContract(StrictContract):
    """Reject unknown fields and mutation for persisted configuration values."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )


class LearnerAgeGroup(StrEnum):
    """Privacy-minimized learner age context used by package policy."""

    minor = "minor"
    adult = "adult"
    not_provided = "not_provided"


class LearningPreferenceIntent(FrozenStrictContract):
    """Learner choices captured before deterministic preference resolution."""

    audience: AudienceIntent | None
    prior_knowledge: PreferenceText | None
    learning_goals: tuple[LearningGoalText, ...] = Field(max_length=10)
    level: Literal["auto", "beginner", "intermediate", "advanced", "mixed"]
    language: LanguageIntent

    @model_validator(mode="after")
    def require_unique_learning_goals(self) -> Self:
        """Reject goals whose wording differs only by case or whitespace."""

        normalized_goals = tuple(
            " ".join(learning_goal.casefold().split())
            for learning_goal in self.learning_goals
        )
        if len(normalized_goals) != len(set(normalized_goals)):
            raise ValueError("learning goals must be unique")
        return self


class LearningPreferenceDefaults(FrozenStrictContract):
    """Server-selected P0 learning values frozen with an accepted request.

    These values are not learner controls in P0, but they still affect prompts,
    course validation, assessment generation, and rendered output. Keeping them
    in the execution profile prevents a replacement worker from applying newer
    process defaults to already accepted work.
    """

    desired_depth: PreferenceText = "Comprehensive, foundational-to-applied"
    duration_minutes: int = Field(default=120, gt=0, le=100_000)
    tone: Annotated[str, Field(min_length=1, max_length=200)] = (
        "Clear, rigorous, and encouraging"
    )
    accessibility_requirements: tuple[PreferenceText, ...] = Field(
        default=(
            "Semantic headings",
            "Plain-language definitions",
            "Textual explanations of visual concepts",
        ),
        min_length=1,
        max_length=20,
    )
    assessment_item_count: int = Field(default=15, gt=0, le=1_000)
    passing_percentage: int = Field(default=70, ge=0, le=100)

    @model_validator(mode="after")
    def require_unique_accessibility_requirements(self) -> Self:
        """Reject duplicated requirements that differ only by case or spacing."""

        normalized_requirements = tuple(
            " ".join(requirement.casefold().split())
            for requirement in self.accessibility_requirements
        )
        if len(normalized_requirements) != len(set(normalized_requirements)):
            raise ValueError("accessibility requirements must be unique")
        return self


class CurriculumShapeLimits(FrozenStrictContract):
    """Finite local curriculum ranges stored with each accepted request."""

    minimum_objectives: int = Field(default=5, ge=1, le=100)
    maximum_objectives: int = Field(default=12, ge=1, le=100)
    minimum_modules: int = Field(default=3, ge=1, le=100)
    maximum_modules: int = Field(default=6, ge=1, le=100)
    minimum_sections_per_module: int = Field(default=2, ge=1, le=100)
    maximum_sections_per_module: int = Field(default=5, ge=1, le=100)
    minimum_content_blocks_per_section: int = Field(default=3, ge=1, le=500)
    maximum_content_blocks_per_section: int = Field(default=12, ge=1, le=500)

    @model_validator(mode="after")
    def require_ordered_shape_ranges(self) -> Self:
        """Ensure every minimum can be satisfied by its paired maximum."""

        ordered_ranges = (
            (self.minimum_objectives, self.maximum_objectives),
            (self.minimum_modules, self.maximum_modules),
            (
                self.minimum_sections_per_module,
                self.maximum_sections_per_module,
            ),
            (
                self.minimum_content_blocks_per_section,
                self.maximum_content_blocks_per_section,
            ),
        )
        if any(
            minimum_value > maximum_value
            for minimum_value, maximum_value in ordered_ranges
        ):
            raise ValueError("curriculum shape minimum cannot exceed its maximum")
        return self


class RequestRetryPolicy(FrozenStrictContract):
    """Finite retry configuration frozen with an accepted request."""

    maximum_attempts: int = Field(ge=1, le=10)
    base_seconds: float = Field(gt=0, le=60)
    maximum_seconds: float = Field(gt=0, le=60)
    jitter_ratio: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def require_ordered_delays(self) -> Self:
        """Keep the exponential delay cap at or above the initial delay."""

        if self.maximum_seconds < self.base_seconds:
            raise ValueError("maximum retry delay cannot be below the base delay")
        return self


class InputExecutionLimits(FrozenStrictContract):
    """Hard input and normalized-content bounds accepted for one job."""

    maximum_input_bytes: int = Field(gt=0, le=1_000_000_000)
    maximum_metadata_bytes: int = Field(gt=0, le=10_000_000)
    maximum_normalized_characters: int = Field(gt=0, le=10_000_000)
    maximum_pdf_pages: int = Field(gt=0, le=10_000)


class RunExecutionLimits(FrozenStrictContract):
    """Finite scarce-resource limits restored for every replacement worker."""

    maximum_turns: int = Field(gt=0, le=10_000)
    maximum_research_calls: int = Field(gt=0, le=10_000)
    maximum_search_calls: int = Field(gt=0, le=10_000)
    maximum_extract_calls: int = Field(gt=0, le=10_000)
    maximum_sources: int = Field(gt=0, le=10_000)
    maximum_extracted_bytes: int = Field(gt=0, le=1_000_000_000)
    maximum_input_tokens: int = Field(gt=0, le=100_000_000)
    maximum_output_tokens: int = Field(gt=0, le=100_000_000)
    maximum_retries: int = Field(gt=0, le=1_000)
    maximum_repairs: int = Field(gt=0, le=1_000)
    maximum_elapsed_seconds: float = Field(gt=0, le=86_400)

    @model_validator(mode="after")
    def require_consistent_research_call_limits(self) -> Self:
        """Specific search/extract ceilings must fit the aggregate ceiling."""

        specific_call_limit = self.maximum_search_calls + self.maximum_extract_calls
        if specific_call_limit > self.maximum_research_calls:
            raise ValueError(
                "maximum search and extract calls exceed research-call limit"
            )
        return self


class ExecutionProfile(FrozenStrictContract):
    """Immutable versions and finite limits used for one accepted job."""

    schema_version: SchemaVersion
    engine_version: Identifier
    prompt_version: Identifier
    policy_version: Identifier
    model_id: Identifier
    reasoning_effort: Literal["low", "medium", "high", "xhigh"]
    retry_policy: RequestRetryPolicy
    input_limits: InputExecutionLimits
    run_limits: RunExecutionLimits
    preference_defaults: LearningPreferenceDefaults = Field(
        default_factory=LearningPreferenceDefaults
    )
    curriculum_shape_limits: CurriculumShapeLimits = Field(
        default_factory=CurriculumShapeLimits
    )

    @model_validator(mode="after")
    def require_retry_budget_capacity(self) -> Self:
        """Ensure the run budget can pay every configured retry attempt."""

        maximum_retry_count = self.retry_policy.maximum_attempts - 1
        if self.run_limits.maximum_retries < maximum_retry_count:
            raise ValueError("run retry limit cannot cover the retry policy")
        return self


class _GenerationRequestIdentity(FrozenStrictContract):
    """Validated request fields that participate in the canonical hash."""

    schema_version: SchemaVersion
    request_version: RequestContractVersion
    input_payload: InputPayload
    preferences: LearningPreferenceIntent
    provider_consent: bool
    learner_age_group: LearnerAgeGroup
    policy_flags: tuple[Identifier, ...] = Field(max_length=50)
    execution_profile: ExecutionProfile

    @field_validator("input_payload", mode="after")
    @classmethod
    def copy_input_payload_with_exact_metadata(
        cls,
        input_payload: InputPayload,
    ) -> InputPayload:
        """Detach caller state and reject metadata that JSON would coerce."""

        normalized_metadata = _copy_finite_json_metadata(input_payload.metadata)
        # Rebuilding the older mutable ingestion model gives the durable
        # request its own nested instance and metadata containers. A caller
        # retaining the original InputPayload cannot mutate this snapshot.
        return InputPayload(
            input_type=input_payload.input_type,
            value=input_payload.value,
            media_type=input_payload.media_type,
            file_name=input_payload.file_name,
            metadata=normalized_metadata,
        )

    @model_validator(mode="after")
    def validate_identity_invariants(self) -> Self:
        """Reject ambiguous ordering and request data outside stored bounds."""

        if tuple(sorted(set(self.policy_flags))) != self.policy_flags:
            raise ValueError("policy flags must be sorted and unique")
        _validate_input_payload_bounds(
            input_payload=self.input_payload,
            input_limits=self.execution_profile.input_limits,
        )
        return self


class GenerationRequest(_GenerationRequestIdentity):
    """Complete generation-affecting state accepted for one durable job."""

    request_hash: HashValue

    @classmethod
    def create(
        cls,
        *,
        schema_version: SchemaVersion,
        request_version: RequestContractVersion,
        input_payload: InputPayload,
        preferences: LearningPreferenceIntent,
        provider_consent: bool,
        learner_age_group: LearnerAgeGroup,
        policy_flags: tuple[str, ...],
        execution_profile: ExecutionProfile,
    ) -> Self:
        """Normalize one request before computing its canonical identity."""

        # Hash a fully validated hashless contract rather than the caller's raw
        # arguments. This keeps Pydantic whitespace normalization and the
        # canonical identity in lockstep and rejects oversized input before
        # text or bytes are copied into their stored encoding.
        normalized_identity = _GenerationRequestIdentity(
            schema_version=schema_version,
            request_version=request_version,
            input_payload=input_payload,
            preferences=preferences,
            provider_consent=provider_consent,
            learner_age_group=learner_age_group,
            policy_flags=policy_flags,
            execution_profile=execution_profile,
        )
        normalized_identity_data = _request_identity_data(
            schema_version=normalized_identity.schema_version,
            request_version=normalized_identity.request_version,
            input_payload=normalized_identity.input_payload,
            preferences=normalized_identity.preferences,
            provider_consent=normalized_identity.provider_consent,
            learner_age_group=normalized_identity.learner_age_group,
            policy_flags=normalized_identity.policy_flags,
            execution_profile=normalized_identity.execution_profile,
        )
        return cls(
            **normalized_identity.model_dump(mode="python"),
            request_hash=_hash_identity_data(normalized_identity_data),
        )

    @model_validator(mode="after")
    def validate_request_hash(self) -> Self:
        """Reject a copied or tampered hash after all fields are normalized."""

        # Recompute after Pydantic has normalized every nested contract. This
        # catches a copied hash, a modified durable row, and direct model
        # validation that bypasses the ``create`` convenience factory.
        if self.request_hash != _derive_request_hash(self):
            raise ValueError("canonical request hash does not match request")
        return self


def serialize_generation_request(generation_request: GenerationRequest) -> str:
    """Return the ASCII canonical JSON stored in the request envelope.

    ``InputPayload.value`` is the only field that can contain bytes. An
    explicit type tag prevents byte input from colliding with equal UTF-8 text
    and avoids relying on Pydantic's configurable byte codec.
    """

    try:
        # Build one detached validated snapshot, then derive both the hash and
        # stored body from that same snapshot. This closes the small race in
        # which legacy mutable InputPayload metadata could otherwise change
        # between separate hash and storage conversions.
        normalized_identity = _normalized_request_identity(generation_request)
        identity_data = _request_identity_data(
            schema_version=normalized_identity.schema_version,
            request_version=normalized_identity.request_version,
            input_payload=normalized_identity.input_payload,
            preferences=normalized_identity.preferences,
            provider_consent=normalized_identity.provider_consent,
            learner_age_group=normalized_identity.learner_age_group,
            policy_flags=normalized_identity.policy_flags,
            execution_profile=normalized_identity.execution_profile,
        )
        if generation_request.request_hash != _hash_identity_data(identity_data):
            raise ValueError
        identity_data["request_hash"] = generation_request.request_hash
        return _canonical_json(identity_data)
    except (TypeError, ValueError):
        # Raise after leaving the handler so a mutated payload or Pydantic
        # validation object cannot remain attached as sensitive context.
        pass
    raise ValueError("generation request cannot be serialized")


def deserialize_generation_request(serialized_request: str) -> GenerationRequest:
    """Restore and verify one canonical durable request without defaults."""

    try:
        parsed_value = json.loads(serialized_request)
        if not isinstance(parsed_value, dict):
            raise ValueError
        request_data = dict(parsed_value)
        input_payload_data = request_data.get("input_payload")
        if not isinstance(input_payload_data, dict):
            raise ValueError
        restored_input_payload_data = dict(input_payload_data)
        restored_input_payload_data["value"] = _decode_input_value(
            restored_input_payload_data.get("value")
        )
        request_data["input_payload"] = restored_input_payload_data
        return GenerationRequest.model_validate(request_data)
    except (TypeError, ValueError):
        # Leave the exception handler before raising the public error. ``from
        # None`` hides a traceback chain but still retains ``__context__``;
        # raising below after the handler exits removes the sensitive
        # structured Pydantic/JSON error from the public exception entirely.
        pass
    raise ValueError("stored generation request is invalid")


def _request_identity_data(
    *,
    schema_version: str,
    request_version: str,
    input_payload: InputPayload,
    preferences: LearningPreferenceIntent,
    provider_consent: bool,
    learner_age_group: LearnerAgeGroup,
    policy_flags: tuple[str, ...],
    execution_profile: ExecutionProfile,
) -> dict[str, object]:
    """Return every generation-affecting field except the hash itself."""

    input_payload_data = input_payload.model_dump(
        mode="json",
        exclude={"value"},
    )
    input_payload_data["value"] = _encode_input_value(input_payload.value)
    return {
        "schema_version": schema_version,
        "request_version": request_version,
        "input_payload": input_payload_data,
        "preferences": preferences.model_dump(mode="json"),
        "provider_consent": provider_consent,
        "learner_age_group": learner_age_group.value,
        "policy_flags": list(policy_flags),
        "execution_profile": execution_profile.model_dump(mode="json"),
    }


def _encode_input_value(input_value: str | bytes) -> dict[str, str]:
    """Encode raw input with a type tag and reversible ASCII body."""

    if isinstance(input_value, str):
        return {"kind": "text", "data": input_value}
    encoded_bytes = base64.urlsafe_b64encode(input_value).decode("ascii")
    return {"kind": "bytes", "data": encoded_bytes}


def _decode_input_value(encoded_value: object) -> str | bytes:
    """Decode an exact tagged input value from untrusted persisted JSON."""

    if not isinstance(encoded_value, dict) or set(encoded_value) != {
        "kind",
        "data",
    }:
        raise ValueError("stored generation request has invalid input encoding")
    input_kind = encoded_value.get("kind")
    encoded_data = encoded_value.get("data")
    if not isinstance(input_kind, str) or not isinstance(encoded_data, str):
        raise ValueError("stored generation request has invalid input encoding")
    if input_kind == "text":
        return encoded_data
    if input_kind != "bytes":
        raise ValueError("stored generation request has invalid input encoding")
    try:
        return base64.b64decode(
            encoded_data.encode("ascii"),
            altchars=b"-_",
            validate=True,
        )
    except (UnicodeEncodeError, binascii.Error) as encoding_error:
        raise ValueError(
            "stored generation request has invalid input encoding"
        ) from encoding_error


def _derive_request_hash(generation_request: GenerationRequest) -> str:
    """Recompute one request's labeled SHA-256 identity."""

    normalized_identity = _normalized_request_identity(generation_request)
    identity_data = _request_identity_data(
        schema_version=normalized_identity.schema_version,
        request_version=normalized_identity.request_version,
        input_payload=normalized_identity.input_payload,
        preferences=normalized_identity.preferences,
        provider_consent=normalized_identity.provider_consent,
        learner_age_group=normalized_identity.learner_age_group,
        policy_flags=normalized_identity.policy_flags,
        execution_profile=normalized_identity.execution_profile,
    )
    return _hash_identity_data(identity_data)


def _normalized_request_identity(
    generation_request: GenerationRequest,
) -> _GenerationRequestIdentity:
    """Detach and revalidate every hash-bearing field from one request."""

    return _GenerationRequestIdentity(
        schema_version=generation_request.schema_version,
        request_version=generation_request.request_version,
        input_payload=generation_request.input_payload,
        preferences=generation_request.preferences,
        provider_consent=generation_request.provider_consent,
        learner_age_group=generation_request.learner_age_group,
        policy_flags=generation_request.policy_flags,
        execution_profile=generation_request.execution_profile,
    )


def _hash_identity_data(identity_data: dict[str, object]) -> str:
    """Hash the exact canonical JSON bytes for generation-affecting fields."""

    canonical_bytes = _canonical_json(identity_data).encode("ascii")
    return f"sha256:{sha256(canonical_bytes).hexdigest()}"


def _canonical_json(value: object) -> str:
    """Serialize deterministic ASCII JSON or fail without echoing its data."""

    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as serialization_error:
        raise ValueError(
            "generation request contains non-serializable metadata"
        ) from serialization_error


def _copy_finite_json_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Return detached finite JSON metadata or one content-free safe error."""

    try:
        normalized_metadata = _copy_finite_json_value(
            metadata,
            active_container_ids=set(),
        )
    except (RecursionError, ValueError):
        raise ValueError("metadata must contain only finite JSON values") from None
    if not isinstance(normalized_metadata, dict):
        # The public InputPayload type already guarantees a top-level mapping,
        # but keep this helper safe if that shared contract changes later.
        raise ValueError("metadata must contain only finite JSON values")
    return normalized_metadata


def _copy_finite_json_value(
    value: object,
    *,
    active_container_ids: set[int],
) -> object:
    """Recursively detach only values that round-trip through strict JSON."""

    if value is None:
        return value
    if isinstance(value, str):
        return str(value)
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError
        return float(value)
    if isinstance(value, list):
        container_id = id(value)
        if container_id in active_container_ids:
            raise ValueError
        active_container_ids.add(container_id)
        try:
            return [
                _copy_finite_json_value(
                    item,
                    active_container_ids=active_container_ids,
                )
                for item in value
            ]
        finally:
            active_container_ids.remove(container_id)
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError
        container_id = id(value)
        if container_id in active_container_ids:
            raise ValueError
        active_container_ids.add(container_id)
        try:
            return {
                key: _copy_finite_json_value(
                    item,
                    active_container_ids=active_container_ids,
                )
                for key, item in value.items()
            }
        finally:
            active_container_ids.remove(container_id)
    # Tuples, sets, dates, arbitrary objects, and custom serializers can all
    # change type or meaning after JSON recovery, so the durable boundary
    # rejects them instead of guessing a normalization.
    raise ValueError


def _validate_input_payload_bounds(
    *,
    input_payload: InputPayload,
    input_limits: InputExecutionLimits,
) -> None:
    """Enforce raw-input and canonical-metadata bytes before persistence."""

    raw_input = input_payload.value
    input_byte_count = (
        len(raw_input.encode("utf-8")) if isinstance(raw_input, str) else len(raw_input)
    )
    if input_byte_count == 0:
        raise ValueError("input cannot be empty")
    if input_byte_count > input_limits.maximum_input_bytes:
        raise ValueError("input exceeds the execution profile byte limit")

    normalized_metadata = _copy_finite_json_metadata(input_payload.metadata)
    metadata_byte_count = len(_canonical_json(normalized_metadata).encode("ascii"))
    if metadata_byte_count > input_limits.maximum_metadata_bytes:
        raise ValueError("metadata exceeds the execution profile byte limit")
