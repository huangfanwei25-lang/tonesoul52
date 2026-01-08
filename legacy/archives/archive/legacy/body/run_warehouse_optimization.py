
import sys
import os
import json
import time

# Ensure we can import body modules
sys.path.append(os.getcwd())

from body.dream.weaver import DreamWeaver
from body.memory.hippocampus import MemoryConsolidator

def generate_file_tree(startpath):
    tree = []
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith('.py') or f.endswith('.md'):
                tree.append(f"{subindent}{f}")
    return "\n".join(tree)

def optimize_warehouse():
    print("🏗️ [Architect] Scanning Warehouse Structure...")
    repo_root = os.getcwd()
    structure = generate_file_tree(repo_root)
    
    # Truncate if too long (though structure usually fits)
    if len(structure) > 3000:
        structure = structure[:3000] + "\n...(truncated)"
        
    print(f"📊 Structure Snapshot:\n{structure[:500]}...\n")
    
    # Initialize Brain
    hippocampus = MemoryConsolidator()
    weaver = DreamWeaver(hippocampus)
    
    topic = "ToneSoul Repository Structure Optimization"
    content = f"""
    The user wants to OPTIMIZE the current Warehouse (Repository) Structure.
    Current File Tree:
    {structure}
    
    Goal: Identify redundant folders, legacy code, and suggest a cleaner, more agentic architecture.
    """
    
    print("🚀 [DreamWeaver] Starting Targeted Simulation (Deep Dive)...")
    
    # Manually trigger synthesis (Bypassing foraging loop)
    # We use _synthesize directly
    report = weaver._synthesize(content)
    
    # Save to insights
    weaver._persist_insight(report)
    
    print("\n✅ [DreamWeaver] Simulation Complete. Report generated.")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    optimize_warehouse()
