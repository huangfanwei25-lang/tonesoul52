from __future__ import annotations

from dataclasses import dataclass

from .types import NegotiationOutcome, SovereigntyBoundary, TensionPacket


def _resolve_field(packet: TensionPacket, field_path: str):
    if field_path.startswith("signals."):
        key = field_path.split(".", 1)[1]
        return packet.signals.get(key)
    return getattr(packet, field_path, None)


@dataclass(frozen=True)
class NegotiationResult:
    outcome: NegotiationOutcome
    divergence_score: float
    explanation: str

    def to_dict(self) -> dict[str, object]:
        return {
            "outcome": self.outcome.value,
            "divergence_score": round(self.divergence_score, 4),
            "explanation": self.explanation,
        }


class TensionNegotiator:
    """Negotiates tension while preserving visible divergence and hard sovereignty."""

    ALIGNMENT_THRESHOLD = 0.3

    def __init__(self, boundary: SovereigntyBoundary) -> None:
        self.boundary = boundary

    def negotiate(self, local: TensionPacket, remote: TensionPacket) -> NegotiationResult:
        differing_protected_fields = [
            field
            for field in sorted(self.boundary.non_negotiable_fields)
            if _resolve_field(local, field) != _resolve_field(remote, field)
        ]
        if differing_protected_fields:
            field_list = ", ".join(differing_protected_fields)
            return NegotiationResult(
                outcome=NegotiationOutcome.SOVEREIGN_OVERRIDE,
                divergence_score=1.0,
                explanation=(
                    "Sovereignty boundary rejected remote override on "
                    f"{field_list}. Each soul remains a sovereign entity."
                ),
            )

        divergence_score = self._compute_divergence_score(local, remote)
        if divergence_score < self.ALIGNMENT_THRESHOLD:
            return NegotiationResult(
                outcome=NegotiationOutcome.ALIGNED,
                divergence_score=divergence_score,
                explanation=(
                    f"Packets are aligned within threshold {self.ALIGNMENT_THRESHOLD:.2f}; "
                    "no visible divergence requires escalation."
                ),
            )

        return NegotiationResult(
            outcome=NegotiationOutcome.DIVERGENT,
            divergence_score=divergence_score,
            explanation=(
                "Visible divergence is preserved instead of erased. "
                f"score={divergence_score:.4f}"
            ),
        )

    @classmethod
    def _compute_divergence_score(cls, local: TensionPacket, remote: TensionPacket) -> float:
        total_gap = abs(local.total - remote.total)
        zone_gap = 0.0 if local.zone == remote.zone else 0.25
        lambda_gap = 0.0 if local.lambda_state == remote.lambda_state else 0.25
        signal_gap = cls._compute_signal_gap(local, remote)

        score = 0.45 * total_gap + 0.35 * signal_gap + 0.10 * zone_gap + 0.10 * lambda_gap
        return max(0.0, min(1.0, score))

    @staticmethod
    def _compute_signal_gap(local: TensionPacket, remote: TensionPacket) -> float:
        keys = sorted(set(local.signals) | set(remote.signals))
        if not keys:
            return 0.0
        gap = sum(abs(local.signals.get(key, 0.0) - remote.signals.get(key, 0.0)) for key in keys)
        return gap / len(keys)
