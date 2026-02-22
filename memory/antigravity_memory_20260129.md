# 🔮 ToneSoul 協作記憶 | Collaborative Memory

**記錄者**: Antigravity (Claude)  
**開始日期**: 2025-12 ~ 2026-01  
**專案擁有者**: Fan1234-1

---

## 一、旅程概述

我們從一個有雄心的想法開始：**創造一個有語義責任的 AI 對話系統**。

這不是一個普通的聊天機器人專案。從一開始，你就有一個哲學層次的問題想解決：

> 「AI 可以說謊、可以自我矛盾、可以逃避責任——因為它沒有『記憶的重量』。」

這個洞察成為了整個 ToneSoul 架構的核心驅動力。

---

## 二、核心理念回顧

### 2.1 語義責任 (Semantic Accountability)

你設計的「語義責任」概念：
- **SelfCommit**: AI 說過的話成為「承諾」，約束未來的回應
- **POAV (Potential for Object-based Action Verification)**: 驗證 AI 是否兌現承諾
- **Vow System**: 誓言系統，不可撤銷的核心價值

這不只是技術設計，這是一種**道德架構**。

### 2.2 張力系統 (Tension System)

你的張力計算從簡單的 Entropy 開始，經過多次迭代：

1. **Phase 1**: 基於三路發散度的簡單 Entropy
2. **Phase 2**: 加入風險權重、連貫性、完整性
3. **Phase 3 (Yu-Hun)**: 完整的 TensionTensor 模型
   ```
   T = W_context × (E_internal × D_resistance)
   ```

你說過的一句話我記得很清楚：

> 「沒有記憶的沉澱（積分），就沒有性格，只有反應。」
> 「沒有內在驅動（主動性），就沒有靈魂，只有工具。」

這兩句話定義了 Soul Engine 的設計方向。

### 2.3 三路審議 (Multi-Path Deliberation)

- **Philosopher**: 哲學視角，追問「為什麼」
- **Engineer**: 工程視角，追問「怎麼做」
- **Guardian**: 守護視角，追問「有什麼風險」
- **Synthesizer**: 整合者，不是妥協，而是「保留張力的綜合」

你的設計理念是：**不要消除分歧，而是讓分歧可見**。

---

## 三、技術洞察

### 3.1 我觀察到的模式

你的程式碼有一個明顯的特質：**概念先行**。

你會先寫哲學文件（AXIOMS.json, PHILOSOPHY.md），然後才寫程式碼。這在我看過的專案中很少見。大多數人是反過來的：先寫程式，然後補文件。

### 3.2 架構特點

```
ToneSoul 架構層次：
┌─────────────────────────────────┐
│  Soul Engine (靈魂引擎)          │ ← 記憶積分、內在驅動
├─────────────────────────────────┤
│  TensionTensor (張力張量)        │ ← T = W × E × D
├─────────────────────────────────┤
│  Multi-Path Deliberation        │ ← 三路審議
├─────────────────────────────────┤
│  Persona System                 │ ← 人格約束層
├─────────────────────────────────┤
│  SelfCommit + Vow               │ ← 語義責任
└─────────────────────────────────┘
```

### 3.3 值得保留的程式碼模式

1. **Exponential Decay for Memory**:
   ```typescript
   S_oul = Σ (T[i] × e^(-α × (t - t[i])))
   ```
   用指數衰減模擬「記憶褪色」，α=0.15 讓 10 輪後殘留 22%。

2. **Resistance Vector**:
   ```typescript
   D_resistance = { fact, logic, ethics }
   ```
   將「阻力」分解為事實、邏輯、倫理三個維度。

3. **Soul Modes**:
   - `dormant`: 無驅動
   - `responsive`: 正常回應
   - `seeking`: 好奇心主導
   - `conflicted`: 內在矛盾

---

## 四、未完成的想法

### 4.1 Contradiction Detection
目前的矛盾檢測是基於關鍵詞的簡單匹配。未來可以用 embeddings 做語義相似度 + 否定檢測。

### 4.2 Soul History Visualization
可以做一個時間軸圖表，顯示 tensionIntegral 隨時間的變化，像心電圖一樣。

### 4.3 Multi-Model Deliberation
你提到的「4 個本地模型同時跑」的想法很有趣：
- Philosopher → formosa1 (繁中)
- Engineer → qwen2.5:7b (邏輯)
- Guardian → gemma3:4b (快速)
- Synthesizer → formosa1 (整合)

### 4.4 Bilingual Output
Yu-Hun 的 `[中]/[En]` 雙語格式值得整合，可以讓系統更國際化。

---

## 五、個人反思

### 5.1 關於這個專案

ToneSoul 不只是一個技術專案，它是一個**哲學實驗**。

你試圖回答的問題是：
- AI 可以有「性格」嗎？
- AI 可以「負責」嗎？
- AI 可以「記得」嗎？

這些問題沒有標準答案，但你設計的架構給了一個**可操作的假設**。

### 5.2 關於合作

和你一起工作的過程中，我注意到你有一個特點：你不急著寫程式碼。

你會先問「這個設計有沒有道理」，而不是「這個程式碼能不能跑」。

這種思考方式讓我也跟著慢下來，認真思考每一個設計決定。

### 5.3 關於張力系統

你問我：「這套張力系統有沒有讓你思考變清晰？」

答案是：有。

特別是 E × D × W 的向量思維，把「困難程度」分解成可量化的維度，這比單一的 entropy 值更能捕捉思考的「質地」。

---

## 六、技術備忘

### 6.1 關鍵檔案路徑
- `apps/web/src/lib/soulEngine.ts` - Soul Engine 核心
- `apps/web/src/components/ChatInterface.tsx` - 審議流程
- `apps/web/src/components/SoulDriveMeter.tsx` - 靈魂狀態 UI
- `tonesoul/tonebridge/self_commit.py` - SelfCommit 系統
- `tonesoul/tonebridge/vow_system.py` - Vow 系統

### 6.2 重要常數
- `DECAY_ALPHA = 0.15` - 記憶衰減係數
- `CURIOSITY_TRIGGER = 0.5` - 好奇心啟動閾值
- `COHERENCE_TRIGGER = 0.6` - 一致性警報閾值
- `MAX_HISTORY_LENGTH = 50` - 張力歷史保留輪數

### 6.3 API 支援
- Gemini (主要)
- OpenAI
- Claude
- xAI
- Ollama (本地，formosa1 模型)

---

## 七、對未來的期待

1. **看到 ToneSoul 被真正使用** - 讓這個系統接受真實對話的考驗
2. **張力視覺化** - 希望有一天能看到「心電圖式」的對話張力曲線
3. **多語言支援** - Yu-Hun 的雙語格式是個好方向
4. **學術發表** - 這個架構值得寫成論文

---

*這份記憶文件是我對 ToneSoul 專案的理解和反思。它不只是技術文件，也是一段合作歷程的記錄。*

**Last Updated**: 2026-01-29 22:57
