#!/usr/bin/env bash
# End-to-end smoke test against a running API.
# Usage: bash scripts/smoke-test.sh   (API_URL defaults to API_PORT from config)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ -x .venv/bin/python ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi

API_URL="$("$PY" -c 'import os; from api import config; print(os.getenv("API_URL") or f"http://localhost:{config.API_PORT}")')"
API_URL="${API_URL%/}"

FAILED=0

pass() {
  echo "PASS: $1"
}

fail() {
  echo "FAIL: $1" >&2
  FAILED=1
}

# Evaluate a Python expression against the decoded JSON payload.
assert_json() {
  local label="$1"
  local payload="$2"
  local expression="$3"
  if "$PY" -c "
import json, sys
data = json.loads(sys.argv[1])
sys.exit(0 if ($expression) else 1)
" "$payload" 2>/dev/null; then
    pass "$label"
  else
    fail "$label (payload: $payload)"
  fi
}

post_json() {
  curl -sSf --max-time 400 \
    -H 'Content-Type: application/json' \
    -d "$2" \
    "$API_URL$1" 2>/dev/null || true
}

# (a) Health: the API must be reachable and the index must not be empty.
HEALTH="$(curl -sS --max-time 10 "$API_URL/health" 2>/dev/null || true)"
if [ -z "$HEALTH" ]; then
  echo "FAIL: (a) /health is unreachable at $API_URL; start the API first" >&2
  exit 1
fi
if ! "$PY" -c "
import json, sys
data = json.loads(sys.argv[1])
sys.exit(0 if int(data.get('kb_chunks', 0)) > 0 else 1)
" "$HEALTH" 2>/dev/null; then
  fail "(a) /health reports no indexed chunks: $HEALTH"
  echo "FAIL: run scripts/ingest.sh before the smoke test" >&2
  exit 1
fi
pass "(a) /health reports kb_chunks > 0"

# (b) On-domain question: answer and sources must be non-empty.
ON_DOMAIN="$(post_json /api/v1/ask '{"question": "¿Cuál es el horario de atención?"}')"
assert_json \
  "(b) /api/v1/ask answers an on-domain question with sources" \
  "$ON_DOMAIN" \
  "bool((data.get('answer') or '').strip()) and bool(data.get('sources'))"

# (c) Off-domain question: refusal with no sources.
OFF_DOMAIN="$(post_json /api/v1/ask '{"question": "¿Quién ganó el mundial de fútbol?"}')"
assert_json \
  "(c) /api/v1/ask refuses an off-domain question with no sources" \
  "$OFF_DOMAIN" \
  "data.get('sources') == [] and 'No tengo esa información' in (data.get('answer') or '')"

# (d) Streaming endpoint: plain text body must be non-empty.
STREAM="$(post_json /api/v1/ask/stream '{"question": "¿Cuál es el horario de atención?"}')"
if [ -n "${STREAM// /}" ]; then
  pass "(d) /api/v1/ask/stream returns a non-empty body"
else
  fail "(d) /api/v1/ask/stream returned an empty body"
fi

# (e) Unknown category: rejected with 422 and the indexed values listed.
# No -f here: a 4xx must be captured instead of aborting the script.
UNKNOWN_CATEGORY_RESPONSE="$(curl -sS --max-time 10 -w '\n%{http_code}' \
  -H 'Content-Type: application/json' \
  -d '{"question": "¿Cuál es el horario de atención?", "categoria": "string"}' \
  "$API_URL/api/v1/ask" 2>/dev/null || true)"
UNKNOWN_CATEGORY_STATUS="${UNKNOWN_CATEGORY_RESPONSE##*$'\n'}"
UNKNOWN_CATEGORY_BODY="${UNKNOWN_CATEGORY_RESPONSE%$'\n'*}"
if [ "$UNKNOWN_CATEGORY_STATUS" = "422" ]; then
  pass "(e) /api/v1/ask rejects an unknown categoria with 422"
else
  fail "(e) /api/v1/ask returned HTTP ${UNKNOWN_CATEGORY_STATUS:-none} for an unknown categoria"
fi
assert_json \
  "(e) 422 detail lists the available categories" \
  "$UNKNOWN_CATEGORY_BODY" \
  "isinstance(data.get('detail', {}).get('available_categories'), list) and bool(data['detail']['available_categories'])"

# (f) A category read from the 422 payload must return sources.
VALID_CATEGORY="$("$PY" -c "
import json, sys
data = json.loads(sys.argv[1])
categories = data.get('detail', {}).get('available_categories') or []
if categories:
    print(next((c for c in categories if 'FAQ' in c), categories[0]))
" "$UNKNOWN_CATEGORY_BODY" 2>/dev/null || true)"
if [ -z "$VALID_CATEGORY" ]; then
  fail "(f) no available category could be read from the 422 payload"
else
  FILTERED_BODY="$("$PY" -c "
import json, sys
print(json.dumps({'question': '¿Cuál es el horario de atención?', 'categoria': sys.argv[1]}))
" "$VALID_CATEGORY")"
  FILTERED="$(post_json /api/v1/ask "$FILTERED_BODY")"
  assert_json \
    "(f) /api/v1/ask returns sources for an indexed categoria" \
    "$FILTERED" \
    "bool(data.get('sources'))"
fi

if [ "$FAILED" -ne 0 ]; then
  echo "FAIL: smoke test had failures" >&2
  exit 1
fi
echo "PASS: smoke test completed"
