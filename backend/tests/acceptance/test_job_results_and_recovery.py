"""Credential-free acceptance for durable results, delivery, and recovery."""

from typing import Any, cast

import pytest
from txt2crs.ai.fake_runtime import FakeRuntime
from txt2crs.ai.runtime import TurnRequest
from txt2crs.application import Txt2CrsApplication
from txt2crs.jobs import JobNotFoundError, JobRecord, JobStatus
from txt2crs.jobs.artifact_store import FilesystemPrivateArtifactStore
from txt2crs.rendering.artifacts import ArtifactRenderer

from app.services.txt2crs_worker import SerialTxt2CrsWorker, WorkerApplication
from tests.acceptance.conftest import DurableResultsHarness


def _submit(
    application: Txt2CrsApplication,
    harness: DurableResultsHarness,
    *,
    user_id: str,
    idempotency_key: str,
) -> JobRecord:
    """Submit one deterministic request through the public package facade."""

    return application.submit(
        user_id=user_id,
        idempotency_key=idempotency_key,
        generation_request=harness.request(),
        admission_reservation=application.default_admission_reservation(),
    )


def _complete(
    application: Txt2CrsApplication,
    harness: DurableResultsHarness,
    *,
    user_id: str = "owner-results-one",
    idempotency_key: str = "results-request-one",
) -> JobRecord:
    """Submit and execute one complete deterministic course using public handles."""

    submitted = _submit(
        application,
        harness,
        user_id=user_id,
        idempotency_key=idempotency_key,
    )
    with application.create_executor(
        job_id=submitted.job_id,
        user_id=user_id,
    ) as executor:
        completed = executor.execute()
    assert completed.status is JobStatus.completed
    return completed


def _read_artifact(
    application: Txt2CrsApplication,
    *,
    user_id: str,
    job_id: str,
    artifact_id: str,
) -> bytes:
    """Consume one verified stream while always closing its package context."""

    with application.open_artifact(
        job_id=job_id,
        user_id=user_id,
        artifact_id=artifact_id,
    ) as chunks:
        return b"".join(chunks)


def _run_worker_until_completed(
    application: Txt2CrsApplication,
    harness: DurableResultsHarness,
    *,
    job_id: str,
    user_id: str,
) -> None:
    """Start a fresh serial supervisor and wait through bounded public polling."""

    worker = SerialTxt2CrsWorker(
        application=cast(WorkerApplication, application),
        poll_interval_seconds=0.01,
        shutdown_timeout_seconds=2,
    )
    worker.start()
    try:
        harness.wait_for_status(
            application,
            job_id=job_id,
            user_id=user_id,
            expected_status=JobStatus.completed,
        )
    finally:
        worker.close()


def test_completed_job_exposes_bounded_result_manifest_and_repeatable_bytes(
    durable_results_harness: DurableResultsHarness,
) -> None:
    """One public lifecycle produces the complete private result surface."""

    application = durable_results_harness.open()
    try:
        completed = _complete(application, durable_results_harness)
        snapshot = application.get_public_job(
            job_id=completed.job_id,
            user_id="owner-results-one",
        )
        manifest = application.get_artifact_manifest(
            job_id=completed.job_id,
            user_id="owner-results-one",
        )
        first_course_pdf = _read_artifact(
            application,
            user_id="owner-results-one",
            job_id=completed.job_id,
            artifact_id="course_pdf",
        )
        repeated_course_pdf = _read_artifact(
            application,
            user_id="owner-results-one",
            job_id=completed.job_id,
            artifact_id="course_pdf",
        )

        assert snapshot.revision == completed.revision
        assert snapshot.status is JobStatus.completed
        assert snapshot.progress.total_units == 9
        assert snapshot.progress.completed_units == 9
        assert snapshot.course_title == "Python Basics"
        assert snapshot.resolved_audience == ("First-year computer-science students")
        assert snapshot.resolved_level == "beginner"
        assert snapshot.resolved_language == "en"
        assert snapshot.objective_count == 1
        assert snapshot.module_count == 1
        assert len(snapshot.sources) == 1
        assert snapshot.sources_truncated is False
        assert snapshot.artifacts.count == 16
        assert len(manifest.artifacts) == 16
        assert first_course_pdf == repeated_course_pdf
        assert first_course_pdf.startswith(b"%PDF")
    finally:
        application.close()


def test_owner_and_missing_identifier_reads_are_indistinguishable(
    durable_results_harness: DurableResultsHarness,
) -> None:
    """Status, manifest, and bytes authorize by owner inside each query."""

    application = durable_results_harness.open()
    try:
        owner_one_job = _complete(application, durable_results_harness)
        owner_two_job = _submit(
            application,
            durable_results_harness,
            user_id="owner-results-two",
            idempotency_key="results-request-one",
        )
        assert owner_two_job.job_id != owner_one_job.job_id

        protected_reads = (
            lambda user_id, job_id: application.get_public_job(
                job_id=job_id,
                user_id=user_id,
            ),
            lambda user_id, job_id: application.get_artifact_manifest(
                job_id=job_id,
                user_id=user_id,
            ),
            lambda user_id, job_id: _read_artifact(
                application,
                user_id=user_id,
                job_id=job_id,
                artifact_id="course_pdf",
            ),
        )
        for protected_read in protected_reads:
            with pytest.raises(JobNotFoundError):
                protected_read("owner-results-two", owner_one_job.job_id)
            with pytest.raises(JobNotFoundError):
                protected_read("owner-results-one", "job-missing-results")
    finally:
        application.close()


def test_completed_artifacts_survive_reopen_with_identical_metadata_and_bytes(
    durable_results_harness: DurableResultsHarness,
) -> None:
    """Delivery reads use durable files rather than an in-memory provider result."""

    with durable_results_harness.open() as first_application:
        completed = _complete(first_application, durable_results_harness)
        job_id = completed.job_id
        first_manifest = first_application.get_artifact_manifest(
            job_id=job_id,
            user_id="owner-results-one",
        )
        first_bytes = _read_artifact(
            first_application,
            user_id="owner-results-one",
            job_id=job_id,
            artifact_id="course_html",
        )

    with durable_results_harness.open() as reopened_application:
        reopened_snapshot = reopened_application.get_public_job(
            job_id=job_id,
            user_id="owner-results-one",
        )
        reopened_manifest = reopened_application.get_artifact_manifest(
            job_id=job_id,
            user_id="owner-results-one",
        )
        reopened_bytes = _read_artifact(
            reopened_application,
            user_id="owner-results-one",
            job_id=job_id,
            artifact_id="course_html",
        )

        assert reopened_snapshot.status is JobStatus.completed
        assert reopened_manifest == first_manifest
        assert reopened_bytes == first_bytes


def test_accepted_job_completes_after_replacement_without_a_wake_event(
    durable_results_harness: DurableResultsHarness,
) -> None:
    """A new worker discovers durable accepted work before its first wait."""

    with durable_results_harness.open() as first_application:
        submitted = _submit(
            first_application,
            durable_results_harness,
            user_id="owner-accepted-restart",
            idempotency_key="accepted-restart",
        )
        durable_request = first_application.recover(
            job_id=submitted.job_id,
            user_id="owner-accepted-restart",
        ).request

    with durable_results_harness.open() as replacement_application:
        replacement_request = replacement_application.recover(
            job_id=submitted.job_id,
            user_id="owner-accepted-restart",
        ).request
        assert replacement_request == durable_request

        _run_worker_until_completed(
            replacement_application,
            durable_results_harness,
            job_id=submitted.job_id,
            user_id="owner-accepted-restart",
        )

        completed = replacement_application.recover(
            job_id=submitted.job_id,
            user_id="owner-accepted-restart",
        )
        assert completed.job.status is JobStatus.completed
        assert completed.request == durable_request


def test_design_course_checkpoint_restarts_with_only_remaining_model_turns(
    durable_results_harness: DurableResultsHarness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolved preferences and the exact plan survive a module-boundary exit."""

    original_runtime_turn = FakeRuntime.run_validated_turn

    def interrupt_before_module(
        runtime: FakeRuntime,
        **turn_arguments: Any,
    ) -> Any:
        request = cast(TurnRequest, turn_arguments["request"])
        # Runtime request stages use underscores, while durable checkpoints use
        # a colon to separate ``write_module`` from the canonical module ID.
        # Interrupting on the runtime spelling proves that ``design_course`` is
        # already durable before the first module-writing provider side effect.
        if request.stage == "write_module_mod-foundations":
            raise SystemExit("simulated replacement after design_course")
        return original_runtime_turn(runtime, **turn_arguments)

    monkeypatch.setattr(
        FakeRuntime,
        "run_validated_turn",
        interrupt_before_module,
    )
    with durable_results_harness.open() as first_application:
        submitted = _submit(
            first_application,
            durable_results_harness,
            user_id="owner-design-restart",
            idempotency_key="design-restart",
        )
        with first_application.create_executor(
            job_id=submitted.job_id,
            user_id="owner-design-restart",
        ) as executor:
            with pytest.raises(SystemExit, match="after design_course"):
                executor.execute()
        interrupted_state = first_application.recover(
            job_id=submitted.job_id,
            user_id="owner-design-restart",
        )
        assert interrupted_state.checkpoint is not None
        assert interrupted_state.checkpoint.stage == "design_course"
        assert interrupted_state.checkpoint.sequence == 4

    replacement_stages: list[str] = []

    def record_replacement_turn(
        runtime: FakeRuntime,
        **turn_arguments: Any,
    ) -> Any:
        request = cast(TurnRequest, turn_arguments["request"])
        replacement_stages.append(request.stage)
        return original_runtime_turn(runtime, **turn_arguments)

    monkeypatch.setattr(
        FakeRuntime,
        "run_validated_turn",
        record_replacement_turn,
    )
    with durable_results_harness.open(
        scenario=durable_results_harness.scenario_after("design_course")
    ) as replacement_application:
        _run_worker_until_completed(
            replacement_application,
            durable_results_harness,
            job_id=submitted.job_id,
            user_id="owner-design-restart",
        )

        assert replacement_stages == [
            "write_module_mod-foundations",
            "generate_review_pack",
            "design_assessment",
            "generate_assessment",
        ]
        completed_state = replacement_application.recover(
            job_id=submitted.job_id,
            user_id="owner-design-restart",
        )
        assert completed_state.request == interrupted_state.request


def test_final_checkpoint_restarts_rendering_without_model_work(
    durable_results_harness: DurableResultsHarness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A render interruption resumes from the accepted canonical bundle."""

    original_render_bundle = ArtifactRenderer.render_bundle
    original_runtime_turn = FakeRuntime.run_validated_turn

    def interrupt_rendering(
        renderer: ArtifactRenderer,
        bundle: object,
    ) -> Any:
        del renderer, bundle
        raise SystemExit("simulated replacement before rendering")

    monkeypatch.setattr(
        ArtifactRenderer,
        "render_bundle",
        interrupt_rendering,
    )
    with durable_results_harness.open() as first_application:
        submitted = _submit(
            first_application,
            durable_results_harness,
            user_id="owner-render-restart",
            idempotency_key="render-restart",
        )
        with first_application.create_executor(
            job_id=submitted.job_id,
            user_id="owner-render-restart",
        ) as executor:
            with pytest.raises(SystemExit, match="before rendering"):
                executor.execute()
        interrupted_state = first_application.recover(
            job_id=submitted.job_id,
            user_id="owner-render-restart",
        )
        assert interrupted_state.job.status is JobStatus.rendering
        assert interrupted_state.checkpoint is not None
        assert interrupted_state.checkpoint.stage == "cross_validate_artifacts"

    model_stages: list[str] = []

    def reject_model_turn(
        runtime: FakeRuntime,
        **turn_arguments: Any,
    ) -> Any:
        request = cast(TurnRequest, turn_arguments["request"])
        model_stages.append(request.stage)
        return original_runtime_turn(runtime, **turn_arguments)

    monkeypatch.setattr(ArtifactRenderer, "render_bundle", original_render_bundle)
    monkeypatch.setattr(FakeRuntime, "run_validated_turn", reject_model_turn)
    with durable_results_harness.open(
        scenario=durable_results_harness.local_replay_scenario()
    ) as replacement_application:
        _run_worker_until_completed(
            replacement_application,
            durable_results_harness,
            job_id=submitted.job_id,
            user_id="owner-render-restart",
        )
        assert model_stages == []


def test_delivery_restart_and_repeated_reads_do_not_repeat_model_work(
    durable_results_harness: DurableResultsHarness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A private-save interruption replays local delivery from its checkpoint."""

    original_save = FilesystemPrivateArtifactStore.save
    save_call_count = 0

    def interrupt_first_save(
        artifact_store: FilesystemPrivateArtifactStore,
        **save_arguments: Any,
    ) -> None:
        nonlocal save_call_count
        save_call_count += 1
        if save_call_count == 1:
            raise SystemExit("simulated replacement during delivery")
        original_save(artifact_store, **save_arguments)

    monkeypatch.setattr(
        FilesystemPrivateArtifactStore,
        "save",
        interrupt_first_save,
    )
    with durable_results_harness.open() as first_application:
        submitted = _submit(
            first_application,
            durable_results_harness,
            user_id="owner-delivery-restart",
            idempotency_key="delivery-restart",
        )
        with first_application.create_executor(
            job_id=submitted.job_id,
            user_id="owner-delivery-restart",
        ) as executor:
            with pytest.raises(SystemExit, match="during delivery"):
                executor.execute()
        interrupted_state = first_application.recover(
            job_id=submitted.job_id,
            user_id="owner-delivery-restart",
        )
        assert interrupted_state.job.status is JobStatus.delivering
        assert interrupted_state.checkpoint is not None
        assert interrupted_state.checkpoint.stage == "cross_validate_artifacts"

    model_stages: list[str] = []
    original_runtime_turn = FakeRuntime.run_validated_turn

    def record_unexpected_model_turn(
        runtime: FakeRuntime,
        **turn_arguments: Any,
    ) -> Any:
        request = cast(TurnRequest, turn_arguments["request"])
        model_stages.append(request.stage)
        return original_runtime_turn(runtime, **turn_arguments)

    monkeypatch.setattr(FilesystemPrivateArtifactStore, "save", original_save)
    monkeypatch.setattr(
        FakeRuntime,
        "run_validated_turn",
        record_unexpected_model_turn,
    )
    with durable_results_harness.open(
        scenario=durable_results_harness.local_replay_scenario()
    ) as replacement_application:
        _run_worker_until_completed(
            replacement_application,
            durable_results_harness,
            job_id=submitted.job_id,
            user_id="owner-delivery-restart",
        )
        first_bytes = _read_artifact(
            replacement_application,
            user_id="owner-delivery-restart",
            job_id=submitted.job_id,
            artifact_id="course_pdf",
        )
        repeated_bytes = _read_artifact(
            replacement_application,
            user_id="owner-delivery-restart",
            job_id=submitted.job_id,
            artifact_id="course_pdf",
        )

        assert model_stages == []
        assert save_call_count == 1
        assert first_bytes == repeated_bytes
