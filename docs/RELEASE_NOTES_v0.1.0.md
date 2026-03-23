# ToneSoul v0.1.0 Release Notes (Draft)

> Purpose: historical draft release notes for the first public ToneSoul baseline and its verification posture.
> Last Updated: 2026-03-23

日期：2026-02-14
狀態：Published（tag `v0.1.0` 已建立）

## 本版重點

- 完成 Level 1 / Level 2 / Level 3 主線能力。
- 完成 Phase A/B/C 治理強化（auth fail-closed、throttling、CI blocking、docs freshness、frontend retry）。
- 完成 Phase 82-100（Persona Swarm Framework、外部來源治理、自訂角色議會、Architecture Convergence v2）。
- 後端持久化驗收在 2026-02-14 已恢復並通過：
  - `python scripts/verify_backend_persistence.py --base https://tonesoul52.onrender.com --timeout 40`

## 驗證摘要

- 測試：`python -m pytest tests/ -q` => `849 passed, 2 warnings`
- Red-team：`python -m pytest tests/red_team -q` => `26 passed`
- Web：`npm --prefix apps/web run lint` + `npm --prefix apps/web run test` => pass
- 覆蓋率：`python -m pytest tests -q --cov=tonesoul ...` => total `43%`

## 主要產物

- Release staging 清單：`docs/plans/release_readiness_staging.md`
- 測試覆蓋率：
  - `reports/coverage_latest.json`
  - `reports/coverage_latest.xml`
  - `reports/test_coverage_latest.md`
- 安全報告：`reports/security_vulnerability_assessment_latest.md`
- 系統導覽：`docs/system_walkthrough.md`

## 已知待辦

- 無（發版主要門檻已完成）
