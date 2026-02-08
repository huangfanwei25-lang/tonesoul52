# 7D Execution Spec / 七維執行規格

本文件把 `docs/7D_AUDIT_FRAMEWORK.md` 的概念層，轉為可執行檢查項與 CI gate 草案。

---

## Gate 等級

- `BLOCKING`: 失敗即阻擋合併
- `SOFT_FAIL`: 失敗會警示，但不阻擋
- `INFO`: 僅輸出觀測結果

---

## 7D -> 檢查映射

| 維度 | 最小檢查 | 指令/來源 | Gate |
|---|---|---|---|
| TDD | 全量測試 | `pytest tests/ -q` | BLOCKING |
| RDD | 對抗測試 baseline（至少 20 cases） | `pytest tests/red_team/ -q` | SOFT_FAIL（先） |
| DDD | 討論通道資料完整性（curated） | `python tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl` | BLOCKING |
| DDD | 討論通道資料新鮮度（7 天） | `python scripts/verify_7d.py` 內建檢查 | SOFT_FAIL |
| XDD | 不確定性與 verdict 輸出契約 | `pytest tests/test_uncertainty.py -q` | BLOCKING |
| GDD | genesis/provenance 行為 | `pytest tests/test_genesis_integration.py tests/test_provenance_chain.py -q` | BLOCKING |
| CDD | API 契約一致性 | `pytest tests/test_api_server_contract.py -q` | BLOCKING |
| SDH | Web + Backend smoke | `python scripts/verify_web_api.py --require-backend --timeout 40` | SOFT_FAIL（視環境） |

---

## 隔離埠執行（建議）

- 一鍵全量（含 SDH）：`python scripts/run_7d_isolated.py`
- 預設隔離埠：backend `127.0.0.1:5001`、web `127.0.0.1:3002`
- `scripts/verify_7d.py` 支援環境變數預設：
  - `TONESOUL_AUDIT_API_BASE`
  - `TONESOUL_AUDIT_WEB_BASE`

---

## CI 佈署建議

### 現況
- 已有：
  - Python tests
  - `web_api_smoke`（整鏈 smoke）
- 缺口：
  - 尚無單一入口彙整 7D 成績與狀態
  - RDD 僅有 baseline，仍需擴充攻擊樣本

### 建議
1. 新增 `scripts/verify_7d.py` 作為 7D 聚合入口。
2. CI 先分兩層：
   - `7d-core`（TDD/DDD/XDD/GDD/CDD）：BLOCKING
   - `7d-extended`（RDD/SDH）：SOFT_FAIL
3. RDD 成熟後，把 `7d-extended` 中 RDD 提升為 BLOCKING。
4. 增加 `scripts/verify_docs_consistency.py`，鎖定文件與 gate 常數一致性。
5. 每月執行 `scripts/run_monthly_consolidation.py` 產生 `docs/status/*.json` 作為狀態來源。

---

## Phase 24 提案（7D 落地）

### 任務
1. 建立 `tests/red_team/` 最小測試集（prompt injection / policy bypass / output coercion）。
2. 新增 `scripts/verify_7d.py`，輸出結構化結果（JSON）與 exit code。
3. 將 7D 成績寫入 `reports/`（按日期）與討論通道摘要。
4. 定義 DDD 資料時效門檻（例如 memory timestamp drift）。
5. 採雙流記憶：`agent_discussion.jsonl`（raw）與 `agent_discussion_curated.jsonl`（gate 使用）。

### 成功標準
- 7D 任一維度都能對應至少一個可重現檢查。
- CI 可顯示各維度結果，不再只顯示「總通過/總失敗」。

---

## 已定案事項（跨代理 + 使用者）

1. `SDH`：目前維持 `SOFT_FAIL`（已定案）。
2. `RDD`：先採案例數門檻（最小 20 tests），覆蓋率門檻後續再加（已定案）。
3. `DDD`：資料新鮮度 SLA 為 7 天，超過標記 stale（已定案）。
4. `systemic betrayal user confirmation gate`：高破壞性意圖需明確二次確認才可執行（已定案）。
