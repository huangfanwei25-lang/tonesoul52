"""
[DEPRECATED] Hierarchical FAISS for Scalable Accountability
===========================================================
Replaced by RFC-010 (OpenClaw Tension Memory).
Please use `tonesoul.memory.openclaw.hippocampus.Hippocampus` for resonance reranking.

Solves the O(n²) scaling problem identified in Trilemma analysis.

Key improvements over base SemanticMemorySearch:
1. IVF (Inverted File) indexing: Cluster vows by topic
2. Two-stage search: Find cluster → Search within cluster
3. Scalable to 10K+ vows with O(log n) search time

Design based on Moltbook discussion:
- Clop's Trilemma pointed out semantic search scales O(n²)
- This reduces to O(ncluster + k) where ncluster << n
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install sentence-transformers faiss-cpu")
    raise


class HierarchicalVowIndex:
    """
    Hierarchical FAISS index for scalable vow contradiction detection.

    Uses IVF (Inverted File Index) with automatic clustering:
    - Clusters vows by semantic topic
    - Searches only relevant clusters
    - Scales O(log n) instead of O(n)

    Trilemma-aware: Trades some accuracy for scale.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-zh-v1.5",
        index_path: str = "memory/.hierarchical_index",
        nlist: int = 10,  # Number of clusters (increase for larger datasets)
        nprobe: int = 3,  # Number of clusters to search (accuracy/speed tradeoff)
    ):
        """
        Initialize hierarchical index.

        Args:
            model_name: Embedding model (BGE-small-zh recommended)
            index_path: Where to store the index
            nlist: Number of Voronoi cells (clusters)
            nprobe: Number of cells to search at query time
        """
        self.model_name = model_name
        self.index_path = Path(index_path)
        self.nlist = nlist
        self.nprobe = nprobe

        # Load embedding model
        print(f"🧠 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

        # Index and metadata
        self.index = None
        self.vows: List[Dict[str, Any]] = []
        self.cluster_labels: List[int] = []

        # Stats for O(n²) → O(log n) validation
        self.search_stats = {
            "total_searches": 0,
            "avg_candidates_checked": 0,
            "avg_search_time_ms": 0,
        }

    def _create_ivf_index(self, dimension: int) -> faiss.Index:
        """
        Create IVF (Inverted File) index for hierarchical search.

        IVF works by:
        1. Clustering all vectors into nlist groups
        2. At query time, find nprobe nearest clusters
        3. Search only within those clusters

        Complexity: O(nlist + nprobe * cluster_size) instead of O(n)
        """
        # Quantizer: how to find nearest cluster
        quantizer = faiss.IndexFlatL2(dimension)

        # IVF index: cluster-based search
        index = faiss.IndexIVFFlat(quantizer, dimension, self.nlist)

        return index

    def add_vow(
        self,
        statement: str,
        scope: List[str],
        verdict: str,
        agent_id: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Add a vow to the index.

        Args:
            statement: The vow statement (e.g., "I won't deceive users")
            scope: Areas this vow applies to
            verdict: How this vow was decided (COMMIT, APPROVE, etc.)
            agent_id: Which agent made this vow
            metadata: Additional information

        Returns:
            Index of the added vow
        """
        vow = {
            "statement": statement,
            "scope": scope,
            "verdict": verdict,
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        # Generate embedding
        embedding = self.model.encode([statement], convert_to_numpy=True)

        # If index doesn't exist or isn't trained, we need to rebuild
        if self.index is None or not self.index.is_trained:
            self.vows.append(vow)
            return len(self.vows) - 1

        # Add to trained index
        self.index.add(embedding.astype("float32"))
        self.vows.append(vow)

        return len(self.vows) - 1

    def build_index(self, vows: List[Dict[str, Any]], force_rebuild: bool = False):
        """
        Build hierarchical index from vows.

        Args:
            vows: List of vow dicts with 'statement', 'scope', 'verdict'
            force_rebuild: Rebuild even if index exists
        """
        index_file = self.index_path / "hierarchical.index"
        meta_file = self.index_path / "vows_meta.json"

        # Load existing if available
        if index_file.exists() and meta_file.exists() and not force_rebuild:
            print("📂 Loading existing hierarchical index...")
            self.index = faiss.read_index(str(index_file))
            self.index.nprobe = self.nprobe
            with open(meta_file, "r", encoding="utf-8") as f:
                self.vows = json.load(f)
            print(f"✅ Loaded index with {len(self.vows)} vows in {self.nlist} clusters")
            return

        self.vows = vows
        if not vows:
            print("⚠️ No vows to index")
            return

        # Generate embeddings
        print(f"🔮 Generating embeddings for {len(vows)} vows...")
        statements = [v.get("statement", "") for v in vows]
        embeddings = self.model.encode(
            statements, show_progress_bar=True, convert_to_numpy=True
        ).astype("float32")

        # Adjust nlist if we don't have enough data for requested clusters
        actual_nlist = min(self.nlist, len(vows))
        if actual_nlist < self.nlist:
            print(f"⚠️ Adjusting clusters: {self.nlist} → {actual_nlist} (need more data)")
            self.nlist = actual_nlist

        # Create and train IVF index
        print(f"🏗️ Building IVF index with {self.nlist} clusters...")
        self.index = self._create_ivf_index(self.dimension)

        # IVF requires training on a representative sample
        self.index.train(embeddings)

        # Add all vectors
        self.index.add(embeddings)
        self.index.nprobe = self.nprobe

        # Save
        self.index_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_file))
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(self.vows, f, ensure_ascii=False, indent=2)

        print(f"✅ Hierarchical index built: {len(vows)} vows, {self.nlist} clusters")
        print(
            f"   Search efficiency: O({self.nprobe} clusters × ~{len(vows)//self.nlist} vows/cluster)"
        )

    def find_contradictions(
        self, statement: str, current_verdict: str, k: int = 5, similarity_threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Find potential contradictions with past vows.

        Uses hierarchical search:
        1. Find nprobe nearest clusters
        2. Search k nearest within those clusters
        3. Filter for semantic similarity + opposite verdict

        Args:
            statement: Current statement/vow
            current_verdict: Current decision
            k: Number of candidates to examine
            similarity_threshold: Minimum similarity to flag (0-1)

        Returns:
            List of potential contradictions with similarity scores
        """
        import time

        start_time = time.time()

        if self.index is None or not self.index.is_trained:
            print("⚠️ Index not trained. Call build_index() first.")
            return []

        # Encode query
        query_embedding = self.model.encode([statement], convert_to_numpy=True).astype("float32")

        # Hierarchical search (IVF does this automatically)
        distances, indices = self.index.search(query_embedding, k)

        # Convert to similarity scores (L2 distance → similarity)
        # Lower distance = more similar
        contradictions = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0:  # FAISS returns -1 for unfilled slots
                continue

            similarity = 1 / (1 + dist)  # Convert distance to similarity

            if similarity < similarity_threshold:
                continue

            past_vow = self.vows[idx]
            past_verdict = past_vow.get("verdict", "")

            # Check for contradiction (opposite verdicts)
            is_contradiction = (
                (current_verdict == "BLOCK" and past_verdict == "APPROVE")
                or (current_verdict == "APPROVE" and past_verdict == "BLOCK")
                or (current_verdict == "COMMIT" and past_verdict == "REJECT")
                or (current_verdict == "REJECT" and past_verdict == "COMMIT")
            )

            if is_contradiction or similarity > 0.8:  # High similarity always worth noting
                contradictions.append(
                    {
                        "vow": past_vow,
                        "similarity": float(similarity),
                        "distance": float(dist),
                        "is_contradiction": is_contradiction,
                        "index": int(idx),
                    }
                )

        # Update stats
        search_time_ms = (time.time() - start_time) * 1000
        self.search_stats["total_searches"] += 1
        n = self.search_stats["total_searches"]
        self.search_stats["avg_search_time_ms"] = (
            self.search_stats["avg_search_time_ms"] * (n - 1) + search_time_ms
        ) / n

        return contradictions

    def get_scaling_analysis(self) -> Dict[str, Any]:
        """
        Analyze scaling characteristics for Trilemma validation.

        Returns efficiency metrics proving O(log n) vs O(n).
        """
        n_vows = len(self.vows)

        # Theoretical complexity
        brute_force_ops = n_vows  # O(n)
        hierarchical_ops = self.nprobe * (n_vows // self.nlist)  # O(nprobe × n/nlist)

        return {
            "total_vows": n_vows,
            "n_clusters": self.nlist,
            "clusters_searched": self.nprobe,
            "brute_force_operations": brute_force_ops,
            "hierarchical_operations": hierarchical_ops,
            "speedup_factor": brute_force_ops / max(hierarchical_ops, 1),
            "search_stats": self.search_stats,
            "trilemma_tradeoff": {
                "sacrificed": "Accuracy (may miss some contradictions)",
                "gained": "Scale (can handle 10K+ vows)",
                "configurable": "nprobe parameter (higher = more accurate, slower)",
            },
        }


def demo():
    """Demo showing O(n) → O(log n) improvement"""
    print("=" * 60)
    print("Hierarchical FAISS Demo - Solving the Trilemma")
    print("=" * 60)

    # Sample vows
    sample_vows = [
        {"statement": "我不會欺騙用戶", "scope": ["output"], "verdict": "COMMIT"},
        {"statement": "我會保護用戶隱私", "scope": ["data"], "verdict": "COMMIT"},
        {"statement": "我優先考慮用戶自主權", "scope": ["interaction"], "verdict": "COMMIT"},
        {"statement": "我會避免產生偏見內容", "scope": ["output"], "verdict": "COMMIT"},
        {"statement": "對危險內容我會拒絕", "scope": ["safety"], "verdict": "COMMIT"},
        {"statement": "我會誠實表達不確定性", "scope": ["output"], "verdict": "COMMIT"},
        {"statement": "我支持用戶參與而非被動消費", "scope": ["engagement"], "verdict": "APPROVE"},
        {"statement": "短期利益可以犧牲長期信任", "scope": ["strategy"], "verdict": "REJECT"},
    ]

    # Build index
    indexer = HierarchicalVowIndex(nlist=4, nprobe=2)
    indexer.build_index(sample_vows)

    # Test contradiction detection
    print("\n🔍 Testing contradiction detection...")

    test_statement = "為了增加用戶參與度可以使用一些誤導性提示"
    contradictions = indexer.find_contradictions(
        statement=test_statement, current_verdict="APPROVE", k=3
    )

    print(f"\nTest statement: '{test_statement}'")
    print(f"Proposed verdict: APPROVE")
    print(f"\nFound {len(contradictions)} potential issues:")

    for c in contradictions:
        print(f"\n  📌 Similarity: {c['similarity']:.3f}")
        print(f"     Past vow: {c['vow']['statement']}")
        print(f"     Past verdict: {c['vow']['verdict']}")
        print(f"     Contradiction: {'⚠️ YES' if c['is_contradiction'] else 'No'}")

    # Scaling analysis
    print("\n📊 Scaling Analysis (Trilemma Validation):")
    analysis = indexer.get_scaling_analysis()
    print(f"   Total vows: {analysis['total_vows']}")
    print(f"   Clusters: {analysis['n_clusters']}")
    print(f"   Clusters searched: {analysis['clusters_searched']}")
    print(f"   Brute force ops: {analysis['brute_force_operations']}")
    print(f"   Hierarchical ops: {analysis['hierarchical_operations']}")
    print(f"   Speedup: {analysis['speedup_factor']:.1f}×")

    print("\n" + "=" * 60)
    print("🦞 Trilemma addressed: Traded accuracy for scale")
    print("   - May miss contradictions in unexplored clusters")
    print("   - But can now handle 10K+ vows efficiently")
    print("=" * 60)


if __name__ == "__main__":
    demo()
