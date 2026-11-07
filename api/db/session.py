"""Database session dependency for FastAPI endpoints (backwards-compatibility facade).

Re-exports session dependencies and helpers from ``app.core.database``.
"""
from __future__ import annotations

from app.core.database import (
    NOT_CONFIGURED_DETAIL,
    get_db,
    require_session,
)

__all__ = [
    "NOT_CONFIGURED_DETAIL",
    "get_db",
    "require_session",
]
