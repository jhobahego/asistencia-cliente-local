"""FastAPI service exposing the local vector RAG over Ollama.

All endpoints live under ``/api/v1``.
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any

import httpx
import ollama
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import DBAPIError

from api import config
from api.db.router import router as pqrsd_router
from api.rag import LocalVectorRAG

# ollama-python rewrites httpx.ConnectError into the builtin ConnectionError,
# so the builtin type must be part of the "Ollama is unavailable" mapping.
OLLAMA_UNAVAILABLE = (
    httpx.ConnectError,
    httpx.TimeoutException,
    ollama.ResponseError,
    ConnectionError,
)


class AskRequest(BaseModel):
    """Incoming question with an optional category filter."""

    question: str = Field(min_length=1, max_length=2000)
    categoria: str | None = Field(
        default=None,
        description=(
            "Exact match against indexed `categoria` metadata values. "
            "An unknown value returns 422 with the available categories."
        ),
    )


class SourceModel(BaseModel):
    """One grounding fragment returned with the answer."""

    content: str
    metadata: dict[str, Any]
    distance: float


class AskResponse(BaseModel):
    """Grounded answer plus its traceable sources."""

    answer: str
    sources: list[SourceModel]


_ASK_BODY_EXAMPLES = {
    "sin_categoria": {
        "summary": "No category filter",
        "description": (
            "Omit categoria unless you know the exact indexed value; "
            "an unknown value is rejected with 422."
        ),
        "value": {"question": "¿Cuál es el horario de atención?"},
    }
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create the vector RAG and the generation semaphore once per process."""
    app.state.rag = LocalVectorRAG()
    app.state.semaphore = asyncio.Semaphore(config.LLM_CONCURRENCY_LIMIT)
    yield


app = FastAPI(title="asistencia-cliente-local", lifespan=lifespan)
app.include_router(pqrsd_router)


@app.exception_handler(DBAPIError)
async def _database_unreachable(request: Request, exc: DBAPIError) -> JSONResponse:
    """A configured but unreachable database degrades to 503, never 500."""
    return JSONResponse(
        status_code=503,
        content={"detail": "Relational database is unreachable"},
    )


def _question(payload: AskRequest) -> str:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="question must not be blank")
    return question


async def _category(rag: LocalVectorRAG, categoria: str | None) -> str | None:
    """Normalize and validate the optional exact-match category filter."""
    if categoria is None:
        return None
    value = categoria.strip()
    if not value:
        return None
    available = await asyncio.to_thread(rag.categories)
    if value not in available:
        raise HTTPException(
            status_code=422,
            detail={
                "message": f"Unknown categoria: {value!r}",
                "available_categories": available,
            },
        )
    return value


def _ollama_unavailable() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail=f"Ollama unavailable at {config.OLLAMA_BASE_URL}",
    )


def _internal_error() -> HTTPException:
    return HTTPException(
        status_code=500,
        detail="Internal error while answering the question",
    )


async def _answer(
    rag: LocalVectorRAG,
    semaphore: asyncio.Semaphore,
    question: str,
    categoria: str | None,
) -> dict[str, Any]:
    # Concurrency 1 on this hardware: the semaphore covers retrieval and
    # generation so a second request never competes for RAM.
    try:
        async with semaphore:
            return await rag.ask(question, categoria)
    except OLLAMA_UNAVAILABLE as exc:
        raise _ollama_unavailable() from exc
    except Exception as exc:
        raise _internal_error() from exc


async def _prepare(
    rag: LocalVectorRAG, question: str, categoria: str | None
) -> list[dict[str, Any]]:
    try:
        return await rag.prepare(question, categoria)
    except OLLAMA_UNAVAILABLE as exc:
        raise _ollama_unavailable() from exc
    except Exception as exc:
        raise _internal_error() from exc


@app.get("/health")
def health(request: Request) -> dict[str, Any]:
    """Liveness probe; never calls Ollama."""
    rag: LocalVectorRAG = request.app.state.rag
    return {
        "status": "ok",
        "model": rag.model,
        "embedding_model": rag.embed_model,
        "kb_chunks": rag.count(),
    }


@app.post("/api/v1/ask", response_model=AskResponse)
async def ask(
    request: Request,
    payload: Annotated[AskRequest, Body(openapi_examples=_ASK_BODY_EXAMPLES)],
) -> AskResponse:
    """Answer a question grounded on the local knowledge base."""
    rag: LocalVectorRAG = request.app.state.rag
    question = _question(payload)
    categoria = await _category(rag, payload.categoria)
    result = await _answer(
        rag,
        request.app.state.semaphore,
        question,
        categoria,
    )
    return AskResponse(**result)


@app.post("/api/v1/ask/stream")
async def ask_stream(
    request: Request,
    payload: Annotated[AskRequest, Body(openapi_examples=_ASK_BODY_EXAMPLES)],
) -> StreamingResponse:
    """Stream answer tokens as plain text.

    Retrieval runs before the response starts so failures still map to a
    proper HTTP status; only generation errors appear inside the stream.
    """
    rag: LocalVectorRAG = request.app.state.rag
    semaphore: asyncio.Semaphore = request.app.state.semaphore
    question = _question(payload)
    categoria = await _category(rag, payload.categoria)
    chunks = await _prepare(rag, question, categoria)

    async def tokens() -> AsyncIterator[str]:
        try:
            async with semaphore:
                async for token in rag.stream_answer(question, chunks):
                    yield token
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # headers are already sent, so mark the body
            yield f"\n[stream error: {exc}]"

    return StreamingResponse(tokens(), media_type="text/plain; charset=utf-8")


@app.post("/api/v1/sync-kb")
async def sync_kb() -> dict[str, Any]:
    """Re-index the knowledge base in a worker thread."""
    # Lazy import keeps the heavy ingestion stack out of API startup.
    from api.ingest import build_or_update_vector_db

    try:
        stats = await asyncio.to_thread(build_or_update_vector_db)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Knowledge base sync failed"
        ) from exc
    return {"status": "ok", **stats}
