"""Isolated FastAPI composition for credential-free browser journeys.

This module lives below ``tests`` on purpose. It reuses production routes,
middleware, authentication, readiness coordination, and the serial worker,
while replacing only the package lifecycle with the public deterministic
factory. No browser-only control route is added to the API graph.
"""

import os
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Literal, cast

from fastapi import FastAPI
from txt2crs.application import (
    DeterministicGenerationScenario,
    Txt2CrsApplication,
)

from app.core.config import Settings, settings
from app.main import create_app
from app.services.txt2crs_application import Txt2CrsApplicationLifecycle
from app.services.txt2crs_readiness import (
    CachedReadinessCoordinator,
    ReadinessChecks,
    ReadinessCheckState,
    ReadinessSnapshot,
    ReadinessStatus,
)
from app.services.txt2crs_runtime import RuntimeOwnershipCoordinator
from app.services.txt2crs_worker import SerialTxt2CrsWorker
from tests.support.deterministic_course import (
    DurableSubmissionHarness,
    build_complete_course_scenario,
    build_deterministic_execution_profile,
    build_unconsumed_submission_scenario,
)

BROWSER_TEST_ENABLE_ENVIRONMENT_VARIABLE = "TXT2CRS_ENABLE_BROWSER_TEST_APP"
BROWSER_TEST_STATE_ENVIRONMENT_VARIABLE = "TXT2CRS_BROWSER_TEST_STATE_DIRECTORY"
BROWSER_TEST_SCENARIO_ENVIRONMENT_VARIABLE = "TXT2CRS_BROWSER_TEST_SCENARIO"
BROWSER_TEST_FRONTEND_ENVIRONMENT_VARIABLE = "TXT2CRS_BROWSER_TEST_FRONTEND_HOST"
BrowserScenarioName = Literal["complete", "failed"]


class DeterministicBrowserLifecycle(Txt2CrsApplicationLifecycle):
    """Own one deterministic facade behind the production lifecycle seam."""

    def __init__(
        self,
        *,
        state_directory: Path,
        scenario: DeterministicGenerationScenario,
    ) -> None:
        # The deterministic lifecycle does not initialize the real provider
        # parent: doing so would retain production settings and secret-bearing
        # factory state in a browser-test process.
        self._state_directory = state_directory
        self._scenario = scenario
        self._lock = RLock()
        self._application: Txt2CrsApplication | None = None
        self._is_started = False

    @property
    def application(self) -> Txt2CrsApplication | None:
        """Return the current public facade, if startup completed."""

        with self._lock:
            return self._application

    @property
    def is_started(self) -> bool:
        """Return whether this isolated lifecycle completed startup."""

        with self._lock:
            return self._is_started

    @property
    def is_configured(self) -> bool:
        """The deterministic facade is configured exactly when it is open."""

        with self._lock:
            return self._application is not None

    def start(self) -> None:
        """Open the public deterministic application once."""

        with self._lock:
            if self._is_started:
                return

            harness = DurableSubmissionHarness(
                state_directory=self._state_directory,
                execution_profile=build_deterministic_execution_profile(),
                scenario=self._scenario,
            )
            application = harness.open(scenario=self._scenario)
            self._application = application
            self._is_started = True

    def close(self) -> None:
        """Clear ownership first, then close every package-owned resource."""

        with self._lock:
            application = self._application
            self._application = None
            self._is_started = False
        if application is not None:
            application.close()


class DeterministicBrowserReadiness(CachedReadinessCoordinator):
    """Expose truthful local capacity for the credential-free test graph.

    The package's normal aggregate correctly reports its reduced deterministic
    adapter set rather than pretending every production upload adapter exists.
    Browser journeys only submit prompt/text requests, so this test-only cache
    evaluates that narrower reviewed capability plus the real worker and
    runtime-ownership state.
    """

    def __init__(
        self,
        *,
        worker: SerialTxt2CrsWorker,
        runtime_ownership: RuntimeOwnershipCoordinator,
    ) -> None:
        self._browser_worker = worker
        self._browser_runtime_ownership = runtime_ownership
        self._lock = RLock()
        self._is_started = False
        self._is_closed = False

    def start(self) -> None:
        """Mark the side-effect-free local readiness owner as started."""

        with self._lock:
            if self._is_closed:
                raise RuntimeError("Deterministic browser readiness is closed.")
            self._is_started = True

    def snapshot(self) -> ReadinessSnapshot:
        """Combine the real worker and ownership state without provider probes."""

        with self._lock:
            is_active = self._is_started and not self._is_closed
        worker_snapshot = self._browser_worker.snapshot()
        ownership_snapshot = self._browser_runtime_ownership.snapshot()
        accepting_jobs = (
            is_active
            and worker_snapshot.is_alive
            and worker_snapshot.has_capacity
            and not worker_snapshot.is_shutting_down
            and ownership_snapshot.is_available
        )
        check_state = (
            ReadinessCheckState.ready
            if accepting_jobs
            else ReadinessCheckState.unavailable
        )
        return ReadinessSnapshot(
            status=(
                ReadinessStatus.ready if accepting_jobs else ReadinessStatus.unavailable
            ),
            accepting_jobs=accepting_jobs,
            configured_model_id="gpt-5.6",
            enabled_input_modes=("prompt", "text"),
            checks=ReadinessChecks(
                authentication=ReadinessCheckState.ready,
                model=ReadinessCheckState.ready,
                research=ReadinessCheckState.ready,
                storage=ReadinessCheckState.ready,
                worker=check_state,
                inputs=ReadinessCheckState.ready,
                admission=ReadinessCheckState.ready,
                runtime_ownership=check_state,
            ),
            warnings=(),
            recovery_actions=(),
            checked_at=datetime.now(UTC),
            is_fresh=is_active,
        )

    def close(self) -> None:
        """Clear local readiness ownership without leaving a thread behind."""

        with self._lock:
            self._is_closed = True
            self._is_started = False


def _require_enabled_browser_test_process() -> None:
    """Fail closed unless this process explicitly enables test composition."""

    if os.environ.get(BROWSER_TEST_ENABLE_ENVIRONMENT_VARIABLE) != "1":
        raise RuntimeError(
            "The deterministic browser test application is disabled. "
            f"Set {BROWSER_TEST_ENABLE_ENVIRONMENT_VARIABLE}=1 only in an "
            "isolated test process."
        )


def _select_scenario(
    scenario_name: BrowserScenarioName,
) -> DeterministicGenerationScenario:
    """Return one finite reviewed scenario; arbitrary fixture input is denied."""

    if scenario_name == "complete":
        return build_complete_course_scenario()
    if scenario_name == "failed":
        # The deliberately incomplete first turn is consumed by the real
        # executor and eventually reaches the normal retry-safe failed state.
        return build_unconsumed_submission_scenario()
    raise ValueError("Unknown deterministic browser scenario.")


def _build_browser_settings(state_directory: Path) -> Settings:
    """Return fast finite shell settings without reading provider credentials."""

    # ``model_copy`` is appropriate here because every replacement value is a
    # narrower valid member of the already validated production field type.
    # Engine storage is still owned by the deterministic lifecycle, but using
    # isolated paths here prevents accidental future shell consumers from
    # touching the normal application volume.
    return settings.model_copy(
        update={
            "FRONTEND_HOST": os.environ.get(
                BROWSER_TEST_FRONTEND_ENVIRONMENT_VARIABLE,
                settings.FRONTEND_HOST,
            ),
            "TXT2CRS_STATE_ROOT": state_directory,
            "TXT2CRS_JOB_DB_PATH": state_directory / "jobs.sqlite3",
            "TXT2CRS_ARTIFACT_ROOT": state_directory / "artifacts",
            "TXT2CRS_CODEX_HOME": state_directory / "codex-home",
            "TXT2CRS_WORKER_ROOT": state_directory.parent / "browser-worker",
            "TXT2CRS_WORKER_POLL_SECONDS": 0.02,
            "TXT2CRS_WORKER_SHUTDOWN_TIMEOUT_SECONDS": 5.0,
            "TXT2CRS_READINESS_REFRESH_SECONDS": 1.0,
            "TXT2CRS_READINESS_STALE_AFTER_SECONDS": 2.0,
            "TXT2CRS_READINESS_SHUTDOWN_TIMEOUT_SECONDS": 5.0,
            "TXT2CRS_AUTH_MONITOR_POLL_SECONDS": 0.02,
            "TXT2CRS_AUTH_SHUTDOWN_TIMEOUT_SECONDS": 5.0,
        }
    )


def create_deterministic_browser_app(
    *,
    state_directory: Path,
    scenario_name: BrowserScenarioName,
) -> FastAPI:
    """Create one isolated app using production HTTP and worker composition."""

    _require_enabled_browser_test_process()
    if state_directory.exists() or state_directory.is_symlink():
        # Never chmod, reuse, or delete a caller-owned directory. The
        # Playwright configuration gives each run a new parent directory and
        # passes a not-yet-created ``state`` child through this trust boundary.
        raise ValueError("Browser tests require a fresh state directory.")

    # Reject an existing symbolic-link parent before resolving the final path.
    # This keeps an environment-controlled test path from escaping the
    # temporary root even though this module is deliberately test-only.
    parent_to_check = state_directory.parent
    while parent_to_check != parent_to_check.parent:
        if parent_to_check.is_symlink():
            raise ValueError("Browser test state cannot use a symbolic-link parent.")
        parent_to_check = parent_to_check.parent

    resolved_state_directory = state_directory.resolve(strict=False)
    resolved_state_directory.mkdir(mode=0o700, parents=False, exist_ok=False)
    resolved_state_directory.chmod(0o700)

    scenario = _select_scenario(scenario_name)
    browser_settings = _build_browser_settings(resolved_state_directory)

    def build_deterministic_lifecycle(
        _application_settings: Settings,
    ) -> Txt2CrsApplicationLifecycle:
        """Build a fresh owner for each ASGI lifespan entry."""

        return DeterministicBrowserLifecycle(
            state_directory=resolved_state_directory,
            scenario=scenario,
        )

    def build_deterministic_readiness(
        _application: Txt2CrsApplication | None,
        worker: SerialTxt2CrsWorker | None,
        runtime_ownership: RuntimeOwnershipCoordinator,
        _application_settings: Settings,
    ) -> CachedReadinessCoordinator:
        """Build local readiness over the same worker used for execution."""

        if worker is None:
            raise RuntimeError("The deterministic browser worker is required.")
        return DeterministicBrowserReadiness(
            worker=worker,
            runtime_ownership=runtime_ownership,
        )

    return create_app(
        application_settings=browser_settings,
        txt2crs_lifecycle_factory=build_deterministic_lifecycle,
        txt2crs_readiness_factory=build_deterministic_readiness,
        txt2crs_execution_profile_factory=(
            lambda _application_settings: build_deterministic_execution_profile()
        ),
    )


def create_deterministic_browser_app_from_environment() -> FastAPI:
    """Uvicorn factory that accepts only an explicit state path and scenario."""

    raw_state_directory = os.environ.get(BROWSER_TEST_STATE_ENVIRONMENT_VARIABLE)
    if raw_state_directory is None or not raw_state_directory.strip():
        raise RuntimeError("The browser test state directory is required.")
    raw_scenario = os.environ.get(
        BROWSER_TEST_SCENARIO_ENVIRONMENT_VARIABLE,
        "complete",
    )
    if raw_scenario not in {"complete", "failed"}:
        raise RuntimeError("The browser test scenario must be complete or failed.")
    scenario_name = cast(BrowserScenarioName, raw_scenario)
    return create_deterministic_browser_app(
        state_directory=Path(raw_state_directory),
        scenario_name=scenario_name,
    )
