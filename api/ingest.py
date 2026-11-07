"""Build or update the persistent ChromaDB collection from ``knowledge_base/`` (backwards-compatibility facade).

Re-exports ingestion routines, splitters, and CLI entry points from ``app.services.ingest_service``.
"""
from __future__ import annotations

from app.services.ingest_service import (
    MARKDOWN_HEADERS,
    MARKDOWN_SEPARATORS,
    MIN_CHUNK_CHARS,
    SUPPORTED_SUFFIXES,
    Chunk,
    IngestService,
    _chunks_for_file,
    _delete_orphan_sources,
    _knowledge_base_files,
    _markdown_chunks,
    _pdf_chunks,
    build_or_update_vector_db,
    generate_chunk_id,
    main,
)

__all__ = [
    "MARKDOWN_HEADERS",
    "MARKDOWN_SEPARATORS",
    "MIN_CHUNK_CHARS",
    "SUPPORTED_SUFFIXES",
    "Chunk",
    "IngestService",
    "_chunks_for_file",
    "_delete_orphan_sources",
    "_knowledge_base_files",
    "_markdown_chunks",
    "_pdf_chunks",
    "build_or_update_vector_db",
    "generate_chunk_id",
    "main",
]

if __name__ == "__main__":
    raise SystemExit(main())
