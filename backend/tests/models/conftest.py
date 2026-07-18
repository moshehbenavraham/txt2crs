"""
Conftest for model validation tests.

These tests are pure unit tests that don't require database or settings.
They test Pydantic model validation in isolation.
"""

import pytest


# Override the session-scoped db fixture from the parent conftest
# to avoid loading settings/database for pure model tests
@pytest.fixture(scope="session", autouse=True)
def db() -> None:
    """No-op fixture to override parent conftest's db fixture."""
    return None
