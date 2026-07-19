# SPDX-License-Identifier: MIT-0

"""Public-only deterministic application lifecycle acceptance."""

from pathlib import Path

from tests.factories import (
    deterministic_generation_request,
    deterministic_generation_scenario,
    standard_admission_reservation,
)
from txt2crs.application import (
    ApplicationAdmissionConfig,
    ApplicationStorageConfig,
    DeterministicApplicationConfig,
    DeterministicApplicationFactory,
)


def test_public_factory_runs_and_purges_complete_deterministic_lifecycle(
    tmp_path: Path,
) -> None:
    """No shell, network, credential, or private engine import is required."""

    generation_request = deterministic_generation_request()
    application = DeterministicApplicationFactory(
        DeterministicApplicationConfig(
            storage=ApplicationStorageConfig(
                state_directory=(tmp_path / "state").resolve(),
                maximum_artifact_job_bytes=20_000_000,
                artifact_retention_days=30,
            ),
            admission=ApplicationAdmissionConfig(
                window_seconds=3_600,
                maximum_jobs_per_user=10,
                maximum_jobs_global=100,
                maximum_reserved_tokens_per_user=1_000_000,
                maximum_reserved_tokens_global=10_000_000,
                maximum_research_cost_microusd_per_user=1_000_000,
                maximum_research_cost_microusd_global=10_000_000,
            ),
            default_execution_profile=generation_request.execution_profile,
            scenario=deterministic_generation_scenario(),
        )
    ).create()

    submitted = application.submit(
        user_id="owner-123",
        idempotency_key="public-lifecycle-123",
        generation_request=generation_request,
        admission_reservation=standard_admission_reservation(),
    )
    runnable = application.next_runnable()
    assert runnable is not None and runnable.job.job_id == submitted.job_id

    completed = application.create_executor(
        job_id=submitted.job_id,
        user_id="owner-123",
    ).execute()
    snapshot = application.get_public_job(
        job_id=completed.job_id,
        user_id="owner-123",
    )
    manifest = application.get_artifact_manifest(
        job_id=completed.job_id,
        user_id="owner-123",
    )

    assert completed.status.value == "completed"
    assert snapshot.status.value == "completed"
    assert len(manifest.artifacts) == 16
    with application.open_artifact(
        job_id=completed.job_id,
        user_id="owner-123",
        artifact_id="course_html",
    ) as chunks:
        assert b"course-content" in b"".join(chunks)

    recovered = application.recover(
        job_id=completed.job_id,
        user_id="owner-123",
    )
    assert recovered.job == completed
    purge_result = application.purge_owner(user_id="owner-123")
    assert purge_result.deleted_job_count == 1
    assert purge_result.deleted_artifact_job_count == 1

    repeated_purge = application.purge_owner(user_id="owner-123")
    assert repeated_purge.deleted_job_count == 0
    assert repeated_purge.deleted_artifact_job_count == 0
    application.close()
