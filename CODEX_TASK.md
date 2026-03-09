# Codex Task: Phase 7 — Dream Engine 整合 + 觀測儀表板 + 自動喚醒

**交付者**: Antigravity (Architect)
**日期**: 2026-03-09
**分支**: feat/env-perception（不可 push 到 master）

---

## ⚠️ 永遠要做的事（每次 commit 前）

```bash
python -m pytest tests/ -x --tb=short -q
ruff check tonesoul tests
```

**跳過 = 整個交付失敗。**

## ⚠️ 安全護欄（讀 AGENTS.md「Codex Full-Auto 安全護欄」段落）

- 不可刪除 tonesoul/ 下的核心模組
- 不可修改 .env, .gitignore, AGENTS.md, MEMORY.md
- 不可 commit API key 或 .env
- 不可 push 到 master
- 不可安裝系統套件
- 連續失敗 3 次必須停止並留記錄

---

## 脈絡恢復（先讀這些）

1. AGENTS.md — 行為規範
2. MEMORY.md — 公私記憶隔離
3. tonesoul/dream_engine.py — 現有 Dream Engine（633 行，已有完整碰撞邏輯）
4. tonesoul/dream_observability.py — 現有觀測模組
5. tonesoul/memory/write_gateway.py — 剛完成的記憶寫入閘門
6. tonesoul/memory/consolidator.py — 睡眠鞏固邏輯

---

## Task A：Dream Engine 接線 Write Gateway

### 目標
Dream Engine 的 `_build_collision` 產生的碰撞結果，需要經過 MemoryWriteGateway 寫入 soul.db。

### 步驟
1. 讀取 `dream_engine.py` 的 `run_cycle()` 方法
2. 在碰撞完成後，將 `DreamCollision` 轉換為 payload
3. 通過 `MemoryWriteGateway.write_payload()` 寫入
4. 確保 provenance 包含 source_url 和 dream_cycle_id
5. 測試：在 `tests/test_dream_engine.py` 中驗證寫入路徑

---

## Task B：觀測儀表板增強

### 目標
`dream_observability.py` 已有 SVG 圖表生成。增加以下指標追蹤：

### 步驟
1. 讀取 `dream_observability.py`，理解現有結構
2. 加入 `write_gateway` 的寫入統計（written/skipped/rejected 計數）
3. 加入 Dream Engine 碰撞成功率（collision 數 / stimuli 考慮數）
4. 如果有 `token_meter.py`，整合 token 使用量顯示
5. 測試：確保新指標能被正確計算

---

## Task C：自動喚醒機制

### 目標
`wakeup_loop.py` 已存在但可能未接線。確認它能：

### 步驟
1. 讀取 `wakeup_loop.py`，理解現有邏輯
2. 確認它能定時觸發 `DreamEngine.run_cycle()`
3. 確認它能觸發 `sleep_consolidate()` 做記憶壓縮
4. 加入簡單的排程邏輯（例如每 N 小時執行一次 dream cycle）
5. 加入 circuit breaker：如果 Dream Engine 連續 3 次失敗，暫停 1 小時
6. 測試：在 `tests/test_wakeup_loop.py` 中驗證排程和 circuit breaker

---

## Task D：把剩餘未追蹤檔案 commit

### 步驟
1. `git status` 檢查未追蹤檔案
2. 排除不該 commit 的：.env, *.db, *.jsonl 等 gitignore 已排除的
3. `git add` 合適的檔案
4. 跑 pytest + ruff
5. `git commit -m "feat: wire dream engine to write gateway, enhance observability, implement wakeup scheduler"`
6. `git push origin feat/env-perception`

---

## Task E：更新進度報告

### 步驟
1. 更新 `docs/status/` 裡的相關報告
2. 記錄：
   - Dream Engine ↔ Write Gateway 接線狀態
   - 新增的觀測指標
   - wakeup_loop 的排程配置
   - 目前 test 通過數

---

## 不要做的事

- ❌ 不改 GovernanceKernel 的核心邏輯（已審計通過）
- ❌ 不碰 unified_pipeline.py（剛重構完，不要再動）
- ❌ 不碰 soul_db.py 的 schema（write_gateway 已接好）
- ❌ 不要建新的 CI workflow
- ❌ 如果不確定，選保守方案
