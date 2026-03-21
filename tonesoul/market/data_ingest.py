"""ToneSoul Market Data Ingestor — Phase 1 Data Layer.

Fetches auditable financial data from TWSE/MOPS via FinMind,
converts it into ToneSoul EnvironmentStimulus format for governance processing.

Data sources:
- Monthly revenue (月營收)
- Quarterly income statement (損益表)
- Quarterly balance sheet (資產負債表)
- Quarterly cash flow statement (現金流量表)
- Institutional investor activity (法人買賣超)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FINMIND_DATASETS = {
    "monthly_revenue": "TaiwanStockMonthRevenue",
    "income_statement": "TaiwanStockFinancialStatements",
    "balance_sheet": "TaiwanStockBalanceSheet",
    "cash_flow": "TaiwanStockCashFlowsStatement",
    "institutional": "TaiwanStockInstitutionalInvestorsBuySell",
    "margin": "TaiwanStockMarginPurchaseShortSale",
    "price": "TaiwanStockPrice",
    "dividend": "TaiwanStockDividend",
    "per_pbr": "TaiwanStockPER",
}


@dataclass
class MarketStimulus:
    """A single market data point converted to ToneSoul stimulus format.

    This mirrors EnvironmentStimulus but is specialized for financial data.
    It carries provenance (data source, fetch timestamp) and can be promoted
    through SubjectivityLayer tagging (event vs meaning vs tension).
    """

    stock_id: str
    dataset: str
    date: str
    data: Dict[str, Any]
    source: str = "FinMind/TWSE"
    fetched_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    subjectivity_layer: str = "event"  # raw data = event layer


class MarketDataIngestor:
    """Fetches Taiwan stock financial data via FinMind.

    Usage:
        ingestor = MarketDataIngestor()
        stimuli = ingestor.fetch_monthly_revenue("5289", "2025-01-01")
    """

    def __init__(self, token: Optional[str] = None):
        try:
            from FinMind.data import DataLoader

            self._loader = DataLoader()
            if token:
                self._loader.login_by_token(api_token=token)
            self._available = True
        except ImportError:
            logger.warning("FinMind not installed. pip install FinMind")
            self._available = False
            self._loader = None

    @property
    def is_available(self) -> bool:
        return self._available

    # -----------------------------------------------------------------
    # Monthly Revenue (月營收)
    # -----------------------------------------------------------------

    def fetch_monthly_revenue(
        self,
        stock_id: str,
        start_date: str = "2024-01-01",
    ) -> List[MarketStimulus]:
        """Fetch monthly revenue data from TWSE/MOPS.

        Returns a list of MarketStimulus, one per month.
        Key fields: revenue, revenue_month, revenue_year,
                    revenue_yoy (year-over-year growth).
        """
        if not self._available:
            return []

        df = self._loader.taiwan_stock_month_revenue(
            stock_id=stock_id,
            start_date=start_date,
        )
        if df is None or df.empty:
            logger.warning("No monthly revenue data for %s", stock_id)
            return []

        stimuli = []
        for _, row in df.iterrows():
            data = row.to_dict()
            # Calculate YoY if possible
            stimulus = MarketStimulus(
                stock_id=stock_id,
                dataset="monthly_revenue",
                date=str(data.get("date", "")),
                data=data,
            )
            stimuli.append(stimulus)

        logger.info("Fetched %d monthly revenue records for %s", len(stimuli), stock_id)
        return stimuli

    # -----------------------------------------------------------------
    # Quarterly Financial Statements (季報)
    # -----------------------------------------------------------------

    def fetch_income_statement(
        self,
        stock_id: str,
        start_date: str = "2024-01-01",
    ) -> List[MarketStimulus]:
        """Fetch quarterly income statement (損益表).

        Key fields: revenue, gross_profit, operating_income,
                    net_income, eps.
        """
        return self._fetch_financial(
            stock_id,
            "TaiwanStockFinancialStatements",
            "income_statement",
            start_date,
        )

    def fetch_balance_sheet(
        self,
        stock_id: str,
        start_date: str = "2024-01-01",
    ) -> List[MarketStimulus]:
        """Fetch quarterly balance sheet (資產負債表).

        Key fields: total_assets, inventory, accounts_receivable,
                    cash_and_equivalents, total_liabilities, equity.
        """
        return self._fetch_financial(
            stock_id,
            "TaiwanStockBalanceSheet",
            "balance_sheet",
            start_date,
        )

    def fetch_cash_flow(
        self,
        stock_id: str,
        start_date: str = "2024-01-01",
    ) -> List[MarketStimulus]:
        """Fetch quarterly cash flow statement (現金流量表).

        Key fields: operating_cash_flow, investing_cash_flow,
                    financing_cash_flow, free_cash_flow.
        """
        return self._fetch_financial(
            stock_id,
            "TaiwanStockCashFlowsStatement",
            "cash_flow",
            start_date,
        )

    # -----------------------------------------------------------------
    # Price & Valuation (股價 + 估值)
    # -----------------------------------------------------------------

    def fetch_price(
        self,
        stock_id: str,
        start_date: str = "2024-01-01",
    ) -> List[MarketStimulus]:
        """Fetch daily OHLCV price data."""
        if not self._available:
            return []

        df = self._loader.taiwan_stock_daily(
            stock_id=stock_id,
            start_date=start_date,
        )
        if df is None or df.empty:
            return []

        stimuli = []
        for _, row in df.iterrows():
            stimuli.append(
                MarketStimulus(
                    stock_id=stock_id,
                    dataset="price",
                    date=str(row.get("date", "")),
                    data=row.to_dict(),
                )
            )

        logger.info("Fetched %d price records for %s", len(stimuli), stock_id)
        return stimuli

    def fetch_per_pbr(
        self,
        stock_id: str,
        start_date: str = "2024-01-01",
    ) -> List[MarketStimulus]:
        """Fetch PE ratio, PBR, dividend yield data."""
        if not self._available:
            return []

        df = self._loader.taiwan_stock_per_pbr(
            stock_id=stock_id,
            start_date=start_date,
        )
        if df is None or df.empty:
            return []

        return [
            MarketStimulus(
                stock_id=stock_id,
                dataset="per_pbr",
                date=str(row.get("date", "")),
                data=row.to_dict(),
            )
            for _, row in df.iterrows()
        ]

    # -----------------------------------------------------------------
    # Institutional Investors (法人買賣超)
    # -----------------------------------------------------------------

    def fetch_institutional(
        self,
        stock_id: str,
        start_date: str = "2024-01-01",
    ) -> List[MarketStimulus]:
        """Fetch institutional investor buy/sell data (三大法人)."""
        if not self._available:
            return []

        df = self._loader.taiwan_stock_institutional_investors(
            stock_id=stock_id,
            start_date=start_date,
        )
        if df is None or df.empty:
            return []

        return [
            MarketStimulus(
                stock_id=stock_id,
                dataset="institutional",
                date=str(row.get("date", "")),
                data=row.to_dict(),
            )
            for _, row in df.iterrows()
        ]

    # -----------------------------------------------------------------
    # Convenience: Fetch All
    # -----------------------------------------------------------------

    def fetch_full_profile(
        self,
        stock_id: str,
        start_date: str = "2024-01-01",
    ) -> Dict[str, List[MarketStimulus]]:
        """Fetch all available data for a stock.

        Returns a dict keyed by dataset name.
        """
        return {
            "monthly_revenue": self.fetch_monthly_revenue(stock_id, start_date),
            "income_statement": self.fetch_income_statement(stock_id, start_date),
            "balance_sheet": self.fetch_balance_sheet(stock_id, start_date),
            "cash_flow": self.fetch_cash_flow(stock_id, start_date),
            "price": self.fetch_price(stock_id, start_date),
            "per_pbr": self.fetch_per_pbr(stock_id, start_date),
            "institutional": self.fetch_institutional(stock_id, start_date),
        }

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _fetch_financial(
        self,
        stock_id: str,
        dataset_id: str,
        dataset_name: str,
        start_date: str,
    ) -> List[MarketStimulus]:
        """Generic fetcher for financial statement datasets."""
        if not self._available:
            return []

        try:
            method_map = {
                "income_statement": "taiwan_stock_financial_statement",
                "balance_sheet": "taiwan_stock_balance_sheet",
                "cash_flow": "taiwan_stock_cash_flows_statement",
            }
            method_name = method_map.get(dataset_name)
            if not method_name:
                raise ValueError(f"Unknown dataset_name: {dataset_name}")

            fetch_method = getattr(self._loader, method_name)
            df = fetch_method(
                stock_id=stock_id,
                start_date=start_date,
            )
        except Exception as exc:
            logger.warning("Failed to fetch %s for %s: %s", dataset_name, stock_id, exc)
            return []

        if df is None or df.empty:
            logger.warning("No %s data for %s", dataset_name, stock_id)
            return []

        stimuli = []
        for _, row in df.iterrows():
            stimuli.append(
                MarketStimulus(
                    stock_id=stock_id,
                    dataset=dataset_name,
                    date=str(row.get("date", "")),
                    data=row.to_dict(),
                )
            )

        logger.info("Fetched %d %s records for %s", len(stimuli), dataset_name, stock_id)
        return stimuli
