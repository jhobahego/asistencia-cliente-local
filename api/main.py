"""FastAPI service exposing the local vector RAG over Ollama (backwards-compatibility facade).

Re-exports the application instance, endpoints, request/response schemas, and
exception helpers from ``app``.
"""
from __future__ import annotations

from app.api.v1.endpoints.pqrsd import router as pqrsd_router
from app.api.v1.endpoints.rag import (
    _ASK_BODY_EXAMPLES,
    _answer,
    _category,
    _prepare,
    _question,
    ask,
    ask_stream,
    sync_kb,
)
from app.core.exceptions import (
    OLLAMA_UNAVAILABLE,
    database_unreachable_handler as _database_unreachable,
    internal_error_exception as _internal_error,
    ollama_unavailable_exception as _ollama_unavailable,
)
from app.main import app, health, lifespan
from app.schemas.rag import AskRequest, AskResponse, SourceModel
from app.services.rag_service import LocalVectorRAG

__all__ = [
    "AskRequest",
    "AskResponse",
    "LocalVectorRAG",
    "OLLAMA_UNAVAILABLE",
    "SourceModel",
    "_ASK_BODY_EXAMPLES",
    "_answer",
    "_category",
    "_database_unreachable",
    "_internal_error",
    "_ollama_unavailable",
    "_prepare",
    "_question",
    "app",
    "ask",
    "ask_stream",
    "health",
    "lifespan",
    "pqrsd_router",
    "sync_kb",
]
