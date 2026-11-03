"""Relational persistence layer for the citizen-service backend.

The ORM models mirror ``db/schema.sql``. They cover tables, columns,
constraints and indexes; the triggers, the ``next_radicado`` function, the
reporting view and the row-level-security policy live only in the SQL script,
because SQLAlchemy cannot express them portably.

Drift guard: ``python scripts/check_schema.py`` compares the mapped metadata
against ``db/schema.sql``.

This package is imported by ``api.main`` only for the PQRSD routes; the RAG
service keeps working without a PostgreSQL server because the engine is
created lazily and an empty ``DATABASE_URL`` returns 503 on the case endpoints.
Install ``sqlalchemy`` and ``psycopg[binary]`` (both in ``api/requirements.txt``)
before using the relational backend.
"""

from api.db.models import Base

__all__ = ["Base"]
