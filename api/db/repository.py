"""Repository for the PQRSD case file (backwards-compatibility facade).

Re-exports repository classes, exceptions, and constants from ``app.repositories.pqrsd_repository``.
"""
from __future__ import annotations

from app.repositories.pqrsd_repository import (
    HOLIDAY_WINDOW_DAYS,
    Conflict,
    InvalidTransition,
    NotFound,
    PqrsdRepository,
    RepositoryError,
)

__all__ = [
    "HOLIDAY_WINDOW_DAYS",
    "Conflict",
    "InvalidTransition",
    "NotFound",
    "PqrsdRepository",
    "RepositoryError",
]
