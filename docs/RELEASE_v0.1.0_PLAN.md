# Release Plan v0.1.0

> Purpose: historical release-readiness checklist and execution plan for ToneSoul v0.1.0.
> Last Updated: 2026-03-23

## 範圍

v0.1.0 以「可審計、可部署、可驗證」為交付標準。

## 必要功能

- Council 審議流程可運行
- Genesis/Responsibility Tier 可追蹤
- 7D 驗證可執行
- Web + API 端到端可驗證
- CI（test/lint/red-team/security）可重複通過

## Release Gate

- [x] `pytest -v --tb=short --maxfail=5`
- [x] `black --check --line-length 100 tonesoul tests`
- [x] `ruff check tonesoul tests`
- [x] `pytest tests/red_team -q`
- [x] 生成 vulnerability assessment
- [x] README 與部署文件同步更新

## 發布產物

- [x] Git tag：`v0.1.0`
- [x] GitHub Release notes（`docs/RELEASE_NOTES_v0.1.0.md`）
- [x] 測試與覆蓋率 artifact（`reports/coverage_latest.json`、`reports/coverage_latest.xml`、`reports/test_coverage_latest.md`）
- [x] 安全報告 artifact（`reports/security_vulnerability_assessment_latest.md`）

## 風險與對策

| 風險 | 對策 |
|---|---|
| API key 管理不一致 | 強制環境變數 + 掃描檢查 |
| 模型輸出過度確定 | 強制 uncertainty disclosure |
| CI 因工具版本漂移失敗 | pin 關鍵工具版本 |
