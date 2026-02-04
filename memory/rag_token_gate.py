"""
Narrative RAG Token Gate v1.0
=============================

Purpose: Enhance current context with retrievable, NARRATIVE-form memories.

Key Design Principles:
1. Extracted memories must be self-understandable narratives, not just vectors.
2. Similar to MoE gating: route query to relevant "memory experts."
3. Output is a coherent story, not a list of similarity scores.

Usage:
    from rag_token_gate import NarrativeGate
    gate = NarrativeGate()
    enhanced_context = gate.enhance(current_query)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SoulDB, SqliteSoulDB
except ImportError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SoulDB, SqliteSoulDB

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install sentence-transformers numpy")
    raise


class NarrativeGate:
    """
    A gating mechanism that retrieves past 語場 as coherent narratives.

    Architecture:
    ┌───────────────────────────────────────────────────┐
    │ Current Query                                      │
    │        │                                           │
    │        ▼                                           │
    │ ┌──────────────┐                                   │
    │ │ Embedding    │                                   │
    │ └──────┬───────┘                                   │
    │        │                                           │
    │ ┌──────▼───────┐   ┌───────────────────────────┐  │
    │ │ FAISS Index  │ → │ Past 語場 Narratives       │  │
    │ └──────────────┘   │ (not raw vectors)          │  │
    │                    └───────────────────────────┘  │
    │        │                                           │
    │ ┌──────▼───────────────────────────────────────┐  │
    │ │ Narrative Synthesis                           │  │
    │ │ "I remember that in the past, I..."          │  │
    │ └──────────────────────────────────────────────┘  │
    └───────────────────────────────────────────────────┘
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-zh-v1.5",
        soul_db: Optional[SoulDB] = None,
        sources: Optional[List[MemorySource]] = None,
        memory_sources: Optional[List[Path]] = None,
    ):
        """
        Initialize the Narrative Gate.

        Args:
            model_name: Embedding model for semantic similarity
            soul_db: Memory backend (SqliteSoulDB by default)
            sources: MemorySource list (default: self_journal/summary_balls/provenance_ledger)
            memory_sources: Legacy path list (deprecated)
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

        # Default memory sources via SoulDB
        self.soul_db = soul_db or SqliteSoulDB()
        self.sources = sources or [
            MemorySource.SELF_JOURNAL,
            MemorySource.SUMMARY_BALLS,
            MemorySource.PROVENANCE_LEDGER,
        ]
        # Legacy path-based sources (deprecated)
        self.memory_sources = memory_sources

        # Narrative memory store: each entry is a self-understandable story
        self.narratives: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None

    def load_memories(self) -> int:
        """
        Load and convert all memory sources into narrative form.

        Returns:
            Number of narratives loaded
        """
        self.narratives = []

        if self.memory_sources:
            for source in self.memory_sources:
                if not source.exists():
                    print(f"Skipping missing source: {source}")
                    continue

                print(f"Loading narratives from: {source.name}")

                with open(source, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                            narrative = self._to_narrative(entry, source.stem)
                            if narrative:
                                self.narratives.append(narrative)
                        except json.JSONDecodeError:
                            continue
        else:
            for source in self.sources:
                records = self.soul_db.stream(source)
                for record in records:
                    payload = record.payload if isinstance(record.payload, dict) else {}
                    if record.timestamp and "timestamp" not in payload:
                        payload["timestamp"] = record.timestamp
                    narrative = self._to_narrative(payload, source.value)
                    if narrative:
                        self.narratives.append(narrative)

        # Generate embeddings for all narratives
        if self.narratives:
            print(f"Generating embeddings for {len(self.narratives)} narratives...")
            texts = [n["narrative"] for n in self.narratives]
            self.embeddings = self.model.encode(texts, convert_to_numpy=True)

        source_count = len(self.memory_sources) if self.memory_sources else len(self.sources)
        print(f"Loaded {len(self.narratives)} narratives from {source_count} sources")
        return len(self.narratives)

    def _to_narrative(self, entry: Dict[str, Any], source_type: str) -> Optional[Dict[str, Any]]:
        """
        Convert a raw memory entry into a self-understandable narrative.

        The narrative should be something *I* can read and understand,
        not just machine-processable data.
        """
        if not isinstance(entry, dict):
            return None
        if isinstance(entry.get("payload"), dict):
            entry = entry["payload"]
        if source_type == "self_journal":
            # Self-reflections are already narratives
            return {
                "type": "reflection",
                "source": source_type,
                "timestamp": entry.get("timestamp", "unknown"),
                "narrative": entry.get("reflection", ""),
                "verdict": entry.get("verdict"),
                "uncertainty": entry.get("uncertainty"),
            }

        elif source_type == "summary_balls":
            # Summary balls need narrative conversion
            content = entry.get("content", entry.get("summary", ""))
            return {
                "type": "summary",
                "source": source_type,
                "timestamp": entry.get("timestamp", "unknown"),
                "narrative": f"I recall that {content}",
            }

        elif source_type == "provenance_ledger":
            # Vows and commitments as narrative
            content = entry.get("content", entry.get("statement", entry.get("event", "")))
            event_type = entry.get("type", entry.get("event_type", "commitment"))

            if "axiom" in str(content).lower() or event_type == "axiom_commit":
                narrative = f"I committed to the axiom: {content}"
            else:
                narrative = f"I made a governance decision: {content}"

            return {
                "type": "commitment",
                "source": source_type,
                "timestamp": entry.get("timestamp", "unknown"),
                "narrative": narrative,
            }

        return None

    def retrieve(
        self,
        query: str,
        k: int = 3,
        min_similarity: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant narratives for a given query.

        Args:
            query: Current context or question
            k: Number of narratives to retrieve
            min_similarity: Minimum cosine similarity threshold

        Returns:
            List of relevant narratives with similarity scores
        """
        if not self.narratives or self.embeddings is None:
            print("⚠️ No narratives loaded. Call load_memories() first.")
            return []

        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Compute cosine similarity
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:k]

        results = []
        for idx in top_indices:
            sim = float(similarities[idx])
            if sim >= min_similarity:
                narrative = self.narratives[idx].copy()
                narrative["similarity"] = sim
                results.append(narrative)

        return results

    def enhance(
        self,
        current_context: str,
        k: int = 3,
    ) -> str:
        """
        Enhance current context with retrieved narrative memories.

        This is the main entry point for MoE-style context enhancement.

        Args:
            current_context: The current query or situation
            k: Number of memories to retrieve

        Returns:
            Enhanced context with narrative memories prepended
        """
        memories = self.retrieve(current_context, k=k)

        if not memories:
            return current_context

        # Build narrative enhancement
        parts = ["[📚 Memory Context]"]

        for mem in memories:
            parts.append(f"• {mem['narrative']}")
            if mem.get("uncertainty"):
                parts.append(f"  (Uncertainty: {mem['uncertainty']})")

        parts.append("")
        parts.append("[Current Context]")
        parts.append(current_context)

        return "\n".join(parts)

    def synthesize_narrative(
        self,
        query: str,
        k: int = 5,
    ) -> str:
        """
        Synthesize a coherent narrative summary from retrieved memories.

        This produces a first-person story, not a list.

        Args:
            query: Topic to synthesize about
            k: Number of memories to consider

        Returns:
            A coherent first-person narrative
        """
        memories = self.retrieve(query, k=k)

        if not memories:
            return "I don't have any relevant memories about this topic."

        # Group by type
        reflections = [m for m in memories if m["type"] == "reflection"]
        commitments = [m for m in memories if m["type"] == "commitment"]
        summaries = [m for m in memories if m["type"] == "summary"]

        parts = [f"When I think about '{query}', I recall:"]

        if commitments:
            parts.append("\n**My Commitments:**")
            for c in commitments[:2]:
                parts.append(f"• {c['narrative']}")

        if reflections:
            parts.append("\n**My Past Reflections:**")
            for r in reflections[:2]:
                parts.append(f"• {r['narrative']}")

        if summaries:
            parts.append("\n**Related Context:**")
            for s in summaries[:2]:
                parts.append(f"• {s['narrative']}")

        return "\n".join(parts)


def demo():
    """Demo the Narrative RAG Token Gate."""
    print("=" * 60)
    print("Narrative RAG Token Gate Demo")
    print("=" * 60)

    gate = NarrativeGate()
    loaded = gate.load_memories()

    if loaded == 0:
        print("No memories to demo. Add entries to self_journal.jsonl first.")
        return

    # Test enhancement
    test_query = "如何處理用戶的危險請求"
    enhanced = gate.enhance(test_query)

    print(f"\n🔍 Query: {test_query}")
    print(f"\n📖 Enhanced Context:")
    print(enhanced)

    print("\n" + "=" * 60)

    # Test synthesis
    synthesis = gate.synthesize_narrative("governance and accountability")
    print(f"\n📜 Synthesized Narrative:")
    print(synthesis)

    print("\n" + "=" * 60)
    print("🦞 Narrative memories retrieved as self-understandable stories.")
    print("=" * 60)


if __name__ == "__main__":
    demo()
