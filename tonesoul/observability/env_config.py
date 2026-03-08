"""Centralized environment variable loader with graceful fallbacks.

Loads from .env if present (via python-dotenv), then falls back to
safe defaults so that CI environments work without real credentials.

Usage:
    from tonesoul.observability.env_config import load_env, get_env
    load_env()  # Call once at startup
    api_key = get_env("GEMINI_API_KEY", default="mock")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv as _dotenv_load
except ImportError:
    _dotenv_load = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Default values (safe for CI — no real API calls)
# ---------------------------------------------------------------------------

_DEFAULTS: dict[str, str] = {
    # LLM
    "OLLAMA_HOST": "http://localhost:11434",
    "OLLAMA_MODEL": "gemma3:4b",
    "GEMINI_API_KEY": "",
    "LLM_FALLBACK_MODE": "local",
    # Moltbook
    "MOLTBOOK_API_KEY": "",
    "MOLTBOOK_API_URL": "https://www.moltbook.com/api/v1",
    # Budget
    "DAILY_TOKEN_BUDGET_USD": "5.00",
    # Observability
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "json",
    # Database
    "SOUL_DB_PATH": "data/soul.db",
    "AUDIT_DB_PATH": "data/audit.db",
}

_loaded = False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_env(env_path: Optional[Path] = None) -> None:
    """Load environment variables from .env file if it exists.

    Falls back to defaults for any variable not set.
    Safe to call multiple times (idempotent).
    """
    global _loaded
    if _loaded:
        return
    _loaded = True

    if env_path is None:
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"

    if _dotenv_load and env_path.exists():
        _dotenv_load(dotenv_path=str(env_path), override=False)


def get_env(key: str, *, default: Optional[str] = None) -> str:
    """Get an environment variable with fallback chain.

    Priority: OS env var > .env file > _DEFAULTS > default arg > ""

    Args:
        key: Environment variable name.
        default: Override default if not in _DEFAULTS.

    Returns:
        The resolved value (never None).
    """
    load_env()  # ensure .env is loaded
    value = os.environ.get(key)
    if value is not None:
        return value
    if key in _DEFAULTS:
        return _DEFAULTS[key]
    if default is not None:
        return default
    return ""


def is_ci() -> bool:
    """Detect if running in a CI environment."""
    ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI", "TRAVIS"]
    return any(os.environ.get(v) for v in ci_vars)


def is_mock_mode() -> bool:
    """Detect if we should use mock LLM (no real API keys available)."""
    return not get_env("GEMINI_API_KEY") and not get_env("OLLAMA_HOST")


def get_all_config() -> dict[str, str]:
    """Return all resolved configuration values (for debugging)."""
    load_env()
    result = {}
    for key in _DEFAULTS:
        result[key] = get_env(key)
    return result
