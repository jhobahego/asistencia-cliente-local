# AGENTS.md

Agent and contributor guide for `asistencia-cliente-local`: local-only customer-support prototype (FastAPI RAG over Ollama, no cloud).

## Stack

- **Ollama** — local model runtime (default `qwen2.5:3b-instruct-q4_K_M`).
- **Open WebUI** (`ghcr.io/open-webui/open-webui:main`) — web chat on port 3000.
- **FastAPI** (`api/`) — minimal RAG API answering only from `docs/*.md`.
- **Deps** (`api/requirements.txt`): `fastapi`, `uvicorn`, `pydantic`, `requests`. No vector DB, no dotenv.

## Structure

- `api/main.py` — endpoints (`/health`, `/v1/chat`, `/v1/chat/stream`); env-based config, no dotenv.
- `api/rag.py` — keyword RAG over `docs/*.md` (no embeddings).
- `api/system_prompt.txt` — grounding rules; re-read from disk on each request (no restart needed).
- `docs/faq-ejemplo.md` — answerable knowledge base. `MODELOS.md`, `BENCHMARK.md`, `EVALUACION.md` are meta-docs, excluded from retrieval.
- `scripts/pull-models.sh` — pulls the default model (alternatives commented).
- `scripts/test-local.sh` — sanity checks (Ollama, compose file, `compileall`).
- `docker-compose.yml` — CPU-only `ollama` + `open-webui` services.

## Run commands

```bash
docker compose up -d                    # Ollama + Open WebUI (CPU-only)
bash scripts/pull-models.sh             # default model, once
bash scripts/test-local.sh              # sanity checks
set -a; source .env; set +a             # required: API does not auto-load .env
uvicorn api.main:app --port "${API_PORT:-8000}"
curl localhost:8000/health
```

Windows PowerShell: load `.env` with `Get-Content .env | Where-Object { $_ -match '\S' -and -not $_.TrimStart().StartsWith('#') } | ForEach-Object { $k,$v = $_ -split '=', 2; Set-Item "env:$($k.Trim())" $v.Trim() }`, then `uvicorn api.main:app --port $env:API_PORT`.

## Environment variables

| Variable | Default (`api/main.py`) | Notes |
|----------|-------------------------|-------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen2.5:3b-instruct-q4_K_M` | Chat model |
| `API_PORT` | `8000` | Used only in the uvicorn CLI flag, not read by `api/main.py` |
| `RAG_TOP_K` | `3` | Retrieved doc sections used as context |
| `TEMPERATURE` | `0.2` | Generation temperature |
| `OLLAMA_TIMEOUT` | `120` | Seconds for `POST /v1/chat` (modest CPU-only: 300; NVIDIA: 60–120) |
| `OLLAMA_STREAM_TIMEOUT` | `180` | Seconds for `POST /v1/chat/stream` (modest CPU-only: 400; NVIDIA: 120–180) |

## RAG notes

- Chunking: markdown `##` sections, one chunk keeps heading plus body; chunks under 40 chars are dropped.
- Scoring: accent-insensitive stem overlap with stopwords removed, fuzzy 4+ char prefix match (0.7), and a small Spanish synonym map; best variant wins per query concept so long docs do not inflate scores.
- `EXCLUDED_FILES = {"MODELOS.md", "BENCHMARK.md", "EVALUACION.md"}` — never answerable content.
- Zero overlap on every chunk returns empty context; the caller then triggers the refusal path defined in `api/system_prompt.txt` (`"No tengo esa información en mi base local"`).

## Checks

- `python3 -m compileall api` (or `.venv/bin/python -m compileall api`).
- `bash scripts/test-local.sh` — requires Ollama running and Docker available.
- Docs-only changes have no runnable RED; use structural checks plus visual readback.

## Conventions

- README is Spanish, neutral register; code, comments, and this file are English.
- Keep the service dependency-free: no vector DB, no dotenv, no new packages without need.
- `docker-compose.yml` stays CPU-only; document the NVIDIA `gpus: all` variant in README only.
- Do not commit hardware-specific values (machine names, RAM sizes, tok/s figures) to shared docs; use generic profiles (CPU-only 1B–3.8B, NVIDIA 7B–14B approximate).
