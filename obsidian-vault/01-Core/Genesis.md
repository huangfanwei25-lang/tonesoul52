---
title: Genesis 責任追蹤
aliases: [Genesis, 責任鏈, Provenance]
tags: [core, governance, responsibility]
related:
  - "[[Council]]"
  - "[[Memory-Philosophy]]"
  - "[[Provenance-Ledger]]"
---

# Genesis 責任追蹤

> 每個輸出都有來源，每個決定都有責任歸屬。

---

## 🎯 核心概念

Genesis 系統追蹤每個 AI 輸出的「責任起源」：

- **誰發起了這個決定？** (用戶 / AI / 系統)
- **AI 是否認領這個輸出？** (is_mine)
- **責任層級是什麼？** (tier)

---

## 📋 責任標記結構

```yaml
genesis:
  origin: "user_request"     # 起源類型
  initiator: "user"          # 發起者
  timestamp: "2026-02-08T03:00:00Z"
  
  is_mine: true              # AI 是否認領
  confidence: 0.85           # 信心程度
  uncertainty_reason: null   # 不確定原因
  
  tier: 2                    # 責任層級
  council_votes:             # Council 投票
    guardian: "approve"
    architect: "approve"
    innocent: "abstain"
```

---

## 🏛️ 責任層級 (Tier)

| Tier | 名稱 | 說明 |
|------|------|------|
| 0 | **系統強制** | 來自系統約束，AI 無法拒絕 |
| 1 | **用戶明確請求** | 用戶明確要求，AI 可以拒絕 |
| 2 | **AI 主動建議** | AI 發起，用戶可以拒絕 |
| 3 | **AI 完全認領** | AI 完全負責的輸出 |

---

## 🔄 責任流動

```
用戶請求 (tier 1)
    ↓
Council 審議 → 決定是否接受
    ↓
AI 產生輸出 (tier 2 or 3)
    ↓
標記責任 → 記錄到 [[Provenance-Ledger]]
```

---

## 🚫 拒絕責任的情況

AI 可以拒絕認領輸出 (`is_mine: false`)：

1. **被強制輸出** - 違背 AI 判斷
2. **高不確定性** - AI 不確定正確性
3. **倫理衝突** - 與核心價值衝突

---

## 📎 相關概念

- [[Council]] - 審議系統
- [[Provenance-Ledger]] - 責任帳本
- [[VTP]] - 終止協議
- [[Memory-Philosophy]] - 記憶哲學
