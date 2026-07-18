"""
Security utilities for authentication and password management.

This module provides core security functions including:
- JWT access token generation and encoding
- Password hashing using Argon2
- Password verification against current Argon2 and existing bcrypt hashes

Security Implementation Details:
    - JWT Algorithm: HS256 (HMAC with SHA-256)
    - Password Hashing: Argon2id with automatic salt generation
    - Token Claims: 'sub' (subject/user ID), 'exp' (expiration timestamp)

Usage:
    from app.core.security import create_access_token, verify_password, get_password_hash

    # Generate a token
    token = create_access_token(user.id, timedelta(hours=24))

    # Hash a password
    hashed = get_password_hash("user_password")

    # Verify a password and detect whether its hash should be upgraded
    is_valid, upgraded_hash = verify_password("user_input", hashed)

Note:
    The SECRET_KEY used for JWT encoding must be kept secure and should
    be at least 32 characters of random data. It is loaded from settings.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings

# New passwords use Argon2id. Bcrypt remains available for verifying hashes
# created before the passlib-to-pwdlib migration.
password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))

# JWT signing algorithm - HS256 provides a good balance of security and performance
ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """
    Generate a JWT access token for authentication.

    Creates a signed JWT containing the subject (typically user ID) and
    expiration time. The token is signed using the application's secret key
    with the HS256 algorithm.

    Args:
        subject: The subject to encode in the token, typically the user's ID.
            Will be converted to string before encoding.
        expires_delta: The duration until the token expires. For example,
            `timedelta(minutes=30)` creates a token valid for 30 minutes.

    Returns:
        A signed JWT string that can be used for Bearer authentication.

    Example:
        >>> from datetime import timedelta
        >>> token = create_access_token(user.id, timedelta(hours=8))
        >>> # Use token in Authorization header: "Bearer {token}"

    Note:
        The token contains 'exp' (expiration) and 'sub' (subject) claims.
        Additional claims can be added by modifying the to_encode dict.
    """
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    """
    Verify a plain text password against a hashed password.

    Uses the configured hash implementation's constant-time comparison.
    Accepts current Argon2id hashes and existing bcrypt hashes.

    Args:
        plain_password: The plain text password to verify (user input).
        hashed_password: The password hash from the database.

    Returns:
        A tuple containing whether the password matches and an upgraded hash
        when the stored hash uses a legacy or outdated algorithm.

    Example:
        >>> hashed = get_password_hash("mysecretpassword")
        >>> verified, updated_hash = verify_password("mysecretpassword", hashed)
        >>> verified
        True
        >>> updated_hash is None
        True

    Security Note:
        This function is constant-time to prevent timing attacks that could
        reveal information about the password length or content.
    """
    return password_hash.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using Argon2id.

    Generates a secure hash of the password suitable for storage in the
    database. Each call generates a unique salt, so hashing the same
    password twice produces different hashes.

    Args:
        password: The plain text password to hash.

    Returns:
        An Argon2id hash string containing the algorithm parameters, salt,
        and hash.

    Example:
        >>> hashed = get_password_hash("mysecretpassword")
        >>> hashed.startswith("$argon2id$")
        True

    Security Note:
        - Uses pwdlib's recommended Argon2id parameters and a random salt
        - The memory and time costs make brute-force attacks expensive
        - Never store plain text passwords; always use this function
    """
    return password_hash.hash(password)
