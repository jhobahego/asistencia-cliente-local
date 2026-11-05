# Feature: Cross-platform dev CLI

## Objective

Replace the six platform-specific helper scripts under `scripts/` with one
cross-platform Python CLI, and document its subcommands in the README
quickstarts so a Linux, macOS, or Windows user runs the same commands.

## Problem

- `scripts/` currently holds five bash scripts plus a duplicated PowerShell
  launcher (`run-api.sh` / `run-api.ps1`). Windows users cannot run the bash
  scripts without WSL or Git Bash.
- The README duplicates two quickstarts and relies on platform-specific
  commands (`cp`, `Copy-Item`, `bash`, `.\scripts\...ps1`).
- Every duplicated script re-implements Python/venv discovery, so behavior
  drifts across platforms.

## Scope

- Add `scripts/dev.py`, a stdlib-only entrypoint with subcommands: `setup`,
  `models`, `ingest`, `api`, `smoke`, `check`.
- Remove `scripts/ingest.sh`, `scripts/pull-models.sh`, `scripts/run-api.sh`,
  `scripts/run-api.ps1`, `scripts/smoke-test.sh`, `scripts/test-local.sh`.
- Update `README.md` quickstarts and operations to use the single CLI.
- Update `AGENTS.md` repository map, setup, and verification protocol.
- No changes to `api/` runtime behavior or the HTTP contract.

## Route

Delegated direct: one bounded writer for `scripts/dev.py`, README, and
AGENTS.md (2+ non-trivial files). Parent verifies and commits one work unit.

## Tasks

- [x] S1 Add `scripts/dev.py` with the six subcommands.
- [x] S2 Delete the five bash scripts and the PowerShell launcher.
- [x] S3 Rewrite README quickstarts, add a scripts reference table, and update
      all script references.
- [x] S4 Update AGENTS.md repository map, setup, and verification sections.
- [x] S5 Verify: compileall, `--help`, `check`, and one idempotent `ingest`.

## CLI contract

| Command | Behavior |
|---|---|
| `setup` | Create `.venv` when missing, install `api/requirements.txt`, copy `.env.example` to `.env` when missing. |
| `models` | Pull `OLLAMA_MODEL` and `OLLAMA_EMBED_MODEL` via the `ollama` Python client using `OLLAMA_BASE_URL`. |
| `ingest [--reset]` | Run `python -m api.ingest`; forward extra arguments. |
| `api [--host] [--port] [--reload]` | Run `uvicorn api.main:app` on `API_PORT` by default; forward extra arguments. |
| `smoke [--url]` | HTTP smoke test: health, on-domain, off-domain, stream, unknown category, valid category. |
| `check` | Ollama reachability, configured models, `compileall`, and `docker compose config` when Docker exists. |

Every command except `setup` re-executes the script with the repository
`.venv` interpreter when one exists, so users never need to activate it.

## Delivery strategy

`ask-on-risk` (default). Forecast is ~650 authored changed lines dominated by
deleting the six legacy scripts; no pull request is planned in this task.

## Checks

- `python -m compileall -q scripts api`
- `python scripts/dev.py --help`
- `python scripts/dev.py check` (Ollama 0.40.13 is running)
- `python scripts/dev.py ingest` (idempotent with the current corpus)
- `python scripts/dev.py smoke` only when the API is running.

## Progress

Implemented.

- S1: `scripts/dev.py` provides `setup`, `models`, `ingest`, `api`, `smoke`,
  and `check`; non-setup commands re-execute in `.venv`, and `ingest` / `api`
  forward extra arguments.
- S2: removed `ingest.sh`, `pull-models.sh`, `run-api.sh`, `run-api.ps1`,
  `smoke-test.sh`, and `test-local.sh`.
- S3: README has one cross-platform Quickstart, a Scripts table, and no legacy
  script references.
- S4: AGENTS.md repository map, setup, and verification protocol use
  `python scripts/dev.py ...`.
- S5 observed results:
  - `python -m compileall -q scripts api`: passed with no output.
  - `python scripts/dev.py --help`: listed all six subcommands.
  - `python scripts/dev.py check`: all PASS (Ollama 0.40.13, configured models,
    `compileall` for `api/` and `scripts/`, `docker compose config`).
  - `python scripts/dev.py ingest` twice: both runs returned
    `{"files_indexed": 2, "chunks_indexed": 15, "collection_count": 15}`
    (idempotent).
  - `smoke` against `scripts/dev.py api --port 8010`: (a), (b), (d), (e), and
    (f) passed. (c) failed because the locally configured `qwen2.5:1.5b`
    answered the off-domain question from parametric knowledge
    (`sources: []` was correct, the refusal phrase was not); this is model
    behavior, not CLI logic. Port 8000 was occupied by the user's running API
    during the first attempt, so the retry used 8010.
  - The unreachable-API smoke path was also observed separately (FAIL + exit 1).

Environment note: the login shell's bare `python` is an unconfigured pyenv
shim, so verification commands were run with the repository `.venv/bin`
prepended to `PATH`. README now names `python3` and `py -3` as the platform
fallbacks.
