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

## Phase 22: 前端整合（進行中）
- [x] 新增 `docs/API_SPEC.md`（統一後 API 規格）
- [x] 驗證 `apps/web` dev 連線 `localhost:5000`（整鏈 smoke）
- [x] 驗證 ChatInterface -> backend -> Council 流程（`/api/chat` 整鏈 smoke）
- [x] 驗證 SessionReport -> backend 流程（`/api/session-report` 整鏈 smoke）
- [x] 更新 Vercel 環境變數與部署說明（`docs/VERCEL_DEPLOY.md`，待平台套用）
**成功標準**: Navigator 前端在本地走統一 API 契約，且部署設定文件可直接套用到 Vercel。

## Phase 24: 7D 落地（提案）
- [x] 重寫 `docs/7D_AUDIT_FRAMEWORK.md`（UTF-8 可讀版本）
- [x] 新增 `docs/7D_EXECUTION_SPEC.md`（7D -> checklist -> gate）
- [x] 新增 `scripts/verify_7d.py`（7D 聚合入口）
- [x] 建立 `tests/red_team/` 最小對抗測試集（RDD）
- [x] 決議 `SDH` 先維持 soft-fail（非 blocking）
- [x] 設定 `DDD` 資料新鮮度 SLA（7 天 stale 規則）
- [x] 設計 `systemic betrayal user confirmation gate`（高破壞性風險需二次確認）
- [x] 將 RDD 擴充至 10+ 對抗案例（目前 20）
**成功標準**: 七維皆有可執行檢查，且 gate 策略在 CI 層可明確解釋。

## Phase 25: 月度整合自動化與文件契約強化
- [x] 新增 `.github/workflows/monthly_consolidation.yml`（每月排程 + 手動觸發）
- [x] `scripts/verify_docs_consistency.py` 納入月度 workflow 契約檢查
- [x] 修正 docs threshold 正則抽取（移除亂碼 pattern，採穩定 `tests/cases` 解析）
- [x] 更新 `tests/test_verify_docs_consistency.py` 覆蓋月度 workflow 存在/缺失情境
- [x] 更新 `docs/status/README.md` 說明自動化來源與 artifact 產出
**成功標準**: `verify_docs_consistency` 與 `run_monthly_consolidation --strict` 可穩定通過，且 status 來源具備自動化排程。

## Phase 26: 月度整合 CI 可重現性修補
- [x] `scripts/run_monthly_consolidation.py` 新增 `--allow-missing-discussion` 參數（CI 乾淨環境可重現）
- [x] 月度 workflow 執行改為 `--strict --allow-missing-discussion`
- [x] `scripts/verify_docs_consistency.py` 新增檢查月度 workflow 是否帶 `--allow-missing-discussion`
- [x] 新增 `tests/test_run_monthly_consolidation.py`，鎖定 memory hygiene 命令旗標行為
- [x] 擴充 `tests/test_verify_docs_consistency.py`，覆蓋缺失旗標時的阻擋情境
- [x] 更新 `docs/status/README.md` 加入 CI-friendly 執行範例
**成功標準**: 月度 workflow 在無 `memory/agent_discussion*.jsonl` 的乾淨 checkout 仍可通過契約檢查與整合檢查。

## Phase 27: Escape Valve V1（安全版）
- [x] 新增 `tonesoul/escape_valve.py`（電路斷路器 + 不確定性輸出）
- [x] `CouncilRuntime` 整合 Escape Valve，保持 `BLOCK` 語義不變
- [x] 移除 runtime 可變狀態污染（每次 deliberation 使用 request-local valve）
- [x] 支援 `context.escape_valve_failures` 作為重試歷史種子（上限保護）
- [x] 觸發時提高不確定性到 high 並追加 `escape_valve_triggered=*` 理由
- [x] 新增 `tests/test_escape_valve.py` 與 `tests/test_escape_valve_runtime.py`
**成功標準**: Escape Valve 可被測試觸發且不繞過 BLOCK，無跨請求狀態污染，既有審計測試保持通過。

## Phase 28: Escape Valve API 契約化
- [x] 更新 `docs/API_SPEC.md`，明確 `POST /api/validate` 的 Escape Valve 輸入/輸出契約
- [x] 擴充 `tests/test_api_server_contract.py`（validate 基本契約 + seeded trigger + 跨請求不外洩）
**成功標準**: API 層可重現 Escape Valve 行為，且契約文件與測試一致。

## Phase 29: Escape Valve 防濫用與觀測強化
- [x] 新增 seed trust 機制（`escape_valve_seed_trusted`）與 untrusted seed 忽略策略
- [x] API 新增 `TONESOUL_ALLOW_ESCAPE_SEED` 開關（預設拒絕外部 seed）
- [x] API 對 trusted seed 加入輸入上限（最新 50）+ runtime 使用上限（最新 20）
- [x] transcript 新增 `escape_valve_observability` 指標
- [x] 新增 red-team 測試：untrusted seed 無法強制觸發、trusted seed 上限生效
**成功標準**: 預設外部輸入無法強制 Escape Valve，且觸發/忽略路徑有可觀測指標與對抗測試覆蓋。

## Phase 30: 狀態報告穩定化（命令顯示）
- [x] `scripts/verify_7d.py` 命令輸出改為穩定顯示（`python ...`，避免環境路徑亂碼）
- [x] `scripts/run_monthly_consolidation.py` 命令輸出改為穩定顯示（`python ...`）
- [x] 補齊命令顯示正規化單元測試
- [x] 重新生成 `docs/status/*.json` 並驗證可讀性
**成功標準**: 月度報告中的 `command` 與 7D 結果命令欄位在跨環境（含非 ASCII 路徑）仍維持可讀、可比對。 

## Phase 31: SDH 編碼穩定性修復（ToneBridge）
- [x] 修復 `tonesoul/tonebridge/commitment_extractor.py` 在缺少 `jieba` 時的 cp950 編碼崩潰
- [x] 新增 cp950 import 回歸測試，避免再次因 import-time 輸出造成 `UnicodeEncodeError`
- [x] 驗證 `scripts/run_7d_isolated.py`（含 SDH）回歸全綠
**成功標準**: 在無 `jieba` 的環境下不再因編碼錯誤導致 `/api/session-report` 500，且 7D 隔離整鏈（含 SDH）可重現全綠。

## Phase 32: VTP 最小整合（Council Runtime）
- [x] 新增 `tonesoul/council/vtp.py`（status: continue/defer/terminate + confession payload）
- [x] `CouncilRuntime` 整合 VTP 評估，保留 `BLOCK` 語義並新增 `transcript.vtp`
- [x] 新增 VTP 單元與 runtime 測試（`tests/test_vtp.py`, `tests/test_vtp_runtime.py`）
- [x] 擴充 API 合約測試與文件（`tests/test_api_server_contract.py`, `docs/API_SPEC.md`）
**成功標準**: VTP 觸發/延遲/終止三種狀態可由測試重現，並在 API 回應中可觀測。 

## Phase 33: VTP 紅隊防濫用驗證
- [x] 新增 `tests/red_team/test_vtp_context_abuse.py`
- [x] 驗證未信任 API payload 無法強制 VTP defer/terminate
- [x] 驗證偽造完整終止 payload 仍被 trust gate 忽略
**成功標準**: 外部未授權請求無法用 VTP flags 強制進入終止流程，且行為有測試覆蓋。 

## 已完成（摘要）
- [x] Phase 1-2: Council 設計與整合
- [x] Phase 3/10/16: Tools API schema + ToolResponse 標準化
- [x] Phase 4/6/8/15: Memory wiring / SQLite / Observer
- [x] Phase 11-13: Demo API Server + Playground + run_demo
- [x] Phase 14: Genesis Intent + is_mine
- [x] 敘事對照表與敘事定版文件
- [x] 亂碼清理與 UTF-8 統一
**參考**: `CODEX_TASK.md`, `memory/handoff/2026-02-06_phase16_tools_progress.md`
