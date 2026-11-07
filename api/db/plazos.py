"""Business-day arithmetic for PQRSD deadlines and statutory terms (backwards-compatibility facade).

Re-exports deadline computation helpers from ``app.domain.plazos``.
"""
from __future__ import annotations

from app.domain.plazos import (
    WEEKEND,
    add_business_days,
    is_business_day,
)

__all__ = [
    "WEEKEND",
    "add_business_days",
    "is_business_day",
]
