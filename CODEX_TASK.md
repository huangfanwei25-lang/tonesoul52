# Codex Task: Phase 572-577 — 品質深化 + 代碼衛生 (Quality Hardening)

**指派者**: 痕 (Hén)
**日期**: 2026-03-20
**分支**: `feat/env-perception`
**前置條件**: 2491 tests passing, lint clean, 186/186 模組單元測試覆蓋

> **單元測試收斂已完成。**
> 本輪目標：整合測試強化、deprecated 模組清理、property-based testing、安全邊界強化。
> 6 個 Phase，從「測試數量」轉向「測試品質 + 程式碼衛生」。

---

## 脈絡（先讀這些）

1. `tests/test_end_to_end_pipeline.py` — 參考現有整合測試的模式
2. `tests/test_workflow_contracts.py` — 參考工作流契約測試
3. `tests/test_unified_pipeline_v2_runtime.py` — 參考管線運行時測試
4. `tonesoul/council_adapter.py` — 已 deprecated，但仍被引用
5. `tonesoul/tonesoul_llm.py` — 已 deprecated，需確認引用鏈
6. `tonesoul/unified_core.py` — 已 deprecated，有 _legacy compat 層

---

## Phase 572: 管線整合測試 — 多模組穿透 (20+ tests)

現有 7 個整合測試覆蓋局部。目標：增加跨子系統的端到端測試路徑。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_integration_tonebridge_pipeline.py`
  測試 ToneBridge → TensionEngine → Council → Governance 的完整流程。

  - 構造一個假對話，讓它穿過 entropy_engine → rupture_detector → tension_engine → governance kernel
  - 測試正常路徑、高張力觸發 escalation、低張力正常通過
  - 驗證 dispatch_trace 在整個流程中的傳遞完整性
  - 至少 6 個測試

- [ ] **Task B**: 建立 `tests/test_integration_memory_lifecycle.py`
  測試記憶從寫入到結晶到衰減的完整生命週期。

  - 記憶寫入 → hippocampus 存儲 → crystallizer 結晶 → decay 衰減 → stats 統計
  - 測試記憶召回（新鮮 vs 陳舊）
  - 測試 subjectivity_admissibility 在記憶存取中的決策
  - 至少 6 個測試

- [ ] **Task C**: 建立 `tests/test_integration_deliberation_council.py`
  測試審議引擎到 Council 的完整審議流程。

  - perspectives → gravity → engine → summary_generator
  - 測試多觀點收斂
  - 測試審議超時 / 截斷
  - 至少 6 個測試

### 成功標準
- [ ] 3 個新測試檔，共 20+ 測試通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 572): integration tests — tonebridge pipeline + memory lifecycle + deliberation council`

---

## Phase 573: Deprecated 模組清理 (0 新測試，清理任務)

7 個 deprecated 模組需要確認引用鏈，清理不再需要的間接引用。

### 任務清單

- [ ] **Task A**: 分析 deprecated 引用鏈
  用 grep 確認以下 7 個模組的引用狀態：
  - `tonesoul/council_adapter.py`
  - `tonesoul/role_council.py`
  - `tonesoul/tonesoul_llm.py`
  - `tonesoul/unified_core.py`
  - `tonesoul/market/forecaster.py`
  - `tonesoul/market/gold_detector.py`
  - `tonesoul/_legacy/unified_core_compat.py`

  在 `CODEX_HANDBACK.md` 中列出每個模組被誰引用。

- [ ] **Task B**: 為每個 deprecated 模組加上統一的 deprecation 標記
  如果模組頂部還沒有模組級屬性，加上：
  `__deprecated__ = True  # Scheduled for removal. Use [替代模組] instead.`

- [ ] **Task C**: 確認所有 deprecated 模組的 __init__.py re-export 有 deprecation warning
  檢查 `tonesoul/__init__.py` 和各子目錄 `__init__.py`，如果 re-export 了 deprecated 模組，加上 warning。

### 成功標準
- [ ] 7 個 deprecated 模組都有統一的 `__deprecated__` 標記
- [ ] 引用鏈記錄在 CODEX_HANDBACK.md
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `chore(Phase 573): deprecated module audit + unified deprecation markers`

---

## Phase 574: 安全邊界強化測試 (18+ tests)

現有安全測試（test_api_phase_a_security, test_rdd_injection 等）覆蓋 API 層。
增加內部模組的安全邊界測試。

### 任務清單

- [ ] **Task A**: 建立 `tests/test_security_memory_boundary.py`
  測試記憶系統的安全邊界。

  - 測試記憶寫入的 sanitization（惡意 payload、超長輸入、特殊字元）
  - 測試記憶查詢的注入防護
  - 測試 corpus consent 的未授權存取
  - 至少 6 個測試

- [ ] **Task B**: 建立 `tests/test_security_governance_bypass.py`
  測試治理核心的繞過嘗試。

  - 測試 action_set lockdown 模式下的操作限制
  - 測試 constraint_stack 的約束注入
  - 測試 DCS 狀態機的非法狀態轉移
  - 至少 6 個測試

- [ ] **Task C**: 建立 `tests/test_security_llm_boundary.py`
  測試 LLM 客戶端邊界。

  - 測試超長 prompt 的截斷處理
  - 測試回應中的 prompt injection 過濾
  - 測試 model registry 的未註冊模型拒絕
  - 至少 6 個測試

### 成功標準
- [ ] 3 個新測試檔，共 18+ 測試通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 574): security boundary tests — memory + governance + LLM`

---

## Phase 575: Property-Based Testing 引入 (15+ tests)

用 hypothesis 對核心數學模組做屬性測試，找出邊界值 bug。

### 任務清單

- [ ] **Task A**: 確認 hypothesis 已安裝
  跑 `pip list | grep hypothesis`。如果沒有，在 `pyproject.toml` 的 dev dependencies 加入 `hypothesis`，然後 `pip install hypothesis`。
  **注意**: 只能用 pip install，不可安裝系統層級套件。

- [ ] **Task B**: 建立 `tests/test_property_tension_engine.py`
  對 TensionEngine 做屬性測試。

  - 張力值永遠在 [0, 1] 範圍
  - 衰減後的張力 <= 衰減前
  - 多次累加後的積分值單調遞增（在無衰減時）
  - 空輸入產生零張力
  - 至少 5 個 property tests

- [ ] **Task C**: 建立 `tests/test_property_soul_db.py`
  對 SoulDB 做屬性測試。

  - 寫入後讀取得到相同值
  - 刪除後查詢返回空
  - 批次操作的冪等性
  - 至少 5 個 property tests

- [ ] **Task D**: 建立 `tests/test_property_drift_monitor.py`
  對 DriftMonitor 做屬性測試。

  - EMA 值永遠在合理範圍
  - 穩定輸入不觸發漂移警報
  - 劇烈變化觸發警報
  - 至少 5 個 property tests

### 成功標準
- [ ] hypothesis 已安裝（或確認已存在）
- [ ] 3 個新測試檔，共 15+ property tests 通過
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 575): property-based testing — tension_engine + soul_db + drift_monitor`

---

## Phase 576: 測試品質加固 — 擴充瘦弱測試 (15+ tests)

有 4 個測試檔 <15 行，可能過於簡陋：
- `test_ystm_demo_entry.py` (7L)
- `test_unified_pipeline_dispatch.py` (8L)
- `test_issue_codes.py` (12L)
- `test_handoff_builder_security.py` (14L)

### 任務清單

- [ ] **Task A**: 擴充 `tests/test_ystm_demo_entry.py`
  目前只有 1 個 smoke test。讀 `tonesoul/ystm_demo.py` 確認是否有更多可測邏輯。
  如果只是 import 入口（5L），保持精簡但加上 import 完整性檢查。

- [ ] **Task B**: 擴充 `tests/test_unified_pipeline_dispatch.py`
  目前只有 8L。讀源碼確認 dispatch 邏輯，補上邊界測試。
  至少達到 5 個測試。

- [ ] **Task C**: 擴充 `tests/test_issue_codes.py`
  目前 12L。補上所有 issue code 的格式驗證和唯一性檢查。
  至少達到 4 個測試。

- [ ] **Task D**: 擴充 `tests/test_handoff_builder_security.py`
  目前 14L。讀源碼補上安全相關的邊界測試。
  至少達到 4 個測試。

### 成功標準
- [ ] 4 個測試檔都擴充完畢，各 >= 4 個測試
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `test(Phase 576): test quality hardening — expand thin test files`

---

## Phase 577: CI 健康檢查 + README 更新 (文件任務)

確認 CI pipeline 和專案文件是最新的。

### 任務清單

- [ ] **Task A**: 確認 `pytest-ci.yml` 的測試命令是否正確
  讀 `.github/workflows/pytest-ci.yml`，確認它跑的是 `pytest tests/ -x`。
  如果有寫死的測試數量斷言，更新到 2491+。

- [ ] **Task B**: 更新 README.md 的測試狀態
  如果 README.md 提到測試數量，更新為最新值 (2491+)。
  如果 README.md 提到模組數量或覆蓋率，更新為 186/186。

- [ ] **Task C**: 確認 `pyproject.toml` 的 pytest 配置
  讀 `pyproject.toml`，確認 pytest 的 testpaths、markers 正確。
  如果缺少 `[tool.pytest.ini_options]` 區段，補上基礎配置。

- [ ] **Task D**: 更新 `task.md` 的 Phase 歷史
  在 task.md 底部加上 Phase 572-577 的歷史記錄。

### 成功標準
- [ ] CI 配置確認正確或已更新
- [ ] README 和 pyproject.toml 資訊一致
- [ ] `ruff check` 無錯誤
- [ ] `pytest tests/ -x` 全過，無回歸
- [ ] commit: `chore(Phase 577): CI health check + README + pyproject.toml sync`

---

## 禁止事項（所有 Phase 通用）

- 不可刪除任何現有源碼檔案（deprecated 模組也不刪，只加標記）
- 不可修改 `.env`, `.gitignore`, `AGENTS.md`, `MEMORY.md`, `CODEX_PROTOCOL.md`
- 不可 push 到 `master`
- 不可安裝新的系統層級套件（pip install 可以）
- 不可修改 `tonesoul/governance/kernel.py` 核心邏輯
- 不可修改 `tonesoul/unified_pipeline.py` 路由結構
- 不可使用 `--no-verify` 繞過 hooks

## 技術提示

- 整合測試需要多模組聯動 — 用 monkeypatch mock LLM 調用，但讓模組間的真實邏輯流動
- Property-based testing 用 `hypothesis`：`from hypothesis import given, strategies as st`
- deprecated 模組**不刪除**，只加標記。刪除是 Phase 600+ 的事
- CI workflow 修改要保守 — 只改測試指令參數，不改觸發條件
- 安全測試參考 `tests/test_rdd_injection.py` 和 `tests/test_api_phase_a_security.py` 的模式
- 每次 commit 前必須跑 `ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q`
