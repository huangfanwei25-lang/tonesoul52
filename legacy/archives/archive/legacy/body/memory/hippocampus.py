import json
import os
import time
import uuid
from dataclasses import dataclass, asdict, field
from typing import List, Any, Optional, Dict


@dataclass
class Engram:
    """
    A unit of long-term memory (Conscious Ingestion).
    Represents a consolidated fact or experience.
    """
    engram_id: str
    content: str
    source_record_id: Optional[str]
    importance: float # 0.0 - 1.0
    timestamp: float
    tags: List[str] = field(default_factory=list)


class MemoryConsolidator:
    """
    The Hippocampus of ToneSoul.
    Consolidates short-term ledger entries into long-term Engrams.
    """
    MEMORY_FILE = "core_memory.json"


    def __init__(self):
        from .vector_store import VectorStore
        self.vector_store = VectorStore()
        
        # We still keep loaded engrams for fast in-mem access if needed,
        # but primarily rely on vector store for search.
        self.engrams: List[Engram] = []
        # Load logic is now handled by vector_store internally (it loads numpy + json)
        # But to maintain compat with valid_memory checks, we might want to sync?
        # For now, let's trust vector_store.metadata as the source of truth.
        self._sync_mem_from_store()

    def _sync_mem_from_store(self):
        """Syncs local engram list from vector store metadata."""
        if self.vector_store.metadata:
            self.engrams = [Engram(**m) for m in self.vector_store.metadata]
        else:
            self.engrams = []

    def engrave(self, content: str, source_id: str = None, importance: float = 0.5, tags: List[str] = None):
        """
        Creates a new Engram and stores it in the Vector DB.
        """
        from ..brain.llm_client import llm_client
        
        # 1. Generate Embedding
        vector = llm_client.get_embedding(content)
        if not vector:
            print(f" [Hippocampus] Failed to embed '{content[:30]}...'. Memory skipped.")
            return

        # 2. Create Engram Object
        engram = Engram(
            engram_id=str(uuid.uuid4()),
            content=content,
            source_record_id=source_id,
            importance=importance,
            timestamp=time.time(),
            tags=tags or []
        )
        
        # 3. Save to Vector Store
        self.vector_store.add(vector, asdict(engram))
        self.engrams.append(engram)
        
        print(f" [Hippocampus] Engraved (Vectorized): '{content[:30]}...' (Imp={importance:.2f})")

    def recall(self, query: str, top_k: int = 3) -> List[Engram]:
        """
        Retrieves relevant Engrams based on query context using Vector Search.
        """
        from ..brain.llm_client import llm_client
        
        # 1. Embed Query
        query_vector = llm_client.get_embedding(query)
        if not query_vector:
            return []

        # 2. Search Vector DB
        # Lower threshold to find *something* if exists
        results = self.vector_store.search(query_vector, k=top_k, threshold=0.3)
        
        engrams = []
        for meta, score in results:
            engram = Engram(**meta)
            # Boost score by importance? 
            # Vector score is cosine similarity [0,1].
            # Let's trust semantic similarity primarily.
            engrams.append(engram)
            print(f" [Recall] Found: '{engram.content[:30]}...' (Sim={score:.2f})")

        return engrams

    def consolidate(self, ledger_records: List[Dict]):
        """
        Scans recent ledger records and extracts high-value memories.
        This is the 'Conscious Ingestion' process.
        """
        print(" [Hippocampus] Consolidating memories...")
        count = 0
        for record in ledger_records:
            # StepLedger stores results as dicts. Catch attributes or keys.
            
            # Heuristic 1: Explicit Facts / High Importance content
            content_summary = record.get('content_summary', '')
            metrics = record.get('metrics', {})
            
            # Use Responsibility or Ethics as indicators if high
            r_score = metrics.get('R', 0.5)
            e_score = metrics.get('E', 1.0)
            
            if r_score > 0.8 and content_summary:
                content = f"Verified Interaction: {content_summary}"
                if not self._exists(content):
                    self.engrave(content, record.get('event_id'), importance=r_score, tags=["verified", "ledger"])
                    count += 1

            # Heuristic 2: Tension-based lessons
            t_score = metrics.get('T', 0.0)
            if t_score > 0.7:
                content = f"High Tension Event recorded: {content_summary}"
                if not self._exists(content):
                    self.engrave(content, record.get('event_id'), importance=0.8, tags=["stress", "lesson"])
                    count += 1

        if count > 0:
            print(f" [Hippocampus] Consolidated {count} new semantic engrams.")
        else:
            print(" [Hippocampus] No new significant memories found.")

    def _exists(self, content: str) -> bool:
        return any(e.content == content for e in self.engrams)

