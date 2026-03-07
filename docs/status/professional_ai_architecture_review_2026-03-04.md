# Professional AI Architecture Review (2026-03-04)

## Reading Notes
- document_type: historical architecture review
- review_date: 2026-03-04
- intent: capture a point-in-time professional assessment of architecture readiness
- not_for_use_as: current dirty-workspace health verdict
- PowerShell note: read with `Get-Content -Raw -Encoding UTF8` to avoid mojibake

## Provenance
- primary_basis:
  - code references captured in this file
  - local verification commands run on 2026-03-04
- later changes may invalidate the operational details while leaving the architectural judgment historically useful

## Scope
- 評估對象：ToneSoul Phase II 近期交付（Resistance + V2 模組 + 壓測資料 + 子模組處理）。
- 評估標準：以「專業 AI 架構師」視角，重點看可維運性、可驗證性、上線風險，而不只任務打勾率。
- 評估時間：2026-03-04（本次審查）。

## Executive Verdict
- 任務完成度（Delivery）：`高`（已完成大部分承諾項，且有 commit 與測試證據）。
- 架構成熟度（Architecture Readiness）：`中上`（核心能力已落地，但 V2 有「模組完成 > 主流程接線」落差）。
- 生產就緒度（Production Readiness）：`中`（仍有 mock 路徑與 repo hygiene 風險需要收斂）。

## Evidence Snapshot
- Resistance 核心模組已存在：`FrictionCalculator` / `PainEngine` / `CircuitBreaker` / `PerturbationRecovery`  
  - `tonesoul/resistance.py:71`
  - `tonesoul/resistance.py:223`
  - `tonesoul/resistance.py:417`
  - `tonesoul/resistance.py:587`
- `TensionEngine` 目前已接入 `PainEngine.evaluate_throttle`  
  - `tonesoul/tension_engine.py:24`
  - `tonesoul/tension_engine.py:193`
  - `tonesoul/tension_engine.py:285`
- Hippocampus V2 的 `B_vec` 與 `recall_corrective` 已實作  
  - `tonesoul/memory/hippocampus.py:185`
  - `tonesoul/memory/hippocampus.py:214`
  - `tonesoul/memory/hippocampus.py:247`
- 本次實測：`python -m pytest -q` -> `1197 passed, 0 failed`（2026-03-04 審查執行）。
- same-origin 模式仍回 `governance_capability: "mock_only"`  
  - `apps/web/src/app/api/governance-status/route.ts:76`
  - `apps/web/src/app/api/governance-status/route.ts:80`
- submodule 狀態為 deinit（未初始化）但仍保留在 repo  
  - `docs/status/submodule_integrity_latest.md:17`

## Professional Gap Assessment

### Gap A: V2 模組接線不完整（P0）
- 現況：V2 模組多為「存在 + 單元測試」，但主流程主要僅接 `PainEngine`。
- 風險：架構文件會顯示已完成，但 runtime 行為與設計目標（預防凍結、擾動恢復、方向記憶召回）可能不一致。
- 影響：遇到高壓/發散場景時，無法保證預期保護策略一定生效。

### Gap B: same-origin 的治理能力仍是 mock（P1）
- 現況：API 在 same-origin 情境直接回報 `mock_only`。
- 風險：前端可能顯示「可用」但不代表 runtime governance fully enforced。
- 影響：部署環境切換（local/preview/prod）時，能力一致性不足。

### Gap C: Submodule 清理尚未收口（P1）
- 現況：邏輯上已 deinit，但 `OpenClaw-Memory` 與 `tae_fix` 仍在子模組拓撲。
- 風險：新環境 checkout/rebuild 可能出現不一致；維運者難判斷 canonical source of truth。
- 影響：發版可重現性與故障排查效率下降。

### Gap D: Release Hygiene 未封板（P2）
- 現況：分支仍有未收斂變更與未追蹤檔。
- 風險：回溯與審計成本上升；容易把暫存資料帶進後續交付。
- 影響：PR/Release 品質門檻不穩定。

## Next Steps (Recommended Plan)

### Step 1 (P0): 完成 V2 Runtime 接線閉環
- 目標：讓 `CircuitBreaker`、`PerturbationRecovery`、`recall_corrective` 真正進入主推理路徑（不只存在於模組/測試）。
- DoD：
- 在主流程可追蹤到觸發條件、決策輸出、失敗策略（freeze/recover/rollback）。
- 新增 integration tests 覆蓋「高摩擦 + 高 Lyapunov + 擾動恢復 + 記憶召回」連續場景。
- 在 API 回傳中可見結構化欄位（例如 break_reason、recovery_path、memory_correction_hit）。

### Step 2 (P1): 收斂治理能力語義（mock vs runtime）
- 目標：統一 `governance_capability` 在 local/preview/prod 的判定規則。
- DoD：
- same-origin 不再無條件回 `mock_only`；改成可驗證的 runtime probe 或明確 feature flag。
- 對 `mock_only` 與 `runtime_ready` 建立 CI contract tests，避免回歸。

### Step 3 (P1): 完成 Submodule 決策
- 目標：二選一落地，避免長期灰色狀態。
- 路徑 A：正式保留 submodule，補齊初始化與版本治理流程。
- 路徑 B：改 vendored/monorepo，移除 `.gitmodules` 與對應 gitlink。
- DoD：
- `submodule_integrity_latest.md` 無「not initialized」警告。
- README/運維文件明確寫出單一真實來源（single source of truth）。

### Step 4 (P2): Release Gate 固化
- 目標：把目前人工驗證流程變成不可跳過的自動門檻。
- DoD：
- CI 至少包含：`python -m pytest -q`、`python -m black --check ...`、`python scripts/verify_submodule_integrity.py --strict`。
- 發版前必過架構驗收清單（runtime 接線、治理模式、依賴拓撲、可重現性）。

## Suggested Immediate Priority (this week)
- 先做 Step 1（Runtime 接線）與 Step 2（治理語義），因為它們直接影響「是否真的在運行你設計的治理架構」。
- Step 3、Step 4 隨後接續，作為交付收口與長期穩定化。

## Final Professional Judgment
- 這批工作不是「只做表面」，核心工程確實完成了不少。
- 但以專業架構標準來看，目前屬於「功能完成、治理主幹尚待收口」的階段。
- 一旦把 runtime 接線與治理語義補齊，整體就會從「完成任務」升級為「可穩定上線的架構」。

## 2026-03-04 Step 2 Execution Update (Codex)
- Status: completed
- Scope completed:
  - Added runtime mode normalization across `chat`, `conversation`, `consent`, and `session-report` API routes.
  - Added explicit `backend_mode` and `deliberation_level: "unavailable"` to non-fallback transport/invalid-JSON error responses (HTTP 502/504 paths).
  - Kept mock paths explicit with `backend_mode: "mock_fallback"` and `deliberation_level: "mock"`.
  - Kept successful backend-forwarded paths explicit with `backend_mode` backfill and `deliberation_level: "runtime"` when backend payload omits them.
- Verification:
  - `npm --prefix apps/web run test -- src/__tests__/apiRoutes.chatTransport.test.ts src/__tests__/apiRoutes.transportFallback.test.ts src/__tests__/apiRoutes.invalidJson.test.ts src/__tests__/apiRoutes.governanceStatus.test.ts src/__tests__/apiRoutes.backendHealth.test.ts`
    - Result: 5/5 files passed, 47/47 tests passed.
  - `python -m pytest -q tests/test_verify_web_api.py`
    - Result: 11/11 tests passed.

## Next Step (Recommended)
1. Complete Step 1 runtime governance wiring end-to-end:
   - Emit freeze/recover/rollback observability fields from runtime path.
   - Add integration tests that prove governance decisions are enforced in runtime, not only in static checks.
2. Add API contract tests for error-shape consistency:
   - Require `backend_mode` + `deliberation_level` in all route responses (success, fallback, and failure).
3. Add release gate:
   - CI checks for route contract tests + smoke command `python scripts/verify_web_api.py --same-origin --elisa-scenario`.
