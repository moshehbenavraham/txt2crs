# SPDX-License-Identifier: MIT-0

"""Public package metadata for the txt2crs course-generation library.

The functional modules are intentionally introduced test-first. Keeping this
top-level module small also prevents importing optional AI, research, or
persistence dependencies when a caller only needs package metadata.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version

try:
    # Reading the installed distribution metadata gives editable installs,
    # wheels, and source installations one authoritative Python version.
    __version__ = distribution_version("txt2crs")
except PackageNotFoundError:
    # This fallback supports direct source-tree inspection before installation.
    # Normal development, testing, and production paths install the package.
    __version__ = "0+unknown"

__all__ = ["__version__"]
