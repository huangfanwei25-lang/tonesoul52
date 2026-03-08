"""
ToneSoul LM Studio Client
Connects to LM Studio's OpenAI-compatible local server for LLM inference.
Provides the same interface as OllamaClient for seamless pipeline integration.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional

import requests

from tonesoul.observability.token_meter import TokenMeter
from tonesoul.schemas import LLMCallMetrics


class LMStudioError(Exception):
    """Raised when LM Studio returns an error or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class LMStudioClient:
    """Wrapper for LM Studio's OpenAI-compatible local API."""

    def __init__(
        self,
        host: str = "http://localhost:1234",
        model: str | None = None,
        meter: TokenMeter | None = None,
    ):
        """
        Initialize LM Studio client.

        Args:
            host: LM Studio server URL (default: http://localhost:1234)
            model: Model to use (default: auto-detect from server)
            meter: Optional token meter for usage recording
        """
        self.host = host.rstrip("/")
        self.model = model
        self._chat_history: List[Dict] = []
        self._meter = meter
        self.last_metrics: LLMCallMetrics | None = None

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
        usage = payload.get("usage")
        if not isinstance(usage, dict):
            self.last_metrics = None
            return

        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")
        if not isinstance(prompt_tokens, int) or not isinstance(completion_tokens, int):
            self.last_metrics = None
            return
        if not isinstance(total_tokens, int):
            total_tokens = prompt_tokens + completion_tokens

        metrics = LLMCallMetrics(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )
        self.last_metrics = metrics
        if self._meter is not None:
            self._meter.record(
                model=model,
                prompt_tokens=metrics.prompt_tokens,
                completion_tokens=metrics.completion_tokens,
            )

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
            model = self._get_model(timeout_seconds=self._remaining_seconds(deadline))
        except TimeoutError:
            return {
                "ok": False,
                "supported": True,
                "backend": "lmstudio",
                "model": self.model,
                "reason": "timeout",
                "latency_ms": int(round((time.perf_counter() - started) * 1000)),
            }
        except LMStudioError as exc:
            return {
                "ok": False,
                "supported": True,
                "backend": "lmstudio",
                "model": self.model,
                "reason": "model_resolution_error",
                "detail": str(exc),
                "latency_ms": int(round((time.perf_counter() - started) * 1000)),
            }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 32,
            "temperature": 0.0,
            "stream": False,
        }
        try:
            response = requests.post(
                f"{self.host}/v1/chat/completions",
                json=payload,
                timeout=self._request_timeout(deadline),
            )
            latency_ms = int(round((time.perf_counter() - started) * 1000))
            if response.status_code != 200:
                return {
                    "ok": False,
                    "supported": True,
                    "backend": "lmstudio",
                    "model": model,
                    "reason": f"http_{response.status_code}",
                    "latency_ms": latency_ms,
                }
            data = response.json()
            choices = data.get("choices")
            message = (
                choices[0]["message"]["content"] if isinstance(choices, list) and choices else ""
            )
            text = str(message or "").strip()
            return {
                "ok": bool(text),
                "supported": True,
                "backend": "lmstudio",
                "model": model,
                "reason": "ready" if text else "empty_response",
                "latency_ms": latency_ms,
                "usage_available": isinstance(data.get("usage"), dict),
            }
        except requests.exceptions.Timeout:
            return {
                "ok": False,
                "supported": True,
                "backend": "lmstudio",
                "model": model,
                "reason": "timeout",
                "latency_ms": int(round((time.perf_counter() - started) * 1000)),
            }
        except TimeoutError:
            return {
                "ok": False,
                "supported": True,
                "backend": "lmstudio",
                "model": model,
                "reason": "timeout",
                "latency_ms": int(round((time.perf_counter() - started) * 1000)),
            }
        except requests.exceptions.RequestException as exc:
            return {
                "ok": False,
                "supported": True,
                "backend": "lmstudio",
                "model": model,
                "reason": "request_error",
                "detail": str(exc),
                "latency_ms": int(round((time.perf_counter() - started) * 1000)),
            }

    def is_available(self) -> bool:
        """Check if LM Studio server is running."""
        try:
            deadline = self._deadline(2.0)
            response = requests.get(
                f"{self.host}/v1/models",
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
                f"{self.host}/v1/models",
                timeout=self._request_timeout(deadline),
            )
            if response.status_code == 200:
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            pass
        return []

    def _get_model(self, timeout_seconds: float = 5.0) -> str:
        """Get the model ID to use. Auto-detects if not set."""
        if self.model:
            return self.model
        if max(0.0, float(timeout_seconds)) < 0.02:
            raise TimeoutError("probe_deadline_exhausted")
        models = self.list_models(timeout_seconds=timeout_seconds)
        # Filter out embedding models
        chat_models = [m for m in models if "embed" not in m.lower()]
        if chat_models:
            self.model = chat_models[0]
            return self.model
        if models:
            self.model = models[0]
            return self.model
        raise LMStudioError("No models loaded in LM Studio")

    def start_chat(self, history: Optional[List[Dict]] = None):
        """Start a new chat session (GeminiClient/OllamaClient compatible)."""
        self._chat_history = history or []
        return self

    def send_message(self, message: str) -> str:
        """Send a message and get response (GeminiClient/OllamaClient compatible)."""
        self._chat_history.append({"role": "user", "content": message})
        response = self.chat(self._chat_history)
        self._chat_history.append({"role": "assistant", "content": response})
        return response

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate a one-shot response."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages)

    def chat(self, messages: List[Dict], system: Optional[str] = None) -> str:
        """
        Multi-turn chat via OpenAI-compatible API.

        Args:
            messages: List of {role, content} dicts
            system: Optional system prompt
        """
        model = self._get_model()

        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted_messages.append({"role": role, "content": content})

        payload = {
            "model": model,
            "messages": formatted_messages,
            "max_tokens": 512,
            "temperature": 0.7,
            "stream": False,
        }

        try:
            response = requests.post(
                f"{self.host}/v1/chat/completions",
                json=payload,
                timeout=120,
            )

            if response.status_code == 200:
                data = response.json()
                self._record_usage(model, data)
                return data["choices"][0]["message"]["content"]
            else:
                raise LMStudioError(
                    f"LM Studio HTTP {response.status_code}: {response.text[:200]}",
                    status_code=response.status_code,
                )
        except LMStudioError:
            raise
        except requests.exceptions.Timeout:
            raise LMStudioError("LM Studio 回應超時")
        except requests.exceptions.RequestException as e:
            raise LMStudioError(f"LM Studio 連接失敗: {e}")


def create_lmstudio_client(
    model: Optional[str] = None,
    meter: TokenMeter | None = None,
) -> LMStudioClient:
    """Factory function to create an LM Studio client."""
    return LMStudioClient(model=model, meter=meter)
