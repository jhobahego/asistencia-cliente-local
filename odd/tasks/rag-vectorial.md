# Feature: rag-vectorial

## Objective

Replace the keyword-only `api/rag.py` with a persistent vector RAG: ChromaDB
(`PersistentClient`, cosine/HNSW) + Ollama embeddings + two-stage chunking,
exposed through FastAPI with source/distance traceability.

Branch: `feat/rag-vectorial/jhon-hernandez` (never work on `main`).

## Problem

`api/rag.py` reloads `docs/*.md` on every request and ranks by stem overlap.
It cannot handle paraphrases outside its synonym map, has no persistence, no
PDF support, and no notion of semantic distance. The technical report
`mejora-rag-local.md` proposes ChromaDB + `bge-m3`/`llama3.1`.

## Why

The repo must stay 100% local and CPU-first. The proposed models do not fit this
machine (`bge-m3` 1.2 GB, `llama3.1` 8B), so the implementation is calibrated
for the actual hardware budget instead of copying the report defaults.

## Local hardware budget (measured)

| Resource | Value |
|---|---|
| CPU | AMD A12-9720P, 4 cores / 4 threads, 2.7 GHz max |
| RAM | 7.2 GB total, ~2.7 GB available during this work |
| GPU | Radeon R7 iGPU only; no CUDA, no usable ROCm |
| Disk free | ~27 GB |
| Ollama | 0.40.13, server on `localhost:11434` |
| Python | 3.13.5 (`.venv`) |

Model decisions derived from this budget:

- Chat: keep `qwen2.5:3b-instruct-q4_K_M` (~1.9 GB, already pulled).
- Embeddings: `nomic-embed-text` (768 dims, 274 MB) instead of `bge-m3`
  (1.2 GB) or `qwen3-embedding:0.6b` (639 MB, ~4x slower on 4 CPU cores).
- LLM concurrency: 1 (a second concurrent generation would swap on 7.2 GB).

## Authorized scope

- `api/` modules: config, embeddings, lexical gate, ingestion, vector RAG, FastAPI.
- `knowledge_base/` as the only indexed corpus; move `docs/faq-ejemplo.md` there.
- `scripts/`: model pull, ingestion, local checks, smoke test.
- `api/requirements.txt`, `.gitignore`, `.env.example`.
- `AGENTS.md`, `README.md`, `docs/arquitectura-rag.png`, this task file.

## Out of scope

- Cloud APIs, telemetry, dotenv, auth, Docker changes.
- Re-embedding with a second model (documented as an upgrade path only).
- Push, PR, merge (human decisions).

## Tasks

| ID | Task | Route | State |
|---|---|---|---|
| R1 | Validate environment: install deps, pull `nomic-embed-text`, probe APIs | inline env action | done |
| R2 | `api/config.py` + `api/embeddings.py` (batch `/api/embed`, nomic prefixes, `truncate=False`) | delegated writer | done |
| R3 | `api/lexical.py` (reuse proven Spanish normalization/synonyms as precision gate) | delegated writer | done |
| R4 | `api/ingest.py` (Markdown two-stage split, PDF per page, deterministic IDs, stale-chunk prune, batch upsert) | delegated writer | done |
| R5 | `api/rag.py` (LocalVectorRAG: async query embedding, Chroma query, hybrid gate, ask/stream) | delegated writer | done |
| R6 | `api/main.py` + `system_prompt.txt` (lifespan, semaphore, canonical + legacy endpoints) | delegated writer | done |
| R7 | scripts + KB migration + `.gitignore` + `.env.example` | delegated writer | done |
| R8 | `AGENTS.md` + `README.md` + architecture image | parent | done |
| R9 | End-to-end verification: ingest, real queries, stream, refusals, compileall | parent | done |
| R10 | Native receipt-driven review | parent | disabled: runtime transport unsupported |

## Acceptance criteria

- `python -m api.ingest` indexes every `.md`/`.pdf` under `knowledge_base/` and
  is idempotent (second run adds no duplicates).
- `POST /api/v1/ask` returns the answer plus `sources[].metadata` and
  `sources[].distance` for every grounding chunk.
- Off-domain questions return the exact refusal from `api/system_prompt.txt`
  with `sources: []`.
- Legacy `/v1/chat` and `/v1/chat/stream` keep working (additive change).
- No network calls outside `OLLAMA_BASE_URL` (Chroma telemetry disabled).
- Code, comments, and `AGENTS.md` in English; README in neutral Spanish.

## Checks

- `.venv/bin/python -m compileall -q api`
- `.venv/bin/python -m api.ingest` twice (idempotency: identical chunk count)
- `bash scripts/smoke-test.sh` against a running uvicorn
- Manual refusal check with an off-domain question
- TDD exception: the repo has no test runner and no pytest dependency; the
  runnable check is the end-to-end smoke test plus deterministic ingest output.

## Calibration evidence (measured on the real FAQ, nomic-embed-text)

Naive `max_distance = 0.65` is unusable: off-domain questions score 0.32–0.45,
overlapping the on-domain range 0.20–0.41. A pure absolute threshold cannot
separate them.

Hybrid gate adopted instead:

```
keep chunk if distance <= RAG_MAX_DISTANCE AND
            (distance <= RAG_STRONG_DISTANCE OR lexical_evidence(query, chunk) > 0)
```

Measured defaults: `RAG_MAX_DISTANCE=0.50`, `RAG_STRONG_DISTANCE=0.25`.

| Query | Best distance | Type | Gate |
|---|---|---|---|
| ¿cuál es el horario de atención? | 0.200 | on | accept (strong) |
| necesito factura para mi empresa | 0.198 | on | accept (strong) |
| se me rompió el producto, ¿tiene garantía? | 0.236 | on | accept (strong) |
| ¿puedo cambiar el talle? | 0.261 | on | accept (lexical) |
| ¿puedo pagar con tarjeta de crédito? | 0.293 | on | accept (lexical) |
| ¿hasta dónde llegan los envíos? | 0.400 | on | accept (lexical) |
| ¿cuál es la capital de Francia? | 0.321 | off | reject (no lexical) |
| ¿a cuánto está el dólar hoy? | 0.381 | off | reject (no lexical) |
| dame una receta de empanadas | 0.430 | off | reject (no lexical) |

Result on the probe set: 13/17 on-domain accepted (safe misses refuse), 14/15
off-domain rejected. The only false accept was "cambio una rueda pinchada",
which shares the stem "cambio/cambiar" with a product-exchange chunk; the
grounding prompt still refuses. The synonym map remains tunable.

## Route

- R2–R7: delegated direct, one writer (7+ non-trivial files; writer trigger).
- R1, R8–R9: inline (environment actions and orchestrator-owned documentation).
- Evidence: multi-file API rewrite + measured calibration + model installation
  exceed the inline evidence budget.

## Progress

- 2026-11-01: branch created. R1 done: chromadb 1.5.9, ollama 0.6.3,
  langchain-text-splitters 1.1.3, pypdf 6.21.4 installed in `.venv`;
  `nomic-embed-text` pulled (274 MB). Probed `/api/embed`, Chroma upsert/query/
  delete, and LangChain splitters. Calibration measured (table above).

- 2026-11-01: R2-R7 implemented by one writer. Verified: `compileall` clean;
  two ingestion runs both returned `{"files_indexed":1,"chunks_indexed":10,"collection_count":10}`;
  `--reset` reproduced 10; all six routes registered.
- 2026-11-01: R9 end-to-end on uvicorn: `/health` returned `kb_chunks: 10`;
  `scripts/smoke-test.sh` passed all four checks; `/api/v1/sync-kb` returned
  `collection_count: 10`; legacy `/v1/chat` returned `sources: ["faq-ejemplo.md"]`;
  legacy SSE emitted `sources` -> `delta` -> `[DONE]`.
- 2026-11-01: prompt-format finding. With `[Fragmento N - Fuente: ...]` as the
  first line of each block, the 3B model answered by echoing the header
  (observed on "¿Hasta dónde llegan los envíos?"). Moved the `[Fuente: ...]`
  label to the END of each block and added "start with the answer" rules;
  re-tested: "Los envíos se hacen a todo el país..." and correct citations.
- 2026-11-01: one API run still over-refused the envíos paraphrase at
  `TEMPERATURE=0.2` (same prompt); repeated runs answered correctly, so this is
  sampling variance, not a retrieval failure. Documented in AGENTS.md; `0.0`
  reduces it.
- 2026-11-01: R8 docs written (`AGENTS.md`, `README.md`, architecture image).
- 2026-11-01: native review attempted with explicit user consent on the full
  candidate (21 files, 2202 lines). Lineage `review-dfce41431b5bf56b` started,
  but all four lens captures failed. The three lens child sessions recorded
  `finish.reason = "length"` with ~147.5k input tokens, 32,000 reasoning tokens
  and 0 output tokens: the reviewer model exhausted its output budget while
  reasoning. The fourth lens failed with
  `immutable_review_transport_unsupported`.
- 2026-11-01: slice review attempted. A temporary worktree at commit
  `4523605` and a detached HEAD in the main worktree both returned
  `immutable_review_transport_unsupported`: the active runtime is not eligible
  for immutable receipt review, and the supported runtimes (Claude Code,
  Codex) are not installed. No review approval, receipt, or PASS is claimed.
- 2026-11-01: the oversized lineage was abandoned with the v2
  operator-disposition record (no captured results, no findings). The user then
  authorized `gentle-ai review mode disable --scope clone --cwd <repo>`; RDD is
  off for this clone only (`global: on`, `clone-local: off`). Delivery remains
  under ordinary repository policy.
