"""Shared pipeline context schema for runtime and governance pipelines.

Provides a common dataclass that both UnifiedPipeline (runtime) and
yss_pipeline (governance/offline) can use as a shared context snapshot.

This bridges the schema divergence identified in RFC-009 §5 (Phase 100C).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PipelineContextSnapshot:
    """Shared context schema for both runtime and governance pipelines.

    Fields are intentionally Optional so that each pipeline can populate
    only the subset it produces, while the other pipeline can consume
    whatever is available.
    """

    # TensionEngine output
    tension_score: Optional[float] = None
    tension_zone: Optional[str] = None  # "safe" / "transit" / "risk" / "danger"
    tension_signals: Optional[Dict[str, float]] = None

    # SelfCommitStack
    commitment_stack: List[str] = field(default_factory=list)

    # RuptureDetector
    rupture_signals: List[Dict[str, Any]] = field(default_factory=list)

    # Memory summary
    memory_summary: Optional[Dict[str, Any]] = None

    # Semantic topics from ToneBridge
    semantic_topics: List[str] = field(default_factory=list)

    # Council verdict summary (post-deliberation)
    verdict_type: Optional[str] = None  # "approve" / "refine" / "block" / "declare_stance"
    verdict_coherence: Optional[float] = None

    # Provenance
    genesis: Optional[str] = None
    responsibility_tier: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for cross-pipeline transport."""
        return {
            "tension_score": self.tension_score,
            "tension_zone": self.tension_zone,
            "tension_signals": self.tension_signals,
            "commitment_stack": self.commitment_stack,
            "rupture_signals": self.rupture_signals,
            "memory_summary": self.memory_summary,
            "semantic_topics": self.semantic_topics,
            "verdict_type": self.verdict_type,
            "verdict_coherence": self.verdict_coherence,
            "genesis": self.genesis,
            "responsibility_tier": self.responsibility_tier,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineContextSnapshot":
        """Deserialize from dict."""
        return cls(
            tension_score=data.get("tension_score"),
            tension_zone=data.get("tension_zone"),
            tension_signals=data.get("tension_signals"),
            commitment_stack=data.get("commitment_stack", []),
            rupture_signals=data.get("rupture_signals", []),
            memory_summary=data.get("memory_summary"),
            semantic_topics=data.get("semantic_topics", []),
            verdict_type=data.get("verdict_type"),
            verdict_coherence=data.get("verdict_coherence"),
            genesis=data.get("genesis"),
            responsibility_tier=data.get("responsibility_tier"),
        )
