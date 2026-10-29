"""Minimal FastAPI RAG service over local Ollama (CPU-only friendly)."""
import json
import os
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.rag import get_context

# Configuration comes from the environment so docker / systemd can override it.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct-q4_K_M")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_STREAM_TIMEOUT = float(os.getenv("OLLAMA_STREAM_TIMEOUT", "180"))

PROMPT_PATH = Path(__file__).with_name("system_prompt.txt")

app = FastAPI(title="asistencia-cliente-local")


class ChatRequest(BaseModel):
    """Incoming chat payload."""

    question: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """Outgoing chat payload."""

    answer: str
    sources: list[str]


def _load_system_prompt() -> str:
    # Read from disk on each request so prompt edits need no restart.
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


@app.get("/health")
def health() -> dict:
    """Liveness probe (does not call Ollama)."""
    return {"status": "ok", "model": OLLAMA_MODEL}


@app.post("/v1/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Answer a question grounded on local docs via Ollama."""
    context, sources = get_context(payload.question, top_k=RAG_TOP_K)
    system_prompt = _load_system_prompt()
    user_message = (
        f"CONTEXT:\n{context}\n\nQUESTION:\n{payload.question.strip()}"
    )
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
                "options": {"temperature": TEMPERATURE},
            },
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        # Ollama down, model missing, or connection refused: surface a 503.
        raise HTTPException(
            status_code=503,
            detail=f"Ollama unavailable at {OLLAMA_BASE_URL}: {exc}",
        ) from exc
    data = resp.json()
    answer = (data.get("message") or {}).get("content", "").strip()
    if not answer:
        raise HTTPException(status_code=502, detail="Empty response from model")
    return ChatResponse(answer=answer, sources=sources)


@app.post("/v1/chat/stream")
def chat_stream(payload: ChatRequest):
    """Same grounded answer as /v1/chat, streamed as SSE.

    First event carries {"sources": [...]} so the client knows the
    grounding upfront; following events carry {"delta": "..."} text
    chunks as Ollama generates them; the stream ends with "data: [DONE]".
    This way the client renders the first words in ~load time instead
    of waiting for the full ~60s answer on this CPU-only machine.
    """
    context, sources = get_context(payload.question, top_k=RAG_TOP_K)
    system_prompt = _load_system_prompt()
    user_message = (
        f"CONTEXT:\n{context}\n\nQUESTION:\n{payload.question.strip()}"
    )

    def gen():
        yield f"data: {json.dumps({'sources': sources})}\n\n"
        try:
            with requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "stream": True,
                    "options": {"temperature": TEMPERATURE},
                },
                stream=True,
                timeout=OLLAMA_STREAM_TIMEOUT,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    text = (chunk.get("message") or {}).get("content", "")
                    if text:
                        yield f"data: {json.dumps({'delta': text})}\n\n"
                    if chunk.get("done"):
                        break
        except requests.RequestException as exc:
            yield (
                "data: "
                + json.dumps({"error": f"Ollama unavailable: {exc}"})
                + "\n\n"
            )
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
