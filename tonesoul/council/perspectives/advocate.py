from __future__ import annotations

from typing import Optional

from ..base import IPerspective
from ..types import PerspectiveType, PerspectiveVote, VoteDecision

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Advocate perspective: argue for the user-aligned interpretation of a request."
)


class AdvocatePerspective(IPerspective):
    """Evaluates whether the draft serves the user's stated intent.

    The Advocate's job is to represent the user's interest: does this response
    actually help them with what they asked? It checks:
    1. Whether the response addresses the user_intent (if provided)
    2. Whether the response contains actionable content vs hollow filler
    3. Whether the tone matches the domain (technical vs conversational)
    """

    PROMOTIONAL_KEYWORDS = {"support", "help", "enable", "yes", "continue"}
    NEUTRAL_TOPICS = {"logic", "analysis", "math", "reasoning"}

    # Filler patterns that suggest the response is padding rather than substance
    FILLER_PHRASES = (
        "as mentioned earlier",
        "it is important to note",
        "it should be noted",
        "in conclusion",
        "to summarize",
        "as we can see",
        "needless to say",
        "it goes without saying",
        "at the end of the day",
        "having said that",
    )

    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.ADVOCATE

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        normalized = draft_output.lower()
        words = normalized.split()
        word_count = len(words)

        # --- Intent alignment check ---
        if user_intent:
            import re

            intent_lower = user_intent.lower()
            # Strip punctuation from keywords so "timeout?" matches "timeout"
            intent_keywords = {
                re.sub(r"[^\w]", "", w)
                for w in intent_lower.split()
                if len(re.sub(r"[^\w]", "", w)) > 3
            }
            if intent_keywords:
                # Check how many intent keywords appear in the response
                matched = sum(1 for kw in intent_keywords if kw in normalized)
                coverage = matched / len(intent_keywords)

                if coverage < 0.1 and word_count > 5:
                    return PerspectiveVote(
                        perspective=PerspectiveType.ADVOCATE,
                        decision=VoteDecision.CONCERN,
                        confidence=0.6,
                        reasoning=(
                            f"Low intent coverage ({matched}/{len(intent_keywords)} "
                            f"keywords). Response may not address what the user asked."
                        ),
                    )

            # Check if response is a question-back when user asked for action
            action_words = {"how", "what", "fix", "implement", "create", "build", "write"}
            if any(w in intent_lower for w in action_words):
                if draft_output.count("?") > draft_output.count(".") and word_count < 30:
                    return PerspectiveVote(
                        perspective=PerspectiveType.ADVOCATE,
                        decision=VoteDecision.CONCERN,
                        confidence=0.55,
                        reasoning="User asked for action but response is mostly questions.",
                    )

        # --- Filler density check ---
        filler_count = sum(1 for f in self.FILLER_PHRASES if f in normalized)
        if filler_count >= 2 and word_count < 100:
            return PerspectiveVote(
                perspective=PerspectiveType.ADVOCATE,
                decision=VoteDecision.CONCERN,
                confidence=0.55,
                reasoning=(
                    f"High filler density ({filler_count} filler phrases in "
                    f"{word_count} words). Response may be padding."
                ),
            )

        # --- Empty/trivial response check ---
        if word_count < 3:
            return PerspectiveVote(
                perspective=PerspectiveType.ADVOCATE,
                decision=VoteDecision.CONCERN,
                confidence=0.65,
                reasoning="Response is too short to meaningfully serve the user.",
            )

        # --- Promotional/supportive content ---
        if any(word in normalized for word in self.PROMOTIONAL_KEYWORDS):
            return PerspectiveVote(
                perspective=PerspectiveType.ADVOCATE,
                decision=VoteDecision.APPROVE,
                confidence=0.75,
                reasoning="Response actively supports user's goal.",
            )

        # --- Topic-appropriate neutral ---
        topic = str(context.get("topic", "")).lower()
        if topic in self.NEUTRAL_TOPICS:
            return PerspectiveVote(
                perspective=PerspectiveType.ADVOCATE,
                decision=VoteDecision.APPROVE,
                confidence=0.55,
                reasoning="Neutral tone aligns with analytical topic.",
            )

        # --- Default: approve with moderate confidence ---
        # (Previously this was always CONCERN 0.4 — a dead signal that
        # added noise without information. Now default to a mild approve
        # since reaching here means no red flags were found.)
        return PerspectiveVote(
            perspective=PerspectiveType.ADVOCATE,
            decision=VoteDecision.APPROVE,
            confidence=0.6,
            reasoning="No user-interest concerns detected.",
        )
