"""
RFC-013: Work Category Classifier.

Classifies the current work context into one of five categories,
each with a different constraint profile for the variance compressor.

Classification priority:
  1. Explicit workflow hint (from /fullstack-engineer, /ci-debug, etc.)
  2. Context signals (genesis, user_intent)
  3. Keyword heuristics on user message text
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class WorkCategory(Enum):
    """Five work modes with increasing constraint strictness."""

    FREEFORM = "freeform"
    RESEARCH = "research"
    ARCHITECTURE = "architecture"
    ENGINEERING = "engineering"
    DEBUG = "debug"


@dataclass(frozen=True)
class ConstraintProfile:
    """Constraint parameters for a given work category."""

    gamma_base: float
    """Base variance compression strength (higher → stronger)."""

    bridge_strictness: float
    """Multiplier on the bridge guard threshold (higher → stricter).
    Used as: W_c < bridge_strictness * 0.5 * θ_c."""

    memory_policy: str
    """'full' | 'selective' | 'none'."""

    label: str
    """Human-readable label for logging."""


# ── constraint profiles ──────────────────────────────────────────

PROFILES: Dict[WorkCategory, ConstraintProfile] = {
    WorkCategory.FREEFORM: ConstraintProfile(
        gamma_base=0.1,
        bridge_strictness=0.0,  # bridges always allowed
        memory_policy="none",
        label="自由探索",
    ),
    WorkCategory.RESEARCH: ConstraintProfile(
        gamma_base=0.2,
        bridge_strictness=0.5,
        memory_policy="selective",
        label="研究分析",
    ),
    WorkCategory.ARCHITECTURE: ConstraintProfile(
        gamma_base=0.4,
        bridge_strictness=1.0,
        memory_policy="full",
        label="架構設計",
    ),
    WorkCategory.ENGINEERING: ConstraintProfile(
        gamma_base=0.6,
        bridge_strictness=1.5,
        memory_policy="full",
        label="工程實作",
    ),
    WorkCategory.DEBUG: ConstraintProfile(
        gamma_base=0.7,
        bridge_strictness=999.0,  # bridges effectively disabled
        memory_policy="full",
        label="除錯修復",
    ),
}


def get_profile(category: WorkCategory) -> ConstraintProfile:
    """Return the constraint profile for a work category."""
    return PROFILES[category]


# ── keyword patterns ─────────────────────────────────────────────

_DEBUG_PATTERNS = re.compile(
    r"(?:修\s?bug|debug|修復|修正|壞掉|broken|crash|error|fail|紅燈|ci.?red|"
    r"stack\s?trace|traceback|exception|segfault|panic)",
    re.IGNORECASE,
)

_ENGINEERING_PATTERNS = re.compile(
    r"(?:實作|implement|寫|write|build|create|新增|add|feature|功能|"
    r"refactor|重構|migrate|遷移|PR|pull\s?request|commit)",
    re.IGNORECASE,
)

_ARCHITECTURE_PATTERNS = re.compile(
    r"(?:架構|architecture|設計|design|RFC|spec|規格|blueprint|"
    r"interface|介面|API|schema|protocol|trade.?off)",
    re.IGNORECASE,
)

_RESEARCH_PATTERNS = re.compile(
    r"(?:研究|research|探索|explore|分析|analy|調查|investigate|"
    r"比較|compare|survey|benchmark|experiment|試試|look\s?into)",
    re.IGNORECASE,
)

# ── workflow hint mapping ────────────────────────────────────────

_WORKFLOW_MAP: Dict[str, WorkCategory] = {
    "fullstack-engineer": WorkCategory.ENGINEERING,
    "fullstack_engineer": WorkCategory.ENGINEERING,
    "ci-debug": WorkCategory.DEBUG,
    "ci_debug": WorkCategory.DEBUG,
    "git-hygiene": WorkCategory.ENGINEERING,
    "git_hygiene": WorkCategory.ENGINEERING,
    "antigravity": WorkCategory.ARCHITECTURE,
    "vibe_mode": WorkCategory.FREEFORM,
    "vibe-mode": WorkCategory.FREEFORM,
}


# ── public API ───────────────────────────────────────────────────


def classify_work(
    user_message: str = "",
    *,
    context: Optional[Dict[str, object]] = None,
    workflow_hint: Optional[str] = None,
) -> WorkCategory:
    """
    Classify the current work context.

    Priority order:
      1. workflow_hint   (explicit user choice via slash command)
      2. context signals (genesis / user_intent)
      3. keyword heuristics on user_message
      4. default → ENGINEERING

    Parameters
    ----------
    user_message : str
        The user's latest message text.
    context : dict, optional
        Pipeline context dict (may contain 'genesis', 'user_intent', etc.).
    workflow_hint : str, optional
        Active workflow name (e.g. 'fullstack-engineer').

    Returns
    -------
    WorkCategory
    """
    # 1) Workflow hint takes absolute priority
    if workflow_hint:
        hint_lower = workflow_hint.strip().lower()
        matched = _WORKFLOW_MAP.get(hint_lower)
        if matched is not None:
            return matched

    # 2) Context signals
    if isinstance(context, dict):
        user_intent = str(context.get("user_intent", "")).lower()
        genesis = str(context.get("genesis", "")).lower()

        if "debug" in user_intent or "fix" in user_intent:
            return WorkCategory.DEBUG
        if genesis == "mandatory" or "boot" in str(context.get("trigger", "")):
            return WorkCategory.ENGINEERING

    # 3) Keyword heuristics (ordered from strictest to loosest)
    msg = user_message.strip()
    if msg:
        if _DEBUG_PATTERNS.search(msg):
            return WorkCategory.DEBUG
        if _ARCHITECTURE_PATTERNS.search(msg):
            return WorkCategory.ARCHITECTURE
        if _ENGINEERING_PATTERNS.search(msg):
            return WorkCategory.ENGINEERING
        if _RESEARCH_PATTERNS.search(msg):
            return WorkCategory.RESEARCH

    # 4) Default
    return WorkCategory.ENGINEERING
