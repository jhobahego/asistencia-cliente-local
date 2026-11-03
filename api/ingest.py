"""Build or update the persistent ChromaDB collection from ``knowledge_base/``.

Run as ``python -m api.ingest [--reset]``. The run is idempotent: chunk IDs
are deterministic, so re-indexing the same files rewrites the same rows and
stale chunks (edited or deleted sources) are pruned.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from pypdf import PdfReader

from api import config
from api.embeddings import OllamaEmbedder

MARKDOWN_HEADERS = [("#", "categoria"), ("##", "seccion"), ("###", "pregunta")]
MARKDOWN_SEPARATORS = ["\n\n", "\n", ".", " ", ""]
MIN_CHUNK_CHARS = 40
SUPPORTED_SUFFIXES = {".md", ".pdf"}


@dataclass(frozen=True)
class Chunk:
    """One indexed fragment with its deterministic ID and metadata."""

    id: str
    content: str
    metadata: dict[str, str | int]


def generate_chunk_id(source: str, index: int, content: str) -> str:
    """Build a stable chunk ID from the source, position and content."""
    digest = hashlib.md5(content.encode("utf-8")).hexdigest()[:8]
    return f"{source}_chunk_{index}_{digest}"


def _knowledge_base_files() -> list[Path]:
    """Every ``.md``/``.pdf`` file under the knowledge base, sorted."""
    root = config.KNOWLEDGE_BASE_DIR
    if not root.is_dir():
        return []
    return sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def _markdown_chunks(path: Path, source: str) -> list[Chunk]:
    """Split Markdown by headers first, then by size, keeping the headers."""
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=MARKDOWN_HEADERS, strip_headers=False
    )
    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=MARKDOWN_SEPARATORS,
    )
    chunks: list[Chunk] = []
    index = 0
    for document in header_splitter.split_text(path.read_text(encoding="utf-8")):
        for piece in size_splitter.split_text(document.page_content):
            content = piece.strip()
            if len(content) < MIN_CHUNK_CHARS:
                continue
            metadata: dict[str, str | int] = {
                "source": source,
                "file_type": "markdown",
                "categoria": str(document.metadata.get("categoria", "General")),
                "seccion": str(document.metadata.get("seccion", "N/A")),
                "pregunta": str(document.metadata.get("pregunta", "N/A")),
            }
            chunks.append(
                Chunk(generate_chunk_id(source, index, content), content, metadata)
            )
            index += 1
    return chunks


def _pdf_chunks(path: Path, source: str) -> list[Chunk]:
    """Split a PDF page by page, keeping the page number in metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=180,
        separators=MARKDOWN_SEPARATORS,
    )
    chunks: list[Chunk] = []
    index = 0
    reader = PdfReader(str(path))
    for page_number, page in enumerate(reader.pages, start=1):
        for piece in splitter.split_text(page.extract_text() or ""):
            content = piece.strip()
            if len(content) < MIN_CHUNK_CHARS:
                continue
            metadata: dict[str, str | int] = {
                "source": source,
                "file_type": "pdf",
                "page": page_number,
                "categoria": "Documento PDF",
            }
            chunks.append(
                Chunk(generate_chunk_id(source, index, content), content, metadata)
            )
            index += 1
    return chunks


def _chunks_for_file(path: Path, source: str) -> list[Chunk]:
    if path.suffix.lower() == ".pdf":
        return _pdf_chunks(path, source)
    return _markdown_chunks(path, source)


def _create_client() -> chromadb.ClientAPI:
    """Open the persistent Chroma client with telemetry disabled."""
    config.CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(config.CHROMA_DB_PATH),
        settings=Settings(anonymized_telemetry=False),
    )


def _get_collection(
    client: chromadb.ClientAPI, reset: bool
) -> chromadb.Collection:
    """Return the collection, recreating it when ``reset`` is requested."""
    if reset:
        existing = {collection.name for collection in client.list_collections()}
        if config.CHROMA_COLLECTION in existing:
            client.delete_collection(config.CHROMA_COLLECTION)
    return client.get_or_create_collection(
        name=config.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def _delete_orphan_sources(
    collection: chromadb.Collection, known_sources: set[str]
) -> None:
    """Drop chunks whose source file no longer exists in the knowledge base."""
    if collection.count() == 0:
        return
    rows = collection.get(include=["metadatas"])
    metadatas = rows.get("metadatas") or []
    orphan_ids = [
        chunk_id
        for chunk_id, metadata in zip(rows["ids"], metadatas)
        if (metadata or {}).get("source") not in known_sources
    ]
    if orphan_ids:
        collection.delete(ids=orphan_ids)


def build_or_update_vector_db(reset: bool = False) -> dict:
    """Index ``knowledge_base/`` into Chroma and return run statistics."""
    client = _create_client()
    collection = _get_collection(client, reset)
    embedder = OllamaEmbedder()

    files_indexed = 0
    chunks_indexed = 0
    known_sources: set[str] = set()

    for path in _knowledge_base_files():
        source = path.relative_to(config.KNOWLEDGE_BASE_DIR).as_posix()
        known_sources.add(source)
        chunks = _chunks_for_file(path, source)
        if not chunks:
            continue

        wanted_ids = {chunk.id for chunk in chunks}
        existing_ids = collection.get(where={"source": source}, include=[])["ids"]
        stale_ids = [
            chunk_id for chunk_id in existing_ids if chunk_id not in wanted_ids
        ]
        if stale_ids:
            collection.delete(ids=stale_ids)

        # Bounded batches: 32 short chunks is the CPU/RAM sweet spot here.
        for start in range(0, len(chunks), config.EMBED_BATCH_SIZE):
            batch = chunks[start : start + config.EMBED_BATCH_SIZE]
            collection.upsert(
                ids=[chunk.id for chunk in batch],
                embeddings=embedder.embed_documents(
                    [chunk.content for chunk in batch]
                ),
                documents=[chunk.content for chunk in batch],
                metadatas=[chunk.metadata for chunk in batch],
            )

        files_indexed += 1
        chunks_indexed += len(chunks)

    _delete_orphan_sources(collection, known_sources)

    return {
        "files_indexed": files_indexed,
        "chunks_indexed": chunks_indexed,
        "collection_count": collection.count(),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: index the knowledge base and print one JSON line."""
    parser = argparse.ArgumentParser(
        description="Index knowledge_base/ into the local ChromaDB collection."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="delete and recreate the collection before indexing",
    )
    args = parser.parse_args(argv)

    stats = build_or_update_vector_db(reset=args.reset)
    if stats["files_indexed"] == 0:
        print(
            "WARNING: no indexable .md/.pdf content found in "
            f"{config.KNOWLEDGE_BASE_DIR}; the collection is empty.",
            file=sys.stderr,
        )
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
