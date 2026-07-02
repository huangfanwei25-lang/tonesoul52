# 知識閘活性審計 (Epistemic Gate Liveness Audit) — 2026-06-29

使用者的「約束導向 AI 開發」提案（2026-06-29）在治理覆蓋層列了六個 **知識閘 (epistemic
gates)**；語魂九層自述地圖（`docs/architecture/tonesoul_layer_map_2026-06-29.md`）第 7/9 層也指認了
其中數個的實作。本審計回答一個誠實問題：**每個閘真的存在嗎？有沒有被 live（非測試）模組
`import`？**——把 `claim ≤ evidence` 套在這些閘自己身上。

> 方法與邊界：grep on master 2026-06-29。每個 importer 都以**實際 import 陳述 + 行號**佐證
> （非「檔案含某字串」——v1 犯了這個錯，見文末修正紀錄）。**這驗的是「模組存在 + 被 live 模組
> import」，不是「每條 runtime 路徑都執行」，更不是「不可繞過」（`AXIOMS.meta.not_for`）。**
> 「接線」≠「每條路都跑」≠「擋得住」。

| 知識閘 | 實作模組 | 已驗 live importer（import 陳述:行） | 狀態 |
|---|---|---|---|
| 1 主張 ≤ 證據 | `council/evidence_detector.py`、`grounding_check.py`、`reviewer/evidence_levels.py` | `council/perspectives/analyst.py:6`、`unified_pipeline.py:878`、`reviewer/report.py:11`、`reviewer/claim_patterns.py:9` | **LIVE** |
| 2 語義漂移 | `drift_monitor.py` | `unified_pipeline.py:308`、`yuhun/world_sense.py:41` | **LIVE** |
| 3 黑鏡反證 | `council/semantic_overclaim_sensor.py`（+ Critic 視角 forced devil's advocate） | `council/pre_output_council.py:180` | **LIVE** |
| 4 記憶寫入 | `memory/sovereignty_gate.py`（MemorySovereigntyGate） | `memory/handoff_ingester.py:9`、`evolution/corpus_builder.py:191` | **LIVE** |
| 5 來源痕跡 | `memory/provenance_chain.py`（ProvenanceManager / isnad） | `council/runtime.py:13`、`memory/crystallizer.py:271`、`openclaw_auditor.py:10` | **LIVE** |
| 6 安全邊界 | `yss_gates.py` | `unified_pipeline.py:638`、`yss_pipeline.py:36` | **LIVE** |

**排除（誠實標註）：** `council/atomic_claims.py` 雖屬「主張≤證據」家族，但其檔頭自述
`# DORMANT (as of 2026-06-15)... not imported by any live module`，grep 確認**無 live importer**，
故**不計入** LIVE 證據。

## 發現

**六個知識閘各自至少有一個已驗 live importer（多數接進 `unified_pipeline.py`）→ 知識閘這一層是
活的，不是 parked。**

對照 `responsibility_runtime`：問責核心**曾是 Policy placebo（0 live consumer）**，直到 `#219`
才接上第一條 observe-only 影子線。所以語魂兩種閘**活性不同**：知識閘（管「說」）早已 live；
責任閘（管「做/寫」）才剛接線、且只在 shadow。

## 不宣稱什麼（meta.not_for）

- 不宣稱任何閘「不可繞過」；只記錄**接線事實**。
- `MemorySovereigntyGate` LIVE 指的是它在 egress edge 上 live；中央 `write_payload` 路徑
  **故意不 gate**（`AXIOMS.json` Axiom 8）——正是 `#219` shadow 在量測、未來 enforce 才會碰的邊界。

## 修正紀錄（meta 原則實證：約束/宣稱本身可審查、可反駁）

- **v1（commit `0755969`）三處 overclaim**，由 **codex（不同模型）紅隊**抓到、我逐一對碼覆驗確認：
  1. 把 **DORMANT** 的 `atomic_claims.py` 列為 LIVE（違反本審計自己的判準）；
  2. 把 `alert_escalation.py`（drift）、`escalation.py`（yss）列為 importer，實際只是**字串出現**、
     非 `import`；
  3. 來源歸因過強：六閘清單其實出自使用者提案，非地圖列舉。
- **根因**：v1 用 `grep -rln`（檔案含字串）當「已驗 importer」——string-presence ≠ import。
- **修正**：改以 import 陳述 + 行號佐證；移除 dormant / string-only 條目；改正歸因。
- 這正是 meta 原則的運轉：宣稱 overclaim → 異模型外眼抓到 → 對碼覆驗 → 帶 provenance 修正。
