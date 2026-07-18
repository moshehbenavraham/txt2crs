"""
Property-based tests for Item-related Pydantic models.

Tests validation rules using Hypothesis to generate random inputs,
ensuring models correctly accept valid data and reject invalid data.

Validation rules tested:
    - title: 1-255 characters, required
    - description: Optional, max 255 characters
    - source_url: Optional, max 2048 characters
    - content: Optional, text (no length limit in model)
    - content_type: Optional, literal "general"
    - item_metadata: Optional, dict[str, Any]

Run with: uv run pytest tests/models/test_item_models.py -v
"""

from typing import Any

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from app.models import Item, ItemCreate, ItemUpdate

# --- Custom Strategies ---

# Valid title strategy - 1 to 255 characters
valid_title_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "Zs", "P"),
        blacklist_characters="\x00\n\r\t",
    ),
    min_size=1,
    max_size=255,
).filter(lambda s: len(s.strip()) >= 1)

# Invalid title strategy - empty or too long
invalid_empty_title_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=("Zs",),  # Only whitespace
    ),
    min_size=0,
    max_size=10,
)

invalid_long_title_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N")),
    min_size=256,
    max_size=300,
)

# Valid description strategy - optional, max 255 characters
description_strategy = st.one_of(
    st.none(),
    st.text(
        alphabet=st.characters(
            whitelist_categories=("L", "N", "Zs", "P"),
            blacklist_characters="\x00\n\r",
        ),
        min_size=0,
        max_size=255,
    ),
)

# Invalid description strategy - too long
invalid_long_description_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N")),
    min_size=256,
    max_size=300,
)

# Valid source_url strategy - optional, max 2048 characters
source_url_strategy = st.one_of(
    st.none(),
    st.text(
        alphabet=st.characters(
            whitelist_categories=("L", "N", "P"),
            whitelist_characters=":/.-_?&=",
            blacklist_characters="\x00\n\r\t",
        ),
        min_size=0,
        max_size=2048,
    ),
)

# Valid content strategy - optional, no length limit
content_strategy = st.one_of(
    st.none(),
    st.text(
        alphabet=st.characters(
            whitelist_categories=("L", "N", "Zs", "P"),
            blacklist_characters="\x00",
        ),
        min_size=0,
        max_size=5000,
    ),
)

# Valid content_type strategy - only "general" or None
content_type_strategy = st.one_of(
    st.none(),
    st.just("general"),
)

# Valid item_metadata strategy - optional dict
item_metadata_strategy = st.one_of(
    st.none(),
    st.dictionaries(
        keys=st.text(
            alphabet=st.characters(whitelist_categories=("L", "N")),
            min_size=1,
            max_size=50,
        ),
        values=st.one_of(
            st.text(min_size=0, max_size=100),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans(),
            st.none(),
        ),
        min_size=0,
        max_size=10,
    ),
)


# --- ItemCreate Tests ---


class TestItemCreateValidation:
    """Property-based tests for ItemCreate model."""

    @pytest.mark.hypothesis
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(
        title=valid_title_strategy,
        description=description_strategy,
        source_url=source_url_strategy,
        content=content_strategy,
        content_type=content_type_strategy,
        item_metadata=item_metadata_strategy,
    )
    def test_valid_item_create_accepted(
        self,
        title: str,
        description: str | None,
        source_url: str | None,
        content: str | None,
        content_type: str | None,
        item_metadata: dict[str, Any] | None,
    ) -> None:
        """ItemCreate accepts any valid title with optional fields."""
        assume(len(title.strip()) >= 1)

        item = ItemCreate(
            title=title,
            description=description,
            source_url=source_url,
            content=content,
            content_type=content_type,  # type: ignore[arg-type]
            item_metadata=item_metadata,
        )
        # Title gets stripped
        assert item.title.strip() == title.strip()
        assert item.description == (description.strip() if description else description)

    @pytest.mark.hypothesis
    @settings(
        max_examples=25,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(title=invalid_empty_title_strategy)
    def test_empty_title_rejected(self, title: str) -> None:
        """ItemCreate rejects empty or whitespace-only titles."""
        assume(len(title.strip()) == 0)

        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title=title)

        errors = exc_info.value.errors()
        assert any("title" in str(e.get("loc", [])) for e in errors), (
            f"Expected title validation error, got: {errors}"
        )

    @pytest.mark.hypothesis
    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(title=invalid_long_title_strategy)
    def test_long_title_rejected(self, title: str) -> None:
        """ItemCreate rejects titles longer than 255 characters."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title=title)

        errors = exc_info.value.errors()
        assert any("title" in str(e.get("loc", [])) for e in errors), (
            f"Expected title validation error, got: {errors}"
        )

    @pytest.mark.hypothesis
    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(description=invalid_long_description_strategy)
    def test_long_description_rejected(self, description: str) -> None:
        """ItemCreate rejects descriptions longer than 255 characters."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(
                title="Valid Title",
                description=description,
            )

        errors = exc_info.value.errors()
        assert any("description" in str(e.get("loc", [])) for e in errors), (
            f"Expected description validation error, got: {errors}"
        )

    def test_invalid_content_type_rejected(self) -> None:
        """ItemCreate rejects invalid content_type values."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(
                title="Valid Title",
                content_type="invalid_type",  # type: ignore[arg-type]
            )

        errors = exc_info.value.errors()
        assert any("content_type" in str(e.get("loc", [])) for e in errors), (
            f"Expected content_type validation error, got: {errors}"
        )

    def test_extra_fields_rejected(self) -> None:
        """ItemCreate rejects unknown fields (strict mode)."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(
                title="Valid Title",
                unknown_field="should_fail",  # type: ignore[call-arg]
            )

        errors = exc_info.value.errors()
        assert any(e.get("type") == "extra_forbidden" for e in errors), (
            f"Expected extra_forbidden error, got: {errors}"
        )

    def test_minimal_item_accepted(self) -> None:
        """ItemCreate accepts item with only required title."""
        item = ItemCreate(title="A")
        assert item.title == "A"
        assert item.description is None
        assert item.source_url is None
        assert item.content is None
        assert item.content_type is None
        assert item.item_metadata is None


# --- ItemUpdate Tests ---


class TestItemUpdateValidation:
    """Property-based tests for ItemUpdate model."""

    @pytest.mark.hypothesis
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(
        title=st.one_of(st.none(), valid_title_strategy),
        description=description_strategy,
        source_url=source_url_strategy,
        content=content_strategy,
        content_type=content_type_strategy,
        item_metadata=item_metadata_strategy,
    )
    def test_valid_item_update_accepted(
        self,
        title: str | None,
        description: str | None,
        source_url: str | None,
        content: str | None,
        content_type: str | None,
        item_metadata: dict[str, Any] | None,
    ) -> None:
        """ItemUpdate accepts valid partial updates."""
        if title is not None:
            assume(len(title.strip()) >= 1)

        item = ItemUpdate(
            title=title,
            description=description,
            source_url=source_url,
            content=content,
            content_type=content_type,  # type: ignore[arg-type]
            item_metadata=item_metadata,
        )
        if title is not None:
            assert item.title is not None
            assert item.title.strip() == title.strip()
        else:
            assert item.title is None

    def test_all_fields_optional(self) -> None:
        """ItemUpdate allows empty update (all fields None/default)."""
        item = ItemUpdate()
        assert item.title is None
        assert item.description is None
        assert item.source_url is None
        assert item.content is None
        assert item.content_type is None
        assert item.item_metadata is None

    @pytest.mark.hypothesis
    @settings(
        max_examples=25,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(title=invalid_empty_title_strategy)
    def test_empty_title_update_rejected(self, title: str) -> None:
        """ItemUpdate rejects empty or whitespace-only titles when provided."""
        assume(len(title.strip()) == 0 and title != "")
        assume(title is not None)

        # Only test if title is provided but empty after strip
        with pytest.raises(ValidationError) as exc_info:
            ItemUpdate(title=title)

        errors = exc_info.value.errors()
        assert any("title" in str(e.get("loc", [])) for e in errors), (
            f"Expected title validation error, got: {errors}"
        )

    @pytest.mark.hypothesis
    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
    )
    @given(title=invalid_long_title_strategy)
    def test_long_title_update_rejected(self, title: str) -> None:
        """ItemUpdate rejects titles longer than 255 characters."""
        with pytest.raises(ValidationError) as exc_info:
            ItemUpdate(title=title)

        errors = exc_info.value.errors()
        assert any("title" in str(e.get("loc", [])) for e in errors), (
            f"Expected title validation error, got: {errors}"
        )

    def test_extra_fields_rejected(self) -> None:
        """ItemUpdate rejects unknown fields (strict mode)."""
        with pytest.raises(ValidationError) as exc_info:
            ItemUpdate(
                title="Valid Title",
                owner_id="should_fail",  # type: ignore[call-arg]
            )

        errors = exc_info.value.errors()
        assert any(e.get("type") == "extra_forbidden" for e in errors), (
            f"Expected extra_forbidden error, got: {errors}"
        )


def test_item_owner_id_column_is_indexed() -> None:
    index_names = {index.name for index in Item.__table__.indexes}
    assert "ix_item_owner_id" in index_names


def test_item_content_type_column_preserves_database_length() -> None:
    assert Item.__table__.c.content_type.type.length == 50
