# Codex Task: Phase 566-571 — ✅ 已完成 (2026-03-20 審核通過)

> **審核者**: 痕 (Hén)
> **審核日期**: 2026-03-20
> **結果**: ✅ ALL 6 PHASES PASS — 188 新測試，2303 → 2491，lint clean，無回歸
>
> | Phase | Commit | 新測試 | 累積 |
> |-------|--------|--------|------|
> | 566 | `ae1445a` | 37 | 2340 |
> | 567 | `eda3893` | 25 | 2365 |
> | 568 | `30a4eb0` | 23 | 2388 |
> | 569 | `98573c9` | 30 | 2418 |
> | 570 | `9d80c28` | 29 | 2447 |
> | 571 | `1efa7d6` | 44 | 2491 |
>
> 源碼修改: 0 處。純測試新增 (43 檔, +3448L)。
> **最終收斂完成 — tonesoul/ 全部源碼模組均有測試覆蓋。**

---

## 原始工單（保留參考）

**指派者**: 痕 (Hén)
**日期**: 2026-03-19
**分支**: `feat/env-perception`
**前置條件**: 2303 tests passing, lint clean

> **最終收斂任務。6 個 Phase，43 個模組，做完後全部源碼模組都有測試覆蓋。**
> 這是最後一輪。完成後 tonesoul/ 下不再有未測模組。

---

## 脈絡（先讀這些）

1. `tests/test_tonebridge_analyzer.py` — 參考 Phase 560 的測試結構
2. `tests/test_skill_apply.py` — 參考 Phase 565 的邊界測試模式
3. `tests/test_alert_escalation.py` — 參考 class 分組模式
4. `tests/test_governance_kernel.py` — 參考大型核心模組的測試策略

---

## Phase 566: LLM 客戶端 + Market 子系統 (5 模組, 30+ tests)

覆蓋 LLM 客戶端封裝和 Market 子系統的核心模組。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_ollama_client.py`
  讀 `tonesoul/llm/ollama_client.py` (377L)。Ollama LLM 客戶端封裝。

  - 測試客戶端初始化（預設參數、自訂端點）
  - 測試請求建構（prompt 格式化、模型選擇）
  - 測試回應解析（正常、空回應、錯誤格式）
  - 測試連線失敗的 graceful fallback
  - 測試 timeout 處理
  - 至少 7 個測試

- [ ] **Task B**: 建立 `tests/test_lmstudio_client.py`
  讀 `tonesoul/llm/lmstudio_client.py` (313L)。LM Studio 客戶端封裝。

  - 測試客戶端初始化
  - 測試 API 呼叫格式
  - 測試錯誤回應處理
  - 測試 streaming 模式（如有）
  - 至少 6 個測試

- [ ] **Task C**: 建立 `tests/test_gold_detector.py`
  讀 `tonesoul/market/gold_detector.py` (382L)。黃金偵測器 — 偵測有價值的資訊片段。

  - 測試偵測邏輯和評分
  - 測試閾值判定
  - 測試各資訊類型的處理
  - 至少 7 個測試

- [ ] **Task D**: 建立 `tests/test_data_ingest.py`
  讀 `tonesoul/market/data_ingest.py` (346L)。資料攝入管線。

  - 測試資料格式驗證
  - 測試攝入流程（正常、異常資料）
  - 測試批次處理
  - 至少 6 個測試

- [ ] **Task E**: 建立 `tests/test_forecaster.py`
  讀 `tonesoul/market/forecaster.py` (210L)。預測器。

  - 測試預測模型輸入/輸出
  - 測試歷史資料查詢
  - 至少 5 個測試

### 成功標準
- [ ] 5 個新測試檔，共 30+ 測試通過
- [ ] `ruff check tests/ tonesoul/llm/ tonesoul/market/` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 566): LLM clients + market gold_detector + data_ingest + forecaster`

---

## Phase 567: YSTM 子系統全覆蓋 (8 模組, 25+ tests)

YSTM（You-Soul-Tension-Model）是語魂的張力視覺化子系統，8 個模組全部未測。
小模組居多，可以精簡。`ystm_demo.py` (5L) 如果只是腳本入口，可跳過或寫 1 個 smoke test。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_ystm_demo.py`
  讀 `tonesoul/ystm/demo.py` (400L)。YSTM 展示邏輯。

  - 測試 demo 流程的各步驟
  - 測試輸出格式
  - 至少 6 個測試

- [ ] **Task B**: 建立 `tests/test_ystm_diff.py`
  讀 `tonesoul/ystm/diff.py` (196L)。張力差異計算。

  - 測試差異計算邏輯
  - 測試邊界值（相同輸入、空輸入）
  - 至少 4 個測試

- [ ] **Task C**: 建立 `tests/test_ystm_representation.py`
  讀 `tonesoul/ystm/representation.py` (176L)。張力表示層。

  - 測試表示建構
  - 測試序列化
  - 至少 4 個測試

- [ ] **Task D**: 建立 `tests/test_ystm_acceptance.py`
  讀 `tonesoul/ystm/acceptance.py` (146L)。接受度判定。

  - 測試接受/拒絕邏輯
  - 測試閾值邊界
  - 至少 3 個測試

- [ ] **Task E**: 建立 `tests/test_ystm_terrain.py`
  讀 `tonesoul/ystm/terrain.py` (117L)。張力地形。

  - 測試地形建構
  - 至少 3 個測試

- [ ] **Task F**: 建立 `tests/test_ystm_projection.py`
  讀 `tonesoul/ystm/projection.py` (54L)。張力投影。

  - 至少 2 個測試

- [ ] **Task G**: 建立 `tests/test_ystm_energy.py`
  讀 `tonesoul/ystm/energy.py` (40L)。張力能量。

  - 至少 2 個測試

- [ ] **Task H**: 建立 `tests/test_ystm_demo_entry.py`（如 `ystm_demo.py` 只有 5L）
  讀 `tonesoul/ystm_demo.py` (5L)。如果只是 import + run，1 個 smoke test 即可。

  - 至少 1 個測試

### 成功標準
- [ ] 8 個新測試檔，共 25+ 測試通過
- [ ] `ruff check tests/test_ystm_*.py tonesoul/ystm/` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 567): YSTM subsystem full coverage — demo + diff + representation + acceptance + terrain + projection + energy`

---

## Phase 568: ToneBridge 軌跡 + Perception + Corpus 同意 (3 模組, 20+ tests)

覆蓋 ToneBridge 最後的軌跡模組、感知子系統和語料庫同意機制。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_tonebridge_trajectory.py`
  讀 `tonesoul/tonebridge/trajectory.py` (311L)。張力軌跡 — 追蹤對話中的張力演變。

  - 測試軌跡記錄（新增時間點）
  - 測試軌跡查詢（時間範圍、最近 N 個）
  - 測試軌跡統計（趨勢、峰值）
  - 測試空軌跡的 graceful 處理
  - 至少 7 個測試

- [ ] **Task B**: 建立 `tests/test_perception_stimulus.py`
  讀 `tonesoul/perception/stimulus.py` (275L)。刺激處理 — 外部輸入的感知分類。

  - 測試刺激分類邏輯
  - 測試強度評估
  - 測試多刺激聚合
  - 至少 6 個測試

- [ ] **Task C**: 建立 `tests/test_corpus_consent.py`
  讀 `tonesoul/corpus/consent.py` (237L)。語料庫同意機制。

  - 測試同意狀態管理（授權、撤銷）
  - 測試同意驗證邏輯
  - 測試預設同意策略
  - 至少 6 個測試

### 成功標準
- [ ] 3 個新測試檔，共 20+ 測試通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 568): tonebridge trajectory + perception stimulus + corpus consent`

---

## Phase 569: Tech Trace + Observability + Loop (7 模組, 25+ tests)

覆蓋技術追蹤、可觀測性和事件迴圈子系統。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_tech_trace_normalize.py`
  讀 `tonesoul/tech_trace/normalize.py` (291L)。追蹤資料正規化。

  - 測試各資料型態的正規化
  - 測試格式轉換
  - 測試異常輸入
  - 至少 6 個測試

- [ ] **Task B**: 建立 `tests/test_tech_trace_validate.py`
  讀 `tonesoul/tech_trace/validate.py` (142L)。追蹤資料驗證。

  - 測試驗證規則
  - 測試通過/失敗回饋
  - 至少 4 個測試

- [ ] **Task C**: 建立 `tests/test_tech_trace_capture.py`
  讀 `tonesoul/tech_trace/capture.py` (127L)。追蹤資料擷取。

  - 測試擷取流程
  - 測試資料完整性
  - 至少 3 個測試

- [ ] **Task D**: 建立 `tests/test_observability_logger.py`
  讀 `tonesoul/observability/logger.py` (235L)。可觀測性日誌。

  - 測試日誌層級
  - 測試結構化日誌輸出
  - 測試日誌過濾
  - 至少 5 個測試

- [ ] **Task E**: 建立 `tests/test_observability_env_config.py`
  讀 `tonesoul/observability/env_config.py` (113L)。環境設定。

  - 測試設定載入（預設值、env vars）
  - 測試設定驗證
  - 至少 3 個測試

- [ ] **Task F**: 建立 `tests/test_loop_events.py`
  讀 `tonesoul/loop/events.py` (204L)。迴圈事件。

  - 測試事件建立
  - 測試事件分發
  - 至少 4 個測試

- [ ] **Task G**: 建立 `tests/test_loop_config.py`
  讀 `tonesoul/loop/config.py` (64L)。迴圈設定。

  - 測試設定欄位
  - 至少 2 個測試

### 成功標準
- [ ] 7 個新測試檔，共 25+ 測試通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 569): tech_trace normalize + validate + capture + observability logger + env_config + loop events + config`

---

## Phase 570: Core 根模組 (6 模組, 20+ tests)

覆蓋 tonesoul/ 根目錄下的核心工具模組。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_service_manager.py`
  讀 `tonesoul/service_manager.py` (227L)。服務管理器。

  - 測試服務註冊 / 取消
  - 測試服務查詢
  - 測試生命週期管理
  - 至少 5 個測試

- [ ] **Task B**: 建立 `tests/test_error_event.py`
  讀 `tonesoul/error_event.py` (215L)。錯誤事件。

  - 測試事件建立
  - 測試事件屬性
  - 測試事件序列化
  - 至少 4 個測試

- [ ] **Task C**: 建立 `tests/test_dcs.py`
  讀 `tonesoul/dcs.py` (163L)。DCS（Decision Context Stack）。

  - 測試 stack push/pop
  - 測試 context 查詢
  - 至少 4 個測試

- [ ] **Task D**: 建立 `tests/test_constraint_stack.py`
  讀 `tonesoul/constraint_stack.py` (149L)。約束堆疊。

  - 測試約束添加 / 移除
  - 測試約束衝突偵測
  - 至少 3 個測試

- [ ] **Task E**: 建立 `tests/test_unified_controller.py`
  讀 `tonesoul/unified_controller.py` (137L)。統一控制器。

  - 測試控制器初始化
  - 測試指令分發
  - 至少 3 個測試

- [ ] **Task F**: 建立 `tests/test_context_compiler.py`
  讀 `tonesoul/context_compiler.py` (135L)。上下文編譯器。

  - 測試上下文組裝
  - 測試欄位合併
  - 至少 3 個測試

### 成功標準
- [ ] 6 個新測試檔，共 20+ 測試通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 570): service_manager + error_event + dcs + constraint_stack + unified_controller + context_compiler`

---

## Phase 571: 尾部收斂 — 全部小模組 (14 模組, 25+ tests)

最後的掃尾。14 個小模組全部覆蓋。做完後 tonesoul/ 不再有未測模組。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_subjectivity_admissibility.py`
  讀 `tonesoul/memory/subjectivity_admissibility.py` (197L)。主觀性可採納判定。

  - 測試可採納性判定邏輯
  - 測試邊界案例
  - 至少 4 個測試

- [ ] **Task B**: 建立 `tests/test_memory_stats.py`
  讀 `tonesoul/memory/stats.py` (99L)。記憶統計。

  - 測試統計計算
  - 至少 2 個測試

- [ ] **Task C**: 建立 `tests/test_openclaw_embeddings.py`
  讀 `tonesoul/memory/openclaw/embeddings.py` (68L)。OpenClaw 嵌入。

  - 測試嵌入生成
  - 至少 2 個測試

- [ ] **Task D**: 建立 `tests/test_concept_store.py`
  讀 `tonesoul/semantic/concept_store.py` (92L)。概念儲存。

  - 測試概念 CRUD
  - 至少 3 個測試

- [ ] **Task E**: 建立 `tests/test_semantic_embedder.py`
  讀 `tonesoul/semantic/embedder.py` (80L)。語義嵌入器。

  - 測試嵌入計算
  - 至少 2 個測試

- [ ] **Task F**: 建立 `tests/test_perspective_axiomatic_inference.py`
  讀 `tonesoul/council/perspectives/axiomatic_inference.py` (70L)。公理推理觀點。

  - 測試推理邏輯
  - 至少 2 個測試

- [ ] **Task G**: 建立 `tests/test_perspective_critic.py`
  讀 `tonesoul/council/perspectives/critic.py` (68L)。批評者觀點。

  - 測試批評生成
  - 至少 2 個測試

- [ ] **Task H**: 建立 `tests/test_perspective_advocate.py`
  讀 `tonesoul/council/perspectives/advocate.py` (46L)。倡議者觀點。

  - 至少 2 個測試

- [ ] **Task I**: 建立 `tests/test_async_queue.py`
  讀 `tonesoul/shared/async_queue.py` (139L)。非同步佇列。

  - 測試 enqueue / dequeue
  - 測試容量限制
  - 至少 3 個測試

- [ ] **Task J**: 建立 `tests/test_shared_errors.py`
  讀 `tonesoul/shared/errors.py` (66L)。共用錯誤定義。

  - 測試各 Exception 類別
  - 至少 2 個測試

- [ ] **Task K**: 建立 `tests/test_issue_codes.py`
  讀 `tonesoul/issue_codes.py` (96L)。問題代碼定義。

  - 測試代碼格式
  - 至少 2 個測試

- [ ] **Task L**: 建立 `tests/test_corpus_schema.py`
  讀 `tonesoul/evolution/corpus_schema.py` (48L)。語料庫 Schema。

  - 測試 schema 驗證
  - 至少 2 個測試

- [ ] **Task M**: 建立 `tests/test_action_set_module.py`
  讀 `tonesoul/action_set.py` (32L)。行動集定義。
  注意：已有 `test_action_set` 但可能不覆蓋此檔。檢查後決定是否需要新測試。

  - 至少 1 個測試

- [ ] **Task N**: 建立 `tests/test_tonesoul_config.py`
  讀 `tonesoul/config.py` (64L)。全域設定。

  - 測試設定載入
  - 至少 2 個測試

### 成功標準
- [ ] 14 個新測試檔，共 25+ 測試通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 571): final convergence — 14 tail modules fully covered`

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

- 所有模組的 import 路徑已確認存在
- LLM 客戶端（ollama_client, lmstudio_client）依賴外部服務 — **必須** mock HTTP 調用，用 `monkeypatch` 替換 `httpx.Client` 或 `requests.Session`
- Market 模組可能依賴外部資料 — mock 掉所有 I/O
- YSTM 模組多為純計算，直接測即可
- 小模組（<100L）可以精簡測試，每檔 2-3 個 test 足夠
- `ystm_demo.py` 只有 5L，如果只是 import 入口，1 個 smoke test 即可
- 測試命名請保持 `test_[模組名].py` 或 `test_[子系統]_[模組名].py` 格式
- 如果某模組的測試檔名會與已存在的衝突（如 `test_action_set` 已存在），請用 `test_action_set_module.py` 避免衝突
- 每次 commit 前必須跑 `ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q`
- 參考前幾輪的測試風格（class 分組、monkeypatch mock、tmp_path fixture）
