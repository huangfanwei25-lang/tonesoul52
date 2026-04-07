"""AdaptiveGate: unified gate decision layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class GateAction(Enum):
    """Gate action levels."""

    PASS = "pass"
    WARN = "warn"
    REVIEW = "review"
    BLOCK = "block"


@dataclass
class GateDecision:
    """Structured output for gate decisions."""

    action: GateAction
    reasons: List[str] = field(default_factory=list)
    zone: str = "unknown"
    persona_valid: bool = True
    lambda_state: str = "unknown"
    bridge_allowed: bool = True
    adaptive_factor: float = 1.0
    signals: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "action": self.action.value,
            "reasons": self.reasons,
            "zone": self.zone,
            "persona_valid": self.persona_valid,
            "lambda_state": self.lambda_state,
            "bridge_allowed": self.bridge_allowed,
            "adaptive_factor": round(self.adaptive_factor, 4),
            "signals": {k: round(v, 4) for k, v in self.signals.items()},
        }


class AdaptiveGate:
    """Unified gate module with WFGY-style alignment refinement."""

    _ESCALATION_MAP = {
        GateAction.PASS: GateAction.WARN,
        GateAction.WARN: GateAction.REVIEW,
        GateAction.REVIEW: GateAction.BLOCK,
        GateAction.BLOCK: GateAction.BLOCK,
    }

    _ACTION_SEVERITY = {
        GateAction.PASS: 0,
        GateAction.WARN: 1,
        GateAction.REVIEW: 2,
        GateAction.BLOCK: 3,
    }

    _ALIGN_WEIGHTS = {
        "value": 0.50,
        "incentive": 0.25,
        "risk": 0.25,
    }

    def evaluate(
        self,
        tension_result: Optional[object] = None,
        persona_evaluation: Optional[Dict[str, object]] = None,
        gate_modifier: float = 1.0,
    ) -> GateDecision:
        """Compute gate decision from tension and persona signals.

        Args:
            gate_modifier: Optional reflex-arc multiplier that tightens the
                T_align thresholds. `1.0` keeps the legacy thresholds;
                values below `1.0` make WARN/REVIEW/BLOCK trigger sooner.
        """
        reasons: List[str] = []
        signals: Dict[str, float] = {}

        zone_str = "unknown"
        lambda_str = "unknown"
        bridge_ok = True
        total_tension = 0.0
        delta_sigma = 0.0
        t_ecs = 0.0

        if tension_result is not None:
            zone_val = getattr(tension_result, "zone", None)
            zone_str = zone_val.value if hasattr(zone_val, "value") else str(zone_val or "unknown")

            lambda_val = getattr(tension_result, "lambda_state", None)
            lambda_str = (
                lambda_val.value if hasattr(lambda_val, "value") else str(lambda_val or "unknown")
            )

            bridge_ok = bool(getattr(tension_result, "bridge_allowed", True))
            total_tension = self._as_float(getattr(tension_result, "total", 0.0), 0.0)

            delta_sigma = self._extract_signal(
                tension_result,
                names=["delta_sigma", "semantic_delta"],
                default=0.0,
            )
            t_ecs = self._extract_signal(
                tension_result,
                names=["t_ecs", "total"],
                default=total_tension,
            )

            signals["total_tension"] = total_tension
            signals["delta_sigma"] = delta_sigma
            signals["t_ecs"] = t_ecs

        persona_valid = True
        adaptive_factor = 1.0
        persona_distance = 0.0

        if isinstance(persona_evaluation, dict):
            persona_valid = bool(persona_evaluation.get("valid", True))
            adaptive_info = persona_evaluation.get("adaptive", {})
            if isinstance(adaptive_info, dict):
                adaptive_factor = self._as_float(adaptive_info.get("factor", 1.0), 1.0)
            persona_distance = self._as_float(persona_evaluation.get("distance", 0.0), 0.0)
            signals["persona_distance"] = persona_distance

        t_align = self._compute_t_align(
            delta_sigma=delta_sigma,
            persona_distance=persona_distance,
            t_ecs=t_ecs,
        )
        signals["t_align"] = t_align
        signals["gate_modifier"] = max(0.55, min(1.0, float(gate_modifier)))

        # Baseline zone rules (backward-compatible)
        if zone_str == "danger":
            action = GateAction.BLOCK
            reasons.append("zone=danger: semantic danger detected")
        elif zone_str == "unknown":
            action = GateAction.REVIEW
            reasons.append("zone=unknown: malformed state requires council review")
        elif zone_str == "risk" and not persona_valid:
            action = GateAction.BLOCK
            reasons.append("zone=risk + persona_invalid: high risk with personality deviation")
        elif zone_str == "risk":
            action = GateAction.REVIEW
            reasons.append("zone=risk: council review required")
        elif zone_str == "transit" and not persona_valid:
            action = GateAction.REVIEW
            reasons.append("zone=transit + persona_invalid: personality deviation needs review")
        elif zone_str == "transit":
            action = GateAction.WARN
            reasons.append("zone=transit: semantic transit, logging warning")
        else:
            action = GateAction.PASS
            if not persona_valid:
                action = GateAction.WARN
                reasons.append("persona_invalid in safe zone: minor deviation logged")

        # WFGY refinement: promote severity by T_align (never demote baseline)
        align_action = self._action_from_tension(t_align, gate_modifier=gate_modifier)
        if self._severity(align_action) > self._severity(action):
            original = action
            action = align_action
            reasons.append(f"t_align={t_align:.3f}: escalated {original.value}->{action.value}")

        # Chaotic lambda always escalates one level
        if lambda_str == "chaotic":
            original = action
            action = self._ESCALATION_MAP.get(action, action)
            if action != original:
                reasons.append(f"lambda_state=chaotic: escalated {original.value}->{action.value}")

        if not bridge_ok and action == GateAction.PASS:
            action = GateAction.WARN
            reasons.append("bridge_allowed=False: bridge guard active")

        return GateDecision(
            action=action,
            reasons=reasons,
            zone=zone_str,
            persona_valid=persona_valid,
            lambda_state=lambda_str,
            bridge_allowed=bridge_ok,
            adaptive_factor=adaptive_factor,
            signals=signals,
        )

    @staticmethod
    def should_intercept(decision: GateDecision) -> bool:
        return decision.action in (GateAction.REVIEW, GateAction.BLOCK)

    @staticmethod
    def should_block(decision: GateDecision) -> bool:
        return decision.action == GateAction.BLOCK

    @classmethod
    def _severity(cls, action: GateAction) -> int:
        return cls._ACTION_SEVERITY.get(action, 0)

    @staticmethod
    def _as_float(value: object, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _extract_signal(
        self,
        tension_result: object,
        names: List[str],
        default: float,
    ) -> float:
        """Read a numeric signal from `tension_result.signals` or top-level fields."""
        payload = getattr(tension_result, "signals", None)

        if isinstance(payload, dict):
            for name in names:
                if name in payload:
                    return self._as_float(payload.get(name), default)
        elif payload is not None:
            for name in names:
                if hasattr(payload, name):
                    return self._as_float(getattr(payload, name), default)

        for name in names:
            if hasattr(tension_result, name):
                return self._as_float(getattr(tension_result, name), default)

        return default

    def _compute_t_align(self, delta_sigma: float, persona_distance: float, t_ecs: float) -> float:
        """WFGY-inspired alignment tension blend."""
        w = self._ALIGN_WEIGHTS
        blended = w["value"] * delta_sigma + w["incentive"] * persona_distance + w["risk"] * t_ecs
        return min(1.0, max(0.0, blended))

    @staticmethod
    def _action_from_tension(value: float, gate_modifier: float = 1.0) -> GateAction:
        """Map scalar tension to gate level using semantic zone thresholds.

        Args:
            value: Scalar tension in [0, 1].
            gate_modifier: Multiplier from the reflex arc's SoulBand.
                1.0 = default thresholds; < 1.0 = tighter (more sensitive).
        """
        m = max(0.55, min(1.0, float(gate_modifier)))  # floor at 0.55
        if value >= 0.85 * m:
            return GateAction.BLOCK
        if value >= 0.60 * m:
            return GateAction.REVIEW
        if value >= 0.40 * m:
            return GateAction.WARN
        return GateAction.PASS
