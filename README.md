# Asistencia al cliente local

Prototipo de atención al cliente con LLM open-source 100% local: sin nube, sin costo por consulta y con los datos siempre en el equipo.

## Perfiles de hardware

| Perfil | Descripción | Modelos de chat |
|--------|-------------|-----------------|
| Modesto (CPU-only) | Sin GPU dedicada; todo corre en CPU | 1B–3.8B en GGUF `Q4_K_M` |
| Potente (NVIDIA) | GPU NVIDIA con CUDA | 7B–14B (rangos aproximados, ver abajo) |

## Quickstart (Linux)

```bash
# 1. Ollama + Open WebUI (por defecto, CPU-only)
docker compose up -d

# 2. Modelo por defecto (una sola vez)
bash scripts/pull-models.sh

# 3. Verificación rápida
bash scripts/test-local.sh

# 4. API RAG. La API NO carga .env sola (sin dotenv): exportarlo antes.
python3 -m venv .venv && source .venv/bin/activate
pip install -r api/requirements.txt
set -a; source .env; set +a
uvicorn api.main:app --port "${API_PORT:-8000}"

# 5. Probar
curl localhost:8000/health
curl -X POST localhost:8000/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Cuál es el horario de atención?"}'
```

Chat web: `http://localhost:3000` · Documentación de la API: `http://localhost:8000/docs`.

## Quickstart (Windows, PowerShell)

```powershell
# 1. Ollama + Open WebUI (por defecto, CPU-only)
docker compose up -d

# 2. Modelo por defecto (una sola vez)
ollama pull qwen2.5:3b-instruct-q4_K_M

# 3. API RAG. La API NO carga .env sola (sin dotenv): exportarlo antes.
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r api/requirements.txt
Get-Content .env | Where-Object { $_ -match '\S' -and -not $_.TrimStart().StartsWith('#') } | ForEach-Object { $k,$v = $_ -split '=', 2; Set-Item "env:$($k.Trim())" $v.Trim() }
uvicorn api.main:app --port $env:API_PORT

# 4. Probar
curl.exe localhost:8000/health
```

## Variables de entorno

Los valores por defecto son los que trae el código en `api/main.py`. La API no lee `.env` por sí sola (sin dependencia dotenv); exportar las variables antes de arrancar uvicorn (ver comandos anteriores). `API_PORT` no lo lee `api/main.py`; se usa en la línea de comandos de uvicorn (`.env.example` trae 8000).

| Variable | Valor por defecto (`api/main.py`) | Descripción |
|----------|-----------------------------------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL del servidor Ollama |
| `OLLAMA_MODEL` | `qwen2.5:3b-instruct-q4_K_M` | Modelo de chat |
| `API_PORT` | `8000` | Puerto de escucha de uvicorn (flag de línea de comandos) |
| `RAG_TOP_K` | `3` | Secciones de docs recuperadas como contexto |
| `TEMPERATURE` | `0.2` | Temperatura de generación |
| `OLLAMA_TIMEOUT` | `120` | Timeout en segundos de `POST /v1/chat` |
| `OLLAMA_STREAM_TIMEOUT` | `180` | Timeout en segundos de `POST /v1/chat/stream` |

Timeouts recomendados:

| Perfil | `OLLAMA_TIMEOUT` | `OLLAMA_STREAM_TIMEOUT` |
|--------|------------------|-------------------------|
| Modesto (CPU-only) | 300 | 400 (valores incluidos en `.env.example`) |
| Potente (NVIDIA) | 60–120 | 120–180 |

## Docker

El `docker-compose.yml` por defecto es CPU-only (`docker compose up -d`, sin configuración de GPU). Para NVIDIA, agregar `gpus: all` al servicio `ollama` en una copia local (no modificar el archivo del repo):

```yaml
services:
  ollama:
    image: ollama/ollama
    gpus: all  # solo variante NVIDIA
```

## Modelos recomendados

Perfil modesto (CPU-only, `Q4_K_M`):

- **Por defecto:** `qwen2.5:3b-instruct-q4_K_M` — mejor equilibrio entre calidad de español y seguimiento de instrucciones en 3B.
- **Alternativo (equipo exigido):** `gemma3:1b` — más rápido, respuestas más cortas.
- Alternativas en `docs/MODELOS.md`: `llama3.2:3b`, `phi4-mini` (3.8B, necesita más RAM libre); embeddings `nomic-embed-text` / `bge-m3`.

Perfil potente (NVIDIA, rangos aproximados):

- **7B–8B en `Q4_K_M`** (~4–6 GB de VRAM): por ejemplo `qwen2.5:7b`, `llama3.1:8b`. Buen punto de partida para una GPU NVIDIA media.
- **13B–14B en `Q4_K_M`** (~8–10 GB de VRAM): por ejemplo `qwen2.5:14b`. Mejor español y razonamiento cuando la VRAM lo permite.
- Los tamaños son aproximados; revisar la VRAM libre con `nvidia-smi` antes de descargar un modelo mayor.

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Prueba de vida (no llama a Ollama) |
| `POST` | `/v1/chat` | Respuesta fundamentada `{"question": "..."}` → `{"answer", "sources"}` |
| `POST` | `/v1/chat/stream` | Misma respuesta por SSE (primero `{"sources"}`, luego fragmentos `{"delta"}`, termina con `[DONE]`) |
