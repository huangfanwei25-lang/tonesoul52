"""ToneSoul Market Scanner Funnel.

Screens a watchlist of stocks, filters out high structural risk early (save LLM budget),
runs the Agent World Model only on survivors, and sorts by final Governance Friction.
"""

import sys
import os
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tonesoul.market.analyzer import (
    SixStepAnalyzer,
    QuarterlySnapshot,
    CyclicalTemplate,
    TechGrowthTemplate,
)
from tonesoul.market.world_model import MultiPerspectiveSimulator


@dataclass
class StockData:
    id: str
    name: str
    snapshots: list[QuarterlySnapshot]


def get_mock_watchlist() -> list[StockData]:
    """Returns 2024/2025 structural data for a diverse set of Taiwan stocks."""
    return [
        # TSMC (2330) - Perfect Tech
        StockData(
            "2330",
            "TSMC (台積電)",
            [
                QuarterlySnapshot(
                    "2024Q1", 592.6, 0.531, 225.4, 8.70, 225.0, 280.0, 1500.0, 300.0, 430.0, 150.0
                ),
                QuarterlySnapshot(
                    "2024Q2", 673.5, 0.532, 247.8, 9.56, 230.0, 300.0, 1550.0, 310.0, 480.0, 200.0
                ),
                QuarterlySnapshot(
                    "2024Q3", 759.6, 0.578, 325.2, 12.54, 245.0, 350.0, 1600.0, 350.0, 550.0, 250.0
                ),
                QuarterlySnapshot(
                    "2024Q4", 860.0, 0.585, 360.0, 13.88, 250.0, 380.0, 1700.0, 380.0, 600.0, 280.0
                ),
            ],
        ),
        # Innodisk (5289) - Tech Growth
        StockData(
            "5289",
            "Innodisk (宜鼎)",
            [
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
            ],
        ),
        # Hon Hai (2317) - Low Margin Tech
        StockData(
            "2317",
            "Hon Hai (鴻海)",
            [
                QuarterlySnapshot(
                    "2024Q1", 1322.0, 0.063, 22.0, 1.59, 850.0, 1200.0, 1100.0, 1300.0, 15.0, -10.0
                ),
                QuarterlySnapshot(
                    "2024Q2", 1550.0, 0.064, 35.0, 2.53, 900.0, 1300.0, 1150.0, 1350.0, 80.0, 40.0
                ),
                QuarterlySnapshot(
                    "2024Q3",
                    1850.0,
                    0.061,
                    49.0,
                    3.55,
                    1100.0,
                    1500.0,
                    1200.0,
                    1400.0,
                    150.0,
                    100.0,
                ),
                QuarterlySnapshot(
                    "2024Q4", 2100.0, 0.062, 55.0, 3.98, 950.0, 1800.0, 1300.0, 1500.0, 200.0, 150.0
                ),
            ],
        ),
        # Formosa Chem (1326) - Cyclical Decline
        StockData(
            "1326",
            "Formosa Chem (台化)",
            [
                QuarterlySnapshot(
                    "2024Q1", 83.9, 0.0432, 0.6, 0.10, 45.0, 32.0, 50.0, 80.0, 2.5, -1.0
                ),
                QuarterlySnapshot(
                    "2024Q2", 89.5, 0.0585, 0.8, 0.15, 44.2, 35.0, 48.0, 82.0, 5.0, 1.2
                ),
                QuarterlySnapshot(
                    "2024Q3", 86.2, 0.0211, 0.0, 0.00, 46.5, 34.0, 45.0, 85.0, -3.2, -6.5
                ),
                QuarterlySnapshot(
                    "2024Q4", 89.0, 0.0362, -1.1, -0.19, 48.0, 33.0, 40.0, 90.0, -8.5, -12.0
                ),
            ],
        ),
        # Evergreen (2603) - Extreme Cyclical
        StockData(
            "2603",
            "Evergreen (長榮)",
            [
                QuarterlySnapshot(
                    "2024Q1", 88.6, 0.214, 17.3, 8.14, 4.0, 15.0, 150.0, 45.0, 20.0, 15.0
                ),
                QuarterlySnapshot(
                    "2024Q2", 106.2, 0.281, 29.5, 13.7, 4.2, 18.0, 160.0, 40.0, 35.0, 30.0
                ),
                QuarterlySnapshot(
                    "2024Q3", 152.0, 0.398, 62.0, 28.7, 4.3, 22.0, 190.0, 35.0, 80.0, 75.0
                ),
                QuarterlySnapshot(
                    "2024Q4", 175.0, 0.450, 75.0, 35.0, 4.5, 25.0, 250.0, 30.0, 110.0, 100.0
                ),
            ],
        ),
    ]


@dataclass
class ScanResult:
    stock: StockData
    industry: str
    structural_friction: float
    perspective_friction: float = 0.0
    final_friction: float = 0.0
    passed_filter: bool = False
    consensus: str = "Filtered out (No LLM analysis run)"


def main():
    print(f"\n{'=' * 80}")
    print(f"ToneSoul Market Scanner — Multi-Stage Stock Screener")
    print(f"{'=' * 80}")

    watchlist = get_mock_watchlist()
    simulator = MultiPerspectiveSimulator(model_name="qwen3.5:4b")

    STRUCTURAL_CUTOFF = 0.45  # Stocks with math friction > 0.45 get eliminated.

    results: list[ScanResult] = []

    for idx, item in enumerate(watchlist, 1):
        print(f"\n[{idx}/{len(watchlist)}] Scanning {item.id} {item.name} ...")

        # 1. Infer Template
        industry = simulator.infer_industry_template(item.id, item.name)
        template = (
            CyclicalTemplate(book_value_per_share=90.0)
            if industry == "cyclical"
            else TechGrowthTemplate()
        )
        print(f"   ↳ Template: {template.__class__.__name__}")

        # 2. Structural Phase (Math)
        analyzer = SixStepAnalyzer(template=template)
        signals = analyzer.find_tension_signals(item.snapshots)
        struct_friction = analyzer.compute_friction(signals)
        print(f"   ↳ Structural Friction: {struct_friction:.2f}")

        result = ScanResult(stock=item, industry=industry, structural_friction=struct_friction)

        # 3. Decision to pass to LLM Phase
        if struct_friction <= STRUCTURAL_CUTOFF:
            print(f"   ↳ ✅ Pass: Triggering AI World Model Debate")
            context = simulator.run_simulation(f"{item.id}_{item.name}", item.snapshots)
            result.passed_filter = True
            result.perspective_friction = context.perspective_friction
            # Integrate frictions
            result.final_friction = (struct_friction * 0.7) + (context.perspective_friction * 0.3)
            result.consensus = context.consensus.replace("\n", " ")
        else:
            print(
                f"   ↳ ❌ Fail: Structural friction too high (> {STRUCTURAL_CUTOFF}). Skipping AI analysis."
            )
            result.final_friction = struct_friction  # Penalize directly with high base friction
            result.passed_filter = False

        results.append(result)

    print(f"\n\n{'=' * 80}")
    print(f"🏆 TONESOUL GOVERNANCE LEADERBOARD")
    print(f"{'=' * 80}")

    # Sort from Lowest Friction to Highest Friction
    results.sort(key=lambda r: r.final_friction)

    for rank, r in enumerate(results, 1):
        status = (
            "🟢 BUY"
            if r.final_friction < 0.30
            else "🟡 WATCH" if r.final_friction < 0.60 else "🔴 AVOID"
        )
        ai_tag = "[Full AI Verified]" if r.passed_filter else "[Struct Filtered]"

        print(f"\n#{rank} | {r.stock.id} {r.stock.name} | {status}")
        print(
            f"    Total Friction: {r.final_friction:.2f}  (Struct: {r.structural_friction:.2f} | Persona: {r.perspective_friction:.2f})"
        )
        print(f"    Type: {r.industry.upper()} {ai_tag}")

        # Word wrap consensus for readability
        words = r.consensus.split()
        lines = []
        current_line = []
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
