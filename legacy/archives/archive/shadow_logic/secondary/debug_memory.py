
import sys
import os
import time
sys.path.append(os.getcwd())
from body.memory.hippocampus import MemoryConsolidator

def debug_memory():
    print("Initializing Hippocampus...")
    hippocampus = MemoryConsolidator()
    
    print(f"Total Engrams: {len(hippocampus.engrams)}")
    
    # Sort by timestamp
    sorted_engrams = sorted(hippocampus.engrams, key=lambda x: x.timestamp, reverse=True)
    
    print("\n--- Last 5 Engrams (Newest First) ---")
    for i, e in enumerate(sorted_engrams[:5]):
        content_preview = e.content[:50].replace('\n', ' ')
        # extract topic if possible (it's not a field in Engram, but maybe in content?)
        # Wait, engram has no 'topic' field? 
        # run_dream_cycle.py: memory_system.engrave(topic, code_content...)
        # Hippocampus.engrave(content, source_id, ...)
        # It seems 'topic' argument in run_dream_cycle is passed as 'content'?
        # No. run_dream_cycle: memory_system.engrave(topic, f"Code Content...", ...)
        # Check Hippocampus.engrave signature: engrave(self, content: str, source_id: str = None, ...)
        # So 'topic' is passed as 'content'?? No.
        
        # run_dream_cycle calling: memory_system.engrave(topic, code_content_str, importance=0.85)
        # Hippocampus.engrave definition: (self, content, source_id, importance, tags)
        # So 'topic' -> 'content'. 
        # 'code_content_str' -> 'source_id'.
        
        print(f"[{i}] Time: {time.ctime(e.timestamp)} | Imp: {e.importance} | Content: {content_preview}...")

if __name__ == "__main__":
    debug_memory()
