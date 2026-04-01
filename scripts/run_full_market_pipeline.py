"""Run ToneSoul Full Market Pipeline (Phase 2 + 3) for targeted stocks."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tonesoul.market.analyzer import (
    SixStepAnalyzer,
    QuarterlySnapshot,
    CyclicalTemplate,
    TechGrowthTemplate,
)
from tonesoul.market.world_model import MultiPerspectiveSimulator


def main():
    stock_id = sys.argv[1] if len(sys.argv) > 1 else "1326"
    print("=" * 60)
    print(f"ToneSoul Market Mirror — Full Pipeline (Structural + LLM World Model) for {stock_id}")
    print("=" * 60)

    if stock_id == "1326":
        company_name = "Formosa Chemicals & Fibre (台化)"
        snapshots = [
            QuarterlySnapshot("2024Q1", 83.9, 0.0432, 0.6, 0.10, 45.0, 32.0, 50.0, 80.0, 2.5, -1.0),
            QuarterlySnapshot("2024Q2", 89.5, 0.0585, 0.8, 0.15, 44.2, 35.0, 48.0, 82.0, 5.0, 1.2),
            QuarterlySnapshot(
                "2024Q3", 86.2, 0.0211, 0.0, 0.00, 46.5, 34.0, 45.0, 85.0, -3.2, -6.5
            ),
            QuarterlySnapshot(
                "2024Q4", 89.0, 0.0362, -1.1, -0.19, 48.0, 33.0, 40.0, 90.0, -8.5, -12.0
            ),
        ]
    else:
        # Default to 5289 (Innodisk)
        company_name = "Innodisk (宜鼎)"
        snapshots = [
            QuarterlySnapshot(
                "2024Q4", 22.28, 0.291, 2.71, 2.99, 16.44, 11.84, 30.00, 0, 6.42, 5.85
            ),
            QuarterlySnapshot(
                "2025Q1", 26.19, 0.306, 3.32, 3.68, 15.77, 14.87, 28.66, 0, 1.66, 1.07
            ),
            QuarterlySnapshot(
                "2025Q2", 30.28, 0.259, 1.74, 2.02, 26.92, 16.57, 20.68, 2.39, -8.56, -8.50
            ),
            QuarterlySnapshot(
                "2025Q3", 38.07, 0.328, 6.43, 6.87, 28.74, 24.19, 24.95, 1.83, -0.16, -0.44
            ),
            QuarterlySnapshot(
                "2025Q4", 48.07, 0.332, 8.73, 9.29, 53.85, 32.92, 16.45, 13.14, -15.69, -16.12
            ),
        ]

    simulator = MultiPerspectiveSimulator(model_name="qwen3.5:4b")

    print("\n[Phase 3A] Auto-classifying Industry Template using LLM...")
    industry = simulator.infer_industry_template(stock_id, company_name)
    print(f"✅ Inferred Industry: {industry.upper()}")

    if industry == "cyclical":
        template = CyclicalTemplate(book_value_per_share=54.0)
    else:
        template = TechGrowthTemplate()

    print(f"\n[Phase 2] Running structural analysis using {template.__class__.__name__}...")
    analyzer = SixStepAnalyzer(template=template)
    signals = analyzer.find_tension_signals(snapshots)
    friction = analyzer.compute_friction(signals)

    print(f"📊 Structural Friction: {friction:.2f}")
    if signals:
        for s in signals:
            print(f"   - {s.signal_id} ({s.severity})")

    print("\n[Phase 3B] Running Multi-Agent World Model Simulation (Value vs Macro vs Short)...")
    context = simulator.run_simulation(f"{stock_id}_{company_name}", snapshots)

    for p_id, narrative in context.persona_narratives.items():
        print(f"\n🧠 [{p_id.upper()} INVESTOR]")
        print(f"   {narrative}")

    print("\n🎯 [GOVERNANCE CONSENSUS]")
    print(f"   {context.consensus}")

    print(f"\n{'=' * 60}")
    print(f"ToneSoul Governance Verdict for {company_name} ({stock_id}):")
    final_friction = (friction * 0.7) + (context.perspective_friction * 0.3)
    print(f"Final Integrated Friction: {final_friction:.2f}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
