# 孤兒模組審計 — 2026-04-11

工具：`scripts/analyze_codebase_graph.py`（全 AST 靜態分析）

## Summary

| 分類 | 數量 | 說明 |
| --- | ---: | --- |
| 總孤兒（零 in-degree） | 134 | 沒有被其他 tonesoul 模組直接 import |
| 假陽性（被 scripts/tests/init 引用） | 121 | 正常 — entry point 或間接載入 |
| **真孤兒** | **13** | 完全沒人引用 |

## 假陽性說明

134 個「孤兒」中有 121 個不是死碼，原因如下：

- **Entry points**：`unified_pipeline`、`observer_window`、`autonomous_schedule` 等被 scripts/ 直接呼叫
- **Init re-exports**：`council.runtime`、`deliberation.types`、`tonebridge.analyzer` 等被 `__init__.py` 匯出
- **Test-only**：`council.perspectives.*`、`poav`、`tsr_metrics` 等被測試直接 import
- **Dynamic dispatch**：Council perspectives 被 `perspective_factory` 動態載入

## 13 個真孤兒

| 模組 | 行數 | 最後修改 | 診斷 | 建議 |
| --- | ---: | --- | --- | --- |
| `audit_interface` | 356 | 2026-02-05 (format) | CLI 工具，有 argparse，設計為獨立執行 | **標記 entry point** |
| `constraint_stack` | 149 | 2026-02-05 (format) | YAML 約束堆疊渲染器，有 argparse | **標記 entry point** |
| `context_compiler` | 135 | 2026-02-07 (lint) | 上下文編譯器，有 argparse | **標記 entry point** |
| `council.council_cli` | 172 | 2026-02-23 (security) | Node.js callable entry point，`python -m` 執行 | **標記 entry point** |
| `council.transcript` | 365 | 2026-02-07 (lint) | Council transcript logger，P2 Issue 10 產物 | **調查** — 可能該被 council.runtime 引用 |
| `evidence_collector` | 265 | 2026-02-05 (format) | 證據收集 CLI，有 argparse | **標記 entry point** |
| `skill_promoter` | 375 | 2026-02-07 (lint) | Skill 晉升邏輯 | **調查** — 可能被 skill_gate 取代 |
| `tech_trace.validate` | 142 | 2026-02-05 (format) | Tech trace 驗證 CLI，有 argparse | **標記 entry point** |
| `ystm.acceptance` | 146 | 2026-02-05 (format) | YSTM 接受度計算 | **保留** — ystm 子系統內部使用 |
| `ystm.audit` | 55 | 2026-01-09 (v5.3) | YSTM 審計日誌 | **保留** — ystm 子系統內部使用 |
| `ystm.governance` | 174 | 2026-02-07 (lint) | YSTM 治理邏輯 | **保留** — ystm 子系統內部使用 |
| `ystm.render` | 504 | 2026-02-07 (lint) | YSTM 渲染引擎 | **保留** — ystm 子系統內部使用 |
| `ystm_demo` | 5 | 2026-01-09 (v5.3) | 相容性包裝，轉發到 ystm.demo | **可刪** — 5 行 wrapper |

## 診斷結論

### 真正的死碼：0～2 個

大多數「真孤兒」其實是 **CLI entry points**（有 argparse）或 **子系統內部模組**（ystm）。

唯二需要調查的：
1. **`council.transcript`** — 365 行，設計為 council 的 transcript logger，但 council.runtime 沒 import 它。可能是遺忘接線。
2. **`skill_promoter`** — 375 行，skill 晉升邏輯。`skill_gate.py` 已存在，可能功能重疊。

### 建議行動

1. `ystm_demo.py`（5 行 wrapper）可以安全刪除
2. `council.transcript` 需要檢查是否該被 council.runtime 引用
3. `skill_promoter` 需要檢查是否與 skill_gate 功能重疊
4. 其餘 10 個保留原樣 — 不是死碼
