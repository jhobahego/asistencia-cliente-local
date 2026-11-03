# Asistencia al cliente local

Servicio de atención al cliente con RAG vectorial 100 % local: FastAPI +
ChromaDB + Ollama. Sin nube, sin telemetría, sin costo por consulta y con los
datos siempre en el equipo.

El flujo es simple:

1. Los documentos de `knowledge_base/` se fragmentan y se indexan en ChromaDB.
2. La pregunta se convierte en un vector con `nomic-embed-text`.
3. Se recuperan los fragmentos más cercanos y se filtran con una compuerta
   híbrida (distancia + evidencia léxica).
4. El LLM local responde usando solo esos fragmentos y devuelve las fuentes.

## Arquitectura

![Arquitectura del RAG vectorial](docs/arquitectura-rag.png)

```
knowledge_base/ ──ingesta──> ChromaDB persistente (cosine/HNSW)
                                      ▲
pregunta ──embedding──> top_k ──compuerta──> prompt ──Ollama──> respuesta
```

## Perfiles de hardware

| Perfil | Descripción | Modelos de chat | Embeddings |
|--------|-------------|-----------------|------------|
| Modesto (CPU-only) | Sin GPU dedicada; todo corre en CPU | 1B–3.8B en GGUF `Q4_K_M` | `nomic-embed-text` |
| Potente (NVIDIA) | GPU NVIDIA con CUDA | 7B–14B | `bge-m3` o `qwen3-embedding:0.6b` |

> Este repositorio está calibrado para el perfil modesto: 4 núcleos, 7.2 GB de
> RAM y sin CUDA/ROCm. Los modelos y umbrales concretos de esa máquina están
> documentados en `AGENTS.md`.

## Requerimientos

| Necesidad | Versión mínima | Para qué se usa |
|-----------|----------------|-----------------|
| Docker + Compose v2 (`docker compose`) | Docker 24+ | Opcional: levanta Ollama + Open WebUI. Sin Docker, instalar Ollama nativo |
| Python + venv + pip | Python 3.10+ | API RAG y scripts de ingesta |
| Ollama CLI (`ollama`) | Última estable | Descarga los modelos una sola vez |
| curl | Cualquiera reciente | Probar `/health`, la API y el smoke test |
| Puertos libres | — | `3000` (Open WebUI), `8000` (API), `11434` (Ollama) |
| Disco | ~1 GB libre | Modelo de chat (~2 GB aparte) + embeddings (274 MB) + venv (~530 MB) + índice |

Dependencias de Python (`api/requirements.txt`): `fastapi`, `uvicorn`,
`pydantic`, `httpx`, `chromadb`, `ollama`, `langchain-text-splitters`, `pypdf`,
`python-dotenv`.

### Linux

- Docker Engine + plugin Compose, con el servicio en ejecución y el usuario en
  el grupo `docker` (o usar `sudo`).
- `python3`, `python3-venv`, `pip`, `bash`, `curl`, `git`.
- Verificar con: `docker --version`, `docker compose version`,
  `python3 --version`, `ollama --version`.

### Windows (PowerShell)

- Windows 10/11 de 64 bits con WSL2 + Docker Desktop (backend WSL2) en
  ejecución.
- Python 3.10+ desde `python.org` con la opción `Add to PATH` marcada.
- PowerShell 5.1+ y `curl.exe` (incluido desde Windows 10).
- Ollama Desktop para Windows, o descargar los modelos dentro del contenedor:
  `docker exec -it <contenedor-ollama> ollama pull qwen2.5:3b-instruct-q4_K_M`.

## Quickstart (Linux)

```bash
# 1. Ollama + Open WebUI (CPU-only)
docker compose up -d

# 2. Configuración opcional: crear .env a partir del ejemplo
cp -n .env.example .env    # omitir si .env ya existe

# 3. Dependencias de Python
python3 -m venv .venv
.venv/bin/pip install -r api/requirements.txt

# 4. Modelos: chat + embeddings (una sola vez)
bash scripts/pull-models.sh

# 5. Índice vectorial (una sola vez, o después de cambiar documentos)
bash scripts/ingest.sh

# 6. API (lee API_PORT desde .env)
bash scripts/run-api.sh

# 7. Probar
curl localhost:8000/health
curl -X POST localhost:8000/api/v1/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Cuál es el horario de atención?"}'
```

Documentación interactiva: `http://localhost:8000/docs`.

## Quickstart (Windows, PowerShell)

```powershell
# 1. Ollama + Open WebUI (CPU-only)
docker compose up -d

# 2. Configuración opcional: crear .env a partir del ejemplo
Copy-Item .env.example .env    # omitir si .env ya existe

# 3. Dependencias
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r api/requirements.txt

# 4. Modelos (una sola vez); se leen de .env a través de api.config
$model = python -c "from api import config; print(config.OLLAMA_MODEL)"
$embed = python -c "from api import config; print(config.OLLAMA_EMBED_MODEL)"
ollama pull $model
ollama pull $embed

# 5. Índice vectorial
python -m api.ingest

# 6. API (lee API_PORT desde .env)
.\scripts\run-api.ps1

# 7. Probar
curl.exe localhost:8000/health
```

> Si PowerShell bloquea la ejecución de scripts, iniciar la API con
> `powershell -ExecutionPolicy Bypass -File .\scripts\run-api.ps1`.

## Uso sin Docker (Ollama nativo)

Sin Docker no hay Open WebUI en `http://localhost:3000`; la API en
`http://localhost:8000` funciona igual porque solo necesita
`http://localhost:11434`.

```bash
# 1. Instalar Ollama (una sola vez): https://ollama.com/download
curl -fsSL https://ollama.com/install.sh | sh

# 2. Dependencias de Python
python3 -m venv .venv
.venv/bin/pip install -r api/requirements.txt

# 3. Configuración opcional: crear .env a partir del ejemplo
cp -n .env.example .env    # omitir si .env ya existe

# 4. Servidor + modelos
ollama serve &
bash scripts/pull-models.sh

# 5. API RAG
bash scripts/ingest.sh
bash scripts/run-api.sh
```

> Open WebUI es un chat directo contra Ollama: no pasa por esta API ni usa la
> base vectorial. Para consultar el RAG, usar `/api/v1/ask`, el streaming o
> `http://localhost:8000/docs`.

## Base de conocimiento

- Solo se indexan `knowledge_base/**/*.md` y `knowledge_base/**/*.pdf`.
- Markdown: `#` se guarda como `categoria`, `##` como `seccion` y `###` como
  `pregunta`. Conviene mantener una pregunta por `##` para que cada fragmento
  sea autocontenido.
- PDF: se indexa página por página y la metadata incluye `page`.
- `docs/` contiene documentación meta (`MODELOS.md`, `BENCHMARK.md`,
  `EVALUACION.md`) y **no** se indexa.
- Después de agregar o editar documentos:

```bash
bash scripts/ingest.sh          # reconstruye/actualiza el índice
# o, con la API levantada:
curl -X POST localhost:8000/api/v1/sync-kb
```

La ingesta es idempotente: volver a ejecutarla no duplica fragmentos y elimina
los que ya no corresponden a ningún archivo.

## Variables de entorno

`api/config.py` carga `.env` desde la raíz del repositorio con `python-dotenv`
al importarse. Las variables ya exportadas en el entorno tienen prioridad sobre
el archivo; si `.env` no existe, se usan los valores por defecto. `API_PORT` lo
leen los scripts de arranque (`run-api.sh` y `run-api.ps1`), no `api/main.py`.

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL del servidor Ollama |
| `OLLAMA_MODEL` | `qwen2.5:3b-instruct-q4_K_M` | Modelo de chat |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Modelo de embeddings; cambiarlo exige reindexar |
| `API_PORT` | `8000` | Puerto de la API para los scripts de arranque |
| `RAG_TOP_K` | `4` | Fragmentos recuperados antes de la compuerta |
| `RAG_MAX_DISTANCE` | `0.50` | Distancia de coseno máxima |
| `RAG_STRONG_DISTANCE` | `0.25` | Distancia aceptada sin evidencia léxica |
| `LLM_CONCURRENCY_LIMIT` | `1` | Generaciones simultáneas; 1 en CPU-only |
| `EMBED_BATCH_SIZE` | `32` | Tamaño de lote de embeddings |
| `CHROMA_DB_PATH` | `./chroma_db` | Ruta del índice persistente |
| `CHROMA_COLLECTION` | `asistencia_cliente_kb` | Nombre de la colección |
| `KNOWLEDGE_BASE_DIR` | `./knowledge_base` | Corpus indexado |
| `TEMPERATURE` | `0.2` | Temperatura de generación (`0.0` = más determinista) |
| `OLLAMA_TIMEOUT` | `300` | Timeout de respuesta completa (segundos) |
| `OLLAMA_STREAM_TIMEOUT` | `400` | Timeout de streaming (segundos) |

Timeouts recomendados:

| Perfil | `OLLAMA_TIMEOUT` | `OLLAMA_STREAM_TIMEOUT` |
|--------|------------------|-------------------------|
| Modesto (CPU-only) | 300 | 400 |
| Potente (NVIDIA) | 60–120 | 120–180 |

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado, modelos y cantidad de fragmentos indexados |
| `POST` | `/api/v1/ask` | `{question, categoria?}` → `{answer, sources[{content, metadata, distance}]}` |
| `POST` | `/api/v1/ask/stream` | Misma entrada; respuesta token por token en texto plano |
| `POST` | `/api/v1/sync-kb` | Reindexa `knowledge_base/` en un hilo aparte |
| `POST` | `/v1/chat` | Compatibilidad legacy; `sources` es `list[str]` |
| `POST` | `/v1/chat/stream` | SSE legacy: `sources` → `delta` → `[DONE]` |

`categoria` es un filtro exacto sobre la metadata del encabezado `#`. Una
categoría inexistente devuelve `sources: []` y la respuesta de rechazo.

Ejemplo de streaming:

```bash
curl -N -X POST localhost:8000/api/v1/ask/stream \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Hacen envíos a domicilio?"}'
```

## Modelos recomendados

### Perfil modesto (CPU-only)

- **Chat por defecto:** `qwen2.5:3b-instruct-q4_K_M` (~1.9 GB). Mejor
  equilibrio entre español, instrucciones y RAM en 3B.
- **Embeddings:** `nomic-embed-text` (~274 MB, 768 dimensiones). Requiere los
  prefijos `search_document:` y `search_query:`; el código ya los aplica.
- **Alternativa de chat:** `gemma3:1b` si el equipo necesita más velocidad.
- **No usar en 7 GB:** `llama3.1:8b` (~4.7 GB) no entra junto con el sistema;
  `bge-m3` (1.2 GB) es mejor en español pero compite por RAM y CPU.

### Perfil potente (NVIDIA)

- **Chat:** 7B–14B en `Q4_K_M` (`qwen2.5:7b`, `qwen2.5:14b`), según VRAM.
- **Embeddings:** `bge-m3` (1024 dimensiones, sin prefijos) o
  `qwen3-embedding:0.6b` (1024 dimensiones, mejor multilingüe).
- Al cambiar el modelo de embeddings hay que reindexar todo:
  `python -m api.ingest --reset`.

## Operación y diagnóstico

- **Primer arranque:** si `/health` devuelve `kb_chunks: 0`, falta ejecutar
  `bash scripts/ingest.sh`. Sin índice, todas las respuestas son el rechazo.
- **Respuestas lentas:** en CPU-only una respuesta completa tarda ~20–100 s.
  Usar `/api/v1/ask/stream` para ver los tokens mientras se generan.
- **Reindexar:** `bash scripts/ingest.sh`; tarda ~30–40 s para el corpus de
  ejemplo.
- **Cambiar el modelo de embeddings:** actualizar `OLLAMA_EMBED_MODEL`, ejecutar
  `python -m api.ingest --reset` y volver a medir la compuerta. Mezclar
  vectores de modelos distintos produce resultados inválidos.
- **Borrar el índice:** `chroma_db/` es un artefacto generado; se puede borrar
  y reconstruir sin riesgo.
- **PDF:** la ruta está implementada, pero el corpus de ejemplo no incluye PDF.
  Agregar uno pequeño y repetir el smoke test antes de confiar en ella.

## Verificación

```bash
bash scripts/test-local.sh        # Ollama, compose, modelos y compileall
bash scripts/ingest.sh            # ejecutar dos veces: mismo collection_count
bash scripts/run-api.sh &
bash scripts/smoke-test.sh        # health, on-domain, off-domain y stream
```

Resultado esperado: `/health` con `kb_chunks: 10` para la FAQ de ejemplo; una
pregunta del dominio devuelve respuesta y fuentes; una pregunta fuera del
dominio devuelve `sources: []` y el texto exacto
`No tengo esa información en mi base local`.

## Docker

El `docker-compose.yml` es CPU-only (`docker compose up -d`). Para NVIDIA,
agregar `gpus: all` al servicio `ollama` en una copia local; no modificar el
archivo del repositorio:

```yaml
services:
  ollama:
    image: ollama/ollama
    gpus: all  # solo variante NVIDIA
```

## Privacidad

- Sin llamadas a servicios externos: solo `OLLAMA_BASE_URL`.
- Telemetría de Chroma deshabilitada en ingesta y consulta.
- Sin autenticación: enlazar a `127.0.0.1` salvo que la red sea confiable.
- No commitear `.env`, `chroma_db/`, modelos ni cachés generadas.
