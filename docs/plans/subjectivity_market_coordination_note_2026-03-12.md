# Subjectivity / Market Coordination Note (2026-03-12)

## Purpose

這份說明不是新 phase。

它只做一件事：把 `Market Mirror` 與 `CODEX subjectivity` 兩條工作線的
commit 邊界講清楚，避免後續 agent 讀錯最近的歷史。

## Commit Boundary

### Market Mirror

`1ab648c`

Commit message:

`feat(market): Phase 136-137 Dream Engine + Gold Detector [antigravity]`

這一筆才是 Market Mirror 的實際提交，範圍包括：

- `tonesoul/market/`
- `scripts/run_gold_scan.py`
- `scripts/test_dream_engine_5289.py`
- 其他 market 掃描 / 分析腳本
- `tests/smoke_test_market.py`
- market 規劃文件，例如 `docs/plans/phase140_codex_coordination_briefing.md`

### CODEX Subjectivity Lane

本次 CODEX 提交是另一條獨立工作線。

它的範圍是 subjectivity review / reporting / handoff / preview mirror，
不是 market pipeline。

主要內容包括：

- `docs/plans/memory_subjectivity_*`
- `docs/status/subjectivity_*`
- `tonesoul/memory/subjectivity_*`
- `scripts/run_subjectivity_*`
- `scripts/run_reviewed_promotion.py`
- `tests/test_subjectivity_*`
- `tests/test_run_subjectivity_*`
- `scripts/run_refreshable_artifact_report.py`
- `scripts/run_worktree_settlement_report.py`
- `scripts/run_repo_governance_settlement_report.py`

## Reading Rule For Future Agents

如果你在 `1ab648c` 之後看到另一筆同日 commit，請不要把它當成
Market Mirror 的延伸。

判斷方式很簡單：

- 只要變更集中在 `tonesoul/memory/subjectivity_*`、`docs/status/subjectivity_*`
  與 handoff / mirror scripts，它就是 CODEX 的 subjectivity lane
- 只有碰到 `tonesoul/market/` 與 market scripts，才算 Market Mirror

## Negative Scope

這份 subjectivity 提交明確不包含：

- `tonesoul/market/`
- `scripts/run_gold_scan.py`
- `scripts/test_dream_engine_5289.py`
- `tests/smoke_test_market.py`
- `memory/crystals.jsonl`

## Why This Note Exists

`docs/plans/phase140_codex_coordination_briefing.md` 已經說明：

- Market Mirror 與 subjectivity review 系統沒有交集
- CODEX 可以安全提交自己的 Phase 239/240 subjectivity 變更

這份 note 只是把「理論上可分開」進一步寫成「實際 commit 邊界已分開」。
