# SPDX-License-Identifier: MIT-0

"""HMAC authentication with timestamp validation and replay protection."""

import hmac
from collections.abc import Callable
from hashlib import sha256
from threading import Lock
from typing import Protocol

from pydantic import SecretStr


class RequestAuthenticationError(PermissionError):
    """Safe request-authentication failure without secret/body details."""


class ReplayStore(Protocol):
    """Atomically claim a request signature until its expiry."""

    def record_once(
        self,
        replay_key: str,
        *,
        expires_at: float,
        current_time: float,
    ) -> bool:
        """Return false when the key has already been observed."""


class InMemoryReplayStore:
    """Thread-safe replay store for one-process deployments and tests."""

    def __init__(self) -> None:
        self._expirations: dict[str, float] = {}
        self._lock = Lock()

    def record_once(
        self,
        replay_key: str,
        *,
        expires_at: float,
        current_time: float,
    ) -> bool:
        """Prune expired entries and atomically insert a new key."""

        with self._lock:
            self._expirations = {
                key: expiration
                for key, expiration in self._expirations.items()
                if expiration >= current_time
            }
            if replay_key in self._expirations:
                return False
            self._expirations[replay_key] = expires_at
            return True


class SignedRequestVerifier:
    """Verify internal webhook bodies before authorization or job lookup."""

    def __init__(
        self,
        *,
        secret: SecretStr,
        maximum_clock_skew_seconds: int,
        clock: Callable[[], float],
        replay_store: ReplayStore,
    ) -> None:
        if maximum_clock_skew_seconds < 1:
            raise ValueError("maximum_clock_skew_seconds must be positive")
        self._secret = secret
        self._maximum_clock_skew_seconds = maximum_clock_skew_seconds
        self._clock = clock
        self._replay_store = replay_store

    def verify(
        self,
        *,
        timestamp: int,
        provided_signature: str,
        body: bytes,
    ) -> str:
        """Authenticate a fresh body and return its non-secret SHA-256 digest."""

        current_time = self._clock()
        if abs(current_time - timestamp) > self._maximum_clock_skew_seconds:
            raise RequestAuthenticationError("The request timestamp is invalid.")
        if len(provided_signature) != 64:
            raise RequestAuthenticationError("The request signature is invalid.")

        signed_payload = str(timestamp).encode("ascii") + b"." + body
        expected_signature = hmac.new(
            self._secret.get_secret_value().encode("utf-8"),
            signed_payload,
            sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected_signature, provided_signature):
            raise RequestAuthenticationError("The request signature is invalid.")

        replay_key = sha256(
            f"{timestamp}:{provided_signature}".encode("ascii")
        ).hexdigest()
        if not self._replay_store.record_once(
            replay_key,
            expires_at=current_time + self._maximum_clock_skew_seconds,
            current_time=current_time,
        ):
            raise RequestAuthenticationError("The request is a replay.")
        return sha256(body).hexdigest()
