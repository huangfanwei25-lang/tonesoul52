# 治理決策記錄 — responsibility_runtime gate 接入 dream_engine（shadow 模式）

- 日期：2026-06-29
- agent：claude-opus-4-8
- 擁有者裁決：黃梵威（Fan-Wei）於本 session 明確選擇 shadow（default-OFF 量測），非 enforce
- 狀態：APPROVED for shadow-only；enforce 為**獨立、未授權**的後續決策

> 本記錄本身是這段決策的 episodic trace —— 讓未來（擁有者或下一個 agent）能回溯
> 「2026-06-29 為什麼選 shadow 不選 enforce」。這是 Fan-Wei 在本 session 提出的框架
> （知覺定位 / 海馬迴）遞迴套用在治理決策層的結果。

---

## 【治理決策記錄】

**決策：**
在 `tonesoul/dream_engine.py:_persist_collisions` 的每個真實 collision 寫入點，**旁路**接入
`responsibility_runtime` gate，**shadow 模式、預設關閉**。對每個 collision payload：
建一個 `memory.write.propose` intent（best-effort 翻譯）→ `validate_intent` →
`decide_fail_closed(FakePolicyEngine, …)` → `Enforcer.enforce`（用 `RecordingMemoryAdapter`，
**不碰真實寫入**）→ 記錄 gate 判斷（executed / denied + reason）以及它與**實際**
`write_payload` 結果的一致性。**真實寫入仍走原本那條線、無條件**；gate 不 gating、不阻擋。

**為什麼：**
`responsibility_runtime` 問責核心目前**零 live consumer**（僅 tests/probe + 一個借用
`_has_visible_content` 字串 helper 的 import）——正是它自己架構文件 §10 命名的
**「Policy placebo：決策存在但 app 忽略它」**。shadow 讓這個 gate **第一次在真實
durable-write payload 上運轉**，產生**可回溯的 episodic trace**，作為未來任何 enforce 決策的
**證據基礎**。measure-before-enforce：你無法治理你看不見的東西。

**張力來源：**
`AXIOMS.json` Axiom 8（記憶主權，P0）記載一條**刻意的擁有者決定**：
「中央 `write_payload` 路徑 intentionally NOT gated（會破壞 first-party writes / the dream cycle）」。
- shadow **不反轉**這條：它不 gating、不改變任何寫入結果，只觀察。
- 但 shadow **為未來的 enforce 預鋪**——而 enforce **會**反轉這條 P0 邊界。
  因此 **enforce 是獨立的、需擁有者明確授權、且需更新該 Axiom-8 note 的決策**，本記錄不涵蓋。
- 另：responsibility-native-runtime plan 三份文件把 Phase 1–3 限定在 **fake adapter**。
  本 shadow 仍用 `RecordingMemoryAdapter`（fake），**不引入 real adapter**，故仍在 plan 範圍的
  精神內；它是「在真實 payload 上跑 fake-adapter gate」，不是「用 real adapter 寫記憶」。

**可逆性：**
高。單一 call-site 旁路 + 預設關閉 flag。
- 關掉 flag = 完全恢復原行為（shadow 不執行）。
- 移除 = 還原一個 import + 一段被 `try/except` 包住的 shadow block。
- shadow 永遠不影響真實寫入：整段 wrapped，任何 gate 例外只記進 observability、吞掉，
  **絕不**讓 gate 的失敗改變 dream 的寫入結果（否則就等於偷偷 enforce）。

---

## 設計約束（實作必須守）

1. **隔離（最重要）**：shadow gate 全程 `try/except`；任何例外 → 記成
   `responsibility_shadow.error`，**不**重拋、**不**改變 `write_payload` 的呼叫或結果。
2. **不雙寫**：Enforcer 用 `RecordingMemoryAdapter`（只記錄、回傳 dict），**不**碰
   `write_gateway`。真實寫入只有原本那一行。
3. **預設關閉**：`DreamEngine(..., responsibility_shadow=False)`；只有顯式開啟才跑。
   開啟後也只「觀察+記錄」，不改寫入。
4. **線索跟著記憶走**：gate 判斷寫進該 collision 的 `observability["responsibility_shadow"]`
   —— 日後翻任何一條 dream 記憶都看得到「問責 gate 當時怎麼判它」。
5. **可歸類的 ledger**：cycle 層彙總一份 shadow 摘要（counts + 不一致清單）進
   `DreamCycleResult.write_gateway["responsibility_shadow"]`，給聚合回顧用。
6. **量測 = 一致性（知覺定位）**：記錄 gate `executed`(allow) 與**實際寫入是否成功**的
   agree / diverge。diverge 清單才是未來 enforce 決策的依據。
7. **replay-safe**：用既有 `InMemoryTraceStore` + `replay_trace`，episodic 事件可重建。
8. **誠實標註（meta.not_for）**：所有 docs / 欄位都標 **shadow / measurement**，
   **不得**宣稱「記憶已被 gate」「不可繞過」「gate 有知覺」。這是 in-process 觀察層，
   不是 OS-level 憑證邊界，也不是 non-bypassability proof。
9. **best-effort 翻譯的誠實**：collision payload（world-facing schema）→ intent JSON 的轉換
   可能 lossy；因此 shadow 判的是「真實寫入的一個 sanitized 投影」——這正是它只能當
   **量測**、不能當 enforcement 的原因之一，需在欄位與 docs 標明。

## 明確不做（留給擁有者的後續決策）

- ❌ 不接 real `MemoryAdapter`（不讓 gate 真的寫/擋記憶）。
- ❌ 不反轉 Axiom 8 的「write_payload intentionally ungated」note。
- ❌ 不接 `pre_output_council`（output-side 是另一條 seam，本刀不碰）。
- ❌ enforce flip = 獨立 PR + 擁有者授權 + 更新 Axiom-8 note + shadow 量測證據支持後才談。
