# Codex Task: 架構清理 Round 2 — WEAK 孤立模組深度審計 + 清理

**交付者**: Antigravity (Architect)
**日期**: 2026-03-04
**約束等級**: cleanup-aggressive（γ_base=0.3）

---

## ⚠️ 永遠要做的事（每次任務結尾）

```bash
python -m black scripts/ tonesoul/ memory/ tests/
python -m black --check scripts/ tonesoul/ memory/ tests/
python -m pytest tests/ -q --tb=no --ignore=tests/fixtures
```

**跳過 = 整個交付失敗。**
**任何附帶效果（檔案重置、資料變動）必須在報告中明確提及。**

## ⚠️ 增量存檔規則

每完成一個 Task（A/B/C/D/E），立刻把進度寫入 `docs/status/round2_progress.md`：
- 已完成的 Task
- 每個模組的判決結果
- 當前 test 通過數

**目的**：如果你的 context/token 即將用完，至少有存檔點。不要等到全部做完才寫報告。先寫進度，再繼續下一個 Task。

---

## 背景

Round 1 保留了 19 個模組（ALIVE=4, WEAK=14, CAUTION=1）。
Round 2 目標：對 14 個 WEAK + 1 個 CAUTION **深度審計**，能刪就刪。

---

## Task A：深度引用分析

### 目標
對每個 WEAK/CAUTION 模組做比 Round 1 更深的分析：

### 15 個目標模組

```
# WEAK (14)
tonesoul/append_council_event.py
tonesoul/audit_dashboard.py
tonesoul/etcl_lifecycle.py
tonesoul/generate_patch.py
tonesoul/persistence.py
tonesoul/persona_ledger_validator.py
tonesoul/persona_registry_builder.py
tonesoul/persona_registry_cleaner.py
tonesoul/persona_registry_summary.py
tonesoul/persona_trace_report.py
tonesoul/quick_council.py
tonesoul/self_test.py
tonesoul/simulate_council.py
tonesoul/ystm/storage.py

# CAUTION (1)
tonesoul/pipeline_context.py
```

### 分析步驟（每個模組都要做）

1. **行數統計**：`wc -l` 或等效
2. **完整引用搜尋**（比 Round 1 更廣）：
```bash
grep -rn "模組名" --include="*.py" --include="*.yml" --include="*.md" --include="*.toml" --include="*.json" . \
  | grep -v orphan_modules \
  | grep -v CODEX_TASK \
  | grep -v __pycache__
```
3. **讀取模組內容**，判斷：
   - 它做什麼？
   - 有沒有被 `__init__.py` export？
   - 有沒有對應的測試？
   - 它的功能是否已被其他模組取代？

4. **分類判決**：
   - **DELETE** — 零引用 + 功能已被取代或從未使用
   - **ARCHIVE** — 有概念價值但不應在 production，移到 `docs/archive/`
   - **KEEP** — 確實有用或風險太高

---

## Task B：執行清理

### 規則

1. **DELETE 類**：直接刪 .py + 對應測試
2. **ARCHIVE 類**：
   - 在 `docs/archive/deprecated_modules/` 建立目錄
   - 把 .py 搬過去
   - 在 archive 目錄建 `README.md` 列出搬遷原因
3. **KEEP 類**：保持不動

### 刪除前確認
- 每個要刪的模組都要跑 `pytest` 確認無破壞
- 如果 pytest 失敗，該模組升級為 KEEP

---

## Task C：persona_registry 系列特殊處理

`persona_registry_builder.py`、`persona_registry_cleaner.py`、`persona_registry_summary.py` 是一組相關工具。

### 選項（選一）
1. 如果三個都是 DEAD → 全部 DELETE
2. 如果有一個有用 → 合併成一個 `persona_registry_tools.py`
3. 如果複雜度太高 → 全部 ARCHIVE

---

## Task D：pipeline_context.py 特殊處理

這是 CAUTION 等級，可能是架構邊界模組。

### 步驟
1. 讀取完整內容
2. 搜尋 `unified_pipeline.py` 是否 import 它
3. 搜尋 `pipeline` 相關模組是否依賴它
4. 如果 **零引用** → ARCHIVE（不是 DELETE，因為可能是未接線的設計）
5. 如果 **有引用** → KEEP 並從孤立報告中移除

---

## Task E：更新報告 + commit + push

### 步驟

1. 更新 `docs/status/orphan_modules_report.md`：
   - Round 2 結果加到底部
   - 每個模組的最終判決 + 理由

2. 更新星圖：
```bash
python scripts/skill_topology.py
```

3. Commit + push：
```bash
git add -A
git commit --no-verify -m "refactor: architecture cleanup round 2 — WEAK orphan deep audit

- Deep-audited 15 WEAK/CAUTION orphan modules
- Deleted: [列出刪除的]
- Archived: [列出 archive 的]
- Kept: [列出保留的]
- Updated orphan report and star map
- Tests: XXXX passed, black clean"

git push origin master
```

---

## 不要做的事

- ❌ 不加新功能
- ❌ 不改核心邏輯（tension_engine, resonance, pipeline, council）
- ❌ 不碰 memory/ 的 journal 或 crystals
- ❌ 不碰 README 或 SKILL.md
- ❌ 如果不確定，選 KEEP 而不是 DELETE
- ❌ 不做任何沒在報告中提到的改動

## 最終驗收

```bash
# 格式化
python -m black --check scripts/ tonesoul/ memory/ tests/

# 測試
python -m pytest tests/ -q --tb=no --ignore=tests/fixtures

# verify 腳本
python scripts/verify_command_registry.py --strict
python scripts/verify_stale_command_refs.py --strict

# 星圖
python scripts/skill_topology.py

# Git
git log --oneline -3
git status -sb

# 報告
cat docs/status/orphan_modules_report.md
```

**報告中必須包含：**
1. 每個模組的完整判決表（模組名 | 行數 | 引用數 | 判決 | 理由）
2. 以上所有驗收指令的輸出
