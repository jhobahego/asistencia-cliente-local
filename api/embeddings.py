"""Ollama client wrappers for embeddings (backwards-compatibility facade).

Re-exports OllamaEmbedder and prompt prefix constants from ``app.infrastructure.ollama``.
"""
from __future__ import annotations

from app.infrastructure.ollama import (
    DOCUMENT_PREFIX,
    QUERY_PREFIX,
    OllamaEmbedder,
)

__all__ = [
    "DOCUMENT_PREFIX",
    "OllamaEmbedder",
    "QUERY_PREFIX",
]
