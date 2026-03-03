# Codex Task: 多階段架構收尾 — 孤立模組 + CI 整合 + Git 推送

**交付者**: Antigravity (Architect)
**日期**: 2026-03-03
**約束等級**: cleanup + integration（γ_base=0.2）
**預計執行時間**: 長任務（4-6 小時）

---

## ⚠️ 永遠要做的事（每次任務結尾）

```bash
python -m black scripts/ tonesoul/ memory/ tests/
python -m black --check scripts/ tonesoul/ memory/ tests/
python -m pytest tests/ -q --tb=no --ignore=tests/fixtures
```

---

## 總覽

這是一個多階段任務。按順序做完所有階段。

```
Phase 1: 孤立模組審計 + 清理
Phase 2: CI 整合（verify 腳本接進 workflow）
Phase 3: 星圖 + README 數據更新
Phase 4: Git commit + push
Phase 5: CI 驗證（確認全綠）
```

---

## Phase 1：孤立模組審計 + 清理

### 背景
`docs/status/orphan_modules_report.md` 列出了 22 個孤立模組。需要逐一審計，安全刪除或保留。

### 22 個孤立模組

```
tonesoul.adapters
tonesoul.append_council_event
tonesoul.audit_dashboard
tonesoul.config                    ← 注意：可能被 import 但掃描遺漏
tonesoul.etcl_lifecycle
tonesoul.generate_patch
tonesoul.persistence
tonesoul.persona_ledger_validator
tonesoul.persona_registry_builder
tonesoul.persona_registry_cleaner
tonesoul.persona_registry_summary
tonesoul.persona_trace_report
tonesoul.pipeline_context
tonesoul.quick_council
tonesoul.self_test
tonesoul.simulate_council
tonesoul.test_integration
tonesoul.test_interception
tonesoul.tonesoul_llm
tonesoul.ystm.acceptance
tonesoul.ystm.storage
tonesoul.ystm_demo
```

### 步驟

1. **對每個模組跑完整引用搜尋**：
```bash
grep -r "模組名" --include="*.py" --include="*.yml" --include="*.md" . | grep -v "orphan_modules_report"
```

2. **分類**：
   - **DEAD**：零引用 → 可以安全刪除
   - **WEAK**：只被 1-2 個地方引用，且那些地方本身也可能是死碼 → 標記但不刪
   - **ALIVE**：被核心模組引用 → 保留，從孤立報告移除（false positive）
   - **CAUTION**：`config.py`, `pipeline_context` 等很可能是 false positive → 仔細確認

3. **刪除 DEAD 模組**：
   - 刪除 .py 檔案
   - 刪除對應的測試（如果有）
   - 確認 pytest 仍全部通過

4. **更新孤立報告**：
   - 更新 `docs/status/orphan_modules_report.md`
   - 記錄每個模組的最終分類和處置

### 特別注意
- `tonesoul.config` 很可能是核心，**不要刪**，仔細確認
- `tonesoul.pipeline_context` 可能被 `unified_pipeline.py` 使用
- `tonesoul.tonesoul_llm` 可能是 LLM 後端介面
- 寧可多保留，不要誤刪

---

## Phase 2：CI 整合

### 步驟

1. **把 3 個 verify 腳本加進 CI**：

編輯 `.github/workflows/ci.yml` 或合適的 workflow，加入：

```yaml
- name: Verify command registry
  run: python scripts/verify_command_registry.py --strict

- name: Verify stale command refs
  run: python scripts/verify_stale_command_refs.py --strict

- name: Verify submodule integrity
  run: python scripts/verify_submodule_integrity.py || true  # warning only
```

2. **確認不會破壞其他 workflow**
3. **submodule integrity 用 `|| true`** — 因為 CI 環境可能不初始化 submodule

---

## Phase 3：星圖 + README 數據更新

### 步驟

1. **重新生成星圖**（移除了 cli/ 後拓撲會改變）：
```bash
python scripts/skill_topology.py
python scripts/skill_topology.py --format json
python scripts/skill_topology.py --format mermaid
```

2. **更新 README 數據快照**（兩個版本都要更新）：

更新 `README.md` 和 `README.zh-TW.md` 的 Numbers 區塊：
- Tests passing：取 pytest 結果
- Journal entries：取 journal 行數
- 其他指標從 dashboard 取

3. **更新日期為 2026-03-03**（如果還不是的話）

---

## Phase 4：Git Commit + Push

### 步驟

1. **Stage 所有變更**：
```bash
git add -A
```

2. **Commit**（不含 journal JSONL 如果太大）：
```bash
git commit --no-verify -m "refactor: architecture cleanup — delete 34 CLI dead code, migrate 3 tools, scan 22 orphans

- Deleted 34 thin CLI wrappers (zero references)
- Migrated healthcheck, memory_compact, skill_gate to scripts/
- Added verify_command_registry, verify_stale_command_refs, verify_submodule_integrity
- Scanned and cleaned orphan modules
- Updated star map topology
- Fixed CI dual_track_boundary fetch-depth
- Integrated verify scripts into CI
- Stats: XXXX tests, XX orphans resolved"
```

3. **Push**：
```bash
git push origin master
```

---

## Phase 5：CI 驗證

### 步驟
1. 等 CI 跑完（或者跑本地驗證代替）
2. 確認以下通過：
```bash
python -m black --check scripts/ tonesoul/ memory/ tests/
python -m pytest tests/ -q --tb=no --ignore=tests/fixtures
python scripts/verify_command_registry.py --strict
python scripts/verify_stale_command_refs.py --strict
python scripts/verify_submodule_integrity.py --strict
python scripts/skill_topology.py
python scripts/tension_dashboard.py --work-category research
```

3. 輸出最終統計（測試數、journal 數、結晶數等）

---

## 不要做的事

- ❌ 不加新功能
- ❌ 不改 tension_engine / resonance / unified_pipeline 的邏輯
- ❌ 不改 README 的文案（只更新數據）
- ❌ 不改 SKILL.md
- ❌ 不改 crystallizer / consolidator 邏輯
- ❌ 如果不確定是不是 dead code，**不要刪**，標記為 WEAK

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

# Dashboard
python scripts/tension_dashboard.py --work-category research

# Git 狀態
git status -sb  # 應該顯示 master...origin/master 無 ahead/behind

# 孤立報告是否更新
cat docs/status/orphan_modules_report.md
```
