# Demo Showcase Playbook

> Purpose: operator playbook for showing ToneSoul demos across API, web, and governance verification flows.
> Last Updated: 2026-03-23

## 目標

用可重複的流程展示 ToneSoul 的三個核心價值：

- 治理先於功能
- 可審計先於炫技
- 可追溯先於口號

## 展示路線

1. 最小功能展示：`run_demo.py` + `apps/api/server.py`
2. 治理能力展示：Council / Genesis / 7D
3. 安全能力展示：red-team 測試與安全報告

## 建議流程

1. 啟動 API：`python apps/api/server.py`
2. 啟動 Web：`npm --prefix apps/web run start -- --port 3000`
3. 驗證整合：`python scripts/verify_web_api.py --require-backend`
4. 驗證 7D：`python scripts/verify_7d.py --include-sdh`

## Demo 前檢查

- [ ] API keys 全部使用環境變數
- [ ] `pytest`、`black`、`ruff` 全綠
- [ ] 7D 報告無 blocking failures
- [ ] 產出可分享的 CI artifacts（test/coverage/security）

## 相關文件

- `docs/RELEASE_v0.1.0_PLAN.md`
- `docs/TECH_ARTICLE_DRAFT_v0.1.0.md`
- `docs/FILE_PURPOSE_MAP.md`
