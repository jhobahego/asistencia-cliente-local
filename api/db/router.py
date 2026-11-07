"""HTTP routes for the PQRSD case file (backwards-compatibility facade).

Re-exports router and error handlers from ``app.api.v1.endpoints.pqrsd``.
"""
from __future__ import annotations

from app.api.v1.endpoints.pqrsd import (
    _http_error,
    router,
)

__all__ = [
    "_http_error",
    "router",
]
