from __future__ import annotations

from tonesoul.market.gold_detector import GoldDetector, GoldSignal


def test_institutional_accumulation_requires_enough_positive_days() -> None:
    detector = GoldDetector()

    assert detector._detect_institutional_accumulation([]) is None
    assert detector._detect_institutional_accumulation([{"buy": 1, "sell": 0}] * 4) is None
    assert (
        detector._detect_institutional_accumulation(
            [{"date": f"2026-03-{day:02d}", "buy": 10, "sell": 30} for day in range(1, 21)]
        )
        is None
    )


def test_institutional_accumulation_detects_strong_buying_signal() -> None:
    detector = GoldDetector()
    data = []
    for day in range(1, 21):
        if day <= 15:
            data.append({"date": f"2026-03-{day:02d}", "buy": 120, "sell": 20})
        else:
            data.append({"date": f"2026-03-{day:02d}", "buy": 20, "sell": 60})

    signal = detector._detect_institutional_accumulation(data)

    assert signal is not None
    assert signal.signal_type == "institutional_accumulation"
    assert signal.raw_data["net_buy_days"] == 15
    assert signal.detected_at == "2026-03-20"


def test_revenue_breakout_detects_stagnation_then_breakout() -> None:
    detector = GoldDetector()
    data = [
        {"date": "2025-10-01", "revenue_yoy": 1.0},
        {"date": "2025-11-01", "revenue_yoy": 2.0},
        {"date": "2025-12-01", "revenue_yoy": 3.0},
        {"date": "2026-01-01", "revenue_yoy": 4.0},
        {"date": "2026-02-01", "revenue_yoy": 18.0},
        {"date": "2026-03-01", "revenue_yoy": 22.0},
    ]

    signal = detector._detect_revenue_breakout(data)

    assert signal is not None
    assert signal.signal_type == "revenue_breakout"
    assert signal.raw_data["avg_early"] < 5.0
    assert signal.raw_data["avg_late"] > 10.0


def test_margin_inflection_detects_consecutive_improvement() -> None:
    detector = GoldDetector()
    data = [
        {"date": "2025Q4", "revenue": 100, "gross_profit": 20},
        {"date": "2026Q1", "revenue": 100, "gross_profit": 18},
        {"date": "2026Q2", "revenue": 100, "gross_profit": 24},
        {"date": "2026Q3", "revenue": 100, "gross_profit": 30},
    ]

    signal = detector._detect_margin_inflection(data)

    assert signal is not None
    assert signal.signal_type == "margin_inflection"
    assert signal.raw_data["margins"][-1] > signal.raw_data["margins"][-2]


def test_inventory_clearance_detects_declining_inventory_ratio() -> None:
    detector = GoldDetector()
    balance_sheets = [
        {"date": "2025Q4", "inventory": 100},
        {"date": "2026Q1", "inventory": 80},
        {"date": "2026Q2", "inventory": 60},
    ]
    income_statements = [
        {"date": "2025Q4", "revenue": 100},
        {"date": "2026Q1", "revenue": 100},
        {"date": "2026Q2", "revenue": 100},
    ]

    signal = detector._detect_inventory_clearance(income_statements, balance_sheets)

    assert signal is not None
    assert signal.signal_type == "inventory_clearance"
    assert signal.raw_data["ratios"] == [1.0, 0.8, 0.6]


def test_pe_discount_filters_noise_and_detects_discount() -> None:
    detector = GoldDetector()
    data = [{"date": f"2025-{month:02d}-01", "PER": pe} for month, pe in enumerate([0, 500, 20, 22, 21, 23, 24, 25, 26, 27, 28, 12], start=1)]

    signal = detector._detect_pe_discount(data)

    assert signal is not None
    assert signal.signal_type == "pe_discount"
    assert signal.raw_data["current_pe"] == 12.0
    assert signal.raw_data["avg_pe"] > signal.raw_data["current_pe"]


def test_scan_aggregates_signals_into_gold_report(monkeypatch) -> None:
    detector = GoldDetector()
    monkeypatch.setattr(
        detector,
        "_detect_institutional_accumulation",
        lambda data: GoldSignal("institutional_accumulation", 1.0, "2026-03-20", "inst"),
    )
    monkeypatch.setattr(
        detector,
        "_detect_revenue_breakout",
        lambda data: GoldSignal("revenue_breakout", 1.0, "2026-03-20", "rev"),
    )
    monkeypatch.setattr(
        detector,
        "_detect_margin_inflection",
        lambda data: GoldSignal("margin_inflection", 1.0, "2026-03-20", "margin"),
    )
    monkeypatch.setattr(
        detector,
        "_detect_inventory_clearance",
        lambda income, balance: GoldSignal("inventory_clearance", 1.0, "2026-03-20", "inventory"),
    )
    monkeypatch.setattr(
        detector,
        "_detect_pe_discount",
        lambda data: GoldSignal("pe_discount", 1.0, "2026-03-20", "pe"),
    )
    monkeypatch.setattr(detector, "_calc_trailing_eps", lambda income: 8.0)
    monkeypatch.setattr(detector, "_get_latest_price", lambda prices: 80.0)

    report = detector.scan("5289", [], [], [], [], [], [])

    assert report.stock_id == "5289"
    assert report.gold_score == 1.0
    assert report.verdict == "GOLD"
    assert report.trailing_eps == 8.0
    assert report.current_price == 80.0
    assert report.current_pe == 10.0
    assert len(report.signals) == 5
