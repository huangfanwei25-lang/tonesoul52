"""ToneSoul Market Mirror: Gold Detector — 從沙裡找到金子的那一刻

Pure Python signal detector. Zero LLM dependency.
Uses only hard, auditable market data to detect the inflection point
where a stock transforms from ordinary to extraordinary.

Five signals:
1. Institutional Accumulation (法人連續買超)
2. Revenue Breakout (營收 YoY 突破)
3. Margin Inflection (毛利率拐點)
4. Inventory Clearance (去庫存完成)
5. PE Discount (本益比仍被低估)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GoldSignal:
    """A single detected signal indicating potential transformation."""
    signal_type: str        # e.g. "institutional_accumulation"
    strength: float         # 0.0 to 1.0
    detected_at: str        # ISO date string
    evidence: str           # Human-readable summary of raw data
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GoldReport:
    """Aggregate report from scanning a single stock."""
    stock_id: str
    gold_score: float         # Weighted composite: 0.0 to 1.0
    verdict: str              # "GOLD", "SILVER", "SAND"
    signals: List[GoldSignal] = field(default_factory=list)
    trailing_eps: float = 0.0
    current_price: float = 0.0
    current_pe: float = 0.0


class GoldDetector:
    """Scans raw FinMind data for transformation signals.
    
    All math is done in Python. No LLM calls.
    """

    # Signal weights for composite score
    WEIGHTS = {
        "institutional_accumulation": 0.25,
        "revenue_breakout": 0.25,
        "margin_inflection": 0.20,
        "inventory_clearance": 0.15,
        "pe_discount": 0.15,
    }

    def scan(
        self,
        stock_id: str,
        monthly_revenue: List[Dict[str, Any]],
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]],
        institutional_data: List[Dict[str, Any]],
        per_pbr_data: List[Dict[str, Any]],
        price_data: List[Dict[str, Any]],
    ) -> GoldReport:
        """Run all 5 signal detectors and produce a GoldReport."""
        signals: List[GoldSignal] = []

        # 1. Institutional Accumulation
        sig = self._detect_institutional_accumulation(institutional_data)
        if sig:
            signals.append(sig)

        # 2. Revenue Breakout
        sig = self._detect_revenue_breakout(monthly_revenue)
        if sig:
            signals.append(sig)

        # 3. Margin Inflection
        sig = self._detect_margin_inflection(income_statements)
        if sig:
            signals.append(sig)

        # 4. Inventory Clearance
        sig = self._detect_inventory_clearance(income_statements, balance_sheets)
        if sig:
            signals.append(sig)

        # 5. PE Discount
        sig = self._detect_pe_discount(per_pbr_data)
        if sig:
            signals.append(sig)

        # Compute composite score
        score = 0.0
        for s in signals:
            weight = self.WEIGHTS.get(s.signal_type, 0.0)
            score += s.strength * weight

        # Determine verdict
        if score >= 0.7:
            verdict = "GOLD"
        elif score >= 0.5:
            verdict = "SILVER"
        else:
            verdict = "SAND"

        # Extract trailing EPS and current price for context
        trailing_eps = self._calc_trailing_eps(income_statements)
        current_price = self._get_latest_price(price_data)
        current_pe = (current_price / trailing_eps) if trailing_eps > 0 else 0.0

        return GoldReport(
            stock_id=stock_id,
            gold_score=round(score, 3),
            verdict=verdict,
            signals=signals,
            trailing_eps=round(trailing_eps, 2),
            current_price=round(current_price, 2),
            current_pe=round(current_pe, 1),
        )

    # ─── Signal 1: Institutional Accumulation ─────────────────────

    def _detect_institutional_accumulation(
        self, institutional_data: List[Dict[str, Any]]
    ) -> Optional[GoldSignal]:
        """Detects sustained net buying by institutional investors (三大法人).
        
        Logic:
        - Look at the last 20 trading days.
        - Count days where net_buy > 0.
        - If >= 14/20 days are net positive → strong signal.
        """
        if not institutional_data:
            return None

        recent = institutional_data[-20:]
        if len(recent) < 5:
            return None

        net_buy_days = 0
        total_net = 0.0
        for row in recent:
            # FinMind fields: buy, sell → net = buy - sell
            buy = float(row.get("buy", 0) or 0)
            sell = float(row.get("sell", 0) or 0)
            net = buy - sell
            if net > 0:
                net_buy_days += 1
            total_net += net

        ratio = net_buy_days / len(recent)
        strength = min(1.0, ratio / 0.7)  # 70% buy days = full strength

        if strength < 0.3:
            return None

        return GoldSignal(
            signal_type="institutional_accumulation",
            strength=round(strength, 2),
            detected_at=str(recent[-1].get("date", "")),
            evidence=f"Institutional net buy {net_buy_days}/{len(recent)} days, total net: {total_net:,.0f} shares",
            raw_data={"net_buy_days": net_buy_days, "total_days": len(recent), "total_net": total_net},
        )

    # ─── Signal 2: Revenue Breakout ───────────────────────────────

    def _detect_revenue_breakout(
        self, monthly_revenue: List[Dict[str, Any]]
    ) -> Optional[GoldSignal]:
        """Detects a revenue YoY breakout after a period of decline or stagnation.
        
        Logic:
        - Look at the last 6 months of YoY growth.
        - If the most recent 2 months show > 10% YoY growth after ≥ 2 months of < 5% → breakout.
        """
        if len(monthly_revenue) < 6:
            return None

        recent_6 = monthly_revenue[-6:]
        yoy_values = []

        for row in recent_6:
            yoy = float(row.get("revenue_yoy", 0) or row.get("YoY", 0) or 0)
            yoy_values.append(yoy)

        if len(yoy_values) < 6:
            return None

        # Check pattern: stagnation then breakout
        early = yoy_values[:4]  # First 4 months
        late = yoy_values[4:]   # Last 2 months

        avg_early = sum(early) / len(early)
        avg_late = sum(late) / len(late)

        # Breakout: early was below 5%, late is above 10%
        if avg_early < 5.0 and avg_late > 10.0:
            strength = min(1.0, avg_late / 30.0)  # 30% YoY = full strength
        elif avg_late > 15.0:
            # Even without prior stagnation, strong growth is notable
            strength = min(1.0, avg_late / 40.0)
        else:
            return None

        return GoldSignal(
            signal_type="revenue_breakout",
            strength=round(max(strength, 0.3), 2),
            detected_at=str(recent_6[-1].get("date", "")),
            evidence=f"Revenue YoY: early avg {avg_early:.1f}% → recent avg {avg_late:.1f}% (breakout!)",
            raw_data={"yoy_values": yoy_values, "avg_early": avg_early, "avg_late": avg_late},
        )

    # ─── Signal 3: Margin Inflection ─────────────────────────────

    def _detect_margin_inflection(
        self, income_statements: List[Dict[str, Any]]
    ) -> Optional[GoldSignal]:
        """Detects a gross margin turning point (from declining to expanding).
        
        Logic:
        - Look at the last 4 quarters of gross margin.
        - If Q1-Q2 were declining and Q3-Q4 are expanding → inflection.
        """
        if len(income_statements) < 4:
            return None

        recent_4 = income_statements[-4:]
        margins = []

        for row in recent_4:
            rev = float(row.get("revenue", 0) or row.get("Revenue", 0) or 0)
            gp = float(row.get("gross_profit", 0) or row.get("GrossProfit", 0) or 0)
            if rev > 0:
                margins.append(gp / rev)
            else:
                margins.append(0.0)

        if len(margins) < 4:
            return None

        # Check inflection: first half declining, second half expanding
        first_half_trend = margins[1] - margins[0]
        second_half_trend = margins[3] - margins[2]

        if first_half_trend < -0.005 and second_half_trend > 0.005:
            # Classic V-shape inflection
            strength = min(1.0, abs(second_half_trend) / 0.03)
        elif margins[-1] > margins[-2] > margins[-3]:
            # Consecutive improvement
            improvement = margins[-1] - margins[-3]
            strength = min(1.0, improvement / 0.05)
        else:
            return None

        return GoldSignal(
            signal_type="margin_inflection",
            strength=round(max(strength, 0.3), 2),
            detected_at=str(recent_4[-1].get("date", "")),
            evidence=f"Gross margins: {[f'{m:.1%}' for m in margins]} — inflection detected",
            raw_data={"margins": margins},
        )

    # ─── Signal 4: Inventory Clearance ────────────────────────────

    def _detect_inventory_clearance(
        self, income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]],
    ) -> Optional[GoldSignal]:
        """Detects inventory-to-revenue ratio declining (destocking complete).
        
        Logic:
        - Calculate inventory / quarterly revenue for last 4 quarters.
        - If the ratio has been declining for 2+ consecutive quarters → clearance signal.
        """
        if len(balance_sheets) < 3 or len(income_statements) < 3:
            return None

        n = min(len(balance_sheets), len(income_statements), 4)
        ratios = []

        for i in range(-n, 0):
            inv = float(balance_sheets[i].get("inventory", 0) or balance_sheets[i].get("Inventory", 0) or 0)
            rev = float(income_statements[i].get("revenue", 0) or income_statements[i].get("Revenue", 0) or 0)
            if rev > 0:
                ratios.append(inv / rev)
            else:
                ratios.append(0.0)

        if len(ratios) < 3:
            return None

        # Check for consecutive declines
        declines = sum(1 for i in range(1, len(ratios)) if ratios[i] < ratios[i - 1])

        if declines >= 2:
            total_drop = ratios[0] - ratios[-1]
            strength = min(1.0, total_drop / 0.15)  # 15% ratio drop = full strength
            strength = max(strength, 0.3)
        else:
            return None

        return GoldSignal(
            signal_type="inventory_clearance",
            strength=round(strength, 2),
            detected_at=str(balance_sheets[-1].get("date", "")),
            evidence=f"Inventory/Revenue ratio: {[f'{r:.2f}' for r in ratios]} — clearance trend",
            raw_data={"ratios": ratios},
        )

    # ─── Signal 5: PE Discount ────────────────────────────────────

    def _detect_pe_discount(
        self, per_pbr_data: List[Dict[str, Any]]
    ) -> Optional[GoldSignal]:
        """Detects if current PE is significantly below its own historical average.
        
        Logic:
        - Calculate average PE over the full dataset.
        - If current PE < 0.7 * avg_pe → stock is undervalued relative to its own history.
        """
        if len(per_pbr_data) < 10:
            return None

        pe_values = []
        for row in per_pbr_data:
            pe = float(row.get("PER", 0) or row.get("per", 0) or 0)
            if 1.0 < pe < 200.0:  # Filter nonsense values
                pe_values.append(pe)

        if len(pe_values) < 10:
            return None

        avg_pe = sum(pe_values) / len(pe_values)
        current_pe = pe_values[-1]

        if current_pe < avg_pe * 0.7:
            discount = 1.0 - (current_pe / avg_pe)
            strength = min(1.0, discount / 0.4)  # 40% discount = full strength
        elif current_pe < avg_pe * 0.85:
            strength = 0.4
        else:
            return None

        return GoldSignal(
            signal_type="pe_discount",
            strength=round(strength, 2),
            detected_at=str(per_pbr_data[-1].get("date", "")),
            evidence=f"Current PE {current_pe:.1f}x vs historical avg {avg_pe:.1f}x ({(1 - current_pe/avg_pe)*100:.0f}% discount)",
            raw_data={"current_pe": current_pe, "avg_pe": avg_pe},
        )

    # ─── Helpers ──────────────────────────────────────────────────

    def _calc_trailing_eps(self, income_statements: List[Dict[str, Any]]) -> float:
        """Sum EPS from the last 4 quarterly income statements."""
        recent = income_statements[-4:]
        total = 0.0
        for row in recent:
            eps = float(row.get("eps", 0) or row.get("EPS", 0) or 0)
            total += eps
        return total

    def _get_latest_price(self, price_data: List[Dict[str, Any]]) -> float:
        """Get the most recent closing price."""
        if not price_data:
            return 0.0
        latest = price_data[-1]
        return float(latest.get("close", 0) or latest.get("Close", 0) or 0)
