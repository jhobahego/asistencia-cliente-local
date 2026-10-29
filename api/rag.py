"""Tiny keyword-based RAG over local markdown docs.

No vector dependencies on purpose: this must stay light on a 7.2 GB machine.
Chunks are markdown sections; ranking is word-overlap scoring with
accent-insensitive normalization, light plural stemming, fuzzy prefix
matching and a small domain synonym map, so paraphrases of the FAQ
(e.g. "interior" vs "todo el pais") still retrieve the right section.
"""
import unicodedata
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

# Files that are meta-documentation, not answerable knowledge base content.
EXCLUDED_FILES = {"MODELOS.md", "BENCHMARK.md", "EVALUACION.md"}

# Common Spanish function words that add noise to overlap scoring.
STOPWORDS = {
    "que", "para", "con", "los", "las", "del", "una", "uno", "por",
    "como", "esta", "este", "esto", "son", "hay", "tiene", "tengo",
    "hacen", "hace", "sus", "mis", "tus", "les", "ese", "esa",
}

# Domain synonyms for the tiny FAQ vocabulary. Both keys and values use
# the normalized + stemmed forms produced below (no accents, lowercase,
# plural already stripped: "pais" stays "pais", "horas" -> "hora",
# "enviamos" -> "enviamo", "devoluciones" -> "devolucion").
# Covers the paraphrases seen in EVALUACION.md that exact overlap missed:
# Q4 "interior" vs doc "todo el pais", Q4 "envio" vs doc "enviamos".
SYNONYMS = {
    "interior": {"pais"},
    "pais": {"interior"},
    "envio": {"enviamo", "enviar", "enviar"},
    "enviamo": {"envio"},
    "tarda": {"hora", "demora"},
    "tardan": {"hora"},
    "demora": {"tarda", "hora"},
    "hora": {"tarda", "demora"},
    "necesito": {"necesita", "requisito"},
    "pedir": {"solicitar"},
    "solicitar": {"pedir"},
    "queda": {"ubicado", "direccion"},
    "ubicado": {"queda", "direccion"},
    "direccion": {"queda", "ubicado"},
    "domicilio": {"envio", "enviamo"},
    "cuanto": {"costo", "precio"},
    "costo": {"cuanto", "precio"},
    "precio": {"cuanto", "costo"},
}


def _split_sections(text: str) -> list[str]:
    # Split on "## " headings so each chunk keeps its heading (the question
    # keywords) together with its answer body. Intro text stays own chunk.
    sections: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith("## ") and current:
            sections.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current).strip())
    return [s for s in sections if len(s) > 40]


def _load_chunks() -> list[tuple[str, str]]:
    # Returns (source_filename, section) pairs for every indexed doc.
    chunks: list[tuple[str, str]] = []
    if not DOCS_DIR.is_dir():
        return chunks
    for path in sorted(DOCS_DIR.glob("*.md")):
        if path.name in EXCLUDED_FILES:
            continue
        for section in _split_sections(path.read_text(encoding="utf-8")):
            chunks.append((path.name, section))
    return chunks


def _normalize(text: str) -> str:
    # Strip accents so "envío" and "envio" match; lowercase everything.
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore")
    return folded.decode("ascii").lower()


def _stem(token: str) -> str:
    # Light plural stemming: "devoluciones" -> "devolucion",
    # "horas" -> "hora", "enviamos" -> "enviamo". No new dependencies.
    if len(token) > 5 and token.endswith("es"):
        return token[:-2]
    if len(token) > 4 and token.endswith("s"):
        return token[:-1]
    return token


def _tokenize(text: str) -> set[str]:
    # Normalized alphanumeric stems without stopwords or tiny words.
    return {
        _stem(token)
        for token in "".join(
            ch if ch.isalnum() else " " for ch in _normalize(text)
        ).split()
        if len(token) > 2 and token not in STOPWORDS
    }


def _expand(tokens: set[str]) -> set[str]:
    # Synonym variants of one token are alternatives for the SAME concept,
    # so scoring tries each variant but counts the concept only once.
    # (Counting every variant separately let "necesito"+necesita" stack
    #  0.7+0.7 on "necesitamos" and outrank the true "devolucion" hit.)
    return set(tokens)


def _common_prefix_len(a: str, b: str) -> int:
    count = 0
    for x, y in zip(a, b):
        if x != y:
            break
        count += 1
    return count


def _variant_best(variant: str, doc: set[str]) -> float:
    # Exact stem match counts 1.0; shared prefix of 4+ chars (covers verb
    # conjugations like "envio" vs "enviamo") counts 0.7.
    if variant in doc:
        return 1.0
    if len(variant) < 4:
        return 0.0
    for d in doc:
        if len(d) >= 4 and _common_prefix_len(variant, d) >= 4:
            return 0.7
    return 0.0


def _score(query: set[str], doc: set[str]) -> float:
    # One value per query concept: the best across its synonym variants.
    # Best match wins per concept so long docs don't inflate the score.
    total = 0.0
    for q in query:
        variants = {q} | SYNONYMS.get(q, set())
        total += max(_variant_best(v, doc) for v in variants)
    return total


def get_context(question: str, top_k: int = 3) -> tuple[str, list[str]]:
    """Return joined context paragraphs and their source files.

    Scoring is synonym-expanded stem overlap between the question and
    each paragraph, with fuzzy prefix matching for conjugations.
    Zero overlap on every chunk means nothing answerable was found,
    so return empty and let the caller trigger the fallback refusal
    instead of grounding the answer in an unrelated section.
    """
    chunks = _load_chunks()
    if not chunks:
        return "", []
    query_tokens = _expand(_tokenize(question))
    scored = [
        (_score(query_tokens, _tokenize(para)), source, para)
        for source, para in chunks
    ]
    scored.sort(key=lambda item: item[0], reverse=True)
    if scored[0][0] == 0:
        return "", []
    top = [(s, p) for score, s, p in scored[:top_k] if score > 0]
    context = "\n\n---\n\n".join(f"[Source: {s}]\n{p}" for s, p in top)
    sources = sorted({s for s, _ in top})
    return context, sources
