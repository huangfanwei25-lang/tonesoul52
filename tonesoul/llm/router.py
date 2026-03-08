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

import time
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

    @property
    def last_metrics(self) -> Any:
        """Expose the last usage metrics emitted by the active client, if any."""
        if self._cached_client is None:
            return None
        return getattr(self._cached_client, "last_metrics", None)

    @staticmethod
    def _deadline(timeout_seconds: float) -> float:
        return time.perf_counter() + max(0.1, float(timeout_seconds))

    @staticmethod
    def _remaining_seconds(deadline: float) -> float:
        return max(0.0, float(deadline) - time.perf_counter())

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

    def inference_check(self, timeout_seconds: float = 10.0) -> Dict[str, Any]:
        """Run a bounded inference-readiness probe for the active backend."""
        started = time.perf_counter()
        deadline = self._deadline(timeout_seconds)
        client = self.get_client()
        backend = self.active_backend
        selection_latency_ms = int(round((time.perf_counter() - started) * 1000))
        if client is None:
            return {
                "ok": False,
                "supported": False,
                "backend": backend,
                "reason": "no_client",
                "latency_ms": selection_latency_ms,
                "selection_latency_ms": selection_latency_ms,
                "timeout_seconds": float(timeout_seconds),
            }

        model = getattr(client, "model", None)
        if model is not None and not isinstance(model, (str, int, float, bool)):
            model = getattr(model, "model_name", None) or type(model).__name__
        probe = getattr(client, "probe_completion", None)
        if not callable(probe):
            return {
                "ok": True,
                "supported": False,
                "backend": backend,
                "model": model,
                "reason": "probe_unsupported",
                "latency_ms": selection_latency_ms,
                "selection_latency_ms": selection_latency_ms,
                "timeout_seconds": float(timeout_seconds),
            }

        remaining_timeout = self._remaining_seconds(deadline)
        if remaining_timeout < 0.02:
            return {
                "ok": False,
                "supported": True,
                "backend": backend,
                "model": model,
                "reason": "timeout",
                "latency_ms": selection_latency_ms,
                "selection_latency_ms": selection_latency_ms,
                "timeout_seconds": float(timeout_seconds),
            }

        try:
            result = probe(timeout_seconds=float(remaining_timeout))
        except Exception as exc:
            total_latency_ms = int(round((time.perf_counter() - started) * 1000))
            return {
                "ok": False,
                "supported": True,
                "backend": backend,
                "model": model,
                "reason": f"probe_exception:{exc.__class__.__name__}",
                "detail": str(exc),
                "latency_ms": total_latency_ms,
                "selection_latency_ms": selection_latency_ms,
                "timeout_seconds": float(timeout_seconds),
            }

        normalized = dict(result) if isinstance(result, dict) else {"ok": False}
        probe_latency_ms = normalized.get("latency_ms")
        if isinstance(probe_latency_ms, (int, float)):
            normalized["probe_latency_ms"] = int(probe_latency_ms)
            normalized["latency_ms"] = selection_latency_ms + int(probe_latency_ms)
        else:
            normalized["latency_ms"] = int(round((time.perf_counter() - started) * 1000))
        normalized.setdefault("ok", False)
        normalized.setdefault("supported", True)
        normalized.setdefault("backend", backend)
        normalized.setdefault("model", model)
        normalized["selection_latency_ms"] = selection_latency_ms
        normalized["timeout_seconds"] = float(timeout_seconds)
        return normalized

    def reset(self) -> None:
        """Clear cached client, forcing re-resolution on next get_client() call."""
        self._cached_client = None
        self._cached_backend = None
