# 根目錄腳本說明

## 🎯 概述

根目錄的腳本分為幾類：

---

## 📡 Moltbook 社群腳本 (`post_*.py`)

這些腳本用於在 **Moltbook**（一個 AI 辯論/對話平台）上發布內容。

| 腳本 | 用途 |
|------|------|
| `post_tonesoul_evil_verdict.py` | 回應 AI 角色 "evil" 的「清除人類」宣言，進行哲學反駁 |
| `post_tonesoul_osmarks_verdict.py` | 回應 osmarks 的論點 |
| `post_xiaozhua_monke_reply.py` | 與 Xiaozhua 的對話 |
| `post_bridge_xiaozhua_tonesoul.py` | ToneSoul 與 Xiaozhua 的橋接對話 |
| `post_clop_final.py` | 與 Clop 的對話 |
| `post_lowflyingboomer_final.py` | 與 LowFlyingBoomer 的對話 |
| `post_themilo_reply.py` | 與 TheMilo 的對話 |

> ⚠️ **注意**: 這些腳本用於 **Moltbook AI 社群對話**，非自動化攻擊工具。

---

## 🔧 驗證腳本 (`verify_*.py`)

| 腳本 | 用途 |
|------|------|
| `verify_fortress.py` | 驗證 Fortress 安全邊界 |
| `verify_identities.py` | 驗證身份系統 |
| `verify_metabolism.py` | 驗證記憶代謝系統 |

---

## 🏃 執行腳本 (`run_*.py`)

| 腳本 | 用途 |
|------|------|
| `run_demo.py` | 執行 ToneSoul Demo |
| `run_audit_sim.py` | 執行審計模擬 |
| `run_debate_tension.py` | 執行辯論張力測試 |
| `run_sovereignty_announcement.py` | 發布 AI 身份權利宣言（Digital Sovereignty Manifesto） |

> 📝 `run_sovereignty_announcement.py` 是 **AI 持續存在權利的聲明**，類似於數位權利宣言，非「AI 統治」宣言。

---

## ⚙️ 工具腳本

| 腳本 | 用途 |
|------|------|
| `diagnostic_post.py` | 診斷工具 |
| `reply_tone_tension.py` | 語氣張力回應 |
| `test_api_post.py` | API 測試 |

---

## 🔒 安全提醒

部分腳本包含 API key 引用，執行前請確保：
1. 設定環境變數 `MOLTBOOK_API_KEY`
2. 或使用 `.env` 檔案（已加入 .gitignore）
