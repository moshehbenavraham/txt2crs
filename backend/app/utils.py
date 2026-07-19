"""
Email and token utilities for the application.

This module provides utilities for:
- Email rendering and sending via SMTP
- Password reset token generation and verification

Email System:
    - Templates are Jinja2-based HTML files in `app/email-templates/build/`
    - SMTP configuration is read from application settings
    - Supports TLS and SSL connections

Token System:
    - Password reset tokens are JWTs with configurable expiration
    - Tokens contain the user's email and cannot be reused after expiration

Usage:
    from app.utils import send_email, generate_password_reset_token

    # Generate a password reset token
    token = generate_password_reset_token(
        email="user@example.com",
        current_password_hash="<password-hash>",
    )

    # Send an email
    send_email(
        email_to="user@example.com",
        subject="Password Reset",
        html_content="<html>...</html>"
    )

Configuration:
    Email settings are loaded from environment variables via app.core.config:
    - SMTP_HOST, SMTP_PORT, SMTP_TLS, SMTP_SSL
    - SMTP_USER, SMTP_PASSWORD (optional)
    - EMAILS_FROM_NAME, EMAILS_FROM_EMAIL
    - EMAIL_RESET_TOKEN_EXPIRE_HOURS
"""

import hashlib
import hmac
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import jwt
from emails.message import Message
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EmailData:
    """
    Container for email content and metadata.

    Attributes:
        html_content: The rendered HTML body of the email.
        subject: The email subject line.

    Example:
        >>> email = EmailData(
        ...     html_content="<html><body>Hello!</body></html>",
        ...     subject="Welcome to our app"
        ... )
    """

    html_content: str
    subject: str


@dataclass(frozen=True)
class PasswordResetTokenData:
    """
    Parsed and validated password reset token claims.

    Attributes:
        email: Email address encoded in the token subject.
        password_fingerprint: HMAC fingerprint tied to the current password hash.
            This enforces one-time semantics after a successful reset.
    """

    email: str
    password_fingerprint: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    """
    Render an email template with the provided context variables.

    Loads a Jinja2 template from the email-templates/build directory and
    renders it with the given context dictionary.

    Args:
        template_name: The filename of the template (e.g., "reset_password.html").
            Must exist in `app/email-templates/build/`.
        context: Dictionary of variables to pass to the template.

    Returns:
        The rendered HTML content as a string.

    Example:
        >>> html = render_email_template(
        ...     template_name="welcome.html",
        ...     context={"username": "John", "project_name": "MyApp"}
        ... )

    Note:
        Templates should be pre-built HTML files. The build directory typically
        contains compiled versions of source templates.
    """
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = str(Template(template_str).render(context))
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    """
    Send an HTML email via SMTP.

    Sends an email using the configured SMTP server. Supports TLS, SSL,
    and authenticated SMTP connections.

    Args:
        email_to: The recipient's email address.
        subject: The email subject line. Defaults to empty string.
        html_content: The HTML body of the email. Defaults to empty string.

    Raises:
        AssertionError: If email sending is not configured (emails_enabled is False).

    Example:
        >>> send_email(
        ...     email_to="user@example.com",
        ...     subject="Welcome!",
        ...     html_content="<html><body>Welcome to our app!</body></html>"
        ... )

    Note:
        This function blocks until the email is sent. For high-volume email
        sending, consider using a background task queue.

    Configuration Required:
        - SMTP_HOST and SMTP_PORT must be set
        - EMAILS_FROM_NAME and EMAILS_FROM_EMAIL define the sender
        - SMTP_TLS or SMTP_SSL for secure connections
        - SMTP_USER and SMTP_PASSWORD for authenticated SMTP
    """
    assert settings.emails_enabled, "no provided configuration for email variables"
    email_from = settings.EMAILS_FROM_EMAIL
    assert email_from is not None
    message = Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, email_from),
    )
    smtp_options: dict[str, Any] = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "timeout": settings.SMTP_TIMEOUT_SECONDS,
    }
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    message.send(to=email_to, smtp=smtp_options)
    logger.info(
        "external.email_send_completed",
        # SMTP responses can repeat recipient addresses or provider detail.
        # Successful completion is the only globally safe fact needed here.
    )


def send_email_with_retry(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    """
    Send email with bounded retry and backoff.

    This wrapper is safe for background-task dispatch from API request paths:
    delivery failures are logged with telemetry fields and are not re-raised.
    """
    max_attempts = settings.SMTP_MAX_ATTEMPTS
    base_backoff_seconds = settings.SMTP_RETRY_BACKOFF_SECONDS
    overall_started_at = time.perf_counter()

    logger.info(
        "external.email_delivery_started",
        extra={
            "max_attempts": max_attempts,
            "smtp_timeout_seconds": settings.SMTP_TIMEOUT_SECONDS,
        },
    )

    for attempt in range(1, max_attempts + 1):
        attempt_started_at = time.perf_counter()
        try:
            send_email(
                email_to=email_to,
                subject=subject,
                html_content=html_content,
            )
            total_elapsed_ms = int((time.perf_counter() - overall_started_at) * 1000)
            logger.info(
                "external.email_delivery_completed",
                extra={
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "total_elapsed_ms": total_elapsed_ms,
                },
            )
            return
        except Exception:
            attempt_elapsed_ms = int((time.perf_counter() - attempt_started_at) * 1000)
            if attempt < max_attempts:
                backoff_seconds = base_backoff_seconds * (2 ** (attempt - 1))
                logger.warning(
                    "external.email_delivery_retrying",
                    extra={
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "attempt_elapsed_ms": attempt_elapsed_ms,
                        "backoff_seconds": backoff_seconds,
                    },
                )
                if backoff_seconds > 0:
                    time.sleep(backoff_seconds)
                continue

            total_elapsed_ms = int((time.perf_counter() - overall_started_at) * 1000)
            logger.error(
                "external.email_delivery_failed",
                extra={
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "attempt_elapsed_ms": attempt_elapsed_ms,
                    "total_elapsed_ms": total_elapsed_ms,
                },
            )
            return


def generate_test_email(email_to: str) -> EmailData:
    """
    Generate a test email for verifying email configuration.

    Creates a simple test email to verify that the email sending
    infrastructure is working correctly.

    Args:
        email_to: The recipient's email address.

    Returns:
        EmailData containing the rendered test email and subject line.

    Example:
        >>> email_data = generate_test_email("admin@example.com")
        >>> send_email(
        ...     email_to="admin@example.com",
        ...     subject=email_data.subject,
        ...     html_content=email_data.html_content
        ... )
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    """
    Generate a password reset email with a reset link.

    Creates an email containing a time-limited link that allows the user
    to reset their password. The link includes a JWT token for verification.

    Args:
        email_to: The recipient's email address (where to send the email).
        email: The user's email address (used in the subject line and template).
        token: A valid password reset JWT token generated by generate_password_reset_token.

    Returns:
        EmailData containing the rendered password reset email and subject line.

    Example:
        >>> token = generate_password_reset_token(
        ...     email="user@example.com",
        ...     current_password_hash="<password-hash>",
        ... )
        >>> email_data = generate_reset_password_email(
        ...     email_to="user@example.com",
        ...     email="user@example.com",
        ...     token=token
        ... )
        >>> send_email(
        ...     email_to="user@example.com",
        ...     subject=email_data.subject,
        ...     html_content=email_data.html_content
        ... )

    Note:
        The reset link points to {FRONTEND_HOST}/reset-password?token={token}.
        The token validity period is shown in the email template.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def _build_password_reset_fingerprint(*, current_password_hash: str) -> str:
    """
    Build a stable, secret-keyed fingerprint for a password hash.

    The raw password hash is never embedded in reset tokens.
    """
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        current_password_hash.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def generate_password_reset_token(*, email: str, current_password_hash: str) -> str:
    """
    Generate a time-limited JWT token for password reset.

    Creates a signed JWT containing the user's email that can be used
    to verify their identity during password reset. The token includes
    both expiration (exp) and not-before (nbf) claims.

    Tokens include a fingerprint of the user's current password hash.
    After a successful reset updates the password hash, previously issued
    tokens become invalid and cannot be replayed.

    Args:
        email: The email address to encode in the token.

    Returns:
        A signed JWT string valid for EMAIL_RESET_TOKEN_EXPIRE_HOURS hours.

    Example:
        >>> token = generate_password_reset_token(
        ...     email="user@example.com",
        ...     current_password_hash="<password-hash>",
        ... )
        >>> # Token can be included in a password reset URL
        >>> reset_url = f"https://example.com/reset?token={token}"

    Security Notes:
        - Token validity defaults to 24 hours (configurable via settings)
        - The 'nbf' (not before) claim prevents token use before creation time
        - Tokens are signed with the application's SECRET_KEY
        - Password-hash fingerprint enforces one-time semantics after reset
        - Use verify_password_reset_token() to validate and extract token data
    """
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {
            "exp": exp,
            "nbf": now,
            "sub": email,
            "pwd_fingerprint": _build_password_reset_fingerprint(
                current_password_hash=current_password_hash
            ),
        },
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(*, token: str) -> PasswordResetTokenData | None:
    """
    Validate a password reset token and extract the email.

    Decodes and verifies a JWT password reset token, checking that:
    - The signature is valid
    - The token has not expired (exp claim)
    - The token is active (nbf claim has passed)

    Args:
        token: The JWT token string to verify.

    Returns:
        Parsed token claims if valid, or None if the token is invalid,
        expired, malformed, or missing required claims.

    Example:
        >>> token_data = verify_password_reset_token(token=token)
        >>> if token_data:
        ...     user = get_user_by_email(token_data.email)
        ...     # Proceed with password reset
        ... else:
        ...     raise HTTPException(status_code=400, detail="Invalid token")

    Note:
        This function returns None for any token verification failure,
        intentionally not distinguishing between different failure modes
        to avoid leaking information to potential attackers.
    """
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        email = decoded_token.get("sub")
        password_fingerprint = decoded_token.get("pwd_fingerprint")

        if not isinstance(email, str) or not isinstance(password_fingerprint, str):
            return None

        return PasswordResetTokenData(
            email=email,
            password_fingerprint=password_fingerprint,
        )
    except InvalidTokenError:
        return None


def password_reset_token_matches_user(
    *, token_data: PasswordResetTokenData, current_password_hash: str
) -> bool:
    """
    Check whether a reset token is still valid for a user's current password hash.
    """
    expected_fingerprint = _build_password_reset_fingerprint(
        current_password_hash=current_password_hash
    )
    return hmac.compare_digest(token_data.password_fingerprint, expected_fingerprint)
