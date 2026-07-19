"""
Database and API schema models.

This module defines all SQLModel-based models for the application, including:
- Database table models (User, Item)
- API request schemas (UserCreate, ItemCreate, etc.)
- API response schemas (UserPublic, ItemPublic, etc.)

Model Categories:
    - Base models: Shared field definitions (UserBase, ItemBase)
    - Create models: Input validation for POST requests
    - Update models: Input validation for PUT/PATCH requests
    - Public models: Response serialization
    - Table models: Database table definitions (table=True)

Validation:
    Request models use strict validation (extra="forbid") to reject
    unknown fields and prevent data leakage attacks.
"""

import uuid
from datetime import UTC, datetime
from typing import Any, Literal, cast

from pydantic import ConfigDict, EmailStr, model_validator
from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlmodel import Field, Relationship, SQLModel

# Content type for stored items - validated at Pydantic level, stored as string in DB
ContentType = Literal["general"]


def get_datetime_utc() -> datetime:
    """Return a timezone-aware UTC timestamp for new database records."""
    return datetime.now(UTC)


class StrictAPIModel(SQLModel):
    """
    Base model for API request validation with strict settings.

    Use this as the base class for all request schemas (Create, Update)
    to enforce strict validation:
    - extra="forbid": Reject any fields not defined in the model
    - validate_default=True: Validate default values
    - str_strip_whitespace=True: Strip whitespace from string inputs

    This prevents API consumers from sending unexpected fields that could
    indicate data leakage attempts or API misuse.

    Example:
        class UserCreate(StrictAPIModel):
            email: EmailStr
            password: str
    """

    # SQLModel's model_config annotation is narrower than Pydantic's ConfigDict.
    model_config = cast(
        Any,
        ConfigDict(
            extra="forbid",
            validate_default=True,
            str_strip_whitespace=True,
        ),
    )


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Request model config - rejects unknown fields to prevent data leakage
_STRICT_REQUEST_CONFIG = ConfigDict(
    extra="forbid",
    validate_default=True,
    str_strip_whitespace=True,
)


class UserCreate(UserBase):
    """
    Request body for creating a new user (admin endpoint).

    Validates email format, password strength, and rejects unknown fields.
    Used by superusers to create new user accounts with optional permissions.
    """

    model_config = cast(Any, _STRICT_REQUEST_CONFIG)
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    """
    Request body for user self-registration.

    Public endpoint schema with strict validation. Users cannot set
    is_active or is_superuser flags during registration.
    """

    model_config = cast(Any, _STRICT_REQUEST_CONFIG)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(SQLModel):
    """
    Request body for updating a user (admin endpoint).

    All fields are optional. Superusers can update any user's details
    including email, password, and permission flags.
    """

    model_config = cast(Any, _STRICT_REQUEST_CONFIG)
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @model_validator(mode="after")
    def reject_explicit_null_email(self) -> UserUpdate:
        """
        Allow email omission for PATCH while rejecting explicit null values.

        This keeps partial-update semantics (field omitted means unchanged)
        without permitting payloads that violate DB non-null constraints.
        """
        if "email" in self.model_fields_set and self.email is None:
            raise ValueError("email may be omitted, but cannot be null")
        return self


class UserUpdateMe(SQLModel):
    """
    Request body for users updating their own profile.

    Limited to non-privileged fields (full_name, email). Users cannot
    change their own is_active or is_superuser status.
    """

    model_config = cast(Any, _STRICT_REQUEST_CONFIG)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def reject_explicit_null_email(self) -> UserUpdateMe:
        """Allow omitted email while rejecting explicit null payload values."""
        if "email" in self.model_fields_set and self.email is None:
            raise ValueError("email may be omitted, but cannot be null")
        return self


class UpdatePassword(SQLModel):
    """
    Request body for password change.

    Requires both current password (for verification) and new password.
    Both must meet the 8-128 character length requirement.
    """

    model_config = cast(Any, _STRICT_REQUEST_CONFIG)
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    # API result fields - all optional for backward compatibility
    source_url: str | None = Field(default=None, max_length=2048)
    content: str | None = Field(default=None, sa_type=Text)
    content_type: ContentType | None = Field(
        default=None,
        max_length=50,
        # SQLModel's typed ``sa_type`` argument accepts a SQLAlchemy type
        # class, not a configured type instance.  Supplying the complete
        # column keeps the database's existing VARCHAR(50) contract while
        # allowing both mypy and ty to validate this model without an ignore.
        sa_column=Column(String(50), nullable=True),
    )
    item_metadata: dict[str, Any] | None = Field(default=None, sa_type=JSON)


class ItemCreate(ItemBase):
    """
    Request body for creating a new item.

    Requires title, all other fields are optional. Rejects unknown fields
    to prevent API misuse.
    """

    model_config = cast(Any, _STRICT_REQUEST_CONFIG)


class ItemUpdate(SQLModel):
    """
    Request body for updating an item.

    All fields are optional for partial updates. Rejects unknown fields
    to prevent API misuse.
    """

    model_config = cast(Any, _STRICT_REQUEST_CONFIG)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    source_url: str | None = Field(default=None, max_length=2048)
    content: str | None = None
    content_type: ContentType | None = None
    item_metadata: dict[str, Any] | None = None


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str


class PasswordRecoveryRequest(SQLModel):
    """
    Request body for initiating password recovery.

    Uses JSON body input (instead of URL path parameters) to avoid exposing
    email addresses in route paths captured by access logs and browser history.
    """

    model_config = cast(Any, _STRICT_REQUEST_CONFIG)
    email: EmailStr = Field(max_length=255)


class NewPassword(SQLModel):
    """
    Request body for password reset completion.

    Submitted after user clicks the password reset link. Token is from
    the email link, new_password must meet strength requirements.
    """

    model_config = cast(Any, _STRICT_REQUEST_CONFIG)
    token: str
    new_password: str = Field(min_length=8, max_length=128)
