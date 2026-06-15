from __future__ import annotations

from tonesoul.market.analyzer import QuarterlySnapshot
from tonesoul.market.world_model import (
    PERSONA_RAY,
    PERSONA_SHORT,
    PERSONA_WARREN,
    STANCE_BEARISH,
    STANCE_BULLISH,
    STANCE_MIXED,
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


# ── classify_persona_stance additional branches ───────────────────────────────


def test_classify_persona_stance_detects_bearish_language() -> None:
    persona = InvestmentPersona(id="bear", name="Bear", system_prompt="")
    stance = classify_persona_stance(
        persona,
        "The stock is overvalued with deteriorating margins and obvious downside risk.",
    )
    assert stance.stance == STANCE_BEARISH
    assert "overvalued" in stance.bearish_terms
    assert stance.conviction > 0.0


def test_classify_persona_stance_detects_watchful_language() -> None:
    persona = InvestmentPersona(id="macro", name="Macro", system_prompt="")
    stance = classify_persona_stance(
        persona,
        "Stay cautious. Monitor the inventory cycle and wait for clearer confirmation.",
    )
    assert stance.stance == STANCE_WATCHFUL
    assert stance.conviction > 0.0


def test_classify_persona_stance_empty_narrative_returns_mixed() -> None:
    persona = InvestmentPersona(id="x", name="X", system_prompt="")
    stance = classify_persona_stance(persona, "")
    assert stance.stance == STANCE_MIXED


def test_classify_persona_stance_error_narrative_returns_mixed() -> None:
    persona = InvestmentPersona(id="x", name="X", system_prompt="")
    stance = classify_persona_stance(persona, "error: LLM unreachable")
    assert stance.stance == STANCE_MIXED


# ── build_strategy_plurality_report edge cases ────────────────────────────────


def test_build_strategy_plurality_report_empty_input() -> None:
    report = build_strategy_plurality_report({})
    assert report.perspectives == []
    assert report.dominant_conflict == "insufficient_signal"


def test_build_strategy_plurality_report_panic_language_flag() -> None:
    report = build_strategy_plurality_report(
        {
            "bear": "There is panic and forced selling with capitulation across the board.",
            "macro": "Deteriorating environment.",
        },
        personas=[PERSONA_SHORT, PERSONA_RAY],
    )
    assert "panic_language" in report.irrationality_flags
    assert report.recommended_posture == "slow_down"


def test_build_strategy_plurality_report_conviction_vs_patience() -> None:
    report = build_strategy_plurality_report(
        {
            "value": "Undervalued with improving fundamentals and clear upside.",
            "macro": "Monitor closely; cautious and uncertain about macro.",
        },
        personas=[PERSONA_WARREN, PERSONA_RAY],
    )
    assert report.dominant_conflict == "conviction_vs_patience"
    assert report.recommended_posture == "monitor_for_resolution"


# ── format_snapshots_for_llm ─────────────────────────────────────────────────


def test_format_snapshots_for_llm_empty_list() -> None:
    simulator = _DeterministicSimulator()
    result = simulator.format_snapshots_for_llm([])
    assert result == "No data available."


def test_format_snapshots_for_llm_includes_quarter_data() -> None:
    simulator = _DeterministicSimulator()
    snaps = [QuarterlySnapshot(quarter="2025Q3", revenue=5.0, gross_margin=0.25, eps=0.8)]
    result = simulator.format_snapshots_for_llm(snaps)
    assert "2025Q3" in result
    assert "5.0" in result
