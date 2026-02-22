# CI 有效性審計報告（2026-02-21）

> 範圍：`.github/workflows/*.yml`、相關 verifier scripts、workflow contracts 測試  
> 目標：避免「為了綠燈而綠燈」，只保留有治理價值的紅綠訊號

## 一、結論摘要

1. 遠端最新 `origin/master`（`d153528425b8c22202d56489235c6a37877a43f9`）在 GitHub API 上的 check-runs / workflow-runs 皆為成功。
2. 本輪找到並修正一個「有價值但會誤擋」的 gate 缺陷：`Dual-Track Boundary` 會把 private 路徑刪除也當違規。
3. 本輪同步修正 `Git Hygiene` 門檻漂移（workflow=40、主線規劃=28 不一致）。
4. 仍存在部分 workflow 功能重疊（`test.yml`、`ci.yml`、`pytest-ci.yml`、`integrity_tests.yml`），屬效率問題，不是 correctness 問題。

## 二、Workflow 有效性分類

| Workflow | 主要用途 | 分類 | 判斷 |
|---|---|---|---|
| `test.yml` | 主 CI（matrix test/lint/web/docs/red-team/attribution/memory） | `blocking` | 核心主線 gate |
| `repo_healthcheck.yml` | 聚合治理健康檢查與 artifact | `blocking` | 有治理價值 |
| `dual_track_boundary.yml` | 公私資料邊界防護 | `blocking` | 有治理價值（本輪已修） |
| `git_hygiene.yml` | git 物件與 tracked-ignored 衛生 | `blocking` | 有治理價值（門檻已對齊） |
| `semantic_health.yml` | council 語義健康與 AXIOMS 驗證 | `blocking` | 有領域價值 |
| `external_source_registry.yml` | 外部來源信任策略 | `blocking/operational` | 有治理價值 |
| `persona_swarm.yml` | swarm readiness gate | `blocking/operational` | 有治理價值 |
| `monthly_consolidation.yml` | 月度維運彙整 | `operational` | 非每次 PR 阻擋 |
| `agent-integrity-check.yml` | Agent 指令檔 hash 與隱藏字元防護 | `blocking` | 安全必要 |
| `vercel_preflight.yml` | 部署前手動 preflight | `operational` | 手動防呆 |
| `ci.yml` | 次主線 CI（test/lint/web_api_smoke） | `advisory/overlap` | 與 `test.yml` 重疊 |
| `pytest-ci.yml` | 單一 pytest lane | `advisory/overlap` | 與 `test.yml` matrix 重疊 |
| `integrity_tests.yml` | 模組與 schema/py_compile 快檢 | `advisory/overlap` | 與 `ci.yml`/`test.yml`部分重疊 |
| `critical_path.yml` | 小型 smoke | `advisory/overlap` | 與主 CI smoke 重疊 |

## 三、已修正問題

### P0（已修）：Dual-Track Boundary 誤擋 private 路徑刪除

**問題**  
舊邏輯只看 path，不看 git status。刪除 private 檔案（本來是合規清理）也會被判違規。

**修正內容**

- `scripts/verify_dual_track_boundary.py`
  - 改為解析 `name-status`（支援 `A/M/C/R/D`）
  - `D`（刪除）對 private path 視為允許清理，不阻擋
  - `R`（rename）會同時檢查舊/新路徑，防止 private 路徑外移漏檢
  - 新增 UTF-16 fallback 讀取（相容 PowerShell 可能產生的 `changed_files.txt` 編碼）
- `.github/workflows/dual_track_boundary.yml`
  - changed files 產生方式從 `--name-only` 改為 `--name-status`
- `tests/test_verify_dual_track_boundary.py`
  - 新增 name-status/UTF-16/刪除允許/rename 阻擋測試
- `tests/test_workflow_contracts.py`
  - 更新 dual-track workflow contract 斷言（name-status）

### P1（已修）：Git Hygiene 門檻不一致

**問題**  
`git_hygiene.yml` 使用 `--max-tracked-ignored 40`，但主線計畫與執行命令使用 28。

**修正內容**

- `.github/workflows/git_hygiene.yml`：40 -> 28
- `scripts/run_repo_healthcheck.py`：`DEFAULT_MAX_TRACKED_IGNORED` 40 -> 28
- `tests/test_run_repo_healthcheck.py`：同步更新斷言
- `tests/test_workflow_contracts.py`：新增 `git_hygiene` 門檻 contract 測試
- `docs/status/README.md`：同步文件命令為 28

## 四、驗證結果

### 本地測試

- `pytest -q tests/test_verify_dual_track_boundary.py tests/test_workflow_contracts.py tests/test_run_repo_healthcheck.py`  
  - `34 passed`
- `pytest -q`  
  - `915 passed, 2 warnings`
- `black --check --line-length 100 ...`（相關修改檔）  
  - pass
- `ruff check ...`（相關修改檔）  
  - pass

### 行為重現（Dual-Track）

- `D private_path + M normal_path`：`overall_ok=true`（允許清理）
- `R private_path -> public_path`：`overall_ok=false`（正確阻擋）

## 五、仍待決策（非阻擋、效率議題）

1. `test.yml` 與 `pytest-ci.yml` 都在 push/pr 執行 pytest，訊號高度重疊。
2. `ci.yml` 與 `test.yml` 都執行 lint 與部分測試，重複消耗 CI 配額。
3. `integrity_tests.yml` / `critical_path.yml` 與主 CI 有重疊快檢步驟。

建議先不一次性砍 workflow，改採「主責 CI + 補充 CI」兩層策略：

- 主責阻擋：`test.yml` + `repo_healthcheck.yml` + `dual_track_boundary.yml` + `agent-integrity-check.yml`
- 補充觀測：其餘改成 schedule 或 `workflow_dispatch`，避免每次 push 重複跑。

## 六、RFC-007 快速註記（本輪審閱）

`docs/rfc-007-structured-event-metadata.md` 方向正確，但需先修正 3 點再實作：

1. `ComputeGate.evaluate()` 前段沒有 verdict，`risk_level` 規則要拆成前段粗標記 + 後段 journal 升級。
2. 路徑應為 `tonesoul/gates/compute.py`（非 `gates/compute.py`）。
3. `user_intent` 穿透到 `record_self_memory()` 在 `pre_output_council.py` / `runtime.py` 仍有斷點，RFC 提案值得落地。
