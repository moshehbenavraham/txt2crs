"""Common schemas used across API integrations."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Structured error response for API errors.

    Provides consistent error format across all API endpoints.
    """

    error_code: str
    message: str
    details: dict[str, str] | None = None
