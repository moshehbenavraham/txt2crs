"""Tests-first FastAPI lifespan ownership for the txt2crs facade."""

from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient
from txt2crs.application import Txt2CrsApplication

from app.core.config import Settings
from app.main import (
    Txt2CrsAuthenticationFactory,
    Txt2CrsLifecycleFactory,
    Txt2CrsReadinessFactory,
    Txt2CrsWorkerFactory,
    create_app,
)
from app.services.txt2crs_application import Txt2CrsApplicationLifecycle
from app.services.txt2crs_authentication import SystemAuthenticationCoordinator
from app.services.txt2crs_readiness import CachedReadinessCoordinator
from app.services.txt2crs_runtime import RuntimeOwnershipCoordinator
from app.services.txt2crs_worker import SerialTxt2CrsWorker


def _test_settings(tmp_path: Path, *, is_configured: bool = True) -> Settings:
    """Return an isolated shell configuration for one test application."""

    state_root = tmp_path / "state"
    return Settings(
        _env_file=None,
        PROJECT_NAME="txt2crs Lifespan Test",
        ENVIRONMENT="local",
        SECRET_KEY="local-dev-secret-key",
        POSTGRES_SERVER="localhost",
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD="test-password",
        POSTGRES_DB="app",
        FIRST_SUPERUSER="admin@example.com",
        FIRST_SUPERUSER_PASSWORD="test-superuser-password",
        TXT2CRS_STATE_ROOT=state_root,
        TXT2CRS_JOB_DB_PATH=state_root / "jobs.sqlite3",
        TXT2CRS_ARTIFACT_ROOT=state_root / "artifacts",
        TXT2CRS_CODEX_HOME=state_root / "codex-home",
        TXT2CRS_WORKER_ROOT=tmp_path / "worker",
        TAVILY_API_KEY="test-tavily-key" if is_configured else None,
    )


class RecordingLifecycle:
    """Small lifecycle double used to verify FastAPI ownership."""

    def __init__(
        self,
        *,
        is_configured: bool,
        start_error: Exception | None = None,
        close_error: Exception | None = None,
        events: list[str] | None = None,
    ) -> None:
        self.is_configured = is_configured
        self.start_error = start_error
        self.close_error = close_error
        self.events = events if events is not None else []
        self.application = cast(Txt2CrsApplication, object()) if is_configured else None
        self.start_calls = 0
        self.close_calls = 0

    def start(self) -> None:
        self.start_calls += 1
        self.events.append("lifecycle.start")
        if self.start_error is not None:
            raise self.start_error

    def close(self) -> None:
        self.close_calls += 1
        self.events.append("lifecycle.close")
        if self.close_error is not None:
            raise self.close_error


class RecordingWorker:
    """Small worker double used to prove exact lifespan ordering."""

    def __init__(
        self,
        *,
        start_error: Exception | None = None,
        close_error: Exception | None = None,
        events: list[str] | None = None,
    ) -> None:
        self.start_error = start_error
        self.close_error = close_error
        self.events = events if events is not None else []
        self.start_calls = 0
        self.close_calls = 0

    def start(self) -> None:
        self.start_calls += 1
        self.events.append("worker.start")
        if self.start_error is not None:
            raise self.start_error

    def close(self) -> None:
        self.close_calls += 1
        self.events.append("worker.close")
        if self.close_error is not None:
            raise self.close_error


class RecordingWorkerFactory:
    """Return configured worker doubles and retain only safe call counts."""

    def __init__(self, workers: tuple[RecordingWorker, ...]) -> None:
        self._workers = list(workers)
        self.applications: list[Txt2CrsApplication] = []
        self.settings: list[Settings] = []

    def __call__(
        self,
        application: Txt2CrsApplication,
        application_settings: Settings,
        runtime_ownership: RuntimeOwnershipCoordinator,
    ) -> SerialTxt2CrsWorker:
        del runtime_ownership
        self.applications.append(application)
        self.settings.append(application_settings)
        return cast(SerialTxt2CrsWorker, self._workers.pop(0))


class RecordingReadiness:
    """Observe cache lifecycle without running a maintenance thread."""

    def __init__(self, events: list[str]) -> None:
        self.events = events

    def start(self) -> None:
        self.events.append("readiness.start")

    def close(self) -> None:
        self.events.append("readiness.close")


class RecordingAuthentication:
    """Observe cached authentication lifecycle without provider work."""

    def __init__(self, events: list[str]) -> None:
        self.events = events

    def start(self) -> None:
        self.events.append("authentication.start")

    def close(self) -> None:
        self.events.append("authentication.close")


def _factory_for(
    lifecycle: RecordingLifecycle,
) -> Txt2CrsLifecycleFactory:
    """Adapt one recording lifecycle to the typed application factory."""

    def build_lifecycle(_settings: Settings) -> Txt2CrsApplicationLifecycle:
        return cast(Txt2CrsApplicationLifecycle, lifecycle)

    return build_lifecycle


def _worker_factory_for(
    *workers: RecordingWorker,
) -> tuple[Txt2CrsWorkerFactory, RecordingWorkerFactory]:
    """Adapt recording workers to the typed FastAPI factory seam."""

    worker_factory = RecordingWorkerFactory(workers)
    return cast(Txt2CrsWorkerFactory, worker_factory), worker_factory


@pytest.mark.parametrize("is_configured", [True, False])
def test_fastapi_lifespan_owns_one_configured_or_unconfigured_service(
    tmp_path: Path,
    is_configured: bool,
) -> None:
    lifecycle = RecordingLifecycle(is_configured=is_configured)
    recording_worker = RecordingWorker()
    worker_factory, worker_factory_recorder = _worker_factory_for(recording_worker)
    application = create_app(
        application_settings=_test_settings(
            tmp_path,
            is_configured=is_configured,
        ),
        txt2crs_lifecycle_factory=_factory_for(lifecycle),
        txt2crs_worker_factory=worker_factory,
    )

    with TestClient(application) as client:
        assert application.state.txt2crs_lifecycle is lifecycle
        assert application.state.txt2crs_worker is (
            recording_worker if is_configured else None
        )
        assert client.get("/api/v1/openapi.json").status_code == 200
        liveness_response = client.get("/api/v1/utils/health-check/")
        assert liveness_response.status_code == 200
        assert liveness_response.json() is True
        assert lifecycle.start_calls == 1
        assert lifecycle.close_calls == 0
        assert recording_worker.start_calls == (1 if is_configured else 0)

    assert lifecycle.close_calls == 1
    assert recording_worker.close_calls == (1 if is_configured else 0)
    assert len(worker_factory_recorder.applications) == (1 if is_configured else 0)


def test_sequential_lifespans_receive_fresh_services(tmp_path: Path) -> None:
    created_lifecycles: list[RecordingLifecycle] = []
    first_worker = RecordingWorker()
    second_worker = RecordingWorker()
    worker_factory, _worker_factory_recorder = _worker_factory_for(
        first_worker,
        second_worker,
    )

    def create_lifecycle(_settings: Settings) -> Txt2CrsApplicationLifecycle:
        lifecycle = RecordingLifecycle(is_configured=True)
        created_lifecycles.append(lifecycle)
        return cast(Txt2CrsApplicationLifecycle, lifecycle)

    application = create_app(
        application_settings=_test_settings(tmp_path),
        txt2crs_lifecycle_factory=cast(
            Callable[[Settings], Txt2CrsApplicationLifecycle],
            create_lifecycle,
        ),
        txt2crs_worker_factory=worker_factory,
    )

    with TestClient(application):
        first_lifecycle = application.state.txt2crs_lifecycle
        first_lifespan_worker = application.state.txt2crs_worker
    with TestClient(application):
        second_lifecycle = application.state.txt2crs_lifecycle
        second_lifespan_worker = application.state.txt2crs_worker

    assert first_lifecycle is not second_lifecycle
    assert first_lifespan_worker is first_worker
    assert second_lifespan_worker is second_worker
    assert len(created_lifecycles) == 2
    assert all(lifecycle.start_calls == 1 for lifecycle in created_lifecycles)
    assert all(lifecycle.close_calls == 1 for lifecycle in created_lifecycles)
    assert first_worker.close_calls == 1
    assert second_worker.close_calls == 1


def test_startup_failure_still_closes_the_partial_lifecycle(
    tmp_path: Path,
) -> None:
    lifecycle = RecordingLifecycle(
        is_configured=True,
        start_error=RuntimeError("private startup detail"),
    )
    application = create_app(
        application_settings=_test_settings(tmp_path),
        txt2crs_lifecycle_factory=_factory_for(lifecycle),
        txt2crs_worker_factory=_worker_factory_for(RecordingWorker())[0],
    )

    with pytest.raises(RuntimeError, match="private startup detail"):
        with TestClient(application):
            pytest.fail("The application must not serve after startup failure.")

    assert lifecycle.start_calls == 1
    assert lifecycle.close_calls == 1


def test_configured_lifespan_starts_and_closes_worker_before_facade(
    tmp_path: Path,
) -> None:
    """Worker ownership begins after composition and ends before facade cleanup."""

    events: list[str] = []
    lifecycle = RecordingLifecycle(is_configured=True, events=events)
    worker = RecordingWorker(events=events)
    application = create_app(
        application_settings=_test_settings(tmp_path),
        txt2crs_lifecycle_factory=_factory_for(lifecycle),
        txt2crs_worker_factory=_worker_factory_for(worker)[0],
    )

    with TestClient(application):
        assert events == ["lifecycle.start", "worker.start"]

    assert events == [
        "lifecycle.start",
        "worker.start",
        "worker.close",
        "lifecycle.close",
    ]


def test_readiness_refresh_precedes_worker_and_closes_after_worker(
    tmp_path: Path,
) -> None:
    """Startup probes cannot race recovery and shutdown follows dependencies."""

    events: list[str] = []
    lifecycle = RecordingLifecycle(is_configured=True, events=events)
    worker = RecordingWorker(events=events)
    readiness = RecordingReadiness(events)

    def create_readiness(
        _application: Txt2CrsApplication | None,
        _worker: SerialTxt2CrsWorker | None,
        _runtime_ownership: RuntimeOwnershipCoordinator,
        _settings: Settings,
    ) -> CachedReadinessCoordinator:
        return cast(CachedReadinessCoordinator, readiness)

    application = create_app(
        application_settings=_test_settings(tmp_path),
        txt2crs_lifecycle_factory=_factory_for(lifecycle),
        txt2crs_worker_factory=_worker_factory_for(worker)[0],
        txt2crs_readiness_factory=cast(
            Txt2CrsReadinessFactory,
            create_readiness,
        ),
    )

    with TestClient(application):
        assert events == [
            "lifecycle.start",
            "readiness.start",
            "worker.start",
        ]

    assert events == [
        "lifecycle.start",
        "readiness.start",
        "worker.start",
        "worker.close",
        "readiness.close",
        "lifecycle.close",
    ]


def test_authentication_starts_before_readiness_and_closes_after_it(
    tmp_path: Path,
) -> None:
    """Startup refreshes both caches before work and reverses exact ownership."""

    events: list[str] = []
    lifecycle = RecordingLifecycle(is_configured=True, events=events)
    worker = RecordingWorker(events=events)
    readiness = RecordingReadiness(events)
    authentication = RecordingAuthentication(events)

    def create_readiness(
        _application: Txt2CrsApplication | None,
        _worker: SerialTxt2CrsWorker | None,
        _runtime_ownership: RuntimeOwnershipCoordinator,
        _settings: Settings,
    ) -> CachedReadinessCoordinator:
        return cast(CachedReadinessCoordinator, readiness)

    def create_authentication(
        _application: Txt2CrsApplication | None,
        _runtime_ownership: RuntimeOwnershipCoordinator,
        _settings: Settings,
    ) -> SystemAuthenticationCoordinator:
        return cast(SystemAuthenticationCoordinator, authentication)

    application = create_app(
        application_settings=_test_settings(tmp_path),
        txt2crs_lifecycle_factory=_factory_for(lifecycle),
        txt2crs_worker_factory=_worker_factory_for(worker)[0],
        txt2crs_readiness_factory=cast(Txt2CrsReadinessFactory, create_readiness),
        txt2crs_authentication_factory=cast(
            Txt2CrsAuthenticationFactory,
            create_authentication,
        ),
    )

    with TestClient(application):
        assert application.state.txt2crs_authentication is authentication
        assert events == [
            "lifecycle.start",
            "authentication.start",
            "readiness.start",
            "worker.start",
        ]

    assert events == [
        "lifecycle.start",
        "authentication.start",
        "readiness.start",
        "worker.start",
        "worker.close",
        "readiness.close",
        "authentication.close",
        "lifecycle.close",
    ]


def test_worker_start_failure_closes_worker_and_facade_once(
    tmp_path: Path,
) -> None:
    """A partially started supervisor cannot leak the configured facade."""

    events: list[str] = []
    lifecycle = RecordingLifecycle(is_configured=True, events=events)
    worker = RecordingWorker(
        start_error=RuntimeError("private worker startup"),
        events=events,
    )
    application = create_app(
        application_settings=_test_settings(tmp_path),
        txt2crs_lifecycle_factory=_factory_for(lifecycle),
        txt2crs_worker_factory=_worker_factory_for(worker)[0],
    )

    with pytest.raises(RuntimeError, match="private worker startup"):
        with TestClient(application):
            pytest.fail("The application must not serve after worker failure.")

    assert events == [
        "lifecycle.start",
        "worker.start",
        "worker.close",
        "lifecycle.close",
    ]
    assert worker.close_calls == 1
    assert lifecycle.close_calls == 1


def test_shutdown_attempts_facade_close_after_worker_close_failure(
    tmp_path: Path,
) -> None:
    """The first cleanup failure is authoritative but cannot skip the facade."""

    events: list[str] = []
    lifecycle = RecordingLifecycle(is_configured=True, events=events)
    worker = RecordingWorker(
        close_error=RuntimeError("private worker cleanup"),
        events=events,
    )
    application = create_app(
        application_settings=_test_settings(tmp_path),
        txt2crs_lifecycle_factory=_factory_for(lifecycle),
        txt2crs_worker_factory=_worker_factory_for(worker)[0],
    )

    with pytest.raises(RuntimeError, match="private worker cleanup"):
        with TestClient(application):
            pass

    assert events[-2:] == ["worker.close", "lifecycle.close"]
    assert lifecycle.close_calls == 1
