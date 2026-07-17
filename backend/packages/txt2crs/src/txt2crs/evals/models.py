# SPDX-License-Identifier: MIT-0

"""Strict contracts for repeatable private evaluation and public aggregates."""

from typing import Literal

from pydantic import Field

from txt2crs.domain.models import HashValue, Identifier, SchemaVersion, StrictContract


class EvaluationCase(StrictContract):
    """Versioned private test case without embedded learner content."""

    schema_version: SchemaVersion
    case_id: Identifier
    case_version: Identifier
    category: Literal[
        "short_prompt",
        "long_transcript",
        "malformed_input",
        "noisy_extraction",
        "conflicting_evidence",
        "prompt_injection",
        "inaccessible_source",
        "multilingual_rtl",
        "specialist_high_risk",
        "quota_exhaustion",
        "cancellation",
        "invalid_schema",
        "citation_failure",
    ]
    input_hash: HashValue
    expected_invariants: list[Identifier] = Field(min_length=1, max_length=100)
    private_input_reference: str = Field(min_length=1, max_length=2_000)


class EvaluationResult(StrictContract):
    """Private per-case output with immutable artifact/version evidence."""

    schema_version: SchemaVersion
    case_id: Identifier
    case_version: Identifier
    passed: bool
    artifact_hashes: dict[Identifier, HashValue]
    invariant_results: dict[Identifier, bool]
    rubric_scores: dict[Identifier, float]
    prompt_version: Identifier
    schema_versions: dict[Identifier, str]
    model_id: Identifier
    runtime_version: Identifier
    template_version: Identifier
    evidence_version: HashValue | None

    # Human-review signals are deliberately stored only on the private result.
    # The public aggregate contract below has no matching fields, which prevents
    # learner feedback or correction details from leaking during publication.
    learner_rating: int | None = Field(default=None, ge=1, le=5)
    correction_reason_codes: list[Identifier] = Field(
        default_factory=list,
        max_length=100,
    )
    human_review_status: Literal["not_requested", "pending", "completed"] = (
        "not_requested"
    )
    private_feedback_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=2_000,
    )
    private_output_reference: str = Field(min_length=1, max_length=2_000)


class EvaluationPlan(StrictContract):
    """Dry-run/live execution scope shown before provider use."""

    schema_version: SchemaVersion
    case_ids: list[Identifier]
    model_id: Identifier
    maximum_turns: int = Field(gt=0)
    live: bool


class PublishedEvaluationAggregate(StrictContract):
    """Bounded publishable metrics with no case IDs or private references."""

    schema_version: SchemaVersion
    case_count: int = Field(ge=0)
    passed_count: int = Field(ge=0)
    pass_rate: float = Field(ge=0, le=1)
    mean_rubric_scores: dict[Identifier, float]
    invariant_pass_rates: dict[Identifier, float]
