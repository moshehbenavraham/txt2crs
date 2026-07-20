# SPDX-License-Identifier: MIT-0

"""App-owned authentication for one dedicated ChatGPT subscription identity.

This module deliberately does *not* shell out to ``codex login``. The official
Python SDK starts the Codex app-server binary bundled in this distribution and
asks that server to begin ChatGPT's device-code flow. A temporary command can
print the resulting challenge today; the future FastAPI/frontend shell can
render the exact same browser-safe model.

Credential bytes never cross this boundary. Codex writes and refreshes them in
the caller-provided ``CODEX_HOME`` while txt2crs sees only account type and
high-level authentication state.
"""

import os
import re
from collections.abc import Callable, Mapping
from enum import StrEnum
from pathlib import Path
from threading import RLock, Thread
from typing import Annotated, Protocol, cast
from urllib.parse import urlsplit

from openai_codex import Codex, CodexConfig
from pydantic import Field

from txt2crs.ai.codex_runtime import (
    CodexSubscriptionRuntime,
    OfficialCodexSdkAdapter,
)
from txt2crs.domain.models import StrictContract

_OPENAI_DEVICE_AUTHENTICATION_HOST = "auth.openai.com"
_DEVICE_USER_CODE_PATTERN = re.compile(r"^[A-Za-z0-9-]{4,64}$")


class SystemAuthenticationState(StrEnum):
    """Safe states that an application setup screen may display."""

    signed_out = "signed_out"
    waiting_for_user = "waiting_for_user"
    authenticated = "authenticated"
    failed = "failed"


class SystemAuthenticationSnapshot(StrictContract):
    """Browser-safe state for the dedicated system authentication ceremony."""

    state: SystemAuthenticationState
    verification_url: Annotated[str, Field(max_length=2_048)] | None = None
    user_code: Annotated[str, Field(max_length=64)] | None = None
    message: Annotated[str, Field(min_length=1, max_length=500)]


class SystemAuthenticationError(RuntimeError):
    """A safe local failure that never includes provider response details."""


class _DeviceCodeLoginHandle(Protocol):
    """Public SDK handle methods used while a user completes device login."""

    login_id: str
    verification_url: str
    user_code: str

    def wait(self) -> object:
        """Wait for Codex's account/login/completed notification."""

    def cancel(self) -> object:
        """Cancel the active Codex login attempt."""


class _AuthenticationClient(Protocol):
    """Narrow public Codex API needed by system authentication."""

    def login_chatgpt_device_code(self) -> _DeviceCodeLoginHandle:
        """Start ChatGPT device-code authentication."""

    def account(self, *, refresh_token: bool = False) -> object:
        """Read the current normalized account union."""

    def logout(self) -> None:
        """Clear Codex-managed credentials."""

    def close(self) -> None:
        """Stop the bundled Codex app-server process."""


AuthenticationClientFactory = Callable[[], _AuthenticationClient]
AuthenticationClientBuilder = Callable[[CodexConfig], _AuthenticationClient]


def _build_official_codex_client(config: CodexConfig) -> _AuthenticationClient:
    """Construct the public SDK client through its bundled runtime dependency."""

    return Codex(config)


class DedicatedSystemAuthenticator:
    """Own one in-app device-code ceremony for a dedicated system identity.

    The class is framework-independent. A FastAPI route can call
    :meth:`start_device_code_login`, return the snapshot as JSON, and poll
    :meth:`current_status`. The temporary console entry point uses the same
    methods until that application shell exists.
    """

    def __init__(self, *, client_factory: AuthenticationClientFactory) -> None:
        self._client_factory = client_factory
        self._lock = RLock()
        self._state = SystemAuthenticationState.signed_out
        self._verification_url: str | None = None
        self._user_code: str | None = None
        self._message = "Dedicated ChatGPT subscription is not connected."
        self._active_client: _AuthenticationClient | None = None
        self._active_login_handle: _DeviceCodeLoginHandle | None = None
        self._completion_thread: Thread | None = None
        # A generation number prevents a cancelled background thread from
        # overwriting the state of a newer authentication attempt.
        self._attempt_generation = 0

    @classmethod
    def create(
        cls,
        *,
        worker_directory: Path,
        codex_home: Path,
        parent_environment: Mapping[str, str] | None = None,
        client_builder: AuthenticationClientBuilder | None = None,
    ) -> "DedicatedSystemAuthenticator":
        """Create an authenticator backed only by packaged SDK dependencies.

        ``CODEX_HOME`` is explicit and file-backed so a dedicated application
        identity cannot silently reuse a developer's OS keyring or personal
        Codex configuration. API-key variables are overwritten with empty
        values because the SDK merges its configured environment over the
        parent process environment when it launches app-server.
        """

        if worker_directory.is_symlink() or codex_home.is_symlink():
            raise ValueError("Worker and CODEX_HOME directories cannot be symlinks.")

        worker_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        worker_directory.chmod(0o700)
        codex_home.mkdir(mode=0o700, parents=True, exist_ok=True)
        codex_home.chmod(0o700)
        resolved_worker_directory = worker_directory.resolve(strict=True)
        resolved_codex_home = codex_home.resolve(strict=True)

        supplied_environment = dict(
            os.environ if parent_environment is None else parent_environment
        )
        sdk_environment = CodexSubscriptionRuntime.build_child_environment(
            supplied_environment,
            codex_home=resolved_codex_home,
        )

        # CodexConfig.env is merged over os.environ rather than replacing it.
        # Blank every observed spelling plus the canonical names so no ambient
        # Platform or research key can select a different billing/auth path.
        environment_key_candidates = {
            *os.environ,
            *supplied_environment,
            *CodexSubscriptionRuntime._REMOVED_CHILD_ENVIRONMENT_KEYS,
        }
        for environment_key in environment_key_candidates:
            if (
                environment_key.upper()
                in CodexSubscriptionRuntime._REMOVED_CHILD_ENVIRONMENT_KEYS
            ):
                sdk_environment[environment_key] = ""

        authentication_overrides = (
            *OfficialCodexSdkAdapter.build_config_overrides(research_mcp=None),
            # This app accepts only the ChatGPT subscription path.
            'forced_login_method="chatgpt"',
            # A dedicated on-disk store under CODEX_HOME is portable into the
            # future standalone deployment and never shares an OS keyring.
            'cli_auth_credentials_store="file"',
        )
        sdk_config = CodexConfig(
            cwd=str(resolved_worker_directory),
            env=sdk_environment,
            config_overrides=authentication_overrides,
            client_name="txt2crs-system-auth",
            client_title="txt2crs Dedicated System Authentication",
        )
        resolved_client_builder = client_builder or _build_official_codex_client
        return cls(
            client_factory=lambda: resolved_client_builder(sdk_config),
        )

    def start_device_code_login(self) -> SystemAuthenticationSnapshot:
        """Start OAuth inside app-server and return only the frontend challenge."""

        with self._lock:
            if self._state is SystemAuthenticationState.waiting_for_user:
                return self._snapshot_locked()
            if self._state is SystemAuthenticationState.authenticated:
                return self._snapshot_locked()

            authentication_client: _AuthenticationClient | None = None
            try:
                authentication_client = self._client_factory()
                login_handle = authentication_client.login_chatgpt_device_code()
                verification_url = self._validate_verification_url(
                    login_handle.verification_url
                )
                user_code = self._validate_user_code(login_handle.user_code)
            except Exception as authentication_start_error:
                if authentication_client is not None:
                    authentication_client.close()
                self._set_failed_locked()
                raise SystemAuthenticationError(
                    "ChatGPT authentication could not be started."
                ) from authentication_start_error

            # The client cannot be ``None`` here because every path that fails
            # before assignment exits through the safe exception above.
            assert authentication_client is not None

            self._attempt_generation += 1
            attempt_generation = self._attempt_generation
            self._state = SystemAuthenticationState.waiting_for_user
            self._verification_url = verification_url
            self._user_code = user_code
            self._message = (
                "Open the verification page and sign in with the dedicated "
                "ChatGPT subscription account."
            )
            self._active_client = authentication_client
            self._active_login_handle = login_handle
            waiting_snapshot = self._snapshot_locked()

            completion_thread = Thread(
                target=self._complete_device_code_login,
                args=(attempt_generation, authentication_client, login_handle),
                name="txt2crs-system-authentication",
                daemon=True,
            )
            self._completion_thread = completion_thread
            completion_thread.start()
            return waiting_snapshot

    def current_status(self, *, refresh: bool = False) -> SystemAuthenticationSnapshot:
        """Return current state, optionally re-reading persisted Codex auth."""

        with self._lock:
            if self._state is SystemAuthenticationState.waiting_for_user or not refresh:
                return self._snapshot_locked()

        authentication_client: _AuthenticationClient | None = None
        try:
            authentication_client = self._client_factory()
            account_type = self._read_account_type(authentication_client)
        except Exception:
            account_type = None
        finally:
            if authentication_client is not None:
                authentication_client.close()

        with self._lock:
            # The completion thread may change ``self._state`` between the
            # two lock acquisitions, so the narrowing from the first lock
            # block no longer holds; cast back to the full enum so this
            # re-check compares against the live value.
            state_after_refresh = cast(SystemAuthenticationState, self._state)
            if state_after_refresh is not SystemAuthenticationState.waiting_for_user:
                if account_type == "chatgpt":
                    self._set_authenticated_locked()
                else:
                    self._set_signed_out_locked()
            return self._snapshot_locked()

    def wait_for_current_attempt(
        self,
        *,
        timeout_seconds: float | None = None,
    ) -> SystemAuthenticationSnapshot:
        """Wait for the active ceremony; useful for bootstrap commands/tests."""

        if timeout_seconds is not None and timeout_seconds < 0:
            raise ValueError("timeout_seconds cannot be negative.")
        with self._lock:
            completion_thread = self._completion_thread
        if completion_thread is not None:
            completion_thread.join(timeout=timeout_seconds)
        with self._lock:
            return self._snapshot_locked()

    def logout(self) -> SystemAuthenticationSnapshot:
        """Cancel any ceremony and ask Codex to clear the dedicated account."""

        self.close()
        authentication_client: _AuthenticationClient | None = None
        try:
            authentication_client = self._client_factory()
            authentication_client.logout()
        except Exception as logout_error:
            raise SystemAuthenticationError(
                "The dedicated ChatGPT account could not be signed out."
            ) from logout_error
        finally:
            if authentication_client is not None:
                authentication_client.close()
        with self._lock:
            self._set_signed_out_locked()
            return self._snapshot_locked()

    def close(self) -> None:
        """Cancel pending login and close its bundled app-server process."""

        with self._lock:
            self._attempt_generation += 1
            login_handle = self._active_login_handle
            authentication_client = self._active_client
            self._active_login_handle = None
            self._active_client = None
            self._completion_thread = None
            self._set_signed_out_locked()

        if login_handle is not None:
            try:
                login_handle.cancel()
            except Exception:
                # Cleanup is best-effort; there is no safe provider detail to
                # surface and client.close() still terminates app-server.
                pass
        if authentication_client is not None:
            authentication_client.close()

    def _complete_device_code_login(
        self,
        attempt_generation: int,
        authentication_client: _AuthenticationClient,
        login_handle: _DeviceCodeLoginHandle,
    ) -> None:
        """Wait in the background and project only a safe final state."""

        authentication_succeeded = False
        account_type: str | None = None
        try:
            completion_notification = login_handle.wait()
            authentication_succeeded = (
                getattr(completion_notification, "success", False) is True
            )
            if authentication_succeeded:
                try:
                    account_type = self._read_account_type(authentication_client)
                except Exception:
                    # The login-completed notification can arrive just before
                    # this app-server session exposes the newly persisted
                    # account. Preserve the successful ceremony so a fresh
                    # client can verify the isolated CODEX_HOME below.
                    account_type = None
        except Exception:
            authentication_succeeded = False
        finally:
            authentication_client.close()

        if authentication_succeeded and account_type is None:
            account_type = self._read_persisted_account_type(attempt_generation)

        with self._lock:
            if attempt_generation != self._attempt_generation:
                return
            self._active_login_handle = None
            self._active_client = None
            self._completion_thread = None
            if authentication_succeeded and account_type == "chatgpt":
                self._set_authenticated_locked()
            elif authentication_succeeded and account_type == "apiKey":
                self._state = SystemAuthenticationState.failed
                self._verification_url = None
                self._user_code = None
                self._message = (
                    "A ChatGPT subscription account is required; API-key "
                    "authentication was rejected."
                )
            elif authentication_succeeded:
                self._state = SystemAuthenticationState.failed
                self._verification_url = None
                self._user_code = None
                self._message = (
                    "ChatGPT authentication completed, but the saved account "
                    "could not yet be verified. Run this command again to "
                    "verify the connected account."
                )
            else:
                self._set_failed_locked()

    def _read_persisted_account_type(
        self,
        attempt_generation: int,
    ) -> str | None:
        """Reopen Codex once when the login session has stale account state."""

        with self._lock:
            if attempt_generation != self._attempt_generation:
                return None

        verification_client: _AuthenticationClient | None = None
        try:
            # Hermes treats a completed token exchange as persisted ChatGPT
            # auth, while AIOS detects that saved OAuth state on re-entry. A
            # fresh SDK client gives txt2crs the same re-entry behavior without
            # reading token bytes across this package boundary.
            verification_client = self._client_factory()
            return self._read_account_type(verification_client)
        except Exception:
            return None
        finally:
            if verification_client is not None:
                verification_client.close()

    @staticmethod
    def _read_account_type(authentication_client: _AuthenticationClient) -> str | None:
        """Read the public account union while delegating refresh to Codex."""

        account_response = authentication_client.account(refresh_token=True)
        account = getattr(account_response, "account", None)
        account_root = getattr(account, "root", None)
        raw_account_type = getattr(account_root, "type", None)
        return raw_account_type if isinstance(raw_account_type, str) else None

    @staticmethod
    def _validate_verification_url(raw_url: str) -> str:
        """Reject a compromised or malformed device-code destination."""

        parsed_url = urlsplit(raw_url)
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname != _OPENAI_DEVICE_AUTHENTICATION_HOST
            or parsed_url.username is not None
            or parsed_url.password is not None
            or parsed_url.fragment
        ):
            raise ValueError("Codex returned an invalid authentication URL.")
        return raw_url

    @staticmethod
    def _validate_user_code(raw_user_code: str) -> str:
        """Accept only the short display code shape documented by app-server."""

        if _DEVICE_USER_CODE_PATTERN.fullmatch(raw_user_code) is None:
            raise ValueError("Codex returned an invalid device user code.")
        return raw_user_code

    def _snapshot_locked(self) -> SystemAuthenticationSnapshot:
        """Build one immutable projection while the caller holds the lock."""

        return SystemAuthenticationSnapshot(
            state=self._state,
            verification_url=self._verification_url,
            user_code=self._user_code,
            message=self._message,
        )

    def _set_authenticated_locked(self) -> None:
        """Project a connected ChatGPT identity without personal account data."""

        self._state = SystemAuthenticationState.authenticated
        self._verification_url = None
        self._user_code = None
        self._message = "Dedicated ChatGPT subscription is connected."

    def _set_signed_out_locked(self) -> None:
        """Reset public state without touching credential bytes directly."""

        self._state = SystemAuthenticationState.signed_out
        self._verification_url = None
        self._user_code = None
        self._message = "Dedicated ChatGPT subscription is not connected."

    def _set_failed_locked(self) -> None:
        """Use one generic failure message instead of provider error details."""

        self._state = SystemAuthenticationState.failed
        self._verification_url = None
        self._user_code = None
        self._message = "ChatGPT authentication failed. Start a new sign-in attempt."


__all__ = [
    "DedicatedSystemAuthenticator",
    "SystemAuthenticationError",
    "SystemAuthenticationSnapshot",
    "SystemAuthenticationState",
]
