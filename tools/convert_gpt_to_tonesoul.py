#!/usr/bin/env python3
"""
ToneSoul GPT 語場轉換工具
========================
將 ChatGPT 導出的 conversations.json 轉換為 ToneSoul 記憶格式

使用方式:
    python convert_gpt_to_tonesoul.py --input ./conversations.json --output ./tonesoul_memories.json

需要:
    pip install google-generativeai tqdm
    
環境變數:
    GEMINI_API_KEY=your_api_key
"""

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

# 嘗試導入 tqdm
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

# 嘗試導入 Gemini SDK (dry-run 模式不需要)
genai = None
def lazy_import_genai():
    global genai
    if genai is None:
        try:
            import google.generativeai as _genai
            genai = _genai
        except ImportError:
            print("請先安裝 google-generativeai: pip install google-generativeai")
            sys.exit(1)
    return genai


# ==================== 數據結構 ====================

@dataclass
class ConversationTurn:
    """單輪對話"""
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


# ==================== ChatGPT JSON 解析器 ====================

class ChatGPTParser:
    """解析 ChatGPT 導出的 conversations.json"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def parse(self) -> List[ParsedConversation]:
        """解析 JSON 文件"""
        print(f"📂 正在解析: {self.filepath}")
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conversations = []
        
        for conv_data in tqdm(data, desc="解析對話"):
            try:
                parsed = self._parse_conversation(conv_data)
                if parsed and len(parsed.turns) >= 2:  # 至少要有一問一答
                    conversations.append(parsed)
            except Exception as e:
                print(f"⚠️ 解析失敗: {e}")
                continue
        
        print(f"✅ 成功解析 {len(conversations)} 個對話")
        return conversations
    
    def _parse_conversation(self, conv_data: Dict) -> Optional[ParsedConversation]:
        """解析單個對話"""
        conv_id = conv_data.get('id', conv_data.get('conversation_id', ''))
        title = conv_data.get('title', '無標題')
        create_time = conv_data.get('create_time', 0)
        
        # 解析訊息樹
        mapping = conv_data.get('mapping', {})
        if not mapping:
            return None
        
        turns = []
        
        for node_id, node_data in mapping.items():
            message = node_data.get('message')
            if not message:
                continue
            
            author = message.get('author', {})
            role = author.get('role', '')
            
            if role not in ['user', 'assistant']:
                continue
            
            content = message.get('content', {})
            parts = content.get('parts', [])
            
            # 提取文字內容
            text_parts = []
            for part in parts:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and 'text' in part:
                    text_parts.append(part['text'])
            
            if not text_parts:
                continue
            
            text = '\n'.join(text_parts)
            if not text.strip():
                continue
            
            timestamp = message.get('create_time', create_time) or create_time
            
            turns.append(ConversationTurn(
                role=role,
                content=text[:5000],  # 限制長度
                timestamp=timestamp or 0
            ))
        
        # 按時間排序
        turns.sort(key=lambda x: x.timestamp)
        
        return ParsedConversation(
            id=conv_id,
            title=title,
            create_time=create_time or 0,
            turns=turns
        )


# ==================== 三視角分析器 ====================

class ThreePersonaAnalyzer:
    """使用 Gemini API 進行三視角分析"""
    
    def __init__(self, api_key: str):
        genai_module = lazy_import_genai()
        genai_module.configure(api_key=api_key)
        self.model = genai_module.GenerativeModel('gemini-2.0-flash')
        self.request_count = 0
        self.last_request_time = 0
        
    def analyze_batch(self, conversations: List[ParsedConversation]) -> ThreePersonaInsight:
        """分析一批對話"""
        # 準備對話摘要
        summaries = []
        for conv in conversations:
            summary = self._summarize_conversation(conv)
            summaries.append(f"【{conv.title}】\n{summary}")
        
        combined = "\n\n---\n\n".join(summaries)
        
        # 限制輸入長度
        if len(combined) > 15000:
            combined = combined[:15000] + "\n\n[...截斷...]"
        
        # 呼叫 API
        prompt = self._build_analysis_prompt(combined)
        response = self._call_api(prompt)
        
        return self._parse_response(response)
    
    def _summarize_conversation(self, conv: ParsedConversation) -> str:
        """摘要單個對話"""
        lines = []
        for turn in conv.turns[:10]:  # 只取前 10 輪
            prefix = "👤 用戶" if turn.role == 'user' else "🤖 AI"
            content = turn.content[:200] + "..." if len(turn.content) > 200 else turn.content
            lines.append(f"{prefix}: {content}")
        return "\n".join(lines)
    
    def _build_analysis_prompt(self, content: str) -> str:
        """構建分析 Prompt"""
        return f"""
你是 ToneSoul 的三視角分析系統。請分析以下對話記錄，從三個角度提取洞察：

【對話記錄】:
{content}

請輸出 JSON 格式的三視角分析（繁體中文）:
{{
  "philosopher": {{
    "coreTheme": "這批對話的核心主題是什麼？",
    "values": ["涉及的價值觀1", "價值觀2"],
    "insight": "哲學層面的深度洞察（2-3句）"
  }},
  "engineer": {{
    "methods": ["可重用的方法論或工具1", "工具2"],
    "patterns": ["發現的模式1", "模式2"],
    "insight": "實用層面的洞察（2-3句）"
  }},
  "guardian": {{
    "risks": ["潛在風險1", "風險2"],
    "blindSpots": ["盲點1", "盲點2"],
    "insight": "守護層面的提醒（2-3句）"
  }},
  "keywords": ["關鍵詞1", "關鍵詞2", "關鍵詞3"],
  "summary": "一句話綜合摘要"
}}

請只輸出 JSON，不要有其他文字。
"""
    
    def _call_api(self, prompt: str) -> str:
        """呼叫 Gemini API（帶速率限制）"""
        # 速率限制：每分鐘不超過 60 次
        self.request_count += 1
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0:  # 至少間隔 1 秒
            time.sleep(1.0 - elapsed)
        
        self.last_request_time = time.time()
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.3
                }
            )
            return response.text
        except Exception as e:
            print(f"⚠️ API 錯誤: {e}")
            time.sleep(5)  # 錯誤時等待 5 秒
            raise
    
    def _parse_response(self, response: str) -> ThreePersonaInsight:
        """解析 API 回應"""
        try:
            data = json.loads(response)
            return ThreePersonaInsight(
                philosopher=data.get('philosopher', {}),
                engineer=data.get('engineer', {}),
                guardian=data.get('guardian', {})
            )
        except json.JSONDecodeError:
            return ThreePersonaInsight(
                philosopher={"insight": "解析失敗"},
                engineer={"insight": "解析失敗"},
                guardian={"insight": "解析失敗"}
            )


# ==================== 轉換器 ====================

class GPTToToneSoulConverter:
    """GPT 語場轉 ToneSoul 記憶"""
    
    def __init__(self, api_key: str, batch_size: int = 5):
        self.analyzer = ThreePersonaAnalyzer(api_key)
        self.batch_size = batch_size
        self.checkpoint_file = ".conversion_checkpoint.json"
        
    def convert(self, conversations: List[ParsedConversation], output_path: str) -> None:
        """執行轉換"""
        # 載入檢查點
        processed_ids = self._load_checkpoint()
        memories: List[ToneSoulMemory] = []
        
        # 過濾已處理的對話
        remaining = [c for c in conversations if c.id not in processed_ids]
        print(f"📊 待處理: {len(remaining)} / {len(conversations)} 個對話")
        
        # 分批處理
        batches = [remaining[i:i+self.batch_size] for i in range(0, len(remaining), self.batch_size)]
        
        for batch_idx, batch in enumerate(tqdm(batches, desc="轉換進度")):
            try:
                # 分析這批對話
                insight = self.analyzer.analyze_batch(batch)
                
                # 取第一個對話的時間作為時間標籤
                first_conv = batch[0]
                time_label = self._get_time_label(first_conv.create_time)
                
                # 創建記憶
                memory = ToneSoulMemory(
                    id=f"memory_{hashlib.md5(first_conv.id.encode()).hexdigest()[:12]}",
                    conversationId=first_conv.id,
                    createdAt=int(first_conv.create_time * 1000) if first_conv.create_time else int(time.time() * 1000),
                    timeLabel=time_label,
                    philosopher=insight.philosopher,
                    engineer=insight.engineer,
                    guardian=insight.guardian,
                    keywords=insight.philosopher.get('values', [])[:5],
                    messageCount=sum(len(c.turns) for c in batch),
                    summary=f"批次包含 {len(batch)} 個對話"
                )
                memories.append(memory)
                
                # 更新檢查點
                for conv in batch:
                    processed_ids.add(conv.id)
                self._save_checkpoint(processed_ids)
                
                # 每 10 批保存一次
                if batch_idx % 10 == 0:
                    self._save_memories(memories, output_path)
                    
            except Exception as e:
                print(f"\n⚠️ 批次 {batch_idx} 處理失敗: {e}")
                continue
        
        # 最終保存
        self._save_memories(memories, output_path)
        print(f"\n✅ 轉換完成！生成 {len(memories)} 條記憶")
        print(f"📁 輸出: {output_path}")
    
    def _get_time_label(self, timestamp: float) -> str:
        """生成時間標籤"""
        if not timestamp:
            return "未知時間"
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y年%m月")
        except:
            return "未知時間"
    
    def _load_checkpoint(self) -> set:
        """載入檢查點"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def _save_checkpoint(self, processed_ids: set) -> None:
        """保存檢查點"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(list(processed_ids), f)
    
    def _save_memories(self, memories: List[ToneSoulMemory], output_path: str) -> None:
        """保存記憶"""
        output_data = [asdict(m) for m in memories]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)


# ==================== 主程式 ====================

def main():
    parser = argparse.ArgumentParser(description='ToneSoul GPT 語場轉換工具')
    parser.add_argument('--input', '-i', required=True, help='ChatGPT conversations.json 路徑')
    parser.add_argument('--output', '-o', default='tonesoul_memories.json', help='輸出文件路徑')
    parser.add_argument('--batch-size', '-b', type=int, default=5, help='每批處理的對話數')
    parser.add_argument('--dry-run', action='store_true', help='只解析不呼叫 API')
    
    args = parser.parse_args()
    
    # 檢查 API Key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key and not args.dry_run:
        print("❌ 請設定 GEMINI_API_KEY 環境變數")
        print("   Windows: set GEMINI_API_KEY=your_key")
        print("   Linux/Mac: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    
    # 檢查輸入文件
    if not os.path.exists(args.input):
        print(f"❌ 找不到文件: {args.input}")
        sys.exit(1)
    
    # 解析 ChatGPT 對話
    parser_obj = ChatGPTParser(args.input)
    conversations = parser_obj.parse()
    
    if args.dry_run:
        print(f"\n📊 Dry Run 模式")
        print(f"   對話數: {len(conversations)}")
        print(f"   總訊息數: {sum(len(c.turns) for c in conversations)}")
        print(f"   批次數: {len(conversations) // args.batch_size + 1}")
        print(f"   預估 API 呼叫: {len(conversations) // args.batch_size + 1} 次")
        return
    
    # 執行轉換
    converter = GPTToToneSoulConverter(api_key, args.batch_size)
    converter.convert(conversations, args.output)


if __name__ == '__main__':
    main()
