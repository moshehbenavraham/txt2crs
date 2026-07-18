from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from pydantic.networks import EmailStr
from sqlalchemy import text

from app.api.deps import get_current_active_superuser
from app.core.constants import HTTPStatusCode
from app.core.db import engine
from app.core.telemetry import get_service_version
from app.models import Message
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    database: str
    version: str


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    """Legacy health check for backwards compatibility."""
    return True


@router.get("/health/", response_model=HealthCheckResponse)
def health(response: Response) -> HealthCheckResponse:
    """
    Production health check with database connectivity verification.

    Uses a short-lived raw connection instead of a pooled session to avoid
    exhausting the connection pool under heavy monitoring (resolves M-6).
    """
    db_status = "unhealthy"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    overall_status = "healthy" if db_status == "healthy" else "unhealthy"

    if overall_status == "unhealthy":
        response.status_code = HTTPStatusCode.SERVICE_UNAVAILABLE

    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.now(UTC).isoformat(),
        database=db_status,
        version=get_service_version(),
    )
