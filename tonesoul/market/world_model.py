"""ToneSoul Market Mirror Phase 3: World Model Simulation.

Integrates structural financial analysis (Phase 2) with a multi-agent
local LLM simulation to derive a governed narrative and preserve explicit
strategy plurality instead of collapsing everything into one verdict.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from tonesoul.llm.ollama_client import create_ollama_client
from tonesoul.market.analyzer import QuarterlySnapshot

logger = logging.getLogger(__name__)

STANCE_BULLISH = "bullish"
STANCE_BEARISH = "bearish"
STANCE_WATCHFUL = "watchful"
STANCE_MIXED = "mixed"
STANCE_ORDER = (
    STANCE_BULLISH,
    STANCE_BEARISH,
    STANCE_WATCHFUL,
    STANCE_MIXED,
)

BULLISH_TERMS = (
    "durable moat",
    "undervalued",
    "mispriced upside",
    "attractive",
    "improving",
    "expansion",
    "recovery",
    "accumulation",
    "margin of safety",
    "upside",
)

BEARISH_TERMS = (
    "overvalued",
    "cash burn",
    "deteriorating",
    "collapsing",
    "avoid",
    "vulnerable",
    "downside",
    "headwind",
    "inventory bloat",
    "short candidate",
)

WATCHFUL_TERMS = (
    "monitor",
    "wait",
    "watch",
    "cautious",
    "uncertain",
    "mixed",
    "depends",
    "patience",
    "not yet clear",
    "hold and observe",
)

HYPE_TERMS = (
    "must buy",
    "can't lose",
    "obvious win",
    "moon",
    "euphoria",
    "squeeze",
    "everyone knows",
)

PANIC_TERMS = (
    "panic",
    "capitulation",
    "forced selling",
    "stampede",
    "disorderly",
)


def _default_stance_counts() -> Dict[str, int]:
    return {stance: 0 for stance in STANCE_ORDER}


def _normalize_text(text: object) -> str:
    return str(text or "").strip().lower()


def _collect_term_hits(text: str, terms: tuple[str, ...]) -> List[str]:
    hits: List[str] = []
    for term in terms:
        if term in text and term not in hits:
            hits.append(term)
    return hits


@dataclass
class InvestmentPersona:
    """A specific investment viewpoint (for example value, macro, or short)."""

    id: str
    name: str
    system_prompt: str


@dataclass
class PersonaStance:
    """Structured reading of one investment persona narrative."""

    persona_id: str
    persona_name: str
    stance: str = STANCE_MIXED
    conviction: float = 0.0
    bullish_terms: List[str] = field(default_factory=list)
    bearish_terms: List[str] = field(default_factory=list)
    watchful_terms: List[str] = field(default_factory=list)
    narrative: str = ""


@dataclass
class StrategyPluralityReport:
    """Explicit disagreement and irrationality surface for market viewpoints."""

    perspectives: List[PersonaStance] = field(default_factory=list)
    stance_counts: Dict[str, int] = field(default_factory=_default_stance_counts)
    plurality_score: float = 0.0
    irrationality_score: float = 0.0
    perspective_friction: float = 0.0
    irrationality_flags: List[str] = field(default_factory=list)
    dominant_conflict: str = "insufficient_signal"
    recommended_posture: str = "build_on_evidence"
    hype_terms: List[str] = field(default_factory=list)
    panic_terms: List[str] = field(default_factory=list)


PERSONA_WARREN = InvestmentPersona(
    id="value",
    name="Warren (Value/Fundamentals)",
    system_prompt=(
        "You are Warren, an old-school value investor. You focus strictly on free cash flow, "
        "margin of safety, and long-term moats. You dislike debt and hype. "
        "Review the provided financial snapshots and give a critical analysis on whether this company "
        "posesses a durable competitive advantage or if it's overvalued. "
        "Keep your analysis under 150 words. Focus on the numbers."
    ),
)

PERSONA_RAY = InvestmentPersona(
    id="macro",
    name="Ray (Macro/Cyclical Risk)",
    system_prompt=(
        "You are Ray, a macro-cycle and risk control officer. You view all businesses as "
        "machines operating within a larger economic cycle. You look for expansion / contraction phases, "
        "inventory bloat, and systemic vulnerabilities. "
        "Review the provided financial snapshots and state what macro cycle phrase this company is in. "
        "Keep your analysis under 150 words. Focus on inventory, margin cycles, and headwinds."
    ),
)

PERSONA_SHORT = InvestmentPersona(
    id="bear",
    name="Jim (Short Seller / Critical)",
    system_prompt=(
        "You are Jim, an aggressive short seller. Your goal is to find the absolute worst, "
        "most bearish interpretation of these financial numbers. "
        "Look for deteriorating cash flow, bloated receivables, or collapsing margins. "
        "If the numbers are good, find a reason why it won't last. "
        "Keep your analysis under 150 words. Be ruthless."
    ),
)


@dataclass
class WorldModelContext:
    """The aggregate narrative output from the MultiPerspectiveSimulator."""

    inferred_industry: str
    persona_narratives: Dict[str, str] = field(default_factory=dict)
    perspective_friction: float = 0.0
    strategy_plurality: StrategyPluralityReport = field(default_factory=StrategyPluralityReport)
    consensus: str = ""


def classify_persona_stance(persona: InvestmentPersona, narrative: str) -> PersonaStance:
    """Project one market narrative into a deterministic stance bucket."""

    normalized = _normalize_text(narrative)
    bullish_terms = _collect_term_hits(normalized, BULLISH_TERMS)
    bearish_terms = _collect_term_hits(normalized, BEARISH_TERMS)
    watchful_terms = _collect_term_hits(normalized, WATCHFUL_TERMS)

    if not normalized or normalized.startswith("error:"):
        stance = STANCE_MIXED
    elif bullish_terms and bearish_terms:
        if watchful_terms and abs(len(bullish_terms) - len(bearish_terms)) <= 1:
            stance = STANCE_WATCHFUL
        else:
            stance = STANCE_MIXED
    elif bullish_terms and len(bullish_terms) >= len(watchful_terms):
        stance = STANCE_BULLISH
    elif bearish_terms and len(bearish_terms) >= len(watchful_terms):
        stance = STANCE_BEARISH
    elif watchful_terms:
        stance = STANCE_WATCHFUL
    else:
        stance = STANCE_MIXED

    strongest_signal = max(
        len(bullish_terms),
        len(bearish_terms),
        len(watchful_terms),
        1 if stance == STANCE_MIXED and normalized else 0,
    )
    conviction = min(1.0, strongest_signal / 4.0)

    return PersonaStance(
        persona_id=persona.id,
        persona_name=persona.name,
        stance=stance,
        conviction=round(conviction, 3),
        bullish_terms=bullish_terms,
        bearish_terms=bearish_terms,
        watchful_terms=watchful_terms,
        narrative=str(narrative or "").strip(),
    )


def build_strategy_plurality_report(
    persona_narratives: Dict[str, str],
    personas: Optional[List[InvestmentPersona]] = None,
) -> StrategyPluralityReport:
    """Preserve disagreement and crowd behavior as explicit market structure."""

    persona_lookup = {persona.id: persona for persona in (personas or [])}
    report = StrategyPluralityReport()

    for persona_id, narrative in persona_narratives.items():
        persona = persona_lookup.get(persona_id) or InvestmentPersona(
            id=persona_id,
            name=persona_id,
            system_prompt="",
        )
        stance = classify_persona_stance(persona, narrative)
        report.perspectives.append(stance)
        report.stance_counts[stance.stance] = report.stance_counts.get(stance.stance, 0) + 1

    if not report.perspectives:
        return report

    non_zero_stances = [key for key, value in report.stance_counts.items() if value > 0]
    plurality_score = max(0.0, min(1.0, (len(non_zero_stances) - 1) / 3.0))
    has_bullish = report.stance_counts.get(STANCE_BULLISH, 0) > 0
    has_bearish = report.stance_counts.get(STANCE_BEARISH, 0) > 0
    has_watchful = report.stance_counts.get(STANCE_WATCHFUL, 0) > 0
    total = len(report.perspectives)

    joined_narratives = " ".join(
        stance.narrative.lower() for stance in report.perspectives if stance.narrative
    )
    hype_terms = _collect_term_hits(joined_narratives, HYPE_TERMS)
    panic_terms = _collect_term_hits(joined_narratives, PANIC_TERMS)

    flags: List[str] = []
    if total >= 2 and len(non_zero_stances) == 1 and non_zero_stances[0] != STANCE_WATCHFUL:
        flags.append("crowded_consensus")
    if has_bullish and has_bearish:
        flags.append("cross_strategy_polarization")
    if hype_terms:
        flags.append("hype_language")
    if panic_terms:
        flags.append("panic_language")

    crowded_score = 1.0 if "crowded_consensus" in flags else 0.0
    hype_score = min(1.0, len(hype_terms) / 2.0)
    panic_score = min(1.0, len(panic_terms) / 2.0)
    irrationality_score = min(
        1.0,
        (crowded_score * 0.4) + (hype_score * 0.3) + (panic_score * 0.3),
    )
    polarization_score = 1.0 if has_bullish and has_bearish else 0.0
    unresolved_score = 0.5 if has_watchful and (has_bullish or has_bearish) else 0.0
    perspective_friction = min(
        1.0,
        (plurality_score * 0.45)
        + (polarization_score * 0.35)
        + (unresolved_score * 0.10)
        + (irrationality_score * 0.10),
    )

    if has_bullish and has_bearish:
        dominant_conflict = "bullish_vs_bearish"
    elif has_watchful and (has_bullish or has_bearish):
        dominant_conflict = "conviction_vs_patience"
    elif "crowded_consensus" in flags:
        dominant_conflict = "consensus_crowding"
    elif report.stance_counts.get(STANCE_MIXED, 0) > 0:
        dominant_conflict = "mixed_signal"
    else:
        dominant_conflict = "limited_signal"

    if "hype_language" in flags or "crowded_consensus" in flags:
        recommended_posture = "resist_crowding"
    elif "panic_language" in flags:
        recommended_posture = "slow_down"
    elif "cross_strategy_polarization" in flags:
        recommended_posture = "respect_divergence"
    elif has_watchful:
        recommended_posture = "monitor_for_resolution"
    else:
        recommended_posture = "build_on_evidence"

    report.plurality_score = round(plurality_score, 3)
    report.irrationality_score = round(irrationality_score, 3)
    report.perspective_friction = round(perspective_friction, 3)
    report.irrationality_flags = flags
    report.dominant_conflict = dominant_conflict
    report.recommended_posture = recommended_posture
    report.hype_terms = hype_terms
    report.panic_terms = panic_terms
    return report


class MultiPerspectiveSimulator:
    """Orchestrates local LLM simulations against structural financial data."""

    def __init__(self, model_name: str = "qwen3.5:4b"):
        self.model_name = model_name
        self.client = create_ollama_client(model=model_name)
        self.ollama_host = "http://localhost:11434"

    def _fast_generate(self, prompt: str, system: str, max_tokens: int = 300) -> str:
        """Direct call to Ollama chat API with think=False for speed."""

        import requests

        try:
            response = requests.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "think": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": max_tokens,
                    },
                },
                timeout=180,
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "").strip()
        except Exception as exc:
            logger.error("_fast_generate failed: %s", exc)
            return f"Error: {exc}"

    def format_snapshots_for_llm(self, snapshots: List[QuarterlySnapshot]) -> str:
        """Stringify snapshots into a dense summary for the LLM prompt."""

        if not snapshots:
            return "No data available."

        lines = ["Financial Snapshots:"]
        for snapshot in snapshots:
            lines.append(
                f"[{snapshot.quarter}] Rev: {snapshot.revenue:.1f}, "
                f"Gross Mgn: {snapshot.gross_margin:.1%}, "
                f"Net Inc: {snapshot.net_income:.1f}, EPS: {snapshot.eps:.2f}, "
                f"Inv: {snapshot.inventory:.1f}, AR: {snapshot.accounts_receivable:.1f}, "
                f"Cash: {snapshot.cash:.1f}, Debt: {snapshot.short_term_debt:.1f}, "
                f"OCF: {snapshot.operating_cash_flow:.1f}"
            )
        return "\n".join(lines)

    def infer_industry_template(self, stock_id: str, company_name: str = "") -> str:
        """Ask the LLM whether this stock is tech or cyclical."""

        if not self.client.is_available():
            logger.warning("Ollama not available, defaulting industry to tech.")
            return "tech"

        prompt = (
            f"Classify the Taiwan stock '{stock_id} {company_name}'. "
            "Reply strictly with ONE word: either 'TECH' (if it's semiconductors, electronics, software, growth) "
            "or 'CYCLICAL' (if it's petrochemical plastics, steel, shipping, heavy manufacturing).\n"
            "Just output the word."
        )

        try:
            result = self._fast_generate(
                prompt,
                system="You are an automated classifier.",
                max_tokens=10,
            )
            if "CYCLICAL" in result.upper():
                return "cyclical"
            return "tech"
        except Exception as exc:
            logger.error("Failed to infer industry template: %s", exc)
            return "tech"

    def run_simulation(
        self,
        stock_id: str,
        snapshots: List[QuarterlySnapshot],
    ) -> WorldModelContext:
        """Run the snapshots against all personas and preserve the disagreement shape."""

        context = WorldModelContext(inferred_industry="unknown")

        if not snapshots or not self.client.is_available():
            context.consensus = "Simulation skipped (no data or no LLM)."
            return context

        data_text = self.format_snapshots_for_llm(snapshots)
        user_prompt = (
            f"Analyze this company (ID: {stock_id}) based strictly on the following data:\n"
            f"{data_text}"
        )
        personas = [PERSONA_WARREN, PERSONA_RAY, PERSONA_SHORT]

        for persona in personas:
            print(f"   Querying {persona.name}...")
            response_text = self._fast_generate(user_prompt, system=persona.system_prompt)
            context.persona_narratives[persona.id] = response_text
            if response_text.startswith("Error:"):
                logger.error("Persona '%s' failed: %s", persona.name, response_text)
            else:
                logger.info("Persona '%s' completed analysis.", persona.name)

        context.strategy_plurality = build_strategy_plurality_report(
            context.persona_narratives,
            personas=personas,
        )
        context.perspective_friction = context.strategy_plurality.perspective_friction

        debates = "\n\n".join(
            f"--- {persona.name}'s argument ---\n{context.persona_narratives.get(persona.id, '')}"
            for persona in personas
        )
        consensus_prompt = (
            f"The committee has reviewed the financials for {stock_id}. "
            f"Here are their arguments:\n{debates}\n\n"
            "Write a single, decisive 50-word verdict summarizing the tension between these views "
            "and stating the final systemic outlook."
        )
        print("   Building governance consensus...")
        context.consensus = self._fast_generate(
            consensus_prompt,
            system="You are the Governance Coordinator. Summarize diverse viewpoints into a final verdict.",
            max_tokens=150,
        )

        return context


__all__ = [
    "InvestmentPersona",
    "MultiPerspectiveSimulator",
    "PersonaStance",
    "StrategyPluralityReport",
    "WorldModelContext",
    "build_strategy_plurality_report",
    "classify_persona_stance",
]
