from __future__ import annotations

from dataclasses import dataclass

from tonesoul.market.data_ingest import MarketDataIngestor, MarketStimulus


@dataclass
class _FakeRow:
    payload: dict

    def to_dict(self) -> dict:
        return dict(self.payload)

    def get(self, key: str, default=None):
        return self.payload.get(key, default)


class _FakeDataFrame:
    def __init__(self, rows: list[dict]):
        self._rows = [_FakeRow(row) for row in rows]
        self.empty = not rows

    def iterrows(self):
        for index, row in enumerate(self._rows):
            yield index, row


class _Loader:
    def __init__(
        self, *, monthly=None, daily=None, per_pbr=None, institutional=None, financial=None
    ):
        self._monthly = monthly
        self._daily = daily
        self._per_pbr = per_pbr
        self._institutional = institutional
        self._financial = financial

    def taiwan_stock_month_revenue(self, **kwargs):
        return self._monthly

    def taiwan_stock_daily(self, **kwargs):
        return self._daily

    def taiwan_stock_per_pbr(self, **kwargs):
        return self._per_pbr

    def taiwan_stock_institutional_investors(self, **kwargs):
        return self._institutional

    def taiwan_stock_financial_statement(self, **kwargs):
        if isinstance(self._financial, Exception):
            raise self._financial
        return self._financial

    def taiwan_stock_balance_sheet(self, **kwargs):
        if isinstance(self._financial, Exception):
            raise self._financial
        return self._financial

    def taiwan_stock_cash_flows_statement(self, **kwargs):
        if isinstance(self._financial, Exception):
            raise self._financial
        return self._financial


def _ingestor(*, available=True, loader=None) -> MarketDataIngestor:
    ingestor = MarketDataIngestor.__new__(MarketDataIngestor)
    ingestor._available = available
    ingestor._loader = loader
    return ingestor


def test_fetch_monthly_revenue_returns_empty_when_unavailable() -> None:
    ingestor = _ingestor(available=False, loader=None)

    assert ingestor.fetch_monthly_revenue("5289") == []


def test_fetch_monthly_revenue_converts_rows_to_market_stimuli() -> None:
    ingestor = _ingestor(
        loader=_Loader(
            monthly=_FakeDataFrame(
                [
                    {"date": "2026-01-01", "revenue": 100},
                    {"date": "2026-02-01", "revenue": 120},
                ]
            )
        )
    )

    stimuli = ingestor.fetch_monthly_revenue("5289")

    assert len(stimuli) == 2
    assert all(isinstance(item, MarketStimulus) for item in stimuli)
    assert stimuli[0].stock_id == "5289"
    assert stimuli[0].dataset == "monthly_revenue"
    assert stimuli[1].data["revenue"] == 120


def test_fetch_financial_returns_empty_on_unknown_dataset_name() -> None:
    ingestor = _ingestor(loader=_Loader(financial=_FakeDataFrame([{"date": "2026Q1"}])))

    assert ingestor._fetch_financial("5289", "ignored", "unknown", "2024-01-01") == []


def test_fetch_financial_returns_empty_when_loader_raises() -> None:
    ingestor = _ingestor(loader=_Loader(financial=RuntimeError("loader failed")))

    assert ingestor.fetch_income_statement("5289") == []


def test_fetch_financial_converts_rows_for_statement_dataset() -> None:
    ingestor = _ingestor(
        loader=_Loader(
            financial=_FakeDataFrame(
                [
                    {"date": "2026Q1", "revenue": 200},
                    {"date": "2026Q2", "revenue": 240},
                ]
            )
        )
    )

    stimuli = ingestor.fetch_balance_sheet("5289")

    assert [item.dataset for item in stimuli] == ["balance_sheet", "balance_sheet"]
    assert [item.date for item in stimuli] == ["2026Q1", "2026Q2"]


def test_fetch_price_and_per_pbr_return_empty_for_empty_dataframes() -> None:
    ingestor = _ingestor(
        loader=_Loader(
            daily=_FakeDataFrame([]),
            per_pbr=_FakeDataFrame([]),
        )
    )

    assert ingestor.fetch_price("5289") == []
    assert ingestor.fetch_per_pbr("5289") == []


def test_fetch_full_profile_aggregates_all_fetchers(monkeypatch) -> None:
    ingestor = _ingestor(loader=_Loader())
    monkeypatch.setattr(ingestor, "fetch_monthly_revenue", lambda stock_id, start_date: ["monthly"])
    monkeypatch.setattr(ingestor, "fetch_income_statement", lambda stock_id, start_date: ["income"])
    monkeypatch.setattr(ingestor, "fetch_balance_sheet", lambda stock_id, start_date: ["balance"])
    monkeypatch.setattr(ingestor, "fetch_cash_flow", lambda stock_id, start_date: ["cash"])
    monkeypatch.setattr(ingestor, "fetch_price", lambda stock_id, start_date: ["price"])
    monkeypatch.setattr(ingestor, "fetch_per_pbr", lambda stock_id, start_date: ["per"])
    monkeypatch.setattr(ingestor, "fetch_institutional", lambda stock_id, start_date: ["inst"])

    profile = ingestor.fetch_full_profile("5289", "2025-01-01")

    assert profile == {
        "monthly_revenue": ["monthly"],
        "income_statement": ["income"],
        "balance_sheet": ["balance"],
        "cash_flow": ["cash"],
        "price": ["price"],
        "per_pbr": ["per"],
        "institutional": ["inst"],
    }
