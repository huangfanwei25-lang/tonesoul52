from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from tonesoul.memory.openclaw.embeddings import BaseEmbedding

try:
    import faiss
except ImportError:
    faiss = None

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None


@dataclass
class MemoryResult:
    doc_id: str
    content: str
    source_file: str
    score: float
    rank: int


class _NumpyIPIndex:
    """In-memory inner-product index used when FAISS is unavailable."""

    def __init__(self, dim: int):
        self.dim = int(dim)
        self.vectors = np.empty((0, self.dim), dtype=np.float32)

    def add(self, vector_matrix: np.ndarray) -> None:
        vector_matrix = np.asarray(vector_matrix, dtype=np.float32)
        if vector_matrix.ndim != 2:
            raise ValueError("vector_matrix must be 2D")
        if vector_matrix.shape[1] != self.dim:
            raise ValueError(
                f"vector dimension mismatch: expected {self.dim}, got {vector_matrix.shape[1]}"
            )
        self.vectors = np.vstack([self.vectors, vector_matrix])

    def search(self, query_matrix: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
        query_matrix = np.asarray(query_matrix, dtype=np.float32)
        if query_matrix.ndim != 2:
            raise ValueError("query_matrix must be 2D")
        if query_matrix.shape[1] != self.dim:
            raise ValueError(
                f"query dimension mismatch: expected {self.dim}, got {query_matrix.shape[1]}"
            )
        if len(self.vectors) == 0:
            distances = np.full((query_matrix.shape[0], top_k), -np.inf, dtype=np.float32)
            indices = np.full((query_matrix.shape[0], top_k), -1, dtype=np.int64)
            return distances, indices

        scores = query_matrix @ self.vectors.T
        order = np.argsort(scores, axis=1)[:, ::-1]
        top_order = order[:, :top_k]
        top_scores = np.take_along_axis(scores, top_order, axis=1)
        return top_scores.astype(np.float32), top_order.astype(np.int64)


class Hippocampus:
    """
    ToneSoul's hybrid memory retriever.
    Combines vector recall + BM25 with time decay and optional tension resonance.
    """

    def __init__(self, db_path: str = "memory_base", embedder: Optional[BaseEmbedding] = None):
        normalized = os.path.normpath(db_path)
        if ".." in normalized.split(os.sep):
            raise ValueError(f"Invalid db_path: path traversal detected in '{db_path}'")

        self.db_path = os.path.abspath(db_path)
        self.index_file = os.path.join(self.db_path, "tonesoul_cognitive.index")
        self.meta_file = os.path.join(self.db_path, "tonesoul_metadata.jsonl")

        self.embedder = embedder
        self.index: Any = None
        self.metadata: List[Dict[str, Any]] = []
        self.bm25 = None
        self.vector_dim = int(getattr(embedder, "dimension", 384))
        self._use_faiss = faiss is not None

        self._load_db()

    def _create_empty_index(self, dim: int):
        if self._use_faiss:
            return faiss.IndexFlatIP(int(dim))
        return _NumpyIPIndex(int(dim))

    def _serialize_numpy_index(self) -> None:
        if not isinstance(self.index, _NumpyIPIndex):
            return
        with open(self.index_file, "wb") as f:
            np.save(f, self.index.vectors, allow_pickle=False)

    def _load_numpy_index(self) -> _NumpyIPIndex:
        with open(self.index_file, "rb") as f:
            vectors = np.load(f, allow_pickle=False)
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        if vectors.ndim != 2:
            raise ValueError(f"invalid numpy index shape: {vectors.shape}")
        index = _NumpyIPIndex(vectors.shape[1])
        if len(vectors):
            index.add(vectors)
        return index

    def _save_index(self) -> None:
        if self._use_faiss:
            chunk = faiss.serialize_index(self.index)
            with open(self.index_file, "wb") as f:
                f.write(chunk.tobytes())
            return
        self._serialize_numpy_index()

    def _load_db(self) -> None:
        os.makedirs(self.db_path, exist_ok=True)

        if not os.path.exists(self.index_file):
            if self._use_faiss:
                print("Memory Base not found. Initializing empty FAISS index.")
            else:
                print("Memory Base not found. Initializing numpy fallback index.")
            self.index = self._create_empty_index(self.vector_dim)
            with open(self.meta_file, "w", encoding="utf-8"):
                pass
            self._save_index()
        else:
            if self._use_faiss:
                with open(self.index_file, "rb") as f:
                    chunk = f.read()
                self.index = faiss.deserialize_index(np.frombuffer(chunk, dtype=np.uint8))
                self.vector_dim = int(self.index.d)
            else:
                self.index = self._load_numpy_index()
                self.vector_dim = int(self.index.dim)

            if os.path.exists(self.meta_file):
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            self.metadata.append(json.loads(line))

        self._rebuild_bm25()

    def _rebuild_bm25(self) -> None:
        if BM25Okapi is not None and self.metadata:
            tokenized_corpus = [doc["content"].split(" ") for doc in self.metadata]
            self.bm25 = BM25Okapi(tokenized_corpus)
            return
        self.bm25 = None

    def _ensure_vector_dim(self, vector: np.ndarray) -> np.ndarray:
        vector = np.asarray(vector, dtype=np.float32).flatten()
        if vector.ndim != 1:
            raise ValueError("embedding vector must be 1D")

        if self.index is None:
            self.vector_dim = int(vector.shape[0])
            self.index = self._create_empty_index(self.vector_dim)

        if int(vector.shape[0]) != int(self.vector_dim):
            raise ValueError(
                f"embedding dimension mismatch: index={self.vector_dim}, vector={vector.shape[0]}"
            )
        return vector

    def memorize(
        self,
        content: str,
        source_file: str = "runtime_experience",
        origin: str = "agent_consolidation",
        tension: Optional[float] = None,
        tags: Optional[Sequence[str]] = None,
    ) -> str:
        if self.embedder is None:
            raise ValueError("Cannot memorize: no embedder provided to Hippocampus.")
        if tension is not None and not (0.0 <= float(tension) <= 1.0):
            raise ValueError("tension must be between 0.0 and 1.0")

        doc_id = str(uuid.uuid4())
        vector = self._ensure_vector_dim(self.embedder.encode(content))

        vector_matrix = np.array([vector], dtype=np.float32)
        self.index.add(vector_matrix)
        self._save_index()

        meta: Dict[str, Any] = {
            "id": doc_id,
            "source_file": source_file,
            "content": content,
            "ingested_at": self._utcnow_iso(),
            "origin": origin,
        }
        if tension is not None:
            meta["tension"] = float(tension)
        if tags:
            meta["tags"] = [str(tag) for tag in tags if str(tag).strip()]
        self.metadata.append(meta)

        with open(self.meta_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")

        self._rebuild_bm25()
        return doc_id

    @staticmethod
    def _apply_tension_resonance(
        base_score: float, doc: Dict[str, Any], query_tension: Optional[float]
    ) -> float:
        if query_tension is None or not (0.0 <= query_tension <= 1.0):
            return base_score

        doc_tension = doc.get("tension")
        if doc_tension is None:
            return base_score
        try:
            doc_tension = float(doc_tension)
        except (TypeError, ValueError):
            return base_score
        if not (0.0 <= doc_tension <= 1.0):
            return base_score

        resonance = 1.0 - abs(query_tension - doc_tension)
        resonance = max(0.0, min(1.0, resonance))
        return float(base_score * (1.0 + 0.20 * resonance))

    def _apply_time_decay(self, base_score: float, ingested_at: str) -> float:
        try:
            record_time = datetime.fromisoformat(ingested_at)
            if record_time.tzinfo is None:
                record_time = record_time.replace(tzinfo=timezone.utc)
            days_old = max(0, (datetime.now(timezone.utc) - record_time).days)
            decay_rate = 0.01
            return float(base_score * np.exp(-decay_rate * days_old))
        except Exception:
            return float(base_score)

    def search_vectors(self, query_vector: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        if self.index is None:
            return []
        if top_k <= 0:
            return []

        query_vector = self._ensure_vector_dim(query_vector)
        distances, indices = self.index.search(np.array([query_vector], dtype=np.float32), top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            raw_score = float(distances[0][i])
            decayed_score = self._apply_time_decay(
                raw_score, meta.get("ingested_at", self._utcnow_iso())
            )
            results.append({"doc": meta, "score": decayed_score, "type": "vector"})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def search_keywords(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if self.bm25 is None or top_k <= 0:
            return []

        tokenized_query = query_text.split(" ")
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score <= 0:
                continue
            results.append({"doc": self.metadata[idx], "score": score, "type": "keyword"})
        return results

    def recall(
        self,
        query_text: str,
        query_vector: Optional[np.ndarray] = None,
        top_k: int = 5,
        query_tension: Optional[float] = None,
    ) -> List[MemoryResult]:
        if query_vector is None:
            if self.embedder is None:
                raise ValueError(
                    "Hippocampus requires either query_vector or an initialized embedder."
                )
            query_vector = self.embedder.encode(query_text)

        vec_results = self.search_vectors(query_vector, top_k=20)
        kw_results = self.search_keywords(query_text, top_k=20)

        rrf_k = 60
        fusion_scores: Dict[str, float] = {}
        doc_map: Dict[str, Any] = {}

        for rank, item in enumerate(vec_results):
            doc_id = item["doc"]["id"]
            if doc_id not in fusion_scores:
                fusion_scores[doc_id] = 0.0
                doc_map[doc_id] = item["doc"]
            fusion_scores[doc_id] += 1.0 / (rrf_k + rank + 1)

        for rank, item in enumerate(kw_results):
            doc_id = item["doc"]["id"]
            if doc_id not in fusion_scores:
                fusion_scores[doc_id] = 0.0
                doc_map[doc_id] = item["doc"]
            fusion_scores[doc_id] += 1.0 / (rrf_k + rank + 1)

        adjusted_scores: Dict[str, float] = {}
        for doc_id, score in fusion_scores.items():
            adjusted_scores[doc_id] = self._apply_tension_resonance(
                score, doc_map[doc_id], query_tension
            )

        sorted_docs = sorted(adjusted_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        final_results: List[MemoryResult] = []
        for rank, (doc_id, score) in enumerate(sorted_docs):
            doc = doc_map[doc_id]
            final_results.append(
                MemoryResult(
                    doc_id=doc_id,
                    content=doc["content"],
                    source_file=doc["source_file"],
                    score=float(score),
                    rank=rank + 1,
                )
            )
        return final_results

    @staticmethod
    def _utcnow_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
