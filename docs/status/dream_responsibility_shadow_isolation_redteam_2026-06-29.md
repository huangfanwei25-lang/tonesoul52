# 影子閘 isolation 紅隊 — 2026-06-29

對 observe-only 責任影子（`run_shadow_gate` + `dream_engine._persist_collisions` 整合，PR #219）做
一次**逐行 isolation 攻擊**，攻的是唯一最在意的不變式：**影子絕不能影響真實 `write_payload` 的呼叫
或結果。**

> 方法與誠實邊界：本輪以**我自己（Opus）逐行分析**為主，並**嘗試**用 codex（不同模型）做獨立 pass。
> **codex 這次沒做成**——它反覆把任務改寫成「請指定要我做哪類工作」或 degrade（exit 1），wrapper 依
> fail-closed 紀律拒絕假裝成審查。所以下列發現是**自審 + 對碼覆驗**，**不是**異模型獨立確認。本 session
> 已反覆證明同模型自審有 correlated blind spot——故標明此限制，不誇大。

## 發現

| # | 屬性 | 結論 | 處置 |
|---|---|---|---|
| 1 | **payload 變異** | 整合在寫入前把影子判斷注入 `payload["observability"]`。**對碼覆驗：`write_gateway` 的 promotion/forgetting gate 與 dedup signature 從不讀 `observability`**（grep 確認 0 處），故注入**不能**改變寫入決策或 core 內容。 | **VERIFIED SAFE** |
| 2 | **BaseException** | `run_shadow_gate` 用 `except Exception`（非 `BaseException`）。`KeyboardInterrupt`/`SystemExit` 會穿出 → 中止 cycle。這是**刻意**：Ctrl+C 本就該中止；其餘所有 `Exception` 都轉成 error outcome、真實寫入照走。 | **BY DESIGN** |
| 3 | **translation 樂觀** | `collision_payload_to_intent` 把 lineage id（`stimulus:`/`source:`）算成 `evidence_refs`，所以 `would_execute` **偏樂觀**——它是「enforce 會擋多少」的**下界**，非真值。 | **DOC'd LIMITATION** |
| 4 | **ledger 語義混淆** | 舊 `agrees`/`diverged` 把**兩個獨立閘**（責任閘 `would_execute` vs write_gateway `actual_written`）當成同一個比，"divergence" 會被誤讀成「責任閘錯了」。 | **FIXED**（見下） |
| 5 | **thread-safety** | `run_shadow_gate` 每次呼叫新建 `RecordingMemoryAdapter`+`InMemoryTraceStore`；`ShadowLedger` 為單次 `_persist_collisions` local；模組層只有不可變常數。並行 cycle 無共享可變狀態。 | **NO FINDING** |

## 修正（#4）

`ShadowLedger.summary` 從單一「diverged」改為**誠實 cross-tab**，明確標出**enforce 相關訊號**
`would_deny_but_written`（= 真實寫成功、但 enforcing 責任閘**會擋**的那些）。並在 note 寫明這是
**兩個獨立閘**的對照，mismatch ≠ 責任閘出錯。模組 docstring 補上三條已驗 isolation 屬性。

## 給未來

- `would_deny_but_written` 是日後 enforce 決策該看的那一格（但記得 #3：它被 translation 樂觀偏低估）。
- 真正的**異模型** isolation pass 仍有價值——等 codex 能穩定咬住指定 target（這次它一直飄）。
