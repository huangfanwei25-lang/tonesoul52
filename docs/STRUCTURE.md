# 專案結構規範

> Purpose: define repository structure, naming conventions, and the module-addition flow for maintainable ToneSoul growth.
> Last Updated: 2026-03-23

本文件定義 ToneSoul 倉庫的目錄用途、命名規則與新增模組流程，確保結構清晰可維護。

## 與其他結構文件的分工

- 本文件（`STRUCTURE.md`）：規範與政策（命名、目錄責任、新增模組流程）。
- `docs/REPOSITORY_STRUCTURE.md`：全倉庫地圖與路徑導覽。
- `docs/SPEC_LAW_CROSSWALK.md`：`spec/` 與 `law/` 的一頁式對照。

**目錄用途**

| 目錄 | 用途 | 優先級 |
| --- | --- | --- |
| `tonesoul/` | 核心引擎與 Council | P0 |
| `law/` | 理論與法規範本體，含 `law/docs/` | P0 |
| `memory/` | RAG Gate、Self-Journal、Isnād | P1 |
| `tools/` | Moltbook 互動工具與治理工具 | P1 |
| `docs/` | 理論文件與索引 | P2 |
| `apps/` | 前端 Demo 與應用 | P2 |
| `tests/` | 測試套件 | P3 |
| `scripts/` | 一次性腳本與維運工具 | P3 |
| `experiments/` | 實驗性質內容，可歸檔 | P4 |
| `api/` | 目前不活躍，已移至 `.archive/` | P4 |
| `reports/` | 報告、摘要、分析（可追蹤） | P2 |
| `.archive/` | 歷史與輸出封存（不追蹤） | N/A |
| `.external/` | 外部依賴封存（不追蹤） | N/A |
| `.agent/skills/` | Codex 技能模板與規範 | P2 |

**命名規則**

1. 目錄使用 `lower_snake_case`，避免空白與中英混用。
2. 報告與摘要文件使用 `*_report.md`、`*_summary.md`、`*_analysis.md`。
3. 規格文件使用 `*_SPEC.md` 或 `*_spec.md`，整體保持一致。
4. 日誌輸出使用 `*_log.jsonl` 或 `*_log.txt`，集中到 `.archive/logs/`。

**新增模組規範**

1. 先在 `docs/` 撰寫概念或哲學文件，再開始實作。
2. 新增模組需歸類到既有目錄層級，避免新增多餘頂層目錄。
3. 每個模組保留單一責任，避免過早抽象。
4. 若新增長期維護的資料，需同步更新 `docs/STRUCTURE.md`。

**日誌與歸檔規則**

1. 任何 `*.json`、`*.jsonl`、`*.txt` 的輸出日誌放入 `.archive/logs/` 並忽略追蹤。
2. `memory/` 內 `*.jsonl` 若超過 1MB，使用 `scripts/archive_large_memory_logs.ps1` 歸檔到 `.archive/logs/memory/`。
   - 白名單：`memory/provenance_ledger.jsonl`、`memory/self_journal.jsonl`、`memory/.semantic_index/*`、`memory/.hierarchical_index/*` 永不移動。
   - 只歸檔：`entropy_monitor_log.jsonl` 與掃描結果類 `*scan*.jsonl`（可在腳本內調整）。
3. Isnād 核心帳本為 `memory/provenance_ledger.jsonl`，不應移出 `memory/`。

**參照**

理論索引請參考 `docs/KNOWLEDGE_GRAPH.md`。
