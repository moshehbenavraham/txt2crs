# SPDX-License-Identifier: MIT-0

"""Tests for bounded private-to-public durable job projections."""

from dataclasses import asdict
from datetime import UTC, datetime

import pytest

from tests.factories import (
    valid_generation_request,
    valid_pipeline_checkpoint,
    valid_source_data,
)
from txt2crs.generation.pipeline import PipelineCheckpoint
from txt2crs.ingestion.models import IngestionLimits, InputPayload
from txt2crs.ingestion.service import IngestionService
from txt2crs.jobs.models import JobCheckpoint, JobRecord, JobStatus, ResumeState
from txt2crs.jobs.preparation import GenerationPreparationService
from txt2crs.jobs.public_queries import (
    PublicJobProjectionError,
    project_public_job_snapshot,
)
from txt2crs.security.policy import ContentPolicy

_PRIVATE_INPUT = "PRIVATE NORMALIZED LEARNER INPUT SENTINEL"
_PRIVATE_EVIDENCE = "PRIVATE EVIDENCE EXCERPT SENTINEL"
_PRIVATE_PROVIDER_ID = "provider-private-model-id"
_PRIVATE_PATH = "/home/ada/private/course-source.pdf"
_HASH = "sha256:" + ("a" * 64)


def _job(
    *,
    status: JobStatus = JobStatus.validating,
    failure_code: str | None = None,
    request_hash: str = "sha256:" + ("b" * 64),
) -> JobRecord:
    """Return one authorized durable job with stable public timestamps."""

    return JobRecord(
        schema_version="1.0",
        job_id="job-public-query",
        user_id="owner-1",
        idempotency_key="private-idempotency-key",
        request_hash=request_hash,
        status=status,
        revision=7,
        failure_code=failure_code,
        created_at=datetime(2026, 7, 19, 10, 0, tzinfo=UTC),
        updated_at=datetime(2026, 7, 19, 10, 15, tzinfo=UTC),
    )


def _complete_pipeline_checkpoint() -> PipelineCheckpoint:
    """Build accepted cumulative state containing both public and private data."""

    source_data = valid_source_data()
    source_data["canonical_url"] = (
        "https://docs.python.org/3/tutorial/?access_token=private#section"
    )
    source_data["title"] = "The Python Tutorial token-secret123456"
    source_data["publisher_or_author"] = "Python Software Foundation"

    private_evidence_data = {
        "schema_version": "1.0",
        "evidence_id": "ev-private",
        "source_id": source_data["source_id"],
        "excerpt": _PRIVATE_EVIDENCE,
        "location": {
            "label": "Private source location",
            "page": 4,
            "timestamp_seconds": None,
        },
        "content_hash": _HASH,
        "retrieval_method": "web_extract",
        "prompt_injection_warning": True,
    }

    return valid_pipeline_checkpoint(
        normalized_text=_PRIVATE_INPUT,
        input_type="pdf",
        media_type="application/pdf",
        input_metadata={
            "private_path": _PRIVATE_PATH,
            "provider_request_id": "provider-private-request-id",
        },
        warnings=[
            f"Recovered OCR warning from {_PRIVATE_PATH}",
            "x" * 2_000,
        ],
        source_data=source_data,
        evidence_data=private_evidence_data,
        unresolved_conflicts=[
            "Conflicting duration guidance",
            f"Private diagnostic at {_PRIVATE_PATH}",
        ],
        usage_records=[
            {
                "billing_source": "chatgpt_subscription",
                "token_usage_state": "reported",
                "subscription_quota_state": "available",
                "input_tokens": 987,
                "output_tokens": 654,
                "estimated_api_cost": None,
                "model_id": _PRIVATE_PROVIDER_ID,
                "latency_ms": 123,
                "retries": 1,
            }
        ],
    )


def _resume_state(
    *,
    job: JobRecord | None = None,
    checkpoint: PipelineCheckpoint | None = None,
) -> ResumeState:
    """Wrap a complete request and optional pipeline checkpoint for projection."""

    if checkpoint is None:
        request = valid_generation_request(
            input_payload=InputPayload(
                input_type="pdf",
                value=b"%PDF-private-raw-bytes",
                media_type="application/pdf",
                file_name="../../private/course-source.pdf",
                metadata={"private_path": _PRIVATE_PATH},
            )
        )
    else:
        # ``valid_pipeline_checkpoint`` creates this exact accepted request
        # before replacing its normalized document with private sentinels.
        # Keep the public-query fixture coherent with that durable identity.
        input_document = checkpoint.input_document
        request = valid_generation_request(
            input_payload=InputPayload(
                input_type=input_document.input_type,
                value=(
                    input_document.normalized_text
                    if input_document.input_type in {"prompt", "text", "url"}
                    else b"bounded-private-input"
                ),
                media_type=input_document.media_type,
                file_name=(
                    "course-source.pdf" if input_document.input_type == "pdf" else None
                ),
                metadata={},
            )
        )
    selected_job = (job or _job()).model_copy(
        update={"request_hash": request.request_hash}
    )
    durable_checkpoint = (
        JobCheckpoint(
            schema_version="1.0",
            checkpoint_id="checkpoint-public-query-9",
            job_id=selected_job.job_id,
            stage=checkpoint.stage,
            sequence=checkpoint.sequence,
            artifact_version=_HASH,
            evidence_version=_HASH,
            artifact=checkpoint.model_dump(mode="json"),
            budget_snapshot=asdict(checkpoint.budget_snapshot),
        )
        if checkpoint is not None
        else None
    )
    return ResumeState(
        job=selected_job,
        request=request,
        checkpoint=durable_checkpoint,
    )


def test_public_snapshot_allowlists_useful_state_without_private_payloads() -> None:
    """A realistic cumulative checkpoint cannot leak through public JSON."""

    snapshot = project_public_job_snapshot(
        resume_state=_resume_state(checkpoint=_complete_pipeline_checkpoint()),
        artifact_manifest=None,
    )
    serialized_snapshot = snapshot.model_dump_json()

    assert snapshot.job_id == "job-public-query"
    assert snapshot.revision == 7
    assert snapshot.status is JobStatus.validating
    assert snapshot.last_accepted_stage == "cross_validate_artifacts"
    assert snapshot.progress.completed_units == 9
    assert snapshot.progress.total_units == 9
    assert snapshot.input.input_type == "pdf"
    assert snapshot.input.display_name == "course-source.pdf"
    assert snapshot.input.size_bytes == len(b"bounded-private-input")
    assert snapshot.input.extraction_warnings_truncated is False
    assert snapshot.course_title == "Python Basics"
    assert snapshot.resolved_audience == "First-year computer-science students"
    assert snapshot.resolved_level == "beginner"
    assert snapshot.resolved_language == "en"
    assert snapshot.objective_count == 1
    assert snapshot.module_count == 1
    assert snapshot.sources[0].canonical_url == "https://docs.python.org/3/tutorial/"
    assert snapshot.sources[0].title == "The Python Tutorial [REDACTED]"
    assert snapshot.sources_truncated is False
    assert snapshot.conflicts[0] == "Conflicting duration guidance"
    assert snapshot.conflicts[1] == "Private diagnostic at [PRIVATE_PATH]"
    assert snapshot.conflicts_truncated is False
    assert snapshot.artifacts.available is False
    assert snapshot.artifacts.count == 0

    for private_value in (
        _PRIVATE_INPUT,
        _PRIVATE_EVIDENCE,
        _PRIVATE_PROVIDER_ID,
        _PRIVATE_PATH,
        "private-idempotency-key",
        "provider-private-request-id",
        "access_token",
        "private-raw-bytes",
        "987",
        "654",
    ):
        assert private_value not in serialized_snapshot

    assert set(snapshot.model_dump(mode="json")) == {
        "schema_version",
        "job_id",
        "revision",
        "status",
        "created_at",
        "updated_at",
        "last_accepted_stage",
        "progress",
        "input",
        "failure",
        "course_title",
        "resolved_audience",
        "resolved_level",
        "resolved_language",
        "objective_count",
        "module_count",
        "sources",
        "sources_truncated",
        "conflicts",
        "conflicts_truncated",
        "artifacts",
    }


def test_public_snapshot_bounds_messages_lists_and_progress() -> None:
    """Untrusted display strings and counters stay finite and coherent."""

    checkpoint = _complete_pipeline_checkpoint()
    snapshot = project_public_job_snapshot(
        resume_state=_resume_state(checkpoint=checkpoint),
        artifact_manifest=None,
    )

    assert len(snapshot.input.extraction_warnings) == 2
    assert all(len(warning) <= 500 for warning in snapshot.input.extraction_warnings)
    assert snapshot.progress.total_units is not None
    assert 0 <= snapshot.progress.completed_units <= snapshot.progress.total_units
    assert snapshot.progress.total_units <= 108
    assert all(len(conflict) <= 500 for conflict in snapshot.conflicts)
    assert len(snapshot.sources) <= 12


def test_public_snapshot_truncates_lists_and_omits_credential_urls() -> None:
    """Maximum private lists and credential URLs cannot expand public output."""

    credential_source = valid_source_data()
    credential_source["canonical_url"] = (
        "https://private-user:private-password@example.test/source?token=private"
    )
    checkpoint = valid_pipeline_checkpoint(
        warnings=[f"Extraction warning {index}" for index in range(100)],
        unresolved_conflicts=[f"Unresolved conflict {index}" for index in range(100)],
        source_data=credential_source,
    )

    snapshot = project_public_job_snapshot(
        resume_state=_resume_state(checkpoint=checkpoint),
        artifact_manifest=None,
    )

    assert len(snapshot.input.extraction_warnings) == 20
    assert snapshot.input.extraction_warnings[0] == "Extraction warning 0"
    assert snapshot.input.extraction_warnings[-1] == "Extraction warning 19"
    assert snapshot.input.extraction_warnings_truncated is True
    assert len(snapshot.conflicts) == 20
    assert snapshot.conflicts[0] == "Unresolved conflict 0"
    assert snapshot.conflicts[-1] == "Unresolved conflict 19"
    assert snapshot.conflicts_truncated is True
    assert snapshot.sources[0].canonical_url is None
    assert "private-user" not in snapshot.model_dump_json()
    assert "private-password" not in snapshot.model_dump_json()


def test_public_snapshot_caps_sources_and_reports_omitted_valid_items() -> None:
    """The polling projection cannot grow with a large valid evidence set."""

    checkpoint_data = valid_pipeline_checkpoint().model_dump(mode="json")
    source_records: list[dict[str, object]] = []
    for source_index in range(13):
        source_record = valid_source_data()
        source_record.update(
            {
                "source_id": f"src-public-{source_index:02d}",
                "canonical_url": f"https://example.test/source/{source_index}",
                "title": f"Public source {source_index}",
            }
        )
        source_records.append(source_record)
    checkpoint_data["evidence_set"]["sources"] = source_records
    checkpoint_data["evidence_set"]["excerpts"][0]["source_id"] = "src-public-00"
    checkpoint = PipelineCheckpoint.model_validate(checkpoint_data)

    snapshot = project_public_job_snapshot(
        resume_state=_resume_state(checkpoint=checkpoint),
        artifact_manifest=None,
    )

    assert len(snapshot.sources) == 12
    assert snapshot.sources[0].title == "Public source 0"
    assert snapshot.sources[-1].title == "Public source 11"
    assert snapshot.sources_truncated is True
    assert "Public source 12" not in snapshot.model_dump_json()


def test_public_snapshot_omits_secret_shaped_url_paths() -> None:
    """A path segment must not become a second way to reflect URL credentials."""

    private_path_token = "token-secret123456"
    credential_source = valid_source_data()
    credential_source["canonical_url"] = (
        f"https://example.test/course/{private_path_token}/lesson"
    )
    checkpoint = valid_pipeline_checkpoint(source_data=credential_source)

    snapshot = project_public_job_snapshot(
        resume_state=_resume_state(checkpoint=checkpoint),
        artifact_manifest=None,
    )

    assert snapshot.sources[0].canonical_url is None
    assert private_path_token not in snapshot.model_dump_json()


def test_accepted_snapshot_uses_fixed_display_copy_without_raw_input() -> None:
    """A request without a checkpoint exposes only a safe source label."""

    resume_state = _resume_state(job=_job(status=JobStatus.accepted))

    snapshot = project_public_job_snapshot(
        resume_state=resume_state,
        artifact_manifest=None,
    )

    assert snapshot.status is JobStatus.accepted
    assert snapshot.last_accepted_stage is None
    assert snapshot.progress.completed_units == 0
    assert snapshot.progress.total_units is None
    assert snapshot.input.display_name == "course-source.pdf"
    assert snapshot.input.size_bytes == len(b"%PDF-private-raw-bytes")
    assert snapshot.input.extraction_warnings == ()
    assert snapshot.input.extraction_warnings_truncated is False
    assert snapshot.course_title is None
    assert snapshot.resolved_audience is None
    assert snapshot.resolved_level is None
    assert snapshot.resolved_language is None
    assert snapshot.objective_count is None
    assert snapshot.module_count is None
    assert snapshot.sources == ()
    assert snapshot.sources_truncated is False
    assert snapshot.conflicts == ()
    assert snapshot.conflicts_truncated is False
    assert "%PDF-private-raw-bytes" not in snapshot.model_dump_json()


def test_text_input_size_counts_utf8_bytes_without_exposing_text() -> None:
    """Display metadata measures transport bytes, not Unicode code points."""

    private_text = "Course input with \N{GREEK SMALL LETTER PI}."
    request = valid_generation_request(value=private_text)
    resume_state = ResumeState(
        job=_job(
            status=JobStatus.accepted,
            request_hash=request.request_hash,
        ),
        request=request,
        checkpoint=None,
    )

    snapshot = project_public_job_snapshot(
        resume_state=resume_state,
        artifact_manifest=None,
    )

    assert snapshot.input.size_bytes == len(private_text.encode("utf-8"))
    assert private_text not in snapshot.model_dump_json()


def test_completed_snapshot_reports_the_finite_course_plan_total() -> None:
    """Completion fills every checkpoint unit in the accepted course plan."""

    snapshot = project_public_job_snapshot(
        resume_state=_resume_state(
            job=_job(status=JobStatus.completed),
            checkpoint=valid_pipeline_checkpoint(),
        ),
        artifact_manifest=None,
    )

    assert snapshot.progress.total_units == 9
    assert snapshot.progress.completed_units == 9
    assert snapshot.objective_count == 1
    assert snapshot.module_count == 1


def test_public_snapshot_rejects_job_and_request_identity_mismatch() -> None:
    """A direct projection caller cannot pair a job with another request."""

    coherent_state = _resume_state(job=_job(status=JobStatus.accepted))
    mismatched_state = ResumeState(
        job=coherent_state.job.model_copy(update={"request_hash": _HASH}),
        request=coherent_state.request,
        checkpoint=None,
    )

    with pytest.raises(PublicJobProjectionError) as error_info:
        project_public_job_snapshot(
            resume_state=mismatched_state,
            artifact_manifest=None,
        )

    assert error_info.value.__cause__ is None
    assert error_info.value.__context__ is None


def test_preparation_only_snapshot_exposes_progress_without_private_state() -> None:
    """Sequence-1 preparation is useful publicly without exposing its contents."""

    private_goal = "PRIVATE LEARNING GOAL SENTINEL"
    request = valid_generation_request(
        value=_PRIVATE_INPUT,
        learning_goal=private_goal,
    )
    preparation = GenerationPreparationService(
        ingestion_service=IngestionService(
            limits=IngestionLimits(
                maximum_input_bytes=1_000,
                maximum_normalized_characters=2_000,
            ),
            adapters={},
        ),
        content_policy=ContentPolicy(policy_version="content-policy-v1"),
    ).prepare(request)
    job = _job(
        status=JobStatus.researching,
        request_hash=request.request_hash,
    )
    resume_state = ResumeState(
        job=job,
        request=request,
        checkpoint=JobCheckpoint(
            schema_version="1.0",
            checkpoint_id="checkpoint-public-query-1",
            job_id=job.job_id,
            stage="prepare_input",
            sequence=1,
            artifact_version=_HASH,
            evidence_version=None,
            artifact=preparation.model_dump(mode="json"),
            budget_snapshot={},
        ),
    )

    snapshot = project_public_job_snapshot(
        resume_state=resume_state,
        artifact_manifest=None,
    )
    serialized_snapshot = snapshot.model_dump_json()

    assert snapshot.last_accepted_stage == "prepare_input"
    assert snapshot.progress.completed_units == 1
    assert snapshot.progress.total_units is None
    assert snapshot.input.input_type == "text"
    assert snapshot.input.display_name == "Pasted text"
    assert snapshot.sources == ()
    assert snapshot.course_title is None
    for private_value in (
        _PRIVATE_INPUT,
        private_goal,
        preparation.request_hash,
        preparation.policy_decision.policy_version,
        preparation.policy_decision.reason_code,
        preparation.planning_preferences.desired_depth,
    ):
        assert private_value not in serialized_snapshot


def test_public_snapshot_rejects_checkpoint_from_a_different_request() -> None:
    """A transplanted checkpoint cannot expose another request's safe leaves."""

    requested_job = valid_generation_request(value="Requested learner source.")
    foreign_request = valid_generation_request(value="Foreign learner source.")
    foreign_preparation = GenerationPreparationService(
        ingestion_service=IngestionService(
            limits=IngestionLimits(
                maximum_input_bytes=1_000,
                maximum_normalized_characters=2_000,
            ),
            adapters={},
        ),
        content_policy=ContentPolicy(policy_version="content-policy-v1"),
    ).prepare(foreign_request)
    job = _job(
        status=JobStatus.researching,
        request_hash=requested_job.request_hash,
    )
    resume_state = ResumeState(
        job=job,
        request=requested_job,
        checkpoint=JobCheckpoint(
            schema_version="1.0",
            checkpoint_id="checkpoint-foreign-preparation",
            job_id=job.job_id,
            stage="prepare_input",
            sequence=1,
            artifact_version=_HASH,
            evidence_version=None,
            artifact=foreign_preparation.model_dump(mode="json"),
            budget_snapshot={},
        ),
    )

    with pytest.raises(PublicJobProjectionError) as error_info:
        project_public_job_snapshot(
            resume_state=resume_state,
            artifact_manifest=None,
        )

    assert "Foreign learner source" not in str(error_info.value)
    assert error_info.value.__cause__ is None
    assert error_info.value.__context__ is None


@pytest.mark.parametrize(
    ("failure_code", "public_code", "public_message"),
    [
        (
            "provider_consent_required",
            "provider_consent_required",
            "Permission to use the configured providers is required.",
        ),
        (
            "private_provider_failure_code",
            "generation_failed",
            "Course generation could not be completed.",
        ),
        (
            "cancelled",
            "cancelled",
            "Course generation was cancelled.",
        ),
    ],
)
def test_public_failure_mapping_never_reflects_private_codes(
    failure_code: str,
    public_code: str,
    public_message: str,
) -> None:
    """Only reviewed package failures cross the public projection boundary."""

    status = JobStatus.cancelled if failure_code == "cancelled" else JobStatus.failed
    snapshot = project_public_job_snapshot(
        resume_state=_resume_state(job=_job(status=status, failure_code=failure_code)),
        artifact_manifest=None,
    )

    assert snapshot.failure is not None
    assert snapshot.failure.code == public_code
    assert snapshot.failure.message == public_message
    if failure_code == "private_provider_failure_code":
        assert failure_code not in snapshot.model_dump_json()


def test_failed_snapshot_cannot_report_a_cancelled_failure() -> None:
    """A private code cannot contradict the durable public terminal status."""

    snapshot = project_public_job_snapshot(
        resume_state=_resume_state(
            job=_job(status=JobStatus.failed, failure_code="cancelled")
        ),
        artifact_manifest=None,
    )

    assert snapshot.failure is not None
    assert snapshot.failure.code == "generation_failed"
    assert snapshot.failure.message == "Course generation could not be completed."


def test_incompatible_checkpoint_raises_context_free_projection_error() -> None:
    """Corrupt private checkpoint content is never echoed or chained publicly."""

    private_sentinel = "PRIVATE MALFORMED CHECKPOINT SENTINEL"
    resume_state = _resume_state(job=_job(status=JobStatus.drafting))
    resume_state = ResumeState(
        job=resume_state.job,
        request=resume_state.request,
        checkpoint=JobCheckpoint(
            schema_version="1.0",
            checkpoint_id="checkpoint-malformed",
            job_id=resume_state.job.job_id,
            stage="write_module:private",
            sequence=5,
            artifact_version=_HASH,
            evidence_version=None,
            artifact={"raw_private_payload": private_sentinel},
            budget_snapshot={"private_tokens": 999},
        ),
    )

    with pytest.raises(
        PublicJobProjectionError,
        match="public job snapshot",
    ) as error_info:
        project_public_job_snapshot(
            resume_state=resume_state,
            artifact_manifest=None,
        )

    assert private_sentinel not in str(error_info.value)
    assert error_info.value.__cause__ is None
    assert error_info.value.__context__ is None
