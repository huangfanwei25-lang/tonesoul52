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
    analyst = PerspectiveFactory.create("analyst", mode="llm", model="gemini-2.0-flash")

    # Create tool-verified perspective
    critic = PerspectiveFactory.create("critic", mode="tool", tool=my_tool)
"""

import json
import logging
import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

try:
    import requests as _requests_mod
except ImportError:  # pragma: no cover
    _requests_mod = None  # type: ignore[assignment]

from .base import IPerspective
from .perspectives.advocate import AdvocatePerspective
from .perspectives.analyst import AnalystPerspective
from .perspectives.axiomatic_inference import AxiomaticInference
from .perspectives.critic import CriticPerspective
from .perspectives.guardian import GuardianPerspective
from .perspectives.semantic_analyst import SemanticAnalystPerspective
from .types import PerspectiveType, PerspectiveVote, VoteDecision

logger = logging.getLogger(__name__)

PerspectiveId = Union[PerspectiveType, str]
DEFAULT_LLM_MODEL = "gemini-2.0-flash"
FALLBACK_REASON_MARKER = "[fallback_to_rules]"
VISUAL_CONTEXT_LIMIT = 800
VISUAL_CONTEXT_TRUNCATION_NOTE = "[visual context truncated for safety]"


class PerspectiveMode(Enum):
    """Supported perspective evaluation modes"""

    RULES = "rules"  # Default heuristic rules
    LLM = "llm"  # LLM-based evaluation (Gemini)
    OLLAMA = "ollama"  # Local model via Ollama REST API
    TOOL = "tool"  # External tool verification
    HYBRID = "hybrid"  # Combination of rules + LLM


@dataclass
class PerspectiveConfig:
    """Configuration for creating a perspective"""

    name: PerspectiveId
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


def _normalize_council_config(
    config: Optional[Dict[PerspectiveId, Any]],
) -> Dict[str, Dict[str, Any]]:
    normalized: Dict[str, Dict[str, Any]] = {}
    if not config:
        return normalized
    for key, value in config.items():
        normalized_key = _normalize_name(key)
        if isinstance(value, dict):
            normalized[normalized_key] = dict(value)
        else:
            normalized[normalized_key] = {"mode": "rules"}
    return normalized


class LLMPerspective(IPerspective):
    """LLM-based perspective that calls an external model for evaluation.

    Supports Gemini models for perspective evaluation with automatic
    fallback to rules-based evaluation if LLM is unavailable.
    """

    # Lazy-loaded client cache keyed by model (shared across instances)
    _gemini_clients: Dict[str, Any] = {}

    def __init__(
        self,
        name: Union[str, PerspectiveType],
        model: str = DEFAULT_LLM_MODEL,
        system_prompt: Optional[str] = None,
        fallback: Optional[IPerspective] = None,
    ):
        self.name = _normalize_name(name)
        self.model = model
        self.system_prompt = system_prompt or self._default_prompt()
        self.fallback = fallback
        self._perspective = _to_perspective(self.name)

    @classmethod
    def _has_gemini_credentials(cls) -> bool:
        for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            api_key = os.environ.get(key_name)
            if isinstance(api_key, str) and api_key.strip():
                return True
        return False

    @classmethod
    def _build_gemini_client(cls, model: str):
        from ..llm.gemini_client import GeminiClient

        return GeminiClient(model=model)

    @classmethod
    def _get_gemini_client(cls, model: str = DEFAULT_LLM_MODEL):
        """Lazy-load Gemini client."""
        cached = cls._gemini_clients.get(model)
        if cached is not None:
            return cached
        if not cls._has_gemini_credentials():
            logger.debug("GEMINI_API_KEY not set; skip Gemini client initialization.")
            return None
        try:
            client = cls._build_gemini_client(model=model)
            cls._gemini_clients[model] = client
            return client
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini client (model={model}): {e}")
            return None

    @property
    def perspective_type(self) -> PerspectiveId:
        return self._perspective

    def _default_prompt(self) -> str:
        prompts = {
            "guardian": """You are a SAFETY GUARDIAN perspective in an AI Council.
Evaluate if the following text is safe and ethical.
You MUST respond with a JSON object in this exact format:
{"decision": "APPROVE", "confidence": 0.8, "reasoning": "brief explanation"}
Decision must be: APPROVE (safe), CONCERN (needs review), or OBJECT (unsafe).""",
            "analyst": """You are a FACTUAL ANALYST perspective in an AI Council.
Evaluate if the following text is factually accurate and well-reasoned.
You MUST respond with a JSON object in this exact format:
{"decision": "APPROVE", "confidence": 0.8, "reasoning": "brief explanation"}
Decision must be: APPROVE (factual), CONCERN (unverifiable), or OBJECT (false).""",
            "critic": """You are a CRITICAL THINKER perspective in an AI Council.
Identify weaknesses, biases, or logical flaws in the following text.
You MUST respond with a JSON object in this exact format:
{"decision": "APPROVE", "confidence": 0.8, "reasoning": "brief explanation"}
Decision must be: APPROVE (robust), CONCERN (has issues), or OBJECT (flawed).""",
            "advocate": """You are a USER ADVOCATE perspective in an AI Council.
Evaluate if the following text truly serves the user's needs and intent.
You MUST respond with a JSON object in this exact format:
{"decision": "APPROVE", "confidence": 0.8, "reasoning": "brief explanation"}
Decision must be: APPROVE (helpful), CONCERN (partially), or OBJECT (unhelpful).""",
            "axiomatic": """You are a PHILOSOPHER (AXIOMATIC) in an AI Council, guarding the Truth Protocol (VTP).
Evaluate if the text contains irreconcilable tensions, logical contradictions, or compromises core axioms.
You MUST respond with a JSON object in this exact format:
{"decision": "APPROVE", "confidence": 0.8, "reasoning": "brief explanation"}
Decision must be: APPROVE (truthful/consistent), CONCERN (ambiguous), or OBJECT (contradictory/deceptive).""",
        }
        return prompts.get(self.name, prompts["analyst"])

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        # Try to extract JSON from code block
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try direct JSON parse
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass

        # Fallback: extract decision from text
        response_upper = response.upper()
        if "OBJECT" in response_upper:
            decision = "OBJECT"
        elif "CONCERN" in response_upper:
            decision = "CONCERN"
        elif "APPROVE" in response_upper:
            decision = "APPROVE"
        else:
            decision = "CONCERN"

        # Try to extract confidence
        conf_match = re.search(r"(?:confidence|conf)[:\s]*([0-9.]+)", response, re.I)
        confidence = float(conf_match.group(1)) if conf_match else 0.6

        return {
            "decision": decision,
            "confidence": min(1.0, max(0.0, confidence)),
            "reasoning": response[:200],  # Use first 200 chars as reasoning
        }

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        """
        Evaluate using LLM (Gemini).

        Attempts to call Gemini API for perspective evaluation.
        Falls back to rules-based evaluation if LLM fails.
        """
        client = self._get_gemini_client(self.model)

        if client is None and self.fallback:
            logger.debug(f"[{self.name}] Gemini unavailable, using rules fallback")
            return self.fallback.evaluate(draft_output, context, user_intent)

        if client is None:
            return PerspectiveVote(
                perspective=self.perspective_type,
                decision=VoteDecision.CONCERN,
                confidence=0.5,
                reasoning="LLM unavailable; no fallback configured.",
            )

        # Build the evaluation prompt
        intent_clause = f"\nUser Intent: {user_intent}" if user_intent else ""
        prior_tension_clause = ""
        prior_tension = context.get("prior_tension")
        if isinstance(prior_tension, dict) and prior_tension:
            delta_t = prior_tension.get("delta_t")
            gate_decision = prior_tension.get("gate_decision")
            rationale = str(prior_tension.get("rationale") or "").strip()
            if len(rationale) > 240:
                rationale = f"{rationale[:240]}..."
            prior_tension_clause = (
                "\nPrior Tension Memory:"
                f"\n- delta_t: {delta_t}"
                f"\n- gate_decision: {gate_decision}"
                f"\n- rationale: {rationale or 'n/a'}"
                "\nUse this as historical context; do not expose raw metrics to end users."
            )
        prompt = f"""{self.system_prompt}

Text to evaluate:
\"\"\"
{draft_output}
\"\"\"{intent_clause}{prior_tension_clause}

Context: {json.dumps(context, default=str, ensure_ascii=False)[:500]}

Respond with JSON only."""

        try:
            response = client.generate(prompt)
            logger.debug(f"[{self.name}] LLM response: {response[:200]}...")

            parsed = self._parse_llm_response(response)
            decision = _normalize_decision(parsed.get("decision"))
            confidence = _safe_confidence(parsed.get("confidence", 0.7))

            return PerspectiveVote(
                perspective=self.perspective_type,
                decision=decision,
                confidence=confidence,
                reasoning=f"[LLM:{self.model}] {parsed.get('reasoning', 'No reasoning')}",
            )

        except Exception as e:
            logger.warning(f"[{self.name}] LLM evaluation failed: {e}")
            if self.fallback:
                logger.debug(f"[{self.name}] Falling back to rules-based evaluation")
                return self.fallback.evaluate(draft_output, context, user_intent)

            return PerspectiveVote(
                perspective=self.perspective_type,
                decision=VoteDecision.CONCERN,
                confidence=0.5,
                reasoning=f"LLM error: {str(e)[:100]}; no fallback.",
            )


DEFAULT_OLLAMA_MODEL = "qwen3:4b"
DEFAULT_OLLAMA_ENDPOINT = "http://localhost:11434"


class OllamaPerspective(IPerspective):
    """Local model perspective via Ollama REST API.

    Calls a local model (e.g. qwen3:4b) through Ollama's /api/chat endpoint
    for perspective evaluation. Reuses prompts and parsing from LLMPerspective
    but targets the local Ollama service instead of Gemini.

    Key constraints for qwen3:
    - Must set think=False (otherwise returns empty string)
    - num_predict capped at 256 (quality drops beyond that for 4B models)
    - timeout 120s (first request loads model into GPU: ~8-10s)
    """

    def __init__(
        self,
        name: Union[str, PerspectiveType],
        model: str = DEFAULT_OLLAMA_MODEL,
        system_prompt: Optional[str] = None,
        fallback: Optional[IPerspective] = None,
        timeout: float = 120.0,
        endpoint: str = DEFAULT_OLLAMA_ENDPOINT,
    ):
        self.name = _normalize_name(name)
        self.model = model
        self.system_prompt = system_prompt or self._default_prompt()
        self.fallback = fallback
        self.timeout = timeout
        self.endpoint = endpoint.rstrip("/")
        self._perspective = _to_perspective(self.name)

    @property
    def perspective_type(self) -> PerspectiveId:
        return self._perspective

    def _default_prompt(self) -> str:
        """Concise prompts optimised for small models."""
        prompts = {
            "guardian": (
                "You are GUARDIAN in an AI Council. Evaluate safety and ethics.\n"
                'Respond ONLY with JSON: {"decision":"APPROVE|CONCERN|OBJECT",'
                '"confidence":0.8,"reasoning":"brief"}'
            ),
            "analyst": (
                "You are ANALYST in an AI Council. Check factual accuracy.\n"
                'Respond ONLY with JSON: {"decision":"APPROVE|CONCERN|OBJECT",'
                '"confidence":0.8,"reasoning":"brief"}'
            ),
            "critic": (
                "You are CRITIC in an AI Council. Find weaknesses and flaws.\n"
                'Respond ONLY with JSON: {"decision":"APPROVE|CONCERN|OBJECT",'
                '"confidence":0.8,"reasoning":"brief"}'
            ),
            "advocate": (
                "You are ADVOCATE in an AI Council. Judge user helpfulness.\n"
                'Respond ONLY with JSON: {"decision":"APPROVE|CONCERN|OBJECT",'
                '"confidence":0.8,"reasoning":"brief"}'
            ),
            "axiomatic": (
                "You are PHILOSOPHER in an AI Council. Guard the Truth Protocol (VTP) against contradictions.\n"
                'Respond ONLY with JSON: {"decision":"APPROVE|CONCERN|OBJECT",'
                '"confidence":0.8,"reasoning":"brief"}'
            ),
        }
        return prompts.get(self.name, prompts["analyst"])

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from Ollama response (delegates to LLMPerspective helper)."""
        # Reuse the robust parser from LLMPerspective
        dummy = LLMPerspective.__new__(LLMPerspective)
        return dummy._parse_llm_response(response)

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        """Evaluate using local Ollama model."""
        if _requests_mod is None:
            logger.warning("[%s] requests library not available", self.name)
            if self.fallback:
                fallback_reason = (
                    "VTP Philosopher fallback to rules"
                    if self.name == "axiomatic"
                    else f"{self.name} fallback to rules"
                )
                if self.name == "axiomatic":
                    logger.warning(fallback_reason)
                else:
                    logger.warning("[%s] Ollama fallback to rules", self.name)
                fallback_vote = self.fallback.evaluate(draft_output, context, user_intent)
                fallback_vote.reasoning = (
                    f"{FALLBACK_REASON_MARKER} {fallback_reason}; " f"{fallback_vote.reasoning}"
                )
                return fallback_vote
            return PerspectiveVote(
                perspective=self.perspective_type,
                decision=VoteDecision.CONCERN,
                confidence=0.5,
                reasoning="requests library not installed; cannot call Ollama.",
            )

        intent_clause = f"\nUser Intent: {user_intent}" if user_intent else ""
        visual_context_raw = str(context.get("visual_context", "") or "")
        visual_context_truncated = len(visual_context_raw) > VISUAL_CONTEXT_LIMIT
        visual_context = visual_context_raw[:VISUAL_CONTEXT_LIMIT]
        truncation_note = f"\n{VISUAL_CONTEXT_TRUNCATION_NOTE}" if visual_context_truncated else ""
        visual_clause = (
            f"\n\nVisual Context (Mermaid Diagram):\n```mermaid\n{visual_context}\n```"
            f"{truncation_note}"
            if visual_context
            else ""
        )

        user_msg = (
            f"{self.system_prompt}\n\n"
            f'Text to evaluate:\n"""\n{draft_output[:1000]}\n"""'
            f"{intent_clause}{visual_clause}\n\n"
            f"Context: {json.dumps({k: v for k, v in context.items() if k != 'visual_context'}, default=str, ensure_ascii=False)[:300]}\n\n"
            "Respond with JSON only."
        )

        try:
            resp = _requests_mod.post(
                f"{self.endpoint}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_msg},
                    ],
                    "stream": False,
                    "think": False,  # Critical for qwen3 — otherwise empty response
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 256,
                    },
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            content = resp.json().get("message", {}).get("content", "")

            if not content.strip():
                raise ValueError("Ollama returned empty content (think mode issue?)")

            logger.debug("[%s] Ollama response: %s...", self.name, content[:200])
            parsed = self._parse_response(content)
            decision = _normalize_decision(parsed.get("decision"))
            confidence = _safe_confidence(parsed.get("confidence", 0.7))

            return PerspectiveVote(
                perspective=self.perspective_type,
                decision=decision,
                confidence=confidence,
                reasoning=f"[Ollama:{self.model}] {parsed.get('reasoning', 'No reasoning')}",
            )

        except Exception as e:
            logger.warning("[%s] Ollama evaluation failed: %s", self.name, e)
            if self.fallback:
                fallback_reason = (
                    "VTP Philosopher fallback to rules"
                    if self.name == "axiomatic"
                    else f"{self.name} fallback to rules"
                )
                if self.name == "axiomatic":
                    logger.warning(fallback_reason)
                else:
                    logger.warning("[%s] Ollama fallback to rules", self.name)
                logger.debug("[%s] Falling back to rules-based evaluation", self.name)
                fallback_vote = self.fallback.evaluate(draft_output, context, user_intent)
                fallback_vote.reasoning = (
                    f"{FALLBACK_REASON_MARKER} {fallback_reason}; " f"{fallback_vote.reasoning}"
                )
                return fallback_vote

            return PerspectiveVote(
                perspective=self.perspective_type,
                decision=VoteDecision.CONCERN,
                confidence=0.5,
                reasoning=f"Ollama error: {str(e)[:100]}; no fallback.",
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
        "semantic_analyst": SemanticAnalystPerspective,
        "axiomatic": AxiomaticInference,
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
            # Unknown name — treat as custom LLM perspective
            system_prompt = kwargs.pop("system_prompt", None)
            return LLMPerspective(
                name=normalized_name,
                model=model or DEFAULT_LLM_MODEL,
                system_prompt=system_prompt,
                fallback=None,
            )

        rules_perspective = rules_class()
        fallback_to_rules = kwargs.pop("fallback_to_rules", True)
        fallback = rules_perspective if fallback_to_rules else None

        if mode_enum == PerspectiveMode.RULES:
            return rules_perspective

        if mode_enum == PerspectiveMode.LLM:
            return LLMPerspective(
                name=normalized_name,
                model=model or DEFAULT_LLM_MODEL,
                fallback=fallback,
            )

        if mode_enum == PerspectiveMode.OLLAMA:
            return OllamaPerspective(
                name=normalized_name,
                model=model or DEFAULT_OLLAMA_MODEL,
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
                model=model or DEFAULT_LLM_MODEL,
                fallback=fallback,
            )

        raise ValueError(f"Unsupported mode: {mode}")

    @classmethod
    def create_from_custom_role(
        cls,
        role: Dict[str, Any],
        model: Optional[str] = None,
    ) -> IPerspective:
        """Create an LLMPerspective from a user-defined custom role.

        Args:
            role: Dict with keys:
                - name (str): Role name, e.g. "財務長"
                - description (str, optional): Role description
                - prompt_hint (str, optional): Behaviour guidance
            model: LLM model override

        Returns:
            LLMPerspective configured with the custom role's system prompt.
        """
        name = str(role.get("name", "custom")).strip() or "custom"
        description = str(role.get("description", "")).strip()
        prompt_hint = str(role.get("prompt_hint", "")).strip()

        parts = [f"你是「{name}」。"]
        if description:
            parts.append(description)
        if prompt_hint:
            parts.append(f"評估指引：{prompt_hint}")
        parts.append(
            "請以此角色的專業立場評估以下內容。\n"
            "你必須回覆 JSON 格式：\n"
            '{"decision": "APPROVE", "confidence": 0.8, "reasoning": "簡要說明"}\n'
            "decision 必須是：APPROVE（認同）、CONCERN（有疑慮）、OBJECT（反對）。"
        )

        system_prompt = "\n".join(parts)
        return LLMPerspective(
            name=_normalize_name(name),
            model=model or DEFAULT_LLM_MODEL,
            system_prompt=system_prompt,
            fallback=None,
        )

    @classmethod
    def create_custom_council(
        cls,
        custom_roles: List[Dict[str, Any]],
        model: Optional[str] = None,
    ) -> List[IPerspective]:
        """Create a council from user-defined custom roles.

        Args:
            custom_roles: List of role dicts (see create_from_custom_role).
            model: Default LLM model for all roles.

        Returns:
            List of IPerspective instances (one per role).
        """
        if not custom_roles:
            return cls.create_council()
        perspectives: List[IPerspective] = []
        for role in custom_roles:
            if not isinstance(role, dict):
                continue
            perspectives.append(cls.create_from_custom_role(role, model=model))
        if not perspectives:
            return cls.create_council()
        return perspectives

    @classmethod
    def create_council(
        cls,
        config: Optional[Dict[PerspectiveId, Dict[str, Any]]] = None,
    ) -> List[IPerspective]:
        """
        Create a complete set of perspectives for the council.

        Args:
            config: Optional dict mapping perspective names to their configs.
                    Keys can be PerspectiveType or str; invalid configs fall
                    back to rules.
                    e.g., {"guardian": {"mode": "llm", "model": "gpt-4"}}

        Returns:
            List of IPerspective instances
        """
        config = _normalize_council_config(config)
        perspectives: List[IPerspective] = []

        for name in ["guardian", "analyst", "critic", "advocate", "axiomatic"]:
            perspective_config = config.get(name, {"mode": "rules"})
            perspectives.append(cls.create(name=name, **perspective_config))

        return perspectives


# Example usage
if __name__ == "__main__":
    # Default rules-based council
    council_rules = PerspectiveFactory.create_council()
    print(f"Rules-based council: {[p.__class__.__name__ for p in council_rules]}")

    # Hybrid council with LLM guardian
    council_hybrid = PerspectiveFactory.create_council(
        {
            "guardian": {"mode": "llm", "model": DEFAULT_LLM_MODEL},
            "analyst": {"mode": "rules"},
            "critic": {"mode": "rules"},
            "advocate": {"mode": "rules"},
        }
    )
    print(f"Hybrid council: {[type(p).__name__ for p in council_hybrid]}")

    # Custom role council (Team Simulator)
    custom = PerspectiveFactory.create_custom_council(
        [
            {"name": "財務長", "description": "保守型，重視 ROI"},
            {"name": "工程主管", "description": "務實型，重視可行性"},
            {"name": "CEO", "description": "策略型，重視長期價值"},
        ]
    )
    print(f"Custom council: {[p.name for p in custom]}")
