# GPT-5.3 架構分析報告

## 架構層次

1. **前端層**：Next.js (apps/web) + 多個 API route，透過 backend URL/same-origin 模式轉發。參考 apps/web/src/app/api/_shared/backendConfig.ts:46。
2. **後端層 A**：Flask API（apps/api/server.py）承擔 chat/consent/memory/evolution 等主要服務。
3. **後端層 B**：Vercel serverless（api/*.py + api/_shared/core.py）提供另一套 API 入口。
4. **核心領域層**：tonesoul/（治理、管線、記憶、LLM、council）；核心流程集中在 unified_pipeline.py:78。
5. **資料/治理層**：memory/, memory_base/, law/, spec/, docs/ + 大量 workflow/scripts。

## 主要弱點（專業視角，按風險排序）

1. **發布封裝有實質風險**：pyproject 的 package include 是 tonesoul52*，但實際主套件是 tonesoul，會造成打包內容錯誤或空包。證據：pyproject.toml:70、pyproject.toml:6。CI 又用 PYTHONPATH=. 繞過封裝驗證，風險被掩蓋。證據：ci.yml:38。
2. **後端雙軌邏輯重複，容易漂移**：Flask 與 serverless 各自維護 rate-limit、payload 驗證、cache key 等同類函式。證據：apps/api/server.py:137、api/_shared/core.py:311。
3. **認證邊界不一致**：有 read token 機制，但關鍵寫入/運算端點（/api/chat, /api/consolidate, /api/consent*）未套同級驗證。證據：server.py:312、server.py:1289、server.py:1506、server.py:1866。
4. **Git hygiene/資料治理壓力高**：大體積 memory 歷史檔直接進 repo（單檔 33MB、43MB 級），有隱私與倉庫膨脹風險。例：self_journal.before_20260301.jsonl、provenance_ledger.before_20260301.jsonl。
5. **.gitignore 存在混編/Null byte 污染**，規則可靠性與跨平台一致性有風險。證據：.gitignore:100 到 :104。
6. **LLM backend 整合未完成**：新增了 LM Studio client，但主匯出與主流程仍只支援 Gemini/Ollama。證據：tonesoul/llm/lmstudio_client.py:20、tonesoul/llm/__init__.py:6、apps/api/server.py:1677。
7. **核心檔案過大（維護性弱點）**：unified_pipeline.py、apps/api/server.py 都是超大型單檔，改動耦合與回歸風險高。
8. **規格與實作路徑有漂移**：架構規格仍引用 body/*，但現行目錄已不是這個拓樸。證據：TAE-01_Architecture_Spec.md:36。
9. **子模組未初始化，重現環境有缺口**。證據：.gitmodules:1 與目前 submodule status 警告。

## 補充

- 我有跑針對 Ollama fallback 的測試：tests/test_ollama_fallback.py 共 7 項通過。
- experiments/test_lmstudio_governance.py 是腳本型，不是 pytest 測試（collect 0）。
- 掃描過程執行 hygiene script，讓 docs/status/git_hygiene_latest.json/.md 出現更新痕跡（目前也在 dirty 狀態裡）。

## 後續建議

1. 若你要，我下一步可以直接給你一份「弱點修復順序 + 具體 PR 切分」(P0/P1/P2)。
2. 也可以先做「最小風險修補包」：先解封裝問題、統一路由認證策略、清理 .gitignore 編碼污染。
