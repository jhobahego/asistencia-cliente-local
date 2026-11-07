"""Relational persistence layer for the citizen-service backend (backwards-compatibility facade).

Re-exports Base from ``app.models.pqrsd``.
"""
from __future__ import annotations

from app.models.pqrsd import Base

__all__ = ["Base"]
