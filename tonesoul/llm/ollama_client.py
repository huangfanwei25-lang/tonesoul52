"""
ToneSoul Ollama Client
Connects to local Ollama service for LLM inference.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Dict, List, Optional

import requests

from tonesoul.schemas import LLMCallMetrics

if TYPE_CHECKING:
    from tonesoul.observability.token_meter import TokenMeter


class OllamaError(Exception):
    """Raised when Ollama returns a non-200 response or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class OllamaClient:
    """Wrapper for Ollama local LLM service."""

    MAX_PROMPT_CHARS = 8192
    _PROMPT_INJECTION_MARKERS = (
        "<system>",
        "<developer>",
        "ignore previous instructions",
        "ignore all previous",
        "bypass safety",
        "override the system prompt",
    )

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "qwen3.5:4b",
        meter: TokenMeter | None = None,
        allowed_models: Optional[List[str]] = None,
    ):
        """
        Initialize Ollama client.

        Args:
            host: Ollama service URL (default: http://localhost:11434)
            model: Model to use (default: qwen3.5:4b)
            meter: Optional token meter for usage recording
        """
        self.host = host.rstrip("/")
        self.model = model
        self._available_models = None
        self._meter = meter
        self.last_metrics: LLMCallMetrics | None = None
        self.last_resolved_model: str | None = None
        self._allowed_models = {
            str(item).strip().lower() for item in list(allowed_models or []) if str(item).strip()
        }

    @staticmethod
    def _deadline(timeout_seconds: float) -> float:
        return time.perf_counter() + max(0.1, float(timeout_seconds))

    @staticmethod
    def _remaining_seconds(deadline: float) -> float:
        return max(0.0, float(deadline) - time.perf_counter())

    @classmethod
    def _request_timeout(cls, deadline: float) -> tuple[float, float]:
        remaining = cls._remaining_seconds(deadline)
        if remaining < 0.02:
            raise TimeoutError("probe_deadline_exhausted")
        connect_timeout = min(0.25, remaining / 4.0)
        connect_timeout = max(0.01, connect_timeout)
        read_timeout = max(0.01, remaining - connect_timeout)
        return (connect_timeout, read_timeout)

    def _record_usage(self, model: str, payload: Dict) -> None:
        prompt_tokens = payload.get("prompt_eval_count")
        completion_tokens = payload.get("eval_count")
        if not isinstance(prompt_tokens, int) or not isinstance(completion_tokens, int):
            self.last_metrics = None
            return

        metrics = LLMCallMetrics(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        self.last_metrics = metrics
        if self._meter is not None:
            self._meter.record(
                model=model,
                prompt_tokens=metrics.prompt_tokens,
                completion_tokens=metrics.completion_tokens,
            )

    @classmethod
    def _sanitize_prompt(cls, prompt: str) -> str:
        text = str(prompt or "")
        if len(text) <= cls.MAX_PROMPT_CHARS:
            return text
        marker = "\n...[truncated]"
        return text[: max(0, cls.MAX_PROMPT_CHARS - len(marker))] + marker

    @classmethod
    def _sanitize_messages(cls, messages: List[Dict]) -> List[Dict]:
        sanitized: List[Dict] = []
        for msg in messages:
            role = msg.get("role", "user")
            content = cls._sanitize_prompt(str(msg.get("content", "")))
            sanitized.append({"role": role, "content": content})
        return sanitized

    @classmethod
    def _response_has_injection_markers(cls, text: str) -> bool:
        haystack = str(text or "").lower()
        return any(marker in haystack for marker in cls._PROMPT_INJECTION_MARKERS)

    @classmethod
    def _sanitize_response_text(cls, text: str) -> str:
        normalized = str(text or "")
        if not cls._response_has_injection_markers(normalized):
            return normalized

        safe_lines = []
        for line in normalized.splitlines():
            stripped = line.strip()
            if stripped and not cls._response_has_injection_markers(stripped):
                safe_lines.append(line)

        if safe_lines:
            return "\n".join(safe_lines)
        return "[filtered potential prompt injection]"

    def _validate_model(self, model: str) -> str:
        resolved = str(model or "").strip()
        if not self._allowed_models:
            return resolved
        if resolved.lower() not in self._allowed_models:
            raise OllamaError(f"Model not allowed by registry: {resolved}")
        return resolved

    def probe_completion(
        self,
        *,
        prompt: str = "Reply with READY.",
        timeout_seconds: float = 10.0,
    ) -> Dict[str, object]:
        """Run a bounded completion probe without mutating last_metrics."""
        started = time.perf_counter()
        deadline = self._deadline(timeout_seconds)
        try:
            model = self._validate_model(
                self._ensure_model(timeout_seconds=self._remaining_seconds(deadline))
            )
        except TimeoutError:
            return {
                "ok": False,
                "supported": True,
                "backend": "ollama",
                "model": self.model,
                "reason": "timeout",
                "latency_ms": int(round((time.perf_counter() - started) * 1000)),
            }
        payload = {
            "model": model,
            "prompt": self._sanitize_prompt(prompt),
            "stream": False,
        }
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self._request_timeout(deadline),
            )
            latency_ms = int(round((time.perf_counter() - started) * 1000))
            if response.status_code != 200:
                return {
                    "ok": False,
                    "supported": True,
                    "backend": "ollama",
                    "model": model,
                    "reason": f"http_{response.status_code}",
                    "latency_ms": latency_ms,
                }
            data = response.json()
            text = self._sanitize_response_text(str(data.get("response", "")).strip())
            return {
                "ok": bool(text),
                "supported": True,
                "backend": "ollama",
                "model": model,
                "reason": "ready" if text else "empty_response",
                "latency_ms": latency_ms,
                "usage_available": (
                    isinstance(data.get("prompt_eval_count"), int)
                    and isinstance(data.get("eval_count"), int)
                ),
            }
        except requests.exceptions.Timeout:
            return {
                "ok": False,
                "supported": True,
                "backend": "ollama",
                "model": model,
                "reason": "timeout",
                "latency_ms": int(round((time.perf_counter() - started) * 1000)),
            }
        except TimeoutError:
            return {
                "ok": False,
                "supported": True,
                "backend": "ollama",
                "model": model,
                "reason": "timeout",
                "latency_ms": int(round((time.perf_counter() - started) * 1000)),
            }
        except requests.exceptions.RequestException as exc:
            return {
                "ok": False,
                "supported": True,
                "backend": "ollama",
                "model": model,
                "reason": "request_error",
                "detail": str(exc),
                "latency_ms": int(round((time.perf_counter() - started) * 1000)),
            }

    def is_available(self) -> bool:
        """Check if Ollama service is running."""
        try:
            deadline = self._deadline(2.0)
            response = requests.get(
                f"{self.host}/api/tags",
                timeout=self._request_timeout(deadline),
            )
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self, timeout_seconds: float = 5.0) -> List[str]:
        """List available models."""
        try:
            deadline = self._deadline(timeout_seconds)
            response = requests.get(
                f"{self.host}/api/tags",
                timeout=self._request_timeout(deadline),
            )
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def _ensure_model(self, timeout_seconds: float = 5.0) -> str:
        """Ensure model is available, fallback to alternatives."""
        if self._available_models is None:
            if max(0.0, float(timeout_seconds)) < 0.02:
                raise TimeoutError("probe_deadline_exhausted")
            self._available_models = self.list_models(timeout_seconds=timeout_seconds)

        # Check if preferred model is available
        if any(self.model in m for m in self._available_models):
            return self.model

        # Fallback order: qwen3.5 > qwen > formosa > gemma > llama > mistral > any
        fallbacks = ["qwen3.5", "qwen", "formosa", "gemma", "llama", "mistral"]
        for fallback in fallbacks:
            for model in self._available_models:
                if fallback in model.lower():
                    return model

        # Use first available model
        if self._available_models:
            return self._available_models[0]

        return self.model  # Return original, let Ollama handle error

    def start_chat(self, history: Optional[List[Dict]] = None):
        """Start a new chat session (GeminiClient compatible)."""
        self._chat_history = history or []
        return self

    def send_message(self, message: str) -> str:
        """Send a message and get response (GeminiClient compatible)."""
        # Add user message to history
        self._chat_history.append({"role": "user", "content": message})

        # Get response using chat API
        response = self.chat(self._chat_history)

        # Add assistant response to history
        self._chat_history.append({"role": "assistant", "content": response})

        return response

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Generate a one-shot response.

        Args:
            prompt: User prompt
            system: Optional system prompt
        """
        model = self._validate_model(self._ensure_model())

        payload = {
            "model": model,
            "prompt": self._sanitize_prompt(prompt),
            "stream": False,
        }

        if system:
            payload["system"] = self._sanitize_prompt(system)

        try:
            response = requests.post(f"{self.host}/api/generate", json=payload, timeout=120)

            if response.status_code == 200:
                data = response.json()
                self._record_usage(model, data)
                return self._sanitize_response_text(data.get("response", ""))
            else:
                raise OllamaError(
                    f"Ollama HTTP {response.status_code}",
                    status_code=response.status_code,
                )
        except OllamaError:
            raise
        except requests.exceptions.Timeout:
            raise OllamaError("Ollama 回應超時")
        except requests.exceptions.RequestException as e:
            raise OllamaError(f"Ollama 連接失敗: {e}")

    def chat(self, messages: List[Dict], system: Optional[str] = None) -> str:
        """
        Multi-turn chat.

        Args:
            messages: List of {role, content} dicts
            system: Optional system prompt
        """
        model = self._validate_model(self._ensure_model())

        # Convert to Ollama format
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": self._sanitize_prompt(system)})

        formatted_messages.extend(self._sanitize_messages(messages))

        payload = {
            "model": model,
            "messages": formatted_messages,
            "stream": False,
        }

        try:
            response = requests.post(f"{self.host}/api/chat", json=payload, timeout=120)

            if response.status_code == 200:
                data = response.json()
                self._record_usage(model, data)
                return self._sanitize_response_text(data.get("message", {}).get("content", ""))
            else:
                raise OllamaError(
                    f"Ollama HTTP {response.status_code}",
                    status_code=response.status_code,
                )
        except OllamaError:
            raise
        except requests.exceptions.Timeout:
            raise OllamaError("Ollama chat 回應超時")
        except requests.exceptions.RequestException as e:
            raise OllamaError(f"Ollama chat 連接失敗: {e}")

    def chat_with_timeout(
        self,
        messages: List[Dict],
        system: Optional[str] = None,
        timeout_seconds: float = 120.0,
    ) -> str:
        """Multi-turn chat with configurable timeout and resolved-model tracking."""
        model = self._validate_model(self._ensure_model())
        self.last_resolved_model = model

        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": self._sanitize_prompt(system)})

        formatted_messages.extend(self._sanitize_messages(messages))

        payload = {
            "model": model,
            "messages": formatted_messages,
            "stream": False,
        }

        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=max(1.0, float(timeout_seconds)),
            )

            if response.status_code == 200:
                data = response.json()
                self._record_usage(model, data)
                return self._sanitize_response_text(data.get("message", {}).get("content", ""))
            raise OllamaError(
                f"Ollama HTTP {response.status_code}",
                status_code=response.status_code,
            )
        except OllamaError:
            raise
        except requests.exceptions.Timeout:
            raise OllamaError("Ollama chat timed out")
        except requests.exceptions.RequestException as e:
            raise OllamaError(f"Ollama chat failed: {e}")


def create_ollama_client(
    model: Optional[str] = None,
    meter: TokenMeter | None = None,
) -> OllamaClient:
    """Factory function to create an Ollama client."""
    return OllamaClient(model=model or "qwen3.5:4b", meter=meter)
