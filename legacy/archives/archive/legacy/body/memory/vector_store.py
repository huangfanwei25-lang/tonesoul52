import json
import os
import numpy as np
from typing import List, Dict, Any, Tuple

class VectorStore:
    """
    A lightweight, local Vector Database.
    Stores vectors in a numpy file and metadata in a JSON file.
    """
    def __init__(self, storage_dir: str = "memory/vectors"):
        self.storage_dir = storage_dir
        self.vectors_file = os.path.join(storage_dir, "vectors.npy")
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        
        self.vectors = None # Numpy array (N, D)
        self.metadata = []  # List of dicts matching indices
        
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

        self._load()

    def _load(self):
        if os.path.exists(self.vectors_file) and os.path.exists(self.metadata_file):
            try:
                self.vectors = np.load(self.vectors_file)
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f" [VectorStore] Loaded {len(self.metadata)} items.")
            except Exception as e:
                print(f" [VectorStore] Load failed: {e}. Starting fresh.")
                self.vectors = None
                self.metadata = []
        else:
            self.vectors = None
            self.metadata = []

    def _save(self):
        if self.vectors is not None:
            np.save(self.vectors_file, self.vectors)
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)

    def add(self, vector: List[float], meta: Dict[str, Any]):
        """
        Adds a vector and its metadata to the store.
        """
        vec_np = np.array(vector, dtype='float32')
        
        if self.vectors is None:
            self.vectors = vec_np.reshape(1, -1)
        else:
            self.vectors = np.vstack([self.vectors, vec_np])
            
        self.metadata.append(meta)
        
        # Check for pruning
        # For now we'll do a hard prune of oldest entries if we hit a limit
        # This will be replaced by distillation in Phase 2
        MAX_ENTRIES = 1000
        if len(self.metadata) > MAX_ENTRIES:
             self.prune(len(self.metadata) - MAX_ENTRIES)
        else:
            self._save()

    def prune(self, n: int):
        """Removes the oldest N entries."""
        if n <= 0 or self.vectors is None:
            return
            
        print(f" [VectorStore] Pruning {n} oldest entries...")
        self.vectors = self.vectors[n:]
        self.metadata = self.metadata[n:]
        self._save()

    def delete_batch(self, ids: List[str]):
        """Deletes entries by their engram_id."""
        if self.vectors is None:
            return
            
        indices_to_keep = [i for i, m in enumerate(self.metadata) if m.get('engram_id') not in ids]
        
        if len(indices_to_keep) == len(self.metadata):
            return
            
        self.vectors = self.vectors[indices_to_keep]
        self.metadata = [self.metadata[i] for i in indices_to_keep]
        self._save()
        print(f" [VectorStore] Deleted {len(ids)} items.")

    def search(self, query_vector: List[float], k: int = 5, threshold: float = 0.0) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches for k nearest neighbors using Cosine Similarity.
        Returns list of (metadata, score).
        """
        if self.vectors is None or len(self.vectors) == 0:
            return []

        query_np = np.array(query_vector, dtype='float32')
        
        # Normalize Query
        norm_q = np.linalg.norm(query_np)
        if norm_q == 0:
            return []
        query_norm = query_np / norm_q

        # Normalize Database
        # Note: Optimization would be to store normalized vectors
        norms_db = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        norms_db[norms_db == 0] = 1.0 # Avoid div by zero
        db_norm = self.vectors / norms_db

        # Cosine Similarity: dot product of normalized vectors
        scores = np.dot(db_norm, query_norm)
        
        # Get top K indices
        # argsort sorts ascending, so we take last k and reverse
        top_k_indices = np.argsort(scores)[-k:][::-1]
        
        results = []
        for idx in top_k_indices:
            score = float(scores[idx])
            if score >= threshold:
                results.append((self.metadata[idx], score))
        
        return results
