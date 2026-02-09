"""
Build Semantic Index for ToneSoul Memory
=========================================

One-time script to build the initial FAISS index from self_journal.jsonl.
Run this after installing sentence-transformers and faiss-cpu.

Usage:
    python scripts/build_semantic_index.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    from apps.core.memory_semantic_search import SemanticMemorySearch

    print("=" * 60)
    print("ToneSoul - Building Semantic Memory Index")
    print("=" * 60)

    # Initialize searcher
    print("\n🔧 Initializing semantic search system...")
    searcher = SemanticMemorySearch()

    # Build index
    print("\n📚 Building index from self_journal.jsonl...")
    print("(First run will download BGE model ~100MB)")
    searcher.index_journal(force_rebuild=True)

    # Verify
    print("\n✅ Index built successfully!")
    print(f"📊 Indexed {len(searcher.memories)} memories")
    print("📂 Index saved to: memory/.semantic_index/")

    # Quick test
    print("\n🔍 Testing semantic search...")
    test_query = "我應該拒絕危險的內容"
    results = searcher.search(test_query, k=3)

    print(f"\nQuery: '{test_query}'")
    print(f"Found {len(results)} similar memories:\n")

    for i, result in enumerate(results, 1):
        print(
            f"{i}. Distance: {result['distance']:.3f} | Similarity: {result['similarity_score']:.3f}"
        )
        stmt = result["memory"].get("statement", "N/A")
        print(f"   Statement: {stmt[:80]}...")
        print()

    print("=" * 60)
    print("✅ Semantic memory system ready!")
    print("=" * 60)


if __name__ == "__main__":
    main()
