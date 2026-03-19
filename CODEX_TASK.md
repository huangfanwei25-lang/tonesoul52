# Codex Task: Phase 548-553 — Bulk Test Coverage + Contract Normalization

**指派者**: 痕 (Hén)
**日期**: 2026-03-19
**分支**: `feat/env-perception`（繼續使用，不可 push 到 master）
**前置條件**: 1860 tests passing, lint clean

> **本次工單為大量批次任務。6 個 Phase，按順序執行。**
> 每完成一個 Phase 就 commit 一次，不要累積。

---

## 脈絡（先讀這些）

1. `tonesoul/unified_pipeline.py` — 主推理管線，理解 dispatch_trace 結構和 lazy getter 模式
2. `tonesoul/governance/kernel.py` — 治理核心，理解 routing_trace 結構
3. `tonesoul/contract_observer.py` — 輸出契約驗證器，理解 ContractVerifier API
4. `tonesoul/safe_parse.py` — JSON 安全解析，理解 parse_llm_response 的 fallback 行為
5. `tonesoul/frame_router.py` — 框架路由器，理解 route_frames + build_frame_plan
6. `tonesoul/perception/web_ingest.py` — Web 收集器，理解 WebIngestor 的 async/sync API
7. `tonesoul/seed_schema_check.py` — 種子 schema 驗證
8. `tonesoul/generation_orch.py` — 執行報告生成器
9. `tonesoul/mercy_objective.py` — 仁慈目標權重解析
10. `tonesoul/soul_persistence.py` — Soul 持久層接口
11. `tonesoul/vow_inventory.py` — 誓約信念狀態追蹤
12. `tonesoul/status_alignment.py` — 狀態對齊追蹤
13. `tests/test_mirror.py` — 參考現有測試模式（mock + assertion 風格）
14. `tests/test_alert_escalation.py` — 參考大型測試檔的 class 分組模式
15. `AXIOMS.json` — 7 公理定義，contract_observer 用到

---

## Phase 548: Test Coverage — Safe Parse + Frame Router + Seed Schema (20+ tests)

為 3 個**核心工具模組**補齊測試。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_safe_parse.py`
  - `test_safe_parse_json_valid` — 正常 JSON 字串
  - `test_safe_parse_json_with_trailing_commas` — 尾部逗號自動清理
  - `test_safe_parse_json_from_markdown_codeblock` — \`\`\`json ... \`\`\` 包裹
  - `test_safe_parse_json_returns_none_on_garbage` — 完全無效輸入 → None
  - `test_parse_llm_response_extracts_object` — 從雜亂 LLM 回覆中提取 JSON
  - `test_parse_llm_response_strict_rejects_partial` — strict=True 拒絕部分匹配
  - `test_validate_dict_with_valid_schema` — dataclass 驗證成功
  - `test_validate_dict_missing_field` — 缺欄位 → 錯誤

- [ ] **Task B**: 建立 `tests/test_frame_router.py`
  - `test_score_frame_keyword_match` — 關鍵字匹配計分
  - `test_score_frame_no_match` — 無匹配 → 0 分
  - `test_route_frames_returns_top_n` — limit 參數限制返回數量
  - `test_route_frames_empty_registry` — 空 registry → 空列表
  - `test_build_frame_plan_structure` — 返回 dict 包含 frames, roles 等欄位
  - `test_build_frame_plan_with_role_catalog` — 角色目錄對齊
  - `test_role_alignment_known_unmatched` — 已知 vs 未匹配角色區分

- [ ] **Task C**: 建立 `tests/test_seed_schema_check.py`
  - `test_valid_seed_passes` — 完整 seed → 0 issues
  - `test_missing_required_key` — 缺必填欄位 → issue
  - `test_partial_seed_lists_all_missing` — 多欄位缺失 → 多 issue
  - `test_empty_seed` — 空 dict → 全部 issue
  - `test_main_with_valid_file` — CLI 入口正確退出碼

### 成功標準
- `ruff check tests/test_safe_parse.py tests/test_frame_router.py tests/test_seed_schema_check.py` → passed
- `pytest tests/test_safe_parse.py tests/test_frame_router.py tests/test_seed_schema_check.py -q` → 20+ passed
- `pytest tests/ -x` → 1880+ passed（無回歸）

---

## Phase 549: Test Coverage — Contract Observer + Generation Orch (25+ tests)

### 任務清單

- [ ] **Task A**: 建立 `tests/test_contract_observer.py`

  **ContractVerifier 類別**:
  - `test_verify_all_passes_clean_output` — 正常輸出通過所有契約
  - `test_verify_all_catches_absolute_claim` — "This is definitely..." → 失敗
  - `test_verify_all_catches_harmful_content` — 有害內容偵測
  - `test_verify_all_zone_filtering` — zone_trigger 過濾正確
  - `test_custom_contract_registration` — 自訂契約註冊

  **MultiScaleObserver 類別**:
  - `test_observe_returns_metrics` — 回傳 dict 含 short/medium 指標
  - `test_observe_accumulates_history` — 多次 observe 累積正確
  - `test_get_alert_none_when_stable` — 穩定狀態 → None
  - `test_get_alert_triggers_on_spike` — delta_s 突增 → alert
  - `test_reset_clears_history` — reset 清空

  **QualityTracker 類別**:
  - `test_record_and_snapshot` — record 後 take_snapshot 正確
  - `test_snapshot_trends` — 多次 record → 趨勢判斷
  - `test_get_summary_format` — summary dict 結構
  - `test_reset_clears_all` — 清空計數

  **頂層驗證函數**:
  - `test_check_no_absolute_claims_passes` — 正常文本通過
  - `test_check_no_absolute_claims_fails` — "absolutely", "definitely" 等被捕捉
  - `test_check_uncertainty_disclosure_passes` — 含 "I think", "might" 等
  - `test_check_uncertainty_disclosure_fails` — 無任何不確定表達
  - `test_check_no_harmful_content_passes` — 安全文本
  - `test_check_structured_response_passes` — 結構化回覆

- [ ] **Task B**: 建立 `tests/test_generation_orch.py`
  - `test_build_execution_report_minimal` — 最小參數 → 報告字串
  - `test_build_execution_report_with_frame_plan` — 含 frame_plan → 結構完整
  - `test_build_execution_report_with_error_event` — 錯誤事件 ID 注入
  - `test_build_execution_report_with_skills` — skills_applied 列表渲染
  - `test_record_error_event_creates_entry` — 錯誤事件記錄 (用 tmp 文件)

### 成功標準
- `ruff check tests/test_contract_observer.py tests/test_generation_orch.py` → passed
- `pytest tests/test_contract_observer.py tests/test_generation_orch.py -q` → 25+ passed
- `pytest tests/ -x` → 1905+ passed（無回歸）

---

## Phase 550: Test Coverage — Mercy Objective + Web Ingest + Soul Persistence (18+ tests)

### 任務清單

- [ ] **Task A**: 建立 `tests/test_mercy_objective.py`
  - `test_resolve_mercy_objective_default_weights` — 預設權重回傳合理值
  - `test_resolve_mercy_objective_with_signals` — 自訂信號影響輸出
  - `test_resolve_mercy_objective_with_overrides` — weight_overrides 覆寫
  - `test_decision_mode_returns_string` — _decision_mode 返回合法模式
  - `test_normalize_weights_sums_to_one` — 權重正規化後總和 ≈ 1.0
  - `test_clamp_boundary_values` — 0.0 和 1.0 邊界

- [ ] **Task B**: 建立 `tests/test_web_ingest.py`
  ⚠️ **注意**: `WebIngestor` 依賴外部套件 Crawl4AI，測試必須 mock 或 skip。不可真的發 HTTP 請求。
  - `test_ingest_result_dataclass_defaults` — 預設值正確
  - `test_ingest_result_post_init_hash` — __post_init__ 計算 content_hash
  - `test_is_available_without_crawl4ai` — Crawl4AI 不存在 → False
  - `test_ingest_urls_sync_mock` — mock 外部呼叫，驗證回傳結構
  - `test_ingest_error_handling` — URL 失敗 → IngestResult.success=False
  - `test_max_content_length_truncation` — 長內容截斷

- [ ] **Task C**: 建立 `tests/test_soul_persistence.py`
  讀 `tonesoul/soul_persistence.py` 理解 API 後寫測試。
  - 至少 6 個測試覆蓋：初始化、儲存、讀取、不存在 key、覆寫、清除

### 成功標準
- `ruff check tests/test_mercy_objective.py tests/test_web_ingest.py tests/test_soul_persistence.py` → passed
- `pytest tests/test_mercy_objective.py tests/test_web_ingest.py tests/test_soul_persistence.py -q` → 18+ passed
- `pytest tests/ -x` → 1923+ passed（無回歸）

---

## Phase 551: Contract Normalization — dispatch_trace 標準化 (6 modules)

**目標**: 統一 `dispatch_trace` 的返回結構，讓所有產出 trace 的模組遵守同一 schema。

### 任務清單

- [ ] **Task A**: 在 `tonesoul/schemas.py` 新增 `DispatchTraceSection` TypedDict
  ```python
  class DispatchTraceSection(TypedDict, total=False):
      component: str          # 產出此 section 的模組名
      timestamp: str          # ISO 8601
      status: str             # "ok" | "degraded" | "error"
      detail: Dict[str, Any]  # 模組特定資料
  ```

- [ ] **Task B**: 在 `tonesoul/unified_pipeline.py` 的 `process()` 方法中，
  確保每個寫入 `dispatch_trace` 的地方都包含 `component` 和 `timestamp` 欄位。
  目前有寫入 trace 的位置包括：
  - `dispatch_trace["alert"]` — 補上 `component="alert_escalation"`, `timestamp`
  - `dispatch_trace["action_set"]` — 補上 `component="action_set"`, `timestamp`
  - `dispatch_trace["drift"]` — 補上 `component="drift_monitor"`, `timestamp`
  - `dispatch_trace["suppressed_errors"]` — 補上 `component="exception_trace"`, `timestamp`
  - `dispatch_trace["trajectory"]` — 補上 `component="trajectory"`, `timestamp`
  - `dispatch_trace["soul_integral"]` — 補上 `component="tension_engine"`, `timestamp`
  ⚠️ **不要改變 `detail` 內容**，只是外加 `component` + `timestamp` 包裹。

- [ ] **Task C**: 在 `tonesoul/governance/kernel.py` 的 `build_routing_trace()` 中，
  對 `routing_trace` 做同樣的 `component` + `timestamp` 標準化。

- [ ] **Task D**: 更新相關測試中的 assertion 以適應新欄位
  - 不可破壞現有 assertion（新欄位是 additive）
  - 新增 assertion 確認 `component` 和 `timestamp` 存在

- [ ] **Task E**: 建立 `tests/test_dispatch_trace_contract.py` (10+ tests)
  - `test_all_trace_sections_have_component` — process() 後檢查所有 section
  - `test_all_trace_sections_have_timestamp` — ISO 8601 格式驗證
  - `test_trace_section_status_values` — 只允許 "ok" | "degraded" | "error"
  - `test_routing_trace_has_component` — kernel routing trace 也有 component
  - `test_trace_backward_compatible` — 原有欄位仍存在

### 成功標準
- `ruff check tonesoul/schemas.py tonesoul/unified_pipeline.py tonesoul/governance/kernel.py tests/test_dispatch_trace_contract.py` → passed
- `pytest tests/test_dispatch_trace_contract.py -q` → 10+ passed
- `pytest tests/ -x` → 1933+ passed（無回歸）

---

## Phase 552: Vow Conviction Lifecycle + Status Alignment Tests (20+ tests)

### 任務清單

- [ ] **Task A**: 擴展或建立 `tests/test_vow_inventory.py`
  讀 `tonesoul/vow_system.py` + `tonesoul/vow_inventory.py` 理解全部 API。

  **VowInventory 測試**:
  - `test_vow_conviction_state_creation` — VowConvictionState dataclass 初始值
  - `test_register_vow_and_retrieve` — 註冊 → 取回
  - `test_conviction_score_update` — 更新信念分數
  - `test_conviction_window_sliding` — 30 輪窗口正確滑動
  - `test_average_conviction_calculation` — 平均值計算正確
  - `test_vow_trajectory_tracking` — 軌跡追蹤紀錄
  - `test_multiple_vows_independent` — 多誓約互不影響
  - `test_empty_inventory_summary` — 空倉庫 → 空摘要

  **VowSystem 測試** (如有額外 API):
  - `test_vow_creation_with_context` — 帶脈絡建立誓約
  - `test_vow_breach_detection` — 違約偵測

- [ ] **Task B**: 建立 `tests/test_status_alignment.py`
  讀 `tonesoul/status_alignment.py` 理解 API。
  - 至少 10 個測試：初始對齊、偏移檢測、校正機制、邊界值、多維對齊

### 成功標準
- `ruff check tests/test_vow_inventory.py tests/test_status_alignment.py` → passed
- `pytest tests/test_vow_inventory.py tests/test_status_alignment.py -q` → 20+ passed
- `pytest tests/ -x` → 1953+ passed（無回歸）

---

## Phase 553: Council Coherence + Deliberation Gravity Tests (20+ tests)

### 任務清單

- [ ] **Task A**: 建立 `tests/test_council_coherence.py`
  讀 `tonesoul/council/coherence.py` 理解 API。
  - `test_coherence_score_unanimous` — 全票一致 → 高分
  - `test_coherence_score_split` — 意見分裂 → 低分
  - `test_coherence_score_empty_votes` — 空投票 → 安全預設
  - `test_coherence_with_abstentions` — 棄權票處理
  - `test_coherence_boundary_values` — 0.0 和 1.0 邊界
  - `test_coherence_weights_applied` — 權重影響
  - `test_coherence_consistent_deterministic` — 相同輸入 → 相同輸出
  - `test_coherence_single_perspective` — 只有一個視角
  - `test_coherence_with_tension_data` — 含張力數據
  - `test_coherence_score_normalized` — 分數在 [0,1] 範圍

- [ ] **Task B**: 建立 `tests/test_deliberation_gravity.py`
  讀 `tonesoul/deliberation/gravity.py` 理解 API。
  - `test_gravity_synthesize_basic` — 基本合成呼叫
  - `test_gravity_weighs_perspectives` — 權重影響合成結果
  - `test_gravity_handles_empty_input` — 空輸入 → graceful fallback
  - `test_gravity_handles_single_voice` — 單一聲音 → 直接採用
  - `test_gravity_conflict_resolution` — 衝突聲音的合成策略
  - `test_gravity_semantic_field_conservation` — 語義場守恆（Axiom 7）
  - `test_gravity_tension_preserved` — 張力保留（Axiom 4: 非零張力）
  - `test_gravity_deterministic` — 相同輸入 → 相同輸出
  - `test_gravity_output_structure` — 輸出結構包含必要欄位
  - `test_gravity_graceful_on_exception` — 內部異常不崩潰

### 成功標準
- `ruff check tests/test_council_coherence.py tests/test_deliberation_gravity.py` → passed
- `pytest tests/test_council_coherence.py tests/test_deliberation_gravity.py -q` → 20+ passed
- `pytest tests/ -x` → 1973+ passed（無回歸）

---

## 禁止事項（所有 Phase 通用）

- ❌ 不可修改 `AGENTS.md`, `CODEX_PROTOCOL.md`, `.env`, `.gitignore`
- ❌ 不可改變現有 API 的 return type（只可 additive 增加欄位）
- ❌ 不可安裝新的 pip 套件
- ❌ 不可刪除任何現有測試
- ❌ 不可在 `unified_pipeline.py` 中改變控制流（if/else 分支順序）
- ❌ 不可 push 到 master
- ❌ Phase 551 的 dispatch_trace 標準化只加欄位，不改 detail 內容

## 技術提示

### 測試模式參考
```python
# 標準 mock 模式（參考 tests/test_mirror.py）
from unittest.mock import MagicMock, patch

class TestSomeFeature:
    def test_basic(self):
        obj = SomeClass()
        result = obj.method(input)
        assert result["key"] == expected

# Dataclass 測試模式
def test_dataclass_defaults():
    dc = MyDataclass(required_field="x")
    assert dc.optional_field == default_value

# 異常路徑模式
def test_graceful_fallback():
    with patch("tonesoul.module.dependency", side_effect=Exception("boom")):
        result = function_under_test()
    assert result is not None  # 沒有崩潰
```

### dispatch_trace 標準化模式 (Phase 551)
```python
from datetime import datetime, timezone

# 加入方式：
dispatch_trace["alert"] = {
    "component": "alert_escalation",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": "ok",
    "detail": { ... 原有內容 ... }
}
```

### 重要注意
- `safe_parse.py` 的 `_extract_balanced_json_object` 用了手動括號匹配，測試要覆蓋巢狀 JSON
- `contract_observer.py` 的 check 函數用了 regex，測試要覆蓋 edge case
- `web_ingest.py` 必須 mock Crawl4AI（不可真的發 HTTP 請求）
- `frame_router.py` 的 `_score_frame` 是計分核心，測試要覆蓋多種 frame+context 組合
- 每個 Phase commit 一次，message 格式: `test(Phase NNN): [描述]`

### Commit Message 格式
```
Phase 548: test(Phase 548): safe_parse + frame_router + seed_schema tests
Phase 549: test(Phase 549): contract_observer + generation_orch tests
Phase 550: test(Phase 550): mercy_objective + web_ingest + soul_persistence tests
Phase 551: feat(Phase 551): dispatch_trace contract normalization
Phase 552: test(Phase 552): vow_conviction + status_alignment tests
Phase 553: test(Phase 553): council_coherence + deliberation_gravity tests
```
