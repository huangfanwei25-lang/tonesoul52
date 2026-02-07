"""
ToneSoul Corpus Pipeline

High-level interface that combines:
- Consent management
- Conversation storage
- ToneSoul deliberation

Provides a simple API for the web frontend.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .consent import ConsentManager, ConsentType, UserConsent
from .storage import CorpusStorage


@dataclass
class PipelineResponse:
    """Response from the corpus pipeline."""

    response: str
    conversation_id: str
    turn_index: int
    deliberation: Optional[Dict[str, Any]] = None
    suggested_replies: Optional[List[Dict]] = None

    def to_dict(self) -> dict:
        result = {
            "response": self.response,
            "conversation_id": self.conversation_id,
            "turn_index": self.turn_index,
        }
        if self.deliberation:
            result["deliberation"] = self.deliberation
        if self.suggested_replies:
            result["suggested_replies"] = self.suggested_replies
        return result


class CorpusPipeline:
    """
    High-level corpus collection pipeline.

    Combines consent, storage, and ToneSoul deliberation
    into a simple interface for web apps.

    Usage:
        pipeline = CorpusPipeline()

        # Check/record consent
        if not pipeline.has_consent(session_id):
            pipeline.record_consent(session_id, ConsentType.RESEARCH)

        # Start conversation
        conv_id = pipeline.start_conversation(session_id)

        # Process messages
        response = pipeline.process_message(conv_id, "Hello!")
    """

    def __init__(
        self,
        consent_db: str = "data/users.db",
        corpus_db: str = "data/corpus.db",
        corpus_jsonl: str = "data/corpus.jsonl",
    ):
        self.consent_manager = ConsentManager(consent_db)
        self.corpus_storage = CorpusStorage(corpus_db, corpus_jsonl)

        # ToneSoul deliberation engine (lazy load)
        self._deliberation_engine = None

    def _get_deliberation_engine(self):
        """Lazy load ToneSoul deliberation engine."""
        if self._deliberation_engine is None:
            try:
                from tonesoul.deliberation import InternalDeliberation

                self._deliberation_engine = InternalDeliberation()
            except ImportError:
                pass
        return self._deliberation_engine

    # ===== Session Management =====

    def generate_session_id(self) -> str:
        """Generate a new anonymous session ID."""
        return f"session_{uuid.uuid4().hex}"

    def has_consent(self, session_id: str) -> bool:
        """Check if session has valid consent."""
        return self.consent_manager.has_valid_consent(session_id)

    def record_consent(
        self,
        session_id: str,
        consent_type: ConsentType = ConsentType.RESEARCH,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserConsent:
        """Record user consent."""
        return self.consent_manager.record_consent(session_id, consent_type, ip_address, user_agent)

    def withdraw_consent(self, session_id: str) -> Dict[str, Any]:
        """Withdraw consent and delete all data."""
        # Withdraw consent
        consent_withdrawn = self.consent_manager.withdraw_consent(session_id)

        # Delete corpus data
        deleted_count = self.corpus_storage.delete_session_data(session_id)

        return {"consent_withdrawn": consent_withdrawn, "conversations_deleted": deleted_count}

    # ===== Conversation Management =====

    def start_conversation(self, session_id: str, model: str = "formosa1") -> str:
        """Start a new conversation. Returns conversation ID."""
        if not self.has_consent(session_id):
            raise ValueError("No valid consent for session")

        consent = self.consent_manager.get_consent(session_id)
        conv = self.corpus_storage.create_conversation(
            session_id=session_id,
            consent_version=consent.consent_version if consent else "1.0",
            model=model,
        )
        return conv.id

    def process_message(
        self, conversation_id: str, user_input: str, use_deliberation: bool = True
    ) -> PipelineResponse:
        """
        Process a user message through ToneSoul.

        Returns the AI response and stores the turn.
        """
        deliberation_data = None
        suggested_replies = None

        # Run ToneSoul deliberation
        if use_deliberation:
            engine = self._get_deliberation_engine()
            if engine:
                try:
                    from tonesoul.deliberation import DeliberationContext

                    # Get conversation history
                    conv = self.corpus_storage.get_conversation(conversation_id)
                    history = []
                    if conv:
                        for turn in conv.turns[-5:]:  # Last 5 turns
                            history.append({"role": "user", "content": turn.user_input})
                            history.append({"role": "assistant", "content": turn.ai_response})

                    context = DeliberationContext(
                        user_input=user_input, conversation_history=history
                    )

                    result = engine.deliberate_sync(context)
                    ai_response = result.response
                    deliberation_data = result.to_api_response()

                    # Extract suggested replies
                    if result.suggested_replies:
                        suggested_replies = [sr.to_dict() for sr in result.suggested_replies]

                except Exception as e:
                    print(f"Deliberation error: {e}")
                    ai_response = self._fallback_response(user_input)
            else:
                ai_response = self._fallback_response(user_input)
        else:
            ai_response = self._fallback_response(user_input)

        # Store the turn
        turn_index = self.corpus_storage.add_turn(
            conversation_id=conversation_id,
            user_input=user_input,
            ai_response=ai_response,
            deliberation=deliberation_data,
        )

        return PipelineResponse(
            response=ai_response,
            conversation_id=conversation_id,
            turn_index=turn_index,
            deliberation=deliberation_data,
            suggested_replies=suggested_replies,
        )

    def _fallback_response(self, user_input: str) -> str:
        """Fallback response when deliberation is unavailable."""
        return f"收到你的訊息：「{user_input[:50]}...」。ToneSoul 正在思考中..."

    def end_conversation(self, conversation_id: str):
        """End a conversation and save to JSONL backup."""
        conv = self.corpus_storage.get_conversation(conversation_id)
        if conv:
            conv.ended_at = datetime.now()
            self.corpus_storage.save_to_jsonl(conv)

    # ===== Statistics =====

    def get_stats(self) -> Dict[str, Any]:
        """Get combined statistics."""
        consent_stats = self.consent_manager.get_consent_stats()
        corpus_stats = self.corpus_storage.get_corpus_stats()

        return {"consent": consent_stats, "corpus": corpus_stats}


def create_corpus_pipeline(
    consent_db: str = "data/users.db",
    corpus_db: str = "data/corpus.db",
    corpus_jsonl: str = "data/corpus.jsonl",
) -> CorpusPipeline:
    """Factory function."""
    return CorpusPipeline(consent_db, corpus_db, corpus_jsonl)
