"""
EXAMPLE: Unit testing CRUD functions with Hypothesis

PATTERN: Property-Based Testing for Pydantic Models
USE WHEN: Testing validation rules and CRUD operations
TAGS: testing, hypothesis, unit-test, crud, pydantic

This example demonstrates:
1. Property-based testing with Hypothesis
2. Testing Pydantic model validation
3. Mocking database session
4. Testing edge cases automatically

Based on: backend/tests/models/test_user_models.py
"""

import pytest
from hypothesis import given, strategies as st, settings
from pydantic import ValidationError

from app.models import UserCreate, ItemCreate, ItemUpdate


# =============================================================================
# HYPOTHESIS STRATEGIES
# =============================================================================

# Strategy for generating valid email addresses
email_strategy = st.emails()

# Strategy for valid passwords (8-128 chars)
valid_password_strategy = st.text(
    min_size=8,
    max_size=128,
    alphabet=st.characters(
        blacklist_categories=("Cs",),  # Exclude surrogate characters
        blacklist_characters="\x00",  # Exclude null
    ),
)

# Strategy for invalid passwords (too short)
short_password_strategy = st.text(min_size=0, max_size=7)

# Strategy for item titles (1-255 chars)
valid_title_strategy = st.text(min_size=1, max_size=255).filter(lambda x: x.strip())


# =============================================================================
# USER MODEL TESTS
# =============================================================================


class TestUserCreate:
    """Tests for UserCreate Pydantic model validation."""

    @given(
        email=email_strategy,
        password=valid_password_strategy,
    )
    @settings(max_examples=50)
    def test_accepts_valid_email_and_password(
        self,
        email: str,
        password: str,
    ) -> None:
        """
        Property: UserCreate accepts any valid email with password 8-128 chars.

        This test generates random valid inputs to verify the model
        accepts all valid combinations.
        """
        user = UserCreate(email=email, password=password)

        # Email should be stored (possibly normalized)
        assert user.email is not None
        assert "@" in user.email

        # Password should be stored as-is (hashing happens in CRUD layer)
        assert user.password == password

    @given(password=short_password_strategy)
    @settings(max_examples=20)
    def test_rejects_short_password(self, password: str) -> None:
        """
        Property: UserCreate rejects passwords shorter than 8 characters.
        """
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password=password)

        # Verify the error is about password length
        errors = exc_info.value.errors()
        assert any("password" in str(e["loc"]) for e in errors)

    def test_rejects_invalid_email_format(self) -> None:
        """
        Unit test: UserCreate rejects malformed email addresses.
        """
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationError):
                UserCreate(email=email, password="validpassword123")

    @given(
        email=email_strategy,
        password=valid_password_strategy,
        full_name=st.text(max_size=255) | st.none(),
    )
    @settings(max_examples=30)
    def test_accepts_optional_full_name(
        self,
        email: str,
        password: str,
        full_name: str | None,
    ) -> None:
        """
        Property: full_name is optional and can be any string up to 255 chars.
        """
        user = UserCreate(email=email, password=password, full_name=full_name)
        assert user.full_name == full_name


# =============================================================================
# ITEM MODEL TESTS
# =============================================================================


class TestItemCreate:
    """Tests for ItemCreate Pydantic model validation."""

    @given(title=valid_title_strategy)
    @settings(max_examples=50)
    def test_accepts_valid_title(self, title: str) -> None:
        """
        Property: ItemCreate accepts any non-empty title up to 255 chars.
        """
        item = ItemCreate(title=title)
        assert item.title == title

    def test_rejects_empty_title(self) -> None:
        """
        Unit test: ItemCreate requires non-empty title.
        """
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title="")

        errors = exc_info.value.errors()
        assert any("title" in str(e["loc"]) for e in errors)

    def test_rejects_title_too_long(self) -> None:
        """
        Unit test: ItemCreate rejects titles over 255 characters.
        """
        long_title = "a" * 256

        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title=long_title)

        errors = exc_info.value.errors()
        assert any("title" in str(e["loc"]) for e in errors)

    @given(
        title=valid_title_strategy,
        description=st.text(max_size=255) | st.none(),
    )
    @settings(max_examples=30)
    def test_accepts_optional_description(
        self,
        title: str,
        description: str | None,
    ) -> None:
        """
        Property: description is optional and can be any string up to 255 chars.
        """
        item = ItemCreate(title=title, description=description)
        assert item.description == description


class TestItemUpdate:
    """Tests for ItemUpdate Pydantic model (partial updates)."""

    def test_all_fields_optional(self) -> None:
        """
        Unit test: ItemUpdate allows empty updates (no fields set).
        """
        # All fields are optional for partial updates
        update = ItemUpdate()

        # model_dump(exclude_unset=True) should return empty dict
        data = update.model_dump(exclude_unset=True)
        assert data == {}

    @given(title=valid_title_strategy)
    @settings(max_examples=20)
    def test_partial_update_title_only(self, title: str) -> None:
        """
        Property: ItemUpdate can update just the title.
        """
        update = ItemUpdate(title=title)
        data = update.model_dump(exclude_unset=True)

        assert data == {"title": title}
        assert "description" not in data


# =============================================================================
# KEY PATTERNS
# =============================================================================
#
# 1. Hypothesis Strategies
#    - st.emails() - generates valid emails
#    - st.text(min_size=X, max_size=Y) - generates strings
#    - st.none() - generates None
#    - strategy | st.none() - optional values
#    - strategy.filter(predicate) - filter generated values
#
# 2. Test Decorators
#    @given(param=strategy)  - inject generated values
#    @settings(max_examples=N)  - limit test iterations
#
# 3. Validation Error Testing
#    with pytest.raises(ValidationError) as exc_info:
#        Model(invalid_data)
#    errors = exc_info.value.errors()
#
# 4. Partial Update Testing
#    model.model_dump(exclude_unset=True)
#    - Only includes explicitly set fields
#    - Essential for testing PATCH-style updates


# =============================================================================
# RUNNING TESTS
# =============================================================================
#
# # Run all tests in this file
# uv run pytest tests/models/test_user_models.py -v
#
# # Run only hypothesis tests
# uv run pytest tests/models/ -v -m hypothesis
#
# # Run with more examples (thorough testing)
# uv run pytest tests/models/ -v --hypothesis-seed=0
