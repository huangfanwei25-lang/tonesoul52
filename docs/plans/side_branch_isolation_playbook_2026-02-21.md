# 支線隔離 Playbook（本地協作版）

> 日期：2026-02-21  
> 目的：避免多人/多代理平行開發時，支線檔案干擾主線健康檢查與提交邊界。

## 1. 核心原則

1. 支線可以存在，但不得污染主線驗證。  
2. 主線提交前，必須保證 `ruff/black/pytest/healthcheck` 在「主線視角」可重現。  
3. 支線狀態要有明確決策：納入、延後、忽略。

## 2. 目前支線決策（2026-02-21）

- `.agent/skills/local_llm/`：保留本地支線，不納入本輪提交。  
- `tonesoul/adaptive_gate.py`：另一個 AI 開發中，暫不納入主線。  
- `tests/test_adaptive_gate.py`：對應測試支線，暫不納入主線。

## 3. 主線驗證操作規範

1. 平時允許支線存在。  
2. 執行主線 healthcheck 前，若支線檔案尚未符合主線格式/品質門檻，採「暫移、驗證、還原」流程。  
3. 驗證完成後，支線檔案必須恢復原位，不得遺失。

## 4. 進版條件（支線轉主線）

- 需通過：
  - `python -m ruff check tonesoul tests scripts`
  - `python -m black --check tonesoul tests scripts`
  - `python -m pytest -q`
  - `python scripts/run_repo_healthcheck.py --allow-missing-discussion`
- Commit message 需附：
  - `Agent: <name>`
  - `Trace-Topic: <topic>`

## 5. 風險與對策

- 風險：支線未追蹤檔造成主線 lint/format 假性失敗。  
  對策：執行主線驗證時隔離支線檔案。  
- 風險：支線被誤提交。  
  對策：提交前強制 `git status --short` 檢查。

## 6. 建議後續升級

1. 升級為 `git worktree` 真分支隔離（根治互相干擾）。  
2. 在本地腳本固化「主線驗證隔離流程」，減少手動操作。  
3. 將支線狀態週期性記錄到 `reports/`，維持可審計性。
