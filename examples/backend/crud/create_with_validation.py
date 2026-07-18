"""
EXAMPLE: Create entity with validation and error handling

PATTERN: CRUD Create with Duplicate Check
USE WHEN: Creating new database records that require uniqueness validation
TAGS: crud, validation, error-handling, create

This example demonstrates:
1. Input validation using Pydantic strict models
2. Duplicate checking before insert
3. Proper error handling with semantic error codes
4. Transaction management with SQLModel

Based on: app/crud.py:create_user
"""

from sqlmodel import Session, select

from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.core.security import get_password_hash
from app.models import User, UserCreate


def create_user_with_duplicate_check(
    *,
    session: Session,
    user_create: UserCreate,
) -> User:
    """
    Create a new user with email uniqueness validation.

    Preconditions:
        - session is an active database session
        - user_create contains valid email and password (8-128 chars)

    Postconditions:
        - Returns User with auto-generated UUID id
        - User.hashed_password contains an Argon2id hash (never plain password)
        - User exists in database (committed)

    Args:
        session: Database session for query execution.
        user_create: User creation data with email, password, optional full_name.

    Returns:
        The created User object with generated UUID and timestamps.

    Raises:
        AppException: USER_ALREADY_EXISTS if email is taken.

    Example:
        >>> from app.models import UserCreate
        >>> user_data = UserCreate(
        ...     email="newuser@example.com",
        ...     password="SecureP@ss123",
        ...     full_name="John Doe"
        ... )
        >>> user = create_user_with_duplicate_check(session=session, user_create=user_data)
        >>> print(user.id, user.email)
    """
    # Step 1: Check for existing user with same email
    existing_user = session.exec(
        select(User).where(User.email == user_create.email)
    ).first()

    if existing_user:
        raise AppException(
            code=ErrorCode.USER_ALREADY_EXISTS,
            detail=f"User with email '{user_create.email}' already exists",
        )

    # Step 2: Create user with hashed password
    # IMPORTANT: Never store plain password, always hash
    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )

    # Step 3: Persist to database
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


# === USAGE IN ROUTE HANDLER ===
#
# from app.api.deps import SessionDep
# from examples.backend.crud.create_with_validation import create_user_with_duplicate_check
#
# @router.post("/users/", response_model=UserPublic, status_code=201)
# def create_user(session: SessionDep, user_in: UserCreate) -> User:
#     return create_user_with_duplicate_check(session=session, user_create=user_in)


# === KEY PATTERNS USED ===
#
# 1. Keyword-only arguments (*, session: Session)
#    - Forces named arguments for clarity
#
# 2. model_validate with update dict
#    - Converts Pydantic model to SQLModel
#    - Injects computed fields (hashed_password)
#
# 3. Structured exceptions (AppException)
#    - Use ErrorCode enum for machine-readable errors
#    - Follows RFC 9457 Problem Details format
#
# 4. Session lifecycle: add -> commit -> refresh
#    - refresh() populates auto-generated fields (id, timestamps)
