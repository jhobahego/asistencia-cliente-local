# Benchmark en CPU (A12)

Objetivo: saber qué modelo responde aceptable en tu máquina antes de atarlo a la API.

## Pasos

```bash
# 1. El modelo tiene que estar descargado
ollama pull qwen2.5:3b-instruct-q4_K_M

# 2. Correr con métricas (repetí con cada candidato)
ollama run qwen2.5:3b-instruct-q4_K_M --verbose
# dentro del prompt: "Resumí en 3 líneas la política de devoluciones."

# 3. Mirar RAM libre en otra terminal mientras responde
free -h
```

## Qué medir

| Métrica | Dónde sale | Qué es aceptable acá |
|---------|-----------|----------------------|
| tok/s (eval rate) | salida de `--verbose` | 1B: 15–30 · 3B: 5–12 |
| Tiempo total | salida de `--verbose` | Menos de 30 s para respuestas cortas |
| RAM libre | `free -h` | Mantener 500 MB+ libres para el sistema |

## Valores esperados en el A12

- **1B (`gemma3:1b`):** 15–30 tok/s, fluido incluso con el navegador abierto.
- **3B (`qwen2.5:3b`, `llama3.2:3b`):** 5–12 tok/s, bien para RAG con respuestas cortas.
- **3.8B (`phi4-mini`):** 3–8 tok/s, solo con todo lo demás cerrado.

> Advertencia: no pruebes 7B–8B como uso diario en esta máquina. Ocupan casi toda la RAM y caen a 1–2 tok/s. Solo tendría sentido como prueba puntual de calidad, nunca por defecto.
