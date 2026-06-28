# 知識閘活性審計 (Epistemic Gate Liveness Audit) — 2026-06-29

語魂九層自述地圖（`docs/architecture/tonesoul_layer_map_2026-06-29.md`）的第 7/9 層列了六個
**知識閘 (epistemic gates)**。本審計回答一個誠實問題：**每個閘真的存在嗎？有沒有接進 live
（非測試）模組？**——把 `claim ≤ evidence` 套在這些閘自己身上。

> 方法與邊界：grep on master 2026-06-29。每個閘的判定 = 實作模組存在 **且** 有非測試 live 模組
> import 它。**這驗的是「靜態存在 + 被 live 模組 import」，不是「每條 runtime 路徑都執行」，
> 更不是「不可繞過」（`AXIOMS.meta.not_for`）。** 「接線」≠「每條路都跑」≠「擋得住」。

| 知識閘 | 實作模組 | 已驗 live importer | 狀態 |
|---|---|---|---|
| 1 主張 ≤ 證據 (Claim ≤ Evidence) | `council/evidence_detector.py`、`council/atomic_claims.py`、`grounding_check.py`、`reviewer/evidence_levels.py` | `unified_pipeline.py`、`council/perspectives/analyst.py`、`reviewer/report.py`、`reviewer/claim_patterns.py` | **LIVE** |
| 2 語義漂移 (Semantic Drift) | `drift_monitor.py` | `unified_pipeline.py`（`_get_drift_monitor`:305）、`alert_escalation.py` | **LIVE** |
| 3 黑鏡反證 (Black Mirror Rebuttal) | `council/semantic_overclaim_sensor.py`（+ Critic 視角的 forced devil's advocate） | `council/pre_output_council.py` | **LIVE** |
| 4 記憶寫入 (Memory Write) | `memory/sovereignty_gate.py`（MemorySovereigntyGate） | `memory/handoff_ingester.py`、`evolution/corpus_builder.py` | **LIVE** |
| 5 來源痕跡 (Source Trace) | `memory/provenance_chain.py`（isnad hash-chain） | `council/runtime.py`、`memory/crystallizer.py` | **LIVE** |
| 6 安全邊界 (Safety Boundary) | `yss_gates.py` | `unified_pipeline.py`、`yss_pipeline.py`、`escalation.py` | **LIVE** |

## 發現

**六個知識閘全部接進 live 模組**，多數接進 `unified_pipeline.py`（活的主管線）。**知識閘這一層是
活的，不是 parked。**

這跟 `responsibility_runtime` 形成對照：問責核心**曾是 Policy placebo（0 live consumer）**，直到
`#219` 才接上第一條 observe-only 影子線（`dream_responsibility_shadow`）。所以語魂的兩種閘**活性
不同**：知識閘（管「說」的層）早已 live；責任閘（管「做/寫」的層）才剛開始接線、且只在 shadow。

## 不宣稱什麼（meta.not_for）

- 本文件**不宣稱**任何閘「不可繞過」或「擋得住所有越界」。它只記錄**接線事實**。
- `MemorySovereigntyGate` 自己的 enforcement note 已載明：中央 `write_payload` 路徑**故意不 gate**
  （見 `AXIOMS.json` Axiom 8）——所以「記憶寫入閘 LIVE」指的是它在**兩個 egress edge** 上 live，
  **不**涵蓋 `write_payload` 主路。這正是 `#219` shadow 在量測、未來 enforce 才會碰的那條邊界。
