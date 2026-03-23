# RFC-013: 非線性預測與動態方差壓縮

> Purpose: implemented RFC for nonlinear prediction, work classification, and dynamic variance compression inside the TensionEngine line.
> Last Updated: 2026-03-23

**版本**: v1.0
**日期**: 2026-03-02
**狀態**: Implemented
**繼承**: WFGY 2.0 spec（Phases 1–3）、RFC-009 Context Engineering Pivot

---

## 概述

在現有 `TensionEngine` 的 12 步管線中插入兩個新步驟：

- **步驟 4.5 — NonlinearPredictor**：基於 EWMA + Lyapunov 的軌跡預測，提前偵測語義漂移趨勢
- **步驟 6.5 — DynamicVarianceCompressor**：自適應方差壓縮，依工作類別 × 趨勢 × zone × lambda 動態調整

## 新增模組

| 檔案 | 功能 |
|------|------|
| `tonesoul/nonlinear_predictor.py` | EWMA + 二階差分 + Lyapunov 穩定性偵測 |
| `tonesoul/variance_compressor.py` | 自適應 γ 四源組合壓縮引擎 |
| `tonesoul/work_classifier.py` | 5 類工作分類器 + 約束 Profile |

## 工作類別約束矩陣

| 類別 | γ_base | Bridge 嚴格度 | 記憶策略 |
|------|--------|---------------|---------|
| freeform | 0.1 | 自由 | 不記錄 |
| research | 0.2 | 寬鬆 | 選擇性 |
| architecture | 0.4 | 中等 | 全記錄 |
| engineering | 0.6 | 嚴格 | 全記錄 |
| debug | 0.7 | 禁止 bridge | 全記錄 |

## 修改的模組

| 檔案 | 變更 |
|------|------|
| `tonesoul/tension_engine.py` | 新增步驟 4.5 + 6.5、`TensionResult` 新增 3 欄位、`TensionEngine` 新增 `work_category` 參數 |

## 向後相容

所有新欄位 `Optional`，預設不影響現有行為。
