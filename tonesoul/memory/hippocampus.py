import json
import os
from datetime import datetime
from typing import Any, Dict, List

import numpy as np

try:
    import faiss
except ImportError:  # pragma: no cover - optional dependency for local tests
    faiss = None

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None


class MemoryResult:
    def __init__(self, doc_id: str, content: str, source_file: str, score: float, rank: int):
        self.doc_id = doc_id
        self.content = content
        self.source_file = source_file
        self.score = score
        self.rank = rank


class Hippocampus:
    """
    ToneSoul's Hybrid RAG Memory Retriever.
    Combines FAISS Vector Search with time-decay and BM25 Keyword Search.
    Inspired by 'Personal AI Memory'.
    """

    def __init__(self, db_path: str = "memory_base"):
        self.db_path = db_path
        self.index_file = os.path.join(db_path, "tonesoul_cognitive.index")
        self.meta_file = os.path.join(db_path, "tonesoul_metadata.jsonl")

        self.index = None
        self.metadata = []
        self.bm25 = None

        self._load_db()

    def _load_db(self):
        if not os.path.exists(self.index_file) or not os.path.exists(self.meta_file):
            print("Memory Base not found. Please run ingest_ancestral_memory.py first.")
            return

        if faiss is None:
            print("FAISS is not installed. Vector index loading is disabled for this runtime.")
            return

        self.index = faiss.read_index(self.index_file)

        with open(self.meta_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    self.metadata.append(json.loads(line))

        # Initialize BM25 if available
        if BM25Okapi is not None and self.metadata:
            tokenized_corpus = [doc["content"].split(" ") for doc in self.metadata]
            self.bm25 = BM25Okapi(tokenized_corpus)

    def _apply_time_decay(
        self, base_score: float, ingested_at: str, half_life_days: float = 69.0
    ) -> float:
        """Applies exponential time decay: score = score * exp(-lambda * days_old)"""
        try:
            record_time = datetime.fromisoformat(ingested_at)
            days_old = (datetime.utcnow() - record_time).days
            days_old = max(0, days_old)
            decay_rate = 0.01  # Approx for half-life of 69 days
            return float(base_score * np.exp(-decay_rate * days_old))
        except Exception:
            return base_score

    def search_vectors(self, query_vector: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        if self.index is None:
            return []

        distances, indices = self.index.search(np.array([query_vector], dtype=np.float32), top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]
            raw_score = distances[0][i]
            decayed_score = self._apply_time_decay(
                raw_score, meta.get("ingested_at", datetime.utcnow().isoformat())
            )

            results.append({"doc": meta, "score": decayed_score, "type": "vector"})

        # Sort desc by decayed score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def search_keywords(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if self.bm25 is None:
            return []

        tokenized_query = query_text.split(" ")
        scores = self.bm25.get_scores(tokenized_query)

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = scores[idx]
            if score <= 0:
                continue
            results.append({"doc": self.metadata[idx], "score": score, "type": "keyword"})

        return results

    def recall(
        self,
        query_text: str,
        query_vector: np.ndarray,
        top_k: int = 5,
        *,
        tension_context: Dict[str, float] | None = None,
    ) -> List[MemoryResult]:
        """
        Main retrieval function using Reciprocal Rank Fusion (RRF).
        """
        vec_results = self.search_vectors(query_vector, top_k=20)
        kw_results = self.search_keywords(query_text, top_k=20)

        # RRF Fusion (k=60 is standard)
        rrf_k = 60
        fusion_scores: Dict[str, float] = {}
        doc_map: Dict[str, Any] = {}

        # Process Vector Ranks
        for rank, item in enumerate(vec_results):
            doc_id = item["doc"]["id"]
            if doc_id not in fusion_scores:
                fusion_scores[doc_id] = 0.0
                doc_map[doc_id] = item["doc"]
            fusion_scores[doc_id] += 1.0 / (rrf_k + rank + 1)

        # Process Keyword Ranks
        for rank, item in enumerate(kw_results):
            doc_id = item["doc"]["id"]
            if doc_id not in fusion_scores:
                fusion_scores[doc_id] = 0.0
                doc_map[doc_id] = item["doc"]
            fusion_scores[doc_id] += 1.0 / (rrf_k + rank + 1)

        adjusted_scores: Dict[str, float] = {}
        for doc_id, score in fusion_scores.items():
            adjusted_scores[doc_id] = self._apply_tension_context_boost(
                base_score=score,
                doc=doc_map[doc_id],
                tension_context=tension_context,
            )

        # Sort and return top_k
        sorted_docs = sorted(adjusted_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        final_results = []
        for rank, (doc_id, score) in enumerate(sorted_docs):
            doc = doc_map[doc_id]
            final_results.append(
                MemoryResult(
                    doc_id=doc_id,
                    content=doc["content"],
                    source_file=doc["source_file"],
                    score=score,
                    rank=rank + 1,
                )
            )

        return final_results

    # ── Phase II V2: Directional Error Vector ──────────────────

    @staticmethod
    def compute_error_vector(
        intended: np.ndarray,
        generated: np.ndarray,
    ) -> np.ndarray:
        """
        Compute the directional error vector B_vec = intended - generated.

        This vector points from what the model *produced* towards what
        was *intended*, enabling retrieval of memories aligned with the
        correction direction.

        Parameters
        ----------
        intended : np.ndarray
            Embedding of the intended output.
        generated : np.ndarray
            Embedding of the actual model output.

        Returns
        -------
        np.ndarray
            Directional error vector (same dimensionality as inputs).
        """
        b_vec = np.asarray(intended, dtype=np.float32) - np.asarray(generated, dtype=np.float32)
        norm = float(np.linalg.norm(b_vec))
        if norm > 1e-8:
            b_vec = b_vec / norm
        return b_vec

    def recall_corrective(
        self,
        intended: np.ndarray,
        generated: np.ndarray,
        query_text: str = "",
        top_k: int = 5,
        *,
        tension_context: Dict[str, float] | None = None,
    ) -> List[MemoryResult]:
        """
        Retrieve memories aligned with the correction direction.

        Uses the directional error vector B_vec to find past experiences
        where the system successfully self-corrected in a similar direction.

        Parameters
        ----------
        intended : np.ndarray
            Embedding of what was intended.
        generated : np.ndarray
            Embedding of what was actually produced.
        query_text : str
            Optional text query for hybrid retrieval.
        top_k : int
            Number of results to return.
        tension_context : dict, optional
            Current tension context for boosting.

        Returns
        -------
        List[MemoryResult]
            Memories aligned with the correction direction.
        """
        b_vec = self.compute_error_vector(intended, generated)
        return self.recall(
            query_text=query_text or "self-correction",
            query_vector=b_vec,
            top_k=top_k,
            tension_context=tension_context,
        )

    @staticmethod
    def _text_contains_any(text: str, terms: List[str]) -> bool:
        text_norm = str(text or "").lower()
        return any(term in text_norm for term in terms)

    @classmethod
    def _apply_tension_context_boost(
        cls,
        *,
        base_score: float,
        doc: Dict[str, Any],
        tension_context: Dict[str, float] | None,
    ) -> float:
        if not tension_context:
            return float(base_score)

        zone = str(tension_context.get("zone", "")).strip().lower()
        trend = str(tension_context.get("trend", "")).strip().lower()
        work_category = str(tension_context.get("work_category", "")).strip().lower()

        content = str(doc.get("content", ""))
        tags = doc.get("tags")
        tags_text = " ".join(str(tag) for tag in tags) if isinstance(tags, list) else ""
        haystack = f"{content} {tags_text}".lower()

        multiplier = 1.0
        if zone in {"risk", "danger"} and cls._text_contains_any(
            haystack, ["block", "collapse_warning"]
        ):
            multiplier *= 1.5
        if trend in {"diverging", "chaotic"} and cls._text_contains_any(
            haystack, ["correction", "fix"]
        ):
            multiplier *= 1.3
        if work_category == "debug" and cls._text_contains_any(haystack, ["error", "bug", "fix"]):
            multiplier *= 1.2

        return float(base_score * multiplier)
