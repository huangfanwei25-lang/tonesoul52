"""
ToneSoul Gemini Client
Connects to Google Gemini API for chat and one-shot generation.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional


def _load_genai():
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "Missing dependency: google-generativeai. Install with: pip install google-generativeai"
        ) from exc
    return genai


def _resolve_api_key(api_key: Optional[str] = None) -> Optional[str]:
    candidates = [
        api_key,
        os.environ.get("GEMINI_API_KEY"),
        os.environ.get("GOOGLE_API_KEY"),
    ]
    for candidate in candidates:
        if isinstance(candidate, str):
            cleaned = candidate.strip()
            if cleaned:
                return cleaned
    return None


class GeminiClient:
    """Wrapper for Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        self.api_key = _resolve_api_key(api_key)
        if not self.api_key:
            raise ValueError(
                "Missing Gemini API key. Set GEMINI_API_KEY or GOOGLE_API_KEY, "
                "or pass api_key explicitly."
            )

        genai = _load_genai()
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self.chat = None

    def start_chat(self, history: Optional[List[Dict]] = None):
        """Start a new chat session."""
        formatted_history = []
        if history:
            for msg in history:
                role = "user" if msg.get("role") == "user" else "model"
                formatted_history.append({"role": role, "parts": [msg.get("content", "")]})
        self.chat = self.model.start_chat(history=formatted_history)
        return self

    def send_message(self, message: str) -> str:
        """Send a message and return text response."""
        if self.chat is None:
            self.start_chat()
        response = self.chat.send_message(message)
        return response.text

    def generate(self, prompt: str) -> str:
        """Generate a one-shot response (no chat history)."""
        response = self.model.generate_content(prompt)
        return response.text


def create_gemini_client(api_key: Optional[str] = None) -> GeminiClient:
    """Factory function to create a Gemini client."""
    return GeminiClient(api_key=api_key)


def _build_narrative_reasoning_prompt(verdict_dict: dict) -> str:
    verdict = verdict_dict.get("verdict", "unknown")
    coherence = int(verdict_dict.get("coherence", {}).get("overall", 0.5) * 100)
    votes = (
        ", ".join([f"{v['perspective']}: {v['decision']}" for v in verdict_dict.get("votes", [])])
        or "[資料不足]"
    )
    divergence = verdict_dict.get("divergence_analysis", {}).get("core_divergence", "none")

    return f"""You are a bounded council dossier summarizer.

Goal function:
- Success = preserve the final verdict, coherence, visible vote pattern, and core divergence in 2-3 concise Chinese sentences without inventing hidden chain-of-thought.

Priority:
- P0: do not fabricate hidden reasoning or omit visible disagreement signals.
- P1: keep verdict, coherence, votes, and divergence aligned with the provided evidence.
- P2: keep the wording concise and replay-safe.

If any field is missing or weakly supported, mark [資料不足] instead of guessing.

Available evidence:
- final_verdict: {verdict}
- coherence_score: {coherence}%
- votes: {votes}
- core_divergence: {divergence}

Output spec:
- Chinese only
- 2-3 sentences
- bounded replay-safe summary, not hidden reasoning transcript
"""


def generate_narrative_reasoning(client: GeminiClient, verdict_dict: dict) -> str:
    """Generate narrative inner reasoning from Council verdict."""
    prompt = _build_narrative_reasoning_prompt(verdict_dict)

    try:
        return client.generate(prompt)
    except Exception as exc:
        return f"(narrative_reasoning_generation_failed: {exc})"
