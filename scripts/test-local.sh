#!/usr/bin/env bash
# Local sanity checks: Ollama, compose file, API sources.
# Does NOT pull models or start services.
set -euo pipefail

ollama --version
curl -s localhost:11434/api/tags
docker compose config
python3 -m compileall api
