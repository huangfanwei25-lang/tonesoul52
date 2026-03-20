# Codex Task: Phase 578-581 — Deprecated 模組移除

**指派者**: 痕 (Hén)
**日期**: 2026-03-20
**分支**: feat/env-perception（不可 push 到 master）
**前置條件**: 2572 tests passing, lint clean

---

## 全局規則

1. **每個 Phase 單獨 commit**，commit message 格式：`refactor(Phase N): [摘要]`
2. 每個 Phase 完成後：`ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q` 全過
3. 測試數會因移除 deprecated 測試檔而下降 — 這是預期行為。預期最終 ≥ 2520
4. **禁止修改** `governance/kernel.py`、`unified_pipeline.py`、`AGENTS.md`、`CODEX_PROTOCOL.md`
5. **禁止修改** `tonesoul/inter_soul/` — 這是 Phase 582-583 已審核通過的套件
6. 連續失敗 3 次 → 停下，寫 CODEX_HANDBACK.md

---

## Phase 578: 移除 council_adapter.py + tonesoul_llm.py

**脈絡**: 這兩個模組是最薄的 deprecated 包裝，僅被自身的 deprecated 測試引用。

### 任務
- [ ] 刪除 `tonesoul/council_adapter.py`
- [ ] 刪除 `tests/test_council_adapter_deprecated.py`
- [ ] 刪除 `tonesoul/tonesoul_llm.py`
- [ ] 刪除 `tests/test_tonesoul_llm_deprecated.py`
- [ ] 更新 `scripts/healthcheck.py` — 從模組清單中移除 `"tonesoul.tonesoul_llm"` 那行
- [ ] 確認 `tonesoul/__init__.py` 沒有 re-export 這兩個模組
- [ ] ruff + pytest 全過

### 禁止
- ❌ 不可修改 `tonesoul/council/runtime.py`（Phase 579 處理）
- ❌ 不可刪除 `tonesoul_simple_app.py` 或 `tonesoul_simple_bridge.py`（引用的是 `tonesoul52`，不是本次目標）

---

## Phase 579: 遷移 build_council_summary → council/runtime.py，移除 role_council.py

**脈絡**: `tonesoul/role_council.py` 有一個核心函數 `build_council_summary()`（~54 行）被兩處活躍碼使用：
1. `tonesoul/council/runtime.py` L12 — `from ..role_council import build_council_summary`
2. `tonesoul/frame_router.py` L8 — `from .role_council import build_council_summary`

`council/runtime.py` 已有 `_build_role_summary()` 包裝方法，是自然的吸收點。

### 任務
- [ ] 將 `build_council_summary()` 及其所有輔助函數（`_decision_mode`, `_collect_operational_roles` 等）從 `role_council.py` 搬到 `council/runtime.py` 的模組層級
- [ ] 更新 `council/runtime.py` — 移除 `from ..role_council import build_council_summary`，改用本地定義
- [ ] 更新 `frame_router.py` — 改 import 來源：`from .council.runtime import build_council_summary`
- [ ] 保留 `merged["role_council"]` 鍵名不變（向後相容 transcript 結構）
- [ ] 刪除 `tonesoul/role_council.py`
- [ ] 刪除 `tests/test_role_council_integration.py`
- [ ] 檢查 `tests/test_council_runtime.py` — 若有 `role_council` 字串引用，確認它是 transcript 鍵名（保留）還是 import 路徑（更新）
- [ ] 檢查 `tests/test_custom_role_council.py` — 如果它測的是 `tonesoul.role_council` 模組就刪除；如果測的是 council runtime 的 role 功能就保留
- [ ] ruff + pytest 全過

### 技術提示
- `build_council_summary` 簽名：`(context, selected_frames, role_summary, role_catalog) -> Dict[str, object]`
- 搬遷後確保 `_build_role_summary()` 方法仍然正確調用本地版本
- `run_role_council()` 是另一個 deprecated 包裝（L165），可以一起移除

---

## Phase 580: 移除 unified_core.py + _legacy/unified_core_compat.py

**脈絡**: `UnifiedCore` 是舊的主協調器，已被 `UnifiedPipeline` 完全取代。

### 任務
- [ ] 刪除 `tonesoul/unified_core.py`
- [ ] 刪除 `tonesoul/_legacy/unified_core_compat.py`
- [ ] 如果 `tonesoul/_legacy/` 目錄只剩 `__init__.py`，刪除整個 `tonesoul/_legacy/` 目錄
- [ ] 刪除 `tests/test_unified_core.py`
- [ ] 刪除 `tests/test_unified_core_properties.py`
- [ ] 更新 `scripts/healthcheck.py` — 移除 `"tonesoul.unified_core"` 那行
- [ ] 更新 `examples/demo_loop_integration.py` — 將 `from tonesoul.unified_core import UnifiedCore` 改為 `from tonesoul.unified_pipeline import UnifiedPipeline`，並在範例中使用 `UnifiedPipeline`
- [ ] 刪除 repo 根目錄的 `fix_nonlocal.py`（一次性修復腳本，目標已不存在）
- [ ] ruff + pytest 全過

### 禁止
- ❌ 不可刪除 `tonesoul_simple_app.py` 或 `tonesoul_simple_bridge.py`（引用 `tonesoul52`）
- ❌ 不可修改 `tonesoul/drift_tracker.py`（僅 docstring 提到，無程式碼依賴）

---

## Phase 581: 移除 market deprecated 模組 + 更新 scripts

**脈絡**: `tonesoul/market/forecaster.py` 和 `tonesoul/market/gold_detector.py` 已標記 deprecated。

### 任務
- [ ] 刪除 `tonesoul/market/forecaster.py`
- [ ] 刪除 `tonesoul/market/gold_detector.py`
- [ ] 刪除 `tests/test_forecaster.py`
- [ ] 刪除 `tests/test_gold_detector.py`
- [ ] 刪除 `tests/test_market_deprecation.py`
- [ ] 確認 `tonesoul/market/__init__.py` 沒有 re-export 已刪除的模組
- [ ] 更新 `scripts/run_gold_scan.py` — 移除 `from tonesoul.market.gold_detector import ...`，改為：`import sys; sys.exit("run_gold_scan.py: GoldDetector has been removed. See task.md Phase 581.")`
- [ ] 更新 `scripts/run_market_sweep.py` — 同上處理
- [ ] 更新 `scripts/test_dream_engine_5289.py` — 同上處理（`from tonesoul.market.forecaster import ...` 改為退出通知）
- [ ] ruff + pytest 全過

### 技術提示
- `tonesoul/market/` 下還有其他非 deprecated 模組，不要刪除整個 `market/` 目錄

---

## 成功標準

- [ ] 7 個 deprecated 模組已從 `tonesoul/` 刪除
- [ ] 對應的 deprecated 測試檔已刪除
- [ ] 所有活躍碼的引用已遷移或更新
- [ ] 不產生新的 DeprecationWarning（舊的 warning 減少是正確的）
- [ ] `ruff check tonesoul tests` 通過
- [ ] `pytest tests/ -x --tb=short -q` 通過，測試數 ≥ 2520

## CODEX_HANDBACK.md 需記錄

1. 每個 Phase 刪除了哪些檔案
2. Phase 579 中 build_council_summary 遷移的具體位置（哪一行）
3. 最終測試計數
4. 任何阻塞或設計決策
