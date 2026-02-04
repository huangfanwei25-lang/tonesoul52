"""
Demo: LoopEngine Integration with UnifiedCore

This demo showcases the Ralph-inspired iterative self-correction feature.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tonesoul.unified_core import UnifiedCore
from tonesoul.loop.events import PromiseDetectedEvent, IterationStartEvent


async def demo_iterative_correction():
    """Demonstrate iterative self-correction using LoopEngine"""

    print("=" * 70)
    print("  ToneSoul + Ralph: Iterative Self-Correction Demo")
    print("=" * 70)

    # Initialize UnifiedCore
    print("\n[1] Initializing UnifiedCore...")
    core = UnifiedCore(
        persona_payload={
            "id": "demo_persona",
            "home_vector": {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
            "tolerance": {"deltaT": 0.3, "deltaS": 0.35, "deltaR": 0.4},
        }
    )
    print("✓ Core initialized")

    # Test output that might need correction
    test_output = "This is a test output that might have semantic drift."

    print(f"\n[2] Processing output with iterative correction...")
    print(f"Input: {test_output}")
    print()

    # Use process_with_correction
    result = await core.process_with_correction(
        output=test_output,
        max_corrections=3,
        correction_threshold=0.5,
    )

    # Display results
    print("\n" + "=" * 70)
    print("  Results")
    print("=" * 70)

    print(f"\n📊 Summary:")
    print(f"  Final Output: {result['final_output']}")
    print(f"  Corrections: {result['corrections']}")
    print(f"  State: {result['state']}")
    print(f"  Duration: {result['duration_ms']}ms")
    print(f"  Success: {result['success']}")

    # Display correction history
    print(f"\n📝 Correction History:")
    for i, correction in enumerate(result["correction_history"], 1):
        tension = correction.get("semantic_tension", {})
        print(f"  Iteration {i}:")
        print(f"    - Mean Tension: {tension.get('mean', 0):.3f}")
        print(f"    - Intervention: {correction.get('intervention', 'N/A')}")
        print(f"    - Corrected: {correction.get('corrected', False)}")

    # Display events
    print(f"\n📡 Events ({len(result['events'])}):")
    for event in result["events"]:
        if isinstance(event, IterationStartEvent):
            print(f"  → Iteration {event.iteration}/{event.max_iterations} started")
        elif isinstance(event, PromiseDetectedEvent):
            print(f"  ✓ Promise detected: {event.phrase}")
        elif event.event_type == "loop_complete":
            print(f"  ✓ Loop completed")

    print("\n" + "=" * 70)
    print("  Demo Complete")
    print("=" * 70)


async def demo_simple_usage():
    """Simple usage example"""
    print("\n\n" + "=" * 70)
    print("  Simple Usage Example")
    print("=" * 70)

    # Minimal setup
    core = UnifiedCore(
        persona_payload={
            "id": "simple",
            "home_vector": {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
        }
    )

    # Process with correction
    result = await core.process_with_correction(
        output="Simple test",
        max_corrections=2,
    )

    print(f"\nFinal: {result['final_output']}")
    print(f"Iterations: {result['corrections']}")
    print(f"Success: {result['success']}")


if __name__ == "__main__":
    # Run demos
    asyncio.run(demo_iterative_correction())
    asyncio.run(demo_simple_usage())
