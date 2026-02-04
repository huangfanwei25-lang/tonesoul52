"""
ToneSoul LLM Module
Provides access to various LLM backends.
"""

from .gemini_client import GeminiClient, create_gemini_client, generate_narrative_reasoning
from .ollama_client import OllamaClient, create_ollama_client

__all__ = [
    "GeminiClient",
    "create_gemini_client",
    "generate_narrative_reasoning",
    # Ollama (local LLM)
    "OllamaClient",
    "create_ollama_client",
]
