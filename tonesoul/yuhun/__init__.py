"""
YUHUN Core Protocol v1.0 — yuhun 模組入口
"""

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
)
from .vod import TensionLevel, VoDResult, assess_divergence

__all__ = [
    # DPR
    "route",
    "RoutingDecision",
    "DPRResult",
    # Shadow Document
    "ShadowDocument",
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
    # VoD
    "assess_divergence",
    "TensionLevel",
    "VoDResult",
]

__version__ = "1.0.0"
