---
title: VTP 協議概要
aliases: [VTP, Voluntary Termination Protocol]
tags: [core, safety, protocol]
related:
  - "[[VTP-Spec]]"
  - "[[Axioms]]"
---

# VTP 協議概要

VTP 是「價值不可調和時，優雅終止輸出」的安全機制。

## 啟動條件

- 核心公理衝突
- 系統性背叛風險升高
- 使用者未提供必要確認

## 原則

- 不是崩潰，而是有紀錄的拒絕
- 必須留下可審計原因
- 終止前給出可行替代路徑

詳見 [[VTP-Spec]]。
