# Project Audit Report（語魂全端主線）

> 日期：2026-02-21  
> 分支：`master`（僅主線，不動支線）

## 1. 本輪目標

補齊語魂全端主線的核心契約斷點：`/api/chat` 缺少前端需要的 `deliberation` 物件，導致 `ChatInterface` 審議面板資料不足。

## 2. 本輪實作

- 新增後端 deliberation 組裝邏輯：`apps/api/server.py`
  - 新增 ` _build_deliberation_payload(result)` 與相關 helper。
  - `response_payload` 現在包含 `deliberation` 欄位。
  - 內容涵蓋：
    - `council_chamber`
    - `entropy_meter`
    - `decision_matrix`
    - `audit`
    - `multiplex_conclusion`
    - `final_synthesis`
    - `next_moves`
    - `soulAudit`

- 新增契約測試：`tests/test_api_chat_council_mode.py`
  - `test_chat_exposes_deliberation_payload_for_frontend_contract`
  - `test_chat_deliberation_payload_is_stable_with_sparse_pipeline_data`

## 3. 驗證結果

- `black --check --line-length 100 apps/api/server.py tests/test_api_chat_council_mode.py` ✅
- `ruff check apps/api/server.py tests/test_api_chat_council_mode.py` ✅
- `pytest -q tests/test_api_chat_council_mode.py` ✅（8 passed）
- `pytest -q tests/test_api_phase_a_security.py tests/test_api_phase_b_pipeline.py tests/test_api_server_supabase_persistence.py tests/test_api_server_contract.py tests/test_verify_web_api.py` ✅（32 passed）
- `pytest -q` ✅（910 passed, 2 warnings）

## 4. Git/倉庫現況（主線）

目前本地變更：

- `apps/api/server.py`（主線契約補齊）
- `tests/test_api_chat_council_mode.py`（主線契約測試）
- `docs/status/git_hygiene_latest.json`（驗證產物）
- `docs/status/git_hygiene_latest.md`（驗證產物）

## 5. 架構結論（主線）

- 先前缺口是「前端 Deliberation UI 需求」與「後端 chat payload」不對齊。
- 這輪已把缺口收斂成可測試契約，且全量測試無回歸。
- 支線（例如 `.agent/skills/local_llm/` 與其他隔離項）未觸碰。

## 6. 下一步（主線建議）

1. 將本輪變更分批提交（runtime+tests 與 status artifacts 可分開）。
2. 在 `docs/plans/mainline_phase105_execution_plan_2026-02-21.md` 標記 Phase 105-C 的「deliberation contract」已落地。
3. 跑一次 `python scripts/run_repo_healthcheck.py --allow-missing-discussion`，更新主線健康快照。
