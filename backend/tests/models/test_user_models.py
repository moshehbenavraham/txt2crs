"""
Property-based tests for User-related Pydantic models.

Tests validation rules using Hypothesis to generate random inputs,
ensuring models correctly accept valid data and reject invalid data.

Validation rules tested:
    - Email: Valid EmailStr format
    - Password: 8-128 characters
    - full_name: Optional, max 255 characters
    - is_active, is_superuser: Boolean flags

Run with: uv run pytest tests/models/test_user_models.py -v
"""

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from app.models import (
    UpdatePassword,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
)

# --- Custom Strategies ---

# Valid email strategy - generates RFC 5321-compliant emails
email_strategy = st.emails()

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

# Valid full_name strategy - optional, max 255 characters
full_name_strategy = st.one_of(
    st.none(),
    st.text(
        alphabet=st.characters(
            whitelist_categories=("L", "N", "Zs"),
            blacklist_characters="\x00\n\r\t",
        ),
        min_size=1,
        max_size=255,
    ).filter(lambda s: len(s.strip()) > 0 if s else True),
)


# --- UserCreate Tests ---


class TestUserCreateValidation:
    """Property-based tests for UserCreate model."""

    @pytest.mark.hypothesis
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(
        email=email_strategy,
        password=valid_password_strategy,
        full_name=full_name_strategy,
        is_active=st.booleans(),
        is_superuser=st.booleans(),
    )
    def test_valid_user_create_accepted(
        self,
        email: str,
        password: str,
        full_name: str | None,
        is_active: bool,
        is_superuser: bool,
    ) -> None:
        """UserCreate accepts any valid email/password/full_name combo."""
        assume(len(password.strip()) >= 8)  # Ensure password meets min after strip

        user = UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        # EmailStr normalizes domain to lowercase and may encode IDN to punycode
        assert "@" in user.email
        # Local part (before @) should be preserved
        assert user.email.split("@")[0].lower() == email.split("@")[0].lower()
        # Password is stripped if whitespace-only, so compare stripped version
        assert user.password.strip() == password.strip()

    @pytest.mark.hypothesis
    @settings(
        max_examples=25,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(password=invalid_short_password_strategy)
    def test_short_password_rejected(self, password: str) -> None:
        """UserCreate rejects passwords shorter than 8 characters."""
        assume(len(password.strip()) < 8)

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password=password,
            )

        errors = exc_info.value.errors()
        assert any("password" in str(e.get("loc", [])) for e in errors), (
            f"Expected password validation error, got: {errors}"
        )

    @pytest.mark.hypothesis
    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(password=invalid_long_password_strategy)
    def test_long_password_rejected(self, password: str) -> None:
        """UserCreate rejects passwords longer than 128 characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password=password,
            )

        errors = exc_info.value.errors()
        assert any("password" in str(e.get("loc", [])) for e in errors), (
            f"Expected password validation error, got: {errors}"
        )

    @pytest.mark.hypothesis
    @settings(max_examples=25)
    @given(
        invalid_email=st.text(
            alphabet=st.characters(whitelist_categories=("L", "N")),
            min_size=1,
            max_size=50,
        ).filter(
            lambda s: "@" not in s or "." not in s.split("@")[-1] if "@" in s else True
        )
    )
    def test_invalid_email_rejected(self, invalid_email: str) -> None:
        """UserCreate rejects invalid email formats."""
        assume("@" not in invalid_email or not invalid_email.endswith(".com"))

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email=invalid_email,
                password="validpassword123",
            )

        errors = exc_info.value.errors()
        assert any("email" in str(e.get("loc", [])) for e in errors), (
            f"Expected email validation error, got: {errors}"
        )

    def test_extra_fields_rejected(self) -> None:
        """UserCreate rejects unknown fields (strict mode)."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="validpassword123",
                unknown_field="should_fail",  # type: ignore[call-arg]
            )

        errors = exc_info.value.errors()
        assert any(e.get("type") == "extra_forbidden" for e in errors), (
            f"Expected extra_forbidden error, got: {errors}"
        )


# --- UserRegister Tests ---


class TestUserRegisterValidation:
    """Property-based tests for UserRegister model."""

    @pytest.mark.hypothesis
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(
        email=email_strategy,
        password=valid_password_strategy,
        full_name=full_name_strategy,
    )
    def test_valid_registration_accepted(
        self,
        email: str,
        password: str,
        full_name: str | None,
    ) -> None:
        """UserRegister accepts valid email/password combinations."""
        assume(len(password.strip()) >= 8)

        user = UserRegister(
            email=email,
            password=password,
            full_name=full_name,
        )
        # EmailStr normalizes domain to lowercase and may encode IDN to punycode
        # Just verify the model was created and has a valid email
        assert "@" in user.email
        # Local part (before @) should be preserved
        assert user.email.split("@")[0].lower() == email.split("@")[0].lower()
        assert user.password.strip() == password.strip()

    def test_cannot_set_is_superuser(self) -> None:
        """UserRegister does not allow setting is_superuser."""
        with pytest.raises(ValidationError):
            UserRegister(
                email="test@example.com",
                password="validpassword123",
                is_superuser=True,  # type: ignore[call-arg]
            )

    def test_cannot_set_is_active(self) -> None:
        """UserRegister does not allow setting is_active."""
        with pytest.raises(ValidationError):
            UserRegister(
                email="test@example.com",
                password="validpassword123",
                is_active=False,  # type: ignore[call-arg]
            )


# --- UserUpdate Tests ---


class TestUserUpdateValidation:
    """Property-based tests for UserUpdate model."""

    @pytest.mark.hypothesis
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(
        email=email_strategy,
        password=st.one_of(st.none(), valid_password_strategy),
        full_name=full_name_strategy,
        is_active=st.booleans(),
        is_superuser=st.booleans(),
    )
    def test_valid_update_accepted(
        self,
        email: str,
        password: str | None,
        full_name: str | None,
        is_active: bool,
        is_superuser: bool,
    ) -> None:
        """UserUpdate accepts valid partial updates."""
        if password is not None:
            assume(len(password.strip()) >= 8)

        user = UserUpdate(
            email=email,
            password=password,
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        # EmailStr normalizes domain to lowercase and may encode IDN to punycode
        assert user.email is not None
        assert "@" in user.email
        # Local part (before @) should be preserved
        assert user.email.split("@")[0].lower() == email.split("@")[0].lower()
        if password is not None:
            assert user.password is not None
            assert user.password.strip() == password.strip()
        else:
            assert user.password is None

    def test_all_fields_optional(self) -> None:
        """UserUpdate omits defaulted booleans from partial-update data."""
        user = UserUpdate()
        assert user.email is None
        assert user.password is None
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.full_name is None
        assert user.model_dump(exclude_unset=True) == {}

    @pytest.mark.parametrize("field_name", ["is_active", "is_superuser"])
    def test_explicit_null_boolean_rejected(self, field_name: str) -> None:
        """Boolean update fields reject explicit null values."""
        with pytest.raises(ValidationError):
            UserUpdate(**{field_name: None})

    @pytest.mark.parametrize("field_name", ["is_active", "is_superuser"])
    def test_boolean_openapi_fields_are_optional_but_not_nullable(
        self, field_name: str
    ) -> None:
        """OpenAPI permits omission but never advertises JSON null."""
        schema = UserUpdate.model_json_schema()
        field_schema = schema["properties"][field_name]

        assert field_name not in schema.get("required", [])
        assert field_schema["type"] == "boolean"
        assert "anyOf" not in field_schema

    def test_explicit_null_email_rejected(self) -> None:
        """UserUpdate rejects explicit null email while allowing omission."""
        with pytest.raises(ValidationError):
            UserUpdate(email=None)


# --- UserUpdateMe Tests ---


class TestUserUpdateMeValidation:
    """Property-based tests for UserUpdateMe model."""

    @pytest.mark.hypothesis
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(
        email=email_strategy,
        full_name=full_name_strategy,
    )
    def test_valid_self_update_accepted(
        self,
        email: str,
        full_name: str | None,
    ) -> None:
        """UserUpdateMe accepts valid email and full_name."""
        user = UserUpdateMe(
            email=email,
            full_name=full_name,
        )
        # EmailStr normalizes domain to lowercase and may encode IDN to punycode
        assert user.email is not None
        assert "@" in user.email
        # Local part (before @) should be preserved
        assert user.email.split("@")[0].lower() == email.split("@")[0].lower()
        # full_name gets stripped
        if full_name is not None:
            assert (
                user.full_name == full_name.strip()
                if full_name.strip()
                else user.full_name == ""
            )
        else:
            assert user.full_name is None

    def test_explicit_null_email_rejected(self) -> None:
        """UserUpdateMe rejects explicit null email while allowing omission."""
        with pytest.raises(ValidationError):
            UserUpdateMe(email=None)

    def test_cannot_set_is_superuser(self) -> None:
        """UserUpdateMe does not allow setting is_superuser."""
        with pytest.raises(ValidationError):
            UserUpdateMe(
                email="test@example.com",
                is_superuser=True,  # type: ignore[call-arg]
            )

    def test_cannot_set_is_active(self) -> None:
        """UserUpdateMe does not allow setting is_active."""
        with pytest.raises(ValidationError):
            UserUpdateMe(
                email="test@example.com",
                is_active=False,  # type: ignore[call-arg]
            )

    def test_cannot_set_password(self) -> None:
        """UserUpdateMe does not allow setting password."""
        with pytest.raises(ValidationError):
            UserUpdateMe(
                email="test@example.com",
                password="newpassword123",  # type: ignore[call-arg]
            )


# --- UpdatePassword Tests ---


class TestUpdatePasswordValidation:
    """Property-based tests for UpdatePassword model."""

    @pytest.mark.hypothesis
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(
        current_password=valid_password_strategy,
        new_password=valid_password_strategy,
    )
    def test_valid_password_update_accepted(
        self,
        current_password: str,
        new_password: str,
    ) -> None:
        """UpdatePassword accepts valid current and new passwords."""
        assume(len(current_password.strip()) >= 8)
        assume(len(new_password.strip()) >= 8)

        update = UpdatePassword(
            current_password=current_password,
            new_password=new_password,
        )
        assert update.current_password.strip() == current_password.strip()
        assert update.new_password.strip() == new_password.strip()

    @pytest.mark.hypothesis
    @settings(
        max_examples=25,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(current_password=invalid_short_password_strategy)
    def test_short_current_password_rejected(self, current_password: str) -> None:
        """UpdatePassword rejects current password shorter than 8 characters."""
        assume(len(current_password.strip()) < 8)

        with pytest.raises(ValidationError) as exc_info:
            UpdatePassword(
                current_password=current_password,
                new_password="validnewpass123",
            )

        errors = exc_info.value.errors()
        assert any("current_password" in str(e.get("loc", [])) for e in errors), (
            f"Expected current_password validation error, got: {errors}"
        )

    @pytest.mark.hypothesis
    @settings(
        max_examples=25,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(new_password=invalid_short_password_strategy)
    def test_short_new_password_rejected(self, new_password: str) -> None:
        """UpdatePassword rejects new password shorter than 8 characters."""
        assume(len(new_password.strip()) < 8)

        with pytest.raises(ValidationError) as exc_info:
            UpdatePassword(
                current_password="validcurrentpass",
                new_password=new_password,
            )

        errors = exc_info.value.errors()
        assert any("new_password" in str(e.get("loc", [])) for e in errors), (
            f"Expected new_password validation error, got: {errors}"
        )

    def test_extra_fields_rejected(self) -> None:
        """UpdatePassword rejects unknown fields (strict mode)."""
        with pytest.raises(ValidationError) as exc_info:
            UpdatePassword(
                current_password="validcurrentpass",
                new_password="validnewpass123",
                confirm_password="should_fail",  # type: ignore[call-arg]
            )

        errors = exc_info.value.errors()
        assert any(e.get("type") == "extra_forbidden" for e in errors), (
            f"Expected extra_forbidden error, got: {errors}"
        )
