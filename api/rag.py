"""Vector RAG over the local knowledge base: ChromaDB + Ollama.

Retrieval is cosine similarity over persisted embeddings, gated by the
measured hybrid rule so semantically close but unrelated chunks never reach
the model. There is no keyword fallback: an empty gate result means the
refusal path in ``api/system_prompt.txt`` takes over.
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import chromadb
import ollama
from chromadb.config import Settings

from api import config
from api.embeddings import OllamaEmbedder
from api.lexical import lexical_evidence

PROMPT_PATH = Path(__file__).with_name("system_prompt.txt")
EMPTY_CONTEXT = "NO SE ENCONTRÓ INFORMACIÓN RELEVANTE EN LA BASE DE CONOCIMIENTO."


class LocalVectorRAG:
    """Answer questions grounded only on chunks stored in Chroma."""

    def __init__(
        self,
        top_k: int | None = None,
        max_distance: float | None = None,
        strong_distance: float | None = None,
        model: str | None = None,
        embed_model: str | None = None,
        temperature: float | None = None,
        base_url: str | None = None,
        chroma_path: str | Path | None = None,
        collection_name: str | None = None,
        timeout: float | None = None,
        stream_timeout: float | None = None,
    ) -> None:
        self.top_k = max(1, top_k if top_k is not None else config.RAG_TOP_K)
        self.max_distance = (
            max_distance if max_distance is not None else config.RAG_MAX_DISTANCE
        )
        self.strong_distance = (
            strong_distance
            if strong_distance is not None
            else config.RAG_STRONG_DISTANCE
        )
        self.model = model or config.OLLAMA_MODEL
        self.embed_model = embed_model or config.OLLAMA_EMBED_MODEL
        self.temperature = (
            temperature if temperature is not None else config.TEMPERATURE
        )
        self.base_url = (base_url or config.OLLAMA_BASE_URL).rstrip("/")
        path = Path(chroma_path) if chroma_path is not None else config.CHROMA_DB_PATH
        name = collection_name or config.CHROMA_COLLECTION

        self._chroma = chromadb.PersistentClient(
            path=str(path),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._chroma.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
        self._embedder = OllamaEmbedder(model=self.embed_model, base_url=self.base_url)
        # Two clients so each path honors its own timeout: a full answer and
        # a token stream have very different expected durations.
        self._chat_client = ollama.AsyncClient(
            host=self.base_url,
            timeout=timeout if timeout is not None else config.OLLAMA_TIMEOUT,
        )
        self._stream_client = ollama.AsyncClient(
            host=self.base_url,
            timeout=(
                stream_timeout
                if stream_timeout is not None
                else config.OLLAMA_STREAM_TIMEOUT
            ),
        )

    def count(self) -> int:
        """Number of chunks currently stored in the collection."""
        return int(self._collection.count())

    def categories(self) -> list[str]:
        """Distinct, non-empty ``categoria`` values currently indexed."""
        result = self._collection.get(include=["metadatas"])
        metadatas = result.get("metadatas") or []
        return sorted(
            {
                str(metadata["categoria"])
                for metadata in metadatas
                if metadata and metadata.get("categoria")
            }
        )

    async def retrieve_context(
        self, query: str, categoria: str | None = None
    ) -> list[dict[str, Any]]:
        """Return the chunks that pass the hybrid relevance gate."""
        if self.count() == 0:
            return []

        vector = await self._embedder.embed_query(query)
        query_kwargs: dict[str, Any] = {
            "query_embeddings": [vector],
            "n_results": self.top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        # Omit the filter entirely when there is no category: Chroma rejects
        # an empty where clause.
        if categoria:
            query_kwargs["where"] = {"categoria": categoria}

        result = await asyncio.to_thread(self._collection.query, **query_kwargs)
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        chunks: list[dict[str, Any]] = []
        for document, metadata, raw_distance in zip(documents, metadatas, distances):
            if document is None or raw_distance is None:
                continue
            distance = float(raw_distance)
            if distance > self.max_distance:
                continue
            if (
                distance > self.strong_distance
                and lexical_evidence(query, document) <= 0
            ):
                continue
            chunks.append(
                {
                    "content": document,
                    "metadata": dict(metadata or {}),
                    "distance": round(distance, 4),
                }
            )
        return chunks

    def _system_prompt(self) -> str:
        # Read on every call so prompt edits need no service restart.
        return PROMPT_PATH.read_text(encoding="utf-8").strip()

    @staticmethod
    def _format_context(chunks: list[dict[str, Any]]) -> str:
        if not chunks:
            return EMPTY_CONTEXT
        blocks: list[str] = []
        for chunk in chunks:
            metadata = chunk.get("metadata") or {}
            source = metadata.get("source", "desconocido")
            # Source label goes LAST on purpose: with the label first, the 3B
            # model echoed the header instead of answering (measured). The
            # answer comes first, the citation after it.
            label = f"[Fuente: {source}"
            if metadata.get("file_type") == "pdf" and "page" in metadata:
                label += f", página {metadata['page']}"
            label += "]"
            blocks.append(f"{chunk.get('content', '')}\n{label}")
        return "\n\n".join(blocks)

    def build_messages(
        self, user_query: str, chunks: list[dict[str, Any]]
    ) -> list[dict[str, str]]:
        """Build the chat messages with the grounded context block."""
        system = (
            f"{self._system_prompt()}\n\n"
            f"CONTEXT:\n{self._format_context(chunks)}"
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user_query},
        ]

    async def ask(self, query: str, categoria: str | None = None) -> dict[str, Any]:
        """Retrieve context, generate the full answer, return sources."""
        chunks = await self.retrieve_context(query, categoria)
        response = await self._chat_client.chat(
            model=self.model,
            messages=self.build_messages(query, chunks),
            stream=False,
            options={"temperature": self.temperature},
        )
        answer = (response.message.content or "").strip()
        return {"answer": answer, "sources": chunks}

    async def prepare(
        self, query: str, categoria: str | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve context before streaming so errors precede the headers."""
        return await self.retrieve_context(query, categoria)

    async def stream_answer(
        self, query: str, chunks: list[dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """Stream answer tokens for an already retrieved context."""
        stream = await self._stream_client.chat(
            model=self.model,
            messages=self.build_messages(query, chunks),
            stream=True,
            options={"temperature": self.temperature},
        )
        async for part in stream:
            content = part.message.content
            if content:
                yield content

    async def ask_stream(
        self, query: str, categoria: str | None = None
    ) -> AsyncGenerator[str, None]:
        """Convenience wrapper: retrieve the context, then stream tokens."""
        chunks = await self.prepare(query, categoria)
        async for token in self.stream_answer(query, chunks):
            yield token
