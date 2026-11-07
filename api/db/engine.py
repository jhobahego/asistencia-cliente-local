"""Engine and session management for the optional PostgreSQL backend (backwards-compatibility facade).

Re-exports database engine utilities from ``app.core.database``.
"""
from __future__ import annotations

from app.core.database import (
    DatabaseNotConfigured,
    NOT_CONFIGURED_DETAIL,
    database_url,
    get_engine,
    get_session_factory,
    ping,
    reset,
    session_scope,
)

__all__ = [
    "DatabaseNotConfigured",
    "NOT_CONFIGURED_DETAIL",
    "database_url",
    "get_engine",
    "get_session_factory",
    "ping",
    "reset",
    "session_scope",
]
