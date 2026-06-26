# StockLens — 多空誠實框(台股 MVP)

> ToneSoul 的 claim-boundary 紀律,套到股票推理這個 **overclaim 最氾濫**的領域。
> 作者:Fan-Wei Huang(黃梵威）/ Claude (Opus 4.8)。日期:2026-06-26。
> 狀態:**application / MVP Phase 1**。`apps/` 是應用層,不是 canonical `tonesoul/` 治理碼。

---

## 它是什麼 / 不是什麼(邊界烤進結構,不是免責小字)

**不是:** 投資建議、不給買賣判定(`verdict` 永遠是 `None`)、不預測價格或未來、不接行情、不碰內線。

**是:** 拿**你自己**的分析,逼出誠實——
1. **強制拆多空對照**:四個面向(基本面 / 技術面 / 籌碼面 / 消息面)每個都要有**多空兩邊**;只給單邊或漏掉就標出來(這是 Council「保留異議、不塌成單邊」套到一檔股票)。
2. **抓你自己的 overclaim**:`保證 / 穩賺 / 必漲 / 零風險` 這類措辭(中文 lexical)——正是 AXIOMS 禁止的那一類 claim。
3. **抓「語言超過證據」**:措辭很篤定(必漲)卻只有 E0/E1 證據 → 標出來。
4. **列出兩邊都不可知的事**:未來價格、總經轉向、黑天鵝、內線、別人接下來的行為。

**決定和錢是你的。它幫你想,不替你想。**

---

## 【治理決策記錄】

- **決策:** 新增 `apps/stocklens/` 應用——把 ToneSoul 的 claim-evidence 紀律應用到台股分析,作為**誠實層**(非預測器/顧問)。
- **為什麼:** (a) 這可能是 ToneSoul 一直缺的**真實使用者 × 真實天天用的 use case**(對齊 2026 前沿「具體貢獻未證實 → 去證明它」);(b) 股市是 overclaim 最氾濫的領域,正是 claim-boundary 最該用的地方;(c) 起手最小、**重用既有**(evidence ladder、auditor 邏輯),不蓋新引擎。
- **張力來源:** 「新增一個應用」 vs restraint / budget / 「別把語魂變成能力產品」。化解方式:**框成誠實層而非預測器**(通過 capability-vs-restraint filter:它**約束** overclaim,不**增加**預測能力),且 scope 最小(deterministic、重用、不接資料源)。財經領域的法律風險用**結構性拒絕買賣判定**化解,不是貼免責。
- **可逆性:** 完全可逆。`apps/` 獨立,不碰 `tonesoul/` 治理碼;刪掉不影響核心。

---

## 資料形狀(你餵的東西)

```json
{
  "stock": "2330 台積電",
  "points": [
    {"dimension": "基本面", "side": "bull", "claim": "先進製程市占領先,毛利率 50%+", "evidence_level": "E2"},
    {"dimension": "基本面", "side": "bear", "claim": "資本支出龐大,景氣循環向下時獲利會修正", "evidence_level": "E1"}
  ]
}
```

- `dimension`:`基本面 / 技術面 / 籌碼面 / 消息面`
- `side`:`bull`(多)/ `bear`(空)
- `evidence_level`:`E0`(demo/憑感覺)…`E4`(獨立可複現)——沿用 `tonesoul/reviewer/evidence_levels.py` 的同一把尺
- `claim`:你的論點(一句)

## 跑

```bash
python apps/stocklens/core.py apps/stocklens/example_2330.json        # 人讀格式
python apps/stocklens/core.py apps/stocklens/example_2330.json --json # 結構化 JSON
```

---

## MVP 範圍 / non-goals

**MVP 做的(Phase 1):** 上面四件,**全 deterministic**(不需 API / 不需模型即可跑)。

**刻意不做(各自要再過 gate):**
- ❌ 預測價格 / 漲跌方向 / 買賣訊號
- ❌ 接即時行情、財報抓取、回測引擎
- ❌ LLM 自動生成多空論點(若日後加,須標 `llm_candidate`、opt-in、永不權威——比照 auditor Phase 3 紅線)
- ❌ 宣稱語義理解(它跟整個 ToneSoul 一樣:標模式、不理解;換句話說可穿透)

## Roadmap(一步步)

- **P1(本檔):** deterministic 多空誠實框 + overclaim + 證據錯配 + cannot-verify。
- **P2:** 釘更多台股 overclaim 詞彙 + false-positive fixtures;接 `ts` CLI 成 `ts stock`;characterization 報告(catch/miss + null)。
- **P3(若需要、且過 gate):** opt-in LLM 層**建議**你漏掉的空方論點(標 candidate、不權威)。
- 「適合我」:依使用回饋,把**你最常犯的 overclaim**收進詞彙、把你的四面權重變成你的 profile(連到「門」#191 的個人對齊 spec)。

*StockLens v0.1（application / MVP;非投資建議)*
