"""Ollama embeddings with model-specific input prefixes.

Embeddings are always passed to Chroma explicitly, so this module never
registers a Chroma embedding function and never re-embeds implicitly.
"""
from __future__ import annotations

import ollama

from api import config

DOCUMENT_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "


class OllamaEmbedder:
    """Batch document embeddings and single query embeddings via Ollama."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        batch_size: int | None = None,
    ) -> None:
        self.model = model or config.OLLAMA_EMBED_MODEL
        self.base_url = (base_url or config.OLLAMA_BASE_URL).rstrip("/")
        self.batch_size = (
            batch_size if batch_size is not None else config.EMBED_BATCH_SIZE
        )
        self.batch_size = max(1, self.batch_size)
        # nomic-embed-text is trained with task prefixes; other models are
        # used as-is so the same client keeps working with a swapped model.
        self._uses_prefix = self.model.startswith("nomic-embed-text")
        self._client = ollama.Client(host=self.base_url)
        self._async_client = ollama.AsyncClient(host=self.base_url)

    def _document_input(self, text: str) -> str:
        return f"{DOCUMENT_PREFIX}{text}" if self._uses_prefix else text

    def _query_input(self, text: str) -> str:
        return f"{QUERY_PREFIX}{text}" if self._uses_prefix else text

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed documents in bounded batches, preserving input order."""
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = [
                self._document_input(text)
                for text in texts[start : start + self.batch_size]
            ]
            # truncate=False fails loudly instead of silently cutting input:
            # a truncated chunk would be indexed with the wrong meaning.
            response = self._client.embed(
                model=self.model, input=batch, truncate=False
            )
            vectors.extend(list(embedding) for embedding in response.embeddings)
        return vectors

    async def embed_query(self, text: str) -> list[float]:
        """Embed one search query with the query prefix."""
        response = await self._async_client.embed(
            model=self.model, input=self._query_input(text), truncate=False
        )
        return list(response.embeddings[0])
