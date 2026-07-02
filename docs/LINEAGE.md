# 語魂世代史 — The ToneSoul Lineage (2025-07 → today)

> 白話版,寫給外來的人。由 2026-07-02 對 8 個已封存前代倉庫的實地考古整理
> (逐倉讀 README + 抽讀核心原始碼;推論處標「※」)。
> 一句話總結:**每一代死掉的都是「假裝有的能力」,活下來的都是「可審計的形狀」。**

弧線:宣言 → 偽量化 → 正統工程詞彙 → 假實作 → 真資料結構 → 今天的可跑治理。

## 七代(依誕生時間)

| 代 | 倉庫(封存) | 問的問題 | 實況 | 活到今天的 |
|---|---|---|---|---|
| G1 | Genesis-ChainSet0.1(2025-07) | AI 能不能為自己說的話負責? | 人格協議寫成 prompt,零程式 | 編號誓言(∑049)→ `vow_system.py`;整個專案的一句話定義 |
| G2 | tone-soul-integrity(2025-07) | 語氣責任能不能量化? | 真管線假大腦(keyword if-else + mock embedding) | POAV ≥0.90 門檻 → `poav.py`;drift 檢測 |
| G3 | ToneSoul-Integrity-Protocol(2025-08) | 理論骨架是什麼? | 一天壽命的 EPK 三層摘要 | 「公理層不可分裂」→ `AXIOMS.json` ※ |
| G4 | tone-soul-integrity-tonesoul-xai(2025-08) | 能不能給責任一套數學? | 最完整的形式化 README;自承「程式能力不足」 | ρ 責任鏈 → Isnād chain;Φ/κ 偽數學死了 |
| G5 | governable-ai(2025-08) | 治理能不能用軟體工程正統做? | ~90% manifesto(DDD/Policy-as-Code) | Policy 詞彙 → `responsibility_runtime`;DDD 死(2026-06 裁決:absorb 詞彙、reject 實作) |
| G6 | AI-Ethics(2025-08) | 怎麼把思想歸檔成正典? | Codex 五卷檔案庫 | 「變更必留痕」→ 治理決策記錄 ※ |
| G7 | ai-soul-spine-system(2025-09) | 能不能造可執行的脊椎? | 外殼完整、核心硬編碼(`return 0.95`) | **Time-Island 原名活到今天**;它的假實作正是 E0-E4 分級要防的 |
| G8 | tonesoul-codex(2025-09) | 責任能不能變成可審計的資料結構? | 全血統程式最真(pydantic SourceTrace/VowObject) | SourceTrace → Isnād;VowObject 生命週期 → vow 系統;TrustLevel → E0-E4 ※ |

G8 之後經過渡 monolith ToneSoul-Architecture-Engine(TAE-01,2025-11,已標 superseded)
收斂為現行正典 **tonesoul52**(2025-12–)。

## 考古警告

8 個裡有 5 個的 README 在 2025-11 被「Guardian Protocol v1.0」統一重寫過——
它們描述的是**事後回填**的架構,不是誕生原貌。未修飾的原始地層只有
ToneSoul-Integrity-Protocol 和 tonesoul-xai。讀前代 README 時記得這層濾鏡。

## 死了但值得回訪的(parked assets)

1. **VowCollapsePredictor(G2/G4 的 κ)** — 違諾*之前*的預測性預警;當年死於沒有
   真訊號可餵,今天的 calibration 訊號(`calibration_score.py`)是候選燃料。
2. **VowObject.WithdrawalConditions(G8)** — 撤回承諾的合約化(修復責任人/
   行動/期限),比現行 vow 系統更細;值得對照補課。
3. **ΔI 反思差分(G4)** — 量測「反思前後誠實度有沒有真的變好」;honesty auditor
   有近親,但 before/after 差分這個形狀沒有。
4. **逐步 TrustLevel(G8)** — 每個 trace step 帶信任等級的粒度,今天只在 claim
   層(E0-E4)、不在 step 層。

## 這頁存在的理由

前代不是黑歷史,是**已付學費的實驗記錄**:G7 的硬編碼 0.95 教會了這個專案
「described ≠ implemented」,才有今天的證據分級;G2 的假大腦教會了「真管線
不等於真能力」,才有今天對 lexical gate 的誠實標注。封存它們、如實描述它們,
本身就是這個框架的論點在自己身上運作。
