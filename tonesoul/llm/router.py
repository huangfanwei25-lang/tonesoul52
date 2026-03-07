"""
ToneSoul LLM Router — unified backend selection with waterfall fallback.

This module provides a single entry point for obtaining an LLM client,
abstracting away the complexity of multiple backends (Ollama, LM Studio,
Gemini) behind a simple interface.

Usage:
    from tonesoul.llm.router import LLMRouter

    router = LLMRouter()
    client = router.get_client()        # Returns best available client
    health = router.health_check()      # {"ollama": True, "lmstudio": False, "gemini": True}

Author: Antigravity
Date: 2026-03-07
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class LLMRouter:
    """
    Unified LLM backend router with waterfall fallback.

    Supports:
      - "gemini"   → Cloud (Google Gemini)
      - "ollama"   → Local (Ollama)
      - "lmstudio" → Local (LM Studio, OpenAI-compatible)
      - "auto"     → Ollama → LMStudio → Gemini (default)
    """

    def __init__(self, preferred_backend: str = "auto") -> None:
        self._preferred = preferred_backend.strip().lower()
        self._cached_client: Any = None
        self._cached_backend: Optional[str] = None

    @property
    def active_backend(self) -> Optional[str]:
        """Name of the currently active backend, or None if not yet resolved."""
        return self._cached_backend

    def get_client(self) -> Any:
        """
        Get the best available LLM client.

        Uses GovernanceKernel for routing if available, otherwise
        falls back to direct resolution.

        Returns:
            An LLM client instance, or None if all backends are unavailable.
        """
        if self._cached_client is not None:
            return self._cached_client

        try:
            from tonesoul.governance.kernel import GovernanceKernel

            kernel = GovernanceKernel()
            decision = kernel.resolve_llm_backend(preferred_backend=self._preferred)
            self._cached_client = decision.client
            self._cached_backend = decision.backend
        except Exception:
            # Fallback if GovernanceKernel is unavailable
            self._cached_client = self._direct_resolve()

        return self._cached_client

    def _direct_resolve(self) -> Any:
        """Direct resolution without GovernanceKernel (fallback path)."""
        backends = {
            "ollama": self._try_ollama,
            "lmstudio": self._try_lmstudio,
            "gemini": self._try_gemini,
        }

        if self._preferred in backends:
            client = backends[self._preferred]()
            if client is not None:
                self._cached_backend = self._preferred
                return client

        # Auto: try all in order
        for name, factory in backends.items():
            client = factory()
            if client is not None:
                self._cached_backend = name
                return client

        return None

    @staticmethod
    def _try_ollama() -> Any:
        try:
            from tonesoul.llm.ollama_client import create_ollama_client

            client = create_ollama_client()
            if client.is_available() and client.list_models():
                return client
        except Exception:
            pass
        return None

    @staticmethod
    def _try_lmstudio() -> Any:
        try:
            from tonesoul.llm.lmstudio_client import create_lmstudio_client

            client = create_lmstudio_client()
            if client.is_available():
                return client
        except Exception:
            pass
        return None

    @staticmethod
    def _try_gemini() -> Any:
        try:
            from tonesoul.llm.gemini_client import create_gemini_client

            return create_gemini_client()
        except Exception:
            pass
        return None

    def health_check(self) -> Dict[str, bool]:
        """Check which backends are currently available."""
        return {
            "ollama": self._try_ollama() is not None,
            "lmstudio": self._try_lmstudio() is not None,
            "gemini": self._try_gemini() is not None,
        }

    def reset(self) -> None:
        """Clear cached client, forcing re-resolution on next get_client() call."""
        self._cached_client = None
        self._cached_backend = None
