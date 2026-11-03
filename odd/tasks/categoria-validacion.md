# Feature: categoria-validacion

## Objective

Make the optional `categoria` filter fail loudly instead of silently degrading
into the off-domain refusal, and stop Swagger UI from injecting a placeholder
`"string"` category into the generated request body.

Branch: `feat/rag-vectorial/jhon-hernandez`.

## Problem

`AskRequest.categoria` is an exact-match Chroma metadata filter
(`api/rag.py:105-106`). When no explicit example exists, Swagger UI's sample
generator expands `anyOf: [string, null]` into the literal `"string"`, so
"Try it out" from `/docs` sends `"categoria": "string"`. That matches no chunk,
`retrieve_context` returns `[]`, and the model emits the fixed refusal:
indistinguishable from a genuine off-domain question.

Measured against the live collection (15 chunks):

- `where={"categoria": "string"}` -> 0 ids.
- `where={"categoria": "FAQ de ejemplo — Tienda ficticia \"El Ombú\""}` -> 4 ids.
- Real categories: the FAQ example and the LaLiga document only.

## Why

A typo or a client placeholder must be diagnosable. A silent refusal hides the
real cause and turns a client bug into a phantom retrieval bug.

## Scope

- `api/rag.py`: expose the indexed category values.
- `api/main.py`: validate the filter on every endpoint that accepts it, return
  422 with `available_categories`, and add a request-body example so `/docs`
  prefills a body without a category.
- `scripts/smoke-test.sh`: guard both the 422 path and the valid-filter path.
- `AGENTS.md`: document the contract and retire the stale pitfall.

## Out of scope

- Fuzzy or case-insensitive category matching.
- Adding pytest: this repo has no test runner, so verification stays
  `compileall` + a live HTTP check + the smoke test.
- Caching the category list across requests.

## Decisions

- **Validate instead of tolerate.** Treating `"string"` as "no filter" would
  mask typos forever. A 422 listing the available values is self-explanatory.
- **Blocking metadata scan per filtered request.** `categories()` walks the
  collection metadata; the corpus is 15 chunks and ingestion already accepts a
  full metadata scan for pruning. Revisit only if it measurably hurts.
- **Blank means no filter.** `""`/whitespace normalizes to `None`, preserving
  the previous truthiness behavior.
- **Legacy endpoints share the contract.** Same request model, same validation.

## Tasks

| ID | Task | Route | State |
|---|---|---|---|
| C1 | Add `LocalVectorRAG.categories()` | delegated | done |
| C2 | Validate category, 422 + available list, OpenAPI example | delegated | done |
| C3 | Extend smoke test (422 + valid filter) | delegated | done |
| C4 | Update `AGENTS.md` contract and pitfalls | delegated | done |
| C5 | Verify end to end, commit work unit | inline | done |

## Acceptance criteria

- `POST /api/v1/ask` with `"categoria": "string"` -> 422 with a non-empty
  `detail.available_categories`.
- Same question without `categoria`, or with a real one -> 200 with sources.
- `/openapi.json` request body example for `/api/v1/ask` omits `categoria`.
- `bash -n scripts/smoke-test.sh` passes.
- `.venv/bin/python -m compileall -q api` passes.

## Verification

```bash
.venv/bin/python -m compileall -q api
bash -n scripts/smoke-test.sh
.venv/bin/python -c "from api.rag import LocalVectorRAG; print(LocalVectorRAG().categories())"
# temp server on 8011, no Ollama needed for the 422 and the OpenAPI check
```

## Delivery

Forecast: ~100 authored changed lines (additions + deletions), under the ~400
planning heuristic. Single work unit, single commit. No chain strategy needed.

## Progress

- 2026-11-01: diagnosis confirmed; task file created; writer delegated.
- 2026-11-01: C1-C4 implemented in `6ccccb7`.
- 2026-11-01: verification. Independent read-only verifier: pass, no findings.
  Parent end to end against Ollama: the prefilled body (no `categoria`) returns
  200 with sources; `"categoria": "string"` returns 422 listing both indexed
  categories; `scripts/smoke-test.sh` passes 8/8 checks, including the new (e)
  and (f).
- Risk assessment: `high` (shell process boundary in the smoke test). RDD is
  off for this clone, so the gate was writer self-verification + independent
  verifier + parent spot check.
- Not verified: Swagger UI browser rendering of the named example. Only
  `/openapi.json` was inspected; the request body matches the documented
  example and is proven to return 200.

## Accepted changes

- `LocalVectorRAG.categories()` reads the indexed metadata instead of
  hardcoding corpus values.
- Validation runs before the generation semaphore, so a rejected filter never
  queues behind an answer on this CPU-only machine.
- The smoke test derives a valid category from the 422 payload rather than
  duplicating the corpus strings, but prefers a category containing `FAQ`
  because the on-domain probe question is the FAQ one.
