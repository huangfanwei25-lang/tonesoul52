"""
ToneSoul Ollama Client
Connects to local Ollama service for LLM inference.
"""

import requests
from typing import List, Dict, Optional


class OllamaClient:
    """Wrapper for Ollama local LLM service."""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama service URL (default: http://localhost:11434)
            model: Model to use (default: qwen2.5:7b, fallback: gemma3:4b)
        """
        self.host = host.rstrip("/")
        self.model = model
        self._available_models = None
    
    def is_available(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []
    
    def _ensure_model(self) -> str:
        """Ensure model is available, fallback to alternatives."""
        if self._available_models is None:
            self._available_models = self.list_models()
        
        # Check if preferred model is available
        if any(self.model in m for m in self._available_models):
            return self.model
        
        # Fallback order: qwen > gemma > llama > mistral > any
        fallbacks = ["qwen", "gemma", "llama", "mistral"]
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
        model = self._ensure_model()
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"(Ollama error: {response.status_code})"
        except requests.exceptions.Timeout:
            return "(Ollama 回應超時，請稍後再試)"
        except Exception as e:
            return f"(Ollama 連接失敗: {e})"
    
    def chat(self, messages: List[Dict], system: Optional[str] = None) -> str:
        """
        Multi-turn chat.
        
        Args:
            messages: List of {role, content} dicts
            system: Optional system prompt
        """
        model = self._ensure_model()
        
        # Convert to Ollama format
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
            "stream": False,
        }
        
        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                return f"(Ollama error: {response.status_code})"
        except requests.exceptions.Timeout:
            return "(Ollama 回應超時，請稍後再試)"
        except Exception as e:
            return f"(Ollama 連接失敗: {e})"


def create_ollama_client(model: Optional[str] = None) -> OllamaClient:
    """Factory function to create an Ollama client."""
    return OllamaClient(model=model or "qwen2.5:7b")
