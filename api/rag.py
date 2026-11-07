"""Vector RAG over the local knowledge base: ChromaDB + Ollama (backwards-compatibility facade).

Re-exports core RAG components and constants from ``app.services.rag_service``.
"""
from __future__ import annotations

from app.services.rag_service import (
    DEFAULT_SYSTEM_PROMPT,
    EMPTY_CONTEXT,
    LocalVectorRAG,
    PROMPT_PATH,
    RAGService,
    REFUSAL_STRING,
)

__all__ = [
    "DEFAULT_SYSTEM_PROMPT",
    "EMPTY_CONTEXT",
    "LocalVectorRAG",
    "PROMPT_PATH",
    "RAGService",
    "REFUSAL_STRING",
]
