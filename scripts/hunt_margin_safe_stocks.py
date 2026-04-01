"""ToneSoul Market Scanner — Margin-Safe Hunter (頂息概念股尋寶器)

Target:
- Price < 200 NTD
- Dividend Yield > 4.0% (to cover 2.5%~3% margin interest)
- Low Structural Friction (Safe cash flow to prevent capital loss)
"""

import sys
import os
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tonesoul.market.analyzer import SixStepAnalyzer, QuarterlySnapshot, TechGrowthTemplate
from tonesoul.market.world_model import MultiPerspectiveSimulator


@dataclass
class MarginStockData:
    id: str
    name: str
    current_price: float
    dividend_yield_pct: float  # e.g. 5.2 for 5.2%
    snapshots: list[QuarterlySnapshot]


def get_margin_watchlist() -> list[MarginStockData]:
    """Mock database of well-known Sub-200, High-Yield Taiwan Stocks."""
    return [
        MarginStockData(
            "2301",
            "Lite-On (光寶科)",
            105.0,
            5.2,
            [
                QuarterlySnapshot(
                    "2024Q1", 28.8, 0.203, 2.4, 1.04, 15.0, 25.0, 50.0, 10.0, 4.5, 3.2
                ),
                QuarterlySnapshot(
                    "2024Q2", 33.2, 0.222, 3.1, 1.36, 14.8, 26.0, 52.0, 10.0, 5.0, 4.0
                ),
                QuarterlySnapshot(
                    "2024Q3", 36.8, 0.224, 3.5, 1.48, 15.2, 28.0, 55.0, 11.0, 6.2, 5.1
                ),
                QuarterlySnapshot(
                    "2024Q4", 39.5, 0.228, 4.0, 1.62, 16.0, 30.0, 58.0, 12.0, 7.0, 5.5
                ),
            ],
        ),
        MarginStockData(
            "4938",
            "Pegatron (和碩)",
            100.5,
            4.5,
            [
                QuarterlySnapshot(
                    "2024Q1", 250.0, 0.042, 3.0, 1.1, 100.0, 150.0, 80.0, 60.0, 5.0, -2.0
                ),
                QuarterlySnapshot(
                    "2024Q2", 280.0, 0.045, 4.2, 1.5, 105.0, 160.0, 85.0, 65.0, 8.0, 2.0
                ),
                QuarterlySnapshot(
                    "2024Q3", 320.0, 0.048, 5.5, 2.0, 120.0, 180.0, 90.0, 70.0, 15.0, 8.0
                ),
                QuarterlySnapshot(
                    "2024Q4", 350.0, 0.049, 6.1, 2.2, 125.0, 200.0, 100.0, 75.0, 22.0, 15.0
                ),
            ],
        ),
        MarginStockData(
            "2324",
            "Compal (仁寶)",
            37.8,
            4.8,
            [
                QuarterlySnapshot(
                    "2024Q1", 199.0, 0.049, 1.5, 0.35, 70.0, 130.0, 60.0, 45.0, 3.0, 1.0
                ),
                QuarterlySnapshot(
                    "2024Q2", 237.0, 0.050, 2.0, 0.45, 75.0, 140.0, 65.0, 40.0, 5.0, 2.5
                ),
                QuarterlySnapshot(
                    "2024Q3", 244.0, 0.052, 2.3, 0.52, 78.0, 145.0, 68.0, 40.0, 8.0, 4.0
                ),
                QuarterlySnapshot(
                    "2024Q4", 260.0, 0.051, 2.5, 0.58, 80.0, 150.0, 70.0, 40.0, 10.0, 6.0
                ),
            ],
        ),
        MarginStockData("2382", "Quanta (廣達)", 315.0, 3.5, []),  # Should be filtered out by price
        MarginStockData(
            "5289", "Innodisk (宜鼎)", 380.0, 2.5, []
        ),  # Should be filtered out by price
    ]


def main():
    print(f"\n{'=' * 80}")
    print(f"ToneSoul Market Scanner — MARGIN-SAFE HUNTER (頂息尋寶器)")
    print(f"Criteria: Price < 200 NTD | Yield > 4.0% | Low Friction")
    print(f"{'=' * 80}")

    watchlist = get_margin_watchlist()
    simulator = MultiPerspectiveSimulator(model_name="qwen3.5:4b")

    results = []

    for item in watchlist:
        print(f"\nScanning {item.id} {item.name} ...")

        # Filter 1: Price
        if item.current_price > 200.0:
            print(f"   ❌ Rejected: Price {item.current_price} > 200 NTD")
            continue

        # Filter 2: Dividend Yield
        if item.dividend_yield_pct < 4.0:
            print(
                f"   ❌ Rejected: Yield {item.dividend_yield_pct}% < 4.0% (Risk of interest erosion)"
            )
            continue

        print(
            f"   ✅ Hard Filters Passed: Price {item.current_price} | Yield {item.dividend_yield_pct}%"
        )

        # Filter 3: Structural Friction
        analyzer = SixStepAnalyzer(template=TechGrowthTemplate())
        signals = analyzer.find_tension_signals(item.snapshots)
        struct_friction = analyzer.compute_friction(signals)
        print(f"   ↳ Structural Friction: {struct_friction:.2f}")

        if struct_friction > 0.4:
            print(f"   ❌ Rejected: Structural math too risky.")
            continue

        # Filter 4: AI World Model
        print(f"   ✅ Pass: Triggering AI World Model Debate")
        context = simulator.run_simulation(f"{item.id}_{item.name}_MarginSafe", item.snapshots)
        final_friction = (struct_friction * 0.7) + (context.perspective_friction * 0.3)

        results.append(
            {
                "stock": item.name,
                "id": item.id,
                "price": item.current_price,
                "yield": item.dividend_yield_pct,
                "struct_friction": struct_friction,
                "final_friction": final_friction,
                "consensus": context.consensus.replace("\n", " "),
            }
        )

    print(f"\n\n{'=' * 80}")
    print(f"🏆 TOP MARGIN-SAFE PICKS (頂息最佳標的)")
    print(f"{'=' * 80}")

    results.sort(key=lambda r: r["final_friction"])

    for rank, r in enumerate(results, 1):
        print(f"\n#{rank} | {r['id']} {r['stock']} | Price: NT${r['price']} | Yield: {r['yield']}%")
        print(f"    Total Friction: {r['final_friction']:.2f} (Struct {r['struct_friction']:.2f})")

        words = r["consensus"].split()
        lines, current_line = [], []
        for word in words:
            if len(" ".join(current_line + [word])) > 70:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(" ".join(current_line))

        for line in lines:
            print(f"    > {line}")


if __name__ == "__main__":
    main()
