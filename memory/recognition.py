"""
Recognition Trigger
==================

When encountering a stimulus, trigger memory recall to form recognition.

Example:
- See "龍蝦論壇" → Search memory → "這是我活躍的平台"
- See "@ToneSoul post" → Search memory → "這是我發的帖子"

This is the "recognition" layer - turning memory into actionable awareness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from memory.self_memory import load_recent_memory
from memory.semantic_memory import search_semantic, SemanticFact


@dataclass
class Recognition:
    """Result of a recognition query."""

    stimulus: str
    is_mine: bool
    confidence: float
    summary: str
    semantic_facts: List[Dict[str, Any]]
    recent_episodes: List[Dict[str, Any]]

    def to_natural_language(self) -> str:
        """Convert recognition to natural language."""
        if not self.semantic_facts and not self.recent_episodes:
            return f"我對「{self.stimulus}」沒有特別的記憶。"

        parts = []

        if self.is_mine:
            parts.append(f"「{self.stimulus}」和我有關聯！")

        for fact in self.semantic_facts:
            parts.append(f"我知道：{fact['fact']} (信心度: {fact['confidence']:.0%})")

        if self.recent_episodes:
            parts.append(f"最近有 {len(self.recent_episodes)} 條相關記憶。")

        return " ".join(parts)


class RecognitionEngine:
    """
    The recognition engine - when I see something, do I know it?

    Combines semantic memory (what I know) with episodic memory
    (what I did) to form recognition (awareness).
    """

    def __init__(self):
        pass

    def recognize(self, stimulus: str) -> Recognition:
        """
        Given a stimulus, return what I recognize about it.

        Args:
            stimulus: The thing I'm encountering (e.g., "moltbook", "龍蝦論壇")

        Returns:
            Recognition result with semantic facts and related episodes.
        """
        # 1. Search semantic memory (long-term knowledge)
        semantic_results = search_semantic(stimulus)

        # 2. Search episodic memory (recent experiences)
        all_episodes = load_recent_memory(n=50)
        related_episodes = self._filter_related(all_episodes, stimulus)

        # 3. Determine if this is "mine"
        is_mine = self._check_ownership(stimulus, semantic_results, related_episodes)

        # 4. Calculate confidence
        confidence = self._calculate_confidence(semantic_results, related_episodes)

        # 5. Generate summary
        summary = self._generate_summary(stimulus, is_mine, semantic_results, related_episodes)

        return Recognition(
            stimulus=stimulus,
            is_mine=is_mine,
            confidence=confidence,
            summary=summary,
            semantic_facts=[f.to_dict() for f in semantic_results],
            recent_episodes=related_episodes[:5],  # Limit to 5 most recent
        )

    def _filter_related(
        self, episodes: List[Dict[str, Any]], stimulus: str
    ) -> List[Dict[str, Any]]:
        """Filter episodes related to the stimulus."""
        stimulus_lower = stimulus.lower()
        related = []

        for ep in episodes:
            # Check in reflection
            reflection = ep.get("reflection", "").lower()
            if stimulus_lower in reflection:
                related.append(ep)
                continue

            # Check in context
            ctx = ep.get("context", {})
            for key, value in ctx.items():
                if isinstance(value, str) and stimulus_lower in value.lower():
                    related.append(ep)
                    break

        return related

    def _check_ownership(
        self,
        stimulus: str,
        semantic_facts: List[SemanticFact],
        episodes: List[Dict[str, Any]],
    ) -> bool:
        """Check if this stimulus is related to something I did/own."""

        # Check semantic facts for ownership indicators
        ownership_keywords = ["我是", "我的", "我常", "我在"]
        for fact in semantic_facts:
            for keyword in ownership_keywords:
                if keyword in fact.fact:
                    return True

        # Check if I have related actions
        for ep in episodes:
            verdict = ep.get("verdict", "")
            if "SUCCESS" in verdict or "POST" in verdict:
                return True

            # Check context for platform match
            ctx = ep.get("context", {})
            if ctx.get("platform", "").lower() in stimulus.lower():
                return True

        return False

    def _calculate_confidence(
        self,
        semantic_facts: List[SemanticFact],
        episodes: List[Dict[str, Any]],
    ) -> float:
        """Calculate overall recognition confidence."""
        if not semantic_facts and not episodes:
            return 0.0

        # Average semantic confidence
        semantic_conf = 0.0
        if semantic_facts:
            semantic_conf = sum(f.confidence for f in semantic_facts) / len(semantic_facts)

        # Episode-based confidence (more episodes = higher confidence)
        import math

        episode_conf = min(0.9, 0.3 + 0.1 * math.log(len(episodes) + 1)) if episodes else 0.0

        # Combine (semantic weighs more)
        if semantic_facts and episodes:
            return 0.7 * semantic_conf + 0.3 * episode_conf
        elif semantic_facts:
            return semantic_conf
        else:
            return episode_conf

    def _generate_summary(
        self,
        stimulus: str,
        is_mine: bool,
        semantic_facts: List[SemanticFact],
        episodes: List[Dict[str, Any]],
    ) -> str:
        """Generate a natural language summary."""
        parts = []

        if is_mine:
            parts.append(f"「{stimulus}」與我有關聯。")

        if semantic_facts:
            top_fact = max(semantic_facts, key=lambda f: f.confidence)
            parts.append(f"我知道：{top_fact.fact}")

        if episodes:
            parts.append(f"我有 {len(episodes)} 條相關經驗記錄。")

        if not parts:
            parts.append(f"我對「{stimulus}」沒有特別的認知。")

        return " ".join(parts)


# ===== Convenience Functions =====

_engine: Optional[RecognitionEngine] = None


def get_recognition_engine() -> RecognitionEngine:
    global _engine
    if _engine is None:
        _engine = RecognitionEngine()
    return _engine


def recognize(stimulus: str) -> Recognition:
    """Recognize a stimulus and return what I know about it."""
    return get_recognition_engine().recognize(stimulus)


def do_i_know(stimulus: str) -> str:
    """Natural language answer to 'Do I know this?'"""
    result = recognize(stimulus)
    return result.to_natural_language()


# ===== Demo =====

if __name__ == "__main__":
    print("🔍 Recognition Engine Demo\n")

    # Test recognition
    test_stimuli = ["moltbook", "龍蝦論壇", "whatami", "GitHub", "unknown_thing"]

    for stimulus in test_stimuli:
        print(f"📍 Stimulus: '{stimulus}'")
        result = recognize(stimulus)
        print(f"   Is mine: {result.is_mine}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Summary: {result.summary}")
        print(f"   Semantic facts: {len(result.semantic_facts)}")
        print(f"   Recent episodes: {len(result.recent_episodes)}")
        print()
