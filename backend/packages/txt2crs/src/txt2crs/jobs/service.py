# SPDX-License-Identifier: MIT-0

"""Owner-authorized job application service and private delivery boundary."""

import json
from hashlib import sha256
from threading import RLock
from typing import Any, Protocol

from pydantic import BaseModel

from txt2crs.jobs.models import (
    CompletedJobPayload,
    JobCheckpoint,
    JobRecord,
    JobStatus,
    ResumeState,
)
from txt2crs.jobs.quota import AdmissionReservation
from txt2crs.jobs.stage_result import StageResult
from txt2crs.jobs.store import (
    ConcurrencyConflictError,
    JobNotFoundError,
    SqliteJobStore,
)
from txt2crs.rendering.artifacts import RenderedArtifact


class PrivateArtifactStore(Protocol):
    """Store generated artifacts behind owner authorization."""

    def save(
        self,
        *,
        user_id: str,
        job_id: str,
        artifacts: dict[str, RenderedArtifact],
    ) -> None:
        """Persist one idempotent private artifact set."""


class CompletionNotificationSink(Protocol):
    """Send a completion notification with provider-level idempotency."""

    def send_completion(
        self,
        *,
        user_id: str,
        job_id: str,
        idempotency_key: str,
    ) -> None:
        """Send or deduplicate one completion notification."""


class InMemoryPrivateArtifactStore:
    """Owner-scoped deterministic artifact store for tests/local demos."""

    def __init__(self) -> None:
        self._artifacts: dict[
            tuple[str, str],
            dict[str, RenderedArtifact],
        ] = {}
        self._lock = RLock()
        self.save_count = 0

    def save(
        self,
        *,
        user_id: str,
        job_id: str,
        artifacts: dict[str, RenderedArtifact],
    ) -> None:
        """Save once; exact replays are harmless and conflicts fail closed."""

        storage_key = (user_id, job_id)
        with self._lock:
            existing_artifacts = self._artifacts.get(storage_key)
            if existing_artifacts is not None:
                if existing_artifacts != artifacts:
                    raise ValueError("A different private artifact set already exists.")
                return
            self._artifacts[storage_key] = dict(artifacts)
            self.save_count += 1

    def get(
        self,
        *,
        user_id: str,
        job_id: str,
    ) -> dict[str, RenderedArtifact]:
        """Return artifacts only for their exact owner."""

        with self._lock:
            artifacts = self._artifacts.get((user_id, job_id))
            if artifacts is None:
                raise JobNotFoundError("The requested artifacts were not found.")
            return dict(artifacts)


class JobService:
    """Coordinate durable state, accepted checkpoints, and delivery side effects."""

    def __init__(
        self,
        *,
        store: SqliteJobStore,
        artifact_store: PrivateArtifactStore,
        notification_sink: CompletionNotificationSink,
    ) -> None:
        self._store = store
        self._artifact_store = artifact_store
        self._notification_sink = notification_sink

    def submit(
        self,
        *,
        user_id: str,
        idempotency_key: str,
        input_hash: str,
        admission_reservation: AdmissionReservation,
    ) -> JobRecord:
        """Submit or replay one tenant-owned job."""

        return self._store.create_or_get_job(
            user_id=user_id,
            idempotency_key=idempotency_key,
            input_hash=input_hash,
            admission_reservation=admission_reservation,
        )

    def start(
        self,
        *,
        job_id: str,
        user_id: str,
        expected_revision: int,
    ) -> JobRecord:
        """Claim an accepted job for research."""

        return self._store.compare_and_swap_status(
            job_id=job_id,
            user_id=user_id,
            expected_revision=expected_revision,
            new_status=JobStatus.researching,
        )

    def resume(self, *, job_id: str, user_id: str) -> ResumeState:
        """Return owner-scoped state and only the last accepted checkpoint."""

        return ResumeState(
            job=self._store.get_job(job_id=job_id, user_id=user_id),
            checkpoint=self._store.latest_checkpoint(
                job_id=job_id,
                user_id=user_id,
            ),
        )

    def fail(
        self,
        *,
        job_id: str,
        user_id: str,
        expected_revision: int,
        failure_code: str,
    ) -> JobRecord:
        """Settle a non-terminal job as an explicit visible failure."""

        return self._store.compare_and_swap_status(
            job_id=job_id,
            user_id=user_id,
            expected_revision=expected_revision,
            new_status=JobStatus.failed,
            failure_code=failure_code,
        )

    def cancel(
        self,
        *,
        job_id: str,
        user_id: str,
        expected_revision: int,
    ) -> JobRecord:
        """Settle a non-terminal job after an owner-authorized cancellation."""

        return self._store.compare_and_swap_status(
            job_id=job_id,
            user_id=user_id,
            expected_revision=expected_revision,
            new_status=JobStatus.cancelled,
            failure_code="cancelled",
        )

    def checkpoint_stage(
        self,
        *,
        job_id: str,
        user_id: str,
        expected_revision: int,
        stage: str,
        sequence: int,
        result: StageResult,
        artifact_version: str,
        evidence_version: str | None,
        budget_snapshot: dict[str, Any],
        next_status: JobStatus,
        required_stage: bool,
    ) -> JobRecord:
        """Checkpoint accepted output or convert unusable required output to failure."""

        if not result.can_checkpoint(required_stage=required_stage):
            return self._store.compare_and_swap_status(
                job_id=job_id,
                user_id=user_id,
                expected_revision=expected_revision,
                new_status=JobStatus.failed,
                failure_code=result.issue_code or "stage_not_accepted",
            )

        if isinstance(result.artifact, BaseModel):
            artifact_data = result.artifact.model_dump(mode="json")
        elif isinstance(result.artifact, dict):
            artifact_data = result.artifact
        else:
            raise TypeError("Checkpoint artifacts must be models or dictionaries.")
        checkpoint = JobCheckpoint(
            schema_version="1.0",
            checkpoint_id=f"checkpoint-{job_id}-{sequence}",
            job_id=job_id,
            stage=stage,
            sequence=sequence,
            artifact_version=artifact_version,
            evidence_version=evidence_version,
            artifact=artifact_data,
            budget_snapshot=budget_snapshot,
        )
        return self._store.save_checkpoint(
            checkpoint=checkpoint,
            user_id=user_id,
            expected_job_revision=expected_revision,
            next_status=next_status,
        )

    def complete(
        self,
        *,
        job_id: str,
        user_id: str,
        expected_revision: int,
        payload: CompletedJobPayload,
    ) -> JobRecord:
        """Store privately, dispatch one idempotent notification, and complete."""

        current_job = self._store.get_job(job_id=job_id, user_id=user_id)
        if current_job.status is JobStatus.completed:
            return current_job

        # Entering ``delivering`` is durable. If a worker or storage provider
        # fails afterward, a replacement worker must continue that same outbox
        # operation instead of attempting the invalid delivering->delivering
        # transition.
        if current_job.status is JobStatus.delivering:
            if current_job.revision != expected_revision:
                raise ConcurrencyConflictError(
                    "The job revision changed before delivery resumed."
                )
            delivering_job = current_job
        else:
            delivering_job = self._store.compare_and_swap_status(
                job_id=job_id,
                user_id=user_id,
                expected_revision=expected_revision,
                new_status=JobStatus.delivering,
            )
        self._artifact_store.save(
            user_id=user_id,
            job_id=job_id,
            artifacts=payload.artifacts,
        )
        payload_hash = _hash_completed_payload(payload)
        self._store.record_delivery_if_absent(
            job_id=job_id,
            user_id=user_id,
            payload_hash=payload_hash,
        )
        if self._store.delivery_needs_notification(
            job_id=job_id,
            user_id=user_id,
        ):
            self._notification_sink.send_completion(
                user_id=user_id,
                job_id=job_id,
                idempotency_key=f"delivery:{job_id}",
            )
            self._store.mark_delivery_notified(job_id=job_id, user_id=user_id)
        return self._store.compare_and_swap_status(
            job_id=job_id,
            user_id=user_id,
            expected_revision=delivering_job.revision,
            new_status=JobStatus.completed,
        )


def _hash_completed_payload(payload: CompletedJobPayload) -> str:
    """Hash names, media types, content hashes, and public-safe usage."""

    canonical_payload = {
        "artifacts": {
            artifact_name: {
                "file_name": artifact.file_name,
                "media_type": artifact.media_type,
                "content_hash": sha256(artifact.content).hexdigest(),
            }
            for artifact_name, artifact in sorted(payload.artifacts.items())
        },
        "usage_summary": payload.usage_summary,
    }
    canonical_json = json.dumps(
        canonical_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{sha256(canonical_json.encode('utf-8')).hexdigest()}"
