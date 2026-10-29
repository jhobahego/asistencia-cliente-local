# Feature: asistencia-cliente-local

## Objetivo
Prototipo de asistencia al cliente con LLM open-source 100% local en LMDE 7, optimizado para CPU-only (AMD A12, 7.2GB RAM).

## Problema
Se necesita una solución de atención al cliente local, sin cloud, que responda rápido y con alucinaciones mínimas, corriendo en hardware modesto.

## Por qué
Privacidad / offline + costo cero + control total de datos. Modelos chicos quantizados permiten iterar sin GPU.

## Alcance autorizado
- Carpeta `asistencia-cliente-local/` como raíz del proyecto
- Stack: Ollama (runtime) + Qwen2.5:3B / Llama3.2:3B / Phi-4-mini / Gemma3:1B (GGUF Q4_K_M) + Open WebUI + FastAPI RAG mínimo
- Docs en español, código y comentarios en inglés
- Solo archivos listados en Allowed edit surfaces del writer. Nada fuera de esta carpeta.

## Fuera de alcance
- Fine-tuning, 7B-8B por defecto, ROCm, deploy cloud, push a remoto sin pedirlo.

## Restricciones hardware (verificadas 2026-10-29)
- AMD A12-9720P 4c, 7.2GB RAM (~4.5GB libre), sin NVIDIA, Topaz XT sin ROCm -> CPU-only
- Objetivo: 1B-3.8B Q4_K_M, 5-15 tok/s, <4GB RAM por modelo

## Checklist
- [x] T1 scaffold base: README, .gitignore, docker-compose (ollama+open-webui), .env.example, scripts pull/test
- [x] T2 api RAG mínima: FastAPI /v1/chat + ingest de docs/ + system prompt anti-alucinaciones + requirements
- [x] T3 docs/faq + evaluación: 20 preguntas fijas, guía de benchmark CPU, guía de modelos
- [x] T4 verificación: `docker compose config`, `python -m compileall`, prueba `ollama run --verbose` documentada (manual, no auto en CI) — hecho 2026-10-29: pull qwen2.5:3b-instruct-q4_K_M OK (1.9GB), eval 2.60 tok/s, prompt eval 4.87 tok/s, total 37.4s, alucina sin RAG (dice Alibaba 24/7 vs FAQ L-V 9-18)
- [x] T5 fix recall RAG: normalización sin acentos + stemming plural + stopwords + sinónimos dominio (interior<->pais) + fuzzy prefijo 4+ + conteo por concepto + vacío real si score 0 — retrieval 15/15 top-1 OK (Q4/Q7 corregidos), 2 trampas puras devuelven vacío para fallback limpio
- [x] T6 streaming SSE: POST /v1/chat/stream en api/main.py (primer evento sources, luego deltas, cierra [DONE]) — compile OK, verificado e2e con curl -N: sources primero + 6 deltas en vivo + [DONE], respuesta correcta

## Criterios de aceptación
- `docker compose config` válido, estructura corre en LMDE 7 Debian 13 base
- Modelo default documentado: qwen2.5:3b-instruct-q4_K_M, fallback gemma3:1b
- RAG con temperatura 0.1-0.3 y fallback "no sé si no está en contexto"
- README con pasos Ollama + LM Studio/Jan alternativo + benchmark esperado en A12

## Checks aplicables
- Estructurales: `docker compose config`, `python -m compileall api`
- Funcionales manuales: `ollama pull`, `ollama run <modelo> --verbose`, `curl localhost:11434`, `curl localhost:8000/v1/chat`
- Excepción TDD: no hay runner determinístico para LLM; se sustituye por checks estructurales + evaluación manual documentada

## Ruta
- T1-T3: delegated direct (un writer, prepara lectura + escribe 2+ files no-triviales)
- Evidencia trigger: scaffold >10 files, excede batch inline 3 calls / 10k tokens

## Progreso
- 2026-10-29: carpeta creada, doc ODD creado. Pendiente T1.
- 2026-10-29: T1-T3 implementados y verificados (docker compose config OK, compileall OK, bash -n OK, smoke get_context OK). Pendiente T4 manual.
- 2026-10-29: T4 hecho — Ollama 0.40.13 instalado, servicio active, modelo qwen2.5:3b-instruct-q4_K_M registrado. Siguiente: compose + API RAG para corregir alucinación.
- 2026-10-29: API RAG verificada — /health ok, horario responde L-V 9-18 Sab 9-13 con [Source: faq-ejemplo.md], trampa helicóptero devuelve fallback "No tengo esa información..." correcto. RAG cura alucinación Alibaba 24/7.
- 2026-10-29: EVALUACION.md 20/20 corrida — 12/15 respondibles OK, 5/5 trampas OK, latencia prom ~61s (19/20 >30s), NO aprueba. Fallos: Q3 alucina dirección, Q4+Q7 falsos rechazos (recall keyword), latencia sistémica A12.
- 2026-10-29: T5 hecho en api/rag.py (verificado retrieval 15/15 + compile OK). PENDIENTE: reiniciar uvicorn (corre código viejo) y re-probar Q4/Q7 end-to-end.
- 2026-10-29: T5 verificado e2e tras reinicio — Q4 responde 48-72h hábiles y Q7 ticket+sin uso, ambas con [Source: faq-ejemplo.md]. Falsos rechazos curados; el 3B sí puenteó interior<->país con el chunk correcto.
