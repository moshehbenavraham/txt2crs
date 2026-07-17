# SPDX-License-Identifier: MIT-0

"""Tests for authenticated, timestamped, replay-resistant internal requests."""

import hmac
from hashlib import sha256

import pytest
from pydantic import SecretStr

from txt2crs.security.signed_requests import (
    InMemoryReplayStore,
    RequestAuthenticationError,
    SignedRequestVerifier,
)


def signature(secret: str, timestamp: int, body: bytes) -> str:
    """Produce the documented HMAC spelling used by request tests."""

    signed_payload = str(timestamp).encode("ascii") + b"." + body
    return hmac.new(secret.encode("utf-8"), signed_payload, sha256).hexdigest()


def verifier() -> SignedRequestVerifier:
    """Build a verifier with deterministic time and an isolated replay store."""

    return SignedRequestVerifier(
        secret=SecretStr("internal-webhook-secret"),
        maximum_clock_skew_seconds=300,
        clock=lambda: 1_000.0,
        replay_store=InMemoryReplayStore(),
    )


def test_valid_request_is_authenticated_once() -> None:
    """A correct request returns a stable body digest for auditing."""

    body = b'{"job_id":"job-1"}'
    timestamp = 900

    body_digest = verifier().verify(
        timestamp=timestamp,
        provided_signature=signature("internal-webhook-secret", timestamp, body),
        body=body,
    )

    assert body_digest == sha256(body).hexdigest()


def test_bad_signature_old_timestamp_and_replay_are_rejected() -> None:
    """Authentication fails before an internal request can create AI spend."""

    body = b'{"job_id":"job-1"}'
    request_verifier = verifier()

    with pytest.raises(RequestAuthenticationError, match="signature"):
        request_verifier.verify(
            timestamp=900,
            provided_signature="0" * 64,
            body=body,
        )
    with pytest.raises(RequestAuthenticationError, match="timestamp"):
        request_verifier.verify(
            timestamp=100,
            provided_signature=signature("internal-webhook-secret", 100, body),
            body=body,
        )

    valid_signature = signature("internal-webhook-secret", 900, body)
    request_verifier.verify(
        timestamp=900,
        provided_signature=valid_signature,
        body=body,
    )
    with pytest.raises(RequestAuthenticationError, match="replay"):
        request_verifier.verify(
            timestamp=900,
            provided_signature=valid_signature,
            body=body,
        )


def test_authentication_errors_never_echo_secrets_or_request_bodies() -> None:
    """Error text is safe for operational logs."""

    body = b'{"private_input":"never log me"}'
    with pytest.raises(RequestAuthenticationError) as captured_error:
        verifier().verify(
            timestamp=900,
            provided_signature="internal-webhook-secret",
            body=body,
        )

    rendered_error = str(captured_error.value)
    assert "internal-webhook-secret" not in rendered_error
    assert "never log me" not in rendered_error
