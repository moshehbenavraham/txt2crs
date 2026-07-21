# SPDX-License-Identifier: MIT-0

"""Owner-authorized job application service and private delivery boundary."""

import json
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from datetime import UTC, datetime
from hashlib import sha256
from threading import RLock
from typing import Any, Protocol

from pydantic import BaseModel

from txt2crs.jobs.artifact_queries import (
    ARTIFACT_STREAM_CHUNK_BYTES,
    ArtifactManifest,
    _build_artifact_manifest_from_rendered,
    _validate_private_rendered_artifact_metadata,
)
from txt2crs.jobs.models import (
    CompletedJobPayload,
    JobCheckpoint,
    JobRecord,
    JobStatus,
    ResumeState,
)
from txt2crs.jobs.notifications import DeliveryNotificationPolicy
from txt2crs.jobs.public_queries import (
    PublicJobPage,
    PublicJobSnapshot,
    decode_public_job_cursor,
    encode_public_job_cursor,
    project_public_job_snapshot,
    project_public_job_summary,
)
from txt2crs.jobs.quota import AdmissionCapacity, AdmissionReservation
from txt2crs.jobs.requests import GenerationRequest
from txt2crs.jobs.stage_result import StageResult
from txt2crs.jobs.store import (
    ConcurrencyConflictError,
    InvalidJobListRequestError,
    JobNotFoundError,
    SqliteJobStore,
)
from txt2crs.rendering.artifacts import RenderedArtifact


class PrivateArtifactStore(Protocol):
    """Store and read generated artifacts behind owner authorization."""

    def save(
        self,
        *,
        user_id: str,
        job_id: str,
        artifacts: dict[str, RenderedArtifact],
    ) -> None:
        """Persist one idempotent private artifact set."""

    def get_manifest(
        self,
        *,
        user_id: str,
        job_id: str,
    ) -> ArtifactManifest:
        """Return verified path-free metadata for one exact owner and job."""

    def open_artifact(
        self,
        *,
        user_id: str,
        job_id: str,
        artifact_id: str,
    ) -> AbstractContextManager[Iterator[bytes]]:
        """Open one verified bounded byte stream for the context lifetime."""

    def purge_owner(self, *, user_id: str) -> int:
        """Delete every artifact job for one owner and return the count."""


class InMemoryPrivateArtifactStore:
    """Owner-scoped deterministic artifact store for tests/local demos."""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._artifacts: dict[
            tuple[str, str],
            dict[str, RenderedArtifact],
        ] = {}
        self._created_at: dict[tuple[str, str], datetime] = {}
        self._lock = RLock()
        self._clock = clock or (lambda: datetime.now(UTC))
        self.save_count = 0

    def save(
        self,
        *,
        user_id: str,
        job_id: str,
        artifacts: dict[str, RenderedArtifact],
    ) -> None:
        """Save once; exact replays are harmless and conflicts fail closed."""

        _validate_private_rendered_artifact_metadata(artifacts)
        storage_key = (user_id, job_id)
        artifact_snapshot = dict(artifacts)
        with self._lock:
            existing_artifacts = self._artifacts.get(storage_key)
            if existing_artifacts is not None:
                if existing_artifacts != artifact_snapshot:
                    raise ValueError("A different private artifact set already exists.")
                return
            # Obtain and validate the timestamp before mutating either map.
            # Otherwise a failing clock would leave an artifact entry with no
            # corresponding manifest metadata, and an exact retry would return
            # early from that permanently partial state.
            created_at = self._now()
            self._artifacts[storage_key] = artifact_snapshot
            self._created_at[storage_key] = created_at
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

    def get_manifest(
        self,
        *,
        user_id: str,
        job_id: str,
    ) -> ArtifactManifest:
        """Return canonical metadata from one immutable in-memory snapshot."""

        storage_key = (user_id, job_id)
        with self._lock:
            artifacts = self._artifacts.get(storage_key)
            created_at = self._created_at.get(storage_key)
            if artifacts is None or created_at is None:
                raise JobNotFoundError("The requested artifact was not found.")
            artifact_snapshot = dict(artifacts)
        return _build_artifact_manifest_from_rendered(
            job_id=job_id,
            created_at=created_at,
            artifacts=artifact_snapshot,
        )

    @contextmanager
    def open_artifact(
        self,
        *,
        user_id: str,
        job_id: str,
        artifact_id: str,
    ) -> Iterator[Iterator[bytes]]:
        """Yield immutable bounded chunks for one exact owner and artifact ID."""

        storage_key = (user_id, job_id)
        with self._lock:
            artifacts = self._artifacts.get(storage_key)
            created_at = self._created_at.get(storage_key)
            selected_artifact = (
                artifacts.get(artifact_id) if artifacts is not None else None
            )
            if selected_artifact is None or created_at is None:
                raise JobNotFoundError("The requested artifact was not found.")
            # Validate the selected public ID/metadata through the same strict
            # models used by the filesystem store before yielding its bytes.
            _build_artifact_manifest_from_rendered(
                job_id=job_id,
                created_at=created_at,
                artifacts={artifact_id: selected_artifact},
            )
            content_snapshot = bytes(selected_artifact.content)
        yield _iter_in_memory_artifact_chunks(content_snapshot)

    def purge_owner(self, *, user_id: str) -> int:
        """Atomically remove every in-memory artifact set for one owner."""

        with self._lock:
            owner_keys = [
                storage_key
                for storage_key in self._artifacts
                if storage_key[0] == user_id
            ]
            for storage_key in owner_keys:
                del self._artifacts[storage_key]
                del self._created_at[storage_key]
            return len(owner_keys)

    def _now(self) -> datetime:
        """Return an aware UTC timestamp for immutable manifest metadata."""

        current_time = self._clock()
        if current_time.tzinfo is None:
            raise ValueError("Artifact store clock must return a timezone-aware time.")
        return current_time.astimezone(UTC)


class JobService:
    """Coordinate durable state, accepted checkpoints, and delivery side effects."""

    def __init__(
        self,
        *,
        store: SqliteJobStore,
        artifact_store: PrivateArtifactStore,
        notification_policy: DeliveryNotificationPolicy,
    ) -> None:
        self._store = store
        self._artifact_store = artifact_store
        self._notification_policy = notification_policy

    def submit(
        self,
        *,
        user_id: str,
        idempotency_key: str,
        generation_request: GenerationRequest,
        admission_reservation: AdmissionReservation,
    ) -> JobRecord:
        """Durably submit or replay one complete tenant-owned request."""

        return self._store.create_or_get_job(
            user_id=user_id,
            idempotency_key=idempotency_key,
            generation_request=generation_request,
            admission_reservation=admission_reservation,
        )

    def inspect_admission_capacity(
        self,
        *,
        user_id: str,
        reservation: AdmissionReservation,
    ) -> AdmissionCapacity:
        """Return owner capacity from the authoritative durable ledger."""

        return self._store.inspect_admission_capacity(
            user_id=user_id,
            reservation=reservation,
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

        return self._store.get_resume_state(job_id=job_id, user_id=user_id)

    def next_runnable(self) -> ResumeState | None:
        """Return one exact worker item without exposing store queries."""

        return self._store.next_runnable_job()

    def record_runtime_activity(self, *, job_id: str, user_id: str) -> JobRecord:
        """Record a content-free worker heartbeat for one owner/job."""

        return self._store.record_runtime_activity(job_id=job_id, user_id=user_id)

    def get_public_snapshot(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> PublicJobSnapshot:
        """Return one owner-authorized allowlist without private resume state."""

        resume_state = self._store.get_resume_state(
            job_id=job_id,
            user_id=user_id,
        )
        return self._project_public_resume_state(
            resume_state=resume_state,
            user_id=user_id,
        )

    def list_public_jobs(
        self,
        *,
        user_id: str,
        page_size: int,
        cursor: str | None = None,
    ) -> PublicJobPage:
        """Return one owner-scoped newest-first page of public summaries."""

        if page_size < 1 or page_size > 50:
            raise InvalidJobListRequestError("The job-list page size is invalid.")
        cursor_position = decode_public_job_cursor(cursor)
        resume_states = self._store.list_resume_states(
            user_id=user_id,
            # Fetch one extra row to determine continuation without a separate
            # owner count that could race concurrent submissions.
            limit=page_size + 1,
            before_created_at=(
                cursor_position[0] if cursor_position is not None else None
            ),
            before_job_id=(cursor_position[1] if cursor_position is not None else None),
        )
        visible_states = resume_states[:page_size]
        summaries = tuple(
            project_public_job_summary(
                self._project_public_resume_state(
                    resume_state=resume_state,
                    user_id=user_id,
                )
            )
            for resume_state in visible_states
        )
        next_cursor = (
            encode_public_job_cursor(visible_states[-1].job)
            if len(resume_states) > page_size and visible_states
            else None
        )
        return PublicJobPage(
            schema_version="1.0",
            items=summaries,
            next_cursor=next_cursor,
        )

    def _project_public_resume_state(
        self,
        *,
        resume_state: ResumeState,
        user_id: str,
    ) -> PublicJobSnapshot:
        """Attach optional artifacts to an already owner-authorized snapshot."""

        job_id = resume_state.job.job_id
        artifact_manifest: ArtifactManifest | None = None
        try:
            artifact_manifest = self._artifact_store.get_manifest(
                user_id=user_id,
                job_id=job_id,
            )
        except JobNotFoundError:
            # A job can be accepted or actively generating before artifacts
            # exist. Integrity failures remain visible and are never converted
            # into a false "not available" result.
            pass
        return project_public_job_snapshot(
            resume_state=resume_state,
            artifact_manifest=artifact_manifest,
        )

    def get_artifact_manifest(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> ArtifactManifest:
        """Return owner-scoped path-free artifact metadata."""

        return self._artifact_store.get_manifest(
            user_id=user_id,
            job_id=job_id,
        )

    def open_artifact(
        self,
        *,
        job_id: str,
        user_id: str,
        artifact_id: str,
    ) -> AbstractContextManager[Iterator[bytes]]:
        """Return the package-owned context for one verified private stream."""

        return self._artifact_store.open_artifact(
            user_id=user_id,
            job_id=job_id,
            artifact_id=artifact_id,
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
        """Store privately, persist explicit notification state, and complete."""

        current_job = self._store.get_job(job_id=job_id, user_id=user_id)
        payload_hash = _hash_completed_payload(payload)
        notification_state = self._notification_policy.state_for_completion()
        if current_job.status is JobStatus.completed:
            # A completed replay performs no provider or filesystem work, but
            # it still proves that the caller supplied the exact payload and
            # policy state that already own this delivery.
            self._store.record_delivery_if_absent(
                job_id=job_id,
                user_id=user_id,
                payload_hash=payload_hash,
                notification_state=notification_state,
            )
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
        self._store.record_delivery_if_absent(
            job_id=job_id,
            user_id=user_id,
            payload_hash=payload_hash,
            notification_state=notification_state,
        )
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


def _iter_in_memory_artifact_chunks(content: bytes) -> Iterator[bytes]:
    """Yield the deterministic store's immutable bytes in production-sized chunks."""

    for offset in range(0, len(content), ARTIFACT_STREAM_CHUNK_BYTES):
        yield content[offset : offset + ARTIFACT_STREAM_CHUNK_BYTES]
