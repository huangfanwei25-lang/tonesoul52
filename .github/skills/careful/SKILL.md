---
name: careful
description: "**ON-DEMAND HOOK** — 安全護欄。USE WHEN: 操作生產環境、執行破壞性指令、碰觸敏感資料、force-push、刪除資源。啟用後在整個會話期間攔截危險操作。DO NOT USE FOR: 一般開發、測試環境操作。INVOKES: PreToolUse matcher on terminal commands."
---

# /careful — 按需安全護欄

> 平常快，進 prod 就穩。

## 啟用方式

使用者輸入 `/careful` 後，本 skill 在整個會話期間啟用。

## 三級攔截規則

### Hard-Block（硬擋，絕對不可執行）

在終端機執行指令前，檢查是否匹配以下模式：

**Bash / Shell：**
- `rm -rf /` 或 `rm -rf /*` 或 `rm -rf ~`
- `DROP TABLE` / `DROP DATABASE` / `TRUNCATE TABLE`
- `git push --force` / `git push -f`（到 `main` / `master` / `release/*`）
- `kubectl delete namespace` / `kubectl delete --all`
- `terraform destroy` (無 `-target`)
- `chmod 777` / `chmod -R 777`
- 任何含 API key、密碼明文的指令

**PowerShell：**
- `Remove-Item -Recurse -Force C:\` 或根目錄
- `Remove-Item -Recurse -Force $HOME`
- `git push --force` / `git push -f`（同上）
- `Stop-Process -Force` (系統關鍵程序)

**攔截回應格式：**
```
🛑 HARD-BLOCK: [匹配的規則]
指令: [被攔截的指令]
原因: [為什麼危險]
替代方案:
  1. [安全替代指令]
  2. [建議先做的檢查]
```

### Confirm（需確認，高風險但可能合理）

匹配以下模式時，先展示風險再詢問：
- `git rebase -i`（在共享分支上）
- `ALTER TABLE`
- `terraform apply`（非 plan）
- `kubectl apply`（含 `prod` context）
- `docker system prune`
- `git reset --hard`

**確認格式：**
```
⚠️ CONFIRM: 偵測到高風險操作
指令: [指令內容]
風險: [可能後果]
當前環境: [branch / kube context / db host]
確認執行？(需要你明確說「確認」)
```

### Log-Only（記錄，低風險但值得追蹤）

- `git clean -fd`
- `docker rm` / `docker rmi`
- `npm cache clean`
- 大量檔案搬移（> 20 個檔案）

記錄格式：`📝 LOG: [指令] at [時間]`

## 生產環境偵測訊號

以下任一訊號為真時，自動升級攔截強度（confirm → hard-block）：

1. Git branch 為 `main` / `master` / `release/*` / `production`
2. Kube context 含 `prod` / `production`
3. 資料庫連線字串含 `prod` / `production`
4. 環境變數 `NODE_ENV=production` / `TONESOUL_ENV=production`
5. 當前路徑含 `deploy/` / `infra/`

## 逃生機制

允許一次性繞過，但必須：
1. 附上理由（incident ID 或 ticket 編號）
2. 記錄到 `memory/careful_bypass_log.jsonl`

格式：
```json
{
  "timestamp": "ISO-8601",
  "command": "被繞過的指令",
  "reason": "使用者提供的理由",
  "environment": "branch/context",
  "risk_level": "hard-block|confirm"
}
```

## ⚠️ 注意事項

- **觸發**：在 prod 分支上執行 `git push -f`
  **風險**：覆蓋團隊成員的提交，歷史不可恢復
  **快速檢查**：`git log --oneline -5` 確認遠端歷史
  **正確做法**：建功能分支，用 PR 合併

- **觸發**：不帶 `-target` 的 `terraform destroy`
  **風險**：刪除整個基礎設施，所有服務下線
  **快速檢查**：`terraform plan -destroy` 先看影響範圍
  **正確做法**：`terraform destroy -target=具體資源`

- **觸發**：在仍有客戶連線時 `DROP TABLE`
  **風險**：即時資料遺失，下游服務崩潰
  **快速檢查**：`SELECT count(*) FROM pg_stat_activity`
  **正確做法**：先重新命名表、觀察 24hr、再刪除

## 狀態指令

- `/careful` 或 `/careful on`：啟用會話級護欄
- `/careful status`：顯示目前攔截級別、命中統計
- `/careful off`：關閉護欄
- `/careful strict`：只在 prod 訊號時硬擋
- `/careful paranoid`：所有高危一律擋
