from __future__ import annotations

import pytest

from tonesoul.market.data_ingest import (
    FINMIND_DATASETS,
    MarketDataIngestor,
    MarketStimulus,
)


# ─── MarketStimulus ───────────────────────────────────────────────────────────

class TestMarketStimulus:
    def test_required_fields(self):
        ms = MarketStimulus(
            stock_id="2330",
            dataset="monthly_revenue",
            date="2025-01-01",
            data={"revenue": 100_000},
        )
        assert ms.stock_id == "2330"
        assert ms.dataset == "monthly_revenue"
        assert ms.date == "2025-01-01"
        assert ms.data["revenue"] == 100_000

    def test_default_source(self):
        ms = MarketStimulus(stock_id="x", dataset="d", date="2025-01-01", data={})
        assert ms.source == "FinMind/TWSE"

    def test_default_subjectivity_layer(self):
        ms = MarketStimulus(stock_id="x", dataset="d", date="2025-01-01", data={})
        assert ms.subjectivity_layer == "event"

    def test_fetched_at_auto_set(self):
        ms = MarketStimulus(stock_id="x", dataset="d", date="2025-01-01", data={})
        assert ms.fetched_at  # non-empty string

    def test_custom_source(self):
        ms = MarketStimulus(stock_id="x", dataset="d", date="d", data={}, source="Custom")
        assert ms.source == "Custom"


# ─── FINMIND_DATASETS ────────────────────────────────────────────────────────

class TestFinmindDatasets:
    def test_contains_expected_keys(self):
        for key in ("monthly_revenue", "income_statement", "balance_sheet",
                    "cash_flow", "institutional", "price"):
            assert key in FINMIND_DATASETS

    def test_values_are_strings(self):
        for value in FINMIND_DATASETS.values():
            assert isinstance(value, str)


# ─── MarketDataIngestor (FinMind not installed) ───────────────────────────────

class TestMarketDataIngestorNoFinMind:
    def test_is_available_false_when_no_finmind(self):
        ingestor = MarketDataIngestor()
        assert ingestor.is_available is False

    def test_fetch_monthly_revenue_returns_empty(self):
        ingestor = MarketDataIngestor()
        assert ingestor.fetch_monthly_revenue("2330") == []

    def test_fetch_income_statement_returns_empty(self):
        ingestor = MarketDataIngestor()
        assert ingestor.fetch_income_statement("2330") == []

    def test_fetch_balance_sheet_returns_empty(self):
        ingestor = MarketDataIngestor()
        assert ingestor.fetch_balance_sheet("2330") == []

    def test_fetch_cash_flow_returns_empty(self):
        ingestor = MarketDataIngestor()
        assert ingestor.fetch_cash_flow("2330") == []

    def test_fetch_price_returns_empty(self):
        ingestor = MarketDataIngestor()
        assert ingestor.fetch_price("2330") == []

    def test_fetch_per_pbr_returns_empty(self):
        ingestor = MarketDataIngestor()
        assert ingestor.fetch_per_pbr("2330") == []

    def test_fetch_institutional_returns_empty(self):
        ingestor = MarketDataIngestor()
        assert ingestor.fetch_institutional("2330") == []

    def test_fetch_full_profile_all_empty(self):
        ingestor = MarketDataIngestor()
        profile = ingestor.fetch_full_profile("2330")
        assert isinstance(profile, dict)
        for v in profile.values():
            assert v == []

    def test_fetch_full_profile_has_all_keys(self):
        ingestor = MarketDataIngestor()
        profile = ingestor.fetch_full_profile("2330")
        for key in ("monthly_revenue", "income_statement", "balance_sheet",
                    "cash_flow", "price", "per_pbr", "institutional"):
            assert key in profile
