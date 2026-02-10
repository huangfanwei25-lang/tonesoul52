# Task

## Phase 47: 收斂衝刺（P0 / P1 / P2）

### P0（先做，阻塞交付）
- [x] 清除 lint/format drift（ruff + black --check 全綠）
- [x] scripts/run_repo_healthcheck.py --allow-missing-discussion 回到 overall_ok=true
- [x] root npm test 可執行（對齊 python -m pytest tests/ -q）
- [x] live SDH 端到端可重現（scripts/run_7d_isolated.py + --include-sdh pass）
- [x] 新增 ConnectionResetError 啟動抖動回歸測試（tests/test_run_7d_isolated.py）
**成功標準**: 阻塞性品質門檻恢復可重現全綠，且 SDH live smoke 有可重演證據。

### P1（本週收斂，降低維護風險）
- [x] 決議 commit attribution 策略（僅檢查 HEAD / 檢查 N 筆歷史 / 僅 PR 增量）
- [x] 將 attribution 決策落地到 CI（warning 或 blocking 一致化）
- [x] apps/showcase/ 追蹤策略先收斂（暫採 .gitignore，避免工作樹噪音）
**成功標準**: 歸屬規範有單一可執行策略，CI 行為與團隊預期一致。

### P2（可延後，保持倉庫乾淨）
- [ ] 規劃 Git object hygiene 定期策略（count-objects / fsck 例行檢查）
- [ ] 將收斂週規則寫入維運文件（避免再次框架擴張造成 drift）
**成功標準**: 有文件化的例行保養節奏，且不增加日常交付負擔。

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

## Phase 34: 多代理提交歸屬規範
- [x] 新增 `scripts/verify_commit_attribution.py`（檢查 `Agent` / `Trace-Topic` trailers）
- [x] 新增 `tests/test_verify_commit_attribution.py`
- [x] 更新 `CONTRIBUTING.md` 提交歸屬格式與驗證指令
**成功標準**: 共享作者身份下，commit message 能附帶代理與議題來源，降低跨代理責任歸屬歧義。 

## Phase 35: CI 可見性整合（Commit Attribution）
- [x] `ToneSoul CI` 新增 `commit_attribution` job
- [x] 每次 push 自動輸出 HEAD attribution 解析結果
- [x] 缺失 trailers 先以 warning 呈現（不阻斷 CI）
**成功標準**: 歸屬資訊可在 CI 日誌直接追蹤，且不影響現有交付節奏。 

## Phase 36: Vercel 輸出異常修補（Chat Route）
- [x] 重現線上異常（`tonesoul52.vercel.app/api/chat` 回 `backend_mode=mock_fallback`）
- [x] `apps/web/src/app/api/chat/route.ts` 改為預設禁用 transport mock fallback（需顯式 `TONESOUL_ENABLE_CHAT_MOCK_FALLBACK=1`）
- [x] 新增 Vercel 防呆：若 `TONESOUL_BACKEND_URL` 缺失或指向 localhost，直接回 `503` 配置錯誤
- [x] 新增測試 `apps/web/src/__tests__/apiRoutes.chatTransport.test.ts`（disabled fallback / explicit fallback / vercel misconfig）
- [x] 更新 `docs/API_SPEC.md` 與 `docs/VERCEL_DEPLOY.md` 的 fallback 契約與部署變數
**成功標準**: production 不再因後端失聯而靜默回 mock 內容，Vercel 配置錯誤可即時暴露，且 web build+tests 全通過。

## Phase 37: 全倉庫健康檢查與多觀點整合
- [x] 修復 `scripts/` 既存 lint/format 債務（`analyze_journal.py`, `build_semantic_index.py` + black 格式化）
- [x] 全域品質檢查（`ruff/black/pytest/web lint+test`）重跑並確認全綠
- [x] 重跑 `verify_7d --include-sdh` 並補跑 live-service `verify_web_api` 驗證 SDH 路徑
- [x] 更新 `REPO_CONSOLIDATION.md`（工程/哲學/現實/AI 多角度審計 + 高 CP 路線）
**成功標準**: 腳本層品質債務清空、7D 阻斷維度維持 0 失敗，且整合審計文件反映最新可重演結果。

## Phase 38: 一鍵健康檢查與 CI 可見性
- [x] 新增 `scripts/run_repo_healthcheck.py`（整合 ruff/black/pytest/web lint+test/verify_7d）
- [x] 輸出 `docs/status/repo_healthcheck_latest.json` + `docs/status/repo_healthcheck_latest.md`
- [x] 新增 `tests/test_run_repo_healthcheck.py`（命令構建、skip 條件、Markdown 輸出）
- [x] 新增 `.github/workflows/repo_healthcheck.yml`（blocking + artifact upload）
- [x] 更新 `docs/status/README.md` 的產物說明與執行方式
**成功標準**: 本地可一鍵取得健康檢查快照，CI 可上傳可讀/可機器解析 artifact，且缺 discussion 檔時可用 `--allow-missing-discussion` 走 CI-friendly 路徑。 

## Phase 39: Vercel Preflight Guard
- [x] 新增 `scripts/verify_vercel_preflight.py`（backend URL、fallback policy、可選 health probe）
- [x] 新增 `tests/test_verify_vercel_preflight.py`（URL/fallback/health probe 判斷）
- [x] 新增 `.github/workflows/vercel_preflight.yml`（`workflow_dispatch` 手動 preflight）
- [x] 更新 `docs/VERCEL_DEPLOY.md` 與 `docs/API_SPEC.md` 的 preflight 指令
**成功標準**: 部署前可用單一指令阻擋高風險配置（localhost backend、mock fallback 開啟、report provider fallback 未關閉），並可在需要時加做 `/api/health` 連通檢查。 

## Phase 40: Multi-Model Council Runtime Wiring
- [x] `CouncilRuntime` 在未顯式傳入視角配置時接入 `get_council_config()`
- [x] 新增 `TONESOUL_COUNCIL_MODE` 環境變數（支援 `rules | hybrid | full_llm`，預設 `hybrid`）
- [x] `model_registry` 支援 `rules` 別名並保持 `rules_only` 相容
- [x] 新增 runtime/model registry 測試覆蓋（預設、alias、invalid fallback、request override）
**成功標準**: 後端可透過環境變數切換 council 模式，且顯式 request 設定優先級高於環境變數，行為有測試保護。 

## Phase 41: 討論通道文字完整性防呆
- [x] `memory/agent_discussion.py` 新增文字異常偵測（`replacement_char` / `private_use_char`）
- [x] curated stream 過濾異常訊息，保留 raw 歷史但避免污染共用閱讀流
- [x] `scripts/verify_memory_hygiene.py` 新增 `text_anomalies` 檢查並納入 blocking gate
- [x] 補齊回歸測試（`tests/test_agent_discussion.py`, `tests/test_verify_memory_hygiene.py`）
**成功標準**: 討論檔可維持 JSON 結構 + 文字可讀性雙重契約，且新的亂碼訊息不會進入 curated 記憶流。 

## Phase 42: Council 模式前端可切換
- [x] `/api/chat` 支援 `council_mode` 與 `perspective_config`（含輸入驗證）
- [x] `UnifiedPipeline.process(...)` 串接 council mode override 到 `CouncilRequest.perspective_config`
- [x] ChatInterface 新增 backend chat 的 council mode 下拉選單並帶入請求
- [x] 補齊 API 合約與紅隊型別混淆測試，更新 `docs/API_SPEC.md`
**成功標準**: 使用者可在前端切換 `rules/hybrid/full_llm` 並透過 `/api/chat` 生效，且不合法輸入會被 API 明確阻擋。 

## Phase 43: Web Chat Route 契約防呆
- [x] `apps/web/src/app/api/chat/route.ts` 新增 `council_mode` / `perspective_config` 型別驗證與 alias 正規化
- [x] 清理 route 中既有亂碼判斷字串，統一為可維護的問題/情緒判定
- [x] 補齊 route 測試（invalid payload 阻擋 + `rules_only -> rules` 轉換）
**成功標準**: Next route 在進入 backend 前可攔截無效 payload，且 council mode 轉換行為有測試鎖定。 

## Phase 44: Council Mode 持久化與 E2E Smoke
- [x] ChatInterface `council_mode` 選擇持久化（localStorage）
- [x] CouncilRuntime transcript 新增 `council_mode_observability`
- [x] `scripts/verify_web_api.py` 新增 `--check-council-modes`（驗證 mode 切換生效）
- [x] 補齊測試（runtime / verify_web_api helpers）
**成功標準**: 重整頁面後保留使用者 council mode，且可用單一 smoke 指令驗證 web->backend mode 切換與觀測欄位。 

## Phase 45: SDH 自動化升級（Mode Switch Gate）
- [x] `scripts/verify_7d.py` 的 SDH 檢查預設加入 `--check-council-modes`
- [x] CI `web_api_smoke` 改為強制驗證 council mode 切換
- [x] 補齊 `tests/test_verify_7d.py`，鎖定 SDH 命令旗標
- [x] 更新 7D / API 文件中的 smoke 指令
**成功標準**: `include-sdh` 與 CI smoke 都會驗證 mode switch，不再只驗證基本連通。 

## Phase 46: Healthcheck 與 SDH 旗標對齊
- [x] `run_repo_healthcheck.py` 新增 `--[no-]check-council-modes` 並傳遞到 `verify_7d`
- [x] `verify_7d.py` 新增 `--[no-]check-council-modes`（預設啟用）
- [x] 補齊 `tests/test_run_repo_healthcheck.py` / `tests/test_verify_7d.py` 旗標測試
- [x] 更新 `docs/status/README.md` 的 live SDH 執行範例
**成功標準**: healthcheck 可顯式開關 mode-switch smoke，且預設行為維持啟用並有測試保護。 

## 已完成（摘要）
- [x] Phase 1-2: Council 設計與整合
- [x] Phase 3/10/16: Tools API schema + ToolResponse 標準化
- [x] Phase 4/6/8/15: Memory wiring / SQLite / Observer
- [x] Phase 11-13: Demo API Server + Playground + run_demo
- [x] Phase 14: Genesis Intent + is_mine
- [x] 敘事對照表與敘事定版文件
- [x] 亂碼清理與 UTF-8 統一
**參考**: `CODEX_TASK.md`, `memory/handoff/2026-02-06_phase16_tools_progress.md`



