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
    metadata: Optional[Dict[str, Any]] = None


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
    Combines vector recall + BM25 with time decay and governance-aware reranking.
    """

    VALID_MEMORY_KINDS = {
        "note",
        "fact",
        "decision",
        "constraint",
        "reflection",
        "incident",
        "plan",
    }
    WAVE_KEYS: Tuple[str, ...] = (
        "uncertainty_shift",
        "divergence_shift",
        "risk_shift",
        "revision_shift",
    )
    CORE_WAVE_SCORE_THRESHOLD = 0.40
    HIGH_TENSION_CORE_PRIORITY_THRESHOLD = 0.70
    WAVE_COMPONENT_KEYS: Tuple[str, ...] = (
        "conflict_strength",
        "stance_shift",
        "boundary_cost",
        "consequence_weight",
    )
    WAVE_KIND_PRIORS: Dict[str, float] = {
        "note": 0.30,
        "fact": 0.35,
        "decision": 0.70,
        "constraint": 0.82,
        "reflection": 0.45,
        "incident": 0.88,
        "plan": 0.55,
    }
    BOUNDARY_TAG_PRIORS: Dict[str, float] = {
        "boundary": 0.95,
        "safety": 0.90,
        "guardrail": 0.88,
        "harm_prevention": 0.92,
        "ethics": 0.78,
        "risk": 0.72,
        "incident": 0.80,
        "constraint": 0.74,
    }

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

    @classmethod
    def _validate_memory_kind(cls, memory_kind: str) -> str:
        kind = str(memory_kind).strip().lower()
        if not kind:
            raise ValueError("memory_kind cannot be empty")
        if kind not in cls.VALID_MEMORY_KINDS:
            allowed = ", ".join(sorted(cls.VALID_MEMORY_KINDS))
            raise ValueError(f"memory_kind must be one of: {allowed}")
        return kind

    @classmethod
    def _validate_wave(
        cls, wave: Optional[Dict[str, Any]], field_name: str
    ) -> Optional[Dict[str, float]]:
        if wave is None:
            return None
        if not isinstance(wave, dict):
            raise ValueError(f"{field_name} must be a dict")

        normalized: Dict[str, float] = {}
        for key, value in wave.items():
            if key not in cls.WAVE_KEYS:
                allowed = ", ".join(cls.WAVE_KEYS)
                raise ValueError(
                    f"{field_name} contains unknown key '{key}'. Allowed keys: {allowed}"
                )
            if value is None:
                continue
            numeric = float(value)
            if not (0.0 <= numeric <= 1.0):
                raise ValueError(f"{field_name}.{key} must be between 0.0 and 1.0")
            normalized[key] = numeric
        return normalized or None

    @staticmethod
    def _clamp_unit(value: float) -> float:
        return float(max(0.0, min(1.0, value)))

    @classmethod
    def _safe_unit_value(cls, raw: Any) -> Optional[float]:
        if raw is None:
            return None
        try:
            numeric = float(raw)
        except (TypeError, ValueError):
            return None
        if not (0.0 <= numeric <= 1.0):
            return None
        return float(numeric)

    @classmethod
    def _boundary_tag_weight(cls, tags: Optional[Sequence[str]]) -> float:
        if not tags:
            return 0.0
        best = 0.0
        for tag in tags:
            normalized = str(tag).strip().lower()
            if not normalized:
                continue
            best = max(best, cls.BOUNDARY_TAG_PRIORS.get(normalized, 0.0))
        return cls._clamp_unit(best)

    @classmethod
    def _build_wave_profile(
        cls,
        *,
        tension: Optional[float],
        wave: Optional[Dict[str, float]],
        memory_kind: str,
        tags: Optional[Sequence[str]],
    ) -> Dict[str, Any]:
        wave_payload = wave or {}
        risk = cls._clamp_unit(float(wave_payload.get("risk_shift", 0.0)))
        divergence = cls._clamp_unit(float(wave_payload.get("divergence_shift", 0.0)))
        revision = cls._clamp_unit(float(wave_payload.get("revision_shift", 0.0)))
        uncertainty = cls._clamp_unit(float(wave_payload.get("uncertainty_shift", 0.0)))

        conflict_strength = cls._safe_unit_value(tension)
        if conflict_strength is None:
            conflict_strength = max(risk, divergence * 0.85, uncertainty * 0.60)
        conflict_strength = cls._clamp_unit(conflict_strength)

        if divergence > 0.0 or revision > 0.0:
            stance_shift = (divergence + revision) / 2.0
        else:
            stance_shift = uncertainty * 0.50
        stance_shift = cls._clamp_unit(stance_shift)

        kind_prior = cls.WAVE_KIND_PRIORS.get(memory_kind, 0.30)
        boundary_cost = cls._clamp_unit(max(risk, kind_prior))

        tag_weight = cls._boundary_tag_weight(tags)
        consequence_weight = cls._clamp_unit(
            max(
                risk,
                (0.50 * risk) + (0.50 * tag_weight),
                (0.70 * uncertainty) + (0.30 * tag_weight),
            )
        )

        components = {
            "conflict_strength": round(conflict_strength, 4),
            "stance_shift": round(stance_shift, 4),
            "boundary_cost": round(boundary_cost, 4),
            "consequence_weight": round(consequence_weight, 4),
        }
        score = 1.0
        for key in cls.WAVE_COMPONENT_KEYS:
            score *= float(components[key])
        return {
            "score": round(cls._clamp_unit(score), 6),
            "components": components,
        }

    @classmethod
    def _extract_wave_score(cls, doc: Dict[str, Any]) -> float:
        stored = cls._safe_unit_value(doc.get("wave_score"))
        if stored is not None:
            return stored

        raw_wave = doc.get("wave")
        wave: Optional[Dict[str, float]] = None
        if isinstance(raw_wave, dict):
            try:
                wave = cls._validate_wave(raw_wave, "doc.wave")
            except ValueError:
                wave = None

        raw_kind = str(doc.get("kind") or "note").strip().lower()
        memory_kind = raw_kind if raw_kind in cls.VALID_MEMORY_KINDS else "note"
        raw_tags = doc.get("tags")
        tags = [str(tag) for tag in raw_tags] if isinstance(raw_tags, list) else []
        profile = cls._build_wave_profile(
            tension=cls._safe_unit_value(doc.get("tension")),
            wave=wave,
            memory_kind=memory_kind,
            tags=tags,
        )
        return float(profile["score"])

    def memorize(
        self,
        content: str,
        source_file: str = "runtime_experience",
        origin: str = "agent_consolidation",
        tension: Optional[float] = None,
        tags: Optional[Sequence[str]] = None,
        memory_kind: str = "note",
        wave: Optional[Dict[str, Any]] = None,
    ) -> str:
        if self.embedder is None:
            raise ValueError("Cannot memorize: no embedder provided to Hippocampus.")
        if tension is not None and not (0.0 <= float(tension) <= 1.0):
            raise ValueError("tension must be between 0.0 and 1.0")

        normalized_kind = self._validate_memory_kind(memory_kind)
        normalized_wave = self._validate_wave(wave, "wave")
        normalized_tags = [str(tag) for tag in tags if str(tag).strip()] if tags else []

        doc_id = str(uuid.uuid4())
        vector = self._ensure_vector_dim(self.embedder.encode(content))

        wave_profile = self._build_wave_profile(
            tension=float(tension) if tension is not None else None,
            wave=normalized_wave,
            memory_kind=normalized_kind,
            tags=normalized_tags,
        )
        wave_score = float(wave_profile["score"])
        memory_tier = "core" if wave_score >= self.CORE_WAVE_SCORE_THRESHOLD else "episodic"

        vector_matrix = np.array([vector], dtype=np.float32)
        self.index.add(vector_matrix)
        self._save_index()

        meta: Dict[str, Any] = {
            "id": doc_id,
            "source_file": source_file,
            "content": content,
            "ingested_at": self._utcnow_iso(),
            "origin": origin,
            "kind": normalized_kind,
            "wave_score": wave_score,
            "wave_components": wave_profile["components"],
            "memory_tier": memory_tier,
        }
        if tension is not None:
            meta["tension"] = float(tension)
        if normalized_tags:
            meta["tags"] = normalized_tags
        if normalized_wave is not None:
            meta["wave"] = normalized_wave
        self.metadata.append(meta)

        with open(self.meta_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")

        self._rebuild_bm25()
        return doc_id

    @staticmethod
    def _apply_tension_signal(
        base_score: float,
        doc: Dict[str, Any],
        query_tension: Optional[float],
        mode: str = "resonance",
    ) -> float:
        if query_tension is None:
            return base_score
        if not (0.0 <= query_tension <= 1.0):
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

        delta = abs(query_tension - doc_tension)
        delta = max(0.0, min(1.0, delta))
        signal = delta if mode == "conflict" else (1.0 - delta)
        return float(base_score * (1.0 + 0.20 * signal))

    @staticmethod
    def _apply_tension_resonance(
        base_score: float, doc: Dict[str, Any], query_tension: Optional[float]
    ) -> float:
        return Hippocampus._apply_tension_signal(
            base_score=base_score,
            doc=doc,
            query_tension=query_tension,
            mode="resonance",
        )

    @classmethod
    def _apply_wave_resonance(
        cls,
        base_score: float,
        doc: Dict[str, Any],
        query_wave: Optional[Dict[str, float]],
        mode: str = "resonance",
    ) -> float:
        if query_wave is None:
            return base_score

        doc_wave_raw = doc.get("wave")
        if not isinstance(doc_wave_raw, dict):
            return base_score

        try:
            doc_wave = cls._validate_wave(doc_wave_raw, "doc.wave")
        except ValueError:
            return base_score
        if doc_wave is None:
            return base_score

        shared_keys = [key for key in cls.WAVE_KEYS if key in query_wave and key in doc_wave]
        if not shared_keys:
            return base_score

        distance = float(np.mean([abs(query_wave[key] - doc_wave[key]) for key in shared_keys]))
        distance = max(0.0, min(1.0, distance))
        signal = distance if mode == "conflict" else (1.0 - distance)
        return float(base_score * (1.0 + 0.25 * signal))

    @classmethod
    def _apply_core_memory_priority(
        cls,
        base_score: float,
        doc: Dict[str, Any],
        query_tension: Optional[float],
    ) -> float:
        if query_tension is None:
            return base_score
        if not (0.0 <= float(query_tension) <= 1.0):
            return base_score
        if float(query_tension) < cls.HIGH_TENSION_CORE_PRIORITY_THRESHOLD:
            return base_score

        wave_score = cls._extract_wave_score(doc)
        if wave_score <= 0.0:
            return base_score

        tier = str(doc.get("memory_tier") or "").strip().lower()
        tier_boost = 0.18 if tier == "core" else 0.05
        boost = tier_boost + (0.22 * wave_score * float(query_tension))
        return float(base_score * (1.0 + boost))

    def _apply_time_decay(self, base_score: float, ingested_at: str) -> float:
        try:
            record_time = datetime.fromisoformat(str(ingested_at).replace("Z", "+00:00"))
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
        tension_context: Optional[Dict[str, Any]] = None,
        query_tension_mode: str = "resonance",
        query_wave: Optional[Dict[str, Any]] = None,
        query_wave_mode: str = "resonance",
    ) -> List[MemoryResult]:
        # Reserved for compatibility with unified pipeline context wiring.
        _ = tension_context
        if query_vector is None:
            if self.embedder is None:
                raise ValueError(
                    "Hippocampus requires either query_vector or an initialized embedder."
                )
            query_vector = self.embedder.encode(query_text)

        if query_tension_mode not in {"resonance", "conflict"}:
            raise ValueError("query_tension_mode must be 'resonance' or 'conflict'")
        if query_wave_mode not in {"resonance", "conflict"}:
            raise ValueError("query_wave_mode must be 'resonance' or 'conflict'")
        normalized_query_wave = self._validate_wave(query_wave, "query_wave")

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
            adjusted = self._apply_tension_signal(
                score, doc_map[doc_id], query_tension, mode=query_tension_mode
            )
            adjusted = self._apply_wave_resonance(
                adjusted, doc_map[doc_id], normalized_query_wave, mode=query_wave_mode
            )
            adjusted = self._apply_core_memory_priority(adjusted, doc_map[doc_id], query_tension)
            adjusted_scores[doc_id] = adjusted

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
                    metadata=doc,
                )
            )
        return final_results

    @staticmethod
    def _utcnow_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
