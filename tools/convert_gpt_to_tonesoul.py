#!/usr/bin/env python3
"""
ToneSoul GPT 轉換工具
====================
將 ChatGPT conversations.json 轉換為 ToneSoul 記憶格式。

使用方式:
    python convert_gpt_to_tonesoul.py --input ./conversations.json --output ./tonesoul_memories.json

依賴:
    pip install google-generativeai tqdm

環境變數:
    GEMINI_API_KEY=your_api_key
"""

from __future__ import annotations

import json
import os
import sys
import time
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# Ensure we can import from repository root when used as a tool.
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Optional tqdm
try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, **kwargs):
        return iterable


# Optional Gemini SDK (lazy import)
genai = None


def lazy_import_genai():
    global genai
    if genai is None:
        try:
            import google.generativeai as _genai

            genai = _genai
        except ImportError:
            print("請先安裝 google-generativeai：pip install google-generativeai")
            sys.exit(1)
    return genai


# ==================== 基本資料結構 ====================


@dataclass
class ConversationTurn:
    """單一訊息"""

    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float


@dataclass
class ParsedConversation:
    """解析後的對話"""

    id: str
    title: str
    create_time: float
    turns: List[ConversationTurn]


@dataclass
class ThreePersonaInsight:
    """三視角洞察"""

    philosopher: Dict[str, Any]
    engineer: Dict[str, Any]
    guardian: Dict[str, Any]


@dataclass
class ToneSoulMemory:
    """ToneSoul 記憶格式"""

    id: str
    conversationId: str
    createdAt: int
    timeLabel: str
    philosopher: Dict[str, Any]
    engineer: Dict[str, Any]
    guardian: Dict[str, Any]
    keywords: List[str]
    messageCount: int
    summary: str


# ==================== ChatGPT JSON 解析 ====================


class ChatGPTParser:
    """解析 ChatGPT conversations.json"""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self) -> List[ParsedConversation]:
        print(f"[convert] 載入檔案: {self.filepath}")
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        conversations: List[ParsedConversation] = []

        for conv_data in tqdm(data, desc="解析對話"):
            try:
                parsed = self._parse_conversation(conv_data)
                if parsed and len(parsed.turns) >= 2:
                    conversations.append(parsed)
            except Exception as e:
                print(f"[warn] 解析失敗: {e}")
                continue

        print(f"[convert] 解析完成，共 {len(conversations)} 筆")
        return conversations

    def _parse_conversation(self, conv_data: Dict[str, Any]) -> Optional[ParsedConversation]:
        conv_id = conv_data.get("id", conv_data.get("conversation_id", ""))
        title = conv_data.get("title", "untitled")
        create_time = conv_data.get("create_time", 0)

        mapping = conv_data.get("mapping", {})
        if not mapping:
            return None

        turns: List[ConversationTurn] = []

        for _, node_data in mapping.items():
            message = node_data.get("message")
            if not message:
                continue

            author = message.get("author", {})
            role = author.get("role", "")

            if role not in ["user", "assistant"]:
                continue

            content = message.get("content", {})
            parts = content.get("parts", [])

            text_parts: List[str] = []
            for part in parts:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])

            if not text_parts:
                continue

            text = "\n".join(text_parts).strip()
            if not text:
                continue

            timestamp = message.get("create_time", create_time) or create_time

            turns.append(
                ConversationTurn(
                    role=role,
                    content=text[:5000],
                    timestamp=timestamp or 0,
                )
            )

        turns.sort(key=lambda x: x.timestamp)

        return ParsedConversation(
            id=conv_id, title=title, create_time=create_time or 0, turns=turns
        )


# ==================== 三視角分析器 ====================


class ThreePersonaAnalyzer:
    """使用 Gemini API 進行三視角分析"""

    def __init__(self, api_key: str):
        genai_module = lazy_import_genai()
        genai_module.configure(api_key=api_key)
        self.model = genai_module.GenerativeModel("gemini-2.0-flash")
        self.request_count = 0
        self.last_request_time = 0.0

    def analyze_batch(self, conversations: List[ParsedConversation]) -> ThreePersonaInsight:
        summaries = []
        for conv in conversations:
            summary = self._summarize_conversation(conv)
            summaries.append(f"## {conv.title}\n{summary}")

        combined = "\n\n---\n\n".join(summaries)
        if len(combined) > 15000:
            combined = combined[:15000] + "\n\n[...truncated...]"

        prompt = self._build_analysis_prompt(combined)
        response = self._call_api(prompt)
        return self._parse_response(response)

    def _summarize_conversation(self, conv: ParsedConversation) -> str:
        lines = []
        for turn in conv.turns[:10]:
            prefix = "USER" if turn.role == "user" else "AI"
            content = turn.content[:200] + "..." if len(turn.content) > 200 else turn.content
            lines.append(f"{prefix}: {content}")
        return "\n".join(lines)

    def _build_analysis_prompt(self, content: str) -> str:
        return f"""
請根據以下對話摘要，輸出**有效 JSON**，用於 ToneSoul 的三視角記憶整理。

對話摘要：
{content}

請回傳以下結構（欄位可簡短）：
{{
  "philosopher": {{
    "coreTheme": "...",
    "values": ["...", "..."],
    "insight": "..."
  }},
  "engineer": {{
    "methods": ["...", "..."],
    "patterns": ["...", "..."],
    "insight": "..."
  }},
  "guardian": {{
    "risks": ["...", "..."],
    "blindSpots": ["...", "..."],
    "insight": "..."
  }},
  "keywords": ["...", "...", "..."],
  "summary": "..."
}}
"""

    def _call_api(self, prompt: str) -> str:
        self.request_count += 1
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self.last_request_time = time.time()

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json", "temperature": 0.3},
            )
            return response.text
        except Exception as e:
            print(f"[error] Gemini API 失敗: {e}")
            time.sleep(5)
            raise

    def _parse_response(self, response: str) -> ThreePersonaInsight:
        try:
            data = json.loads(response)
            return ThreePersonaInsight(
                philosopher=data.get("philosopher", {}),
                engineer=data.get("engineer", {}),
                guardian=data.get("guardian", {}),
            )
        except json.JSONDecodeError:
            return ThreePersonaInsight(
                philosopher={"insight": "解析失敗"},
                engineer={"insight": "解析失敗"},
                guardian={"insight": "解析失敗"},
            )


# ==================== 轉換流程 ====================


class GPTToToneSoulConverter:
    """GPT 轉 ToneSoul 記憶"""

    def __init__(self, api_key: str, batch_size: int = 5):
        self.analyzer = ThreePersonaAnalyzer(api_key)
        self.batch_size = batch_size
        self.checkpoint_file = ".conversion_checkpoint.json"

    def convert(self, conversations: List[ParsedConversation], output_path: str) -> None:
        processed_ids = self._load_checkpoint()
        memories: List[ToneSoulMemory] = []

        remaining = [c for c in conversations if c.id not in processed_ids]
        print(f"[convert] 待處理 {len(remaining)} / {len(conversations)}")

        batches = [
            remaining[i : i + self.batch_size] for i in range(0, len(remaining), self.batch_size)
        ]

        for batch_idx, batch in enumerate(tqdm(batches, desc="轉換中")):
            try:
                insight = self.analyzer.analyze_batch(batch)

                first_conv = batch[0]
                time_label = self._get_time_label(first_conv.create_time)

                memory = ToneSoulMemory(
                    id=f"memory_{hashlib.md5(first_conv.id.encode()).hexdigest()[:12]}",
                    conversationId=first_conv.id,
                    createdAt=(
                        int(first_conv.create_time * 1000)
                        if first_conv.create_time
                        else int(time.time() * 1000)
                    ),
                    timeLabel=time_label,
                    philosopher=insight.philosopher,
                    engineer=insight.engineer,
                    guardian=insight.guardian,
                    keywords=insight.philosopher.get("values", [])[:5],
                    messageCount=sum(len(c.turns) for c in batch),
                    summary=f"已處理 {len(batch)} 個對話",
                )
                memories.append(memory)

                for conv in batch:
                    processed_ids.add(conv.id)
                self._save_checkpoint(processed_ids)

                if batch_idx % 10 == 0:
                    self._save_memories(memories, output_path)

            except Exception as e:
                print(f"[error] 第 {batch_idx} 批失敗: {e}")
                continue

        self._save_memories(memories, output_path)
        print(f"[convert] 完成，共產生 {len(memories)} 筆")
        print(f"[convert] 輸出：{output_path}")

    def _get_time_label(self, timestamp: float) -> str:
        if not timestamp:
            return "unknown"
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m")
        except Exception:
            return "unknown"

    def _load_checkpoint(self) -> set:
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def _save_checkpoint(self, processed_ids: set) -> None:
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(list(processed_ids), f)

    def _save_memories(self, memories: List[ToneSoulMemory], output_path: str) -> None:
        output_data = [asdict(m) for m in memories]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)


# ==================== ToolResponse Wrapper ====================


def convert_tool_response(
    input_path: str,
    output_path: str = "tonesoul_memories.json",
    batch_size: int = 5,
    dry_run: bool = False,
    genesis=None,
) -> Dict[str, Any]:
    try:
        from memory.genesis import Genesis
        from tools.schema import ToolErrorCode, tool_error, tool_success
    except Exception as exc:
        return {
            "success": False,
            "data": None,
            "error": {"code": "E999", "message": str(exc)},
            "genesis": None,
            "responsibility_tier": None,
            "intent_id": None,
        }

    resolved_genesis = genesis or Genesis.AUTONOMOUS

    try:
        parser_obj = ChatGPTParser(input_path)
        conversations = parser_obj.parse()
    except Exception as exc:
        return tool_error(
            code=ToolErrorCode.INVALID_INPUT,
            message=str(exc),
            genesis=resolved_genesis,
        )

    if dry_run:
        return tool_success(
            data={
                "dry_run": True,
                "conversations": len(conversations),
                "output_path": output_path,
            },
            genesis=resolved_genesis,
            intent_id=None,
        )

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return tool_error(
            code=ToolErrorCode.MISSING_CREDENTIALS,
            message="Missing GEMINI_API_KEY.",
            genesis=resolved_genesis,
        )

    try:
        converter = GPTToToneSoulConverter(api_key, batch_size)
        converter.convert(conversations, output_path)
        return tool_success(
            data={
                "dry_run": False,
                "conversations": len(conversations),
                "output_path": output_path,
            },
            genesis=resolved_genesis,
            intent_id=None,
        )
    except Exception as exc:
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message=str(exc),
            genesis=resolved_genesis,
        )


def main():
    parser = argparse.ArgumentParser(description="ToneSoul GPT 轉換工具")
    parser.add_argument("--input", "-i", required=True, help="ChatGPT conversations.json 路徑")
    parser.add_argument(
        "--output",
        "-o",
        default="tonesoul_memories.json",
        help="輸出檔案路徑",
    )
    parser.add_argument("--batch-size", "-b", type=int, default=5, help="每批大小")
    parser.add_argument("--dry-run", action="store_true", help="只解析不呼叫 API")

    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key and not args.dry_run:
        print("缺少 GEMINI_API_KEY。")
        print("Windows: set GEMINI_API_KEY=your_key")
        print("Linux/Mac: export GEMINI_API_KEY=your_key")
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"找不到輸入檔案: {args.input}")
        sys.exit(1)

    parser_obj = ChatGPTParser(args.input)
    conversations = parser_obj.parse()

    if args.dry_run:
        print("\n[dry-run] 預估結果")
        print(f"  對話數: {len(conversations)}")
        print(f"  訊息總數: {sum(len(c.turns) for c in conversations)}")
        print(f"  預估批次: {len(conversations) // args.batch_size + 1}")
        return

    converter = GPTToToneSoulConverter(api_key, args.batch_size)
    converter.convert(conversations, args.output)


if __name__ == "__main__":
    main()
