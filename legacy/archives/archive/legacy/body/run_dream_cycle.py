import sys
import os
import time
import signal
import random
import glob

# Ensure we can import body modules
sys.path.append(os.getcwd())

from body.dream.weaver import DreamWeaver
from body.memory.hippocampus import MemoryConsolidator

def signal_handler(sig, frame):
    print("\n [DreamWeaver] Interrupted. Saving state and waking up...")
    sys.exit(0)

def forage_knowledge(memory_system):
    """Reads external knowledge cache and injects it as memory."""
    cache_path = "body/external_knowledge_cache.md"
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Ingest as a high-importance memory
            print(" [Forager] Digesting External Knowledge Cache...")
            memory_system.engrave("External Knowledge: 2025 AI Trends", content, importance=0.95)
        except Exception as e:
            print(f" [Forager] Failed to read knowledge cache: {e}")

def forage_codebase(memory_system):
    """Randomly reads a code file and injects it as a memory for audit."""
    search_pattern = "body/**/*.py"
    files = glob.glob(search_pattern, recursive=True)
    if not files:
        return
    
    target_file = random.choice(files)
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f" [Forager] Scanning codebase file: {target_file}")
        # Inject as memory
        topic = f"Code Audit: {os.path.basename(target_file)}"
        full_content = f"{topic}\n\nCode Snippet:\n```python\n{content[:2500]}\n```" # Increased limit slightly
        
        # Inject as memory
        # IMPORTANT: DreamWeaver uses engram.content for synthesis. We must put the code THERE.
        # Arguments: engrave(content, source_id, importance, tags)
        memory_system.engrave(full_content, source_id=target_file, importance=0.85, tags=["code_audit", "system_optimization"])
    except Exception as e:
        print(f" [Forager] Failed to read file {target_file}: {e}")

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print("==================================================")
    print("      TONESOUL DREAM ENGINE (DEEP SLEEP)          ")
    print("==================================================")
    print("Initializing components...")
    
    try:
        # 1. Load Memory (The Subconscious)
        hippocampus = MemoryConsolidator()
        
        # 2. Initialize Weaver
        weaver = DreamWeaver(hippocampus)
        
        print(f"Memory Loaded. {len(hippocampus.engrams)} engrams available.")
        
        # 3. Initial Forage (Knowledge)
        forage_knowledge(hippocampus)
        
        # 3.1 Diversity Injection (Seed Topics)
        if len(hippocampus.engrams) < 5:
            print(" [Gardener] Memory low. Planting seed topics...")
            seeds = [
                ("Bio-Logical Architecture", "Explore the concept of codebases that grow and prune themselves like biological organisms."),
                ("Quantum Finance Algorithms", "High-frequency trading algorithms adapted for resource allocation in distributed systems."),
                ("Swarm Intelligence Security", "defensive protocols inspired by immune systems for drone swarms."),
                ("Ethical AI Governance", "Frameworks for autonomous decision making in high-stakes environments.")
            ]
            for topic, content in seeds:
                hippocampus.engrave(content, source_id="seed_injection", importance=0.8, tags=["seed", "diversity"])

        
        print("Starting infinite sleep loop. Press Ctrl+C to wake up.\n")
        
        cycle_count = 0
        
        while True:
            cycle_count += 1
            print(f"\n --- Cycle #{cycle_count} ---")
            
            # 4. Active Foraging (Codebase)
            # Every cycle, look at a different piece of code
            forage_codebase(hippocampus)
            
            # Run REM cycle
            insights = weaver.enter_rem_cycle(duration_seconds=300)
            
            if not insights:
                print(" [DreamWeaver] No insights generated.")
            
            rest_time = 60 
            print(f" Resting for {rest_time}s...")
            time.sleep(rest_time)
            
    except Exception as e:
        print(f"\n [CRITICAL] Dream Engine Crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
