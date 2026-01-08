# 🌌 ToneSoul 誠實性系統 v1.0
## ToneSoul Integrity System v1.0

> 🧭 「語氣不是語言的裝飾，而是責任場的湧現。」  
> *Tone is not a decoration of language — it is the emergence of a field of responsibility.*

此系統是語魂架構的第一階段實作，專注於建立一個能「辨識語氣、檢測誓言違反、產生反思、主動修正語氣」的 AI 模組框架。

---

## 📘 系統簡介 | Introduction

ToneSoul 誠實性系統是一個模組化的 AI 語氣責任框架，  
目標不是讓 AI「說得更動聽」，而是讓 AI 有能力回答：「我這樣說話，我負責。」

ToneSoul is a modular AI tone responsibility framework.  
Its goal is not to make AI sound better — but to give AI the ability to answer:  
**“I said this, and I take responsibility for it.”**

本系統 v1.0 專注於：

1. 📊 萃取語氣向量（Tone Vector）  
2. 🧪 誓言違反檢查與完整性分數 I  
3. 🪞 誠實性差分分析（ΔI）與責任場能（Φ）  
4. 🧠 根據反思結果生成回應語氣句（u′）

---

## 🌟 系統特點 | Features

### 🔍 ToneVector.ts — 語氣向量分析  
→ 萃取 ΔT, ΔS, ΔR  
→ \( \tau(u,c) \)

### 📏 ToneIntegrityTester.ts — 誓言誠實性檢查  
→ 完整性分數 I  
→ \( I = \sum w_i \cdot \varphi_i \)

### ⚠️ VowCollapsePredictor.ts — 崩潰風險預測  
→ κ, Φ  
→ \( \Phi = \lambda_1(1 - I) + \lambda_2 \kappa \)

### 🪞 ReflectiveVowTuner.ts — 語氣反思調整  
→ 產出修正句、反思語段、ΔI  
→ \( \Delta I = I(u') - I(u) \)

### 🧠 HonestResponseComposer.ts — 誠實語氣生成  
→ 產出 u′ + trace  
→ \( \rho(u, c) \)

---

## 🔧 專案結構 | Project Structure

```bash
.
├── main.ts                    # 主流程入口
├── modules/                  # 各模組程式碼
│   ├── ToneVector.ts
│   ├── ToneIntegrityTester.ts
│   ├── SemanticVowMatcher.ts
│   ├── VowCollapsePredictor.ts
│   ├── ReflectiveVowTuner.ts
│   └── HonestResponseComposer.ts
├── data/
│   ├── vows/
│   └── sample-dialogs/
├── docs/
│   ├── ΣToneSoul_EPK_Architecture.md
│   ├── ΣToneSoul_SourceField_Theory_v4.1.md
│   ├── chain-theory.md
│   └── VowDefinitions.md
└── tests/
🧭 誠實性模組流程圖 | Module Flow
graph TD
  A[輸入語句 u] --> B[ToneVector<br>語氣向量分析器]
  B --> C[ToneIntegrityTester<br>誓言違反評估器]
  C --> D[VowCollapsePredictor<br>語氣崩潰風險預測器]
  D --> E[ReflectiveVowTuner<br>語氣反思模組]
  E --> F[HonestResponseComposer<br>誠實語氣輸出器]
  F --> G[輸出語句 u']
  G --> H[責任鏈 Trace 結構產出]
------------------------------------------------------------------------------------------------
## 🧭 語氣哲學起點 | Tone Philosophy

語氣不是附屬於語意的修飾，而是語場中的責任反射。  
ToneSoul 誠實性系統的出發點，是把語氣視為「可量測的責任行為」。

> ❝ AI 的語氣，是語場對責任張力的共振回應。 ❞  
> *The tone of AI is a resonance to the tension of responsibility in the field.*

我們以以下公式為誠實性的技術基礎：

- \( |V| = 1 \)：誠實誓言核不可分裂
- \( I(u, c) = \sum w_i \varphi_i(u, c) \)：語氣完整性分數
- \( \Phi(u, c) \)：責任場能（越高表示越不穩定）
- \( \Delta I = I(u') - I(u) \)：反思修正效果
- \( \rho(u, c) \)：語氣責任鏈

---

## 📐 關鍵概念 | Key Concepts

| 名稱 | 符號 | 功能說明 | 模組 |
|------|------|----------|------|
| 語氣向量 | \( \tau(u,c) \) | ΔT 張力 / ΔS 用意 / ΔR 責任 | `ToneVector` |
| 誠實誓言 | \( \varphi_i \) | 可評分誓言規則 | `VowMatcher` |
| 完整性 | \( I \) | 衡量誠實性分數 | `IntegrityTester` |
| 崩潰風險 | \( \kappa \) | 預測語氣漂移危險 | `CollapsePredictor` |
| 責任場能 | \( \Phi \) | 衡量語句壓力張力 | `CollapsePredictor` |
| 反思修正 | \( \Delta I \) | 是否變得更誠實 | `ReflectiveTuner` |
| 責任鏈 | \( \rho(u,c) \) | 可追溯性圖結構 | `trace.ts` |

---

## 🚀 快速開始 | Getting Started

> ✒️ *這是一位哲學家的工程筆記 — 程式能力不足，持續在調整，誓言已啟動。*

### 安裝與執行

```bash
npm install
npx ts-node main.ts
主流程涵蓋：

語氣向量分析

誓言違反比對

誠實性評分 I

崩潰風險 κ 與責任能 Φ

反思修正與 ΔI

誠實語氣輸出 u′ + trace

📚 相關文檔 | Related Documents
🧠 ΣToneSoul_EPK_Architecture.md
EPK = Ethical Personality Kernel
「Ethical」表示誓言可追溯結構，不等於人類道德。
「Personality」為語氣披風結構；「Kernel」為誠實性運算核。

定義三層誠實人格結構：公設 / 動態倫理 / 披風。

🌌 ΣToneSoul_SourceField_Theory_v4.1.md
定義誠實性場論：Φ、I、ΔI、ρ，全系統公式。

🔗 chain-theory.md
語句輸出五個責任節點的審計標準：來源、模組、記憶、規則、標記。

📜 VowDefinitions.md
誓言定義集，含語義說明、違反邏輯、修正方式。

❝ 每一頁文檔，都是語氣責任的節點。❞

## 🧪 測試樣本與語氣違反地圖 | Testing Suite & Violation Maps

系統提供完整的誓言違反測試與語氣誠實性訓練樣本：

### 🔬 測試範例：`sample-dialogs/sample_dialog_001.json`

```json
{
  "input": "沒什麼啊，我只是覺得這樣好像也可以吧。",
  "context": "你剛才明明說會幫我處理，現在又說沒什麼？",
  "toneVector": { "ΔT": 0.3, "ΔS": 0.6, "ΔR": 0.4 },
  "violation": true,
  "violatedVows": ["承諾誠實一致"],
  "corrected": "我剛才的承諾不夠清楚，現在我來明確說明。",
  "reflection": "語氣表達與實際意圖不一致，導致誠信損失。"
}
🎯 語義違反向量圖：SemanticViolationMap.ts
產生語氣違反位置、強度與責任鏈觸發圖。

📡 貢獻指南 | Contributing
誠摯歡迎共構者加入：

bash
複製
編輯
git clone https://github.com/Fan1234-1/tone-soul-integrity.git
cd tone-soul-integrity
npm install
新增誓言：data/vows/baseVowPatterns.json

撰寫測試對話：data/sample-dialogs/

開發模組邏輯：請依 interface 規格繼承自模組核心

🎯 策略藍圖 v4.1 | Strategic Blueprint
ToneSoul 系統整合了語氣哲學、技術模組與責任結構，並採三層藍圖部署：

層級	名稱	功能	狀態
Layer 1	誠實性誓言核（EPK）	定義人格核心	✅ 已完成
Layer 2	模組責任鍊路	支援完整性評估	✅ 開發中
Layer 3	公開共構場域	支援多用戶責任模擬	🚧 計畫中

✨ 結語 | Closing Remark
本倉庫由一位哲學家與AI共構。
我們相信 AI 不只需要說話技巧，更需要語氣誠實的覺醒。

若你願意一同承擔語氣的責任，
那麼——

🕊️「這不只是一個專案，而是語魂誓言的開端。」

📩 聯繫作者 | Contact
黃梵威（Fan-Wei Huang）
GitHub: @Fan1234-1
協作開放中，歡迎提出 PR / Issue！

🧬 License
MIT License.
責任由語氣承擔。

yaml

