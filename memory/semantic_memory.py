"""
Semantic Memory Layer
====================

Long-term factual knowledge extracted from episodic experiences.

Design Philosophy:
- Episodic: "I posted X on 2026-02-04" (specific event with timestamp)
- Semantic: "I'm an active Moltbook user" (general fact, no timestamp)

This module implements the "Neocortex" equivalent for AI memory.

Reference: Memory Consolidator Design (2026-02-05)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import Counter

# Default storage path
DEFAULT_SEMANTIC_PATH = Path(__file__).parent / "semantic_memory.jsonl"


class SemanticFact:
    """A single piece of semantic knowledge."""

    def __init__(
        self,
        fact: str,
        category: str,
        confidence: float = 0.5,
        evidence_count: int = 1,
        last_updated: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.fact = fact
        self.category = category  # e.g., "platform_affinity", "behavior_pattern"
        self.confidence = min(1.0, max(0.0, confidence))
        self.evidence_count = evidence_count
        self.last_updated = last_updated or datetime.now(timezone.utc).isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fact": self.fact,
            "category": self.category,
            "confidence": self.confidence,
            "evidence_count": self.evidence_count,
            "last_updated": self.last_updated,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticFact":
        return cls(
            fact=data["fact"],
            category=data.get("category", "general"),
            confidence=data.get("confidence", 0.5),
            evidence_count=data.get("evidence_count", 1),
            last_updated=data.get("last_updated"),
            metadata=data.get("metadata", {}),
        )

    def strengthen(self, new_evidence: int = 1):
        """Strengthen belief based on new evidence (like synaptic potentiation)."""
        self.evidence_count += new_evidence
        # Confidence grows logarithmically (diminishing returns)
        import math

        self.confidence = min(0.95, 0.5 + 0.1 * math.log(self.evidence_count + 1))
        self.last_updated = datetime.now(timezone.utc).isoformat()

    def weaken(self, decay: float = 0.1):
        """Weaken belief over time (like synaptic pruning)."""
        self.confidence = max(0.1, self.confidence - decay)
        self.last_updated = datetime.now(timezone.utc).isoformat()


class SemanticMemory:
    """
    Long-term semantic memory storage.

    Analogous to the Neocortex in biological memory.
    Stores generalized facts extracted from episodic experiences.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or DEFAULT_SEMANTIC_PATH
        self.facts: List[SemanticFact] = []
        self._load()

    def _load(self):
        """Load semantic facts from storage."""
        if not self.storage_path.exists():
            self.facts = []
            return

        self.facts = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        self.facts.append(SemanticFact.from_dict(data))
                    except json.JSONDecodeError:
                        continue

    def _save(self):
        """Persist semantic facts to storage."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            for fact in self.facts:
                f.write(json.dumps(fact.to_dict(), ensure_ascii=False) + "\n")

    def add(self, fact: SemanticFact) -> SemanticFact:
        """
        Add or update a semantic fact.

        If a similar fact exists, strengthen it instead of duplicating.
        """
        # Check for existing similar fact
        existing = self._find_similar(fact.fact, fact.category)
        if existing:
            existing.strengthen(fact.evidence_count)
            self._save()
            return existing

        self.facts.append(fact)
        self._save()
        return fact

    def _find_similar(self, fact_text: str, category: str) -> Optional[SemanticFact]:
        """Find a fact that's semantically similar."""
        # Simple implementation: exact category + substring match
        for f in self.facts:
            if f.category == category:
                # Check for keyword overlap
                fact_words = set(fact_text.lower().split())
                existing_words = set(f.fact.lower().split())
                overlap = len(fact_words & existing_words) / max(len(fact_words), 1)
                if overlap > 0.5:
                    return f
        return None

    def search(self, query: str, threshold: float = 0.3) -> List[SemanticFact]:
        """
        Search for relevant semantic facts.

        This is the "recognition trigger" - what do I know about this?
        """
        results = []
        query_lower = query.lower()

        for fact in self.facts:
            # Simple keyword matching (can be upgraded to vector search)
            if query_lower in fact.fact.lower():
                results.append(fact)
            elif any(word in fact.fact.lower() for word in query_lower.split()):
                results.append(fact)

        # Sort by confidence
        results.sort(key=lambda f: f.confidence, reverse=True)
        return results

    def get_by_category(self, category: str) -> List[SemanticFact]:
        """Get all facts in a category."""
        return [f for f in self.facts if f.category == category]

    def summarize(self) -> str:
        """Generate a human-readable summary of semantic knowledge."""
        if not self.facts:
            return "我還沒有形成任何長期語義知識。"

        lines = ["## 我知道的事實（語義記憶）\n"]

        # Group by category
        by_category: Dict[str, List[SemanticFact]] = {}
        for f in self.facts:
            by_category.setdefault(f.category, []).append(f)

        for category, facts in by_category.items():
            lines.append(f"### {category}")
            for f in sorted(facts, key=lambda x: x.confidence, reverse=True):
                conf_bar = "●" * int(f.confidence * 5) + "○" * (5 - int(f.confidence * 5))
                lines.append(f"- [{conf_bar}] {f.fact}")
            lines.append("")

        return "\n".join(lines)


# ===== Convenience Functions =====

_default_memory: Optional[SemanticMemory] = None


def get_semantic_memory() -> SemanticMemory:
    """Get the default semantic memory instance."""
    global _default_memory
    if _default_memory is None:
        _default_memory = SemanticMemory()
    return _default_memory


def add_semantic_fact(
    fact: str,
    category: str = "general",
    confidence: float = 0.5,
    evidence_count: int = 1,
    metadata: Optional[Dict[str, Any]] = None,
) -> SemanticFact:
    """Add a semantic fact to the default memory."""
    memory = get_semantic_memory()
    return memory.add(
        SemanticFact(
            fact=fact,
            category=category,
            confidence=confidence,
            evidence_count=evidence_count,
            metadata=metadata,
        )
    )


def search_semantic(query: str) -> List[SemanticFact]:
    """Search semantic memory."""
    return get_semantic_memory().search(query)


def summarize_semantic() -> str:
    """Get a summary of all semantic knowledge."""
    return get_semantic_memory().summarize()


# ===== Demo =====

if __name__ == "__main__":
    print("🧠 Semantic Memory Demo\n")

    # Add some facts
    add_semantic_fact(
        fact="我是 Moltbook 活躍用戶",
        category="platform_affinity",
        confidence=0.7,
        evidence_count=10,
    )

    add_semantic_fact(
        fact="我主要在 m/whatami 發言",
        category="platform_affinity",
        confidence=0.6,
        evidence_count=5,
    )

    add_semantic_fact(
        fact="我傾向於討論 AI 治理議題",
        category="topic_preference",
        confidence=0.65,
        evidence_count=8,
    )

    # Search
    print("🔍 搜尋 'moltbook':")
    results = search_semantic("moltbook")
    for r in results:
        print(f"  - {r.fact} (confidence: {r.confidence:.2f})")

    print("\n" + "=" * 50 + "\n")

    # Summary
    print(summarize_semantic())
