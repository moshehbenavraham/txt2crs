# SPDX-License-Identifier: MIT-0

"""Public framework-independent application composition boundary."""

from txt2crs.application.config import (
    ApplicationAdmissionConfig,
    ApplicationStorageConfig,
    DeterministicApplicationConfig,
    DeterministicGenerationScenario,
    DeterministicTurn,
    RealApplicationConfig,
)
from txt2crs.application.facade import (
    ApplicationClosedError,
    ApplicationCloseError,
    ApplicationExecutor,
    ExecutorAlreadyUsedError,
    Txt2CrsApplication,
)
from txt2crs.application.factories import (
    ApplicationFactory,
    DeterministicApplicationFactory,
    RealApplicationFactory,
)
from txt2crs.application.owner_lifecycle import (
    OwnerPurgeCoordinator,
    OwnerPurgeError,
    OwnerPurgeResult,
)
from txt2crs.application.readiness import (
    AggregateApplicationReadinessInspector,
    ApplicationReadiness,
    ApplicationReadinessChecks,
    ApplicationReadinessCheckState,
    ApplicationReadinessStatus,
)

__all__ = [
    "ApplicationAdmissionConfig",
    "ApplicationCloseError",
    "ApplicationClosedError",
    "ApplicationExecutor",
    "ApplicationFactory",
    "ApplicationReadiness",
    "ApplicationReadinessChecks",
    "ApplicationReadinessCheckState",
    "ApplicationReadinessStatus",
    "ApplicationStorageConfig",
    "AggregateApplicationReadinessInspector",
    "DeterministicApplicationConfig",
    "DeterministicApplicationFactory",
    "DeterministicGenerationScenario",
    "DeterministicTurn",
    "ExecutorAlreadyUsedError",
    "OwnerPurgeCoordinator",
    "OwnerPurgeError",
    "OwnerPurgeResult",
    "RealApplicationConfig",
    "RealApplicationFactory",
    "Txt2CrsApplication",
]
