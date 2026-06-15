# DORMANT (as of 2026-06-15): RRF fusion layer for hybrid keyword+vector search; designed to work with hippocampus but never wired — all production memory calls use direct hippocampus/semantic_graph/visual_chain, not fusion pipeline. Test-only import (tests/test_memory_hybrid_search.py); see docs/architecture/architecture_legibility_2026-06-15.md
"""Hybrid search with Reciprocal Rank Fusion (RRF).

Two search modalities solve different problems:
  Keyword search   — precise term matching, good for known names and exact phrases
  Vector search    — semantic similarity, good for paraphrases and concept neighbors

Neither alone is sufficient. Keyword misses synonyms; vector misses exact terms.
RRF fuses ranked lists from both by giving each document a score based on its
*rank position*, not its raw similarity score. This makes the two modalities
commensurable even when their scales are incompatible.

RRF formula:
  score(d) = Σ_i  1 / (k + rank_i(d))

  where k=60 is a stability constant that prevents high-rank documents
  from dominating when only one modality retrieved them. A document
  ranked 1st by both modalities scores ~2/61 ≈ 0.033; one ranked 1st
  by only one modality scores ~1/61 ≈ 0.016.

Reranking layer (optional):
  After RRF fusion, scores are adjusted by secondary signals:
    trust_weight    (0.15) — source reliability, from governance trust scores
    freshness_weight (0.15) — zone freshness, from memory/freshness.py
    graph_bonus      (0.10) — graph depth, if the result is a graph-expanded neighbor

  Weights are deliberately modest. RRF's rank signal should dominate;
  the secondary signals break ties and surface well-trusted results
  when RRF scores are close.

Relationship to Hippocampus:
  Hippocampus already wraps FAISS (vector) and BM25 (keyword) but calls them
  independently. This module provides the RRF fusion layer that combines their
  ranked outputs into a single coherent result list, plus the reranking step
  that incorporates trust and freshness signals from the governance layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

__ts_layer__ = "memory"
__ts_purpose__ = (
    "Hybrid search: fuse keyword and vector ranked lists via Reciprocal Rank Fusion, "
    "then rerank with trust and freshness signals."
)

# RRF stability constant — higher k = less aggressive rank fusion
RRF_K: int = 60

# Reranking signal weights (must sum to ≤ 1.0 after base_weight)
_BASE_WEIGHT: float = 0.60
_TRUST_WEIGHT: float = 0.15
_FRESHNESS_WEIGHT: float = 0.15
_GRAPH_BONUS_MAX: float = 0.10


# ── Data structures ───────────────────────────────────────────────────────────


@dataclass
class RankedItem:
    """A single item from a single-modality ranked list."""

    doc_id: str
    content: str = ""
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FusedResult:
    """A document after RRF fusion, carrying provenance from both modalities."""

    doc_id: str
    content: str
    rrf_score: float
    final_score: float  # after reranking; equals rrf_score if no reranking
    keyword_rank: Optional[int]  # None if not in keyword results
    vector_rank: Optional[int]  # None if not in vector results
    trust_score: float = 0.5
    freshness_score: float = 1.0
    graph_depth: int = 0  # 0 = direct hit; >0 = graph-expanded neighbor
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def retrieved_by(self) -> str:
        if self.keyword_rank is not None and self.vector_rank is not None:
            return "both"
        if self.keyword_rank is not None:
            return "keyword"
        return "vector"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content": self.content[:200],  # truncate for logging
            "rrf_score": round(self.rrf_score, 6),
            "final_score": round(self.final_score, 6),
            "keyword_rank": self.keyword_rank,
            "vector_rank": self.vector_rank,
            "trust_score": round(self.trust_score, 4),
            "freshness_score": round(self.freshness_score, 4),
            "graph_depth": self.graph_depth,
            "retrieved_by": self.retrieved_by,
        }


# ── RRF fusion ────────────────────────────────────────────────────────────────


def rrf_fuse(
    keyword_results: List[RankedItem],
    vector_results: List[RankedItem],
    *,
    k: int = RRF_K,
) -> List[FusedResult]:
    """Fuse two ranked lists using Reciprocal Rank Fusion.

    Both lists should be ordered best-first. The output is ordered by
    fused RRF score, descending.

    Documents that appear in only one list still receive an RRF score
    (from that single rank), so no results are silently dropped.
    """
    # Build rank index: doc_id → (0-indexed rank, item)
    keyword_index: Dict[str, Tuple[int, RankedItem]] = {
        item.doc_id: (rank, item) for rank, item in enumerate(keyword_results)
    }
    vector_index: Dict[str, Tuple[int, RankedItem]] = {
        item.doc_id: (rank, item) for rank, item in enumerate(vector_results)
    }

    all_doc_ids = set(keyword_index) | set(vector_index)

    fused: List[FusedResult] = []
    for doc_id in all_doc_ids:
        k_entry = keyword_index.get(doc_id)
        v_entry = vector_index.get(doc_id)

        # RRF score is the sum of 1/(k + 1 + rank) for each modality
        # Using 1-indexed rank: rank 0 → position 1 → 1/(k+1)
        rrf_score = 0.0
        if k_entry is not None:
            rrf_score += 1.0 / (k + 1 + k_entry[0])
        if v_entry is not None:
            rrf_score += 1.0 / (k + 1 + v_entry[0])

        # Prefer the richer item (vector results often carry more metadata)
        source_item = (v_entry or k_entry)[1]

        fused.append(
            FusedResult(
                doc_id=doc_id,
                content=source_item.content,
                rrf_score=round(rrf_score, 6),
                final_score=round(rrf_score, 6),
                keyword_rank=k_entry[0] if k_entry else None,
                vector_rank=v_entry[0] if v_entry else None,
                metadata=source_item.metadata,
            )
        )

    return sorted(fused, key=lambda r: r.rrf_score, reverse=True)


# ── Reranking ─────────────────────────────────────────────────────────────────


def rerank_with_signals(
    results: List[FusedResult],
    *,
    trust_scores: Optional[Dict[str, float]] = None,
    freshness_scores: Optional[Dict[str, float]] = None,
    graph_depths: Optional[Dict[str, int]] = None,
) -> List[FusedResult]:
    """Rerank fused results by incorporating trust, freshness, and graph signals.

    RRF score contributes _BASE_WEIGHT (0.60) of the final score.
    Secondary signals share the remaining 0.40, weighted as configured.

    All input scores are expected to be in [0.0, 1.0]. Out-of-range values
    are clamped silently.
    """
    trust = trust_scores or {}
    freshness = freshness_scores or {}
    depths = graph_depths or {}

    # Normalize RRF scores to [0, 1] range across this result set
    max_rrf = max((r.rrf_score for r in results), default=1.0)
    if max_rrf == 0.0:
        max_rrf = 1.0

    reranked: List[FusedResult] = []
    for result in results:
        normalized_rrf = result.rrf_score / max_rrf

        t = max(0.0, min(1.0, trust.get(result.doc_id, result.trust_score)))
        f = max(0.0, min(1.0, freshness.get(result.doc_id, result.freshness_score)))
        depth = depths.get(result.doc_id, result.graph_depth)
        # Graph bonus: direct hits get full bonus, neighbors get decayed bonus
        graph_bonus = _GRAPH_BONUS_MAX / (1 + depth) if depth >= 0 else 0.0

        final = (
            _BASE_WEIGHT * normalized_rrf + _TRUST_WEIGHT * t + _FRESHNESS_WEIGHT * f + graph_bonus
        )

        reranked.append(
            FusedResult(
                doc_id=result.doc_id,
                content=result.content,
                rrf_score=result.rrf_score,
                final_score=round(min(1.0, final), 6),
                keyword_rank=result.keyword_rank,
                vector_rank=result.vector_rank,
                trust_score=t,
                freshness_score=f,
                graph_depth=depth,
                metadata=result.metadata,
            )
        )

    return sorted(reranked, key=lambda r: r.final_score, reverse=True)


# ── Convenience ───────────────────────────────────────────────────────────────


def hybrid_search(
    keyword_results: List[RankedItem],
    vector_results: List[RankedItem],
    *,
    k: int = RRF_K,
    trust_scores: Optional[Dict[str, float]] = None,
    freshness_scores: Optional[Dict[str, float]] = None,
    graph_depths: Optional[Dict[str, int]] = None,
    limit: int = 10,
) -> List[FusedResult]:
    """Fuse and rerank in one call. Returns top ``limit`` results."""
    fused = rrf_fuse(keyword_results, vector_results, k=k)
    if trust_scores or freshness_scores or graph_depths:
        fused = rerank_with_signals(
            fused,
            trust_scores=trust_scores,
            freshness_scores=freshness_scores,
            graph_depths=graph_depths,
        )
    return fused[:limit]
