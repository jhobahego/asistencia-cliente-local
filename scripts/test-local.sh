#!/usr/bin/env bash
# Local sanity checks: Ollama models, compose file, API sources.
# Does NOT pull models or start services.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ -x .venv/bin/python ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi

MODEL="${OLLAMA_MODEL:-qwen2.5:3b-instruct-q4_K_M}"
EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"

ollama --version

if ! TAGS="$(curl -s localhost:11434/api/tags)"; then
  echo "ERROR: Ollama is not reachable at localhost:11434." >&2
  exit 1
fi

MISSING=0
for model in "$MODEL" "$EMBED_MODEL"; do
  # Ollama reports untagged models as "<name>:latest", so accept both forms.
  if grep -qF "\"$model\"" <<<"$TAGS" || grep -qF "\"$model:" <<<"$TAGS"; then
    echo "OK: model '$model' is available."
  else
    echo "ERROR: model '$model' is missing. Run: bash scripts/pull-models.sh" >&2
    MISSING=1
  fi
done
if [ "$MISSING" -ne 0 ]; then
  exit 1
fi

docker compose config
"$PY" -m compileall -q api

echo "OK: local checks passed."
