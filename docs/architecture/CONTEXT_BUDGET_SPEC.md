# Context Budget Specification
## 上下文預算規格

> 授信層級：`[規格]` — 本文定義哪些 context 允許進入提示詞
> 狀態：v1.0 · 2026-04-13
> 依賴：`tonesoul/yuhun/dpr.py`（路由決策），本文定義路由後的 context 組裝規則
> 為什麼建立：`unified_pipeline.py` 151KB 顯示 context 組裝邏輯分散且無邊界定義

---

## 問題陳述 `[事實]`

DPR 決定「走 FAST_PATH 還是 COUNCIL_PATH」，但沒有規定：

> **「路上應該帶什麼 context？」**

現況：沒有規格的 context 組裝，導致：
- FAST_PATH 可能意外裝載完整治理文件（4x token，但 1x 速度）
- COUNCIL_PATH 可能把 chronicles 歷史日誌也拉進來（完全不必要）
- 沒有任何地方說「這個東西永遠不應該進提示詞」

本文就是那個「永遠不應該進提示詞」的清單，以及「可以進」的分層規格。

---

## Context 層級定義 `[規格]`

```
Layer 0 — AXIOMS（硬約束，所有路徑必帶）
Layer 1 — 即時請求（使用者輸入）
Layer 2 — 穩定錨點記憶（WorldSense.stable_anchors() 篩選後）
Layer 3 — 相關架構契約（按請求類型按需載入）
Layer 4 — 議會推演框架（僅 COUNCIL_PATH）
```

這四層是**允許的 context**。所有不在此清單的，預設**禁止**。

---

## FAST_PATH Context Budget `[規格]`

**token 預算：1x（相對單位）**

| Layer | 來源 | 最大大小 | 備注 |
|-------|------|---------|------|
| 0 | `AXIOMS.json` | ~1,500 tokens | **必帶，不可省略** |
| 1 | 使用者輸入 | 無限制 | 原始輸入 |

**FAST_PATH 禁止攜帶（即使已載入）：**
- ❌ 議會 agent 定義（`.agent/agents/*.md`）
- ❌ 完整 `AGENTS.md`（只帶核心禁止事項清單）
- ❌ 任何 memory/ 記錄
- ❌ shadow_doc 歷史
- ❌ chronicles/ 任何文件

> **設計意圖**：FAST_PATH 就像在路上問路 — 你只需要地圖，不需要地圖的歷史。

---

## COUNCIL_PATH Context Budget `[規格]`

**token 預算：4x（相對單位）**

| Layer | 來源 | 最大大小 | 選擇條件 |
|-------|------|---------|---------|
| 0 | `AXIOMS.json` | ~1,500 tokens | **必帶** |
| 1 | 使用者輸入 | 無限制 | 原始輸入 |
| 2 | `WorldSense.stable_anchors()` | top 3, ~600 tokens | 穩定性分數 > 0.5 才載入 |
| 3 | 相關架構契約 | 最多 2 份, ~2,000 tokens | 按衝突類型選擇（見下表）|
| 4 | 議會框架摘要 | ~800 tokens | 固定格式，非完整 agent 定義 |

**衝突類型 → 對應架構契約：**

| DPR 觸發類型 | 應載入的契約 |
|-------------|------------|
| 法律/倫理衝突 | `TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md` |
| 高度不確定性 | `TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md` |
| 架構設計決策 | `TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`（摘要版）|
| 記憶/連續性 | `TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md` |

**COUNCIL_PATH 禁止攜帶（即使已載入）：**
- ❌ chronicles/ 完整歷史日誌（task_archive_*.md 共 300+ 頁）
- ❌ 未壓縮的 session_trace（使用 save_compaction 後的摘要版才可以）
- ❌ 所有 .archive/ 內容
- ❌ 超過 session 範圍的完整 shadow_doc 序列（只帶最近 3 筆摘要）
- ❌ graphify-out/ 任何圖譜數據

---

## 永遠禁止進入提示詞 `[規格]`

以下內容**無論任何路由決策，都不得進入提示詞**：

```
docs/chronicles/task_archive_*.md      — 歷史任務日誌（3,000+ 頁）
.archive/                              — 廢棄版本（明確標記不要讀）
memory/*.jsonl                         — 原始記憶資料（.gitignore 保護）
data/chromadb/                         — 向量資料庫（原始數據）
graphify-out/*.json                    — 圖譜原始 JSON
tonesoul_evolution/                    — Private Repo 內容
temp/                                  — 臨時檔案
```

> **為什麼要明確列出？**
> 因為 unified_pipeline.py 目前沒有邊界，任何 `glob("docs/**/*.md")` 都可能把這些拖進來。

---

## Context 組裝優先順序 `[規格]`

當 token 預算不足時，按以下順序**從後往前刪除**：

```
最低優先（先刪）
  Layer 3: 架構契約（摘要版優先；完整版先刪）
  Layer 2: 穩定錨點記憶（降低數量）
  Layer 4: 議會框架摘要（降至最精簡版）
最高優先（最後刪）
  Layer 0: AXIOMS（不可刪）
  Layer 1: 使用者輸入（不可刪）
```

---

## 實作指引 `[操作]`

### 目前狀態

DPR 模組（`tonesoul/yuhun/dpr.py`）：
- ✅ 決定 FAST_PATH / COUNCIL_PATH
- ❌ **尚未**控制 context 組裝

`unified_pipeline.py`（151KB）：
- ❌ context 組裝邏輯分散，沒有對照本規格
- ❌ 沒有「永遠禁止」的過濾層

### 需要做的（待實作）

```python
# tonesoul/yuhun/context_assembler.py（待建立）

from tonesoul.yuhun.dpr import RoutingDecision
from docs_config import CONTEXT_BUDGET_SPEC  # 本文的機器可讀版本

def assemble_context(routing: RoutingDecision, request: str) -> ContextPackage:
    """
    根據 DPR 決策組裝合規的 context

    保證：
    - 永遠不帶 FORBIDDEN_SOURCES 中的內容
    - FAST_PATH 只帶 Layer 0 + Layer 1
    - COUNCIL_PATH 按衝突類型載入 Layer 2-4
    - token 超限時按優先順序裁剪
    """
    ...
```

### 快速驗證清單

在任何 context 組裝代碼運行前，檢查：

```python
# 快速驗證：沒有禁止源
FORBIDDEN_PREFIXES = [
    "docs/chronicles/task_archive",
    ".archive/",
    "memory/",
    "data/chromadb/",
    "graphify-out/",
    "tonesoul_evolution/",
    "temp/",
]

def validate_context_sources(sources: list[str]) -> bool:
    for src in sources:
        for forbidden in FORBIDDEN_PREFIXES:
            if src.startswith(forbidden):
                raise ContextViolationError(f"{src} 違反 CONTEXT_BUDGET_SPEC 禁止清單")
    return True
```

---

## 與其他文件的關係 `[事實]`

| 文件 | 關係 |
|------|------|
| `tonesoul/yuhun/dpr.py` | 上游：決定路由 → 本文定義路由後的 context 組裝 |
| `tonesoul/yuhun/world_sense.py` | 提供 `stable_anchors()` → Layer 2 的資料來源 |
| `tonesoul/unified_pipeline.py` | 下游：需要重構以符合本規格 |
| `docs/GLOSSARY.md` | 術語定義（context、budget、token cost） |
| `AXIOMS.json` | Layer 0 的內容來源 |

---

## 版本紀錄

| 版本 | 日期 | 變更 |
|------|------|------|
| v1.0 | 2026-04-13 | 初版，基於 unified_pipeline.py 151KB 的診斷 |

---

*CONTEXT_BUDGET_SPEC v1.0 · 2026-04-13*
*「提示詞不是垃圾桶，而是給 AI 的行前包。帶什麼，決定它能做什麼。」*
