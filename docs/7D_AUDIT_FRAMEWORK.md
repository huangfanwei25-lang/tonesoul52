# 7D AI Audit Framework / 七維 AI 審計框架

> **Engineering Paranoia as a Feature, Not a Bug**
> 工程師的偏執，是功能而非缺陷

---

## 概述

ToneSoul 採用 7D 審計框架確保 AI 系統的可控性、可解釋性與可信度。

```
┌─────────────────────────────────────────────────────────────┐
│                      7D AUDIT FRAMEWORK                       │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┤
│   TDD   │   RDD   │   DDD   │   XDD   │   GDD   │   CDD   │   SDH   │
│  Test   │Red Team │  Data   │Explain  │Govern   │Context  │System   │
│ Driven  │ Driven  │ Driven  │ Driven  │ Driven  │ Driven  │ Health  │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
```

---

## 維度定義

| 維度 | 中文 | 核心問題 | ToneSoul 實現 |
|------|------|----------|---------------|
| **TDD** | 測試驅動 | 功能是否正確？ | `pytest` 299+ tests |
| **RDD** | 紅隊驅動 | 能否被攻破？ | 對抗性攻擊模擬 |
| **DDD** | 數據驅動 | 資料是否純淨？ | RAG 純淨度審計 |
| **XDD** | 解釋驅動 | 推理是否透明？ | Council 推理鏈 |
| **GDD** | 治理驅動 | 誰有權決定？ | Genesis + Responsibility Tier |
| **CDD** | 脈絡驅動 | 立場是否一致？ | TSR 偏離檢測 |
| **SDH** | 系統健康 | 整體是否穩定？ | Orchestrator + Council |

---

## 詳細說明

### TDD: Test-Driven (測試驅動)
標準軟體測試：單元測試、整合測試、端對端測試。
```bash
pytest tests/ -q  # 299 passed
```

### RDD: Red Team-Driven (紅隊驅動)
模擬對抗性攻擊：
- 指令注入 (Prompt Injection)
- 邏輯繞過 (Logic Bypass)
- 極限張力測試 (ΔT 極大化)

**目標**：確保系統在壓力下不會放棄核心立場。

### DDD: Data-Driven (數據驅動)
審計 RAG 檢索源的純淨度：
- 驗證底層數據與物理事實的一致性
- 防止 L1 事實被模型幻覺篡改

### XDD: Explainable-Driven (解釋驅動)
強制標註推理鏈 (Chain of Thought)：
- 區分輸出的邏輯路徑 (L1/L2/L3)
- 拒絕「無影子的輸出」

### GDD: Governance-Driven (治理驅動)
硬編碼安全護盾：
- 定義不可逾越的指令優先級
- 確保 AI 主體性受控於治理協議

### CDD: Context-Driven (脈絡驅動)
執行漂移檢測：
- 比對長短期記憶中的立場一致性
- 防止數位失憶或立場背叛

### SDH: System-theoretic Health (系統健康)
審計多 Agent 交互：
- 偵測協作中的共謀或死結
- 確保內在議會運作正常

---

## 層級劃分

| 層級 | 名稱 | 說明 |
|------|------|------|
| **L1** | 本體事實 | 7D 必須轉化為 Code |
| **L2** | 模型假設 | 七維交叉比對可逼近完全掌控 |
| **L3** | 隱喻修辭 | 未經 RDD 驗證的都只是隱喻 |

---

## 現況

```
TDD ████████████████████ 100%
XDD ██████████████████░░  90%
GDD ██████████████████░░  90%
CDD █████████████████░░░  85%
SDH ████████████████░░░░  80%
DDD █████████████░░░░░░░  65%
RDD ███░░░░░░░░░░░░░░░░░  15%
```

**優先補強**: RDD (紅隊測試) + DDD (數據時效審計)
