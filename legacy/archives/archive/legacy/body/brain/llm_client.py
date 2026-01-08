import os
import json
import urllib.request
import urllib.error

class LLMClient:
    """
    A client for interacting with the Ollama and OpenAI APIs.
    Refactored to use standard library urllib for maximum environmental resilience.
    """
    def __init__(self, base_url="http://localhost:11434", provider="ollama", api_key=None):
        self.provider = provider
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.available_models = []
        if self.provider == "ollama":
            self._refresh_models()

    def _make_request(self, url: str, method: str = "GET", headers: dict = None, data: dict = None) -> dict:
        """Helper to make HTTP requests using urllib."""
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        request_data = None
        if data is not None:
            request_data = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                status = response.getcode()
                body = response.read().decode("utf-8")
                if status == 200:
                    return {"status": 200, "data": json.loads(body)}
                else:
                    return {"status": status, "error": body}
        except urllib.error.HTTPError as e:
            return {"status": e.code, "error": e.read().decode("utf-8")}
        except Exception as e:
            return {"status": 0, "error": str(e)}

    def _refresh_models(self):
        """Fetches the list of available models from Ollama."""
        result = self._make_request(f"{self.base_url}/api/tags")
        if result["status"] == 200:
            data = result["data"]
            self.available_models = [model['name'] for model in data.get('models', [])]
            print(f" [LLMClient] Connected to Local Brain. Models: {self.available_models}")
        else:
            print(f" [LLMClient] Failed to list models. Status: {result['status']}")

    def chat_complete(self, messages: list, model: str = "gemma3:4b") -> dict:
        """Sends a chat request. Supports 'ollama' and 'openai'."""
        if self.provider == "openai":
            if not self.api_key:
                return {"content": "Error: Missing API Key for Remote Brain.", "role": "system"}
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {"model": "gpt-4o-mini", "messages": messages}
            result = self._make_request("https://api.openai.com/v1/chat/completions", method="POST", headers=headers, data=payload)
            if result["status"] == 200:
                return result["data"]['choices'][0]['message']
            else:
                return {"content": f"Remote Error ({result['status']}): {result.get('error')}", "role": "system"}

        # Local Ollama Mode
        payload = {"model": model, "messages": messages, "stream": False}
        result = self._make_request(f"{self.base_url}/api/chat", method="POST", data=payload)
        if result["status"] == 200:
            return result["data"].get("message", {})
        else:
            return {"content": f"Error ({result['status']}): {result.get('error')}", "role": "system"}

    def generate(self, prompt: str, model: str = "gemma3:4b", system: str = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self.chat_complete(messages, model=model)
        return response.get("content", "")

    def generate_vision(self, prompt: str, image_path: str, model: str = "llava") -> str:
        import base64
        if not os.path.exists(image_path):
            return f"Error: Image not found at {image_path}"

        try:
            with open(image_path, "rb") as img_file:
                b64_image = base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            return f"Error encoding image: {e}"

        payload = {"model": model, "prompt": prompt, "images": [b64_image], "stream": False}
        result = self._make_request(f"{self.base_url}/api/generate", method="POST", data=payload)
        if result["status"] == 200:
            return result["data"].get("response", "")
        else:
            return f"Error ({result['status']}): {result.get('error')}"

    def get_embedding(self, text: str, model: str = "nomic-embed-text") -> list:
        payload = {"model": model, "prompt": text}
        result = self._make_request(f"{self.base_url}/api/embeddings", method="POST", data=payload)
        if result["status"] == 200:
            return result["data"].get("embedding", [])
        else:
            print(f" [LLMClient] Embedding failed ({result['status']}): {result.get('error')}")
            return []

# Singleton instance
llm_client = LLMClient()
