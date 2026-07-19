"""
FastAPI-shell services that compose public package and infrastructure APIs.

Reusable education behavior stays in the ``txt2crs`` package. Shell services
own only application lifecycle, HTTP-facing coordination, and safe translation
at the documented package boundary.
"""

from app.services.txt2crs_application import Txt2CrsApplicationLifecycle

__all__ = ["Txt2CrsApplicationLifecycle"]
