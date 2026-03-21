"""
Multi-Model Perspective Registry

Inspired by OpenClaw's multi-agent architecture: different perspectives
use different LLM models to create genuine style diversity and productive
tension, avoiding the "clone problem" of uniform responses.

Usage:
    from tonesoul.council.model_registry import get_perspective_model, MULTI_MODEL_COUNCIL_CONFIG

    # Get model for specific perspective
    model = get_perspective_model("guardian")  # Returns "gemini-1.5-pro"

    # Use pre-built config with PerspectiveFactory
    perspectives = PerspectiveFactory.create_council(MULTI_MODEL_COUNCIL_CONFIG)
"""

from copy import deepcopy
from typing import Dict, Mapping, Optional

from .perspective_factory import DEFAULT_LLM_MODEL

# Default perspective-to-model mapping
# Key insight: Different models have different "personalities"
# - Pro models: More cautious, thorough analysis
# - Flash models: Quick, creative, sometimes more agreeable
# - Local models: Independent, different training data
PERSPECTIVE_MODEL_MAP: Dict[str, str] = {
    # Guardian: Use stable, cautious model for safety evaluation
    "guardian": "gemini-1.5-pro",
    # Analyst: Use fast model for factual analysis
    "analyst": DEFAULT_LLM_MODEL,
    # Critic: Use different model for genuine critical perspective
    # Falls back to flash if Ollama unavailable
    "critic": "gemini-1.5-flash",
    # Advocate: Use creative model for user advocacy
    "advocate": DEFAULT_LLM_MODEL,
    # Axiomatic: Use stable model for logical inference
    "axiomatic": "gemini-1.5-pro",
}

# Pre-built council configuration for multi-model setup
MULTI_MODEL_COUNCIL_CONFIG: Dict[str, Dict[str, str]] = {
    "guardian": {"mode": "llm", "model": PERSPECTIVE_MODEL_MAP["guardian"]},
    "analyst": {"mode": "llm", "model": PERSPECTIVE_MODEL_MAP["analyst"]},
    "critic": {"mode": "llm", "model": PERSPECTIVE_MODEL_MAP["critic"]},
    "advocate": {"mode": "llm", "model": PERSPECTIVE_MODEL_MAP["advocate"]},
    "axiomatic": {"mode": "rules"},  # Keep axiomatic as rules-based for determinism
}

# Hybrid configuration: Some LLM, some rules (cost-effective)
HYBRID_COUNCIL_CONFIG: Dict[str, Dict[str, str]] = {
    "guardian": {"mode": "llm", "model": DEFAULT_LLM_MODEL},  # Safety: LLM
    "analyst": {"mode": "rules"},  # Cost savings
    "critic": {"mode": "llm", "model": "gemini-1.5-flash"},  # Critical: LLM
    "advocate": {"mode": "rules"},  # Cost savings
    "axiomatic": {"mode": "rules"},  # Deterministic
}

# Full rules-based (no API costs, fastest)
RULES_ONLY_COUNCIL_CONFIG: Dict[str, Dict[str, str]] = {
    "guardian": {"mode": "rules"},
    "analyst": {"mode": "rules"},
    "critic": {"mode": "rules"},
    "advocate": {"mode": "rules"},
    "axiomatic": {"mode": "rules"},
}

# Local model configuration (Ollama + qwen3.5:4b)
# Strategy: Only Guardian and Critic use LLM — they produce the most
# meaningful divergence. Others stay rules-based for cost/speed.
LOCAL_COUNCIL_CONFIG: Dict[str, Dict[str, str]] = {
    "guardian": {"mode": "ollama", "model": "qwen3.5:4b"},
    "analyst": {"mode": "rules"},
    "critic": {"mode": "ollama", "model": "qwen3.5:4b"},
    "advocate": {"mode": "rules"},
    "axiomatic": {"mode": "ollama", "model": "qwen3.5:4b"},
}


def _normalize_name(value: object) -> str:
    return str(value).strip().lower()


def get_perspective_model(perspective_name: str) -> str:
    """Get the recommended model for a specific perspective."""
    return PERSPECTIVE_MODEL_MAP.get(_normalize_name(perspective_name), DEFAULT_LLM_MODEL)


def get_council_config(
    mode: str = "hybrid",
    custom_map: Optional[Mapping[str, str]] = None,
) -> Dict[str, Dict[str, str]]:
    """
    Get council configuration by mode.

    Args:
        mode: "full_llm", "hybrid", "rules", or "rules_only"
        custom_map: Optional custom perspective-to-model mapping

    Returns:
        Configuration dict for PerspectiveFactory.create_council()
    """
    normalized_mode = _normalize_name(mode)
    if normalized_mode == "full_llm":
        config = deepcopy(MULTI_MODEL_COUNCIL_CONFIG)
    elif normalized_mode in {"rules", "rules_only"}:
        config = deepcopy(RULES_ONLY_COUNCIL_CONFIG)
    elif normalized_mode == "local":
        config = deepcopy(LOCAL_COUNCIL_CONFIG)
    else:
        config = deepcopy(HYBRID_COUNCIL_CONFIG)

    # Apply custom overrides
    if custom_map:
        for perspective, model in custom_map.items():
            perspective_name = _normalize_name(perspective)
            if perspective_name in config:
                config[perspective_name] = {"mode": "llm", "model": model}

    return config


# Model characteristics documentation
MODEL_CHARACTERISTICS = {
    "gemini-1.5-pro": {
        "style": "thorough, cautious, balanced",
        "best_for": ["guardian", "axiomatic"],
        "cost": "medium",
        "speed": "slow",
    },
    "gemini-1.5-flash": {
        "style": "quick, creative, sometimes bold",
        "best_for": ["critic", "advocate"],
        "cost": "low",
        "speed": "fast",
    },
    "gemini-2.0-flash": {
        "style": "balanced, modern, efficient",
        "best_for": ["analyst", "advocate"],
        "cost": "low",
        "speed": "fast",
    },
    "qwen3.5:4b": {
        "style": "concise, independent, local-only",
        "best_for": ["guardian", "critic"],
        "cost": "free",
        "speed": "medium (32-37 tok/s)",
    },
}
