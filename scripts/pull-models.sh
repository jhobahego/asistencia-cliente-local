#!/usr/bin/env bash
# Pull the chat and embedding models used by the local RAG.
# CPU-only machine (7.2 GB RAM): small Q4_K_M chat models, no ROCm / CUDA.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ -x .venv/bin/python ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi

MODEL="$("$PY" -c 'from api import config; print(config.OLLAMA_MODEL)')"
EMBED_MODEL="$("$PY" -c 'from api import config; print(config.OLLAMA_EMBED_MODEL)')"

# Chat: best balance of Spanish quality vs RAM on this hardware.
ollama pull "$MODEL"

# Embeddings: 768 dims, ~274 MB, CPU-friendly. Do not switch to bge-m3
# (1.2 GB) or an 8B model on this 7 GB CPU-only machine.
ollama pull "$EMBED_MODEL"

# Chat alternatives (uncomment the one you want to try):
# ollama pull llama3.2:3b          # solid generalist fallback, similar size
# ollama pull phi4-mini            # strong reasoning, 3.8B needs more free RAM
# ollama pull gemma3:1b            # fastest fallback when the machine struggles
