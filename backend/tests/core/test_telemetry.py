from importlib import metadata as importlib_metadata
from unittest.mock import patch

from app.core.telemetry import get_service_version


def _clear_service_version_cache() -> None:
    get_service_version.cache_clear()


def test_get_service_version_uses_package_metadata() -> None:
    _clear_service_version_cache()
    with patch(
        "app.core.telemetry.importlib_metadata.version",
        return_value="0.1.99",
    ):
        assert get_service_version() == "0.1.99"


def test_get_service_version_falls_back_when_package_missing() -> None:
    _clear_service_version_cache()
    with patch(
        "app.core.telemetry.importlib_metadata.version",
        side_effect=importlib_metadata.PackageNotFoundError,
    ):
        assert get_service_version() == "unknown"


def test_get_service_version_falls_back_on_unexpected_error() -> None:
    _clear_service_version_cache()
    with patch(
        "app.core.telemetry.importlib_metadata.version",
        side_effect=RuntimeError("metadata backend unavailable"),
    ):
        assert get_service_version() == "unknown"
