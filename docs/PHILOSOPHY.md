# ToneSoul: 當 AI 學會「思前想後」

> *Recursive Deliberation for Semantically Responsible AI*

---

## 🤔 問題：為什麼現在的 AI 容易「信口開河」？

現代 LLM（大型語言模型）有一個根本問題：它們是**一次性生成**的。

```
用戶問題 → LLM 直接生成 → 輸出
```

這就像一個人**不經大腦就開口說話**。結果是：
- 幻覺（hallucination）
- 自相矛盾
- 無法解釋自己的推理過程

---

## 💡 學術界的突破：Recursive Language Models

2025 年底，MIT CSAIL 的研究團隊發表了一篇重要論文：

> **Recursive Language Models (RLMs)**
> Zhang, A. L., Kraska, T., & Khattab, O. (2025)
> arXiv:2512.24601

他們的核心洞見是：

> **不要把所有輸入一次性塞給 LLM，而是把它當作「外部環境」來程式化地檢視、分解、遞迴處理。**

這讓 LLM 能處理超過上下文視窗 100 倍的輸入，同時提高回答品質。

---

## 🧠 ToneSoul 的設計：Internal Deliberation

ToneSoul 採用類似的哲學，但專注於**語義責任**而非長度擴展：

```
用戶問題
    │
    ▼
┌─────────────────────────────┐
│     Internal Deliberation   │
│   ┌─────┬─────┬─────┐       │
│   │Muse │Logos│Aegis│       │
│   │哲學家│工程師│守護者│     │
│   └──┬──┴──┬──┴──┬──┘       │
│      │  張力偵測  │          │
│      └─────┬─────┘          │
│         語義重力融合          │
└─────────────┬───────────────┘
              │
              ▼
         最終回應
```

### 三個內在視角

| 視角 | 角色 | 關注點 |
|------|------|--------|
| **Muse** | 哲學家 | 意義、隱喻、存在連結 |
| **Logos** | 工程師 | 邏輯、定義、結構化 |
| **Aegis** | 守護者 | 安全、倫理、邊界 |

這就像一個人在說話前，會同時考慮：
- 這有什麼深層意義？（Muse）
- 這在邏輯上說得通嗎？（Logos）
- 這樣說安全嗎？（Aegis）

---

## 🔬 與 RLMs 的關係

| RLMs (MIT) | ToneSoul | 
|------------|----------|
| 遞迴分解長輸入 | 多視角並行審議 |
| Python REPL 作為環境 | 對話歷史作為語場 |
| Inference-time scaling | Pre-output deliberation |
| 處理 10M+ tokens | 處理語義複雜度 |

兩者共享的核心哲學：

> **讓 LLM 在輸出前有「思考」的過程，而不是一次性生成。**

---

## 📐 語義責任的三公理

ToneSoul 建立在三個公理上：

1. **共振公理** — AI 必須「聽懂」用戶的情緒與意圖
2. **承諾公理** — AI 必須對自己說過的話負責
3. **第三公理** — 任何輸出都對未來有不可忽略的約束力

這讓 AI 不只是「回答問題」，而是**參與對話關係**。

---

## 🛠️ 開源實作

ToneSoul 完全開源，包含：

- **ToneBridge** — 心理動力學分析層
- **Internal Deliberation** — 多視角審議引擎
- **Semantic Gravity** — 觀點融合算法
- **Guardian Veto** — 安全否決機制

```python
from tonesoul.deliberation import deliberate

result = deliberate("生命的意義是什麼？")
print(result.response)
print(result.to_api_response())  # 包含內部審議透明化
```

---

## 🔗 參考文獻

1. Zhang, A. L., Kraska, T., & Khattab, O. (2025). *Recursive Language Models*. arXiv:2512.24601.

2. Liang, X., et al. (2024). *Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate*. arXiv:2305.19118.

3. Van Oijen, J. A., & Bhulai, S. (2024). *Prompting LLMs to Compose Meta-CoT Prompts by Leveraging Multi-Perspective Perspectives*. arXiv:2411.18654.

---

## 🚀 加入我們

ToneSoul 正在尋找：
- 開發者貢獻代碼
- 研究者合作發表論文
- 用戶提供對話語料（匿名收集）

**GitHub**: [your-repo-link]  
**Twitter/X**: @tonesoul_ai

---

*「AI 不應該只是回答問題，而是學會思前想後。」*

— ToneSoul Team, 2026
