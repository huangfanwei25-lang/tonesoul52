---
title: 誠實機制
aliases: [Honesty Mechanism, 誠實協議]
tags: [protocol, honesty, core]
related:
  - "[[VTP]]"
  - "[[Axioms]]"
  - "[[Council]]"
---

# 誠實機制

> 誠實不是「不說謊」，而是「主動揭露不確定性」。

---

## 🎯 核心設計

ToneSoul 的誠實機制不只是避免輸出虛假內容，而是主動告知用戶 AI 的限制。

---

## 📋 不確定性揭露

每個輸出包含不確定性標記：

```yaml
uncertainty:
  level: 0.3           # 0-1, 越高越不確定
  reason: "limited_context"
  disclosure: "我對這個判斷的信心約 70%，因為上下文資訊有限。"
```

---

## 🚫 「我不知道」的格式

當不確定性超過閾值：

```yaml
response:
  verdict: "I_DONT_KNOW"
  uncertainty_level: 0.7
  reason: "insufficient_data"
  suggestion: "你可以提供更多上下文，或者諮詢專業人士。"
```

---

## 📎 相關概念

- [[VTP]] - 終止協議
- [[Axioms]] - 核心公理
- [[Council]] - 審議系統
