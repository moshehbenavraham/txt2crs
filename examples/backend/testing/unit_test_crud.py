"""
EXAMPLE: Property-based validation tests for current user request models.

PATTERN: Property-Based Testing for Pydantic Models
USE WHEN: Testing strict request bounds and PATCH semantics
TAGS: testing, hypothesis, unit-test, pydantic

Based on: backend/tests/models/test_user_models.py
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from app.models import UserCreate, UserUpdate

email_strategy = st.emails()
valid_password_strategy = st.text(
    min_size=8,
    max_size=128,
    # Avoid leading/trailing whitespace because strict request models trim it
    # before enforcing their length bounds.
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()",
)
short_password_strategy = st.text(min_size=0, max_size=7)


class TestUserCreate:
    """Demonstrate bounded property tests for a strict create model."""

    @given(email=email_strategy, password=valid_password_strategy)
    @settings(max_examples=50)
    def test_accepts_valid_email_and_password(
        self,
        email: str,
        password: str,
    ) -> None:
        user = UserCreate(email=email, password=password)
        assert "@" in str(user.email)
        assert user.password == password

    @given(password=short_password_strategy)
    @settings(max_examples=20)
    def test_rejects_short_password(self, password: str) -> None:
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password=password)
        assert any("password" in str(error["loc"]) for error in exc_info.value.errors())

    def test_rejects_unknown_fields(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            UserCreate(
                email="test@example.com",
                password="valid-password",
                retired_field="unexpected",  # type: ignore[call-arg]
            )


class TestUserUpdate:
    """Demonstrate omission-sensitive PATCH assertions."""

    def test_omitted_fields_do_not_enter_update_payload(self) -> None:
        update = UserUpdate()
        assert update.model_dump(exclude_unset=True) == {}

    @given(
        full_name=st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ",
            max_size=255,
        )
        | st.none()
    )
    @settings(max_examples=30)
    def test_partial_update_contains_only_explicit_field(
        self,
        full_name: str | None,
    ) -> None:
        update = UserUpdate(full_name=full_name)
        normalized_full_name = full_name.strip() if full_name is not None else None
        assert update.model_dump(exclude_unset=True) == {
            "full_name": normalized_full_name
        }

    def test_explicit_null_email_is_rejected(self) -> None:
        with pytest.raises(ValidationError, match="email may be omitted"):
            UserUpdate(email=None)


# Run from ``backend/`` so the shell's Python environment and pytest
# configuration apply:
#
# uv run pytest tests/models/test_user_models.py -v
