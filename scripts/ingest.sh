#!/usr/bin/env bash
# Build or update the persistent vector index from knowledge_base/.
# Extra arguments are forwarded to `python -m api.ingest` (e.g. --reset).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ -x .venv/bin/python ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi

exec "$PY" -m api.ingest "$@"
