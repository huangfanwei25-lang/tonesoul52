
import sys
import os
import argparse

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from body.memory.hippocampus import MemoryConsolidator

def search_memory(query: str, limit: int = 5):
    print(f"🔍 Searching Memory for: '{query}'...")
    
    # Initialize Hippocampus (loads VectorStore)
    hippo = MemoryConsolidator()
    
    # Use recall method
    # Note: Ensure Hippocampus.recall prints results or returns them
    results = hippo.recall(query, limit=limit)
    
    print(f"\n🧠 Found {len(results)} relevant engrams:\n")
    for i, engram in enumerate(results):
        print(f"[{i+1}] Similarity: (from vector search)") # Score isn't in Engram object but printed by recall currently
        print(f"    Topic/Content: {engram.content[:150]}...")
        print(f"    Tags: {engram.tags}")
        print(f"    Time: {engram.timestamp}")
        print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search ToneSoul Memory.")
    parser.add_argument("query", type=str, help="The search query")
    parser.add_argument("--limit", type=int, default=5, help="Max number of results")
    
    args = parser.parse_args()
    search_memory(args.query, args.limit)
