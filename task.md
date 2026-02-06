# Task

## Phase 17: 收尾三部曲
- [x] README 更新（反映 Council / Genesis / Memory / Tools API + 快速啟動）
- [x] 記憶總結（寫入 `memory/self_journal.jsonl`，含 Phase 14-16 與亂碼修復）
- [x] 誠實機制設計（Phase 18 預告，草案：docs/HONESTY_MECHANISM.md）
**成功標準**: README 完整更新、self_journal 有新紀錄、誠實機制有可討論的設計草案。

## Phase 18: 誠實機制設計（草案）
- [x] 在 verdict 設計加入 `uncertainty_level`
- [x] 定義「我不知道」的正式輸出格式
- [x] 提出測試/驗證方向（不需立即實作）
**成功標準**: 產出一份可評審的設計草案（文件或規格），可進入下一輪討論。

## Phase 19: 誠實機制實作
- [x] `CouncilVerdict` 新增不確定性欄位
- [x] `verdict` 結構化輸出加入不確定性
- [x] `CouncilRuntime` 依 `responsibility_tier` 調整不確定性
- [x] 測試覆蓋基礎不確定性計算
**成功標準**: 產出可運行的不確定性欄位與結構化輸出，並有基礎測試。

## Phase 21: API 統一與 Runtime Drift 修正
- [x] Flask 補齊 conversation/consent 契約並與 web 對齊
- [x] Next API routes 改為 backend-first，fallback 僅限 transport failure
- [x] 路由每次請求動態解析 `TONESOUL_BACKEND_URL`
- [x] `verify_web_api.py` + CI `web_api_smoke` 完成整鏈 smoke（含 `--require-backend`）
- [x] 審計文件更新（`reports/api_unification_audit_2026-02-06.md`、`reports/facade_runtime_audit_2026-02-06.md`）
**成功標準**: web/backend 契約可重現驗證，且 fallback 不再遮蔽 backend 異常。

## 已完成（摘要）
- [x] Phase 1-2: Council 設計與整合
- [x] Phase 3/10/16: Tools API schema + ToolResponse 標準化
- [x] Phase 4/6/8/15: Memory wiring / SQLite / Observer
- [x] Phase 11-13: Demo API Server + Playground + run_demo
- [x] Phase 14: Genesis Intent + is_mine
- [x] 敘事對照表與敘事定版文件
- [x] 亂碼清理與 UTF-8 統一
**參考**: `CODEX_TASK.md`, `memory/handoff/2026-02-06_phase16_tools_progress.md`
