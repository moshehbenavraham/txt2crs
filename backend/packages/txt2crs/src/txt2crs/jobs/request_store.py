# SPDX-License-Identifier: MIT-0

"""SQLite helpers for immutable generation-request envelopes.

The main job store owns transactions, owner authorization, and public error
translation. This module owns only request-envelope SQL and integrity checks
so those details do not make the already broad job store harder for a new
contributor to navigate.
"""

import sqlite3

from txt2crs.jobs.models import JobRecord
from txt2crs.jobs.requests import (
    GenerationRequest,
    deserialize_generation_request,
)


class PersistedRequestError(RuntimeError):
    """Stored request state is missing or cannot be restored exactly."""


def request_envelope_matches(
    connection: sqlite3.Connection,
    *,
    job_id: str,
    user_id: str,
    request_hash: str,
    serialized_request: str,
) -> bool:
    """Return whether an idempotent replay matches the exact stored envelope."""

    request_row = connection.execute(
        """
        SELECT request_hash, request_json
        FROM generation_requests
        WHERE job_id = ? AND user_id = ?
        """,
        (job_id, user_id),
    ).fetchone()
    return (
        request_row is not None
        and str(request_row["request_hash"]) == request_hash
        and str(request_row["request_json"]) == serialized_request
    )


def insert_request_envelope(
    connection: sqlite3.Connection,
    *,
    job_id: str,
    user_id: str,
    generation_request: GenerationRequest,
    serialized_request: str,
    timestamp: str,
) -> None:
    """Insert one envelope inside the caller-owned admission transaction."""

    connection.execute(
        """
        INSERT INTO generation_requests(
            job_id, user_id, schema_version, request_hash,
            request_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            job_id,
            user_id,
            generation_request.schema_version,
            generation_request.request_hash,
            serialized_request,
            timestamp,
        ),
    )


def load_request_envelope(
    connection: sqlite3.Connection,
    *,
    job: JobRecord,
) -> GenerationRequest:
    """Restore and cross-check one already owner-authorized request envelope."""

    request_row = connection.execute(
        """
        SELECT schema_version, request_hash, request_json
        FROM generation_requests
        WHERE job_id = ? AND user_id = ?
        """,
        (job.job_id, job.user_id),
    ).fetchone()
    if request_row is None:
        raise PersistedRequestError("The persisted generation request is unavailable.")

    generation_request: GenerationRequest | None = None
    try:
        generation_request = deserialize_generation_request(
            str(request_row["request_json"])
        )
    except ValueError:
        # Leave the handler before raising so the private serialized request is
        # not attached to the repository error through exception context.
        pass
    if generation_request is None:
        raise PersistedRequestError("The persisted generation request is unavailable.")

    if (
        str(request_row["schema_version"]) != generation_request.schema_version
        or str(request_row["request_hash"]) != generation_request.request_hash
        or job.request_hash != generation_request.request_hash
    ):
        raise PersistedRequestError("The persisted generation request is unavailable.")
    return generation_request
