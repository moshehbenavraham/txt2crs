# SPDX-License-Identifier: MIT-0

"""Tests for the allowlisted private-to-public progress boundary."""

from datetime import UTC, datetime

from txt2crs.observability.events import (
    PrivateRunEvent,
    project_public_progress,
)


def test_public_progress_does_not_leak_private_diagnostics() -> None:
    """Prompts, paths, tokens, provider bodies, and request IDs stay private."""

    private_event = PrivateRunEvent(
        event_id="private-event-1",
        job_id="job-private-123",
        stage="collect_evidence",
        status="running",
        occurred_at=datetime(2026, 7, 17, 12, tzinfo=UTC),
        public_message="Collecting reviewed evidence.",
        completed_items=2,
        total_items=5,
        private_diagnostics={
            "prompt": "hidden system prompt",
            "input": "private learner input",
            "path": "/home/ada/private/source.pdf",
            "authorization": "Bearer secret-token",
            "provider_body": {"request_id": "provider-private-id"},
            "chain_of_thought": "never expose",
        },
    )

    public_event = project_public_progress(private_event)
    rendered_public_event = public_event.model_dump_json()

    assert public_event.stage == "collect_evidence"
    assert public_event.completed_items == 2
    assert "hidden system prompt" not in rendered_public_event
    assert "/home/ada" not in rendered_public_event
    assert "secret-token" not in rendered_public_event
    assert "provider-private-id" not in rendered_public_event
    assert "chain_of_thought" not in rendered_public_event
    assert "job-private-123" not in rendered_public_event


def test_public_progress_bounds_large_messages_and_counts() -> None:
    """A malicious provider message cannot create unbounded browser payloads."""

    private_event = PrivateRunEvent(
        event_id="event-2",
        job_id="job-2",
        stage="write_lessons",
        status="running",
        occurred_at=datetime(2026, 7, 17, 12, tzinfo=UTC),
        public_message="x" * 10_000,
        completed_items=-5,
        total_items=1_000_000,
        private_diagnostics={},
    )

    public_event = project_public_progress(private_event)

    assert len(public_event.message) <= 500
    assert public_event.completed_items == 0
    assert public_event.total_items == 10_000
