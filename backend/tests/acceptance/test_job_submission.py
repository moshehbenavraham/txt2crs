"""Credential-free acceptance tests for durable job admission and replay."""

from typing import Any

import pytest
from txt2crs.application import Txt2CrsApplication
from txt2crs.jobs import (
    AdmissionQuotaExceededError,
    IdempotencyConflictError,
    JobNotFoundError,
    JobRecord,
    PreparationPolicyError,
)

from tests.acceptance.conftest import DurableSubmissionHarness


def _submit(
    application: Txt2CrsApplication,
    harness: DurableSubmissionHarness,
    *,
    user_id: str = "owner-one",
    idempotency_key: str = "request-one",
    value: str = "Teach relational database indexes.",
) -> JobRecord:
    """Submit through public package contracts and its shared reservation."""

    return application.submit(
        user_id=user_id,
        idempotency_key=idempotency_key,
        generation_request=harness.request(value=value),
        admission_reservation=application.default_admission_reservation(),
    )


def test_durable_commit_survives_close_and_reopen(
    durable_submission_harness: DurableSubmissionHarness,
) -> None:
    first_application = durable_submission_harness.open()
    submitted = _submit(first_application, durable_submission_harness)
    submitted_job_id = submitted.job_id
    submitted_request_hash = submitted.request_hash
    first_application.close()

    reopened_application = durable_submission_harness.open()
    try:
        recovered = reopened_application.recover(
            job_id=submitted_job_id,
            user_id="owner-one",
        )
        runnable = reopened_application.next_runnable()

        assert recovered.job.job_id == submitted_job_id
        assert recovered.request.request_hash == submitted_request_hash
        assert runnable is not None
        assert runnable.job.job_id == submitted_job_id
    finally:
        reopened_application.close()


def test_same_owner_key_replays_same_job_and_changed_work_conflicts(
    durable_submission_harness: DurableSubmissionHarness,
) -> None:
    application = durable_submission_harness.open()
    try:
        first = _submit(application, durable_submission_harness)
        replay = _submit(application, durable_submission_harness)

        assert replay.job_id == first.job_id
        assert replay.revision == first.revision
        with pytest.raises(IdempotencyConflictError):
            _submit(
                application,
                durable_submission_harness,
                value="Teach a different course about query planning.",
            )
        runnable = application.next_runnable()
        assert runnable is not None and runnable.job.job_id == first.job_id
    finally:
        application.close()


def test_atomic_admission_refuses_second_new_job_without_losing_first(
    durable_submission_harness: DurableSubmissionHarness,
) -> None:
    application = durable_submission_harness.open(maximum_jobs_per_user=1)
    try:
        first = _submit(application, durable_submission_harness)

        with pytest.raises(AdmissionQuotaExceededError):
            _submit(
                application,
                durable_submission_harness,
                idempotency_key="request-two",
                value="Teach transaction isolation.",
            )

        recovered = application.recover(
            job_id=first.job_id,
            user_id="owner-one",
        )
        assert recovered.job.job_id == first.job_id
        assert application.next_runnable().job.job_id == first.job_id
    finally:
        application.close()


def test_same_key_isolated_between_two_owners_and_cross_owner_reads_hide_job(
    durable_submission_harness: DurableSubmissionHarness,
) -> None:
    application = durable_submission_harness.open()
    try:
        first_owner_job = _submit(
            application,
            durable_submission_harness,
            user_id="owner-one",
            idempotency_key="shared-browser-key",
        )
        second_owner_job = _submit(
            application,
            durable_submission_harness,
            user_id="owner-two",
            idempotency_key="shared-browser-key",
        )

        assert first_owner_job.job_id != second_owner_job.job_id
        with pytest.raises(JobNotFoundError):
            application.recover(
                job_id=first_owner_job.job_id,
                user_id="owner-two",
            )
        with pytest.raises(JobNotFoundError):
            application.recover(
                job_id=second_owner_job.job_id,
                user_id="owner-one",
            )
    finally:
        application.close()


@pytest.mark.parametrize(
    ("value", "provider_consent", "expected_reason"),
    [
        (
            "Teach relational database indexes.",
            False,
            "provider_consent_required",
        ),
        (
            "Give medical treatment and prescription advice.",
            True,
            "high_risk_review_required",
        ),
    ],
)
def test_policy_refusal_creates_no_durable_job(
    durable_submission_harness: DurableSubmissionHarness,
    value: str,
    provider_consent: bool,
    expected_reason: str,
) -> None:
    application = durable_submission_harness.open()
    try:
        with pytest.raises(PreparationPolicyError) as captured_error:
            application.submit(
                user_id="owner-one",
                idempotency_key="policy-refusal",
                generation_request=durable_submission_harness.request(
                    value=value,
                    provider_consent=provider_consent,
                ),
                admission_reservation=application.default_admission_reservation(),
            )

        assert captured_error.value.reason_code == expected_reason
        assert application.next_runnable() is None
    finally:
        application.close()


def test_submission_and_policy_refusal_never_create_provider_resources(
    durable_submission_harness: DurableSubmissionHarness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider_resource_calls: list[str] = []

    def reject_provider_resources(*_args: Any, **_kwargs: Any) -> None:
        provider_resource_calls.append("provider")
        raise AssertionError("provider resources started in a request")

    monkeypatch.setattr(
        "txt2crs.application.factories.JobRuntimeResourcesFactory.create",
        reject_provider_resources,
    )
    application = durable_submission_harness.open()
    try:
        accepted = _submit(application, durable_submission_harness)
        assert accepted.status.value == "accepted"

        with pytest.raises(PreparationPolicyError):
            application.submit(
                user_id="owner-one",
                idempotency_key="missing-consent",
                generation_request=durable_submission_harness.request(
                    provider_consent=False
                ),
                admission_reservation=application.default_admission_reservation(),
            )
        assert provider_resource_calls == []
    finally:
        application.close()
