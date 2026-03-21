from __future__ import annotations

from tonesoul.market.analyzer import QuarterlySnapshot
from tonesoul.market.world_model import (
    PERSONA_RAY,
    PERSONA_SHORT,
    PERSONA_WARREN,
    STANCE_BEARISH,
    STANCE_BULLISH,
    STANCE_WATCHFUL,
    InvestmentPersona,
    MultiPerspectiveSimulator,
    build_strategy_plurality_report,
    classify_persona_stance,
)


class _AvailableClient:
    def is_available(self) -> bool:
        return True


class _DeterministicSimulator(MultiPerspectiveSimulator):
    def __init__(self) -> None:
        self.model_name = "stub"
        self.client = _AvailableClient()
        self.ollama_host = "http://localhost:11434"
        self.calls: list[tuple[str, str, int]] = []

    def _fast_generate(self, prompt: str, system: str, max_tokens: int = 300) -> str:
        self.calls.append((prompt, system, max_tokens))
        if "Warren" in system:
            return "Undervalued with durable moat and improving cash flow."
        if "Ray" in system:
            return (
                "Cautious and watchful. Monitor and wait because the macro path is not yet clear."
            )
        if "Jim" in system:
            return "Overvalued with deteriorating cash conversion and clear downside risk."
        return "Consensus: respect the divergence and wait for cleaner proof."


def test_classify_persona_stance_detects_bullish_language() -> None:
    persona = InvestmentPersona(id="value", name="Value", system_prompt="")

    stance = classify_persona_stance(
        persona,
        "The stock looks undervalued with a durable moat and improving fundamentals.",
    )

    assert stance.stance == STANCE_BULLISH
    assert "undervalued" in stance.bullish_terms
    assert stance.conviction > 0.0


def test_build_strategy_plurality_report_marks_polarized_split() -> None:
    report = build_strategy_plurality_report(
        {
            "value": "Undervalued with durable moat and recovery upside.",
            "macro": "Cautious and watchful. Monitor the headwind and wait for confirmation.",
            "bear": "Overvalued, deteriorating, and vulnerable to downside.",
        },
        personas=[PERSONA_WARREN, PERSONA_RAY, PERSONA_SHORT],
    )

    assert report.stance_counts[STANCE_BULLISH] == 1
    assert report.stance_counts[STANCE_BEARISH] == 1
    assert report.stance_counts[STANCE_WATCHFUL] == 1
    assert report.dominant_conflict == "bullish_vs_bearish"
    assert "cross_strategy_polarization" in report.irrationality_flags
    assert report.recommended_posture == "respect_divergence"
    assert report.perspective_friction >= 0.7


def test_build_strategy_plurality_report_marks_crowding_and_hype() -> None:
    report = build_strategy_plurality_report(
        {
            "value": "This is a must buy with obvious win upside and durable moat.",
            "macro": "Everyone knows this recovery is real and the stock cannot lose.",
            "bear": "Even the short case fails; obvious win, squeeze, and upside remain.",
        },
        personas=[PERSONA_WARREN, PERSONA_RAY, PERSONA_SHORT],
    )

    assert report.stance_counts[STANCE_BULLISH] == 3
    assert "crowded_consensus" in report.irrationality_flags
    assert "hype_language" in report.irrationality_flags
    assert report.recommended_posture == "resist_crowding"
    assert report.irrationality_score > 0.0


def test_run_simulation_surfaces_strategy_plurality() -> None:
    simulator = _DeterministicSimulator()
    snapshots = [QuarterlySnapshot(quarter="2025Q4", revenue=10.0, gross_margin=0.3, eps=1.2)]

    context = simulator.run_simulation("2330", snapshots)

    assert context.persona_narratives["value"].startswith("Undervalued")
    assert context.strategy_plurality.dominant_conflict == "bullish_vs_bearish"
    assert context.strategy_plurality.stance_counts[STANCE_WATCHFUL] == 1
    assert context.perspective_friction == context.strategy_plurality.perspective_friction
    assert context.consensus.startswith("Consensus:")
