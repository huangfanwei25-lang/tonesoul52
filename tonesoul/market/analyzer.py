"""ToneSoul Six-Step Financial Analyzer — Phase 2 Analysis Layer.

Automates the user's six-step financial analysis framework:
  1. Build financial structure
  2. Find anomaly signals (→ TensionEngine)
  3. Reconstruct business model (→ DreamEngine)
  4. Time series analysis (→ Consolidator)
  5. Management language analysis (→ SubjectivityLayer)
  6. Build investment scenarios (→ GovernanceKernel)
"""

from __future__ import annotations

import logging
import typing
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step output schemas
# ---------------------------------------------------------------------------


@dataclass
class TensionSignal:
    """A single anomaly / tension point found in financial data."""

    signal_id: str
    severity: str  # "low" | "medium" | "high" | "critical"
    description: str
    metric_a: str  # e.g. "revenue"
    metric_a_value: float
    metric_b: str  # e.g. "operating_cash_flow"
    metric_b_value: float
    expected_relationship: str  # e.g. "both should grow together"
    actual_relationship: str  # e.g. "diverging"


@dataclass
class QuarterlySnapshot:
    """Structured quarterly financial snapshot."""

    quarter: str  # e.g. "2025Q4"
    revenue: float = 0.0
    gross_profit: float = 0.0
    gross_margin: float = 0.0
    operating_income: float = 0.0
    net_income: float = 0.0
    eps: float = 0.0
    inventory: float = 0.0
    accounts_receivable: float = 0.0
    cash: float = 0.0
    short_term_debt: float = 0.0
    operating_cash_flow: float = 0.0
    free_cash_flow: float = 0.0


@dataclass
class InvestmentScenario:
    """A single investment scenario (Bull/Base/Bear)."""

    name: str  # "bull" | "base" | "bear"
    target_price: float
    eps_estimate: float = 0.0
    pe_multiple: float = 0.0
    bvps_estimate: float = 0.0
    pbr_multiple: float = 0.0
    valuation_model: str = "PE"  # "PE" or "PBR"
    conditions: List[str] = field(default_factory=list)
    probability: float = 0.33


@dataclass
class AnalysisResult:
    """Complete analysis output from the six-step framework."""

    stock_id: str
    analysis_date: str
    snapshots: List[QuarterlySnapshot] = field(default_factory=list)
    tension_signals: List[TensionSignal] = field(default_factory=list)
    scenarios: List[InvestmentScenario] = field(default_factory=list)
    friction_score: float = 0.0
    verdict: str = ""  # "buy" | "hold" | "sell" | "watch"
    confidence: float = 0.0
    summary: str = ""


# ---------------------------------------------------------------------------
# Industry Templates
# ---------------------------------------------------------------------------

if typing.TYPE_CHECKING:
    from typing import Protocol
else:
    try:
        from typing import Protocol
    except ImportError:

        class Protocol:
            pass


class IndustryTemplate(Protocol):
    def find_tension_signals(self, snapshots: List[QuarterlySnapshot]) -> List[TensionSignal]: ...
    def analyze_trends(self, snapshots: List[QuarterlySnapshot]) -> Dict[str, str]: ...
    def build_scenarios(
        self, snapshots: List[QuarterlySnapshot], current_price: float, annual_eps: float
    ) -> List[InvestmentScenario]: ...


class TechGrowthTemplate:
    """Original Template: Suited for tech, semi, and high-growth sectors (e.g. 5289 Innodisk)."""

    def find_tension_signals(self, snapshots: List[QuarterlySnapshot]) -> List[TensionSignal]:
        if len(snapshots) < 2:
            return []

        signals: List[TensionSignal] = []
        latest = snapshots[-1]
        previous = snapshots[-2]

        if (
            latest.revenue > previous.revenue
            and latest.operating_cash_flow < previous.operating_cash_flow
        ):
            signals.append(
                TensionSignal(
                    signal_id="revenue_vs_ocf",
                    severity="high",
                    description=f"Revenue grew from {previous.revenue:.1f} to {latest.revenue:.1f} "
                    f"but OCF dropped from {previous.operating_cash_flow:.1f} to {latest.operating_cash_flow:.1f}",
                    metric_a="revenue",
                    metric_a_value=latest.revenue,
                    metric_b="operating_cash_flow",
                    metric_b_value=latest.operating_cash_flow,
                    expected_relationship="both should grow together",
                    actual_relationship="diverging",
                )
            )

        if previous.revenue > 0 and previous.inventory > 0:
            rev_growth = (latest.revenue - previous.revenue) / previous.revenue
            inv_growth = (
                (latest.inventory - previous.inventory) / previous.inventory
                if previous.inventory > 0
                else 0
            )
            if inv_growth > rev_growth * 1.5 and inv_growth > 0.2:
                signals.append(
                    TensionSignal(
                        signal_id="inventory_vs_revenue",
                        severity="high" if inv_growth > rev_growth * 3 else "medium",
                        description=f"Inventory grew {inv_growth:.0%} vs revenue grew {rev_growth:.0%}",
                        metric_a="revenue_growth",
                        metric_a_value=rev_growth,
                        metric_b="inventory_growth",
                        metric_b_value=inv_growth,
                        expected_relationship="inventory should grow proportionally to revenue",
                        actual_relationship="inventory outpacing revenue",
                    )
                )

        if previous.revenue > 0 and previous.accounts_receivable > 0:
            ar_growth = (
                (latest.accounts_receivable - previous.accounts_receivable)
                / previous.accounts_receivable
                if previous.accounts_receivable > 0
                else 0
            )
            if ar_growth > rev_growth * 1.5 and ar_growth > 0.2:
                signals.append(
                    TensionSignal(
                        signal_id="ar_vs_revenue",
                        severity="medium",
                        description=f"Accounts receivable grew {ar_growth:.0%} vs revenue grew {rev_growth:.0%}",
                        metric_a="revenue_growth",
                        metric_a_value=rev_growth,
                        metric_b="ar_growth",
                        metric_b_value=ar_growth,
                        expected_relationship="AR should grow proportionally",
                        actual_relationship="AR outpacing revenue",
                    )
                )

        if latest.cash < previous.cash and latest.short_term_debt > previous.short_term_debt:
            signals.append(
                TensionSignal(
                    signal_id="cash_vs_debt",
                    severity="medium",
                    description=f"Cash dropped from {previous.cash:.1f} to {latest.cash:.1f} "
                    f"while debt increased from {previous.short_term_debt:.1f} to {latest.short_term_debt:.1f}",
                    metric_a="cash",
                    metric_a_value=latest.cash,
                    metric_b="short_term_debt",
                    metric_b_value=latest.short_term_debt,
                    expected_relationship="healthy companies don't burn cash while borrowing",
                    actual_relationship="cash down, debt up",
                )
            )

        if latest.operating_cash_flow < 0:
            signals.append(
                TensionSignal(
                    signal_id="negative_ocf",
                    severity="high" if latest.operating_cash_flow < -10 else "medium",
                    description=f"Operating cash flow is negative: {latest.operating_cash_flow:.1f}",
                    metric_a="operating_cash_flow",
                    metric_a_value=latest.operating_cash_flow,
                    metric_b="net_income",
                    metric_b_value=latest.net_income,
                    expected_relationship="OCF should be positive for profitable companies",
                    actual_relationship="profitable but cash-burning",
                )
            )

        return signals

    def analyze_trends(self, snapshots: List[QuarterlySnapshot]) -> Dict[str, str]:
        if len(snapshots) < 3:
            return {"status": "insufficient data for trend analysis"}

        trends: Dict[str, str] = {}
        revenues = [s.revenue for s in snapshots]
        if all(revenues[i] <= revenues[i + 1] for i in range(len(revenues) - 1)):
            trends["revenue"] = f"accelerating ({revenues[0]:.1f} → {revenues[-1]:.1f})"
        elif revenues[-1] > revenues[0]:
            trends["revenue"] = f"growing with volatility ({revenues[0]:.1f} → {revenues[-1]:.1f})"
        else:
            trends["revenue"] = f"declining ({revenues[0]:.1f} → {revenues[-1]:.1f})"

        margins = [s.gross_margin for s in snapshots]
        if margins[-1] > margins[0] + 0.02:
            trends["gross_margin"] = f"improving ({margins[0]:.1%} → {margins[-1]:.1%})"
        elif margins[-1] < margins[0] - 0.02:
            trends["gross_margin"] = f"declining ({margins[0]:.1%} → {margins[-1]:.1%})"
        else:
            trends["gross_margin"] = f"stable ({margins[0]:.1%} → {margins[-1]:.1%})"

        eps_list = [s.eps for s in snapshots]
        trends["eps"] = f"{eps_list[0]:.2f} → {eps_list[-1]:.2f}"

        return trends

    def build_scenarios(
        self,
        snapshots: List[QuarterlySnapshot],
        current_price: float,
        annual_eps: float,
    ) -> List[InvestmentScenario]:
        latest = snapshots[-1] if snapshots else None
        if not latest:
            return []

        q_eps = latest.eps
        annualized_growth = (q_eps * 4 - annual_eps) / annual_eps if annual_eps > 0 else 0

        bull_eps = annual_eps * (1 + max(annualized_growth, 0.5))
        base_eps = annual_eps * (1 + max(annualized_growth * 0.6, 0.2))
        bear_eps = annual_eps * (1 + min(annualized_growth * 0.3, 0.1))

        bull_pe = min(50, max(30, 1 / max(annualized_growth * 0.01, 0.01)))
        base_pe = min(40, max(25, bull_pe * 0.8))
        bear_pe = min(30, max(15, bull_pe * 0.6))

        return [
            InvestmentScenario(
                name="bull",
                eps_estimate=round(bull_eps, 2),
                pe_multiple=round(bull_pe, 1),
                target_price=round(bull_eps * bull_pe, 0),
                probability=0.25,
                valuation_model="PE",
                conditions=[
                    "Revenue growth accelerates",
                    "Inventory converts to shipments",
                    "OCF turns positive",
                    "AI revenue share reaches 30%",
                ],
            ),
            InvestmentScenario(
                name="base",
                eps_estimate=round(base_eps, 2),
                pe_multiple=round(base_pe, 1),
                target_price=round(base_eps * base_pe, 0),
                probability=0.50,
                valuation_model="PE",
                conditions=[
                    "Revenue growth moderates",
                    "Margins stay stable",
                    "Inventory slowly digested",
                ],
            ),
            InvestmentScenario(
                name="bear",
                eps_estimate=round(bear_eps, 2),
                pe_multiple=round(bear_pe, 1),
                target_price=round(bear_eps * bear_pe, 0),
                probability=0.25,
                valuation_model="PE",
                conditions=[
                    "DRAM price correction",
                    "Inventory write-downs",
                    "Growth decelerates sharply",
                ],
            ),
        ]


@dataclass
class CyclicalTemplate:
    """New Template: Suited for cyclical, petrochemical, and raw material sectors (e.g. 1326 Formosa Chemicals)."""

    book_value_per_share: float = 50.0

    def find_tension_signals(self, snapshots: List[QuarterlySnapshot]) -> List[TensionSignal]:
        if len(snapshots) < 2:
            return []

        signals: List[TensionSignal] = []
        latest = snapshots[-1]
        previous = snapshots[-2]

        # C1: Gross margin crash
        if latest.gross_margin < previous.gross_margin - 0.02 and latest.gross_margin < 0.05:
            signals.append(
                TensionSignal(
                    signal_id="margin_crash",
                    severity="high",
                    description=f"Gross margin crashed from {previous.gross_margin:.1%} to {latest.gross_margin:.1%}",
                    metric_a="gross_margin",
                    metric_a_value=latest.gross_margin,
                    metric_b="previous_margin",
                    metric_b_value=previous.gross_margin,
                    expected_relationship="margin should be stable during mid-cycle",
                    actual_relationship="severe contraction",
                )
            )

        # C2: Sustained operating loss but inventory increasing
        if latest.operating_income < 0 and latest.inventory > previous.inventory * 1.05:
            signals.append(
                TensionSignal(
                    signal_id="inventory_build_during_loss",
                    severity="high",
                    description=f"Building inventory ({previous.inventory:.1f} → {latest.inventory:.1f}) while reporting operating loss ({latest.operating_income:.1f})",
                    metric_a="inventory",
                    metric_a_value=latest.inventory,
                    metric_b="operating_income",
                    metric_b_value=latest.operating_income,
                    expected_relationship="inventory should decrease during cycle trough to preserve cash",
                    actual_relationship="inventory building while losing money",
                )
            )

        # C3: Deep cycle trough (negative OCF)
        if latest.operating_cash_flow < -5.0:
            signals.append(
                TensionSignal(
                    signal_id="deep_trough_cash_burn",
                    severity="critical" if latest.operating_cash_flow < -10 else "medium",
                    description=f"Severe cash burn (OCF: {latest.operating_cash_flow:.1f})",
                    metric_a="operating_cash_flow",
                    metric_a_value=latest.operating_cash_flow,
                    metric_b="cash",
                    metric_b_value=latest.cash,
                    expected_relationship="OCF should stabilize",
                    actual_relationship="accelerating cash burn",
                )
            )

        return signals

    def analyze_trends(self, snapshots: List[QuarterlySnapshot]) -> Dict[str, str]:
        if len(snapshots) < 3:
            return {"status": "insufficient data for trend analysis"}

        trends: Dict[str, str] = {}
        margins = [s.gross_margin for s in snapshots]
        if margins[-1] > margins[-2] and margins[-2] > margins[-3]:
            trends["cycle_phase"] = "expansion (improving margins)"
        elif margins[-1] < margins[-2] and margins[-2] < margins[-3]:
            trends["cycle_phase"] = "contraction (declining margins)"
        else:
            trends["cycle_phase"] = "bouncing along bottom / transition"

        eps_list = [s.eps for s in snapshots]
        trends["eps_trend"] = f"{eps_list[0]:.2f} → {eps_list[-1]:.2f}"
        return trends

    def build_scenarios(
        self,
        snapshots: List[QuarterlySnapshot],
        current_price: float,
        annual_eps: float,
    ) -> List[InvestmentScenario]:
        bvps = self.book_value_per_share

        bull_pbr = 1.3
        base_pbr = 1.0
        bear_pbr = 0.8

        return [
            InvestmentScenario(
                name="bull",
                bvps_estimate=bvps,
                pbr_multiple=bull_pbr,
                target_price=round(bvps * bull_pbr, 0),
                probability=0.25,
                valuation_model="PBR",
                conditions=[
                    "Product spread expands sharply",
                    "Inventory devaluation reverses",
                    "Global demand recovers",
                ],
            ),
            InvestmentScenario(
                name="base",
                bvps_estimate=bvps,
                pbr_multiple=base_pbr,
                target_price=round(bvps * base_pbr, 0),
                probability=0.50,
                valuation_model="PBR",
                conditions=[
                    "Spreads stabilize at breakeven",
                    "Inventory digests slowly",
                    "Capacity utilization crawls to 80%",
                ],
            ),
            InvestmentScenario(
                name="bear",
                bvps_estimate=bvps,
                pbr_multiple=bear_pbr,
                target_price=round(bvps * bear_pbr, 0),
                probability=0.25,
                valuation_model="PBR",
                conditions=[
                    "Oil prices crash",
                    "New capacity dumps into market",
                    "Persistent cash burn",
                ],
            ),
        ]


class SixStepAnalyzer:
    """Automates the six-step financial analysis framework.

    Usage:
        analyzer = SixStepAnalyzer(template=CyclicalTemplate(book_value_per_share=55.0))
        result = analyzer.analyze(profile, current_price=41.5)
    """

    def __init__(self, template: Optional[Any] = None):
        if template is None:
            self.template = TechGrowthTemplate()
        else:
            self.template = template

    def find_tension_signals(self, snapshots: List[QuarterlySnapshot]) -> List[TensionSignal]:
        return self.template.find_tension_signals(snapshots)

    def analyze_trends(self, snapshots: List[QuarterlySnapshot]) -> Dict[str, str]:
        return self.template.analyze_trends(snapshots)

    def build_scenarios(
        self,
        snapshots: List[QuarterlySnapshot],
        current_price: float,
        annual_eps: float,
    ) -> List[InvestmentScenario]:
        return self.template.build_scenarios(snapshots, current_price, annual_eps)

    def compute_friction(self, signals: List[TensionSignal]) -> float:
        """Compute friction score from tension signals.

        Uses exponential diminishing returns: each additional signal
        adds proportionally less friction. This prevents saturation
        when multiple related signals fire simultaneously.

        Returns 0.0 (no friction) to 1.0 (maximum friction).
        """
        if not signals:
            return 0.0

        severity_weights = {
            "low": 0.08,
            "medium": 0.15,
            "high": 0.25,
            "critical": 0.40,
        }

        # Sort by severity (highest first) for diminishing returns
        weights = sorted(
            [severity_weights.get(s.severity, 0.15) for s in signals],
            reverse=True,
        )

        friction = 0.0
        for i, w in enumerate(weights):
            diminishing = 0.7**i
            friction += w * diminishing

        return min(1.0, friction)
