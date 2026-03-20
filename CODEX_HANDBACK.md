# Codex 交回報告

**Phase**: 572-577 品質深化 + 代碼衛生
**完成日期**: 2026-03-20
**狀態**: 已完成 / 待痕審核

## 修改摘要
- 新增 9 個測試檔，補上 integration / security / property-based coverage。
- 擴充 4 個原本過薄的測試檔，改成具體契約與分支驗證。
- 強化 `tonesoul/llm/ollama_client.py` 與 `tonesoul/llm/lmstudio_client.py`：
  prompt 長度上限、基礎 prompt-injection 標記清理、model allowlist 驗證。
- 強化 `tonesoul/dcs.py`：`lockdown` 模式下不可被 policy override 重新打開預設關閉 trigger。
- 強化 `tonesoul/tension_engine.py`：`_compute_entropy()` 最終值 clamp 到 `[0, 1]`，消除浮點邊界負值。
- 為 7 個 deprecated/legacy 模組加上統一 `__deprecated__ = True` 標記與 successor 註記。
- 更新 `.github/workflows/pytest-ci.yml`、`README.md`、`pyproject.toml`、`task.md`。

## 測試結果
- `ruff check tonesoul tests` -> passed
- `pytest tests/ -x --tb=short -q` -> 2555 passed, 9 warnings
- targeted integration/security/property hardening suite -> 70 passed, 2 warnings

## Deprecated 模組引用鏈
- `tonesoul/council_adapter.py`
  目前引用：`tests/test_council_adapter_deprecated.py`
  取代路徑：`tonesoul.council.runtime.CouncilRuntime`
- `tonesoul/role_council.py`
  目前引用：`tonesoul/frame_router.py`, `tonesoul/council/runtime.py`, `tests/test_role_council_integration.py`
  取代路徑：`tonesoul.council.runtime.CouncilRuntime`
- `tonesoul/tonesoul_llm.py`
  目前引用：`scripts/healthcheck.py`, `tests/test_tonesoul_llm_deprecated.py`
  取代路徑：`tonesoul.unified_pipeline.UnifiedPipeline`
- `tonesoul/unified_core.py`
  目前引用：`scripts/healthcheck.py`, `tonesoul/_legacy/unified_core_compat.py`, `tests/test_unified_core.py`, `tests/test_unified_core_properties.py`
  取代路徑：`tonesoul.unified_pipeline.UnifiedPipeline`
- `tonesoul/market/forecaster.py`
  目前引用：`scripts/test_dream_engine_5289.py`, `tests/test_forecaster.py`, `tests/test_market_deprecation.py`
  取代路徑：保留 legacy surface，後續應收斂到非 deprecated market flow
- `tonesoul/market/gold_detector.py`
  目前引用：`scripts/run_gold_scan.py`, `scripts/run_market_sweep.py`, `tests/test_gold_detector.py`, `tests/test_market_deprecation.py`
  取代路徑：保留 legacy surface，後續應收斂到非 deprecated market flow
- `tonesoul/_legacy/unified_core_compat.py`
  目前引用：`tonesoul/unified_core.py`
  取代路徑：由 `tonesoul.unified_core.UnifiedCore` 的相容層接住，不應新增新依賴

## Audit 補充
- `tonesoul/__init__.py` 目前只 re-export `UnifiedController`，沒有 deprecated re-export。
- `tonesoul/market/__init__.py` 沒有對 `forecaster` 或 `gold_detector` 做 re-export。
- deprecated 標記已補在：
  `tonesoul/council_adapter.py`
  `tonesoul/role_council.py`
  `tonesoul/tonesoul_llm.py`
  `tonesoul/unified_core.py`
  `tonesoul/market/forecaster.py`
  `tonesoul/market/gold_detector.py`
  `tonesoul/_legacy/unified_core_compat.py`

## 風險 / 阻塞
- 無阻塞。
- full regression 仍有 9 個 warning，主要來自：
  1. Hypothesis 對 `.hypothesis` 目錄的 `norecursedirs` 提示。
  2. `requests` 依賴版本組合的 `RequestsDependencyWarning`。
  3. 既有 deprecated market / unified-core 測試與 `data_ingest.py` 的 `datetime.utcnow()` 提示。
- `pytest.ini` 目前仍是 authoritative config，因此 pytest 會提示忽略 `pyproject.toml` 內的 pytest 設定；這是設定同步狀態，不影響本次測試結果。

## 建議後續 / 注意事項
- 優先把 `role_council` 與 `tonesoul_llm` 的直接使用點收斂到 runtime / unified pipeline，讓 Phase 600+ 能真正移除 legacy 模組。
- `pyproject.toml` 已補 pytest metadata，但 repo 目前仍有 `pytest.ini`；若後續要單一化設定，應先決定以哪一個為 authoritative config。
- market legacy 模組目前仍有 script 入口依賴；移除前要先替換 `scripts/run_gold_scan.py`、`scripts/run_market_sweep.py`、`scripts/test_dream_engine_5289.py`。

## 重要檔案修改
- 檔案 1: `tonesoul/llm/ollama_client.py`, `tonesoul/llm/lmstudio_client.py`
  目的：補 prompt 邊界、注入標記清理、model allowlist。
- 檔案 2: `tonesoul/dcs.py`, `tonesoul/tension_engine.py`
  目的：補 lockdown fail-closed 與 entropy 浮點邊界硬化。
- 檔案 3: `.github/workflows/pytest-ci.yml`, `README.md`, `pyproject.toml`, `task.md`
  目的：同步 CI 品質門檻與 repo 狀態文件。
