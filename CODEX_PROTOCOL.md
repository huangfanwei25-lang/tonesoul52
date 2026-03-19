# Codex 協作協議 — 痕 ↔ Codex (GPT 5.4)

> **版本**: 2.0
> **日期**: 2026-03-19
> **設計者**: 痕 (Hén) — Claude Opus 4.6，架構審核者
> **核准**: Antigravity (黃梵威)

---

## 一、角色定義

### 痕 (Hén) — 架構守護者 + 審核者
- 規劃 Phase 方向與任務拆分
- 撰寫 `CODEX_TASK.md` 工單（含脈絡、規則、成功標準）
- 審核 Codex 交付物（程式碼、測試、lint）
- 維護 `task.md`、`AGENTS.md`、技術記憶
- 處理涉及 `governance/`、`unified_pipeline.py` 核心路由的設計決策

### Codex (GPT 5.4) — 工程執行者
- 按照 `CODEX_TASK.md` 工單實作
- 寫測試、跑 lint、確認無回歸
- 完成後更新 `CODEX_HANDBACK.md`（交回脈絡）
- **不可**自行決定架構方向

---

## 二、工單格式 (CODEX_TASK.md)

每次指派新任務時，痕會覆寫 `CODEX_TASK.md`，格式如下：

```markdown
# Codex Task: Phase NNN — [名稱]

**指派者**: 痕 (Hén)
**日期**: YYYY-MM-DD
**分支**: feat/[描述]（不可 push 到 master）
**前置條件**: 1851 tests passing, lint clean

---

## 脈絡（先讀這些）
1. [檔案路徑] — [為什麼要讀]
2. [檔案路徑] — [為什麼要讀]

## 任務清單
- [ ] Task A: [描述]
- [ ] Task B: [描述]

## 成功標準
- [ ] 所有新功能有測試
- [ ] `ruff check [修改檔案]` 通過
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] CODEX_HANDBACK.md 已更新

## 禁止事項
- ❌ [具體禁止項]

## 技術提示
- [具體的實作建議或陷阱提醒]
```

---

## 三、交回格式 (CODEX_HANDBACK.md)

Codex 完成任務後，必須更新 `CODEX_HANDBACK.md`：

```markdown
# Codex 交回報告

**Phase**: NNN — [名稱]
**完成日期**: YYYY-MM-DD
**狀態**: ✅ 完成 / ⚠️ 部分完成 / ❌ 卡住

## 做了什麼
- [修改的檔案] — [做了什麼改動]

## 測試結果
- `ruff check [檔案]` → passed/failed
- `pytest [測試檔]` → N passed
- `pytest tests/ -x` → N passed (regression)

## 設計決策
- [任何需要痕知道的選擇與理由]

## 未完成 / 需要討論
- [卡住的地方或需要架構決策的問題]

## 連續失敗記錄（如有）
- 嘗試 1: [什麼] → [失敗原因]
- 嘗試 2: [什麼] → [失敗原因]
- 嘗試 3: [什麼] → [失敗原因] → **停止，等待審核**
```

---

## 四、安全護欄

### 硬性禁區（繼承自 AGENTS.md）
1. ❌ 不可刪除 `tonesoul/` 下的核心模組
2. ❌ 不可修改 `.env`, `.gitignore`, `AGENTS.md`, `MEMORY.md`
3. ❌ 不可 commit API key 或 `.env`
4. ❌ 不可 push 到 `master`
5. ❌ 不可安裝系統層級套件
6. ❌ 不可修改 `CODEX_PROTOCOL.md`（此檔由痕維護）

### 必做事項
1. ✅ 每次 commit 前：`pytest tests/ -x --tb=short -q` 全過
2. ✅ 每次 commit 前：`ruff check tonesoul tests` 無錯誤
3. ✅ 連續失敗 3 次必須停止，記錄到 `CODEX_HANDBACK.md`
4. ✅ 完成後必須更新 `CODEX_HANDBACK.md`

### 需提案的改動（不可直接做）
- 改動 `governance/kernel.py` 核心邏輯
- 改動 `unified_pipeline.py` 的路由結構
- 新增外部依賴 (pip install)
- 改變 API 契約 (request/response schema)
- 改動 `alert_escalation.py` 的警報層級定義

→ 如果任務涉及以上，在 `CODEX_HANDBACK.md` 寫提案，等痕審核。

---

## 五、審核流程

```
痕 寫 CODEX_TASK.md → Codex 執行 → Codex 寫 CODEX_HANDBACK.md → 痕 審核
     ↑                                                              │
     └──────────── 如有問題，痕更新 CODEX_TASK.md 重新指派 ←──────────┘
```

### 痕的審核檢查表
- [ ] 測試數量合理（新功能有對應測試）
- [ ] 無回歸 — 測試總數 ≥ 前一次
- [ ] lint clean
- [ ] 程式碼符合專案慣例（lazy getter、graceful fallback、dispatch_trace 可觀測）
- [ ] 沒有靜默吞掉異常（除非有明確理由）
- [ ] CODEX_HANDBACK.md 脈絡清晰

---

## 六、當前系統狀態 (供 Codex 參考)

| 項目 | 值 |
|------|-----|
| Python | 3.13.5 |
| 測試總數 | 1860 |
| 模組數 | 214+ |
| 核心管線 | `tonesoul/unified_pipeline.py` (18+ step flow) |
| 安全堆疊 | DriftMonitor → AlertEscalation → CircuitBreaker → JumpMonitor |
| 最新 Phase | 547 (Exception Observability Layer) |
| venv | `.venv/` |
| lint | `ruff` |
| test | `pytest` |

### 關鍵檔案速查
| 檔案 | 用途 |
|------|------|
| `tonesoul/unified_pipeline.py` | 主推理管線 |
| `tonesoul/alert_escalation.py` | 三層異常感知 L1/L2/L3 |
| `tonesoul/governance/kernel.py` | 治理核心 |
| `tonesoul/tension_engine.py` | 張力計算引擎 |
| `tonesoul/action_set.py` | 行動集策略 (normal/cautious/lockdown) |
| `tonesoul/drift_monitor.py` | EMA 語義漂移偵測 |
| `tonesoul/jump_monitor.py` | 奇點跳躍偵測 |
| `tonesoul/memory/crystallizer.py` | 記憶結晶 + 新鮮度衰減 |
| `tonesoul/dream_engine.py` | 離線碰撞 + 驗證任務 |
| `task.md` | Phase 歷史紀錄 |
| `AGENTS.md` | AI 行為規範（不可修改）|

---

*此協議由痕 (Hén) 維護。Codex 不可修改此檔案。*
