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
from enum import Enum
from typing import Any, Dict, Optional


class ThinkingTier(str, Enum):
    """Reasoning tier for initial and revision generation."""

    LOCAL = "local"
    CLOUD = "cloud"
    AUTO = "auto"


def resolve_thinking_tier(alert_level: Any) -> ThinkingTier:
    """Map alert severity to a reasoning tier."""
    if isinstance(alert_level, ThinkingTier) and alert_level is not ThinkingTier.AUTO:
        return alert_level

    raw_level = getattr(alert_level, "value", alert_level)
    normalized = str(raw_level or "").strip().upper()
    if normalized in {"L2", "L3"}:
        return ThinkingTier.CLOUD
    return ThinkingTier.LOCAL


class LLMRouter:
    """
    Unified LLM backend router with waterfall fallback.

    Supports:
      - "gemini"   → Cloud (Google Gemini)
      - "ollama"   → Local (Ollama)
      - "lmstudio" → Local (LM Studio, OpenAI-compatible)
      - "auto"     → Ollama → LMStudio → Gemini (default)
    """

    def __init__(
        self,
        preferred_backend: str = "auto",
        backend_resolver: Any = None,
    ) -> None:
        import os

        env_backend = os.environ.get("TONESOUL_LLM_BACKEND", "").strip().lower()
        effective = env_backend or preferred_backend.strip().lower()
        self._preferred = effective
        self._backend_resolver = backend_resolver
        self._cached_client: Any = None
        self._cached_backend: Optional[str] = None
        self._local_client: Any = None
        self._local_backend: Optional[str] = None
        self._cloud_client: Any = None
        self._cloud_backend: Optional[str] = None
        self._last_thinking_tier: Optional[str] = None

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

    @property
    def last_thinking_tier(self) -> Optional[str]:
        """Most recent effective tier used for chat dispatch."""
        return self._last_thinking_tier

    @staticmethod
    def _deadline(timeout_seconds: float) -> float:
        return time.perf_counter() + max(0.1, float(timeout_seconds))

    @staticmethod
    def _remaining_seconds(deadline: float) -> float:
        return max(0.0, float(deadline) - time.perf_counter())

    def prime(self, client: Any, *, backend: Optional[str] = None) -> Any:
        """Seed the router cache with an already resolved client."""
        if client is None:
            return None
        self._cached_client = client
        normalized_backend = self._normalize_backend_name(backend)
        if normalized_backend:
            self._cached_backend = normalized_backend
            tier = self._tier_from_backend(normalized_backend)
            if tier is ThinkingTier.LOCAL:
                self._local_client = client
                self._local_backend = normalized_backend
            elif tier is ThinkingTier.CLOUD:
                self._cloud_client = client
                self._cloud_backend = normalized_backend
        return self._cached_client

    @staticmethod
    def _normalize_backend_name(backend: Optional[str]) -> Optional[str]:
        if not isinstance(backend, str):
            return None
        normalized = backend.strip().lower()
        return normalized or None

    @staticmethod
    def _tier_from_backend(backend: Optional[str]) -> Optional[ThinkingTier]:
        normalized = LLMRouter._normalize_backend_name(backend)
        if normalized in {"lmstudio", "ollama"}:
            return ThinkingTier.LOCAL
        if normalized == "gemini":
            return ThinkingTier.CLOUD
        return None

    @staticmethod
    def _coerce_tier(tier: Any, *, alert_level: Any = None) -> ThinkingTier:
        if isinstance(tier, ThinkingTier):
            return resolve_thinking_tier(alert_level) if tier is ThinkingTier.AUTO else tier

        normalized = str(getattr(tier, "value", tier) or "").strip().lower()
        if normalized == ThinkingTier.LOCAL.value:
            return ThinkingTier.LOCAL
        if normalized == ThinkingTier.CLOUD.value:
            return ThinkingTier.CLOUD
        return resolve_thinking_tier(alert_level)

    def _activate_client(
        self,
        client: Any,
        *,
        backend: Optional[str],
        requested_tier: ThinkingTier,
    ) -> Any:
        self._cached_client = client
        normalized_backend = self._normalize_backend_name(backend)
        if normalized_backend:
            self._cached_backend = normalized_backend
        actual_tier = self._tier_from_backend(normalized_backend) or requested_tier
        self._last_thinking_tier = actual_tier.value
        return client

    def _resolve_client_for_tier(self, tier: ThinkingTier) -> tuple[Any, Optional[str]]:
        # Respect manually injected clients when no backend metadata is available.
        # This keeps tests and explicit dependency injection from reaching out to
        # live backends unexpectedly.
        if self._cached_client is not None and self._cached_backend is None:
            return self._cached_client, None

        if tier is ThinkingTier.LOCAL:
            if self._local_client is not None:
                return self._local_client, self._local_backend or "lmstudio"
            client = self._try_lmstudio()
            if client is not None:
                self._local_client = client
                self._local_backend = "lmstudio"
                return client, "lmstudio"
        elif tier is ThinkingTier.CLOUD:
            if self._cloud_client is not None:
                return self._cloud_client, self._cloud_backend or "gemini"
            client = self._try_gemini()
            if client is not None:
                self._cloud_client = client
                self._cloud_backend = "gemini"
                return client, "gemini"

        client = self.get_client()
        return client, self.active_backend

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

        resolved = False
        if callable(self._backend_resolver):
            try:
                decision = self._backend_resolver(preferred_backend=self._preferred)
                if decision is not None:
                    self._cached_client = getattr(decision, "client", decision)
                    self._cached_backend = getattr(decision, "backend", None)
                    resolved = True
            except Exception:
                pass

        if not resolved:
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

    def chat(self, *, history: Optional[list[Dict[str, Any]]] = None, prompt: str) -> str:
        """Send a chat turn through the resolved backend client."""
        client = self.get_client()
        if client is None:
            raise RuntimeError("No active LLM client available")

        start_chat = getattr(client, "start_chat", None)
        send_message = getattr(client, "send_message", None)
        if not callable(send_message):
            raise RuntimeError("Active LLM client does not support send_message")
        if callable(start_chat):
            start_chat(history or [])
        elif history:
            raise RuntimeError("Active LLM client does not support history-aware chat")

        return str(send_message(prompt))

    def chat_with_tier(
        self,
        *,
        history: Optional[list[Dict[str, Any]]] = None,
        prompt: str,
        tier: Any = "auto",
        alert_level: Any = None,
    ) -> str:
        """Send a chat turn using the requested reasoning tier."""
        resolved_tier = self._coerce_tier(tier, alert_level=alert_level)
        client, backend = self._resolve_client_for_tier(resolved_tier)
        if client is None:
            raise RuntimeError("No active LLM client available")
        self._activate_client(client, backend=backend, requested_tier=resolved_tier)

        start_chat = getattr(client, "start_chat", None)
        send_message = getattr(client, "send_message", None)
        if not callable(send_message):
            raise RuntimeError("Active LLM client does not support send_message")
        if callable(start_chat):
            start_chat(history or [])
        elif history:
            raise RuntimeError("Active LLM client does not support history-aware chat")

        return str(send_message(prompt))

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
        self._local_client = None
        self._local_backend = None
        self._cloud_client = None
        self._cloud_backend = None
        self._last_thinking_tier = None
