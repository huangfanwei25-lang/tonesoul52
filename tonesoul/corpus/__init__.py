# DORMANT (as of 2026-06-15): No non-test imports; unused in live entry points (ts CLI, mcp_server); not re-exported from tonesoul/__init__.py; separate corpus_schema/corpus_builder in evolution/ are local-only; see docs/architecture/architecture_legibility_2026-06-15.md
"""
ToneSoul Corpus Collection Module

Manages user consent, conversation storage, and data pipeline
for collecting training data.

Privacy-first design:
- Versioned consent tracking
- Anonymized session IDs
- No raw IP storage
- Opt-out support
"""

from .consent import ConsentManager, ConsentType, UserConsent
from .pipeline import CorpusPipeline, create_corpus_pipeline
from .storage import Conversation, ConversationTurn, CorpusStorage

__ts_layer__ = "evolution"
__ts_purpose__ = "Corpus utilities: training and evaluation data management for self-improvement."

__all__ = [
    # Consent
    "ConsentManager",
    "UserConsent",
    "ConsentType",
    # Storage
    "CorpusStorage",
    "Conversation",
    "ConversationTurn",
    # Pipeline
    "CorpusPipeline",
    "create_corpus_pipeline",
]
