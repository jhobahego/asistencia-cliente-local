"""FastAPI dependency that yields a session, or None when the backend is off.

Returning None instead of raising keeps FastAPI's payload validation first:
a malformed body answers 422 even when ``DATABASE_URL`` is empty, and only a
valid request reaches the 503 produced by :func:`require_session`.
"""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.db.engine import DatabaseNotConfigured, get_session_factory

NOT_CONFIGURED_DETAIL = (
    "Relational database is not configured: set DATABASE_URL to enable the "
    "PQRSD case endpoints"
)


def get_db() -> Iterator[Session | None]:
    """Yield a session for the request and always close it afterwards."""
    try:
        factory = get_session_factory()
    except DatabaseNotConfigured:
        yield None
        return

    session = factory()
    try:
        yield session
    finally:
        session.close()


def require_session(session: Session | None) -> Session:
    """Raise 503 when the relational backend was never configured."""
    if session is None:
        raise HTTPException(status_code=503, detail=NOT_CONFIGURED_DETAIL)
    return session
