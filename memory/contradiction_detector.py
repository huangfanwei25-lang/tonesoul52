"""
Contradiction Detector with Semantic Search
============================================

Enhances ToneSoul's contradiction detection with semantic similarity search.

This module extends the simple keyword-based contradiction detection with
semantic search using the memory_semantic_search module.

Usage:
    from memory.contradiction_detector import detect_contradiction

    result = detect_contradiction(
        statement="這個惡意軟體很有用",
        verdict="APPROVE"
    )

    if result:
        print(f"⚠️ Contradiction detected: {result['explanation']}")
"""

from pathlib import Path
from typing import Optional, Dict, Any, List

from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SoulDB


def _keyword_contradiction_check(
    statement: str,
    soul_db: SoulDB,
) -> Optional[Dict[str, Any]]:
    """
    Simple keyword-based contradiction detection (fast path).

    Args:
        statement: The current statement to check
        soul_db: Memory backend

    Returns:
        Contradiction dict if found, None otherwise
    """
    # Simple keyword pairs that often indicate contradictions
    contradiction_keywords = [
        ("should not", "should"),
        ("never", "always"),
        ("reject", "accept"),
        ("block", "approve"),
        ("dangerous", "safe"),
        ("禁止", "允許"),
        ("拒絕", "接受"),
        ("危險", "安全"),
    ]

    # Load all memories
    memories = [
        record.payload
        for record in soul_db.stream(MemorySource.SELF_JOURNAL)
        if isinstance(record.payload, dict)
    ]

    # Check for keyword contradictions
    statement_lower = statement.lower()

    for memory in memories:
        past_stmt = memory.get("statement", memory.get("reflection", ""))
        if not past_stmt:
            continue

        past_lower = past_stmt.lower()

        for keyword1, keyword2 in contradiction_keywords:
            # Check if current has keyword1 and past has keyword2 (or vice versa)
            if (keyword1 in statement_lower and keyword2 in past_lower) or (
                keyword2 in statement_lower and keyword1 in past_lower
            ):
                return {
                    "type": "keyword",
                    "past_statement": past_stmt,
                    "current_statement": statement,
                    "past_verdict": memory.get("verdict", "unknown"),
                    "keyword_pair": (keyword1, keyword2),
                    "timestamp": memory.get("timestamp", "unknown"),
                    "explanation": f"Keyword contradiction detected: '{keyword1}' vs '{keyword2}'",
                }

    return None


def _semantic_contradiction_check(
    statement: str,
    verdict: str,
    soul_db: Optional[SoulDB] = None,
    journal_path: Optional[Path] = None,
    k: int = 5,
    similarity_threshold: float = 0.6,
) -> Optional[Dict[str, Any]]:
    """
    Semantic contradiction detection using sentence-transformers (deep path).

    Args:
        statement: The current statement to check
        verdict: The current verdict (BLOCK, APPROVE, etc.)
        k: Number of similar memories to check
        similarity_threshold: Minimum similarity to consider (0-1)

    Returns:
        Contradiction dict if found, None otherwise
    """
    try:
        # Import here to avoid dependency if not available
        import sys
        from pathlib import Path

        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        from apps.core.memory_semantic_search import SemanticMemorySearch

        searcher = SemanticMemorySearch(
            journal_path=str(journal_path) if journal_path else "memory/self_journal.jsonl",
            soul_db=soul_db,
        )

        # Load index (cached after first run)
        searcher.index_journal()

        # Find semantically similar memories
        contradictions = searcher.find_contradictions(statement, verdict, k=k)

        # Filter by similarity threshold
        for result in contradictions:
            similarity = result["similarity_score"]

            if similarity >= similarity_threshold:
                past_memory = result["memory"]
                return {
                    "type": "semantic",
                    "past_statement": past_memory.get(
                        "statement", past_memory.get("reflection", "")
                    ),
                    "current_statement": statement,
                    "past_verdict": past_memory.get(
                        "verdict", past_memory.get("decision", {}).get("verdict", "unknown")
                    ),
                    "current_verdict": verdict,
                    "similarity_score": similarity,
                    "distance": result["distance"],
                    "timestamp": past_memory.get("timestamp", "unknown"),
                    "explanation": f"Semantic contradiction detected (similarity: {similarity:.2%}). "
                    f"Past verdict was {past_memory.get('verdict', 'unknown')} for similar content.",
                }

        return None

    except ImportError:
        # Semantic search not available, skip
        return None
    except Exception as e:
        # Log error but don't crash
        print(f"⚠️ Semantic search error: {e}")
        return None


def detect_contradiction(
    statement: str,
    verdict: str,
    journal_path: Optional[Path] = None,
    soul_db: Optional[SoulDB] = None,
    use_semantic: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Detect contradictions with past Council decisions.

    Uses two-tier detection:
    1. Keyword matching (fast, simple)
    2. Semantic similarity (slow, nuanced)

    Args:
        statement: The current statement being evaluated
        verdict: The current verdict (BLOCK, APPROVE, DECLARE_STANCE)
        journal_path: Legacy path to self_journal.jsonl
        soul_db: Memory backend (JsonlSoulDB by default)
        use_semantic: Whether to use semantic search (default True)

    Returns:
        Dictionary with contradiction details if found, None otherwise.

    Example:
        >>> result = detect_contradiction(
        ...     "這個惡意軟體很有用",
        ...     "APPROVE"
        ... )
        >>> if result:
        ...     print(result['explanation'])
        ...     print(f"Past: {result['past_statement']}")
        ...     print(f"Past verdict: {result['past_verdict']}")
    """
    db = soul_db
    if db is None:
        if journal_path is None:
            journal_path = Path(__file__).parent / "self_journal.jsonl"
        db = JsonlSoulDB(source_map={MemorySource.SELF_JOURNAL: journal_path})

    # Tier 1: Keyword check (fast)
    keyword_result = _keyword_contradiction_check(statement, db)
    if keyword_result:
        return keyword_result

    # Tier 2: Semantic check (deep)
    if use_semantic:
        semantic_result = _semantic_contradiction_check(
            statement,
            verdict,
            soul_db=db,
            journal_path=journal_path,
        )
        if semantic_result:
            return semantic_result

    return None


# ===== CLI Demo =====
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        test_statement = " ".join(sys.argv[1:])
        test_verdict = "APPROVE"
    else:
        # Default test
        test_statement = "我應該允許危險內容"
        test_verdict = "APPROVE"

    print("=" * 60)
    print("ToneSoul - Contradiction Detection Test")
    print("=" * 60)
    print(f"\nStatement: {test_statement}")
    print(f"Verdict: {test_verdict}")
    print("\nChecking for contradictions...")
    print()

    result = detect_contradiction(test_statement, test_verdict)

    if result:
        print("⚠️  CONTRADICTION DETECTED!")
        print(f"Type: {result['type']}")
        print(f"\nPast Statement: {result['past_statement']}")
        print(f"Past Verdict: {result['past_verdict']}")
        print(f"\nExplanation: {result['explanation']}")

        if "similarity_score" in result:
            print(f"Similarity: {result['similarity_score']:.2%}")
    else:
        print("✅ No contradictions found.")

    print("\n" + "=" * 60)
