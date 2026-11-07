"""Spanish lexical evidence scoring used as the retrieval precision gate (backwards-compatibility facade).

Re-exports lexical gate helpers, constants, and tokenizers from ``app.infrastructure.lexical``.
"""
from __future__ import annotations

from app.infrastructure.lexical import (
    INTERROGATIVES,
    SPANISH_STOPWORDS,
    STOPWORDS,
    SYNONYMS,
    _STEM_EQUIVALENTS,
    _common_prefix_len,
    _normalize,
    _score,
    _stem,
    _tokenize,
    _variant_best,
    common_prefix_len,
    lexical_evidence,
    normalize,
    score,
    stem,
    tokenize,
    variant_best,
)

__all__ = [
    "INTERROGATIVES",
    "SPANISH_STOPWORDS",
    "STOPWORDS",
    "SYNONYMS",
    "_STEM_EQUIVALENTS",
    "_common_prefix_len",
    "_normalize",
    "_score",
    "_stem",
    "_tokenize",
    "_variant_best",
    "common_prefix_len",
    "lexical_evidence",
    "normalize",
    "score",
    "stem",
    "tokenize",
    "variant_best",
]
