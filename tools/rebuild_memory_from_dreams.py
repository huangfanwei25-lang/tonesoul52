
import sys
import os
import json
import time

# Add parent to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from body.memory.hippocampus import MemoryConsolidator

def rebuild():
    print("🔧 Starting Memory Reconstruction from Dreams...")
    
    insights_file = "dream_insights.json"
    if not os.path.exists(insights_file):
        print("❌ No dream_insights.json found.")
        return

    # Load insights
    try:
        with open(insights_file, 'r', encoding='utf-8') as f:
            dreams = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        # Try line-by-line if JSON is corrupt?
        # But let's assume valid JSON based on previous view.
        return

    print(f"📚 Found {len(dreams)} dream entries.")
    
    # Initialize Memory
    memory = MemoryConsolidator()
    print(f"🧠 Current Memory Size: {len(memory.vector_store.metadata)}")
    
    success_count = 0
    skip_count = 0
    
    # Iterate and Engrave
    for i, dream in enumerate(dreams):
        topic = dream.get('topic', 'Unknown Topic')
        
        # Construct content similar to DreamWeaver.enter_rem_cycle feedback loop
        # Format: "Dream Insight on {topic}: {structure}..."
        
        simulation = dream.get('simulation', {})
        if isinstance(simulation, dict):
            structure = simulation.get('structure', '')
        else:
            structure = str(simulation) # Fallback if simulation is string
            
        if not structure:
            print(f"⚠️ Skipping dream {i}: No structure found.")
            continue
            
        content = f"Dream Insight on {topic}: {structure[:1000]}..." # Limit to 1000 chars for embedding
        
        # Check if already exists (naive check)
        if any(m.get('content') == content for m in memory.vector_store.metadata):
             skip_count += 1
             continue
             
        # Engrave
        print(f"[{i+1}/{len(dreams)}] Engraving: {topic[:30]}...")
        try:
            memory.engrave(
                content=content,
                source_id="rebuild_tool",
                importance=0.8,
                tags=["dream_insight", "restored"]
            )
            success_count += 1
            # Sleep slightly to avoid overwhelming Ollama
            time.sleep(0.1) 
        except Exception as e:
            print(f"❌ Failed to engrave: {e}")
            
    print(f"\n✅ Reconstruction Complete.")
    print(f"   - Restored: {success_count}")
    print(f"   - Skipped: {skip_count}")
    print(f"   - Final Size: {len(memory.vector_store.metadata)}")

if __name__ == "__main__":
    rebuild()
