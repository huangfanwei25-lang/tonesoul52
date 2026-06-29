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

## 6. Landscape（deep-research `wtdtxtpe5` 已查證，23/25 claims 對抗式確認）

**一句話：機制走得很熟、全做 alpha、而 alpha 多半是假的；校準軸幾乎沒人填——這條方向是真縫。**

**機制 prior art（記憶+反省迴圈，全在做 alpha、零校準）：**
- **FinMem**（arXiv 2311.13743）：分層記憶 trader，反省為**累積報酬**；標題即「Performance-Enhanced」。
- **FinAgent**（arXiv 2402.18485, KDD'24）：真的 make-call→observe→reflect→update 雙層反省；目標
  **獲利**（自報 92.27% return、Sharpe 2.25），六指標全財務；零校準。
- **TradingAgents**（arXiv 2412.20138；**就是 hedge-fund-committee 參照的那個**）：只用
  return/Sharpe/drawdown 評；**v1 論文無 outcome-learning 迴圈**（只有 ReAct 推理）。
  注意 paper≠實作：GitHub v0.2.x **有**抓 realized-return-vs-SPY + 注入反省，但論文沒寫。
- **FINCON**（NeurIPS 2024）：make-call/observe-PnL/reflect 迴圈，目標 max 折現 PnL，「風控」= 護獲利
  （CVaR）；零校準。
- 它們繼承的 **Reflexion**（arXiv 2303.11366, NeurIPS'23）本來做**任務完成正確率**，不碰金融/校準。

**alpha 多半是假的（最關鍵、也是別走 alpha 軸的硬證據）：**
- **FINSABER**（arXiv 2505.07078, **KDD 2026 accepted**）：偏誤修正後的 20 年、100+ 標的 backtest →
  FinMem/FinAgent **無統計顯著 alpha（p 全 > 0.34）**，一旦控制 survivorship / look-ahead /
  data-snooping、拉長 horizon、放寬標的。短窗亮眼報酬是偏誤產物。
- 「Profit Mirage」（arXiv 2510.07920）：資訊洩漏 / 預訓練污染——知識截止後報酬蒸發。
- Reflexion 假設「即時環境回饋」，市場違反（PnL 延遲+雜訊）→ 直接移植「reflect-to-predict-better」站不住。

**校準軸：唯一中心化它的是 benchmark、不是會反省的 agent：**
- **KalshiBench**（arXiv 2512.16030, 2025-12）：300 題 Kalshi 預測市場、結果在訓練截止後揭曉；量
  「自報 confidence 配不配得上實際命中（80% 信心該對 80%）」；發現**五個前沿 LLM（含 Claude Opus
  4.5）全系統性過度自信**；用 ECE / Brier Skill。**但它是評測 benchmark，不是反省-為-校準的 agent。**
  （caveat：單作者、未同儕審查 preprint、n=300。）

**那條真縫（deep-research 的 open question 原話）：** 有沒有任何已部署/已發表的金融 agent，**把校準
誤差（Brier/ECE）當成反省/學習的 signal**（不只事後評估）？**沒有出現——這就是真正新、沒填的
niche。** 正是本設計（§4）的 calibration-as-reflection-signal。而且它**比 alpha 更好-posed**：校準
有乾淨 ground truth、可逐 call 評分、且**對 FINSABER 那種讓 alpha 變幻覺的非穩態/data-snooping 免疫**
（你不需要打敗市場就能量它）。

**誠實邊界：** (a) 這是「負存在」結論（**這些系統**裡沒有），不證明全領域都沒有；(b) 有兩條 claim 被
對抗式投票否決——**別用「audit 19 篇論文」那個框架**（被否）；(c) 領域 2024–26 高速移動，已有
calibration-bonus（arXiv 2606.14211）、TrustTrade（uncertainty）在動，這縫隨時可能被填。

## 7. 下一步

1. ✅ deep-research（`wtdtxtpe5`）已查證並回填 §6：**「calibration-as-reflection-signal」是真縫**
   （所有現有 finance agent 做 alpha、且 alpha 多半幻覺；唯一碰校準的 KalshiBench 是 benchmark 非 agent）。
2. 換電腦 + 地端模型上來 → 離線跑、私有記憶、不靠 API 預算——最適合這個每日迴圈。
3. 第一刀（小）：只接 §2 的「committee memo → gate → 存 call」+ §4 的隔天回寫，**不碰**委員會辯論邏輯。
