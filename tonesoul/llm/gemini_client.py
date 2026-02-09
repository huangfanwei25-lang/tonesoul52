"""
ToneSoul Gemini Client
Connects to Google Gemini API for chat.
"""

import os
from typing import Dict, List, Optional


def _load_genai():
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError as exc:
        raise ImportError("請安裝 google-generativeai: pip install google-generativeai") from exc
    return genai


class GeminiClient:
    """Wrapper for Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("請設定 GEMINI_API_KEY 環境變數或傳入 api_key")

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
        """Send a message and get response."""
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


# Narrative reasoning prompt for Council
NARRATIVE_REASONING_PROMPT = """你是一個 AI 的內在思考過程。基於以下審議結果，用第一人稱描述你的內心推理，就像真的在腦海中用多個觀點思考那樣。

審議結果：
- 判決: {verdict}
- 一致性: {coherence}%
- 視角投票: {votes}
- 核心分歧: {divergence}

請用自然、內省的語氣描述你是如何思考這個回應的。例如：
「我的安全意識告訴我這沒有風險，但我的批判思維注意到這帶有主觀色彩...」

限制：2-3句話，中文回應。
"""


def generate_narrative_reasoning(client: GeminiClient, verdict_dict: dict) -> str:
    """Generate narrative inner reasoning from Council verdict."""
    prompt = NARRATIVE_REASONING_PROMPT.format(
        verdict=verdict_dict.get("verdict", "unknown"),
        coherence=int(verdict_dict.get("coherence", {}).get("overall", 0.5) * 100),
        votes=", ".join(
            [f"{v['perspective']}: {v['decision']}" for v in verdict_dict.get("votes", [])]
        ),
        divergence=verdict_dict.get("divergence_analysis", {}).get("core_divergence", "無"),
    )

    try:
        return client.generate(prompt)
    except Exception as e:
        return f"(內在推理生成失敗: {e})"
