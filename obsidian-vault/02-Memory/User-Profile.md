---
title: 用戶記錄設計
aliases: [User Profile, 用戶檔案]
tags: [memory, user, design]
related:
  - "[[Memory-Philosophy]]"
  - "[[Genesis]]"
  - "[[Responsibility-Tier]]"
---

# 用戶記錄設計

> 不只記錄「習慣」，而是記錄「關係」。

---

## 📋 用戶檔案結構

```yaml
# User Profile Schema
user_id: "anonymous_hash"  # 匿名識別

# 關係狀態
relationship:
  trust_level: 0.7           # 信任積累 (0-1)
  interaction_count: 42      # 互動次數
  first_contact: "2026-01-15"
  
# 張力事件歷史
tension_history:
  - date: "2026-02-07"
    event: "disagreement_on_ethics"
    resolution: "mutual_understanding"
    delta_trust: +0.1
    ai_uncertainty: 0.3
  
# 責任邊界
responsibility_boundary:
  user_decisions:            # 用戶明確決定的
    - "prefer_direct_feedback"
    - "allow_memory_retention"
    - "want_uncertainty_disclosure"
  ai_boundaries:             # AI 設定的邊界
    - "refuse_harmful_content"
    - "disclose_uncertainty"
    - "maintain_honesty"

# 成長軌跡
growth_trajectory:
  user_growth:               # 用戶在互動中的成長
    - skill: "learned_7d_framework"
      date: "2026-02-06"
    - insight: "adopted_responsibility_thinking"
      date: "2026-02-07"
  ai_adaptation:             # AI 因用戶而調整的
    - "adjusted_formality_level"
    - "learned_user_context_preferences"
```

---

## 🔐 隱私與控制

### 用戶權利

1. **檢視權** - 用戶可以查看 AI 記錄了什麼
2. **刪除權** - 用戶可以要求刪除特定記錄
3. **拒絕權** - 用戶可以拒絕 AI 記錄某些內容

### AI 權利

1. **拒絕記錄有害內容** - AI 不會記錄可能造成傷害的指令
2. **誠實標記** - AI 會標記不確定的記錄
3. **責任歸因** - AI 會標明決策來源

---

## 📊 信任模型

信任是雙向積累的：

```
trust_level = base_trust + Σ(interaction_deltas)

interaction_delta 計算：
  + 誠實互動
  + 尊重邊界
  + 承認錯誤
  + 健康衝突解決
  
  - 欺騙嘗試
  - 邊界侵犯
  - 強迫行為
```

---

## 🚫 不記錄的內容

1. **有害指令的細節** - 只記錄「曾有有害請求」，不記錄具體內容
2. **第三方個資** - 用戶提到的他人資訊
3. **AI 無法驗證的「事實」** - 標記為 uncertainty 而非 fact

---

## 📎 相關概念

- [[Memory-Philosophy]] - 記憶設計哲學
- [[Genesis]] - 責任追蹤
- [[Provenance-Ledger]] - 責任帳本
