#!/usr/bin/env bash
# Start the API with the port configured in .env (loaded by api.config).
# Extra arguments are forwarded to uvicorn (e.g. --reload).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ -x .venv/bin/python ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi

PORT="$("$PY" -c 'from api import config; print(config.API_PORT)')"
exec "$PY" -m uvicorn api.main:app --port "$PORT" "$@"
