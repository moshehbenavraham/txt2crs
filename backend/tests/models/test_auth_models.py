"""
Property-based tests for authentication-related Pydantic models.

Tests validation rules using Hypothesis to generate random inputs,
ensuring models correctly accept valid data and reject invalid data.

Validation rules tested:
    - NewPassword: token (required), new_password (8-128 chars)

Run with: uv run pytest tests/models/test_auth_models.py -v
"""

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from app.models import NewPassword

# --- Custom Strategies ---

# Valid password strategy - 8 to 128 characters
valid_password_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "S"),
        blacklist_characters="\x00\n\r",
    ),
    min_size=8,
    max_size=128,
).filter(lambda s: len(s.strip()) >= 8)

# Invalid password strategy - too short (less than 8 chars)
invalid_short_password_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "S"),
        blacklist_characters="\x00\n\r",
    ),
    min_size=1,
    max_size=7,
)

# Invalid password strategy - too long (more than 128 chars)
invalid_long_password_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters="\x00\n\r",
    ),
    min_size=129,
    max_size=200,
)

# Valid token strategy - any non-empty string (typically JWT)
valid_token_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N"),
        whitelist_characters=".-_",
    ),
    min_size=1,
    max_size=500,
).filter(lambda s: len(s.strip()) >= 1)


# --- NewPassword Tests ---


class TestNewPasswordValidation:
    """Property-based tests for NewPassword model."""

    @pytest.mark.hypothesis
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(
        token=valid_token_strategy,
        new_password=valid_password_strategy,
    )
    def test_valid_new_password_accepted(
        self,
        token: str,
        new_password: str,
    ) -> None:
        """NewPassword accepts valid token and password combinations."""
        assume(len(new_password.strip()) >= 8)
        assume(len(token.strip()) >= 1)

        reset = NewPassword(
            token=token,
            new_password=new_password,
        )
        # Token gets stripped
        assert reset.token.strip() == token.strip()
        assert reset.new_password.strip() == new_password.strip()

    @pytest.mark.hypothesis
    @settings(
        max_examples=25,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(new_password=invalid_short_password_strategy)
    def test_short_password_rejected(self, new_password: str) -> None:
        """NewPassword rejects passwords shorter than 8 characters."""
        assume(len(new_password.strip()) < 8)

        with pytest.raises(ValidationError) as exc_info:
            NewPassword(
                token="valid.jwt.token",
                new_password=new_password,
            )

        errors = exc_info.value.errors()
        assert any("new_password" in str(e.get("loc", [])) for e in errors), (
            f"Expected new_password validation error, got: {errors}"
        )

    @pytest.mark.hypothesis
    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(new_password=invalid_long_password_strategy)
    def test_long_password_rejected(self, new_password: str) -> None:
        """NewPassword rejects passwords longer than 128 characters."""
        with pytest.raises(ValidationError) as exc_info:
            NewPassword(
                token="valid.jwt.token",
                new_password=new_password,
            )

        errors = exc_info.value.errors()
        assert any("new_password" in str(e.get("loc", [])) for e in errors), (
            f"Expected new_password validation error, got: {errors}"
        )

    def test_missing_token_rejected(self) -> None:
        """NewPassword requires a token."""
        with pytest.raises(ValidationError) as exc_info:
            NewPassword(
                new_password="validpassword123",
            )  # type: ignore[call-arg]

        errors = exc_info.value.errors()
        assert any("token" in str(e.get("loc", [])) for e in errors), (
            f"Expected token validation error, got: {errors}"
        )

    def test_missing_password_rejected(self) -> None:
        """NewPassword requires a new_password."""
        with pytest.raises(ValidationError) as exc_info:
            NewPassword(
                token="valid.jwt.token",
            )  # type: ignore[call-arg]

        errors = exc_info.value.errors()
        assert any("new_password" in str(e.get("loc", [])) for e in errors), (
            f"Expected new_password validation error, got: {errors}"
        )

    def test_extra_fields_rejected(self) -> None:
        """NewPassword rejects unknown fields (strict mode)."""
        with pytest.raises(ValidationError) as exc_info:
            NewPassword(
                token="valid.jwt.token",
                new_password="validpassword123",
                confirm_password="should_fail",  # type: ignore[call-arg]
            )

        errors = exc_info.value.errors()
        assert any(e.get("type") == "extra_forbidden" for e in errors), (
            f"Expected extra_forbidden error, got: {errors}"
        )

    def test_realistic_jwt_token_accepted(self) -> None:
        """NewPassword accepts realistic JWT-style tokens."""
        # Typical JWT format: header.payload.signature
        realistic_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"

        reset = NewPassword(
            token=realistic_token,
            new_password="validpassword123",
        )
        assert reset.token == realistic_token

    @pytest.mark.hypothesis
    @settings(
        max_examples=25,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(
        password=st.text(
            alphabet=st.characters(
                whitelist_categories=("L", "N", "P", "S", "Zs"),
                blacklist_characters="\x00\n\r",
            ),
            min_size=8,
            max_size=128,
        )
    )
    def test_passwords_with_special_chars_accepted(self, password: str) -> None:
        """NewPassword accepts passwords with special characters."""
        assume(len(password.strip()) >= 8)

        reset = NewPassword(
            token="valid.jwt.token",
            new_password=password,
        )
        assert reset.new_password.strip() == password.strip()

    def test_unicode_password_accepted(self) -> None:
        """NewPassword accepts passwords with unicode characters."""
        unicode_password = "пароль123ñ"  # Cyrillic + Spanish

        reset = NewPassword(
            token="valid.jwt.token",
            new_password=unicode_password,
        )
        assert reset.new_password == unicode_password
