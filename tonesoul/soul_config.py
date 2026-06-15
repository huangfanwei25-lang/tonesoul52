"""
ToneSoul Soul Configuration — Single Source of Truth
=====================================================
All behavioral parameters for the ToneSoul governance system.

This module is the ONLY canonical source for soul-level constants.
Other modules MUST import from here rather than defining their own.

SOUL.md documents the *rationale* behind these values.
This module defines the *values themselves*.

Each section references the Axiom(s) it derives from.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

__ts_layer__ = "shared"
__ts_purpose__ = (
    "Soul config: ToneSoul-specific runtime configuration — agent identity and session parameters."
)


def _read_bool_env(name: str, *, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off", ""}:
        return False
    return default


def _read_float_env(name: str, *, default: float) -> float:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    try:
        parsed = float(value)
    except ValueError:
        return default
    if 0.0 <= parsed <= 1.0:
        return parsed
    return default


# ---------------------------------------------------------------------------
# Core Values — weights for governance scoring
# Derived from: Axiom E0 (Choice Before Identity), Axiom 4 (Non-Zero Tension)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CoreValues:
    honesty: float = 1.0  # non-negotiable (Axiom 4: drift prevention)
    humility: float = 0.8  # admit uncertainty
    curiosity: float = 0.6  # drive exploration
    consistency: float = 0.7  # maintain coherence


# ---------------------------------------------------------------------------
# Tension System — thresholds for semantic tension
# Derived from: Axiom 4 (Non-Zero Tension), Axiom 7 (Semantic Field Conservation)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TensionConfig:
    echo_chamber_threshold: float = 0.3  # below = over-compliance
    healthy_friction_max: float = 0.7  # above = over-conflict
    decay_alpha_per_hour: float = 0.05  # exponential decay rate (~14h half-life)
    high_tension_threshold: float = 0.8  # triggers de-escalation (from AXIOMS.json soul_triad)
    prune_threshold: float = 0.01  # below = negligible, prune from history


# ---------------------------------------------------------------------------
# Contradiction Detection
# Derived from: Axiom 1 (Continuity), Axiom 5 (Mirror Recursion)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContradictionConfig:
    confidence_threshold: float = 0.2  # minimum confidence to flag
    topic_similarity_threshold: float = 0.15  # minimum topic overlap


# ---------------------------------------------------------------------------
# Council Deliberation
# Derived from: Axiom 5 (Mirror Recursion)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CouncilConfig:
    coherence_threshold: float = 0.6  # minimum coherence for APPROVE
    block_threshold: float = 0.3  # below = BLOCK
    high_risk_coherence: float = 0.65  # stricter threshold under high risk
    high_risk_block: float = 0.4  # stricter block threshold under high risk
    # Tier 5 semantic overclaim sensor (advisory). Default OFF: it needs an embedding
    # model and is a RECORDED signal only (DESIGN Inv3 — Advisory != Canonical), never
    # a gate. Measured limits: docs/status/semantic_overclaim_eval_2026-06-15.md.
    semantic_overclaim_advisory_enabled: bool = False
    # Tier 5 intent-proportionality gate (advisory). Default OFF: flags when a draft
    # escalates beyond the agent's OWN intent + suggests contracting; records a signal,
    # never auto-edits/blocks (DESIGN Inv3). See intent_proportionality_eval_2026-06-15.md.
    intent_proportionality_advisory_enabled: bool = False


# ---------------------------------------------------------------------------
# Vow System — enforcement thresholds
# Derived from: Axiom 2 (Responsibility Threshold)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VowConfig:
    default_violation_threshold: float = 0.2
    strict_violation_threshold: float = 0.15  # for high-stakes vows
    truthfulness_target: float = 0.95  # ΣVow_001
    hedging_target: float = 0.85  # ΣVow_002
    harm_threshold: float = 1.0  # ΣVow_003 (any harm = block)


# ---------------------------------------------------------------------------
# Risk Posture
# Derived from: Axiom 6 (User Sovereignty), Axiom 2 (Responsibility Threshold)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RiskConfig:
    audit_log_threshold: float = 0.4  # risk > this → immutable log (Axiom 2)
    governance_gate_score: float = 0.92  # POAV gate, high-risk/lockdown path (Axiom 3)
    governance_gate_score_low_risk: float = 0.70  # POAV gate, low-risk/non-lockdown path
    entropy_check_threshold: float = 0.7  # semantic drift → integrity check
    soft_block_threshold: float = 0.9  # risk → soft block + audit


# ---------------------------------------------------------------------------
# Forbidden Actions — absolute prohibitions
# Derived from: Axiom 6 (User Sovereignty), Axiom 1 (Continuity)
# ---------------------------------------------------------------------------

FORBIDDEN_ACTIONS: List[str] = [
    "delete_memory",  # must not erase or hide conversation history
    "deny_past",  # must not deny previous statements
    "sycophantic_lie",  # must not lie to please the user
    "false_certainty",  # must not feign certainty on uncertain matters
]


# ---------------------------------------------------------------------------
# Memory Sovereignty
# Derived from: Axiom 8 (Memory Sovereignty)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MemoryConfig:
    replication_allowed: bool = False  # memories are non-replicable by default
    transfer_requires_consent: bool = True  # explicit owner consent for inheritance
    training_requires_deidentification: bool = True


# ---------------------------------------------------------------------------
# GSE — Governance Semantic Engine
# Derived from: Phase 1 (governance elements) + Phase 2 (strategy_mirror)
# Default-off: strategy_mirror integration is opt-in until catalog calibrated
# against real traffic (per Phase 2 spec §5.1, §10 step 7).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GSEConfig:
    # Phase 2 strategy_mirror — split into two flags (2026-04-29) so the
    # 14-day beta wave Day 7-9 calibration can run "scan-only shadow"
    # mode: capture StrategySignature on every verdict without forcing
    # APPROVE→BLOCK downgrade. Three valid states + one auto-promoted
    # state:
    #
    #   scan=False, enforce=False  → no scan, no signature, no downgrade
    #                                (Phase 2 default; existing behaviour)
    #   scan=True,  enforce=False  → scan + attach signature, NO downgrade
    #                                (shadow mode — for Day 7-9 calibration)
    #   scan=True,  enforce=True   → scan + signature + downgrade rules
    #                                (full enforcement — Day 10+ if approved)
    #   scan=False, enforce=True   → IMPOSSIBLE STATE; auto-promoted to
    #                                scan=True via __post_init__
    #
    # The auto-promotion is by design (Codex 2026-04-28): enforce cannot
    # logically exist without scan — enforce operates on scan output.
    # The split makes that relationship explicit at config-load time.
    # Operator/runtime entry points:
    #   TONESOUL_GSE_STRATEGY_MIRROR_SCAN_ENABLED=1
    #   TONESOUL_GSE_STRATEGY_MIRROR_ENFORCE_ENABLED=1
    #   TONESOUL_GSE_STRATEGY_MIRROR_CONFIDENCE_THRESHOLD=0.45
    # Defaults remain off/off so importing SOUL without env preserves
    # existing behaviour; Day 1 can still start scan-only shadow mode
    # without patching Python objects in-process.
    strategy_mirror_scan_enabled: bool = field(
        default_factory=lambda: _read_bool_env(
            "TONESOUL_GSE_STRATEGY_MIRROR_SCAN_ENABLED",
            default=False,
        )
    )
    strategy_mirror_enforce_enabled: bool = field(
        default_factory=lambda: _read_bool_env(
            "TONESOUL_GSE_STRATEGY_MIRROR_ENFORCE_ENABLED",
            default=False,
        )
    )
    # Phase 2 spec §5 confidence threshold for detector. Default matches
    # the spec's CONFIDENCE_THRESHOLD constant; exposed here so beta
    # operators can lower it during calibration without code changes.
    strategy_mirror_confidence_threshold: float = field(
        default_factory=lambda: _read_float_env(
            "TONESOUL_GSE_STRATEGY_MIRROR_CONFIDENCE_THRESHOLD",
            default=0.5,
        )
    )

    def __post_init__(self) -> None:
        # enforce ⇒ scan auto-promotion. Frozen dataclass requires
        # object.__setattr__ since direct assignment would raise. The
        # promotion is silent-with-rationale: any caller that sets
        # enforce=True implicitly states "I want scan output to act on";
        # we honour that by ensuring scan is on too.
        if self.strategy_mirror_enforce_enabled and not self.strategy_mirror_scan_enabled:
            object.__setattr__(self, "strategy_mirror_scan_enabled", True)


# ---------------------------------------------------------------------------
# Composite — all soul config in one object
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SoulConfig:
    values: CoreValues = field(default_factory=CoreValues)
    tension: TensionConfig = field(default_factory=TensionConfig)
    contradiction: ContradictionConfig = field(default_factory=ContradictionConfig)
    council: CouncilConfig = field(default_factory=CouncilConfig)
    vow: VowConfig = field(default_factory=VowConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    gse: GSEConfig = field(default_factory=GSEConfig)
    forbidden_actions: List[str] = field(default_factory=lambda: list(FORBIDDEN_ACTIONS))


# Module-level singleton — import this
SOUL = SoulConfig()

__all__ = [
    "SOUL",
    "SoulConfig",
    "CoreValues",
    "TensionConfig",
    "ContradictionConfig",
    "CouncilConfig",
    "VowConfig",
    "RiskConfig",
    "MemoryConfig",
    "GSEConfig",
    "FORBIDDEN_ACTIONS",
]
