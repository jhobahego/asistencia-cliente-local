"""Environment-driven configuration for the local vector RAG.

One module owns defaults so the API and the ingestion CLI always agree.
Relative paths resolve against the repository root, which keeps behavior
stable no matter which directory the process starts from. The repository-root
``.env`` file is loaded here with python-dotenv; variables already exported in
the process environment take precedence over it.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# This file lives at <repo_root>/api/config.py.
REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"
load_dotenv(ENV_FILE)


def _env(name: str, default: str) -> str:
    """Return the env value for ``name``, or ``default`` when unset/blank."""
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()


def _env_int(name: str, default: int, minimum: int | None = None) -> int:
    """Parse an integer env var and clamp it to ``minimum`` when given."""
    raw = _env(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc
    if minimum is not None and value < minimum:
        return minimum
    return value


def _env_float(name: str, default: float) -> float:
    """Parse a float env var."""
    raw = _env(name, str(default))
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number, got {raw!r}") from exc


def _resolve_path(name: str, default: str) -> Path:
    """Resolve a possibly relative path against the repository root."""
    path = Path(_env(name, default)).expanduser()
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


API_PORT = _env_int("API_PORT", 8000, minimum=1)

OLLAMA_BASE_URL = _env("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = _env("OLLAMA_MODEL", "qwen2.5:3b-instruct-q4_K_M")
OLLAMA_EMBED_MODEL = _env("OLLAMA_EMBED_MODEL", "nomic-embed-text")
TEMPERATURE = _env_float("TEMPERATURE", 0.2)

# Retrieval gate. Tuned on the real FAQ with nomic-embed-text: a single
# absolute distance threshold cannot separate on-domain from off-domain
# questions, so retrieval also requires lexical evidence unless the match
# is strong.
RAG_TOP_K = _env_int("RAG_TOP_K", 4, minimum=1)
RAG_MAX_DISTANCE = _env_float("RAG_MAX_DISTANCE", 0.50)
RAG_STRONG_DISTANCE = _env_float("RAG_STRONG_DISTANCE", 0.25)

# Hardware budget: one CPU-only generation at a time and small embedding
# batches keep the 7.2 GB machine from swapping.
LLM_CONCURRENCY_LIMIT = _env_int("LLM_CONCURRENCY_LIMIT", 1, minimum=1)
EMBED_BATCH_SIZE = _env_int("EMBED_BATCH_SIZE", 32, minimum=1)

CHROMA_DB_PATH = _resolve_path("CHROMA_DB_PATH", "./chroma_db")
CHROMA_COLLECTION = _env("CHROMA_COLLECTION", "asistencia_cliente_kb")
KNOWLEDGE_BASE_DIR = _resolve_path("KNOWLEDGE_BASE_DIR", "./knowledge_base")

# Optional relational backend (PQRSD case file). Empty means "not configured":
# the RAG service keeps working and the case endpoints answer 503.
DATABASE_URL = _env("DATABASE_URL", "")
DB_POOL_SIZE = _env_int("DB_POOL_SIZE", 5, minimum=1)
DB_POOL_TIMEOUT = _env_int("DB_POOL_TIMEOUT", 10, minimum=1)
DB_CONNECT_TIMEOUT = _env_int("DB_CONNECT_TIMEOUT", 5, minimum=1)
DB_ECHO = _env("DB_ECHO", "false").lower() in {"1", "true", "yes", "on"}

OLLAMA_TIMEOUT = _env_float("OLLAMA_TIMEOUT", 300)
OLLAMA_STREAM_TIMEOUT = _env_float("OLLAMA_STREAM_TIMEOUT", 400)
