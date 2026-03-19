# Codex Task: Phase 554-559 — ✅ 已完成 (2026-03-19 審核通過)

> **審核者**: 痕 (Hén)
> **審核日期**: 2026-03-19
> **結果**: ✅ ALL 6 PHASES PASS — 169 新測試，1975 → 2144，lint clean，無回歸
>
> | Phase | Commit | 新測試 | 累積 |
> |-------|--------|--------|------|
> | 554 | `3f9e4e4` | 39 | 2014 |
> | 555 | `5c8cd9a` | 29 | 2043 |
> | 556 | `1931b96` | 38 | 2081 |
> | 557 | `dd63a3d` | 31 | 2112 |
> | 558 | `91b0f80` | 8 | 2120 |
> | 559 | `433d7bd` | 24 | 2144 |
>
> 下一輪工單待指派。

---

## 原始工單（保留參考）

**指派者**: 痕 (Hén)
**日期**: 2026-03-19
**分支**: `feat/env-perception`
**前置條件**: 1975 tests passing, lint clean

> 系統收斂任務。6 個 Phase，按順序執行。
> **目標：消除 11 個核心模組的測試盲區，清理死碼，硬化模組邊界。**

---

## 脈絡（先讀這些）

1. `tonesoul/memory_manager.py` (652L) — 記憶管理器，最大未測模組
2. `tonesoul/persona_dimension.py` (447L) — 人格維度空間，DriftMonitor 依賴
3. `tonesoul/semantic_control.py` (404L) — 語義控制層，pipeline 輔助
4. `tonesoul/benevolence.py` (385L) — 仁慈裁決引擎
5. `tonesoul/skill_promoter.py` (375L) — 技能晉升管線
6. `tonesoul/audit_interface.py` (356L) — 審計接口
7. `tonesoul/council_capability.py` (314L) — Council 能力聲明
8. `tonesoul/evidence_collector.py` (265L) — 證據蒐集器
9. `tonesoul/intent_verification.py` (257L) — 意圖驗證
10. `tonesoul/jump_monitor.py` (212L) — 奇點跳躍偵測
11. `tonesoul/escalation.py` (113L) — 升級策略
12. `tonesoul/council_adapter.py` (45L) — **0 imports，疑似死碼**
13. `tonesoul/tonesoul_llm.py` (295L) — **0 imports，疑似死碼**
14. `tests/test_alert_escalation.py` — 參考大型測試檔的 class 分組模式
15. `tests/test_dispatch_trace_contract.py` — 參考 dispatch_trace 測試模式

---

## Phase 554: Test Coverage — Memory Manager + Persona Dimension (25+ tests)

為系統中**最大的兩個未測模組**補齊測試。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_memory_manager.py`
  讀 `tonesoul/memory_manager.py` (652L) 理解全部 API。這是記憶管理器，負責記憶的存取、索引、淘汰。

  - `test_init_default_config` — 預設配置初始化
  - `test_store_memory_basic` — 基本記憶存入
  - `test_retrieve_memory_by_key` — 按 key 取回
  - `test_retrieve_nonexistent_key` — 不存在的 key → None / 空
  - `test_store_and_overwrite` — 覆寫已有 key
  - `test_memory_index_consistency` — 索引與實際記憶一致
  - `test_memory_eviction_policy` — 淘汰策略（如有 LRU/freshness）
  - `test_bulk_store_and_list` — 批量存入 → 列表正確
  - `test_clear_all_memories` — 清空操作
  - `test_memory_search_by_tag` — 按標籤搜尋（如有）
  - `test_memory_persistence_roundtrip` — 存→取→比較一致
  - `test_memory_metadata_preserved` — metadata 欄位保留
  - `test_concurrent_access_safety` — 多次快速存取不崩潰

- [ ] **Task B**: 建立 `tests/test_persona_dimension.py`
  讀 `tonesoul/persona_dimension.py` (447L) 理解 API。這是人格維度空間模組，DriftMonitor 依賴它。

  - `test_persona_vector_creation` — 向量初始化
  - `test_persona_distance_calculation` — 兩點間距離
  - `test_persona_normalize` — 向量正規化
  - `test_persona_drift_detection` — 漂移偵測（與 DriftMonitor 的接口）
  - `test_persona_boundary_clamp` — 邊界值限制
  - `test_persona_dimension_names` — 維度名稱對應正確
  - `test_persona_interpolation` — 兩向量插值
  - `test_persona_zero_vector` — 零向量邊界
  - `test_persona_high_dimensional` — 多維空間不崩潰
  - `test_persona_serialization` — 序列化/反序列化
  - `test_persona_ema_update` — EMA 更新（如有 exponential moving average）
  - `test_persona_snapshot` — 快照功能

### 成功標準
- `ruff check tests/test_memory_manager.py tests/test_persona_dimension.py` → passed
- `pytest tests/test_memory_manager.py tests/test_persona_dimension.py -q` → 25+ passed
- `pytest tests/ -x` → 2000+ passed（無回歸）

---

## Phase 555: Test Coverage — Semantic Control + Benevolence + Escalation (22+ tests)

### 任務清單

- [ ] **Task A**: 建立 `tests/test_semantic_control.py`
  讀 `tonesoul/semantic_control.py` (404L) 理解 API。語義控制層，管理語義場約束。

  - `test_semantic_control_init` — 初始化不崩潰
  - `test_apply_control_basic` — 基本控制施加
  - `test_control_constraint_enforcement` — 約束執行
  - `test_control_boundary_violation` — 邊界違反偵測
  - `test_control_passthrough_clean` — 乾淨輸入通過
  - `test_control_multiple_constraints` — 多重約束同時施加
  - `test_control_report_structure` — 控制報告結構正確
  - `test_control_graceful_on_error` — 異常不崩潰

- [ ] **Task B**: 建立 `tests/test_benevolence.py`
  讀 `tonesoul/benevolence.py` (385L) 理解 API。仁慈裁決引擎，判斷是否應展現善意。

  - `test_benevolence_score_neutral` — 中性輸入 → 中性分數
  - `test_benevolence_score_positive` — 正面情境 → 高分
  - `test_benevolence_score_negative` — 負面情境 → 低分
  - `test_benevolence_override_by_axiom` — 公理覆寫
  - `test_benevolence_boundary_values` — 0.0 和 1.0 邊界
  - `test_benevolence_weights_structure` — 權重結構驗證
  - `test_benevolence_deterministic` — 相同輸入 → 相同輸出

- [ ] **Task C**: 建立 `tests/test_escalation.py`
  讀 `tonesoul/escalation.py` (113L) 理解 API。升級策略模組。

  - `test_escalation_level_determination` — 等級判定
  - `test_escalation_threshold_boundary` — 門檻邊界
  - `test_escalation_step_up` — 逐級升級
  - `test_escalation_step_down` — 降級
  - `test_escalation_max_level` — 最高等級限制
  - `test_escalation_default_state` — 初始狀態
  - `test_escalation_summary` — 摘要結構

### 成功標準
- `ruff check tests/test_semantic_control.py tests/test_benevolence.py tests/test_escalation.py` → passed
- `pytest tests/test_semantic_control.py tests/test_benevolence.py tests/test_escalation.py -q` → 22+ passed
- `pytest tests/ -x` → 2022+ passed（無回歸）

---

## Phase 556: Test Coverage — Skill Promoter + Audit Interface + Council Capability (20+ tests)

### 任務清單

- [ ] **Task A**: 建立 `tests/test_skill_promoter.py`
  讀 `tonesoul/skill_promoter.py` (375L) 理解 API。技能晉升管線。

  - `test_skill_promotion_eligible` — 合格技能晉升
  - `test_skill_promotion_ineligible` — 不合格 → 拒絕
  - `test_skill_promotion_criteria` — 晉升條件檢查
  - `test_skill_score_calculation` — 分數計算
  - `test_skill_promotion_history` — 晉升歷史追蹤
  - `test_skill_demotion` — 降級機制（如有）
  - `test_skill_list_sorted` — 排序正確

- [ ] **Task B**: 建立 `tests/test_audit_interface.py`
  讀 `tonesoul/audit_interface.py` (356L) 理解 API。審計接口。

  - `test_audit_record_creation` — 記錄建立
  - `test_audit_record_fields` — 必要欄位存在
  - `test_audit_query_by_time` — 按時間查詢
  - `test_audit_query_by_component` — 按組件查詢
  - `test_audit_summary_structure` — 摘要結構
  - `test_audit_empty_log` — 空日誌 → 安全回傳

- [ ] **Task C**: 建立 `tests/test_council_capability.py`
  讀 `tonesoul/council_capability.py` (314L) 理解 API。Council 能力聲明。

  - `test_capability_declaration` — 能力宣告
  - `test_capability_query` — 能力查詢
  - `test_capability_match_role` — 能力與角色匹配
  - `test_capability_unknown_role` — 未知角色 → 安全處理
  - `test_capability_list_all` — 列出所有能力
  - `test_capability_deterministic` — 相同輸入 → 相同輸出
  - `test_capability_empty_registry` — 空 registry → 安全回傳

### 成功標準
- `ruff check tests/test_skill_promoter.py tests/test_audit_interface.py tests/test_council_capability.py` → passed
- `pytest tests/test_skill_promoter.py tests/test_audit_interface.py tests/test_council_capability.py -q` → 20+ passed
- `pytest tests/ -x` → 2042+ passed（無回歸）

---

## Phase 557: Test Coverage — Evidence Collector + Intent Verification + Jump Monitor (22+ tests)

### 任務清單

- [ ] **Task A**: 建立 `tests/test_evidence_collector.py`
  讀 `tonesoul/evidence_collector.py` (265L) 理解 API。證據蒐集器。

  - `test_collect_evidence_basic` — 基本蒐集
  - `test_evidence_dedup` — 重複證據去重
  - `test_evidence_ranking` — 證據排序
  - `test_evidence_source_tracking` — 來源追蹤
  - `test_evidence_empty_input` — 空輸入 → 空結果
  - `test_evidence_max_capacity` — 容量限制
  - `test_evidence_summary` — 摘要結構
  - `test_evidence_filter_by_type` — 按類型過濾

- [ ] **Task B**: 建立 `tests/test_intent_verification.py`
  讀 `tonesoul/intent_verification.py` (257L) 理解 API。意圖驗證模組。

  - `test_verify_intent_match` — 意圖匹配
  - `test_verify_intent_mismatch` — 意圖不匹配 → 失敗
  - `test_verify_intent_ambiguous` — 模糊意圖處理
  - `test_verification_confidence_score` — 信心分數
  - `test_verification_report_structure` — 報告結構
  - `test_verification_empty_context` — 空脈絡 → 安全處理
  - `test_verification_multiple_intents` — 多意圖場景

- [ ] **Task C**: 建立 `tests/test_jump_monitor.py`
  讀 `tonesoul/jump_monitor.py` (212L) 理解 API。奇點跳躍偵測。

  - `test_jump_detection_normal` — 正常波動 → 不觸發
  - `test_jump_detection_spike` — 突變 → 觸發
  - `test_jump_threshold_boundary` — 門檻邊界
  - `test_jump_cooldown` — 冷卻期
  - `test_jump_history_tracking` — 歷史追蹤
  - `test_jump_reset` — 重置
  - `test_jump_summary` — 摘要結構

### 成功標準
- `ruff check tests/test_evidence_collector.py tests/test_intent_verification.py tests/test_jump_monitor.py` → passed
- `pytest tests/test_evidence_collector.py tests/test_intent_verification.py tests/test_jump_monitor.py -q` → 22+ passed
- `pytest tests/ -x` → 2064+ passed（無回歸）

---

## Phase 558: Dead Code Audit + Deprecation Markers (8+ tests)

**目標**: 驗證並標記死碼模組，為未來清理做準備。

### 任務清單

- [ ] **Task A**: 驗證 `tonesoul/council_adapter.py` (45L, 0 imports)
  1. 搜索全 codebase 確認無使用（`grep -r "council_adapter" tonesoul/ tests/`）
  2. 如確認無使用，在檔案頂部加 deprecation 警告：
     ```python
     import warnings
     warnings.warn(
         "council_adapter is deprecated and scheduled for removal. "
         "Use tonesoul.council.perspectives directly.",
         DeprecationWarning,
         stacklevel=2,
     )
     ```
  3. 建立 `tests/test_council_adapter_deprecated.py`：
     - `test_import_emits_deprecation_warning` — import 時觸發 DeprecationWarning
     - `test_module_still_importable` — 不崩潰

- [ ] **Task B**: 驗證 `tonesoul/tonesoul_llm.py` (295L, 0 imports)
  1. 搜索全 codebase 確認無使用
  2. 如確認無使用，在檔案頂部加 deprecation 警告（同上模式）
  3. 建立 `tests/test_tonesoul_llm_deprecated.py`：
     - `test_import_emits_deprecation_warning`
     - `test_module_still_importable`

- [ ] **Task C**: 驗證 `tonesoul/market/forecaster.py` 和 `tonesoul/market/gold_detector.py`
  1. 搜索全 codebase 確認使用狀況
  2. 如為孤立模組（不影響主管線），加 deprecation 警告
  3. 建立 `tests/test_market_deprecation.py`：
     - `test_forecaster_import_warning`
     - `test_gold_detector_import_warning`

- [ ] **Task D**: 修復 `dispatch_trace["repair_eligible"]` 一致性問題
  在 `tonesoul/unified_pipeline.py` 中，`dispatch_trace["repair_eligible"] = True` 是唯一未經 `_build_trace_section()` 包裹的寫入。
  改為使用 `_build_trace_section()` 包裹，或移入 `dispatch_trace["repair"]["detail"]` 中。
  ⚠️ 不可改變語義，只做結構標準化。

### 成功標準
- `ruff check` 相關檔案 → passed
- deprecation warning 測試全過
- `dispatch_trace["repair_eligible"]` 已標準化
- `pytest tests/ -x` → 2072+ passed（無回歸）

---

## Phase 559: YSS Pipeline 收斂測試 (15+ tests)

`yss_pipeline.py` (1091L) 和 `yss_gates.py` (940L) 是兩個大型未測模組。它們是 YSS (語魂脊柱系統) 的核心管線。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_yss_pipeline.py`
  讀 `tonesoul/yss_pipeline.py` 理解 API。

  - `test_yss_pipeline_init` — 初始化不崩潰
  - `test_yss_pipeline_process_minimal` — 最小輸入處理
  - `test_yss_pipeline_output_structure` — 輸出結構正確
  - `test_yss_pipeline_stage_sequence` — 階段順序正確
  - `test_yss_pipeline_error_in_stage` — 單階段錯誤 → 安全降級
  - `test_yss_pipeline_empty_input` — 空輸入 → 安全處理
  - `test_yss_pipeline_context_propagation` — 上下文傳遞
  - `test_yss_pipeline_trace_output` — 追蹤輸出

- [ ] **Task B**: 建立 `tests/test_yss_gates.py`
  讀 `tonesoul/yss_gates.py` 理解 API。

  - `test_gate_pass_condition` — 通過條件
  - `test_gate_block_condition` — 阻擋條件
  - `test_gate_threshold_boundary` — 門檻邊界值
  - `test_gate_chain_execution` — 多閘門連鎖
  - `test_gate_bypass_flag` — bypass 旗標（如有）
  - `test_gate_report_structure` — 報告結構
  - `test_gate_graceful_on_error` — 異常不崩潰

### 成功標準
- `ruff check tests/test_yss_pipeline.py tests/test_yss_gates.py` → passed
- `pytest tests/test_yss_pipeline.py tests/test_yss_gates.py -q` → 15+ passed
- `pytest tests/ -x` → **2087+ passed（無回歸）**

---

## 禁止事項（所有 Phase 通用）

- ❌ 不可修改 `AGENTS.md`, `CODEX_PROTOCOL.md`, `.env`, `.gitignore`
- ❌ 不可改變現有 API 的 return type（只可 additive 增加欄位）
- ❌ 不可安裝新的 pip 套件
- ❌ 不可刪除任何現有測試
- ❌ 不可在 `unified_pipeline.py` 中改變控制流（if/else 分支順序）
- ❌ 不可 push 到 master
- ❌ Phase 558 的死碼清理只加 deprecation 警告，**不可刪除檔案**
- ❌ Phase 558 的 dispatch_trace 修復只做結構標準化，不改語義

## 技術提示

### 測試模式參考
```python
# 標準 mock 模式（參考 tests/test_alert_escalation.py）
from unittest.mock import MagicMock, patch

class TestSomeFeature:
    def test_basic(self):
        obj = SomeClass()
        result = obj.method(input)
        assert result["key"] == expected

# Deprecation 測試模式 (Phase 558)
import warnings
def test_import_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        import tonesoul.council_adapter  # noqa: F401
        dep_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(dep_warnings) >= 1
        assert "deprecated" in str(dep_warnings[0].message).lower()

# 異常路徑模式
def test_graceful_fallback():
    with patch("tonesoul.module.dependency", side_effect=Exception("boom")):
        result = function_under_test()
    assert result is not None  # 沒有崩潰
```

### 重要注意
- `memory_manager.py` 是 652 行的大模組，需要仔細讀 API 後再寫測試
- `persona_dimension.py` 被 `drift_monitor.py` 依賴 — 測試要確認 DriftMonitor 的接口能正常調用
- `yss_pipeline.py` (1091L) 和 `yss_gates.py` (940L) 是大型模組，先讀 class 和 public method，再逐一測試
- Phase 558 的死碼驗證必須先做 grep 確認，不可假設
- 每個 Phase commit 一次，message 格式: `test(Phase NNN): [描述]`

### Commit Message 格式
```
Phase 554: test(Phase 554): memory_manager + persona_dimension tests
Phase 555: test(Phase 555): semantic_control + benevolence + escalation tests
Phase 556: test(Phase 556): skill_promoter + audit_interface + council_capability tests
Phase 557: test(Phase 557): evidence_collector + intent_verification + jump_monitor tests
Phase 558: refactor(Phase 558): dead code deprecation + dispatch_trace consistency
Phase 559: test(Phase 559): yss_pipeline + yss_gates convergence tests
```
