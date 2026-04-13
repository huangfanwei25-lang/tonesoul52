"""
YUHUN Core Protocol v1.0 — yuhun 模組入口
"""

from .context_assembler import (
    ContextAssembler,
    ContextPackage,
    ContextViolationError,
    validate_context_sources,
)
from .dpr import DPRResult, RoutingDecision, route
from .shadow_doc import (
    BlockerSeverity,
    CreatorOutput,
    IntentFrame,
    L1Blocker,
    L2Opportunity,
    LegalProfile,
    Lifecycle,
    LogicianOutput,
    OutputMode,
    SafetyOutput,
    SafetyVerdict,
    ShadowDocument,
    TensionMetrics,
    TrajectoryDigest,
)
from .vod import TensionLevel, VoDResult, assess_divergence

__all__ = [
    # DPR
    "route",
    "RoutingDecision",
    "DPRResult",
    # Shadow Document
    "ShadowDocument",
    "TrajectoryDigest",
    "LogicianOutput",
    "CreatorOutput",
    "SafetyOutput",
    "SafetyVerdict",
    "IntentFrame",
    "TensionMetrics",
    "LegalProfile",
    "Lifecycle",
    "L1Blocker",
    "L2Opportunity",
    "BlockerSeverity",
    "OutputMode",
    # Context Assembler
    "ContextAssembler",
    "ContextPackage",
    "ContextViolationError",
    "validate_context_sources",
    # VoD
    "assess_divergence",
    "TensionLevel",
    "VoDResult",
]

__version__ = "1.0.0"
