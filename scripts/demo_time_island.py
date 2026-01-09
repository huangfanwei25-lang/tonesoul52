"""
Time-Island Lightweight Demo
輕量級時間島展示

This demo creates real Time-Islands from user input without heavy LLM calls.
It demonstrates the core protocol: capturing decisions in bounded contexts.

Usage:
    python scripts/demo_time_island.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tonesoul.time_island import TimeIslandManager, IslandState


def main():
    print("=" * 60)
    print("   🏝️  Time-Island Protocol Demo (Lightweight)")
    print("   語魂時間島協議展示")
    print("=" * 60)
    
    # Setup manager with persistence
    storage_path = os.path.join(
        os.path.dirname(__file__), "..", "memory", "time_islands.json"
    )
    manager = TimeIslandManager(storage_path=storage_path)
    
    # Try to load existing islands
    try:
        manager.load()
        existing = len(manager.islands)
        if existing > 0:
            print(f"\n📂 Loaded {existing} existing islands from memory.")
    except Exception:
        pass
    
    print("\n📝 Enter your thoughts/decisions. Each entry becomes a Time-Island.")
    print("   Type 'list' to see all islands, 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("🌊 > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not user_input:
            continue
        
        if user_input.lower() == "quit":
            break
        
        if user_input.lower() == "list":
            islands = manager.list_islands()
            if not islands:
                print("   No islands yet.")
            else:
                print(f"\n   📋 Total Islands: {len(islands)}")
                for island in islands[-5:]:  # Show last 5
                    state_emoji = {
                        IslandState.DRAFT: "📝",
                        IslandState.ACTIVE: "🔵",
                        IslandState.COMPLETED: "✅",
                        IslandState.ARCHIVED: "📦",
                    }.get(island.state, "❓")
                    print(f"   {state_emoji} {island.id}: {island.bounded_context[:40]}...")
                print()
            continue
        
        # Create a new island for this thought
        island = manager.create_island(user_input)
        island.add_input("user_input", user_input)
        
        # Simple metrics (no LLM, just heuristics)
        # Tension: based on punctuation
        tension = min(1.0, user_input.count("!") * 0.2 + user_input.count("?") * 0.15)
        # Risk: very low for demo
        risk = 0.1
        # Value fit: assume good
        value_fit = 0.85
        
        island.update_resonance(value_fit=value_fit, consensus=0.8, risk=risk)
        island.update_drift(tension * 0.5)  # Drift proportional to tension
        
        # Complete the island
        manager.complete_current()
        
        print(f"   ✅ Island {island.id} created (drift={island.drift_from_start:.2f})")
        
        # Save after each island
        try:
            manager.save()
        except Exception as e:
            print(f"   ⚠️ Save failed: {e}")
    
    # Final save
    try:
        manager.save()
        print(f"\n💾 Saved {len(manager.islands)} islands to {storage_path}")
    except Exception as e:
        print(f"\n⚠️ Final save failed: {e}")
    
    print("\n" + "=" * 60)
    print("   Demo Complete. Your thoughts are now Time-Islands.")
    print("=" * 60)


if __name__ == "__main__":
    main()
