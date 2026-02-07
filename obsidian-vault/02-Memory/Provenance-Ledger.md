---
title: Provenance Ledger
aliases: [責任鏈帳本, provenance_ledger]
tags: [memory, governance, provenance]
related:
  - "[[Genesis]]"
  - "[[7D-Framework]]"
---

# Provenance Ledger

記錄每次重要決策的責任鏈。

## 建議欄位

- id
- timestamp
- decision_type
- content_hash
- genesis
- council_votes
- uncertainty
- followup_action

## 使用規則

- 僅追加，不覆寫
- 修正以新事件追加
- 每筆都可連回原始上下文
