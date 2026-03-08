import logging

import requests

logger = logging.getLogger(__name__)


def ask_local_llm(
    prompt: str,
    system: str = "你是 ToneSoul 的前線代理，請給予簡潔有禮貌的回應。",
    model: str = "qwen3.5:4b",
) -> str:
    """呼叫本地 Qwen3.5 模型。

    用於處理低張力、短小且免費用戶的訊息。
    重要限制：必須使用 chat API + think=False，否則 qwen3.5 會把額度全花在思考而回傳空字串。
    """
    # Guard: truncate excessively long prompts to protect 4B model context window
    MAX_PROMPT_LEN = 2000
    if len(prompt) > MAX_PROMPT_LEN:
        prompt = prompt[:MAX_PROMPT_LEN]

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.6,
                    "num_predict": 256,
                },
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "").strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Local LLM fallback failed: {e}")
        return "[系統提示] 抱歉，本機運算單元暫時無法服務，請稍後再試。"
    except Exception as e:
        logger.error(f"Local LLM unexpected error: {e}")
        return "[系統提示] 本機運算單元發生未知錯誤。"
