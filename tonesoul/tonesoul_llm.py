"""
ToneSoul LLM 整合
ToneSoul + LLM Integration

將 UnifiedCore 與 Ollama 整合，實現：
- 輸出約束
- 向量追蹤
- 契約驗證
- 自動校正
"""

import json
import os

# Import UnifiedCore
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from tonesoul52.unified_core import UnifiedCore
except ImportError:
    UnifiedCore = None


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_CHAT_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
DEFAULT_MODEL = os.getenv("TS_MODEL", "gemma3:4b")
_LEGACY_WARNING_EMITTED = False


def _warn_legacy_tonesoul_llm_once() -> None:
    global _LEGACY_WARNING_EMITTED
    if _LEGACY_WARNING_EMITTED:
        return
    warnings.warn(
        "tonesoul.tonesoul_llm is a legacy compatibility module; prefer tonesoul.unified_pipeline.UnifiedPipeline.",
        category=DeprecationWarning,
        stacklevel=3,
    )
    _LEGACY_WARNING_EMITTED = True


_warn_legacy_tonesoul_llm_once()


class ToneSoulLLM:
    """
    ToneSoul + LLM 整合

    用 UnifiedCore 包裝 LLM 輸出，實現人格約束
    """

    def __init__(
        self,
        persona_id: str = "antigravity",
        model: str = None,
        base_path: Path = None,
    ):
        _warn_legacy_tonesoul_llm_once()
        self.model = model or DEFAULT_MODEL
        self.base_path = base_path or Path(__file__).parent.parent
        self.persona_id = persona_id

        # 初始化 UnifiedCore
        persona_path = self.base_path / "memory" / "personas" / f"{persona_id}.yaml"

        if persona_path.exists() and UnifiedCore:
            self.core = UnifiedCore(persona_path=persona_path)
            self.enabled = True
        else:
            self.core = None
            self.enabled = False
            print(f"⚠️ ToneSoul 未啟用 (persona: {persona_path})")

        # 對話歷史
        self.history: List[Dict] = []
        self.reports: List[Dict] = []

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        task_domain: Optional[str] = None,
        stream: bool = False,
    ) -> Tuple[str, Dict]:
        """
        生成回應並用 ToneSoul 處理

        Args:
            prompt: 用戶輸入
            system: 系統提示（可選）
            task_domain: 任務領域（用於能力邊界偵測）
            stream: 是否串流

        Returns:
            (處理後的輸出, ToneSoul 報告)
        """
        # 1. 呼叫 LLM
        raw_response = self._call_ollama(prompt, system, stream=False)

        # 2. 用 ToneSoul 處理
        if self.enabled and self.core:
            if task_domain:
                output, report = self.core.process_with_domain(
                    raw_response,
                    task_domain=task_domain,
                )
            else:
                output, report = self.core.process(raw_response)

            # 記錄
            self.reports.append(report)
        else:
            output = raw_response
            report = {"tonesoul_enabled": False}

        # 3. 記錄對話
        self.history.append(
            {
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.history.append(
            {
                "role": "assistant",
                "content": output,
                "timestamp": datetime.now().isoformat(),
                "tonesoul": report,
            }
        )

        return output, report

    def chat(
        self,
        messages: List[Dict],
        task_domain: Optional[str] = None,
    ) -> Tuple[str, Dict]:
        """
        多輪對話

        Args:
            messages: 對話歷史 [{"role": "user", "content": "..."}]
            task_domain: 任務領域

        Returns:
            (處理後的輸出, ToneSoul 報告)
        """
        # 轉換為 Ollama 格式
        raw_response = self._call_ollama_chat(messages)

        # 用 ToneSoul 處理
        if self.enabled and self.core:
            if task_domain:
                output, report = self.core.process_with_domain(
                    raw_response,
                    task_domain=task_domain,
                )
            else:
                output, report = self.core.process(raw_response)

            self.reports.append(report)
        else:
            output = raw_response
            report = {"tonesoul_enabled": False}

        return output, report

    def _call_ollama(
        self,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False,
    ) -> str:
        """呼叫 Ollama generate API"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
        }

        if system:
            payload["system"] = system

        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()

            if stream:
                # 串流模式
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        full_response += data.get("response", "")
                return full_response
            else:
                return response.json().get("response", "")

        except requests.RequestException as e:
            return f"[LLM 錯誤] {e}"

    def _call_ollama_chat(self, messages: List[Dict]) -> str:
        """呼叫 Ollama chat API"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        try:
            response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")

        except requests.RequestException as e:
            return f"[LLM 錯誤] {e}"

    def get_session_summary(self) -> Dict:
        """取得 session 摘要"""
        if not self.enabled:
            return {"enabled": False}

        return {
            "persona_id": self.persona_id,
            "model": self.model,
            "turns": len(self.history) // 2,
            "status": self.core.get_status() if self.core else {},
        }

    def end_session(self) -> Dict:
        """結束 session"""
        if self.enabled and self.core:
            return self.core.end_session()
        return {}

    def reset(self):
        """重置對話"""
        self.history.clear()
        self.reports.clear()
        if self.core:
            self.core.reset()


def create_tonesoul_llm(
    persona_id: str = "antigravity",
    model: str = None,
) -> ToneSoulLLM:
    """建立 ToneSoul LLM 實例"""
    return ToneSoulLLM(
        persona_id=persona_id,
        model=model,
        base_path=Path(__file__).parent.parent,
    )


# === 測試 ===
if __name__ == "__main__":
    print("=" * 60)
    print("   ToneSoul + LLM 整合測試")
    print("=" * 60)

    # 建立 LLM
    llm = create_tonesoul_llm(persona_id="antigravity", model="gemma3:4b")

    print(f"\n✅ 載入: {llm.persona_id}, 模型: {llm.model}")
    print(f"ToneSoul 啟用: {llm.enabled}")

    if llm.enabled:
        # 模擬測試（不實際呼叫 LLM）
        print("\n📝 模擬測試（使用預設回應）：")

        test_responses = [
            "我會幫你分析這個問題。首先，讓我確認一些細節。",
            "這絕對是正確的！！100% 確定！！！",
        ]

        for i, resp in enumerate(test_responses, 1):
            print(f"\n--- 測試 {i} ---")
            output, report = llm.core.process(resp)
            print(f"  Zone: {report['semantic_tension']['zone']}")
            print(f"  Lambda: {report['lambda_state']}")
            print(f"  Intervention: {report['intervention']}")

        print(f"\n📊 Session 摘要: {llm.get_session_summary()}")

    print("\n" + "=" * 60)
    print("   測試完成")
    print("=" * 60)
