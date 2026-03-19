# Codex Task: Phase 547 — Exception Observability Layer

**指派者**: 痕 (Hén) — Claude Opus 4.6
**日期**: 2026-03-19
**分支**: `feat/exception-observability`（不可 push 到 master）
**前置條件**: 1851 tests passing, lint clean

---

## ⚠️ 每次 commit 前必做

```bash
python -m pytest tests/ -x --tb=short -q
python -m ruff check tonesoul tests
```

跳過 = 整個交付失敗。連續失敗 3 次必須停止，記錄到 `CODEX_HANDBACK.md`。

完整規範請讀 `CODEX_PROTOCOL.md`。

---

## 脈絡（先讀這些）

1. `AGENTS.md` — 行為規範（注意「永遠不要靜默吞掉異常」）
2. `CODEX_PROTOCOL.md` — 你的工作流程規範
3. `tonesoul/unified_pipeline.py` — 主管線（18+ lazy getters，大量 `except: pass`）
4. `tonesoul/governance/kernel.py` — 治理核心（LLM 探測 + 摩擦計算）
5. `tonesoul/dream_engine.py` — 離線碰撞引擎（Phase 543 驗證區塊）

---

## 背景

專案有 47 個 `except Exception: pass` 區塊，其中 18 個在關鍵路徑。這違反 AGENTS.md 的原則。目標是在**不改變行為**的前提下，讓這些靜默失敗可觀測。

**核心原則**: 不改邏輯，只加觀測。所有改動必須是：
- `pass` → `pass` + 把錯誤記到 `dispatch_trace` 或結構化欄位
- 不影響返回值、不改 fallback 行為、不改流程

---

## Task A: 建立輕量異常追蹤工具

**檔案（新建）**: `tonesoul/exception_trace.py`

```python
"""Lightweight exception observer — records suppressed exceptions without changing control flow."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SuppressedError:
    """A single suppressed exception record."""
    component: str        # e.g. "governance_kernel", "drift_monitor"
    operation: str        # e.g. "_get_governance_kernel", "compute_friction"
    error_type: str       # e.g. "ImportError", "ConnectionError"
    message: str          # str(e)


class ExceptionTrace:
    """Session-scoped collector for suppressed exceptions.
    
    Usage:
        trace = ExceptionTrace()
        try:
            ...
        except Exception as e:
            trace.record("component", "operation", e)
            pass  # original behavior preserved
        
        # At end of pipeline:
        dispatch_trace["suppressed_errors"] = trace.summary()
    """
    
    def __init__(self) -> None:
        self._errors: List[SuppressedError] = []
    
    def record(self, component: str, operation: str, error: Exception) -> None:
        """Record a suppressed exception. Does not re-raise."""
        self._errors.append(SuppressedError(
            component=component,
            operation=operation,
            error_type=type(error).__name__,
            message=str(error)[:200],  # truncate long messages
        ))
    
    @property
    def has_errors(self) -> bool:
        return len(self._errors) > 0
    
    @property
    def count(self) -> int:
        return len(self._errors)
    
    def summary(self) -> Dict[str, Any]:
        """Return structured summary for dispatch_trace injection."""
        if not self._errors:
            return {"suppressed_count": 0}
        return {
            "suppressed_count": len(self._errors),
            "errors": [
                {
                    "component": e.component,
                    "operation": e.operation,
                    "error_type": e.error_type,
                    "message": e.message,
                }
                for e in self._errors
            ],
        }
```

**測試**: 新建 `tests/test_exception_trace.py`
- `test_empty_trace_summary` — 空 trace 正確輸出
- `test_record_adds_error` — 記錄後 count 增加
- `test_summary_structure` — summary 欄位結構正確
- `test_message_truncation` — 超長 message 被截斷到 200 字元
- `test_has_errors_flag` — has_errors 正確反映狀態

---

## Task B: 注入 ExceptionTrace 到 UnifiedPipeline.process()

**檔案**: `tonesoul/unified_pipeline.py`

1. 在 `__init__` 加 `self._exc_trace = ExceptionTrace()`
2. 在 `process()` 方法開頭加 `self._exc_trace = ExceptionTrace()` (reset per-call)
3. 在以下**關鍵路徑**的 `except Exception: pass` 區塊加入 `self._exc_trace.record(...)`：

### 必改的 lazy getters (每個都是同一模式)：

找這些方法，每個裡面都有 `except Exception: pass`：
- `_get_governance_kernel()`
- `_get_llm_router()`  
- `_get_llm_client()` (多處)
- `_get_tonebridge()`
- `_get_council()`
- `_get_trajectory()`
- `_get_drift_monitor()`
- `_get_alert_escalation()`
- `_get_deliberation()`
- `_get_tension_engine()`

改法（每個都一樣）：
```python
# 改前：
except Exception:
    pass

# 改後：
except Exception as e:
    self._exc_trace.record("unified_pipeline", "_get_XXX", e)
```

### 必改的 process() 內部 try/except：

在 `process()` 方法裡面搜尋所有 `except Exception: pass`，加入 trace.record。
至少包括：
- Section 2.4 AlertEscalation 的 try/except（~line 1689）
- JUMP trigger 呼叫的 except（~line 1679）
- soul_persistence 的 save

4. 在 `process()` 末尾、return 之前，加入：
```python
if self._exc_trace.has_errors:
    dispatch_trace["suppressed_errors"] = self._exc_trace.summary()
```

**測試**: 在 `tests/test_unified_pipeline_v2_runtime.py` 加：
- `test_suppressed_errors_absent_on_clean_run` — 正常執行不應有 suppressed_errors
- `test_suppressed_errors_present_on_init_failure` — mock 一個 getter 拋異常，確認 trace 出現

---

## Task C: 注入 ExceptionTrace 到 GovernanceKernel

**檔案**: `tonesoul/governance/kernel.py`

同模式：
1. 在 `__init__` 加 `self._exc_trace = ExceptionTrace()`
2. 在以下 `except Exception: pass` 加 `self._exc_trace.record(...)`：
   - `_try_ollama()`
   - `_try_lmstudio()`
   - `_try_gemini()`
   - `_get_friction_calculator()`
   - `_get_circuit_breaker()`
   - `_get_perturbation_recovery()`
   - `compute_runtime_friction()`
3. 在 `build_routing_trace()` 裡加入 suppressed_errors（如果有的話）

**測試**: 在 `tests/test_governance_kernel.py`（或新建）加：
- `test_kernel_exc_trace_default_empty` — 初始化後 trace 為空
- `test_kernel_records_backend_probe_failure` — mock Ollama 失敗，確認 trace 有記錄

---

## 成功標準

- [ ] `tonesoul/exception_trace.py` 新建，含 SuppressedError + ExceptionTrace
- [ ] UnifiedPipeline 的 **至少 10 個** `except: pass` 改為 `except as e: trace.record(...)`
- [ ] GovernanceKernel 的 **至少 5 個** `except: pass` 改為 trace.record
- [ ] `dispatch_trace["suppressed_errors"]` 在有異常時出現
- [ ] 所有新功能有測試
- [ ] `ruff check tonesoul/exception_trace.py tonesoul/unified_pipeline.py tonesoul/governance/kernel.py tests/test_exception_trace.py` → 通過
- [ ] `pytest tests/ -x -q` → 全過，**測試總數 ≥ 1858**（至少 +7 新測試）
- [ ] `CODEX_HANDBACK.md` 已更新

---

## 禁止事項

- ❌ 不改任何 `except` 區塊的 **控制流**（不改 return 值、不改 fallback 行為）
- ❌ 不刪除任何現有的 `except: pass`（只在旁邊加 trace.record）
- ❌ 不改 `alert_escalation.py` 的警報邏輯
- ❌ 不改 `AGENTS.md`, `CODEX_PROTOCOL.md`, `AGENT_PROTOCOL.md`
- ❌ 不加新的外部依賴
- ❌ 不改 Tier 3 (LOW severity) 的 except 區塊 — 那些是故意設計的 probe/fallback
- ❌ 不碰 `tonesoul/llm/router.py` 和 `tonesoul/llm/ollama_client.py` — 那些探測模式的靜默是正確的

## 技術提示

1. `ExceptionTrace` 是 **pure dataclass**，不要加 logging import，只收集資料
2. `process()` 每次呼叫開頭 reset trace，避免跨 request 累積
3. lazy getters 定義在 class body，但 `self._exc_trace` 在 `__init__` 設定 → 確認 `__init__` 早於 getter 呼叫
4. `message` 截斷到 200 字元，避免 dispatch_trace 膨脹
5. 參考 `dispatch_trace["alert"]` 的寫法 — 同樣是在 return 前注入 trace
6. 現有測試不應受影響 — 你只是在 `pass` 旁邊多加一行 `trace.record`

---

*指派者: 痕 (Hén) | 日期: 2026-03-19*

---

## 交付格式

1. 每個 Task 一個 commit
2. Commit message 格式：`feat: add mirror schema (Phase 140 Task A)`
3. 每個 commit 前跑 pytest + ruff
4. 最後 `git push origin feat/env-perception`
5. 在 `docs/status/` 留一份狀態報告
