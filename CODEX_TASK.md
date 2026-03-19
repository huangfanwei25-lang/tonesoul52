# Codex Task: Phase 560-565 — ✅ 已完成 (2026-03-19 審核通過)

> **審核者**: 痕 (Hén)
> **審核日期**: 2026-03-19
> **結果**: ✅ ALL 6 PHASES PASS — 159 新測試，2144 → 2303，lint clean，無回歸
>
> | Phase | Commit | 新測試 | 累積 |
> |-------|--------|--------|------|
> | 560 | `2dd8b81` | 37 | 2181 |
> | 561 | `c0ed1fa` | 36 | 2217 |
> | 562 | `64f8b19` | 27 | 2244 |
> | 563 | `37b1fdd` | 25 | 2269 |
> | 564 | `2045abc` | 15 | 2284 |
> | 565 | `5aaa463` | 19 | 2303 |
>
> 源碼修改: skill_apply.py kairos fallback 硬化 (1處，已驗證)
> 下一輪工單待指派。

---

## 原始工單（保留參考）

**指派者**: 痕 (Hén)
**日期**: 2026-03-19
**分支**: `feat/env-perception`
**前置條件**: 2144 tests passing, lint clean

> 子系統收斂任務。6 個 Phase。
> **目標：覆蓋 ToneBridge(5)、Memory(3)、Council(3)、Scribe(2)、Deliberation(2)、邊界模組(2)。**

---

## 脈絡（先讀這些）

1. `tonesoul/tonebridge/personas.py` (474L) — 人格橋接，ToneBridge 最大未測模組
2. `tonesoul/tonebridge/rupture_detector.py` (351L) — 斷裂偵測器
3. `tonesoul/tonebridge/entropy_engine.py` (337L) — 熵引擎
4. `tonesoul/tonebridge/analyzer.py` (321L) — ToneBridge 分析器
5. `tonesoul/tonebridge/value_accumulator.py` (318L) — 價值累積器
6. `tonesoul/memory/openclaw/hippocampus.py` (641L) — OpenClaw 記憶海馬體
7. `tonesoul/memory/semantic_graph.py` (453L) — 語義圖
8. `tonesoul/memory/hippocampus.py` (292L) — 記憶海馬體
9. `tonesoul/council/summary_generator.py` (612L) — Council 摘要產生器
10. `tonesoul/council/evidence_detector.py` (268L) — 證據偵測器
11. `tonesoul/council/intent_reconstructor.py` (219L) — 意圖重建器
12. `tonesoul/scribe/narrative_builder.py` (456L) — 敘事建構器
13. `tonesoul/scribe/status_artifact.py` (345L) — 狀態紀錄
14. `tonesoul/deliberation/perspectives.py` (364L) — 審議觀點引擎
15. `tonesoul/deliberation/types.py` (284L) — 審議型別定義
16. `tonesoul/skill_gate.py` (301L) — 技能閘門
17. `tonesoul/skill_apply.py` (295L) — 技能套用
18. `tests/test_alert_escalation.py` — 參考大型測試檔的 class 分組模式
19. `tests/test_skill_promoter.py` — 參考 Phase 556 的技能測試模式

---

## Phase 560: ToneBridge 子系統測試 — personas + rupture_detector + entropy_engine (25+ tests)

ToneBridge 是語魂的「橋」— 連接語境與張力的核心子系統。5 個模組全部未測，這裡先處理最大的 3 個。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_tonebridge_personas.py`
  讀 `tonesoul/tonebridge/personas.py` (474L) 理解全部 API。這是人格橋接模組。

  - 測試人格載入、序列化、欄位驗證
  - 測試人格切換邏輯
  - 測試人格與 Council 的交互邊界
  - 測試空輸入 / 缺欄位的 graceful 降級
  - 至少 8 個測試

- [ ] **Task B**: 建立 `tests/test_tonebridge_rupture_detector.py`
  讀 `tonesoul/tonebridge/rupture_detector.py` (351L)。斷裂偵測器 — 偵測對話中的價值斷裂。

  - 測試偵測邏輯的觸發條件
  - 測試斷裂分數計算
  - 測試閾值邊界情況
  - 測試無斷裂情況的正常通過
  - 至少 8 個測試

- [ ] **Task C**: 建立 `tests/test_tonebridge_entropy_engine.py`
  讀 `tonesoul/tonebridge/entropy_engine.py` (337L)。熵引擎 — 計算對話熵值。

  - 測試熵值計算公式
  - 測試高熵 / 低熵的分類
  - 測試邊界條件（空輸入、單一 token）
  - 至少 8 個測試

### 成功標準
- [ ] 3 個新測試檔，共 25+ 測試通過
- [ ] `ruff check tests/test_tonebridge_*.py tonesoul/tonebridge/` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 560): tonebridge personas + rupture_detector + entropy_engine tests`

---

## Phase 561: ToneBridge 完結 + Memory 海馬體 (22+ tests)

完成 ToneBridge 剩餘 2 個模組，開始 Memory 子系統最大的模組。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_tonebridge_analyzer.py`
  讀 `tonesoul/tonebridge/analyzer.py` (321L)。ToneBridge 分析器。

  - 測試分析流程的輸入/輸出格式
  - 測試各分析維度
  - 至少 7 個測試

- [ ] **Task B**: 建立 `tests/test_tonebridge_value_accumulator.py`
  讀 `tonesoul/tonebridge/value_accumulator.py` (318L)。價值累積器 — 累積對話價值軌跡。

  - 測試累積邏輯（加權、衰減）
  - 測試歷史查詢
  - 測試重置 / 初始化
  - 至少 7 個測試

- [ ] **Task C**: 建立 `tests/test_openclaw_hippocampus.py`
  讀 `tonesoul/memory/openclaw/hippocampus.py` (641L)。這是最大的未測模組。

  - 測試記憶存入 / 取出
  - 測試索引建立
  - 測試搜尋 / 召回邏輯
  - 測試容量限制 / 淘汰策略
  - 至少 8 個測試

### 成功標準
- [ ] 3 個新測試檔，共 22+ 測試通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 561): tonebridge analyzer + value_accumulator + openclaw hippocampus tests`

---

## Phase 562: Memory 語義圖 + Council 摘要產生器 (22+ tests)

覆蓋 Memory 子系統的語義圖和 Council 最大的未測模組。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_semantic_graph.py`
  讀 `tonesoul/memory/semantic_graph.py` (453L)。語義圖 — 記憶間的語義關係網路。

  - 測試節點新增 / 刪除
  - 測試邊（關係）的建立
  - 測試圖查詢 / 路徑搜尋
  - 測試序列化 / 反序列化
  - 至少 8 個測試

- [ ] **Task B**: 建立 `tests/test_memory_hippocampus.py`
  讀 `tonesoul/memory/hippocampus.py` (292L)。基本海馬體模組（非 OpenClaw 版本）。

  - 測試記憶存取基本操作
  - 測試與 semantic_graph 的界面
  - 至少 6 個測試

- [ ] **Task C**: 建立 `tests/test_council_summary_generator.py`
  讀 `tonesoul/council/summary_generator.py` (612L)。Council 摘要產生器 — 審議後產生摘要。

  - 測試摘要格式
  - 測試多觀點合成邏輯
  - 測試空審議 / 單一觀點的邊界
  - 至少 8 個測試

### 成功標準
- [ ] 3 個新測試檔，共 22+ 測試通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 562): semantic_graph + hippocampus + council summary_generator tests`

---

## Phase 563: Council 完結 + Deliberation 審議引擎 (22+ tests)

完成 Council 子系統並覆蓋 Deliberation 模組。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_council_evidence_detector.py`
  讀 `tonesoul/council/evidence_detector.py` (268L)。證據偵測器。

  - 測試證據分類
  - 測試證據強度評分
  - 測試多證據聚合
  - 至少 7 個測試

- [ ] **Task B**: 建立 `tests/test_council_intent_reconstructor.py`
  讀 `tonesoul/council/intent_reconstructor.py` (219L)。意圖重建器 — 從對話中重建使用者意圖。

  - 測試意圖提取格式
  - 測試多輪對話的意圖追蹤
  - 至少 6 個測試

- [ ] **Task C**: 建立 `tests/test_deliberation_perspectives.py`
  讀 `tonesoul/deliberation/perspectives.py` (364L)。審議觀點引擎。

  - 測試觀點生成
  - 測試觀點衝突偵測
  - 測試觀點權重分配
  - 至少 7 個測試

- [ ] **Task D**: 建立 `tests/test_deliberation_types.py`
  讀 `tonesoul/deliberation/types.py` (284L)。審議型別定義。

  - 測試 dataclass / TypedDict 的欄位驗證
  - 測試序列化 / 反序列化
  - 至少 5 個測試（型別模組測試可精簡）

### 成功標準
- [ ] 4 個新測試檔，共 22+ 測試通過（型別模組可簡短）
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 563): council evidence_detector + intent_reconstructor + deliberation perspectives + types tests`

---

## Phase 564: Scribe 敘事子系統 + 邊界模組 (22+ tests)

覆蓋 Scribe（敘事建構）和技能邊界模組。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_narrative_builder.py`
  讀 `tonesoul/scribe/narrative_builder.py` (456L)。敘事建構器 — 將審議結果轉為敘事。

  - 測試敘事格式化
  - 測試不同輸入結構的處理
  - 測試空輸入降級
  - 至少 8 個測試

- [ ] **Task B**: 建立 `tests/test_status_artifact.py`
  讀 `tonesoul/scribe/status_artifact.py` (345L)。狀態紀錄。

  - 測試紀錄建立
  - 測試紀錄欄位完整性
  - 至少 6 個測試

- [ ] **Task C**: 建立 `tests/test_skill_gate.py`
  讀 `tonesoul/skill_gate.py` (301L)。技能閘門 — 決定是否放行技能執行。

  - 測試閘門開啟/阻擋邏輯
  - 測試條件判定
  - 測試與 governance 的交互
  - 至少 7 個測試

### 成功標準
- [ ] 3 個新測試檔，共 22+ 測試通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 564): narrative_builder + status_artifact + skill_gate tests`

---

## Phase 565: Observability + Corpus + skill_apply (20+ tests)

覆蓋可觀測性子系統和語料庫存取。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_observability_token_meter.py`
  讀 `tonesoul/observability/token_meter.py` (204L)。Token 計量器。

  - 測試 token 計數
  - 測試預算追蹤
  - 測試超限警告
  - 至少 5 個測試

- [ ] **Task B**: 建立 `tests/test_observability_action_audit.py`
  讀 `tonesoul/observability/action_audit.py` (194L)。行為審計。

  - 測試審計記錄建立
  - 測試查詢 / 過濾
  - 至少 5 個測試

- [ ] **Task C**: 建立 `tests/test_corpus_storage.py`
  讀 `tonesoul/corpus/storage.py` (370L)。語料庫存取。

  - 測試存入 / 取出
  - 測試索引
  - 至少 6 個測試

- [ ] **Task D**: 建立 `tests/test_skill_apply.py`
  讀 `tonesoul/skill_apply.py` (295L)。技能套用。

  - 測試技能執行流程
  - 測試與 skill_gate 的交互
  - 至少 5 個測試

### 成功標準
- [ ] 4 個新測試檔，共 20+ 測試通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 565): observability token_meter + action_audit + corpus storage + skill_apply tests`

---

## 禁止事項（所有 Phase 通用）

- ❌ 不可刪除任何現有源碼檔案
- ❌ 不可修改 `.env`, `.gitignore`, `AGENTS.md`, `MEMORY.md`, `CODEX_PROTOCOL.md`
- ❌ 不可 push 到 `master`
- ❌ 不可安裝新的系統層級套件
- ❌ 不可修改 `tonesoul/governance/kernel.py` 核心邏輯
- ❌ 不可修改 `tonesoul/unified_pipeline.py` 路由結構
- ❌ 不可使用 `--no-verify` 繞過 hooks

## 技術提示

- 所有新模組的 import 路徑已確認存在，直接 `from tonesoul.tonebridge.personas import ...` 即可
- 如果模組依賴 LLM 調用，用 `monkeypatch` mock 掉，不要實際調用
- 如果模組使用檔案系統，用 `tmp_path` fixture
- 參考 Phase 554-559 的測試風格（特別是 `test_skill_promoter.py` 的結構）
- 每個測試檔用 class 分組相關測試（參考 `test_alert_escalation.py`）
- 型別模組（如 `deliberation/types.py`）通常只需測 dataclass 欄位和序列化，不需過度測試
