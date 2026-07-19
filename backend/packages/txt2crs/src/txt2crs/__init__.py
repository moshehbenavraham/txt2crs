# SPDX-License-Identifier: MIT-0

"""Public package metadata for the txt2crs course-generation library.

The functional modules are intentionally introduced test-first. Keeping this
top-level module small also prevents importing optional AI, research, or
persistence dependencies when a caller only needs package metadata.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version
from typing import Any

try:
    # Reading the installed distribution metadata gives editable installs,
    # wheels, and source installations one authoritative Python version.
    __version__ = distribution_version("txt2crs")
except PackageNotFoundError:
    # This fallback supports direct source-tree inspection before installation.
    # Normal development, testing, and production paths install the package.
    __version__ = "0+unknown"

# These are the three entry points an application shell normally needs.  They
# remain lazy so importing ``txt2crs`` for version metadata does not also load
# optional research, document-processing, or Codex SDK dependencies.
_LAZY_APPLICATION_EXPORT_NAMES = (
    "DeterministicApplicationFactory",
    "RealApplicationFactory",
    "Txt2CrsApplication",
)
_LAZY_APPLICATION_EXPORT_NAME_SET = frozenset(_LAZY_APPLICATION_EXPORT_NAMES)


def __getattr__(attribute_name: str) -> Any:
    """Load application entry points only when a caller first requests one."""

    if attribute_name in _LAZY_APPLICATION_EXPORT_NAME_SET:
        from txt2crs import application

        return getattr(application, attribute_name)
    raise AttributeError(f"module {__name__!r} has no attribute {attribute_name!r}")


def __dir__() -> list[str]:
    """Include lazy public names in interactive discovery and documentation."""

    return sorted({*globals(), *_LAZY_APPLICATION_EXPORT_NAMES})


__all__ = ["__version__", *_LAZY_APPLICATION_EXPORT_NAMES]
