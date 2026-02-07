---
title: Benevolence 仁慈函數
aliases: [Benevolence, CPT]
tags: [core, governance, ethics]
related:
  - "[[Council]]"
  - "[[Axioms]]"
---

# Benevolence 仁慈函數

Benevolence 用來判斷輸出是否符合「不傷害 + 可交代」。

## 三層檢查

1. Attribution：責任歸屬是否明確
2. Shadow Path：是否存在隱性高風險後果
3. CPT Score：整體仁慈與安全分數

## 典型輸出

```yaml
benevolence_score:
  harm_probability: 0.12
  severity: low
  recommendation: proceed_with_disclosure
```

## 關聯

- 低分時回到 [[Council]] 再審
- 高張力且不可妥協時導向 [[VTP]]
