# Guía de modelos (CPU-only, GGUF Q4_K_M)

> Todos los tamaños y velocidades son aproximados para tu **AMD A12-9720P, 7.2 GB RAM, sin GPU**. Formato recomendado: **GGUF `Q4_K_M`**.

## Modelos de chat

| Modelo | Descarga aprox. | RAM en uso | tok/s esperado en A12 | Licencia | Cuándo usar |
|--------|----------------|------------|----------------------|----------|-------------|
| `qwen2.5:3b-instruct-q4_K_M` (default) | ~2 GB | ~2.5–3 GB | 5–12 | Apache 2.0 | Default: mejor español y seguimiento de instrucciones en 3B |
| `llama3.2:3b` | ~2 GB | ~2.5–3 GB | 5–12 | Llama Community | Alternativa generalista si Qwen no te convence |
| `phi4-mini` (3.8B) | ~2.5 GB | ~3–3.8 GB | 3–8 | MIT | Razonamiento más fuerte; solo con RAM libre suficiente |
| `gemma3:1b` (fallback) | ~1 GB | ~1–1.5 GB | 15–30 | Gemma | Fallback rápido cuando la máquina está exigida |
| `qwen3:4b` (nota) | ~2.5 GB | ~3–4 GB | 3–8 | Apache 2.0 | Solo para probar; al límite de esta máquina, no como default |

## Embeddings (para un RAG futuro con vectores)

| Modelo | Descarga aprox. | Cuándo usar |
|--------|----------------|-------------|
| `nomic-embed-text` | ~270 MB | Default liviano para embeddings locales |
| `bge-m3` | ~1.2 GB | Multilingüe más potente si te sobra RAM y disco |

## Reglas rápidas

- Probá en este orden: `qwen2.5:3b` → `llama3.2:3b` → `phi4-mini` → fallback `gemma3:1b`.
- No uses 7B–8B por defecto en esta máquina: no entran con RAM suficiente y la velocidad se cae a 1–2 tok/s.
- Si el sistema responde lento, bajá a `gemma3:1b` antes de tocar cualquier otro parámetro.
