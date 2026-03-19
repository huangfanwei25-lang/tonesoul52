"""ToneSoul Gold Detector — Multi-Stock Validation

Scans a diverse watchlist of:
- 🌟 Star stocks (currently thriving)
- 💀 Fallen stocks (unexpectedly collapsed)

Uses only hard data, zero LLM. Pure Python signal detection.
Includes FinMind data consolidation logic to convert pivot-format
financial statements into quarterly flat records.
"""

import sys
import os
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tonesoul.market.gold_detector import GoldDetector, GoldReport
from tonesoul.market.data_ingest import MarketDataIngestor


# Diverse watchlist: requested stocks
WATCHLIST = [
    ("3037", "欣興 Unimicron", "🌟 ABF Carrier"),
    ("2368", "金像電 GCE", "🌟 Server PCB"),
    ("2308", "台達電 Delta", "🌟 Power/Thermal"),
    ("3163", "波若威 Browave", "🌟 Silicon Photonics"),
    ("3017", "奇鋐 AVC", "🌟 Thermal Solutions"),
]


def consolidate_financial_pivot(stimuli_list):
    """Consolidate FinMind pivot-format rows into flat quarterly dicts.
    
    FinMind returns financial statements as:
        {date: "2024-03-31", type: "Revenue", value: 12345}
        {date: "2024-03-31", type: "GrossProfit", value: 3456}
    
    We consolidate into:
        {date: "2024-03-31", Revenue: 12345, GrossProfit: 3456, ...}
    """
    quarters = defaultdict(dict)
    for s in stimuli_list:
        d = s.data
        date = d.get("date", "")
        field_type = d.get("type", "")
        value = d.get("value", 0)
        if date and field_type:
            quarters[date]["date"] = date
            quarters[date][field_type] = value
    
    # Sort by date and return as list
    return [v for k, v in sorted(quarters.items())]


def consolidate_institutional(stimuli_list):
    """Consolidate institutional investor data by date.
    
    FinMind returns one row per investor type per day:
        {date: "2025-03-10", name: "Foreign_Investor", buy: 1000, sell: 500}
        {date: "2025-03-10", name: "Investment_Trust", buy: 200, sell: 100}
    
    We consolidate into one row per date with total buy/sell.
    """
    daily = defaultdict(lambda: {"buy": 0, "sell": 0, "date": ""})
    for s in stimuli_list:
        d = s.data
        date = d.get("date", "")
        if not date:
            continue
        daily[date]["date"] = date
        daily[date]["buy"] += float(d.get("buy", 0) or 0)
        daily[date]["sell"] += float(d.get("sell", 0) or 0)
    
    return [v for k, v in sorted(daily.items())]


def scan_single(ingestor, detector, stock_id, start_date="2024-06-01"):
    """Fetch data, consolidate, and run GoldDetector for one stock."""
    revenue_raw = ingestor.fetch_monthly_revenue(stock_id, start_date)
    income_raw = ingestor.fetch_income_statement(stock_id, start_date)
    balance_raw = ingestor.fetch_balance_sheet(stock_id, start_date)
    inst_raw = ingestor.fetch_institutional(stock_id, start_date)
    per_pbr_raw = ingestor.fetch_per_pbr(stock_id, start_date)
    price_raw = ingestor.fetch_price(stock_id, start_date)

    # Consolidate pivot-format financial data into quarterly flat dicts
    income_data = consolidate_financial_pivot(income_raw)
    balance_data = consolidate_financial_pivot(balance_raw)
    
    # Monthly revenue is already flat (one row per month)
    revenue_data = [s.data for s in revenue_raw]
    
    # Institutional: consolidate per-investor-type rows into daily totals
    inst_data = consolidate_institutional(inst_raw)
    
    # PER/PBR and Price are already flat
    per_pbr_data = [s.data for s in per_pbr_raw]
    price_data = [s.data for s in price_raw]

    return detector.scan(
        stock_id=stock_id,
        monthly_revenue=revenue_data,
        income_statements=income_data,
        balance_sheets=balance_data,
        institutional_data=inst_data,
        per_pbr_data=per_pbr_data,
        price_data=price_data,
    )


def main():
    print(f"\n{'═' * 70}")
    print(f"  ToneSoul Gold Detector — 從沙裡找到金子的那一刻")
    print(f"  Multi-Stock Validation (Pure Python, Zero LLM)")
    print(f"{'═' * 70}")

    ingestor = MarketDataIngestor()
    if not ingestor.is_available:
        print("❌ FinMind is not available. Install: pip install FinMind")
        return

    detector = GoldDetector()
    results = []

    target_watchlist = WATCHLIST
    if len(sys.argv) > 1:
        custom_id = sys.argv[1]
        target_watchlist = [(custom_id, "User Target", "🔍 Custom Scan")]

    for stock_id, name, tag in target_watchlist:
        print(f"\n📡 Scanning {stock_id} {name} ({tag})...")
        try:
            report = scan_single(ingestor, detector, stock_id)
            results.append((stock_id, name, tag, report))
            emoji = {"GOLD": "🥇", "SILVER": "🥈", "SAND": "⏳"}[report.verdict]
            print(f"   {emoji} Score={report.gold_score:.3f} | EPS={report.trailing_eps:.1f} | PE={report.current_pe:.1f}x | Price={report.current_price:.0f}")
            for sig in report.signals:
                print(f"      ✦ {sig.signal_type}: {sig.strength:.2f} — {sig.evidence}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback; traceback.print_exc()
        time.sleep(1)

    # ─── Leaderboard ──────────────────────────────────────────────
    print(f"\n{'═' * 70}")
    print(f"  📊 GOLD DETECTOR LEADERBOARD")
    print(f"{'═' * 70}")
    print(f"  {'#':<3} {'V':<6} {'Score':<7} {'ID':<6} {'Name':<16} {'Tag':<22} {'EPS':>6} {'PE':>6} {'Price':>7}")
    print(f"  {'─' * 3} {'─' * 6} {'─' * 7} {'─' * 6} {'─' * 16} {'─' * 22} {'─' * 6} {'─' * 6} {'─' * 7}")

    sorted_r = sorted(results, key=lambda x: x[3].gold_score, reverse=True)
    for i, (sid, name, tag, r) in enumerate(sorted_r, 1):
        emoji = {"GOLD": "🥇", "SILVER": "🥈", "SAND": "⏳"}[r.verdict]
        short_name = name[:14]
        short_tag = tag[:20]
        print(f"  {i:<3} {emoji:<4} {r.gold_score:<7.3f} {sid:<6} {short_name:<16} {short_tag:<22} {r.trailing_eps:>6.1f} {r.current_pe:>6.1f} {r.current_price:>7.0f}")

    print(f"\n{'═' * 70}\n")


if __name__ == "__main__":
    main()
