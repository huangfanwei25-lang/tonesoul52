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
