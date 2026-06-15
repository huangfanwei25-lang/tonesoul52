# NOTE (as of 2026-06-15): this is the self-evolution / corpus-building DATA pipeline (CorpusBuilder, ContextDistiller), live via apps/api/server.py. Distinct from council/voting_evolution.py (council voting-weight evolution) — that module was renamed 2026-06-15 to end the grep collision with this package.
"""ToneSoul self-evolution modules."""

from .context_distiller import ContextDistiller, ContextPattern, DistillationResult
from .corpus_builder import CorpusBuilder
from .corpus_schema import CorpusEntry

__ts_layer__ = "evolution"
__ts_purpose__ = "Evolution package: self-improvement, skill promotion, and trial-wave exports."

__all__ = [
    "ContextDistiller",
    "ContextPattern",
    "DistillationResult",
    "CorpusBuilder",
    "CorpusEntry",
]
