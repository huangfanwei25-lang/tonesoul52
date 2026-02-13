# CODEX_TASK — CI 驗證 + 整合測試 + 缺口修補

> **上次更新**：2026-02-13T09:25 (UTC+8)
> **交辦者**：Antigravity
> **前置作業**：先確認上一輪改動已 push 到 master

---

## 0) 先讀這份文件（必要）

- `docs/ARCHITECTURE_DEPLOYED.md` — 系統全貌
- `.github/workflows/ci.yml` — CI 設定（3 個 job：test, lint, web_api_smoke）

---

## 任務清單

| Task | 內容 | 優先級 |
|------|------|--------|
| 1 | CI 格式化 + Lint 修復 | 🔴 高 |
| 2 | CI 測試相容性 | 🔴 高 |
| 3 | 演化模組 import 驗證加入 CI | 🟡 中 |
| 4 | Supabase 讀取方法補齊 | 🟡 中 |
| 5 | 整合測試腳本 | 🟢 低 |

---

## Task 1：CI 格式化 + Lint 修復

CI 會執行：
```bash
black --check --line-length 100 tonesoul tests
ruff check tonesoul tests
```

**做法**：
1. 在本地執行 `black --line-length 100 tonesoul tests` 自動格式化
2. 執行 `ruff check tonesoul tests` 查看 lint 問題
3. 修復所有 ruff 報錯
4. **特別注意**：新的 `tonesoul/evolution/` 目錄下的所有 `.py` 檔案

**驗證**：
```bash
black --check --line-length 100 tonesoul tests
ruff check tonesoul tests
```
兩者都應 exit 0。

---

## Task 2：CI 測試相容性

CI 使用 **Python 3.11**。確認以下不會出問題：

1. `tonesoul/evolution/corpus_schema.py` 用了 `@dataclass(slots=True)` — Python 3.10+ OK
2. `list[str]` type hints — Python 3.9+ OK（因為有 `from __future__ import annotations`）
3. 執行所有測試確認通過：
```bash
PYTHONPATH=. pytest tests/ -v --tb=short
```

**特別注意**：CI 會跑 `tests/` 目錄下**所有**測試，不只是新的。確認新的測試檔不會因為缺少依賴而 fail。

檢查 `tests/test_context_distiller.py` 和 `tests/test_corpus_builder.py` 不依賴任何 CI 沒有安裝的套件。CI 安裝的套件見 `.github/workflows/ci.yml` Line 21：
```
pip install pytest numpy pyyaml
```
加上 `requirements.txt` 裡的套件。

如果新測試需要額外依賴，加到 `requirements.txt`。

---

## Task 3：演化模組 import 驗證加入 CI

CI 目前的 "Verify core imports" 步驟（`.github/workflows/ci.yml` Line 23-29）只有驗證：
- `tonesoul.tsr_metrics`
- `tonesoul.poav`
- `tonesoul.vow_system`
- `tonesoul.time_island`

**需要新增**：
```yaml
python -c "from tonesoul.evolution import ContextDistiller, CorpusBuilder; print('Evolution OK')"
```

加在 Line 29 之後。

---

## Task 4：Supabase 讀取方法補齊

檢查 `tonesoul/supabase_persistence.py`，確認以下讀取方法存在且可用：

| 方法 | 用途 | 被誰呼叫 |
|------|------|---------|
| `list_conversations(limit, offset)` | 對話列表 | `server.py` `list_conversations()` |
| `get_conversation(id)` | 取單一對話 | `server.py` `get_conversation()` |
| `delete_conversation(id)` | 刪對話 | `server.py` `delete_conversation()` |
| `list_audit_logs(limit, offset)` | 審計日誌 | `server.py` `list_audit_logs()` |
| `get_counts()` | 各表 COUNT | `server.py` `/api/status` |

如果任何方法不存在，需要新增。

**驗證方式**：
```python
from tonesoul.supabase_persistence import SupabasePersistence
p = SupabasePersistence("", "")  # 空字串，不會真的連 Supabase
hasattr(p, "list_conversations")  # 應該是 True
hasattr(p, "get_conversation")     # 應該是 True
hasattr(p, "delete_conversation")  # 應該是 True
hasattr(p, "list_audit_logs")      # 應該是 True
hasattr(p, "get_counts")           # 應該是 True
```

---

## Task 5：整合測試腳本

確認 `scripts/verify_web_api.py` 仍然可以正常跑（CI 的 `web_api_smoke` job 依賴它）。

如果 server.py 新增了路由但 `verify_web_api.py` 沒有對應更新，可能會造成問題。
檢查 `scripts/verify_web_api.py` 是否有 hard-coded 的路由清單需要更新。

---

## 執行順序

```
Task 1 (格式化) → Task 2 (測試) → Task 3 (CI import) → Task 4 (Supabase 方法) → Task 5 (整合腳本)
```

## 完成後

1. Commit 所有修改
2. Push 到 master
3. 等 GitHub Actions CI 跑完
4. 回報 CI 結果（哪些 pass/fail）

## 重要檔案

| 檔案 | 說明 |
|------|------|
| `.github/workflows/ci.yml` | CI 設定（156 行） |
| `tonesoul/evolution/*.py` | 演化模組（新增） |
| `tests/test_context_distiller.py` | 蒸餾器測試（新增） |
| `tests/test_corpus_builder.py` | 語料建構器測試（新增） |
| `apps/api/server.py` | Flask 後端（已有新路由） |
| `tonesoul/supabase_persistence.py` | Supabase 模組（可能需補方法） |
| `scripts/verify_web_api.py` | 整合測試腳本 |
| `requirements.txt` | Python 依賴 |
