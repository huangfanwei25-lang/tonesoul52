# ToneSoul v1.0 Release GO/NO-GO (2026-02-24)

## 結論

- 決策：`RC-GO`、`GA-NO-GO (暫緩)`
- 解讀：
  - 目前版本已達「可候選發版」穩定度，可進入 `v1.0.0-rc.1` 階段。
  - 但尚未達到「正式 GA（v1.0.0）」標準，仍有明確阻塞項需收斂。

## 已完成證據（Stable Baseline）

1. 7D 全綠（含 SDH）
   - 指令：
     - `python scripts/verify_7d.py --include-sdh --web-base https://tonesoul52-ruby.vercel.app --api-base https://tonesoul52-ruby.vercel.app --sync`
   - 結果：`OVERALL = 100`

2. Production smoke 全綠（same-origin）
   - 指令：
     - `python scripts/verify_web_api.py --web-base https://tonesoul52-ruby.vercel.app --api-base https://tonesoul52-ruby.vercel.app --same-origin`
   - 結果：`/api/backend-health`, `/api/chat`, `/api/conversation`, `/api/consent`, `/api/session-report` 全部成功

3. GitHub Actions 綠燈
   - Commit `fbbbbd1` 的主要 workflow（CI / ToneSoul CI / Repo Healthcheck / Pytest CI / Semantic Health 等）均為 `completed/success`

4. Web 發佈與靜態頁面
   - `npm --prefix apps/web run build` 成功
   - `/about` 可用，Google 驗證頁 `/googlec8eda191f83dd4fe.html` 可用（HTTP 200）

## 阻塞項（GA 前必須完成）

1. Elisa 整合 Phase 108 尚未完成（task.md）
   - `P0`: payload profile + route contract tests + `verify_web_api.py` integration scenario
   - `P1`: preflight Elisa checks + governance status surface
   - `P2`: CI blocking smoke for Elisa integration contract
   - `P3`: operational hardening（runbook / rollback / release checklist）

2. v1.0 正式 release artifact 尚未建立
   - 缺 `docs/RELEASE_NOTES_v1.0.0.md`
   - 缺 tag `v1.0.0`（目前僅 `v0.1.0`）

## 發版門檻表

| Gate | 目前狀態 | 說明 |
|---|---|---|
| 7D + SDH | PASS | 已達正式門檻 |
| CI workflows | PASS | 主流程綠燈 |
| Production API smoke | PASS | same-origin + mock fallback 正常 |
| Elisa Contract（P0-P2） | FAIL | 尚未實作完整阻擋門檻 |
| Runbook / Rollback（P3） | FAIL | 尚未補齊 |
| Release Artifacts（v1.0） | FAIL | release notes/tag 未建立 |

## 執行策略（建議）

1. 先發 `v1.0.0-rc.1`
   - 用於鎖定穩定基線，避免持續開發污染發版基準。

2. 兩輪收斂後 GA
   - Round A：完成 Phase 108 P0-P2（契約 + CI 阻擋）
   - Round B：完成 P3 + release artifact + tag `v1.0.0`

3. GA 驗收命令（固定）
   - `python scripts/verify_7d.py --include-sdh --web-base https://tonesoul52-ruby.vercel.app --api-base https://tonesoul52-ruby.vercel.app --sync`
   - `python scripts/verify_web_api.py --web-base https://tonesoul52-ruby.vercel.app --api-base https://tonesoul52-ruby.vercel.app --same-origin`
   - `npm --prefix apps/web run build`

## GA Status Update (2026-02-24)

- Decision update: `GA-GO`
- Resolution summary:
  - Phase 108 P0-P3 all completed (payload contract, preflight checks, CI blocking smoke, runbook/rollback).
  - v1.0.0 release artifact created: `docs/RELEASE_NOTES_v1.0.0.md`.
  - Release tag `v1.0.0` is published.
