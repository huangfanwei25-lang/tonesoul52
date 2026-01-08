
import sys
import os
import json
import numpy as np
from collections import Counter

# Add parent directory to path to import body modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from body.memory.vector_store import VectorStore

def analyze():
    print("🔍 Analyzing Memory Distribution...")
    
    store = VectorStore(storage_dir="memory/vectors")
    print(f"🧠 Total Engrams: {len(store.metadata)}")
    
    if not store.metadata:
        print("Empty memory.")
        return

    # Analyze Topics (if available in tags or content)
    # Since topic isn't a strict field in metadata (only content, source_id, importance, tags),
    # we'll try to guess topic from tags or content snippet.
    
    sources = Counter()
    tags_counter = Counter()
    importance_scores = []
    
    for meta in store.metadata:
        sources[meta.get('source_id', 'unknown')] += 1
        tags = meta.get('tags', [])
        for t in tags:
            tags_counter[t] += 1
        importance_scores.append(meta.get('importance', 0.5))
        
    print("\n📊 Source Distribution:")
    for src, count in sources.most_common():
        print(f"  - {src}: {count}")
        
    print("\n🏷️  Top Tags:")
    for tag, count in tags_counter.most_common(10):
        print(f"  - {tag}: {count}")
        
    print("\n⭐ Importance Stats:")
    print(f"  - Max: {max(importance_scores)}")
    print(f"  - Avg: {sum(importance_scores)/len(importance_scores):.2f}")
    
    # Check for duplicates (content matching)
    contents = [m.get('content') for m in store.metadata]
    duplicates = len(contents) - len(set(contents))
    print(f"\n♻️  Potential Duplicates (exact content match): {duplicates}")

if __name__ == "__main__":
    analyze()
