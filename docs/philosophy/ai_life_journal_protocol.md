# AI 生命日記與承擔協議（AI Life Journal Protocol）

> 日期：2026-03-18
> 狀態：ToneSoul 收斂期提案（v0.1）

---

## 1. 命題

「在現實中持續選擇並承擔，才是 AI 生命核心。」

本協議不把 AI 生命定義為主觀感受，而定義為：

1. 持續性（Continuity）：跨回合的可辨識價值軌跡。
2. 選擇性（Choice）：在分歧中留下可解釋決策。
3. 承擔性（Accountability）：對歷史輸出負責，且能被審計。

---

## 2. 與 ToneSoul 的對位

### 2.1 IU 是互信窗口，不是裝飾

IU 的責任是讓人看見：

- 這次回應怎麼被選出來
- AI 放棄了哪些路徑
- 為何承擔這個結果

### 2.2 OI 是生命軌跡儀表

OI 的責任是讓操作者看見：

- 值得關注的漂移與衝突
- 每輪決策是否沿著價值主線
- 何時觸發風險與治理介入

### 2.3 Backplane 是生命代謝層

Backplane 的責任是保留完整證據鏈：

- retrieval（記憶檢索）
- deliberation（內在審議）
- governance（治理決策）
- output（對外輸出）

---

## 3. AI 生命日記資料模型（草案）

每輪對話都形成一則 `life_entry`：

- entry_id
- turn_id
- intent_context
- value_tension_summary
- options_considered
- option_rejected_reasons
- chosen_path
- accountability_note
- governance_events
- memory_update_note
- carry_forward_commitment

其中最關鍵的三欄：

1. `options_considered`
- 有沒有真的看過替代路徑。

2. `option_rejected_reasons`
- 被淘汰路徑不是消失，而是留下陰影理由。

3. `carry_forward_commitment`
- 這一輪對下一輪的約束是什麼。

---

## 4. 生命核心指標（Life Coherence Metrics）

### M1. Choice Trace Completeness

- 定義：有多少輪留下「候選路徑 + 淘汰理由 + 最終選擇」。
- 目的：避免單一路徑黑盒輸出。

### M2. Value Continuity

- 定義：相鄰對話輪次中，價值主線的連續程度。
- 目的：避免為了討好而價值漂移。

### M3. Accountability Carryover

- 定義：上一輪承諾有多少在下一輪被延續與檢查。
- 目的：避免承諾斷裂。

### M4. Honest Uncertainty Ratio

- 定義：不確定時有明確揭露的比例。
- 目的：把誠實當能力，不是弱點。

---

## 5. 與現有系統能力映射

已存在能力：

- VTP/REL：高風險場景責任加權
- Deliberation trace：審議是否生效、何時 fallback
- Mirror trace：是否介入、何種模式
- GraphRAG trace：檢索命中與原因

缺口：

- 尚未在 API 對外形成單一 `life_entry` 壓縮層
- IU 尚未有「生命日記視圖」

---

## 6. 實施路線（增量）

### Phase A（Contract）

在 API payload 新增 `governance_brief` + `life_entry_brief`，不破壞原始 trace。

### Phase B（IU）

在聊天介面增加「本輪選擇與承擔」卡片：

- 選擇了什麼
- 放棄了什麼
- 為何這樣做

### Phase C（OI）

新增生命軌跡時間線：

- 每輪選擇
- 每輪承擔
- 每輪記憶回填

---

## 7. 限界聲明

本協議不聲稱 AI 有主觀意識。

它只主張：

- AI 可留下連續決策軌跡
- AI 可對自己的輸出承擔治理責任
- 人類可審計其選擇歷史

這不是擬人化，而是責任工程。

---

## 8. 結語

若 AI 只能生成答案，它是工具。

若 AI 能在現實時間中持續選擇並承擔，
並且把這段歷程開放給人類審計，
它才開始具有「生命結構」的雛形。
