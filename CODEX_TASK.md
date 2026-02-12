# CODEX_TASK — 語魂後端重構：從聊天介面轉向 AI 自我演化引擎

> **上次更新**：2026-02-13T01:25 (UTC+8)
> **交辦者**：Antigravity (Gemini)
> **狀態**：🟡 待啟動

---

## 📌 重要：先讀這些文件

你沒有記憶，所以必須先讀以下文件來理解系統全貌：

| 順序 | 文件 | 為什麼要讀 |
|------|------|-----------|
| 1 | `docs/ARCHITECTURE_DEPLOYED.md` | **最重要** — 系統架構全局圖、前後端分工、蒸餾路線圖、哲學基底 |
| 2 | `docs/ARCHITECTURE_BOUNDARIES.md` | 三層架構（Application → Governance → Infrastructure）與依賴規則 |
| 3 | `apps/api/server.py` | Flask 後端主程式（974行），所有 API 路由 |
| 4 | `tonesoul/unified_pipeline.py` | 統一管線（724行），核心處理流程 |
| 5 | `tonesoul/supabase_persistence.py` | Supabase 持久化模組（458行） |
| 6 | `tonesoul/tonebridge/commitment_extractor.py` | 第三公理：承諾/斷裂/價值追蹤 |
| 7 | `tonesoul/council/` | 議會系統目錄 |
| 8 | `docs/engineering/OVERVIEW.md` | 五卷工程基石總覽 |

---

## 🧠 核心理念（讀了 ARCHITECTURE_DEPLOYED.md 之後你會了解）

- **前端** (`apps/web`) = **使用者的服務** — 對話介面、個人化、資料管理
- **後端** (`apps/api` + `tonesoul/`) = **AI 的服務** — 議會審議、語橋分析、自我演化
- 後端 **不需要人類 UI**。`apps/council-playground/chat.html` 是早期原型，應移除
- 後端的真正使命：累積結構化觀測資料 → 整理脈絡 → 為本地語魂蒸餾做準備

**語魂的終極目標**不是做「更聰明的 AI 聊天機器人」，而是蒸餾出一個 **有倫理判斷能力的本地智能體**。每次對話產生的議會審議、語橋分析、承諾追蹤資料都是語料。

---

## 🎯 本次任務總覽

```
Task 1: 後端清理（移除 legacy chat.html，整理 Playground）
Task 2: 讀取類 API 補齊
Task 3: 脈絡整理模組（SEAL-like 自我演化基礎）
Task 4: 語料標記格式設計
Task 5: 測試
```

---

## Task 1：後端清理

### 1A. 移除 `apps/council-playground/chat.html`

**為什麼**：前端已有完整 Next.js 聊天介面（`apps/web`），後端不需要第二個聊天 UI。
後端的定位是服務 AI 的基礎設施，不是服務使用者的介面。

**做法**：
- 刪除 `apps/council-playground/chat.html`（1386 行）
- 修改 `apps/api/server.py` 中對 chat.html 的引用（如果有 route 指向它，移除）

**驗證**：搜尋 `chat.html` 確認所有引用已清理：
```bash
grep -r "chat.html" apps/ --include="*.py" --include="*.js" --include="*.html"
```

### 1B. 改版 Playground 為系統狀態儀表板

`apps/council-playground/index.html` 從「使用者聊天入口」轉變為「AI 觀測儀表板」。

**新的首頁應顯示**：
1. **系統健康狀態**（呼叫 `GET /api/health`）
   - LLM 後端狀態、Supabase 連線、記憶數量
2. **審計日誌摘要**（呼叫 `GET /api/audit-logs`，顯示最近 10 筆）
3. **語料統計**（對話數、訊息數、承諾追蹤數）
4. **自我演化狀態**（Task 3 完成後）

**不應包含**：
- ❌ 聊天輸入框（那是前端的事）
- ❌ 使用者登入/註冊
- ❌ 任何面向一般使用者的功能

**修改檔案**：
- `apps/council-playground/index.html` — 改為儀表板 layout
- `apps/council-playground/style.css` — 深色主題、状態卡片、glassmorphism
- `apps/council-playground/app.js` — fetchStatus / fetchAuditLogs / fetchStats

---

## Task 2：讀取類 API 補齊

目前 `server.py` 主要只寫入 Supabase，缺讀取 API。

### 2A. 在 `tonesoul/supabase_persistence.py` 新增讀取方法

```python
class SupabasePersistence:
    # ... 現有的寫入方法 ...

    # 新增：
    def list_conversations(self, limit: int = 20, offset: int = 0) -> dict:
        """查 conversations 表，回傳 { conversations: [...], total: N }"""

    def get_conversation(self, conversation_id: str) -> dict | None:
        """查 conversations + messages，回傳完整對話（含所有訊息）"""

    def delete_conversation(self, conversation_id: str) -> bool:
        """刪除對話（CASCADE 會清 messages）"""

    def list_audit_logs(self, limit: int = 20, offset: int = 0) -> dict:
        """查 audit_logs 表"""

    def list_memories(self, limit: int = 50) -> list:
        """查 soul_memories 表"""

    def get_counts(self) -> dict:
        """各表 COUNT"""
```

### 2B. 在 `apps/api/server.py` 新增路由

| 方法 | 路由 | 說明 |
|------|------|------|
| GET | `/api/conversations` | 列出所有對話（分頁） |
| GET | `/api/conversations/<id>` | 取得單一對話含訊息 |
| DELETE | `/api/conversations/<id>` | 刪除對話 |
| GET | `/api/audit-logs` | 審計日誌（分頁） |
| GET | `/api/status` | 系統狀態總覽 |

**注意**：修改現有 `GET /api/memories`（server.py ~Line 292），如果 `supabase_persistence.enabled`，從 Supabase 讀取，否則 fallback 到本地 `self_journal.jsonl`。

---

## Task 3：脈絡整理模組（核心——SEAL-like 自我演化基礎）

> 這是最重要的 Task。這不是「功能」，是語魂自我演化的起點。

### 3A. 建立 `tonesoul/evolution/context_distiller.py` [NEW]

**目的**：從歷史對話中提取**有用的脈絡**，而不只是存著。

參考 SEAL (Self-Evolving Adversarial Learning) 框架的概念，但改為 **合作式自我演化**：

```python
"""
語魂自我演化 — 脈絡蒸餾器

從 Supabase 中的歷史對話提取以下類型的結構化脈絡：

1. 決策模式（哪些議會審議路徑產生了好的結果）
2. 價值累積（哪些承諾被兌現、哪些斷裂了）
3. 語氣演化（使用者語氣如何隨時間變化）
4. 衝突解決（哪些衝突被成功解決、怎麼解決的）
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ContextPattern:
    """一個被提取出的脈絡模式"""
    pattern_type: str        # "decision" | "value" | "tone_shift" | "conflict_resolution"
    description: str         # 人類可讀的描述
    evidence: List[str]      # 來源對話 ID 列表
    confidence: float        # 0.0 - 1.0
    extracted_at: str        # ISO timestamp
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistillationResult:
    """一次蒸餾的輸出"""
    patterns: List[ContextPattern]
    conversations_analyzed: int
    time_range: tuple  # (earliest, latest)
    summary: str


class ContextDistiller:
    """
    從歷史對話中蒸餾有用的脈絡。

    使用方式：
        distiller = ContextDistiller(supabase_persistence)
        result = distiller.distill(limit=100)
        # result.patterns 就是提取出的脈絡
    """

    def __init__(self, persistence):
        """
        Args:
            persistence: SupabasePersistence 實例
        """
        self.persistence = persistence

    def distill(self, limit: int = 100) -> DistillationResult:
        """
        分析最近 N 筆對話，提取脈絡模式。

        步驟：
        1. 從 Supabase 讀取對話 + audit_logs
        2. 分析議會審議記錄 → 提取決策模式
        3. 分析承諾/斷裂記錄 → 提取價值累積
        4. 分析連續對話的語氣變化 → 提取語氣演化
        5. 對比不同時期的同類議題 → 提取衝突解決模式
        """
        ...

    def extract_decision_patterns(self, audit_logs: List[Dict]) -> List[ContextPattern]:
        """
        從審計日誌提取決策模式。

        看的是：
        - philosopher/engineer/guardian 三視角分歧大時，synthesizer 怎麼調和的
        - 哪些類型的問題觸發了 guardian 的高風險警告
        - synthesizer 的最終決策是否被使用者接受（看後續對話）
        """
        ...

    def extract_value_accumulation(self, conversations: List[Dict]) -> List[ContextPattern]:
        """
        從承諾追蹤提取價值累積。

        看的是：
        - self_commits 中哪些被後續對話證實兌現
        - ruptures 中哪些被修復
        - emergent_values 中有什麼新浮現的價值
        """
        ...

    def extract_tone_evolution(self, conversations: List[Dict]) -> List[ContextPattern]:
        """
        從語氣軌跡提取演化趨勢。

        看的是：
        - 同一使用者的語氣如何隨時間變化
        - 崩潰風險高的對話後，下一次對話的改善情況
        """
        ...

    def extract_conflict_resolutions(self, conversations: List[Dict]) -> List[ContextPattern]:
        """
        提取成功的衝突解決案例。

        看的是：
        - 高張力對話中議會如何化解
        - 使用者表達不滿時，系統如何應對並恢復
        """
        ...
```

### 3B. 在 `server.py` 新增蒸餾 API

```
POST /api/evolution/distill
  → 觸發一次脈絡蒸餾
  → 回傳 DistillationResult

GET /api/evolution/patterns
  → 查看已蒸餾出的脈絡模式

GET /api/evolution/summary
  → 語魂演化摘要（多少脈絡、最近的演化趨勢）
```

### 3C. 建立 `tonesoul/evolution/__init__.py` [NEW]

```python
"""語魂自我演化模組"""
from .context_distiller import ContextDistiller, ContextPattern, DistillationResult

__all__ = ["ContextDistiller", "ContextPattern", "DistillationResult"]
```

---

## Task 4：語料標記格式

### 4A. 建立 `tonesoul/evolution/corpus_schema.py` [NEW]

設計語料標記格式，為未來蒸餾做準備。

```python
"""
語魂語料標記格式

每一筆語料記錄一個「倫理決策點」——
不是教 AI 說什麼，而是記錄 AI 怎麼思考、怎麼負責。
"""

@dataclass
class CorpusEntry:
    """
    一筆可蒸餾的語料。

    這不是 chat transcript。這是結構化的「決策記錄」。
    """
    # 情境
    user_message: str
    conversation_context: str   # 簡化的對話脈絡（不是全部歷史）

    # 議會審議記錄
    philosopher_stance: str     # 哲學家的立場
    engineer_approach: str      # 工程師的方案
    guardian_risk: str          # 守護者的風險評估
    synthesizer_decision: str   # 最終決策

    # 倫理維度
    tension_level: float        # 張力等級 0.0-1.0
    values_invoked: List[str]   # 被觸發的價值觀
    commitments_made: List[str] # 做出的承諾
    risks_identified: List[str] # 識別到的風險

    # 結果
    final_response: str         # 最終回應
    user_satisfaction: Optional[str]  # 使用者反應（如果有）

    # 元資料
    timestamp: str
    conversation_id: str
    quality_score: Optional[float]  # 人工或自動評分
    tags: List[str]             # 標籤（如 "ethical_dilemma", "emotional_support"）
```

### 4B. 建立 `tonesoul/evolution/corpus_builder.py` [NEW]

將 Supabase 中的對話 + audit_logs 轉換為 CorpusEntry 格式：

```python
class CorpusBuilder:
    def __init__(self, persistence):
        self.persistence = persistence

    def build_from_conversation(self, conversation_id: str) -> List[CorpusEntry]:
        """
        將一個對話轉換為一系列 CorpusEntry。
        每一輪 user→assistant 交換產生一筆 entry。
        """
        ...

    def build_batch(self, limit: int = 100) -> List[CorpusEntry]:
        """
        批次轉換多個對話。
        只轉換有完整 audit_log 的對話（有審議記錄的才有價值）。
        """
        ...

    def export_jsonl(self, entries: List[CorpusEntry], path: str):
        """匯出為 JSONL 格式（可用於蒸餾）"""
        ...
```

---

## Task 5：測試

### 5A. 單元測試

新增以下測試檔案：

| 測試檔 | 測試目標 |
|--------|---------|
| `tests/test_supabase_read.py` | Task 2 的讀取方法 |
| `tests/test_context_distiller.py` | Task 3 的脈絡蒸餾器 |
| `tests/test_corpus_builder.py` | Task 4 的語料建構器 |
| `tests/test_server_new_routes.py` | Task 2B 的新 API 路由 |

**注意**：測試應該可以在沒有 Supabase 的情況下跑（用 mock data）。

### 5B. 整合驗證

```bash
# 健康檢查
curl https://tonesoul52.onrender.com/api/health

# 系統狀態
curl https://tonesoul52.onrender.com/api/status

# 對話列表
curl https://tonesoul52.onrender.com/api/conversations

# 審計日誌
curl https://tonesoul52.onrender.com/api/audit-logs

# 觸發脈絡蒸餾
curl -X POST https://tonesoul52.onrender.com/api/evolution/distill

# 查看蒸餾結果
curl https://tonesoul52.onrender.com/api/evolution/patterns
```

---

## 重要參考檔案

| 檔案 | 行數 | 說明 |
|------|------|------|
| `docs/ARCHITECTURE_DEPLOYED.md` | ~280 | **必讀**：系統全貌、前後端分工、倫理智能體願景 |
| `docs/ARCHITECTURE_BOUNDARIES.md` | 193 | 三層架構與依賴規則 |
| `apps/api/server.py` | 974 | Flask 後端，所有路由 |
| `tonesoul/unified_pipeline.py` | 724 | 統一管線處理流程 |
| `tonesoul/supabase_persistence.py` | 458 | Supabase 持久化（寫入已完成、讀取待補） |
| `tonesoul/tonebridge/commitment_extractor.py` | — | 第三公理：承諾/斷裂追蹤 |
| `tonesoul/council/` | — | 議會系統（Philosopher/Engineer/Guardian/Synthesizer） |
| `apps/council-playground/chat.html` | 1386 | **待刪除** — legacy 聊天 UI |
| `apps/council-playground/index.html` | — | **待改版** → 系統儀表板 |
| `docs/plans/supabase_migration.sql` | — | Supabase 表結構 |

## 環境變數（已設定在 Render）

| 變數 | 值 |
|------|----|
| `SUPABASE_URL` | `https://sjtoyjsnykstclcbktoo.supabase.co` |
| `SUPABASE_KEY` | （service_role key，已設定） |
| `GEMINI_API_KEY` | （已設定） |
| `GOOGLE_API_KEY` | （相容別名） |

## 優先順序

```
Task 1 (清理) → Task 2 (讀取 API) → Task 3 (脈絡整理) → Task 4 (語料格式) → Task 5 (測試)
     ↑                   ↑                    ↑
   簡單快速            Task 3 依賴此        最重要的產出
```

Task 3 是這次任務的核心。Task 1 和 2 是前置準備。
