# SPDX-License-Identifier: MIT-0

"""Separate private operational facts from browser-safe job progress."""

from datetime import datetime
from typing import Any

from pydantic import Field

from txt2crs.domain.models import Identifier, StrictContract
from txt2crs.security.redaction import sanitize_public_text


class PrivateRunEvent(StrictContract):
    """Restricted operational event that is never returned from public APIs."""

    event_id: Identifier
    job_id: Identifier
    stage: Identifier
    status: Identifier
    occurred_at: datetime
    public_message: str
    completed_items: int
    total_items: int
    private_diagnostics: dict[str, Any]


class PublicProgressEvent(StrictContract):
    """Allowlisted progress safe to show only to the authorized job owner."""

    stage: Identifier
    status: Identifier
    occurred_at: datetime
    message: str = Field(max_length=500)
    completed_items: int = Field(ge=0, le=10_000)
    total_items: int = Field(ge=0, le=10_000)


def project_public_progress(private_event: PrivateRunEvent) -> PublicProgressEvent:
    """Create a new allowlisted object; never mutate-and-return private data."""

    bounded_total = min(10_000, max(0, private_event.total_items))
    bounded_completed = min(
        bounded_total,
        max(0, private_event.completed_items),
    )
    return PublicProgressEvent(
        stage=private_event.stage,
        status=private_event.status,
        occurred_at=private_event.occurred_at,
        message=sanitize_public_text(private_event.public_message),
        completed_items=bounded_completed,
        total_items=bounded_total,
    )
