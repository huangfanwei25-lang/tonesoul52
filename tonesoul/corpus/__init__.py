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

from .consent import ConsentManager, UserConsent, ConsentType
from .storage import CorpusStorage, Conversation, ConversationTurn
from .pipeline import CorpusPipeline, create_corpus_pipeline


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
    "create_corpus_pipeline"
]
