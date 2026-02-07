# Release Plan v0.1.0

## 範圍

v0.1.0 以「可審計、可部署、可驗證」為交付標準。

## 必要功能

- Council 審議流程可運行
- Genesis/Responsibility Tier 可追蹤
- 7D 驗證可執行
- Web + API 端到端可驗證
- CI（test/lint/red-team/security）可重複通過

## Release Gate

- [ ] `pytest -v --tb=short --maxfail=5`
- [ ] `black --check --line-length 100 tonesoul tests`
- [ ] `ruff check tonesoul tests`
- [ ] `pytest tests/red_team -q`
- [ ] 生成 vulnerability assessment
- [ ] README 與部署文件同步更新

## 發布產物

- Git tag：`v0.1.0`
- GitHub Release notes
- 測試與覆蓋率 artifact
- 安全報告 artifact

## 風險與對策

| 風險 | 對策 |
|---|---|
| API key 管理不一致 | 強制環境變數 + 掃描檢查 |
| 模型輸出過度確定 | 強制 uncertainty disclosure |
| CI 因工具版本漂移失敗 | pin 關鍵工具版本 |
