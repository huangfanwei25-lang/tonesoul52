---
description: CI 紅燈除錯流程 — 本地綠但遠端紅
---

# CI Debug Workflow

當使用者說「CI 有紅燈」或 GitHub Actions 失敗時，**不要只跑本地 pytest**。

## 1. 先用 GitHub API 拉 CI 狀態
// turbo
```
read_url_content https://api.github.com/repos/Fan1234-1/tonesoul52/actions/runs?per_page=5&status=completed
```
解析 JSON，找出 `conclusion: "failure"` 的 workflow。

## 2. 拉失敗 workflow 的 job 細節
// turbo
```
read_url_content https://api.github.com/repos/Fan1234-1/tonesoul52/actions/runs/{run_id}/jobs
```
找出哪個 step 的 `conclusion` 是 `failure`。

## 3. 檢查本地 vs 遠端差異（最常見的坑）

### 3a. 檔案沒被 Git 追蹤
// turbo
```bash
git ls-files <suspicious_file>
```
如果輸出為空 → 檔案只存在本地，CI 看不到。

### 3b. 檢查 `.git/info/exclude`（隱形黑名單）
// turbo
```bash
cat .git/info/exclude
```
這個檔案是**本地限定的排除規則**，不會出現在 `.gitignore` 裡，容易被忽略。

### 3c. 檢查 requirements.txt
CI 只安裝 `requirements.txt` 裡列的套件。本地 `.venv` 可能有額外安裝的套件（如 `freezegun`）。

## 4. 常見 CI 失敗模式

| 症狀 | 原因 | 修復 |
|------|------|------|
| `ModuleNotFoundError` | 檔案沒 `git add` 或套件沒在 `requirements.txt` | `git add -f` + 更新 requirements |
| `AGENTS.md hash mismatch` | `agent-integrity-check.yml` 裡的 hash 過期 | 更新 yml 裡的 EXPECTED hash |
| `Commit Attribution` 失敗 | commit 缺少 `Authored-by:` trailer | 加 trailer 或調整 workflow 容忍度 |
| `ruff I001` | import 排序問題 | `ruff check --fix` |

## 5. 驗證修復後
// turbo
```bash
git push origin master
```
然後再次用步驟 1 的 API 確認新 run 是否全綠。

## 關鍵原則
> **本地 pytest 全過 ≠ CI 全過。** 永遠要用 GitHub API 或瀏覽器確認遠端狀態。
