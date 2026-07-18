from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def is_rate_limiting_enabled(environment: str) -> bool:
    """Disable rate limiting only for explicit local development."""
    return environment != "local"


# Rate limiter using client IP address
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    enabled=is_rate_limiting_enabled(settings.ENVIRONMENT),
)

# Rate limit strings for different endpoint types
AUTH_RATE_LIMIT = "5/minute"  # Login, password recovery
SIGNUP_RATE_LIMIT = "10/minute"  # User registration
