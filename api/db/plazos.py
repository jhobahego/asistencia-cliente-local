"""Business-day arithmetic for PQRSD deadlines.

The legal terms of Resolucion 369 de 2019 are counted in business days, so
weekends and the ``festivo`` catalog are excluded. The function is pure: the
caller loads the holidays from the database.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta

WEEKEND = frozenset({5, 6})  # Saturday, Sunday in date.weekday()


def add_business_days(start: date, days: int, holidays: Iterable[date] = ()) -> date:
    """Return the date ``days`` business days after ``start``.

    Counting begins the day after ``start``, which matches how a petition
    filed on one day starts its term the following business day.
    """
    if days < 1:
        raise ValueError("days must be at least 1")

    excluded = set(holidays)
    current = start
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() not in WEEKEND and current not in excluded:
            remaining -= 1
    return current


def is_business_day(value: date, holidays: Iterable[date] = ()) -> bool:
    """Whether ``value`` is a weekday that is not in the holiday catalog."""
    return value.weekday() not in WEEKEND and value not in set(holidays)
