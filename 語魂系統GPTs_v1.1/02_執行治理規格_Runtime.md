# 語魂執行治理規格（Runtime, v1.1）

日期：2026-02-11  
狀態：`authoritative`（執行期行為規格）  
依賴：`01_術語與門檻單一規格.md`

## 0. 範圍聲明

本文件只定義「系統執行期」行為，不含社群投票、人員權限、版本治理流程。

## 1. Runtime 組件分層（現行可追溯）

1. Web 入口層（API transport）
- `apps/web/src/app/api/chat/route.ts`
- `apps/web/src/app/api/conversation/route.ts`
- `apps/web/src/app/api/consent/route.ts`
- `apps/web/src/app/api/session-report/route.ts`
- `apps/web/src/app/api/backend-health/route.ts`
- `apps/web/src/app/api/_shared/backendConfig.ts`

2. Web fallback 判斷層
- `apps/web/src/lib/chatFallback.ts`
- `apps/web/src/components/ChatInterface.tsx`

3. Council 審議層
- `tonesoul/council/pre_output_council.py`
- `tonesoul/council/verdict.py`
- `tonesoul/council/types.py`

4. Gate/風險判定層
- `tonesoul/yss_gates.py`
- `tonesoul/yss_pipeline.py`
- `tonesoul/poav.py`
- `tonesoul/semantic_control.py`

5. 審計格式與樣例
- `law/step_ledger_schema.json`
- `docs/engineering/EXAMPLES/step_ledger_example.md`
- `scripts/verify_web_api.py`（整合驗證腳本）

## 2. 最小執行閉環

1. INPUT  
接收輸入與上下文（web route 或 pipeline context）。

2. SENSE  
計算或估計 `ΔT/ΔS/ΔΣ/ΔR`，並產生風險訊號。

3. DELIBERATE  
多視角審議（Guardian/Analyst/Critic/Advocate 或 Muse/Logos/Aegis 映射）。

4. GATE  
依 `P0/P1/P2 + POAV` 作 `PASS/REWRITE/BLOCK` 判定。

5. OUTPUT  
`PASS` 放行；`REWRITE` 重寫再審；`BLOCK` 拒絕並提供替代路徑。

6. TRACE  
輸出審計資料（至少可回放決策理由、門檻、時間戳）。

## 3. Fallback 與可觀測性規格

## 3.1 Backend URL 驗證（Vercel）

- 由 `apps/web/src/app/api/_shared/backendConfig.ts` 驗證：
  - 必須有 `TONESOUL_BACKEND_URL`
  - 不可 local host
  - 協定必須 `https`

若不合法：回傳 `503` 並附 `config_issue`（不可偽裝成功）。

## 3.2 Transport fallback（web route）

`/api/chat`、`/api/conversation`、`/api/consent`、`/api/session-report`：

1. 後端連線失敗時：
- 若對應 `TONESOUL_ENABLE_*_MOCK_FALLBACK=1`，回 `mock_fallback`
- 否則回可觀測錯誤（`backend unavailable`）

2. backend_mode 必須可見：
- `backend` 或 `mock_fallback`
- fallback 時需附 `fallback_reason`

## 3.3 Degraded backend fallback（前端側）

- `apps/web/src/lib/chatFallback.ts` 的 `isBackendDegradedResponse()` 會辨識例如「LLM 服務不可用」。
- `apps/web/src/components/ChatInterface.tsx` 在允許條件下可切 `legacy_provider`，並標示 active mode。

## 4. Gate 規格與當前實作對齊

## 4.1 P0 gate

- `tonesoul/yss_gates.py::p0_gate()`  
- 目標：若命中 P0 約束，決策不可放行。

## 4.2 POAV gate

- `tonesoul/yss_gates.py::poav_gate()` + `tonesoul/poav.py`
- 說明：
  - `enforce=false` 時，低分可能是 `record_only`
  - `enforce=true` 時，低於門檻可直接 `block`
- 因此：REWRITE/PASS/BLOCK 的最終行為需由上層流程整合判定，不可只看單一函式。

## 4.3 DCS/升級判定

- `tonesoul/yss_gates.py::dcs_gate()`
- `tonesoul/yss_gates.py::escalation_gate()`

## 5. 審計與留痕（Runtime 必備）

每次高風險判定至少保留：

1. `timestamp`
2. `input_hash`
3. `delta_t / delta_s / delta_sigma / delta_r`
4. `p_level_triggered`
5. `poav_score`
6. `gate_decision`
7. `final_action`
8. `rationale_summary`

註：本 repo 目前為「schema + gate report + transcript」混合形態；未採 legacy 的單一 body step_ledger 模組路徑。

## 6. 執行期測試要求（最小集）

1. Web API 整合 smoke
- `scripts/verify_web_api.py`

2. Council 行為
- `tests/test_pre_output_council.py`
- `tests/test_pre_output_council_integration.py`
- `tests/test_verdict.py`

3. Gateway/Gate 相關
- `tests/test_gateway_integration.py`
- `tests/test_verify_web_api.py`

4. Fallback
- `apps/web/src/__tests__/chatFallback.test.ts`
- `apps/web/src/__tests__/apiRoutes.transportFallback.test.ts`

## 7. 禁止事項（Runtime）

1. 禁止回傳不可觀測錯誤（只說失敗，不說原因）。
2. 禁止 fallback 時偽裝為 backend 正常成功。
3. 禁止在文件中引用不存在的 runtime 路徑。
4. 禁止混用 `ΔS` 與 `ΔΣ` 的語義。
