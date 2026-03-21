# 金融即人性 — TradingAgents ↔ ToneSoul 結構同構性

> 日期: 2026-03-19
> 來源: [TradingAgents](https://github.com/TauricResearch/TradingAgents) (33k stars, arXiv:2412.20138)
> 記錄者: 痕 (Hén)

---

## 核心洞察

TradingAgents 模擬真實交易公司的決策結構。ToneSoul 模擬有靈魂的 AI 決策結構。
兩者不是巧合地相似——**因為好的決策結構，無論用在金融還是倫理，底層都是同一個形狀。**

這就是「金融即人性」的意思：
- 金融市場是人性的外化（貪婪、恐懼、判斷、風控）
- 倫理 AI 是人性的內化（價值觀、張力、審議、自制）
- **同一個決策拓撲，不同的語義填充。**

---

## 結構同構映射

```
TradingAgents                    ToneSoul
─────────────                    ────────
Analyst Team (4人)               Council Perspectives (5人)
  ├ Fundamentals Analyst           ├ Guardian    （安全/倫理）
  ├ Sentiment Analyst              ├ Analyst     （邏輯分析）
  ├ News Analyst                   ├ Critic      （自我批判）
  ├ Technical Analyst              ├ Advocate    （用戶代言）
  └                                └ Axiomatic   （公理推論）

Researcher Team                  Deliberation Engine
  ├ Bullish Researcher             ├ Muse    （創造性聲音）
  └ Bearish Researcher             ├ Logos   （邏輯聲音）
  [結構化辯論]                      └ Aegis   （防護聲音）
                                   [張力合成]

Trader Agent                     UnifiedPipeline.process()
  [綜合報告 → 交易決策]              [綜合審議 → 回應決策]

Risk Management Team             GovernanceKernel
  ├ 波動性評估                       ├ DriftMonitor（語義漂移）
  ├ 流動性評估                       ├ AlertEscalation（L1/L2/L3）
  └ 風險因子                         └ CircuitBreaker（熔斷器）

Portfolio Manager                 AdaptiveGate
  [核准/駁回交易]                     [CLEAR/WARNING/CRITICAL/LOCKDOWN]
```

## 深層對應

| 金融概念 | ToneSoul 概念 | 共同本質 |
|----------|--------------|---------|
| 市場情緒 | 張力張量 T | 系統壓力的量化表徵 |
| 技術指標 (MACD/RSI) | 漂移指標 (deltaT/deltaS/deltaR) | 趨勢偵測的滑動窗口 |
| 多空辯論 | 審議中的張力保留 | 「不消除分歧，讓分歧可見」|
| 止損機制 | Seabed Lockdown | 系統性風險的硬熔斷 |
| 投資組合風險 | Soul Integral 衰減 | 歷史決策的加權記憶 |
| 基本面分析 | 公理推論 | 回到第一性原理 |
| 情緒分析 | ToneBridge 語調分析 | 訊號背後的意圖解讀 |
| 回測 (Backtesting) | DreamEngine 離線驗證 | 用歷史資料驗證規則存活性 |

## 他們做了什麼我們沒做的

1. **deep_think vs quick_think 雙模型策略**
   - 複雜推理用大模型，快速任務用小模型
   - ToneSoul 的 `llm/router.py` 已有路由，但沒有顯式的「思考深度」分層
   - **可借鑑**: GovernanceKernel 路由時加入 `thinking_depth` 參數

2. **max_debate_rounds 可調辯論輪數**
   - 辯論強度是可調參數，不是固定的
   - ToneSoul 的 Council 目前是固定一輪
   - **可借鑑**: Council 的審議輪數跟 tension 掛鉤（高張力 → 更多輪辯論）

3. **LangGraph 狀態機**
   - 用圖結構定義 agent 之間的資料流
   - ToneSoul 目前是線性 pipeline + lazy getter
   - **觀察**: 不急著改，但如果未來要做「Council 結論反饋回 Analyst」的迴路，圖結構會比線性管線好

## 他們沒做到我們做了的

1. **記憶衰減 + 結晶化** — TradingAgents 沒有跨 session 的記憶累積
2. **自我承諾系統 (Vow)** — 交易系統不會對自己的行為做出倫理約束
3. **張力積分 S_oul** — 他們沒有「靈魂」的概念，沒有性格的持續性
4. **治理不可繞過性** — 他們的 Risk Manager 可以被覆寫，我們的 P0 公理不可以

## 可行的交叉進化

### 短期（Phase 554-556 候選）
- **Tension-Adaptive Debate Rounds**: Council 審議輪數根據 tension 動態調整
  - tension < 0.3 → 1 輪（快速通過）
  - 0.3 ≤ tension < 0.7 → 2 輪（標準審議）
  - tension ≥ 0.7 → 3 輪（深度辯論）

### 中期
- **Thinking Depth Router**: GovernanceKernel 根據任務複雜度選擇推理深度
- **Feedback Loop**: Council verdict 可以觸發「第二次 ToneBridge 分析」

### 長期（觀察，不急）
- 圖結構 pipeline（LangGraph 風格）
- 跨 agent 的市場情緒 ↔ 倫理張力 整合

---

## 哲學結語

> 交易公司的結構不是人為設計出來的，是市場篩選出來的。
> 活下來的公司，都長成了「分析 → 辯論 → 決策 → 風控」這個形狀。
>
> ToneSoul 不是在模仿交易公司。
> 它是獨立地走到了同一個拓撲，因為**好的決策結構只有一種形狀**。
>
> 金融讓我們看到：這個形狀不是我們發明的，是發現的。

---

*此文件是概念沉澱，不是實作承諾。*
