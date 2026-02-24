---
description: Git 衛生與推送準則 — 防止殭屍程式與推送卡住
---

# Git 衛生開發準則

## 推送前必做（每次 commit 後）

// turbo
1. 確認 loose objects 數量，超過 500 就先 gc：
```powershell
git count-objects -vH
```

// turbo
2. 如果 loose count > 500 或 size > 50 MiB，執行清理：
```powershell
git gc --prune=now
```

// turbo
3. 推送時帶 progress，避免誤判殭屍：
```powershell
git push --progress
```

## 每週維護（建議週一）

// turbo
4. 深度壓縮（耗時但有效）：
```powershell
git gc --aggressive --prune=now
```

// turbo
5. 確認 pack size 合理（< 200 MiB）：
```powershell
git count-objects -vH
```

## 禁止事項

- **禁止** 追蹤超過 5 MiB 的檔案（用 .gitignore 排除）
- **禁止** 把 memory/*.jsonl、*.db、*.gguf 加入 git
- **禁止** 在背景執行 `git push` 而不帶 `--progress`

## 大檔案警戒清單

以下檔案必須永遠保持在 `.gitignore`：
```
memory/provenance_ledger.jsonl   # ~30 MiB
memory/self_journal.jsonl        # ~40 MiB
memory/soul.db                   # ~4.8 MiB
structure.txt                    # ~7.2 MiB
*.gguf                           # 模型檔 > 1 GiB
```

## 卡住時的處理 SOP

1. `git status` 確認 HEAD 與 origin 是否已同步
2. 如果已同步 → push 其實成功了，終止殭屍程式
3. 如果未同步 → `git push --progress` 重試，觀察百分比
4. 如果 30 秒無進度 → 檢查網路/認證，考慮用 SSH：
```powershell
git remote set-url origin git@github.com:Fan1234-1/tonesoul52.git
```
