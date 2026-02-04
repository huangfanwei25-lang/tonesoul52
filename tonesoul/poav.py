import re
from typing import Dict, List

DEFAULT_MAX_TOKENS = 800
DEFAULT_MAX_AVG_SENTENCE = 40
DEFAULT_EVIDENCE_TARGET = 8.0
DEFAULT_PATH_WEIGHT = 2.0

EVIDENCE_KEYWORDS = (
    "evidence",
    "source",
    "reference",
    "link",
    "path",
    "file",
    "log",
    "report",
    "audit",
    "hash",
    "context",
    "constraint",
)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text)


def _split_sentences(text: str) -> List[str]:
    chunks = re.split(r"[.!?\n]+", text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def _count_keyword_hits(text: str) -> int:
    text_lower = text.lower()
    return sum(text_lower.count(keyword) for keyword in EVIDENCE_KEYWORDS)


def _count_path_hits(text: str) -> int:
    windows_paths = re.findall(r"[A-Za-z]:\\[^\\\s]+", text)
    unix_paths = re.findall(r"/[^\s]+", text)
    file_names = re.findall(r"\b\w+\.(?:json|ya?ml|md|csv|log|txt|html|svg|png)\b", text.lower())
    return len(windows_paths) + len(unix_paths) + len(file_names)


def score(
    text: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_avg_sentence: int = DEFAULT_MAX_AVG_SENTENCE,
    evidence_target: float = DEFAULT_EVIDENCE_TARGET,
    path_weight: float = DEFAULT_PATH_WEIGHT,
) -> Dict[str, float]:
    tokens = _tokenize(text)
    token_count = len(tokens)
    sentences = _split_sentences(text)
    sentence_count = len(sentences)
    unique_sentences = len({sentence.strip().lower() for sentence in sentences})

    keyword_hits = _count_keyword_hits(text)
    path_hits = _count_path_hits(text)

    if token_count == 0:
        return {
            "parsimony": 0.0,
            "orthogonality": 0.0,
            "audibility": 0.0,
            "verifiability": 0.0,
            "total": 0.0,
            "token_count": 0.0,
            "sentence_count": 0.0,
            "unique_sentences": 0.0,
            "avg_sentence_tokens": 0.0,
            "keyword_hits": float(keyword_hits),
            "path_hits": float(path_hits),
        }

    parsimony = _clamp(1.0 - (token_count / float(max_tokens or 1)))
    orthogonality = _clamp(unique_sentences / float(sentence_count)) if sentence_count else 0.0
    avg_sentence_tokens = token_count / float(sentence_count or 1)
    audibility = _clamp(1.0 - (avg_sentence_tokens / float(max_avg_sentence or 1)))
    evidence_signals = keyword_hits + (path_hits * path_weight)
    verifiability = _clamp(evidence_signals / float(evidence_target or 1.0))

    total = (parsimony + orthogonality + audibility + verifiability) / 4.0
    return {
        "parsimony": parsimony,
        "orthogonality": orthogonality,
        "audibility": audibility,
        "verifiability": verifiability,
        "total": total,
        "token_count": float(token_count),
        "sentence_count": float(sentence_count),
        "unique_sentences": float(unique_sentences),
        "avg_sentence_tokens": float(avg_sentence_tokens),
        "keyword_hits": float(keyword_hits),
        "path_hits": float(path_hits),
    }
