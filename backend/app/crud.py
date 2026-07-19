"""
Database CRUD operations for User and Item models.

This module provides create, read, update functions for the core domain models.
All functions follow the pattern of receiving a database session and returning
model instances.

All functions use Design-by-Contract (DbC) documentation:
- **Preconditions**: What must be true before calling the function
- **Postconditions**: What will be true after the function returns
- **Invariants**: What remains constant throughout operation
- **Raises**: Exceptions that may be raised and their conditions

Usage:
    from app import crud
    from app.api.deps import get_db

    # Create user
    user = crud.create_user(session=session, user_create=user_data)

    # Authenticate user
    user = crud.authenticate(session=session, email="user@example.com", password="secret")

    # Create item
    item = crud.create_item(session=session, item_in=item_data, owner_id=user.id)
"""

import uuid

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate

# Valid hashes used only to equalize password work for failed authentication.
# Their source passwords are not credentials and the hashes are never stored.
DUMMY_ARGON2_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$hjgjb3AO1hTbIvPyTido1Q"
    "$MelcZm0QrwTPLP8sxyQ8xgGgg7m60dAWa5Ppj+v1f+E"
)
DUMMY_BCRYPT_PASSWORD_HASH = (
    # Encoded bcrypt data can contain apparent short words by chance.
    "$2b$12$/ZsLFJfWQIE2AY8A7LXdVuMHYKuxUxVf.0fo6FLDt1rwTt.e0shda"  # spellchecker:disable-line
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a new user in the database.

    Creates a user record with a securely hashed password. The password
    from user_create is never stored directly.

    Preconditions:
        - session: Active database session (not closed/rolled back)
        - user_create.email: Valid email format, 1-255 characters
        - user_create.password: 8-128 characters, meets security requirements
        - Email must be unique (no existing user with same email)

    Postconditions:
        - Returns User with auto-generated UUID id
        - User.hashed_password is an Argon2id hash of user_create.password
        - User.is_active == True (default)
        - User.is_superuser == False (default, unless specified)
        - User exists in database (committed)

    Invariants:
        - User.id is immutable after creation
        - User.email can be updated but must remain unique
        - Original password is never stored (only hash)

    Args:
        session: Database session for query execution.
        user_create: User creation data including email and password.

    Returns:
        The created User object with generated UUID and timestamps.

    Raises:
        IntegrityError: If email already exists in database.
        ValidationError: If user_create fails Pydantic validation.

    Example:
        >>> from app.models import UserCreate
        >>> user_data = UserCreate(
        ...     email="newuser@example.com",
        ...     password="SecureP@ss123",
        ...     full_name="John Doe"
        ... )
        >>> user = create_user(session=session, user_create=user_data)
        >>> assert user.id is not None
        >>> assert user.email == "newuser@example.com"
    """
    db_obj = User.model_validate(
        user_create,
        update={
            "hashed_password": get_password_hash(user_create.password),
            "email": user_create.email.lower(),
        },
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update an existing user's information.

    Updates user fields from user_in. Only fields explicitly set in user_in
    are updated (partial update). If password is included, it is securely hashed.

    Preconditions:
        - session: Active database session (not closed/rolled back)
        - db_user: Valid User object that exists in database
        - user_in.email (if provided): Valid email, unique across users
        - user_in.password (if provided): 8-128 characters

    Postconditions:
        - Only fields explicitly set in user_in are modified
        - If password provided: User.hashed_password updated to new hash
        - User.id remains unchanged
        - Changes are committed to database
        - Returns refreshed User with latest database state

    Invariants:
        - User.id is immutable
        - Password is never stored in plain text
        - Unset fields in user_in remain unchanged

    Args:
        session: Database session for query execution.
        db_user: Existing User object to update.
        user_in: Update data with fields to modify.

    Returns:
        The updated User object with refreshed data from database.

    Raises:
        IntegrityError: If updated email conflicts with existing user.
        ValidationError: If user_in fails Pydantic validation.

    Example:
        >>> from app.models import UserUpdate
        >>> update_data = UserUpdate(full_name="Jane Doe")
        >>> updated_user = update_user(
        ...     session=session,
        ...     db_user=existing_user,
        ...     user_in=update_data
        ... )
        >>> assert updated_user.full_name == "Jane Doe"
        >>> assert updated_user.id == existing_user.id  # ID unchanged
    """
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Retrieve a user by their email address.

    Performs a case-insensitive email lookup. Returns None if no user
    is found with the given email.

    Preconditions:
        - session: Active database session (not closed/rolled back)
        - email: Non-empty string (case-insensitive matching)

    Postconditions:
        - If user exists with case-insensitive email match: Returns User object
        - If no user found: Returns None
        - Database state is unchanged (read-only operation)

    Invariants:
        - Email matching is case-insensitive (lowercased before lookup)
        - No side effects on database

    Args:
        session: Database session for query execution.
        email: Email address to search for.

    Returns:
        User object if found, None otherwise.

    Raises:
        No exceptions raised for normal operation.
        SQLAlchemyError: If database connection fails.

    Example:
        >>> user = get_user_by_email(session=session, email="user@example.com")
        >>> if user:
        ...     print(f"Found user: {user.full_name}")
        ... else:
        ...     print("User not found")
    """
    statement = select(User).where(User.email == email.lower())
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """Authenticate a user by email and password.

    Looks up user by email and verifies the password hash. Returns None
    if email is not found or password doesn't match.

    Preconditions:
        - session: Active database session (not closed/rolled back)
        - email: Non-empty string
        - password: Non-empty string (plain-text)

    Postconditions:
        - If email exists AND password matches hash: Returns User object
        - If email not found OR password mismatch: Returns None
        - Database state is unchanged (read-only operation)
        - No information leakage about which condition failed

    Invariants:
        - Password comparison is constant-time (prevents timing attacks)
        - Plain-text password is never logged or stored
        - User.is_active status is NOT checked (caller responsibility)

    Args:
        session: Database session for query execution.
        email: User's email address.
        password: Plain-text password to verify.

    Returns:
        User object if authentication succeeds, None otherwise.

    Raises:
        No exceptions raised for authentication failure (returns None).
        SQLAlchemyError: If database connection fails.

    Example:
        >>> user = authenticate(
        ...     session=session,
        ...     email="user@example.com",
        ...     password="userpassword"
        ... )
        >>> if user:
        ...     if user.is_active:
        ...         print("Login successful")
        ...     else:
        ...         print("Account is disabled")
        ... else:
        ...     print("Invalid credentials")
    """
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        # Unknown users perform both supported hash algorithms so their timing
        # matches invalid attempts against current and legacy accounts.
        verify_password(password, DUMMY_ARGON2_PASSWORD_HASH)
        verify_password(password, DUMMY_BCRYPT_PASSWORD_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        # The real hash already performed one algorithm. Run the other one so
        # every failed authentication performs one Argon2 and one bcrypt check.
        complementary_hash = (
            DUMMY_ARGON2_PASSWORD_HASH
            if db_user.hashed_password.startswith(("$2a$", "$2b$", "$2y$"))
            else DUMMY_BCRYPT_PASSWORD_HASH
        )
        verify_password(password, complementary_hash)
        return None
    if updated_password_hash is not None:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """Create a new item owned by the specified user.

    Creates an item record with the provided data and assigns ownership
    to the specified user ID.

    Preconditions:
        - session: Active database session (not closed/rolled back)
        - item_in.title: 1-255 characters, non-empty after whitespace strip
        - item_in.description: Optional, max 1000 characters if provided
        - owner_id: Valid UUID referencing an existing, active user

    Postconditions:
        - Returns Item with auto-generated UUID id
        - Item.owner_id == owner_id
        - Item.title == item_in.title (whitespace stripped)
        - Item exists in database (committed)
        - Item.id is unique across all items

    Invariants:
        - Item.id is immutable after creation
        - Item.owner_id is immutable after creation
        - Item always has exactly one owner

    Args:
        session: Database session for query execution.
        item_in: Item creation data (title, description, content_type, etc.).
        owner_id: UUID of the user who will own this item.

    Returns:
        The created Item object with generated UUID and timestamps.

    Raises:
        IntegrityError: If owner_id doesn't reference valid user (FK constraint).
        ValidationError: If item_in fails Pydantic validation.

    Example:
        >>> from app.models import ItemCreate
        >>> item_data = ItemCreate(
        ...     title="Meeting Notes",
        ...     description="Q4 planning meeting notes"
        ... )
        >>> item = create_item(
        ...     session=session,
        ...     item_in=item_data,
        ...     owner_id=current_user.id
        ... )
        >>> assert item.id is not None
        >>> assert item.owner_id == current_user.id
    """
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
