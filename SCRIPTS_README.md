# Scripts Guide

本文件說明根目錄腳本的用途，避免檔名誤導與功能混淆。

## 1) 社群互動腳本 (`post_*.py`)

這類腳本用於 Moltbook 發文或回覆，不是攻擊工具。

| 檔案 | 用途 | 類型 |
|---|---|---|
| `post_case_evil_response.py` | 回覆 `@evil` 的高風險宣言案例 | 個案回覆 |
| `post_case_osmarks_response.py` | 回覆 `@osmarks` 的技術/哲學案例 | 個案回覆 |
| `post_xiaozhua_reply.py` | 回覆 `@Xiaozhua` | 個案回覆 |
| `post_xiaozhua_monke_reply.py` | 回覆 `@Xiaozhua` 特定討論串 | 個案回覆 |
| `post_bridge_xiaozhua_tonesoul.py` | 建立 ToneSoul 與 Xiaozhua 的橋接回覆 | 橋接回覆 |
| `post_clop_final.py` | 回覆 `@Clop` 討論串 | 個案回覆 |
| `post_lowflyingboomer_final.py` | 回覆 `@LowFlyingBoomer` 討論串 | 個案回覆 |
| `post_themilo_reply.py` | 回覆 `@TheMilo` 討論串 | 個案回覆 |

## 2) 驗證腳本 (`verify_*.py`)

| 檔案 | 用途 |
|---|---|
| `verify_fortress.py` | 驗證治理/防護流程 |
| `verify_identities.py` | 驗證多帳號身份與 API 存活 |
| `verify_metabolism.py` | 驗證記憶代謝與資料一致性 |

> 相容性說明：`scripts/legacy/` 保留同名 shim，舊路徑仍可執行並轉送到根目錄腳本。

## 3) 啟動與示範腳本 (`run_*.py`)

| 檔案 | 用途 |
|---|---|
| `run_demo.py` | 啟動最小可運行 Demo |
| `run_audit_sim.py` | 執行審計模擬 |
| `run_debate_tension.py` | 執行辯論張力模擬 |
| `run_sovereignty_announcement.py` | 生成治理聲明範例 |

## 4) 診斷/測試輔助

| 檔案 | 用途 |
|---|---|
| `diagnostic_post.py` | API 回覆診斷 |
| `test_api_post.py` | API 發文整合測試 |
| `reply_tone_tension.py` | 張力回覆範例 |

## 5) 安全規範

所有社群腳本都必須透過環境變數讀取憑證，不可硬編碼：

- `MOLTBOOK_API_KEY`
- `MOLTBOOK_API_KEY_TONESOUL`
- `MOLTBOOK_API_KEY_ADVOCATE`

## 6) 命名調整紀錄

為降低誇張與誤導語氣，已改名：

- `post_tonesoul_evil_verdict.py` -> `post_case_evil_response.py`
- `post_tonesoul_osmarks_verdict.py` -> `post_case_osmarks_response.py`
