# Phase 547 Status Report — Exception Observability Layer

**日期**: 2026-03-19  
**狀態**: 完成

## 概要

本階段為 ToneSoul 關鍵 fallback 路徑補上輕量級 suppressed-exception observability。
原本的控制流、return 值與 fallback 行為保持不變；新增內容只負責把被壓下的例外整理成結構化 trace。

## 變更重點

- 新增 `tonesoul/exception_trace.py`
  - `SuppressedError`
  - `ExceptionTrace`
- `tonesoul/unified_pipeline.py`
  - `__init__` 與 `process()` 掛入 `_exc_trace`
  - 任務指定的 10 個 lazy getters 補上 `trace.record(...)`
  - 多個 `process()` 內原本 `except Exception: pass` 的關鍵區塊補上記錄
  - 在 pipeline return 前注入 `dispatch_trace["suppressed_errors"]`
- `tonesoul/governance/kernel.py`
  - backend probe / friction / recovery fallback 補上 `trace.record(...)`
  - `build_routing_trace()` 在有 suppress 時附帶 `suppressed_errors`
- 測試
  - 新增 `tests/test_exception_trace.py`（5 tests）
  - 擴充 pipeline / kernel 測試（+4 tests）

## 驗證

- `python -m ruff check tonesoul/exception_trace.py tonesoul/unified_pipeline.py tonesoul/governance/kernel.py tests/test_exception_trace.py tests/test_unified_pipeline_v2_runtime.py tests/test_governance_kernel.py` → passed
- `python -m pytest tests/test_exception_trace.py tests/test_unified_pipeline_v2_runtime.py tests/test_governance_kernel.py -q` → 40 passed
- `python -m ruff check tonesoul tests` → passed
- `python -m pytest tests/ -x --tb=short -q` → 1860 passed

## 備註

- 為了通過本階段要求的全量 `ruff check tonesoul tests`，另外修正了三個既有測試檔的純 lint 問題：
  - `tests/smoke_test_market.py`
  - `tests/test_jump_engine.py`
  - `tests/test_run_market_sweep.py`
- 這些 lint 修正不改測試語意，只處理 import 排序、冗餘 f-string 與檔尾換行。
