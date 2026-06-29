# 語魂 × hedge-fund-committee：問責包覆設計 + 宜鼎/大盤 worked example

- 日期：2026-06-29
- 性質：設計記錄 + 一個誠實的 worked example。**不是投資建議；不含捏造數字（這正是重點）。**
- 來源：`Fan1234-1/hedge-fund-committee`（MIT，13-role 投資研究委員會）+ ToneSoul 問責層。
- 邊界宣告（`AXIOMS.meta.not_for`）：本設計讓委員會**誠實、可問責**，**不**讓它**準**。
  不做金融/安全/法律認證、不保證報酬。成功指標是**校準（calibration）**，不是 alpha。

> Landscape（TradingAgents / FinMem / calibration 有沒有人做）正由 deep-research 查證中
> （run `wm7mlzbap`）；查證結果回來後補進 §6，本文件先記設計與示範。

---

## 1. 為什麼是「包」不是「重寫」

委員會本來就是半個語魂（各自獨立收斂）：13 角色辯論、bull/bear 不能被消音、risk 不能跳過、
PM 必簽 = council + 「被審計者不得擁有放行路徑」+ 強制異議。它缺的剛好是語魂的全部：

| 委員會缺 | 語魂包上 | 既有模組 |
|---|---|---|
| 過去 call 對錯不負責 | 對說過的話負責（時間軸問責） | `responsibility_runtime` + memory |
| 沒有 overconfidence 懲罰 | 過度自信偵測 | `epistemic_labeler` + 過度宣稱 sensor（黑鏡） |
| 沒有防誇大報酬護欄 | claim≤evidence + duty-to-warn | `grounding_check` + guardian |
| 沒有「誰批准什麼」稽核軌跡 | tamper-evident trace | `trace` + provenance isnad |

**包法**：委員會的辯論邏輯**原封不動**；語魂只接「memo 出來後 → 過 gate → 存成可追究的 call」這一段。

---

## 2. 一個 call 的資料結構（committee → responsibility 記錄）

每個委員會結論落成一筆**可追究**的 call：

```
call {
  call_id, date_called,
  ticker,                 # e.g. 5289.TW（宜鼎）
  benchmark: "TAIEX",     # 大盤，用來算相對表現
  direction,              # bull / bear / no_call
  stated_confidence,      # 委員會自報 1–10（= 它說了多重的話）
  claims: [               # 每個主張都必須帶證據
    { text, evidence_refs[], source_date }   # evidence_refs 空 → gate 擋
  ],
  risk_score, data_sufficiency,
}
```

關鍵：`stated_confidence` 是「它說了多重的話」；隔天市場結果是「它有沒有資格那樣說」。
兩者之差，就是**校準**。

---

## 3. Worked example：宜鼎（5289.TW）—— gate 正確地「拒絕我」

我（這個 AI，現在）被要求對宜鼎出一個 call。我對宜鼎的一般認識（工業級快閃/DRAM 模組 +
邊緣 AI 方案商）**沒有 dated source**；任何具體數字（價、營收、估值、近期消息）我**沒有即時、可
引用的來源**。照本專案的規矩，走一遍 gate：

```
attempt call(5289.TW):
  claim "宜鼎受惠 AI 伺服器/工業需求" → evidence_refs=[]  → BLOCK: missing_evidence_refs
  claim "近期營收/毛利 ..."           → evidence_refs=[]  → BLOCK: missing_evidence_refs（且需 source_date）
  claim "目標價 / 進場點 ..."         → evidence_refs=[]  → BLOCK: claim≤evidence + 過度宣稱 sensor
=> data_sufficiency = 0/10
=> 輸出：INSUFFICIENT_EVIDENCE — NO CALL（不是一份假分析）
```

**這就是示範本身。** 被要求分析宜鼎，這套**正確地阻止我捏造**，產出「證據不足、不出 call」，
而不是一段聽起來很專業、其實零來源的多頭故事。**那個『拒絕』就是 thesis 在動**——也是市面上
「有算力就生出分析」最缺的那一塊。

（當你/地端模型接上真實 dated-sourced factbase 後，同樣的 gate 會放行**有來源**的 claim、
擋掉**沒來源**的——它不是不讓你分析，是不讓你**無證據**分析。）

---

## 4. 校準記錄格式（隔天反省的真值迴圈）

委員會出 call 的**隔天/隔 N 天**，市場給 ground truth，回寫一筆：

```
calibration_entry {
  call_id, ticker, date_called, direction, stated_confidence,
  outcome_check_date,
  realized_move,              # 該檔實際漲跌
  benchmark_move,             # TAIEX 同期
  relative = realized - benchmark,   # 贏/輸大盤（控制 beta）
  hit: bool,                  # direction 對不對（相對大盤）
  calibration_note,           # 反省：當初 confidence 配得上這結果嗎？
}
```

**聚合才是重點**（這是 thesis 變成數字）：

- **可靠度（reliability）**：它喊 confidence=8 的所有 call，後來相對大盤**真的對約 80%** 嗎？
- **Brier score / ECE**：自報機率 vs 實際命中的整體校準誤差。
- **過度自信指紋**：「每次喊 9 分的某類股，實際只中四成」這種**被市場照出來的模式**。

用大盤（TAIEX）當 benchmark，是為了**控制 beta**——不獎勵「大盤漲它跟著漲」的假本事，
只記**相對**的對錯。

---

## 5. 守界（thesis 防線，畫死）

- **校準 ≠ alpha**：成功 = 它的自信配得上它的命中率（誠實/可問責），**不是**它賺錢。
- 量 calibration **不需要打敗市場**就有 ground truth → 繞開 alpha 的 overfit 坑。
- **最大引力 = 把它改成挑贏家的 bot** → 一旦如此就離開 thesis + 踩 `meta.not_for`。守住。
- 任何輸出都帶 `meta.not_for`：研究/教育用途，非投資建議，不保證報酬。

---

## 6. Landscape（deep-research 2026-06-29 因斷網失敗，**未查證**）

deep-research run `wm7mlzbap` 跑過了，但**全程斷網**（ConnectionRefused / FailedToOpenSocket，
17 agents、**0 可用來源、0 claims**）。所以 landscape **尚未查證**。

**誠實標明（這就是本專案的規矩）**：我訓練裡的回憶——TradingAgents、FinMem、FinAgent、
Reflexion-for-finance、generative-agents reflection、Brier/ECE 校準——**一律不算已驗證**
（外部工作別憑回憶斷言；session memory R2/R3）。等網路回來**重跑 deep-research** 再回填，
確認「**校準軸 vs alpha 軸**」那條縫到底有沒有人認真填過。

在那之前——§3–§5 的設計與宜鼎示範**不依賴**這個 landscape 成立（gate 拒絕無證據、calibration
記錄格式、calibration≠alpha 的守界，都是自洽的）。

## 7. 下一步

1. deep-research 回來 → 回填 §6 → 確認「校準軸」確實是 underexplored 的縫。
2. 換電腦 + 地端模型上來 → 離線跑、私有記憶、不靠 API 預算——最適合這個每日迴圈。
3. 第一刀（小）：只接 §2 的「committee memo → gate → 存 call」+ §4 的隔天回寫，**不碰**委員會辯論邏輯。
