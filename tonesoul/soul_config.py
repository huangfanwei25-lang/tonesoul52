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

from dataclasses import dataclass, field
from typing import List

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
    governance_gate_score: float = 0.92  # POAV consensus required (Axiom 3)
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
    "FORBIDDEN_ACTIONS",
]
