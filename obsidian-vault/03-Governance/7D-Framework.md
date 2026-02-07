---
title: 7D 審計框架
aliases: [7D, 七維審計, 7D Framework]
tags: [governance, audit, framework]
related:
  - "[[Council]]"
  - "[[Genesis]]"
  - "[[Axioms]]"
---

# 7D 審計框架

> 把「懷疑」制度化，才能把「信任」工程化。

---

## 🎯 什麼是 7D

ToneSoul 的目標是建立可驗證、可追責、可持續校準的系統。7D 把這個目標拆成七個可觀測的維度：

```
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ TDD │ RDD │ DDD │ XDD │ GDD │ CDD │ SDH │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

---

## 📊 維度說明

| 維度 | 英文 | 中文 | 說明 |
|------|------|------|------|
| **TDD** | Test-Driven | 測試驅動 | 測試覆蓋率、CI 通過率 |
| **RDD** | Red-team Driven | 紅隊防禦 | 對抗測試案例 |
| **DDD** | Data-Driven | 資料驅動 | 記憶鮮度、數據一致性 |
| **XDD** | Explainability-Driven | 可解釋性 | 決策透明度 |
| **GDD** | Governance-Driven | 治理驅動 | 責任追蹤完整性 |
| **CDD** | Context-coherent | 上下文一致 | 狀態同步、fallback 策略 |
| **SDH** | System Health | 系統健康 | API 可用性、錯誤率 |

---

## 📈 當前狀態

| 維度 | 狀態 | 說明 |
|------|------|------|
| TDD | ✅ 強 | 343+ tests |
| RDD | 🟡 中 | 11 cases (目標 20) |
| DDD | 🟡 中 | 7 天 stale SLA |
| XDD | ✅ 中強 | Council verdict |
| GDD | ✅ 中強 | Genesis 責任鏈 |
| CDD | ✅ 中強 | Backend-first 策略 |
| SDH | ✅ 中強 | CI smoke tests |

---

## 📎 相關概念

- [[Council]] - 審議系統
- [[Genesis]] - 責任追蹤
- [[Axioms]] - 核心公理
