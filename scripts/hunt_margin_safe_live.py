"""ToneSoul Market Scanner — LIVE MARGIN-SAFE HUNTER (即時頂息尋寶器)

Fetches real TWSE data via FinMind for a watchlist to find:
- Price < 200 NTD
- Dividend Yield > 4.0%
- Low Structural Friction
- World Model Buy Consensus
"""

import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tonesoul.market.analyzer import SixStepAnalyzer, QuarterlySnapshot, TechGrowthTemplate
from tonesoul.market.world_model import MultiPerspectiveSimulator
from tonesoul.market.data_ingest import MarketDataIngestor


def get_value(stimuli, target_type: str, fallback_types=None) -> float:
    """Helper to extract a specific financial value from a list of stimuli."""
    for item in stimuli:
        if item.data.get("type") == target_type:
            return float(item.data.get("value", 0.0))
    if fallback_types:
        for ftype in fallback_types:
            for item in stimuli:
                if item.data.get("type") == ftype:
                    return float(item.data.get("value", 0.0))
    return 0.0


def convert_to_snapshots(income_data, balance_data, cash_data) -> list[QuarterlySnapshot]:
    """Converts FinMind flattened stimuli into ToneSoul QuarterlySnapshots."""
    # Group by date
    grouped = defaultdict(lambda: {"income": [], "balance": [], "cash": []})

    for item in income_data:
        grouped[item.date]["income"].append(item)
    for item in balance_data:
        grouped[item.date]["balance"].append(item)
    for item in cash_data:
        grouped[item.date]["cash"].append(item)

    snapshots = []
    # Sort dates to ensure chronological order
    for date in sorted(grouped.keys()):
        g = grouped[date]
        if not g["income"]:
            continue

        rev = get_value(g["income"], "Revenue")
        gp = get_value(g["income"], "GrossProfit")
        ni = get_value(g["income"], "IncomeAfterTaxes")
        eps = get_value(g["income"], "EPS")

        # Balance Sheet
        inv = get_value(g["balance"], "Inventory", ["Inventories"])
        ar = get_value(g["balance"], "AccountsReceivable", ["AccountsAndNotesReceivable"])
        cash = get_value(g["balance"], "CashAndCashEquivalents")
        std = get_value(g["balance"], "ShortTermBorrowings")

        # Cash Flow
        ocf = get_value(
            g["cash"], "CashFlowsFromOperatingActivities", ["NetCashInflowFromOperatingActivities"]
        )
        capex = get_value(g["cash"], "PropertyAndPlantAndEquipment")
        fcf = ocf - capex

        # TWSE values are often in thousands. ToneSoul relies on Billions for visuals but
        # ratios (margins, YoY) are scale-invariant, so division by 1_000_000_000 makes it Billions.
        scale = 1_000_000_000.0

        snap = QuarterlySnapshot(
            quarter=date,  # e.g. "2024-03-31"
            revenue=rev / scale,
            gross_profit=gp / scale,
            gross_margin=(gp / rev) if rev else 0.0,
            operating_income=get_value(g["income"], "OperatingIncome") / scale,
            net_income=ni / scale,
            eps=eps,  # EPS is not scaled
            inventory=inv / scale,
            accounts_receivable=ar / scale,
            cash=cash / scale,
            short_term_debt=std / scale,
            operating_cash_flow=ocf / scale,
            free_cash_flow=fcf / scale,
        )
        snapshots.append(snap)

    return snapshots


def main():
    print(f"\n{'=' * 80}")
    print(f"ToneSoul LIVE Market Scanner — MARGIN-SAFE HUNTER (即時頂息尋寶器)")
    print(f"Criteria: Price < 200 NTD | Yield > 4.0% | Live TWSE Data")
    print(f"{'=' * 80}")

    ingestor = MarketDataIngestor()
    if not ingestor.is_available:
        print("FinMind Data Ingestor is offline. Exiting.")
        return

    simulator = MultiPerspectiveSimulator(model_name="qwen3.5:4b")

    # We test a diverse pool of potential dividend stocks
    target_stocks = {
        "2324": "Compal (仁寶)",
        "2301": "Lite-On (光寶科)",
        "2356": "Inventec (英業達)",
        "4938": "Pegatron (和碩)",
        "5289": "Innodisk (宜鼎)",
    }

    results = []

    for stock_id, stock_name in target_stocks.items():
        print(f"\n🔍 [LIVE] Scanning {stock_id} {stock_name} ...")

        # 1. Fetch live valuation data
        val_data = ingestor.fetch_per_pbr(stock_id, start_date="2024-01-01")
        if not val_data:
            print(f"   ❌ Rejected: No live valuation data found via API.")
            continue

        latest_val = val_data[-1].data
        yield_pct = float(latest_val.get("dividend_yield", 0.0))

        price_data = ingestor.fetch_price(stock_id, start_date="2024-01-01")
        if not price_data:
            print(f"   ❌ Rejected: No live price data found via API.")
            continue

        current_price = float(price_data[-1].data.get("close", 0.0))

        # Filter 1 & 2
        if current_price > 200.0:
            print(f"   ❌ Rejected: LIVE Price {current_price} > 200 NTD")
            continue

        if yield_pct < 4.0:
            print(f"   ❌ Rejected: LIVE Yield {yield_pct}% < 4.0%")
            continue

        print(f"   ✅ Hard Filters Passed: Price NT${current_price} | Yield {yield_pct}%")

        # 3. Fetch Financial Data for Structural Engine
        print("   📥 Downloading live TWSE financial datasets...")
        profile = ingestor.fetch_full_profile(stock_id, start_date="2023-01-01")

        snapshots = convert_to_snapshots(
            profile["income_statement"], profile["balance_sheet"], profile["cash_flow"]
        )

        if len(snapshots) < 4:
            print(f"   ❌ Rejected: Not enough quarterly data to analyze trends.")
            continue

        # Get the latest 4-6 quarters to avoid LLM context overload
        recent_snapshots = snapshots[-6:]

        # Filter 3: Structural Math
        analyzer = SixStepAnalyzer(template=TechGrowthTemplate())
        signals = analyzer.find_tension_signals(recent_snapshots)
        struct_friction = analyzer.compute_friction(signals)
        print(f"   ↳ Live Structural Friction: {struct_friction:.2f}")

        if struct_friction > 0.4:
            print(f"   ❌ Rejected: Structural math too risky. Skiping AI.")
            continue

        # Filter 4: AI World Model
        print(f"   ✅ Pass: Triggering Live AI World Model Debate")
        context = simulator.run_simulation(f"{stock_id}_{stock_name}_LiveSafe", recent_snapshots)
        final_friction = (struct_friction * 0.7) + (context.perspective_friction * 0.3)

        results.append(
            {
                "stock": stock_name,
                "id": stock_id,
                "price": current_price,
                "yield": yield_pct,
                "struct_friction": struct_friction,
                "final_friction": final_friction,
                "consensus": context.consensus.replace("\n", " "),
            }
        )

    print(f"\n\n{'=' * 80}")
    print(f"🏆 TOP LIVE MARGIN-SAFE PICKS (即時頂息最佳標的)")
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
