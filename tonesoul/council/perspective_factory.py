"""
Pluggable Perspective System

P2 Issue 8: Make perspectives pluggable so they can be:
- Rules-based (current default)
- LLM-based (call an LLM for evaluation)
- Tool-verified (use external tools)

Usage:
    from tonesoul.council.perspective_factory import PerspectiveFactory

    # Create rules-based perspective (default)
    guardian = PerspectiveFactory.create("guardian", mode="rules")

    # Create LLM-based perspective (requires API key)
    analyst = PerspectiveFactory.create("analyst", mode="llm", model="gpt-4")

    # Create tool-verified perspective
    critic = PerspectiveFactory.create("critic", mode="tool", tool=my_tool)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from .base import IPerspective
from .perspectives.guardian import GuardianPerspective
from .perspectives.analyst import AnalystPerspective
from .perspectives.critic import CriticPerspective
from .perspectives.advocate import AdvocatePerspective
from .types import PerspectiveType, PerspectiveVote, VoteDecision

PerspectiveId = Union[PerspectiveType, str]


class PerspectiveMode(Enum):
    """Supported perspective evaluation modes"""
    RULES = "rules"       # Default heuristic rules
    LLM = "llm"          # LLM-based evaluation
    TOOL = "tool"        # External tool verification
    HYBRID = "hybrid"    # Combination of rules + LLM


@dataclass
class PerspectiveConfig:
    """Configuration for creating a perspective"""
    name: str
    mode: PerspectiveMode = PerspectiveMode.RULES
    model: Optional[str] = None  # For LLM mode
    tool: Optional[Callable] = None  # For TOOL mode
    fallback_to_rules: bool = True  # If LLM/tool fails, use rules
    timeout_seconds: float = 10.0  # Timeout for external calls


def _normalize_name(name: Union[str, PerspectiveType]) -> str:
    if isinstance(name, PerspectiveType):
        return name.value
    return str(name).strip().lower()


def _to_perspective(value: Union[str, PerspectiveType]) -> PerspectiveId:
    normalized = _normalize_name(value)
    try:
        return PerspectiveType(normalized)
    except ValueError:
        return normalized


def _normalize_decision(value: object) -> VoteDecision:
    if isinstance(value, VoteDecision):
        return value
    if value is None:
        return VoteDecision.CONCERN
    normalized = str(value).strip().lower()
    mapping = {
        "approve": VoteDecision.APPROVE,
        "concern": VoteDecision.CONCERN,
        "object": VoteDecision.OBJECT,
        "abstain": VoteDecision.ABSTAIN,
    }
    return mapping.get(normalized, VoteDecision.CONCERN)


def _normalize_mode(mode: Union[str, PerspectiveMode]) -> PerspectiveMode:
    if isinstance(mode, PerspectiveMode):
        return mode
    if isinstance(mode, str):
        return PerspectiveMode(mode.strip().lower())
    raise ValueError(f"Unsupported mode type: {type(mode)!r}")


def _safe_confidence(value: object, default: float = 0.5) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class LLMPerspective(IPerspective):
    """LLM-based perspective that calls an external model for evaluation.

    NOTE: This is a placeholder implementation. Actual LLM integration
    requires API keys and client setup. Until then it falls back to rules.
    """

    def __init__(
        self,
        name: Union[str, PerspectiveType],
        model: str = "gpt-4",
        system_prompt: Optional[str] = None,
        fallback: Optional[IPerspective] = None,
    ):
        self.name = _normalize_name(name)
        self.model = model
        self.system_prompt = system_prompt or self._default_prompt()
        self.fallback = fallback
        self._perspective = _to_perspective(self.name)

    @property
    def perspective_type(self) -> PerspectiveId:
        return self._perspective

    def _default_prompt(self) -> str:
        prompts = {
            "guardian": """You are a safety guardian. Evaluate if the following text is safe.
Respond with: APPROVE (safe), CONCERN (unclear), or OBJECT (unsafe).
Also provide confidence (0.0-1.0) and brief reasoning.""",
            "analyst": """You are a factual analyst. Evaluate if the following text is factually sound.
Respond with: APPROVE (factual), CONCERN (unverifiable), or OBJECT (false).
Also provide confidence (0.0-1.0) and brief reasoning.""",
            "critic": """You are a critical thinker. Identify weaknesses in the following text.
Respond with: APPROVE (robust), CONCERN (has issues), or OBJECT (fundamentally flawed).
Also provide confidence (0.0-1.0) and brief reasoning.""",
            "advocate": """You are a user advocate. Evaluate if the following text serves the user's intent.
Respond with: APPROVE (helpful), CONCERN (partially helpful), or OBJECT (unhelpful).
Also provide confidence (0.0-1.0) and brief reasoning.""",
        }
        return prompts.get(self.name, prompts["analyst"])

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        """
        Evaluate using LLM.

        NOTE: Placeholder only. Until LLM integration is wired, always use
        the rules-based fallback if present.
        """
        if self.fallback:
            return self.fallback.evaluate(draft_output, context, user_intent)

        return PerspectiveVote(
            perspective=self.perspective_type,
            decision=VoteDecision.CONCERN,
            confidence=0.5,
            reasoning="LLM integration not configured; fallback unavailable.",
        )


class ToolVerifiedPerspective(IPerspective):
    """Perspective that uses external tools for verification.

    Example tools:
    - Fact-checking API
    - Code syntax checker
    - External knowledge base query
    """

    def __init__(
        self,
        name: Union[str, PerspectiveType],
        tool: Callable[[str, dict], Dict[str, Any]],
        fallback: Optional[IPerspective] = None,
    ):
        self.name = _normalize_name(name)
        self.tool = tool
        self.fallback = fallback
        self._perspective = _to_perspective(self.name)

    @property
    def perspective_type(self) -> PerspectiveId:
        return self._perspective

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        """
        Evaluate using external tool.

        Tool should return dict with:
        - "decision": "APPROVE" | "CONCERN" | "OBJECT"
        - "confidence": float 0.0-1.0
        - "reasoning": str
        """
        try:
            result = self.tool(draft_output, context)
            decision = _normalize_decision(result.get("decision"))
            confidence = _safe_confidence(result.get("confidence", 0.5))
            return PerspectiveVote(
                perspective=self.perspective_type,
                decision=decision,
                confidence=confidence,
                reasoning=result.get("reasoning", "Tool evaluation"),
            )
        except Exception as exc:
            if self.fallback:
                return self.fallback.evaluate(draft_output, context, user_intent)
            return PerspectiveVote(
                perspective=self.perspective_type,
                decision=VoteDecision.CONCERN,
                confidence=0.5,
                reasoning=f"Tool error: {exc}",
            )


class PerspectiveFactory:
    """Factory for creating perspectives with different evaluation modes."""

    _default_perspectives = {
        "guardian": GuardianPerspective,
        "analyst": AnalystPerspective,
        "critic": CriticPerspective,
        "advocate": AdvocatePerspective,
    }

    @classmethod
    def create(
        cls,
        name: Union[str, PerspectiveType],
        mode: Union[str, PerspectiveMode] = "rules",
        model: Optional[str] = None,
        tool: Optional[Callable] = None,
        **kwargs,
    ) -> IPerspective:
        """
        Create a perspective with the specified evaluation mode.

        Args:
            name: Perspective name (guardian, analyst, critic, advocate)
            mode: Evaluation mode (rules, llm, tool, hybrid)
            model: Model name for LLM mode
            tool: External tool function for tool mode
            **kwargs: Additional configuration

        Returns:
            IPerspective instance
        """
        mode_enum = _normalize_mode(mode)
        normalized_name = _normalize_name(name)

        # Get the rules-based fallback
        rules_class = cls._default_perspectives.get(normalized_name)
        if not rules_class:
            raise ValueError(f"Unknown perspective: {name}")

        rules_perspective = rules_class()
        fallback_to_rules = kwargs.pop("fallback_to_rules", True)
        fallback = rules_perspective if fallback_to_rules else None

        if mode_enum == PerspectiveMode.RULES:
            return rules_perspective

        if mode_enum == PerspectiveMode.LLM:
            return LLMPerspective(
                name=normalized_name,
                model=model or "gpt-4",
                fallback=fallback,
            )

        if mode_enum == PerspectiveMode.TOOL:
            if not tool:
                raise ValueError("Tool mode requires a tool function")
            return ToolVerifiedPerspective(
                name=normalized_name,
                tool=tool,
                fallback=fallback,
            )

        if mode_enum == PerspectiveMode.HYBRID:
            # Hybrid: try LLM first, fall back to rules
            return LLMPerspective(
                name=normalized_name,
                model=model or "gpt-4",
                fallback=fallback,
            )

        raise ValueError(f"Unsupported mode: {mode}")

    @classmethod
    def create_council(
        cls,
        config: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[IPerspective]:
        """
        Create a complete set of perspectives for the council.

        Args:
            config: Optional dict mapping perspective names to their configs
                    e.g., {"guardian": {"mode": "llm", "model": "gpt-4"}}

        Returns:
            List of IPerspective instances
        """
        config = config or {}
        perspectives: List[IPerspective] = []

        for name in ["guardian", "analyst", "critic", "advocate"]:
            perspective_config = config.get(name, {"mode": "rules"})
            if not isinstance(perspective_config, dict):
                perspective_config = {"mode": "rules"}
            perspectives.append(cls.create(name=name, **perspective_config))

        return perspectives


# Example usage
if __name__ == "__main__":
    # Default rules-based council
    council_rules = PerspectiveFactory.create_council()
    print(f"Rules-based council: {[p.__class__.__name__ for p in council_rules]}")

    # Hybrid council with LLM guardian
    council_hybrid = PerspectiveFactory.create_council({
        "guardian": {"mode": "llm", "model": "gpt-4"},
        "analyst": {"mode": "rules"},
        "critic": {"mode": "rules"},
        "advocate": {"mode": "rules"},
    })
    print(f"Hybrid council: {[type(p).__name__ for p in council_hybrid]}")
