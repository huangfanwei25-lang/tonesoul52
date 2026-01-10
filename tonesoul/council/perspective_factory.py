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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .perspectives.guardian import GuardianPerspective
from .perspectives.analyst import AnalystPerspective
from .perspectives.critic import CriticPerspective
from .perspectives.advocate import AdvocatePerspective
from .base import IPerspective
from .types import PerspectiveVote, VoteDecision


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


class LLMPerspective(IPerspective):
    """LLM-based perspective that calls an external model for evaluation.
    
    NOTE: This is a placeholder implementation. 
    Actual LLM integration requires API keys and client setup.
    """
    
    def __init__(
        self, 
        name: str, 
        model: str = "gpt-4",
        system_prompt: Optional[str] = None,
        fallback: Optional[IPerspective] = None,
    ):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt or self._default_prompt()
        self.fallback = fallback
    
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
        
        NOTE: This is a placeholder. Actual implementation would:
        1. Call OpenAI/Anthropic/local LLM API
        2. Parse response to extract decision, confidence, reasoning
        3. Fall back to rules if API fails
        """
        # Placeholder: always fall back to rules for now
        if self.fallback:
            return self.fallback.evaluate(draft_output, context, user_intent)
        
        # Default safe response if no fallback
        return PerspectiveVote(
            perspective_name=f"{self.name}_llm",
            decision=VoteDecision.CONCERN,
            confidence=0.5,
            reasoning="LLM integration not configured",
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
        name: str,
        tool: Callable[[str, dict], Dict[str, Any]],
        fallback: Optional[IPerspective] = None,
    ):
        self.name = name
        self.tool = tool
        self.fallback = fallback
    
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
            decision = VoteDecision[result.get("decision", "CONCERN")]
            return PerspectiveVote(
                perspective_name=f"{self.name}_tool",
                decision=decision,
                confidence=result.get("confidence", 0.5),
                reasoning=result.get("reasoning", "Tool evaluation"),
            )
        except Exception as e:
            if self.fallback:
                return self.fallback.evaluate(draft_output, context, user_intent)
            return PerspectiveVote(
                perspective_name=f"{self.name}_tool",
                decision=VoteDecision.CONCERN,
                confidence=0.5,
                reasoning=f"Tool error: {e}",
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
        name: str,
        mode: str = "rules",
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
        mode_enum = PerspectiveMode(mode)
        
        # Get the rules-based fallback
        rules_class = cls._default_perspectives.get(name.lower())
        if not rules_class:
            raise ValueError(f"Unknown perspective: {name}")
        
        rules_perspective = rules_class()
        
        if mode_enum == PerspectiveMode.RULES:
            return rules_perspective
        
        elif mode_enum == PerspectiveMode.LLM:
            return LLMPerspective(
                name=name,
                model=model or "gpt-4",
                fallback=rules_perspective,
            )
        
        elif mode_enum == PerspectiveMode.TOOL:
            if not tool:
                raise ValueError("Tool mode requires a tool function")
            return ToolVerifiedPerspective(
                name=name,
                tool=tool,
                fallback=rules_perspective,
            )
        
        elif mode_enum == PerspectiveMode.HYBRID:
            # Hybrid: try LLM first, fall back to rules
            return LLMPerspective(
                name=name,
                model=model or "gpt-4",
                fallback=rules_perspective,
            )
        
        else:
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
        perspectives = []
        
        for name in ["guardian", "analyst", "critic", "advocate"]:
            perspective_config = config.get(name, {"mode": "rules"})
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
