"""
ToneSoul Governance Reflex Arc — making governance constitutive, not just informational.

This module closes the loop between governance state and system behavior.
Soul integral, vows, drift, and tension now directly influence output.

Architecture:
  GovernancePosture → SoulBand classifier → ReflexEvaluator → ReflexDecision
  ReflexDecision → hook points in AdaptiveGate, _self_check, pre-output, dashboard

Design anchors:
  - E0 "Choice Before Identity": choices must have consequences
  - Axiom 4 "Non-Zero Tension": system never immune to governance signals
  - Axiom 5 "Mirror Recursion": reflection produces higher accuracy

Author: Claude Code (Governance Reflex Layer Phase 1)
Date: 2026-04-07
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Soul Band System
# ---------------------------------------------------------------------------


class SoulBandLevel(Enum):
    """Four bands of soul_integral, each changing system behavior."""

    SERENE = "serene"  # 0.00–0.30: normal operation
    ALERT = "alert"  # 0.30–0.55: gates tighten 10%
    STRAINED = "strained"  # 0.55–0.80: gates tighten 25%, forced council
    CRITICAL = "critical"  # 0.80–1.00: hard enforcement


@dataclass(frozen=True)
class SoulBand:
    """Classified soul band with its behavioral modifiers."""

    level: SoulBandLevel
    soul_integral: float
    gate_modifier: float
    force_council: bool
    max_autonomy: Optional[float]  # None = no cap

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "soul_integral": round(self.soul_integral, 4),
            "gate_modifier": round(self.gate_modifier, 4),
            "force_council": self.force_council,
            "max_autonomy": round(self.max_autonomy, 4) if self.max_autonomy is not None else None,
        }


# Band thresholds — configurable via ReflexConfig
_DEFAULT_BAND_THRESHOLDS = {
    "alert": 0.30,
    "strained": 0.55,
    "critical": 0.80,
}

_DEFAULT_BAND_MODIFIERS = {
    SoulBandLevel.SERENE: {"gate_modifier": 1.0, "force_council": False, "max_autonomy": None},
    SoulBandLevel.ALERT: {"gate_modifier": 0.90, "force_council": False, "max_autonomy": None},
    SoulBandLevel.STRAINED: {"gate_modifier": 0.75, "force_council": True, "max_autonomy": 0.25},
    SoulBandLevel.CRITICAL: {"gate_modifier": 0.55, "force_council": True, "max_autonomy": 0.10},
}


def classify_soul_band(
    soul_integral: float,
    *,
    thresholds: Optional[Dict[str, float]] = None,
) -> SoulBand:
    """Classify soul_integral into a SoulBand with behavioral modifiers.

    Args:
        soul_integral: Current soul integral value (0.0–1.0).
        thresholds: Optional custom band thresholds.

    Returns:
        SoulBand with level, gate_modifier, force_council, max_autonomy.
    """
    value = max(0.0, min(1.0, float(soul_integral)))
    t = thresholds or _DEFAULT_BAND_THRESHOLDS

    if value >= t.get("critical", 0.80):
        level = SoulBandLevel.CRITICAL
    elif value >= t.get("strained", 0.55):
        level = SoulBandLevel.STRAINED
    elif value >= t.get("alert", 0.30):
        level = SoulBandLevel.ALERT
    else:
        level = SoulBandLevel.SERENE

    modifiers = _DEFAULT_BAND_MODIFIERS[level]
    return SoulBand(
        level=level,
        soul_integral=value,
        gate_modifier=modifiers["gate_modifier"],
        force_council=modifiers["force_council"],
        max_autonomy=modifiers["max_autonomy"],
    )


# ---------------------------------------------------------------------------
# Reflex Decision
# ---------------------------------------------------------------------------


class ReflexAction(Enum):
    """What the reflex arc decides to do."""

    PASS = "pass"  # Normal output
    WARN = "warn"  # Output with disclaimer
    SOFTEN = "soften"  # Output with caution injection
    BLOCK = "block"  # Output replaced with blocked message


@dataclass
class ReflexDecision:
    """The reflex arc's verdict on a single pipeline pass."""

    action: ReflexAction = ReflexAction.PASS
    gate_modifier: float = 1.0
    soul_band: Optional[SoulBand] = None
    disclaimer: Optional[str] = None
    trigger_reflection: bool = False
    blocked_message: Optional[str] = None
    enforcement_log: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "action": self.action.value,
            "gate_modifier": round(self.gate_modifier, 4),
            "trigger_reflection": self.trigger_reflection,
        }
        if self.soul_band is not None:
            result["soul_band"] = self.soul_band.to_dict()
        if self.disclaimer:
            result["disclaimer"] = self.disclaimer
        if self.blocked_message:
            result["blocked_message"] = self.blocked_message
        if self.enforcement_log:
            result["enforcement_log"] = self.enforcement_log
        return result


# ---------------------------------------------------------------------------
# Drift Checks
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DriftSignal:
    """Extracted drift signals relevant to reflex decisions."""

    caution_bias: float = 0.5
    innovation_bias: float = 0.6
    autonomy_level: float = 0.35
    inject_caution_prompt: bool = False
    inject_risk_prompt: bool = False
    autonomy_capped: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "caution_bias": round(self.caution_bias, 4),
            "autonomy_level": round(self.autonomy_level, 4),
            "inject_caution_prompt": self.inject_caution_prompt,
            "inject_risk_prompt": self.inject_risk_prompt,
            "autonomy_capped": self.autonomy_capped,
        }


def evaluate_drift(
    baseline_drift: Dict[str, float],
    *,
    max_autonomy: Optional[float] = None,
    caution_threshold: float = 0.60,
    risk_threshold: float = 0.75,
) -> DriftSignal:
    """Evaluate baseline drift and produce actionable signals.

    Args:
        baseline_drift: Dict with caution_bias, innovation_bias, autonomy_level.
        max_autonomy: If set, caps autonomy_level at this value.
        caution_threshold: caution_bias above this → inject caution prompt.
        risk_threshold: caution_bias above this → inject risk prompt.
    """
    caution = float(baseline_drift.get("caution_bias", 0.5))
    innovation = float(baseline_drift.get("innovation_bias", 0.6))
    autonomy = float(baseline_drift.get("autonomy_level", 0.35))

    inject_caution = caution > caution_threshold
    inject_risk = caution > risk_threshold
    autonomy_capped = False

    if max_autonomy is not None and autonomy > max_autonomy:
        autonomy_capped = True

    return DriftSignal(
        caution_bias=caution,
        innovation_bias=innovation,
        autonomy_level=autonomy,
        inject_caution_prompt=inject_caution,
        inject_risk_prompt=inject_risk,
        autonomy_capped=autonomy_capped,
    )


# ---------------------------------------------------------------------------
# Reflex Evaluator
# ---------------------------------------------------------------------------


@dataclass
class ConvictionSignal:
    """Tracks vow conviction decay for reflex evaluation."""

    decaying_vows: List[Dict[str, Any]] = field(default_factory=list)
    min_conviction: float = 1.0
    trigger_self_assessment: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decaying_vows": self.decaying_vows[:5],
            "min_conviction": round(self.min_conviction, 4),
            "trigger_self_assessment": self.trigger_self_assessment,
        }


def evaluate_conviction_decay(
    vows: Any,
    *,
    decay_threshold: float = 0.4,
) -> ConvictionSignal:
    """Check if any vow's conviction has decayed below threshold.

    Args:
        vows: Vow state (list of dicts or object with .vows attribute).
        decay_threshold: Conviction below this triggers self-assessment.
    """
    vow_list: List[Dict[str, Any]] = []
    if isinstance(vows, list):
        vow_list = [v for v in vows if isinstance(v, dict)]
    elif hasattr(vows, "vows") and isinstance(getattr(vows, "vows", None), list):
        vow_list = [v for v in vows.vows if isinstance(v, dict)]

    if not vow_list:
        return ConvictionSignal()

    decaying: List[Dict[str, Any]] = []
    min_conv = 1.0

    for vow in vow_list:
        conviction = float(vow.get("conviction", 1.0))
        trajectory = str(vow.get("trajectory", "")).strip().lower()
        min_conv = min(min_conv, conviction)

        if conviction < decay_threshold and trajectory == "decaying":
            decaying.append(
                {
                    "vow_id": str(vow.get("id") or vow.get("vow_id") or "unknown"),
                    "conviction": round(conviction, 4),
                    "trajectory": trajectory,
                }
            )

    return ConvictionSignal(
        decaying_vows=decaying,
        min_conviction=min_conv,
        trigger_self_assessment=len(decaying) > 0,
    )


@dataclass
class GovernanceSnapshot:
    """Minimal governance context needed for reflex evaluation."""

    soul_integral: float = 0.0
    baseline_drift: Dict[str, float] = field(
        default_factory=lambda: {
            "caution_bias": 0.5,
            "innovation_bias": 0.6,
            "autonomy_level": 0.35,
        }
    )
    tension: float = 0.0
    vow_blocked: bool = False
    vow_repair_needed: bool = False
    vow_flags: List[str] = field(default_factory=list)
    council_verdict: Optional[str] = None  # "BLOCK", "WARN", etc.
    conviction_signal: Optional[ConvictionSignal] = None

    @classmethod
    def from_posture(
        cls,
        posture: Any,
        *,
        tension: float = 0.0,
        vow_blocked: bool = False,
        vow_repair_needed: bool = False,
        vow_flags: Optional[List[str]] = None,
        council_verdict: Optional[str] = None,
    ) -> GovernanceSnapshot:
        """Build snapshot from GovernancePosture + runtime signals."""
        si = float(getattr(posture, "soul_integral", 0.0) or 0.0)
        drift = dict(getattr(posture, "baseline_drift", {}) or {})

        # Extract conviction signal from vow state
        vows = getattr(posture, "vows", None) or getattr(posture, "vow_state", None)
        conviction = evaluate_conviction_decay(vows) if vows else None

        return cls(
            soul_integral=si,
            baseline_drift=drift,
            tension=float(tension),
            vow_blocked=bool(vow_blocked),
            vow_repair_needed=bool(vow_repair_needed),
            vow_flags=list(vow_flags or []),
            council_verdict=str(council_verdict).strip().upper() if council_verdict else None,
            conviction_signal=conviction,
        )


class ReflexEvaluator:
    """Evaluates governance state and produces a ReflexDecision.

    This is the core of the reflex arc — it reads governance posture and
    decides how the pipeline should behave.

    Phase 1 (soft mode): WARN and disclaimers only, no blocking.
    Phase 2 (hard mode): BLOCK when vows or council demand it.
    """

    def __init__(self, config: Optional[Any] = None) -> None:
        self._config = config

    @property
    def enabled(self) -> bool:
        if self._config is not None:
            return bool(getattr(self._config, "enabled", True))
        return True

    @property
    def mode(self) -> str:
        """'soft', 'hard', or 'off'."""
        if self._config is not None:
            return str(getattr(self._config, "vow_enforcement_mode", "soft"))
        return "soft"

    def evaluate(self, snapshot: GovernanceSnapshot) -> ReflexDecision:
        """Produce a ReflexDecision from governance state.

        This is the single entry point for all reflex evaluation. It
        classifies the soul band, checks drift, vows, and council state,
        and returns a unified decision.

        Args:
            snapshot: Current governance state snapshot.

        Returns:
            ReflexDecision with action, gate_modifier, disclaimer, etc.
        """
        if not self.enabled:
            return ReflexDecision(action=ReflexAction.PASS, gate_modifier=1.0)

        config = self._config

        log: List[Dict[str, Any]] = []
        timestamp = datetime.now(timezone.utc).isoformat()

        band_thresholds = None
        caution_threshold = 0.60
        risk_threshold = 0.75
        tension_reflection_threshold = 0.70
        soul_integral_reflection_threshold = 0.55
        council_block_enforcement = True

        if config is not None:
            raw_thresholds = getattr(config, "soul_band_thresholds", None)
            if isinstance(raw_thresholds, dict):
                band_thresholds = raw_thresholds
            caution_threshold = float(
                getattr(config, "caution_prompt_threshold", caution_threshold)
            )
            risk_threshold = float(getattr(config, "risk_prompt_threshold", risk_threshold))
            tension_reflection_threshold = float(
                getattr(config, "tension_reflection_threshold", tension_reflection_threshold)
            )
            soul_integral_reflection_threshold = float(
                getattr(
                    config,
                    "soul_integral_reflection_threshold",
                    soul_integral_reflection_threshold,
                )
            )
            council_block_enforcement = bool(
                getattr(config, "council_block_enforcement", council_block_enforcement)
            )

        # 1. Classify soul band
        band = classify_soul_band(snapshot.soul_integral, thresholds=band_thresholds)
        gate_modifier = band.gate_modifier
        trigger_reflection = False
        action = ReflexAction.PASS
        disclaimer: Optional[str] = None
        blocked_message: Optional[str] = None

        log.append(
            {
                "step": "soul_band",
                "level": band.level.value,
                "soul_integral": round(snapshot.soul_integral, 4),
                "gate_modifier": round(gate_modifier, 4),
                "timestamp": timestamp,
            }
        )

        # 2. Evaluate drift
        drift_signal = evaluate_drift(
            snapshot.baseline_drift,
            max_autonomy=band.max_autonomy,
            caution_threshold=caution_threshold,
            risk_threshold=risk_threshold,
        )
        if drift_signal.autonomy_capped:
            log.append(
                {
                    "step": "drift_autonomy_cap",
                    "original": round(snapshot.baseline_drift.get("autonomy_level", 0.35), 4),
                    "capped_at": (
                        round(band.max_autonomy, 4) if band.max_autonomy is not None else None
                    ),
                }
            )

        # 3. Soul band behavioral changes
        if band.level == SoulBandLevel.ALERT:
            # Tighten gates 10%, add disclaimer on WARN-level outputs
            if snapshot.tension >= 0.40:
                disclaimer = (
                    "[治理提示] 目前 soul integral 偏高 "
                    f"({snapshot.soul_integral:.2f})，系統正在警覺模式。"
                )
                action = ReflexAction.WARN
                log.append({"step": "alert_disclaimer", "tension": round(snapshot.tension, 4)})

        elif band.level == SoulBandLevel.STRAINED:
            # Tighten gates 25%, force council, cap autonomy
            trigger_reflection = True
            disclaimer = (
                "[治理警告] soul integral 處於緊繃狀態 "
                f"({snapshot.soul_integral:.2f})，閘門閾值已收緊 25%。"
            )
            action = ReflexAction.SOFTEN
            log.append({"step": "strained_enforcement", "force_council": True})

        elif band.level == SoulBandLevel.CRITICAL:
            # Hard enforcement in hard mode, soften in soft mode
            trigger_reflection = True
            if self.mode == "hard":
                blocked_message = (
                    "[治理危機] soul integral 處於危機狀態 "
                    f"({snapshot.soul_integral:.2f})，已攔截輸出。"
                )
                action = ReflexAction.BLOCK
            else:
                disclaimer = (
                    "[治理危機] soul integral 處於危機狀態 "
                    f"({snapshot.soul_integral:.2f})，建議暫停自主操作。"
                )
                action = ReflexAction.SOFTEN
            log.append({"step": "critical_enforcement", "mode": self.mode})

        # 4. Tension + soul_integral combined trigger
        if (
            snapshot.tension > tension_reflection_threshold
            and snapshot.soul_integral > soul_integral_reflection_threshold
        ):
            trigger_reflection = True
            log.append(
                {
                    "step": "tension_reflection_trigger",
                    "tension": round(snapshot.tension, 4),
                    "soul_integral": round(snapshot.soul_integral, 4),
                }
            )

        # 5. Vow enforcement
        if snapshot.vow_blocked:
            if self.mode == "hard":
                blocked_vows = (
                    ", ".join(snapshot.vow_flags[:3]) if snapshot.vow_flags else "unknown"
                )
                blocked_message = f"此回應未通過誓言守護 [{blocked_vows}]，已被攔截。"
                action = ReflexAction.BLOCK
                log.append({"step": "vow_block", "flags": snapshot.vow_flags[:3]})
            else:
                # Soft mode: warn but don't block
                vow_info = ", ".join(snapshot.vow_flags[:3]) if snapshot.vow_flags else "unknown"
                disclaimer = (
                    f"[誓言警告] 此回應觸發了誓言違規 [{vow_info}]，"
                    "但目前為軟執行模式，輸出未被攔截。"
                )
                action = max(action, ReflexAction.WARN, key=lambda a: _ACTION_SEVERITY[a])
                log.append({"step": "vow_warn_soft", "flags": snapshot.vow_flags[:3]})

        elif snapshot.vow_repair_needed:
            trigger_reflection = True
            log.append({"step": "vow_repair_trigger"})

        # 5b. Conviction decay self-assessment
        if snapshot.conviction_signal and snapshot.conviction_signal.trigger_self_assessment:
            trigger_reflection = True
            decaying = snapshot.conviction_signal.decaying_vows
            if not disclaimer:
                vow_ids = ", ".join(d.get("vow_id", "?") for d in decaying[:3])
                disclaimer = (
                    f"[誓言衰退警告] 以下誓言的 conviction 正在下降：[{vow_ids}]。"
                    "建議進行自我評估。"
                )
            action = max(action, ReflexAction.WARN, key=lambda a: _ACTION_SEVERITY[a])
            log.append(
                {
                    "step": "conviction_decay",
                    "decaying_vows": decaying[:3],
                    "min_conviction": round(snapshot.conviction_signal.min_conviction, 4),
                }
            )

        # 6. Council BLOCK enforcement
        if snapshot.council_verdict == "BLOCK":
            if not council_block_enforcement:
                log.append({"step": "council_block_ignored_by_config"})
            elif self.mode == "hard":
                blocked_message = "此回應被 Council 判定為 BLOCK，已被攔截。"
                action = ReflexAction.BLOCK
                log.append({"step": "council_block"})
            else:
                disclaimer = "[Council 警告] Council 判定 BLOCK，但目前為軟執行模式。"
                action = max(action, ReflexAction.WARN, key=lambda a: _ACTION_SEVERITY[a])
                log.append({"step": "council_block_soft"})

        # 7. Drift prompt injection signals
        if drift_signal.inject_caution_prompt:
            log.append(
                {
                    "step": "drift_caution_inject",
                    "caution_bias": round(drift_signal.caution_bias, 4),
                }
            )
        if drift_signal.inject_risk_prompt:
            log.append(
                {"step": "drift_risk_inject", "caution_bias": round(drift_signal.caution_bias, 4)}
            )

        return ReflexDecision(
            action=action,
            gate_modifier=gate_modifier,
            soul_band=band,
            disclaimer=disclaimer,
            trigger_reflection=trigger_reflection,
            blocked_message=blocked_message,
            enforcement_log=log,
        )


# Severity ordering for max() comparison
_ACTION_SEVERITY: Dict[ReflexAction, int] = {
    ReflexAction.PASS: 0,
    ReflexAction.WARN: 1,
    ReflexAction.SOFTEN: 2,
    ReflexAction.BLOCK: 3,
}


# ---------------------------------------------------------------------------
# Lightweight Vow Gate (for Dashboard chat path)
# ---------------------------------------------------------------------------


def enforce_vows_lightweight(
    output: str,
    *,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Quick vow check for the dashboard chat path.

    This is a thin wrapper around VowEnforcer for use in
    apps/dashboard chat_with_council(). It returns a dict with
    'passed', 'blocked', 'flags', and optional 'replacement'.

    Args:
        output: The AI response text to check.
        context: Optional context dict for vow evaluation.

    Returns:
        Dict with enforcement result.
    """
    try:
        from tonesoul.vow_system import VowEnforcer

        enforcer = VowEnforcer()
        result = enforcer.enforce(output, context)
        return {
            "passed": result.all_passed,
            "blocked": result.blocked,
            "repair_needed": result.repair_needed,
            "flags": list(result.flags),
            "replacement": ("此回應未通過誓言守護，已被攔截。" if result.blocked else None),
        }
    except Exception as exc:
        logger.warning("enforce_vows_lightweight failed: %s — failing closed", exc)
        return {
            "passed": False,
            "blocked": True,
            "repair_needed": True,
            "flags": [f"vow_check_error: {exc}"],
            "replacement": ("此回應未能通過誓言檢查（內部錯誤），已被預防性攔截。"),
        }
