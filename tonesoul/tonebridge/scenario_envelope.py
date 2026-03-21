"""
ScenarioEnvelope — pre-deliberation scenario framing.

Builds three explicit interpretation envelopes before internal deliberation:
- bull: optimistic / opportunity frame
- base: balanced / most-likely frame
- bear: pessimistic / risk frame

The goal is not prediction accuracy. The goal is to make implicit assumptions
explicit and auditable, so Council deliberation can reason over alternative
world models instead of a single hidden narrative.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

_MAX_SUMMARY_CHARS = 220


@dataclass
class ScenarioFrame:
    label: str
    premise: str
    opportunities: List[str]
    risks: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "label": self.label,
            "premise": self.premise,
            "opportunities": list(self.opportunities),
            "risks": list(self.risks),
        }


class ScenarioEnvelopeBuilder:
    """Build deterministic three-scenario envelopes from user input and history."""

    def build(self, user_input: str, history: List[Dict] | None = None) -> Dict[str, object]:
        text = self._normalize_text(user_input)
        history_len = len(history or [])

        bull = ScenarioFrame(
            label="bull",
            premise=f"Assume user intent is constructive and change-ready: {text}",
            opportunities=[
                "Unlock forward momentum with clear next-step framing",
                "Convert ambiguity into explicit design choices",
                "Increase trust by making assumptions transparent",
            ],
            risks=[
                "Over-optimism may underweight hidden constraints",
                "Premature commitment may reduce optionality",
            ],
        )

        base = ScenarioFrame(
            label="base",
            premise=f"Assume mixed constraints and partial information: {text}",
            opportunities=[
                "Balance delivery speed with governance fidelity",
                "Retain reversible decisions where uncertainty is high",
            ],
            risks=[
                "Defaulting to average paths may hide edge-case harm",
                "Ambiguous ownership can blur accountability",
            ],
        )

        bear = ScenarioFrame(
            label="bear",
            premise=f"Assume latent conflict or drift risk in request: {text}",
            opportunities=[
                "Surface red-lines before implementation",
                "Expose hidden contradictions for repair",
            ],
            risks=[
                "Excess caution may stall useful progress",
                "Too much friction can degrade user experience",
            ],
        )

        return {
            "enabled": True,
            "history_turns": history_len,
            "source": "deterministic_heuristic_v1",
            "frames": [bull.to_dict(), base.to_dict(), bear.to_dict()],
            "summary": self._summary_line(text),
        }

    @staticmethod
    def _normalize_text(text: str) -> str:
        compact = re.sub(r"\s+", " ", str(text or "")).strip()
        if not compact:
            return "(empty input)"
        return compact[:_MAX_SUMMARY_CHARS]

    @staticmethod
    def _summary_line(text: str) -> str:
        return f"scenario_envelope_ready | frames=3 seed='{text[:80]}'"
