"""Tests for strict durable job write and read transport contracts."""

from datetime import UTC, datetime
from typing import cast

import pytest
from pydantic import TypeAdapter, ValidationError
from txt2crs.jobs import (
    ArtifactDeliverable,
    ArtifactFormat,
    ArtifactManifest,
    ArtifactMetadata,
    JobStatus,
    PublicArtifactAvailability,
    PublicFailureCode,
    PublicInputSummary,
    PublicJobFailure,
    PublicJobProgress,
    PublicJobSnapshot,
    PublicResearchMetrics,
    PublicSourceSummary,
)

from app.schemas.jobs import (
    ArtifactManifestPublic,
    IdempotencyKey,
    JobAcceptedPublic,
    JobResearchPublic,
    JobResultPublic,
    JobSourcePublic,
    JobStatusPublic,
    JobSubmissionRequest,
    JobUploadMetadata,
    PromptJobInput,
    TextJobInput,
    UrlJobInput,
    YouTubeJobInput,
    parse_job_upload_metadata,
)


def _preferences() -> dict[str, object]:
    """Return one complete valid learner-preference object."""

    return {
        "level": "auto",
        "audience": None,
        "prior_knowledge": None,
        "learning_goals": [],
        "language": "auto",
    }


def _submission(input_value: dict[str, object]) -> dict[str, object]:
    """Return a valid submission around the supplied discriminated input."""

    return {
        "input": input_value,
        "preferences": _preferences(),
        "consent_to_ai_processing": True,
        "learner_age_group": "adult",
    }


@pytest.mark.parametrize(
    ("input_value", "expected_type"),
    [
        ({"type": "prompt", "value": "Teach database indexes."}, PromptJobInput),
        ({"type": "text", "value": "A"}, TextJobInput),
        ({"type": "url", "value": "https://example.com/course"}, UrlJobInput),
        (
            {"type": "youtube", "value": "https://video.example/watch?v=1"},
            YouTubeJobInput,
        ),
    ],
)
def test_submission_parses_each_reviewed_discriminated_input(
    input_value: dict[str, object],
    expected_type: type[object],
) -> None:
    request = JobSubmissionRequest.model_validate(_submission(input_value))

    assert isinstance(request.input, expected_type)
    assert request.preferences.language == "auto"


@pytest.mark.parametrize(
    "payload",
    [
        _submission({"type": "image", "value": "private"}),
        _submission({"type": "prompt", "value": "ab"}),
        _submission({"type": "prompt", "value": "x" * 10_001}),
        _submission({"type": "text", "value": "   "}),
        _submission({"type": "text", "value": "x" * 200_001}),
        _submission({"type": "url", "value": "http://example.com"}),
        _submission({"type": "url", "value": "/relative"}),
        _submission({"type": "url", "value": f"https://example.com/{'x' * 2_040}"}),
        _submission(
            {"type": "youtube", "value": "https://user:pass@example.com/watch"}
        ),
        _submission({"type": "youtube", "value": "https://example.com/#private"}),
    ],
)
def test_submission_rejects_unreviewed_or_out_of_bounds_input(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        JobSubmissionRequest.model_validate(payload)


@pytest.mark.parametrize(
    "payload",
    [
        {**_submission({"type": "prompt", "value": "Valid topic"}), "owner": "x"},
        _submission(
            {"type": "prompt", "value": "Valid topic", "private_path": "/tmp/x"}
        ),
        {
            **_submission({"type": "prompt", "value": "Valid topic"}),
            "preferences": {**_preferences(), "model_id": "gpt-private"},
        },
    ],
)
def test_submission_rejects_unknown_fields_at_every_level(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError, match="extra"):
        JobSubmissionRequest.model_validate(payload)


@pytest.mark.parametrize(
    "preference_changes",
    [
        {"level": "expert"},
        {"audience": ""},
        {"audience": "x" * 501},
        {"prior_knowledge": ""},
        {"prior_knowledge": "x" * 2_001},
        {"learning_goals": ["ab"]},
        {"learning_goals": ["x" * 501]},
        {"learning_goals": [f"Goal {index}" for index in range(11)]},
        {"learning_goals": ["Learn joins", "  learn   JOINS "]},
        {"language": ""},
        {"language": "x" * 36},
    ],
)
def test_submission_rejects_invalid_preferences(
    preference_changes: dict[str, object],
) -> None:
    payload = _submission({"type": "prompt", "value": "Valid topic"})
    payload["preferences"] = {**_preferences(), **preference_changes}

    with pytest.raises(ValidationError):
        JobSubmissionRequest.model_validate(payload)


def test_submission_strips_human_text_and_keeps_unique_goals() -> None:
    payload = _submission({"type": "prompt", "value": "  Teach indexes.  "})
    payload["preferences"] = {
        **_preferences(),
        "audience": "  first-year students  ",
        "prior_knowledge": "  basic SQL  ",
        "learning_goals": ["  Explain B-trees  ", "Compare index scans"],
    }

    request = JobSubmissionRequest.model_validate(payload)

    assert request.input.value == "Teach indexes."
    assert request.preferences.audience == "first-year students"
    assert request.preferences.prior_knowledge == "basic SQL"
    assert request.preferences.learning_goals == (
        "Explain B-trees",
        "Compare index scans",
    )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("consent_to_ai_processing", False),
        ("consent_to_ai_processing", 1),
        ("learner_age_group", "child"),
        ("learner_age_group", None),
    ],
)
def test_submission_requires_literal_consent_and_reviewed_age_group(
    field_name: str,
    invalid_value: object,
) -> None:
    payload = _submission({"type": "prompt", "value": "Valid topic"})
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        JobSubmissionRequest.model_validate(payload)


@pytest.mark.parametrize("age_group", ["minor", "adult", "not_provided"])
def test_submission_accepts_every_reviewed_age_group(age_group: str) -> None:
    payload = _submission({"type": "prompt", "value": "Valid topic"})
    payload["learner_age_group"] = age_group

    assert JobSubmissionRequest.model_validate(payload).learner_age_group == age_group


def test_upload_metadata_has_no_input_or_transport_override_fields() -> None:
    valid_metadata = {
        "preferences": _preferences(),
        "consent_to_ai_processing": True,
        "learner_age_group": "not_provided",
    }

    metadata = JobUploadMetadata.model_validate(valid_metadata)
    assert metadata.preferences.level == "auto"

    for forbidden_field in ("input", "file_path", "owner", "model_id", "budget"):
        with pytest.raises(ValidationError, match="extra"):
            JobUploadMetadata.model_validate(
                {**valid_metadata, forbidden_field: "private"}
            )


def test_upload_metadata_parser_rejects_invalid_json_and_duplicate_keys() -> None:
    for metadata_json in (
        "not-json",
        "[]",
        "\ud800",
        (
            '{"preferences":{"level":"auto","audience":null,'
            '"prior_knowledge":null,"learning_goals":[],"language":"auto"},'
            '"consent_to_ai_processing":true,"learner_age_group":"adult",'
            '"learner_age_group":"minor"}'
        ),
    ):
        with pytest.raises(ValueError, match="metadata is invalid"):
            parse_job_upload_metadata(metadata_json)


@pytest.mark.parametrize(
    "idempotency_key",
    [
        "request-01",
        "browser.retry_2",
        "owner:course:20260719",
        "a" * 128,
    ],
)
def test_idempotency_key_accepts_only_the_reviewed_pattern(
    idempotency_key: str,
) -> None:
    adapter = TypeAdapter(IdempotencyKey)

    assert adapter.validate_python(idempotency_key) == idempotency_key


@pytest.mark.parametrize(
    "idempotency_key",
    [
        "",
        " ",
        "contains space",
        "contains/slash",
        "contains@email",
        "a" * 129,
        7,
    ],
)
def test_idempotency_key_rejects_invalid_or_coerced_values(
    idempotency_key: object,
) -> None:
    adapter = TypeAdapter(IdempotencyKey)

    with pytest.raises(ValidationError):
        adapter.validate_python(idempotency_key)


def test_accepted_response_is_frozen_bounded_and_allowlisted() -> None:
    response = JobAcceptedPublic(
        schema_version="1.0",
        job_id="job-123",
        status="accepted",
        revision=0,
        status_url="/api/v1/jobs/job-123",
    )

    assert response.model_dump() == {
        "schema_version": "1.0",
        "job_id": "job-123",
        "status": "accepted",
        "revision": 0,
        "status_url": "/api/v1/jobs/job-123",
    }
    with pytest.raises(ValidationError):
        JobAcceptedPublic.model_validate(
            {**response.model_dump(), "idempotency_key": "private"}
        )
    with pytest.raises(ValidationError):
        JobAcceptedPublic(
            schema_version="1.0",
            job_id="job-123",
            status="accepted",
            revision=cast(int, -1),
            status_url="/api/v1/jobs/job-123",
        )


def _public_snapshot(
    *,
    status: JobStatus = JobStatus.completed,
    last_accepted_stage: str | None = "cross_validate_artifacts",
) -> PublicJobSnapshot:
    """Return one complete package projection for explicit mapper tests."""

    has_failure = status in {JobStatus.failed, JobStatus.cancelled}
    failure_code = (
        PublicFailureCode.cancelled
        if status is JobStatus.cancelled
        else PublicFailureCode.generation_failed
    )
    return PublicJobSnapshot(
        schema_version="1.0",
        job_id="job-results-1",
        revision=14,
        status=status,
        created_at=datetime(2026, 7, 20, 8, 0, tzinfo=UTC),
        updated_at=datetime(2026, 7, 20, 8, 15, tzinfo=UTC),
        runtime_activity_at=datetime(2026, 7, 20, 8, 14, tzinfo=UTC),
        last_accepted_stage=last_accepted_stage,
        progress=PublicJobProgress(
            completed_units=9,
            total_units=9,
        ),
        input=PublicInputSummary(
            input_type="pdf",
            display_name="course.pdf",
            size_bytes=2_048,
            extraction_warnings=("One page used OCR.",),
            extraction_warnings_truncated=False,
        ),
        failure=(
            PublicJobFailure(
                code=failure_code,
                message=(
                    "Course generation was cancelled."
                    if status is JobStatus.cancelled
                    else "Course generation could not be completed."
                ),
            )
            if has_failure
            else None
        ),
        course_title="Python Foundations",
        resolved_audience="First-year students",
        resolved_level="beginner",
        resolved_language="en",
        objective_count=3,
        module_count=2,
        research=PublicResearchMetrics(
            fetched_source_count=2,
            charged_source_units=2,
            accepted_source_count=1,
        ),
        sources=(
            PublicSourceSummary(
                title="Python documentation",
                canonical_url="https://docs.python.org/3/",
                publisher="Python Software Foundation",
                retrieved_at=datetime(2026, 7, 20, 7, 0, tzinfo=UTC),
            ),
        ),
        sources_truncated=False,
        conflicts=("One source uses older terminology.",),
        conflicts_truncated=False,
        artifacts=PublicArtifactAvailability(available=True, count=16),
    )


def test_status_response_maps_only_reviewed_package_projection_fields() -> None:
    """The shell nests useful public leaves without serializing private state."""

    response = JobStatusPublic.from_package(_public_snapshot())
    serialized_response = response.model_dump(mode="json")

    assert set(serialized_response) == {
        "schema_version",
        "job_id",
        "status",
        "revision",
        "created_at",
        "updated_at",
        "runtime_activity_at",
        "progress",
        "input",
        "failure",
        "result",
        "artifacts",
    }
    assert response.progress.stage == "ready"
    assert response.progress.message == "Your course materials are ready."
    assert response.input.size_bytes == 2_048
    assert response.input.warnings_truncated is False
    assert response.failure is None
    assert response.result is not None
    assert response.result.title == "Python Foundations"
    assert response.result.audience == "First-year students"
    assert response.result.objective_count == 3
    assert response.result.research.fetched_source_count == 2
    assert response.result.research.accepted_source_count == 1
    assert response.result.sources[0].url == "https://docs.python.org/3/"
    assert response.artifacts.manifest_url == ("/api/v1/jobs/job-results-1/artifacts")
    assert "last_accepted_stage" not in serialized_response


@pytest.mark.parametrize(
    ("status", "expected_stage", "expected_message"),
    [
        (JobStatus.accepted, "queued", "Your course is queued securely."),
        (JobStatus.researching, "researching", "Researching the course source."),
        (JobStatus.drafting, "drafting", "Writing the course modules."),
        (JobStatus.validating, "validating", "Checking all course materials."),
        (JobStatus.rendering, "rendering", "Creating publication formats."),
        (JobStatus.delivering, "delivering", "Securing the finished files."),
        (JobStatus.completed, "ready", "Your course materials are ready."),
        (JobStatus.failed, "failed", "Course generation stopped safely."),
        (JobStatus.cancelled, "cancelled", "Course generation was cancelled."),
    ],
)
def test_status_mapper_exhaustively_uses_fixed_safe_progress_copy(
    status: JobStatus,
    expected_stage: str,
    expected_message: str,
) -> None:
    """Every package status maps to reviewed copy rather than private text."""

    response = JobStatusPublic.from_package(_public_snapshot(status=status))

    assert response.status == status.value
    assert response.progress.stage == expected_stage
    assert response.progress.message == expected_message


def test_status_and_result_contracts_reject_unknown_or_unbounded_fields() -> None:
    """Polling contracts stay strict even when called outside FastAPI."""

    response_payload = JobStatusPublic.from_package(_public_snapshot()).model_dump()
    with pytest.raises(ValidationError, match="extra"):
        JobStatusPublic.model_validate(
            {**response_payload, "checkpoint": {"private": True}}
        )

    source = JobSourcePublic(
        title="Reviewed source",
        url=None,
        publisher="Publisher",
        retrieved_at=datetime(2026, 7, 20, 7, 0, tzinfo=UTC),
    )
    with pytest.raises(ValidationError):
        JobResultPublic(
            title="Course",
            audience="Learners",
            level="beginner",
            language="en",
            objective_count=1,
            module_count=1,
            research=JobResearchPublic(
                fetched_source_count=13,
                charged_source_units=13,
                accepted_source_count=13,
            ),
            sources=cast(tuple[JobSourcePublic, ...], (source,) * 13),
            sources_truncated=True,
            conflicts=(),
            conflicts_truncated=False,
        )
    with pytest.raises(ValidationError, match="extra"):
        JobSourcePublic.model_validate(
            {**source.model_dump(), "evidence_excerpt": "private"}
        )


def _artifact_manifest() -> ArtifactManifest:
    """Return one unordered-by-deliverable but ID-sorted package manifest."""

    artifact_rows = (
        ("answer_key_html", ArtifactDeliverable.answer_key, ArtifactFormat.html),
        ("assessment_pdf", ArtifactDeliverable.assessment, ArtifactFormat.pdf),
        ("course_docx", ArtifactDeliverable.course, ArtifactFormat.docx),
        ("course_pdf", ArtifactDeliverable.course, ArtifactFormat.pdf),
        (
            "review_pack_markdown",
            ArtifactDeliverable.review_pack,
            ArtifactFormat.markdown,
        ),
    )
    return ArtifactManifest(
        schema_version="1.0",
        job_id="job-results-1",
        created_at=datetime(2026, 7, 20, 8, 15, tzinfo=UTC),
        artifacts=tuple(
            ArtifactMetadata(
                artifact_id=artifact_id,
                deliverable=deliverable,
                format=artifact_format,
                safe_file_name=f"{artifact_id}.{artifact_format.value}",
                media_type="application/octet-stream",
                size_bytes=1_024,
                content_hash="sha256:" + ("a" * 64),
            )
            for artifact_id, deliverable, artifact_format in artifact_rows
        ),
    )


def test_manifest_mapper_groups_stable_path_free_download_metadata() -> None:
    """The shell groups package metadata without bodies or private paths."""

    response = ArtifactManifestPublic.from_package(_artifact_manifest())

    assert [group.deliverable for group in response.deliverables] == [
        "course",
        "review_pack",
        "assessment",
        "answer_key",
    ]
    assert [
        artifact.artifact_id for artifact in response.deliverables[0].artifacts
    ] == [
        "course_docx",
        "course_pdf",
    ]
    artifact = response.deliverables[0].artifacts[0]
    assert artifact.file_name == "course_docx.docx"
    assert artifact.download_url == ("/api/v1/jobs/job-results-1/artifacts/course_docx")
    serialized_response = response.model_dump_json()
    assert "path" not in serialized_response
    assert "content" not in artifact.model_dump()
    with pytest.raises(ValidationError, match="extra"):
        type(artifact).model_validate(
            {**artifact.model_dump(), "filesystem_path": "/private/result"}
        )
