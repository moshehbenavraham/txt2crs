from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.telemetry import get_service_version


def test_health_endpoint_reports_healthy_when_db_available(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/utils/health/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["database"] == "healthy"
    assert payload["version"] == get_service_version()


def test_health_endpoint_returns_503_when_db_unavailable(client: TestClient) -> None:
    with patch(
        "app.api.routes.utils.engine.connect",
        side_effect=RuntimeError("database unavailable"),
    ):
        response = client.get(f"{settings.API_V1_STR}/utils/health/")

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "unhealthy"
    assert payload["database"] == "unhealthy"


def test_health_check_liveness_endpoint_remains_up(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/utils/health-check/")

    assert response.status_code == 200
    assert response.json() is True
