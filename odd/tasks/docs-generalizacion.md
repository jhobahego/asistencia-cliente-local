# Feature: docs-generalizacion

## Objetivo
Generalizar README a Linux/Windows (sin hardware del autor) y crear AGENTS.md.

## Problema
README actual menciona LMDE 7, AMD A12, Topaz XT; no distingue Linux/Windows, no documenta env vars de timeout ni Docker NVIDIA, y falta recomendación para máquina potente.

## Por qué
El proyecto debe configurarse en ambas plataformas y en dos perfiles (modesta CPU-only / potente NVIDIA) sin reescribirlo por máquina.

## Alcance autorizado
- Reescribir README.md existente
- Crear AGENTS.md nuevo en raíz
- No tocar api/, scripts/, docs/, docker-compose.yml, .env

## Fuera de alcance
- Cambiar código, compose, modelos, dotenv; push/remoto; commits (no es repo git)

## Restricciones
- README en español; AGENTS.md en inglés, sin slang ni voseo
- Modesta = genérica (CPU-only, 1B-3.8B Q4_K_M), sin modelo de CPU del autor como ejemplo
- Conservar sección modelos modestos; agregar subsección NVIDIA (7B-14B) como rangos aproximados
- Tabla env con defaults reales: OLLAMA_BASE_URL, OLLAMA_MODEL, API_PORT, RAG_TOP_K, TEMPERATURE, OLLAMA_TIMEOUT (120), OLLAMA_STREAM_TIMEOUT (180); valores modesta 300/400; NVIDIA 60-120/120-180
- API no lee .env sola: documentar `set -a; source .env` (Linux) y equivalente PowerShell (Windows)

## Checklist
- [x] D1 Reescribir README: perfiles, Quickstart Linux + Windows, tabla env, Docker CPU + NVIDIA, modelos modestos + NVIDIA
- [x] D2 Crear AGENTS.md: stack, estructura, comandos, env, RAG, checks, convenciones
- [x] D3 Verificar: compileall api, grep sin A12/Topaz/LMDE en README, lectura visual

## Criterios de aceptación
- `grep -i "A12\|Topaz\|LMDE" README.md` vacío; comandos Linux/Windows copiables; AGENTS.md en inglés

## Checks aplicables
- `python3 -m compileall api` (o `.venv/bin/python -m compileall api`)
- Excepción TDD: docs sin runner; sustituye por checks estructurales + lectura visual

## Ruta
- D1-D2: delegated direct (un writer, 2 files no-triviales, excede batch inline)
- Evidencia trigger: 2 files + reescritura generalista con investigación docs/MODELOS.md

## Progreso
- 2026-10-29: doc creado, pendiente D1.
- 2026-10-29: D1+D2 hechos por writer (README 110 líneas generalista ES + AGENTS.md 65 líneas EN). Evidencia: `compileall api` exit 0, `grep -i "A12\|Topaz\|LMDE"` vacío, lectura visual OK. D3 verificado por parent.
