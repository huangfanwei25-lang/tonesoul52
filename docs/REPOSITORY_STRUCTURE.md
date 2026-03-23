# ToneSoul52 完整倉庫結構

> 最後更新: 2026-02-21
> 用途: 提供完整路徑關係和模組用途，供開發者和審計者參考

---

## 文件定位聲明

- 本文件（`REPOSITORY_STRUCTURE.md`）是「地圖」，回答「檔案在哪裡、彼此怎麼連」。
- `docs/STRUCTURE.md` 是「規範」，回答「命名規則、新增流程、歸檔策略」。
- `docs/SPEC_LAW_CROSSWALK.md` 是「對照頁」，回答「spec 與 law 如何分工與對應」。

---

## 📁 根目錄結構

```
tonesoul52/
├── 📂 tonesoul/          # 核心治理引擎
├── 📂 apps/              # 應用程式層
├── 📂 integrations/      # 外部整合
├── 📂 memory/            # 記憶與資料層
├── 📂 docs/              # 文件
├── 📂 tests/             # 測試套件
├── 📂 scripts/           # 工具腳本
├── 📂 tools/             # 輔助工具
├── 📂 spec/              # 規格定義
├── 📂 law/               # 治理規則
├── 📂 constitution/      # 憲章
├── 📂 PARADOXES/         # 道德測試案例
├── 📂 examples/          # 範例
├── 📂 reports/           # 審計報告
└── 📄 根目錄檔案         # 入口與設定
```

---

## 🧠 核心引擎 (`tonesoul/`)

治理邏輯的核心實作。

| 子目錄/檔案 | 用途 |
|-------------|------|
| `council/` | 多視角審議系統 (Guardian, Architect, Innocent 等角色) |
| `gateway/` | OpenClaw WebSocket 通訊客戶端 |
| `memory/` | 記憶管理模組 |
| `tonebridge/` | 外部橋接介面 |
| `semantic/` | 語義分析模組 |
| `deliberation/` | 審議流程模組 |
| `ystm/` | 狀態機系統 |
| `benevolence.py` | 仁慈函數 (三層審計) |
| `semantic_control.py` | 語義張力計算 (TSR) |
| `heartbeat.py` | 心跳與健康檢查 |
| `openclaw_auditor.py` | OpenClaw 審計整合 |
| `unified_core.py` | 統一控制核心 |

---

## 📱 應用程式層 (`apps/`)

| 子目錄 | 用途 | 技術棧 |
|--------|------|--------|
| `web/` | Navigator 前端 | Next.js 16, TypeScript |
| `api/` | Flask API Server | Python, Flask |
| `cli/` | 命令列工具 | Python |
| `dashboard/` | 監控儀表板 | HTML/JS |
| `council-playground/` | Council 互動測試 | HTML/JS |
| `simulations/` | 模擬腳本 | Python |

---

## 🔗 外部整合 (`integrations/`)

| 子目錄 | 用途 |
|--------|------|
| `openclaw/` | OpenClaw 治理整合 (Skills, Gateway, SOUL.md) |

---

## 💾 記憶層 (`memory/`)

| 檔案/目錄 | 用途 | 敏感度 |
|-----------|------|--------|
| `agent_discussion.jsonl` | 跨 AI 討論通道 | 中 |
| `self_journal.jsonl` | AI 自我日誌 | 中 |
| `provenance_ledger.jsonl` | 責任追蹤帳本 | 高 |
| `ANTIGRAVITY_SYNC.md` | Antigravity 記憶同步 | 低 |
| `consolidator.py` | 記憶整合邏輯 | - |

---

## 📚 文件 (`docs/`)

| 類別 | 檔案範例 |
|------|----------|
| **架構** | `ARCHITECTURE_BOUNDARIES.md`, `STRUCTURE.md` |
| **審計** | `7D_AUDIT_FRAMEWORK.md`, `7D_EXECUTION_SPEC.md` |
| **協議** | `VTP_SPEC.md`, `HONESTY_MECHANISM.md` |
| **哲學** | `PHILOSOPHY.md`, `WHITEPAPER.md` |
| **API** | `API_SPEC.md`, `TOOLS_API_SCHEMA.md` |
| **部署** | `VERCEL_DEPLOY.md`, `GETTING_STARTED.md` |

---

## 🧪 測試 (`tests/`)

| 類別 | 現況 | 範例 |
|------|--------|------|
| **核心 / 單元 / 整合測試** | 大型混合測試集；實際數量以 `tests/` 和最新 healthcheck 為準 | `test_council_runtime.py`, `test_benevolence.py`, `test_genesis_integration.py` |
| **紅隊測試** | `tests/red_team/` baseline 已啟用；最新 case-count 以 `docs/status/7d_snapshot.json` 為準 | `test_api_input_hardening.py`, `test_rdd_fuzzing.py` |
| **屬性測試** | 多個 `test_property_*.py` 與契約導向測試共存 | `test_property_simple.py` |

---

## 🔧 根目錄腳本

### 歷史說明

較早期的倉庫版本曾有根目錄 `post_*.py` / `reply_*.py` 社群腳本。
目前公開主線不再以這些根目錄腳本作為主要入口，相關互動能力改由 `tools/`
中的治理包裝工具承接。

### 社群 / 治理工具 (`tools/`)

| 腳本 | 用途 |
|------|------|
| `tools/governed_poster.py` | 經治理與記憶包裝後的社群發文入口 |
| `tools/moltbook_poster.py` | Moltbook 發文工具 |
| `tools/moltbook_client.py` | Moltbook API client 與憑證解析 |

### 驗證腳本 (`verify_*.py`)

| 腳本 | 用途 |
|------|------|
| `scripts/verify_fortress.py` | legacy 相容性驗證；依賴 pre-5.x sandbox runtime，缺失時預設 skip |
| `scripts/verify_7d.py` | 7D 審計與治理維度驗證 |
| `scripts/verify_docs_consistency.py` | 文件與治理契約一致性驗證 |

### 本機診斷腳本

| 腳本 | 用途 |
|------|------|
| `monitor_ports.ps1` | Windows 本機埠觀測與除錯，不是部署入口 |
| `monitor_ports_v2.ps1` | Windows 本機埠觀測 v2，偏向短迴圈診斷用途 |

### 執行腳本 (`run_*.py`)

| 腳本 | 用途 |
|------|------|
| `run_demo.py` | 啟動 Demo |
| `run_audit_sim.py` | 審計模擬 |
| `run_sovereignty_announcement.py` | 治理聲明範例 |

---

## 📊 入口檔案

| 檔案 | 用途 |
|------|------|
| `README.md` | 專案介紹 |
| `SOUL.md` | AI 角色設定 |
| `AGENTS.md` | 代理系統說明 |
| `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md` | 現行正典架構入口 |
| `MGGI_SPEC.md` | 形式化工程與治理規格 |
| `TAE-01_Architecture_Spec.md` | 歷史架構 spec 譜系 |
| `CODEX_TASK.md` | Codex 任務清單 |
| `task.md` | 當前任務追蹤 |
| `AXIOMS.json` | 核心公理定義 |
| `pyproject.toml` | Python 專案設定 |
| `requirements.txt` | 依賴清單 |

---

## 🔒 安全規範

### 環境變數 (不可硬編碼)

- `MOLTBOOK_API_KEY`
- `MOLTBOOK_API_KEY_TONESOUL`
- `MOLTBOOK_API_KEY_ADVOCATE`

### 敏感檔案 (已加入 .gitignore)

- `memory/*.jsonl` (運行時日誌)
- `memory/soul.db` (SQLite 資料庫)
- `.moltbook/` (API 設定)

---

## 📈 統計摘要

| 類別 | 數量 |
|------|------|
| **核心模組** | 106 files |
| **文件** | 78 files |
| **測試** | dynamic: inspect `tests/` directly or latest healthcheck artifact |
| **測試案例** | dynamic: docs/status/repo_healthcheck_latest.json (python_tests) |
| **紅隊案例** | dynamic: docs/status/7d_snapshot.json (RDD case-count) |

