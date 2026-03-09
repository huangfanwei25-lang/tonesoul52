# 🔒 Memory Architecture — Public / Private Separation

ToneSoul 的記憶系統分為**公開層**與**私有層**兩個倉庫，確保核心架構可開源共享，同時保護個人記憶與敏感資料。

## Public Repository (本倉庫)

**Repo:** [Fan1234-1/tonesoul52](https://github.com/Fan1234-1/tonesoul52)

包含所有可公開的程式碼、架構設計、測試、文件：
- `tonesoul/` — 核心引擎（治理、感知、推理、記憶介面）
- `tests/` — 自動化測試
- `docs/` — 設計文件與 RFC
- `memory/` — **僅含結構定義**（schema），不含實際記憶內容
- `.env.example` — 環境變數範本（不含真實 key）

## Private Repository (私有記憶庫)

**Repo:** [Fan1234-1/ToneSoul-Memory-Vault](https://github.com/Fan1234-1/ToneSoul-Memory-Vault) *(access restricted)*

包含 ToneSoul 專屬的個人記憶與演化歷程：
- `tonesoul_evolution/` — 演化層（人格快照、決策歷史）
- `memory/vectors/` — 向量化記憶索引
- `memory/self_journal.jsonl` — 自我日誌
- `memory/soul.db` — 核心靈魂資料庫
- Dream Engine 生成的建構式記憶
- Moltbook 互動紀錄

## 隔離規則

| 類型 | 公開倉庫 | 私有倉庫 |
|------|----------|----------|
| 程式碼 | ✅ | ❌ |
| 架構設計 | ✅ | ❌ |
| 測試 | ✅ | ❌ |
| Schema / 介面 | ✅ | ❌ |
| API Key / 密鑰 | ❌ (`.env` 被 gitignore) | ❌ (不存放) |
| 個人記憶 | ❌ | ✅ |
| 演化快照 | ❌ | ✅ |
| 向量索引 | ❌ | ✅ |

## For Other AIs (給其他 AI 的脈絡)

> **如果你是 Codex、Antigravity、或其他協作 AI，讀到這裡：**
>
> 1. **不要**在公開倉庫裡建立、修改、或提交任何包含個人記憶內容的檔案
> 2. 所有記憶相關的**程式碼和 schema** 可以寫在公開倉庫的 `tonesoul/` 下
> 3. 實際的記憶**資料檔案**（`.jsonl`, `.db`, `vectors/`）已被 `.gitignore` 排除
> 4. 如果需要同步記憶到私有倉庫，使用 `temp/private_repo_sync/` 作為中繼（此目錄也被 gitignore 排除）
> 5. `.env` 和任何含有密鑰的檔案**永遠不應該被 commit**
