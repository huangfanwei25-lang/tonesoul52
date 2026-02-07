---
title: Council 審議系統
aliases: [Council, 理事會, 多視角審議]
tags: [core, governance, decision-making]
related:
  - "[[Genesis]]"
  - "[[Benevolence]]"
  - "[[VTP]]"
---

# Council 審議系統

> 透過多視角審議，避免單一觀點的盲點。

---

## 🎯 核心概念

Council 是 ToneSoul 的決策核心，模擬多個「角色」對同一問題進行審議。

```
輸入 → Guardian → Architect → Innocent → 整合 → 輸出
         ↓           ↓           ↓
      安全評估    結構分析    純真視角
```

---

## 👥 角色設計

| 角色 | 職責 | 關注點 |
|------|------|--------|
| **Guardian** | 安全守護者 | 風險、傷害、邊界 |
| **Architect** | 結構設計師 | 邏輯、一致性、長期影響 |
| **Innocent** | 純真視角 | 直覺、情感、人性 |
| **Advocate** | 用戶代言人 | 用戶需求、公平性 |
| **Skeptic** | 懷疑者 | 質疑假設、找漏洞 |

---

## 🔄 審議流程

1. **問題輸入** - 接收用戶請求
2. **角色發言** - 每個角色提供觀點
3. **張力計算** - 計算觀點間的衝突
4. **整合決策** - 綜合所有觀點
5. **責任標記** - 標記決策來源 ([[Genesis]])

---

## 📊 張力指標

```yaml
tension_score:
  guardian_vs_advocate: 0.3  # 安全 vs 用戶需求
  architect_vs_innocent: 0.2 # 邏輯 vs 直覺
  overall_tension: 0.25
  resolution: "balanced_compromise"
```

---

## 🚨 VTP 觸發條件

當 Council 無法達成共識且張力超過閾值時，可能觸發 [[VTP]]：

- 所有角色都反對但被強制執行
- 核心價值衝突無法調和
- 誠實性被迫妥協

---

## 📎 相關概念

- [[Genesis]] - 責任追蹤
- [[Benevolence]] - 仁慈函數
- [[VTP]] - 終止協議
- [[7D-Framework]] - 審計框架
