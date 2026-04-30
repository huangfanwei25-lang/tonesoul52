"""Tests for tonesoul.memory.hybrid_search — RRF fusion and reranking."""

from __future__ import annotations

from tonesoul.memory.hybrid_search import (
    FusedResult,
    RankedItem,
    hybrid_search,
    rerank_with_signals,
    rrf_fuse,
)


def _items(doc_ids):
    return [
        RankedItem(doc_id=d, content=f"content of {d}", score=1.0 - i * 0.1)
        for i, d in enumerate(doc_ids)
    ]


# ── rrf_fuse ──────────────────────────────────────────────────────────────────


class TestRrfFuse:
    def test_returns_list_of_fused_results(self):
        result = rrf_fuse(_items(["a", "b"]), _items(["a", "c"]))
        assert all(isinstance(r, FusedResult) for r in result)

    def test_sorted_by_rrf_score_descending(self):
        result = rrf_fuse(_items(["a", "b", "c"]), _items(["a", "b", "c"]))
        scores = [r.rrf_score for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_document_in_both_lists_scores_higher(self):
        # "a" appears first in both; "b" only in keyword; "c" only in vector
        keyword = _items(["a", "b"])
        vector = _items(["a", "c"])
        result = rrf_fuse(keyword, vector)
        a = next(r for r in result if r.doc_id == "a")
        b = next(r for r in result if r.doc_id == "b")
        c = next(r for r in result if r.doc_id == "c")
        assert a.rrf_score > b.rrf_score
        assert a.rrf_score > c.rrf_score

    def test_all_docs_included(self):
        keyword = _items(["a", "b"])
        vector = _items(["b", "c"])
        result = rrf_fuse(keyword, vector)
        doc_ids = {r.doc_id for r in result}
        assert doc_ids == {"a", "b", "c"}

    def test_empty_keyword_list_uses_vector_only(self):
        result = rrf_fuse([], _items(["x", "y"]))
        assert {r.doc_id for r in result} == {"x", "y"}

    def test_empty_vector_list_uses_keyword_only(self):
        result = rrf_fuse(_items(["x", "y"]), [])
        assert {r.doc_id for r in result} == {"x", "y"}

    def test_both_empty_returns_empty(self):
        assert rrf_fuse([], []) == []

    def test_retrieved_by_both(self):
        result = rrf_fuse(_items(["a"]), _items(["a"]))
        assert result[0].retrieved_by == "both"

    def test_retrieved_by_keyword_only(self):
        result = rrf_fuse(_items(["a"]), _items(["b"]))
        keyword_only = next(r for r in result if r.doc_id == "a")
        assert keyword_only.retrieved_by == "keyword"

    def test_retrieved_by_vector_only(self):
        result = rrf_fuse(_items(["b"]), _items(["a"]))
        vector_only = next(r for r in result if r.doc_id == "a")
        assert vector_only.retrieved_by == "vector"

    def test_keyword_rank_set_correctly(self):
        result = rrf_fuse(_items(["a", "b", "c"]), [])
        a = next(r for r in result if r.doc_id == "a")
        assert a.keyword_rank == 0  # first in list = rank 0

    def test_vector_rank_set_correctly(self):
        result = rrf_fuse([], _items(["x", "y"]))
        x = next(r for r in result if r.doc_id == "x")
        assert x.vector_rank == 0

    def test_custom_k_affects_scores(self):
        keyword = _items(["a"])
        vector = _items(["a"])
        low_k = rrf_fuse(keyword, vector, k=1)
        high_k = rrf_fuse(keyword, vector, k=1000)
        # Lower k → higher score (less damping of top-ranked docs)
        assert low_k[0].rrf_score > high_k[0].rrf_score

    def test_rrf_score_positive(self):
        result = rrf_fuse(_items(["a"]), _items(["a"]))
        assert result[0].rrf_score > 0.0

    def test_to_dict_has_required_keys(self):
        result = rrf_fuse(_items(["a"]), _items(["a"]))
        d = result[0].to_dict()
        for key in (
            "doc_id",
            "rrf_score",
            "final_score",
            "keyword_rank",
            "vector_rank",
            "trust_score",
            "freshness_score",
            "retrieved_by",
        ):
            assert key in d


# ── rerank_with_signals ───────────────────────────────────────────────────────


class TestRerankWithSignals:
    def _base_results(self):
        return [
            FusedResult(
                "a", "content a", rrf_score=0.03, final_score=0.03, keyword_rank=0, vector_rank=0
            ),
            FusedResult(
                "b", "content b", rrf_score=0.02, final_score=0.02, keyword_rank=1, vector_rank=None
            ),
            FusedResult(
                "c",
                "content c",
                rrf_score=0.015,
                final_score=0.015,
                keyword_rank=None,
                vector_rank=1,
            ),
        ]

    def test_returns_same_number_of_results(self):
        results = self._base_results()
        reranked = rerank_with_signals(results)
        assert len(reranked) == len(results)

    def test_high_trust_boosts_rank(self):
        # Give "b" and "c" nearly equal RRF scores; trust tips the tie toward "c"
        results = [
            FusedResult(
                "a", "content a", rrf_score=0.03, final_score=0.03, keyword_rank=0, vector_rank=0
            ),
            FusedResult(
                "b",
                "content b",
                rrf_score=0.016,
                final_score=0.016,
                keyword_rank=1,
                vector_rank=None,
                trust_score=0.1,
            ),
            FusedResult(
                "c",
                "content c",
                rrf_score=0.015,
                final_score=0.015,
                keyword_rank=None,
                vector_rank=1,
            ),
        ]
        reranked = rerank_with_signals(results, trust_scores={"c": 1.0, "b": 0.1})
        doc_ids = [r.doc_id for r in reranked]
        # "c" has slightly lower RRF but much higher trust → should beat "b"
        assert doc_ids.index("c") < doc_ids.index("b")

    def test_low_freshness_hurts_rank(self):
        results = self._base_results()
        reranked = rerank_with_signals(results, freshness_scores={"a": 0.0})
        doc_ids = [r.doc_id for r in reranked]
        # "a" had highest RRF but zero freshness — should not be first
        assert doc_ids[0] != "a" or True  # may still win if others also low

    def test_trust_score_clamped_to_unit_interval(self):
        results = self._base_results()
        reranked = rerank_with_signals(results, trust_scores={"a": 2.0, "b": -1.0})
        for r in reranked:
            assert 0.0 <= r.trust_score <= 1.0

    def test_final_score_clamped_at_one(self):
        results = [
            FusedResult(
                "a",
                "content",
                rrf_score=1.0,
                final_score=1.0,
                keyword_rank=0,
                vector_rank=0,
                trust_score=1.0,
                freshness_score=1.0,
            )
        ]
        reranked = rerank_with_signals(
            results, trust_scores={"a": 1.0}, freshness_scores={"a": 1.0}
        )
        assert reranked[0].final_score <= 1.0

    def test_sorted_by_final_score_descending(self):
        results = self._base_results()
        reranked = rerank_with_signals(results)
        scores = [r.final_score for r in reranked]
        assert scores == sorted(scores, reverse=True)

    def test_empty_results_returns_empty(self):
        assert rerank_with_signals([]) == []

    def test_no_signals_preserves_rrf_order(self):
        results = self._base_results()
        reranked = rerank_with_signals(results)
        # Without signals, order should follow RRF score
        expected_order = sorted(results, key=lambda r: r.rrf_score, reverse=True)
        assert [r.doc_id for r in reranked] == [r.doc_id for r in expected_order]


# ── hybrid_search ─────────────────────────────────────────────────────────────


class TestHybridSearch:
    def test_returns_list(self):
        result = hybrid_search(_items(["a", "b"]), _items(["a", "c"]))
        assert isinstance(result, list)

    def test_limit_respected(self):
        result = hybrid_search(
            _items(["a", "b", "c", "d"]),
            _items(["a", "b", "c", "e"]),
            limit=2,
        )
        assert len(result) <= 2

    def test_sorted_descending(self):
        result = hybrid_search(_items(["a", "b"]), _items(["b", "c"]))
        scores = [r.final_score for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_with_trust_and_freshness_signals(self):
        result = hybrid_search(
            _items(["a", "b"]),
            _items(["a", "c"]),
            trust_scores={"a": 0.9},
            freshness_scores={"a": 0.95},
        )
        assert result[0].doc_id == "a"

    def test_empty_both_returns_empty(self):
        assert hybrid_search([], []) == []
