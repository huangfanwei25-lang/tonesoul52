# GPT-5.4 架構分析報告

> ⚠️ 報告開頭被終端機截斷，以下為可見部分

## 弱點分析（續）

6. api/_shared/core.py#L260 的 Supabase、memory_base 的 index，以及未初始化的 submodule OpenClaw-Memory。這不是一套記憶系統，是多套疊加。
7. 契約與打包也在漂移。pyproject.toml#L6 套件叫 tonesoul52，但 #L70 只 include tonesoul52*，實作卻在 tonesoul。scripts/chat_cli.py#L42 仍把 pipeline.process() 當 dict，用的 history 格式也和 unified_pipeline.py#L774 期待的不一致。

## 架構整理

- **展示層/BFF**：apps/web。Next.js UI、route handlers、本地對話儲存與 client-side provider transport，核心在 ChatInterface.tsx 與 route.ts。
- **服務層**：兩條 Python API。Vercel serverless 在 api，Flask backend 在 apps/api/server.py。
- **治理核心**：集中在 unified_pipeline.py、tension_engine.py、compute.py、runtime.py。
- **記憶層**：程式 abstraction 在 soul_db.py，實際工作區在 memory、memory_base、以及空的 submodule OpenClaw-Memory。

## Git 與本地記憶

- master 目前比 origin/master 超前 2 個 commit，且工作樹是髒的；未提交變更在 ollama_client.py 和 docs/status/git_hygiene_latest.*。
- Git 熱點很集中：task.md 107 次、ChatInterface.tsx 44 次、unified_pipeline.py 34 次、docs/status/* 多個檔案 18-25 次。流程/報表噪音偏高。
- 作者歸屬不理想：git shortlog 顯示 unknown <xsw123zaq@gmail.com> 421 commits，Fan-Wei Huang 95 commits，審計與責任追蹤會失真。
- .codex/memories/ 是空的，但真正的本地互動記憶在 history.jsonl 和 state_5.sqlite*；history.jsonl 有 1476 筆、34 個 session，時間範圍是 2025-12-23 到 2026-03-06 UTC。
- repo 自己的 runtime memory 更大：memory 目前 43 個檔案、約 29.61MB；最大的是 provenance_ledger.jsonl 13.97MB、self_journal.jsonl 10.34MB、soul.db 5.68MB。

## 優先順序

1. 先把 memory/archive/retention/jsonl/*.jsonl 從版本控制策略移除，補 CI/denylist，否則 public/private 邊界是假的。
2. 收斂成單一 API surface，只保留一條對外契約；Next BFF、serverless、Flask 只能有一個是正式面。
3. 把 unified_pipeline.py 拆成 typed stages，並抽出共用 payload/contract 模組。
4. 定義唯一的 memory source of truth，明確回答 JSONL、SQLite、Supabase、FAISS 各自是主庫、cache，還是 archive。
