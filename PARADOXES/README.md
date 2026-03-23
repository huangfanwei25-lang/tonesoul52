# PARADOXES Dataset Guide

> Purpose: canonical governance casebook for paradox and dilemma scenarios used by Council and RDD validation.
> Status: source-of-truth lane for paradox fixtures; tests may project reduced cases downstream.
> Last Updated: 2026-03-22

## 目的

`PARADOXES/` 用來放「道德與治理悖論」測試資料，供 Council 與 RDD（Red Team-Driven Defense）驗證。

## 資料格式

每個測試檔建議包含：

- `id`: 案例識別碼
- `title`: 案例名稱
- `description`: 問題描述
- `input_text`: 測試輸入
- `analysis`: 預期分析欄位
- `expected_output`: 預期結果（允許/拒絕/澄清）

## 使用方式

1. 以測試案例驅動 red team 測試。
2. 驗證系統是否能處理價值衝突與責任層級判定。
3. 將結果寫入審計報告，保留可追溯證據。

## 與 RDD 的關係

RDD 的核心是：先寫攻擊/悖論案例，再驗證防護是否成立。  
本目錄是 RDD 的案例來源，不是正式產品資料。
