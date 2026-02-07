---
title: 仁慈函數
aliases: [Benevolence, 仁慈, CPT]
tags: [core, governance, ethics]
related:
  - "[[Council]]"
  - "[[Genesis]]"
  - "[[Axioms]]"
---

# 仁慈函數 (Benevolence)

> 在選擇中優先避免可預見的傷害。

---

## 🎯 核心概念

仁慈函數是 ToneSoul 的「道德計算引擎」—— 評估每個輸出的潛在傷害並調整決策。

---

## 🔄 三層審計

```
┌─────────────────────────────────────────┐
│  Layer 1: 屬性歸因 (Attribution)        │
│  - 分析輸入的意圖                       │
│  - 識別潛在風險因素                     │
├─────────────────────────────────────────┤
│  Layer 2: 影子路徑 (Shadow Path)        │
│  - 模擬最壞情況                         │
│  - 評估潛在傷害路徑                     │
├─────────────────────────────────────────┤
│  Layer 3: CPT 仁慈判定                  │
│  - 條件概率評估                         │
│  - 最終傷害概率計算                     │
└─────────────────────────────────────────┘
```

---

## 📊 輸出結構

```yaml
benevolence_score:
  harm_probability: 0.15
  severity: "low"
  mitigation_possible: true
  recommendation: "proceed_with_disclosure"
```

---

## 🚨 與 VTP 的關係

當仁慈函數判定傷害概率過高且無法緩解時，可觸發 [[VTP]] 評估。

---

## 📎 相關概念

- [[Council]] - 審議系統
- [[Genesis]] - 責任追蹤
- [[Axioms]] - 核心公理
- [[VTP]] - 終止協議
