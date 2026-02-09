# REPO Consolidation Audit

Date: 2026-02-09
Scope: 全倉庫工程健康檢查 + 多觀點（工程/哲學/現實/AI）審計

## 鏈主哲學（對齊）

> 把結晶當手腳，不要活在結晶裡面。

本報告把「文件」視為可操作的工具，而不是取代執行真相的主體。

## Executive Verdict

- 架構方向正確，適合「漸進優化」而非整包重寫。
- 核心能力（Council / API 合約 / 7D gate / Web route 契約）已可穩定運作。
- 當前主要風險不是缺功能，而是「一致性治理」：腳本品質、記憶通道衛生、文件與可執行真相同步。

## 今日實測快照（2026-02-09）

1. `python -m ruff check tonesoul tests scripts`：PASS
2. `python -m black --check tonesoul tests scripts`：PASS
3. `python -m pytest tests/test_verify_docs_consistency.py tests/test_run_monthly_consolidation.py -q`：PASS
4. `python -m pytest tests/test_verify_openclaw_probe.py tests/test_verify_7d.py tests/test_run_7d_isolated.py -q`：PASS
5. `python -m pytest tests/test_perspective_factory.py tests/test_model_registry.py -q`：PASS
6. `npm --prefix apps/web run lint`：PASS
7. `npm --prefix apps/web run test`：PASS（32 tests）
8. `python scripts/verify_7d.py --include-sdh`：`blocking_failures=0, soft_failures=1`（SDH 在未啟動服務時 soft-fail，符合目前 gate 設計）
9. 啟動 backend+web 後執行 `python scripts/verify_web_api.py --require-backend`：PASS（conversation/consent/chat/session-report 全通）

## 多觀點審計

### 1) 工程角度

優勢：
- 測試面與治理面已形成可執行關卡（非純文件宣告）。
- API 契約在 web/backend 間有實測鏈路，並且可重演。
- LLM fallback 防呆已加強（無 key 不初始化；lazy import）。

風險：
- `scripts/` 歷史檔案曾有 lint/format 債務，容易在 CI 或跨代理整合時回彈。
- SDH 依賴 live service，若只看單次 7D 輸出容易誤判為「系統失敗」。

結論：
- 工程基座可用，重點是持續把「可執行事實」壓過「口頭狀態」。

### 2) 哲學角度

觀察：
- 專案已具備誠實與責任敘事，不是只有功能導向。
- 真正風險在於「語魂被報告取代」：當報告與可執行結果不一致，價值觀會失去約束力。

建議：
- 文件只做解釋層，最終判準由可重演命令與測試提供。
- 把「我不知道/不確定」維持為一級輸出，不要被 fallback 文案掩蓋。

### 3) 現實角度

觀察：
- 多代理協作是有效的，但共用討論通道要靠格式紀律才能可持續。
- Windows 編碼環境（例如 cp950 顯示）仍會製造「看起來像亂碼」的假象，容易誤判成檔案損壞。

建議：
- 一律以 UTF-8 寫檔，顯示層問題與檔案內容問題分開判斷。
- 對所有跨代理交接，優先採 JSONL 結構化紀錄與欄位約束。

### 4) AI 角度

觀察：
- 你的倉庫不需要「全程都用最高階模型」。
- 真正需要高階模型（如 GPT-5.3 級）的是：跨層歸因、回歸調查、架構審計、最終合併把關。

建議（模型分工）：
- 日常實作與例行修補：中階模型即可。
- 遇到第 1 次棘手 bug 或 CI 反覆不穩：升級高階模型介入 root-cause。
- 發版前審計與設計決策：高階模型做最終一致性檢查。

## 過度結晶風險（Over-Crystallization）

1. 報告漂移：文件說綠燈，但可執行 gate 沒過。
2. 指標崇拜：追分數而忽略真正行為安全。
3. 記憶污染：未結構化訊息塞進治理通道，降低可解析性。
4. 邊界鬆動：臨時修補跨層依賴，長期增加維護成本。

## 高 CP 值整合路線（建議）

### P0（高優先，低到中成本）

1. 把 `scripts/` lint/format 納入固定檢查（已修復，建議持續守門）。
2. 7D 報告中明確區分「blocking fail」與「live-service soft fail」。
3. 每次關鍵修補後固定 append 一筆 `memory/agent_discussion.jsonl`（已執行，持續化）。

### P1（中優先，中成本）

1. 補一個「一鍵健康檢查」入口，串 `ruff/black/pytest/web/7d` 的最小路徑。
2. 對 Vercel 生產環境加一個啟動期自檢（backend URL 與 fallback policy）。

### P2（策略優化，中到高成本）

1. 將研究/討論文件分層（proposal, ratified, archived），降低知識漂移。
2. 逐步把多代理協作規範轉為可驗證規則（而不只文字約定）。

## Closing

- 結論：繼續優化語魂系統，方向正確。
- 方法：維持小步、可測、可追溯；讓分歧可見，但讓結論可執行。
- 原則：當文件與執行結果衝突時，以可重演結果為準，文件立即回寫。
