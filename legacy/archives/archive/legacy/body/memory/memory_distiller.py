import time
from typing import List, Dict, Any
from .hippocampus import Engram, MemoryConsolidator
from ..brain.llm_client import llm_client

class MemoryDistiller:
    """
    The Alchemist of ToneSoul.
    Processes 'Cold Memories' and distills them into 'Abstracted Insights'.
    
    Goal: Free up space while preserving the 'Essence' of the experience.
    """
    
    def __init__(self, memory_system: MemoryConsolidator):
        self.memory = memory_system

    def distill(self, target_ids: List[str] = None, max_cluster_size: int = 5) -> List[Engram]:
        """
        Takes a set of IDs (or candidates) and compresses them.
        """
        if not target_ids:
            # Foraging: Find older, low-importance engrams
            # Sorted by timestamp (oldest first)
            candidates = sorted(self.memory.engrams, key=lambda x: x.timestamp)
            # Filter for non-vow, lower importance
            candidates = [c for c in candidates if c.importance < 0.9 and "vow" not in c.tags]
            
            if len(candidates) < max_cluster_size:
                return []
            
            target_ids = [c.engram_id for c in candidates[:max_cluster_size]]

        # 1. Fetch Engrams
        cluster = [e for e in self.memory.engrams if e.engram_id in target_ids]
        if not cluster:
            return []

        print(f"⚗️ [Distiller] Distilling {len(cluster)} engrams into one abstraction...")

        # 2. Extract Essence via LLM
        contents = "\n---\n".join([f"Memory from {time.ctime(e.timestamp)}: {e.content}" for e in cluster])
        
        distillation_prompt = (
            "Role: Semantic Alchemist / Knowledge Curator.\n"
            "Task: Distill the following group of memories into a single, high-level 'Abstracted Engram'.\n"
            "Constraint 1: Preserve core facts and lessons.\n"
            "Constraint 2: Discard redundant conversational filler.\n"
            "Constraint 3: Output must be concise but dense.\n"
            "Language: Traditional Chinese (Taiwan).\n\n"
            f"Memories to Distill:\n{contents}"
        )
        
        try:
            abstraction_text = llm_client.generate(distillation_prompt)
            if not abstraction_text:
                return []
                
            # 3. Create New Abstracted Engram
            abstract_content = f"[Abstracted Memory] {abstraction_text}"
            
            # The new engram has the combined importance (or slightly higher as it's a 'lesson')
            avg_importance = sum(e.importance for e in cluster) / len(cluster)
            new_importance = min(0.95, avg_importance + 0.1) 
            
            print(f"✨ [Distiller] Abstraction created: {abstract_content[:50]}...")
            
            # 4. Save New Memory
            self.memory.engrave(
                content=abstract_content,
                source_id="distillation_process",
                importance=new_importance,
                tags=["distilled", "abstraction", "long_term"]
            )
            
            # 5. Cleanup Old Memories
            # We use the vector store's batch deletion
            self.memory.vector_store.delete_batch(target_ids)
            # Update local list (simple way to keep in sync for current session)
            self.memory.engrams = [e for e in self.memory.engrams if e.engram_id not in target_ids]
            
            return cluster # Return what was distilled
            
        except Exception as e:
            print(f"❌ [Distiller] Distillation failed: {e}")
            return []

if __name__ == "__main__":
    # Test stub
    pass
