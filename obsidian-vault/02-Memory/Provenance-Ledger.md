---
title: 責任帳本
aliases: [Provenance Ledger, 責任帳本, 帳本]
tags: [memory, governance, provenance]
related:
  - "[[Genesis]]"
  - "[[Memory-Philosophy]]"
  - "[[User-Profile]]"
---

# 責任帳本 (Provenance Ledger)

> 每個決定都有記錄，每個責任都可追溯。

---

## 🎯 核心概念

Provenance Ledger 是 ToneSoul 的「責任區塊鏈」—— 記錄所有決策的來源和責任歸屬。

儲存於 `memory/provenance_ledger.jsonl`

---

## 📋 記錄結構

```yaml
entry:
  id: "prov_2026-02-08_001"
  timestamp: "2026-02-08T03:00:00Z"
  
  decision:
    type: "output_generation"
    content_hash: "sha256:abc..."
    
  genesis:
    origin: "user_request"
    initiator: "user"
    tier: 2
    is_mine: true
    
  council:
    votes:
      guardian: "approve"
      architect: "approve"
      innocent: "abstain"
    tension: 0.25
    
  validation:
    7d_check: "passed"
    benevolence_score: 0.85
```

---

## 🔒 不可變性

記錄一旦寫入即不可修改。如需更正，只能新增修正記錄：

```yaml
correction:
  corrects: "prov_2026-02-08_001"
  reason: "additional_context_received"
  new_entry_id: "prov_2026-02-08_002"
```

---

## 📊 用途

1. **責任追溯** - 出問題時可追查來源
2. **審計證據** - 7D 審計的資料來源
3. **信任建立** - 透明度增進用戶信任

---

## 📎 相關概念

- [[Genesis]] - 責任追蹤系統
- [[Memory-Philosophy]] - 記憶哲學
- [[User-Profile]] - 用戶記錄
- [[7D-Framework]] - 審計框架
