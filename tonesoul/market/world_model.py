"""ToneSoul Market Mirror Phase 3: World Model Simulation.

Integrates structural financial analysis (Phase 2) with a multi-agent
local LLM simulation to derive a governed narrative and classify templates.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from tonesoul.market.analyzer import (
    AnalysisResult,
    CyclicalTemplate,
    QuarterlySnapshot,
    SixStepAnalyzer,
    TechGrowthTemplate,
)
from tonesoul.llm.ollama_client import create_ollama_client

logger = logging.getLogger(__name__)


@dataclass
class InvestmentPersona:
    """A specific investment viewpoint (e.g., Value, Momentum, Bear)."""
    id: str
    name: str
    system_prompt: str


# Pre-defined Personas
PERSONA_WARREN = InvestmentPersona(
    id="value",
    name="Warren (Value/Fundamentals)",
    system_prompt=(
        "You are Warren, an old-school value investor. You focus strictly on free cash flow, "
        "margin of safety, and long-term moats. You dislike debt and hype. "
        "Review the provided financial snapshots and give a critical analysis on whether this company "
        "posesses a durable competitive advantage or if it's overvalued. "
        "Keep your analysis under 150 words. Focus on the numbers."
    )
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
    )
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
    )
)


@dataclass
class WorldModelContext:
    """The aggregate narrative output from the MultiPerspectiveSimulator."""
    inferred_industry: str
    persona_narratives: Dict[str, str] = field(default_factory=dict)
    perspective_friction: float = 0.0
    consensus: str = ""


class MultiPerspectiveSimulator:
    """Orchestrates local LLM simulations against structural financial data."""

    def __init__(self, model_name: str = "qwen3.5:4b"):
        self.model_name = model_name
        self.client = create_ollama_client(model=model_name)
        self.ollama_host = "http://localhost:11434"

    def _fast_generate(self, prompt: str, system: str, max_tokens: int = 300) -> str:
        """Direct call to Ollama chat API with think=False for speed.

        The generate API lets Qwen spend all its budget on thinking.
        The chat API with think=False forces it to output directly.
        """
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
        except Exception as e:
            logger.error("_fast_generate failed: %s", e)
            return f"Error: {e}"

    def format_snapshots_for_llm(self, snapshots: List[QuarterlySnapshot]) -> str:
        """Stringifies snapshots into a dense summary for the LLM prompt."""
        if not snapshots:
            return "No data available."

        lines = ["Financial Snapshots:"]
        for s in snapshots:
            lines.append(
                f"[{s.quarter}] Rev: {s.revenue:.1f}, Gross Mgn: {s.gross_margin:.1%}, "
                f"Net Inc: {s.net_income:.1f}, EPS: {s.eps:.2f}, "
                f"Inv: {s.inventory:.1f}, AR: {s.accounts_receivable:.1f}, "
                f"Cash: {s.cash:.1f}, Debt: {s.short_term_debt:.1f}, OCF: {s.operating_cash_flow:.1f}"
            )
        return "\n".join(lines)

    def infer_industry_template(self, stock_id: str, company_name: str = "") -> str:
        """Asks the LLM whether this stock is Tech/Growth or Cyclical/Petro/Heavy."""
        if not self.client.is_available():
            logger.warning("Ollama not available, defaulting industry to Tech.")
            return "tech"

        prompt = (
            f"Classify the Taiwan stock '{stock_id} {company_name}'. "
            "Reply strictly with ONE word: either 'TECH' (if it's semiconductors, electronics, software, growth) "
            "or 'CYCLICAL' (if it's petrochemical plastics, steel, shipping, heavy manufacturing).\n"
            "Just output the word."
        )

        try:
            result = self._fast_generate(prompt, system="You are an automated classifier.", max_tokens=10)
            if "CYCLICAL" in result.upper():
                return "cyclical"
            return "tech"
        except Exception as e:
            logger.error("Failed to infer industry template: %s", e)
            return "tech"

    def run_simulation(
        self, stock_id: str, snapshots: List[QuarterlySnapshot]
    ) -> WorldModelContext:
        """Runs the snapshots against all personas and gauges the semantic divergence."""
        context = WorldModelContext(inferred_industry="unknown")

        if not snapshots or not self.client.is_available():
            context.consensus = "Simulation skipped (no data or no LLM)."
            return context

        data_text = self.format_snapshots_for_llm(snapshots)
        user_prompt = f"Analyze this company (ID: {stock_id}) based strictly on the following data:\n{data_text}"

        personas = [PERSONA_WARREN, PERSONA_RAY, PERSONA_SHORT]

        for persona in personas:
            print(f"   ⏳ Querying {persona.name}...")
            resp = self._fast_generate(user_prompt, system=persona.system_prompt)
            context.persona_narratives[persona.id] = resp
            if resp.startswith("Error:"):
                logger.error("Persona '%s' failed: %s", persona.name, resp)
            else:
                logger.info("Persona '%s' completed analysis.", persona.name)

        # Placeholder friction (semantic divergence would require embeddings)
        context.perspective_friction = 0.5

        # Coordinator summarizes the debate
        debates = "\n\n".join(
            f"--- {p.name}'s argument ---\n{context.persona_narratives.get(p.id, '')}"
            for _, p in enumerate(personas)
        )
        consensus_prompt = (
            f"The committee has reviewed the financials for {stock_id}. "
            f"Here are their arguments:\n{debates}\n\n"
            "Write a single, decisive 50-word verdict summarizing the tension between these views "
            "and stating the final systemic outlook."
        )
        print("   ⏳ Building governance consensus...")
        context.consensus = self._fast_generate(
            consensus_prompt,
            system="You are the Governance Coordinator. Summarize diverse viewpoints into a final verdict.",
            max_tokens=150,
        )

        return context

