"""Authenticated system readiness and privileged ChatGPT setup endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from txt2crs.application import SystemAuthenticationError

from app.api.deps import (
    CurrentUser,
    Txt2CrsAuthenticationDep,
    Txt2CrsReadinessDep,
    get_current_active_superuser,
)
from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.core.rate_limit import (
    SYSTEM_AUTH_START_RATE_LIMIT,
    SYSTEM_AUTH_STATUS_RATE_LIMIT,
    SYSTEM_READINESS_RATE_LIMIT,
    limiter,
)
from app.core.txt2crs_errors import translate_txt2crs_exception
from app.models import User
from app.schemas.system import (
    SystemAuthenticationPublic,
    SystemReadinessPublic,
)
from app.services.txt2crs_authentication import (
    SystemAuthenticationBusyError,
    SystemAuthenticationClosedError,
    SystemAuthenticationUnavailableError,
)

router = APIRouter(prefix="/system", tags=["system"])
logger = get_logger(__name__)

CurrentSuperuser = Annotated[User, Depends(get_current_active_superuser)]


@router.get(
    "/readiness",
    response_model=SystemReadinessPublic,
    summary="Read cached course-system readiness",
    description=(
        "Returns the latest coarse cached system projection. This endpoint "
        "never starts Codex, MCP, provider, database, or artifact probe work."
    ),
)
@limiter.limit(SYSTEM_READINESS_RATE_LIMIT)
def read_system_readiness(
    request: Request,  # noqa: ARG001 - required by slowapi
    current_user: CurrentUser,
    readiness: Txt2CrsReadinessDep,
) -> SystemReadinessPublic:
    """Return only the immutable cache to any active authenticated user."""

    del current_user
    return SystemReadinessPublic.from_snapshot(readiness.snapshot())


@router.post(
    "/auth/start",
    response_model=SystemAuthenticationPublic,
    summary="Start dedicated ChatGPT device authentication",
    description=(
        "Superuser-only. Returns only the validated OpenAI verification URL, "
        "short user code, safe state, and recovery message."
    ),
)
@limiter.limit(SYSTEM_AUTH_START_RATE_LIMIT)
def start_system_authentication(
    request: Request,  # noqa: ARG001 - required by slowapi
    current_superuser: CurrentSuperuser,
    authentication: Txt2CrsAuthenticationDep,
) -> SystemAuthenticationPublic:
    """Start or replay one runtime-exclusive package-owned ceremony."""

    del current_superuser
    translated_error: AppException | None = None
    try:
        snapshot = authentication.start_authentication()
    except SystemAuthenticationBusyError:
        logger.info(
            "system.authentication_rejected",
            extra={"reason_code": "runtime_busy"},
        )
        translated_error = AppException(
            code=ErrorCode.SYSTEM_NOT_READY,
            detail="The provider runtime is busy.",
        )
    except SystemAuthenticationUnavailableError, SystemAuthenticationClosedError:
        logger.info(
            "system.authentication_rejected",
            extra={"reason_code": "service_unavailable"},
        )
        translated_error = AppException(
            code=ErrorCode.SYSTEM_NOT_READY,
            detail="System authentication is unavailable.",
        )
    except Exception as error:
        # The central translator recognizes public package errors and turns
        # unknown failures into a generic internal error without their chain.
        translated_error = translate_txt2crs_exception(error)
        if isinstance(error, SystemAuthenticationError):
            logger.info(
                "system.authentication_failed",
                extra={"reason_code": "package_failed"},
            )
    if translated_error is not None:
        # Raise after leaving the ``except`` scope. Otherwise Python attaches
        # the caught package failure as ``__context__`` even with ``from
        # None``, retaining private provider detail in memory.
        raise translated_error from None

    return SystemAuthenticationPublic.from_snapshot(snapshot)


@router.get(
    "/auth/status",
    response_model=SystemAuthenticationPublic,
    summary="Read cached dedicated ChatGPT authentication status",
    description=(
        "Superuser-only. Reads a shell cache and never refreshes credentials "
        "or starts a second provider runtime."
    ),
)
@limiter.limit(SYSTEM_AUTH_STATUS_RATE_LIMIT)
def read_system_authentication_status(
    request: Request,  # noqa: ARG001 - required by slowapi
    current_superuser: CurrentSuperuser,
    authentication: Txt2CrsAuthenticationDep,
) -> SystemAuthenticationPublic:
    """Return only the coordinator's immutable cached package projection."""

    del current_superuser
    return SystemAuthenticationPublic.from_snapshot(authentication.snapshot())


__all__ = ["router"]
