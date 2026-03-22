"""Smoke test: Fetch Innodisk (5289) data and run Step 2 anomaly detection."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tonesoul.market.analyzer import QuarterlySnapshot, SixStepAnalyzer
from tonesoul.market.data_ingest import MarketDataIngestor


def main():
    print("=" * 60)
    print("ToneSoul Market Mirror — Smoke Test")
    print("Target: 宜鼎 (5289)")
    print("=" * 60)

    # Phase 1: Data Ingestion
    print("\n[Phase 1] Fetching data via FinMind...")
    ingestor = MarketDataIngestor()

    if not ingestor.is_available:
        print("❌ FinMind not available")
        return

    print("✅ FinMind loaded")

    # Fetch monthly revenue
    revenues = ingestor.fetch_monthly_revenue("5289", "2025-01-01")
    print(f"📊 Monthly revenue records: {len(revenues)}")

    if revenues:
        for r in revenues[-3:]:
            rev = r.data.get("revenue", 0)
            print(f"   {r.date}: revenue = {rev:,.0f}")

    # Fetch price data
    prices = ingestor.fetch_price("5289", "2025-01-01")
    print(f"📈 Price records: {len(prices)}")
    if prices:
        latest = prices[-1]
        print(f"   Latest: {latest.date} close={latest.data.get('close', 'n/a')}")

    # Phase 2: Anomaly Detection (using hardcoded Goodinfo data we verified)
    print("\n[Phase 2] Running tension analysis on verified Q data...")
    print("  (Using audited Goodinfo data from earlier analysis)")

    snapshots = [
        QuarterlySnapshot(
            quarter="2024Q4",
            revenue=22.28,
            gross_margin=0.291,
            net_income=2.71,
            eps=2.99,
            inventory=16.44,
            accounts_receivable=11.84,
            cash=30.00,
            short_term_debt=0,
            operating_cash_flow=6.42,
            free_cash_flow=5.85,
        ),
        QuarterlySnapshot(
            quarter="2025Q1",
            revenue=26.19,
            gross_margin=0.306,
            net_income=3.32,
            eps=3.68,
            inventory=15.77,
            accounts_receivable=14.87,
            cash=28.66,
            short_term_debt=0,
            operating_cash_flow=1.66,
            free_cash_flow=1.07,
        ),
        QuarterlySnapshot(
            quarter="2025Q2",
            revenue=30.28,
            gross_margin=0.259,
            net_income=1.74,
            eps=2.02,
            inventory=26.92,
            accounts_receivable=16.57,
            cash=20.68,
            short_term_debt=2.39,
            operating_cash_flow=-8.56,
            free_cash_flow=-8.50,
        ),
        QuarterlySnapshot(
            quarter="2025Q3",
            revenue=38.07,
            gross_margin=0.328,
            net_income=6.43,
            eps=6.87,
            inventory=28.74,
            accounts_receivable=24.19,
            cash=24.95,
            short_term_debt=1.83,
            operating_cash_flow=-0.16,
            free_cash_flow=-0.44,
        ),
        QuarterlySnapshot(
            quarter="2025Q4",
            revenue=48.07,
            gross_margin=0.332,
            net_income=8.73,
            eps=9.29,
            inventory=53.85,
            accounts_receivable=32.92,
            cash=16.45,
            short_term_debt=13.14,
            operating_cash_flow=-15.69,
            free_cash_flow=-16.12,
        ),
    ]

    analyzer = SixStepAnalyzer()

    # Step 2: Tension signals
    signals = analyzer.find_tension_signals(snapshots)
    print(f"\n⚡ Tension signals found: {len(signals)}")
    for s in signals:
        severity_icon = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "🔴"}.get(
            s.severity, "⚪"
        )
        print(f"   {severity_icon} [{s.severity.upper()}] {s.signal_id}")
        print(f"      {s.description}")

    # Friction score
    friction = analyzer.compute_friction(signals)
    print(f"\n📊 Friction score: {friction:.2f}")

    # Step 4: Trends
    trends = analyzer.analyze_trends(snapshots)
    print("\n📈 Trends:")
    for metric, trend in trends.items():
        print(f"   {metric}: {trend}")

    # Step 6: Scenarios
    scenarios = analyzer.build_scenarios(snapshots, current_price=905, annual_eps=21.72)
    print("\n🎯 Investment scenarios:")
    for sc in scenarios:
        print(
            f"   {sc.name.upper()}: EPS {sc.eps_estimate} × PE {sc.pe_multiple} = "
            f"NT${sc.target_price:,.0f} (prob {sc.probability:.0%})"
        )
        for c in sc.conditions[:2]:
            print(f"      - {c}")

    # Final verdict
    print(f"\n{'=' * 60}")
    print("ToneSoul GovernanceKernel Verdict:")
    print(f"  Friction: {friction:.2f}")
    if friction < 0.3:
        print("  Decision: BUY (low friction)")
    elif friction < 0.6:
        print("  Decision: BUY with conditions (moderate friction)")
    elif friction < 0.8:
        print("  Decision: WATCH — friction elevated, split entry")
    else:
        print("  Decision: HOLD — too much risk")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
