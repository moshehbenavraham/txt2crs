"""Tests-first FastAPI lifespan ownership for the txt2crs facade."""

from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest
from app.services.txt2crs_application import Txt2CrsApplicationLifecycle
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import Txt2CrsLifecycleFactory, create_app


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
    ) -> None:
        self.is_configured = is_configured
        self.start_error = start_error
        self.start_calls = 0
        self.close_calls = 0

    def start(self) -> None:
        self.start_calls += 1
        if self.start_error is not None:
            raise self.start_error

    def close(self) -> None:
        self.close_calls += 1


def _factory_for(
    lifecycle: RecordingLifecycle,
) -> Txt2CrsLifecycleFactory:
    """Adapt one recording lifecycle to the typed application factory."""

    def build_lifecycle(_settings: Settings) -> Txt2CrsApplicationLifecycle:
        return cast(Txt2CrsApplicationLifecycle, lifecycle)

    return build_lifecycle


@pytest.mark.parametrize("is_configured", [True, False])
def test_fastapi_lifespan_owns_one_configured_or_unconfigured_service(
    tmp_path: Path,
    is_configured: bool,
) -> None:
    lifecycle = RecordingLifecycle(is_configured=is_configured)
    application = create_app(
        application_settings=_test_settings(
            tmp_path,
            is_configured=is_configured,
        ),
        txt2crs_lifecycle_factory=_factory_for(lifecycle),
    )

    with TestClient(application) as client:
        assert application.state.txt2crs_lifecycle is lifecycle
        assert client.get("/api/v1/openapi.json").status_code == 200
        liveness_response = client.get("/api/v1/utils/health-check/")
        assert liveness_response.status_code == 200
        assert liveness_response.json() is True
        assert lifecycle.start_calls == 1
        assert lifecycle.close_calls == 0

    assert lifecycle.close_calls == 1


def test_sequential_lifespans_receive_fresh_services(tmp_path: Path) -> None:
    created_lifecycles: list[RecordingLifecycle] = []

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
    )

    with TestClient(application):
        first_lifecycle = application.state.txt2crs_lifecycle
    with TestClient(application):
        second_lifecycle = application.state.txt2crs_lifecycle

    assert first_lifecycle is not second_lifecycle
    assert len(created_lifecycles) == 2
    assert all(lifecycle.start_calls == 1 for lifecycle in created_lifecycles)
    assert all(lifecycle.close_calls == 1 for lifecycle in created_lifecycles)


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
    )

    with pytest.raises(RuntimeError, match="private startup detail"):
        with TestClient(application):
            pytest.fail("The application must not serve after startup failure.")

    assert lifecycle.start_calls == 1
    assert lifecycle.close_calls == 1

