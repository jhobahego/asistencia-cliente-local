#!/usr/bin/env bash
# Pull the default model and document alternatives.
# CPU-only machine: GGUF Q4_K_M builds, no ROCm / CUDA needed.
set -euo pipefail

# Default: best balance of Spanish quality vs RAM on 7.2 GB machines.
ollama pull qwen2.5:3b-instruct-q4_K_M

# Alternatives (uncomment the one you want to try):
# ollama pull llama3.2:3b          # solid generalist fallback, similar size
# ollama pull phi4-mini            # strong reasoning, 3.8B needs more free RAM
# ollama pull gemma3:1b            # fastest fallback when the machine struggles
