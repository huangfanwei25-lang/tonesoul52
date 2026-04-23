"""Tests for tonesoul.market.analyzer — dataclasses, templates, SixStepAnalyzer."""
from __future__ import annotations

import pytest

from tonesoul.market.analyzer import (
    AnalysisResult,
    CyclicalTemplate,
    InvestmentScenario,
    QuarterlySnapshot,
    SixStepAnalyzer,
    TechGrowthTemplate,
    TensionSignal,
)


# ── Helper factories ───────────────────────────────────────────────────────────

def _snap(**kw) -> QuarterlySnapshot:
    defaults = {
        "quarter": "2025Q4",
        "revenue": 100.0,
        "gross_profit": 35.0,
        "gross_margin": 0.35,
        "operating_income": 15.0,
        "net_income": 12.0,
        "eps": 2.0,
        "inventory": 20.0,
        "accounts_receivable": 15.0,
        "cash": 50.0,
        "short_term_debt": 10.0,
        "operating_cash_flow": 18.0,
        "free_cash_flow": 14.0,
    }
    defaults.update(kw)
    return QuarterlySnapshot(**defaults)


# ── TechGrowthTemplate.find_tension_signals ───────────────────────────────────

class TestTechGrowthTemplateTensionSignals:
    def setup_method(self):
        self.tpl = TechGrowthTemplate()

    def test_empty_snapshots_no_signals(self):
        assert self.tpl.find_tension_signals([]) == []

    def test_single_snapshot_no_signals(self):
        assert self.tpl.find_tension_signals([_snap()]) == []

    def test_revenue_vs_ocf_divergence(self):
        prev = _snap(quarter="Q1", revenue=80.0, operating_cash_flow=20.0)
        latest = _snap(quarter="Q2", revenue=100.0, operating_cash_flow=10.0)
        signals = self.tpl.find_tension_signals([prev, latest])
        ids = [s.signal_id for s in signals]
        assert "revenue_vs_ocf" in ids

    def test_no_signal_when_ocf_grows(self):
        prev = _snap(quarter="Q1", revenue=80.0, operating_cash_flow=10.0)
        latest = _snap(quarter="Q2", revenue=100.0, operating_cash_flow=20.0)
        signals = self.tpl.find_tension_signals([prev, latest])
        assert all(s.signal_id != "revenue_vs_ocf" for s in signals)

    def test_negative_ocf_signal(self):
        prev = _snap(quarter="Q1")
        latest = _snap(quarter="Q2", operating_cash_flow=-5.0)
        signals = self.tpl.find_tension_signals([prev, latest])
        ids = [s.signal_id for s in signals]
        assert "negative_ocf" in ids

    def test_negative_ocf_high_severity_below_neg10(self):
        prev = _snap(quarter="Q1")
        latest = _snap(quarter="Q2", operating_cash_flow=-15.0)
        signals = self.tpl.find_tension_signals([prev, latest])
        ocf_sig = next(s for s in signals if s.signal_id == "negative_ocf")
        assert ocf_sig.severity == "high"

    def test_cash_vs_debt_signal(self):
        prev = _snap(quarter="Q1", cash=50.0, short_term_debt=10.0)
        latest = _snap(quarter="Q2", cash=30.0, short_term_debt=20.0)
        signals = self.tpl.find_tension_signals([prev, latest])
        ids = [s.signal_id for s in signals]
        assert "cash_vs_debt" in ids

    def test_inventory_signal_fires_when_outlpaces_revenue(self):
        prev = _snap(quarter="Q1", revenue=100.0, inventory=10.0)
        # inventory triples while revenue grows 10%
        latest = _snap(quarter="Q2", revenue=110.0, inventory=30.0)
        signals = self.tpl.find_tension_signals([prev, latest])
        ids = [s.signal_id for s in signals]
        assert "inventory_vs_revenue" in ids


# ── TechGrowthTemplate.analyze_trends ────────────────────────────────────────

class TestTechGrowthTemplateAnalyzeTrends:
    def setup_method(self):
        self.tpl = TechGrowthTemplate()

    def test_insufficient_data(self):
        result = self.tpl.analyze_trends([_snap()])
        assert "status" in result

    def test_revenue_accelerating(self):
        snaps = [
            _snap(quarter="Q1", revenue=80.0, gross_margin=0.30, eps=1.0),
            _snap(quarter="Q2", revenue=90.0, gross_margin=0.32, eps=1.5),
            _snap(quarter="Q3", revenue=100.0, gross_margin=0.33, eps=2.0),
        ]
        trends = self.tpl.analyze_trends(snaps)
        assert "revenue" in trends
        assert "gross_margin" in trends
        assert "eps" in trends

    def test_revenue_declining(self):
        snaps = [
            _snap(quarter="Q1", revenue=100.0, gross_margin=0.35, eps=2.0),
            _snap(quarter="Q2", revenue=90.0, gross_margin=0.33, eps=1.5),
            _snap(quarter="Q3", revenue=80.0, gross_margin=0.31, eps=1.0),
        ]
        trends = self.tpl.analyze_trends(snaps)
        assert "declining" in trends["revenue"]

    def test_eps_trend_formatted(self):
        snaps = [
            _snap(quarter="Q1", revenue=80.0, gross_margin=0.30, eps=1.00),
            _snap(quarter="Q2", revenue=90.0, gross_margin=0.31, eps=1.50),
            _snap(quarter="Q3", revenue=100.0, gross_margin=0.32, eps=2.00),
        ]
        trends = self.tpl.analyze_trends(snaps)
        assert "1.00" in trends["eps"]
        assert "2.00" in trends["eps"]


# ── TechGrowthTemplate.build_scenarios ───────────────────────────────────────

class TestTechGrowthTemplateBuildScenarios:
    def setup_method(self):
        self.tpl = TechGrowthTemplate()

    def test_empty_snapshots_returns_empty(self):
        assert self.tpl.build_scenarios([], current_price=100.0, annual_eps=5.0) == []

    def test_returns_three_scenarios(self):
        snaps = [_snap(eps=2.0)]
        scenarios = self.tpl.build_scenarios(snaps, current_price=80.0, annual_eps=8.0)
        assert len(scenarios) == 3

    def test_scenario_names(self):
        snaps = [_snap(eps=2.0)]
        scenarios = self.tpl.build_scenarios(snaps, current_price=80.0, annual_eps=8.0)
        names = [s.name for s in scenarios]
        assert "bull" in names
        assert "base" in names
        assert "bear" in names

    def test_bull_higher_than_bear(self):
        snaps = [_snap(eps=2.0)]
        scenarios = self.tpl.build_scenarios(snaps, current_price=80.0, annual_eps=8.0)
        bull = next(s for s in scenarios if s.name == "bull")
        bear = next(s for s in scenarios if s.name == "bear")
        assert bull.target_price >= bear.target_price

    def test_probabilities_sum_to_1(self):
        snaps = [_snap(eps=2.0)]
        scenarios = self.tpl.build_scenarios(snaps, current_price=80.0, annual_eps=8.0)
        total = sum(s.probability for s in scenarios)
        assert total == pytest.approx(1.0)


# ── CyclicalTemplate.find_tension_signals ─────────────────────────────────────

class TestCyclicalTemplateTensionSignals:
    def setup_method(self):
        self.tpl = CyclicalTemplate()

    def test_empty_no_signals(self):
        assert self.tpl.find_tension_signals([]) == []

    def test_single_snapshot_no_signals(self):
        assert self.tpl.find_tension_signals([_snap()]) == []

    def test_margin_crash_signal(self):
        prev = _snap(quarter="Q1", gross_margin=0.10)
        latest = _snap(quarter="Q2", gross_margin=0.03)
        signals = self.tpl.find_tension_signals([prev, latest])
        ids = [s.signal_id for s in signals]
        assert "margin_crash" in ids

    def test_deep_trough_signal(self):
        prev = _snap(quarter="Q1")
        latest = _snap(quarter="Q2", operating_cash_flow=-8.0)
        signals = self.tpl.find_tension_signals([prev, latest])
        ids = [s.signal_id for s in signals]
        assert "deep_trough_cash_burn" in ids

    def test_deep_trough_critical_below_neg10(self):
        prev = _snap(quarter="Q1")
        latest = _snap(quarter="Q2", operating_cash_flow=-15.0)
        signals = self.tpl.find_tension_signals([prev, latest])
        sig = next(s for s in signals if s.signal_id == "deep_trough_cash_burn")
        assert sig.severity == "critical"

    def test_inventory_build_during_loss_signal(self):
        prev = _snap(quarter="Q1", inventory=100.0, operating_income=5.0)
        latest = _snap(quarter="Q2", inventory=110.0, operating_income=-3.0)
        signals = self.tpl.find_tension_signals([prev, latest])
        ids = [s.signal_id for s in signals]
        assert "inventory_build_during_loss" in ids


# ── CyclicalTemplate.analyze_trends ──────────────────────────────────────────

class TestCyclicalTemplateAnalyzeTrends:
    def setup_method(self):
        self.tpl = CyclicalTemplate()

    def test_insufficient_data(self):
        result = self.tpl.analyze_trends([_snap()])
        assert "status" in result

    def test_expansion_detected(self):
        snaps = [
            _snap(quarter="Q1", gross_margin=0.05, eps=0.5),
            _snap(quarter="Q2", gross_margin=0.08, eps=1.0),
            _snap(quarter="Q3", gross_margin=0.12, eps=1.5),
        ]
        trends = self.tpl.analyze_trends(snaps)
        assert "expansion" in trends.get("cycle_phase", "")

    def test_contraction_detected(self):
        snaps = [
            _snap(quarter="Q1", gross_margin=0.15, eps=2.0),
            _snap(quarter="Q2", gross_margin=0.10, eps=1.5),
            _snap(quarter="Q3", gross_margin=0.05, eps=0.5),
        ]
        trends = self.tpl.analyze_trends(snaps)
        assert "contraction" in trends.get("cycle_phase", "")


# ── CyclicalTemplate.build_scenarios ──────────────────────────────────────────

class TestCyclicalTemplateBuildScenarios:
    def setup_method(self):
        self.tpl = CyclicalTemplate(book_value_per_share=50.0)

    def test_returns_three_scenarios(self):
        scenarios = self.tpl.build_scenarios([], current_price=40.0, annual_eps=1.0)
        assert len(scenarios) == 3

    def test_valuation_model_pbr(self):
        scenarios = self.tpl.build_scenarios([], current_price=40.0, annual_eps=1.0)
        for s in scenarios:
            assert s.valuation_model == "PBR"

    def test_bull_target_higher_than_bear(self):
        scenarios = self.tpl.build_scenarios([], current_price=40.0, annual_eps=1.0)
        bull = next(s for s in scenarios if s.name == "bull")
        bear = next(s for s in scenarios if s.name == "bear")
        assert bull.target_price > bear.target_price

    def test_bvps_reflected_in_target(self):
        tpl = CyclicalTemplate(book_value_per_share=60.0)
        scenarios = tpl.build_scenarios([], current_price=50.0, annual_eps=1.0)
        base = next(s for s in scenarios if s.name == "base")
        assert base.target_price == pytest.approx(60.0)  # bvps * 1.0


# ── SixStepAnalyzer.compute_friction ─────────────────────────────────────────

class TestComputeFriction:
    def setup_method(self):
        self.az = SixStepAnalyzer()

    def _sig(self, severity: str) -> TensionSignal:
        return TensionSignal(
            signal_id="test",
            severity=severity,
            description="",
            metric_a="a",
            metric_a_value=1.0,
            metric_b="b",
            metric_b_value=1.0,
            expected_relationship="",
            actual_relationship="",
        )

    def test_no_signals_returns_zero(self):
        assert self.az.compute_friction([]) == pytest.approx(0.0)

    def test_single_high_signal(self):
        score = self.az.compute_friction([self._sig("high")])
        assert score == pytest.approx(0.25)

    def test_single_critical_signal(self):
        score = self.az.compute_friction([self._sig("critical")])
        assert score == pytest.approx(0.40)

    def test_multiple_signals_diminishing_returns(self):
        signals = [self._sig("high"), self._sig("high"), self._sig("high")]
        score = self.az.compute_friction(signals)
        assert score < 3 * 0.25  # Less than linear sum

    def test_friction_capped_at_one(self):
        signals = [self._sig("critical")] * 10
        assert self.az.compute_friction(signals) <= 1.0

    def test_low_severity(self):
        score = self.az.compute_friction([self._sig("low")])
        assert score == pytest.approx(0.08)

    def test_medium_severity(self):
        score = self.az.compute_friction([self._sig("medium")])
        assert score == pytest.approx(0.15)


# ── SixStepAnalyzer template delegation ──────────────────────────────────────

class TestSixStepAnalyzerDelegation:
    def test_default_template_is_tech_growth(self):
        az = SixStepAnalyzer()
        assert isinstance(az.template, TechGrowthTemplate)

    def test_custom_template_injected(self):
        tpl = CyclicalTemplate()
        az = SixStepAnalyzer(template=tpl)
        assert az.template is tpl

    def test_find_tension_signals_delegates(self):
        az = SixStepAnalyzer()
        prev = _snap(quarter="Q1", revenue=80.0, operating_cash_flow=20.0)
        latest = _snap(quarter="Q2", revenue=100.0, operating_cash_flow=10.0)
        signals = az.find_tension_signals([prev, latest])
        assert any(s.signal_id == "revenue_vs_ocf" for s in signals)

    def test_analyze_trends_delegates(self):
        az = SixStepAnalyzer()
        snaps = [
            _snap(quarter="Q1", revenue=80.0, gross_margin=0.30, eps=1.0),
            _snap(quarter="Q2", revenue=90.0, gross_margin=0.32, eps=1.5),
            _snap(quarter="Q3", revenue=100.0, gross_margin=0.33, eps=2.0),
        ]
        trends = az.analyze_trends(snaps)
        assert "revenue" in trends

    def test_build_scenarios_delegates(self):
        az = SixStepAnalyzer()
        scenarios = az.build_scenarios([_snap(eps=2.0)], current_price=80.0, annual_eps=8.0)
        assert len(scenarios) == 3
