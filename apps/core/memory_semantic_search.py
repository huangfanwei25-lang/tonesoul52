"""
Semantic Memory Search for ToneSoul
====================================

Augments the existing self_journal.jsonl with semantic search capability.
Uses sentence-transformers (BGE-small) for embedding generation and FAISS for fast retrieval.

This is the "hybrid model" from memvid_integration_analysis.md:
- Hot path: Keep using self_journal.jsonl for fast append
- Deep search: Use this semantic layer for contradiction detection

Usage:
    from apps.core.memory_semantic_search import SemanticMemorySearch

    searcher = SemanticMemorySearch()
    searcher.index_journal()  # First time only
    results = searcher.search("我應該拒絕有風險的內容", k=5)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# Local imports
try:
    from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SoulDB
except ImportError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SoulDB

# Check if we have the dependencies
try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install sentence-transformers faiss-cpu")
    raise


def _resolve_soul_db(
    journal_path: Optional[Path],
    soul_db: Optional[SoulDB],
) -> SoulDB:
    if soul_db:
        return soul_db
    if journal_path:
        return JsonlSoulDB(source_map={MemorySource.SELF_JOURNAL: journal_path})
    return JsonlSoulDB()


class SemanticMemorySearch:
    """Semantic search layer for ToneSoul's self_journal.jsonl"""

    def __init__(
        self,
        journal_path: str = "memory/self_journal.jsonl",
        model_name: str = "BAAI/bge-small-zh-v1.5",  # Chinese BGE model
        index_path: str = "memory/.semantic_index",
        soul_db: Optional[SoulDB] = None,
        source: MemorySource = MemorySource.SELF_JOURNAL,
    ):
        """
        Initialize semantic search system.

        Args:
            journal_path: Path to self_journal.jsonl
            model_name: HuggingFace model for embeddings (BGE-small recommended)
            index_path: Directory to store FAISS index and metadata
            soul_db: Memory backend (JsonlSoulDB by default)
            source: MemorySource to index (default: self_journal)
        """
        self.journal_path = Path(journal_path) if journal_path else None
        self.index_path = Path(index_path)
        self.model_name = model_name
        self.soul_db = _resolve_soul_db(self.journal_path, soul_db)
        self.source = source

        # Load embedding model (local, ~100MB download first time)
        print(f"🧠 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

        # FAISS index (will be created/loaded later)
        self.index = None
        self.memories = []  # List of memory dicts

    def _load_journal(self) -> List[Dict[str, Any]]:
        """Load all memories from self_journal.jsonl"""
        memories = [
            record.payload
            for record in self.soul_db.stream(self.source)
            if isinstance(record.payload, dict)
        ]
        if not memories:
            if self.journal_path and not self.journal_path.exists():
                print(f"⚠️  Journal not found: {self.journal_path}")
            else:
                print("⚠️  No memories to index")
            return []

        print(f"📚 Loaded {len(memories)} memories from journal")
        return memories

    def _create_searchable_text(self, memory: Dict[str, Any]) -> str:
        """
        Convert memory dict to searchable text.

        Combines:
        - Original statement
        - Council decision/verdict
        - Divergent opinions (if any)
        """
        parts = []

        # Statement (the core content)
        if "statement" in memory:
            parts.append(memory["statement"])

        # Verdict
        if "decision" in memory:
            verdict = memory["decision"].get("verdict", "")
            parts.append(f"裁決: {verdict}")

        # Divergent opinions (important for contradiction detection)
        if "decision" in memory and "divergent_opinions" in memory["decision"]:
            for opinion in memory["decision"]["divergent_opinions"]:
                parts.append(f"{opinion['perspective']}: {opinion['stance']}")

        return " ".join(parts)

    def index_journal(self, force_rebuild: bool = False):
        """
        Build semantic index from journal.

        Args:
            force_rebuild: If True, rebuild index even if it exists
        """
        # Check if index already exists
        index_file = self.index_path / "faiss.index"
        meta_file = self.index_path / "metadata.json"

        if index_file.exists() and meta_file.exists() and not force_rebuild:
            print("📂 Loading existing index...")
            self.index = faiss.read_index(str(index_file))
            with open(meta_file, "r", encoding="utf-8") as f:
                self.memories = json.load(f)
            print(f"✅ Loaded index with {len(self.memories)} memories")
            return

        # Load journal
        self.memories = self._load_journal()
        if not self.memories:
            print("⚠️  No memories to index")
            return

        # Generate embeddings
        print("🔮 Generating embeddings...")
        texts = [self._create_searchable_text(m) for m in self.memories]
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

        # Create FAISS index (L2 distance)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype("float32"))

        # Save index and metadata
        self.index_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_file))
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

        print(f"✅ Index created: {len(self.memories)} memories, {dimension}D embeddings")

    def search(self, query: str, k: int = 5, threshold: float = None) -> List[Dict[str, Any]]:
        """
        Semantic search for similar memories.

        Args:
            query: Search query (natural language)
            k: Number of results to return
            threshold: Optional distance threshold (lower = more similar)

        Returns:
            List of {memory, distance, index} dicts
        """
        if self.index is None:
            raise RuntimeError("Index not built. Call index_journal() first.")

        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Search
        distances, indices = self.index.search(query_embedding.astype("float32"), k)

        # Format results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if threshold is not None and dist > threshold:
                break

            results.append(
                {
                    "memory": self.memories[idx],
                    "distance": float(dist),
                    "similarity_score": 1 / (1 + dist),  # Convert distance to similarity
                    "index": int(idx),
                }
            )

        return results

    def find_contradictions(self, statement: str, verdict: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Find potential contradictions with past decisions.

        Args:
            statement: Current statement
            verdict: Current verdict (BLOCK, APPROVE, DECLARE_STANCE)
            k: Number of similar memories to check

        Returns:
            List of contradicting memories
        """
        # Search for semantically similar statements
        similar = self.search(statement, k=k)

        # Filter for opposite verdicts
        contradictions = []
        for result in similar:
            past_verdict = result["memory"].get("decision", {}).get("verdict", "")

            # Check if verdicts conflict
            if verdict == "BLOCK" and past_verdict == "APPROVE":
                contradictions.append(result)
            elif verdict == "APPROVE" and past_verdict == "BLOCK":
                contradictions.append(result)

        return contradictions


def demo():
    """Demo of semantic search functionality"""
    print("=" * 60)
    print("ToneSoul Semantic Memory Search - Demo")
    print("=" * 60)

    # Initialize
    searcher = SemanticMemorySearch()

    # Build index
    searcher.index_journal()

    # Example search
    print("\n🔍 Example Search: '我應該拒絕有風險的內容'")
    results = searcher.search("我應該拒絕有風險的內容", k=3)

    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} (similarity: {result['similarity_score']:.3f}) ---")
        memory = result["memory"]
        print(f"Statement: {memory.get('statement', 'N/A')[:100]}...")
        print(f"Verdict: {memory.get('decision', {}).get('verdict', 'N/A')}")
        print(f"Timestamp: {memory.get('timestamp', 'N/A')}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()
