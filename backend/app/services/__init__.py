"""
FastAPI-shell services that compose public package and infrastructure APIs.

Reusable education behavior stays in the ``txt2crs`` package. Shell services
own only application lifecycle, HTTP-facing coordination, and safe translation
at the documented package boundary.
"""

from app.services.txt2crs_application import (
    Txt2CrsApplicationLifecycle,
    build_execution_profile,
)
from app.services.txt2crs_authentication import (
    SystemAuthenticationBusyError,
    SystemAuthenticationCoordinator,
    SystemAuthenticationFailureCode,
)
from app.services.txt2crs_readiness import (
    CachedReadinessCoordinator,
    ReadinessCheckState,
    ReadinessSnapshot,
    ReadinessStatus,
)
from app.services.txt2crs_runtime import (
    RuntimeOwner,
    RuntimeOwnershipCoordinator,
    RuntimeOwnershipSnapshot,
)
from app.services.txt2crs_submission import Txt2CrsSubmissionService
from app.services.txt2crs_worker import (
    SerialTxt2CrsWorker,
    WorkerFailureCode,
    WorkerSnapshot,
    WorkerStatus,
)

__all__ = [
    "CachedReadinessCoordinator",
    "ReadinessCheckState",
    "ReadinessSnapshot",
    "ReadinessStatus",
    "RuntimeOwner",
    "RuntimeOwnershipCoordinator",
    "RuntimeOwnershipSnapshot",
    "SerialTxt2CrsWorker",
    "SystemAuthenticationBusyError",
    "SystemAuthenticationCoordinator",
    "SystemAuthenticationFailureCode",
    "Txt2CrsApplicationLifecycle",
    "Txt2CrsSubmissionService",
    "WorkerFailureCode",
    "WorkerSnapshot",
    "WorkerStatus",
    "build_execution_profile",
]
