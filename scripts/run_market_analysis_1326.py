"""Run ToneSoul Market Analyzer for 台化 (1326)."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tonesoul.market.analyzer import SixStepAnalyzer, QuarterlySnapshot


def main():
    print("=" * 60)
    print("ToneSoul Market Mirror — Targeted Analysis")
    print("Target: 台化 (1326) Formosa Chemicals & Fibre Corp.")
    print("=" * 60)

    # Unit: Billion NTD
    # Data approximated from 2024 public financial reports for testing tension logic.
    snapshots = [
        QuarterlySnapshot(
            quarter="2024Q1",
            revenue=83.9,
            gross_margin=0.0432,
            net_income=0.6,
            eps=0.10,
            inventory=45.0,
            accounts_receivable=32.0,
            cash=50.0,
            short_term_debt=80.0,
            operating_cash_flow=2.5,
            free_cash_flow=-1.0,
        ),
        QuarterlySnapshot(
            quarter="2024Q2",
            revenue=89.5,
            gross_margin=0.0585,
            net_income=0.8,
            eps=0.15,
            inventory=44.2,
            accounts_receivable=35.0,
            cash=48.0,
            short_term_debt=82.0,
            operating_cash_flow=5.0,
            free_cash_flow=1.2,
        ),
        QuarterlySnapshot(
            quarter="2024Q3",
            revenue=86.2,
            gross_margin=0.0211,
            net_income=0.0,
            eps=0.00,
            inventory=46.5,
            accounts_receivable=34.0,
            cash=45.0,
            short_term_debt=85.0,
            operating_cash_flow=-3.2,
            free_cash_flow=-6.5,
        ),
        QuarterlySnapshot(
            quarter="2024Q4",
            revenue=89.0,
            gross_margin=0.0362,
            net_income=-1.1,
            eps=-0.19,
            inventory=48.0,
            accounts_receivable=33.0,
            cash=40.0,
            short_term_debt=90.0,
            operating_cash_flow=-8.5,
            free_cash_flow=-12.0,
        ),
    ]

    print("\n[Phase 2] Running tension analysis on 2024 Q1-Q4 data...")
    from tonesoul.market.analyzer import CyclicalTemplate

    # Using 54.0 as an estimated BVPS for 台化 (1326) context
    analyzer = SixStepAnalyzer(template=CyclicalTemplate(book_value_per_share=54.0))

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
    print(f"\n📈 Trends:")
    for metric, trend in trends.items():
        print(f"   {metric}: {trend}")

    # Step 6: Scenarios
    scenarios = analyzer.build_scenarios(snapshots, current_price=41.5, annual_eps=0.06)
    print(f"\n🎯 Investment scenarios:")
    for sc in scenarios:
        if sc.valuation_model == "PBR":
            print(
                f"   {sc.name.upper()}: BVPS {sc.bvps_estimate} × PBR {sc.pbr_multiple} = NT${sc.target_price:,.0f} (prob {sc.probability:.0%})"
            )
        else:
            print(
                f"   {sc.name.upper()}: EPS {sc.eps_estimate} × PE {sc.pe_multiple} = NT${sc.target_price:,.0f} (prob {sc.probability:.0%})"
            )
        for c in sc.conditions[:2]:
            print(f"      - {c}")

    # Final verdict
    print(f"\n{'=' * 60}")
    print(f"ToneSoul GovernanceKernel Verdict for 台化 (1326):")
    print(f"  Friction: {friction:.2f}")
    if friction < 0.3:
        print(f"  Decision: BUY (low friction)")
    elif friction < 0.6:
        print(f"  Decision: BUY with conditions (moderate friction)")
    elif friction < 0.8:
        print(f"  Decision: WATCH — friction elevated, split entry")
    else:
        print(f"  Decision: HOLD — too much risk")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
